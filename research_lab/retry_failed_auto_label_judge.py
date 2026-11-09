"""Recover failed LOCAL Ollama label judgments; never overwrite original evidence.

The original run reported 21 model/JSON errors as insufficient passages.
This optional post-hoc LOCAL AI-only retry separates genuine model errors
from evidence judgments, without re-running the three parsed judgments.

Read-only originals: 24-case blind form, candidate primary passages,
AUTO_AI_DEVELOPMENT_REVIEW.csv and original summary. Never opens Gold or
private A/B condition key, calls external APIs, or edits frozen outputs.

Commands:
  python -m research_lab.retry_failed_auto_label_judge --project . --probe
  python -m research_lab.retry_failed_auto_label_judge --project . --run
  python -m research_lab.retry_failed_auto_label_judge --project . --run --retry-errors
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

from research_lab.auto_label_judge import (
    COLUMNS, _case_prompt, _parse, _post_local, RESULT,
)
from research_lab.auto_primary_evidence import AUTO
from research_lab.blind_paper_eval import csv_read
from research_lab.fulltext_label_audit import BASE, OUT

RETRY_FILE = "AUTO_AI_RETRY_FAILED_CASES.csv"
RETRY_SUMMARY = "AUTO_AI_RETRY_SUMMARY.json"
RETRY_COLUMNS = (*COLUMNS, "retry_status", "retry_error")
ERROR_PREFIX = "Local model unavailable or output invalid;"
ORIGINAL_ERROR = "INSUFFICIENT_NO_VERIFIED_HISTORICAL_PASSAGE"
VALID = "VALID_AI_JUDGMENT"
ERROR = "MODEL_OR_JSON_ERROR"


def failed_ids(original):
    """Only rows with explicitly documented local model/JSON errors qualify."""
    failed = []
    for row in original:
        if (row["evidence_status"] == ORIGINAL_ERROR
                and (row.get("review_notes") or "").startswith(ERROR_PREFIX)):
            failed.append(row["blind_id"])
    return failed


def model_payload(model, prompt):
    return {
        "model": model, "prompt": prompt,
        "stream": False,
        "think": False,
        "format": "json",
        "options": {"temperature": 0, "num_predict": 1200},
    }


def evaluate(case, evidence, model, endpoint):
    prompt, sources = _case_prompt(case, evidence)
    if prompt is None or not sources:
        raise ValueError("No dated historical source passages for candidate")
    response = _post_local(endpoint, model_payload(model, prompt))
    if not isinstance(response, dict):
        raise ValueError("Ollama returned a non-object result")
    if response.get("done_reason") == "length":
        raise ValueError("Ollama stopped at the configured output-token limit")
    answer = response.get("response")
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("Ollama returned no final response; check think=false")
    obj = json.loads(answer)
    cites = [str(p["paper_id"]) + ":" + str(p["passage_locator"])
             for p in sources[:4]]
    rated = _parse(case, obj, model, cites)
    return {**rated, "retry_status": VALID, "retry_error": ""}


def record_error(case, exc):
    """Do not mislabel an execution failure as a scientific judgment."""
    msg = str(exc).replace("\r", " ").replace("\n", " ")
    return {
        **{c: "" for c in COLUMNS},
        "blind_id": case["blind_id"],
        "snapshot_year": case["snapshot_year"],
        "evidence_sufficient_yes_no": "",
        "review_notes": "No AI judgment; retry execution failed",
        "retry_status": ERROR,
        "retry_error": type(exc).__name__ + ": " + msg[:180],
    }


def _atomic_csv(path, records):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=RETRY_COLUMNS)
    writer.writeheader()
    writer.writerows(records)
    temporary = path.with_suffix(".tmp")
    temporary.write_text("\ufeff" + buffer.getvalue(), encoding="utf-8")
    temporary.replace(path)


def prepare(project):
    root = Path(project).resolve()
    folder = root / OUT
    cases = csv_read(root / BASE / "blind_v2_v3_24.csv")
    original = csv_read(folder / RESULT)
    passages = csv_read(folder / AUTO)
    ids = [c["blind_id"] for c in cases]
    original_ids = [c["blind_id"] for c in original]
    if len(ids) != 24 or len(set(ids)) != 24 or set(ids) != set(original_ids):
        raise ValueError("Original 24-case blind IDs missing or inconsistent")
    if len(original_ids) != len(set(original_ids)):
        raise ValueError("Duplicated original AI review IDs")
    failed = failed_ids(original)
    if not failed:
        raise ValueError("No original local model/JSON failures to retry")
    years = {x["blind_id"]: x["snapshot_year"] for x in cases}
    for row in original + passages:
        if row["blind_id"] not in years or row["snapshot_year"] != years[row["blind_id"]]:
            raise ValueError("Private evidence ID/year mismatch")
    by_case = defaultdict(list)
    for row in passages:
        by_case[row["blind_id"]].append(row)
    for case in cases:
        if case["blind_id"] in failed:
            prompt, eligible = _case_prompt(case, by_case[case["blind_id"]])
            if not prompt or not eligible:
                raise ValueError("Previously failed model case has no eligible source: "
                                 + case["blind_id"])
    return root, folder, cases, original, by_case, failed


def run(project=".", model="qwen3:8b", endpoint="http://127.0.0.1:11434/api/generate",
        probe=False, retry_errors=False):
    root, folder, cases, original, by_case, failed = prepare(project)
    cases_by_id = {r["blind_id"]: r for r in cases}
    if probe:
        cid = failed[0]
        try:
            row = evaluate(cases_by_id[cid], by_case[cid], model, endpoint)
        except Exception as exc:
            print(json.dumps({
                "probe_blind_id": cid, "status": ERROR,
                "error_type": type(exc).__name__,
                "error_message": str(exc)[:240],
                "saved_files": False,
            }, indent=2))
            raise SystemExit(1)
        print(json.dumps({
            "probe_blind_id": cid,
            "status": row["retry_status"],
            "AI_evidence_sufficient": row["evidence_sufficient_yes_no"],
            "thinking_disabled": True, "saved_files": False,
            "scientific_independent_validation": False,
        }, indent=2))
        return

    # Saved original and private source files are never changed.
    out = folder / RETRY_FILE
    manifest = folder / RETRY_SUMMARY
    provenance = {
        "original_review_sha256": hashlib.sha256((folder / RESULT).read_bytes()).hexdigest(),
        "candidate_passages_sha256": hashlib.sha256((folder / AUTO).read_bytes()).hexdigest(),
        "blind_case_sheet_sha256": hashlib.sha256(
            (root / BASE / "blind_v2_v3_24.csv").read_bytes()).hexdigest(),
    }
    if manifest.is_file():
        old_summary = json.loads(manifest.read_text(encoding="utf-8"))
        if old_summary.get("provenance") != provenance:
            raise ValueError("Private inputs have changed; refuse to combine unrelated runs")
        if old_summary.get("model") != model:
            raise ValueError("Existing retry uses a different model; preserve before switching")
    previous = csv_read(out) if out.exists() else []
    if any(set(r) != set(RETRY_COLUMNS) for r in previous):
        raise ValueError("Previous retry CSV schema mismatch")
    previous_ids = [r["blind_id"] for r in previous]
    if len(set(previous_ids)) != len(previous_ids) or not set(previous_ids).issubset(set(failed)):
        raise ValueError("Retry CSV contains duplicate/unexpected case IDs")
    completed = {r["blind_id"]: r for r in previous}
    for row in previous:
        if row["snapshot_year"] != cases_by_id[row["blind_id"]]["snapshot_year"]:
            raise ValueError("Resume snapshot mismatch")
        if row["retry_status"] not in (VALID, ERROR):
            raise ValueError("Resume record has unknown status")
    print("Previously recorded:", len(completed), "original model errors:", len(failed),
          flush=True)
    for idx, cid in enumerate(failed, 1):
        if cid in completed and (
                completed[cid]["retry_status"] == VALID or not retry_errors):
            continue
        case = cases_by_id[cid]
        try:
            result = evaluate(case, by_case[cid], model, endpoint)
        except Exception as exc:
            result = record_error(case, exc)
        completed[cid] = result
        _atomic_csv(out, [completed[x] for x in failed if x in completed])
        print("[%d/%d] %s %s sufficient=%s" % (
            idx, len(failed), cid, result["retry_status"],
            result["evidence_sufficient_yes_no"] or "UNKNOWN"), flush=True)
    tallies = Counter(r["retry_status"] for r in completed.values())
    prior_valid = [x for x in original if x["blind_id"] not in failed
                   and x["evidence_status"] ==
                   "LOCAL_AI_SCORED_ON_MACHINE_EXTRACTED_SOURCES"]
    recovered = [r for r in completed.values() if r["retry_status"] == VALID]
    summary = {
        "schema": "chronohyper_private_ai_retry_v1",
        "stage": "LOCAL_AI_ONLY_POSTHOC_NOT_INDEPENDENT",
        "model": model, "think": False, "json_mode": True,
        "original_failed_case_count": len(failed),
        "retry_cases_recorded": len(completed),
        "retry_AI_valid": tallies[VALID],
        "retry_model_or_JSON_errors": tallies[ERROR],
        "original_valid_judgments_preserved": len(prior_valid),
        "combined_AI_valid_count": len(prior_valid) + len(recovered),
        "combined_AI_sufficient": sum(
            r["evidence_sufficient_yes_no"] == "yes" for r in prior_valid + recovered),
        "combined_AI_insufficient": sum(
            r["evidence_sufficient_yes_no"] == "no" for r in prior_valid + recovered),
        "unresolved_cases": len(failed) - len(recovered),
        "provenance": provenance,
        "original_files_overwritten": False,
        "gold_read": False, "private_A_B_mapping_read": False,
        "independent_scientific_overclaim_rate": None,
        "note": "AI sufficiency is not independently verified full-text semantic correctness.",
    }
    manifest.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=".")
    parser.add_argument("--model", default="qwen3:8b")
    parser.add_argument("--endpoint", default="http://127.0.0.1:11434/api/generate")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--probe", action="store_true", help="Test one original failed case; write nothing")
    group.add_argument("--run", action="store_true", help="Retry only original failed cases; checkpoint separately")
    parser.add_argument("--retry-errors", action="store_true",
                        help="On resume, retry recorded errors but preserve valid completions")
    args = parser.parse_args()
    if args.retry_errors and not args.run:
        parser.error("--retry-errors requires --run")
    run(args.project, args.model, args.endpoint,
        probe=args.probe, retry_errors=args.retry_errors)


if __name__ == "__main__":
    main()
