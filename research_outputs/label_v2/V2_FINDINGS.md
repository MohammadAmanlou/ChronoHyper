# CKL V2 contrastive labeller — real-data experimental result

This is an **exploratory** implementation on the fixed, locked `native_temporal_20` hierarchy.
It does not reassign nodes or improve T2/T3 results, and no reviewer has rated V2 yet.

## Output audit
| Year | Labels | Source-supported partial | Low-support partial | Abstain | Verified lexical supporters |
|---|---:|---:|---:|---:|---:|
| 2020 | 60 | 39 | 17 | 4 | 1146 |
| 2022 | 60 | 37 | 21 | 2 | 1510 |
| 2024 | 60 | 40 | 20 | 0 | 2599 |

**What was established:** all cited phrase occurrences and year-eligible article IDs checked against real input node records (lexical/provenance validity only).
**What was NOT established:** a domain expert finding these clusters scientifically coherent, label improvement over V1, independent NLI/overclaim rate.
**Untouched review cases available:** 24. Provide `BLIND_LABEL_COMPARISON_TO_FILL.csv` to an independent reviewer; DO NOT give them `BLIND_KEY_KEEP_SEPARATE.json`.
**Prior review identifiers:** ['GPT-6 AI-assisted reviewer; non-human; non-blind']. These must not be described as blinded independent human review without direct evidence.

## Reproduction
```bash
python -m research_lab.label_v2 --project . --out research_outputs/label_v2
```
The method contrasts candidate phrases against other members of the same year/level vocabulary. Generic statements are calibrated to *explicit token occurrence* and explicitly refuse to generalize from keyword mentions to all members.
It uses article IDs as provenance only and does not imply an entire article scientifically entails its keyword mention.
The old V1 review is a development diagnostic, not a held-out V2 result.
