# ChronoHyper
**Temporal multi-resolution abstraction of a scientific knowledge hypergraph**  
Mohammad Amanlou · Constructor Knowledge Labs doctoral assessment · Python 3.11 · **private dataset**

This is the **single entry point** for the project. Start with the [four-page research report](report.pdf) or read its [editable source](report.md). The selected model is `native_temporal_20`, frozen before the source-grouped confirmation evaluation. The repository records positive, negative and incomplete findings; passing software tests does **not** prove scientific label faithfulness or admission.

## What is inside

| Path | Purpose |
|---|---|
| [`report.pdf`](report.pdf) · [`report.md`](report.md) | Current scientific report (not the earlier baseline) |
| [`docs/EVALUATION.md`](docs/EVALUATION.md) | T1–T7 evidence, metrics, limitations and remaining reviews |
| [`docs/REPRODUCE.md`](docs/REPRODUCE.md) | Exact Windows commands, expected files and safe run order |
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
.\.venv\Scripts\python.exe -m unittest research_lab.tests_lab research_lab.test_label_v2 -v
.\.venv\Scripts\python.exe .\verify_selected_outputs.py --out outputs_selected
```

**Recorded results:** 65/65 development runs (13 configurations × 5 seeds), 5/5 locked-method confirmation runs, 5/5 pairwise projection runs, 99 constrained nulls, five 10%-deletion stress replicates, four structural snapshot checks and 22 passing software tests. These were run on the original input and their outputs are committed; executing the tests above does **not** rerun all 75 method jobs.

**What remains:** independent blind judgments for 24 V1/V2 label pairs and an evidence-grounded audit of Type-B scientific claims. See [Evaluation and next actions](docs/EVALUATION.md). Type-B paper-source retrieval code is prepared separately but is not part of this main-branch snapshot until its local run and checks are committed.

## Research integrity and confidentiality

- The 2024 held-out cut **worsened** from 0.6623 (development) to 0.7172 (source-group confirmation); lower is better.
- The constrained-shuffle null yielded `p=0.69`; no significant structure advantage is established.
- V1 title ratings: 8 accurate / 28 vague / 12 wrong; only 8 of 48 gloss-overclaim decisions were determinate.
- 24 V2 paired cases are **unrated**; no expert-validated V2 advantage is claimed. The local A/B identity key must not enter Git.
- Original question retrieval was exploratory; no demonstrated speed advantage.

**Keep this repository private.** The supplied dataset, questions and ground truth belong to a confidential recruitment exercise. A GitHub URL is not access permission; the assessor needs an accepted invitation or a separately sent archive.
