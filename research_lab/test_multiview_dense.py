"""Pure CPU/synthetic integrity tests for new source-grounded BGE multi-view study."""
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from research_lab import multiview_dense as mv
from research_lab.retrieval_frontier import _rank_hash

class MultiViewTests(unittest.TestCase):
    def test_source_views_do_not_invent_definitions(self):
        entries=[
            {"name":"Atomic Diffusion","type":"method",
             "text":"Atomic Diffusion Atomic Diffusion Atomic Diffusion method 2024 Material Paper"},
            {"name":"Material Dataset","type":"dataset",
             "text":"Material Dataset Material Dataset Material Dataset dataset "}
        ]
        ctx=["native co-mention context 1","native co-mention context 2"]
        out=mv.build_views(entries,ctx)
        self.assertEqual(out["context"],ctx)
        self.assertIn("2024 Material Paper",out["paper"][0])
        self.assertIn("No dated source title",out["paper"][1])
        self.assertNotIn("native",out["name"][0])

    def test_dense_views_and_rrf_are_deterministic(self):
        scores={"context":[.3,.9,.2],"name":[.8,.1,.2],"paper":[.9,.1,.2]}
        out=mv.three_view_orders(scores)
        self.assertEqual(out["context"][0],1)
        self.assertEqual(out["name"][0],0)
        self.assertEqual(out["paper"][0],0)
        self.assertEqual(out["max_cosine_3view"][0],0)
        self.assertEqual(len(out["rrf_3view"]),3)
        self.assertEqual(len(set(out["rrf_3view"])),3)

    def test_invalid_partial_scores_rejected(self):
        with self.assertRaises(ValueError):
            mv.three_view_orders({"context":[.3],"name":[.4],"paper":[.2,.5]})

    def _mock_ranks(self):
        ref=[]
        ranked=[]
        for idx in range(34):
            q=f"F{idx+1:03}"
            name=f"Test Entity {idx}"
            ref.append({"question_id":q,"target_type":"method","target_name":name})
            candidate=[
              {"type":"method","name":name,"normalized":mv.norm(name),"rank":1}
            ] + [{"type":"method","name":f"Wrong {i} {idx}",
                   "normalized":mv.norm(f"Wrong {i} {idx}"),"rank":i+2}
                  for i in range(99)]
            ranked.append({"question_id":q,"views":{arm:candidate
                              for arm in mv.ARMS}})
        raw={"schema":"chronohyper_multiview_bge_development_v1",
             "stage":"POSTHOC_ALREADY_VIEWED_34_NOT_CONFIRMATORY",
             "gold_accessed_during_ranking":False,
             "candidate_export_depth":100,"dense_model":"TEST",
             "query_file_sha256":"fixture_sha",
             "arms":list(mv.ARMS),"results":ranked}
        raw["ranking_sha256"]=_rank_hash(raw)
        return raw,ref

    def test_scoring_all_34_not_before_rank_and_readonly(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            folder=root/"local_only/multiview_dense_development"
            folder.mkdir(parents=True)
            ranking,ref=self._mock_ranks()
            (folder/"rankings.json").write_text(json.dumps(ranking))
            g=root/"gold.csv"
            with g.open("w",newline="",encoding="utf-8") as f:
                w=csv.DictWriter(f,fieldnames=("question_id","target_type","target_name"))
                w.writeheader();w.writerows(ref)
            q=root/"local_only/fresh_retrieval_screened34/queries_only.csv"
            q.parent.mkdir(parents=True)
            q.write_text("question_id,question\\nF001,Synthetic test?\\n")
            ranking["query_file_sha256"]=hashlib.sha256(q.read_bytes()).hexdigest()
            ranking["ranking_sha256"]=_rank_hash(ranking)
            (folder/"rankings.json").write_text(json.dumps(ranking))
            out=mv.score(root,gold=str(g))
            self.assertEqual(out["correct_at_k_counts"]["context"]["hit_at_5"],34)
            self.assertTrue(out["not_a_new_unseen_test"])
            with self.assertRaises(FileExistsError):mv.score(root,gold=str(g))

    def test_rank_tampering_detected_before_gold(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            folder=root/"local_only/multiview_dense_development"
            folder.mkdir(parents=True)
            ranking,_=self._mock_ranks()
            ranking["results"][0]["views"]["context"][0]["name"]="Tampered"
            (folder/"rankings.json").write_text(json.dumps(ranking))
            with self.assertRaisesRegex(ValueError,"digest changed"):
                mv.score(root,gold="DO_NOT_OPEN_GOLD.csv")

if __name__=="__main__":unittest.main()
