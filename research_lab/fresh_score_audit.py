"""Read-only submission audit for already frozen fresh Type-A retrieval results.

This reports the original 36 attempt denominator; it cannot upgrade the
source-grounded same-corpus experiment into an external test. No tuning,
re-ranking, model runs, or changes to old results.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path

from research_lab.fresh_retrieval import _read_manifest, _read_csv
from research_lab.retrieval_frontier import verify_rankings

DEFAULT_DIR="local_only/fresh_retrieval_screened34"

def _require(cond,msg):
    if not cond: raise ValueError(msg)

def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def _mean(xs):
    _require(bool(xs),"Empty measure")
    return statistics.mean(xs)

def exact_sign_test(wins,losses):
    """Two-sided exact conditional sign p; descriptive in a small, selected sample."""
    n=wins+losses
    if not n:return None
    return min(1.,2*sum(math.comb(n,k) for k in range(min(wins,losses)+1))/(2**n))

def analyze(manifest,screen,ranks,scored):
    _require(manifest.get("stage")=="SAME_CORPUS_PROSPECTIVE_QUESTION_SET_NOT_EXTERNAL",
             "Wrong freeze stage")
    _require(screen.get("schema")=="chronohyper_prerank_source_screen_v1","Missing provenance screen")
    original=screen.get("n_attempted")
    excluded=screen.get("n_documented_excluded")
    valid=screen.get("n_eligible_format")
    _require(isinstance(original,int) and isinstance(excluded,int) and isinstance(valid,int)
             and original==36 and valid==34 and excluded==2 and valid+excluded==original,
             "Expected original 36 targets, 34 eligible, two documented source failures")
    excluded_ids=sorted(x.get("question_id") for x in screen.get("excluded",[]))
    _require(excluded_ids==["F023","F031"],"Different/missing source-failure exclusions")
    _require(screen.get("validation_errors")==[],"Pre-rank screening had errors")
    _require(manifest.get("frozen_before_rank") is True and
             manifest.get("predeclared_primary_route_roots")==4 and
             manifest.get("n_queries")==valid,"Not prospectively frozen with 4-root primary arm")
    digest=verify_rankings(ranks)
    _require(digest==scored.get("rankings_sha256_verified"),
             "Mismatch between scored and frozen rankings digest")
    _require(ranks.get("cutoff")==2025 and len(ranks.get("results",[]))==valid,
             "Ranked corpus cutoff/question count mismatch")
    _require(scored.get("n_queries")==valid and
             scored.get("primary_predeclared_route")=="route_4" and
             scored.get("source_corpus_external_to_original") is False,
             "Score stage/denominator overstated")
    _require(scored.get("questions_sha256")==manifest.get("query_sha256") and
             scored.get("gold_sha256")==manifest.get("gold_sha256"),
             "Score isn't attached to original prospectively frozen questions/gold")
    _require(scored.get("all_root_exactness_verified") is True,
             "All-root flat consistency was not checked")
    _require(len(scored.get("per_question_local_only",[]))==valid,
             "Per-question score mismatch")

    qs={x["question_id"]:x for x in ranks["results"]}
    details={x["question_id"]:x for x in scored["per_question_local_only"]}
    _require(len(qs)==len(details)==valid and set(qs)==set(details),
             "Missing or duplicated questions between rankings and score")
    assert "4" in ranks["budgets"] or 4 in ranks["budgets"]
    routed=[]
    flat=[]
    timing_flat=[]
    timing_route=[]
    for qid in sorted(qs):
        raw=qs[qid]
        s=details[qid]["scores"]
        for arm,item in (("flat",raw["flat"]),("route_4",raw["routes"]["4"])):
            got=s[arm]
            expected=(int(got["rank"] is not None))
            _require(got["hit5"]==expected and
                     (got["rank"] is None or 1 <= got["rank"] <= 5),
                     "Inconsistent per-query hit/rank for "+qid)
            _require(math.isclose(got["mrr5"],0 if not expected else 1/got["rank"],abs_tol=1e-12),
                     "Inconsistent reciprocal rank for "+qid)
            expected_cost=item["candidates_scored"]+(0 if arm=="flat" else item["centroid_scores"])
            _require(got["cost"]==expected_cost,"Mismatched per-query cost: "+qid)
        # Compare exact top-5 candidate IDs for flat vs all 12 root routes.
        allroot=raw["routes"][str(max(ranks["budgets"]))]
        def identities(a):
            return [(v["normalized"],v["type"]) for v in a["top5"]]
        _require(identities(raw["flat"])==identities(allroot),
                 "All root retrieved list differs from flat for "+qid)
        flat.append(s["flat"])
        routed.append(s["route_4"])
        timing_flat.append(raw["flat"]["median_online_ms_including_top5"])
        timing_route.append(raw["routes"]["4"]["median_online_ms_including_routing_and_top5"])
    hit_flat=sum(t["hit5"] for t in flat)
    hit_route=sum(t["hit5"] for t in routed)
    _require(hit_flat==3 and hit_route==2,
             "Observed score differs from the original applicant's 34-query log; investigate before reporting")
    primary=scored["descriptive_paired_contrasts"]["route_4"]
    wins=sum(a["hit5"]>b["hit5"] for a,b in zip(routed,flat))
    losses=sum(a["hit5"]<b["hit5"] for a,b in zip(routed,flat))
    ties=valid-wins-losses
    _require((wins,losses,ties)==(0,1,33) and
             (wins,losses,ties)==(primary["wins"],primary["losses"],primary["ties"]),
             "Paired pattern mismatch")
    difference=(hit_route-hit_flat)/valid
    _require(math.isclose(difference,primary["paired_hit_at_5_difference"],abs_tol=1e-12),
             "Incorrect paired difference")
    cf=_mean([r["cost"] for r in flat])
    cr=_mean([r["cost"] for r in routed])
    _require(math.isclose(cf,scored["per_arm"]["flat"]["mean_online_dot_products"],abs_tol=1e-8) and
             math.isclose(cr,scored["per_arm"]["route_4"]["mean_online_dot_products"],abs_tol=1e-8),
             "Reported cost denominator inconsistent")
    ci=primary["exploratory_paired_bootstrap_95ci"]
    _require(len(ci)==2 and ci[0]<=difference<=ci[1],
             "Paired bootstrap interval excludes observed mean")
    return {
        "schema":"chronohyper_34q_frozen_score_integrity_v1",
        "status":"APPLICANT_LOCAL_RESULT_AUDITED_NO_RERANK",
        "attempted_source_targets":original,
        "source_qualified_queries":valid,
        "pre_ranking_source_exclusions":excluded_ids,
        "same_corpus_as_model":True,
        "new_question_texts":True,
        "externally_independent_source_corpus":False,
        "original_question_author_fulltext_evidence_certified":False,
        "rank_sha256_verified":digest,
        "predeclared_primary_arm":"route_4",
        "flat_hit_n":hit_flat,
        "route4_hit_n":hit_route,
        "flat_hit_at5":hit_flat/valid,
        "route4_hit_at5":hit_route/valid,
        "paired_hit_difference_route_minus_flat":difference,
        "paired_wins_route":wins,
        "paired_losses_route":losses,
        "paired_ties":ties,
        "paired_exact_sign_p_descriptive":exact_sign_test(wins,losses),
        "paired_bootstrap95_exploratory":ci,
        "flat_mrr_at5":_mean([x["mrr5"] for x in flat]),
        "route4_mrr_at5":_mean([x["mrr5"] for x in routed]),
        "flat_online_dot_products_mean":cf,
        "route4_online_dot_products_mean":cr,
        "online_dot_product_reduction_fraction":1-cr/cf,
        "flat_mean_query_median_online_ms":_mean(timing_flat),
        "route4_mean_query_median_online_ms":_mean(timing_route),
        "timing_excludes_query_vectorization_and_offline_index":True,
        "allroot_rankings_equal_flat":True,
        "no_claim_of_statistical_equivalence":True,
        "original_type_B_generated_answer_accuracy_measured":False,
        "interpretation":"The predeclared four-root variant saved ~59.3% of online dot products, but lost one of three flat top-5 hits on the 34 source-qualified new same-corpus questions. A negative observed Hit@5 difference is not evidence of significant harm or proof of equivalence. Do not retune and then reuse this same set as confirmation."
    }

def audit(project=".",directory=DEFAULT_DIR,out="audit_local.json"):
    root=Path(project).resolve()
    folder=Path(directory)
    if not folder.is_absolute():folder=root/folder
    manifest=_read_manifest(root,folder,verify_gold=True)
    screen=json.loads((folder/"pre_rank_source_screen.json").read_text(encoding="utf-8"))
    ranks=json.loads((folder/"rankings.json").read_text(encoding="utf-8"))
    scores=json.loads((folder/"scored.json").read_text(encoding="utf-8"))
    res=analyze(manifest,screen,ranks,scores)
    path=folder/out
    if path.exists():
        prior=json.loads(path.read_text(encoding="utf-8"))
        _require(prior==res,"Prior independent local audit differs; do not overwrite")
    else:
        path.write_text(json.dumps(res,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in res.items() if k not in
                      ("interpretation",)},indent=2))
    print("Preserved audited evidence:",path)
    return res

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project",default=".")
    p.add_argument("--directory",default=DEFAULT_DIR)
    a=p.parse_args()
    audit(a.project,a.directory)

if __name__=="__main__":
    main()
