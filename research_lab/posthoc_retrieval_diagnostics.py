"""Read-only post-hoc failure analysis of ALREADY FROZEN hybrid GPU rankings.

Uses held-back gold ONLY AFTER checking the existing ranking digest.
It does not train, rerank, download weights, or alter the original evidence.
All detailed outputs remain under ignored local_only/. This dataset was
already inspected, and all candidate policies below are DEVELOPMENT ONLY.

Important: output rankings retain only top 20 per arm, so this cannot
infer candidate@64 recall or an unseen test accuracy bound.
"""
from __future__ import annotations
import argparse
import csv
import json
import random
import statistics
from collections import Counter
from pathlib import Path

from research_lab.retrieval_frontier import _rank_hash
from research_lab.retrieval_v2 import norm

ROOT="local_only/advanced_retrieval"
GOLD="local_only/fresh_retrieval_screened34/gold_PRIVATE.csv"
OLD="local_only/fresh_retrieval_screened34/scored.json"
ARMS=("lexical","dense","hybrid_rrf","hybrid_rerank","soft_hierarchy")

def key(item):
    return str(item["type"]),norm(item["name"] if not item.get("normalized") else item["normalized"])

def identity_match(ranked,gold,k=5):
    for i,item in enumerate(ranked[:k]):
        if key(item)==gold:
            return i+1
    return None

def allocate(retrieval,layout):
    """Post-hoc, fixed deterministic no-model rerank alternatives.
    First consume each arm's allotted count; then fill from dense if
    deduplication yields fewer than 5. These are NOT fresh test results.
    """
    picked=[]
    seen=set()
    for arm,n in layout:
        if arm not in retrieval:raise ValueError("Missing arm "+arm)
        consumed=0
        for item in retrieval[arm]:
            k=key(item)
            if k in seen:continue
            seen.add(k);picked.append(item);consumed+=1
            if consumed>=n or len(picked)>=5:break
        if len(picked)>=5:break
    for arm in ("dense","lexical","hybrid_rrf"):
        for item in retrieval[arm]:
            if len(picked)>=5:break
            k=key(item)
            if k in seen:continue
            seen.add(k);picked.append(item)
    return picked[:5]

POLICIES={
    "dense_only":(("dense",5),),
    "dense4_lexical1":(("dense",4),("lexical",1)),
    "dense3_lexical2":(("dense",3),("lexical",2)),
    "dense4_rrf1":(("dense",4),("hybrid_rrf",1)),
    "dense3_rrf2":(("dense",3),("hybrid_rrf",2)),
    "dense3_lex1_rrf1":(("dense",3),("lexical",1),("hybrid_rrf",1)),
}

def _sample_ci(diffs,seed=20261022,draws=5000):
    rng=random.Random(seed)
    n=len(diffs)
    sims=sorted(sum(diffs[rng.randrange(n)] for _ in range(n))/n
                for _ in range(draws))
    return [sims[int(.025*(draws-1))],sims[int(.975*(draws-1))]]

