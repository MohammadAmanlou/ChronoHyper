# Run *only* from the ChronoHyper Git root on the user's checked-out main.
# This single script tests, computes new Type-B evidence and pushes only explicitly listed files.
$ErrorActionPreference = 'Stop'
if (-not (Test-Path '.git') -or -not (Test-Path '.\inputs\data.zip')) {
    throw 'Run from C:\Users\a\Desktop\constructor-ckl-research (Git repository root).'
}
$branch = (git branch --show-current).Trim()
if ($LASTEXITCODE -ne 0 -or $branch -ne 'main') {
    throw "Current branch '$branch' is not main. Use git switch main; git pull --ff-only origin main."
}
$trackedChanges = @(git diff --name-only) + @(git diff --cached --name-only)
if ($trackedChanges.Count -gt 0) {
    throw 'Already modified tracked files found. Review git status and save those changes before running.'
}
$py = '.\.venv\Scripts\python.exe'
if (-not (Test-Path $py)) {
    throw 'Missing Python venv. Execute: py -3.11 -m venv .venv; .\.venv\Scripts\python.exe -m pip install -r requirements.txt'
}
if (-not (Test-Path '.\research_lab\type_b_source_audit.py') -or -not (Test-Path '.\research_lab\test_type_b_source_audit.py')) {
    throw 'The add-on ZIP must be extracted into the repository root (not inside another subfolder).'
}
$env:OPENBLAS_NUM_THREADS = '1'
$env:OMP_NUM_THREADS = '1'
function Check([string]$title, [string[]]$arg) {
    Write-Host "`n>> $title" -ForegroundColor Cyan
    & $py @arg
    if ($LASTEXITCODE -ne 0) { throw "$title FAILED; no Git commit or push attempted." }
}
Check 'Original 10 tests' @('-m','unittest','discover','-s','tests','-v')
Check 'Research lab: 5 + 7 V2 + 3 Type-B tests' @('-m','unittest','research_lab.tests_lab','research_lab.test_label_v2','research_lab.test_type_b_source_audit','-v')
Check 'All four hierarchy snapshots' @('verify_selected_outputs.py','--out','outputs_selected')
Check 'Rank papers without reading answer gold' @('-m','research_lab.type_b_source_audit','rank','--project','.','--out','research_outputs/type_b_audit')
Check 'Score the FROZEN paper ranking against gold source references' @('-m','research_lab.type_b_source_audit','score','--project','.','--out','research_outputs/type_b_audit')
Check 'Certify top-5 flat/hierarchical equivalence and compare runtimes' @('upgrade_scripts/certified_retrieval.py','--project','.','--out','research_outputs/type_b_audit/certified_retrieval_audit.json','--year','2025')
Check 'Final evidence preflight (warnings preserved)' @('final_preflight.py','--project','.','--write','research_outputs/type_b_audit/final_preflight_after_t6.json')
# Check the source-only claim and blank human-review rubric independently.
@'
import csv,json,pathlib
root=pathlib.Path('research_outputs/type_b_audit')
rank=json.loads((root/'frozen_rankings.json').read_text(encoding='utf-8'))
res=json.loads((root/'type_b_source_scores.json').read_text(encoding='utf-8'))
with (root/'CLAIM_LEVEL_REVIEW_BLANK.csv').open(encoding='utf-8-sig',newline='') as f:
 rows=list(csv.DictReader(f))
assert rank['gold_was_not_opened'] is True and len(rank['questions'])==4
assert res['n_type_b']==4 and res['claim_answer_accuracy_measured'] is False
assert len(rows)==36
assert all(not (str(v).strip()) for row in rows for k,v in row.items() if k.startswith('manual_'))
print('CHECK OK: 4 Type-B rankings, 36 UNRATED claim rows, no fabricated answer correctness')
'@ | & $py -
if ($LASTEXITCODE -ne 0) { throw 'The 4-question / 36-claim sanity check failed.' }
$files = @(
  'scripts/run_t6_and_push_main.ps1',
  'research_lab/type_b_source_audit.py',
  'research_lab/test_type_b_source_audit.py',
  'research_outputs/type_b_audit/frozen_rankings.json',
  'research_outputs/type_b_audit/type_b_source_scores.json',
  'research_outputs/type_b_audit/CLAIM_LEVEL_REVIEW_BLANK.csv',
  'research_outputs/type_b_audit/certified_retrieval_audit.json',
  'research_outputs/type_b_audit/final_preflight_after_t6.json'
)
foreach ($f in $files) { if (-not (Test-Path $f)) { throw "Missing expected artifact: $f" } }
git add -- $files
if ($LASTEXITCODE -ne 0) { throw 'git add failed' }
$names = @(git diff --cached --name-only)
if ($names -contains 'research_outputs/label_v2/BLIND_KEY_KEEP_SEPARATE.json') { throw 'Human review unblinding key must not be committed!' }
Write-Host "`nThese eight auditable files are staged:" -ForegroundColor Green
git diff --cached --stat
if ($names.Count -eq 0) { Write-Host 'Nothing new to commit. Checking remote'; git push origin main; exit $LASTEXITCODE }
git commit -m 'Complete Type-B source retrieval audit and reproducibility checks'
if ($LASTEXITCODE -ne 0) { throw 'Commit failed; no push attempted' }
git push origin main
if ($LASTEXITCODE -ne 0) { throw 'Push failed; local commit is safe. Resolve remote conflict before trying again.' }
Write-Host "`nCOMPLETE: Type-B experiment and evidence now published to PRIVATE GitHub main." -ForegroundColor Green
Write-Host 'IMPORTANT: 36 source-entailment ratings and 24 V2 label ratings still require real human review.'
