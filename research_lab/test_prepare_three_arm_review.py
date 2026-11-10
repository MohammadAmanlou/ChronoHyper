"""Synthetic offline tests of new three-arm source-intake prep.

Never opens user's local private paper text or reveals A/B/C keys.
"""
import csv
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from research_lab.blind_paper_eval import csv_read, csv_write
from research_lab.prepare_three_arm_review import (
    prepare, status, OUT, FORM, KEY, LINKS, LIBRARY, RUBRIC,
    PRIOR_V2, PRIOR_V3, PRIOR_COHERENCE, sha,
)


def fake_case(year, index):
    total = 20
    return {
        "year": year, "stable_id": "C{:02d}".format(index), "level": 1,
        "member_count": total, "eligible_member_count": total,
        "member_ids": ["n{:02d}".format(i) for i in range(total)],
        "v2_label": "Graph / Neural",
        "v2_gloss": "Graph and neural terms are seen in the members.",
        "phrase_evidence": {
            "graph neural": {
                "support_count": 6,
                "support_node_ids": ["n{:02d}".format(i) for i in range(6)],
                "provenance_article_ids": ["101", "102"],
            }
        }
    }


class ThreeArmPrepTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.nodes = [
            {
                "id": "n{:02d}".format(i),
                "type": "method",
                "surface_form": "Graph neural research term {:02d}".format(i),
                "first_seen_year": 2018,
                "provenance": {"articles": ["101", "102", "999"]},
            }
            for i in range(20)
        ]
        self.papers = {
            "101": {"id": "101", "title": "Prior graph material paper", "year": "2017"},
            "102": {"id": "102", "title": "Neural material modeling", "year": "2018"},
            "999": {"id": "999", "title": "FUTURE source must be excluded", "year": "2027"},
        }
        for year in (2020, 2022, 2024):
            path = self.root / ("research_outputs/label_v2/"
                                "candidates_v2_{}.json".format(year))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps([fake_case(year, i) for i in range(12)]),
                encoding="utf-8")
        old = [{"year": str(2022 if i % 2 else 2024),
                "stable_id": "C00" if i == 0 else "previous-v2-{}".format(i)}
               for i in range(24)]
        v3 = [{"year": str(2020 if i % 2 else 2022),
               "stable_id": "C01" if i == 1 else "previous-v3-{}".format(i),
               "v3_side": "A" if i % 2 else "B"}
              for i in range(24)]
        coherence = [{
            "snapshot_year": str(2024 if i % 2 else 2020),
            "target_cluster": "C02" if i == 0 else "old-coherence-{}".format(i),
        } for i in range(48)]
        self._save(PRIOR_V2, old, ("year", "stable_id"))
        self._save(PRIOR_V3, v3, ("year", "stable_id", "v3_side"))
        self._save(PRIOR_COHERENCE, coherence, ("snapshot_year", "target_cluster"))

    def tearDown(self):
        self.tmp.cleanup()

    def _save(self, path, rows, fields):
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        csv_write(file, rows, fields)

    @patch("research_lab.prepare_three_arm_review._source")
    def test_12_case_new_stratified_packet_and_all_old_cases_excluded(self, source):
        source.return_value = (self.nodes, self.papers)
        receipt = prepare(self.root)
        self.assertEqual(receipt["cases"], 12)
        self.assertEqual(receipt["stage"], "SOURCE_SCREENING_REQUIRED_NOT_RATED")
        self.assertEqual(receipt["coherence_exclusion_status"],
                         "48_ROW_REAL_TARGETS_EXCLUDED")
        self.assertTrue(receipt["posthoc_design_following_seen_v2_v3_losses"])
        self.assertTrue(receipt["no_real_ratings_yet"])
        base = self.root / OUT
        preview = csv_read(base / FORM)
        keys = csv_read(base / KEY)
        links = csv_read(base / LINKS)
        papers = csv_read(base / LIBRARY)
        self.assertEqual(len(preview), len(keys))
        self.assertEqual([r["snapshot_year"] for r in keys].count("2020"), 4)
        self.assertEqual([r["snapshot_year"] for r in keys].count("2022"), 4)
        self.assertEqual([r["snapshot_year"] for r in keys].count("2024"), 4)
        self.assertNotIn(("2024", "C00"), {
            (r["snapshot_year"], r["stable_id"]) for r in keys})
        self.assertNotIn(("2020", "C01"), {
            (r["snapshot_year"], r["stable_id"]) for r in keys})
        self.assertNotIn(("2020", "C02"), {
            (r["snapshot_year"], r["stable_id"]) for r in keys})
        self.assertTrue(all(set((r["A_method"], r["B_method"],
                                r["C_method"])) == {"v2", "v3", "v4"} for r in keys))
        self.assertNotIn("A_method", preview[0])
        self.assertTrue(all(r["source_evidence_status"].startswith(
            "SOURCE_SCREENING_REQUIRED") for r in preview))
        self.assertTrue(all(p["source_url"] == "" and
                            p["authentic_primary_passage"] == "" for p in papers))
        self.assertFalse(any(r["paper_id"] == "999" for r in links))
        self.assertEqual(status(self.root)["locally_user_attested_complete_paper_records"], 0)
        self.assertFalse((base / "AI_ONLY_REVIEW24.csv").exists())
        before = (sha(base / FORM), sha(base / KEY), sha(base / LINKS))
        with self.assertRaises(FileExistsError):
            prepare(self.root)
        self.assertEqual(before, (sha(base / FORM), sha(base / KEY), sha(base / LINKS)))

    @patch("research_lab.prepare_three_arm_review._source")
    def test_fails_closed_without_prior_private_key(self, source):
        source.return_value = (self.nodes, self.papers)
        (self.root / PRIOR_V3).unlink()
        with self.assertRaises(FileNotFoundError):
            prepare(self.root)
        self.assertFalse((self.root / OUT).exists())

    @patch("research_lab.prepare_three_arm_review._source")
    def test_refuses_insufficient_new_cases_without_using_reviewed(self, source):
        source.return_value = (self.nodes, self.papers)
        source_path = self.root / "research_outputs/label_v2/candidates_v2_2022.json"
        source_path.write_text(
            json.dumps([fake_case(2022, 0), fake_case(2022, 1)]),
            encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unreviewed"):
            prepare(self.root)
        self.assertFalse((self.root / OUT).exists())

    @patch("research_lab.prepare_three_arm_review._source")
    def test_date_cutoff_and_permission_are_checked_only_as_user_attestation(self, source):
        source.return_value = (self.nodes, self.papers)
        prepare(self.root)
        path = self.root / OUT / LIBRARY
        records = csv_read(path)
        for p in records:
            p.update({
                "source_url": "https://arxiv.org/abs/1710.00001",
                "historical_version_date": "2025-01-01",
                "passage_locator": "Section 2, page 3",
                "authentic_primary_passage": (
                    "A synthetic passage used only to test date cutoff and "
                    "source status. No scientific observations can be inferred "
                    "from these characters or their repeated length."),
                "historical_version_verified_yes_no": "yes",
                "access_permission_confirmed_yes_no": "yes",
            })
        csv_write(path, records, tuple(records[0].keys()))
        check = status(self.root)
        self.assertEqual(check["locally_user_attested_complete_paper_records"], 0)
        for p in records:
            p["historical_version_date"] = "2019-01-01"
        csv_write(path, records, tuple(records[0].keys()))
        check = status(self.root)
        self.assertEqual(check["locally_user_attested_complete_paper_records"], len(records))
        self.assertFalse(check["ready_for_blind_semantic_rating"])
        self.assertFalse(check["source_verification_independently_confirmed_by_software"])


if __name__ == "__main__":
    unittest.main()
