"""Offline synthetic tests for a non-confirmatory 34-query source union audit."""
from __future__ import annotations

import copy
import json
import unittest
from research_lab import multiview_source_union_audit as diag
from research_lab.retrieval_frontier import _rank_hash


def fixture():
    rows, ranks = [], {}
    for i in range(34):
        qid=f"F{i+1:03d}"
        target=("method",f"gold{i}")
        views={}
        ranks[qid]={}
        for arm in diag.ARMS:
            items=[{
                "name":f"Nonmatch {i} {arm} {k}",
                "type":"method",
                "normalized":f"nonmatch{i}{arm}{k}",
                "rank":k+1,
            } for k in range(100)]
            pos=None
            if i<10 and arm=="context":
                pos=1
            elif 10<=i<20 and arm=="paper":
                pos=80
            elif 20<=i<30 and arm=="name":
                pos=80
            if pos is not None:
                items[pos-1]={"name":f"Gold {i}","type":"method",
                              "normalized":target[1],"rank":pos}
            views[arm]=items
            ranks[qid][arm]=pos
        rows.append({"question_id":qid,"views":views})
    artifact={"schema":"chronohyper_multiview_bge_development_v1",
              "stage":"POSTHOC_ALREADY_VIEWED_34_NOT_CONFIRMATORY",
              "gold_accessed_during_ranking":False,
              "arms":list(diag.ARMS),"candidate_export_depth":100,
              "results":rows}
    artifact["ranking_sha256"]=_rank_hash(artifact)
    expected={
        a:{"hit_at_"+str(k):
           sum(v[a] is not None and v[a]<=k for v in ranks.values())
           for k in diag.KS}
        for a in diag.ARMS
    }
    scores={
        "schema":"chronohyper_multiview_bge_scored_development_v1",
        "not_a_new_unseen_test":True,
        "rankings_sha256_verified":artifact["ranking_sha256"],
        "correct_at_k_counts":expected,
        "per_question_rank_LOCAL_PRIVATE":ranks,
    }
    return artifact,scores


class MultiViewSourceUnionAuditTest(unittest.TestCase):
    def test_oracle_and_gold_blind_pool_are_distinct(self):
        ranks,scores=fixture()
        out=diag.analyze(ranks,scores)
        self.assertEqual(out["n_questions"],34)
        self.assertEqual(out["missing_from_all_count"],4)
        self.assertEqual(out["best_of_five_oracle_visible_at_k_NOT_AN_ALGORITHM"]["5"],10)
        self.assertEqual(out["best_of_five_oracle_visible_at_k_NOT_AN_ALGORITHM"]["100"],30)
        self.assertEqual(out["fixed_gold_blind_3view_round_robin_pool_RECALL_upper_k"]["300"],30)
        self.assertEqual(out["fixed_pool_300_mean_actual_size"],300)
        self.assertTrue(out["no_original_gold_file_opened"])

    def test_reject_modified_ranking(self):
        ranks,scores=fixture()
        ranks["results"][1]["views"]["paper"][0]["name"]="Tampered"
        with self.assertRaisesRegex(ValueError,"SHA-256"):
            diag.analyze(ranks,scores)

    def test_reject_mismatched_scores(self):
        ranks,scores=fixture()
        scores["correct_at_k_counts"]["context"]["hit_at_5"]=0
        with self.assertRaisesRegex(ValueError,"internally inconsistent"):
            diag.analyze(ranks,scores)

    def test_reject_gold_disagreement_between_views(self):
        ranks,scores=fixture()
        # Q1 source context points to its true entity. Make Name
        # reference another distinct entity while keeping all
        # summary counts mathematically consistent.
        qid="F001"
        scores["per_question_rank_LOCAL_PRIVATE"][qid]["name"]=10
        scores["correct_at_k_counts"]["name"]["hit_at_10"]=1
        scores["correct_at_k_counts"]["name"]["hit_at_20"]=1
        scores["correct_at_k_counts"]["name"]["hit_at_50"]=1
        scores["correct_at_k_counts"]["name"]["hit_at_100"]=11
        with self.assertRaisesRegex(ValueError,"one typed canonical entity"):
            diag.analyze(ranks,scores)

    def test_no_accidental_acceptance_of_partial_data(self):
        ranks,scores=fixture()
        del scores["per_question_rank_LOCAL_PRIVATE"]["F001"]
        with self.assertRaisesRegex(ValueError,"Exact original 34"):
            diag.analyze(ranks,scores)


if __name__=="__main__":
    unittest.main()
