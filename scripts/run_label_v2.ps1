$ErrorActionPreference = 'Stop'
if (-not (Test-Path '.\inputs\data.zip')) { throw 'Run from ChronoHyper repository root.' }
$py = '.\.venv\Scripts\python.exe'
if (-not (Test-Path $py)) { throw 'Missing virtual environment; create one using README.md.' }
& $py -m unittest research_lab.test_label_v2 -v
if ($LASTEXITCODE -ne 0) { throw 'V2 tests failed' }
& $py -m research_lab.label_v2 --project . --out research_outputs/label_v2
if ($LASTEXITCODE -ne 0) { throw 'Label V2 generation failed' }
Write-Host 'V2 outputs generated. Reviewer judgments NOT YET present.'
Write-Host 'Share ONLY BLIND_LABEL_COMPARISON_TO_FILL.csv with an actual reviewer.'
