# Constructor hypergraph abstraction: predeclared multi-method research protocol

## Scientific aim

Can a **native higher-order, semantic-and-temporally-aware coarsening** algorithm satisfy hard laminar display constraints while outperforming (on independent supporting signals) standard semantics-only methods, structure-dominant methods, lossy pairwise projection, and temporally frozen clustering? **Failure of a method is an observation, not a reason to discard its run.**

The provided Constructor assessment has six desired properties P1–P6; the lab focuses on a controlled **level-zero** experiment to select/refine a candidate. P1/P2 and all-level nesting/hyperedge-collapse integration for the selected method must be verified with the original hierarchy generation before hand-in. Its terminal outputs are not the full employer deliverable.

## Hypotheses and falsification criteria

| ID | Scientific expectation to test | A genuinely contradictory result would be | Metric / threat |
|---|---|---|---|
| H1 | A native high-order model preserves heldout scientific relationships better than a semantic-only baseline | Semantic-only consistently lowers normalized heldout hyperedge cut | Paper-heldout normalized connectivity; shared source-text exposure |
| H2 | Semantic-structure integration improves scientific coherence vs structure-only | Incidence or structure-only yields higher title-view coherence and no cut cost | Publication-title cosine proxy is not expert semantics |
| H3 | Temporal warm-start/penalty improves ARI without large current-cut penalty | Frozen control ARI high but cut poor; temporal penalty impairs evidence fit | Cross-year common-node ARI, heldout cut; inertia confound |
| H4 | Native hyperedge operation outperforms naive clique expansion at matched K | Clique performs as well or better under same source cut and runtime | Unweighted clique overweights high-arity events; baseline is intentionally lossy |
| H5 | Robustness improves under matched-protocol 10%-edge removal | Large ARI drop under repeated perturbations | Five perturbation draws, wide descriptive CI |
| H6 | Observed heldout scientific cut beats degree/arity preserving shuffled-null fitting | Original falls inside shuffled score distribution | ≥19 or ≥99 constrained nulls; effective swaps disclosed |
| H7 | Coarse-to-fine routing helps retrieval under fixed candidate-score budget | Flat search wins, or hierarchy makes score computations worse | Actual wall time and operation counts; original 18 questions exploratory |
| H8 | Automatically generated cluster glosses do not overclaim | Independent reviewer finds errors/vagueness on a 48-case prereg sample | Blind human review, evidence citations and Wilson CI |

## Method matrix

| Family | Implementation ID | Scientific purpose |
|---|---|---|
| Semantic | semantic_kmeans | Embedding-only KMeans baseline |
| Higher-order | native_structure | Hyperedge-dominant local refinement (small semantic term) |
| Higher-order | native_semantic_85 | Semantic-dominant native refinement |
| Higher-order | native_balanced_50 | Equal structural/semantic weighting |
| Higher-order | native_joint_70 | Reference-style high-order joint model, no explicit temporal inertia |
| Higher-order | native_structure_75 | Another well-separated structural tradeoff point |
| Evolutionary | native_temporal_03 | Weak temporal regularization |
| Evolutionary | native_temporal_08 | Moderate temporal regularization |
| Evolutionary | native_temporal_20 | Strong temporal penalty; possible over-smoothing |
| Spectral-inspired | incidence_svd | Incidence-normalized SVD initializer + native refinement |
| Temporal control | frozen_previous | Preserve survivor cluster assignments; a deliberately rigid temporal upper control |
| New high-order objective | native_arity_normalized | Per-event connectivity normalized by original arity-1 to match heldout metric |
| New high-order objective | native_paper_balanced | Inverse source-paper event count AND arity normalization; may overcorrect |
| Pairwise control | clique_pairwise | Full unweighted clique expansion; admits high-order information loss |

This is **13 main models × 5 seeds + one expensive pairwise diagnostic**, not a claim that every possible technique from the literature was implemented. Five predeclared seeds: 11, 17, 29, 41, 53. Years: 2020, 2022, 2024. One 2020-fitted semantic encoder (fixed embedding seed 17). A shared 52-paper source-group split is fixed at seed 42 for all baselines. All compared models have a hard **K≤12** top-level limit. No gold answers are accessed during model fitting, development selection or scientific stress runs.

## Evaluation tiers

