# Scientific evidence, open limitations, and next actions
[← Main README](../README.md) · [Reproduce](REPRODUCE.md)

**Interpretation is deliberately conservative.** All quantitative claims below refer to the Constructor-supplied corpus, not a claim of novelty on unseen corpora.

## Latest post-lock same-corpus AI evaluations (20 October 2026)

The applicant has now submitted independently packaged *key-separated*, anonymized worksheets to AI reviewers. File-level integrity checks passed and scorer outputs were obtained locally (full private forms are intentionally git-ignored). A **24-pair** V2–V3 title/gloss comparison has **21 evaluable pairs** with V3 **10 wins/4 losses/7 ties**, mean rating delta **+0.2857/2**, unadjusted paired sign **p=0.1796** (not significant). Conditional gloss overclaim flags were **0/21 evaluable V2** and **0/14 evaluable V3**, with **3 and 10 unclear**, respectively. These are not full-text semantic overclaim rates.

A second score of the **same 24 matched real-versus-mixed clusters** from a 48-row blinded worksheet produced AI means **3.5417 vs 2.7500**, paired delta **+0.7917/5**, 15 wins/5 losses/4 ties, exploratory unadjusted **p=0.0414**, bootstrap CI **[0.2917, 1.25]**. This is not an independent corpus, does not establish paper text entailment and does **not** cancel the nonsignificant structural incidence-shuffle null (`p=0.69`). Neither the reviewer identifier nor lack of access to private historical keys can be externally proven by this scorer.

The complete source hashes, denominator-aware uncertainty caveats and precise T1–T7 rubric mapping are in [ASSESSMENT_STATUS.md](ASSESSMENT_STATUS.md). All original source-group confirmation and old AI-only results remain immutable.



## Verified on applicant's Windows run: historical retrieval frontier (20 October 2026)

The applicant's run of commit `8b0dcfb` passed **10 core, 33 earlier research, and 9 retrieval regression tests** (52 tests total). Four selected hierarchies also passed structural verification. The source ranking artifact was created before reference gold was opened; this is still a **previously inspected, exploratory** 14-question Type-A benchmark.

| Route budget | Historical Type-A Hit@5 | Macro Recall@5 (all required references) | Mean online candidate+centroid dot products | Average query-median online time* |
|---|---:|---:|---:|---:|
| Flat | 2/14 = 0.1429 | 0.0422 | 2,647 | 7.768 ms |
| 1 root | 1/14 = 0.0714 | 0.0065 | 250.7 | 1.807 ms |
| 2 roots | 1/14 = 0.0714 | 0.0065 | 534.3 | 3.306 ms |
| 4 roots | 2/14 = 0.1429 | 0.0487 | 1,114.4 | 6.133 ms |
| 8 roots | 2/14 = 0.1429 | 0.0422 | 2,040.8 | see local historical audit |
| All 12 roots | 2/14 = 0.1429 | 0.0422 | 2,659 | 13.546 ms |

*Online time includes routing, selected candidate scoring and top-five selection, but excludes shared query encoding and offline indexing. Measurements are environment-specific, with small task count and fixed query/arm order.

**Measured descriptive trade-off:** four-root routing does 57.9% fewer candidate+centroid dot products, with the same Hit@5 on these 14 queries, and 21.1% lower measured per-query online time in this Windows run. The four-root macro recall value is slightly higher than flat; it does **not** mean a significant accuracy gain. The paired Hit@5 differences for 4/8/12 roots were exactly zero on these cases, yielding a degenerate bootstrap CI [0,0]; that does **not** establish equivalence on future data. One- and two-root runs each lost one previously successful question; their exact paired two-sided sign test was p=1.0 (one discordance). No budget comparison establishes population-level superiority. Four Type-B synthesis questions remain ungraded for answer correctness.

The source evidence for these *historical* numbers is the user's 20 October Windows validation log and the locally written, untracked `local_only/retrieval_frontier/historical_v2/historical_audit.json`. The raw ranking, original question texts and private gold are deliberately **not copied into this repository**. This result does not supersede the previous five-seed 2024 structural null p=0.69 or the negative source-group heldout gap.

