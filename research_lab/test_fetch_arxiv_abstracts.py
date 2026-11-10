"""Offline tests: no real network and never mutate original primary library."""
import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research_lab.fetch_arxiv_abstracts import (
    ARCHIVE_DIR, collect, parse_arxiv_abstract, source_candidates,
)


def fake_page(date="27 Oct 2017"):
    return (
        '<html><body>'
        '<div class="dateline">[Submitted on ' + date + ' (this version)]</div>'
        '<h1 class="title mathjax"><span class="descriptor">Title:</span> '
        'Crystal Graph Convolutional Neural Networks</h1>'
        '<blockquote class="abstract mathjax">'
        '<span class="descriptor">Abstract:</span> '
        'Our crystal graph convolutional neural network predicts materials '
        'properties from the connection between atoms in crystal structures. '
        'We also evaluate local chemical environments and provide a '
        'transparent interpretation of the model predictions.'
        '</blockquote></body></html>'
    )


class AutoAbstractFetchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.folder = self.root / "local_only/reviews/fulltext_label24"
        self.folder.mkdir(parents=True)
        self.library = self.folder / "PRIMARY_PAPERS_TO_FILL.csv"
        self._csv(
            self.library,
            ["paper_id","paper_title","evidence_access","passage_text"],
            [
                dict(paper_id="5396",paper_title="Frozen original title",
                     evidence_access="",passage_text=""),
                dict(paper_id="registered",paper_title="Existing",
                     evidence_access="FULL_TEXT_USER_INSPECTED",passage_text="Real"),
            ],
        )
        self._csv(
            self.folder/"AUTO_PRIMARY_EVIDENCE_CANDIDATES.csv",
            ["paper_id","versioned_source_url","source_version_date","date_status"],
            [
                dict(paper_id="5396",
                     versioned_source_url="https://arxiv.org/pdf/1710.10324v1",
                     source_version_date="2017-10-27",
                     date_status="ARXIV_V1_WITHIN_CUTOFF"),
                dict(paper_id="registered",
                     versioned_source_url="https://arxiv.org/pdf/1701.00001v1",
                     source_version_date="2017-01-01",
                     date_status="ARXIV_V1_WITHIN_CUTOFF"),
            ],
        )

    def tearDown(self):
        self.tmp.cleanup()

    @staticmethod
    def _csv(path, fields, rows):
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

    def test_parser_preserves_text_and_historical_v1_date(self):
        excerpt, date, title = parse_arxiv_abstract(fake_page())
        self.assertTrue(excerpt.startswith("Our crystal graph"))
        self.assertNotIn("Abstract:", excerpt)
        self.assertEqual(date, "2017-10-27")
        self.assertIn("Crystal Graph", title)

    def test_historical_exact_url_only(self):
        rows = [dict(paper_id="5396",
                     versioned_source_url="https://arxiv.org/pdf/1710.10324v1",
                     source_version_date="2017-10-27",
                     date_status="ARXIV_V1_WITHIN_CUTOFF")]
        self.assertEqual(source_candidates(rows,"5396")[2],
                         "https://arxiv.org/abs/1710.10324v1")
        rows[0]["date_status"] = "UNVERIFIED"
        self.assertIsNone(source_candidates(rows,"5396"))

    @patch("research_lab.fetch_arxiv_abstracts.fetch_arxiv_page")
    def test_fetch_never_marks_user_inspected_and_is_idempotent(self, network):
        network.return_value = fake_page()
        unchanged = self.library.read_bytes()
        result = collect(self.root, pause=0)
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]["status"],
                         "AUTO_FETCHED_PENDING_HUMAN_INSPECTION")
        self.assertEqual(self.library.read_bytes(), unchanged)
        saved = self.folder/ARCHIVE_DIR/"paper_5396_abstract.txt"
        self.assertTrue(saved.is_file())
        network.reset_mock()
        again = collect(self.root, pause=0)
        self.assertEqual(again[0]["status"],"ALREADY_STAGED_NO_OVERWRITE")
        network.assert_not_called()
        self.assertEqual(self.library.read_bytes(),unchanged)

    @patch("research_lab.fetch_arxiv_abstracts.fetch_arxiv_page")
    def test_date_disagreement_refuses_capture(self, network):
        network.return_value = fake_page(date="28 Oct 2017")
        result = collect(self.root, pause=0)
        self.assertEqual(result[0]["status"],"FETCH_OR_VERIFICATION_FAILED")
        self.assertIn("Version date mismatch",result[0]["error"])
        self.assertFalse((self.folder/ARCHIVE_DIR/"paper_5396_abstract.txt").exists())

    @patch("research_lab.fetch_arxiv_abstracts.fetch_arxiv_page")
    def test_bad_markup_refuses_and_preserves_data(self, network):
        network.return_value = '<html><title>Arxiv not available</title></html>'
        result = collect(self.root, pause=0)
        self.assertEqual(result[0]["status"],"FETCH_OR_VERIFICATION_FAILED")
        self.assertFalse((self.folder/ARCHIVE_DIR/"paper_5396_abstract.txt").exists())


if __name__=="__main__":
    unittest.main()
