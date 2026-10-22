"""CPU synthetic regression only, no Hugging Face model download."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
import numpy as np
from unittest.mock import patch

from research_lab import qwen_entity_rerank as q

def record(i):
    return {"type":"method","name":f"Entity {i}","normalized":f"entity{i}","rank":i+1}

class QwenEntityRerankTests(unittest.TestCase):
    def test_union_includes_non_context_sources_without_gold(self):
        ctx=[record(i) for i in range(100)]
        paper=[record(i+100) for i in range(100)]
        rrf=[record(i+200) for i in range(100)]
        name=[record(i+300) for i in range(100)]
        maximum=[record(i+400) for i in range(100)]
        views={"context":ctx,"paper":paper,"rrf_3view":rrf,
               "name":name,"max_cosine_3view":maximum}
        pool=q.candidates(views,300)
        self.assertEqual(len(pool),300)
        self.assertIn(("method","entity100"),[q.key(i) for i in pool])
        self.assertIn(("method","entity300"),[q.key(i) for i in pool])
        self.assertEqual(len(set(q.key(i) for i in pool)),300)

    def test_tie_breaking_is_stable_and_pinned_docs_are_unique(self):
        items=[record(0),record(1),record(2),record(3)]
        ordered=q.order_candidates(items,[3.0,4.0,4.0,1.0])
        self.assertEqual([r["name"] for r in ordered][:2],["Entity 1","Entity 2"])
        pinned=q.anchored(ordered,[items[3],items[0]],2)
        self.assertEqual([r["name"] for r in pinned][:2],["Entity 3","Entity 0"])
        self.assertEqual(len({q.key(i) for i in pinned}),4)
        with self.assertRaisesRegex(ValueError,"non-finite"):
            q.order_candidates(items,[1,np.nan,1,1])

    def test_reject_unknown_model_gold_and_inconsistent_source(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            folder=root/"local_only/multiview_dense_development"
            folder.mkdir(parents=True)
            raw={"schema":"chronohyper_multiview_bge_development_v1",
                 "stage":"POSTHOC_ALREADY_VIEWED_34_NOT_CONFIRMATORY",
                 "gold_accessed_during_ranking":False,
                 "candidate_export_depth":100,
                 "query_file_sha256":"mismatch",
                 "results":[]}
            raw["ranking_sha256"]=q._rank_hash(raw)
            (folder/"rankings.json").write_text(json.dumps(raw))
            with self.assertRaisesRegex(ValueError,"SHA differs"):
                q.read_rankings(root)

    def test_doc_is_typed_and_explicitly_not_proven_relations(self):
        entries=[{"name":"Boron Potential","type":"method",
                  "normalized":"boronpotential",
                  "text":"Boron Potential "*3+"method Boron study 2024"}]
        d=q.make_docs(entries,["Scientific entity: Boron Potential; "
                  "Co-mentioned graph entities (NOT proven semantic relations): Carbon"])
        self.assertIn("Boron study 2024",d[("method","boronpotential")])
        self.assertIn("not verified claims",d[("method","boronpotential")])

    def test_scorer_rejects_tampered_rankings_without_reading_gold(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"local_only/qwen_entity_rerank_development"
            p.mkdir(parents=True)
            artifact={"schema":"chronohyper_qwen_entity_rerank_development_v1",
                      "stage":"POSTHOC_ALREADY_INSPECTED_34_NOT_CONFIRMATORY",
                      "gold_read_during_rank":False,"source_multiview_sha":"test",
                      "results":[]}
            artifact["ranking_sha256"]=q._rank_hash(artifact)
            artifact["results"].append({"question_id":"TAMPER"})
            (p/"rankings.json").write_text(json.dumps(artifact))
            with self.assertRaisesRegex(ValueError,"digest mismatch"):
                q.score(td,gold="DO_NOT_READ_GOLD.csv")

if __name__=="__main__":unittest.main()
