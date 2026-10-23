"""Gold-blind, resumable Qwen3 exact-scientific-entity reranking research.

Inputs: FROZEN previous multiview BGE top-100 candidates and dated native
graph/index. No hidden answer keys, past score files, judge outputs, or
training labels are accessed by --rank. Previously viewed 34 queries are
POST-HOC DEVELOPMENT, not a confirmatory test. No full-text entailment claim.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import os
import statistics
from pathlib import Path
import numpy as np

from research_lab.retrieval_v2 import index, norm
from research_lab.advanced_retrieval import native_context, FRESH_QUERIES, FRESH_GOLD
from research_lab.retrieval_frontier import _rank_hash

MULTIVIEW = "local_only/multiview_dense_development/rankings.json"
OUTPUT = "local_only/qwen_entity_rerank_development"
MODEL = "Qwen/Qwen3-Reranker-0.6B"
ARMS = ("qwen_raw", "qwen_anchor1", "qwen_anchor2", "source_context", "source_rrf")
# Use the complete three genuinely distinct BGE source views. RRF and
# max-cosine are permutations of the same underlying source candidates.
# The old five-arm round-robin skipped Name depth 51..100 and might
# remove correct, already retrieved entities from the Reranker pool.
# This choice is development-only, made after inspecting prior scores.
SOURCES = ("context", "name", "paper")
POOL_POLICY = "GOLD_BLIND_FULL_CONTEXT_NAME_PAPER_TOP100_UNION_V2"
INSTRUCTION = (
    "Given a scientific research question that asks for a particular named "
    "scientific entity, judge whether the scientific entity named in the "
    "Document is the specific answer, NOT merely a related concept. The "
    "Document lists candidate names, original historical paper-title "
    "context and dated hypergraph co-mentions; co-mentions do not prove "
    "semantic relationships. Rank plausibility only, not factual certainty."
)

def key(item):
    return (str(item["type"]), norm(item["normalized"]))

def read_rankings(project, path=MULTIVIEW):
    root = Path(project).resolve()
    file = Path(path)
    if not file.is_absolute():
        file = root / file
    data = json.loads(file.read_text(encoding="utf-8"))
    if data.get("schema") != "chronohyper_multiview_bge_development_v1":
        raise ValueError("Not the frozen multiview source schema")
    if data.get("ranking_sha256") != _rank_hash(data):
        raise ValueError("Multiview ranking digest changed")
    if data.get("stage") != "POSTHOC_ALREADY_VIEWED_34_NOT_CONFIRMATORY":
        raise ValueError("Old 34 questions must remain development")
    if data.get("gold_accessed_during_ranking") is not False:
        raise ValueError("Source rankings not gold-blind")
    if int(data.get("candidate_export_depth", 0)) < 100:
        raise ValueError("Need genuine top-100 from each view")
    qfile = root / FRESH_QUERIES
    if not qfile.is_file() or hashlib.sha256(qfile.read_bytes()).hexdigest() != data.get("query_file_sha256"):
        raise ValueError("Original 34-query SHA differs from GPU source rankings")
    with qfile.open(encoding="utf-8-sig", newline="") as f:
        queries = list(csv.DictReader(f))
    if len(queries) != 34 or len({q["question_id"] for q in queries}) != 34:
        raise ValueError("Exactly 34 unique original queries required")
    source = data["results"]
    if len(source) != 34 or {x["question_id"] for x in source} != {q["question_id"] for q in queries}:
        raise ValueError("The multiview source must contain all original 34 IDs")
    for rec in source:
        if not all(len(rec["views"][v]) >= 100 for v in SOURCES):
            raise ValueError("Missing top-100 source candidate list in " + rec["question_id"])
    return root, data, {q["question_id"]:q["question"] for q in queries}

def candidates(viewlists, max_candidates=300):
    """Gold-free round-robin union; makes room for complementary source views.

    If a source view already includes an entity, retain its original first
    appearance. No target name or gold rank is consulted in this function.
    """
    if not 100 <= max_candidates <= 500:
        raise ValueError("Candidate budget must be between 100 and 500")
    if not all(v in viewlists for v in SOURCES):
        raise ValueError("Missing required BGE source arm")
    # Include ALL source-view top100 entities before reranking; the
    # gold-blind pool is the complete de-duplicated 3-view union and
    # has at most 300 candidates. Do NOT filter Name at depth 50.
    seen = set()
    ordered = []
    for r in range(100):
        for v in SOURCES:
            item = viewlists[v][r]
            identity = key(item)
            if identity not in seen:
                seen.add(identity)
                ordered.append(item)
                if len(ordered) >= max_candidates:
                    return ordered
    return ordered
    return ordered

def make_docs(entries, contexts):
    """Index-resolved typed candidates: real titles and honest co-mentions."""
    if len(entries) != len(contexts):
        raise ValueError("Graph and contexts disagree")
    mapping={}
    for e, full in zip(entries, contexts):
        ident = (e["type"], e["normalized"])
        # Description is already bounded by name/type/title/co-mentions.
        # The canonical name and true source paper titles appear first.
        prefix = str(e["name"]) + " "
        raw = str(e["text"])
        source = raw[len(prefix)*3:] if raw.startswith(prefix*3) else raw
        short = (
            f"Candidate entity: {e['name']}. Scientific entity type: {e['type']}. "
            f"Published historical source paper-title context: {source[:450]}. "
            f"Additional source-dated co-mentioned graph entities (not "
            f"verified claims of functionality): {full[-500:]}"
        )
        if ident in mapping:
            raise ValueError("Duplicate canonical typed target")
        mapping[ident]=short
    return mapping

def order_candidates(items,scores):
    scores = np.asarray(scores).reshape(-1)
    if len(scores) != len(items) or not np.isfinite(scores).all():
        raise ValueError("Invalid non-finite or missing reranker scores")
    ordered = sorted(range(len(items)),
                     key=lambda i:(-float(scores[i]),key(items[i])))
    return [items[i] for i in ordered]

def anchored(items, base, n):
    """Stability comparator with predetermined dense anchors; no gold."""
    if n not in (1,2):
        raise ValueError("Only predefined anchor counts 1 and 2")
    pinned = {key(i) for i in base[:n]}
    return list(base[:n]) + [i for i in items if key(i) not in pinned]

def _as_output(items, max_n=100):
    return [{"name":r["name"],"type":r["type"],
             "normalized":r["normalized"],"rank":i+1}
            for i,r in enumerate(items[:max_n])]

def _checkpoint_write(path,data):
    tmp=path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    os.replace(tmp,path)

def _build_model(model_name,device,max_length):
    from sentence_transformers import CrossEncoder
    return CrossEncoder(model_name, device=device, max_length=max_length,
                        prompts={"entity":INSTRUCTION},
                        default_prompt_name="entity")

def rank(project=".", source=MULTIVIEW, out=OUTPUT,model_name=MODEL,
         device="cuda", batch_size=4, max_length=512,max_candidates=300):
    root, data, questions = read_rankings(project, source)
    folder = Path(out)
    if not folder.is_absolute():folder=root/folder
    folder.mkdir(parents=True,exist_ok=True)
    final=folder/"rankings.json"
    checkpoint=folder/"checkpoint_GOLD_BLIND.json"
    if final.exists():
        raise FileExistsError("The final Qwen rerank results are frozen; no overwrite")
    entries, *_ = index(root, 2025)
    desc=make_docs(entries,native_context(root,entries,2025))
    source_sha=data["ranking_sha256"]
    if checkpoint.exists():
        state=json.loads(checkpoint.read_text(encoding="utf-8"))
        if (state.get("source_multiview_sha") != source_sha
                or state.get("model")!=model_name
                or state.get("max_candidates") != max_candidates
                or state.get("max_length") != max_length
                or state.get("candidate_policy") != POOL_POLICY
                or state.get("prompt_sha256") != hashlib.sha256(INSTRUCTION.encode()).hexdigest()):
            raise ValueError("Incompatible checkpoint; do not mix experiments")
    else:
        state={"source_multiview_sha":source_sha,
               "model":model_name,
               "max_candidates":max_candidates,
               "max_length":max_length,
               "candidate_policy":POOL_POLICY,
               "prompt_sha256":hashlib.sha256(INSTRUCTION.encode()).hexdigest(),
               "completed":{}}
    model=_build_model(model_name,device,max_length)
    for row in data["results"]:
        qid=row["question_id"]
        if qid in state["completed"]:
            continue
        pool=candidates(row["views"],max_candidates)
        missing=[key(x) for x in pool if key(x) not in desc]
        if missing:
            raise ValueError("Candidate identity not found in 2025 canonical index: "+repr(missing[:2]))
        query=questions[qid]
        pairs=[(query,desc[key(item)]) for item in pool]
        raw=model.predict(pairs,batch_size=batch_size,show_progress_bar=False)
        ordered=order_candidates(pool,raw)
        dense=row["views"]["context"]
        state["completed"][qid]={
            "question_id":qid,
            "candidate_pool_n":len(pool),
            "candidate_pool_first100":_as_output(pool),
            "outputs":{
                "qwen_raw":_as_output(ordered),
                "qwen_anchor1":_as_output(anchored(ordered,dense,1)),
                "qwen_anchor2":_as_output(anchored(ordered,dense,2)),
                "source_context":_as_output(dense),
                "source_rrf":_as_output(row["views"]["rrf_3view"]),
            }}
        _checkpoint_write(checkpoint,state)
        print("Saved gold-blind Qwen reranking",qid,
              "candidates",len(pool),flush=True)
    finalrows=[state["completed"][x["question_id"]] for x in data["results"]]
    doc={
       "schema":"chronohyper_qwen_entity_rerank_development_v1",
       "stage":"POSTHOC_ALREADY_INSPECTED_34_NOT_CONFIRMATORY",
       "source_multiview_sha":source_sha,
       "gold_read_during_rank":False,
       "n_questions":len(finalrows),
       "n_canonical_entities":len(entries),
       "model":model_name,"model_instruction_sha256":state["prompt_sha256"],
       "max_candidates":max_candidates,"max_length":max_length,
       "batch_size":batch_size,
       "candidate_policy":POOL_POLICY,
       "arms":list(ARMS),
       "limits":[
         "No full-text paper passages were available; names, titles and co-mentions only",
         "BGE and Qwen results are post-hoc development on 34 seen questions",
         "Historical model, report, 34 frozen results unchanged",
         "A pretrained cross-encoder is not a fact checker; may hurt exact entity retrieval",
         "A source-validated new holdout is mandatory for generalization claims"],
       "results":finalrows}
    doc["ranking_sha256"]=_rank_hash(doc)
    final.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"frozen_rankings":str(final),
                      "n_questions":len(finalrows),
                      "sha256":doc["ranking_sha256"],
                      "gold_used":False},indent=2))

def score(project=".",out=OUTPUT,gold=FRESH_GOLD):
    root=Path(project).resolve()
    folder=Path(out)
    if not folder.is_absolute():folder=root/folder
    ranked=json.loads((folder/"rankings.json").read_text(encoding="utf-8"))
    if ranked.get("ranking_sha256")!=_rank_hash(ranked):
        raise ValueError("Frozen rerank digest mismatch; private Gold not opened")
    if ranked.get("schema")!="chronohyper_qwen_entity_rerank_development_v1":
        raise ValueError("Invalid rerank artifact")
    if ranked.get("stage")!="POSTHOC_ALREADY_INSPECTED_34_NOT_CONFIRMATORY":
        raise ValueError("Unrecognized development stage")
    if ranked.get("gold_read_during_rank") is not False:
        raise ValueError("Ranking stage has not preserved Gold isolation")
    _,source,_=read_rankings(root)
    if ranked.get("source_multiview_sha")!=source["ranking_sha256"]:
        raise ValueError("Multiview source snapshot mismatch")
    output=folder/"score_DEVELOPMENT_ONLY.json"
    if output.exists():raise FileExistsError("Preserve existing Qwen score result")
    path=Path(gold)
    if not path.is_absolute():path=root/path
    with path.open(encoding="utf-8-sig",newline="") as f:
        goldrows=list(csv.DictReader(f))
    goldmap={x["question_id"]:(x["target_type"],norm(x["target_name"])) for x in goldrows}
    rows=ranked["results"]
    if len(goldmap)!=34 or len(goldrows)!=34 or len(rows)!=34 or {x["question_id"] for x in rows}!=set(goldmap):
        raise ValueError("Gold rows or reranked IDs mismatch")
    counts={a: {k:0 for k in (1,5,10,20,100)} for a in ARMS}
    rr={a:[] for a in ARMS}
    pool_count=0
    per=[]
    for row in rows:
        ref=goldmap[row["question_id"]]
        outcomes={}
        # Full candidate pool is not exported; top100 visibility is NOT pool recall.
        for a in ARMS:
            docs=row["outputs"][a]
            if len(docs)!=100:raise ValueError("Truncated ranked outputs")
            identities=[key(x) for x in docs]
            rank1=(identities.index(ref)+1) if ref in identities else None
            outcomes[a]=rank1
            rr[a].append(1/rank1 if rank1 is not None and rank1<=5 else 0.0)
            for k in counts[a]:
                counts[a][k]+=int(rank1 is not None and rank1<=k)
        per.append({"question_id":row["question_id"],"rank":outcomes})
    summary={
      "schema":"chronohyper_qwen_reranker_scored_development_v1",
      "ranking_sha256_verified":ranked["ranking_sha256"],
      "n_questions":34,"gold_was_not_read_during_ranking":True,
      "research_stage":"POSTHOC_NOT_A_FRESH_HOLDOUT",
      "method":ranked["model"],"topk_hit_counts":counts,
      "mrr_at5":{a:statistics.mean(rr[a]) for a in ARMS},
      "per_question_LOCAL_ONLY":per,
      "unobserved_candidate_pool_recall_not_fabricated":True,
      "original_frozen_results_unchanged":True,
    }
    output.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k!="per_question_LOCAL_ONLY"},indent=2))
    return summary


def _paired_delta(a_ranks, b_ranks, k=5):
    """Pure post-hoc matched-query comparison: not an independent significance test."""
    from math import comb
    if len(a_ranks) != len(b_ranks) or not a_ranks:
        raise ValueError("Paired ranks must have identical nonempty length")
    win=loss=tie=0
    for aa,bb in zip(a_ranks,b_ranks):
        hit_a=aa is not None and aa <=k
        hit_b=bb is not None and bb <=k
        if hit_a and not hit_b:win+=1
        elif not hit_a and hit_b:loss+=1
        else:tie+=1
    n=win+loss
    # Exact unadjusted two-sided discordant-pair symmetry test.
    # This is merely descriptive after multiple inspected development variants.
    p=min(1.0, 2.0*sum(comb(n,i) for i in range(min(win,loss)+1))/(2**n)) if n else 1.0
    return {"qwen_better":win,"qwen_worse":loss,"tie":tie,
            "hit_delta":(win-loss)/len(a_ranks),
            "two_sided_exact_discordant_p_EXPLORATORY":p}


def compare_scored(project=".", out=OUTPUT):
    """CPU only. Existing local Qwen scores vs prior BGE, without reopening Gold.

    Does NOT modify existing scored artifacts. The output is private and
    post-hoc development, never a new held-out evaluation.
    """
    root=Path(project).resolve()
    folder=Path(out)
    if not folder.is_absolute():folder=root/folder
    target=folder/"paired_comparison_DEVELOPMENT_ONLY.json"
    if target.exists():
        raise FileExistsError("Keep previous paired audit unchanged")
    source_root, source_rank, _ = read_rankings(root)
    qwen_rank=json.loads((folder/"rankings.json").read_text(encoding="utf-8"))
    qwen_scores=json.loads((folder/"score_DEVELOPMENT_ONLY.json").read_text(encoding="utf-8"))
    source_scores=json.loads((root/"local_only/multiview_dense_development/score_DEVELOPMENT_ONLY.json").read_text(encoding="utf-8"))
    if qwen_rank.get("ranking_sha256") != _rank_hash(qwen_rank):
        raise ValueError("Frozen Qwen ranking SHA mismatch")
    if qwen_rank.get("schema") != "chronohyper_qwen_entity_rerank_development_v1":
        raise ValueError("Qwen ranking schema unknown")
    if qwen_rank.get("source_multiview_sha") != source_rank["ranking_sha256"]:
        raise ValueError("Qwen rankings not from original source snapshot")
    if qwen_scores.get("schema") != "chronohyper_qwen_reranker_scored_development_v1" or (
            qwen_scores.get("ranking_sha256_verified") != qwen_rank["ranking_sha256"]):
        raise ValueError("Local Qwen score does not match frozen Qwen rankings")
    if source_scores.get("schema") != "chronohyper_multiview_bge_scored_development_v1" or (
            source_scores.get("rankings_sha256_verified") != source_rank["ranking_sha256"]):
        raise ValueError("Source score and source ranking hashes disagree")
    if qwen_scores.get("research_stage") != "POSTHOC_NOT_A_FRESH_HOLDOUT" or (
            source_scores.get("not_a_new_unseen_test") is not True):
        raise ValueError("Development status must remain explicit")
    qrows=qwen_scores["per_question_LOCAL_ONLY"]
    source_by_id=source_scores["per_question_rank_LOCAL_PRIVATE"]
    qids=[x["question_id"] for x in qrows]
    if len(qids)!=34 or len(set(qids))!=34 or set(qids)!=set(source_by_id):
        raise ValueError("Exactly the 34 previously scored matching IDs required")
    if set(qids)!={x["question_id"] for x in qwen_rank["results"]}:
        raise ValueError("Ranked question IDs differ from scored question IDs")
    comparisons={a:[] for a in ("qwen_raw","qwen_anchor1","qwen_anchor2")}
    base=[]
    private=[]
    oracle5=0
    for entry in qrows:
        qid=entry["question_id"]
        ranks=entry["rank"]
        if set(ranks)!=set(ARMS):
            raise ValueError("Qwen score arms incomplete: "+qid)
        source=source_by_id[qid]
        if ranks["source_context"] != source["context"] or (
                ranks["source_rrf"] != source["rrf_3view"]):
            raise ValueError("Frozen BGE baselines changed in Qwen evaluation: "+qid)
        br=source["context"]
        base.append(br)
        for a in comparisons:
            comparisons[a].append(ranks[a])
        valid=[r for r in ranks.values() if r is not None and r<=5]
        oracle5+=int(bool(valid))
        private.append({"question_id":qid,
                        "original_context_rank":br,
                        "qwen_rank_by_policy":{a:ranks[a] for a in comparisons}})
    paired={a:_paired_delta(comparisons[a],base,5) for a in comparisons}
    # Verify the declared aggregate counts from the existing scored JSON
    # before any derivative result is presented.
    for a,rs in [("source_context",base),*comparisons.items()]:
        for k in (1,5,10,20,100):
            count=sum(v is not None and v<=k for v in rs)
            if count!=qwen_scores["topk_hit_counts"][a][str(k)]:
                raise ValueError("Scored aggregate mismatch for "+a+"@"+str(k))
    summary={
      "schema":"chronohyper_qwen_bge_paired_posthoc_v1",
      "stage":"POSTHOC_NOT_NEW_CONFIRMATORY_DATA",
      "ranked_34_sha_verified":qwen_rank["ranking_sha256"],
      "source_sha_verified":source_rank["ranking_sha256"],
      "questions":34,
      "gold_file_read_during_comparison":False,
      "bge_context_hit5":sum(v is not None and v<=5 for v in base),
      "qwen_hit5":{a:sum(v is not None and v<=5 for v in rs)
                   for a,rs in comparisons.items()},
      "paired_against_bge_context_HIT5":paired,
      "oracle_ever_correct_within_top5_NOT_DEPLOYABLE":oracle5,
      "limitations":[
        "Same 34 cases were inspected across repeated model selection",
        "Two-sided discordant p-values are descriptive and unadjusted for multiple comparisons",
        "Oracle uses answer knowledge and is never a deployable selector",
        "Candidate pool recall is not top5 accuracy; new independent test is required",
      ],
      "per_question_LOCAL_PRIVATE":private,
    }
    target.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items()
                      if k!="per_question_LOCAL_PRIVATE"},indent=2))
    print("Private paired audit:",target)
    return summary

def main():
    p=argparse.ArgumentParser(description=__doc__)
    act=p.add_mutually_exclusive_group(required=True)
    act.add_argument("--rank",action="store_true")
    act.add_argument("--score",action="store_true")
    act.add_argument("--compare",action="store_true")
    p.add_argument("--project",default=".")
    p.add_argument("--source",default=MULTIVIEW)
    p.add_argument("--out",default=OUTPUT)
    p.add_argument("--model",default=MODEL)
    p.add_argument("--device",default="cuda")
    p.add_argument("--batch-size",type=int,default=4)
    p.add_argument("--max-length",type=int,default=512)
    p.add_argument("--max-candidates",type=int,default=300)
    args=p.parse_args()
    if args.rank:
        rank(args.project,args.source,args.out,args.model,args.device,
             args.batch_size,args.max_length,args.max_candidates)
    elif args.score:
        score(args.project,args.out)
    else:
        compare_scored(args.project,args.out)

if __name__=="__main__":
    main()
