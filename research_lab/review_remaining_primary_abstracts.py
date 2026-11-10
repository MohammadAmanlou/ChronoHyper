"""Human confirmation for five separately verified publisher/arXiv abstracts.

No confirmation -> NO registration. Never modify already reviewed rows.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import webbrowser

from research_lab.fetch_remaining_primary_abstracts import SOURCES, STAGING
from research_lab.fulltext_label_audit import LIBRARY, OUT
from research_lab.record_inspected_paper import read_csv, record


def review(project=".", paper_id=None, input_fn=input, emit_fn=print,
           open_browser=True):
    folder = Path(project).resolve() / OUT
    _, library = read_csv(folder / LIBRARY)
    remaining = [r for r in library if r["paper_id"] in SOURCES and
                 not (r["evidence_access"] or "").strip() and
                 (not paper_id or r["paper_id"] == paper_id)]
    if paper_id and paper_id not in SOURCES:
        raise ValueError("Unknown paper_id")
    saved = skipped = 0
    emit_fn("Original dated source intake only; NOT independent scientific label grading.")
    for r in remaining:
        pid = r["paper_id"]
        source = SOURCES[pid]
        path = folder / STAGING / ("paper_" + pid + "_abstract.txt")
        if not path.is_file():
            skipped += 1
            emit_fn("NO DOWNLOADED ABSTRACT: {} {} (source: {})".format(
                pid, r["paper_title"], source["url"]))
            continue
        emit_fn("\n" + "="*65)
        emit_fn("ID {} | {} | version date {}".format(pid,r["paper_title"],source["date"]))
        emit_fn("Source: " + source["url"])
        emit_fn("Extracted source abstract (not independently reviewed):\n" +
                path.read_text(encoding="utf-8-sig"))
        if open_browser:
            webbrowser.open(source["url"])
        answer = input_fn("After verifying exact article, date AND passage, "
                          "type CONFIRM {}; Enter skips, Q exits: ".format(pid)).strip()
        if answer.upper() == "Q":
            break
        if answer != "CONFIRM " + pid:
            skipped += 1
            emit_fn("SKIPPED: no attestation.")
            continue
        try:
            result = record(
                project=project, paper_id=pid, passage_file=str(path),
                locator=("arXiv v1 abstract page (compared against PDF)"
                         if source["kind"] == "arxiv" else
                         "Original publisher article, Abstract (human-inspected)"),
                source_url=source["url"],
                source_version_date=source["date"],
                apply=True,
            )
            saved += 1
            emit_fn("SAVED WITH BACKUP: " + result["backup"])
        except (ValueError, FileNotFoundError, OSError) as error:
            skipped += 1
            emit_fn("NOT SAVED: " + str(error))
    result = {"reviewed":saved, "skipped":skipped,
              "queued":len(remaining),
              "independent_scientific_label_review":False}
    emit_fn("Summary: "+str(result))
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project",default=".")
    p.add_argument("--paper-id")
    p.add_argument("--no-browser",action="store_true")
    a=p.parse_args()
    review(a.project,a.paper_id,open_browser=not a.no_browser)


if __name__=="__main__":
    main()