1. **Exploratory pilot**: one seed, four algorithms × three time slices; implement/test identical logging and metrics.
2. **Main DEVELOPMENT study**: all 13 main methods × five seeds × three time slices. A separate unweighted clique control may be too slow: run explicitly and report resource cost.
3. **Stress**: before seeing scores choose meaningful algorithms and years. Test matched 10%-edge deletion ×5 and constrained degree/arity-preserving shuffle (≥19 for pilot; 99 only if justified).
4. **Label audit**: 48 prechosen scientific clusters with real provenance; independent human judgments and Wilson CI; never impute blanks.
5. **Selection lock**: use only development evidence, select exactly ONE method with a written rationale. Log every rejected alternative and why.
6. **Reserved source-group confirmation**: evaluate only locked method against article groups withheld from development; do not modify hyperparameters after this run.
7. **Full multi-resolution/label/retrieval hand-in**: rerun selected method inside main `src/` hierarchy, verify P1–P6 and T4, and update `report.md/pdf` and JSON output. This Lab does NOT automatically accomplish step 7.

## Statistics and error bars

- Structural score is normalized hyperedge connectivity on edges grouped by an **asserting-paper holdout**; lower is better, but source node features are transductive and provenance dependencies persist.
- For model comparisons, paper-level paired differences and percentile-bootstrap CIs are reported; a small ~10-paper subset means substantial finite-sample uncertainty. No post-hoc significance promises.
- The independent publication-title character-ngram evaluation is a separate information view, but correlated with the input's surface strings and derived from the same literature. A **blind source-paper / human semantic audit** is needed before claiming semantic faithfulness.
- For time-stability report ARI only on common node IDs across two snapshots; no assumption that all old scientific topics should remain unchanged. A stiff baseline can game ARI.
- Deletion ARI must use exactly the same previous-partition warm start, temporal weight, encoder and fitting partition for reference and perturbation.
- Swapped incidence null must preserve source node degrees, every original edge arity and relation/year constraints; report **successful swaps** to avoid degenerate randomization.
- Paper-source grouping reduces one kind of leakage. It does not remove pretrained-encoder leakage or content shared across papers. The 18 existing benchmark questions have already been inspected in earlier project phases and cannot be relabeled pristine independent tests after tuning.

## Failure documentation requirement

For every attempted run retain: method ID, source checksum, frozen split, seed, snapshot, success/failure state, elapsed time, actual metric vector, aggregation reason, why method failed or succeeded, and exact version of the Python code. Never delete runs with bad values. A failed study can still motivate a defensible change; that change starts a **new exploratory campaign** with a new protocol file, not rewriting previously confirmed outcomes.

## Literature grounded positioning — do not claim exact algorithm reimplementation

1. Zhou, Huang & Schölkopf, *Learning with Hypergraphs: Clustering, Classification, and Embedding*, NeurIPS 2006 — incidence/hypergraph spectral family, not identical to our approximation. https://papers.nips.cc/paper_files/paper/2006/hash/dff8e9c2ac33381546d96deea9922999-Abstract.html
2. Gottesbüren, Heuer, Maas, Sanders & Schlag, *Scalable High-Quality Hypergraph Partitioning*, ACM Transactions on Algorithms 20(1), 2024 — n-level/multi-level hypergraph partitioning with refinement; our native refiner is a simplified independent heuristic, not Mt-KaHyPar. https://doi.org/10.1145/3626527
3. Traag, Waltman & van Eck, *From Louvain to Leiden*, Scientific Reports 9, 5233 (2019) — rigorous community connectivity baselines/multilevel structure, but a graph-based method. https://doi.org/10.1038/s41598-019-41695-z
4. Chakrabarti, Kumar & Tomkins, *Evolutionary Clustering*, KDD 2006 — temporal tradeoff between snapshot quality and historical smoothness. https://doi.org/10.1145/1150402.1150467
5. Ruggeri, Contisciani, Battiston & De Bacco, *Community detection in large hypergraphs*, Science Advances 9(28), eadg9159 (2023) — probabilistic mixed-membership hypergraph community detection; interesting next baseline but NOT implemented by this lab. https://doi.org/10.1126/sciadv.adg9159
6. Singh et al., *SciRepEval: A Multi-Format Benchmark for Scientific Document Representations*, EMNLP 2023 — SPECTER2 scientific embeddings are an optional future semantic baseline; **not currently run**. https://aclanthology.org/2023.emnlp-main.338/

Only ~3–4 of these need fit in the employer's 3–5 page report. The longer appendix and full experiment registry can cite more.
