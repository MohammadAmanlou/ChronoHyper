"""Local evidence-gap audit tests, using invented blind IDs and no external data."""
import unittest
from research_lab import evidence_gap_audit as a


def sample():
    cases=[{"blind_id":"L%03d"%n,"snapshot_year":"2020"} for n in range(1,25)]
    passages=[
      {"blind_id":"L001","snapshot_year":"2020","date_status":a.DATED,
       "evidence_status":a.EXTRACTED},
      {"blind_id":"L002","snapshot_year":"2020","date_status":"UNVERIFIED",
       "evidence_status":a.EXTRACTED}]
    reviews=[
      {"blind_id":c["blind_id"],"snapshot_year":"2020",
       "evidence_status":a.SCORED if c["blind_id"]=="L001" else a.NOT_SCORED,
       "evidence_sufficient_yes_no":"no"}
      for c in cases]
    return cases,passages,reviews


class EvidenceGapAuditTests(unittest.TestCase):
    def test_missing_source_and_dated_ai_insufficiency_are_distinct(self):
        cases,passages,reviews=sample()
        result=a.summarize(cases,passages,reviews)
        self.assertEqual(result["candidate_passages"],2)
        self.assertEqual(result["cases_with_dated_eligible_evidence"],1)
        self.assertEqual(result["cases_actually_scored_by_local_AI"],1)
        self.assertEqual(result["diagnoses"],{
          "DATED_EVIDENCE_AI_SAYS_INSUFFICIENT":1,
          "CANDIDATES_PRESENT_BUT_NOT_DATE_ELIGIBLE":1,
          "NO_SOURCE_CANDIDATES_FOR_CASE":22})
        self.assertEqual(result["scientific_overclaim_rate"],"NOT_EVALUATED")

    def test_reject_unfounded_model_evaluation(self):
        cases,passages,reviews=sample()
        reviews[1]["evidence_status"]=a.SCORED
        with self.assertRaisesRegex(ValueError,"mismatch"):
            a.summarize(cases,passages,reviews)

    def test_reject_unfounded_sufficiency(self):
        cases,passages,reviews=sample()
        reviews[2]["evidence_sufficient_yes_no"]="yes"
        with self.assertRaisesRegex(ValueError,"Unscored"):
            a.summarize(cases,passages,reviews)

    def test_reject_duplicates(self):
        cases,passages,reviews=sample()
        reviews[2]["blind_id"]="L001"
        with self.assertRaises(ValueError):
            a.summarize(cases,passages,reviews)

    def test_crosscheck_existing_summary(self):
        cases,passages,reviews=sample()
        with self.assertRaisesRegex(ValueError,"disagrees"):
            a.summarize(cases,passages,reviews,summary={
              "blind_case_count":24,"sufficient_cases":10})


if __name__=="__main__":
    unittest.main()
