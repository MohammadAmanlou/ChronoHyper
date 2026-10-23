# Assessment evidence and reviewer decisions — 20 October 2026

[Main README](../README.md) · [Original assignment](ASSIGNMENT_SOURCE.md) ·
[Reproduction](REPRODUCE.md) · [Full historical evidence](EVALUATION.md)

## One-page assessment rubric map

| Assignment component | Evidence | Defensible conclusion / outstanding gate |
|---|---|---|
| T1 — original temporal data and QA | `outputs/eda_summary.json`, `outputs_selected/*`, `inputs/data.zip` | Four dated snapshots, arities/growth, source cutoffs and data warnings documented |
| T2 — formal native hypergraph abstraction | `report.pdf`, `src/core.py`, `outputs_selected/hierarchy_*.json` | Formal heuristic surrogate and laminar budget constraints; no global optimality |
| T3/P5 — real temporal identity | `outputs_selected/temporal_events.json`, five-seed and deletion metrics | Persistent IDs and birth/merge/split/death logs; significance/generalization limited |
| T4 — operational high-order collapse | `src/core.py`, `outputs_selected/collapsed_edges_*`, `research_outputs/projection_loss/` | Native edge ID, arity, multiplicity, provenance preserved; clique projection loss quantified |
| T5/P6 — automatic title/gloss and temporal honesty | `research_lab/label_v3.py`, `research_lab/v3_provenance_audit.py` | All 180 V3 phrases cross-checked lexically; 115 abstentions; paper-level overclaim accuracy still **unverified** |
| T6/P3 — noncircular coherence/null | `research_outputs/` nulls, matched 48-item AI review | Positive title/name AI-only contrast; same-corpus, related signal; original structural shuffle `p=0.69` is nonsignificant |
| T6 — stability uncertainty | `metrics.json`, `research_outputs/final_matrix/` | Five seeds, source-group confirmation, 10% edge deletion reruns; not five independent corpora |
| T6 — extrinsic utility | `research_lab/frontier_historical.py` and local output | On **previously inspected** 14 Type-A questions route-4 and flat each hit 2/14; route-4 uses 57.9% fewer dot products; no fresh-task superiority |
| T7 — report/reproducibility | `report.pdf`, `scripts/report.tex`, `report.md`, `AI_USAGE.md`, Actions | Four-page PDF builds with identical normalized text, clean Python 3.11 tests |
| New scientific validation | This file, local rated forms and private evidence | Key-separated AI assessments completed; full-paper/expert scientific entailment and external data remain **open** |

## Newly obtained V2 ↔ V3 paired title/gloss ratings

Scored from user's local `label_v3_fresh/rated_24.csv`, hash
`0736228188678527b98b60be0a59aad37bb370ab7fb8a3db928888b104f01af6`.
The rating file is **not** pushed: it includes original private scientific items.

- **24** blinded same-corpus development pairs; **21** evaluable, **3** insufficient.
- V3 title grade wins/losses/ties: **10 / 4 / 7**; mean V3–V2 score delta **+0.2857** on the 0–2 rating scale.
- Descriptive, unadjusted paired sign **p=0.1795654**. This is *not* evidence of a statistically significant superiority of V3.
- Overclaim judgements: V2 **0 observed yes among 21 determinate** (3 unclear); V3 **0 observed yes among 14 determinate** (10 unclear). Both displayed conditional rates are numerically **0% only in their respective determinate subsets**. Even treating those subsets as independent Bernoulli draws, illustrative exact two-sided 95% upper bounds after zero observed events are **16.1%** (V2, n=21) and **23.2%** (V3, n=14); because review selection and semantic sufficiency are not random, these are *not* guaranteed error bounds for all full-paper claims. Do not write "0 scientific overclaims" as a project conclusion.
- The returned reviewer identifier is **OpenAI GPT-6**. Reviewer identity and full-text expertise are not independently certified by source code. Titles and sampled member names **cannot entail paper claims**.

## Newly returned 48-case AI-only coherence contrast

From the *different* file `local_only/reviews/fresh_semantic/ratings_fresh_48_independent.csv`,
recorded SHA-256:
`a65814b1677a1c49f8be6d9a8a0bd44164ca2be8a6a511ee5f2f7a99e4b10c77`.

