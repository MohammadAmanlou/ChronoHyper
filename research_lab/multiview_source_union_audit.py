"""Read-only diagnosis of already-scored BGE multi-view candidate coverage.

No GPU. No private Gold file is opened: consumes a pre-existing score file
generated after ranking was frozen. The score is already post-hoc development;
oracle unions and source-view allocation diagnostics are NOT achievable
performance or independent-test estimates. Never overwrites existing files.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import statistics
from pathlib import Path
from research_lab.retrieval_frontier import _rank_hash
from research_lab.retrieval_v2 import norm

DEFAULT = "local_only/multiview_dense_development"
ARMS = ("context", "name", "paper", "rrf_3view", "max_cosine_3view")
SOURCES = ("context", "name", "paper")
KS = (1, 5, 10, 20, 50, 100)
POOL_BUDGETS = (100, 200, 300)

def key(item):
    return str(item["type"]), norm(item["normalized"])

def fixed_pool(viewlists, budget):
    """Gold-free, balanced round-robin candidate selection.

    Use each of the three actual source views at depths 1..100; this
    diagnoses recoverability without ever using reference labels to build
    the pool or choose a ranking.
    """
    if budget not in POOL_BUDGETS:
        raise ValueError("Unsupported fixed pool size")
    pool, seen = [], set()
    for depth in range(100):
        for arm in SOURCES:
            item = viewlists[arm][depth]
            identity = key(item)
            if identity in seen:
                continue
            seen.add(identity)
            pool.append(item)
            if len(pool) == budget:
                return pool
    return pool

def analyze(rank, score):
    if rank.get("schema") != "chronohyper_multiview_bge_development_v1":
        raise ValueError("Wrong gold-blind multiview schema")
    if rank.get("ranking_sha256") != _rank_hash(rank):
        raise ValueError("Ranking SHA-256 does not match frozen artifact")
    if rank.get("stage") != "POSTHOC_ALREADY_VIEWED_34_NOT_CONFIRMATORY":
        raise ValueError("Source is not post-hoc development")
    if rank.get("gold_accessed_during_ranking") is not False:
        raise ValueError("Ranker did not assert gold isolation")
    if score.get("schema") != "chronohyper_multiview_bge_scored_development_v1":
        raise ValueError("Unexpected scored development schema")
    if score.get("not_a_new_unseen_test") is not True:
        raise ValueError("Scored source is incorrectly labelled")
    if score.get("rankings_sha256_verified") != rank["ranking_sha256"]:
        raise ValueError("Rank and score describe different artifacts")
    rows = rank["results"]
    per = score.get("per_question_rank_LOCAL_PRIVATE", {})
    qids = [r["question_id"] for r in rows]
    if len(qids) != 34 or len(set(qids)) != 34 or set(qids) != set(per):
        raise ValueError("Exact original 34 question IDs required")
    if set(rank.get("arms", [])) != set(ARMS) or rank.get("candidate_export_depth") != 100:
        raise ValueError("Missing full 5-arm top-100 ranks")

    counts = {a: {str(k): 0 for k in KS} for a in ARMS}
    possible = {str(k):0 for k in KS}
    pooled = {str(k):0 for k in POOL_BUDGETS}
    rescued = {str(k):[] for k in KS}
    missing_all = []
    per_question = {}
    pool_lengths = []
    for row in rows:
        qid = row["question_id"]
        views = row["views"]
        if set(views) != set(ARMS) or any(len(views[a]) != 100 for a in ARMS):
            raise ValueError("Incomplete top-100 candidates: " + qid)
        actual = per[qid]
        if set(actual) != set(ARMS):
            raise ValueError("Incomplete scored arms: " + qid)
        known_gold = set()
        for a in ARMS:
            value = actual[a]
            if value is not None and (type(value) is not int or not 1 <= value <= 100):
                raise ValueError("Illegal gold rank: " + qid)
            if value is not None:
                known_gold.add(key(views[a][value - 1]))
            if len({key(x) for x in views[a]}) != 100:
                raise ValueError("Duplicated canonical candidate: " + qid + " " + a)
            for k in KS:
                if value is not None and value <= k:
                    counts[a][str(k)] += 1
        if len(known_gold) > 1:
            raise ValueError("Scored answer does not refer to one typed canonical entity: " + qid)
        identity = next(iter(known_gold)) if known_gold else None
        if identity is None:
            missing_all.append(qid)
        ranks = [actual[a] for a in ARMS if actual[a] is not None]
        best = min(ranks) if ranks else None
        for k in KS:
            if best is not None and best <= k:
                possible[str(k)] += 1
                if actual["rrf_3view"] is None or actual["rrf_3view"] > k:
                    rescued[str(k)].append(qid)
        pools = {str(k):fixed_pool(views, k) for k in POOL_BUDGETS}
        positions = {}
        for budget, pool in pools.items():
            ids = [key(x) for x in pool]
            positions[budget] = (ids.index(identity)+1) if identity in ids else None
            if positions[budget] is not None:
                pooled[budget] += 1
        pool_lengths.append(len(pools["300"]))
        per_question[qid] = {
            "individual_arm_gold_ranks_LOCAL_ONLY": actual,
            "best_observed_rank_in_any_arm": best,
            "correct_candidate_in_fixed_gold_blind_pool_at": positions,
            "absent_from_all_five_exported_top100": identity is None,
        }

    previous_counts = score.get("correct_at_k_counts",{})
    for arm in ARMS:
        for k in KS:
            recorded=previous_counts.get(arm,{}).get("hit_at_"+str(k))
            if recorded != counts[arm][str(k)]:
                raise ValueError("Existing score is internally inconsistent: "
                                 + arm + "@" + str(k))
    return {
        "schema":"chronohyper_multiview_source_union_diagnostic_v1",
        "research_stage":"POSTHOC_DEVELOPMENT_NOT_FRESH_CONFIRMATION",
        "frozen_rank_sha256_verified":rank["ranking_sha256"],
        "n_questions":34,
        "no_new_gpu_inference":True,
        "no_original_gold_file_opened":True,
        "individual_hit_counts_at_k_verified":counts,
        "best_of_five_oracle_visible_at_k_NOT_AN_ALGORITHM":possible,
        "oracle_discoveries_not_in_rrf_at_k_DEVELOPMENT_ONLY":rescued,
        "fixed_gold_blind_3view_round_robin_pool_RECALL_upper_k":pooled,
        "fixed_pool_300_mean_actual_size":statistics.mean(pool_lengths),
        "missing_from_ALL_exported_top100":missing_all,
        "missing_from_all_count":len(missing_all),
        "per_question_PRIVATE":per_question,
        "limitations":[
            "Best-of-five oracle consults the reference answer, and cannot be deployed as a selector",
            "Fixed pool policy is label-blind but scored retrospectively on the already-viewed 34",
            "Even full candidate pool recall cannot guarantee Hit@5",
            "Only title/name/native co-occurrence evidence was indexed, not independently verified full-paper definitions",
            "Do not use a development score as an independent generalization or model-selection result",
        ],
    }

def run(project=".", directory=DEFAULT):
    root=Path(project).resolve()
    folder=Path(directory)
    if not folder.is_absolute():
        folder=root/folder
    out=folder/"multiview_source_union_audit_LOCAL.json"
    if out.exists():
        raise FileExistsError("Preserve existing forensic diagnostic")
    rank=json.loads((folder/"rankings.json").read_text(encoding="utf-8"))
    if rank.get("ranking_sha256") != _rank_hash(rank):
        raise ValueError("Frozen ranking was modified")
    # Check original query bytes before reading even derivative gold ranks.
    local_queries=root/"local_only/fresh_retrieval_screened34/queries_only.csv"
    if (not local_queries.is_file() or
            hashlib.sha256(local_queries.read_bytes()).hexdigest() != rank.get("query_file_sha256")):
        raise ValueError("Ranked query text mismatch")
    score=json.loads((folder/"score_DEVELOPMENT_ONLY.json").read_text(encoding="utf-8"))
    result=analyze(rank,score)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",
                   encoding="utf-8")
    public={k:v for k,v in result.items()
            if k not in ("per_question_PRIVATE",
                         "oracle_discoveries_not_in_rrf_at_k_DEVELOPMENT_ONLY")}
    print(json.dumps(public,ensure_ascii=False,indent=2))
    print("Per-question private diagnostic: "+str(out))
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project",default=".")
    parser.add_argument("--directory",default=DEFAULT)
    args=parser.parse_args()
    run(args.project,args.directory)

if __name__=="__main__":
    main()
