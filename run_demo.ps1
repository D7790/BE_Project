$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
$projectPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (Test-Path -LiteralPath $projectPython) {
    & $projectPython -m wattsense.server --mode simulated
} else {
    python -m wattsense.server --mode simulated
}

