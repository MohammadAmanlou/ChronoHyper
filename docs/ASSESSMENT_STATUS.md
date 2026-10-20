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

## What is not finished — do not confuse software PASS with scientific PASS

1. **36 Type-B claims:** `local_only/reviews/claims_rated.csv` was created by copying a blank sheet; no verified actual claim-by-claim full-paper judgements have been reported. Mark unknown support `unclear`; citations alone are insufficient. Source claim checks are distinct from generated-answer correctness.
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
