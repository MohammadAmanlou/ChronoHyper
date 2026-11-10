# Local paper intake: safe, repeatable, no clipboard

The user personally inspects the exact dated PDF and copies an authentic paper
paragraph to a UTF-8 plain-text file. The generic recorder:
- reads ONLY that local TXT file and the already prepared local source intake;
- never opens benchmark Gold or private A/B mapping;
- previews before saving;
- rejects obvious PowerShell snippets, short passages, edited paper rows and future-dated sources;
- makes a timestamped backup and atomically updates ONLY the original paper ID;
- never claims that the article establishes scientific cluster-label correctness.

## Next example: 5452

The primary public archive https://arxiv.org/abs/1506.00303v1 identifies
paper 5452 (frozen catalog title missing) as "The AFLOW Standard for
High-Throughput Materials Science Calculations", first submitted 2015-05-31.
The previous auto candidate library identifies this v1 date as cutoff-eligible.
DO NOT edit any original frozen paper title or history.

1. From Windows PowerShell in the repository, run:
   git pull --ff-only origin main
2. Open: https://arxiv.org/pdf/1506.00303v1
3. Actually inspect the Abstract on page 1; copy a clean, substantial paragraph
   straight from the official source.
4. Open Notepad from PowerShell with:
   notepad ".\local_only\reviews\fulltext_label24\paper_5452_abstract.txt"
   Paste just the inspected plain-text passage, then Save as UTF-8 and close.
   DO NOT paste passage into the terminal, and DO NOT put commands inside TXT.
5. Dry-run ONLY:
   .\.venv\Scripts\python.exe -m research_lab.record_inspected_paper --project . --paper-id 5452 --passage-file ".\local_only\reviews\fulltext_label24\paper_5452_abstract.txt" --locator "PDF page 1, Abstract"
   Confirm paper_id, source_url, source_version_date, passage_start and linked
   case-paper count are all correct.
6. Only after this verification, record your explicit source inspection:
   .\.venv\Scripts\python.exe -m research_lab.record_inspected_paper --project . --paper-id 5452 --passage-file ".\local_only\reviews\fulltext_label24\paper_5452_abstract.txt" --locator "PDF page 1, Abstract" --apply
7. Confirm without scoring:
   .\.venv\Scripts\python.exe -m research_lab.fulltext_label_audit --project . --status

For additional primary papers, replace 5452, the text filename and the locator.
Source URL and version date are automatically taken only when there is a
single uncontested date-gated arXiv v1 entry for that paper in the original
auto candidate file. For unverified versions and non-arXiv sources, the
recorder refuses to guess; personally verify the version and pass BOTH
--source-url and --source-version-date YYYY-MM-DD. Even then the software
cannot independently attest online authenticity or scientific entailment.

Existing user-reported status after four source intakes: 28 of 92 linked
case-paper rows populated; 64 still unfilled. Recorded evidence is distinct
from qualified blind expert label evaluation. Scientific overclaim rate and
independent label accuracy remain NOT_EVALUATED. No need to re-run Qwen.
Never upload original private source full texts, mappings or rating sheets
to public GitHub. Do not run assemble until every source access row is
resolved, or score until a genuinely independent reviewer grades the
frozen blind worksheet.


## NEW: Automatically gather version-specific abstracts in bulk (no copy-paste)

From your Windows PowerShell at the repository root:

    git pull --ff-only origin main

Then collect all currently unfilled papers that have a previously verified
arXiv v1 version. Internet access to arxiv.org is required:

    .\.venv\Scripts\python.exe -m research_lab.fetch_arxiv_abstracts --project .

The command downloads **only from the exact arXiv v1 abstract pages** already
linked to the frozen paper IDs. It checks the official page submission date
against the date stored in the original auto candidates before saving text.
It does not overwrite any already downloaded draft or the original reviewed
paper library. Each abstract goes into the private local folder:

    local_only/reviews/fulltext_label24/AUTO_ARXIV_ABSTRACTS_PENDING_REVIEW/