## Complete 180-label provenance audit (locally and clean-CI verified)

`research_lab/v3_provenance_audit.py` verifies, for **every** developmental V3 label from 2020/22/24, exact membership in the frozen hierarchy, nonmetadata denominators, literal phrase supporters in *all* eligible members, publication-year-eligible provenance, and byte-equivalent deterministic V3 output. Unlike small 14-name samples it does not skip members. The checker still cannot establish scientific semantic entailment, so its output explicitly sets independent accuracy and overclaim rate to `null`. On the applicant's 20 October Windows run, all **180/180** cases passed: **5,255** source-name phrase occurrences and **2,103** year-eligible paper references were checked, with **zero structural/lexical errors**. The clean Linux Python 3.11 workflow also passed. These are *provenance* checks, not independent scientific ratings; **115/180 (63.9%)** abstain, and the scientific overclaim rate remains unmeasured.

## Stage 3: sampled-name AI coherence vs year/size-matched mixed controls

The [48 recorded AI-only coherence ratings](../research_outputs/coherence_ai/ratings_48_AI.csv) have source-preserving ID-only comments. An additional reproducible script, `research_lab/coherence_ai.py`, regenerates from the 24 frozen label-review cases **24 actual 14-name cluster samples and 24 same-year, same-size mixes drawn from three other clusters**. The private condition key is generated **only under ignored `local_only/`**, never checked in. [Aggregate score](../research_outputs/coherence_ai/summary_AI_only.json): mean real **3.667/5**, mean mixed-control **2.333/5**, paired difference **+1.333**; across 24 matched pairs **19 real-higher, 2 control-higher, 3 ties** (descriptive sign p=0.000221, paired bootstrap exploratory 95% CI +0.792 to +1.875). Ratings were fixed in the local 48-row sheet before the entire key was joined for the aggregate analysis, but some key exposure had already occurred in the conversation.

**Important non-independence:** The GPT-6 assistant generated AI rating opinions on names alone, but its conversation context had exposed a subset of the true/control key before ratings. It was NOT a strictly key-blind independent evaluator, and the rating samples contain only 14 node *names*, not full article evidence; some names are generic/author names and null samples may share scientific topics. **Do not present this as fully independent P3 semantic validation.** The independent structural degree/arity-null permutation remained **p=0.69**, and this positive but weakly independent sampled-name contrast cannot erase that negative result.

Reproduce after pulling:
```powershell
.\.venv\Scripts\python.exe -m research_lab.coherence_ai --project . --generate
.\.venv\Scripts\python.exe -m research_lab.coherence_ai --project . --score
```
Only the local generated key and score are created under `local_only/`. This study evaluates name-sample topicality, **not** training-holdout full-paper entailment or model output title faithfulness. No new cluster labels were deployed.

## Native higher-order information versus pairwise projection (T2/P4)

This repository now includes a **direct measurement on the original Constructor hypergraph**, computed with [`research_lab/projection_loss.py`](../research_lab/projection_loss.py) and persisted in [`research_outputs/projection_loss/projection_loss.json`](../research_outputs/projection_loss/projection_loss.json). The tool reads **only** graph nodes/hyperedges from `inputs/data.zip` (not questions or gold) and verifies every member reference. The audited numbers are:

| Corpus cutoff | Native hyperedges | Clique pair occurrences | Pair occurrences per event |
|---|---:|---:|---:|
| 2020 | 374 | 13,327 | 35.63 |
| 2022 | 526 | 20,760 | 39.47 |
| 2024 | 983 | 47,983 | 48.81 |
| All supplied events | **1,429** | **72,701** | **50.88** |

