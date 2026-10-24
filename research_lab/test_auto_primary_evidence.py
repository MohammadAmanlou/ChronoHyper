"""Network-free synthetic tests for automated source discovery and passage retrieval."""
import unittest
from research_lab import auto_primary_evidence as a

class AutoPrimaryEvidenceTests(unittest.TestCase):
    def test_historical_arxiv_id(self):
        self.assertEqual(a._arxiv_id("https://arxiv.org/abs/1704.01212"),"1704.01212")
        self.assertEqual(a._arxiv_id("https://arxiv.org/pdf/1704.01212v1.pdf"),"1704.01212")
        self.assertIsNone(a._arxiv_id("https://doi.org/10.1007/abcdef"))

    def test_source_candidate_from_arxiv_is_first_version(self):
        item={"paper_title":"Neural Message Passing for Quantum Chemistry",
              "paper_year":"2017",
              "source_url":"https://arxiv.org/abs/1704.01212"}
        c=a._paper_candidates(item,offline=True)
        self.assertEqual(c[0][0],"https://arxiv.org/pdf/1704.01212v1")
        self.assertEqual(c[0][1],"arxiv_v1")

    def test_rank_passage_uses_question_terms_not_invented_summary(self):
        pages=[(1,"The introduction presents unrelated sentences about generic progress in computer systems. "*12),
               (2,"We demonstrate crystalline graph convolution neural network predictions of material properties. "*12)]
        found=a._rank_passage(pages,
             "Crystal graph neural network material properties")
        self.assertEqual(found["page"],2)
        self.assertGreater(found["score"],0.25)
        self.assertIn("graph convolution",found["passage"])

    def test_empty_page_has_no_science_candidate(self):
        self.assertIsNone(a._rank_passage([(1,"Unrelated prose. "*40)],
                                          "quantum molecular diffusion"))

    def test_never_accept_html_as_pdf(self):
        with self.assertRaisesRegex(ValueError,"Not a PDF"):
            a._pdf_text(b"<html><body>not a primary PDF</body></html>")

    def test_no_network_from_offline_openalex(self):
        self.assertEqual(a._openalex_candidate("Scientific source",2020,offline=True),[])

if __name__=="__main__":
    unittest.main()