Review the local manifest_LOCAL.csv for successful fetches, papers requiring
manual source search, and any network/version mismatch. arXiv may block
automated requests; a failed fetch does not justify inventing or substituting
abstract text. No new candidate paper title, version or label accuracy is
silently inferred.

To try only the next previously identified paper 5396:

    .\.venv\Scripts\python.exe -m research_lab.fetch_arxiv_abstracts --project . --paper-id 5396

The corresponding draft file (if successfully fetched) is
paper_5396_abstract.txt in the pending directory. Inspect the listed exact
arXiv v1 abstract page and compare the text yourself, then run the generic
record command using that saved file (no manual paper text copy needed).
Do not use --apply without that check:

    .\.venv\Scripts\python.exe -m research_lab.record_inspected_paper --project . --paper-id 5396 --passage-file ".\local_only\reviews\fulltext_label24\AUTO_ARXIV_ABSTRACTS_PENDING_REVIEW\paper_5396_abstract.txt" --locator "arXiv v1 abstract page"

Then, after actual human inspection, repeat this command with --apply.

The bulk fetcher never marks paper evidence FULL_TEXT_USER_INSPECTED,
never changes the original 92-row intake, never scores label accuracy and
never creates the blind reviewer packet. It cannot establish sufficient
semantic support for cluster titles merely from abstracts. Paper sources
without a verified historical arXiv v1 are explicitly reported for separate
manual verification.


## Faster way: inspect and attest staged abstracts in one interactive run

After the historical-source bulk fetch has succeeded, run once:

    git pull --ff-only origin main
    .\.venv\Scripts\python.exe -m research_lab.review_staged_abstracts --project .

For every still-unfilled paper whose arXiv v1 abstract was fetched, the
tool prints the local abstract, opens the **historical v1 PDF** in your
default browser and pauses for your explicit attestation. You must personally
check that the printed text actually matches the paper abstract (including
the dated version and source identity). Only then enter the exact confirmation
text: CONFIRM 5396 (for paper ID 5396), replacing the number for each paper.
Press Enter to skip or Q to stop. The input is deliberately case-specific:
software cannot claim that it read a paper as a human.

Each correctly confirmed paper is registered with the existing guarded local
recorder, including a CSV backup. It will not overwrite previously registered
papers. It will not automatically mark uninspected articles. This is a source
review, not independent blind semantic label grading.

Start with just paper 5396 if desired:

    .\.venv\Scripts\python.exe -m research_lab.review_staged_abstracts --project . --paper-id 5396

After review, inspect data intake progress:

    .\.venv\Scripts\python.exe -m research_lab.fulltext_label_audit --project . --status

For the five sources lacking date-gated arXiv v1, use independent source
discovery rather than relying on inferred versions. These remain unfilled
until a real source is verified or explicitly declared unavailable.


## Corrected preprint-year guard (2026-11-10)

The immutable corpus paper_year may describe a later journal/conference
publication (e.g. 2018), whereas arXiv v1 was correctly submitted earlier
(e.g. 2017). The generic recorder now **allows** this difference, while still
enforcing the frozen per-case snapshot date cutoff. It never alters the
original paper_year or paper_title. The regression test
test_arxiv_v1_may_predate_bibliographic_publication_year protects this
rule. Existing local evidence is not rewritten by this code update.

An earlier interactive session saved 12 papers, but 4 were incorrectly
rejected by this guard (5396, 5393, 5387, 5444). Two others were skipped
because an exact confirmation string was not entered (4166, 5404).
Run the interactive review again: it **only queues unfilled papers**.
Inspect the original exact arXiv v1 PDF before explicitly typing
CONFIRM followed by the shown paper ID. Never confirm blindly.


## Five remaining non-indexed papers: verified primary-source retrieval

The five outstanding source records can now be staged without copying text.
A separate, fixed source manifest lists historically dated ORIGINAL
publishers/preprints, not a changed research-corpus field:

