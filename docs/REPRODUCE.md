# Reproduce — one runbook
[← Main README](../README.md) · [Scientific evidence](EVALUATION.md)

**Environment:** Windows PowerShell, Python 3.11, CPU only. Work exclusively from the repository root. Do not rename source files or rerun trained methods into canonical output folders.

## 1 · Install and audit current submission

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:OPENBLAS_NUM_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
git status --short
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m unittest research_lab.tests_lab research_lab.test_label_v2 research_lab.test_type_b_source_audit -v
.\.venv\Scripts\python.exe .\verify_selected_outputs.py --out outputs_selected
.\.venv\Scripts\python.exe .\final_preflight.py --project .
```

Expected **10 core + 15 research tests** and four structurally valid snapshots. The preflight deliberately reports scientific qualifications; do not misinterpret those as corrupt files. Check `git status --short` and preserve any local changes.

## 2 · Reproduce a new selected hierarchy WITHOUT model selection

```powershell
.\.venv\Scripts\python.exe .\export_locked_full_hierarchy.py `
  --lock research_outputs/model_lock.json `
  --confirmation research_outputs/confirmation `
  --seed 17 --out outputs_selected_reproduced --with-2025
.\.venv\Scripts\python.exe .\verify_selected_outputs.py --out outputs_selected_reproduced
```

This works from the **preselected** configuration and stored confirmation run. It does not prove an independent scientific evaluation.

## 3 · Inspect (do not overwrite) the full experiment registry

| Folder | Runs or outputs |
|---|---|
| `research_outputs/final_matrix/` | 13 × 5 = 65 development method runs, 2020/2022/2024 |
| `research_outputs/confirmation/` | Five prelocked runs on separated source-paper groups |
| `research_outputs/projection_5seed/` | Five clique baseline runs |
| `research_outputs/stress_temporal20_extended/` | 99 null shuffles and five deletions |
| `research_outputs/label_v2/` | V2 candidates for 2020/2022/2024 and an **unrated** 24-case A/B sheet |

The Type-B source-retrieval experiment has also **already been executed and committed** in `research_outputs/type_b_audit/`: four frozen paper rankings, gold-source scores, a blank 36-claim review sheet and a 2025 exact-search audit. The rankings were constructed without reading the reference answers and scored only after freezing. Paper-source coverage cannot establish generated answer correctness. The original complete expensive sweep has **already been executed and committed**. Do not spend time rerunning it merely to claim that a new local folder ran every seed. For optional full regeneration, read [the experiment protocol](RESEARCH_PROTOCOL.md) and choose *new* output paths.

## 4 · V2 label reproducibility and independent review options

```powershell
.\.venv\Scripts\python.exe -m research_lab.label_v2 --project . --out research_outputs/label_v2
```

Only `BLIND_LABEL_COMPARISON_TO_FILL.csv` goes to an independent reviewer. Keep `BLIND_KEY_KEEP_SEPARATE.json` on the local machine, excluded from Git; do not regenerate the sheet after ratings start. To score genuine completed ratings, run:

```powershell
.\.venv\Scripts\python.exe -m research_lab.label_v2 `
  --score-blind research_outputs/label_v2/BLIND_LABEL_COMPARISON_TO_FILL.csv `
  --key research_outputs/label_v2/BLIND_KEY_KEEP_SEPARATE.json `
  --out research_outputs/label_v2
