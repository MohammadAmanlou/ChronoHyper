"""Offline guards: V4 is only a new evidence-separated presentation, not a retuned model."""
import json
import tempfile
import unittest
from pathlib import Path

from research_lab.label_v4_exploratory import render_case, run, STAGE
from research_lab.label_v3 import improve_case


def record(count, n=10, term="graph neural", articles=("1", "2")):
    return {
        "year": 2024, "level": 1, "stable_id": "test1",
        "member_count": n, "eligible_member_count": n,
        "v2_label": "Graph Neural Networks / Materials",
        "phrase_evidence": {
            term: {
                "support_count": count,
                "support_node_ids": ["n{}".format(i) for i in range(count)],
                "provenance_article_ids": list(articles),
            },
        },
    }


class V4EvidenceSeparationTests(unittest.TestCase):
    def test_majority_name_evidence_is_not_scientific_confirmation(self):
        row = record(7)
        before = json.dumps(row, sort_keys=True)
        result = render_case(row)
        self.assertEqual(result["display_title"], "Graph Neural")
        self.assertEqual(result["lexical_evidence_state"],
                         "MAJORITY_LEXICAL_CANDIDATE")
        self.assertFalse(result["abstained_from_specific_topic"])
        self.assertEqual(result["scientific_semantic_accuracy"],
                         "NOT_INDEPENDENTLY_MEASURED")
        self.assertEqual(before, json.dumps(row, sort_keys=True))

    def test_partial_is_separate_status_not_title_prefix(self):
        x = render_case(record(4))
        self.assertEqual(x["display_title"], "Graph Neural")
        self.assertEqual(x["lexical_evidence_state"],
                         "PARTIAL_LEXICAL_CANDIDATE")
        self.assertNotIn("Partial theme:", x["display_title"])
        self.assertEqual(x["qualifying_source_phrase_evidence"]["support_count"], 4)

    def test_abstention_is_not_assertion_of_heterogeneity(self):
        row = record(2)
        result = render_case(row)
        self.assertTrue(result["abstained_from_specific_topic"])
        self.assertEqual(result["lexical_evidence_state"],
                         "NO_QUALIFIED_LEXICAL_TOPIC")
        self.assertNotIn("heterogeneous", result["display_title"].lower())
        self.assertIn("not evidence that no shared scientific topic exists",
                      result["display_gloss"])
        self.assertEqual(result["observed_terms_not_confirmed_topics"][0][
            "name_mention_count"], 2)
        self.assertIsNone(result["qualifying_source_phrase_evidence"])

    def test_no_qualifying_phrase_because_of_paper_gate(self):
        x = render_case(record(8, articles=("1",)))
        self.assertTrue(x["abstained_from_specific_topic"])
        self.assertEqual(x["observed_terms_not_confirmed_topics"][0][
                         "article_provenance_count"], 1)

    def test_scoped_lexical_provenance_count_checks(self):
        row = record(4)
        row["phrase_evidence"]["graph neural"]["support_count"] = 6
        with self.assertRaisesRegex(ValueError, "Corrupt provenance"):
            render_case(row)

    def test_v4_matches_v3_status_mapping_on_synthetic_cases(self):
        mapping = {
            "LEADING_NAME_PHRASE_MAJORITY": "MAJORITY_LEXICAL_CANDIDATE",
            "PARTIAL_NAME_PHRASE": "PARTIAL_LEXICAL_CANDIDATE",
            "ABSTAIN_INSUFFICIENT_DOMAIN_PHRASE": "NO_QUALIFIED_LEXICAL_TOPIC",
        }
        for count in (2, 4, 7):
            row = record(count)
            self.assertEqual(render_case(row)["lexical_evidence_state"],
                             mapping[improve_case(row)["label_rule_status"]])

    def test_exploratory_output_is_local_no_score_and_immutable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for yr in (2020, 2022, 2024):
                path = root / "research_outputs/label_v2" / (
                    "candidates_v2_{}.json".format(yr))
                path.parent.mkdir(parents=True, exist_ok=True)
                rows = []
                for idx in range(60):
                    row = record(2 if idx % 2 else 4)
                    row.update(year=yr, stable_id="S{:03d}".format(idx),
                               level=0 if idx < 12 else 1)
                    rows.append(row)
                path.write_text(json.dumps(rows), encoding="utf-8")
            output = root / "local_only/label_v4_exploratory"
            result = run(root)
            self.assertEqual(result["n_records"], 180)
            self.assertEqual(result["stage"], STAGE)
            self.assertTrue(result["24_original_blind_cases_not_reused_as_confirmatory_test"])
            self.assertFalse((root / "score_LOCAL_PRIVATE.json").exists())
            self.assertTrue((output / "v4_exploratory_2024.json").is_file())
            with self.assertRaises(FileExistsError):
                run(root)


if __name__ == "__main__":
    unittest.main()