Among all source events **1,150/1,429 (80.48%)** have arity at least three, with maximum arity **65**. A plain undirected untyped, unprovenanced clique projection contains **70,022 unique node pairs**; collapsing repeated pairs discards **2,679 additional pair occurrences**, while also discarding the identities and group boundaries of the original higher-order events and their relation/paper provenance. The native hypergraph representation retains exactly that event multiplicity, provenance and original arity. These counts quantify a **representation trade-off**, not an information-theoretic entropy loss, and **do not show by themselves that our method is more accurate** than a pairwise baseline. A pairwise encoding supplemented with every original event ID could of course recover the higher-order source; this comparison is specifically to a plain pairwise clique graph. The **five-seed actual clique-projection method baseline** remains separately reported in the frozen model results.

Generate the vector graphic `projection_loss.svg` and recheck the JSON using:

```powershell
.\.venv\Scripts\python.exe -m research_lab.projection_loss --project . --out .\local_only\projection_loss
```

## Experimental generic V3 title/gloss rule (not deployed)

`research_lab/label_v3.py` now applies a **single transparent deterministic rule to all 180 frozen level-0/level-1 cases in 2020/22/24**, not just 24 hand-edited titles: filter broad generic tokens, require at least three supported eligible member names and two dated source articles, name a domain-specific phrase when its literal name coverage is at least 60%, restrict title to `Partial theme:` at 30–60%, and **abstain** below 30%. Its gloss gives exact full-cluster source-name counts with a disclaimer rather than inferring full-paper scientific consensus. All thresholds are **development choices made after seeing earlier examples**; current frozen V1/V2 artifacts, metrics and A/B keys remain unchanged. It has **NO measured held-out semantic superiority yet**, and model confidence here is conditional on lexical evidence rather than external NLI. Do not use the fresh 48 coherence pairs to tune V3 and then claim an unbiased test on those same cases.

Reproduce in ignored scratch:
```powershell
.\.venv\Scripts\python.exe -m research_lab.label_v3 --project . --out .\local_only\label_v3_dev
```

## Fixed, gold-isolated 2025 Type-A development diagnostic

The [separately scored result](../research_outputs/retrieval_v2/dev_diagnostic_2025.json) follows a pre-written method ranking which did not open gold. With 14 previously inspected Type-A questions, both flat and hierarchical scored **2/14 Hit@5**; macro Recall@5 was **0.0422** vs **0.0487** respectively. Average type/name-deduplicated candidate scores: **2647** flat vs **1102.43** routed, plus 12 root centroids. Measured mean per-query median score times in one GitHub runner: **2.52 ms** flat vs **1.78 ms** routed, *excluding offline index preparation and shared query vector creation*. These environment-sensitive measurements demonstrate genuine candidate pruning in this program, not cross-environment latency guarantees, not superior hit-rate, and not new-question confirmation. Do not replace original historical 1/14 vs 2/14 numbers.

## New fair retrieval engine (T6; development only)

`research_lab/retrieval_v2.py` implements a new **shared entity-name + source-paper-title char/word TF-IDF index** for flat and routed search, with identical scoring, type+surface deduplication, centroid-first routing and actual dot-product accounting. The routed arm scores only selected node subsets, unlike the original historic evaluation which computed all scores first. It separates centroid preprocessing from query wall time. **No reference/gold answers are opened by its ranking command.** The original 18 test questions were previously seen, so a run on them is a **development diagnostic** only; no improvement or speedup is claimed before executing a genuine fresh test. Baseline methods and locked original results are untouched.

```powershell
.\.venv\Scripts\python.exe -m research_lab.retrieval_v2 --project . --rank
```

For any brand-new independent test: preserve new `question_id,question,type` queries and separately verified `question_id,expected_methods` references, score with a frozen ranker without looking at gold while adjusting heuristics. New-query originality is a procedural fact, not software-certified.

## Fresh AI coherence study — user-supplied aggregate (2026-10-20)

