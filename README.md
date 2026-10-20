# ChronoHyper
**Temporal multi-resolution abstraction of a scientific knowledge hypergraph**  
Mohammad Amanlou · Constructor Knowledge Labs doctoral assessment · Python 3.11 · **private dataset**

This is the **single entry point** for the project. Start with the completed [four-page scientific report](report.pdf) ([camera-ready LaTeX source](scripts/report.tex)); [report.md](report.md) is a plain-text scientific companion. The GitHub build verified the newly compiled PDF before publishing it to `main`. The selected model is `native_temporal_20`, frozen before the source-grouped confirmation evaluation. The repository records positive, negative and incomplete findings; passing software tests does **not** prove scientific label faithfulness or admission.

## What is inside

| Path | Purpose |
|---|---|
| [`report.pdf`](report.pdf) · [`scripts/report.tex`](scripts/report.tex) · [`report.md`](report.md) | Finished camera-ready article, reproducible typesetting source, and Markdown companion |
| [`docs/EVALUATION.md`](docs/EVALUATION.md) | T1–T7 evidence, metrics, limitations and remaining reviews |
| [`docs/REPRODUCE.md`](docs/REPRODUCE.md) | Exact Windows commands, expected files and safe run order |
| [`docs/REVIEWER_CHECKLIST.md`](docs/REVIEWER_CHECKLIST.md) | Original weighted CKL criteria, evidence gates and live defense |
| [`docs/INDEPENDENT_VALIDATION.md`](docs/INDEPENDENT_VALIDATION.md) | Required isolated label judgments, evidence provenance and fresh-test protocol |
| [`docs/ASSIGNMENT_SOURCE.md`](docs/ASSIGNMENT_SOURCE.md) | Original task description |
| [`AI_USAGE.md`](AI_USAGE.md) | AI-assistance disclosure |
| [`inputs/data.zip`](inputs/data.zip) | Original employer-supplied corpus (do not redistribute) |
| [`src/`](src/) | Original research pipeline and native hyperedge coarsening |
| [`research_lab/`](research_lab/) | Method comparisons, locked evaluation, V2 labels and tests |
| [`outputs_selected/`](outputs_selected/) | **Selected model** hierarchies and temporal event outputs |
| [`metrics.json`](metrics.json) | Selected-model metrics with source references |
| [`research_outputs/`](research_outputs/) | Development/confirmation runs, null tests, robustness and label reviews |
| [`outputs/`](outputs/) | **Historical baseline only**, not the selected model |
| [`scripts/`](scripts/) · [`upgrade_scripts/`](upgrade_scripts/) | Additional reproducible checks and figures |
| [`docs/RESEARCH_PROTOCOL.md`](docs/RESEARCH_PROTOCOL.md) | Detailed prior experimental protocol |

## Quick start (Windows PowerShell)