- 5402: OQMD (Saal et al.), Springer JOM online 2013-09-28,
  https://link.springer.com/article/10.1007/s11837-013-0755-4
- 5403: AFLOW (Curtarolo et al.), arXiv v1 2013-08-26,
  https://arxiv.org/pdf/1308.5715v1
- 5435: solid-state electrolyte diffusion (Marcolongo et al.),
  arXiv v1 2019-10-22, https://arxiv.org/pdf/1910.10090v1
- 5399: linking structural defects (Yang & Buehler),
  npj Computational Materials first published 2022-09-17,
  https://www.nature.com/articles/s41524-022-00879-4
- 5455: scaling deep learning (Merchant et al.), Nature first published
  2023-11-29, https://www.nature.com/articles/s41586-023-06735-9

From PowerShell at the repository root:

    git pull --ff-only origin main
    .\.venv\Scripts\python.exe -m research_lab.fetch_remaining_primary_abstracts --project .

The source-specific fetcher checks article identity, date visible on the
publisher's original webpage or on arXiv v1, and temporal snapshots.
It stores no text in git, never changes frozen paper metadata or the 92
original links, and never claims that downloaded text was inspected.
Failed publisher requests (bot blocking, missing abstract etc) are marked
FETCH_FAILED_NEEDS_MANUAL_SOURCE_REVIEW in
local_only/reviews/fulltext_label24/REMAINING_PRIMARY_ABSTRACTS_PENDING_REVIEW/manifest_LOCAL.csv.
A failed download must not be treated as an unavailable original paper.

For successfully staged original abstracts, use:

    .\.venv\Scripts\python.exe -m research_lab.review_remaining_primary_abstracts --project .

The tool prints one abstract, opens its original linked source, and requires
an explicit case-specific CONFIRM <paper_id> after the applicant compares
the exact passage and date to the original PDF or publisher article.
No auto-confirmation. Enter skips. Q stops. Each affirmative confirmation
uses the existing guarded recorder to back up and update just that one
private library row. A source abstract is a source-intake item, not
scientific evidence of the generated cluster label's semantic accuracy.

Once all unique sources are legitimately resolved, run --status; even
when all are inspected, the independent 24-case scientific blinded
evaluation remains NOT_EVALUATED until a distinct reviewer completes
the separate immutable review form. Never silently mark papers UNAVAILABLE
merely because an automated downloader failed.


## Fair local AI-only blind audit of assembled 24-case packet (10 Nov 2026)

This **optional development diagnostic** applies the same gentle-but-factual
scientific rubric to both blinded labels A/B using the frozen 24-case packet.
Title labels that reasonably capture the topic can score "accurate" even
if not maximally specific. Unsupported specific claims are never accepted
as established; abstract-only ambiguity is "unclear", and cases that
cannot support even a fair title comparison are insufficient. It does not
force a positive finding for V2 or V3. Most passages are abstracts and
source content is only applicant-attested, not independent full-paper review.

Only use the local Ollama server already installed on the user's computer.
No Internet API uploads. No repository keys, prior experiment scores, A/B
mapping, or gold are passed to the model. The original
BLIND_FULLTEXT_LABEL24.csv is SHA-256 checked against the assembled receipt
and NEVER modified. The existing REVIEW_IN_PROGRESS.csv is untouched.
No external sharing permissions are assumed.

Commands from repository root:

    git pull --ff-only origin main
    .\.venv\Scripts\python.exe -m unittest research_lab.test_ai_blind_fulltext_review -v
    ollama list
    .\.venv\Scripts\python.exe -m research_lab.ai_blind_fulltext_review --project . --model qwen3:8b --limit 2
    .\.venv\Scripts\python.exe -m research_lab.ai_blind_fulltext_review --project . --model qwen3:8b

