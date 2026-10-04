from pathlib import Path
root=Path('D:\\academics and projects\\BE_final_year_project\\hardware\\pcb\\wattsense-main-revB-4layer')
out=Path('D:\\academics and projects\\BE_final_year_project\\docs\\evidence\\recheck-2026-09-30\\hardware')
script=(root/'tools/audit_design.py').read_text()
for name in ['schematic.net.xml','erc.json','drc.json','connectivity-audit.json']:
    script=script.replace("ROOT/'reports'/"+repr(name), "Path("+repr(str(out/name))+")")
exec(compile(script,str(root/'tools/audit_design.py'),'exec'),{'__file__':str(root/'tools/audit_design.py')})
script=(root/'tools/check_power_paths.py').read_text()
script=script.replace("root/'reports/power-path-audit.json'", "Path("+repr(str(out/'power-path-audit.json'))+")")
exec(compile(script,str(root/'tools/check_power_paths.py'),'exec'),{'__file__':str(root/'tools/check_power_paths.py')})
