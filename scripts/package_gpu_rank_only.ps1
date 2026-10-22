# Produce a MINIMAL rank-only GPU bundle for a PRIVATE Kaggle Dataset.
# By design: NO gold_PRIVATE.csv, reviewer files, ranking or previous scores.
# Copy ZIP to private Kaggle input; upload only the resulting rankings JSON.
[CmdletBinding()]
param(
    [string]$Output = "local_only\gpu_rank_only.zip"
)
$ErrorActionPreference = 'Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$work=Join-Path $root "local_only\gpu_rank_only_stage"
$zip=Join-Path $root $Output
$allow=@(
    "research_lab\__init__.py",
    "research_lab\advanced_retrieval.py",
    "research_lab\retrieval_v2.py",
    "research_lab\retrieval_frontier.py",
    "inputs\data.zip",
    "outputs_selected\hierarchy_2025.json",
    "local_only\fresh_retrieval_screened34\queries_only.csv",
    "requirements_advanced.txt"
)
if (Test-Path $zip) {throw "Existing GPU package protected: $zip"}
if (Test-Path $work) {throw "Existing staging folder protected: $work"}
New-Item -ItemType Directory -Force $work | Out-Null
try {
    foreach ($rel in $allow) {
        $source=Join-Path $root $rel
        if (-not (Test-Path $source)) { throw "Missing approved rank-only input: $source" }
        $dest=Join-Path $work $rel
        New-Item -ItemType Directory -Force (Split-Path -Parent $dest) | Out-Null
        Copy-Item -LiteralPath $source -Destination $dest
    }
    if (Test-Path (Join-Path $work "local_only\fresh_retrieval_screened34\gold_PRIVATE.csv")) {
        throw "Gold detected in rank-only package. Refuse creation."
    }
    if (Test-Path (Join-Path $work "local_only\reviews")) {throw "Reviewer data detected"}
    $zipdir=Split-Path -Parent $zip
    New-Item -ItemType Directory -Force $zipdir | Out-Null
    Compress-Archive -Path (Join-Path $work '*') -DestinationPath $zip -CompressionLevel Optimal
    Write-Host "PRIVATE GPU bundle (RANK-ONLY, NO GOLD): $zip"
    Get-FileHash -Algorithm SHA256 $zip | Format-Table
    Write-Host "Keep the Kaggle Dataset PRIVATE and never upload any raw Gold or reviewer files."
}
finally {
    Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
}
