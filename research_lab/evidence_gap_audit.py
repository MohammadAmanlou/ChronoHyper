"""Private, read-only audit of source coverage, model errors and AI insufficiency.

Offline: no PDFs, model calls, external APIs, Gold, or A/B condition key.
The source judge records network/invalid-JSON failures as insufficient-source
status; review_notes must therefore be checked before interpreting 24-case totals.
Run: python -m research_lab.evidence_gap_audit --project .
"""
import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

CASES="local_only/reviews/label_v3_fresh/blind_v2_v3_24.csv"
PASSAGES="local_only/reviews/fulltext_label24/AUTO_PRIMARY_EVIDENCE_CANDIDATES.csv"
REVIEWS="local_only/reviews/fulltext_label24/AUTO_AI_DEVELOPMENT_REVIEW.csv"
STATUS="local_only/reviews/fulltext_label24/AUTO_EVIDENCE_STATUS.json"
SUMMARY="local_only/reviews/fulltext_label24/AUTO_AI_REVIEW_SUMMARY.json"
DATED="ARXIV_V1_WITHIN_CUTOFF"
EXTRACTED="AUTO_RETRIEVED_UNVERIFIED_NOT_REVIEWED"
SCORED="LOCAL_AI_SCORED_ON_MACHINE_EXTRACTED_SOURCES"
NOT_SCORED="INSUFFICIENT_NO_VERIFIED_HISTORICAL_PASSAGE"


def read_csv(path, fields):
    with path.open(encoding="utf-8-sig",newline="") as file:
        reader=csv.DictReader(file)
        if not set(fields).issubset(reader.fieldnames or []):
            raise ValueError("CSV schema mismatch: "+path.name)
        return list(reader)