```

If the key was lost and review A/B mapping cannot be recovered, do not guess the mapping or infer paired wins. Report the review as incomplete.

## 5 · Inspect the completed Type-B audit (no rerun needed)

The [Type-B source metrics](../research_outputs/type_b_audit/type_b_source_scores.json) compare flat vs four-route hierarchy on four previously inspected questions; source Recall@5 relative to eligible gold papers = 0.52083 for both, with no quality gain. The [exact-search control](../research_outputs/type_b_audit/certified_retrieval_audit.json) reports identical top-5 results for 18/18 queries and *slower* hierarchical traversal. Keep the 36 rows of [`CLAIM_LEVEL_REVIEW_BLANK.csv`](../research_outputs/type_b_audit/CLAIM_LEVEL_REVIEW_BLANK.csv) unrated until a genuine source-document reviewer checks them. **Do not run `scripts/run_t6_and_push_main.ps1` again to generate fake new evidence**; its initial pipeline has already finished and been pushed.

## 6 · Update figures/report if evidence changes

```powershell
.\.venv\Scripts\python.exe .\scripts\generate_selected_metrics.py
.\.venv\Scripts\python.exe .\scripts\make_report_figures.py
```

The 20 October V1/V2 and Type-B evidence now appears in the updated camera-ready [PDF](../report.pdf), typeset from [scripts/report.tex](../scripts/report.tex). Keep one canonical PDF filename; do not create version-suffixed reports. Retain original metrics and evidence stage labels. The legacy `outputs/` directory is the earlier model, **not** the locked selected output.

## 7 · Camera-ready report (already compiled and pushed)

The **3–5-page illustrated scientific article** is [`report.pdf`](../report.pdf). Its self-contained, auditable typesetting source is [`scripts/report.tex`](../scripts/report.tex); [`report.md`](../report.md) remains the plain-text companion. The PDF was built on GitHub Actions from that TeX source and automatically committed to `main`, after checking the 3–5 page requirement. **You do not need MiKTeX on your laptop to use or deliver the finished PDF.**

Only if you later change the scientific content and deliberately need to render a new PDF, use XeLaTeX in a working TeX environment:

```powershell
xelatex -interaction=nonstopmode -halt-on-error -output-directory=. .\scripts\report.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory=. .\scripts\report.tex
```

Always check page count, charts, equations and citations before committing the PDF; keep the existing filename `report.pdf`. Temporary root files (`report.aux`, `report.log`, etc.) are excluded by `.gitignore`. New data claims must be reconciled in both the manuscript source and `report.md`.

## 8 · Independent scientific validation — staged review protocol

These tasks remain distinct from the completed AI-only diagnostic. They require real reviewers or new data; the existing code must not synthesize human judgments.

**Stage 1 — 24 blind label pairs (qualified human optional; genuinely key-isolated LLM permitted).** Get permission before sharing Constructor-provided data outside its authorized team. Constructor permits an independent blind LLM/NLI judge as well as a human reviewer. If using AI, isolate its context and prompts from the private A/B mapping, prior ratings, label generation and evaluation results; use only authorized independent paper evidence and record the judge model/prompt. A second pass in the existing contaminated conversation is not independent. Do not re-run default `python -m research_lab.label_v2` into canonical outputs: it regenerates the blank sheet. In PowerShell from a clean, updated `main`:

```powershell
New-Item -ItemType Directory -Force .\local_only\reviews | Out-Null
Copy-Item .\research_outputs\label_v2\BLIND_LABEL_COMPARISON_TO_FILL.csv .\local_only\reviews\labels_for_reviewer.csv
.\.venv\Scripts\python.exe -m research_lab.label_v2 --project . --recover-key
```

The recovered A/B key is in `research_outputs/label_v2/BLIND_KEY_KEEP_SEPARATE.json`, ignored by Git. Never share it with the reviewer. The reviewer fills 24 pairs for both A/B title accuracy `accurate/vague/wrong`, gloss overclaim `yes/no/unclear`, actual `reviewer_id`, and comments grounded in available source text. Store their completed sheet locally as `local_only/reviews/labels_rated.csv` and score it:

```powershell
.\.venv\Scripts\python.exe -m research_lab.label_v2 --score-blind .\local_only\reviews\labels_rated.csv --key .\research_outputs\label_v2\BLIND_KEY_KEEP_SEPARATE.json --out .\local_only\reviews\scores
```

Read `local_only/reviews/scores/v2_paired_blind_scores.json`. The scorer reports only genuinely completed ratings; independence is a procedural fact, never software-certified.

**Stage 2 — 36 Type-B source claims.** Consult `research_outputs/type_b_audit/primary_source_audit.csv` (19 limited source excerpts, 17 rubric-only; no complete independent entailment assessment). Make the local working copy:

```powershell
Copy-Item .\research_outputs\type_b_audit\CLAIM_LEVEL_REVIEW_BLANK.csv .\local_only\reviews\claims_rated.csv
```

Review each of the 36 statements against the actual source full text and record publication date, URL/DOI, section/page/figure, exact evidence scope and contradictory passages in `reviewer_notes`. Fill `manual_claim_supported_yes_no_unclear`, `manual_source_citation_verified_yes_no_unclear`, and actual `human_reviewer`. With missing primary-text evidence mark `unclear`; do not interpret abstracts as full confirmation or post-Feb-2026 publications as contemporaneous evidence. Score only after genuine annotation:

```powershell
.\.venv\Scripts\python.exe -m research_lab.type_b_source_audit review --project . --review-file .\local_only\reviews\claims_rated.csv --out .\local_only\reviews\scores
```

Read `local_only/reviews/scores/type_b_claim_review_summary.json`. This is source-claim entailment **not generated-answer correctness**. Never edit the tracked blank review forms.

**Optional extension — actual Type-B answers.** The four original Type-B tasks (Q15–Q18) have **paper rankings only**, not generated answers. An answer-generation + claim/citation grading experiment still needs to be implemented. Freeze one authorized local generator/prompt/decoding budget; pass identical top-5/top-10 paper text excerpts from flat versus hierarchy without gold. Record exact passage IDs, cited final answers/abstentions, unsupported statements, claim recall, citation precision, actual time including routing, token count and costs. Judge blinded to retrieval arm. All 4 questions were previously inspected, hence results stay **exploratory**. Never upload private questions to an external API without permission.

**Optional extension — independent corpus.** Follow Option B in `docs/ASSIGNMENT_SOURCE.md`: collect ~300–500 dated 2019–2024 arXiv abstracts in one predeclared category, form 2020/2022/2024 snapshots and distinct-mention within-abstract **co-occurrence** hyperedges (not factual relations), with reproducible provenance. Keep old model-selection weights, budgets, baseline choices and seeds fixed. Pre-register disjoint papers/questions and new domain-expert reference judgments before inspecting model outputs. Evaluate held-out independent-signal coherence vs null, temporal and perturbation stability, label faithfulness, Type-A hits and Type-B source-grounded answers, with meaningful uncertainty. New corpus construction and answer-generation code **do not currently exist**; write them only after data and annotation permissions are settled.

**Final release after genuine T5/T6 evidence.** Once new actual evidence exists, update `docs/EVALUATION.md`, `report.md` and `scripts/report.tex`, rebuild only `report.pdf`, disclose AI usage and unverified residual claims, run tests and final preflight. Keep 65+5+5 archived runs, model lock and original gold fixed, and keep all secret keys and private reviews under ignored paths. Work only on `main`; do not create extra branches, READMEs or report copies.

## 9 · Fresh, *key-isolated* AI coherence protocol (do not reuse the previous 48 examples)

**Pre-registration:** `research_lab/blind_paper_eval.py` selects **24 previously unseen level-1 clusters**: 8 each from 2020, 2022 and 2024, excluding the 24 V1/V2 examples already inspected. It makes 24 new within-cluster 14-member samples and 24 year-, type- and size-matched mixtures from other clusters, with a fixed seed. All samples show original node names and at most eight time-eligible linked paper **titles**; no gold answer/question is accessed. This is a fresh blind LLM name+paper-title judgment, **not independent full-paper semantic entailment** and not a replacement for the negative arity/degree-preserving shuffle.

First, run in PowerShell:
```powershell
git switch main
git pull --ff-only origin main
.\.venv\Scripts\python.exe -m research_lab.blind_paper_eval --project . --prepare
git status --short
```
The only new files should be ignored under `local_only/reviews/fresh_semantic/`: `blind_review_48.csv`, **`condition_key_PRIVATE.csv`**, and `JUDGE_INSTRUCTIONS.txt`. **Never submit, upload or send the key**; do not push private rated forms to GitHub. Do not use this same ChatGPT project or a model with knowledge of the previous keys to rate the blind file.

**External AI/data-sharing gate:** The employer-provided corpus is private. Get explicit authority for sending member names/paper links outside approved infrastructure before giving `blind_review_48.csv` to ChatGPT or any external API. Otherwise use an authorized isolated/local model. Choose a fresh model session with no prior case/condition exposure and disable cross-chat memory/project attachments as appropriate. Only the blind CSV and `JUDGE_INSTRUCTIONS.txt` should be visible to that evaluator. It must return the same 48 IDs and all original evidence columns, plus `coherence_score_1_to_5` (1–5 for enough evidence), `evidence_sufficient_yes_no`, a truthful model identifier and row-specific evidence notes. Record the exact model name, prompt and data permission in AI_USAGE.

Once the rated CSV has been saved locally, for example as `local_only/reviews/fresh_semantic/ratings_fresh_48.csv`, score it:
```powershell
.\.venv\Scripts\python.exe -m research_lab.blind_paper_eval --project . --score --ratings .\local_only\reviews\fresh_semantic\ratings_fresh_48.csv
Get-Content .\local_only\reviews\fresh_semantic\score_summary.json
git status --short
```
The scorer rejects modified original case content, missing ratings, forged control columns and mismatched IDs. It excludes insufficient-evidence **pairs**; reports paired difference, exact descriptive sign test, year-specific performance and a paired bootstrap interval. Treat the judge's self-reported isolation as a procedural claim, not machine-verified independence. A high real-vs-mixed score cannot erase the preserved constrained structural null `p=0.69` or establish scientific title entailment from full papers.

**Do not treat any AI response in the existing ChronoHyper conversation as a fresh blind rating:** this conversation has seen partial keys and previous scores. If permission for a genuinely isolated model/evidence is unavailable, preserve `P3/P6` as unconfirmed rather than manufacturing ratings.

## 11 · True subset-scored retrieval diagnostic and later fresh evaluation

The new `research_lab.retrieval_v2` scorer uses one shared candidate representation, normalized type/name aliases, names and dated article titles. It routes by centroid **before scoring candidate rows**, and logs centroid comparisons and wall-clock cost. Run once on historical questions (development only; old gold not read):
```powershell
.\.venv\Scripts\python.exe -m research_lab.retrieval_v2 --project . --rank
```
Output `local_only/retrieval_v2/rankings.json`. Preserve it.

To claim an independent extrinsic improvement later, have an authorized *separate source* supply fresh benchmark questions `question_id,question,type` and scientifically checked answer keys `question_id,expected_methods` with references separated before rankings are seen; never include the answer keys in model input. Then:
```powershell
.\.venv\Scripts\python.exe -m research_lab.retrieval_v2 --project . --rank --questions .\local_only\retrieval_v2\new_questions.csv --rankings .\local_only\retrieval_v2\fresh_rankings.json
.\.venv\Scripts\python.exe -m research_lab.retrieval_v2 --project . --score --rankings .\local_only\retrieval_v2\fresh_rankings.json --references .\local_only\retrieval_v2\new_gold_PRIVATE.csv --out .\local_only\retrieval_v2\fresh_score.json
```

## 12 · Safe Windows sync when generated untracked files block git pull

This protects the user's privately generated `research_outputs/fresh_semantic/` (usually a JSON and PDF) by **moving, not deleting**, the untracked directory into `local_only/` before merging. Run from the PROJECT ROOT, not from `local_only/reviews`:

```powershell
cd C:\Users\a\Desktop\constructor-ckl-research
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
New-Item -ItemType Directory -Force .\local_only\saved_artifacts | Out-Null
if (Test-Path .\research_outputs\fresh_semantic) {
  Move-Item -LiteralPath .\research_outputs\fresh_semantic -Destination ".\local_only\saved_artifacts\fresh_semantic_$stamp"
}
git status --short
git pull --ff-only origin main
git log -1 --oneline
git status --short
```

DO NOT delete `ratings_fresh_48.csv`, `condition_key_PRIVATE.csv`, `data.zip`, `model_lock.json` or any tracked research output. `local_only/` is ignored by Git. Running `Get-Content` on a directory raises an error; use `Get-ChildItem` to list folders. The scientific warnings in `final_preflight.py` describe **unresolved validity limits** and must not be suppressed. Avoid publishing a private review sheet to a service without Constructor's explicit authorization.

**Safe aggregate export defaults:** `research_lab.blind_paper_eval --publish-limited` now writes to `local_only/exports/fresh_semantic`; it no longer creates untracked files under a path Git later tracks. Historical aggregate and presentation-only vector SVG are already stored in the canonical `research_outputs/fresh_semantic/`.

## 13 · Experimental V3/V2 blind label audit (NEW, no ratings yet)

To evaluate the GENERAL deterministic 180-case V3 rule against frozen V2 on **24 distinct title-review cases**, generate a locally blinded 8-per-year A/B packet (original 24 V1/V2 title-review cases excluded). This is a **development review** and uses only sampled names and source-paper titles, not full original article evidence; full-paper semantic entailment remains unknown.

```powershell
cd C:\Users\a\Desktop\constructor-ckl-research
.\.venv\Scripts\python.exe -m research_lab.label_v3_blind --project . --prepare
Get-ChildItem .\local_only\reviews\label_v3_fresh
```

Keep the ignored `mapping_PRIVATE.csv` **private**. An externally hosted blind AI must only see `blind_v2_v3_24.csv` and `JUDGE_INSTRUCTIONS.txt` **if sharing Constructor data is explicitly permitted**. Otherwise use a separately isolated authorized local evaluator. A model previously exposed to this project's cases or hidden keys is not strictly independent. No ratings are fabricated.

After a real 24-row UTF-8 rated CSV comes back, save it to `local_only/reviews/label_v3_fresh/rated_24.csv` and run:

```powershell
.\.venv\Scripts\python.exe -m research_lab.label_v3_blind --project . --score --ratings .\local_only\reviews\label_v3_fresh\rated_24.csv
Get-Content .\local_only\reviews\label_v3_fresh\result_LOCAL.json
```

Scoring rejects changed source columns, duplicate IDs and fabricated missing-evidence certainty. The result is labelled AI-only and developmental, so strong V3 results on this same packet cannot certify scientific faithfulness elsewhere.

## 14 · Retrieval budget frontier — gold-separated and exactness-checked (20 October)

After a safe `git pull --ff-only origin main`, run from the project root:

```powershell
.\.venv\Scripts\python.exe -m unittest research_lab.test_retrieval_frontier -v
.\.venv\Scripts\python.exe -m research_lab.retrieval_frontier --project . --rank
Get-ChildItem .\local_only\retrieval_frontier
```

This runs the historical 18 questions (14 Type-A and four Type-B): **no gold is accessed**.
The common node/type/name index, TF-IDF scorer and deterministic tie breaker are
identical for flat and routes with top 1, 2, 4, 8 and 12 roots. Twelve-root top-5
**must exactly match** flat; this is enforced per query. Candidate comparisons
and centroid comparisons are separately counted. Timings include online routing
and top-5, but exclude shared query construction and offline indexing. Differences
in raw milliseconds are environment-dependent. Store the resulting
`local_only/retrieval_frontier/rankings.json` privately.

If independently prepared gold is available as a *separate* UTF-8 CSV with
`question_id,expected_methods` columns (pipe-separated method names),
score **after** ranking:

```powershell
.\.venv\Scripts\python.exe -m research_lab.retrieval_frontier --project . --score --references .\local_only\retrieval_frontier\gold_PRIVATE.csv
Get-Content .\local_only\retrieval_frontier\score.json
```

Do not create or tune reference methods from the produced ranking. Historical
original questions **remain development-only** even when scored after the fact.
Absent new independently sourced questions and scientifically verified gold,
quality improvement/generalization is not established. For short examiner-facing
evidence boundaries, see [reviewer checklist](REVIEWER_CHECKLIST.md).


## 15 · Historical Type-A quality–cost curve (20 October 2026)

**Purpose:** Fill the previously missing quality axis of the route-budget frontier
without silently using answers to choose a ranking. The original 14 Type-A and
four Type-B questions were already inspected. This is **historical development
diagnosis**, not an unseen benchmark.

Run from the project root in PowerShell (two strictly ordered stages):


```powershell
# Stage A: rank; DOES NOT open original ground_truth.json.
.\.venv\Scripts\python.exe -m research_lab.frontier_historical --project . --prepare

