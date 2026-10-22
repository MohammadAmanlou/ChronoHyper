"""CPU-only synthetic regression tests; no pretrained model downloads in CI."""
import json,tempfile,unittest
from pathlib import Path
from zipfile import ZipFile
from unittest.mock import patch
import numpy as np
from research_lab import advanced_retrieval as mod

class FakeReranker:
    def predict(self,pairs,batch_size=16,show_progress_bar=False):
        return np.array([10 if "alpha" in document else 0 for _,document in pairs])

class AdvancedRetrievalTests(unittest.TestCase):
    def setUp(self):
        self.entries=[
            {"name":"Alpha Mechanism","normalized":"alphamechanism","type":"method",
             "text":"Alpha Mechanism Scientific Material Paper","node_ids":["n1"]},
            {"name":"Beta Dataset","normalized":"betadataset","type":"dataset",
             "text":"Beta Dataset Crystal Materials Paper","node_ids":["n2"]},
            {"name":"Gamma Protocol","normalized":"gammaprotocol","type":"technique",
             "text":"Gamma Protocol Elastic Potential Paper","node_ids":["n3"]}
        ]
    def test_rrf_is_deterministic_and_consensus_improves_rank(self):
        out=mod.reciprocal_fusion([[0,1,2],[2,0,1]])
        self.assertEqual(out[0],0)
        self.assertEqual(len(out),3)
    def test_rerank_promotes_semantic_candidate(self):
        texts=["alpha physical explanation","beta physical","gamma physical"]
        obj=mod.retrieval_query("explain an unknown concept",
            np.array([0.1,0.8,0.3]),np.array([0.2,0.6,0.7]),
            texts,self.entries,FakeReranker(),candidate_k=3,rerank_k=3)
        self.assertEqual(obj["hybrid_rerank"][0]["normalized"],"alphamechanism")
        self.assertEqual(len(obj["hybrid_rrf"]),3)
    def test_native_hyperedge_context_is_only_co_mentions_and_cutoff_safe(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)/"inputs";folder.mkdir()
            g={"nodes":[{"id":"n1","type":"method","surface_form":"Alpha Mechanism","first_seen_year":2020},
                        {"id":"n2","type":"dataset","surface_form":"Beta Dataset","first_seen_year":2020},
                        {"id":"n3","type":"technique","surface_form":"Future Secret","first_seen_year":2026}],
               "hyperedges":[{"id":"e1","members":["n1","n2"],"relation_type":"mentions",
                              "year":2024,"provenance":{"article_year":2024}},
                             {"id":"e2","members":["n1","n3"],"relation_type":"mentions",
                              "year":2026,"provenance":{"article_year":2026}}]}
            with ZipFile(folder/"data.zip","w") as zipf:
                zipf.writestr("data/tkh_collection10.json",json.dumps(g))
            s=mod.native_context(td,self.entries)
            self.assertIn("Beta Dataset",s[0])
            self.assertNotIn("Future Secret",s[0])
            self.assertIn("NOT proven semantic relations",s[0])
    def test_score_must_never_read_gold_in_ranking(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"local_only"/"query.csv";p.parent.mkdir()
            p.write_text("question_id,question\nQ1,What is alpha?",encoding="utf-8")
            with patch.object(mod,"old_index",side_effect=ValueError("missing index")):
                with self.assertRaisesRegex(ValueError,"missing index"):
                    mod.rank(td,questions=str(p),out=str(Path(td)/"out"),device="cpu")
                self.assertFalse((Path(td)/"out"/"rankings.json").exists())

if __name__=="__main__":unittest.main()
