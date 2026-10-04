$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    $simulationPython = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
    if (-not (Test-Path -LiteralPath $simulationPython)) { throw 'Create the project virtual environment first; see README.md.' }
    & $simulationPython 'simulations/run_all.py'
    if ($LASTEXITCODE -ne 0) { throw 'Simulation suite failed. See the named log in simulations/results.' }
} finally { Pop-Location }
