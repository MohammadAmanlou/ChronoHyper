# Verified real-data multi-run findings — Constructor CKL

**19 October 2026. Evidence classification:** all numbers below were actually produced by the supplied real-data scripts and archived in `outputs_example/`. These are **source-group DEVELOPMENT / exploratory** evaluations, not a reserved confirmatory result or proof of PhD acceptance.

## Actually completed today

- **11 diverse models × 5 fixed seeds × 3 real snapshots = 165 recorded snapshot fits**. All 55 method/seed jobs completed, no failed jobs omitted. See `outputs_example/all_11_methods_5seeds_3years`.
- **2 newly motivated loss-design candidates × 5 fixed seeds × 3 snapshots = 30 additional snapshot fits**. All 10 additional jobs completed. See `outputs_example/new_weighted_hypotheses_5seeds`.
- **1 full pairwise clique baseline**, plus the rest of the 12-model diagnostic grid, run with seed 17 on three real snapshots (36 snapshot fits); archive `outputs_example/all_12_methods_3years`. This was a deliberately lossy unweighted baseline, not a theorem-level controlled loss-equivalent test.
- **3 targeted year-2024 stress experiments**, each 10%-edge deletion × 5 and degree/arity-preserving incidence shuffles × 19, for `semantic_kmeans`, `native_temporal_08`, `incidence_svd`. The null models performed about 10,600 successful constrained swaps each; degree and arity checks passed. See `outputs_example/all_11_methods_5seeds_3years/stress`.
- **5/5 new method-suite unit tests** passed in the current environment, plus actual development and selection-lock/confirmatory-path *software smoke tests*. A rehearsal of confirmation code is not a genuine frozen scientific confirmation after the final experimental selection.

## Five-seed average, 2024

| Model | Heldout scientific edge cut ↓ | Separate article-title view ↑ | Temporal ARI from 2022 ↑ |
|---|---:|---:|---:|
| `semantic_kmeans` | 0.56562 | 0.11276 | 0.32471 |
| `native_structure` | 0.66715 | 0.12624 | 0.25327 |
| `native_joint_70` | 0.66219 | 0.11787 | 0.28100 |
| `native_temporal_03` | 0.67784 | 0.11874 | 0.71514 |
| `native_temporal_08` | 0.66561 | 0.12069 | 0.79791 |
| `native_temporal_20` | 0.66316 | 0.12046 | 0.91505 |
| `incidence_svd` | 0.66622 | 0.17824 | 0.11655 |
| `frozen_previous` | 0.65528 | 0.11016 | 1.00000 |
| **NEW: `native_arity_normalized`** | **0.66349** | **0.11900** | **0.75349** |
| **NEW: `native_paper_balanced`** | **0.66382** | **0.11859** | **0.74273** |

Remaining tested variants (`native_semantic_85`, `native_balanced_50`, `native_structure_75`) are retained with all numeric outcomes in `method_summary.csv`, not hidden from analysis.

## What did NOT work, and what this means

1. **Native joint is NOT yet uniformly better.** Semantic-only has a lower heldout cut in the 2024 development set (0.56562 vs ~0.66 for native variants) even though graph structure is not part of semantic KMeans fitting. This weakens H1. Potential hypotheses include train-vs-test loss mismatch, source-paper hubs, transductive features, or high-arity event weighting. Causality is NOT established.
2. **Strong temporal inertia buys ARI, possibly by freezing legitimate change.** ARI for `native_temporal_20` is 0.91505, while rigid `frozen_previous` trivially achieves 1.0. A high ARI alone is not evidence of appropriate adaptation. Check heldout edge cut and article-title coherence jointly.
3. **Incidence SVD helps one coherence proxy but harms temporal stability.** It obtains 0.17824 article-title view coherence, higher than most other models, but temporal ARI falls to 0.11655. The title coherence source is correlated with the construction corpus and is not an expert judgment of scientific validity.
4. **Two explicitly motivated objective fixes did not convincingly solve H1.** Arity-normalized training improves development cut from 0.66561 to 0.66349 compared with the temporal joint reference, but its ARI drops from 0.79791 to 0.75349. Per-paper normalization gives cut 0.66382 and ARI 0.74273. These tiny descriptive shifts do not support a victory claim, absent paired inferential testing and confirmation.
5. **The corrected stress test is scientifically uncomfortable, and must be retained.** For year 2024 at seed 17, deletion ARI means were `semantic_kmeans=1.0`, `native_temporal_08≈0.95864`, `incidence_svd≈0.18999`. Semantic-only ARI=1 simply reflects its nondependence on edges, NOT robustness of a hypergraph model. Constrained-shuffle randomization p-values (lower cut better) were `1.00`, `0.85`, `0.95`, respectively (19 shuffles each). These are **not evidence of statistical superiority over constrained randomized structure**. No p-value is interpreted as admission odds.
6. **Original task retrieval is negative.** The separate original 18-question baseline recorded type-A hierarchical Hit@5 0 vs flat 0.1429 on 14 evaluable questions; four type-B questions were not scored. We already inspected the 18 reference answers in earlier development; don't claim a newly untouched benchmark if modifying retrieval based on that inspection.
7. **Label faithfulness by independent humans is still incomplete.** An automatically checked provenance/membership gloss is not semantic entailment. The 48-case human review file remains blank until actually assessed; report NOT_EVALUATED rather than invented 0% overclaims.

## Scientific judgment after real trials

There is currently **no scientifically defensible universally best method**. Some models trade stability for structure, and a simple baseline wins an important holdout cut. The 2024 Pareto chart (development only) should be used to justify tradeoffs, not to choose a model post-hoc from confirmation evidence. The proposed next research improvement is an arity-aware and source-balanced normalized objective tested on source-grouped development, but the first verified run suggests only minor/no convincing gains. A more fundamentally different higher-order method and independent scientific semantic evidence may be required.

## Output archive location inside this Lab ZIP

- `outputs_example/all_11_methods_5seeds_3years/experiment_registry.csv`
- `outputs_example/all_11_methods_5seeds_3years/method_summary.csv`
- `outputs_example/all_11_methods_5seeds_3years/paired_paper_bootstrap.csv`
- `outputs_example/all_11_methods_5seeds_3years/RESEARCH_COMPARISON_REPORT.md`
- `outputs_example/new_weighted_hypotheses_5seeds/` complete source-backed per-seed results
- `outputs_example/all_12_methods_3years/` full pairwise and ten additional baseline diagnostic methods under the same seed
- `outputs_example/FULL_55_RUNS_CONSOLE_LOG.txt` and `outputs_example/NEW_WEIGHTED_HYPOTHESES_LOG.txt`

None of these are a final employer submission until incorporated into a checked, 3–5-page `report.pdf` with updated code, README, temporal event/hierarchy JSON, faithfulness disclosures and a real delivery link.
