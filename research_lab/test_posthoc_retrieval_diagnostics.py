"""Synthetic, 34-item regression for read-only pretrained retriever diagnostics."""
import copy
import unittest

from research_lab.posthoc_retrieval_diagnostics import assess, allocate, identity_match
from research_lab.retrieval_frontier import _rank_hash

def _entry(i, n, ok):
    if ok:
        name=f"Gold {i}"
        normalized=f"gold{i}"
    else:
        name=f"Distractor {i} {n}"
        normalized=f"distractor{i}{n}"
    return {"name":name,"normalized":normalized,"type":"method","score":1.0-n/30}

def fixture():
    rows=[]
    gold=[]
    for i in range(34):
        qid=f"F{i+1:03d}"
        gold.append({"question_id":qid,"target_name":f"Gold {i}",
                     "target_type":"method"})
        retrieval={}
        for arm in ("lexical","dense","hybrid_rrf","hybrid_rerank","soft_hierarchy"):
            correct={
                "lexical":i<4,
                "dense":i<10,
                "hybrid_rrf":i<6,
                "hybrid_rerank":i==15,
                "soft_hierarchy":i==15,
            }[arm]
            loc=2 if correct else -1
            retrieval[arm]=[_entry(i,j,j==loc) for j in range(20)]
        rows.append({"question_id":qid,"retrieval":retrieval})
    rank={"schema":"chronohyper_new_hybrid_rerank_development_v1",
          "stage":"POSTHOC_AFTER_VIEWING_ORIGINAL_34_SCORE_DEVELOPMENT_ONLY",
          "gold_accessed_during_ranking":False,
          "rankings":rows}
    rank["ranking_sha256"]=_rank_hash(rank)
    old={"per_question_local_only":[
        {"question_id":f"F{i+1:03d}",
         "scores":{"flat":{"hit5":int(i<3)}}} for i in range(34)]}
    return rank,gold,old

class PostHocDiagnostics(unittest.TestCase):
    def test_report_matches_34_and_no_accidental_accuracy_claim(self):
        rank,gold,old=fixture()
        summary,detail=assess(rank,gold,old)
        self.assertEqual(summary["arm_hit5"]["dense"],10)
        self.assertEqual(summary["arm_hit5"]["hybrid_rerank"],1)
        self.assertEqual(summary["arm_hit5"]["hybrid_rrf"],6)
        self.assertEqual(summary["descriptive_dense_vs_frozen_flat"]["flat_legacy_hits"],3)
        self.assertEqual(len(detail),34)
        self.assertFalse(summary["rerank_candidate64_recall_measurable_from_top20"])
        self.assertEqual(summary["diagnostic"]["dense_hit_lost_in_rerank_top5"],10)

    def test_reject_modified_rank_artifact(self):
        rank,gold,old=fixture()
        rank["rankings"][0]["retrieval"]["dense"][0]["name"]="Changed"
        with self.assertRaisesRegex(ValueError,"SHA-256"):
            assess(rank,gold,old)

    def test_gold_ids_must_match_exactly(self):
        rank,gold,old=fixture()
        with self.assertRaisesRegex(ValueError,"Exact 34-query"):
            assess(rank,gold[:-1],old)

    def test_policy_allocations_not_oracle_and_deduplicated(self):
        rank,_,_=fixture()
        p=allocate(rank["rankings"][0]["retrieval"],
                   (("dense",3),("lexical",2)))
        self.assertEqual(len(p),5)
        self.assertEqual(len(set((x["type"],x["normalized"]) for x in p)),5)
        self.assertEqual(identity_match(p,("method","gold0")),3)

    def test_unchanged_data_does_not_raise(self):
        rank,gold,old=fixture()
        self.assertEqual(assess(copy.deepcopy(rank),gold,old)[0]["n_queries"],34)

if __name__=="__main__": unittest.main()
