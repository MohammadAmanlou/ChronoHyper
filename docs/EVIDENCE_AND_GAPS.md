# Evidence ledger: locked 2026-10-19 project state

**Read this before interpreting any headline metric.** Locked source-data checksum and selection provenance are in `research_outputs/model_lock.json` and `outputs_selected/selected_export_manifest.json`.

## Verified / source-backed

- Real constructor archive (`inputs/data.zip`) unchanged: SHA256 `414867a07e5fdc4b38f9ad4e96bd5253d31e239012173ca439a1c5441553b4e1`.
- 13 development configurations x five fixed seeds x 2020, 2022, 2024 (65 model-seed jobs; 195 fits) **complete**; `experiment_registry.csv` includes every run; a separate five-seed unweighted clique baseline also complete.
- Locked source-paper confirmation for **only** `native_temporal_20`: five model-seed jobs, **complete**, no documented retuning after seeing confirmation results.
- Selected nested structural exports pass `verify_selected_outputs.py` for 2020/2022/2024 and exploratory 2025. T4 multiplicity counts sum to original event arity for every exported *training* edge.
- 2024 selected heldout cut from development 0.6622658; restricted source confirmation 0.7172032 (**degradation** +0.0549373, lower better). Title coherence and ARI measure the unchanged partition, not a new independent confirmation.
- Five 10%-edge deletions: selected model ARI mean 0.966555; 99 degree/arity-preserving randomized event controls give empirical `p=0.69`, **not significant**.
- 48 author-entered label-topic evaluations: 8 accurate, 28 vague, 12 wrong. Gloss overclaim determinate on 8, unclear on 40. No zero-overclaim population conclusion.
- 14 previously inspected type-A question evaluations: flat 1/14 vs hierarchy 2/14 at Hit@5, both weak; four type-B questions unscored. Candidate-score counts alone are not runtime cost.

## Outstanding acceptance-critical scientific gaps

1. **T5/T6:** Generate improved *scientific* labels with ground-truth provenance citations; compare v1/v2 on a fresh blind expert review set. Do not silently overwrite existing ratings or claim independent blind evaluation.
2. **T6:** Independently check semantic coherence and label claim entailment. Title-based coherence is a correlated second view, not decisive neutrality to circularity.
3. **T6:** Pairwise clique competitor currently *unweighted* for event arity; cannot claim native hypergraph superiority relative to all fair weighted graph reductions.
4. **T6:** Confidence intervals from just five seeds of one tiny 52-paper corpus are not generalization estimates; cite clustered provenance and source-group split sizes.
5. **Extrinsic:** 2025 retrieval is exploratory after previously inspecting the gold. Source-grounded type-B synthesis unanswered. No proven end-to-end indexing speed benefit.
6. **T7:** The current root `report.pdf` is a **source-backed working report** on the selected method; remaining human claims and external scientific review would require later revisions with changes recorded.
7. **Confidentiality and delivery:** Repository must remain private unless authorized; publishing the repo is not delivering it to Constructor.

## Change-control

- Never replace `research_outputs/model_lock.json` or silently rerun confirmation with a different model after looking at results.
- Every follow-up labeler should be named v2 and evaluated on pre-specified *new* review cases, with a new report version.
- Preserve all weak model runs and unsuccessful ablations; the experiment registry is part of scientific accountability.
- The original pipeline `src.run` under `outputs/` and original PDF stored in `docs/legacy_baseline/` are historical. The selected results live in `outputs_selected/` and root `metrics.json`.