- **48** cases = **24 matched real/control pairs**, **24 evaluable**, zero pairs excluded under the supplied rating flags.
- Mean AI rating real/control: **3.5417 / 2.7500**, paired difference **+0.7917** on the five-point scale.
- **15** real-higher, **5** control-higher, **4** ties; descriptive sign **p=0.0413895** and exploratory bootstrap 95% CI **[0.2917,1.25]**.
- These are **same original corpus and same paired inputs** as earlier AI scoring. The label `independent` in the filename is a workflow distinction, *not proof* of reviewer independence, valid full-text entailment, independent corpus confirmation or correction for multiple exploratory analyses.
- The original arity/degree-preserving hypergraph shuffle gave **p=0.69**; this remains a separate, nonsignificant structural null finding.
- Before any paper-level scientific claim, a reviewer must inspect authorized source passages and note missing/unclear scientific support.

## New 36-claim Type-B AI-only source assessment (22 October audit)

The applicant obtained a **separate GPT-6 AI scientific review** of 36 question-to-source claims from a neutral seven-column worksheet. The locally scored review reports **25 supported, 1 contradicted, 10 unclear** (no pending entries). Thus **25/26 = 96.15%** of the reviewer’s *determinate* judgments say supported, but this is **not** the accuracy of generated Type-B answers, not proof that 36/36 source citations entail their claims, and not a reviewer-identity/full-text guarantee. The actual self-reported model identifier is `GPT-6 (AI scientific reviewer)`. The returned neutral CSV has SHA-256 `6c3d7729044932aeeb11e5c437b50e230778d75807d8c1046257ab1ecc215222`; the merged original-column working copy stays in ignored `local_only/`.

