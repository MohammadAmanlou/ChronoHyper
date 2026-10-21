"""Synthetic, data-free verification of sanitized 36-claim AI handoff."""
import csv,tempfile,unittest
from pathlib import Path
from research_lab.type_b_independent_handoff import BASE,PACKET,MERGED,COLS,prepare,merge,read,write

class TypeBIndependentHandoffTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.root=Path(self.t.name)
        data=self.root/BASE
        data.parent.mkdir(parents=True)
        self.headers=list(COLS)+["reference_coverage_flag","gold_eligible_source_ids",
                                 "flat_top5_has_gold_source","hier_top5_has_gold_source"]
        rows=[]
        for i in range(36):
            r={k:"" for k in self.headers}
            r.update(question_id="Q15",claim_id=f"Q15.C{i+1}",required_claim=f"Evidence claim {i+1}",
                     reference_coverage_flag="full",gold_eligible_source_ids="SECRET")
            rows.append(r)
        write(data,self.headers,rows)
    def tearDown(self):self.t.cleanup()
    def test_prepare_excludes_gold_and_earlier_hints(self):
        out=prepare(self.root)
        h,rows=read(out)
        self.assertEqual(h,list(COLS))
        self.assertEqual(len(rows),36)
        self.assertNotIn("SECRET",out.read_text(encoding="utf-8"))
        self.assertEqual(prepare(self.root),out)
    def test_merge_preserves_original_claims_and_coverage(self):
        out=prepare(self.root)
        h,rows=read(out)
        for r in rows:
            r["manual_claim_supported_yes_no_unclear"]="unclear"
            r["manual_source_citation_verified_yes_no_unclear"]="unclear"
            r["human_reviewer"]="TEST_AI_MODEL_NOT_HUMAN"
            r["reviewer_notes"]="Original primary evidence not accessible."
        rating=self.root/"rating.csv"
        write(rating,h,rows)
        destination=merge(self.root,rating)
        headers,full=read(destination)
        self.assertEqual(headers,self.headers)
        self.assertEqual(full[0]["gold_eligible_source_ids"],"SECRET")
        self.assertEqual(full[0]["manual_claim_supported_yes_no_unclear"],"unclear")
        with self.assertRaises(FileExistsError):merge(self.root,rating)
    def test_changed_claim_is_rejected(self):
        packet=prepare(self.root)
        h,rows=read(packet)
        for r in rows:
            r["manual_claim_supported_yes_no_unclear"]="unclear"
            r["manual_source_citation_verified_yes_no_unclear"]="unclear"
            r["human_reviewer"]="TEST_AI"
            r["reviewer_notes"]="No full paper located at this time."
        rows[0]["required_claim"]="CHANGED"
        f=self.root/"rated.csv";write(f,h,rows)
        with self.assertRaisesRegex(ValueError,"edited"):merge(self.root,f)

if __name__=="__main__":unittest.main()
