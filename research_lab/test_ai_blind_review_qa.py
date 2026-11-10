"""Synthetic checks for read-only AI 24-case QA and uncertainty flags."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from research_lab.ai_blind_review_qa import inspect_pair, audit
from research_lab.test_ai_blind_fulltext_review import sample
from research_lab.fulltext_label_audit import OUT, REVIEW, REVIEW_FIELDS, _sha
from research_lab.ai_blind_fulltext_review import FINAL, SUMMARY


class AIReviewQualityAuditTests(unittest.TestCase):
    def test_detects_blank_title_scored_as_accurate(self):
        old = sample(14)
        old["label_B"] = ""
        rated = dict(old)
        rated.update({
            "evidence_sufficient_yes_no": "yes",
            "A_accuracy_accurate_vague_wrong": "vague",
            "B_accuracy_accurate_vague_wrong": "accurate",
            "A_gloss_overclaim_yes_no_unclear": "unclear",
            "B_gloss_overclaim_yes_no_unclear": "unclear",
        })
        issues, _ = inspect_pair(old, rated)
        self.assertIn(("EMPTY_TITLE_WAS_GRADED", "B"),
                      [(x["issue"], x["field_or_arm"]) for x in issues])

    def test_flags_explanation_overclaim_vs_unclear_without_regrading(self):
        old = sample(13)
        rated = dict(old)
        rated.update({
            "evidence_sufficient_yes_no": "yes",
            "A_accuracy_accurate_vague_wrong": "vague",
            "B_accuracy_accurate_vague_wrong": "accurate",
            "A_gloss_overclaim_yes_no_unclear": "unclear",
            "B_gloss_overclaim_yes_no_unclear": "unclear",
            "review_notes": "The gloss for A overclaims by using a scientific assertion without support."
        })
        _, warnings = inspect_pair(old, rated)
        self.assertIn("NOTES_SAY_OVERCLAIM_BUT_FLAG_UNCLEAR",
                      [x["warning"] for x in warnings])
        self.assertEqual(rated["A_gloss_overclaim_yes_no_unclear"], "unclear")

    def test_does_not_falsely_flag_negated_overclaim(self):
        old = sample(1)
        rated = dict(old)
        rated.update({
            "evidence_sufficient_yes_no": "yes",
            "A_accuracy_accurate_vague_wrong": "accurate",
            "B_accuracy_accurate_vague_wrong": "vague",
            "A_gloss_overclaim_yes_no_unclear": "no",
            "B_gloss_overclaim_yes_no_unclear": "no",
            "review_notes": "The gloss for A does not overclaim. Title A is accurate."
        })
        errors, warnings = inspect_pair(old, rated)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_abstention_wrong_requires_manual_scope_review(self):
        old = sample(7)
        old["label_A"] = "Unresolved heterogeneous cluster"
        rated = dict(old)
        rated.update({
            "evidence_sufficient_yes_no": "yes",
            "A_accuracy_accurate_vague_wrong": "wrong",
            "B_accuracy_accurate_vague_wrong": "vague",
            "A_gloss_overclaim_yes_no_unclear": "no",
            "B_gloss_overclaim_yes_no_unclear": "no",
            "review_notes": "TITLE A is wrong because one theme may exist."
        })
        _, warnings = inspect_pair(old, rated)
        self.assertIn("ABSTENTION_GRADED_WRONG_NEEDS_SCOPE_REVIEW",
                      [x["warning"] for x in warnings])

    def test_full_qa_is_read_only_and_verifies_real_fingerprints(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / OUT
            base.mkdir(parents=True)
            original = [sample(i) for i in range(1, 25)]
            original[13]["label_B"] = ""
            orig_path = base / REVIEW
            with orig_path.open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=REVIEW_FIELDS)
                w.writeheader()
                w.writerows(original)
            digest = _sha(orig_path)
            (base / "assembled_receipt_LOCAL.json").write_text(
                json.dumps({"blind_packet_sha256": digest}), encoding="utf-8")
            rated = []
            for row in original:
                obj = dict(row)
                obj.update({
                    "A_accuracy_accurate_vague_wrong": "accurate",
                    "B_accuracy_accurate_vague_wrong": "vague",
                    "A_gloss_overclaim_yes_no_unclear": "no",
                    "B_gloss_overclaim_yes_no_unclear": "unclear",
                    "evidence_sufficient_yes_no": "yes",
                    "reviewer_id": "OLLAMA_LOCAL_QWEN3_8B_AI_ONLY",
                    "review_notes": "PAPER 5396 supports the topic but not all claims.",
                })
                rated.append(obj)
            rated[13]["B_accuracy_accurate_vague_wrong"] = "accurate"
            with (base / FINAL).open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=REVIEW_FIELDS)
                w.writeheader()
                w.writerows(rated)
            (base / SUMMARY).write_text(json.dumps({
                "stage": "AI_ONLY_SAME_CORPUS_DEVELOPMENT_NOT_INDEPENDENT_VALIDATION",
                "blind_packet_sha256": digest,
                "rated_csv_sha256": _sha(base / FINAL),
                "reviewed": 24,
            }), encoding="utf-8")
            before = (_sha(orig_path), _sha(base / FINAL))
            result = audit(root)
            self.assertEqual(result["reviewed_cases"], 24)
            self.assertIn("L014", [x["case"] for x in
                                   result["structural_issues"]])
            self.assertEqual(before, (_sha(orig_path), _sha(base / FINAL)))
            self.assertFalse((base / "score_LOCAL_PRIVATE.json").exists())


if __name__ == "__main__":
    unittest.main()
