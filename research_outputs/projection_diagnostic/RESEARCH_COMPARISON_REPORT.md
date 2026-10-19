# Research experiment registry — all outcomes, not a winners-only report

**Original-data SHA256**: `414867a07e5fdc4b38f9ad4e96bd5253d31e239012173ca439a1c5441553b4e1`
**Frozen embeddings seed**: 17
**Held-out asserting papers split seed**: 42
**Expected executions**: 1; completed 1; failed/missing 0

## ALL method/year results

| Method | Year | Seeds complete | Heldout hyperedge cut ↓ | Independent-view title coherence ↑ | Temporal ARI ↑ | Seconds/snapshot ↓ |
|---|---:|---:|---:|---:|---:|---:|
| clique_pairwise | 2020 | 1/1 | 0.7469 | 0.1830 | — | 0.3150 |
| clique_pairwise | 2022 | 1/1 | 0.6873 | 0.1611 | 0.3420 | 0.4620 |
| clique_pairwise | 2024 | 1/1 | 0.6949 | 0.1219 | 0.2936 | 1.0770 |

## Descriptive Pareto front on 2024

clique_pairwise

## All failed / missing jobs

- None.

## Interpretation and limits

- Do not select a model based only on the 18 previously opened reference questions. Those are exploratory data after inspection.
- The article-title coherence is a second feature view, not blinded expert semantic faithfulness; the latter remains separately unverified until actual annotated review.
- The same paper set underlies every seed; seed standard deviations are NOT cross-corpus generalization confidence intervals.
- Per-paper bootstrap CI is descriptive for the holdout paper subset; clustered edge/node dependence persists.
- Full native hyperedge cut, hierarchy validity P1/P2, collapsed edge conservation and temporal identity must be verified again for any selected method before final claimed T2-T4 performance.
- Clique projection is unweighted: a hyperedge of arity n contributes n(n-1)/2 pair edges and overweights large events. This is a lossy diagnostic, not a fair loss-normalized substitute.
- A high ARI can result from a frozen partition even with bad scientific responsiveness: inspect cut/coherence trade-off jointly.
- No output here proves a PhD offer, supervisor acceptance or funding.
