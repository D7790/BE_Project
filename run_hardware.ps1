param([Parameter(Mandatory = $true)][string]$SerialPort)
$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
$projectPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (!(Test-Path -LiteralPath $projectPython)) {
    throw "Create .venv and install requirements.txt first. See README.md."
}
& $projectPython -m wattsense.server --mode hardware --serial-port $SerialPort
