"""Prospectively frozen, SAME-CORPUS new-query evaluation for ChronoHyper.

One target entity per question, chosen by deterministic balanced root sampling.
An isolated question author must provide documented paraphrased queries before
ranking. Full-text truth/independence is NOT automatically certified.
All generated source-sensitive files stay in ignored local_only/.
"""
from __future__ import annotations
import argparse
import csv
import difflib
import hashlib
import io
import json
import random
import re
import statistics
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from research_lab import retrieval_frontier as frontier
from research_lab.retrieval_v2 import index, norm, questions

N_PER_ROOT=3
SEED="ChronoHyper-prospective-root-stratified-2026-10"
DIR="local_only/fresh_retrieval"
AUTHOR_FIELDS=("question_id","target_name","target_type","paper_title","paper_year")
RETURN_FIELDS=AUTHOR_FIELDS+("question","source_url","evidence_locator",
                               "evidence_access","author_id","question_rationale")
QUERY_FIELDS=("question_id","question","type")
GOLD_FIELDS=("question_id","target_type","target_name")
STAGES=("author-kit","freeze","rank","score")

def _p(root, path):
    p=Path(path)
    return p if p.is_absolute() else root/p

def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _read_csv(path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames or len(set(reader.fieldnames))!=len(reader.fieldnames):
            raise ValueError("Missing/duplicate CSV header")
        return list(reader.fieldnames),list(reader)

def _write_csv(path,cols,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("x",encoding="utf-8-sig",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=cols,extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)

def _save_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("x",encoding="utf-8") as f:
        json.dump(value,f,ensure_ascii=False,indent=2,sort_keys=True)
        f.write("\n")

def _read_manifest(root,folder):
    path=folder/"freeze_manifest.json"
    if not path.is_file():raise FileNotFoundError("First freeze the reviewer-authored questions")
    obj=json.loads(path.read_text(encoding="utf-8"))
    for key,file in (("author_kit_sha256","AUTHOR_KIT.csv"),
                     ("query_sha256","queries_only.csv"),
                     ("gold_sha256","gold_PRIVATE.csv"),
                     ("review_sha256","REVIEWED_QUESTIONS.csv")):
        if not (folder/file).is_file() or _sha(folder/file)!=obj.get(key):
            raise ValueError("Frozen author-kit/questions/gold/review changed: "+file)
    if obj.get("stage")!="SAME_CORPUS_PROSPECTIVE_QUESTION_SET_NOT_EXTERNAL":
        raise ValueError("Unknown provenance stage")
    return obj

def _candidate_catalog(root):
    entries,_,_,_,roots,_,_,_=index(root,2025)
    with ZipFile(root/"inputs/data.zip") as z:
        import json as _json
        g=_json.loads(z.read("data/tkh_collection10.json"))
        papers=list(csv.DictReader(io.StringIO(
            z.read("data/collection10_articles.csv").decode("utf-8-sig"))))
    papers={str(p["id"]):p for p in papers if int(p["year"])<=2025}
    node={str(n["id"]):n for n in g["nodes"]}
    output={}
    for e in entries:
        found=[]
        for nid in e["node_ids"]:
            n=node.get(str(nid),{})
            for aid in n.get("provenance",{}).get("articles",[]):
                p=papers.get(str(aid))
                if p and p.get("title","").strip():
                    found.append((str(p["title"]).strip(),int(p["year"])))
        # A target with only a word-label and no paper is not a source-grounded query.
        if not found:continue
        selected=sorted(set(found),key=lambda t:(-t[1],t[0]))[0]
        if len(e["name"].strip()) < 8 or not norm(e["name"]):continue
        output[(e["type"],e["normalized"])]={
            "target_name":e["name"],"target_type":e["type"],
            "paper_title":selected[0],"paper_year":str(selected[1]),
            "roots":e["roots"]}
    return roots,output

def author_kit(project=".",directory=DIR):
    root=Path(project).resolve()
    folder=_p(root,directory)
    dest=folder/"AUTHOR_KIT.csv"
    if dest.exists():
        raise FileExistsError("Do not replace an existing author kit: "+str(dest))
    roots,records=_candidate_catalog(root)
    if len(roots)<4:raise ValueError("Expected multiple root groups")
    used=set()
    rows=[]
    # Stable per-root ordering avoids selecting favorable search results by hand.
    for r in roots:
        eligible=[(key,record) for key,record in records.items()
                  if r in record["roots"] and key not in used]
        eligible.sort(key=lambda item:hashlib.sha256(
            (SEED+"|"+r+"|"+repr(item[0])).encode("utf-8")).hexdigest())
        if len(eligible)<N_PER_ROOT:raise ValueError("Insufficient dated source candidates in root "+r)
        for key,record in eligible[:N_PER_ROOT]:
            used.add(key)
            rows.append({"question_id":f"F{len(rows)+1:03d}",
                         **{k:record[k] for k in AUTHOR_FIELDS if k!="question_id"}})
    _write_csv(dest,AUTHOR_FIELDS,rows)
    print(json.dumps({"author_packet":str(dest),"n_targets":len(rows),
                      "roots_sampled":len(roots),"targets_per_root":N_PER_ROOT,
                      "gold_from_existing_dated_sources":True,
                      "external_corpus_validation":False},indent=2))
    return rows

def freeze(project=".",directory=DIR,response=""):
    if not response:raise ValueError("An externally authored completed CSV is required")
    root=Path(project).resolve()
    folder=_p(root,directory)
    if (folder/"freeze_manifest.json").exists():
        raise FileExistsError("Freeze already exists. Never rewrite a scored benchmark")
    kh,kit=_read_csv(folder/"AUTHOR_KIT.csv")
    if kh!=list(AUTHOR_FIELDS):raise ValueError("Author-kit columns altered")
    returned=_p(root,response)
    rh,received=_read_csv(returned)
    if rh!=list(RETURN_FIELDS):raise ValueError("Reviewer must preserve exact columns/order")
    if len(received)!=len(kit) or len({x["question_id"] for x in received})!=len(kit):
        raise ValueError("Wrong count or duplicate question IDs")
    expected={r["question_id"]:r for r in kit}
    historic=questions(root)
    old_texts=[" ".join(str(q.get("question","")).lower().split()) for q in historic]
    query_rows=[]
    gold_rows=[]
    records=[]
    for row in received:
        id=row["question_id"]
        if id not in expected or any(row[k]!=expected[id][k] for k in AUTHOR_FIELDS):
            raise ValueError("Changed original target, source, or question ID: "+id)
        q=" ".join(row["question"].strip().split())
        if len(q)<55 or len(q)>450 or not q.endswith("?"):
            raise ValueError(id+": must be a specific, grammatical 55-450 character question ending in '?'")
        target=norm(row["target_name"])
        if target and target in norm(q):
            raise ValueError(id+": question leaks the exact target name")
        if any(difflib.SequenceMatcher(None,q.lower(),old).ratio()>=.82 for old in old_texts):
            raise ValueError(id+": too similar to a previously inspected benchmark question")
        if row["evidence_access"] not in ("FULL_TEXT","ABSTRACT_ONLY"):
            raise ValueError(id+": independently inspect a primary paper; unsupported rows require revision")
        if not re.match(r"^https?://\S+$",row["source_url"].strip()):
            raise ValueError(id+": expected a real primary-source URL")
        if int(row["paper_year"])>2025:
            raise ValueError(id+": future source year")
        if len(row["evidence_locator"].strip())<6 or len(row["question_rationale"].strip())<20:
            raise ValueError(id+": source passage location and task rationale required")
        if not row["author_id"].strip():
            raise ValueError(id+": real reviewer/model identifier is required")
        query_rows.append({"question_id":id,"question":q,"type":"A"})
        gold_rows.append({"question_id":id,"target_type":row["target_type"],
                          "target_name":row["target_name"]})
        records.append(row)
    query_rows.sort(key=lambda z:z["question_id"])
    gold_rows.sort(key=lambda z:z["question_id"])
    # Ensure all files are saved BEFORE running even one ranking.
    output_review=folder/"REVIEWED_QUESTIONS.csv"
    _write_csv(output_review,RETURN_FIELDS,sorted(records,key=lambda z:z["question_id"]))
    _write_csv(folder/"queries_only.csv",QUERY_FIELDS,query_rows)
    _write_csv(folder/"gold_PRIVATE.csv",GOLD_FIELDS,gold_rows)
    manifest={
        "schema":"chronohyper_prospective_fresh_question_freeze_v1",
        "stage":"SAME_CORPUS_PROSPECTIVE_QUESTION_SET_NOT_EXTERNAL",
        "n_queries":len(query_rows),"frozen_before_rank":True,
        "author_kit_sha256":_sha(folder/"AUTHOR_KIT.csv"),
        "review_sha256":_sha(output_review),
        "query_sha256":_sha(folder/"queries_only.csv"),
        "gold_sha256":_sha(folder/"gold_PRIVATE.csv"),
        "source_cutoff_year":2025,"predeclared_primary_route_roots":4,
        "predeclared_primary_metrics":["Hit@5","MRR@5","mean online dot-products"],
        "independent_author_verified":False,
        "full_paper_evidence_verified_by_software":False,
        "gold_seen_by_ranker":False,
        "not_an_external_corpus":True}
    _save_json(folder/"freeze_manifest.json",manifest)
    print(json.dumps({"frozen_manifest":str(folder/"freeze_manifest.json"),
                      "n_queries":len(query_rows),"predeclared_route_roots":4,
                      "ranking_started":False},indent=2))
    return manifest

def rank(project=".",directory=DIR,repeats=5):
    root=Path(project).resolve()
    folder=_p(root,directory)
    freeze_record=_read_manifest(root,folder)
    dest=folder/"rankings.json"
    if dest.exists():raise FileExistsError("Rankings already frozen; do not overwrite")
    ranks=frontier.rank(root,out=str(dest),
                        question_file=str(folder/"queries_only.csv"),
                        cutoff=2025,repeats=repeats)
    actual={x["question_id"] for x in ranks["results"]}
    _,queries=_read_csv(folder/"queries_only.csv")
    if len(actual)!=len(queries) or actual!={x["question_id"] for x in queries}:
        raise AssertionError("Ranked question set differs from freeze")
    print("Frozen ranking digest:",frontier.verify_rankings(ranks))
    return ranks

def _paired_bootstrap(values,seed=20261022,n=5000):
    if not values:raise ValueError("Empty paired contrast")
    rng=random.Random(seed)
    draw=sorted(sum(values[rng.randrange(len(values))] for _ in values)/len(values)
                for _ in range(n))
    return [draw[int(.025*(n-1))],draw[int(.975*(n-1))]]

def score(project=".",directory=DIR):
    root=Path(project).resolve()
    folder=_p(root,directory)
    manifest=_read_manifest(root,folder)
    if (folder/"scored.json").exists():raise FileExistsError("Preserve prior score")
    data=json.loads((folder/"rankings.json").read_text(encoding="utf-8"))
    hash_value=frontier.verify_rankings(data)
    _,gold_rows=_read_csv(folder/"gold_PRIVATE.csv")
    gold={x["question_id"]:(x["target_type"],norm(x["target_name"])) for x in gold_rows}
    if len(gold)!=len(gold_rows) or set(gold)!={x["question_id"] for x in data["results"]}:
        raise ValueError("Gold and ranked IDs must match exactly; no skipped questions")
    arms=["flat"]+[f"route_{k}" for k in data["budgets"]]
    observed={arm:[] for arm in arms}
    details=[]
    for row in data["results"]:
        id=row["question_id"]
        target=gold[id]
        scores={}
        for arm in arms:
            obj=row["flat"] if arm=="flat" else row["routes"][arm[6:]]
            results=obj["top5"]
            matches=[idx+1 for idx,p in enumerate(results)
                     if (p["type"],p["normalized"])==target]
            rank_at=matches[0] if matches else None
            hits=int(bool(matches))
            mrr=1/rank_at if rank_at else 0.
            cost=obj["candidates_scored"]+(0 if arm=="flat" else obj["centroid_scores"])
            if cost<=0:raise ValueError("Invalid candidate cost")
            scores[arm]={"hit5":hits,"mrr5":mrr,"cost":cost,"rank":rank_at}
            observed[arm].append(scores[arm])
        if scores["flat"]["hit5"]!=scores["route_"+str(data["budgets"][-1])]["hit5"]:
            raise AssertionError("All-root expected to reproduce flat")
        details.append({"question_id":id,"scores":scores})
    summary={}
    for arm,records in observed.items():
        summary[arm]={"hit_at_5":statistics.mean(x["hit5"] for x in records),
                      "mrr_at_5":statistics.mean(x["mrr5"] for x in records),
                      "mean_online_dot_products":statistics.mean(x["cost"] for x in records)}
    contrasts={}
    for arm in arms[1:]:
        delta=[a["hit5"]-b["hit5"] for a,b in zip(observed[arm],observed["flat"])]
        contrasts[arm]={"paired_hit_at_5_difference":statistics.mean(delta),
                        "exploratory_paired_bootstrap_95ci":_paired_bootstrap(delta),
                        "wins":sum(x>0 for x in delta),
                        "losses":sum(x<0 for x in delta),
                        "ties":sum(x==0 for x in delta)}
    # Do not use score to choose a new primary route: 4 roots was preregistered.
    result={
        "schema":"chronohyper_prospective_same_corpus_retrieval_score_v1",
        "stage":"SAME_CORPUS_NEW_QUESTIONS_NOT_EXTERNAL_CORPUS",
        "n_queries":len(details),"author_kit_sha256":manifest["author_kit_sha256"],
        "questions_sha256":manifest["query_sha256"],"gold_sha256":manifest["gold_sha256"],
        "rankings_sha256_verified":hash_value,
        "primary_predeclared_route":"route_4",
        "all_root_exactness_verified":True,
        "per_arm":summary,"descriptive_paired_contrasts":contrasts,
        "per_question_local_only":details,
        "independent_author_certified":False,"actual_primary_paper_entailment_certified":False,
        "source_corpus_external_to_original":False,
        "interpretation":"Prospectively frozen NEW question texts on the SAME provided corpus. Target names were sampled from existing indexed evidence; question author saw targets. Exact-name leakage and repeated original questions screened, not an independent external distribution. Do not interpret as generalizable accuracy or paper-answer correctness."}
    _save_json(folder/"scored.json",result)
    print(json.dumps({"n_questions":len(details),
                      "flat":summary["flat"],"predeclared_route4":summary.get("route_4"),
                      "paired_route4":contrasts.get("route_4"),
                      "file":str(folder/"scored.json")},indent=2))
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    modes=p.add_mutually_exclusive_group(required=True)
    for stage in STAGES:modes.add_argument("--"+stage,action="store_true")
    p.add_argument("--project",default=".")
    p.add_argument("--directory",default=DIR)
    p.add_argument("--response",default="")
    p.add_argument("--repeats",type=int,default=5)
    a=p.parse_args()
    if a.author_kit:author_kit(a.project,a.directory)
    elif a.freeze:freeze(a.project,a.directory,a.response)
    elif a.rank:rank(a.project,a.directory,a.repeats)
    else:score(a.project,a.directory)

if __name__=="__main__":main()
