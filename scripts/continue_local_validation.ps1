# Continue the local-only ChronoHyper validation after a safe git pull.
# Run from anywhere: powershell -ExecutionPolicy Bypass -File .\scripts\continue_local_validation.ps1
# Never overwrites canonical research outputs or blind reviewer packets.
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $root ".venv\Scripts\python.exe"
$local = Join-Path $root "local_only"
$review = Join-Path $local "reviews\label_v3_fresh"
$retrieval = Join-Path $local "retrieval_v2\rankings.json"
$v3summary = Join-Path $local "label_v3_dev\summary.json"
$preflight = Join-Path $local "final_preflight.json"

function Run-Python {
    param([string[]]$Arguments)
    & $python @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed (exit $LASTEXITCODE): $($Arguments -join ' ')"
    }
}

Push-Location $root
try {
    if (-not (Test-Path (Join-Path $root ".git"))) {
        throw "Not a Git repository: $root"
    }
    if (-not (Test-Path $python)) {
        throw "Python virtual environment not found: $python"
    }
    foreach ($name in @("research_lab\label_v3.py", "research_lab\label_v3_blind.py", "research_lab\retrieval_v2.py")) {
        if (-not (Test-Path (Join-Path $root $name))) {
            throw "Missing new research module ($name). First move any untracked research_outputs/fresh_semantic into ignored local_only/saved_artifacts and run git pull --ff-only origin main."
        }
    }
    $branch = (& git branch --show-current).Trim()
    if ($LASTEXITCODE -ne 0 -or $branch -ne "main") {
        throw "Expected checked-out main branch; current branch: $branch"
    }
    $deletedTracked = @(& git ls-files --deleted)
    if ($LASTEXITCODE -ne 0) { throw "Cannot audit tracked files" }
    if ($deletedTracked.Count -gt 0) {
        throw "Tracked files are missing; inspect git status and restore only the intended paths before validation: $($deletedTracked -join ', ')"
    }
    New-Item -ItemType Directory -Force $local | Out-Null
    $env:OPENBLAS_NUM_THREADS = "1"
    $env:OMP_NUM_THREADS = "1"

    Write-Host "[1/6] Core tests"
    Run-Python @("-m","unittest","discover","-s","tests","-v")
    Write-Host "[2/6] Research tests"
    Run-Python @("-m","unittest","research_lab.tests_lab","research_lab.test_label_v2","research_lab.test_type_b_source_audit","-v")
    Write-Host "[2b/6] Test retrieval budget frontier"
    Run-Python @("-m","unittest","research_lab.test_retrieval_frontier","research_lab.test_frontier_historical","-v")
    Write-Host "[3/6] Validate frozen selected outputs"
    Run-Python @("verify_selected_outputs.py","--out","outputs_selected")

    Write-Host "[4/6] Generate general V3 development-only labels (180 cases)"
    if (-not (Test-Path $v3summary)) {
        Run-Python @("-m","research_lab.label_v3","--project",".","--out",".\local_only\label_v3_dev")
    } else {
        Write-Host "Existing V3 development summary retained: $v3summary"
    }
    Write-Host "[5/6] Run gold-separated retrieval V2 diagnostics"
    if (-not (Test-Path $retrieval)) {
        Run-Python @("-m","research_lab.retrieval_v2","--project",".","--rank")
    } else {
        Write-Host "Existing retrieval rankings retained: $retrieval"
    }

    # A partial existing packet should never be silently rewritten.
    $packet = Join-Path $review "blind_v2_v3_24.csv"
    $key = Join-Path $review "mapping_PRIVATE.csv"
    if ((Test-Path $packet) -xor (Test-Path $key)) {
        throw "Incomplete existing blind V2/V3 packet. Preserve local files and inspect manually before regenerating."
    }
    if ((Test-Path $packet) -and (Test-Path $key)) {
        Write-Host "Existing blind V2/V3 packet and PRIVATE key preserved."
    } else {
        Write-Host "Preparing new local-only blind V2/V3 packet (NOT scoring it)."
        Run-Python @("-m","research_lab.label_v3_blind","--project",".","--prepare")
    }

    Write-Host "[5b/6] Measure matched 1/2/4/8/12-root retrieval frontier (no gold)"
    $frontier = Join-Path $local "retrieval_frontier\rankings.json"
    if (-not (Test-Path $frontier)) {
        Run-Python @("-m","research_lab.retrieval_frontier","--project",".","--rank")
    } else {
        Write-Host "Existing local frontier retained: $frontier"
    }
    Write-Host "[5c/6] Freeze then score historical Type-A queries with original ZIP gold (development only)"
    $histRoot = Join-Path $local "retrieval_frontier\historical_v2"
    $histReport = Join-Path $histRoot "historical_audit.json"
    if (-not (Test-Path $histReport)) {
        Run-Python @("-m","research_lab.frontier_historical","--project",".","--prepare")
        Run-Python @("-m","research_lab.frontier_historical","--project",".","--evaluate")
    } else {
        Write-Host "Existing historical audit retained: $histReport"
    }
    Write-Host "[6/6] Read-only final preflight (scientific WARN entries are expected)"
    Run-Python @("final_preflight.py","--project",".","--write",".\local_only\final_preflight.json")
    $audit = Get-Content -LiteralPath $preflight -Raw | ConvertFrom-Json
    $v3 = Get-Content -LiteralPath $v3summary -Raw | ConvertFrom-Json
    $head = (& git rev-parse --short HEAD).Trim()
    $status = [ordered]@{
        git_commit = $head
        core_and_research_tests_completed = $true
        frozen_selected_output_verification_completed = $true
        label_v3_development_cases = 180
        v3_development_summary = "local_only/label_v3_dev/summary.json"
        retrieval_rankings = "local_only/retrieval_v2/rankings.json"
        retrieval_frontier_rankings = "local_only/retrieval_frontier/rankings.json"
        historical_frontier_audit = "local_only/retrieval_frontier/historical_v2/historical_audit.json"
        historical_frontier_plot = "local_only/retrieval_frontier/historical_v2/historical_quality_cost.svg"
        historical_frontier_is_independent_test = $false
        blind_review_packet = "local_only/reviews/label_v3_fresh/blind_v2_v3_24.csv"
        private_blind_key = "local_only/reviews/label_v3_fresh/mapping_PRIVATE.csv"
        independent_v3_review_completed = $false
        preflight_blocking_count = @($audit.blocking_items).Count
        preflight_scientific_warning_count = @($audit.qualifications).Count
        ready_for_submission_without_caveat = $audit.ready_for_submission_without_caveat
    }
    $statusFile = Join-Path $local "next_stage_status.json"
    $status | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $statusFile -Encoding UTF8
    Write-Host "Saved local status: $statusFile"
    Write-Host "Next action: review historical frontier output and arrange an authorized independent, key-isolated scientific label evaluation. Never upload mapping_PRIVATE.csv."
    Write-Host "Git status (local_only is ignored):"
    & git status --short
}
finally {
    Pop-Location
}
