# Scientific evidence, open limitations, and next actions
[← Main README](../README.md) · [Reproduce](REPRODUCE.md)

**Interpretation is deliberately conservative.** All quantitative claims below refer to the Constructor-supplied corpus, not a claim of novelty on unseen corpora.

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

## What cannot be repaired by rerunning the same model

1. **Semantic label correctness and overclaim.** A new, independent qualified reader must assess 24 paired V1/V2 A/B examples using `research_outputs/label_v2/BLIND_LABEL_COMPARISON_TO_FILL.csv`. The data are currently blank. The original 48 ratings were AI-assisted, non-blind development diagnostics.
2. **Type-B factual questions.** The Type-B two-stage retrieval experiment is **committed and verified** on `main`: 4 questions, 46 time-eligible papers, 3/5/10-paper source-coverage measures, 36 as-yet-unrated claim rubrics, a deterministic ranking fingerprint, and an exact-top-5 traversal audit. For the gold sources **actually found** in the eligible paper set, flat and routed-hierarchy Recall@5 are both **0.52083** (macro-average over four questions). Counting *all* listed gold sources, including unavailable matches, both score **0.31250**. This is paper-source retrieval only, NOT factual answer correctness. An actual qualified reader with authorized access to full texts must check passage entailment for 36 required claim statements; the missing sources and previously inspected questions mean this is exploratory.
3. **Independent out-of-sample validity.** One corpus and previously inspected questions do not yield generalization evidence. An additional dataset, newly collected ground truth or independent specialist checks would be needed. Never retroactively call examined questions a blind test.
4. **Temporal confidence and null interpretation.** Five seeds and a constrained 99-shuffle null are useful diagnostics but cannot claim proof of an optimal scientific partition. Preserve source-group held-out worsening and non-significant null.

## Human review protocol (do this AFTER freezing the current A/B worksheet)

**V2 labels:** Provide only the A/B worksheet to the reviewer, not the unblinding key or previous V1 judgments. Each row: rate A and B `accurate/vague/wrong`, then `yes/no/unclear` on unsupported gloss claims, include a reviewer identifier and evidence-based comments. If full-text sources are unavailable, choose `unclear`. Do not give the employer-provided materials to an external reviewer without permission to share them. Score paired wins/losses after all genuine reviews; disclose reviewer independence truthfully. Source keyword counts are **not** human scores.

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
- [x] Updated **three-page** vector-illustrated article, scientific Markdown companion, software/structural tests and 26-test CI suite.
- [x] Tested Type-B retrieval/source coverage outputs committed directly to `main` (`7db3e6e`); 25 software tests passed on the applicant's Windows machine.
- [x] AI-only 24-pair diagnostic mapped reproducibly to V1/V2; 36 Type-B rubric claims source-traced with explicit limits.
- [ ] Independent A/B label review and complete authorized Type-B claim-source entailment review, if available.
- [x] Typeset and publish updated 3-page journal-style `report.pdf` from `scripts/report.tex`; verify charts, negative results, and source-scope caveats.
- [ ] Incorporate *real independent* review ratings if obtained, with denominators and uncertainty.
- [ ] Confirm assessor can access the **private** repository or send a confidential ZIP. A URL alone is insufficient.

Prior unhelpful/duplicate how-to documents were removed from the current snapshot to keep navigation simple. Their original text remains retrievable from Git commit history.
