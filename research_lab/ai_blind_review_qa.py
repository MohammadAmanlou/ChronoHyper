"""Read-only QA of the real 24-case local AI blind review.

Does not re-run Qwen, re-grade, open A/B private mapping, edit private CSVs,
touch scientific score, or modify frozen evidence. Distinguishes formal
missing-field defects from heuristic note/grade consistency warnings.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
import re
from pathlib import Path

from research_lab.ai_blind_fulltext_review import _read_packet, FINAL, SUMMARY
from research_lab.blind_paper_eval import csv_read
from research_lab.fulltext_label_audit import FIXED_REVIEW, _sha
from research_lab.label_v3_blind import RATING

AFFIRMATIVE_OVERCLAIM = re.compile(
    r"\bgloss\s+(?:for\s+)?([AB])\s+overclaims?\b", re.IGNORECASE
)
EXPLICIT_TITLE_GRADE = re.compile(
    r"\btitle\s+([AB])\s+is\s+(accurate|vague|wrong)\b", re.IGNORECASE
)


def inspect_pair(original, rated):
    """Only inspect fixed fields and internal consistency; never infer true grades."""
    structural = []
    heuristic = []
    cid = original["blind_id"]
    for field in FIXED_REVIEW:
        if original.get(field) != rated.get(field):
            structural.append(("FROZEN_FIELD_CHANGED", field))
    sufficient = rated.get("evidence_sufficient_yes_no", "").strip().lower()
    if sufficient not in ("yes", "no"):
        structural.append(("INVALID_EVIDENCE_SUFFICIENCY", "evidence_sufficient_yes_no"))
    for arm in ("A", "B"):
        label = (original.get("label_" + arm) or "").strip()
        grade = (rated.get(arm + "_accuracy_accurate_vague_wrong") or "").strip().lower()
        flag = (rated.get(arm + "_gloss_overclaim_yes_no_unclear") or "").strip().lower()
        if sufficient == "yes":
            if not label and grade in RATING:
                structural.append(("EMPTY_TITLE_WAS_GRADED", arm))
            if grade not in RATING:
                structural.append(("MISSING_OR_INVALID_TITLE_GRADE", arm))
            if flag not in ("yes", "no", "unclear"):
                structural.append(("INVALID_GLOSS_FLAG", arm))
        elif sufficient == "no":
            if grade or flag != "unclear":
                structural.append(("INSUFFICIENT_BUT_DETERMINATE", arm))
        if label.lower() == "unresolved heterogeneous cluster" and grade == "wrong":
            heuristic.append(("ABSTENTION_GRADED_WRONG_NEEDS_SCOPE_REVIEW", arm))
    notes = rated.get("review_notes") or ""
    for match in AFFIRMATIVE_OVERCLAIM.finditer(notes):
        arm = match.group(1).upper()
        graded = (rated.get(arm + "_gloss_overclaim_yes_no_unclear") or "").lower()
        if graded != "yes":
            heuristic.append(("NOTES_SAY_OVERCLAIM_BUT_FLAG_" + (graded or "EMPTY").upper(), arm))
    for match in EXPLICIT_TITLE_GRADE.finditer(notes):
        arm, asserted = match.group(1).upper(), match.group(2).lower()
        graded = (rated.get(arm + "_accuracy_accurate_vague_wrong") or "").lower()
        if graded and graded != asserted:
            heuristic.append(("NOTES_TITLE_GRADE_CONTRADICTION", arm))
    return [{"case": cid, "issue": kind, "field_or_arm": arm}
            for kind, arm in structural], [
            {"case": cid, "warning": kind, "field_or_arm": arm}
            for kind, arm in heuristic]


def audit(project="."):
    base, original, original_sha = _read_packet(project)
    path = base / FINAL
    summary_path = base / SUMMARY
    if not path.is_file() or not summary_path.is_file():
        raise FileNotFoundError("AI-only local 24-case review not completed")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if (summary.get("rated_csv_sha256") != _sha(path)
            or summary.get("blind_packet_sha256") != original_sha
            or summary.get("reviewed") != 24
            or summary.get("stage") !=
            "AI_ONLY_SAME_CORPUS_DEVELOPMENT_NOT_INDEPENDENT_VALIDATION"):
        raise ValueError("Saved AI-only review fingerprints or stage mismatch")
    ratings = csv_read(path)
    source = {r["blind_id"]: r for r in original}
    got = {r["blind_id"]: r for r in ratings}
    if (len(ratings) != 24 or len(got) != 24 or set(got) != set(source)):
        raise ValueError("Missing, duplicated or unrecognized blind case rows")
    structural, heuristic = [], []
    for case_id in sorted(source):
        errors, warnings = inspect_pair(source[case_id], got[case_id])
        structural.extend(errors)
        heuristic.extend(warnings)
    report = {
        "stage": "READ_ONLY_POSTHOC_AI_REVIEW_QA_NOT_REGRADING",
        "reviewed_cases": len(ratings),
        "original_packet_sha256_verified": original_sha,
        "ai_only_csv_sha256_verified": _sha(path),
        "structural_issue_count": len(structural),
        "structural_issues": structural,
        "heuristic_warning_count": len(heuristic),
        "heuristic_warnings_need_human_context": heuristic,
        "original_ratings_modified": False,
        "original_scientific_score_modified": False,
        "private_A_B_mapping_read": False,
        "no_model_calls": True,
        "interpretation": ("Heuristic warnings are not confirmed reviewer mistakes; "
                           "inspect the source and full case before correcting a claim. "
                           "Do not retroactively rescore or convert this same-corpus "
                           "development assessment into independent confirmation."),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", default=".")
    args = p.parse_args()
    audit(args.project)


if __name__ == "__main__":
    main()
