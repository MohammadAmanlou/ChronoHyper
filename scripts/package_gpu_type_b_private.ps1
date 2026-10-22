# Private Type-B generation package for Kaggle/remote GPU.
# Only necessary original science source archive + user-reviewed dated passages.
[CmdletBinding()]
param([string]$Output="local_only\gpu_type_b_private.zip")
$ErrorActionPreference="Stop"
$root=(Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$dest=Join-Path $root $Output
$work=Join-Path $root "local_only\type_b_gpu_stage"
if (Test-Path $dest) {throw "Existing package protected: $dest"}
if (Test-Path $work) {throw "Existing staging directory protected: $work"}
$allow=@(
 "research_lab\__init__.py",
 "research_lab\type_b_answer_generation.py",
 "inputs\data.zip",
 "requirements_advanced.txt",
 "local_only\type_b_generation\SOURCE_PASSAGES_TO_FILL.csv"
)
New-Item -ItemType Directory -Force $work | Out-Null
try {
 foreach($path in $allow){
  $source=Join-Path $root $path
  if (-not (Test-Path $source)){throw "Missing evidence file: $source"}
  $target=Join-Path $work $path
  New-Item -ItemType Directory -Force (Split-Path -Parent $target) | Out-Null
  Copy-Item -LiteralPath $source -Destination $target
 }
 $py=Join-Path $root ".venv\Scripts\python.exe"
 & $py -c "from research_lab.type_b_answer_generation import validated_passages; p,r=validated_passages('.');print('Verified formatted fulltext passage rows:',len(r))"
 if ($LASTEXITCODE -ne 0){throw "Missing or malformed fulltext evidence; no GPU bundle created"}
 New-Item -ItemType Directory -Force (Split-Path -Parent $dest) | Out-Null
 Compress-Archive -Path (Join-Path $work '*') -DestinationPath $dest -CompressionLevel Optimal
 Write-Host "PRIVATE PRIMARY-SOURCE PASSAGE DATA - DO NOT PUBLISH:" $dest
 Get-FileHash -Algorithm SHA256 $dest | Format-Table
}
finally {Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue}
