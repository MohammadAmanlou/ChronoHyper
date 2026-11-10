"""Interactive applicant verification of locally staged historical arXiv abstracts.

Never auto-attest a paper. Opens exact historical PDF in browser for comparison.
Records only after user types CONFIRM followed by the correct paper ID.
This is source inspection, not independent scientific label validation.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
import webbrowser

from research_lab.fetch_arxiv_abstracts import (
    ARCHIVE_DIR, AUTO_CANDIDATES, source_candidates, csv_rows
)
from research_lab.fulltext_label_audit import LIBRARY, OUT
from research_lab.record_inspected_paper import record


def collect_review_queue(project=".", paper_id=None):
    folder = Path(project).resolve() / OUT
    library = csv_rows(folder / LIBRARY)
    candidates = csv_rows(folder / AUTO_CANDIDATES)
    queue = []
    for row in library:
        pid = row["paper_id"]
        if paper_id and paper_id != pid:
            continue
        if (row["evidence_access"] or "").strip():
            continue
        source = source_candidates(candidates, pid)
        if not source:
            continue
        pdf, version, _ = source
        text_file = folder / ARCHIVE_DIR / ("paper_" + pid + "_abstract.txt")
        if not text_file.is_file():
            continue
        queue.append((pid, row["paper_title"], pdf, version, text_file))
    if paper_id and not queue:
        raise ValueError("Paper not queued: already recorded or no verified v1 abstract file")
    return queue


def review(project=".", paper_id=None, open_browser=True, input_fn=input, emit_fn=print):
    queue = collect_review_queue(project, paper_id=paper_id)
    if not queue:
        emit_fn("No downloaded, still-unreviewed historical arXiv abstracts.")
        return {"reviewed": 0, "skipped": 0, "available": 0}
    emit_fn("SOURCE INTAKE ONLY: NOT an independent label accuracy review.")
    emit_fn("For each paper, inspect PDF v1 and compare the staged excerpt.")
    emit_fn("Type exactly CONFIRM <paper_id> only after personal inspection.")
    reviewed = skipped = 0
    for index, (pid, title, pdf, version, txt) in enumerate(queue, 1):
        passage = txt.read_text(encoding="utf-8-sig").strip()
        emit_fn("\n" + "="*64)
        emit_fn("Paper {} of {} | ID {} | {}".format(index, len(queue), pid, title))
        emit_fn("Historical source: {} | version {}".format(pdf, version))
        emit_fn("LOCAL EXTRACTED ABSTRACT (NOT YET INSPECTED):\n{}\n".format(passage))
        if open_browser:
            emit_fn("Opening the exact v1 PDF for human verification...")
            webbrowser.open(pdf)
        choice = input_fn(
            "After comparing with original PDF, type CONFIRM {} to record; "
            "press Enter to skip; Q to stop: ".format(pid)
        ).strip()
        if choice.upper() == "Q":
            emit_fn("Stopped. Existing records preserved.")
            break
        if choice != "CONFIRM " + pid:
            skipped += 1
            emit_fn("SKIPPED: no review claim was recorded.")
            continue
        try:
            result = record(project=project, paper_id=pid, passage_file=str(txt),
                            locator="arXiv v1 abstract page (verified against PDF)",
                            apply=True)
        except (ValueError, FileNotFoundError, OSError) as exc:
            skipped += 1
            emit_fn("NOT RECORDED: {}".format(exc))
            continue
        reviewed += 1
        emit_fn("Saved safely; backup: {}".format(result["backup"]))
    return {"reviewed": reviewed, "skipped": skipped, "available": len(queue)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", default=".")
    p.add_argument("--paper-id", help="Review only one source if needed")
    p.add_argument("--no-browser", action="store_true",
                   help="Do not auto-open PDF; user must independently inspect it")
    args = p.parse_args()
    result = review(args.project, args.paper_id, not args.no_browser)
    print("Interactive source intake summary: {}".format(result))
    print("Independent scientific label verification remains NOT_EVALUATED.")


if __name__ == "__main__":
    main()