The [exact uploaded, anonymized summary](../research_outputs/fresh_semantic/summary_AI_only.json) is now preserved with a cryptographic hash of the original rated sheet and anonymized paired deltas, **not** member-name lists, source titles or the private real/control key. The [legible editable vector figure](../research_outputs/fresh_semantic/paired_coherence_AI_only.svg) presents the results by year. This is a user-supplied **AI-only exploratory assessment**: 24/24 evaluable pairs, mean real **3.583/5**, mean mixed control **2.875/5**, paired delta **+0.708/5**, 13 real-higher / 4 control-higher / 7 ties; an unadjusted descriptive paired sign test gives `p=0.0490` with exploratory bootstrap CI **[+0.25,+1.167]**. 2020/22/24 mean pair deltas: **+1.125, +0.625, +0.375**. The rating artifact self-reports model `GPT-6`, but its real independence, data-sharing authorization and sample-by-sample reviewer evidence **cannot be verified from this aggregate alone**; the original rated CSV remains local. Even if the AI judge was truly key-isolated, source article titles correlate with member names and are not full-paper scientific entailment. This study is **not** independent full-text P6 validation, does not show downstream utility and does **not** replace the original non-significant degree/arity-preserving structural null `p=0.69`.

## Newly prepared general V2/V3 blind review (no AI judgments yet)

`research_lab/label_v3_blind.py` produces 24 fixed level-one V2/V3 A/B comparisons across the three real-year snapshots, excluding the original 24 V1/V2 judgment cases. Raw source names, visible paper titles, rubric and private mapping are kept in ignored `local_only/`. The method allows an authorized *key-isolated AI* review and validates immutable evidence and pairwise grades. **No reviewer was run, no new scientific entailment was measured and no V3 superiority is claimed.** The original frozen method, AI rating sheets and old negative results are untouched.

## Constructor assessment requirements: evidence-based acceptance gates

This table follows the original [PhD assessment](ASSIGNMENT_SOURCE.md), not proposed extra experiments. Code tests establish technical integrity; they do not substitute for scientific validity. **Current stage: viable and reproducible partial validation, not 100% scientific completeness.**

| Original requirement | Evidence currently in `main` | Remaining acceptance condition |
|---|---|---|
| Deliverable 0, P1–P2, T2: formal heuristic, laminar hierarchy, 10–15 coarse budgets | `report.pdf`, `src/core.py`, 2020/22/24 hierarchies and `verify_selected_outputs.py` | Demonstrated implementation/structural invariants; no global objective optimum claimed |
| T1: real temporal corpus and hyperedge distributions | `inputs/data.zip`, snapshot stats and `outputs/eda_summary.json` | Verified original dataset, year cutoff and counts; no alternate corpus **required** because Option A was supplied |
| P3, T6: *non-circular* semantic coherence and meaningful null | held-out source-paper connectivity, publication-title second view, 99 constrained null shuffles | Second view remains correlated with name input; domain-blind paper-content or expert coherence validation would strengthen independence. Null `p=0.69` is **not significant** |
| P4, T4: implemented native high-order coarsening | selected collapsed hyperedges and multiplicity verifier | Original-arity and relation provenance verified; no pairwise reinterpretation |
| P5, T3, T6: real temporal IDs, cross-year ARI, five 10% deletion perturbations | temporal event logs, development runs, stress metrics, seeds and bootstrap intervals | ARI can be gamed by freezing old IDs; report measured changes and uncertainty |
| P6, T5–T6: **scientifically faithful titles/glosses and overclaim rate** | four-snapshot generated labels, 48 AI-reviewed samples and blank 24-case A/B form | **PENDING truly independent semantic review (a key-isolated LLM/NLI evaluator is allowed; human review is optional)**. All 48 earlier reviewer IDs say GPT-6; 8/48 gloss cases determinate, 40 unclear. Completed A/B human reviews cannot be fabricated |
| T6: **one** extrinsic task with flat control | 14 exploratory Type-A retrieval questions, Type-B source-recall pilot, 18-query exact retrieval control | Honest initial Type-A result 2/14 hier vs 1/14 flat; previously inspected questions and small N. **Original evaluator computes all candidate dot-products for both arms before routing**: 1088 visited nodes is NOT a speedup |
| T7: 3–5 page paper and AI disclosure | 3-page `report.pdf`, `scripts/report.tex`, `AI_USAGE.md`, pinned `requirements.txt` | Confirm assessor access to private repo and inspect final PDF; disclose remaining gaps |

