# Label evidence separation: lexical provenance versus scientific entailment

This is a **post-hoc methodological clarification** after the private 24-case
Ollama Qwen3:8B run on 9 November 2026. It is not a new score, nor a replacement
for the blinded evaluation, locked selected hierarchy, or 4-page report.

## What the actual local AI run established

- The technical retry produced 24/24 parsable local model answers with 0
  unresolved execution errors.
- Qwen rated **evidence sufficiency = no** for every case when provided short,
  lexically ranked passage windows. This is a judgment about the evidence
  *shown*, not a demonstration that 24 titles are incorrect.
- Its recorded explanations include inadequate paper support for DFT, training,
  force or other shared scientific themes (e.g. L001-L004); and the inability
  of articles to verify case-specific cluster counts such as 9/16 (L022) or
  19/56 (L024).
- The excerpts were automatically extracted and selected by lexical coverage;
  they have **not** been independently confirmed to entail the labels, and
  an absence of a statement in a short excerpt is not proof of contradiction.

## Two logically distinct evidence types

| Claim | Appropriate evidence | What successful verification establishes | What it does NOT establish |
|---|---|---|---|
| At cutoff year Y, K of N non-metadata members explicitly mention phrase P in their exported names | Original frozen hierarchy memberships, original node types / surface forms, cutoff dates, deterministic tokenizer and source identifiers | The structural **count** and temporal provenance are accurate | The entire group coheres scientifically; the phrase has a particular scientific meaning in the paper |
| An arXiv/preprint/paper was available by Y | Dated original version metadata and archived primary source | Source version is admissible for the year | That a chosen passage entails the specific title or gloss |
| Label L is an accurate scientific characterization of group G | Dated primary-paper passages selected by a **predeclared** relevant protocol, whole-group context, qualified blind independent rating | Scientifically meaningful coherence/faithfulness according to the specified rubric | The graph's K/N count unless checked against original source records |
| "Unresolved heterogeneous cluster" | Predeclared abstention and heterogeneity criteria applied to the original group | The **decision to abstain** is rule-conforming | A paper itself says the algorithm's cluster is heterogeneous or that its members share no topic |

For example, **19/56** is a membership/name-coverage proposition about
*ChronoHyper's* output. It is not a claim that an arXiv article contains a
19/56 statistic. The original generated gloss expressly calls this *lexical
provenance*, not independently validated scientific description. Consequently,
a model rejecting a paper excerpt because it lacks "19/56" cannot alone score
the structural proposition as false.

## Existing verified and unverified checks

1. `python -m research_lab.label_v3 --project . --out local_only/label_v3_dev`
   regenerates the **developmental** deterministic V3 labels if they are
   absent. Do not overwrite local reviewed artifacts casually.
2. `python -m research_lab.v3_provenance_audit --project .` validates the
   **180 V3 level-0/level-1 label records** across 2020, 2022, 2024 against
   original node names, frozen memberships and dated source-article references.
   It is a source-data consistency check and uses no benchmark answer Gold.
   Its output lives under `local_only`. If a prior audit exists, it is
   compared for exact identity, not silently replaced.
3. `research_lab/auto_primary_evidence.py` and the private Qwen judge present
   excerpts for a **separate preliminary semantic** evaluation. The model
   receives at most four short top-scoring candidate excerpts per case.
   These ratings are post-hoc development evidence, not independent
   scientific adjudication.
4. Authentic independent primary-paper semantic ratings of the 24 blinded
   A/B pairs **are not yet available**; therefore scientific title accuracy
   and gloss-overclaim-rate numerator/denominator remain **NOT_EVALUATED**.

## Appropriate next review protocol

- **Structural sheet (non-blind data audit):** verify year, group size,
  eligible denominator, exact occurrence count, ID provenance, and the
  implementation of abstention on the original frozen graph. Keep
  `structural_consistent` separate from scientific correctness.
- **Semantic sheet (still blind to A/B algorithm mapping):** have a qualified
  independent reviewer inspect the relevant full primary publication, dated
  version, sampled and broader cluster member context, then rate each arm's
  scientific title and gloss. Source quotations must not be treated as
  instructions. An insufficient source yields *not evaluable*, not *wrong*.
- **Audit disclosures:** record accessible sources, cutoff/version issues,
  how passages were selected, reviewer identity, blinded case coverage,
  denominators, and uncertainty. Do not use the same model's prompts or
  the labels being rated as sole evidence of scientific coherence.
- **If revising labels or a retrieval method after this 24-case outcome:**
  call the new run **post-hoc development**. Do not rewrite the frozen
  confirmation metrics or claim an untouched confirmatory evaluation.

The cited local Qwen notes (e.g. L001/L005/L022/L024) were inspected in a
user-shared terminal excerpt; private full-text passages and secret A/B keys
were never copied into this repository.
