# Evidence-grounded label V2 — reproducible pilot, NOT an independently validated improvement

The code in `research_lab/label_v2.py` is an experimental label candidate generator over **frozen** `native_temporal_20` clusters. It contrasts exact scientific name n-grams with outside-cluster names, restricts claims to eligible source nodes and dated article provenance, and explicitly abstains when support is insufficient. It does **not** refit clusters or change the main report's V1 evaluation.

| Snapshot | Level-0/1 candidates | Supported-partial | Low-support | Abstain | Exact node-name occurrences verified |
|---|---:|---:|---:|---:|---:|
| 2020 | 60 | 39 | 17 | 4 | 1,146 |
| 2022 | 60 | 37 | 21 | 2 | 1,510 |
| 2024 | 60 | 40 | 20 | 0 | 2,599 |

These are **mechanical lexical checks**, not domain correctness scores. The 24 novel source-cluster A/B cases have no real blind human ratings. No V2 win, p-value or semantic overclaim rate can be claimed yet.

Reproduce with:
```powershell
.\.venv\Scripts\python.exe -m research_lab.label_v2 --project . --out research_outputs/label_v2
```

`BLIND_LABEL_COMPARISON_TO_FILL.csv` can be shared with a qualified independent reviewer. Keep `BLIND_KEY_KEEP_SEPARATE.json` **outside version control** and never give it to the reviewer.

Earlier V1 nonblind topic ratings: 8 accurate, 28 vague, 12 wrong of 48; 40 gloss judgments indeterminate. The synthetic test's printed mock A/B evaluation is **not** user research data.
