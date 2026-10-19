# Constructor CKL — Temporal Hypergraph Research Assessment

**Candidate:** Mohammad Amanlou · **Snapshot:** 19 October 2026 · **Repository: PRIVATE**

This repository stores an evidence-audited, multi-method research response to Constructor Knowledge Labs' supplied temporal knowledge hypergraph assessment. It preserves **both successes and negative results**, including the original baseline implementation, 13 development method variants, a separate clique projection, source-grouped confirmation of one *locked* method, four-level hypergraph exports, stress tests and partially completed human annotation.

> **Working assessment snapshot, NOT a finalized claim of scientifically faithful labels.** The strongest evidence-backed report to date is [`report.pdf`](report.pdf) ([source](report.md)), regenerated for the selected method `native_temporal_20`. The earlier different-model PDF is isolated under [`docs/legacy_baseline/`](docs/legacy_baseline/) and is **not** the current selected method's report. An employer submission or PhD admission is **not** implied.

## What is actually verified

| Component | Verified status | Important limitation |
|---|---|---|
| T1: real graph/data audit | Original unmodified dataset SHA-256 checked; 2020/22/24 snapshots built | Source timestamp semantics need care |
| T2: method and four-level hierarchy | Native high-order local heuristic; 12/48/<=144/singletons verified | No proven global optimum; title labels are weak |
| T3: temporal treatment | Warm starts, shared-node matching, versioned event logs | Identity events are heuristic |
| T4: hyperedge collapse | Original arity, event ID, multiplicity and provenance retained | Output collapse files contain **training** events, not all held-out events |
| T5: label creation | Automated evidence files and 48 manually reviewed title ratings | 8 accurate/28 vague/12 wrong; 40 gloss-overclaim judgments unclear |
| T6: evaluation | 65/65 development runs; 5/5 confirmation runs; 5-seed projection baseline; 99-shuffle+5-perturbation stress | p=0.69 not significant; Type-B unscored; question retrieval exploratory |
| T7: report | New 4-page PDF for selected locked model, all underlying CSV/JSON retained | Independent semantic-label faithfulness evaluation outstanding |

**Key empirical contradiction:** mean held-out hyperedge cut in 2024 **worsened** from 0.66227 in development to 0.71720 in confirmation (lower is better); randomization p=0.69 does not establish a structural advantage. These unfavorable findings are deliberately retained.

## Repository layout

```text
inputs/data.zip                  Original Constructor-provided input (private)
src/                             Original end-to-end baseline pipeline
research_lab/                    Distinct algorithms, experiment registry, source-grouped evaluation
upgrade_scripts/                 Additive scientific controls/diagnostics
research_outputs/final_matrix/   13 models x 5 seeds; 2020/2022/2024
research_outputs/projection_5seed/  Unweighted clique projection x 5 seeds
research_outputs/confirmation/   Chosen model x 5 seeds; held-out source papers
research_outputs/model_lock.json Frozen method and development protocol
research_outputs/stress_temporal20_extended/   99 null swaps, 5 deletions
outputs/                         LEGACY baseline method output (DO NOT use as selected results)
outputs_selected/                Current selected four-level hierarchy + review logs
metrics.json                     **Current source-backed selected-model metrics**
report.pdf                       **Current selected-model report (working draft)**
docs/legacy_baseline/            Historical older report/manifest, clearly separated
AI_USAGE.md                      Full AI involvement and candidate checks
scripts/                         Deterministic report figures/metrics and QA helpers
.github/workflows/               Portable unit-test and selected hierarchy CI
```

## Reproduce (Windows / PowerShell)

Create a clean Python **3.11** environment (no GPU needed):

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:OPENBLAS_NUM_THREADS='1'
$env:OMP_NUM_THREADS='1'
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m unittest research_lab.tests_lab -v
.\.venv\Scripts\python.exe .\verify_selected_outputs.py --out outputs_selected
.\.venv\Scripts\python.exe .\final_preflight.py --project .
```

`final_preflight.py` deliberately reports remaining scientific gaps; a `BLOCK` means **not ready to claim full validation**, not that the other tests have failed.

To regenerate the current selected-method **numeric registry** from actual source files (no model rerun):

```powershell
.\.venv\Scripts\python.exe .\scripts\generate_selected_metrics.py
.\.venv\Scripts\python.exe .\scripts\make_report_figures.py
```

To reproduce the **locked selected hierarchy** from the existing confirmed assignment run (no further hyperparameter tuning):

```powershell
.\.venv\Scripts\python.exe .\export_locked_full_hierarchy.py `
  --lock research_outputs/model_lock.json `
  --confirmation research_outputs/confirmation `
  --seed 17 --out outputs_selected_reproduced --with-2025
.\.venv\Scripts\python.exe .\verify_selected_outputs.py --out outputs_selected_reproduced
```

The separate **old reference baseline** command is still available but it is **not** the selected method and writes `outputs/`:

```powershell
.\.venv\Scripts\python.exe -m src.run --data inputs/data.zip --out outputs_baseline_regenerated --seed 17 --null-runs 16
```

The original **13-method development matrix** (expensive, already included as measured files) can be re-run from scratch into a different folder via the commands in [`docs/RESEARCH_PROTOCOL.md`](docs/RESEARCH_PROTOCOL.md) and [`run_research_pipeline.ps1`](run_research_pipeline.ps1). Do not delete/replace original `research_outputs/` to chase a better score after confirmation.

For Linux/macOS use `python3` and `python` in place of the Windows venv paths.

## Reproducing the selected report PDF

Source is `report.md` and charts are generated from archived result CSVs via `scripts/make_report_figures.py`. The provided 4-page PDF was rendered from this Markdown using **Pandoc + XeLaTeX** (an authoring dependency, not a runtime modeling dependency):

```bash
pandoc report.md --from=markdown+tex_math_single_backslash --pdf-engine=xelatex \
  -V geometry:margin=1.35cm -V linestretch=1.05 -V mainfont='DejaVu Sans' -o report.pdf
```

## Research integrity / next steps

- **Human title audit:** 48 reviewed; 8 accurate, 28 vague, 12 wrong. Gloss overclaim 0/8 determinately scorable **with 40 unclear**. It is invalid to call this 0/48, or an independent blinded expert evaluation.
- **Selection:** `native_temporal_20` was frozen before restricted source-paper confirmation; all five seeds were retained. No subsequent retuning on confirmation or the inspected 18 questions is justified as an untouched test.
- **Extrinsic:** 14 previously inspected Type-A questions yield flat Hit@5 1/14 vs hierarchical 2/14; four Type-B questions are not scored. No reliable runtime speedup established.
- **All positive and negative evidence** is archived, including `research_outputs/.../experiment_registry.csv`, `all_runs.csv`, `method_summary.csv`, `paired_paper_bootstrap.csv`, stress JSON and exact article split/protocol.
- **To finish:** independent evidence-constrained semantic label audit; source-grounded labeler revision tested on new cases; reviewer-readable examples, source-grouped null/CI caveats, clean-room reproduction; verify recipient submission deadline and original thread.

See [`docs/EVIDENCE_AND_GAPS.md`](docs/EVIDENCE_AND_GAPS.md), [`docs/GITHUB_PUSH.md`](docs/GITHUB_PUSH.md) and [`AI_USAGE.md`](AI_USAGE.md).

## Confidentiality

The input dataset, question reference answers, and take-home task were supplied for a private assessment. **Keep this repository PRIVATE** until explicit publication rights are verified. Do not add unrelated personal email, API credentials, virtual environments, or unreviewed proprietary material. No open-source redistribution license is asserted for the employer-provided dataset.