**Not required by the original assessment:** an additional 300–500-paper arXiv corpus (Option B is an **alternative** to the supplied Option A), an LLM answering all four Type-B questions (one genuine extrinsic task suffices), a production front-end, graph database or model fine-tuning. These may improve research, but should not delay honest completion of mandatory T5/T6 validation. The most important open gates are **independent label/gloss faithfulness** and a genuinely independent coherence assessment with transparent uncertainty; negative results do not constitute a software defect.

## Stage 2: safe title proposals (24 cases; exploratory only)

[Conservative alternatives to 24 V2 titles](../research_outputs/label_v2/v2_conservative_title_proposals_24.csv) were written **after** viewing AI title scores, so they are development-only and **not** evidence of improved held-out accuracy. **23 title changes were proposed; one pre-existing abstention was retained.** Weakly supported scientific nouns are scoped as subset/mixed topics, and unsupported concept claims are replaced by explicit abstention where necessary. Original locked hierarchies, original V1/V2 label/gloss pairs and gold questions were not changed. The [repair summary](../research_outputs/label_v2/v2_conservative_title_summary_24.json) states that fresh untouched evaluation is still needed; this does NOT resolve independent scientific label entailment.

## Frozen V2 gloss claim audit (source-scoped, 24 cases)

The [24-row V2 claim-by-claim audit](../research_outputs/label_v2/v2_gloss_source_audit_24.csv) and [machine-readable summary](../research_outputs/label_v2/v2_gloss_source_summary_24.json) provide a reproducible, read-only recount on **all members** of the frozen 2022/2024 clusters against the original Constructor archive. The case-by-case A/B worksheet, mapping key and model assignments were not modified.

- **Literal provenance and count claims:** 23 of 23 explicit `N of M` gloss counts, cutoff years and supporting node IDs matched the entire original exported-node membership. **0/23 false count claims** among verifiable assertions (descriptive, not an independent estimate of scientific truth). The 24th gloss is a **qualitative abstention**, not a testable count: `unclear` for this narrower scope.
- **Scientifically meaningful title / full-paper semantic entailment:** **0/24 independently established, 24/24 `unclear`**, so the independent semantic overclaim rate remains **`null`**, not 0%. The count tests validate literal *name occurrences*, not whether source research papers establish a scientifically coherent concept or whether the titles are accurate.
- Two user-supplied AI-only 24-pair forms offer **non-independent exploratory title judgments**: on V2 alone, they agree on 18/24 titles and disagree on six. Some names remain weak (for example, `Set / Ccsd`, `Prediction / Accurate`, or `Stability / Heat Map Visualization`), despite their gloss counts being literally verifiable. Earlier `AI_PRELIM...` reviewer identities are not human evaluators.
- [Per-case two-view AI title notes](../research_outputs/label_v2/v2_title_ai_views_24.csv) preserve the exact 24 V2 judgments and case-specific source-scoped reasons, separate from the 24-row machine-verifiable gloss audit. Of the 24 titles, both AI perspectives called **5 accurate, 11 vague and 2 wrong**, while **6 ratings disagreed**. The two AI perspectives are not two independent expert raters.
- Reproduce this scoped check with `python -m research_lab.label_v2 --project . --audit-v2-gloss`. This never re-runs or changes the frozen hierarchy. **Do not substitute its 0/23 source-count rate for the independent P6 scientific overclaim requirement.**

## Requirement-to-evidence index

