"""Submission-facing paths, figure and scientific-claim guardrails.

Lightweight test for a readable reviewer entry point; detailed scientific
and hierarchy invariants are covered by the existing test suites.
"""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]

class SubmissionSurfaceTests(unittest.TestCase):
    def test_readme_relative_links_exist(self):
        page=(ROOT/"README.md").read_text(encoding="utf-8")
        links=re.findall(r'\]\(([^)]+)\)',page)
        checked=0
        for href in links:
            if href.startswith(("https://","http://","#","mailto:")):
                continue
            path=href.split("#",1)[0]
            if not path:
                continue
            with self.subTest(link=href):
                self.assertTrue((ROOT/path).exists(),f"Broken README link: {href}")
            checked+=1
        self.assertGreaterEqual(checked,7)

    def test_posthoc_claims_are_unambiguous(self):
        readme=(ROOT/"README.md").read_text(encoding="utf-8")
        extended=(ROOT/"report.md").read_text(encoding="utf-8")
        self.assertIn("12/34",readme)
        self.assertIn("29/34",readme)
        self.assertIn("Candidate recall",readme)
        self.assertIn("not independent confirmation",readme.lower())
        self.assertIn("Qwen3",extended)
        self.assertIn("post-hoc",extended.lower())
        self.assertIn("p = 0.69",readme)
        self.assertTrue((ROOT/"AI_USAGE.md").exists())

    def test_aggregate_gpu_evidence_matches_submission(self):
        import json
        path=ROOT/"research_outputs/gpu_retrieval_development_summary.json"
        self.assertTrue(path.is_file())
        rows=json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(rows["scope"]["questions_scored"],34)
        self.assertEqual(rows["observed_out_of_34"]["bge_context"]["hit5"],10)
        self.assertEqual(rows["observed_out_of_34"]["qwen_raw"]["hit5"],12)
        self.assertEqual(rows["observed_out_of_34"]["qwen_anchor1"]["hit5"],12)
        self.assertEqual(rows["source_candidate_union"]["correct_entity_present"],29)
        self.assertIn("NOT_INDEPENDENT",rows["status"])
        self.assertIn("candidate recall",rows["source_candidate_union"]["meaning"].lower())

    def test_source_delta_report_frozen_training_evidence(self):
        import json
        s=json.loads((ROOT/"research_outputs/temporal_locality_posthoc.json").read_text(encoding="utf-8"))
        self.assertTrue(s["training_event_ids_matched_frozen_collapsed_outputs"])
        self.assertTrue(s["original_provider_zip_sha256_verified"])
        self.assertEqual(s["excluded_heldout_source_paper_count"],20)
        self.assertEqual([(q["old_hyperedges"],q["new_hyperedges_added"],
                           q["root_identity_changes_touched"],q["root_identity_changes_untouched"])
                          for q in s["transitions"]],[(209,130,1,10),(339,306,7,20)])
        f=(ROOT/"figures/temporal_locality.svg").read_text(encoding="utf-8")
        for v in ("1/76","10/1429","7/146","20/2018","0.546","0.002"):
            self.assertIn(v,f)
        self.assertIn("post-hoc",f)

    def test_reviewer_rubric_table_and_scientific_boundaries(self):
        page=(ROOT/"README.md").read_text(encoding="utf-8")
        for item in ("**T1**","**T2 / P1–P2**","**T2 / P3–P4**",
                     "**T3 / P5**","**T4**","**T5 / P6**",
                     "**T6** · Independent-view coherence",
                     "**T6** · Real temporal stability",
                     "**T6** · Label overclaim rate",
                     "**T6** · Extrinsic retrieval",
                     "**T7**"):
            with self.subTest(rubric=item):
                self.assertIn(item,page)
        self.assertIn("NOT_EVALUATED",page)
        self.assertIn("not independent confirmation",page.lower())
        self.assertIn("Flat **3/34** vs Route-4 **2/34**",page)
        self.assertIn("4-page PDF",page)
        self.assertLess(len(page),10000)

    def test_single_concise_current_figure_and_no_stale_qwen_doc(self):
        chart=ROOT/"figures/retrieval_development.svg"
        self.assertTrue(chart.is_file())
        text=chart.read_text(encoding="utf-8")
        self.assertIn("<svg",text)
        self.assertIn("29/34",text)
        self.assertIn("12 / 34",text)
        self.assertFalse((ROOT/"docs/QWEN3_RERANK_RUNBOOK.md").exists())
        for doc in ("README.md","docs/ASSESSMENT_STATUS.md",
                    "docs/ADVANCED_GPU_AND_TYPE_B.md"):
            self.assertNotIn("QWEN3_RERANK_RUNBOOK.md",
                             (ROOT/doc).read_text(encoding="utf-8"))

if __name__=="__main__":
    unittest.main()
