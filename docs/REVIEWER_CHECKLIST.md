# Constructor CKL — reviewer evidence and acceptance gates

This is a **review aid**, not an extra manuscript or a claim of acceptance. The canonical
hand-in is the 3–5-page `report.pdf` plus the repository outputs. All private
materials remain authorized-user-only. Original locked artifacts stay unchanged.

## Assignment-weighted rubric (from docs/ASSIGNMENT_SOURCE.md)

| Weight | Requirement | Current defensible evidence | Outstanding / prohibited overclaim |
|---:|---|---|---|
| 25% | Formal objective, semantics–structure trade-off, direct hypergraph construction, complexity and guarantees | `scripts/report.tex`, `src/core.py`, locked `native_temporal_20`, 13 development variants | Objective is a *local heuristic surrogate*, not a proven global optimum; semantic meaning not guaranteed by construction |
| 30% | Non-circular coherence with nulls; CI/stability; label faithfulness; matched extrinsic task | 99 degree/arity constrained shuffles; paired source-group confirmation; five perturbations; exploratory Type-A and Type-B; V1/V2 and V3 diagnostic forms; `research_lab/retrieval_frontier.py` | **Highest-priority gate:** unrelated full-paper/expert or authorized key-isolated judge for independent semantic labels, plus fresh task references; reused queries and AI-assessed names do not establish external utility |
| 15% | Actual temporal snapshots, stable ID matching, births/merges/splits/deaths | 2020/22/24 + exploratory 2025; `outputs_selected/temporal_events.json`; perturbed refits | Similarity of old IDs can inflate stability; event interpretations are heuristic |
| 10% | Native hyperedge coarsening implemented and audited | `outputs_selected/collapsed_edges_*`, multiplicity and provenance checks; 1429 native events | Clique projection *loses untyped event provenance*, but representation-loss counts do not prove predictive improvement |
| 10% | Reproducibility | lock, 65 development + 5 confirmation + 5 clique jobs, pinned requirements, source hashes, verifier, tests | Validate on applicant's actual machine; do not call synthetically tested code a reproduced original-corpus result |
| 10% | Clear 3–5-page paper with genuine AI disclosure | `report.pdf`, `scripts/report.tex`, `AI_USAGE.md` | Check PDF pagination, formula/figure legibility, consistency with `report.md` and recipient access |

## Predefined scientific decision rules

1. **No retroactive test conversion.** Existing 14 Type-A and 4 Type-B questions were inspected. New routing-budget scores on them are DEVELOPMENT diagnostics, even if measured after freezing rankings.
2. **Matched route/flat retrieval.** Both arms use the same dated candidate index, TF-IDF query, tie-breaking and top-5 metric. Route budgets **1, 2, 4, 8, 12** select root groups before scoring candidates. For all 12 roots, route output **must exactly equal flat top-5**; failure is a software error. Report candidate dot products including 12 centroid comparisons, quality by budget, and environment-specific timings. Ranking never reads gold.
3. **Blind label evaluation.** Preserve `local_only/reviews/label_v3_fresh/mapping_PRIVATE.csv`. The 24 V2/V3 comparisons use ONLY new 2020/22/24 cases relative to the old V1/V2 sheet, but originate from the same corpus. A real blind judge must see the case packet without a method key, previous scores or contaminated context. True scientific entailment additionally requires independent full-paper evidence, not merely surface names and paper titles. An authorized AI reviewer is acceptable; do not invent a human review.
4. **Evidence sufficiency.** Rate `unclear` where the visible primary passage cannot establish entailment; report both numerator and denominator. The 115/180 V3 abstentions (63.9%) are a **coverage/quality trade-off**, not a success rate or a V3 semantic improvement.
5. **Null model interpretation.** The pre-existing arity/degree-constrained shuffle gave `p=0.69` (not significant). A separate exploratory name/title AI contrast does not cancel this negative result. Label-claim counts 23/23 correct are *lexical source-count* accuracy only, not independent scientific factuality.
6. **Temporal confirmation.** Lower held-out cut is better. The 2024 mean moved from 0.6623 (development) to 0.7172 (confirmation): a worse cut of ~0.0549. Do not tune on confirmation or erase that gap.
7. **Type-B boundary.** Four prior Type-B retrieval queries gave equal flat and hierarchical available-gold source Recall@5 = 0.52083. No generated-answer correctness was graded and the full-text review of 36 claims remains pending.

## A concise live defense (anticipated questions)

**Why not clique expansion?** Plain unlabeled clique expansion conflates source event identities, arity, multiplicity and provenance. Show the native event record and the actual five-seed clique baseline. State that attaching all event identifiers to a pair graph could reconstruct this information: this is not a theorem that all pairwise encodings fail.

**Why is the coherence result trustworthy?** The model does **not** prove independent scientific semantic coherence. It uses separated source groups, alternative title evidence, constrained nulls, and discloses correlation and a non-significant null. A truly fresh full-paper or appropriately blinded source review remains the acceptance gate.

**What prevents label hallucinations?** Name-phrase evidence, dated source counts, limited claim types, deterministic V3 abstention and an explicitly unmeasured full-paper overclaim rate. Absent articles are not interpreted as confirming scientific content.

**Does routing beat flat retrieval?** Do not assume so. The original pilot hit-rate was 2/14 routed vs 1/14 flat; the common-index revised development check is 2/14 for both. The budget-frontier script measures the cost/quality curve and enforces an all-roots exactness control. Even if it reduces candidate operations, neither speedup nor improved hit-rate generalizes without independent tests.

**What would you do with four additional weeks?** Collect authorization and independent paper passages; preregister fresh queries/reference judgments; run a blinded semantic-faithfulness evaluation with adjudication; compare uncertainty across matched retrieval budgets, year subsets and seeds; characterize temporal-drift failure cases. Preserve both positive and negative findings.

## Actions that are NOT automatable from this repository

- External data-sharing permission, actual independent judge isolation and original-paper entailment.
- An assessor's acceptance or a private-repository collaborator invitation.
- Confirming actual email submission. The formerly discussed 19 October 2026 target date has passed; verify hand-in status directly.
- Author approval of the final PDF. Never overwrite canonical `report.pdf` from an unreviewed edit.

## Commands from Windows PowerShell (repository root)

```powershell
git status --short
.\.venv\Scripts\python.exe -m unittest research_lab.test_retrieval_frontier -v
.\.venv\Scripts\python.exe -m research_lab.retrieval_frontier --project . --rank
Get-Content .\local_only\retrieval_frontier\rankings.json | Select-Object -First 35
.\.venv\Scripts\python.exe final_preflight.py --project . --write .\local_only\final_preflight.json
```

After a genuinely separate file with columns `question_id,expected_methods` exists:

```powershell
.\.venv\Scripts\python.exe -m research_lab.retrieval_frontier --project . --score --references .\local_only\retrieval_frontier\gold_PRIVATE.csv
Get-Content .\local_only\retrieval_frontier\score.json
```

Do not create dummy gold just to populate a graph; if no authorized independent
reference list is ready, leave the score pending. Keep raw reviewer forms and keys
under ignored `local_only/`; do not upload them with the assessment.
