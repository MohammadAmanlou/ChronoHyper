# Assessment status and remaining evidence gates

**Reviewed 8 November 2026 · Mohammad Amanlou · [Main README](../README.md) · [Full scientific report](../report.pdf) · [Detailed evaluation archive](EVALUATION.md)**

**Status:** core implementation and source-dated native-hypergraph invariants have executable checks. Scientific concept-label fidelity, independent new-corpus performance and Type-B factual answer generation have **not** been established. Keep all negative and qualified results visible.

## Requirement-to-evidence map

| Assessment component | Verifiable artifact | Status and limitation |
|---|---|---|
| T1: temporal dataset | `inputs/data.zip`, `outputs/eda_summary.json` | 5,798 entities, 1,429 events, 52 original papers; source-year restrictions |
| T2: hierarchy | `src/core.py`, `outputs_selected/hierarchy_*.json` | Four nested levels, selected budgets and laminar membership checked; local heuristic **not a global optimizer** |
| T3: temporal identities | `outputs_selected/temporal_events.json` | Persistent IDs and overlap-based birth/merge/split/death bookkeeping; inferred concept changes not proven |
| T4: native edge collapse | `outputs_selected/collapsed_edges_*.json` | Higher-order events, IDs, arity, original endpoints, multiplicity and provenance preserved; pairwise alternative recorded |
| T5: dated titles/glosses | `research_lab/label_v3.py`, `research_lab/v3_provenance_audit.py` | 180/180 membership/lexical/date checks, 115 explicit abstentions; **semantic entailment not tested** |
| T6: comparative evaluation | `metrics.json`, `research_outputs/final_matrix/`, `research_outputs/confirmation/` | 65 development seed-method runs, five selected confirmation runs; limited source-group separation |
| T6: null and stability tests | `research_outputs/stress_temporal20_extended/` | 99 degree/arity-preserving null shuffles: **p=0.69**, not significant; five deletion repeats |
| T6: extrinsic retrieval | `research_lab/retrieval_frontier.py`, `research_lab/fresh_retrieval.py` | Predeclared 34-query Flat 3/34 vs Route-4 2/34; route saved 59.3% online dot products but missed one answer |
| T7: reporting and reproducibility | `report.pdf`, `report.md`, `scripts/report.tex`, `docs/REPRODUCE.md` | CI, source and figure checks; source disclosure in `AI_USAGE.md` |

## Findings that constrain the claims

The selected `native_temporal_20` is a trade-off model, not a dominant one. Lower-is-better held-out paper-group cut rose from **0.6623** (development) to **0.7172** (confirmation); structural degree/arity null **p=0.69**. Five seeds represent perturbations of the *same corpus*, not five independent replications.

Historical inspected Type-A comparison: Flat and Route-4 both **2/14 Hit@5** (57.9% fewer online dot products for Route-4). A **different, source-screened** 34-question exercise (two of 36 initial targets excluded **before** ranking because their source-paper association was unverifiable) obtained Flat **3/34** and Route-4 **2/34**. The new question texts were independently authored, but targets and source corpus were reused: this is **not an independent external-corpus test**. Source-level audit cannot validate full scientific answers.

### Exploratory AI-only label and paper review

- A 24-pair V2/V3 title/gloss comparison had **21 evaluable** cases, V3 **10 wins / 4 losses / 7 ties**; descriptive unadjusted paired sign **p≈0.180**, not significant.
- A separate 24-matched-pair, 48-row **AI-only** name/title coherence contrast had mean ratings **3.542 real vs 2.750 control**, descriptive unadjusted sign **p≈0.041**. The same-corpus AI judgments are **not independent full-text scientific validation** and do not overturn structural `p=0.69`.
- On 36 Type-B source-claim judgments, an AI-only review gave **25 yes / 1 no / 10 unclear**. A targeted **nine-claim** second AI review identified a disagreement for `Q16.C3`, uncertainty for `Q15.C8` and `Q17.C3`, and **three Q17 source/task mismatches**: evidence on atomistic MLIP/NEB does not directly answer a coarse-grained molecular-dynamics phase-transition question. These findings concern citations and source/task relevance, **not** verified generated-answer accuracy. No independent qualified full-text review has completed.

### Optional neural retrievers: already inspected 34 cases (post-hoc only)

| Arm | Hit@1 | Hit@5 | Hit@10 | Hit@20 | Hit@100 | MRR@5 |
|---|---:|---:|---:|---:|---:|---:|
| BGE-M3 context | 5 | 10 | 13 | 14 | 25 | 0.1887 |
| Three-view BGE RRF | 3 | 10 | 13 | 16 | 26 | 0.1627 |
| Qwen3-Reranker-0.6B raw | 2 | **12** | **19** | **21** | 28 | 0.1814 |
| Qwen3 + one fixed context anchor | 5 | **12** | 18 | **21** | 28 | **0.2181** |
| Qwen3 + two fixed context anchors | 5 | **12** | 16 | **21** | 28 | 0.2029 |

