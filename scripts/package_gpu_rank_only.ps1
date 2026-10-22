# Minimal, gold-free Kaggle ZIP using a Python POSIX ZIP writer.
# Windows Compress-Archive can put "\" in member names; Kaggle rejects those.
[CmdletBinding()]
param([string]$Output = "local_only\gpu_rank_only.zip")
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "Missing .venv Python: $python" }
Push-Location $root
try {
    & $python .\scripts\make_gpu_zip.py --project . --kind rank --out $Output
    if ($LASTEXITCODE -ne 0) { throw "Private Kaggle ZIP creation/validation failed" }
    Write-Host "Keep dataset PRIVATE. Do not upload gold_PRIVATE.csv or reviewer files."
}
finally { Pop-Location }