def assess(rankings,gold_rows,old_scored=None):
    if rankings.get("schema")!="chronohyper_new_hybrid_rerank_development_v1":
        raise ValueError("Unexpected ranking experiment schema")
    if rankings.get("gold_accessed_during_ranking") is not False:
        raise ValueError("Gold isolation flag is not false")
    if rankings.get("ranking_sha256")!=_rank_hash(rankings):
        raise ValueError("Original GPU ranking SHA-256 mismatch")
    if rankings.get("stage")!="POSTHOC_AFTER_VIEWING_ORIGINAL_34_SCORE_DEVELOPMENT_ONLY":
        raise ValueError("Do not repurpose scores as a confirmatory evaluation")
    if len({r["question_id"] for r in gold_rows}) !=len(gold_rows):
        raise ValueError("Duplicated gold IDs")
    refs={r["question_id"]:(r["target_type"],norm(r["target_name"]))
          for r in gold_rows}
    rows=rankings["rankings"]
    if len(rows)!=34 or len(refs)!=34 or {r["question_id"] for r in rows}!=set(refs):
        raise ValueError("Exact 34-query frozen evaluation set required")
    by_arm={arm:[] for arm in ARMS}
    by_policy={name:[] for name in POLICIES}
    details=[]
    breakdown=Counter()
    for record in rows:
        qid=record["question_id"]
        retrieval=record["retrieval"]
        if not all(arm in retrieval for arm in ARMS):
            raise ValueError("Missing original ranked arm: "+qid)
        gold=refs[qid]
        arms={}
        for arm in ARMS:
            rank5=identity_match(retrieval[arm],gold,5)
            rank20=identity_match(retrieval[arm],gold,20)
            arms[arm]={"rank5":rank5,"rank20":rank20,
                       "hit5":int(rank5 is not None)}
            by_arm[arm].append(arms[arm]["hit5"])
        policy={}
        for name,layout in POLICIES.items():
            rank5=identity_match(allocate(retrieval,layout),gold,5)
            policy[name]={"hit5":int(rank5 is not None),
                          "rank5":rank5}
            by_policy[name].append(int(rank5 is not None))
        # A key distinction: top-20 truncation prevents proving presence
        # or absence in rerank's original 64-item candidate list.
        if arms["dense"]["hit5"] and not arms["hybrid_rerank"]["hit5"]:
            breakdown["dense_hit_lost_in_rerank_top5"]+=1
            if arms["hybrid_rrf"]["rank20"] is not None:
                breakdown["dense_hit_visible_in_rrf_top20"]+=1
            if arms["hybrid_rerank"]["rank20"] is not None:
                breakdown["dense_hit_present_but_demoted_in_rerank_top20"]+=1
            else:
                breakdown["dense_hit_not_in_rerank_top20_UNRESOLVED_CANDIDATE64"]+=1
        if arms["hybrid_rrf"]["hit5"] and not arms["hybrid_rerank"]["hit5"]:
            breakdown["rrf_hit_lost_in_rerank_top5"]+=1
        if arms["hybrid_rerank"]["hit5"] and not arms["dense"]["hit5"]:
            breakdown["rerank_only_hit"]+=1
        details.append({"question_id":qid,"target_type":gold[0],
                        "target_name_PRIVATE":next(r["target_name"]
                                                  for r in gold_rows if r["question_id"]==qid),
                        "arms":arms,"posthoc_policies":policy,
                        "top5":{a:[{"name":x["name"],"type":x["type"]}
                                    for x in retrieval[a][:5]] for a in ARMS}})
    summary={
        "schema":"chronohyper_hybrid_posthoc_failure_audit_v1",
        "experiment_stage":"POSTHOC_DEVELOPMENT_NOT_FRESH_HOLDOUT",
        "rankings_sha256_verified":rankings["ranking_sha256"],
        "n_queries":len(rows),
        "pretrained_dense_bge_m3":True,
        "rerank_candidate64_recall_measurable_from_top20":False,
        "old_model_unchanged":True,
        "arm_hit5":{a:sum(vals) for a,vals in by_arm.items()},
        "arm_hit_at5":{a:sum(vals)/len(vals) for a,vals in by_arm.items()},
        "diagnostic":dict(sorted(breakdown.items())),
        "top20_gold_visibility":{a:sum(d["arms"][a]["rank20"] is not None
                                       for d in details) for a in ARMS},
        "posthoc_fixed_allocations_HIT5_NOT_CONFIRMATORY":{
            name:sum(v) for name,v in by_policy.items()},
        "multiarm_oracle_hit5_UPPER_BOUND_NOT_AN_ALGORITHM":
            sum(any(d["arms"][a]["hit5"] for a in ARMS) for d in details),
        "limitations":[
          "Published 34-query frozen baseline must not be rewritten",
          "Gold accessed only after independently frozen GPU rankings",
          "Rerank output includes only TOP20; absence there does not prove missing in TOP64 candidate pool",
          "Post-hoc allocations use this already-inspected sample and are not independent confirmation",
          "Embedding improvements need a new untouched, source-validated question set"]
    }
    if old_scored is not None:
        original={r["question_id"]:r["scores"]["flat"]["hit5"]
                  for r in old_scored.get("per_question_local_only",[])}
        if set(original)!=set(refs):
            raise ValueError("Old frozen 34-query score IDs mismatch")
        delta=[d["arms"]["dense"]["hit5"]-original[d["question_id"]]
               for d in details]
        summary["descriptive_dense_vs_frozen_flat"]={
            "flat_legacy_hits":sum(original.values()),
            "dense_hits":sum(by_arm["dense"]),
            "paired_win":sum(x==1 for x in delta),
            "paired_loss":sum(x==-1 for x in delta),
            "paired_tie":sum(x==0 for x in delta),
            "delta":statistics.mean(delta),
            "exploratory_paired_bootstrap_95ci":_sample_ci(delta)}
    return summary,details

def run(project=".",directory=ROOT,gold=GOLD,original=OLD):
    root=Path(project).resolve()
    folder=Path(directory)
    if not folder.is_absolute():folder=root/folder
    target=folder/"posthoc_error_audit_LOCAL.json"
    if target.exists():
        raise FileExistsError("Do not overwrite local forensic audit")
    source=folder/"rankings.json"
    # Verify frozen artifact BEFORE reading hidden gold.
    rankings=json.loads(source.read_text(encoding="utf-8"))
    if rankings.get("ranking_sha256")!=_rank_hash(rankings):
        raise ValueError("Frozen ranking changed; Gold MUST remain unopened")
    gold_path=Path(gold)
    if not gold_path.is_absolute():gold_path=root/gold_path
    with gold_path.open(encoding="utf-8-sig",newline="") as f:
        gold_rows=list(csv.DictReader(f))
    past=root/original
    previous=json.loads(past.read_text(encoding="utf-8")) if past.is_file() else None
    summary,details=assess(rankings,gold_rows,previous)
    output={"summary":summary,"per_question_LOCAL_PRIVATE":details}
    target.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    print("Private per-question audit:",target)
    return summary

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project",default=".")
    p.add_argument("--directory",default=ROOT)
    p.add_argument("--gold",default=GOLD)
    p.add_argument("--original",default=OLD)
    args=p.parse_args()
    run(args.project,args.directory,args.gold,args.original)

if __name__=="__main__":main()