def summarize(cases, passages, reviews, status=None, summary=None):
    ids=[r["blind_id"] for r in cases]
    if len(ids)!=24 or len(set(ids))!=24:
        raise ValueError("Expected 24 original blind case IDs")
    review_ids=[r["blind_id"] for r in reviews]
    if len(review_ids)!=24 or len(set(review_ids))!=24 or set(review_ids)!=set(ids):
        raise ValueError("Review IDs do not match 24 original blind case IDs")
    if not set(r["blind_id"] for r in passages).issubset(set(ids)):
        raise ValueError("Unknown blind case in evidence")
    years={r["blind_id"]:str(r["snapshot_year"]) for r in cases}
    for r in passages+reviews:
        if str(r["snapshot_year"])!=years[r["blind_id"]]:
            raise ValueError("Snapshot-year mismatch: "+r["blind_id"])
    grouped=defaultdict(list)
    for r in passages:
        grouped[r["blind_id"]].append(r)
    byreview={r["blind_id"]:r for r in reviews}
    counts=Counter()
    per_year=defaultdict(Counter)
    rows=[]
    for case in cases:
        cid=case["blind_id"]
        evidence=grouped[cid]
        eligible=[r for r in evidence if r["date_status"]==DATED
                  and r["evidence_status"]==EXTRACTED]
        judge=byreview[cid]
        called=judge["evidence_status"]==SCORED
        sufficient=judge["evidence_sufficient_yes_no"].strip().lower()
        if judge["evidence_status"] not in (SCORED,NOT_SCORED):
            raise ValueError("Unexpected judge result for "+cid)
        if sufficient not in ("yes","no"):
            raise ValueError("Unknown AI sufficiency value for "+cid)
        if sufficient=="yes" and (not called or not eligible):
            raise ValueError("Unverified case cannot claim sufficient evidence: "+cid)
        # IMPORTANT: auto_label_judge.run() catches Ollama/JSON exceptions and
        # deliberately stores _no_evidence() with the *same* evidence status
        # as a genuine no-passage source gate. Do not conflate those outcomes.
        notes=(judge.get("review_notes") or "").strip()
        model_failed=notes.startswith("Local model unavailable or output invalid;")
        if called and not eligible:
            category="INCONSISTENT_AI_SCORED_WITHOUT_ELIGIBLE_PASSAGE"
        elif eligible and not called:
            category=("ELIGIBLE_PASSAGES_MODEL_OR_JSON_ERROR" if model_failed
                      else "ELIGIBLE_PASSAGES_UNSCORED_UNEXPLAINED")
        elif sufficient=="yes":
            category="AI_SAYS_SUFFICIENT_NOT_INDEPENDENT"
        elif eligible:
            category="DATED_EVIDENCE_AI_SAYS_INSUFFICIENT"
        elif model_failed:
            category="INCONSISTENT_MODEL_ERROR_WITHOUT_ELIGIBLE_PASSAGE"
        elif evidence:
            category="CANDIDATES_PRESENT_BUT_NOT_DATE_ELIGIBLE"
        else:
            category="NO_SOURCE_CANDIDATES_FOR_CASE"
        counts[category]+=1
        per_year[years[cid]][category]+=1
        rows.append({"blind_id":cid,"year":years[cid],
                     "candidate_passages":len(evidence),
                     "historically_eligible_passages":len(eligible),
                     "AI_output_parsed_successfully":called,
                     "AI_evidence_sufficient":sufficient,"diagnostic":category})
    if summary:
        if summary.get("blind_case_count")!=24 or summary.get("sufficient_cases")!=counts["AI_SAYS_SUFFICIENT_NOT_INDEPENDENT"]:
            raise ValueError("Existing AI summary disagrees with individual review rows")
    result={
      "schema":"chronohyper_private_evidence_gap_audit_v1",
      "scope":"READ_ONLY_OFFLINE_NO_GOLD_NO_BLIND_KEY",
      "blind_cases":24,
      "candidate_passages":len(passages),
      "candidate_date_statuses":dict(sorted(Counter(r["date_status"] for r in passages).items())),
      "cases_with_any_candidate":sum(bool(grouped[cid]) for cid in ids),
      "cases_with_dated_eligible_evidence":sum(r["historically_eligible_passages"]>0 for r in rows),
      "cases_with_eligible_evidence_for_model":sum(r["historically_eligible_passages"]>0 for r in rows),
      "cases_with_successfully_parsed_AI_responses":sum(r["AI_output_parsed_successfully"] for r in rows),
      "cases_with_model_or_JSON_failures":counts["ELIGIBLE_PASSAGES_MODEL_OR_JSON_ERROR"],
      "cases_with_unexplained_source_review_disagreement":counts["ELIGIBLE_PASSAGES_UNSCORED_UNEXPLAINED"]+counts["INCONSISTENT_AI_SCORED_WITHOUT_ELIGIBLE_PASSAGE"]+counts["INCONSISTENT_MODEL_ERROR_WITHOUT_ELIGIBLE_PASSAGE"],
      "AI_sufficient_cases":counts["AI_SAYS_SUFFICIENT_NOT_INDEPENDENT"],
      "diagnoses":dict(sorted(counts.items())),
      "by_snapshot":{k:dict(sorted(v.items())) for k,v in sorted(per_year.items())},
      "case_ids_only_no_private_passages":rows,
      "scientific_overclaim_rate":"NOT_EVALUATED",
      "interpretation":"Source absence, Qwen/JSON execution errors, and AI judgment of insufficient excerpts are separate. None by itself demonstrates an incorrect label; semantic overclaim remains unmeasured."
    }
    if status:
        result["source_paper_counts_NOT_case_coverage"]={
          key:status.get(key) for key in ("unique_accessible_pdf_count",
                    "arxiv_v1_within_cutoff_count","pdf_date_version_unverified_count",
                    "candidate_case_paper_passages")}
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project",default=".")
    a=parser.parse_args()
    root=Path(a.project).resolve()
    cases=read_csv(root/CASES,["blind_id","snapshot_year"])
    passages=read_csv(root/PASSAGES,["blind_id","snapshot_year","date_status","evidence_status"])
    reviews=read_csv(root/REVIEWS,["blind_id","snapshot_year","evidence_status","evidence_sufficient_yes_no"])
    status=json.loads((root/STATUS).read_text(encoding="utf-8")) if (root/STATUS).is_file() else None
    summary=json.loads((root/SUMMARY).read_text(encoding="utf-8")) if (root/SUMMARY).is_file() else None
    print(json.dumps(summarize(cases,passages,reviews,status,summary),ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