# Stage B: verify frozen ranking digest; only THEN open original gold.
.\.venv\Scripts\python.exe -m research_lab.frontier_historical --project . --evaluate

# Short numerical review, without printing private question/answer text:
.\.venv\Scripts\python.exe -c "import json; a=json.load(open('local_only/retrieval_frontier/historical_v2/historical_audit.json')); print(json.dumps(a['quality_measures'],indent=2)); print(json.dumps(a['paired_hit_at_5_contrasts'],indent=2))"

Get-ChildItem .\local_only\retrieval_frontier\historical_v2
```


The same stages run in the updated one-command local validation script. The
five output files (all ignored by Git) are:

- `rankings.json`: unchanged ranked lists for 18 questions, checksum frozen before gold
- `historical_gold_PRIVATE.csv`: original Type-A reference methods, do not share
- `raw_score_PRIVATE.json`: shared-scorer reference-only diagnostic
- `historical_audit.json`: paired Hit@5, all/eligible recall, 14-question bootstrap intervals, exact sign tests, candidate + centroid dot-products and local online timings
- `historical_quality_cost.svg`: vector chart for historical quality versus computation

A checksum protects against *accidental* ranking edits, not malicious
replacement. Results cannot be used to retune the locked model and later
declared fresh. No Type-B generated answers or full-text scientific judgments
have been produced. The scorer retains prior artifacts instead of overwriting
them; new runs require a separate folder. The generic older local frontier file
may lack a checksum; historical_v2 generates its own frozen rank artifact.

The final hand-in report and locked experiment outputs remain unchanged
until the candidate actually verifies the new results and makes an evidence-based
report revision. See the [Reviewer Checklist](REVIEWER_CHECKLIST.md).

## 16 · Exhaustive developmental V3 source-provenance audit

After `git pull --ff-only origin main`, run from Windows PowerShell root:

```powershell
.\.venv\Scripts\python.exe -m unittest research_lab.test_v3_provenance_audit -v
.\.venv\Scripts\python.exe -m research_lab.v3_provenance_audit --project .
Get-Content .\local_only\label_v3_dev\provenance_audit.json
git status --short
```

The updated `scripts/continue_local_validation.ps1` also runs these steps.
This audit reads the original frozen source ZIP and verifies **all 180**
2020/2022/2024 level 0/1 V3 outputs, not selected examples. It checks that
cluster IDs/members match the locked hierarchies; cited name phrases are found
in *every listed original supporter*; no eligible supporter is omitted;
source article IDs exist and satisfy the cutoff; and the V3 text matches the
general deterministic rule. It does not use reference answers, modify
locked outputs, or claim full-paper semantic entailment.

Successful completion produces a local JSON file with source checks and
`independent_semantic_label_accuracy: null` / `scientific_overclaim_rate: null`.
Treat those `null` fields as **scientifically unmeasured**, not software
failures and not 0% error. Never replace independently blind ratings with
this audit. For the approved independent-review process, see
[INDEPENDENT_VALIDATION.md](INDEPENDENT_VALIDATION.md).

A clean Python 3.11 test job is defined in
[GitHub Actions](../.github/workflows/scientific-integrity.yml).
Verify its actual run status under the repository Actions tab; a workflow
file existing does not imply GitHub Actions has executed successfully.

## 17 · Auditing returned AI-only review summaries

The applicant's `rated_24.csv` and `ratings_fresh_48_independent.csv`
were returned and scored locally on 20 October. No original blind mapping keys
or raw responses should be committed to the repository.

```powershell
cd C:\Users\a\Desktop\constructor-ckl-research
.\.venv\Scripts\python.exe -m unittest research_lab.test_assessment_status -v
.\.venv\Scripts\python.exe -m research_lab.assessment_status --project .
Get-Content .\local_only\review_status\summary.json
.\.venv\Scripts\python.exe final_preflight.py --project . --write .\local_only\final_preflight.json
git status --short
```

This conservative reviewer audit checks paired-count arithmetic, review
CSV hash for the 24 labels, insufficiency denominators, and scientific-claim
flags. It does **not** test human/AI reviewer independence or full-text meaning.
See [ASSESSMENT_STATUS.md](ASSESSMENT_STATUS.md).

The 36-row Type-B form `local_only/reviews/claims_rated.csv` is still a **blank
working copy** until a licensed full-text assessor records actual notes,
supports/contradictions and source passages. Do not run the Type-B review
scorer as if it were completed. For another genuine external task evaluation,
all new questions/references must be frozen before any ranking is inspected.


## 18 · Prospective, stratified new-question retrieval test (22 October)

**Scientific role:** A new set of *question texts* on the **existing Constructor
corpus**, with Gold frozen **before ranking**. This is stronger than rerunning the
old inspected 14 Type-A queries, but it is **NOT a separate source corpus** or
external-domain generalization experiment. The question author sees a target
entity and one original source title; authorship independence and full-text
entailment cannot be proved automatically. There is **no Type-B answer
generation** in this study.

### Stage A: deterministic author packet (no model predictions)

From Windows PowerShell at repository root:


```powershell
git pull --ff-only origin main
.\.venv\Scripts\python.exe -m unittest research_lab.test_fresh_retrieval -v
.\.venv\Scripts\python.exe -m research_lab.fresh_retrieval --project . --author-kit
explorer .\local_only\fresh_retrieval

