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
