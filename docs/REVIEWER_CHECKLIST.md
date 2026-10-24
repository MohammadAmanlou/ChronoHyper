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


## Rubric-driven next research campaign (planned, not completed)

The assessment assigns **30% to trustworthy evaluation** and **25% to formal method design**. These must take priority over tuning another retrieval LLM on the same 34 already inspected queries.

| Priority | Experiment and control | Evidence needed to claim completion |
|---|---|---|
| P0 — 30% evaluation | Blind, source-grounded paper-passage review of sampled level-0/1 labels across 2020/2022/2024. Stratify by cluster size, type and abstention status; conceal algorithm, past ratings and keys. Compare against matched random/control groups. | Authentic pre-cutoff primary passages, evaluator identity, independent sufficiency flags, supported/vague/wrong/unclear counts, overclaim-rate numerator AND denominator, null comparison and intervals. Names/titles alone are insufficient. |
| P1 — 25% design | Freeze and compare semantic only, direct hypergraph only, joint native semantic+structure, temporal on/off, clique-projection and a faithful published method baseline at matched budgets. | Predeclared source split, method/seed hashes, event provenance, semantic/structure trade-off, held-out metrics and negative results; NEVER reselect the previously frozen model. |
| P2 — 15% time | Beyond global ARI, compare stable and changing source neighborhoods: retention, localized assignment churn, birth/split/merge/death identities, plus frozen-inertia control. | Three real time snapshots, transparent matching, denominator and CIs across seeds/edge deletion; discuss artificial stability and failure cases. |
| P3 — extrinsic | Write new primary-paper-grounded questions, lock answer references separately, predeclare Flat versus coarse-to-fine candidate budgets and optionally already frozen BGE/Qwen branches. | Exact paired Hit@5/MRR@5, candidate + centroid operations, latency, cost-quality Pareto and paired uncertainty on an untouched set. No gold-informed model selection. |
| P4 — delivery | Re-run verified P1/P2/P4 checks, evidence receipts, CI and a readable 3–5-page canonical report. | No broken reproduction links, no overwritten historical negative result, matching PDF/source, honest AI disclosure. |

**Stop rule:** a reranker is not an independent downstream success merely because its Hit@5 rises on reused development questions. The newly reported Qwen-vs-BGE matched outcome is **5 wins / 3 losses / 26 ties**, net +2/34, unadjusted descriptive p=0.7265625: **no significant improvement**. Original locked Flat 3/34 and Route-4 2/34 stay unchanged.

### Recent primary literature and what it does (not) justify

