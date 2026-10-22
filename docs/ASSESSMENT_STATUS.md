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
