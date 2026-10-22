# Private Kaggle Type-B source passage ZIP, requiring real pre-cutoff evidence.
# Portable forward-slash ZIP members are mandatory for Kaggle.
[CmdletBinding()]
param([string]$Output = "local_only\gpu_type_b_private.zip")
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "Missing .venv Python: $python" }
Push-Location $root
try {
    & $python -c "from research_lab.type_b_answer_generation import validated_passages; p,rows=validated_passages('.'); print('Formatted dated full-text passage rows:',len(rows))"
    if ($LASTEXITCODE -ne 0) { throw "No admissible historical primary full-text evidence; ZIP blocked" }
    & $python .\scripts\make_gpu_zip.py --project . --kind type-b --out $Output
    if ($LASTEXITCODE -ne 0) { throw "Private Type-B Kaggle ZIP creation/validation failed" }
    Write-Host "Keep dataset PRIVATE and confirm passage sharing rights."
}
finally { Pop-Location }
