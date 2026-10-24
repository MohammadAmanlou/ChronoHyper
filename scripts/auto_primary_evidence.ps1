param(
    [switch] $WithLocalJudge,
    [string] $Model = "qwen3:8b"
)
$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path (Join-Path $PSScriptRoot ".."))
$py = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { throw "Python .venv not found; see README setup." }
$library = ".\local_only\reviews\fulltext_label24\PRIMARY_PAPERS_TO_FILL.csv"
if (-not (Test-Path $library)) {
    throw "28-paper source worksheet missing; prepare existing blind review first."
}
$papers = @(Import-Csv $library)
if ($papers.Count -ne 28) { throw "Expected exactly 28 original source papers." }
if (@($papers | Where-Object { -not $_.source_url }).Count -gt 0) {
    throw "The 28-paper worksheet is missing some source URLs. Import the already downloaded LINKS_DRAFT CSV first."
}
$auto = ".\local_only\reviews\fulltext_label24\AUTO_PRIMARY_EVIDENCE_CANDIDATES.csv"
if (Test-Path $auto) {
    throw "Previous automatically extracted candidate file exists: $auto . Preserve it rather than overwriting. Read its status JSON."
}
& $py -m pip install -r requirements_paper_auto.txt
if ($LASTEXITCODE -ne 0) { throw "Optional PDF dependency installation failed." }
& $py -m research_lab.auto_primary_evidence --project .
if ($LASTEXITCODE -ne 0) { throw "Automated paper retrieval failed; check the error." }
$summary = ".\local_only\reviews\fulltext_label24\AUTO_EVIDENCE_STATUS.json"
if (Test-Path $summary) {
    $r = Get-Content $summary -Raw | ConvertFrom-Json
    Write-Host "Open PDFs:" $r.unique_accessible_pdf_count
    Write-Host "ArXiv v1 date-supported:" $r.arxiv_v1_within_cutoff_count
    Write-Host "Case-paper passage candidates:" $r.candidate_case_paper_passages
}
if ($WithLocalJudge) {
    if (-not (Get-Command "ollama" -ErrorAction SilentlyContinue)) {
        throw "The requested local judge needs an installed and running Ollama with model $Model. Source extraction has succeeded."
    }
    & $py -m research_lab.auto_label_judge --project . --model $Model
    if ($LASTEXITCODE -ne 0) { throw "Local model review failed. Source extraction was retained." }
}
Write-Host "Automatic evidence collection complete. No manual paper text entry required."
Write-Host "Private results: .\local_only\reviews\fulltext_label24\"
