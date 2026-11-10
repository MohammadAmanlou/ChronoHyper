"""Stage the five remaining historical primary-paper abstracts, LOCAL ONLY.

Download only verified original arXiv v1 abstracts or dated publisher
abstracts. NEVER mark an article FULL_TEXT_USER_INSPECTED automatically.
No hidden Gold, private blind keys, frozen paper metadata or reviewer
scores are read or modified. Publisher failures are logged, not guessed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
from html.parser import HTMLParser
import json
import re
import time
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from research_lab.fetch_arxiv_abstracts import fetch_arxiv_page, parse_arxiv_abstract
from research_lab.fulltext_label_audit import LIBRARY, OUT, SOURCE
from research_lab.record_inspected_paper import read_csv

STAGING = "REMAINING_PRIMARY_ABSTRACTS_PENDING_REVIEW"
# Dates were checked on the *original* publisher/version pages. They are
# article/publication dates, NOT the date on which we downloaded the page.
SOURCES = {
    "5402": {
        "url": "https://link.springer.com/article/10.1007/s11837-013-0755-4",
        "date": "2013-09-28", "kind": "publisher", "display_date": "28 September 2013",
        "title": "Materials Design and Discovery with High-Throughput Density Functional Theory: The Open Quantum Materials Database (OQMD)",
    },
    "5403": {
        "url": "https://arxiv.org/pdf/1308.5715v1", "date": "2013-08-26",
        "kind": "arxiv", "title": "AFLOW: an automatic framework for high-throughput materials discovery",
    },
    "5435": {
        "url": "https://arxiv.org/pdf/1910.10090v1", "date": "2019-10-22",
        "kind": "arxiv", "title": "Simulating diffusion properties of solid-state electrolytes via a neural network potential: Performance and training scheme",
    },
    "5399": {
        "url": "https://www.nature.com/articles/s41524-022-00879-4",
        "date": "2022-09-17", "kind": "publisher",
        "display_date": "17 September 2022",
        "title": "Linking atomic structural defects to mesoscale properties in crystalline solids using graph neural networks",
    },
    "5455": {
        "url": "https://www.nature.com/articles/s41586-023-06735-9",
        "date": "2023-11-29", "kind": "publisher",
        "display_date": "29 November 2023",
        "title": "Scaling deep learning for materials discovery",
    },
}


class PublisherAbstract(HTMLParser):
    """Extract paragraph text under the publisher's visible Abstract heading."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.heading = None
        self.heading_parts = []
        self.capture = False
        self.in_p = False
        self.p_parts = []
        self.paragraphs = []
        self.excluded = 0
        self.excluded_stack = []

    def handle_starttag(self, tag, attrs):
        if self.excluded_stack:
            if tag in ("script", "style", "noscript", "svg"):
                self.excluded_stack.append(tag)
            return
        if tag in ("script", "style", "noscript", "svg"):
            self.excluded_stack.append(tag)
            return
        if tag in ("h1", "h2", "h3", "h4"):
            if self.capture:
                self.capture = False
            self.heading, self.heading_parts = tag, []
        if tag == "p" and self.capture:
            self.in_p = True
            self.p_parts = []

    def handle_endtag(self, tag):
        if self.excluded_stack:
            if tag == self.excluded_stack[-1]:
                self.excluded_stack.pop()
            return
        if self.heading == tag:
            heading = " ".join("".join(self.heading_parts).split()).casefold()
            self.capture = heading in ("abstract", "summary")
            self.heading = None
        if tag == "p" and self.in_p:
            paragraph = " ".join("".join(self.p_parts).split())
            if paragraph:
                self.paragraphs.append(paragraph)
            self.in_p = False

    def handle_data(self, data):
        if self.excluded_stack:
            return
        if self.heading:
            self.heading_parts.append(data)
        elif self.capture and self.in_p:
            self.p_parts.append(data)


def download_publisher(url, timeout):
    request = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; ChronoHyperLocalSourceReview/1.0)",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urlopen(request, timeout=timeout) as response:
        target = urlparse(response.geturl())
        initial = urlparse(url)
        if target.scheme != "https" or target.hostname != initial.hostname:
            raise ValueError("Unexpected source redirect away from original publisher host")
        if "html" not in response.headers.get("Content-Type", "").lower():
            raise ValueError("Source returned non-HTML page")
        page = response.read(1_800_000).decode("utf-8", "replace")
    return page


