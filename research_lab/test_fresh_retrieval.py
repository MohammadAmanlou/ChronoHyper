"""Synthetic regression checks: freeze, privacy, leakage, paired gold scoring."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research_lab import fresh_retrieval as fresh
from research_lab import retrieval_frontier as frontier

class FreshBenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.folder=self.root/"local_only/fresh_retrieval"
        self.folder.mkdir(parents=True)
        self.kit=[
            {"question_id":"F001","target_name":"Equivariant Graph Networks",
             "target_type":"method","paper_title":"Geometry and molecular potentials","paper_year":"2023"},
            {"question_id":"F002","target_name":"Neural Crystal Optimization",
             "target_type":"technique","paper_title":"Lattice dynamics paper","paper_year":"2024"}
        ]
        fresh._write_csv(self.folder/"AUTHOR_KIT.csv",fresh.AUTHOR_FIELDS,self.kit)
        self.answer=[]
        for k in self.kit:
            r=dict(k)
            r.update(question=(
                "Which geometrically constrained model is discussed for modeling "
                "atomic forces from crystal structures, without naming the model?"
                if k["question_id"]=="F001" else
                "Which computational approach models lattice energy changes "
                "while optimizing parameters based on physical priors?"),
                source_url="https://arxiv.org/abs/2401.12345",
                evidence_locator="Page 3 methods section",
                evidence_access="FULL_TEXT",author_id="TEST_AI_FIXTURE",
                question_rationale="The evidence identifies the target without repeating its name.")
            self.answer.append(r)
        fresh._write_csv(self.folder/"returned.csv",fresh.RETURN_FIELDS,self.answer)
    def tearDown(self):self.temp.cleanup()

    def _freeze(self):
        with patch.object(fresh,"questions",return_value=[
                {"question_id":"Q1","question":"A historical unrelated question?"}]):
            return fresh.freeze(self.root,response=str(self.folder/"returned.csv"))

    def test_neutral_freeze_and_hash_integrity(self):
        result=self._freeze()
        self.assertTrue(result["frozen_before_rank"])
        self.assertEqual(result["predeclared_primary_route_roots"],4)
        self.assertEqual(fresh._read_manifest(self.root,self.folder),result)
        with self.assertRaises(FileExistsError):self._freeze()
        (self.folder/"gold_PRIVATE.csv").write_text("tampered",encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"changed"):
            fresh._read_manifest(self.root,self.folder)

    def test_leaked_target_name_is_blocked(self):
        self.answer[0]["question"]="Which details distinguish Equivariant Graph Networks from ordinary models in recent research?"
        (self.folder/"returned.csv").unlink()
        fresh._write_csv(self.folder/"returned.csv",fresh.RETURN_FIELDS,self.answer)
        with patch.object(fresh,"questions",return_value=[]):
            with self.assertRaisesRegex(ValueError,"leaks"):
                fresh.freeze(self.root,response=str(self.folder/"returned.csv"))

    def test_recycled_original_query_is_blocked(self):
        q=self.answer[0]["question"]
        with patch.object(fresh,"questions",return_value=[{"question_id":"old","question":q}]):
            with self.assertRaisesRegex(ValueError,"previously inspected"):
                fresh.freeze(self.root,response=str(self.folder/"returned.csv"))

    def test_gold_score_exact_type_and_immutable_ranking(self):
        self._freeze()
        def top(name,typ):
            return [{"name":name,"normalized":fresh.norm(name),"type":typ,"score":0.8}]
        def case(id):
            item={"question_id":id,"type":"A",
                  "flat":{"top5":[top("Equivariant Graph Networks","dataset")[0] if id=="F001"
                                  else top("Neural Crystal Optimization","technique")[0]],
                          "candidates_scored":100,"median_online_ms_including_top5":4.0},
                  "routes":{}}
            for budget in (1,2,4,12):
                item["routes"][str(budget)]={
                  "top5":[top("Equivariant Graph Networks","method")[0]
                          if id=="F001" and budget==4 else
                          item["flat"]["top5"][0]],
                  "candidates_scored":100 if budget==12 else budget*7,
                  "centroid_scores":12,
                  "median_online_ms_including_routing_and_top5":2.0}
            return item
        rows=[case("F001"),case("F002")]
        rank={
          "schema":"chronohyper_gold_separated_budget_frontier_v1",
          "evaluation_stage":"NEW_QUERY_PROVENANCE_NOT_VERIFIED",
          "gold_accessed_by_ranker":False,
          "full_root_exactness_asserted":True,
          "budgets":[1,2,4,12],
          "results":rows}
        rank["ranking_sha256"]=frontier._rank_hash(rank)
        (self.folder/"rankings.json").write_text(json.dumps(rank),encoding="utf-8")
        result=fresh.score(self.root)
        self.assertEqual(result["n_queries"],2)
        self.assertEqual(result["per_arm"]["flat"]["hit_at_5"],.5)
        self.assertEqual(result["per_arm"]["route_4"]["hit_at_5"],1.)
        self.assertEqual(result["descriptive_paired_contrasts"]["route_4"]["wins"],1)
        self.assertFalse(result["source_corpus_external_to_original"])
        with self.assertRaises(FileExistsError):fresh.score(self.root)

    def test_bad_extra_gold_missing_is_fatal(self):
        self._freeze()
        gold=self.folder/"gold_PRIVATE.csv"
        gold.unlink()
        fresh._write_csv(gold,fresh.GOLD_FIELDS,[{"question_id":"F001",
              "target_type":"method","target_name":"Equivariant Graph Networks"}])
        with self.assertRaisesRegex(ValueError,"changed"):
            fresh._read_manifest(self.root,self.folder)

if __name__=="__main__":unittest.main()
