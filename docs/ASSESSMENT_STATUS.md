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

The user's private 24-case run returned **0 cases with sufficient AI-reviewed evidence**. The original program stored **21/24** cases as `INSUFFICIENT_NO_VERIFIED_HISTORICAL_PASSAGE`, and **3/24** (`L005`, `L022`, `L024`) received parsed AI judgments of insufficient supplied excerpts. **Crucial implementation caveat:** the original judge also stores **Ollama failures and invalid JSON** under that same `INSUFFICIENT_NO_VERIFIED_HISTORICAL_PASSAGE` status. Thus the initial interpretation that all 21 lack eligible historical excerpts **was not established**. The corrected audit examines the existing per-case `review_notes` and source-gate flags, distinguishing genuine absent/undated evidence, model/JSON errors and unexplained mismatches without repeating inference. These outcomes **do not demonstrate incorrect labels**. A source-paper count of 22 dated PDFs is not case-level evidence coverage; the scientific overclaim rate remains **NOT_EVALUATED**.

The applicant subsequently ran the corrected offline audit: **21 cases have eligible dated source passages but failed due to a local Ollama execution or JSON-processing error; 3 cases received parsed AI judgments of insufficient excerpts.** The evidence source gate itself is therefore **not** the cause of those 21 unsuccessful evaluations. The current exact exception subtype is not yet verified from the private notes; default Qwen3 thinking plus a 650-token limit is one plausible contributor, not a demonstrated diagnosis.

A separate **post-hoc, checkpointed local AI-only retry** is available at `research_lab/retry_failed_auto_label_judge.py`. It turns off thinking in the Ollama API request, requests JSON with more output room, and retries **only original model/JSON errors**. It writes a **different private CSV and summary** and never alters the original 24-case review, the three parsed judgments, selected outputs, or the main PDF. Run its `--probe` before `--run`; the model remains an AI-only preliminary reviewer, not a source of independent semantic entailment.

The applicant can audit the **existing private files offline**, without re-running Qwen3, downloading sources, inspecting answers or reading the hidden A/B mapping:

```powershell
.\.venv\Scripts\python.exe -m research_lab.evidence_gap_audit --project .
```

The diagnostic prints counts and blind IDs only, separates absent/undated passages, model/JSON errors and AI insufficiency, and is covered by synthetic CI tests. Independent scientific adjudication is still outstanding.

## Local AI retry completed (9 November 2026; post-hoc only)

The applicant executed the **real** `--run` after a successful `--probe` on the private Windows research workspace, rather than merely running the synthetic unit tests. The resulting local-only `AUTO_AI_RETRY_SUMMARY.json` reports: **21/21 previously failed model/JSON cases recovered**, **0 retry execution errors**, **3 previously parsed judgments preserved**, **24/24 valid local AI responses combined**, **0/24 marked evidence-sufficient**, and **0 unresolved cases**. Input hashes were saved; original blind sheet, historical passage candidates, review, locked metrics and PDF were not overwritten. These are user-reported local outcomes; the remote CI does not contain the private candidate passages and cannot independently certify the result.

**Interpretation:** the prior 21 errors were *execution/JSON failures*, not missing historical passages. Their successful retry removes the technical failure from this particular run. The local AI then judged all 24 supplied short source excerpts **insufficient to substantiate both candidate labels/glosses**, using a conservative prompt. This is **not** a 100% label-error rate, not a scientific overclaim-rate estimate and not qualified independent human review. Do not convert “AI evidence sufficiency=0/24” to scientific label correctness. The next evidence gate is to inspect case-specific notes and primary passages with version/date provenance, then obtain genuinely independent ratings or transparently record the missing evaluation. Any expanded passage selection or prompt development must be labeled post-hoc; frozen benchmark metrics stay unchanged.

## Scientific-versus-structural source of label insufficiency (9 November 2026)

Inspection of the local Qwen3 review notes showed that some failures concerned
insufficient paper evidence for a shared scientific theme (DFT, training, force),
whereas L022 and L024 concerned **internal graph-output count claims** (9/16
and 19/56) that a primary paper is not expected to contain. The latter must
be verified against the frozen hierarchy and original dated node names, not
through the external source alone. The code already has a deterministic
180-label membership/phrase/cutoff provenance audit, which does **not**
constitute independent semantic correctness. This makes the 0/24 result
unsuitable for claiming a 100% semantic label failure rate. Details and the
separated review protocol are in [Label evidence separation](LABEL_EVIDENCE_SEPARATION.md).

## Local source-name provenance audit reproduced (10 November 2026)

**User-reported Windows run**, after pulling `main`, successfully executed
`python -m research_lab.v3_provenance_audit --project .` against the
applicant's private original corpus and previously generated V3 candidates.
This is **real local data validation**, not synthetic unit-test output.

| Frozen snapshot | V3 labels audited | Majority-name labels | Partial-name labels | Explicit abstentions |
|---|---:|---:|---:|---:|
| 2020 | 60 | 8 | 13 | 39 |
| 2022 | 60 | 6 | 16 | 38 |
| 2024 | 60 | 5 | 17 | 38 |
| **Total** | **180** | **19** | **46** | **115** |

Reported audit properties: **0 structural/lexical errors**, **65** leading or
partial source-name labels, **115/180 (63.89%)** explicit conservative
abstentions, **2,103** dated source-article provenance reference checks,
`locked_model_changed=false`, `gold_answer_files_opened=false`.
The local audit independently *recalculates deterministic graph/name claims*
from original artifacts; it is **not** an independent scientific expert
judgment. The exact number of full-paper semantic entailment claims that can
be evaluated remains **0**, and independently measured label accuracy and
scientific gloss overclaim rate remain **null/not evaluated**. The local
ignored JSON report, as opposed to a private paper PDF or A/B key, is the
source of these reported counts; remote CI cannot attest to local inputs.

**Next evidence gate:** inspect source-date-verified full articles and obtain
an independent, blinded semantic review with per-arm title and gloss grades,
explicit unsupported/unclear cases, denominators and reviewer provenance.
Keep lexical-consistency pass counts separate from scientific correctness
and preserve all negative or inconclusive assessments. See
[Label evidence separation](LABEL_EVIDENCE_SEPARATION.md).

## What remains before scientific delivery can claim completion

1. **Original-paper scientific evidence.** Obtain authorized complete primary-text passages, versions available by the original cutoff and independent qualified adjudication of scientific labels and 36 Type-B source/task claims, especially Q17.
2. **True answer evaluation.** Test actual generated answers with attributed passages and a question-grounded, independent correctness rubric. Citation matching or AI opinions on titles alone are insufficient.
3. **Untouched confirmation.** Predeclare the exact architecture, selected prompt, candidate-union policy and metrics *before* collecting a genuinely new, source-validated question set. Lock ranking hashes before local Gold scoring, and report paired error bars and infrastructure costs.
4. **Human understanding and privacy.** Review the report, source data permissions, licenses, execution instructions and [AI-assistance disclosure](../AI_USAGE.md) before any external delivery. This repository's state does not indicate that the assessment was submitted or accepted.

Historical protocols, original reviewer flags, hashes and the full registry remain in [the evaluation record](EVALUATION.md), [reproduction guide](REPRODUCE.md) and immutable [research outputs](../research_outputs/). Old long working notes remain retrievable in Git history, rather than being mistaken for current scientific conclusions.