| Required work | Files | Verified status / limitation |
|---|---|---|
| Formal objective, P1–P6, comparison to related work | [report.pdf](../report.pdf), `src/core.py` | Heuristic native high-order method; no global optimality claim |
| T1 corpus/year/arity | `inputs/data.zip`, `outputs/snapshot_stats_*.json` | Actual yearly slices; year/first-seen semantics matter |
| T2 nested direct-hypergraph hierarchy | `outputs_selected/hierarchy_*.json`, `research_outputs/final_matrix/` | Laminar/budget checks pass; 13 methods × 5 seeds |
| T3 temporal identity/events | `outputs_selected/temporal_events.json` | Four snapshot checks pass; event types heuristic |
| T4 true hyperedge collapse | `outputs_selected/collapsed_edges_*.json` | Provenance/arity/multiplicity retained for **training** events |
| T5 automatic titles and glosses | `outputs_selected/label_evidence_*.json`, `research_outputs/label_v2/` | V2 keyword/provenance evidence audited, not expert validated |
| T6 controls/robustness | `research_outputs/stress_temporal20_extended/`, `metrics.json` | p=0.69 null (non-significant), 5 perturbation runs |
| T6 source holdout | `research_outputs/confirmation/`, `research_outputs/model_lock.json` | 2024 cut 0.6623→0.7172 **worse** |
| T6 labels | `outputs_selected/label_review_results.json`, blank V2 sheet | V1: 8/28/12 accurate/vague/wrong. 40/48 overclaim unclear |
| T6 downstream utility | `outputs_selected/selected_retrieval_EXPLORATORY_2025.json`, `research_outputs/type_b_audit/` | Type A 2/14 hierarchical vs 1/14 flat (previously inspected); Type B source Recall@5 0.52083 for BOTH routes; claim answer quality unscored |
| T7 paper, code, disclosure | `report.md`, `report.pdf`, `AI_USAGE.md`, `requirements.txt` | Authored, tested, with limitations stated |

## Paired extrinsic T6 check (original 14 Type-A questions)

The archived Hit@5 record has **one hierarchical-only hit (Q1)**, **zero flat-only**, **one both-hit (Q8)** and **12 neither-hit**. An exact paired McNemar/sign-test calculation on the one discordant question gives **two-sided p=1.0**. This is a **descriptive analysis of questions already inspected during development**, not confirmation or evidence of statistically better retrieval. The original TF-IDF implementation computes all candidate scores *before* routing; route-membership counts are not measured acceleration. A separately tested exact branch-and-bound control preserved 18/18 flat rankings but was slower. Source-grounded answer generation is an optional extension, not an implicit success of the retrieval evaluator.

## What cannot be repaired by rerunning the same model

1. **Semantic label correctness and overclaim.** A new, independent qualified reader must assess 24 paired V1/V2 A/B examples using `research_outputs/label_v2/BLIND_LABEL_COMPARISON_TO_FILL.csv`. The data are currently blank. The original 48 ratings were AI-assisted, non-blind development diagnostics.
2. **Type-B factual questions.** The Type-B two-stage retrieval experiment is **committed and verified** on `main`: 4 questions, 46 time-eligible papers, 3/5/10-paper source-coverage measures, 36 as-yet-unrated claim rubrics, a deterministic ranking fingerprint, and an exact-top-5 traversal audit. For the gold sources **actually found** in the eligible paper set, flat and routed-hierarchy Recall@5 are both **0.52083** (macro-average over four questions). Counting *all* listed gold sources, including unavailable matches, both score **0.31250**. This is paper-source retrieval only, NOT factual answer correctness. An actual qualified reader with authorized access to full texts must check passage entailment for 36 required claim statements; the missing sources and previously inspected questions mean this is exploratory.
3. **Independent out-of-sample validity.** One corpus and previously inspected questions do not yield generalization evidence. An additional dataset, newly collected ground truth or independent specialist checks would be needed. Never retroactively call examined questions a blind test.
4. **Temporal confidence and null interpretation.** Five seeds and a constrained 99-shuffle null are useful diagnostics but cannot claim proof of an optimal scientific partition. Preserve source-group held-out worsening and non-significant null.

## Independent review protocol (blind LLM with isolated context or authorized human)

