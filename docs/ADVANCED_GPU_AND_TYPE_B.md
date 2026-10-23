# Optional retrieval experiments (development only)

**Core assessment:** [report.pdf](../report.pdf) and [report.md](../report.md). The locked 34-query Flat/Route-4 evaluation (3/34 vs 2/34 Hit@5) has not been modified. Later neural models are **post-hoc development on the same 34 questions**, never fresh, independent confirmation.

## Completed experiments

| Experiment | Hit@5 / 34 | Notes |
|---|---:|---|
| BGE-M3 Context | 10 | Highest source-only Top-5 together with Paper / fusion |
| BGE-M3 three-view RRF | 10 | Top-100 26 |
| BGE-reranker-v2-m3 | 1 | Degraded ranking; not selected |
| Qwen3-Reranker-0.6B Raw | 12 | Top-10 19; Top-20 21; MRR@5 0.1814 |
| Qwen3 + anchor first Context result | **12** | MRR@5 **0.2181** |
| Qwen3 + anchor first two Context results | 12 | MRR@5 0.2029 |

Actual Qwen result ranking digest: `be9db8e7a090b9457ec9e90e5e98e23d2c997009349a8e2906271e93b2a9cd89`. Its preceding BGE multiview ranking digest: `88f536d78e9e408f526d08bc079111cdd32db76ce13744b0f318c400341c13cd`. These SHA values establish artifact continuity, **not** scientific truth or independence.

The source union included **29/34** correct entities among a mean **208.94** distinct candidate entities per question; this is candidate recall, not prediction accuracy. See [report.md](../report.md#8-gpu-semantic-retrieval-and-qwen3-reranking--post-hoc-development-24-october-2026).

## Reuse without overwriting frozen files

~~~powershell
# From the repository root after installing requirements.txt:
.\.venv\Scripts\python.exe -m unittest research_lab.test_qwen_entity_rerank research_lab.test_qwen_candidate_preflight -v

# Only if the local, ignored original Gold-free rankings and local score files exist:
.\.venv\Scripts\python.exe -m research_lab.qwen_candidate_preflight --project .

# This compares your existing locally scored results only; it DOES NOT run a GPU model.
~~~

Optional Kaggle packaging is implemented in `scripts/package_gpu_rank_only.ps1` and `scripts/package_gpu_qwen_rerank.ps1`. They create **new, private, Gold-free** ZIPs and must never overwrite previous experimental artifacts. Kaggle can unpack nested ZIPs; inspect actual mounted `/kaggle/input` paths rather than guessing an archive basename. Optional GPU dependencies: `requirements_advanced.txt` and `requirements_qwen_rerank.txt`.

**Next scientific step:** predefine model/prompt/candidate policy, author a source-verified untouched benchmark, freeze queries and rank-only outputs, then score once with Gold retained off the inference machine. No additional tuning on these 34 cases counts as new confirmation.
