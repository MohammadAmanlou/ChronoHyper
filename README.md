# ChronoHyper
**Native multi-resolution abstraction of an evolving scientific knowledge hypergraph**

Mohammad Amanlou · Constructor Knowledge Labs PhD research assessment · Python 3.11 · **private-source corpus**

ChronoHyper constructs source-dated, laminar four-level concept hierarchies from native higher-order scientific events. It tracks concept identities over time, preserves original hyperedge provenance/multiplicity, and compares semantic, structural, temporal and pairwise baselines using a locked method. It reports negative outcomes rather than overstating generalization.

**Read the [four-page scientific report](report.pdf) first.** Its editable source is [scripts/report.tex](scripts/report.tex); [report.md](report.md) is the full text companion. The report build and source/PDF text equivalence have passed a [clean CI check](.github/workflows/published-report.yml). Passing code tests is **not** proof of scientifically faithful topic labels or of admission.

## Assignment-facing deliverables

| Official request | Primary artifact |
|---|---|
| Formal objective, native hypergraph coarsening and limits | [report.pdf](report.pdf) · [src/core.py](src/core.py) |
| Hierarchies at 2020, 2022, 2024 (2025 exploratory) | [outputs_selected/](outputs_selected/) — `hierarchy_YEAR.json` |
| Hyperedge collapse with preserved provenance | [outputs_selected/](outputs_selected/) — `collapsed_edges_YEAR_level0.json` |
| Birth / growth / merge / split / death | [temporal_events.json](outputs_selected/temporal_events.json) |
| Source-backed selected-model evaluation | [metrics.json](metrics.json) · [docs/EVALUATION.md](docs/EVALUATION.md) |
| Scientific-review status against **every T1–T7 requirement** | [docs/ASSESSMENT_STATUS.md](docs/ASSESSMENT_STATUS.md) |
| Clean reproducibility and code tests | [docs/REPRODUCE.md](docs/REPRODUCE.md) · [requirements.txt](requirements.txt) |
| AI-assistance disclosure | [AI_USAGE.md](AI_USAGE.md) |

## What the results actually show

