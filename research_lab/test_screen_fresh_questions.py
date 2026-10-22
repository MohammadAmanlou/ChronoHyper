"""No-corpus fixture checks for prospective 36-target screening and disclosure."""
import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from research_lab.fresh_retrieval import AUTHOR_FIELDS,RETURN_FIELDS,_write_csv
from research_lab import screen_fresh_questions as screened

class ScreenFreshTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        folder=self.root/"local_only/fresh_retrieval"
        folder.mkdir(parents=True)
        self.source=folder/"FRESH_QUESTIONS_FROM_AI.csv"
        self.rows=[]
        for n in range(1,37):
            row={"question_id":f"F{n:03}",
                 "target_name":f"Scientific Method {n}",
                 "target_type":"method",
                 "paper_title":f"Published Materials Study {n}",
                 "paper_year":"2025",
                 "question":f"In source paper number {n}, which scientific procedure analyzes a physical property without a named algorithm?",
                 "source_url":"https://arxiv.org/abs/2501.00123",
                 "evidence_locator":"Page 3, experiment section",
                 "evidence_access":"FULL_TEXT",
                 "author_id":"TEST_GPT",
                 "question_rationale":"Synthetic evidence rationale for source and target identity"}
            if n in (23,31):
                row.update(question="",source_url="",evidence_access="",
                           evidence_locator="SUPPORT FAILURE: exact source unverified",
                           question_rationale="UNSUPPORTED SOURCE: Original listed paper cannot be independently authenticated")
            self.rows.append(row)
        self.original=folder/"AUTHOR_KIT.csv"
        _write_csv(self.original,AUTHOR_FIELDS,
                   [{k:r[k] for k in AUTHOR_FIELDS} for r in self.rows])
        _write_csv(self.source,RETURN_FIELDS,self.rows)
        self.patcher=patch.object(screened,"questions",return_value=[
            {"question_id":"old","question":"What is the weather like in Mars?"}])
        self.patcher.start()
    def tearDown(self):
        self.patcher.stop()
        self.tmp.cleanup()
    def test_report_preserves_36_and_two_unsupported(self):
        result,valid=screened.audit(self.root)
        self.assertEqual(result["n_attempted"],36)
        self.assertEqual(result["n_eligible_format"],34)
        self.assertEqual(result["n_documented_excluded"],2)
        self.assertEqual(result["validation_errors"],[])
        self.assertEqual([x["question_id"] for x in result["excluded"]],["F023","F031"])
    def test_modified_source_association_is_detected(self):
        self.rows[4]["paper_title"]="Replaced paper"
        self.source.unlink()
        _write_csv(self.source,RETURN_FIELDS,self.rows)
        result,_=screened.audit(self.root)
        self.assertTrue(any("F005" in x and "changed" in x for x in result["validation_errors"]))
    def test_invalid_third_case_is_not_silently_filtered(self):
        self.rows[6]["question"]="Bad?"
        self.source.unlink()
        _write_csv(self.source,RETURN_FIELDS,self.rows)
        result,_=screened.audit(self.root)
        self.assertTrue(any("F007" in x for x in result["validation_errors"]))
        self.assertEqual(result["n_eligible_format"],33)
    def test_exclusion_requires_explicit_reason_and_blank_fields(self):
        self.rows[22]["evidence_locator"]="not sure"
        self.source.unlink()
        _write_csv(self.source,RETURN_FIELDS,self.rows)
        result,_=screened.audit(self.root)
        self.assertEqual(result["n_documented_excluded"],1)
        self.assertTrue(any("F023" in x for x in result["validation_errors"]))

if __name__=="__main__":unittest.main()