Run from the repository root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:OPENBLAS_NUM_THREADS="1"
$env:OMP_NUM_THREADS="1"
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m unittest research_lab.tests_lab research_lab.test_label_v2 research_lab.test_type_b_source_audit -v
.\.venv\Scripts\python.exe .\verify_selected_outputs.py --out outputs_selected
```

**Recorded results:** 65/65 development runs (13 configurations × 5 seeds), 5/5 locked-method confirmation runs, 5/5 pairwise projection runs, 99 constrained nulls, five 10%-deletion stress replicates, and four structural snapshot checks. The applicant's **20 October 2026 local log reports 10 core + 33 research + 9 frontier tests passing**. Newly added exhaustive V3 provenance-audit tests still require a separate clean local/CI run. The archived numeric runs were completed previously; the test suite does **not** reproduce all 75 expensive jobs.

**Type-B retrieval is now on `main`:** all four Type-B questions were evaluated in a *gold-blind-ranking / gold-only-scoring* two-stage pilot; [paper-source recall and audit](research_outputs/type_b_audit/type_b_source_scores.json) are recorded. For gold papers actually present in the eligible article set, **Recall@5 = 0.52083 for both flat and hierarchical routing**. This is *not* an answer-accuracy or evidence-entailment score. The [certified exact-search comparison](research_outputs/type_b_audit/certified_retrieval_audit.json) returned the same top five papers for all 18 inspected queries, but was slower end-to-end under measured conditions. No claimed quality/latency advantage.

**What remains:** Truly independent scientific evidence checks, which may use an authorized key-isolated LLM/NLI judge (human reviewers are optional), for gloss faithfulness and full-paper claim entailment. Our *AI-only* analysis is already stored (V2 6 wins/V1 2/16 ties on label scores); for 36 claims we tracked 19 publisher/preprint excerpts and 17 rubric-only items, with **no complete independent full-text entailment ratings**. Read [Evaluation and next actions](docs/EVALUATION.md).

## Historical retrieval quality–cost result (20 October local validation)

The two-stage [historical frontier evaluator](research_lab/frontier_historical.py) freezes
all 18 benchmark-question rankings **without gold**, then reads the original provided
references **only in scoring**, evaluating 14 Type-A tasks over route budgets 1–12
and an identical flat index. The applicant ran and locally verified the historical study on 20 October: 4-root Hit@5 was 2/14, matching Flat's 2/14, with 57.9% fewer online dot-products and lower measured per-query time on that Windows run. It records paired Hit@5 differences,
descriptive uncertainty, eligible-vs-unavailable targets and an SVG quality–cost
curve under Git-ignored `local_only/`. The four Type-B questions are explicitly
**not** claim-answer-scored. These previously viewed questions are **development
diagnostics**, not fresh scientific validation; no new accuracy gain is asserted.
For the safe run, use [Reproduce §15](docs/REPRODUCE.md).

## Full-membership V3 verification (source-only implementation)

The new [V3 provenance auditor](research_lab/v3_provenance_audit.py) checks all
180 V3 developmental labels against the original ZIP and frozen cluster
membership, including every cited node-name phrase and source paper's cutoff
year. A [minimal GitHub Actions clean-environment workflow](.github/workflows/scientific-integrity.yml)
also runs the source tests. These checks have **not yet been confirmed on the
applicant's Windows machine**. Even a complete pass does not establish
scientific full-paper entailment; authorized independent review remains pending.

## Assessment report update and confidential review gate

A four-page [LaTeX assessment candidate](scripts/report_candidate_20261020.tex)
was built and checked by [private PDF preflight CI](.github/workflows/report-preview.yml)
on 20 October. It records the verified Route-4 cost/quality pilot, 180-case
V3 evidence provenance, explicit construction guarantees and complexity, and
the predeclared four-week plan. The root delivered `report.pdf` is not
automatically overwritten; promote the verified candidate only after final
author review. The clean CI passed 10+33+18 tests.

No real independent judge ratings have been filled in or fabricated.
The offline [review handoff tool](research_lab/review_handoff.py)
requires an explicit user-permission confirmation flag before packaging
the 24/48-item confidential blind inputs and never uploads them. Instructions:
[Independent Validation](docs/INDEPENDENT_VALIDATION.md).

## Research integrity and confidentiality

- The 2024 held-out cut **worsened** from 0.6623 (development) to 0.7172 (source-group confirmation); lower is better.
- The constrained-shuffle null yielded `p=0.69`; no significant structure advantage is established.
- V1 title ratings: 8 accurate / 28 vague / 12 wrong; only 8 of 48 gloss-overclaim decisions were determinate.
- 24 V2 paired cases have **AI-only exploratory ratings** but remain **unrated by independent domain experts**; no expert-validated superiority is claimed. The local A/B key must not enter Git.
- Type-A and Type-B source retrieval are **exploratory on previously inspected benchmark questions**; matched Type-B source recall does not imply correct generated answers or a demonstrated speed advantage.

**Keep this repository private.** The supplied dataset, questions and ground truth belong to a confidential recruitment exercise. A GitHub URL is not access permission; the assessor needs an accepted invitation or a separately sent archive.
