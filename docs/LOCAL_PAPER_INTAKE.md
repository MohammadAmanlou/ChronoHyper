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
