# Reproduce — one runbook
[← Main README](../README.md) · [Scientific evidence](EVALUATION.md)

**Environment:** Windows PowerShell, Python 3.11, CPU only. Work exclusively from the repository root. Do not rename source files or rerun trained methods into canonical output folders.

## 1 · Install and audit current submission

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:OPENBLAS_NUM_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
git status --short
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m unittest research_lab.tests_lab research_lab.test_label_v2 research_lab.test_type_b_source_audit -v
.\.venv\Scripts\python.exe .\verify_selected_outputs.py --out outputs_selected
.\.venv\Scripts\python.exe .\final_preflight.py --project .
```

Expected **10 core + 15 research tests** and four structurally valid snapshots. The preflight deliberately reports scientific qualifications; do not misinterpret those as corrupt files. Check `git status --short` and preserve any local changes.

## 2 · Reproduce a new selected hierarchy WITHOUT model selection

```powershell
.\.venv\Scripts\python.exe .\export_locked_full_hierarchy.py `
  --lock research_outputs/model_lock.json `
  --confirmation research_outputs/confirmation `
  --seed 17 --out outputs_selected_reproduced --with-2025
.\.venv\Scripts\python.exe .\verify_selected_outputs.py --out outputs_selected_reproduced
```

This works from the **preselected** configuration and stored confirmation run. It does not prove an independent scientific evaluation.

## 3 · Inspect (do not overwrite) the full experiment registry

| Folder | Runs or outputs |
|---|---|
| `research_outputs/final_matrix/` | 13 × 5 = 65 development method runs, 2020/2022/2024 |
| `research_outputs/confirmation/` | Five prelocked runs on separated source-paper groups |
| `research_outputs/projection_5seed/` | Five clique baseline runs |
| `research_outputs/stress_temporal20_extended/` | 99 null shuffles and five deletions |
| `research_outputs/label_v2/` | V2 candidates for 2020/2022/2024 and an **unrated** 24-case A/B sheet |

The Type-B source-retrieval experiment has also **already been executed and committed** in `research_outputs/type_b_audit/`: four frozen paper rankings, gold-source scores, a blank 36-claim review sheet and a 2025 exact-search audit. The rankings were constructed without reading the reference answers and scored only after freezing. Paper-source coverage cannot establish generated answer correctness. The original complete expensive sweep has **already been executed and committed**. Do not spend time rerunning it merely to claim that a new local folder ran every seed. For optional full regeneration, read [the experiment protocol](RESEARCH_PROTOCOL.md) and choose *new* output paths.

## 4 · V2 label reproducibility and human review

```powershell
.\.venv\Scripts\python.exe -m research_lab.label_v2 --project . --out research_outputs/label_v2
```

Only `BLIND_LABEL_COMPARISON_TO_FILL.csv` goes to an independent reviewer. Keep `BLIND_KEY_KEEP_SEPARATE.json` on the local machine, excluded from Git; do not regenerate the sheet after ratings start. To score genuine completed ratings, run:

```powershell
.\.venv\Scripts\python.exe -m research_lab.label_v2 `
  --score-blind research_outputs/label_v2/BLIND_LABEL_COMPARISON_TO_FILL.csv `
  --key research_outputs/label_v2/BLIND_KEY_KEEP_SEPARATE.json `
  --out research_outputs/label_v2
```

If the key was lost and review A/B mapping cannot be recovered, do not guess the mapping or infer paired wins. Report the review as incomplete.

## 5 · Inspect the completed Type-B audit (no rerun needed)

The [Type-B source metrics](../research_outputs/type_b_audit/type_b_source_scores.json) compare flat vs four-route hierarchy on four previously inspected questions; source Recall@5 relative to eligible gold papers = 0.52083 for both, with no quality gain. The [exact-search control](../research_outputs/type_b_audit/certified_retrieval_audit.json) reports identical top-5 results for 18/18 queries and *slower* hierarchical traversal. Keep the 36 rows of [`CLAIM_LEVEL_REVIEW_BLANK.csv`](../research_outputs/type_b_audit/CLAIM_LEVEL_REVIEW_BLANK.csv) unrated until a genuine source-document reviewer checks them. **Do not run `scripts/run_t6_and_push_main.ps1` again to generate fake new evidence**; its initial pipeline has already finished and been pushed.

## 6 · Update figures/report if evidence changes

```powershell
.\.venv\Scripts\python.exe .\scripts\generate_selected_metrics.py
.\.venv\Scripts\python.exe .\scripts\make_report_figures.py
```

The four-page PDF uses Pandoc+XeLaTeX to render `report.md`; regenerate PDF after **actual** scientific report edits. Retain original metrics and evidence stage labels. The legacy `outputs/` directory is the earlier model, **not** the locked selected output.
