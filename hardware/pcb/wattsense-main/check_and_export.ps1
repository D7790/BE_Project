$ErrorActionPreference = 'Stop'
$cadCli = 'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'
$cadPython = 'C:\Program Files\KiCad\10.0\bin\python.exe'
function Invoke-Cad {
    param([string[]]$CadArguments)
    & $cadCli @CadArguments
    if ($LASTEXITCODE -ne 0) { throw ('KiCad command failed: ' + ($CadArguments -join ' ')) }
}
Push-Location $PSScriptRoot
try {
    Invoke-Cad -CadArguments @('sch','erc','wattsense-main.kicad_sch','--format','json','--exit-code-violations','-o','reports/erc.json')
    Invoke-Cad -CadArguments @('pcb','drc','wattsense-main.kicad_pcb','--schematic-parity','--format','json','--exit-code-violations','--refill-zones','--save-board','-o','reports/drc.json')
    Invoke-Cad -CadArguments @('sch','export','netlist','wattsense-main.kicad_sch','--format','kicadxml','-o','reports/schematic.net.xml')
    & $cadPython 'tools/audit_design.py'
    if ($LASTEXITCODE -ne 0) { throw 'Connectivity audit failed. No fresh fabrication archive was produced.' }
    Invoke-Cad -CadArguments @('pcb','export','gerbers','wattsense-main.kicad_pcb','-o','exports/gerbers/','-l','F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts')
    Invoke-Cad -CadArguments @('pcb','export','drill','wattsense-main.kicad_pcb','-o','exports/gerbers/','--excellon-separate-th','--generate-report','--report-path','reports/drill-report.txt')
    Invoke-Cad -CadArguments @('pcb','export','svg','wattsense-main.kicad_pcb','-o','exports/assembly-top-1to1.svg','-l','F.Fab,F.Silkscreen,Edge.Cuts','--sketch-pads-on-fab-layers','--mode-single','--fit-page-to-board','--exclude-drawing-sheet','--black-and-white','--scale','1')
    Invoke-Cad -CadArguments @('sch','export','pdf','wattsense-main.kicad_sch','-o','exports/schematic.pdf')
    & $cadPython 'tools/package_fabrication.py'
    if ($LASTEXITCODE -ne 0) { throw 'Fabrication archive validation failed.' }
    Write-Output 'Checks and fabrication exports completed. These checks do not validate assembled hardware.'
} finally { Pop-Location }
