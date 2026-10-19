# 3–5-page employer research report blueprint (populate ONLY with verified runs)

**Do not send this unfinished blueprint as a real report.** Start from the already generated original three-page `report.md` and update it after actual multi-run experiments.

## Page 1 — scientific problem, objective and prior art

1. Scientific bottleneck: dynamic high-order scientific knowledge cannot be reduced reliably with degree thresholding or pairwise cliques.
2. Formal constraints: hard 12,48,144,singleton budgets; laminar P1; P2, P3–P6 guarantee-vs-measured table.
3. Formal objective: semantic loss + normalized native hyperedge connectivity + temporal change cost. State complexity of selected implementation (empirical runtime and analytical update complexity, worst-case limitations).
4. Literature map: Zhou NeurIPS 2006 hypergraph Laplacian; Gottesbüren et al. TALG 2024 multilevel partitioning; Chakrabarti et al. KDD 2006 temporal cost; optional Traag Sci Rep 2019 projected graph baseline. Do not call the local heuristic an exact reimplementation of any author.

## Page 2 — implemented method and competing explanations

1. Native high-order event collapse: preserve original event ID, relation type, incidence multiplicity. Show cases (all-internal, partial, 3+ supernodes); show invariant and actual unit test.
2. Warm-start from preceding snapshot and stable supernode IDs, true birth/merge/split/growth/death log with attribution limitations.
3. A TABLE, not 12 mini-narratives: semantic baseline; incidence spectral-inspired; native structure-dominant; native joint; temporal joint; rigid control; pairwise clique. Put detailed hyperparameter sweep in appendix.
4. Fidelity of semantic label + one-sentence gloss; cite actual input evidence and human audit if conducted. If no blind audit, say NOT_EVALUATED.

## Page 3 — main empirical result and methodological safeguards

1. Actual 3 genuine snapshot source counts, year restriction avoiding future scientific papers.
2. Publication-group training/dev/confirmation split, shared encoder feature view, seed-lab notebooks.
3. Coherence metric from article titles is a different correlated view; report a raw score plus equal-size random label null with empirical p-resolution. Flag not independent semantic gold.
4. Native heldout connectivity and publication-bootstrap CI vs alternatives; matched 10%-edge deletion×5, degree/arity shuffling and effective swaps; cross-year ARI with uncertainty.
5. Paired plot showing semantic coherence vs temporal ARI vs heldout cut, and cost. Include negative findings and rigorously note one seed vs 5 seeds vs 52 source-paper limitation.

## Page 4 — extrinsic utility and case studies (if available)

1. Actual same-question, same-retriever budget comparison; no all-candidates pre-ranking disguised as cheap hierarchy.
2. If hierarchical retrieval performs worse than flat, say so, investigate routing failures with a few concrete source-grounded question cases; do NOT tune based on the original 18 known answers then call them a pristine test.
3. A figure showing stable vs changed concept clusters with real underlying members/provenance, no invented domain story.
4. At least one unsuccessful experiment with causal hypothesis and follow-up falsification.

## Page 5 / final paragraphs — limitations and what four more weeks would do

1. Explicit honest list: source-dependent title proxy, small article sample, transductive node surface exposure, inability to resolve time to February 2026 from year-only records, unscored type-B questions if applicable, human semantic label review missing if not actually completed.
2. Four-week plan: domain-aligned scientific embeddings using model weights actually installed (e.g. SPECTER2), truly independently annotated cluster glosses, more papers/domain shift, stronger learned coarse router with query-stage speed instrumentation, complete higher-order probabilistic baseline.
3. 3–5 pages of text + figures total for employer; all methods, per-seed runs, matched confidence intervals, negative results and code go in the complete reproducibility appendix.

The full experiment registry is more persuasive than fabricated superiority. The final paper should include the best selected method **and** a clear reason other strong methods were rejected or did not dominate.
