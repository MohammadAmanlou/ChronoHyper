"""Screen 36 independently authored queries BEFORE rankings; preserve source failures.

Never silently discard sampled targets. Creates a separate 34-query experiment
only when the original paper for excluded rows was explicitly unverified by
the source-checking author. Original 36-row author kit/response are untouched.
"""
from __future__ import annotations
import argparse
import csv
import difflib
import hashlib
import json
import re
from pathlib import Path

from research_lab.fresh_retrieval import AUTHOR_FIELDS, RETURN_FIELDS, _read_csv, _write_csv, _save_json
from research_lab.retrieval_v2 import questions, norm

DEFAULT_INPUT="local_only/fresh_retrieval/FRESH_QUESTIONS_FROM_AI.csv"
DEFAULT_STAGED="local_only/fresh_retrieval_screened34"

def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def audit(project=".",source=DEFAULT_INPUT, original_dir="local_only/fresh_retrieval"):
    root=Path(project).resolve()
    kit_path=root/original_dir/"AUTHOR_KIT.csv"
    source_path=Path(source)
    if not source_path.is_absolute():source_path=root/source_path
    kh,kit=_read_csv(kit_path)
    rh,rows=_read_csv(source_path)
    problems=[]
    if kh!=list(AUTHOR_FIELDS):problems.append("Original author kit columns invalid")
    if rh!=list(RETURN_FIELDS):problems.append("Review response column names/order invalid")
    if len(kit)!=36 or len(rows)!=36:problems.append("Expected exactly 36 attempted targets and 36 reviewer rows")
    ref={x["question_id"]:x for x in kit}
    ids=[x["question_id"] for x in rows]
    if len(set(ids))!=len(ids) or set(ids)!=set(ref):
        problems.append("Duplicate/missing/extra question_id")
    historical=[" ".join(str(q.get("question","")).lower().split()) for q in questions(root)]
    excluded=[]
    valid=[]
    for row in rows:
        key=row["question_id"]
        if key not in ref:continue
        if any(row.get(k)!=ref[key].get(k) for k in AUTHOR_FIELDS):
            problems.append(key+": original selected target/paper fields changed")
            continue
        q=" ".join(row.get("question","").strip().split())
        url=row.get("source_url","").strip()
        access=row.get("evidence_access","").strip()
        note=row.get("evidence_locator","").strip()
        rationale=row.get("question_rationale","").strip()
        if not q and not url and not access:
            if (note.startswith("SUPPORT FAILURE:") and
                    rationale.startswith("UNSUPPORTED SOURCE:") and
                    bool(row.get("author_id","").strip())):
                excluded.append({"question_id":key,"target_name":row["target_name"],
                                 "associated_paper_title":row["paper_title"],
                                 "reason":"ORIGINAL_SOURCE_NOT_VERIFIABLE_PRE_RANK",
                                 "reviewer_rationale":rationale})
            else:
                problems.append(key+": incomplete fields without explicit original source verification failure")
            continue
        issues=[]
        if not 55<=len(q)<=450 or not q.endswith("?"):
            issues.append("question must have 55-450 characters and end in ?")
        if norm(row["target_name"]) in norm(q):
            issues.append("normalized target name leaks into question")
        if any(difflib.SequenceMatcher(None,q.lower(),h).ratio()>=.82 for h in historical):
            issues.append("near-duplicate historical benchmark question")
        if not re.match(r"^https?://\S+$",url):issues.append("source URL invalid/missing")
        if access not in ("FULL_TEXT","ABSTRACT_ONLY"):issues.append("invalid evidence access")
        if len(note)<6:issues.append("source evidence locator missing")
        if len(rationale)<20:issues.append("question rationale missing")
        if not row.get("author_id","").strip():issues.append("actual AI author/model identifier missing")
        try:
            if int(row["paper_year"])>2025:issues.append("associated publication after cutoff")
        except ValueError:issues.append("invalid associated source year")
        if issues:problems.append(key+": "+"; ".join(issues))
        else:valid.append(row)
    if len(valid)+len(excluded)!=len(rows):
        problems.append("Not all 36 attempted original targets accounted for")
    if len(excluded)>3:problems.append("More than 3 source exclusions: require new protocol")
    return {
        "schema":"chronohyper_prerank_source_screen_v1",
        "n_attempted":len(kit),"n_returned":len(rows),
        "n_eligible_format":len(valid),"n_documented_excluded":len(excluded),
        "excluded":sorted(excluded,key=lambda x:x["question_id"]),
        "validation_errors":problems,
        "original_author_kit_sha256":_sha(kit_path),
        "original_response_sha256":_sha(source_path),
        "same_original_corpus":True,
        "original_fulltext_truth_independently_verified":False,
        "all_36_targets_retained_in_audit":True,
    },valid

def main():
    p=argparse.ArgumentParser(description=__doc__)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--inspect",action="store_true")
    mode.add_argument("--stage",action="store_true")
    p.add_argument("--project",default=".")
    p.add_argument("--source",default=DEFAULT_INPUT)
    p.add_argument("--directory",default=DEFAULT_STAGED)
    args=p.parse_args()
    report,valid=audit(args.project,args.source)
    print(json.dumps(report,indent=2,ensure_ascii=False))
    if not args.stage:return
    if report["validation_errors"]:
        raise ValueError("Source screening contains other problems; do NOT stage")
    if not report["excluded"]:
        raise ValueError("All 36 rows valid; use original folder, not screened subset")
    root=Path(args.project).resolve()
    folder=Path(args.directory)
    if not folder.is_absolute():folder=root/folder
    if any(folder.exists() and list(folder.iterdir()) for _ in (0,)):
        raise FileExistsError("Screened benchmark directory already used: "+str(folder))
    folder.mkdir(parents=True,exist_ok=True)
    ordered=sorted(valid,key=lambda x:x["question_id"])
    _write_csv(folder/"AUTHOR_KIT.csv",AUTHOR_FIELDS,
               [{k:r[k] for k in AUTHOR_FIELDS} for r in ordered])
    _write_csv(folder/"FRESH_QUESTIONS_FROM_AI.csv",RETURN_FIELDS,ordered)
    _save_json(folder/"pre_rank_source_screen.json",report)
    print("STAGED",len(ordered),"valid of",report["n_attempted"],
          "sampled targets; exclusions documented BEFORE scoring:",folder)

if __name__=="__main__":main()
