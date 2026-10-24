"""Synthetic checks for source-date and evidence-sufficiency validation."""
import unittest
from research_lab import fulltext_label_audit as f

def citation():
    return {"blind_id":"L001","snapshot_year":"2024","paper_id":"10",
      "paper_title":"Sample publication","paper_year":"2023",
      "source_url":"","source_version_date":"","passage_locator":"",
      "passage_text":"","evidence_access":""}

def reviewed():
    r=citation()
    r.update({"source_url":"https://arxiv.org/abs/2310.00001",
       "source_version_date":"2024-08-01",
       "passage_locator":"Section 3.2, page 7",
       "passage_text":"The passage is a synthetic test string intended to validate the input "
                      "format, version metadata and separation between source evidence "
                      "and unexamined bibliographic titles. This sentence extends it.",
       "evidence_access":"FULL_TEXT_USER_INSPECTED"})
    return r

class FullTextLabelAuditTests(unittest.TestCase):
    def test_only_dated_original_sources(self):
        c={"blind_id":"L001","snapshot_year":"2024",
           "member_names":"Method One | Dataset Two"}
        nodes={"n1":{"type":"method","surface_form":"Method One",
              "first_seen_year":2022,"provenance":{"articles":["10","11"]}},
               "n2":{"type":"dataset","surface_form":"Dataset Two",
              "first_seen_year":2023,"provenance":{"articles":["10"]}}}
        papers={"10":{"id":"10","year":"2023","title":"Source ten"},
                "11":{"id":"11","year":"2025","title":"Source eleven"}}
        results=f._case_sources(c,{"stable_id":"S"},
                    {(2024,"S"):{"member_ids":["n1","n2"]}},nodes,papers)
        self.assertEqual([x["id"] for x in results],["10"])

    def test_usable_full_text(self):
        rows,missing=f._trusted_passages([reviewed()],[citation()])
        self.assertEqual(len(rows["L001"]),1)
        self.assertFalse(missing)

    def test_later_version_rejected(self):
        r=reviewed();r["source_version_date"]="2025-03-01"
        with self.assertRaises(ValueError):
            f._trusted_passages([r],[citation()])

    def test_title_only_rejected(self):
        r=reviewed();r["passage_text"]="Short text"
        with self.assertRaises(ValueError):
            f._trusted_passages([r],[citation()])

    def test_unavailable_sources_remain_unrated(self):
        row={k:"" for k in f.PAPER_FIELDS}
        row.update({"blind_id":"L001","snapshot_year":"2024",
                    "evidence_access":"UNAVAILABLE"})
        passages,missing=f._trusted_passages([row],[row])
        self.assertEqual(len(passages),0)
        self.assertEqual(missing["L001"],1)

    def test_wilson_intervals_respect_denominator(self):
        self.assertIsNone(f._wilson(0,0))
        self.assertEqual(f._wilson(0,12)[0],0)
        self.assertEqual(f._wilson(12,12)[1],1)

if __name__=="__main__":
    unittest.main()