def from_publisher(page, meta):
    # Check immutable paper identity and publication date directly against
    # original publisher HTML, never merely against own hardcoded metadata.
    all_visible = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", page)).split())
    title = " ".join(meta["title"].split())
    if title.casefold() not in all_visible.casefold():
        raise ValueError("Publisher page does not confirm original article title")
    if meta["display_date"].casefold() not in all_visible.casefold():
        raise ValueError("Publisher page does not show expected publication date")
    parser = PublisherAbstract()
    parser.feed(page)
    passage = " ".join(parser.paragraphs).strip()
    if len(passage) < 90:
        raise ValueError("Publisher abstract missing/too short; requires manual inspection")
    if len(passage) > 10000:
        raise ValueError("Publisher abstract too long; likely wrong HTML section")
    return passage


def collect(project=".", paper_id=None, timeout=25, pause=1):
    folder = Path(project).resolve() / OUT
    _, library = read_csv(folder / LIBRARY)
    _, cases = read_csv(folder / SOURCE)
    targets = [r for r in library if (r["paper_id"] in SOURCES
               and not (r["evidence_access"] or "").strip())
               and (paper_id is None or r["paper_id"] == paper_id)]
    if paper_id and paper_id not in SOURCES:
        raise ValueError("Unknown paper ID in verified five-source manifest")
    folder_out = folder / STAGING
    folder_out.mkdir(parents=True, exist_ok=True)
    results = []
    for record in targets:
        pid = record["paper_id"]
        src = SOURCES[pid]
        entry = dict(paper_id=pid, paper_title=record["paper_title"],
                     source_url=src["url"], source_version_date=src["date"],
                     source_kind=src["kind"], local_file="", characters="",
                     sha256="", status="", error="")
        try:
            if record["paper_title"].strip().casefold() != src["title"].casefold():
                raise ValueError("Frozen paper title differs from verified primary source")
            related = [r for r in cases if r.get("paper_id") == pid]
            if not related:
                raise ValueError("No original frozen source link")
            cutoff = min(date(int(r["snapshot_year"]), 12, 31) for r in related)
            if date.fromisoformat(src["date"]) > cutoff:
                raise ValueError("Primary source published after original cluster snapshot")
            local = folder_out / ("paper_" + pid + "_abstract.txt")
            entry["local_file"] = str(local)
            if local.exists():
                entry["status"] = "ALREADY_STAGED_NO_OVERWRITE"
                results.append(entry)
                continue
            if src["kind"] == "arxiv":
                absurl = src["url"].replace("/pdf/", "/abs/")
                abstract, actual, actual_title = parse_arxiv_abstract(
                    fetch_arxiv_page(absurl, timeout))
                if actual != src["date"]:
                    raise ValueError("Historical arXiv v1 date mismatch")
                if actual_title.casefold() != src["title"].casefold():
                    raise ValueError("arXiv v1 article title does not match expected title")
                entry["source_url"] = src["url"]
            else:
                abstract = from_publisher(download_publisher(src["url"], timeout), src)
            local.write_text(abstract + "\n", encoding="utf-8")
            entry.update(status="AUTO_FETCHED_PENDING_HUMAN_INSPECTION",
                         characters=str(len(abstract)),
                         sha256=hashlib.sha256(local.read_bytes()).hexdigest())
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as exc:
            entry["status"] = "FETCH_FAILED_NEEDS_MANUAL_SOURCE_REVIEW"
            entry["error"] = type(exc).__name__ + ": " + str(exc)[:240]
        results.append(entry)
        if pause and entry["status"] == "AUTO_FETCHED_PENDING_HUMAN_INSPECTION":
            time.sleep(pause)
    manifest = folder_out / "manifest_LOCAL.csv"
    headers = ("paper_id","paper_title","source_url","source_version_date",
               "source_kind","local_file","characters","sha256","status","error")
    with manifest.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f,fieldnames=headers)
        writer.writeheader()
        writer.writerows(results)
    print(json.dumps({
        "stage": "PRIMARY_PUBLISHER_OR_ARXIV_ABSTRACT_FETCH_ONLY_NOT_HUMAN_INSPECTED",
        "attempted": len(results),
        "status_counts": {status:sum(r["status"] == status for r in results)
                          for status in sorted(set(r["status"] for r in results))},
        "manifest": str(manifest),
        "original_paper_library_modified": False,
        "independent_scientific_label_validation": False,
        "errors": [{"paper_id": r["paper_id"], "error": r["error"]}
                   for r in results if r["error"]],
    }, indent=2, ensure_ascii=False))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project",default=".")
    parser.add_argument("--paper-id")
    parser.add_argument("--timeout",type=float,default=25)
    parser.add_argument("--pause",type=float,default=1)
    args=parser.parse_args()
    if args.timeout <= 0 or args.pause < 0:
        parser.error("timeout must be positive and pause nonnegative")
    collect(args.project,args.paper_id,args.timeout,args.pause)


if __name__=="__main__":
    main()