- Badalyan, Ruggeri & De Bacco, [Structure and inference in hypergraphs with node attributes (Nature Communications, 2024)](https://www.nature.com/articles/s41467-024-51388-5): higher-order structure + informative node attributes; combining these is prior art, not our novelty.
- Kaminski, Misiorek, Pralat & Theberge, [Modularity based community detection in hypergraphs (Journal of Complex Networks, 2024)](https://academic.oup.com/comnet/article/12/5/cnae041/7829128): h-Louvain and structural/graph interpolation, a potential controlled baseline, **not implemented here**.
- Gottesbüren et al., [Scalable High-Quality Hypergraph Partitioning (ACM ToA, 2024)](https://doi.org/10.1145/3626527): optimized multilevel native partitioning reference. Our local heuristic is NOT an Mt-KaHyPar implementation.
- Singh et al., [SciRepEval / SPECTER2 (EMNLP, 2023)](https://aclanthology.org/2023.emnlp-main.338/): a different scientific representation model can provide a secondary **evaluation proxy** on held-out abstracts, but paper-passage entailment still requires independent evidence.

**Candidate research extension, NOT yet an implemented or proven novel algorithm:** evidence-gated, temporally aligned native hyperedge coarsening with abstaining labels. Its plausible contribution is the tested **integration of source dating, native higher-order structure, hierarchy budgets, temporal identity and evidence-constrained labels**, not an unsupported claim to have invented structure/attribute mixing.


## Automatic open-access primary-paper evidence (preferred; no manual pasting)

**Prefer this to the historical manual worksheet procedure below.** The 28-paper
private library already contains original source links. The new automatic
retriever uses arXiv **version 1** where the source URL points to arXiv,
and OpenAlex-linked open-access PDFs for other papers, downloads only PDFs
locally, extracts text with explicit PDF pages, and retrieves passage windows
by the two blinded labels and sampled cluster member names. It does **not**
read Gold, unblind V2/V3, infer missing passages, or silently attribute recent
revisions to an earlier snapshot. Historical arXiv metadata must support a
date at/before the earliest associated snapshot; other PDF versions stay
explicitly **date-unverified**. Every candidate is tagged **unreviewed**.

Windows from the repository root:

~~~powershell
git pull --ff-only origin main
.\.venv\Scripts\python.exe -m pip install -r requirements_paper_auto.txt
.\.venv\Scripts\python.exe -m unittest research_lab.test_auto_primary_evidence research_lab.test_auto_label_judge -v

# No manual editing, default attempts all 28 linked source papers:
.\.venv\Scripts\python.exe -m research_lab.auto_primary_evidence --project .
~~~

Private files created (all ignored by Git):

- \`local_only/reviews/fulltext_label24/AUTO_PRIMARY_EVIDENCE_CANDIDATES.csv\` —
  machine-extracted paper passages with exact PDF page, DOI/arXiv URL,
  SHA-256, lexical match scores and strict evidence-status warnings.
- \`local_only/reviews/fulltext_label24/AUTO_EVIDENCE_STATUS.json\` —
  numbers obtained, missing source PDFs, unverified dates and
  machine-access errors; does **not** claim full-text scientific entailment.
- \`local_only/reviews/fulltext_label24/open_access_pdf_cache/\` —
  private original PDFs; do not commit or distribute copyrighted sources.

For testing, pass \`--limit 3\` **in a clean local-only directory** only
before your definitive full 28-paper run. The script refuses to overwrite
previous evidence output; archive any previous work explicitly first.

### Optional source-grounded AI-only reviewer, entirely local

If you already have [Ollama](https://ollama.com/) available on Windows and
have run \`ollama pull qwen3:8b\` to get a model, run:

~~~powershell
.\.venv\Scripts\python.exe -m research_lab.auto_label_judge --project . --model qwen3:8b
~~~

The script gives the model only *automatically retrieved, historically
dated arXiv v1 candidate passages*. It prompts the model to rate two
blinded label/gloss versions A and B, rejects invalid JSON grades,
abstains when the source/version is unverified, and never reads the
secret mapping or submits any data to an external service. It stores
\`AUTO_AI_DEVELOPMENT_REVIEW.csv\` and
\`AUTO_AI_REVIEW_SUMMARY.json\` under local_only. These are **AI-only
exploratory opinions**, not independent primary-paper expert
corroboration. For externally defensible scientific entailment, an
authorized separate reviewer still needs to inspect original primary
sources and the dated passages.

The legacy \`--assemble\` and \`--score\` commands below are the
**stricter human/independent evidence gate**; do not feed uninspected
automatic snippets into it as if they were user-verified full text.

## Primary-paper evidence review: executable next gate (24 blind label pairs)

**Code prepared and verified on the real corpus, not yet rated:** the new
\`research_lab.fulltext_label_audit\` generated 24 blind V2/V3 cases linked to
**92 case–paper incidences from 28 distinct, source-dated papers** in
GitHub's clean test. That verifies provenance linkage only; it does **not**
establish a single scientific overclaim judgment.

### On the applicant's Windows checkout

~~~powershell
cd C:\Users\a\Desktop\constructor-ckl-research
git pull --ff-only origin main
.\.venv\Scripts\python.exe -m unittest research_lab.test_fulltext_label_audit -v

# WARNING: do not regenerate a blind packet if you already have one:
if (-not (Test-Path ".\local_only\reviews\label_v3_fresh\blind_v2_v3_24.csv")) {
    .\.venv\Scripts\python.exe -m research_lab.label_v3_blind --project . --prepare
}

# Creates new EMPTY local-only source/intake files; preserves old outputs.
.\.venv\Scripts\python.exe -m research_lab.fulltext_label_audit --project . --prepare

# Source access/completeness without pretending paper semantics are checked:
.\.venv\Scripts\python.exe -m research_lab.fulltext_label_audit --project . --status
~~~

Recommended SINGLE worksheet to edit:
\`local_only/reviews/fulltext_label24/PRIMARY_PAPERS_TO_FILL.csv\`.
It contains **28 unique articles**, not 92 repeated case–paper rows.
Original \`paper_id\`, \`paper_title\` and \`paper_year\` are immutable.
For EACH article:

- Locate its genuine official journal/preprint page and **an original
  full-text version published no later than the case snapshot year**.
  Never substitute today's updated text if dated provenance is unknown.
- Enter \`source_url\`, \`source_version_date\` in \`YYYY-MM-DD\`,
  \`passage_locator\` (section/page) and a substantial **verbatim,
  legally accessible primary-text passage** in \`passage_text\`.
  Enter \`evidence_access=FULL_TEXT_USER_INSPECTED\` only after
  independently checking the source. The software validates format,
  paper IDs and cutoff; it **cannot verify passage authenticity online**.
- If a full paper cannot be accessed or dated, leave passage and link
  fields blank and use \`evidence_access=UNAVAILABLE\`. Do **not**
  fill a scientific answer from title or guessed abstract.
- Keep the alternative 92-row
  \`SOURCE_PASSAGES_TO_FILL.csv\` untouched when using the unique-paper
  library. Source passages automatically propagate to all eligible
  blinded cases for that paper. Do not edit both files.

When no \`UNFILLED\` rows remain, run:

~~~powershell
.\.venv\Scripts\python.exe -m research_lab.fulltext_label_audit --project . --status
.\.venv\Scripts\python.exe -m research_lab.fulltext_label_audit --project . --assemble
~~~

Output \`local_only/reviews/fulltext_label24/BLIND_FULLTEXT_LABEL24.csv\`
is the **key-free reviewer worksheet**, together with
\`JUDGE_INSTRUCTIONS.txt\`. Every case lacking inspected full text is
marked \`INSUFFICIENT_NO_FULLTEXT\`; reviewer must mark
\`evidence_sufficient_yes_no=no\`, no title grade and both overclaims
\`unclear\`. A case with passages can ALSO be deemed insufficient.
The reviewer must not see the private mapping, previous scores,
experiment name or outputs; authorized corpus-sharing permission and
actual evaluator independence are requirements, **not software facts**.

Only after a genuine independently completed 24-row reviewer CSV,
with original columns and case evidence unchanged, run:

~~~powershell
.\.venv\Scripts\python.exe -m research_lab.fulltext_label_audit --project . --score --ratings ".\local_only\reviews\fulltext_label24\COMPLETED_REVIEW.csv"
~~~

Private score: \`local_only/reviews/fulltext_label24/score_LOCAL_PRIVATE.json\`.
It computes **evaluable and unclear denominators**, per-version
overclaim rates with Wilson 95% intervals and descriptive paired title
wins/losses. No human/AI review is performed automatically, and no
confirmed scientific overclaim rate exists until the actual reviewer
response is validated. Never commit the filled passage library, answer
keys, blind packet or rated worksheets. The original flat/routed
retrieval, core model and publication remain untouched.

## Positioning relative to existing methods (no unverified novelty claim)

- **Zhou, Huang & Schölkopf (NeurIPS 2006)** established spectral learning directly on hypergraphs ([paper](https://papers.nips.cc/paper/2006/hash/dff8e9c2ac33381546d96deea9922999-Abstract.html)); merely using hyperedges is not a new idea.
- **Chakrabarti, Kumar & Tomkins (KDD 2006)** introduced evolutionary clustering; temporal inertia/matching alone is not new.
- **Schlag et al. (ACM JEA 2022), KaHyPar** describe multilevel high-quality native hypergraph partitioning ([DOI:10.1145/3529090](https://doi.org/10.1145/3529090)); ChronoHyper is not claiming a superior partitioning optimizer.
- **Kamiński et al. (2024), h-Louvain**, address direct hypergraph modularity with graph/hypergraph interpolation ([preprint](https://arxiv.org/abs/2406.17556)). Their setting differs from the non-overlapping, source-dated scientific-label+retrieval assessment here.

**Candidate positioning:** A traceable combination of *dated scientific evidence, native event-preserving coarsening, laminar visual budgets, persistent temporal IDs and abstaining provenance-linked labels*, rather than inventing a new foundational hypergraph objective. Its added value is a tested integrated workflow, not proof of state-of-the-art superiority. Independent semantic and downstream validation remain unproven.

## Predefined scientific decision rules

1. **No retroactive test conversion.** Existing 14 Type-A and 4 Type-B questions were inspected. New routing-budget scores on them are DEVELOPMENT diagnostics, even if measured after freezing rankings.
2. **Matched route/flat retrieval.** Both arms use the same dated candidate index, TF-IDF query, tie-breaking and top-5 metric. Route budgets **1, 2, 4, 8, 12** select root groups before scoring candidates. For all 12 roots, route output **must exactly equal flat top-5**; failure is a software error. Report candidate dot products including 12 centroid comparisons, quality by budget, and environment-specific timings. Ranking never reads gold.
3. **Blind label evaluation.** Preserve `local_only/reviews/label_v3_fresh/mapping_PRIVATE.csv`. The 24 V2/V3 comparisons use ONLY new 2020/22/24 cases relative to the old V1/V2 sheet, but originate from the same corpus. A real blind judge must see the case packet without a method key, previous scores or contaminated context. True scientific entailment additionally requires independent full-paper evidence, not merely surface names and paper titles. An authorized AI reviewer is acceptable; do not invent a human review.
4. **Evidence sufficiency.** Rate `unclear` where the visible primary passage cannot establish entailment; report both numerator and denominator. The 115/180 V3 abstentions (63.9%) are a **coverage/quality trade-off**, not a success rate or a V3 semantic improvement.
5. **Null model interpretation.** The pre-existing arity/degree-constrained shuffle gave `p=0.69` (not significant). A separate exploratory name/title AI contrast does not cancel this negative result. Label-claim counts 23/23 correct are *lexical source-count* accuracy only, not independent scientific factuality.
6. **Temporal confirmation.** Lower held-out cut is better. The 2024 mean moved from 0.6623 (development) to 0.7172 (confirmation): a worse cut of ~0.0549. Do not tune on confirmation or erase that gap.
7. **Type-B boundary.** Four prior Type-B retrieval queries gave equal flat and hierarchical available-gold source Recall@5 = 0.52083. No generated-answer correctness was graded and the full-text review of 36 claims remains pending.

## New measured development result (20 October 2026)

The applicant ran the historical retrieval frontier. On 14 previously inspected
Type-A questions, Route-4 and Flat each achieve Hit@5=2/14, while Route-4
uses mean 1,114.4 rather than 2,647 candidate+centroid dot products (57.9%
fewer); recorded online time falls from 7.768 to 6.133 ms on that machine.
This is a **source-controlled efficiency diagnostic**, NOT an independently
validated new-query accuracy or production speed-up. Paired Hit@5 differences
are exactly zero on the sample, which must NOT be taken as demonstrated
equivalence for unseen data.

The new all-180 V3 lexical evidence audit and clean-environment CI workflow
require successful actual runs before their status can be marked passed.
Independent blind scientific label correctness and Type-B answer entailment
remain substantive missing acceptance evidence. See
[Independent Validation](INDEPENDENT_VALIDATION.md).

## A concise live defense (anticipated questions)

**Why not clique expansion?** Plain unlabeled clique expansion conflates source event identities, arity, multiplicity and provenance. Show the native event record and the actual five-seed clique baseline. State that attaching all event identifiers to a pair graph could reconstruct this information: this is not a theorem that all pairwise encodings fail.

**Why is the coherence result trustworthy?** The model does **not** prove independent scientific semantic coherence. It uses separated source groups, alternative title evidence, constrained nulls, and discloses correlation and a non-significant null. A truly fresh full-paper or appropriately blinded source review remains the acceptance gate.

**What evidence is now fully audited?** The new source checker validates all 180 V3 lexical supporter sets, correct membership and publication cutoff evidence, but cannot evaluate unseen paper-level meaning. No overclaim-rate denominator is produced by it.

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
