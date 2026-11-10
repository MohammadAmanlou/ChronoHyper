"""V4 exploratory rendering: keep scientific titles separate from evidence/abstention.

This is NOT a new fitted method, not a post-hoc repair of 24 inspected labels,
and not a quality improvement claim. It uses exactly the frozen V2 evidence
and V3 thresholds and publishes no original-corpus/private evaluation data.
No source papers, fulltext local reviews, gold or blind A/B keys are read.

Design: a name phrase can be a qualified observed topic *candidate* without
being certified full-paper scientific truth. If no phrase qualifies, display
a neutral "Unresolved topic" with separately identified observed terms, if any.
Never treat abstention as assertion that all cluster members are unrelated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from research_lab.label_v3 import (
    GENERIC, MIN_ARTICLES, MIN_MAJOR, MIN_PARTIAL,
    _domain_phrase, improve_case,
)

YEARS = (2020, 2022, 2024)
OUT = Path("local_only/label_v4_exploratory")
STAGE = "EXPLORATORY_PRESENTATION_ONLY_NO_HUMAN_VALIDATION"
PRIMARY_STATES = {
    "LEADING_NAME_PHRASE_MAJORITY": "MAJORITY_LEXICAL_CANDIDATE",
    "PARTIAL_NAME_PHRASE": "PARTIAL_LEXICAL_CANDIDATE",
    "ABSTAIN_INSUFFICIENT_DOMAIN_PHRASE": "NO_QUALIFIED_LEXICAL_TOPIC",
}


def _observed_terms(row, max_terms=2):
    """Show *observed* V2 phrases, without calling them unified themes."""
    ev = row.get("phrase_evidence", {})
    # Original V2 phrase_evidence contains only selected phrases with source ids.
    # These are descriptive hints, NOT independent topic certainty.
    gathered = []
    n = int(row["eligible_member_count"])
    for term, record in ev.items():
        count = int(record.get("support_count", -1))
        ids = record.get("support_node_ids", [])
        paper_ids = record.get("provenance_article_ids", [])
        if count != len(ids) or count < 0 or count > n:
            raise ValueError("Invalid V2 phrase evidence count")
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate V2 phrase supporter")
        if not _domain_phrase(term):
            continue
        gathered.append({
            "term": term,
            "name_mention_count": count,
            "eligible_members": n,
            "article_provenance_count": len(set(map(str, paper_ids))),
            "disclaimer": "OBSERVED_NODE_NAME_TERM_NOT_VERIFIED_SCIENTIFIC_TOPIC",
        })
    gathered.sort(key=lambda x: (-x["name_mention_count"], x["term"]))
    return gathered[:max_terms]


def render_case(row):
    """Return a separate display candidate, status, scoped gloss and evidence."""
    v3 = improve_case(row)
    state = PRIMARY_STATES[v3["label_rule_status"]]
    candidate = v3["source_phrase_evidence"]
    if candidate is None:
        title = "Unresolved topic"
        # Explicitly avoid claiming genuine heterogeneity from nonfulfillment
        # of a lexical coverage filter.
        gloss = (
            "At the {year} cutoff, the archived candidate phrases did not meet "
            "the 30% name coverage, specificity and two-paper provenance rule. "
            "This is insufficient evidence for a specific label, not evidence "
            "that no shared scientific topic exists."
        ).format(year=v3["year"])
    else:
        title = candidate["phrase"].title()
        gloss = (
            "At the {year} cutoff, {inside}/{n} eligible non-metadata node "
            "names explicitly mention '{phrase}' (from {papers} linked "
            "source articles). This is exact-name provenance, not verified "
            "full-paper scientific entailment."
        ).format(
            year=v3["year"], inside=candidate["support_count"],
            n=candidate["eligible_count"], phrase=candidate["phrase"],
            papers=candidate["source_article_count"],
        )
    return {
        "year": v3["year"],
        "stable_id": v3["stable_id"],
        "level": v3["level"],
        "source_member_count": v3["member_count"],
        "eligible_member_count": v3["eligible_member_count"],
        "display_title": title,
        "display_gloss": gloss,
        "lexical_evidence_state": state,
        "abstained_from_specific_topic": candidate is None,
        "observed_terms_not_confirmed_topics": _observed_terms(row),
        "qualifying_source_phrase_evidence": candidate,
        "v2_original_label_reference": v3["v2_original_label"],
        "v3_original_label_reference": v3["v3_development_label"],
        "lexical_filters_unchanged_from_v3": True,
        "scientific_semantic_accuracy": "NOT_INDEPENDENTLY_MEASURED",
        "no_new_fulltext_or_gold": True,
        "experiment_status": STAGE,
    }


def run(project=".", out=str(OUT)):
    root = Path(project).resolve()
    destination = Path(out)
    if not destination.is_absolute():
        destination = root / destination
    if destination.exists():
        raise FileExistsError("Preserve the first exploratory V4 candidate output; do not overwrite")
    frozen = []
    outputs = {}
    for year in YEARS:
        path = root / "research_outputs" / "label_v2" / (
            "candidates_v2_{}.json".format(year))
        if not path.is_file():
            raise FileNotFoundError(str(path))
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        records = [render_case(row) for row in data
                   if int(row["level"]) in (0, 1)]
        if len(records) != 60 or len({
                (x["level"], x["stable_id"]) for x in records}) != 60:
            raise ValueError("Expected 60 frozen V2 source clusters for " + str(year))
        outputs[year] = records
        frozen.append({
            "year": year, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "record_count": len(records),
            "by_state": dict(Counter(x["lexical_evidence_state"] for x in records)),
        })
    # All source inputs validated before writing any result.
    destination.mkdir(parents=True, exist_ok=False)
    for year, records in outputs.items():
        (destination / "v4_exploratory_{}.json".format(year)).write_text(
            json.dumps(records, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8")
    summary = {
        "schema": "chronohyper_v4_evidence_separated_presentation_v1",
        "stage": STAGE,
        "description": "Separate title/lexical confidence/abstention; no new topic predictor",
        "freeze": frozen, "years": list(YEARS),
        "n_records": sum(len(rows) for rows in outputs.values()),
        "thresholds_identical_to_v3": {
            "partial_name_coverage": MIN_PARTIAL,
            "majority_name_coverage": MIN_MAJOR,
            "article_provenance_min": MIN_ARTICLES,
        },
        "v2_original_outputs_unchanged": True,
        "v3_original_outputs_unchanged": True,
        "scientific_overclaim_rate_independently_measured": False,
        "24_original_blind_cases_not_reused_as_confirmatory_test": True,
        "next_step": (
            "Design and preregister an independently reviewed set of NEW "
            "case-paper question/label judgments, with separate abstention "
            "appropriateness and title-accuracy dimensions."),
    }
    (destination / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=".")
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args()
    run(args.project, args.out)


if __name__ == "__main__":
    main()
