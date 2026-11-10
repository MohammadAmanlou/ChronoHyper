"""No-network tests for local fair blind review, checkpoints and AI-only scoring."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research_lab.ai_blind_fulltext_review import (
    _local_post_validate, _parse_response, _prompt, _read_packet, run,
    FINAL, SUMMARY)
from research_lab.fulltext_label_audit import (
    OUT, BASE, FIXED_REVIEW, REVIEW_FIELDS, REVIEW, _sha)
from research_lab.summarize_ai_fulltext_review import summarize, OUTPUT
from research_lab.blind_paper_eval import csv_read


def sample(i):
    row = {k: "" for k in REVIEW_FIELDS}
    row.update(
        blind_id="L{:03d}".format(i), snapshot_year="2022",
        member_count="20",
        member_names="graph neural networks | crystalline structures",
        source_article_titles="First research paper",
        label_A="Graph neural networks",
        gloss_A="Graph neural networks for predicting materials properties.",
        label_B="Crystal modeling methods",
        gloss_B="Scientific models of crystals.",
        primary_source_passages=(
            "PAPER 5396 | Actual titled study (2018); "
            "https://arxiv.org/pdf/1710.10324v1; 2017-10-27; Abstract\n"
            "The graph convolutional neural network predicts materials properties "
            "from atom connections, with an interpretable representation."),
        evidence_status="USER_ATTESTED_FULLTEXT", passage_count="1",
    )
    return row


def mock_response(payload):
    return {"response": json.dumps({
        "evidence_sufficient_yes_no": "yes",
        "A_accuracy_accurate_vague_wrong": "accurate",
        "B_accuracy_accurate_vague_wrong": "vague",
        "A_gloss_overclaim_yes_no_unclear": "no",
        "B_gloss_overclaim_yes_no_unclear": "unclear",
        "review_notes": (
            "PAPER 5396 supports the central GNN research topic, but it "
            "does not independently establish every detail of the second gloss."),
    })}


class AIBlindReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.base = self.root / OUT
        self.base.mkdir(parents=True)
        self.rows = [sample(i) for i in range(1, 25)]
        self.path = self.base / REVIEW
        with self.path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=REVIEW_FIELDS)
            w.writeheader()
            w.writerows(self.rows)
        (self.base / "assembled_receipt_LOCAL.json").write_text(
            json.dumps({"blind_packet_sha256": _sha(self.path)}),
            encoding="utf-8")
        keypath = self.root / BASE
        keypath.mkdir(parents=True)
        with (keypath / "mapping_PRIVATE.csv").open(
                "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=("blind_id", "v3_side"))
            w.writeheader()
            w.writerows([
                {"blind_id": x["blind_id"],
                 "v3_side": "A" if i % 2 else "B"}
                for i, x in enumerate(self.rows)
            ])

    def tearDown(self):
        self.tmp.cleanup()

    def test_reject_remote_endpoint(self):
        for target in (
            "https://api.example.com/api/generate",
            "http://example.com/api/generate",
            "http://127.0.0.1:11434/other",
            "http://evil@127.0.0.1:11434/api/generate",
        ):
            with self.assertRaises(ValueError):
                _local_post_validate(target)

    def test_fair_prompt_is_neither_too_strict_nor_grade_inflation(self):
        prompt = _prompt(self.rows[0])
        self.assertIn("TITLE A:", prompt)
        self.assertNotIn("mapping_PRIVATE", prompt)
        from research_lab.ai_blind_fulltext_review import SYSTEM
        self.assertIn("broad", SYSTEM.lower())
        self.assertIn("DO NOT INVENT EVIDENCE", SYSTEM.upper())

    def test_overstated_grades_removed_when_insufficient(self):
        obj = json.loads(mock_response({})["response"])
        obj["evidence_sufficient_yes_no"] = "no"
        result = _parse_response(self.rows[0], obj, "qwen3:8b")
        self.assertEqual(result["A_accuracy_accurate_vague_wrong"], "")
        self.assertEqual(result["A_gloss_overclaim_yes_no_unclear"], "unclear")

    def test_reject_unrelated_hallucinated_paper_id(self):
        obj = json.loads(mock_response({})["response"])
        obj["review_notes"] = "PAPER 99999 conclusively establishes this specific approach."
        with self.assertRaisesRegex(ValueError, "cite"):
            _parse_response(self.rows[0], obj, "qwen3:8b")

    @patch("research_lab.ai_blind_fulltext_review._local_post")
    def test_resume_and_final_without_overwriting_independent_score(self, post):
        post.side_effect = lambda endpoint, payload, timeout: mock_response(payload)
        src = self.path.read_bytes()
        run(self.root, limit=2)
        self.assertFalse((self.base / FINAL).exists())
        self.assertEqual(post.call_count, 2)
        run(self.root)
        self.assertEqual(post.call_count, 24)
        self.assertEqual(self.path.read_bytes(), src)
        rated = csv_read(self.base / FINAL)
        self.assertEqual(len(rated), 24)
        self.assertEqual([x["blind_id"] for x in rated],
                         [x["blind_id"] for x in self.rows])
        self.assertTrue(all(x["reviewer_id"].endswith("AI_ONLY") for x in rated))
        for a, b in zip(self.rows, rated):
            self.assertTrue(all(a[k] == b[k] for k in FIXED_REVIEW))
        with self.assertRaises(FileExistsError):
            run(self.root)
        score = summarize(self.root)
        self.assertEqual(score["title_comparison"]["v3_wins"], 12)
        self.assertEqual(score["title_comparison"]["v3_losses"], 12)
        self.assertTrue((self.base / OUTPUT).is_file())
        self.assertFalse((self.base / "score_LOCAL_PRIVATE.json").exists())
        with self.assertRaises(FileExistsError):
            summarize(self.root)

    @patch("research_lab.ai_blind_fulltext_review._local_post")
    def test_invalid_yes_grade_retries_with_schema_and_keeps_original(self, post):
        from research_lab.ai_blind_fulltext_review import OUTPUT_SCHEMA
        original_hash = _sha(self.path)
        bad = json.loads(mock_response({})["response"])
        bad["B_accuracy_accurate_vague_wrong"] = ""
        post.side_effect = [
            {"response": json.dumps(bad)},
            mock_response({}),
        ]
        result = run(self.root, limit=1, attempts=2)
        self.assertIsNone(result)  # A two-case smoke-test never creates a final file
        self.assertEqual(post.call_count, 2)
        first = post.call_args_list[0].args[1]
        second = post.call_args_list[1].args[1]
        self.assertEqual(first["format"], OUTPUT_SCHEMA)
        self.assertEqual(first["format"]["type"], "object")
        self.assertEqual(len(first["format"]["required"]), 6)
        self.assertTrue(second["think"] is False)
        self.assertIn("YOUR PREVIOUS OUTPUT WAS INVALID", second["prompt"])
        self.assertIn("BOTH A and B titles", second["prompt"])
        self.assertIn("L001", second["prompt"])
        self.assertEqual(_sha(self.path), original_hash)
        self.assertFalse((self.base / FINAL).exists())
        self.assertEqual(json.loads(
            (self.base / "AI_ONLY_BLIND24_QWEN_LOCAL" / "L001.json"
            ).read_text(encoding="utf-8"))["ratings"][
                "B_accuracy_accurate_vague_wrong"], "vague")

    @patch("research_lab.ai_blind_fulltext_review._local_post")
    def test_repeated_invalid_grade_stays_unrated(self, post):
        bad = json.loads(mock_response({})["response"])
        bad["A_accuracy_accurate_vague_wrong"] = ""
        post.return_value = {"response": json.dumps(bad)}
        result = run(self.root, limit=1, attempts=2)
        self.assertIsNone(result)
        self.assertEqual(post.call_count, 2)
        self.assertFalse((self.base / FINAL).exists())
        self.assertFalse((self.base / SUMMARY).exists())
        self.assertFalse(
            (self.base / "AI_ONLY_BLIND24_QWEN_LOCAL" / "L001.json").exists())

    @patch("research_lab.ai_blind_fulltext_review._local_post")
    def test_errors_never_create_fake_completed_form(self, post):
        post.side_effect = OSError("offline")
        run(self.root, limit=2, attempts=1)
        self.assertFalse((self.base / FINAL).exists())
        self.assertFalse((self.base / SUMMARY).exists())

    def test_tampered_original_packet_rejected(self):
        self.path.write_text(self.path.read_text(encoding="utf-8") + "\n",
                             encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "changed"):
            _read_packet(self.root)


if __name__ == "__main__":
    unittest.main()
