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

## Next release checklist

- [x] Private repository, real input, pinned dependencies, 65+5+5 research-run registries.
- [x] Four selected hierarchical snapshots, temporal events, direct coarsening, robustness and null logs.
- [x] Current 4-page report and software/structural tests.
- [x] Tested Type-B retrieval/source coverage outputs committed directly to `main` (`7db3e6e`); 25 software tests passed on the applicant's Windows machine.
- [ ] Independent A/B label review and Type-B claim-source entailment review, if available.
- [ ] Summarize actual review ratings with denominators and uncertainty; update report PDF only if supported.
- [ ] Confirm assessor can access the **private** repository or send a confidential ZIP. A URL alone is insufficient.

Prior unhelpful/duplicate how-to documents were removed from the current snapshot to keep navigation simple. Their original text remains retrievable from Git commit history.