A second-pass citation/date/task-fit audit flagged **nine of the 36** for targeted human-or-independent-AI re-adjudication, without modifying the original ratings: `Q15.C6b` (two source papers postdate the *February 2026* task cutoff, although Kim's 2025 preprint supplies an earlier grain-boundary study); `Q15.C8` (a January 2027 journal issue, earliest pre-cutoff existence not established; original `unclear` stands); `Q16.C3` (a categorical `no` inferred from NequIP versus MACE may conflate two compatible mechanism observations); `Q17.C1/C2/C3` (the cited **atomistic MLIP/NEB** evidence does not alone answer the original **coarse-grained molecular dynamics / phase-transition** question); and `Q18.C11/C12/C16` (verify that specific findings cited from an April 2026 journal version already appeared in the December 2025 arXiv preprint). The December 2025 arXiv version of Bheemaguli similarly precedes its March 2026 journal publication. **These flags are NOT revised yes/no truth labels.**

Official publication metadata / preprints for independent verification:
- Bilbrey (published **2026-05-05**): https://www.nature.com/articles/s41524-026-02051-8
- Kim (journal **2026-03-03**, preprint **2025-10-13** with grain-boundary benchmark): https://www.nature.com/articles/s41467-026-70195-8 ; https://arxiv.org/abs/2510.11241
- Bheemaguli (journal **2026-03-30**, preprint **2025-12-03**): https://pubs.rsc.org/en/content/articlehtml/2026/dd/d5dd00534e ; https://arxiv.org/abs/2512.03642
- Sanocki (journal **2026-04-13**, preprint **2025-12-08**): https://pubs.rsc.org/en/content/articlehtml/2026/dd/d5dd00570a ; https://arxiv.org/abs/2512.10989
- Kurban (journal issue **Jan 2027**): https://www.sciencedirect.com/science/article/pii/S0927025626006725

The original task asks Q15/Q17/Q18 **by February 2026**. Evidence observed later is not automatically retroactively admissible; original dated preprints may be, if the specific claim appears in the early version. Keep separate: (i) existence of a paper, (ii) full scientific entailment of a claim, (iii) cutoff admissibility, and (iv) generated-answer correctness. This post-hoc, same-task source check must not be presented as a fresh independent test corpus.


## Targeted second AI review of nine Type-B claims (22 October 2026)

The candidate obtained a **second AI-only, source-version-aware review** of the nine earlier flagged claims. Original 36-row ratings are **NOT rewritten**. Both input sources were locally checked for matching original claim ID/text and all nine reviewer fields were nonempty. The returned review file's SHA-256 was `a7bdbf16c59251a2b4f81c39f0a918aafd5b76cf01c25a63ad98ee426d8f2389`; the original 36-rating CSV was `6c3d7729044932aeeb11e5c437b50e230778d75807d8c1046257ab1ecc215222`. The private row-level overlay stays under `local_only/`.

Of **nine targeted claims**, the new AI reviewer marked **seven source-supported** and **two unclear** (`Q15.C8`, `Q17.C3`). Seven had evidence designated available by the February 2026 cutoff; two were unclear. Only **six of nine** were judged relevant to the **original question**; all three claims `Q17.C1/C2/C3` failed task alignment: atomistic MLIP/NEB migration-barrier proxy studies are **not** evidence of effective **coarse-grained molecular dynamics** or solid-state phase-transition simulation. The reviewer identified one change in source-claim judgment: `Q16.C3` from earlier AI **no** to second AI **yes**, using the 2025 preprint on equivariance-dependent data-scaling exponents. This is an empirical architecture-dependent observation, not a theorem or a controlled causal isolation of E(3) equivariance.

If the nine newer AI judgments are displayed over the original 36 as a *diagnostic overlay only*, the nominal 36-claim **AI vote distribution** becomes **26 yes, 0 no, 10 unclear** (27 rows not retested). This must **never** be described as 26 independently confirmed correct answers or 100% source faithfulness. The 36-claim original scorer's `25/26` output remains frozen as the historical AI reviewer vote. The optional overlay compares **AI opinions**, not original benchmark gold, original paper access, or answer-generation success; the 27 unreviewed task-fit statuses remain unknown. No novel external benchmark, actual answer generation, or human review occurred.

Citations dated **before** the Feb 2026 cutoff that were independently locatable in public sources include:
- Focassio et al. 2024 (surfaces), <https://arxiv.org/html/2403.04217v1>;
- Shuang et al. 2025 (metal grain-boundary limits, model-dependent), <https://arxiv.org/abs/2502.03578v1>;
- Ngo and Ravanbakhsh 2025 (empirical force-field scaling exponents), <https://arxiv.org/html/2510.09768v1>;
- Bheemaguli et al. 2025 (MLIP+NEB, **not** coarse-grained MD), <https://arxiv.org/html/2512.03642v1>;
- Sanocki and Zavadlav 2025 **v1** (OOD, long-range corrections, mixed model/split outcomes), <https://arxiv.org/html/2512.10989v1> (do not substitute its 2026 journal/updated versions for historical evidence).
The reviewer also consulted the 2025 Liu et al. uncertainty paper, <https://arxiv.org/html/2507.21297v1>, but the exact correlated-error causal claim `Q15.C8` remained unclear.

**New highest-priority scientific blocker:** claim-by-claim scientific *source* support is **not** the extrinsic task's **answer correctness**. For Q17 especially, a high source-support vote can mask substantive irrelevance to the original research question. The assessment still needs a genuinely answer-level, task-grounded and preferably new-question check. The paper should emphasize this important failure analysis, not advertise the optimistic conditional 26/26 reviewer vote.

## Prospective new-question task-gain protocol (implementation ready; data pending)

`research_lab/fresh_retrieval.py` independently samples, by deterministic
SHA-256 ordering, three existing source-grounded entities per 2025 root and
emits a neutral author kit (typically **36 targets** across 12 root groups).
The *new* isolated question author sees target names and a pre-cutoff source
title, but **not** model outputs, past retrieval questions or old gold.
Returning questions must cite real primary evidence, paraphrase the target
without copying its name, and remain distinct from previously inspected
questions. Its question text/Gold files are **frozen together with SHA-256
before any ranking** and scored only afterward.

Predeclared primary comparison: **four-root route vs flat** with exact
type+normalized-target match on ALL frozen questions, paired Hit@5,
MRR@5 and cost. Unlike the old 14 questions this produces *prospectively
new question texts*, but targets and index still come from the **same
Constructor corpus**. It is not a new external-domain corpus or generated
Type-B answer correctness. **No novel question scores are claimed until the
separate author CSV is actually received and the three-phase evaluation runs.**
See [REPRODUCE §18](REPRODUCE.md).

## Prospective source quality blocker (22 October 2026)

The isolated question author returned all **36** preselected targets with
the specified first five fields preserved. **F023** (Ziegler–Biersack–Littmark
potential) and **F031** (crystal lattice matrix) have no supported scientific
question or source URL, because the associated listed 2025 review entitled
`Machine Learning Interatomic Potentials: A Review and Framework for
Understanding MLIPs` could not be independently verified as an authentic
primary paper or dated preprint. Independent discovery of related reviews is
**not** permission to silently replace that association.

The model's strict 36-query `--freeze` correctly rejected the first empty
question at F023; no original Gold/ranking manifest was produced. A newly
tested pre-ranking source screen now permits a separately versioned
**34/36 source-qualified subset** with two explicit exclusions, retaining the
original 36-case attempted denominator in
`pre_rank_source_screen.json`. This is a protocol-defined data-quality
exclusion **before any rankings**, not a result-selected improvement.
The other 34 URL/locator entries pass a form check, but full primary-paper
entailment remains unaudited by code. **No fresh Hit@5 result yet exists.**
See [REPRODUCE §18](REPRODUCE.md) for the safe original-file-preserving steps.

## Prospectively scored Type-A task: 36 attempted, 34 scored

The applicant has completed the new source-qualified **34-query** 2025-cutoff
retrieval experiment on the original Constructor corpus. Exactly two originally
sampled targets, **F023/F031**, were excluded for unverifiable associated
paper sources **before ranking**, not after observing results. The predeclared
four-root route achieved **Hit@5=2/34**, versus **3/34** for Flat, while
reducing online candidate+centroid dot products from **2,647 to 1,076.44
(59.3%)**. On 34 paired cases there were **0 route wins, 1 loss and 33
ties**. The bootstrap 95% exploratory CI for Route-4 minus Flat Hit@5 is
**[−0.0882,0]**, with descriptive exact sign **p=1.0**. The older 14-question
equal-Hit@5 finding **did not replicate** on these new question texts.

The same-corpus source index, author-visible targets, potential entity aliases
and incomplete independently checked primary evidence remain limitations.
New query text does not equal an external independent corpus. A checksum
and denominator audit of the user's locally frozen JSON files is now available
via `research_lab.fresh_score_audit` and **must still be run locally**
before publication of a safe aggregate. See [Evaluation](EVALUATION.md) and
[REPRODUCE](REPRODUCE.md).

## Optional high-capacity models are implemented but not evaluated

After seeing Flat Hit@5=3/34 and Route-4=2/34 on the original
same-corpus fresh-question score, a **different** advanced GPU
research method has been authored (BGE-M3 embedding, lexical RRF,
BGE reranking, native dated hyperedge co-mentions, soft root-aware
routing). It does not replace `native_temporal_20`; no neural
model scores are claimed until run. Any evaluation on the same
34 questions is exploratory *development*, not held-out evidence.
A new independently authored frozen query set will be required.

An actual Type-B response generator and AI answer-level grader
have also been implemented separately, but genuine historical
full-text passages, local GPU generation of four responses and
separately returned judgments are **still pending**. The existing
36 claim-source reviewer votes do not supply those metrics. Follow
[ADVANCED_GPU_AND_TYPE_B.md](ADVANCED_GPU_AND_TYPE_B.md).

## What is not finished — do not confuse software PASS with scientific PASS

1. **36 Type-B claims:** the original AI review (25 yes/1 no/10 unclear) is followed by a nine-case second AI recheck (seven yes/two unclear; one no→yes opinion change). This is a **post-hoc AI-only overlay**, not original-gold adjudication. Three Q17 source claims were explicitly judged nonresponsive to the coarse-grained MD/phase-transition question. All 36 claims' full task relevance and actual generated-answer correctness remain unmeasured.
2. **Fresh external or independently constructed Type-A/B tasks:** original 14+4 benchmark questions were inspected. New questions and gold must be authored/frozen **before** ranking; gold must not guide routing choice.
3. **Independent scientific label faithfulness:** a key-separated AI-only title/name vote is not verified full-paper semantic entailment. For an externally credible overclaim rate obtain determinate full-paper cases and retain `unclear` denominators.
4. **T6 end-to-end downstream gain:** 2/14 accuracy and high uncertainty do not establish superiority. The selected method is justified as a transparent stability/native-provenance trade-off.

## Clean release policy

- The evaluator should see **one canonical report** `report.pdf`, **one canonical metrics file** `metrics.json`, and selected hierarchy/temporal artifacts under `outputs_selected/`.
- `outputs/` is the *archived earlier baseline*, `research_outputs/` the immutable evidence registry, `research_lab/` research code, and `local_only/` is git-ignored private reviewers/backups. Keep these directories rather than deleting or renaming locked provenance.
- Any external reviewer CSV, blind allocation key, original source texts or claim notes stay in `local_only/`. Do not commit for "cleanliness".
- The supplemental scored AI-only reviews are **post-selection diagnostic evidence**, not an amendment to the original locked hypothesis test. Do not rewrite the recorded source-group confirmation or unqualifiedly advertise a full-score result.

## Next Windows command — sanitized local status

```powershell
cd C:\Users\a\Desktop\constructor-ckl-research
git pull --ff-only origin main
.\.venv\Scripts\python.exe -m unittest research_lab.test_assessment_status -v
.\.venv\Scripts\python.exe -m research_lab.assessment_status --project .
Get-Content .\local_only\review_status\summary.json
git status --short
```

A PASS from this last tool means **arithmetic/field checks only**. It neither verifies the identity or expertise of an AI reviewer nor scientifically adjudicates publication contents.


## First actual BGE GPU score and follow-up (22 October 2026)

Observed 22 October GPU result (34 already-inspected questions; post-hoc development only): BGE-M3 dense Hit@5=10/34 (29.41%, MRR@5=0.1887); new lexical=4/34, hybrid RRF=6/34, neural reranker=1/34, and reranker+soft root=1/34. Previous separately frozen Flat=3/34 and route4=2/34 remain unchanged. No improved independent-test accuracy, no Type-B generated-answer accuracy and no significant generalization claim.

The neural reranker severely degraded exact-entity retrieval. A read-only, SHA-verifying post-hoc diagnostic is implemented in research_lab/posthoc_retrieval_diagnostics.py. It examines all 34 source-qualified queries, Gold only after ranking verification, dense wins lost by fusion/reranking, known top-20 visibility, and fixed post-hoc score-free allocations. Candidate@64 recall cannot be reconstructed from top-20 exports; no new GPU run or model retuning occurred in this update.

To run (on Windows, from repo root):

    git pull --ff-only origin main
    .\.venv\Scripts\python.exe -m unittest research_lab.test_posthoc_retrieval_diagnostics -v
    .\.venv\Scripts\python.exe -m research_lab.posthoc_retrieval_diagnostics --project .

Read local_only/advanced_retrieval/posthoc_error_audit_LOCAL.json and preserve it under ignored local_only. It is an error analysis, NOT a held-out test. Freeze the selected dense-only approach before evaluating on separately authored new questions.

## Candidate-coverage-oriented multiview development implementation

The GPU error diagnostic showed Dense Top-20 visibility 14/34, with
seven dense Top-5 successes demoted but still in reranker Top-20,
three absent from the exported reranker Top-20 (unknown Top-64 status),
and a post-hoc fixed Dense-4+RRF-1 allocation giving 11/34.
A newly implemented, **not yet GPU-executed** independent multi-view
BGE module separates canonical entity name/type, dated source paper
titles, and previous native hyperedge co-mention context. It writes
gold-blind top-100 rankings for all arms, then scores exact-type
Hit@5/10/20/50/100 against the same already-seen 34 locally.
No paper abstracts are invented or added. This is next-step
development research only, not a replacement for the frozen model,
published metrics, or an independent generalization result.
See [GPU runbook](ADVANCED_GPU_AND_TYPE_B.md).


## Multi-View score and unscored Qwen exact-entity next experiment

BGE multi-view actually executed; 34 already inspected development
questions and frozen SHA
88f536d78e9e408f526d08bc079111cdd32db76ce13744b0f318c400341c13cd.
Hit@5: Context 10/34, Name 6/34, Paper 10/34, RRF 10/34
and Max Cosine 10/34. Candidate Top-20 reached 16/34 for RRF;
Top-100 reached 26/34 for RRF and Max Cosine. Embedding
multiple views did not improve the previously observed top-five.

The Qwen3 exact-entity reranking pipeline
research_lab/qwen_entity_rerank.py is implemented, gold-blind,
checkpointed and CI synthetic tests are added. It is **not run**,
and no new Hit@5 can be claimed. The 34 questions remain
POST-HOC DEVELOPMENT. A new independent full-text verified
question set is still required to support generalization.
See [Qwen GPU procedure](QWEN3_RERANK_RUNBOOK.md).


## Real 34-query multiview BGE score and candidate-pool diagnostic (23 October 2026)

The frozen gold-blind multiview artifact SHA is
\`88f536d78e9e408f526d08bc079111cdd32db76ce13744b0f318c400341c13cd\`.
Measured DEVELOPMENT Hit@5 counts: context 10, canonical name 6,
paper title 10, three-view RRF 10, max cosine 10 (out of 34).
RRF Top20=16, Top50=21, Top100=26; max cosine Top100=26.
The source-grounded multi-view method therefore improves candidate
visibility over the previous single-view BGE Top100 (unknown from
previous export), but does **not** improve top-five results on this sample.

A new read-only \`research_lab.multiview_source_union_audit\` uses
the existing scored ranks and immutable source ranking digest, and
does not open the original Gold. It measures true union-of-view
candidate presence versus oracle best-of-view ranks, and fixed
predeclared round-robin pool recall at 100/200/300. It has not yet
been run against the applicant's local scored files. **No
candidate-pool upper-bound is reported as model Hit@5**.

An optional Qwen3 entity-specific reranker already exists but has
not been run or benchmarked; a separate optional Qwen-compatible
sentence-transformers version is now pinned. New source-verified,
independently authored and SHA-frozen question cases remain
necessary for honest out-of-sample claims. Original selected
hierarchies, metrics, negative results and scientific report unchanged.
