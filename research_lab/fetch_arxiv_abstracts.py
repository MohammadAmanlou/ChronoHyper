"""Retrieve version-specific arXiv abstracts into LOCAL pending files.

Machine-retrieved primary abstracts are NOT FULL_TEXT_USER_INSPECTED and are
NOT independent scientific label assessments. Never modify the original
source-intake library or blind reviewer forms here.
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
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from research_lab.fulltext_label_audit import LIBRARY, OUT

AUTO_CANDIDATES = "AUTO_PRIMARY_EVIDENCE_CANDIDATES.csv"
ARCHIVE_DIR = "AUTO_ARXIV_ABSTRACTS_PENDING_REVIEW"
ARXIV_PDF = re.compile(r"^https://arxiv\.org/pdf/(\d{4}\.\d{4,5}|[a-z-]+(?:\.[A-Z]{2})?/\d{7})(v1)(?:\.pdf)?/?$", re.I)


def csv_rows(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


class ArxivAbstractHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.abstract_depth = 0
        self.descriptor_depth = 0
        self.dateline_depth = 0
        self.title_depth = 0
        self.abstract_parts = []
        self.dateline_parts = []
        self.title_parts = []

    def handle_starttag(self, tag, attrs):
        classes = dict(attrs).get("class", "").split()
        if self.abstract_depth:
            self.abstract_depth += 1
            if "descriptor" in classes:
                self.descriptor_depth = 1
            elif self.descriptor_depth:
                self.descriptor_depth += 1
        elif tag == "blockquote" and "abstract" in classes:
            self.abstract_depth = 1
        if self.dateline_depth:
            self.dateline_depth += 1
        elif "dateline" in classes and tag in ("div", "p"):
            self.dateline_depth = 1
        if self.title_depth:
            self.title_depth += 1
        elif tag == "h1" and "title" in classes:
            self.title_depth = 1

    def handle_endtag(self, tag):
        if self.abstract_depth:
            self.abstract_depth -= 1
            if self.descriptor_depth:
                self.descriptor_depth -= 1
        if self.dateline_depth:
            self.dateline_depth -= 1
        if self.title_depth:
            self.title_depth -= 1

    def handle_data(self, data):
        if self.abstract_depth and not self.descriptor_depth:
            self.abstract_parts.append(data)
        if self.dateline_depth:
            self.dateline_parts.append(data)
        if self.title_depth:
            self.title_parts.append(data)


def parse_arxiv_abstract(page):
    p = ArxivAbstractHTML()
    p.feed(page)
    abstract = html.unescape(" ".join("".join(p.abstract_parts).split()))
    date_line = " ".join("".join(p.dateline_parts).split())
    title = " ".join("".join(p.title_parts).split())
    title = re.sub(r"^Title:\s*", "", title, flags=re.I)
    m = re.search(r"Submitted on\s+(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})", date_line)
    if not m:
        raise ValueError("arXiv v1 submission date not readable; skip rather than infer")
    version_date = datetime.strptime(m.group(1), "%d %b %Y").date().isoformat()
    if len(abstract) < 90 or not title:
        raise ValueError("Missing or implausibly short official arXiv abstract/title")
    return abstract, version_date, title


def source_candidates(rows, paper_id):
    eligible = [r for r in rows if r.get("paper_id") == paper_id
                and r.get("date_status") == "ARXIV_V1_WITHIN_CUTOFF"
                and r.get("source_version_date") and r.get("versioned_source_url")]
    pairs = {(r["versioned_source_url"], r["source_version_date"]) for r in eligible}
    if len(pairs) != 1:
        return None
    url, date_text = next(iter(pairs))
    match = ARXIV_PDF.fullmatch(url)
    if not match:
        return None
    return url, date_text, "https://arxiv.org/abs/" + match.group(1) + match.group(2)


def fetch_arxiv_page(url, timeout):
    req = Request(url, headers={
        "User-Agent": "ChronoHyperPrimarySourceIntake/1.0 (academic local source review)",
        "Accept": "text/html",
    })
    with urlopen(req, timeout=timeout) as res:
        if res.geturl().split("/")[2].lower() not in ("arxiv.org", "www.arxiv.org"):
            raise ValueError("Unexpected redirect outside arxiv.org")
        if "text/html" not in res.headers.get("Content-Type", "").lower():
            raise ValueError("arXiv did not return HTML")
        data = res.read(600_000)
    return data.decode("utf-8", "replace")


def collect(project=".", paper_id=None, timeout=20, pause=1.2):
    folder = Path(project).resolve() / OUT
    library = csv_rows(folder / LIBRARY)
    candidates = csv_rows(folder / AUTO_CANDIDATES)
    destination = folder / ARCHIVE_DIR
    destination.mkdir(parents=True, exist_ok=True)
    pending = [r for r in library if not (r["evidence_access"] or "").strip()]
    if paper_id:
        pending = [r for r in pending if r["paper_id"] == str(paper_id)]
        if not pending:
            raise ValueError("Paper not unfilled or unknown: " + str(paper_id))
    report = []
    for n, paper in enumerate(pending):
        pid = paper["paper_id"]
        result = {
            "paper_id": pid,
            "paper_title_original": paper["paper_title"],
            "status": "",
            "source_pdf_url": "",
            "abstract_url": "",
            "historical_v1_date": "",
            "local_abstract_file": "",
            "characters": "",
            "sha256": "",
            "error": "",
        }
        selected = source_candidates(candidates, pid)
        if not selected:
            result["status"] = "NEEDS_MANUAL_SOURCE_DISCOVERY"
            report.append(result)
            continue
        pdf, expected_date, abstract_url = selected
        result.update(source_pdf_url=pdf, abstract_url=abstract_url,
                      historical_v1_date=expected_date)
        saved = destination / ("paper_" + pid + "_abstract.txt")
        try:
            if saved.is_file():
                result["status"] = "ALREADY_STAGED_NO_OVERWRITE"
                result["local_abstract_file"] = str(saved)
                report.append(result)
                continue
            page = fetch_arxiv_page(abstract_url, timeout)
            abstract, actual_date, title = parse_arxiv_abstract(page)
            if actual_date != expected_date:
                raise ValueError("Version date mismatch expected " + expected_date +
                                 " received " + actual_date)
            # The frozen source title is NEVER modified. The fetched title is
            # exposed for human comparison instead of auto-forcing a match.
            if not title.strip():
                raise ValueError("Missing arXiv source title")
            saved.write_text(abstract + "\n", encoding="utf-8")
            result.update(status="AUTO_FETCHED_PENDING_HUMAN_INSPECTION",
                          local_abstract_file=str(saved), characters=str(len(abstract)),
                          sha256=hashlib.sha256(saved.read_bytes()).hexdigest())
        except (ValueError, UnicodeError, OSError, HTTPError, URLError) as e:
            result["status"] = "FETCH_OR_VERIFICATION_FAILED"
            result["error"] = type(e).__name__ + ": " + str(e)[:200]
        report.append(result)
        if n < len(pending)-1 and pause > 0 and result["status"] == "AUTO_FETCHED_PENDING_HUMAN_INSPECTION":
            time.sleep(pause)
    manifest = destination / "manifest_LOCAL.csv"
    with manifest.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(report[0]) if report else
                                ["paper_id","status"])
        writer.writeheader()
        writer.writerows(report)
    states = {k:sum(r["status"] == k for r in report)
              for k in sorted(set(r["status"] for r in report))}
    summary = {
        "stage": "AUTO_FETCHED_SOURCE_ABSTRACTS_PENDING_HUMAN_INSPECTION",
        "papers_attempted": len(report),
        "status_counts": states,
        "manifest": str(manifest),
        "original_primary_paper_csv_modified": False,
        "independent_scientific_label_review": False,
        "example_next_step": (
            "After personally checking the arXiv v1 abstract, run "
            "python -m research_lab.record_inspected_paper "
            "--project . --paper-id 5396 "
            "--passage-file local_only/reviews/fulltext_label24/"
            "AUTO_ARXIV_ABSTRACTS_PENDING_REVIEW/paper_5396_abstract.txt "
            '--locator "arXiv v1 abstract page" --apply'
        ),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=".")
    parser.add_argument("--paper-id", help="Optional: fetch one paper only")
    parser.add_argument("--timeout", type=float, default=20)
    parser.add_argument("--pause", type=float, default=1.2)
    args = parser.parse_args()
    if args.timeout <= 0 or args.pause < 0:
        parser.error("timeout must be positive and pause cannot be negative")
    collect(args.project, args.paper_id, args.timeout, args.pause)


if __name__ == "__main__":
    main()
