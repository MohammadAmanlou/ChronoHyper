"""Synthetic/localhost-free tests of safe, selective AI-only retry behavior."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research_lab import retry_failed_auto_label_judge as r
from research_lab.auto_label_judge import COLUMNS, RESULT
from research_lab.auto_primary_evidence import AUTO
from research_lab.blind_paper_eval import csv_read, csv_write
from research_lab.fulltext_label_audit import BASE, OUT


def case(cid):
    return {
      "blind_id": cid, "snapshot_year": "2020",
      "member_names": "Graph neural networks | Materials discovery",
      "label_A": "Materials graph models", "gloss_A": "Graph algorithms for materials.",
      "label_B": "Neural materials learning", "gloss_B": "Scientific models for crystals.",
    }


def passage(cid):
    return {
      "blind_id": cid, "snapshot_year": "2020",
      "paper_id": "100", "paper_title": "Materials learning study",
      "date_status": "ARXIV_V1_WITHIN_CUTOFF",
      "evidence_status": "AUTO_RETRIEVED_UNVERIFIED_NOT_REVIEWED",
      "source_version_date": "2019-01-03",
      "passage_locator": "PDF p1 (synthetic)",
      "versioned_source_url": "https://arxiv.org/pdf/1901.00100v1",
      "passage_text": "Graph algorithms for materials are studied using crystals.",
      "match_score": "0.89",
    }


def model_answer(sufficient="no"):
    return {"response": json.dumps({
      "evidence_sufficient_yes_no": sufficient,
      "A_accuracy_accurate_vague_wrong": "accurate",
      "B_accuracy_accurate_vague_wrong": "vague",
      "A_gloss_overclaim_yes_no_unclear": "no",
      "B_gloss_overclaim_yes_no_unclear": "unclear",
      "review_notes": "These candidate source excerpts do not support both glosses sufficiently.",
    })}


def prepared_private_files(tmp):
    root = Path(tmp)
    (root / BASE).mkdir(parents=True)
    (root / OUT).mkdir(parents=True)
    cases = [case("L%03d" % i) for i in range(1, 25)]
    csv_write(root / BASE / "blind_v2_v3_24.csv", cases, cases[0].keys())
    original = []
    for i, c in enumerate(cases):
        is_error = i < 21
        record = {key: "" for key in COLUMNS}
        record.update({
            "blind_id": c["blind_id"], "snapshot_year": c["snapshot_year"],
            "evidence_status": r.ORIGINAL_ERROR if is_error else
             "LOCAL_AI_SCORED_ON_MACHINE_EXTRACTED_SOURCES",
            "evidence_sufficient_yes_no": "no",
            "review_notes": r.ERROR_PREFIX + " JSON output invalid" if is_error
            else "The scientific source excerpt is not sufficient.",
        })
        original.append(record)
    csv_write(root / OUT / RESULT, original, COLUMNS)
    passages = [passage(c["blind_id"]) for c in cases]
    csv_write(root / OUT / AUTO, passages, passages[0].keys())
    return root


class RetryTests(unittest.TestCase):
    def test_payload_disables_thinking_and_requests_json(self):
        p = r.model_payload("qwen3:8b", "Classify")
        self.assertIs(p["think"], False)
        self.assertEqual(p["format"], "json")
        self.assertIs(p["stream"], False)
        self.assertGreaterEqual(p["options"]["num_predict"], 1000)

    def test_bad_json_is_not_called_insufficient_science(self):
        with patch.object(r, "_post_local", return_value={"response": "{", "done": True}):
            with self.assertRaises(json.JSONDecodeError):
                r.evaluate(case("L001"), [passage("L001")],
                           "qwen3:8b", "http://127.0.0.1:11434/api/generate")
        row = r.record_error(case("L001"), ValueError("JSON truncated"))
        self.assertEqual(row["retry_status"], r.ERROR)
        self.assertEqual(row["evidence_sufficient_yes_no"], "")
        self.assertNotEqual(row["retry_status"], r.ORIGINAL_ERROR)

    def test_truncated_output_not_accepted(self):
        with patch.object(r, "_post_local", return_value={
                "response": model_answer()["response"], "done_reason": "length"}):
            with self.assertRaisesRegex(ValueError, "output-token limit"):
                r.evaluate(case("L001"), [passage("L001")],
                           "qwen3:8b", "http://127.0.0.1:11434/api/generate")

    def test_probe_writes_nothing_and_run_preserves_originals(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = prepared_private_files(tmp)
            orig = (root / OUT / RESULT).read_bytes()
            blind = (root / BASE / "blind_v2_v3_24.csv").read_bytes()
            with patch.object(r, "_post_local", return_value=model_answer()) as mocked:
                r.run(str(root), probe=True)
                self.assertEqual(mocked.call_count, 1)
                self.assertFalse((root / OUT / r.RETRY_FILE).exists())
                summary = r.run(str(root))
                self.assertEqual(mocked.call_count, 22)
                self.assertEqual(summary["original_failed_case_count"], 21)
                self.assertEqual(summary["retry_AI_valid"], 21)
                self.assertEqual(summary["original_valid_judgments_preserved"], 3)
                self.assertEqual(summary["combined_AI_insufficient"], 24)
                again = r.run(str(root))
                self.assertEqual(mocked.call_count, 22)
                self.assertEqual(again["retry_cases_recorded"], 21)
            self.assertEqual(orig, (root / OUT / RESULT).read_bytes())
            self.assertEqual(blind, (root / BASE / "blind_v2_v3_24.csv").read_bytes())
            rows = csv_read(root / OUT / r.RETRY_FILE)
            self.assertEqual(len(rows), 21)
            self.assertTrue(all(x["retry_status"] == r.VALID for x in rows))

    def test_failure_checkpoint_can_be_retried_without_touching_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = prepared_private_files(tmp)
            calls = [0]
            def flaky(endpoint, payload):
                calls[0] += 1
                if calls[0] == 1:
                    return {"response": "{"}
                return model_answer()
            with patch.object(r, "_post_local", side_effect=flaky):
                summary = r.run(str(root))
                self.assertEqual(summary["retry_model_or_JSON_errors"], 1)
                self.assertEqual(summary["combined_AI_valid_count"], 23)
                summary = r.run(str(root), retry_errors=True)
                self.assertEqual(summary["retry_model_or_JSON_errors"], 0)
                self.assertEqual(summary["combined_AI_valid_count"], 24)
                self.assertEqual(calls[0], 22)


if __name__ == "__main__":
    unittest.main()