**V2 labels:** The Constructor task explicitly permits a **blind LLM or human** judgment and NLI/entailment checks; a human reviewer is not mandatory. For an AI-only evaluation, use a separately initialized, *key-isolated* evaluator with no access to earlier ChatGPT scoring, answer key, or selected model output, and disclose the model, prompt, evidence scope and adjudication limitations. Provide only the A/B worksheet and authorized independent full-paper passages (not keyword supporter tables used by the labeller), not the unblinding key or previous V1 judgments. Each row: rate A and B `accurate/vague/wrong`, then `yes/no/unclear` on unsupported gloss claims, include a reviewer identifier and evidence-based comments. If full-text sources are unavailable, choose `unclear`. Do not give the employer-provided materials to an external reviewer without permission to share them. Score paired wins/losses after all genuine reviews; disclose reviewer independence truthfully. Source keyword counts are **not** human scores.

**Type-B claims:** Use [`research_outputs/type_b_audit/CLAIM_LEVEL_REVIEW_BLANK.csv`](../research_outputs/type_b_audit/CLAIM_LEVEL_REVIEW_BLANK.csv), which already exists on `main`. For every claim, note full passage/source support (yes/no/unclear), evidence and actual reviewer identity. Do not score factual answer correctness if no answer was generated. Missing gold-paper titles are missing data, not negative entailment examples.

## AI-assisted diagnostic review — NOT independent human validation

A ChatGPT GPT-6 diagnostic review was completed on **20 October 2026** without modifying the original blank reviewer forms.

- [24-case label review](../research_outputs/label_v2/ai_label_review.csv): qualitative A/B label ratings using only sampled member names and displayed article titles, with row-specific reasons. Provisional preferences: **A 8, B 13, ties 3**. These are not independent blinded human evaluations. The A/B identity key was not used; the model style may be inferred from wording, so a paired V1↔V2 scientific win, p-value, or independently validated overclaim rate **cannot** be claimed from these votes.
- [36-claim Type-B evidence triage](../research_outputs/type_b_audit/ai_claim_evidence_triage.csv): case-specific caveats based on the **supplied gold rubric**, not independent full-paper inspection. The rubric marks **31 full, 3 partial and 2 asserted-only** coverage claims; these are *rubric categories*, not verified truth rates or answer accuracy. Every entry explicitly marks full-text verification and factual answer scoring as **not performed**.
- Both human review forms are unchanged: [24-case blinded worksheet](../research_outputs/label_v2/BLIND_LABEL_COMPARISON_TO_FILL.csv) and [36-claim worksheet](../research_outputs/type_b_audit/CLAIM_LEVEL_REVIEW_BLANK.csv). No reviewer ID or human consent is fabricated.
- The dataset and reference rubrics are employer-provided confidential assessment material. Consult Constructor before forwarding source data or blind worksheets to external annotators.

**Remaining scientific gap:** independent, permitted full-text evidence/entailment checking, preferably by a qualified reader; if unavailable, the final report must keep P6 faithfulness and Type-B factual-answer validity **unverified**. Do not rerun the same observed queries and rename them an unseen test.

## Reproducible A/B mapping of the earlier AI-only ratings

The [aggregate analysis](../research_outputs/label_v2/ai_paired_summary.json) pairs the already recorded 24 AI A/B decisions with the frozen V1/V2 candidate texts by **exact label and gloss equality**. All 24 mappings are unique; no secret local key was needed or published.

- **AI label-accuracy rating (0=wrong, 1=vague, 2=accurate):** V2 better on **6**, V1 better on **2**, **16 ties**; mean paired V2 minus V1 score **+0.167**.
- **AI subjective title-plus-gloss preference:** V2 preferred **18**, V1 **3**, **3 ties**. This is distinct from scientific label accuracy.
- A paired sign-test arithmetic yields `p=0.2890625` on the eight non-tied accuracy ratings; **not confirmatory evidence** due to non-independent AI assessment, implicit model-style cues and previously inspected evidence.
- No independently checked gloss entailment, no verified overclaim rate, no human review and no full-text source verification have resulted from this step. Avoid confusing general preference with scientific faithfulness.
- Recompute deterministically, without overwriting the human worksheet or creating a new branch:

```powershell
.\\.venv\\Scripts\\python.exe -m research_lab.label_v2 --project . --summarize-ai
```