```


This samples **3 source-dated target entities per 2025 root group** using a
deterministic SHA-256 ordering (typically 12 groups / **36 targets**), with
source paper titles and recorded years **at or before 2025**. The author
packet \`AUTHOR_KIT.csv\` has five fields:
\`question_id,target_name,target_type,paper_title,paper_year\`.
Do not change targets, root allocation, or filter out difficult items based on
model results. Sampling intentionally covers the locked hierarchy but does not
create a representative estimate of all real-life query frequencies.

### Stage B: isolated question writing BEFORE retrieval

Give only \`AUTHOR_KIT.csv\` to a new **authorized, key/model-result-isolated**
chat that can inspect dated primary papers. Require **all** target rows in one
UTF-8 CSV with the exact twelve columns, in order:

\`question_id,target_name,target_type,paper_title,paper_year,question,source_url,evidence_locator,evidence_access,author_id,question_rationale\`.

An acceptable question:
- A natural, specific 55–450-character English question ending in \`?\`
  and **not including the exact target name**, with an independently checked
  primary paper URL and specific section/page/passage locator.
- A realistic paraphrase of a concept discussed by the given paper, rather
  than a copy of the old benchmark question or an artificial identifier.
- The supplied first five columns unchanged. \`evidence_access\` must be
  \`FULL_TEXT\` or \`ABSTRACT_ONLY\`; the latter is **weaker** and must not
  be presented as independent full-paper entailment. The \`author_id\` is the
  true AI model identifier.
- When a primary source is unavailable, the reviewer must report that
  limitation rather than inventing a URL/section. **Do not generate substitutes
  or quietly remove targets to force 36 passable rows.** Such rows remain an
  unresolved benchmark-preparation gate.

Save the actual reviewer-created CSV as
\`local_only/fresh_retrieval/FRESH_QUESTIONS_FROM_AI.csv\`.

### Stage C: freeze question and reference files *before* evaluation


```powershell
.\.venv\Scripts\python.exe -m research_lab.fresh_retrieval --project . --freeze --response .\local_only\fresh_retrieval\FRESH_QUESTIONS_FROM_AI.csv

