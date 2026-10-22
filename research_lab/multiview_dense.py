"""Independent BGE-M3 multi-view DEVELOPMENT experiment with candidate-recall audit.

Rank NEVER reads Gold. All 34 previous queries are ALREADY inspected and must
never be represented as a fresh, independently confirmed test. Original
rankings, locked hierarchy, metrics.json, selected model and report untouched.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import statistics
import time
from pathlib import Path

import numpy as np
from research_lab.advanced_retrieval import (
    DENSE_MODEL, CUTOFF, FRESH_GOLD, FRESH_QUERIES,
    _as_top, _csv, _dense_encoder, _argsort, native_context, reciprocal_fusion,
)
from research_lab.retrieval_v2 import index, norm
from research_lab.retrieval_frontier import _rank_hash

OUT = "local_only/multiview_dense_development"
ARMS = ("context", "name", "paper", "rrf_3view", "max_cosine_3view")
KS = (1, 5, 10, 20, 50, 100)


def build_views(entries, contexts):
    """Separate source-grounded entity views with no synthetic definitions.

    The context view exactly matches the previous experimental BGE dense
    documents. paper view contains only the original source titles;
    name view only canonical names and types. This permits an ablation
    without introducing unverified 'scientific descriptions'.
    """
    if len(contexts) != len(entries):
        raise ValueError("Context and canonical entity index lengths disagree")
    result = {"context": list(contexts), "name": [], "paper": []}
    for e in entries:
        name = str(e["name"]).strip()
        typ = str(e["type"]).strip()
        # old index repeats the name thrice, followed by type and dated titles
        raw = str(e["text"])
        prefix = name + " "
        prefix3 = prefix * 3
        source_part = raw[len(prefix3):] if raw.startswith(prefix3) else raw
        if source_part.startswith(typ + " "):
            source_part = source_part[len(typ) + 1:]
        source_part = source_part.strip()
        result["name"].append(f"Scientific {typ}: {name}.")
        result["paper"].append(
            f"Scientific {typ}: {name}. Original paper title evidence: {source_part}."
            if source_part else f"Scientific {typ}: {name}. "
            "No dated source title recorded for this entity."
        )
    return result


def topk(scores, k):
    arr = np.asarray(scores, dtype=np.float32)
    if arr.ndim != 1 or not np.isfinite(arr).all():
        raise ValueError("Expected finite one-dimensional similarity scores")
    return sorted(range(arr.size), key=lambda i: (-float(arr[i]), i))[:k]


def three_view_orders(scores):
    """Predeclared unsupervised fusion; no gold-dependent weights."""
    required = ("context", "name", "paper")
    if set(scores) != set(required):
        raise ValueError("Expected context, name and paper view scores")
    length = len(scores["context"])
    if any(len(scores[v]) != length for v in required) or not length:
        raise ValueError("Similarity vectors differ in length")
    singles = {v: topk(scores[v], length) for v in required}
    rrf = reciprocal_fusion([singles[v] for v in required])
    maximum = np.maximum.reduce([np.asarray(scores[v]) for v in required])
    return {**singles, "rrf_3view": rrf,
            "max_cosine_3view": topk(maximum, length)}


def rank(project=".", questions=FRESH_QUERIES, out=OUT,
         device="cuda", model_name=DENSE_MODEL, batch_size=24,
         top_export=100):
    root = Path(project).resolve()
    qpath = Path(questions)
    if not qpath.is_absolute():
        qpath = root / qpath
    destination = Path(out)
    if not destination.is_absolute():
        destination = root / destination
    destination.mkdir(parents=True, exist_ok=True)
    file = destination / "rankings.json"
    if file.exists():
        raise FileExistsError("Preserve existing multiview ranking evidence")
    qs = _csv(qpath)
    if len(qs) != 34:
        raise ValueError("Historical DEVELOPMENT run requires the 34 original query IDs")
    entries, _, _, _, _, _, _, _ = index(root, CUTOFF)
    views = build_views(entries, native_context(root, entries, CUTOFF))
    model = _dense_encoder(model_name, device)
    vectors = {}
    start = time.perf_counter()
    for view, texts in views.items():
        vectors[view] = np.asarray(model.encode(
            texts, batch_size=batch_size, show_progress_bar=True,
            normalize_embeddings=True), dtype=np.float32)
        if vectors[view].ndim != 2 or vectors[view].shape[0] != len(entries) or (
                not np.isfinite(vectors[view]).all()):
            raise ValueError("Invalid pretrained BGE view embedding for " + view)
    offline_build_s = time.perf_counter() - start
    rows = []
    for q in qs:
        begin = time.perf_counter()
        qvec = np.asarray(model.encode(
            [q["question"]], normalize_embeddings=True),
            dtype=np.float32).reshape(-1)
        scores = {v: arr @ qvec for v, arr in vectors.items()}
        ranked = three_view_orders(scores)
        result = {}
        for arm, ids in ranked.items():
            result[arm] = [
                {"name": entries[i]["name"],
                 "type": entries[i]["type"],
                 "normalized": entries[i]["normalized"],
                 "rank": j+1}
                for j, i in enumerate(ids[:top_export])]
        rows.append({"question_id": q["question_id"],
                     "views": result,
                     "online_time_s_with_query_encoding": time.perf_counter() - begin})
    data = {
        "schema": "chronohyper_multiview_bge_development_v1",
        "stage": "POSTHOC_ALREADY_VIEWED_34_NOT_CONFIRMATORY",
        "gold_accessed_during_ranking": False,
        "historical_frozen_model_unchanged": True,
        "n_queries": len(rows),
        "n_indexed_canonical_entities": len(entries),
        "cutoff": CUTOFF,
        "query_file_sha256": hashlib.sha256(qpath.read_bytes()).hexdigest(),
        "dense_model": model_name,
        "views": list(views),
        "arms": list(ARMS),
        "unsupervised_rrf_weighting": "1/3 each, rank-based no gold",
        "candidate_export_depth": top_export,
        "offline_embedding_build_s": offline_build_s,
        "method_limits": [
            "Same Constructor corpus and questions already inspected; developmental only",
            "No new full texts, summaries, inferred definitions, external paper source, or LLM generation",
            "Paper titles and entity names may provide weak explanatory grounding",
            "Cross-encoder deliberately excluded due to observed old development failure",
            "Future genuinely new source-validated questions necessary for confirmation",
        ],
        "results": rows,
    }
    data["ranking_sha256"] = _rank_hash(data)
    file.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"rankings": str(file),
                      "ranking_sha256": data["ranking_sha256"],
                      "n_questions": len(rows),
                      "gold_opened": False}, indent=2))
    return data


def score(project=".", directory=OUT, gold=FRESH_GOLD):
    root = Path(project).resolve()
    folder = Path(directory)
    if not folder.is_absolute():
        folder = root / folder
    ranked = json.loads((folder / "rankings.json").read_text(encoding="utf-8"))
    if ranked.get("schema") != "chronohyper_multiview_bge_development_v1":
        raise ValueError("Wrong ranking schema")
    if ranked.get("ranking_sha256") != _rank_hash(ranked):
        raise ValueError("Ranking digest changed; private Gold must remain unread")
    if ranked.get("stage") != "POSTHOC_ALREADY_VIEWED_34_NOT_CONFIRMATORY" or (
            ranked.get("gold_accessed_during_ranking") is not False):
        raise ValueError("Ranking stage is not gold-blind development")
    out = folder / "score_DEVELOPMENT_ONLY.json"
    if out.exists():
        raise FileExistsError("Preserve earlier scored multiview experiment")
    original_queries = root / FRESH_QUERIES
    if (not original_queries.is_file() or
            hashlib.sha256(original_queries.read_bytes()).hexdigest() !=
            ranked.get("query_file_sha256")):
        raise ValueError("Local frozen 34-query text differs from GPU ranking input")
    private = Path(gold)
    if not private.is_absolute():
        private = root / private
    with private.open(encoding="utf-8-sig", newline="") as stream:
        gold_rows = list(csv.DictReader(stream))
    ref = {r["question_id"]: (r["target_type"], norm(r["target_name"]))
           for r in gold_rows}
    results = ranked["results"]
    if len(ref) != len(gold_rows) or len(ref) != 34 or len(results) != 34 or (
            {r["question_id"] for r in results} != set(ref)):
        raise ValueError("Gold and all 34 ranked IDs must match exactly")
    arms = ranked["arms"]
    if set(arms) != set(ARMS):
        raise ValueError("Arms were modified")
    topdepth = int(ranked["candidate_export_depth"])
    if topdepth < max(KS):
        raise ValueError("Top-K ranking is too shallow for declared recall measures")
    metrics = {a: {k: [] for k in KS} for a in arms}
    reciprocal = {a: [] for a in arms}
    hits_by_query = {}
    for row in results:
        target = ref[row["question_id"]]
        hits_by_query[row["question_id"]] = {}
        for arm in arms:
            candidates = row["views"][arm]
            if len(candidates) < max(KS):
                raise ValueError("Truncated top-100 candidates on " + row["question_id"])
            items = [(c["type"], c["normalized"]) for c in candidates]
            first = items.index(target)+1 if target in items else None
            hits_by_query[row["question_id"]][arm] = first
            reciprocal[arm].append(1/first if first and first <=5 else 0.0)
            for k in KS:
                metrics[arm][k].append(int(first is not None and first <=k))
    summary = {
        "schema": "chronohyper_multiview_bge_scored_development_v1",
        "stage": ranked["stage"],
        "n_queries": len(results),
        "rankings_sha256_verified": ranked["ranking_sha256"],
        "model": ranked["dense_model"],
        "gold_opened_during_ranking": False,
        "not_a_new_unseen_test": True,
        "correct_at_k_counts": {
            a: {f"hit_at_{k}": sum(metrics[a][k]) for k in KS}
            for a in arms},
        "mrr_at5": {a: statistics.mean(reciprocal[a]) for a in arms},
        "per_question_rank_LOCAL_PRIVATE": hits_by_query,
        "no_verified_accuracy_gain_claim": True,
        "limits": [
            "This 34-query evaluation is post-hoc development after previous score exposure",
            "The best arm on these 34 cannot be called an independently tested model",
            "Candidate recall improves only when correct entities are in indexed candidates",
        ],
    }
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k: v for k,v in summary.items()
                      if k != "per_question_rank_LOCAL_PRIVATE"}, indent=2))
    return summary


def main():
    p = argparse.ArgumentParser(description=__doc__)
    action = p.add_mutually_exclusive_group(required=True)
    action.add_argument("--rank", action="store_true")
    action.add_argument("--score", action="store_true")
    p.add_argument("--project", default=".")
    p.add_argument("--questions", default=FRESH_QUERIES)
    p.add_argument("--out", default=OUT)
    p.add_argument("--device", default="cuda")
    p.add_argument("--model", default=DENSE_MODEL)
    p.add_argument("--batch-size", type=int, default=24)
    p.add_argument("--top-export", type=int, default=100)
    args = p.parse_args()
    if args.rank:
        rank(args.project, args.questions, args.out, args.device,
             args.model, args.batch_size, args.top_export)
    else:
        score(args.project, args.out)


if __name__ == "__main__":
    main()