- **Model lock:** `native_temporal_20`, selected before source-group confirmation; **65** development, **5** confirmation and **5** pairwise-projection method runs are archived. Hierarchy budget/membership checks and native collapse provenance checks pass.
- **Negative structural test:** degree/arity-preserving null **p=0.69** (not significant). Lower-is-better source-group held-out event cut **worsened from 0.6623 to 0.7172**. The selected model is a semantic/structure/**temporal stability compromise**, not a proven best partitioner.
- **Historical downstream task:** on **14 previously inspected Type-A questions**, four-root and flat retrieval both hit **2/14**. Four-root routing used **57.9% fewer online candidate+centroid dot products** on those queries, not proven superior retrieval accuracy. Four Type-B questions were audited for *available paper-source coverage*, **not** generated-answer correctness. A 36-claim AI-only source assessment returned **25 yes / 1 no / 10 unclear**; a second AI review of nine concerns changed one opinion to yes and found **three Q17 source claims do not answer the coarse-grained-MD research question**. See [Assessment Status](docs/ASSESSMENT_STATUS.md).
- **V3 source audit:** all **180/180** development labels' frozen-membership/lexical/date support checked with **zero source-level discrepancies**; **115/180** abstain. *This does not establish scientific-paper entailment.*
- **Post-lock AI-only review (20 October):** 24 V2/V3 candidate pairs were graded; **21 evaluable**, V3 **10 wins / 4 losses / 7 ties**, descriptive `p=0.180` (no significant V3 advantage). On **24** matched real/control coherence pairs, mean 5-point AI ratings were **3.542 versus 2.750**, descriptive `p=0.041`. These are **key-separated same-corpus name/title judgements**, *not* certified full-text independent scientific evaluation. Details, insufficiency denominators and hashes: [Assessment Status](docs/ASSESSMENT_STATUS.md).

## Reproduce (Windows PowerShell)

```powershell
cd C:\Users\a\Desktop\constructor-ckl-research
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Fast tests and immutable output verification:
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m unittest research_lab.tests_lab research_lab.test_label_v2 research_lab.test_type_b_source_audit -v
.\.venv\Scripts\python.exe -m unittest research_lab.test_retrieval_frontier research_lab.test_frontier_historical research_lab.test_v3_provenance_audit research_lab.test_review_handoff research_lab.test_assessment_status -v
.\.venv\Scripts\python.exe verify_selected_outputs.py --out outputs_selected

# After actual private reviewer CSVs have been scored:
.\.venv\Scripts\python.exe -m research_lab.assessment_status --project .
```

The full all-in-one safe rerun (which **does not rerun the 75 heavy model jobs**) is `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\continue_local_validation.ps1`. See [the precise reproduction runbook](docs/REPRODUCE.md). Code tests operate on synthetic fixtures or the supplied corpus; no newly published label full-text truth is being manufactured.

## Repository layout: one path per purpose

```text
report.pdf / report.md / metrics.json    ← canonical assessment deliverables
src/                                    ← main pipeline and native hypergraph solver
outputs_selected/                       ← locked model hierarchies and events
research_lab/                           ← evaluation code, comparison and tests
research_outputs/                       ← immutable experiments, nulls, audits
outputs/                                ← original archival baseline, NOT selected
docs/                                   ← original brief, validation and method details
scripts/                                ← PDF source and reproduction automation
local_only/ (git-ignored)               ← private reviewer files, blind keys, backups
```

To avoid losing audit traceability, **do not delete/move archived experimental outputs just to shorten the tree**. Git-ignored scratch and reviewer contents stay local; private identity mappings, full reviewer notes and private ratings are never part of the public deliverables.

## Prospective retrieval study — pending independent question writing

A [root-stratified 36-target author kit](research_lab/fresh_retrieval.py) now
selects dated entities from the existing 2025 source index deterministically
(three per root), before any new query sees model rankings. An isolated
question author must supply 36 properly sourced **paraphrased new questions**;
the benchmark then freezes question texts and private Gold separately
before running the matched four-root-vs-flat retrieval test. The isolated author delivered 36 rows, but **F023 and F031 have
documented unverifiable original paper associations**. A pre-rank,
source-screened 34-question option is available with all 36 attempts
and exclusion reasons retained; see
[reproduction instructions](docs/REPRODUCE.md). The applicant has now scored **34 of 36** original targets after
two independently documented **pre-ranking** source failures.
The predeclared four-root route obtained **2/34** Type-A Hit@5
versus **3/34** for Flat, with **59.3% fewer online dot products**.
This is an honest *negative/ambiguous accuracy* result, not superior
retrieval or an independent new corpus. A separate local JSON integrity
audit must be run before publishing its safe aggregate. Exact
[commands and integrity requirements](docs/REPRODUCE.md#18--prospective-stratified-new-question-retrieval-test-22-october).

## Optional GPU semantic retrieval and actual Type-B answer evaluation

The frozen 34-query result (Flat **3/34**, Route-4 **2/34**) has NOT
been modified. A GPU-evaluated, exploratory research module builds a dated
native-hyperedge co-mention index, BGE-M3 dense embeddings, lexical
TF-IDF, rank-based fusion, BGE neural reranking and a soft root-aware
non-pruning comparison. Observed 22 October GPU result (34 already-inspected questions; post-hoc development only): BGE-M3 dense Hit@5=10/34 (29.41%, MRR@5=0.1887); new lexical=4/34, hybrid RRF=6/34, neural reranker=1/34, and reranker+soft root=1/34. Previous separately frozen Flat=3/34 and route4=2/34 remain unchanged. No improved independent-test accuracy, no Type-B generated-answer accuracy and no significant generalization claim.

A separate module generates actual Type-B Q15–Q18 scientific answers
using a local Qwen2.5-3B-Instruct model and authenticated dated full-text
primary passages and creates a separate AI scoring rubric. **No new
Type-B generated answers/scores are claimed yet.** See the one
[GPU and Type-B runbook](docs/ADVANCED_GPU_AND_TYPE_B.md).
The locked model, root report PDF and original negative results remain
unchanged.

## Remaining scientific boundaries

The **36 Type-B paper claims** now have an AI-only review (25/1/10) but **not a verified independent full-text or task-grounded adjudication**; the older user-created `local_only/reviews/claims_rated.csv` is a separate blank working copy. Nine second-pass concerns need resolution. A truly new question set with pre-frozen gold is also missing. The two new AI evaluations don't remove the coherence circularity risk or override the structural null. See [exact outstanding gates](docs/ASSESSMENT_STATUS.md) and [safe independent reviewer protocol](docs/INDEPENDENT_VALIDATION.md).

**Scope:** the official task does *not* require an interactive frontend, production infrastructure, or training new language models. This repo prioritizes correct hypergraph methods, honest evaluation, temporal identity and reproducibility.
