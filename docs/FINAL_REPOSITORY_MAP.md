# ChronoHyper — reviewer map and evidence boundary

**Applicant:** Mohammad Amanlou  
**Assessment:** Constructor Knowledge Labs, temporal knowledge hypergraph abstraction  
**Selected clustering configuration:** `native_temporal_20` (pre-locked before source-grouped confirmation)  
**Repository visibility:** private; obtaining the repository URL alone does not grant access.

## Read these files first

| File | What it provides |
|---|---|
| [`report.pdf`](../report.pdf) ([source](../report.md)) | Short assessment report: formal objective, algorithm, literature, T4 collapse, validity and limits |
| [`README.md`](../README.md) | Installation, exact commands and traceable outputs |
| [`outputs_selected/metrics.json`](../outputs_selected/metrics.json) | Measured results tied to the frozen method and five seeds |
| [`outputs_selected/hierarchy_2024.json`](../outputs_selected/hierarchy_2024.json) | Four-level nested hierarchy; analogous 2020 and 2022 snapshots |
| [`outputs_selected/temporal_events.json`](../outputs_selected/temporal_events.json) | Persistent ID and change-event data |
| [`research_outputs/model_lock.json`](../research_outputs/model_lock.json) | Frozen model, data SHA-256 and development protocol identifier |
| [`research_outputs/final_matrix/`](../research_outputs/final_matrix/) | 13 models × 5 seeds, complete development results |
| [`research_outputs/confirmation/`](../research_outputs/confirmation/) | 5 selected-method runs on held-out source-paper groups |
| [`research_outputs/projection_5seed/`](../research_outputs/projection_5seed/) | Five-seed pairwise clique baseline |
| [`research_outputs/stress_temporal20_extended/`](../research_outputs/stress_temporal20_extended/) | Five 10% edge deletions and 99 constrained-shuffle nulls |
| [`AI_USAGE.md`](../AI_USAGE.md) | AI assistance, verification and responsibility |
| [`research_lab/label_v2.py`](../research_lab/label_v2.py) | Second-generation source-audited label *candidate*, not a validated performance gain |

## Requirements and verification

- **P1/P2:** selected hierarchy is nested and within the 12/48/144 display budgets; singleton finest level.
- **P3/P4:** method directly operates on native hyperedges; semantics-structure trade-offs and the lossy pairwise baseline are documented. The exported coarsening file records original arity, source, type and repeated endpoints within aggregates.
- **P5:** true 2020/2022/2024 corpus snapshots, persistent identities, warm start, temporal events and cross-snapshot ARI; high ARI by itself cannot distinguish useful stability from inertia.
- **P6:** each top-level and second-level aggregate has automatically generated label/gloss and evidence; original V1 human labels were only 8 accurate, 28 vague, 12 wrong of 48. Only 8/48 over-claim judgments were determinate, with 40 inconclusive.
- **T6:** title-based coherence is a distinct but correlated signal, not fully independent domain-expert judgment. Source holdout had worse normalized connectivity in 2024 (development 0.6623 versus confirmation 0.7172). The 99-shuffle p-value was 0.69: not significant. Exploration on an already-seen 14-question retrieval subset found 2/14 hierarchical Hit@5 versus 1/14 flat; Type-B questions were not scored. No fresh unseen retrieval gain is claimed.
- **Label V2:** automatic phrase/provenance verification of 60 candidate labels per year in 2020, 2022, 2024; blind A/B ratings are still uncollected, so there is **no evidenced V2 accuracy improvement**.

## Reproduction

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m unittest research_lab.tests_lab research_lab.test_label_v2 -v
.\.venv\Scripts\python.exe .\verify_selected_outputs.py --out outputs_selected
powershell -ExecutionPolicy Bypass -File .\scripts\run_label_v2.ps1
```

Re-running `python -m src.run` alone **does not reproduce** the frozen `native_temporal_20` confirmation selection. Read the README for the exact lock-and-export sequence.

## Disclosure and release caveat

This private repository contains Constructor-provided assessment material; do not make it public without permission. The completed code/tests and the still-inconclusive scientific evaluations are **separate** claims. GitHub access for a reviewer requires an explicit invitation to their account. 