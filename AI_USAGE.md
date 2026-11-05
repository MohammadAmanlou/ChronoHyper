# AI assistance and research integrity

**Project:** ChronoHyper — Mohammad Amanlou, Constructor Knowledge Labs research assessment.

**Disclosure.** OpenAI GPT-6 (ChatGPT) materially assisted with experiment design, Python implementation, scientific checking, unit tests, data audits, visualization, report drafting and reproduction instructions during October 2026. The applicant is responsible for verifying and understanding this work before submission. This is **not** a statement that an independent expert reviewed the scientific findings.

**Representative major prompts and verification record.** Prompts below are
representative paraphrases of the main research-assistance instructions, not
verbatim complete transcripts or evidence of unaided authorship.

| Task / module | Representative AI prompt | Accepted / modified output and validation |
|---|---|---|
| Formal model / `src/` | "Construct nested budgets from native time-stamped hyperedges; distinguish guaranteed constraints from empirical semantic quality." | Reviewed local heuristic versus a claimed global optimum; preserved P1/P2/native-event assertions and year-cutoff tests. |
| T4 collapse / `outputs_selected/` | "Handle fully internal, partly internal and three-or-more-supernode hyperedges without losing event identities, arities or multiplicity." | Added native endpoint/provenance checks, original-event accounting, clique-projection audit and frozen source archive hashes. |
| Experimental protocol / `research_lab/` | "Test semantic-vs-structural weights and temporal inertia with source-paper separation, multiple seeds, degree/arity-preserving null and deletion stress." | Fixed five seeds, recorded held-out-cut worsening and non-significant null `p=0.69`; kept failed alternatives and denominators. |
| Labels / `research_lab/label_v2.py`, `label_v3.py` | "Ground labels in dated source occurrences; abstain if evidence is weak; compare candidate labels with blinded review and overclaim denominators." | Checked 180 dated phrase cases and abstentions; did **not** promote same-corpus AI opinions or title overlap to independent full-paper truth. |
| Retrieval / `research_lab/retrieval_frontier.py` | "Compare flat and hierarchical traversal at the same source/candidate scoring budget; freeze ranking output before reading Gold." | Preserved Flat 3/34 vs Route-4 2/34, 59.3% fewer online dot products (not latency), failure cases and prior-score disclosure. |
| Optional GPU / `research_lab/qwen_entity_rerank.py` | "Build a Gold-blind three-view candidate union; score Qwen3 only after freezing its ranking hash; compare wins and losses against BGE." | Verified SHA-linked rankings; 12/34 vs 10/34 Hit@5 on the **same inspected 34**, 5 wins/3 losses/26 ties and unadjusted p=0.7266; **no** independent-win claim. |
| Primary-paper evidence / `auto_primary_evidence.py`, `fulltext_label_audit.py` | "Retrieve only accessible version-dated primary papers; isolate reviewer A/B keys; never fabricate missing passages or human ratings." | Source-bound document-link checks, PDF text and snapshot cutoff tests; automatic excerpts remain **unreviewed** until independently verified. |
| Scientific narrative / `report.md`, `report.pdf` | "Prepare a short, reproducible scientific assessment with figures, major limitations and verified-vs-assumed separation." | Cross-checked source/locked model, selected metrics and PDF rebuild; disclosed unsupported/negative findings rather than editing them away. |

**Human responsibility.** The applicant must be prepared to explain each code
path, model assumption, source, hypothesis, negative outcome and statistical
denominator. Tool-generated prose, code, historical-source links, images and
tests are not evidence of scientific validity without applicant review.
No peer review, autonomous expert judgement, project acceptance or full
validation is inferred from AI assistance.

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
