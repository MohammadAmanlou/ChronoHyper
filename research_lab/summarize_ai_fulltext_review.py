"""Separate post-review AI-only score; never occupy canonical human score output.

The private A/B mapping is read only AFTER finished 24-case local AI ratings
have been validated against immutable case evidence and source hashes.
This is same-corpus development, not independent scientific verification.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
import math
from pathlib import Path

from research_lab.blind_paper_eval import csv_read
from research_lab.fulltext_label_audit import OUT, BASE, KEYS, REVIEW, FIXED_REVIEW, _sha, _wilson
from research_lab.label_v3_blind import RATING
from research_lab.ai_blind_fulltext_review import FINAL, SUMMARY, EXPECTED_COUNT, RUBRIC

OUTPUT = "AI_ONLY_REVIEW24_SCORE_LOCAL.json"


def summarize(project="."):
    root = Path(project).resolve()
    folder = root / OUT
    rated_path, summary_path = folder / FINAL, folder / SUMMARY
    if not rated_path.is_file() or not summary_path.is_file():
        raise FileNotFoundError("Complete the local AI review first")
    receipt = json.loads(summary_path.read_text(encoding="utf-8"))
    if (receipt.get("rubric") != RUBRIC or
            receipt.get("rated_csv_sha256") != _sha(rated_path) or
            receipt.get("blind_packet_sha256") != _sha(folder / REVIEW) or
            receipt.get("stage") !=
            "AI_ONLY_SAME_CORPUS_DEVELOPMENT_NOT_INDEPENDENT_VALIDATION"):
        raise ValueError("AI-only input fingerprints changed")
    original = csv_read(folder / REVIEW)
    rated = csv_read(rated_path)
    if len(original) != EXPECTED_COUNT or len(rated) != EXPECTED_COUNT:
        raise ValueError("Expected exactly 24 case ratings")
    forms = {r["blind_id"]: r for r in original}
    rr = {r["blind_id"]: r for r in rated}
    if len(forms) != 24 or len(rr) != 24 or set(forms) != set(rr):
        raise ValueError("Review IDs changed, missing or repeated")
    # Check every unchanged original field before opening the secret mapping.
    for bid, r in rr.items():
        if any(r.get(k) != forms[bid].get(k) for k in FIXED_REVIEW):
            raise ValueError("Frozen source evidence changed for " + bid)
        if (not r.get("reviewer_id", "").startswith("OLLAMA_LOCAL_") or
                not r.get("reviewer_id", "").endswith("_AI_ONLY")):
            raise ValueError("AI-only review mixed with a different reviewer")
        if len(r.get("review_notes", "").strip()) < 30:
            raise ValueError("Missing case-specific scientific rationale")
        suff = r.get("evidence_sufficient_yes_no", "")
        if suff not in ("yes", "no"):
            raise ValueError("Missing sufficiency judgment")
        titles = [r[arm + "_accuracy_accurate_vague_wrong"] for arm in ("A", "B")]
        claims = [r[arm + "_gloss_overclaim_yes_no_unclear"] for arm in ("A", "B")]
        if suff == "yes":
            if (any(v not in RATING for v in titles) or
                    any(v not in ("yes", "no", "unclear") for v in claims)):
                raise ValueError("Invalid sufficient-source ratings")
        elif any(titles) or claims != ["unclear", "unclear"]:
            raise ValueError("Insufficient-source case has determinate grades")
    keyfile = root / BASE / KEYS
    keys = csv_read(keyfile)
    mapping = {r["blind_id"]: r["v3_side"] for r in keys}
    if (len(mapping) != 24 or set(mapping) != set(forms) or
            any(v not in ("A", "B") for v in mapping.values())):
        raise ValueError("Invalid private A/B mapping")
    wins = losses = ties = sufficient = 0
    breakdown = {"v2": Counter(), "v3": Counter()}
    for bid, row in rr.items():
        v3 = mapping[bid]
        v2 = "B" if v3 == "A" else "A"
        if row["evidence_sufficient_yes_no"] == "yes":
            sufficient += 1
            delta = (RATING[row[v3 + "_accuracy_accurate_vague_wrong"]] -
                     RATING[row[v2 + "_accuracy_accurate_vague_wrong"]])
            wins += delta > 0
            losses += delta < 0
            ties += delta == 0
        for version, arm in (("v2", v2), ("v3", v3)):
            flag = row[arm + "_gloss_overclaim_yes_no_unclear"]
            breakdown[version]["unclear" if flag == "unclear" else "evaluable"] += 1
            if flag == "yes":
                breakdown[version]["overclaim"] += 1
    discordant = wins + losses
    pval = (min(1.0, 2 * sum(math.comb(discordant, k)
            for k in range(min(wins, losses) + 1)) / 2 ** discordant)
            if discordant else None)
    result = {
        "schema": "chronohyper_AI_ONLY_24case_development_score_v1",
        "stage": "LOCAL_AI_ONLY_DEVELOPMENT_NOT_HUMAN_NOT_INDEPENDENT",
        "model": receipt["model"], "rubric": RUBRIC,
        "cases": 24, "sufficient_source_cases": sufficient,
        "insufficient_cases": 24 - sufficient,
        "title_comparison": {
            "v3_wins": wins, "v3_losses": losses, "ties": ties,
            "discordant": discordant, "unadjusted_sign_p_descriptive_only": pval,
        },
        "overclaim_by_model": {
            model: {
                "overclaim": counts["overclaim"], "evaluable": counts["evaluable"],
                "unclear": counts["unclear"],
                "rate": (counts["overclaim"] / counts["evaluable"]
                         if counts["evaluable"] else None),
                "wilson_95ci": _wilson(counts["overclaim"], counts["evaluable"]),
            }
            for model, counts in breakdown.items()
        },
        "rated_csv_sha256": _sha(rated_path),
        "original_private_key_sha256": _sha(keyfile),
        "human_expert_validation": False,
        "independent_corpus_confirmation": False,
        "source_passages_mostly_abstracts": True,
        "no_grade_inflation_policy": "balanced fair rubric, abstain when unsupported",
        "original_independent_human_score_untouched": True,
        "do_not_present_as_independent_label_accuracy": True,
    }
    with (folder / OUTPUT).open("x", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", default=".")
    a = p.parse_args()
    summarize(a.project)


if __name__ == "__main__":
    main()
