"""Synthetic-only regression checks for scientific qualification in review status."""
import copy
import unittest
from research_lab.assessment_status import summarize


class AssessmentStatusTests(unittest.TestCase):
    def setUp(self):
        self.labels = {
            "schema":"chronohyper_v3_v2_blind_AI_names_titles_only_v1",
            "n_pairs":24,"evaluable":21,"excluded":3,
            "v3_wins":10,"v3_losses":4,"ties":7,
            "mean_rating_delta_v3_minus_v2":2/7,
            "descriptive_sign_p_two_sided":0.1795654296875,
            "gloss_overclaim_evaluable":{"v2":21,"v3":14},
            "gloss_overclaim_unclear":{"v2":3,"v3":10},
            "gloss_overclaim_rate":{"v2":0.0,"v3":0.0},
            "self_reported_reviewer_ids":["SYNTHETIC-TEST-ONLY"],
            "independent_paper_entailment_verified":False,
            "independent_judge_identity_verified":False,
            "development_review_not_confirmatory":True,
        }
        self.coh = {
            "schema":"ckl_fresh_key_isolated_paper_title_coherence_v1",
            "n_blind_cases":48,"n_matched_pairs":24,
            "evaluable_pairs":24,"excluded_insufficient_pairs":0,
            "mean_real":3.5416666666666665,"mean_control":2.75,
            "mean_paired_delta":0.7916666666666666,
            "real_higher_pairs":15,"control_higher_pairs":5,"ties":4,
            "exact_sign_p_descriptive_only":0.04138946533203125,
            "paired_bootstrap_95ci_exploratory":[.2916666666666667,1.25],
            "by_year":{"2020":{"evaluable_pairs":8},
                       "2022":{"evaluable_pairs":8},
                       "2024":{"evaluable_pairs":8}},
            "independent_full_paper_entailment_verified":False,
            "self_reported_AI_independence_only":True,
        }

    def test_expected_conservative_summary_and_uncertainty_bound(self):
        result=summarize(self.labels,self.coh)
        self.assertTrue(result["v2_v3"]["positive_direction_but_not_significant_at_0_05"])
        self.assertFalse(result["independent_full_paper_entailment_verified"])
        self.assertFalse(result["independent_human_expert_review_verified"])
        b=result["v2_v3"]["gloss_overclaim"]
        self.assertEqual(b["v3"]["n_unclear"],10)
        self.assertGreater(b["v3"]["exact_two_sided_95pct_upper_if_zero_observed"],.20)
        self.assertGreater(b["v2"]["exact_two_sided_95pct_upper_if_zero_observed"],.15)

    def test_invalid_label_denominator_is_rejected(self):
        self.labels["gloss_overclaim_unclear"]["v3"]=9
        with self.assertRaisesRegex(ValueError,"denominators"):
            summarize(self.labels,self.coh)

    def test_no_claim_of_independent_semantics_is_accepted(self):
        self.coh["independent_full_paper_entailment_verified"]=True
        with self.assertRaisesRegex(ValueError,"claims"):
            summarize(self.labels,self.coh)

    def test_inconsistent_year_coverage_is_rejected(self):
        self.coh["by_year"]["2022"]["evaluable_pairs"]=7
        with self.assertRaisesRegex(ValueError,"Yearly"):
            summarize(self.labels,self.coh)


if __name__ == "__main__":
    unittest.main()
