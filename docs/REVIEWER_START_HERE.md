# ChronoHyper — Reviewer starting point

**Assessment:** Multi-resolution semantic abstraction over an evolving knowledge hypergraph (Constructor Knowledge Labs)  
**Candidate:** Mohammad Amanlou  
**Date:** 19 October 2026 · **Frozen clustering:** `native_temporal_20`

## Read in order

1. [`../report.pdf`](../report.pdf) — **four-page assessment report**, formal model, verified/assumed distinctions, tradeoffs and limitations.
2. [`../README.md`](../README.md) — exact environment, rerun commands, snapshot outputs, and confidentiality.
3. [`../outputs_selected/`](../outputs_selected/) — machine-readable hierarchy per 2020/2022/2024 (additional 2025 exploratory), persistent IDs, collapsed training hyperedges and temporal events.
4. [`../metrics.json`](../metrics.json) — selected-run results with sources, stages and null caveats.
5. [`../research_outputs/`](../research_outputs/) — 13 development methods × 5 seeds, five-seed clique projection, 5 locked source-grouped confirmation runs, 99 constrained controls, all successes **and failures**.
6. [`../AI_USAGE.md`](../AI_USAGE.md) — AI assistance and explicitly verified checks.

## Matching the assessment's tasks

| Requirement | Artifact or evidence | Limit that matters |
|---|---|---|
| **Formal statement / P1–P6** | `report.pdf` §1–§2, `src/core.py`, `research_lab/experiment_suite.py` | Local heuristic, **not** global optimum |
| **T1** source and ≥3 snapshots | `outputs/snapshot_stats_*.json`, `inputs/data.zip` | Source year is not necessarily the entity's first appearance |
| **T2** multilevel, semantic/structural tradeoff | `outputs_selected/hierarchy_{2020,2022,2024}.json`, 13 methods | Stronger ARI does not mean coherent science |
| **T3** temporal stability/events | `outputs_selected/temporal_events.json`, selected export validator | Event type assignments are heuristic |
| **T4** native hyperedge collapse | `outputs_selected/collapsed_edges_*`, `src/core.py` | Only *training* hyperedges are represented in selected export |
| **T5** automatic level-0/1 labels and provenance | `outputs_selected/label_evidence_*.json`, `research_outputs/label_v2` | V1 titles mostly vague/wrong; V2 unreviewed |
| **T6** coherence and null controls | `research_outputs/final_matrix`, `stress_temporal20_extended` | Related title proxy; null p=0.69 |
| **T6** temporal perturbation/CIs | stress JSON and `metrics.json` | 5 seeds of same 52-paper corpus ≠ independent datasets |
| **T6** faithfulness and retrieval | `outputs_selected/label_review_results.json`, `selected_retrieval_EXPLORATORY_2025.json` | 40 uncertain overclaims; Type-B unscored; no proven latency benefit |
| **T7** report, source and disclosure | `report.pdf`, `README.md`, `AI_USAGE.md` | Honest limitations must be read with positives |

## A small set of numbers, and how NOT to read them

- 2024 heldout cut: development **0.6623**, source-group confirmation **0.7172** (**worse by 0.0549**), lower is better.
- Five edge-deletion perturbations: mean ARI **0.9666** under this particular stress. It is not proof of scientific accuracy.
- 99 degree/arity-preserving shuffle controls: empirical p **0.69**: not statistically significant.
- V1 labels reviewed: **8 accurate / 28 vague / 12 wrong**; only 8/48 overclaim judgments determinate. It is invalid to report 0/48.
- Exploratory, already-inspected question lists: hierarchical hit@5 **2/14** versus flat **1/14**; no independent retrieval advantage is established.
- The V2 labeler has source-audited lexical occurrences and a **blank** 24-case blinded worksheet; **no human-rated V2 improvement** has been measured.

## Minimal software integrity check (Windows Python 3.11)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m unittest research_lab.tests_lab research_lab.test_label_v2 -v
.\.venv\Scripts\python.exe .\verify_selected_outputs.py --out outputs_selected
```

The package is intentionally **not licensed for public redistribution**; the data/benchmarks were provided as a private candidate assessment. An attached ZIP is sufficient for confidential review; private Github access must be separately approved.
