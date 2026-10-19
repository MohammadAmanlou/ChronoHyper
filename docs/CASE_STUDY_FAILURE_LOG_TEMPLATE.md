# Scientific decision log — keep failures

Copy this form for EVERY meaningful change to the algorithm. Do not rewrite the previous experiment's row after observing confirmation data.

| Date & prereg protocol SHA | Hypothesis | Original method(s) | Intervention | Observed positive result | Observed negative result | Alternative explanation | Verdict | Next test |
|---|---|---|---|---|---|---|---|---|
| Pilot / see `outputs_example/verified_dev` | H3: temporal smoothness | `native_joint_70` vs `native_temporal_08`, seed17 | Warm-start and 0.08 temporal inertia | 2022→24 ARI 0.3304 → 0.8782 | 2024 heldout edge cut 0.7267 → 0.7129 (smaller is actually better), article-title proxy 0.1159 → 0.1145 (worse) | Some apparent stability may be inertia not science | Promising tradeoff, not a definitive win | Multi-seed + perturbation + independent title audit |
| Pilot / see `outputs_example/verified_dev` | H2: native/spectral effect | `incidence_svd` vs `semantic_kmeans`, seed17 | Incidence-normalized SVD init | 2024 proxy title coherence 0.1013 → 0.1805 | 2022→24 ARI 0.3099 → 0.1437; 2024 cut 0.5997 → 0.7085 (worse) | Structural representation highlights article-local concepts, not stable long-lived taxonomy | Mixed performance; important negative stability finding | Temporal incidence alignment, not just extra λ sweep |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

These rows are **actual pilot output** (one seed and 3 years), not 55-run confirmation. In tables, arrow directions MUST be respected (heldout cut lower is better). The experiment registry remains the quantitative source of truth. Do not invent an ablation or call planned work completed.
