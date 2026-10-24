"""Offline checks of the local-only, source-gated AI research review."""
import unittest
from research_lab import auto_label_judge as j

def sample():
    return {"blind_id":"L001","snapshot_year":"2020",
            "member_names":"Crystal Graph Neural Network",
            "label_A":"Graph materials",
            "label_B":"Materials predictions",
            "gloss_A":"A materials science graph theme.",
            "gloss_B":"Learning crystal properties."}

def evidence(date="ARXIV_V1_WITHIN_CUTOFF"):
    return [{"paper_id":"9","paper_title":"Materials science example",
             "date_status":date,
             "evidence_status":"AUTO_RETRIEVED_UNVERIFIED_NOT_REVIEWED",
             "source_version_date":"2019-10-01",
             "passage_locator":"PDF page 3 (machine extracted)",
             "versioned_source_url":"https://arxiv.org/pdf/1903.01001v1",
             "passage_text":"A real retrieved quotation would appear here.",
             "match_score":"0.9"}]

class AutoJudgeTests(unittest.TestCase):
    def test_requires_historical_source_gate(self):
        prompt,src=j._case_prompt(sample(),evidence("UNVERIFIED"))
        self.assertIsNone(prompt)
        self.assertEqual(src,[])

    def test_blind_arms_and_papers_passed_without_private_mapping(self):
        prompt,src=j._case_prompt(sample(),evidence())
        self.assertEqual(len(src),1)
        self.assertIn("A TITLE:",prompt)
        self.assertIn("B TITLE:",prompt)
        self.assertNotIn("mapping_PRIVATE",prompt)

    def test_insufficient_source_does_not_create_scientific_score(self):
        row=j._no_evidence(sample(),"Historical passage missing")
        self.assertEqual(row["evidence_sufficient_yes_no"],"no")
        self.assertEqual(row["A_accuracy_accurate_vague_wrong"],"")
        self.assertEqual(row["B_gloss_overclaim_yes_no_unclear"],"unclear")

    def test_model_insufficient_cannot_force_positive_grade(self):
        response={"evidence_sufficient_yes_no":"no",
                  "A_accuracy_accurate_vague_wrong":"accurate",
                  "B_accuracy_accurate_vague_wrong":"accurate",
                  "A_gloss_overclaim_yes_no_unclear":"no",
                  "B_gloss_overclaim_yes_no_unclear":"no",
                  "review_notes":"The cited passage does not establish the scientific claim."}
        r=j._parse(sample(),response,"local-test",["9:page3"])
        self.assertEqual(r["A_accuracy_accurate_vague_wrong"],"")
        self.assertEqual(r["A_gloss_overclaim_yes_no_unclear"],"unclear")

    def test_refuses_remote_text_upload(self):
        with self.assertRaisesRegex(ValueError,"Local-only"):
            j._post_local("https://example.com/api/generate",{})

if __name__=="__main__":
    unittest.main()