The first invocation is an optional 2-case smoke test; it writes case
checkpoints, not a misleading completed review. The second invocation
reuses valid checkpoints and processes all remaining cases. If Ollama
stops or emits invalid JSON, unresolved cases remain unresolved and can
be resumed by running the same command. Do not delete/edit checkpoints
to tune outcomes after inspecting grades. The script writes PRIVATE local
AI_ONLY_BLIND24_QWEN_LOCAL/L001.json ... L024.json only after each valid
response. A full 24-case run writes AI_ONLY_REVIEW24.csv and
AI_ONLY_REVIEW24_SUMMARY.json under local_only/reviews/fulltext_label24/.
All files are excluded from git.

Only after a real 24-case AI-only CSV exists, compute descriptive
V2-versus-V3 AI diagnostic in a separate downstream step:

    .\.venv\Scripts\python.exe -m research_lab.summarize_ai_fulltext_review --project .

This is the **first point** that the private A/B mapping is read; the
rating tool has not read it. The output is
AI_ONLY_REVIEW24_SCORE_LOCAL.json with effective denominators, 95% Wilson
intervals and paired descriptive sign test. It never overwrites
score_LOCAL_PRIVATE.json (reserved for actual independent review).
NEVER relabel this AI-only output as independent human expert review,
full-text-verified entailment, confirmation on an unseen corpus, or a
scientifically confirmed overclaim rate. Original source and frozen
retrieval experiments stay unchanged. Do not run the older generic
--score with AI_ONLY_REVIEW24.csv because that generic filename/semantic
stage may be confused with actual independent reviewer results.


### Recovery when Qwen emits incomplete grades (2026-11-10)

A real two-case smoke test recorded L001 but rejected L002 because a
"sufficient=yes" JSON object lacked a required title/gloss grade.
This is **not** the 24/24 synthetic unittest output, which is deliberately
generated only by mocks and written to a temporary test folder.
No actual final 24-case AI reviewer result has been claimed.

