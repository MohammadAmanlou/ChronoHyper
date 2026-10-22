"""Synthetic-only checks that frozen 34-query negative results aren't misrepresented."""
import copy
import unittest
from research_lab.fresh_score_audit import analyze,exact_sign_test
from research_lab.retrieval_frontier import _rank_hash

class NewQuestionAuditTests(unittest.TestCase):
    def dataset(self):
        manifest={"stage":"SAME_CORPUS_PROSPECTIVE_QUESTION_SET_NOT_EXTERNAL",
                  "frozen_before_rank":True,"predeclared_primary_route_roots":4,
                  "n_queries":34,"query_sha256":"querysha","gold_sha256":"goldsha"}
        screen={"schema":"chronohyper_prerank_source_screen_v1",
                "n_attempted":36,"n_documented_excluded":2,
                "n_eligible_format":34,"validation_errors":[],
                "excluded":[{"question_id":"F023"},{"question_id":"F031"}]}
        ranked=[]
        scored_rows=[]
        for idx in range(34):
            qid=f"F{idx+1:03}"
            hits_flat=idx<3
            hits_route=idx<2
            def top(eligible):
                return ([{"normalized":"target","type":"method"}]
                        if eligible else [{"normalized":"not_target","type":"method"}])
            flat={"top5":top(hits_flat),"candidates_scored":2647,
                  "median_online_ms_including_top5":7.2}
            route4={"top5":top(hits_route),"candidates_scored":1064,
                    "centroid_scores":12,
                    "median_online_ms_including_routing_and_top5":6.2}
            route12={"top5":copy.deepcopy(flat["top5"]),"candidates_scored":2647,
                     "centroid_scores":12,
                     "median_online_ms_including_routing_and_top5":9.0}
            ranked.append({"question_id":qid,"flat":flat,
                           "routes":{"4":route4,"12":route12}})
            def mark(hit,cost):
                return {"hit5":int(hit),"mrr5":1.0 if hit else 0.0,
                        "rank":1 if hit else None,"cost":cost}
            scored_rows.append({"question_id":qid,
                                "scores":{"flat":mark(hits_flat,2647),
                                          "route_4":mark(hits_route,1076)}})
        rank={"schema":"chronohyper_gold_separated_budget_frontier_v1",
              "gold_accessed_by_ranker":False,
              "full_root_exactness_asserted":True,
              "cutoff":2025,"budgets":[4,12],"results":ranked}
        rank["ranking_sha256"]=_rank_hash(rank)
        score={"n_queries":34,"primary_predeclared_route":"route_4",
               "rankings_sha256_verified":rank["ranking_sha256"],
               "source_corpus_external_to_original":False,
               "questions_sha256":"querysha","gold_sha256":"goldsha",
               "all_root_exactness_verified":True,
               "per_question_local_only":scored_rows,
               "descriptive_paired_contrasts":{"route_4":{
                   "wins":0,"losses":1,"ties":33,
                   "paired_hit_at_5_difference":-1/34,
                   "exploratory_paired_bootstrap_95ci":[-3/34,0]}},
               "per_arm":{"flat":{"mean_online_dot_products":2647},
                          "route_4":{"mean_online_dot_products":1076}}}
        return manifest,screen,rank,score

    def test_negative_result_exactly_preserved(self):
        result=analyze(*self.dataset())
        self.assertEqual(result["flat_hit_n"],3)
        self.assertEqual(result["route4_hit_n"],2)
        self.assertEqual(result["paired_losses_route"],1)
        self.assertEqual(result["paired_exact_sign_p_descriptive"],1.0)
        self.assertFalse(result["externally_independent_source_corpus"])
        self.assertGreater(result["online_dot_product_reduction_fraction"],.59)

    def test_changed_rankings_rejected(self):
        inputs=list(self.dataset())
        inputs[2]["results"][2]["flat"]["top5"][0]["normalized"]="tamp"
        with self.assertRaisesRegex(ValueError,"modified"):
            analyze(*inputs)

    def test_changed_denominator_rejected(self):
        inputs=list(self.dataset())
        inputs[1]["n_eligible_format"]=36
        with self.assertRaisesRegex(ValueError,"34"):
            analyze(*inputs)

    def test_selected_result_cherry_picking_rejected(self):
        inputs=list(self.dataset())
        inputs[3]["descriptive_paired_contrasts"]["route_4"]["losses"]=0
        with self.assertRaisesRegex(ValueError,"Paired pattern"):
            analyze(*inputs)

    def test_sign_test_preserves_tiny_discordant_denominator(self):
        self.assertEqual(exact_sign_test(0,1),1.0)
        self.assertIsNone(exact_sign_test(0,0))

if __name__=="__main__":
    unittest.main()
