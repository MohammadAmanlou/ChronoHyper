"""Research-only semantic/hybrid retrieval upgrade, separate from the locked model.

No benchmark gold enters --rank. Dense retrieval + lexical TF-IDF + RRF
+ neural cross-encoder, with honest hyperedge CO-OCCURRENCE context.
GPU/Kaggle requirements are installed separately; do not change main requirements.
34 previously seen questions are POST-HOC development, NEVER confirmation.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,statistics,time
from collections import Counter,defaultdict
from pathlib import Path
from zipfile import ZipFile
import numpy as np
from scipy.sparse import hstack
from sklearn.preprocessing import normalize as sparse_normalize
from sklearn.feature_extraction.text import TfidfVectorizer
from research_lab.retrieval_v2 import index as old_index,norm
from research_lab.retrieval_frontier import _rank_hash

DENSE_MODEL="BAAI/bge-m3"
RERANKER_MODEL="BAAI/bge-reranker-v2-m3"
CUTOFF=2025
CANDIDATE_K=100
RERANK_K=64
RRF_K=60
SOFT_ROUTE_BONUS=0.02
DEFAULT="local_only/advanced_retrieval"
FRESH_QUERIES="local_only/fresh_retrieval_screened34/queries_only.csv"
FRESH_GOLD="local_only/fresh_retrieval_screened34/gold_PRIVATE.csv"

def native_context(root,entries,cutoff=CUTOFF,limit=18):
    """Only dated native hyperedge co-incidence, never invented semantic relations."""
    with ZipFile(Path(root)/"inputs/data.zip") as z:
        graph=json.loads(z.read("data/tkh_collection10.json"))
    ids={n["id"]:n for n in graph["nodes"]
         if n["first_seen_year"]<=cutoff}
    incidence=defaultdict(Counter)
    for e in graph["hyperedges"]:
        if e["year"]>cutoff or e.get("provenance",{}).get("article_year",e["year"])>cutoff:
            continue
        members=[v for v in e["members"] if v in ids]
        if len(members)<2:continue
        neighbors=sorted({(ids[n]["type"],ids[n]["surface_form"]) for n in members
                          if ids[n]["type"] not in {"author","article","claim"}
                          and ids[n].get("surface_form")})
        for u in members:
            if u not in ids:continue
            selfkey=(ids[u]["type"],ids[u]["surface_form"])
            for label in neighbors:
                if label!=selfkey: incidence[u][label]+=1
    texts=[]
    for item in entries:
        related=Counter()
        for node_id in item["node_ids"]:
            related.update(incidence.get(node_id,{}))
        # Entities can be hyperedge co-members without having a verified relation.
        nearest=sorted(related.items(),key=lambda x:(-x[1],x[0][0],x[0][1]))[:limit]
        rel="; ".join(f"{key[1]} ({key[0]})" for key,_ in nearest)
        paper_context=item["text"].replace((item["name"]+" ")*3,"").strip()
        texts.append(
            f"Scientific entity: {item['name']}. Entity type: {item['type']}. "
            f"Dated paper/title context: {paper_context}. "
            f"Co-mentioned graph entities (NOT proven semantic relations): {rel}.")
    return texts

def reciprocal_fusion(ranks,weights=None,constant=RRF_K):
    """Rank-based late fusion, no gold-dependent weights."""
    if not ranks:raise ValueError("No retrieval lists")
    weights=weights or [1.]*len(ranks)
    if len(ranks)!=len(weights):raise ValueError("Invalid fusion weighting")
    fused=defaultdict(float)
    for ranking,weight in zip(ranks,weights):
        for i,k in enumerate(ranking):
            fused[int(k)]+=weight/(constant+i+1)
    return sorted(fused,key=lambda j:(-fused[j],j))

def _as_top(indices,scores,entries,n=20):
    return [{"name":entries[j]["name"],"normalized":entries[j]["normalized"],
             "type":entries[j]["type"],"score":float(scores.get(j,0.0))}
            for j in indices[:n]]

def _argsort(vals):
    return sorted(range(len(vals)),key=lambda i:(-float(vals[i]),i))

def _dense_encoder(name,device):
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise ImportError("Install requirements_advanced.txt on Kaggle GPU or a server") from exc
    return SentenceTransformer(name,device=device)

def _cross_encoder(name,device):
    from sentence_transformers import CrossEncoder
    return CrossEncoder(name,device=device,max_length=512)

def retrieval_query(query,lex_score,dense_score,documents,entries,reranker=None,
                    candidate_k=CANDIDATE_K,rerank_k=RERANK_K):
    if len(lex_score)!=len(entries) or len(dense_score)!=len(entries):
        raise ValueError("Candidate score shapes differ")
    lex_order=_argsort(lex_score);dense_order=_argsort(dense_score)
    hyb=reciprocal_fusion([lex_order[:candidate_k],dense_order[:candidate_k]])
    # Soft routing is a future graph-aware ablation; the default high-recall
    # version deliberately DOES NOT hard-remove any candidate.
    base=hyb[:rerank_k]
    if reranker is not None:
        pairs=[(query,documents[j]) for j in base]
        pred=reranker.predict(pairs,batch_size=16,show_progress_bar=False)
        pred=np.asarray(pred).reshape(-1)
        ordered=sorted(range(len(base)),key=lambda i:(-float(pred[i]),base[i]))
        ranked=[base[i] for i in ordered]
        rerank_scores={base[i]:float(pred[i]) for i in range(len(base))}
    else:
        ranked=base
        rerank_scores={j:float(len(base)-k) for k,j in enumerate(base)}
    return {
        "lexical":_as_top(lex_order,{j:float(lex_score[j]) for j in lex_order[:20]},entries),
        "dense":_as_top(dense_order,{j:float(dense_score[j]) for j in dense_order[:20]},entries),
        "hybrid_rrf":_as_top(hyb,{j:float(len(hyb)-k) for k,j in enumerate(hyb[:20])},entries),
        "hybrid_rerank":_as_top(ranked,rerank_scores,entries),
        "n_hybrid_candidates":len(hyb),
        "n_reranked":len(base),
    }

def _csv(path):
    with Path(path).open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        if not {"question_id","question"}.issubset(reader.fieldnames or []):
            raise ValueError("Query worksheet requires question_id and question")
        rows=list(reader)
    if len(rows)!=len({r["question_id"] for r in rows}) or not rows:
        raise ValueError("Duplicate or absent query IDs")
    return rows

def rank(project=".",questions=FRESH_QUERIES,out=DEFAULT,
         dense_model=DENSE_MODEL,reranker_model=RERANKER_MODEL,
         device="cuda",candidate_k=CANDIDATE_K,rerank_k=RERANK_K,
         batch_size=32,no_reranker=False):
    root=Path(project).resolve()
    qfile=Path(questions)
    if not qfile.is_absolute():qfile=root/qfile
    folder=Path(out)
    if not folder.is_absolute():folder=root/folder
    folder.mkdir(parents=True,exist_ok=True)
    dest=folder/"rankings.json"
    if dest.exists():raise FileExistsError("Existing ranking is frozen; do not overwrite")
    qrows=_csv(qfile)
    entries,_,_,_,roots,_,_,_=old_index(root,CUTOFF)
    texts=native_context(root,entries)
    word=TfidfVectorizer(stop_words="english",ngram_range=(1,2),sublinear_tf=True)
    char=TfidfVectorizer(analyzer="char_wb",ngram_range=(3,5),sublinear_tf=True)
    X=sparse_normalize(hstack([word.fit_transform(texts)*0.7,
                               char.fit_transform(texts)*0.3],format="csr"))
    embed=_dense_encoder(dense_model,device)
    begin=time.perf_counter()
    vectors=np.asarray(embed.encode(texts,batch_size=batch_size,
                                     show_progress_bar=True,normalize_embeddings=True),
                       dtype=np.float32)
    embedding_s=time.perf_counter()-begin
    _check=bool(np.isfinite(vectors).all())
    if not _check:raise ValueError("Nonfinite embeddings")
    reranker=None if no_reranker else _cross_encoder(reranker_model,device)
    output=[]
    for q in qrows:
        query=q["question"]
        start=time.perf_counter()
        Q=sparse_normalize(hstack([word.transform([query])*0.7,
                                   char.transform([query])*0.3],format="csr"))
        lx=np.asarray((X@Q.T).toarray()).ravel()
        qv=np.asarray(embed.encode([query],normalize_embeddings=True),
                      dtype=np.float32).ravel()
        d=vectors@qv
        prediction=retrieval_query(query,lx,d,texts,entries,reranker,
                                   candidate_k,rerank_k)
        elapsed=time.perf_counter()-start
        output.append({"question_id":q["question_id"],"type":q.get("type",""),
                       "retrieval":prediction,
                       "total_online_s_including_encoding_and_rerank":elapsed})
    artifact={
        "schema":"chronohyper_new_hybrid_rerank_development_v1",
        "stage":"POSTHOC_AFTER_VIEWING_ORIGINAL_34_SCORE_DEVELOPMENT_ONLY",
        "model_locked_unchanged":True,"gold_accessed_during_ranking":False,
        "old_34_is_not_confirmatory":True,
        "cutoff":CUTOFF,"queries_sha256":hashlib.sha256(qfile.read_bytes()).hexdigest(),
        "n_queries":len(output),"n_entities":len(entries),
        "n_root_groups":len(roots),"dense_model":dense_model,
        "reranker_model":None if no_reranker else reranker_model,
        "device":device,"candidate_k":candidate_k,"rerank_k":rerank_k,
        "entity_embedding_build_s":embedding_s,
        "corpus_text_scope":"dated entity names, primary source titles, native hyperedge co-mentions; no independently fetched full paper text",
        "rankings":output}
    artifact["ranking_sha256"]=_rank_hash(artifact)
    dest.write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"rankings":str(dest),"n_queries":len(output),
                      "sha256":artifact["ranking_sha256"],
                      "gold_read":False},indent=2))
    return artifact

def score(project=".",directory=DEFAULT,gold=FRESH_GOLD):
    root=Path(project).resolve()
    folder=Path(directory)
    if not folder.is_absolute():folder=root/folder
    data=json.loads((folder/"rankings.json").read_text(encoding="utf-8"))
    if data.get("schema")!="chronohyper_new_hybrid_rerank_development_v1" or (
            data.get("ranking_sha256")!=_rank_hash(data)):
        raise ValueError("Ranking file modified or wrong schema")
    dst=folder/"score_DEVELOPMENT_ONLY.json"
    if dst.exists():raise FileExistsError("Keep prior research outcome; do not overwrite")
    path=Path(gold)
    if not path.is_absolute():path=root/path
    with path.open(encoding="utf-8-sig",newline="") as f:rows=list(csv.DictReader(f))
    golds={r["question_id"]:(r["target_type"],norm(r["target_name"])) for r in rows}
    if len(golds)!=len(rows) or len(rows)!=len(data["rankings"]) or set(golds)!={x["question_id"] for x in data["rankings"]}:
        raise ValueError("Gold/query ID mismatch: partial evaluation disallowed")
    arms=("lexical","dense","hybrid_rrf","hybrid_rerank")
    hits={a:[] for a in arms}
    mrr={a:[] for a in arms}
    per_question=[]
    for row in data["rankings"]:
        target=golds[row["question_id"]]
        outcome={}
        for arm in arms:
            names=[(r["type"],r["normalized"]) for r in row["retrieval"][arm][:5]]
            at=names.index(target)+1 if target in names else None
            outcome[arm]={"hit":int(at is not None),"rr":1./at if at else 0.}
            hits[arm].append(outcome[arm]["hit"])
            mrr[arm].append(outcome[arm]["rr"])
        per_question.append({"question_id":row["question_id"],"arms":outcome})
    summary={"schema":"chronohyper_hybrid_development_gold_score_v1",
             "gold_used_in_ranking":False,"research_stage":data["stage"],
             "ranking_sha256_verified":data["ranking_sha256"],
             "n_queries":len(rows),"arms":{
                 arm:{"hit_at5":float(statistics.mean(hits[arm])),
                      "hit_n":sum(hits[arm]),
                      "mrr_at5":float(statistics.mean(mrr[arm]))} for arm in arms},
             "per_question_LOCAL_ONLY":per_question,
             "fixed_architecture_posthoc_development_not_new_holdout":True,
             "original_model_locked_unchanged":True}
    dst.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k!="per_question_LOCAL_ONLY"},indent=2))
    return summary

def main():
    p=argparse.ArgumentParser(description=__doc__)
    action=p.add_mutually_exclusive_group(required=True)
    action.add_argument("--rank",action="store_true")
    action.add_argument("--score",action="store_true")
    p.add_argument("--project",default=".")
    p.add_argument("--questions",default=FRESH_QUERIES)
    p.add_argument("--out",default=DEFAULT)
    p.add_argument("--gold",default=FRESH_GOLD)
    p.add_argument("--device",default="cuda")
    p.add_argument("--dense-model",default=DENSE_MODEL)
    p.add_argument("--reranker-model",default=RERANKER_MODEL)
    p.add_argument("--candidate-k",type=int,default=CANDIDATE_K)
    p.add_argument("--rerank-k",type=int,default=RERANK_K)
    p.add_argument("--batch-size",type=int,default=32)
    p.add_argument("--no-reranker",action="store_true")
    a=p.parse_args()
    if a.rank:rank(a.project,a.questions,a.out,a.dense_model,a.reranker_model,
                   a.device,a.candidate_k,a.rerank_k,a.batch_size,a.no_reranker)
    else:score(a.project,a.out,a.gold)
if __name__=="__main__":
    main()