## Primary-source trace for Type-B (scope-limited)

[Single 36-row source audit](../research_outputs/type_b_audit/primary_source_audit.csv) lists each claim, an independently located publisher/author source URL where one was inspected, the strongest evidence visible there, and an explicit unresolved-entailment flag. **19/36** had at least an abstract or selected publisher section inspected; **17/36** were restricted to the supplied Constructor rubric. **Zero of 36** were certified by complete independent full-text claim/passage review. Even for the 19, abstract consistency does not imply full claim entailment. The original human-annotation sheet remains empty.

The limited external check independently corroborates particular narrower observations, e.g. PES softening on tested uMLIPs ([Deng et al.](https://www.nature.com/articles/s41524-024-01500-6)), within-architecture l=0 NequIP ablation ([Batzner et al.](https://www.nature.com/articles/s41467-022-29939-5)), migration-barrier benchmark screening ([Bheemaguli et al.](https://pubs.rsc.org/en/content/articlehtml/2026/dd/d5dd00534e)), and latent equivariance ([TransIP](https://arxiv.org/abs/2510.00027)). These results must not be generalized to other materials/methods without evidence.

## Next release checklist

- [x] Private repository, real input, pinned dependencies, 65+5+5 research-run registries.
- [x] Four selected hierarchical snapshots, temporal events, direct coarsening, robustness and null logs.
- [x] Updated **four-page** vector-illustrated article, scientific Markdown companion, software/structural tests and 26-test CI suite.
- [x] Tested Type-B retrieval/source coverage outputs committed directly to `main` (`7db3e6e`); 25 software tests passed on the applicant's Windows machine.
- [x] AI-only 24-pair diagnostic mapped reproducibly to V1/V2; 36 Type-B rubric claims source-traced with explicit limits.
- [ ] Independent A/B label review and complete authorized Type-B claim-source entailment review, if available.
- [x] Typeset and publish updated 4-page journal-style `report.pdf` from `scripts/report.tex`; verify charts, negative results, and source-scope caveats.
- [ ] Incorporate *real independent* review ratings if obtained, with denominators and uncertainty.
- [ ] Confirm assessor can access the **private** repository or send a confidential ZIP. A URL alone is insufficient.

Prior unhelpful/duplicate how-to documents were removed from the current snapshot to keep navigation simple. Their original text remains retrievable from Git commit history.


## Additional frontier study (20 October; implementation only, not new measured evidence)

The opt-in `research_lab/retrieval_frontier.py` evaluates a predeclared routed
budget sequence (1/2/4/8/12 root clusters) using one shared source-dated index.
It has an exact top-5 equivalence invariant at 12 roots, separate gold ranking
and scoring modes, candidate + centroid counts, and source-isolated output under
`local_only/`. Toy-fixture unit tests cover the control logic; no new original-data
frontier outputs or independent gold scores are claimed yet. See
[REPRODUCE §14](REPRODUCE.md) and [reviewer checklist](REVIEWER_CHECKLIST.md).



## Historical retrieval budget score (new local-only evaluator; results pending)

The code `research_lab/frontier_historical.py` now fills the previously missing
Type-A **quality-versus-online-computation** axis of the gold-separated budget
frontier. It performs source ranking separately from opening the original
`data/ground_truth.json`, freezes a SHA-256 checksum of the complete rank
artifact, then scores exactly 14 original Type-A questions at all route budgets
and leaves all four Type-B answer questions unscored. It also reports expected
targets unavailable in the 2025 candidate index, paired bootstrap differences
versus flat (resampling query units) and descriptive sign tests. Charts and raw
gold remain in Git-ignored local folders; see [Reproduce §15](REPRODUCE.md).

**Not a measured improvement yet:** this addition is an implementation, not a
new observed real-corpus result until the candidate runs it. Every historical
question was previously inspected; the formal independence and full-paper
semantic-quality gates remain unfulfilled. The frozen `report.pdf`
must not be edited to assert improved accuracy from these data.
