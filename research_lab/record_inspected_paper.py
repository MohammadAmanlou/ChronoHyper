"""Guarded local-only primary-paper evidence intake (NOT semantic label validation).

Applicant must inspect original dated full text, then save the selected passage
as a UTF-8 .txt file. No clipboard, hidden A/B keys, or retrieval Gold are used.
"""
import argparse
import csv
import json
import re
import shutil
import tempfile
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse

from research_lab.fulltext_label_audit import LIBRARY, OUT, PAPER_FIELDS, SOURCE

CANDIDATES = "AUTO_PRIMARY_EVIDENCE_CANDIDATES.csv"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("Missing CSV header")
        return reader.fieldnames, list(reader)


def checked_passage(path):
    if not path.is_file():
        raise FileNotFoundError("Save inspected source passage to a .txt file first: " + str(path))
    value = path.read_text(encoding="utf-8-sig").strip()
    if len(value) < 90:
        raise ValueError("Passage too short")
    if re.search(r"(?im)^\s*(?:PS\s+[A-Z]:\\|cd\s+[A-Z]:\\|\$\w+\s*=|>>>)", value):
        raise ValueError("Possible copied terminal/code content rather than paper text")
    if "\x00" in value:
        raise ValueError("NUL in source text")
    return value


def source_from_candidate(rows, paper_id):
    candidates = [r for r in rows if r.get("paper_id") == paper_id and
                  r.get("date_status") == "ARXIV_V1_WITHIN_CUTOFF" and
                  r.get("source_version_date") and r.get("versioned_source_url")]
    choices = {(r["versioned_source_url"], r["source_version_date"]) for r in candidates}
    return next(iter(choices)) if len(choices) == 1 else None


def record(project=".", paper_id="", passage_file="", locator="",
           source_url=None, source_version_date=None, apply=False):
    root = Path(project).resolve()
    folder = root / OUT
    library = folder / LIBRARY
    fields, records = read_csv(library)
    if not set(PAPER_FIELDS[2:]).issubset(fields):
        raise ValueError("Unexpected paper library schema")
    matches = [r for r in records if r["paper_id"] == str(paper_id)]
    if len(matches) != 1:
        raise ValueError("Paper not unique or not found: " + str(paper_id))
    target = matches[0]
    if target["evidence_access"].strip() or target["passage_text"].strip() or target["source_version_date"].strip():
        raise ValueError("Paper already edited or inspected; never overwrite automatically")
    if len(locator.strip()) < 5:
        raise ValueError("Provide the actual source PDF page or section with --locator")
    passage = checked_passage(Path(passage_file))
    _, cases = read_csv(folder / SOURCE)
    linked = [r for r in cases if r.get("paper_id") == str(paper_id)]
    if not linked:
        raise ValueError("Paper has no original blind case association")
    expected = {(r["paper_title"], r["paper_year"]) for r in linked}
    if expected != {(target["paper_title"], target["paper_year"])}:
        raise ValueError("Source identity differs from original immutable metadata")
    years = [int(r["snapshot_year"]) for r in linked]
    if any(y not in (2020, 2022, 2024) for y in years):
        raise ValueError("Unknown historical snapshot cutoff")
    _, auto = read_csv(folder / CANDIDATES)
    original = source_from_candidate(auto, str(paper_id))
    if source_url is None and source_version_date is None and original:
        url, date_text = original
        provenance = "machine-checked arxiv v1, applicant-inspected PDF"
    else:
        if source_url is None or source_version_date is None:
            raise ValueError("Unverified source: supply --source-url AND --source-version-date after manually inspecting the dated original")
        url, date_text = source_url, source_version_date
        provenance = "applicant-inspected source/date"
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError("Only authenticated-source HTTPS URLs, not credentials or HTTP")
    try:
        version = date.fromisoformat(date_text)
    except (TypeError, ValueError):
        raise ValueError("Invalid YYYY-MM-DD source version date") from None
    if version > date(min(years), 12, 31):
        raise ValueError("Source version is newer than the earliest original snapshot")
    if version.year < int(target["paper_year"]):
        raise ValueError("Version date precedes original paper year; investigate metadata")
    summary = {
        "paper_id": str(paper_id),
        "paper_title_original": target["paper_title"],
        "linked_case_paper_rows": len(linked),
        "source_url": url,
        "source_version_date": date_text,
        "passage_locator": locator.strip(),
        "passage_characters": len(passage),
        "passage_start": passage[:100],
        "date_provenance": provenance,
        "status": "SAVED_WITH_BACKUP" if apply else "DRY_RUN_ONLY",
        "scientific_label_validation": False,
    }
    if not apply:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return summary
    target.update({
        "source_url": url,
        "source_version_date": date_text,
        "passage_locator": locator.strip(),
        "passage_text": passage,
        "evidence_access": "FULL_TEXT_USER_INSPECTED",
    })
    backup = library.with_name(library.name + ".backup-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    shutil.copy2(library, backup)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8-sig", newline="",
                                     dir=folder, prefix="paper-intake-", suffix=".tmp",
                                     delete=False) as f:
        temp = Path(f.name)
        try:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction="raise")
            writer.writeheader()
            writer.writerows(records)
        except BaseException:
            temp.unlink(missing_ok=True)
            raise
    temp.replace(library)
    summary["backup"] = str(backup)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", default=".")
    p.add_argument("--paper-id", required=True)
    p.add_argument("--passage-file", required=True)
    p.add_argument("--locator", required=True)
    p.add_argument("--source-url", default=None)
    p.add_argument("--source-version-date", default=None)
    p.add_argument("--apply", action="store_true", help="Attest the PDF passage/version was personally inspected")
    a = p.parse_args()
    record(project=a.project, paper_id=a.paper_id, passage_file=a.passage_file,
           locator=a.locator, source_url=a.source_url,
           source_version_date=a.source_version_date, apply=a.apply)


if __name__ == "__main__":
    main()
