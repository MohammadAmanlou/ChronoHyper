# CKL V2 label experiment — registered development + untouched paired audit

This documents an additional **candidate labeler**, not a retrospective rebranding of
`native_temporal_20` or an independently validated semantic improvement. The locked
method, node allocations, historic V1 labels, negative evaluation results and all
original source files remain unchanged.

## Hypothesis and method

**Hypothesis:** using cluster-vs-rest discriminatory node-name phrases, gated by
source coverage and temporally eligible article provenance, can produce more
useful and better-calibrated topic candidates than unqualified frequent-term
labels. This is a *testable hypothesis*; it is not yet proven.

- Read the original `inputs/data.zip` and the frozen `outputs_selected/hierarchy_{year}.json`.
- Work on levels 0 and 1. Never move a node, change a frozen assignment or consult
  benchmark ground truth.
- For each cluster, count exact contiguous 1–3-gram mentions in scientific entity
  node names (`method`, `dataset`, `technique`, `component`, etc.), excluding
  metadata-only nodes (`author`, `article`, `claim`, `cited_work`).
- Contrast each n-gram's membership frequency against other available entity
  names from the same evidence cutoff. Score positive smoothed log-odds using
  support count, limited multiword boost and source-article diversity.
- Select up to two non-overlapping phrases; if support falls short, prefix the
  label `Mixed topics:`; if no positive evidence remains, **abstain** from a
  scientific topic assertion instead of inventing one.
- Sentence-level gloss deliberately asserts ONLY exact explicit phrase mentions
  by `support_count / eligible_member_count`, plus the caveat that it does not
  describe the whole cluster. The article IDs establish available provenance,
  **not** textual entailment of an entire paper.
- Run self-audits of *all* cited supporter node IDs and publication cutoffs.
  This is a lexical consistency test, **not** independent semantic accuracy.

### Reproduction

```powershell
.\.venv\Scripts\python.exe -m unittest research_lab.test_label_v2 -v
.\.venv\Scripts\python.exe -m research_lab.label_v2 --project . --out research_outputs/label_v2
```

Expected: 60 label candidates each for cutoffs 2020/2022/2024;
`research_outputs/label_v2/V2_FINDINGS.md`, per-year JSON source citations,
`v2_source_audit.json`, and a 24-case anonymized A/B worksheet.

## Scientific evaluation design (NOT YET COMPLETED)

The old 48-row review was **non-blind and AI-assisted**, and was consulted to
identify general defects of V1. It is *development evidence* and CANNOT serve
as an unbiased V2 performance test.

For a new matched evaluation, the program excludes all old reviewed
(year, stable_id) pairs and samples **24 previously unrated source clusters**
from years 2022/2024. Each sample shows the *same deterministic, label-independent
random member names* and linked available article titles. The original V1 and V2
labels appear as randomized `A` and `B`, without an explicit model identifier.

1. Give `BLIND_LABEL_COMPARISON_TO_FILL.csv` **only** to the reviewer; keep
   `BLIND_KEY_KEEP_SEPARATE.json` private from them.
2. Prefer an independent materials-science/ML reader. Record their actual
   reviewer ID. If the candidate or an AI rates them, disclose it as such.
3. For A and B separately record `accurate / vague / wrong` and
   `yes / no / unclear` over-claim judgments. Write notes and abstain where
   the evidence is insufficient. Do not fill blank values without review.
4. Score the pairs, without silently dropping incomplete ratings:

```powershell
.\.venv\Scripts\python.exe -m research_lab.label_v2 `
  --score-blind research_outputs/label_v2/BLIND_LABEL_COMPARISON_TO_FILL.csv `
  --key research_outputs/label_v2/BLIND_KEY_KEEP_SEPARATE.json `
  --out research_outputs/label_v2
```

The scorer reports V2 wins/losses/ties, mean paired change and exact sign-test
p-value, with a count of reviewable cases and descriptive over-claim rates among
only determinate answers. **No superiority can be inferred** until the genuine
annotations are supplied and assessed; even then, 24 source-group samples are
not broad out-of-distribution validation.

## Limitations / remaining T5/T6 obligations

1. Repeated names in extracted node text can make a phrase frequent without
   establishing a coherent *scientific* concept; this does not verify P3/P6.
2. Gloss statements are faithful to phrase occurrences only. Independent human
   or source-grounded NLI checks are still required for semantic entailment.
3. Labels at level 2 use the older basic routine. The prescribed T5 output is
   levels 0/1; no unsupported improvement to level 2 is claimed.
4. We never use the old 48 reviewer judgments as *gold truth* to manufacture
   label gains, nor change the five-seed model-selection lock retrospectively.
5. Heterogeneous labels may be scientifically honest but unattractive; their
   interpretability must be measured, not assumed.
