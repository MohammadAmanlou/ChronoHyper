# Label V2 — research milestone (19 October 2026)

**Status:** Code prepared and 6 new tests passed on the authentic Constructor snapshot, but its implementation is **not yet present in this remote branch**. Candidate must apply and push `ChronoHyper_Label_V2_Patch_2026-10-19.zip`; do not mistake this milestone for a completed method comparison.

## Problem identified in V1

Original 48-case non-blind, AI-assisted review: **8 accurate / 28 vague / 12 wrong** label titles. Only **8/48** gloss-overclaim judgments were determinate; 40 were `unclear`. Overclaim 0/8 is not an overall 0% rate and is not independent human evidence.

## V2 hypothesis and limited verification

Contrastive 1–3-gram labels from time-eligible scientific entity names, using cluster-vs-rest specificity, support counts and dated article provenance. When support is sparse, the candidate label is explicitly marked mixed or unresolved; the gloss asserts only observed phrase occurrences, not an inferred scientific topic for every member.

A local real-data dry run on the **unchanged** `native_temporal_20` hierarchy generated 60 candidates per 2020, 2022 and 2024 snapshot:

| Year | Candidates | Partial source support | Low-support partial | Abstentions | Verified explicit node-name occurrences |
|---|---:|---:|---:|---:|---:|
| 2020 | 60 | 39 | 17 | 4 | 1,146 |
| 2022 | 60 | 37 | 21 | 2 | 1,510 |
| 2024 | 60 | 40 | 20 | 0 | 2,599 |

These are **mechanical lexical/provenance checks only**. No improved domain-expert accuracy, statistical label advantage or blind overclaim rate has been established.

## Required independent test

- Sample 24 source clusters not included in the original 48 reviews.
- Show identical label-independent random member samples and provenance for A/B pairs; conceal the model mapping in a separate local key.
- Reviewer records `accurate/vague/wrong`, `yes/no/unclear` and reason for both sides.
- Compute paired win/loss/tie and an exact paired sign test; preserve missing or inconclusive judgments.
- Report reviewer independence truthfully; AI-assisted review is not blind expert validation.

## Research safety

Never refit the locked cluster assignments after seeing confirmation or benchmark gold. Keep the original results and `model_lock.json` intact; do not put the A/B unblinding key in the repository. This is a private employer assessment, not public data.

The existing employer deadline is **19 October 2026** (exact hour unspecified). GitHub work is not proof of submission.