Get-Content .\local_only\fresh_retrieval\freeze_manifest.json

```


The module rejects duplicate/modified target IDs, evidence entries without
sources, query text that directly names its target, near-duplicates of old
questions and unqualified references. It then writes **exactly once**:
\`REVIEWED_QUESTIONS.csv\`, \`queries_only.csv\`, \`gold_PRIVATE.csv\`, and
\`freeze_manifest.json\` with separate content hashes. These files stay
**git-ignored**. Critically, all gold must already be frozen before running
\`--rank\` (never edit the output manifest or manually replace data afterward).
Code cannot attest that a link supports the whole query; manually audit
source passages and date/version restrictions.

### Stage D: rank with no Gold and then score


```powershell
.\.venv\Scripts\python.exe -m research_lab.fresh_retrieval --project . --rank

# Only after the ranking file and digest exist:
.\.venv\Scripts\python.exe -m research_lab.fresh_retrieval --project . --score

.\.venv\Scripts\python.exe -c "import json; x=json.load(open('local_only/fresh_retrieval/scored.json')); print('n=',x['n_queries']); print('flat=',x['per_arm']['flat']); print('route4=',x['per_arm']['route_4']); print('paired=',x['descriptive_paired_contrasts']['route_4'])"
git status --short

```


The scorer enforces an *exact set match* between frozen query IDs and Gold
IDs: **no dropping unanswered questions**. The target type and exact
normalized entity name must both match a returned top-5 entry, preventing a
different type with the same spelling from counting as a hit. The primary
comparison is **predeclared four-root vs Flat**, with Hit@5, MRR@5 and online
candidate+centroid dot products; other budgets are exploratory. It reports a
paired question-level bootstrap CI and the per-query hits, but no causal
speed-up or significance guarantee. The all-12-root control must reproduce
flat. Rankings, Gold, author response and results remain under ignored
\`local_only/fresh_retrieval/\`. A successful CI *author-kit smoke test* shows
that the code can select targets; it is **not** proof 36 scientific questions
have been independently written, sourced or evaluated.

The procedure refuses to overwrite previously frozen artifacts. For a genuinely
new version, preserve the old directory and specify a **different** \`--directory\`
from the first step onward. Do not retune the locked model, cutoff, or
predeclared primary route budget after reading score results.


### Correction for an isolated source-unsupported author response (22 October, F023/F031)

The first external author returned **all 36 original targets/fields**, but
\`F023\` and \`F031\` have **no question or source URL** because the exact
associated 2025 review title could not be authenticated. Do **not** invent a
source, silently substitute an unrelated review, delete the original rows,
rerandomize the 36 targets, or force the main strict \`--freeze\` to pass.

If the candidate cannot establish the **original listed paper's** existence,
use the source-failure protocol **before any retrieval ranking**:

\`\`\`powershell
cd C:\Users\a\Desktop\constructor-ckl-research
git pull --ff-only origin main
.\.venv\Scripts\python.exe -m unittest research_lab.test_screen_fresh_questions -v

# Prints errors for ALL 36 and identifies explicitly unsupported sources.
.\.venv\Scripts\python.exe -m research_lab.screen_fresh_questions --project . --inspect

# Do this ONLY if n_eligible_format=34, n_documented_excluded=2,
# validation_errors=[] and the two exclusions are F023 and F031.
.\.venv\Scripts\python.exe -m research_lab.screen_fresh_questions --project . --stage

# This is a NEW source-screened experiment folder. The original 36-row
# author kit, reviewer file and all evidence remain untouched.
.\.venv\Scripts\python.exe -m research_lab.fresh_retrieval --project . --directory .\local_only\fresh_retrieval_screened34 --freeze --response .\local_only\fresh_retrieval_screened34\FRESH_QUESTIONS_FROM_AI.csv

# Rank only after freeze; gold is not read or used by the rank step.
.\.venv\Scripts\python.exe -m research_lab.fresh_retrieval --project . --directory .\local_only\fresh_retrieval_screened34 --rank
.\.venv\Scripts\python.exe -m research_lab.fresh_retrieval --project . --directory .\local_only\fresh_retrieval_screened34 --score
.\.venv\Scripts\python.exe -c "import json; p='local_only/fresh_retrieval_screened34/scored.json'; x=json.load(open(p)); print('Scored questions:',x['n_queries']); print('Flat:',x['per_arm']['flat']); print('Four-root:',x['per_arm']['route_4']); print('Paired:',x['descriptive_paired_contrasts']['route_4'])"
\`\`\`

The \`pre_rank_source_screen.json\` in the screened experiment permanently
records all **36 originally sampled targets** plus why **two were excluded
before model output was visible**. The scored denominator is **34**, *never*
36, and even a source-coverage failure is an important dataset-quality
finding. The two excluded items' original associated scientific review was
**not** authenticated, so this fallback does not establish ground truth for
those two. A source review could later justify a *new separately versioned*
36-item study, without retroactively replacing the original screened result.

The CLI structurally checks links, paper cutoff, original fields, answer-name
leakage and old-question similarity; the code cannot itself guarantee that a
paper passage scientifically entails each of the other 34 questions. The
source-verification problem remains explicitly disclosed in reporting.

**Improved gold isolation:** ranking verifies the precommitted question,
author-response and kit hashes, **not the private gold file**. The score
stage reads and verifies Gold only after \`rankings.json\` exists with its
rank SHA-256.
