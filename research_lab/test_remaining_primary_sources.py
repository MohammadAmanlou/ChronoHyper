"""Offline tests for the five verified original-source abstract fetch/inspection tools."""
import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research_lab.fetch_remaining_primary_abstracts import (
    SOURCES, STAGING, from_publisher, collect,
)
from research_lab.review_remaining_primary_abstracts import review


def publisher_html(src):
    return (
        '<html><h1>' + src["title"] + '</h1>'
        '<div>Published: '+src["display_date"]+'</div>'
        '<h2>Abstract</h2>'
        '<div><p>Materials research uses advanced computational methods to '
        'discover new structures, learn quantitative properties and speed up '
        'the screening of scientific candidates.</p>'
        '<p>These experimental and modelling techniques form a reproducible '
        'framework for identifying candidate materials and identifying '
        'limitations of predictive models.</p></div>'
        '<h2>Access this article</h2>'
        '<p>THIS MUST NOT BE INCLUDED in abstract</p></html>'
    )


class RemainingSourcesTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        self.folder=self.root/"local_only/reviews/fulltext_label24"
        self.folder.mkdir(parents=True)
        self.lib=self.folder/"PRIMARY_PAPERS_TO_FILL.csv"
        self._write(self.lib,
                    ["paper_id","paper_title","paper_year","evidence_access"],
                    [{"paper_id":k,"paper_title":s["title"],
                      "paper_year":s["date"][:4],"evidence_access":""}
                     for k,s in SOURCES.items()])
        self._write(self.folder/"SOURCE_PASSAGES_TO_FILL.csv",
                    ["paper_id","snapshot_year"],
                    [{"paper_id":k,"snapshot_year":"2024"} for k in SOURCES])

    def tearDown(self):
        self.tmp.cleanup()

    @staticmethod
    def _write(path,fields,rows):
        with path.open("w",encoding="utf-8",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_publisher_abstract_only_visible_original_heading(self):
        src=SOURCES["5402"]
        abstract=from_publisher(publisher_html(src),src)
        self.assertTrue(abstract.startswith("Materials research"))
        self.assertIn("reproducible framework",abstract)
        self.assertNotIn("THIS MUST NOT",abstract)
        with self.assertRaisesRegex(ValueError,"publication date"):
            from_publisher(publisher_html(src).replace(src["display_date"],"2026"),src)

    @patch("research_lab.fetch_remaining_primary_abstracts.fetch_arxiv_page")
    def test_collect_arxiv_stages_without_changing_original(self, fetch):
        src=SOURCES["5403"]
        fetch.return_value=(
            "<html><div class='dateline'>[Submitted on 26 Aug 2013]</div>"
            "<h1 class='title'><span class='descriptor'>Title:</span> "
            + src["title"] + "</h1>"
            "<blockquote class='abstract'><span class='descriptor'>Abstract:</span>"
            " Original AFLOW source-based abstract on computational materials "
            " research introduces systematic high throughput workflows to "
            " classify materials and predict their electronic properties."
            "</blockquote></html>"
        )
        before=self.lib.read_bytes()
        result=collect(self.root,paper_id="5403",pause=0)
        self.assertEqual(result[0]["status"],
                         "AUTO_FETCHED_PENDING_HUMAN_INSPECTION")
        self.assertEqual(self.lib.read_bytes(),before)
        file=self.folder/STAGING/"paper_5403_abstract.txt"
        self.assertTrue(file.is_file())
        repeated=collect(self.root,paper_id="5403",pause=0)
        self.assertEqual(repeated[0]["status"],"ALREADY_STAGED_NO_OVERWRITE")

    @patch("research_lab.fetch_remaining_primary_abstracts.download_publisher")
    def test_source_date_and_title_in_html_required(self, fetch):
        src=SOURCES["5455"]
        fetch.return_value=publisher_html(src)
        result=collect(self.root,paper_id="5455",pause=0)
        self.assertEqual(result[0]["status"],"AUTO_FETCHED_PENDING_HUMAN_INSPECTION")
        file=self.folder/STAGING/"paper_5455_abstract.txt"
        self.assertTrue(file.is_file())
        file.unlink()
        fetch.return_value="<html><h2>Abstract</h2><p>no real title or date</p></html>"
        result=collect(self.root,paper_id="5455",pause=0)
        self.assertEqual(result[0]["status"],"FETCH_FAILED_NEEDS_MANUAL_SOURCE_REVIEW")
        self.assertFalse(file.exists())

    @patch("research_lab.review_remaining_primary_abstracts.record")
    @patch("research_lab.review_remaining_primary_abstracts.webbrowser.open")
    def test_only_manual_exact_confirmation_attests(self, browser, writer):
        (self.folder/STAGING).mkdir()
        (self.folder/STAGING/"paper_5402_abstract.txt").write_text(
            "Synthetic original primary paper abstract on "
            "materials databases and high throughput simulations. "*3,encoding="utf-8")
        output=[]
        r=review(self.root,paper_id="5402",open_browser=False,
                 input_fn=lambda p: "",emit_fn=output.append)
        self.assertEqual(r["reviewed"],0)
        writer.assert_not_called()
        browser.assert_not_called()
        writer.return_value={"backup":"ok"}
        r=review(self.root,paper_id="5402",open_browser=False,
                 input_fn=lambda p: "CONFIRM 5402",emit_fn=output.append)
        self.assertEqual(r["reviewed"],1)
        self.assertEqual(writer.call_args.kwargs["source_url"],SOURCES["5402"]["url"])
        self.assertEqual(writer.call_args.kwargs["source_version_date"],"2013-09-28")
        self.assertTrue(writer.call_args.kwargs["apply"])


if __name__=="__main__":
    unittest.main()
