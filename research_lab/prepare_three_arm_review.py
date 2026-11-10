"""Prepare a NEW, case-disjoint 3-arm V2/V3/V4 blind evidence-intake packet.

This is a POST-HOC SAME-CORPUS development candidate set, NOT independent
confirmation. No evaluator is run; no review grades or source passages
are invented. V4 only separates title/display from lexical abstention.
All original corpus nodes and private prior-review keys remain local-only.

Run:
 python -m research_lab.prepare_three_arm_review --project . --prepare
 python -m research_lab.prepare_three_arm_review --project . --status
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random

from research_lab.blind_paper_eval import _eligible, _source, _titles, csv_read, csv_write
from research_lab.label_v3 import improve_case
from research_lab.label_v4_exploratory import render_case

YEARS = (2020, 2022, 2024)
PER_YEAR = 4
SAMPLE_N = 14
MAX_PAPERS = 4
SEED = 20261111
OUT = Path("local_only/reviews/three_arm_new_development")
PRIOR_V2 = Path("research_outputs/label_v2/BLIND_LABEL_COMPARISON_TO_FILL.csv")
PRIOR_V3 = Path("local_only/reviews/label_v3_fresh/mapping_PRIVATE.csv")
PRIOR_COHERENCE = Path("local_only/reviews/fresh_semantic/condition_key_PRIVATE.csv")
ARMS = ("A", "B", "C")
EXPERIMENTS = ("v2", "v3", "v4")
PREVIEW_FIELDS = (
    "blind_id", "snapshot_year", "sampled_member_names",
    "linked_article_titles_context_only",
    "title_A", "gloss_A", "title_B", "gloss_B", "title_C", "gloss_C",
    "source_evidence_status",
)
KEY_FIELDS = ("blind_id", "snapshot_year", "stable_id", "A_method",
              "B_method", "C_method")
CASE_LINK_FIELDS = ("blind_id", "snapshot_year", "paper_id", "paper_title",
                    "paper_year", "source_selection_reason")
PAPER_FIELDS = ("paper_id", "paper_title", "paper_year", "source_url",
                "historical_version_date", "passage_locator",
                "authentic_primary_passage", "access_permission_confirmed_yes_no",
                "historical_version_verified_yes_no", "source_notes")
MANIFEST = "manifest_PRIVATE.json"
FORM = "BLIND_3ARM_PREVIEW_NOT_YET_RATABLE.csv"
KEY = "mapping_PRIVATE.csv"
LINKS = "CASE_PAPER_LINKS_PRIVATE.csv"
LIBRARY = "PRIMARY_PAPERS_TO_VERIFY_LOCAL.csv"
RUBRIC = "PREDECLARED_REVIEW_RUBRIC.txt"

RUBRIC_TEXT = """POST-HOC THREE-ARM BLIND SCIENTIFIC REVIEW: SOURCE INTAKE FIRST.
This worksheet is a PREVIEW ONLY, NOT a source-verified judge packet.
Do not score its A/B/C titles from name overlaps or paper titles alone.
Do not send Constructor-related names, text, or evidence to an external
person, service or LLM without explicit corpus-sharing permission.

Before independent review:
(1) screen the PRIMARY_PAPERS_TO_VERIFY_LOCAL.csv library against authentic
    primary publications and versions actually available by the case year;
(2) verify paper URL, version date, locator, scientific relevance, and
    permission to read/share. Source metadata is NOT verified by this code;
(3) assemble a dated, sufficiently detailed, case-linked reviewer packet
    while keeping the A/B/C private key outside the reviewer context.

PREDECLARED SEPARATE OUTCOMES FOR EACH BLIND ARM:
Title scientific validity: supported/partially_supported/misleading/unclear.
Title informativeness: integer 1..5 ONLY if sufficient scientific evidence.
Abstention appropriateness: appropriate/inappropriate/unclear/not_applicable
  (do NOT treat abstention as a positive scientific claim by default).
Gloss scientific overclaim: yes/no/unclear, separately from graph-name count
  provenance; source-paper abstracts do NOT verify graph internal counts.
Reviewer must note specific dated paper evidence and disagreement/uncertainty.
A/B/C sequence is shuffled independently per case, no prior scores in packet.

