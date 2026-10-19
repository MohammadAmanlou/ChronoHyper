# Research experiment registry — all outcomes, not a winners-only report

**Original-data SHA256**: `414867a07e5fdc4b38f9ad4e96bd5253d31e239012173ca439a1c5441553b4e1`
**Frozen embeddings seed**: 17
**Held-out asserting papers split seed**: 42
**Expected executions**: 65; completed 65; failed/missing 0

## ALL method/year results

| Method | Year | Seeds complete | Heldout hyperedge cut ↓ | Independent-view title coherence ↑ | Temporal ARI ↑ | Seconds/snapshot ↓ |
|---|---:|---:|---:|---:|---:|---:|
| frozen_previous | 2020 | 5/5 | 0.6764 | 0.1873 | — | 0.1916 |
| incidence_svd | 2020 | 5/5 | 0.6595 | 0.2656 | — | 0.1296 |
| native_arity_normalized | 2020 | 5/5 | 0.6718 | 0.1983 | — | 0.1834 |
| native_balanced_50 | 2020 | 5/5 | 0.6680 | 0.2164 | — | 0.1808 |
| native_joint_70 | 2020 | 5/5 | 0.6704 | 0.2020 | — | 0.1842 |
| native_paper_balanced | 2020 | 5/5 | 0.6705 | 0.1972 | — | 0.1730 |
| native_semantic_85 | 2020 | 5/5 | 0.6775 | 0.1871 | — | 0.1840 |
| native_structure | 2020 | 5/5 | 0.6549 | 0.2050 | — | 0.1952 |
| native_structure_75 | 2020 | 5/5 | 0.6634 | 0.2123 | — | 0.1802 |
| native_temporal_03 | 2020 | 5/5 | 0.6704 | 0.2020 | — | 0.1792 |
| native_temporal_08 | 2020 | 5/5 | 0.6704 | 0.2020 | — | 0.1902 |
| native_temporal_20 | 2020 | 5/5 | 0.6704 | 0.2020 | — | 0.1780 |
| semantic_kmeans | 2020 | 5/5 | 0.7042 | 0.1847 | — | 0.0776 |
| frozen_previous | 2022 | 5/5 | 0.6764 | 0.1594 | 1.0000 | 0.0550 |
| incidence_svd | 2022 | 5/5 | 0.5731 | 0.2289 | 0.1377 | 0.1850 |
| native_arity_normalized | 2022 | 5/5 | 0.6798 | 0.1707 | 0.8533 | 0.2624 |
| native_balanced_50 | 2022 | 5/5 | 0.6604 | 0.1686 | 0.2130 | 0.2776 |
| native_joint_70 | 2022 | 5/5 | 0.6393 | 0.1693 | 0.2234 | 0.2678 |
| native_paper_balanced | 2022 | 5/5 | 0.6784 | 0.1694 | 0.8604 | 0.2598 |
| native_semantic_85 | 2022 | 5/5 | 0.6368 | 0.1592 | 0.2319 | 0.2790 |
| native_structure | 2022 | 5/5 | 0.6524 | 0.1743 | 0.2174 | 0.2984 |
| native_structure_75 | 2022 | 5/5 | 0.6537 | 0.1729 | 0.2059 | 0.2664 |
| native_temporal_03 | 2022 | 5/5 | 0.6796 | 0.1625 | 0.6900 | 0.2656 |
| native_temporal_08 | 2022 | 5/5 | 0.6800 | 0.1663 | 0.8434 | 0.2710 |
| native_temporal_20 | 2022 | 5/5 | 0.6769 | 0.1598 | 0.9396 | 0.2726 |
| semantic_kmeans | 2022 | 5/5 | 0.6039 | 0.1524 | 0.2013 | 0.0836 |
| frozen_previous | 2024 | 5/5 | 0.6571 | 0.1105 | 1.0000 | 0.0750 |
| incidence_svd | 2024 | 5/5 | 0.6662 | 0.1782 | 0.1165 | 0.3324 |
| native_arity_normalized | 2024 | 5/5 | 0.6649 | 0.1171 | 0.7214 | 0.5074 |
| native_balanced_50 | 2024 | 5/5 | 0.6547 | 0.1299 | 0.2716 | 0.5160 |
| native_joint_70 | 2024 | 5/5 | 0.6529 | 0.1168 | 0.2995 | 0.5080 |
| native_paper_balanced | 2024 | 5/5 | 0.6554 | 0.1163 | 0.7643 | 0.5286 |
| native_semantic_85 | 2024 | 5/5 | 0.6476 | 0.1160 | 0.3120 | 0.5214 |
| native_structure | 2024 | 5/5 | 0.6532 | 0.1282 | 0.2653 | 0.5346 |
| native_structure_75 | 2024 | 5/5 | 0.6443 | 0.1280 | 0.2609 | 0.5180 |
| native_temporal_03 | 2024 | 5/5 | 0.6818 | 0.1165 | 0.6860 | 0.5146 |
| native_temporal_08 | 2024 | 5/5 | 0.6690 | 0.1182 | 0.8309 | 0.5282 |
| native_temporal_20 | 2024 | 5/5 | 0.6623 | 0.1229 | 0.8930 | 0.5256 |
| semantic_kmeans | 2024 | 5/5 | 0.5705 | 0.1147 | 0.3718 | 0.1336 |

## Descriptive Pareto front on 2024

frozen_previous, incidence_svd, native_arity_normalized, native_balanced_50, native_joint_70, native_structure, native_structure_75, semantic_kmeans

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
