"""Portable process orchestration; preserves native stderr without PowerShell traps."""
from pathlib import Path
import datetime,hashlib,json,subprocess,sys
root=Path(__file__).resolve().parents[1]; out=root/'simulations/results';out.mkdir(exist_ok=True)
commands=[('python-tests',['-m','unittest','discover','-s','tests','-v'])]
commands += [(name,['simulations/'+name+'.py']) for name in ['run_firmware_host_tests','run_spice','run_system','run_hardware','make_plots','make_hardware_plots']]
report={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'RUNNING','hardware_tested':False,'checks':[]}
path=out/'suite-summary.json';path.write_text(json.dumps(report,indent=2))
for name,args in commands:
    with (out/(name+'.log')).open('w',encoding='utf-8') as log:
        result=subprocess.run([sys.executable,*args],cwd=root,stdout=log,stderr=subprocess.STDOUT)
    report['checks'].append({'name':name,'exit_code':result.returncode,'log':name+'.log'})
    if result.returncode:
        report['status']='FAIL';path.write_text(json.dumps(report,indent=2))
        print((out/(name+'.log')).read_text(encoding='utf-8'));sys.exit(result.returncode)
    print('Passed: '+name,flush=True)
report['status']='PASS';report['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
sources=list((root/'wattsense').glob('*.py'))+list((root/'tests').glob('*.py'))+list((root/'simulations').glob('*.py'))+list((root/'firmware/include').glob('*.h'))+list((root/'firmware/src').glob('*.cpp'))+list((root/'simulations').glob('*.cpp'))+[root/'firmware/platformio.ini']
sources += [p for p in (root/'web').iterdir() if p.suffix in ('.js','.css','.html')]
sources += [root/'simulations/hardware-assumptions.json']
report['source_sha256']={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
path.write_text(json.dumps(report,indent=2))
print('Simulation suite passed. Results are synthetic, not hardware measurements.')
