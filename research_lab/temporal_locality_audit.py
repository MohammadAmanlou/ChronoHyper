"""Source-delta localization audit for frozen temporal hypergraph hierarchies.

A newly incident *original* hyperedge exposes an existing node to new source
evidence. Ask whether root-cluster identity changes concentrate among such nodes
rather than unrelated, unchanged-evidence nodes. The one-sided conditional
permutation shuffles *observed churn flags* within original type and prior-edge
degree strata; it is NOT a model performance claim or causal experiment.

Reads only data/tkh_collection10.json from the provider ZIP (never question
Gold), and immutable outputs_selected/hierarchy_{year}.json. Does not refit.
The post-hoc audit is separate from pre-registered scientific confirmation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile

YEARS = (2020, 2022, 2024)


def assignments(document):
    """One nonoverlapping level-0 cluster ID per source node."""
    observed = {}
    groups = [x for x in document["supernodes"] if x["level"] == 0]
    if not groups:
        raise ValueError("No level-0 supernodes")
    for group in groups:
        for node_id in group["member_ids"]:
            if node_id in observed:
                raise ValueError("Node in multiple root clusters: " + node_id)
            observed[node_id] = group["id"]
    if not observed:
        raise ValueError("Empty root partition")
    return observed


def dated_edges(graph, cutoff, excluded_source_papers=()):
    """Mirror src.run.snapshot_raw source and endpoint cutoff conditions."""
    visible = {n["id"] for n in graph["nodes"] if int(n["first_seen_year"]) <= cutoff}
    excluded = set(map(str, excluded_source_papers))
    rows = {}
    for edge in graph["hyperedges"]:
        if (str(edge.get("provenance", {}).get("article_id", "")) in excluded or
                int(edge["year"]) > cutoff or
                int(edge.get("provenance", {}).get("article_year", edge["year"])) > cutoff or
                not all(v in visible for v in edge["members"])):
            continue
        edge_id = edge["id"]
        if edge_id in rows:
            raise ValueError("Duplicate original hyperedge ID " + edge_id)
        rows[edge_id] = set(edge["members"])
    return rows


def _degree_bucket(degree):
    if degree == 0:
        return "0"
    if degree == 1:
        return "1"
    if degree <= 3:
        return "2-3"
    return "4+"


def _rate(num, den):
    return num / den if den else None


def paired_locality(graph, old_document, new_document, old_year, new_year,
                    *, repetitions=999, seed=17, excluded_source_papers=()):
    if new_year <= old_year or repetitions < 1:
        raise ValueError("Snapshots must advance and repetitions >= 1")
    before = assignments(old_document)
    after = assignments(new_document)
    original = dated_edges(graph, old_year, excluded_source_papers)
    evolved = dated_edges(graph, new_year, excluded_source_papers)
    if not set(original) <= set(evolved):
        raise ValueError("Temporal original event IDs are not nested")
    if not set(before) <= set(after):
        raise ValueError("Original hierarchy source node membership is not nested")
    # Stability of original event contents is part of provenance correctness.
    for edge_id, endpoints in original.items():
        if endpoints != evolved[edge_id]:
            raise ValueError("Existing original hyperedge endpoints mutated")
    source_nodes = {n["id"]: n for n in graph["nodes"]}
    shared = sorted(before)
    if set(shared) - set(source_nodes):
        raise ValueError("Unknown source nodes in original partitions")
    new_edges = set(evolved) - set(original)
    touched_nodes = set().union(*(evolved[e] for e in new_edges)) if new_edges else set()
    touched = {v for v in shared if v in touched_nodes}
    unchanged = set(shared) - touched
    changed = {v for v in shared if before[v] != after[v]}
    a = len(changed & touched)
    b = len(touched) - a
    c = len(changed & unchanged)
    d = len(unchanged) - c
    exposure_delta = None if not touched or not unchanged else a / len(touched) - c / len(unchanged)

    degrees = Counter()
    for endpoints in original.values():
        degrees.update(endpoints)
    strata = defaultdict(list)
    for node in shared:
        group = (source_nodes[node]["type"], _degree_bucket(degrees[node]))
        strata[group].append(node)
    # Permute changed labels within SOURCE TYPE and BASELINE DEGREE strata:
    # preserve strata-specific number of changes; preserve touched groups.
    rng = random.Random(seed)
    null_counts = []
    expected = 0.0
    for group in strata.values():
        expected += len(touched.intersection(group)) * len(changed.intersection(group)) / len(group)
    for _ in range(repetitions):
        count = 0
        for group in strata.values():
            n_changed = len(changed.intersection(group))
            if n_changed:
                count += len(set(rng.sample(group, n_changed)) & touched)
        null_counts.append(count)
    p = (1 + sum(x >= a for x in null_counts)) / (repetitions + 1)
    null_mean = sum(null_counts) / len(null_counts)
    null_var = sum((x - null_mean) ** 2 for x in null_counts) / len(null_counts)

    return {
        "transition": f"{old_year}-{new_year}",
        "old_snapshot": old_year,
        "new_snapshot": new_year,
        "shared_preexisting_nodes": len(shared),
        "new_source_nodes": len(set(after) - set(before)),
        "old_hyperedges": len(original),
        "new_hyperedges_added": len(new_edges),
        "shared_nodes_touched_by_new_native_hyperedge": len(touched),
        "shared_nodes_not_touched_by_new_native_hyperedge": len(unchanged),
        "root_identity_changes_total": len(changed),
        "root_identity_changes_touched": a,
        "root_identity_changes_untouched": c,
        "touched_change_rate": _rate(a, a + b),
        "untouched_change_rate": _rate(c, c + d),
        "touched_minus_untouched_change_rate": exposure_delta,
        "fraction_of_churn_on_new_edge_endpoints": _rate(a, len(changed)),
        "stratification": "original node type x original training-hyperedge incidence degree {0,1,2-3,4+}",
        "strata_count": len(strata),
        "stratified_null_expected_touched_churn": expected,
        "stratified_permutation_null_mean": null_mean,
        "stratified_permutation_null_sd": math.sqrt(null_var),
        "one_sided_permutation_p_churn_enrichment_exploratory": p,
        "permutations": repetitions,
        "seed": seed,
        "table": {"touched_changed": a, "touched_unchanged": b,
                  "untouched_changed": c, "untouched_unchanged": d},
        "limitation": (
            "Post-hoc association, not causality; source-edge incidence is not "
            "the whole scientific semantic change; persistent cluster IDs are "
            "overlap-matched heuristic. Counts across two transitions overlap."
        ),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", default=".")
    ap.add_argument("--permutations", type=int, default=999)
    ap.add_argument("--seed", type=int, default=17)
    ap.add_argument("--out", default="local_only/temporal_locality_audit.json")
    args = ap.parse_args()
    root = Path(args.project).resolve()
    archive = root / "inputs/data.zip"
    manifest = json.loads((root / "outputs_selected/selected_export_manifest.json").read_text(encoding="utf-8"))
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    if checksum != manifest["dataset_sha256"]:
        raise ValueError("The source ZIP digest does not match the frozen selected hierarchy")
    excluded = set(map(str, manifest["paper_ids_excluded_from_training"]))
    with ZipFile(archive) as z:
        graph = json.loads(z.read("data/tkh_collection10.json"))
    # Model fit used only non-held-out source papers. Confirm identical
    # original event identities against frozen T4 collapsed output.
    for year in YEARS:
        training_events = dated_edges(graph, year, excluded)
        collapsed = json.loads((root / f"outputs_selected/collapsed_edges_{year}_level0.json").read_text(encoding="utf-8"))
        measured = {entry["id"] for entry in collapsed}
        if set(training_events) != measured:
            raise ValueError(
                f"Fitting-event mismatch for {year}: expected {len(training_events)} "
                f"science-only training edges, frozen collapsed output has {len(measured)}. "
                "Never mix held-out source events into a training-locality claim."
            )
    docs = {year: json.loads((root / f"outputs_selected/hierarchy_{year}.json").read_text(encoding="utf-8"))
            for year in YEARS}
    transitions = [
        paired_locality(graph, docs[a], docs[b], a, b,
                        repetitions=args.permutations, seed=args.seed + i,
                        excluded_source_papers=excluded)
        for i, (a, b) in enumerate(zip(YEARS, YEARS[1:]))
    ]
    record = {
        "schema": "chronohyper_source_delta_temporal_locality_posthoc_v1",
        "stage": "POSTHOC_SAME_CORPUS_EXPLORATORY_NO_GOLD",
        "years": list(YEARS),
        "definition": (
            "Touched: a shared preexisting source node incident to >=1 original "
            "hyperedge first present at the later snapshot. Churn: overlap-matched "
            "root cluster identity changed, not scientific semantic truth."
        ),
        "test": "one-sided permutation of churn within original node-type x prior-incidence-degree strata",
        "source": "original provider science-only hypergraph, frozen selected TRAINING hyperedges and hierarchy roots",
        "original_provider_zip_sha256_verified": checksum,
        "excluded_heldout_source_paper_count": len(excluded),
        "training_event_ids_matched_frozen_collapsed_outputs": True,
        "gold_questions_read": False,
        "new_model_fitted": False,
        "multiple_comparisons_adjusted": False,
        "transitions": transitions,
    }
    target = root / args.out
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise FileExistsError("Never overwrite a prior observational audit: " + str(target))
    target.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
