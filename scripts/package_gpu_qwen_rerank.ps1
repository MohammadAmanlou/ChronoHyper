# PRIVATE Kaggle input for checkpointed Qwen3 entity reranker.
# Accepts ONLY the gold-blind frozen multiview rankings, dated graph/titles,
# frozen question texts and ranker sources. No Gold, old scores or reviews.
[CmdletBinding()]
param([string]$Output="local_only\gpu_qwen_entity_rerank_private.zip")
$ErrorActionPreference="Stop"
$root=(Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python=Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {throw "Virtualenv Python not found: $python"}
Push-Location $root
try {
    & $python .\scripts\make_gpu_zip.py --project . --kind rerank --out $Output
    if ($LASTEXITCODE -ne 0) {throw "Qwen3 private rank-only bundle validation failed"}
    & $python -c "from zipfile import ZipFile; import io; z=ZipFile('local_only/gpu_qwen_entity_rerank_private.zip'); assert 'research_lab/qwen_entity_rerank.py' in z.namelist(); sub=ZipFile(io.BytesIO(z.read('inputs/data.zip'))); assert 'data/ground_truth.json' not in sub.namelist(); print('PRIVATE QWEN RERANK ZIP: PASS')"
    if ($LASTEXITCODE -ne 0) {throw "Qwen archive security check failed"}
    Write-Host "Upload this as a PRIVATE Kaggle Dataset. Do not upload Gold, answer grades, or score files."
}
finally {Pop-Location}
