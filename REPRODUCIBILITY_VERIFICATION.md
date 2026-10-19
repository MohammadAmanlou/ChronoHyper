# Reproducibility verification — 19 October 2026

## Same-data repeated runs

The original 2026-10-19 implementation was executed against the unchanged Constructor data archive, and seven primary result JSON artifacts were compared against independent output-directory results and found to be byte-for-byte identical under the frozen seed and pinned library versions. Hardware-specific elapsed time varies.

## Actual Windows execution verified from candidate terminal transcript

- Host environment: Windows PowerShell, Python 3.11.9, pinned dependencies from `requirements.txt` successfully installed into project `.venv`.
- Authentic input archive SHA256 matched the recorded original `414867a07e5fdc4b38f9ad4e96bd5253d31e239012173ca439a1c5441553b4e1`.
- Full command `python -m src.run --data inputs/data.zip --out outputs --seed 17 --null-runs 16` completed for snapshots 2020/2022/2024/2025 with reported runtime **64.09 seconds**, producing hierarchy, temporal, metric and report outputs.
- The user first observed a Windows default-encoding `UnicodeDecodeError` in one test reader, resolved by explicit `encoding="utf-8"` for all five JSON reads within `tests/test_output_invariants.py`.
- The user then re-ran `python -m unittest discover -s tests -v` on Windows. The uploaded terminal transcript confirms **10 tests run and all passed (OK)** in 0.309 seconds. A few scikit-learn convergence warnings arose only in synthetic edge-case tests and did not fail.

## Scientific limits

These software validation results do not establish that all research hypotheses are empirically supported. The independent semantic claim/overclaim rating remains incomplete, and hierarchical retrieval underperformed the flat baseline on the scored query set. These limits are explicitly recorded in the report and metrics.
