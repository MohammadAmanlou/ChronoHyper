# ChronoHyper

**Multi-resolution semantic abstraction of an evolving scientific knowledge hypergraph**  
Mohammad Amanlou · Constructor Knowledge Labs PhD research assessment · Python 3.11

ChronoHyper builds a **nested four-level hierarchy** from source-dated scientific entities and **native high-order hyperedges**, preserves event provenance and multiplicity, and tracks cluster identity through time. The submitted method is deliberately modest: the goal is auditable abstraction and controlled evaluation, **not** an unsupported state-of-the-art accuracy claim.

## Reviewer start here

**[Scientific report — 4 pages](report.pdf)** · [Evaluation numbers](metrics.json) · [Selected hierarchies](outputs_selected/) · [AI assistance disclosure](AI_USAGE.md)

The PDF is the **locked core assessment**; its text matches the [rebuildable LaTeX source](scripts/report.tex) in the [PDF verification workflow](https://github.com/MohammadAmanlou/ChronoHyper/actions/runs/40093321319). Later experiments are **post-hoc development**, documented separately in [extended results](report.md). The selected model and original benchmark scores were not retroactively changed.

## Requirement-to-evidence checklist

| Constructor requirement | Evidence | What is actually established |
|---|---|---|
| **T1** · Dated TKH, source quality, arities | [EDA](outputs/eda_summary.json) | 5,798 entities, 1,429 original hyperedges, 52 papers; cutoffs and original-event checks |
| **T2 / P1–P2** · Laminar hierarchy, hard budgets | [Native method](src/core.py), [hierarchies](outputs_selected/) | **Verified structurally** across 2020, 2022, 2024 and exploratory 2025; 12/48/≤144/singleton levels |
| **T2 / P3–P4** · Semantic/structure objective and native edges | [Formal report](report.pdf), [comparative experiments](research_outputs/final_matrix/) | 0.70 semantic / 0.30 structural + 0.20 temporal local-move heuristic; **not a global optimum** |
| **T3 / P5** · Stable identity and actual temporal change | [Event log](outputs_selected/temporal_events.json), [locality audit](research_outputs/temporal_locality_posthoc.json) | ID matching and event accounting verified; change events are **overlap heuristics**, not confirmed concept truth |
| **T4** · Internal, partial and multi-group edge collapse | [Collapse implementation](src/core.py), [preserved events](outputs_selected/) | Native event IDs, provenance, original arity, coarse endpoint multiplicities; no pairwise substitution in primary solver |
| **T5 / P6** · Automatic label and gloss | [Label records](outputs_selected/), [source-dated diagnostic](docs/ASSESSMENT_STATUS.md) | Lexical/membership/date checks and abstentions measured; **independent scientific entailment unverified** |
| **T6** · Independent-view coherence and a structural null | [Metrics](metrics.json), [null stress test](research_outputs/stress_temporal20_extended/result.json) | Second-view proxies, held-out paper groups and degree/arity-preserving null; **p = 0.69**, no significant structural gain |
| **T6** · Real temporal stability and perturbation | [Metrics](metrics.json), [perturbation study](research_outputs/stress_temporal20_extended/result.json) | Cross-snapshot ARI, 5 seeds and 10% edge deletion; same-corpus uncertainty, not external replication |
| **T6** · Label overclaim rate | [Assessment audit](docs/ASSESSMENT_STATUS.md) | Structural-claim proxy measured; scientific full-text **overclaim rate NOT_EVALUATED** — cannot report as 0% |
| **T6** · Extrinsic retrieval vs Flat | [Evaluation record](docs/ASSESSMENT_STATUS.md), [extended report](report.md) | Flat **3/34** vs Route-4 **2/34** Hit@5; 59.3% fewer *online dot products*, **not an accuracy win or latency benchmark** |
| **T7** · Report, reproduction and assistance record | [4-page PDF](report.pdf), [AI_USAGE](AI_USAGE.md), [CI](https://github.com/MohammadAmanlou/ChronoHyper/actions/runs/42500835195) | Canonical report within length limit; reproducibility checks pass. Scientific caveats are reported explicitly. |

**What the numbers mean.** The source-held-out hyperedge-cut objective was **0.6623 in development vs 0.7172 in confirmation** (lower is better; it worsened). The **p = 0.69** degree/arity null is not significant. A frozen partition can look stable even if it cannot respond to genuine scientific change. These are not suppressed negative results.

## Reproduce the submitted CPU result

From the repository root on Windows:

~~~powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe verify_selected_outputs.py --out outputs_selected
.\.venv\Scripts\python.exe final_preflight.py --project .
~~~

For a clean Git HEAD deliverable check (not a retraining run):

~~~powershell
.\.venv\Scripts\python.exe scripts\final_handoff.py --project .
~~~

More comprehensive checks, rerun parameters and optional GPU requirements are in the [technical reproduction guide](docs/REPRODUCE.md). Tests verify code and structural consistency, **not** the truth of scientific labels or generalization to new corpora.

## Research extensions — separate from the locked assessment

- **Temporal source-delta locality:** changes in root identity when an existing node gains an admissible new training hyperedge. In **2020–22**, 1/76 touched vs 10/1,429 untouched nodes changed (post-hoc conditional **p=0.546**). In **2022–24**, 7/146 vs 20/2,018 changed (**p=0.002**). Both are exploratory, unadjusted, and **not causal or independent confirmation**. [Data and exclusions](research_outputs/temporal_locality_posthoc.json) · [Figure](figures/temporal_locality.svg).
- **Optional neural retrieval:** BGE-M3 context **10/34**, Qwen3 **12/34** Hit@5 on the *same inspected 34 cases*. Paired 5 wins / 3 losses / 26 ties, unadjusted p=0.7266. The Gold-blind candidate union's **29/34 Candidate recall** is target **presence among candidates**, not Hit@5, and is **not independent confirmation**. [Retrieval figure](figures/retrieval_development.svg) · [Machine-readable development summary](research_outputs/gpu_retrieval_development_summary.json).

The next **scientific** gate is independent, dated, full-paper label/gloss review with explicit unsupported and insufficient-source denominators, followed by a genuinely untouched source-supported retrieval evaluation. Training a larger reranker again on the same inspected 34 questions would not close either gap.

## Repository map and privacy

| Main entry | Purpose |
|---|---|
| [src/](src/) | Small submitted native-hypergraph implementation |
| [outputs_selected/](outputs_selected/) + [metrics.json](metrics.json) | Canonical selected output and frozen metrics |
| [report.pdf](report.pdf) + [AI_USAGE.md](AI_USAGE.md) | Required readable handoff documents |
| [research_lab/](research_lab/) + [research_outputs/](research_outputs/) | **Optional audit trail and developmental experiments**, including negative results; not required reading to understand the submission |
| [docs/ASSESSMENT_STATUS.md](docs/ASSESSMENT_STATUS.md) | Detailed limitation and evidence ledger |

The repository is **private**: [original provider data](inputs/data.zip) may contain reference answers. Do not make it public or distribute source data, local PDFs, Gold or blind-review keys without authorization. The reviewer has collaborator access; a [private ZIP fallback](scripts/final_handoff.py) can be generated from **tracked Git HEAD** if explicitly needed. Independent reviewer acceptance, eligibility, funding and admission are not asserted.
