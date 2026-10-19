# Reviewer entry point — ChronoHyper CKL assessment

**Candidate:** Mohammad Amanlou · **Frozen method:** `native_temporal_20` · **Status:** evidence-audited research submission; human semantic evaluation pending.

## Read in this order

1. [Report (PDF)](../report.pdf) and [source](../report.md): four-page formal method, tradeoffs, results and admitted limitations.
2. [README](../README.md): exact pinned-environment reproductions on Windows and the selected-model adapter.
3. [Selected hierarchies](../outputs_selected): 2020/2022/2024 four-level nested outputs, 2025 exploratory, collapsed training events, stable IDs, and temporal event log.
4. [Metrics](../metrics.json): numbers with source paths, training-development-confirmation stage separation and provenance.
5. [Research experiments](../research_outputs): 13 configurations × 5 seeds (65 dev jobs), 5-seed clique projection, five locked-model confirmation jobs, 99 constrained shuffles and five 10% deletion reruns.
6. [AI disclosure](../AI_USAGE.md): assistance, code ownership, reproducibility checks and limitations.

## Task-to-evidence index

| Task | Where to look | Key caveat |
|---|---|---|
| Formal statement and P1–P6 | Report §1, §2; `src/core.py` | Local heuristic, no global-optimality guarantee |
| T1: temporal input | `inputs/data.zip`, `outputs/snapshot_stats_*.json` | Source year vs first appearance |
| T2: hierarchy and native structure | `outputs_selected/hierarchy_*.json`, 13-method matrix | Structure and semantic objectives conflict |
| T3: identity and events | `outputs_selected/temporal_events.json` | Change-event type heuristic |
| T4: hyperedge collapse | `outputs_selected/collapsed_edges_*.json` | These are training events, not all held-out events |
| T5: automatic labels | `outputs_selected/label_evidence_*.json`, `research_lab/label_v2.py` | V1 titles weak; V2 scientific validity unreviewed |
| T6: coherence and controls | `research_outputs/final_matrix`, `stress_temporal20_extended` | Title proxy correlated; null p=0.69 |
| T6: stability and retrieval | `metrics.json`, exploratory 2025 question file | Retrieval 14 type-A only, type-B unscored |
| T6: label faithfulness | `outputs_selected/label_review_results.json` | Only 8/48 determinate overclaim judgments |
| T7: report and replication | `report.pdf`, README, pinned deps, tests, AI_USAGE | Do not equate test passage with scientific validation |

## Decisions a reviewer should not infer

- `native_temporal_20` was chosen before held-out source-grouped confirmation, but **confirmation cut worsened** from 0.6623 to 0.7172 (lower is better).
- 99 degree/arity-preserving randomizations gave p=0.69, not evidence of significant superiority.
- 48 nonblind V1 titles: 8 accurate / 28 vague / 12 wrong. Forty gloss overclaim judgments remain inconclusive.
- V2 contrastive labeller generated 60 candidates in each of 2020, 2022 and 2024 and source-checked node-name phrases; **no expert-rated V2 improvement** is claimed.
- On an already-inspected question set, hierarchical hit@5 was 2/14 vs flat 1/14; no fresh unseen extrinsic or latency advantage is established.

This archive contains private assessment material; preserve confidentiality and do not redistribute without Constructor authorization.
