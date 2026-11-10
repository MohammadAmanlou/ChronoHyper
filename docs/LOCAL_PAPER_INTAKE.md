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
