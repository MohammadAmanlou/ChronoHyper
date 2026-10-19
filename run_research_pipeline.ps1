param(
  [ValidateSet('pilot','broad','new_hypotheses','finalmatrix','projection','confirmation')]
  [string]$Phase = 'pilot',
  [string]$ChosenMethod = 'native_temporal_08'
)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path '.\src\run.py')) { throw 'Open PowerShell in the ORIGINAL project root (the folder containing src, inputs, requirements.txt).'}
if (-not (Test-Path '.\research_lab\experiment_suite.py')) { throw 'Copy research_lab folder from the upgrade ZIP into the project root.' }
$Python = '.\.venv\Scripts\python.exe'
if (-not (Test-Path $Python)) { throw 'Missing .venv. Run: py -3.11 -m venv .venv; .\.venv\Scripts\python.exe -m pip install -r requirements.txt' }
$env:OPENBLAS_NUM_THREADS='1'
$env:OMP_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
$env:PYTHONHASHSEED='0'

switch ($Phase) {
 'pilot' {
   $out='research_outputs\pilot'
   $methods='semantic_kmeans,native_joint_70,native_temporal_08,incidence_svd'
   $seeds='17'
   $stage='development'
   $extra=@()
 }
 'broad' {
   $out='research_outputs\development_main'
   $methods='semantic_kmeans,native_structure,native_semantic_85,native_balanced_50,native_joint_70,native_structure_75,native_temporal_03,native_temporal_08,native_temporal_20,incidence_svd,frozen_previous'
   $seeds='11,17,29,41,53'
   $stage='development'
   $extra=@()
 }
 'new_hypotheses' {
   $out='research_outputs\new_hypotheses'
   $methods='native_arity_normalized,native_paper_balanced'
   $seeds='11,17,29,41,53'
   $stage='development'
   $extra=@()
 }
 'finalmatrix' {
   $out='research_outputs\final_matrix'
   $methods='semantic_kmeans,native_structure,native_semantic_85,native_balanced_50,native_joint_70,native_structure_75,native_temporal_03,native_temporal_08,native_temporal_20,incidence_svd,frozen_previous,native_arity_normalized,native_paper_balanced'
   $seeds='11,17,29,41,53'
   $stage='development'
   $extra=@()
 }
 'projection' {
   $out='research_outputs\projection_diagnostic'
   $methods='clique_pairwise'
   $seeds='17'
   $stage='development'
   $extra=@('--include-expensive')
 }
 'confirmation' {
   $out='research_outputs\confirmation'
   $methods=$ChosenMethod
   $seeds='11,17,29,41,53'
   $stage='confirmation'
   $extra=@('--lock-file','research_outputs\model_lock.json')
   if (-not (Test-Path 'research_outputs\model_lock.json')) {throw 'Lock method first with: python -m research_lab.lock_selection --development research_outputs/final_matrix --method METHOD_ID --out research_outputs/model_lock.json'}
 }
}
Write-Host "Starting phase: $Phase ; methods: $methods ; seeds: $seeds" -ForegroundColor Cyan
& $Python -m research_lab.experiment_suite --data inputs/data.zip --out $out --years '2020,2022,2024' --seeds $seeds --methods $methods --stage $stage @extra
if ($LASTEXITCODE -ne 0) {
 Write-Warning 'One or more experiments were incomplete. Existing outputs/errors are preserved. Aggregating partial evidence now.'
}
& $Python -m research_lab.aggregate --out $out
if ($LASTEXITCODE -ne 0) {throw 'Aggregation failed. See research_outputs folders and traceback.'}
Write-Host "Results: $out\RESEARCH_COMPARISON_REPORT.md, experiment_registry.csv, all_runs.csv" -ForegroundColor Green
Write-Host 'This does not automatically imply model improvement, an independently heldout test, or a finished submission.'
