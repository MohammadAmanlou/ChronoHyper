"""Summarize private post-lock AI reviews WITHOUT opening blind mapping keys.

Generated artifacts remain under Git-ignored local_only/. These checks verify
arithmetic and form-level consistency, not the judge's knowledge or independence.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

LABEL = "local_only/reviews/label_v3_fresh"
COHERENCE = "local_only/reviews/fresh_semantic"


def _load(path):
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _assert(condition, message):
    if not condition:
        raise ValueError(message)


def summarize(label_result, coherence_result, label_csv=None, coherence_csv=None):
    """Require provenance boundaries; never silently upgrade to human/full-text."""
    _assert(label_result.get("schema") == "chronohyper_v3_v2_blind_AI_names_titles_only_v1",
            "Unexpected label-score schema")
    _assert(coherence_result.get("schema") == "ckl_fresh_key_isolated_paper_title_coherence_v1",
            "Unexpected coherence schema")
    _assert(label_result.get("n_pairs") == 24, "24 labels expected")
    _assert((label_result.get("evaluable", 0) + label_result.get("excluded", 0)) == 24,
            "Invalid evaluable label denominator")
    wins, losses, ties = (label_result.get(k) for k in
                           ("v3_wins", "v3_losses", "ties"))
    _assert(all(isinstance(v, int) and v >= 0 for v in (wins, losses, ties)),
            "Invalid paired comparisons")
    _assert(wins + losses + ties == label_result["evaluable"],
            "Label win/loss/tie totals don't equal evaluable pairs")
    _assert(label_result.get("independent_paper_entailment_verified") is False and
            label_result.get("independent_judge_identity_verified") is False and
            label_result.get("development_review_not_confirmatory") is True,
            "Reviewer independence evidence flags must not be upgraded")
    counted = label_result.get("gloss_overclaim_evaluable", {})
    unknown = label_result.get("gloss_overclaim_unclear", {})
    rates = label_result.get("gloss_overclaim_rate", {})
    bounds = {}
    for arm in ("v2", "v3"):
        n = counted.get(arm)
        k = unknown.get(arm)
        rate = rates.get(arm)
        _assert(isinstance(n,int) and isinstance(k,int) and n>=0 and k>=0 and n+k==24,
                "Gloss rated/unclear denominators do not sum to 24: " + arm)
        _assert((rate is None if n==0 else
                 isinstance(rate,(int,float)) and 0<=rate<=1),
                "Incorrect conditional overclaim rate: " + arm)
        # For zero observed problems, a two-sided exact Clopper-Pearson 95%
        # upper bound is 1 - (0.025) ** (1/n).
        upper = 1 - (0.025 ** (1/n)) if n and rate == 0 else None
        bounds[arm] = {
            "n_determinate": n, "n_unclear": k,
            "observed_overclaim_rate_determinate_only": rate,
            "exact_two_sided_95pct_upper_if_zero_observed": upper,
        }
    n_pairs = coherence_result.get("n_matched_pairs")
    evaluable = coherence_result.get("evaluable_pairs")
    excluded = coherence_result.get("excluded_insufficient_pairs")
    _assert(n_pairs==24 and evaluable+excluded==24 and
            coherence_result.get("n_blind_cases")==48,
            "Invalid matched-pair totals")
    for key in ("real_higher_pairs","control_higher_pairs","ties"):
        _assert(isinstance(coherence_result.get(key),int)
                and coherence_result[key]>=0,"Invalid coherence counts")
    _assert(sum(coherence_result[key] for key in
                ("real_higher_pairs","control_higher_pairs","ties"))==evaluable,
            "Coherence pair count inconsistent")
    _assert(coherence_result.get("independent_full_paper_entailment_verified") is False
            and coherence_result.get("self_reported_AI_independence_only") is True,
            "Full-paper / AI independence claims must be scoped")
    mean_delta=coherence_result.get("mean_paired_delta")
    _assert(math.isclose(coherence_result["mean_real"]-
                         coherence_result["mean_control"], mean_delta,
                         abs_tol=1e-8), "Coherence means/delta inconsistent")
    for yr in ("2020","2022","2024"):
        _assert(yr in coherence_result.get("by_year", {}),
                "Missing coherence year "+yr)
    _assert(sum(coherence_result["by_year"][yr]["evaluable_pairs"]
                for yr in ("2020","2022","2024"))==evaluable,
            "Yearly evaluable counts inconsistent")

    evidence = {"label_rating_sha256": None, "coherence_rating_sha256": None}
    if label_csv and label_csv.is_file():
        labelhash=_sha(label_csv)
        _assert(labelhash==label_result.get("rated_csv_sha256"),
                "Label CSV has changed since scoring; rescore deliberately")
        evidence["label_rating_sha256"]=labelhash
    if coherence_csv and coherence_csv.is_file():
        evidence["coherence_rating_sha256"]=_sha(coherence_csv)
    return {
        "schema": "chronohyper_postlock_ai_review_status_v1",
        "stage": "SAME_CORPUS_KEY_SEPARATED_AI_REVIEW_DEVELOPMENT_DIAGNOSTIC",
        "model_locked_unchanged": True,
        "independent_human_expert_review_verified": False,
        "independent_full_paper_entailment_verified": False,
        "new_external_corpus_confirmatory_test": False,
        "v2_v3": {
            "total_pairs": 24,
            "evaluable_pairs": label_result["evaluable"],
            "excluded_insufficient": label_result["excluded"],
            "v3_wins": wins, "v3_losses": losses,"ties": ties,
            "mean_delta_v3_minus_v2": label_result["mean_rating_delta_v3_minus_v2"],
            "descriptive_unadjusted_sign_p": label_result["descriptive_sign_p_two_sided"],
            "positive_direction_but_not_significant_at_0_05":
                (wins>losses and label_result["descriptive_sign_p_two_sided"] is not None and
                 label_result["descriptive_sign_p_two_sided"]>=0.05),
            "gloss_overclaim": bounds,
            "actual_reviewer_identifiers_self_reported":
                label_result.get("self_reported_reviewer_ids",[]),
        },
        "coherence_matched": {
            "total_pairs":n_pairs, "evaluable_pairs":evaluable,
            "mean_real":coherence_result["mean_real"],
            "mean_control":coherence_result["mean_control"],
            "mean_paired_delta":mean_delta,
            "real_higher":coherence_result["real_higher_pairs"],
            "control_higher":coherence_result["control_higher_pairs"],
            "ties":coherence_result["ties"],
            "descriptive_unadjusted_sign_p":
                coherence_result["exact_sign_p_descriptive_only"],
            "bootstrap_ci95_exploratory":
                coherence_result.get("paired_bootstrap_95ci_exploratory"),
            "same_corpus_not_independent_semantic_ground_truth": True,
        },
        "local_review_data_fingerprints": evidence,
        "outstanding_gates": [
            "independent_full_paper_validation_of_scientific_label_claims",
            "36_type_b_claims_by_authorized_fulltext_reviewer",
            "new_external_or_independently_authored_retrieval_questions_frozen_before_scoring",
        ],
        "interpretation": "Two key-separated AI judgments on same-corpus surface names and paper titles. Do not call these full-text semantics, human review, or confirmatory new-corpus evaluation."
    }


def audit(project=".",output="local_only/review_status/summary.json"):
    root=Path(project).resolve()
    lpath=root/LABEL
    cpath=root/COHERENCE
    labels=_load(lpath/"result_LOCAL.json")
    coh=_load(cpath/"score_independent_48.json")
    if labels is None or coh is None:
        absent=[str(path) for path, found in
                ((lpath/"result_LOCAL.json",labels),(cpath/"score_independent_48.json",coh))
                if found is None]
        raise FileNotFoundError("Actual scored result(s) required: "+", ".join(absent))
    result=summarize(labels,coh,lpath/"rated_24.csv",
                     cpath/"ratings_fresh_48_independent.csv")
    out=Path(output)
    if not out.is_absolute():out=root/out
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False))
    print("Saved ignored status:",out)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project",default=".")
    p.add_argument("--out",default="local_only/review_status/summary.json")
    a=p.parse_args()
    audit(a.project,a.out)


if __name__=="__main__":
    main()
