"""Gold-file-free, CPU-only preflight for the next Qwen3 entity reranker run.

Uses already-scored post-hoc DEVELOPMENT ranks but DOES NOT read Gold file.
Verify source SHA and all 34 question IDs; measure the actual, fixed,
label-blind pool passed to Qwen3; never interpret this as model accuracy.
"""
from __future__ import annotations
import argparse
import json
import statistics
from pathlib import Path

from research_lab import qwen_entity_rerank as q
from research_lab.multiview_dense import ARMS as SOURCE_ARMS

ROOT = "local_only/qwen_entity_rerank_development"
OLD_SCORE = "local_only/multiview_dense_development/score_DEVELOPMENT_ONLY.json"


def audit(root: Path, data: dict, scored: dict, max_candidates: int=300):
    if scored.get("schema") != "chronohyper_multiview_bge_scored_development_v1":
        raise ValueError("Not the previously scored multiview development data")
    if scored.get("not_a_new_unseen_test") is not True:
        raise ValueError("Dataset must remain post-hoc development")
    if scored.get("rankings_sha256_verified") != data.get("ranking_sha256"):
        raise ValueError("Score and frozen source ranking SHA differ")
    past = scored.get("per_question_rank_LOCAL_PRIVATE", {})
    rows = data["results"]
    if len(rows) != 34 or len(past) != 34 or (
            {r["question_id"] for r in rows} != set(past)):
        raise ValueError("Exactly the previous frozen 34 questions required")
    if set(data.get("arms", [])) != set(SOURCE_ARMS):
        raise ValueError("Multiview source arms changed")
    if max_candidates != 300:
        raise ValueError("Preflight is for the 300-budget complete source union")
    counts = []
    hit = 0
    missing = []
    details = []
    for row in rows:
        qid = row["question_id"]
        views = row["views"]
        if any(len(views[arm]) != 100 for arm in SOURCE_ARMS):
            raise ValueError("Top100 incomplete: "+qid)
        ranks = past[qid]
        if set(ranks) != set(SOURCE_ARMS):
            raise ValueError("Missing previous rank scores: "+qid)
        seen_gold=set()
        for arm in SOURCE_ARMS:
            num=ranks[arm]
            if num is not None:
                if type(num) is not int or not 1 <= num <= 100:
                    raise ValueError("Invalid stored gold rank: "+qid)
                seen_gold.add(q.key(views[arm][num-1]))
        if len(seen_gold)>1:
            raise ValueError("Previous views disagree on target identity: "+qid)
        correct=next(iter(seen_gold)) if seen_gold else None
        pool=q.candidates(views,max_candidates)
        identities=[q.key(x) for x in pool]
        if len(identities)!=len(set(identities)):
            raise ValueError("Reranker candidate pool contains duplicates")
        counts.append(len(pool))
        pos=identities.index(correct)+1 if correct in identities else None
        hit+=int(pos is not None)
        if pos is None:
            missing.append(qid)
        details.append({"question_id":qid,
                        "source_top100_visible":correct is not None,
                        "reranker_pool_candidates":len(pool),
                        "target_position_in_UNSORTED_candidate_pool":pos})
    return {
        "schema":"chronohyper_qwen3_candidate_preflight_v1",
        "stage":"POSTHOC_DEVELOPMENT_ONLY",
        "source_rank_sha256_verified":data["ranking_sha256"],
        "model_not_run":True,
        "gold_file_opened":False,
        "n_questions":34,
        "policy":q.POOL_POLICY,
        "max_candidates":max_candidates,
        "min_actual_pool_size":min(counts),
        "mean_actual_pool_size":statistics.mean(counts),
        "max_actual_pool_size":max(counts),
        "target_present_in_gold_blind_pool_count":hit,
        "target_present_in_gold_blind_pool_rate":hit/len(rows),
        "missing":missing,
        "per_question_PRIVATE":details,
        "limitations":[
            "Pool recall only: NOT Hit@5, NOT Qwen3 accuracy",
            "The source score was already computed on 34 inspected development questions",
            "Gold is not accessed during Qwen3 ranking; the local preflight uses previously scored derivative ranks",
            "Prompt instructions and candidate descriptions may be insufficient to distinguish correct scientific answers",
            "Independent source-verified new questions are still needed for confirmation",
        ],
    }


def run(project="."):
    root=Path(project).resolve()
    _,data,_=q.read_rankings(root)
    score_path=root/OLD_SCORE
    score=json.loads(score_path.read_text(encoding="utf-8"))
    summary=audit(root,data,score)
    dest=root/ROOT/"candidate_preflight_LOCAL_PRIVATE.json"
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():
        raise FileExistsError("Preserve prior preflight output: "+str(dest))
    dest.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    pub={k:v for k,v in summary.items() if k!="per_question_PRIVATE"}
    print(json.dumps(pub,ensure_ascii=False,indent=2))
    print("Private candidate positions:",str(dest))
    return summary


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project",default=".")
    args=p.parse_args()
    run(args.project)
