"""Pure CPU, synthetic checks for private Qwen pool-preservation preflight."""
import copy
import unittest
from pathlib import Path

from research_lab.test_multiview_source_union_audit import fixture
from research_lab import qwen_candidate_preflight as pre
from research_lab import qwen_entity_rerank as q


class QwenCandidatePreflightTests(unittest.TestCase):
    def test_complete_three_view_union_has_30_of_34_fixture_gold(self):
        rank, score=fixture()
        report=pre.audit(Path("."),rank,score)
        self.assertEqual(report["n_questions"],34)
        self.assertEqual(report["target_present_in_gold_blind_pool_count"],30)
        self.assertEqual(report["missing"],["F031","F032","F033","F034"])
        self.assertEqual(report["min_actual_pool_size"],300)
        self.assertEqual(report["max_actual_pool_size"],300)
        self.assertTrue(report["model_not_run"])
        self.assertFalse(report["gold_file_opened"])

    def test_name_depth_80_must_be_preserved(self):
        rank,score=fixture()
        first=rank["results"][20]
        pool=q.candidates(first["views"],300)
        target=("method","gold20")
        self.assertIn(target,[q.key(x) for x in pool])
        report=pre.audit(Path("."),rank,score)
        self.assertIsNotNone(report["per_question_PRIVATE"][20]
                             ["target_position_in_UNSORTED_candidate_pool"])

    def test_score_source_mismatch_rejected(self):
        rank,score=fixture()
        score["rankings_sha256_verified"]="tamper"
        with self.assertRaisesRegex(ValueError,"SHA differ"):
            pre.audit(Path("."),rank,score)

    def test_reject_only_partly_scored_results(self):
        rank,score=fixture()
        del score["per_question_rank_LOCAL_PRIVATE"]["F034"]
        with self.assertRaisesRegex(ValueError,"Exactly the previous"):
            pre.audit(Path("."),rank,score)

    def test_disallow_lower_pool_budget(self):
        rank,score=fixture()
        with self.assertRaisesRegex(ValueError,"300-budget"):
            pre.audit(Path("."),rank,score,max_candidates=200)


if __name__=="__main__":
    unittest.main()
