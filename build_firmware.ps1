param([ValidateSet('esp32dev','bringup')][string]$Environment = 'esp32dev')
$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
$actualCore = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".local\platformio"))
New-Item -ItemType Directory -Path $actualCore -Force | Out-Null
# A short alias avoids Windows compiler process/command-path failures.
# All package files remain inside this project's .local directory.
$shortCore = Join-Path $env:USERPROFILE ".ws-pio"
if (Test-Path -LiteralPath $shortCore) {
    $existingAlias = Get-Item -LiteralPath $shortCore -Force
    if ($existingAlias.LinkType -ne "Junction" -or
        [IO.Path]::GetFullPath([string]$existingAlias.Target) -ne $actualCore) {
        throw "The short build alias $shortCore belongs to another location. Choose a different short alias in this script; do not overwrite it."
    }
} else {
    New-Item -ItemType Junction -Path $shortCore -Target $actualCore | Out-Null
}
$env:PLATFORMIO_CORE_DIR = $shortCore
& ".\.venv\Scripts\python.exe" -m platformio run --project-dir firmware --environment $Environment -j 2
exit $LASTEXITCODE