The local reviewer now passes a **six-field JSON Schema** in the documented
Ollama \`/api/generate\` \`format\` parameter and on an invalid response
re-prompts the model with the precise validation error. Source-scientific
judgment, the FAIR_EVIDENCE_RUBRIC_V1 policy, immutable packet and
previously accepted L001 checkpoint are unchanged. If retries still
fail, the affected case stays UNRATED (no automatic invented grades).

After \`git pull --ff-only origin main\`, run:

    .\.venv\Scripts\python.exe -m unittest research_lab.test_ai_blind_fulltext_review -v
    .\.venv\Scripts\python.exe -m research_lab.ai_blind_fulltext_review --project . --model qwen3:8b --limit 2

The smoke test should print L001 CHECKPOINT_OK and either L002 SAVED_AI_ONLY
or a diagnostically useful invalid response error. If both pass, run
without --limit to finish the other 22. Do **not** delete L001.json, modify
original blind packet, or treat passing mock tests as completed local
scientific judging. If a particular case repeatedly fails, leave it
unrated and investigate the local Ollama output rather than filling it
with an invented result.

Source: official Ollama API documentation states \`format\` can be \`json\`
or a JSON Schema; JSON mode alone does not enforce the scientific grade keys.


### Post-hoc read-only QA after a real fair Qwen review (11 Nov 2026)

The user reported a real 24-case local Qwen3:8b development run with
5 V3 wins, 14 V3 losses, 5 ties, descriptive unadjusted paired p≈0.0636.
This result is FROZEN as an observed AI-only developmental diagnostic:
do not rerun or edit until it gives a more favorable result.

Manual inspection of reviewer notes discovered three quality concerns:
- L007: \`Unresolved heterogeneous cluster\` received the categorical
  grade \`wrong\`; a justified abstention is not necessarily a false
  scientific statement. The relationship must be examined in the context
  of the sampled members, source excerpts and evidence sufficiency.
- L013: the note asserts "the gloss for A overclaims", but the structured
  gloss-overclaim field reads \`unclear\`; these are internally discrepant.
- L014: the pasted terminal output did not display \`label_B\` although
  side B was graded \`accurate\`. Determine whether the actual frozen
  label field is empty BEFORE interpreting the grade.

Use the new **read-only** consistency audit on the user's local-only files:

    git pull --ff-only origin main
    .\.venv\Scripts\python.exe -m unittest research_lab.test_ai_blind_review_qa -v
    .\.venv\Scripts\python.exe -m research_lab.ai_blind_review_qa --project .

The command verifies the original assembled receipt and rated CSV hashes,
then examines all 24 rows for empty scientific label titles that were
nevertheless graded, changed frozen evidence, invalid response values,
explicit notes/flag contradictions, and potential over-penalization of
abstentions. Formal integrity problems are separated from *heuristic*
warnings; textual warnings are not proof that Qwen was incorrect. It makes
NO Ollama calls, reads NO private V2/V3 side mapping or benchmark gold,
writes NO files and cannot change the prior measured negative result.
The copied reviewer worksheet and original AI score remain unchanged.

If a title is actually blank, its AI accuracy grade is scientifically
uninterpretable even if a structured output validator accepted it. Record
that limitation transparently rather than silently filling the title,
faking a reviewer correction, or retrospectively altering the previously
frozen p-value.


### L017 / L023 interpretation and V4 evidence-separated prototype (11 Nov 2026)

Real Qwen L017 output: V3 "Amorphous" was marked accurate and V2
"Mixed topics: Carbon / Amorphous" was marked vague. Its rationale
called the V3 gloss an overclaim while assigning "unclear" in the
structured field. The V3 gloss's **17 of 25** statement is a
*locally checkable name-mention count*, NOT a claim that a paper says
"amorphous" 17 times or establishes an entire scientific topic.
The critic may be confusing lexical provenance with paper entailment.
The number must be validated against frozen member names; neither paper
abstracts nor Qwen notes alone attest it.

Real Qwen L023 output: V2 "Mixed topics: Nasicon / Pipeline" got vague;
V3 "Unresolved heterogeneous cluster" got wrong. V3 abstained because
the candidate phrase failed its cutoff-specific lexical support rule.
Failure to identify a topic is NOT a scientific claim that all members
are genuinely heterogeneous. A shared *very broad* domain such as
machine learning in materials science may not justify a more specific
label. Both quality-of-title and appropriateness-of-abstention must
be evaluated independently. Keep the original 5-win / 14-loss /
5-tie AI-only diagnostic (p≈0.0636) frozen; the review is not an
independent semantic acceptance result and Qwen's qualitative
rationale has known possible internal contradictions.

A new **separate** experimental module
\`research_lab/label_v4_exploratory.py\` does NOT infer new semantic
scientific titles or lower V3 thresholds after viewing its losses.
It applies exactly the frozen original V2 phrase evidence and V3
coverage/source-count rules, but represents:

- \`display_title\`: the qualified phrase only, or neutral
  \`Unresolved topic\` when no source-qualified term passes
- \`lexical_evidence_state\`: majority/partial/no-qualified-phrase status
- \`abstained_from_specific_topic\`: an explicit boolean flag
- \`observed_terms_not_confirmed_topics\`: original V2 selected
  phrases with exact name/support counts, marked not semantically verified
- \`display_gloss\`: carefully scoped name-mention and provenance
  claims, never a statement that an abstained cluster is scientifically
  incoherent

To generate ALL 180 (3×60) source-scoped presentations locally:

    git pull --ff-only origin main
    .\.venv\Scripts\python.exe -m unittest research_lab.test_label_v4_exploratory -v
    .\.venv\Scripts\python.exe -m research_lab.label_v4_exploratory --project .

This writes only the ignored folder
\`local_only/label_v4_exploratory/\` and refuses to overwrite it.
It does not open the 24-case private ratings, paper full-text intake,
gold, A/B mapping, or change any previous selected model, V2/V3 or PDF.
A new evaluator should have SEPARATE rubrics for topic-title
utility, semantic entailment, lexical count/provenance accuracy and
whether abstention is appropriate, and should use genuinely unseen,
source-authorized, fulltext-supported cases. Re-scoring this same 24-case
worksheet would only be post-hoc development, NOT confirmation of V4.