NO review or score tool is activated by --prepare. A valid measured result
requires real filled ratings, source screening, proper validity checks, the
hidden key opened ONLY AFTER all blind ratings are frozen, and a fresh-case
analysis distinguished from independent external-corpus confirmation.
This sample is post-hoc and same-corpus by construction; do NOT present
its results as untouched external, preregistered, or independent replication.
"""


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _existing_exclusions(root):
    # Explicitly require the earlier 24-case V3 key. Its hidden side is NEVER
    # used; year/stable_id are read ONLY for excluding already evaluated cases.
    must = (root / PRIOR_V2, root / PRIOR_V3)
    for path in must:
        if not path.is_file():
            raise FileNotFoundError("Cannot prove case exclusion without " + str(path))
    old = csv_read(must[0])
    v3 = csv_read(must[1])
    if len(old) != 24 or len(v3) != 24:
        raise ValueError("Unexpected frozen prior-review size; refuse sampling")
    excluded = set()
    for row in old:
        excluded.add((int(row["year"]), row["stable_id"]))
    for row in v3:
        excluded.add((int(row["year"]), row["stable_id"]))
    if len(excluded) < 24:
        raise ValueError("Prior review case list is incomplete or duplicated")
    sources = {"old_v2_review": sha(must[0]), "old_v3_review_private_key": sha(must[1])}
    # Earlier matched-coherence review may have been prepared locally.
    # If available, exclude its REAL targets too. Its donor controls and
    # partial shared papers still prevent external-corpus independence.
    prior = root / PRIOR_COHERENCE
    coherence_status = "NOT_FOUND_UNVERIFIED_PAST_CASE_COVERAGE"
    if prior.is_file():
        rows = csv_read(prior)
        if len(rows) != 48:
            raise ValueError("Prior 48-row coherence key malformed")
        excluded.update((int(r["snapshot_year"]), r["target_cluster"]) for r in rows)
        sources["prior_coherence_key"] = sha(prior)
        coherence_status = "48_ROW_REAL_TARGETS_EXCLUDED"
    return excluded, sources, coherence_status


def _case_papers(members, papers, year):
    matched = Counter()
    for node in members:
        for aid in set(map(str, node.get("provenance", {}).get("articles", []))):
            paper = papers.get(aid)
            if paper is None or not paper.get("title", "").strip():
                continue
            try:
                pyear = int(paper["year"])
            except (ValueError, TypeError, KeyError):
                continue
            if pyear <= year:
                matched[aid] += 1
    chosen = sorted(matched, key=lambda x: (-matched[x], int(papers[x]["year"]), x))
    return [(aid, papers[aid], matched[aid]) for aid in chosen[:MAX_PAPERS]]


def _cases(root, rng, excluded):
    nodes, papers = _source(root)  # ONLY corpus nodes + paper metadata, no Gold.
    indexed = {n["id"]: n for n in nodes}
    selected = []
    snapshots = []
    for year in YEARS:
        path = root / "research_outputs/label_v2/candidates_v2_{}.json".format(year)
        items = json.loads(path.read_text(encoding="utf-8-sig"))
        eligible = []
        for item in items:
            if int(item["level"]) != 1:
                continue
            key = (year, item["stable_id"])
            if key in excluded:
                continue
            members = [
                indexed[nid] for nid in item["member_ids"]
                if _eligible(indexed[nid], year)
            ]
            if len(members) < SAMPLE_N:
                continue
            eligible.append((item, members))
        snapshots.append({"year": year, "candidate_sha256": sha(path),
                          "not_previously_reviewed_case_candidates": len(eligible)})
        if len(eligible) < PER_YEAR:
            raise ValueError(
                "Only {} unreviewed qualifying level-1 cases in {}; "
                "do NOT silently reuse previous reviewed cases".format(
                    len(eligible), year))
        for item, members in rng.sample(sorted(
                eligible, key=lambda x: x[0]["stable_id"]), PER_YEAR):
            selected.append((year, item, rng.sample(members, SAMPLE_N)))
    rng.shuffle(selected)
    return selected, papers, snapshots


def prepare(project="."):
    root = Path(project).resolve()
    out = root / OUT
    if out.exists():
        raise FileExistsError("Original new-case blind packet is frozen; refusing overwrite")
    excluded, inputs, coherence_status = _existing_exclusions(root)
    rng = random.Random(SEED)
    chosen, papers, snapshots = _cases(root, rng, excluded)
    if len(chosen) != 12:
        raise AssertionError("Expected 4 cases per historical snapshot")
    form, secret, links, library = [], [], [], {}
    case_keys = set()
    for index, (year, item, members) in enumerate(chosen, 1):
        cid = "N{:03d}".format(index)
        case_key = (year, item["stable_id"])
        if case_key in case_keys or case_key in excluded:
            raise ValueError("Duplicate or already-inspected case " + str(case_key))
        case_keys.add(case_key)
        v3 = improve_case(item)
        v4 = render_case(item)
        methods = {
            "v2": (item["v2_label"], item["v2_gloss"]),
            "v3": (v3["v3_development_label"], v3["v3_development_gloss"]),
            "v4": (v4["display_title"], v4["display_gloss"]),
        }
        order = list(EXPERIMENTS)
        rng.shuffle(order)
        record = {
            "blind_id": cid, "snapshot_year": str(year),
            "sampled_member_names": " | ".join(m["surface_form"] for m in members),
            "linked_article_titles_context_only": " | ".join(_titles(members, papers, year)),
            "source_evidence_status": "SOURCE_SCREENING_REQUIRED_NO_SCIENTIFIC_RATING",
        }
        keyrow = {"blind_id": cid, "snapshot_year": str(year),
                  "stable_id": item["stable_id"]}
        for arm, method in zip(ARMS, order):
            record["title_" + arm], record["gloss_" + arm] = methods[method]
            keyrow[arm + "_method"] = method
        form.append(record)
        secret.append(keyrow)
        for aid, paper, name_count in _case_papers(members, papers, year):
            links.append({
                "blind_id": cid, "snapshot_year": str(year),
                "paper_id": aid, "paper_title": paper["title"],
                "paper_year": str(paper["year"]),
                "source_selection_reason": (
                    "SAMPLED_MEMBER_PROVENANCE_COUNT_{}".format(name_count)),
            })
            library[aid] = {
                "paper_id": aid, "paper_title": paper["title"],
                "paper_year": str(paper["year"]),
                "source_url": "", "historical_version_date": "",
                "passage_locator": "", "authentic_primary_passage": "",
                "access_permission_confirmed_yes_no": "",
                "historical_version_verified_yes_no": "",
                "source_notes": "",
            }
    if not links or not library:
        raise ValueError("No paper metadata links exist; refuse source-less evaluation kit")
    # No private data leaves root/local_only. Validate all inputs BEFORE writing.
    out.mkdir(parents=True, exist_ok=False)
    csv_write(out / FORM, form, PREVIEW_FIELDS)
    csv_write(out / KEY, secret, KEY_FIELDS)
    csv_write(out / LINKS, links, CASE_LINK_FIELDS)
    csv_write(out / LIBRARY, [
        library[k] for k in sorted(library, key=lambda x: (int(library[x]["paper_year"]), x))
    ], PAPER_FIELDS)
    (out / RUBRIC).write_text(RUBRIC_TEXT, encoding="utf-8")
    receipt = {
        "schema": "chronohyper_v234_blind_new_case_screening_v1",
        "stage": "SOURCE_SCREENING_REQUIRED_NOT_RATED",
        "cases": len(form), "cases_by_snapshot": {str(y): PER_YEAR for y in YEARS},
        "source_case_paper_associations": len(links),
        "unique_linked_source_papers": len(library),
        "previously_reviewed_case_keys_excluded": len(excluded),
        "coherence_exclusion_status": coherence_status,
        "same_original_corpus": True,
        "posthoc_design_following_seen_v2_v3_losses": True,
        "independent_confirmation_not_possible_from_this_packet": True,
        "no_source_fulltext_verified": True,
        "no_real_ratings_yet": True,
        "no_A_B_C_method_mapping_sent_to_reviewer": True,
        "no_hidden_gold_read": True,
        "source_input_sha256": inputs,
        "candidate_sha256_by_year": snapshots,
        "preview_sha256": sha(out / FORM),
        "private_mapping_sha256": sha(out / KEY),
        "source_library_sha256_initial": sha(out / LIBRARY),
        "rubric_sha256": sha(out / RUBRIC),
    }
    (out / MANIFEST).write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    print("NEXT: inspect LOCAL source-paper library; no AI scoring yet.")
    return receipt


def status(project="."):
    out = Path(project).resolve() / OUT
    receipt = json.loads((out / MANIFEST).read_text(encoding="utf-8"))
    if (sha(out / FORM) != receipt["preview_sha256"] or
            sha(out / KEY) != receipt["private_mapping_sha256"] or
            sha(out / RUBRIC) != receipt["rubric_sha256"]):
        raise ValueError("Original blind preview, key or rubric changed")
    library = csv_read(out / LIBRARY)
    verified = sum(
        r["historical_version_verified_yes_no"].strip().lower() == "yes"
        and r["access_permission_confirmed_yes_no"].strip().lower() == "yes"
        and len(r["authentic_primary_passage"].strip()) >= 90
        and bool(r["source_url"].strip()) and bool(r["historical_version_date"].strip())
        and bool(r["passage_locator"].strip())
        for r in library
    )
    result = {
        "stage": "LOCAL_SOURCE_SCREENING_STATUS_NOT_AI_RATING",
        "cases": receipt["cases"],
        "unique_papers": len(library),
        "locally_user_attested_complete_paper_records": verified,
        "pending_paper_records": len(library)-verified,
        "source_verification_independently_confirmed_by_software": False,
        "scientific_judgments_recorded": 0,
        "ready_for_blind_semantic_rating": False,
        "private_method_mapping_read": False,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    action = p.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--status", action="store_true")
    p.add_argument("--project", default=".")
    a = p.parse_args()
    if a.prepare:
        prepare(a.project)
    else:
        status(a.project)


if __name__ == "__main__":
    main()
