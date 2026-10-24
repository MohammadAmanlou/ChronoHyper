# AI assistance and research integrity

**Project:** ChronoHyper — Mohammad Amanlou, Constructor Knowledge Labs research assessment.

**Disclosure.** OpenAI GPT-6 (ChatGPT) materially assisted with experiment design, Python implementation, scientific checking, unit tests, data audits, visualization, report drafting and reproduction instructions during October 2026. The applicant is responsible for verifying and understanding this work before submission. This is **not** a statement that an independent expert reviewed the scientific findings.

**What was checked.** The code includes structural and provenance invariants, native hyperedge multiplicity preservation, dated-source restrictions, sampled labels, repeated-seed comparisons and source-group controls. Clean CI and local Gold-separated ranking hashes were checked. Negative results were retained: the selected clustering's constrained null is not significant (`p = 0.69`), source-held-out cut worsens (0.6623 → 0.7172), and four-root retrieval does not beat flat on the 34 source-screened queries.

**Post-hoc experiments.** Later BGE-M3 and Qwen3 reranking experiments on those *same 34 already-viewed* questions were guided by interim performance. Qwen3 variants observed 12/34 Hit@5 versus BGE-M3 10/34; 29/34 is only Gold-blind candidate presence, not Hit@5. No independent confirmation, full-paper semantic guarantee, verified generated Type-B factual accuracy, or applicant submission is claimed.

**October 24 evidence-intake extension.** GPT-6 wrote a gated,
local-only source-paper tracing / independent reviewer preparation
pipeline for the existing V2/V3 blind comparison. Source metadata and
synthetic tests were checked in CI; **no primary-paper passages were
retrieved by the assistant and no new scientific judgments were made**.
The human applicant retains responsibility for copyright, source
version checks, evaluator separation and complete review.

**Automation extension.** GPT-6 implemented source-limited open-access
PDF fetching, extraction and lexical evidence selection with optional
local model scoring. These tools were code-tested; each retrieved
passage and any AI-assessed label remain unverified until independently
checked against original historic full-text evidence. No manual input,
new scientific review outcomes or successful bulk retrieval was
fabricated.

**Evidence boundary.** AI reviewer judgments of sampled names/titles and source snippets cannot substitute for independent full-paper/domain adjudication. The original provider-supplied source archive can contain its own reference answers and therefore must stay inside authorized **private** review. Never add newly held-out Gold, blind keys, private reviewer ratings, emails or personal files to commits or GPU input bundles. Experiment hashes, original frozen outputs and remaining open claims are documented in [report.md](report.md), [docs/ASSESSMENT_STATUS.md](docs/ASSESSMENT_STATUS.md), and [research_outputs/](research_outputs/).

A longer chronological AI-assisted working log existed in prior Git history; it was consolidated here for a readable submission-facing disclosure, not to imply unaided authorship.