The early BGE neural cross-encoder degraded Hit@5 to **1/34**. Three source views put the answer in the **Gold-blind candidate pool for 29/34** questions (mean 208.94 candidate entities); **that is candidate recall, not Hit@5**. The five source-absent questions were `F005`, `F024`, `F028`, `F034`, `F036`.

Qwen3 variant Hit@5 of **12/34** versus BGE context **10/34** is a **+2/34 descriptive improvement**, after multiple development-stage choices and inspections. Local matched audit: **5 wins, 3 losses, 26 ties**; exploratory unadjusted two-sided exact discordant-pair **p=0.7265625**, not significant. **No statistical, held-out or cross-corpus improvement claim is justified.** All GPU results were locally scored only after rank-only SHA verification; frozen source rankings and original selected-model outputs were not altered. See [short experiment summary](ADVANCED_GPU_AND_TYPE_B.md) and [Markdown report §8](../report.md#8-gpu-semantic-retrieval-and-qwen3-reranking--post-hoc-development-24-october-2026).

**New evidence-intake engineering gate:** actual-corpus CI generates 24 blinded
V2/V3 label comparisons and source-link candidates from 28 unique pre-cutoff
primary paper records (92 case–paper incidences). Authentic primary full texts
have NOT been retrieved, copied, judged or certified by this step; the
private local intake and reviewer decision are pending. See the
[full-text intake commands](REVIEWER_CHECKLIST.md#primary-paper-evidence-review-executable-next-gate-24-blind-label-pairs).

## Additional temporal diagnostic (8 November 2026; post-hoc)

The [source-delta locality audit](../research_outputs/temporal_locality_posthoc.json)
matches exactly the original fitting hyperedge IDs in the selected collapsed
exports, excludes 20 held-out source papers, and reports exposed versus unexposed
preexisting-node identity changes. **2020–22:** 1/76 vs 10/1,429,
conditional p=0.546; **2022–24:** 7/146 vs 20/2,018, conditional
p=0.002. The comparisons are **exploratory, same-corpus and not adjusted
for repeated post-hoc inspection**; neither is evidence of a causal or
independently verified improvement. Both results, including the null first
transition, are retained.

The local applicant's automatic paper extraction previously reported 26/28
accessible PDFs, 22 with historical arXiv v1 metadata, and 82 candidate
case-paper passages; **the CI repository has no authority to certify their
version authenticity, relevance, copyright or independent human judgments**.
Automated extraction is not a completed semantic overclaim-rate evaluation.

## Qwen3 local evidence gate outcome (9 November 2026)

The user's private, source-filtered 24-case run gave **0 cases with sufficient evidence**. In **21/24**, no eligible dated source passage was presented to the local AI judge; **3/24** (`L005`, `L022`, `L024`) reached the model, which reported the provided excerpts insufficient. Thus **zero does NOT mean that all 24 labels are false or have overclaims**. A paper-level count (22 historically dated arXiv v1 PDFs among 28 linked original papers) must not be conflated with case-specific evidence coverage. The correct scientific full-text overclaim rate remains **NOT_EVALUATED**.

The applicant can audit the **existing private files offline**, without re-running Qwen3, downloading sources, inspecting answers or reading the hidden A/B mapping:

```powershell
.\.venv\Scripts\python.exe -m research_lab.evidence_gap_audit --project .
```

The diagnostic prints counts and blind IDs only, separates absent/undated passages from AI insufficiency, and is covered by synthetic CI tests. Independent scientific adjudication is still outstanding.

## What remains before scientific delivery can claim completion

1. **Original-paper scientific evidence.** Obtain authorized complete primary-text passages, versions available by the original cutoff and independent qualified adjudication of scientific labels and 36 Type-B source/task claims, especially Q17.
2. **True answer evaluation.** Test actual generated answers with attributed passages and a question-grounded, independent correctness rubric. Citation matching or AI opinions on titles alone are insufficient.
3. **Untouched confirmation.** Predeclare the exact architecture, selected prompt, candidate-union policy and metrics *before* collecting a genuinely new, source-validated question set. Lock ranking hashes before local Gold scoring, and report paired error bars and infrastructure costs.
4. **Human understanding and privacy.** Review the report, source data permissions, licenses, execution instructions and [AI-assistance disclosure](../AI_USAGE.md) before any external delivery. This repository's state does not indicate that the assessment was submitted or accepted.

Historical protocols, original reviewer flags, hashes and the full registry remain in [the evaluation record](EVALUATION.md), [reproduction guide](REPRODUCE.md) and immutable [research outputs](../research_outputs/). Old long working notes remain retrievable in Git history, rather than being mistaken for current scientific conclusions.
