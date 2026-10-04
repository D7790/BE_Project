$ErrorActionPreference = 'Stop'
$cadManager = 'C:\Program Files\KiCad\10.0\bin\kicad.exe'
$cadProject = Join-Path $PSScriptRoot 'wattsense-main.kicad_pro'
if (!(Test-Path -LiteralPath $cadManager)) { throw 'KiCad 10 was not found at the configured path. Open wattsense-main.kicad_pro manually in KiCad.' }
# This launches the interactive editor the user requested.
Start-Process -FilePath $cadManager -ArgumentList ('"' + $cadProject + '"')
