"""Offline tests for explicit human-in-the-loop source attestation."""
import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from research_lab.fetch_arxiv_abstracts import ARCHIVE_DIR
from research_lab.review_staged_abstracts import review, collect_review_queue


class InteractiveReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        folder = self.root / "local_only/reviews/fulltext_label24"
        folder.mkdir(parents=True)
        self.folder = folder
        self._csv(folder/"PRIMARY_PAPERS_TO_FILL.csv",
                  ("paper_id", "paper_title", "evidence_access"),
                  [{"paper_id": "5396", "paper_title": "Crystal Graph Neural Networks",
                    "evidence_access": ""},
                   {"paper_id": "5452", "paper_title": "Recorded study",
                    "evidence_access": "FULL_TEXT_USER_INSPECTED"}])
        self._csv(folder/"AUTO_PRIMARY_EVIDENCE_CANDIDATES.csv",
                  ("paper_id", "versioned_source_url",
                   "source_version_date", "date_status"),
                  [
                    {"paper_id": "5396",
                     "versioned_source_url": "https://arxiv.org/pdf/1710.10324v1",
                     "source_version_date": "2017-10-27",
                     "date_status": "ARXIV_V1_WITHIN_CUTOFF"},
                    {"paper_id": "5452",
                     "versioned_source_url": "https://arxiv.org/pdf/1506.00303v1",
                     "source_version_date": "2015-05-31",
                     "date_status": "ARXIV_V1_WITHIN_CUTOFF"},
                  ])
        drafts = folder/ARCHIVE_DIR
        drafts.mkdir()
        (drafts/"paper_5396_abstract.txt").write_text(
            "A new graph neural network architecture predicts "
            "material properties using the atom-level "
            "structural graph and empirical benchmarks. " * 2, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    @staticmethod
    def _csv(path, fields, rows):
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

    @patch("research_lab.review_staged_abstracts.record")
    @patch("research_lab.review_staged_abstracts.webbrowser.open")
    def test_empty_input_does_not_record_or_open_if_disabled(self, browser, writer):
        self.assertEqual(len(collect_review_queue(self.root)), 1)
        output = []
        r = review(self.root, open_browser=False,
                   input_fn=lambda prompt: "", emit_fn=output.append)
        self.assertEqual(r["reviewed"], 0)
        self.assertEqual(r["skipped"], 1)
        writer.assert_not_called()
        browser.assert_not_called()

    @patch("research_lab.review_staged_abstracts.record")
    @patch("research_lab.review_staged_abstracts.webbrowser.open")
    def test_explicit_case_attestation_is_required(self, browser, writer):
        writer.return_value = {"backup": "dummy"}
        r = review(self.root, input_fn=lambda prompt: "CONFIRM 5396",
                   emit_fn=lambda msg: None)
        self.assertEqual(r["reviewed"], 1)
        writer.assert_called_once()
        self.assertTrue(writer.call_args.kwargs["apply"])
        self.assertEqual(writer.call_args.kwargs["paper_id"], "5396")
        browser.assert_called_once_with(
            "https://arxiv.org/pdf/1710.10324v1"
        )

    @patch("research_lab.review_staged_abstracts.record")
    def test_wrong_id_does_not_record(self, writer):
        r = review(self.root, open_browser=False,
                   input_fn=lambda prompt: "CONFIRM 5452",
                   emit_fn=lambda msg: None)
        self.assertEqual(r["skipped"], 1)
        writer.assert_not_called()

    @patch("research_lab.review_staged_abstracts.record")
    def test_q_stops_without_mutation(self, writer):
        r = review(self.root, open_browser=False,
                   input_fn=lambda prompt: "Q",
                   emit_fn=lambda msg: None)
        self.assertEqual(r["reviewed"], 0)
        writer.assert_not_called()


if __name__ == "__main__":
    unittest.main()
