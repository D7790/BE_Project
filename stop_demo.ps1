$ErrorActionPreference = "Stop"
$dashboardPidFile = Join-Path $PSScriptRoot ".local\dashboard.pid"
if (!(Test-Path -LiteralPath $dashboardPidFile)) {
    Write-Output "No background dashboard PID is recorded. For a terminal-launched server, press Ctrl+C in that terminal."
    exit 0
}
$dashboardProcessId = [int](Get-Content -LiteralPath $dashboardPidFile)
$dashboardProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $dashboardProcessId" -ErrorAction SilentlyContinue
$expectedPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (!$dashboardProcess -or !$dashboardProcess.CommandLine.Contains($expectedPython) -or
    $dashboardProcess.CommandLine -notlike "*-m wattsense.server*") {
    Write-Output "The recorded dashboard process is no longer running. No process was stopped."
    exit 0
}
$dashboardChildren = Get-CimInstance Win32_Process | Where-Object {
    $_.ParentProcessId -eq $dashboardProcessId -and $_.CommandLine -like "*-m wattsense.server*"
}
foreach ($dashboardChild in $dashboardChildren) {
    Stop-Process -Id $dashboardChild.ProcessId -ErrorAction SilentlyContinue
}
Stop-Process -Id $dashboardProcessId -ErrorAction SilentlyContinue
Write-Output "Background Wattsense dashboard stopped."

