"""Offline synthetic tests for generic local user-attested paper intake."""
import csv
import tempfile
import unittest
from pathlib import Path

from research_lab.record_inspected_paper import record


class PaperRecorderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.folder = self.root / "local_only/reviews/fulltext_label24"
        self.folder.mkdir(parents=True)
        self.main_file = self.folder / "PRIMARY_PAPERS_TO_FILL.csv"
        self.fields = ("paper_id","paper_title","paper_year",
                       "source_url","source_version_date","passage_locator",
                       "passage_text","evidence_access")
        self.rows = [
            dict.fromkeys(self.fields,""),
            dict.fromkeys(self.fields,""),
        ]
        for r, i in zip(self.rows, ("5452", "other")):
            r.update(paper_id=i, paper_title=("Original source" if i=="5452" else "Other"),
                     paper_year=("2015" if i=="5452" else "2018"))
        self._write("PRIMARY_PAPERS_TO_FILL.csv", self.fields, self.rows)
        self._write("SOURCE_PASSAGES_TO_FILL.csv",
                    ("blind_id","snapshot_year","paper_id","paper_title","paper_year"),
                    [
                        {"blind_id":"L001","snapshot_year":"2020","paper_id":"5452",
                         "paper_title":"Original source","paper_year":"2015"},
                        {"blind_id":"L002","snapshot_year":"2022","paper_id":"5452",
                         "paper_title":"Original source","paper_year":"2015"},
                    ])
        self.auto_row = {
            "paper_id":"5452","date_status":"ARXIV_V1_WITHIN_CUTOFF",
            "source_version_date":"2015-05-31",
            "versioned_source_url":"https://arxiv.org/pdf/1506.00303v1"}
        self._write("AUTO_PRIMARY_EVIDENCE_CANDIDATES.csv",
                    tuple(self.auto_row),[self.auto_row])
        self.passage = self.root / "passage.txt"
        self.passage.write_text(
            "An inspected synthetic source-paper excerpt describes how a "
            "standardized high-throughput simulation workflow uses explicit "
            "settings to make results reproducible across independent "
            "research installations.",encoding="utf-8")
    def tearDown(self):
        self.tmp.cleanup()
    def _write(self, name, fields, rows):
        with (self.folder/name).open("w",encoding="utf-8",newline="") as f:
            w=csv.DictWriter(f,fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
    def _run(self, **kwargs):
        return record(self.root,"5452",str(self.passage),
                      "PDF page 1, Abstract",**kwargs)

    def test_preview_has_no_side_effect_and_apply_is_preserving(self):
        initial = self.main_file.read_bytes()
        preview=self._run()
        self.assertEqual(preview["status"],"DRY_RUN_ONLY")
        self.assertEqual(self.main_file.read_bytes(),initial)
        result=self._run(apply=True)
        self.assertEqual(result["linked_case_paper_rows"],2)
        self.assertEqual(result["source_version_date"],"2015-05-31")
        self.assertTrue(Path(result["backup"]).exists())
        self.assertEqual(Path(result["backup"]).read_bytes(),initial)
        with self.main_file.open(encoding="utf-8-sig",newline="") as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(rows[0]["evidence_access"],"FULL_TEXT_USER_INSPECTED")
        self.assertEqual(rows[0]["paper_id"],"5452")
        self.assertIn("reproducible",rows[0]["passage_text"])
        self.assertEqual(rows[1],self.rows[1])
        with self.assertRaisesRegex(ValueError,"already edited"):
            self._run(apply=True)

    def test_terminal_text_and_short_passage_rejected(self):
        self.passage.write_text(
            "PS C:\\\\Users\\\\a\\\\Desktop\\\\research> $rows | Export-Csv"
            + " X" * 80,encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"terminal"):
            self._run(apply=True)
        self.assertFalse(list(self.folder.glob("*.backup-*")))
        self.passage.write_text("Short",encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"too short"):
            self._run()

    def test_historical_date_guard_rejects_future_version(self):
        with self.assertRaisesRegex(ValueError,"newer"):
            self._run(source_url="https://arxiv.org/pdf/1506.00303v1",
                      source_version_date="2021-01-01")

    def test_arxiv_v1_may_predate_bibliographic_publication_year(self):
        # A journal article catalogued in 2018 can have a valid arXiv v1
        # from 2017. Rejecting it would incorrectly block historical evidence.
        self.rows[0]["paper_year"] = "2018"
        self._write("PRIMARY_PAPERS_TO_FILL.csv", self.fields, self.rows)
        self._write("SOURCE_PASSAGES_TO_FILL.csv",
                    ("blind_id", "snapshot_year", "paper_id", "paper_title", "paper_year"),
                    [
                        {"blind_id": "L001", "snapshot_year": "2020",
                         "paper_id": "5452", "paper_title": "Original source",
                         "paper_year": "2018"},
                        {"blind_id": "L002", "snapshot_year": "2022",
                         "paper_id": "5452", "paper_title": "Original source",
                         "paper_year": "2018"},
                    ])
        self.auto_row["source_version_date"] = "2017-10-27"
        self.auto_row["versioned_source_url"] = "https://arxiv.org/pdf/1710.10324v1"
        self._write("AUTO_PRIMARY_EVIDENCE_CANDIDATES.csv",
                    tuple(self.auto_row), [self.auto_row])
        preview = self._run()
        self.assertEqual(preview["status"], "DRY_RUN_ONLY")
        self.assertEqual(preview["source_version_date"], "2017-10-27")
        saved = self._run(apply=True)
        self.assertEqual(saved["status"], "SAVED_WITH_BACKUP")
        with self.main_file.open(encoding="utf-8-sig",newline="") as f:
            recorded = next(csv.DictReader(f))
        self.assertEqual(recorded["paper_year"], "2018")
        self.assertEqual(recorded["source_version_date"], "2017-10-27")

    def test_requires_explicit_date_for_unverified_source(self):
        self.auto_row["date_status"]="UNVERIFIED"
        self._write("AUTO_PRIMARY_EVIDENCE_CANDIDATES.csv",
                    tuple(self.auto_row),[self.auto_row])
        with self.assertRaisesRegex(ValueError,"Unverified source"):
            self._run()
        result=self._run(source_url="https://arxiv.org/pdf/1506.00303v1",
                         source_version_date="2015-05-31")
        self.assertEqual(result["status"],"DRY_RUN_ONLY")

    def test_missing_source_file_or_wrong_paper(self):
        with self.assertRaises(FileNotFoundError):
            record(self.root,"5452",str(self.root/"missing.txt"),
                   "PDF page 1, Abstract")
        with self.assertRaisesRegex(ValueError,"not found"):
            record(self.root,"nonexistent",str(self.passage),
                   "PDF page 1, Abstract")


if __name__=="__main__":
    unittest.main()
