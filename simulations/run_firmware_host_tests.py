"""Compile/run production policy on host, using isolated copies of config.h.
The real firmware configuration remains hardware-locked throughout.
"""
from pathlib import Path
import hashlib,json,os,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1]
tool=ROOT/'.local/platformio/packages/toolchain-gccmingw32'
compilers=list(tool.rglob('g++.exe'))
assert compilers,'Install platformio/toolchain-gccmingw32 in the project-local PlatformIO core first.'
compiler=compilers[0]
production=(ROOT/'firmware/include/config.h').read_text()
assert 'constexpr bool HARDWARE_CONFIRMED = false;' in production
results=[]
for armed in [False,True]:
    work=ROOT/'.local/host-policy-tests'/('armed-copy' if armed else 'production-locked')
    work.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'firmware/include/controller.h',work/'controller.h')
    shutil.copy2(ROOT/'simulations/firmware_policy_tests.cpp',work/'tests.cpp')
    config=production.replace('constexpr bool HARDWARE_CONFIRMED = false;','constexpr bool HARDWARE_CONFIRMED = true;') if armed else production
    (work/'config.h').write_text(config)
    env=os.environ.copy(); env['PATH']=str(compiler.parent)+os.pathsep+env.get('PATH','')
    command=[str(compiler),'-std=c++11','-O2','-Wall','-Wextra','-include','initializer_list','-static-libgcc','-static-libstdc++','tests.cpp','-o','policy-tests.exe']
    subprocess.run(command,cwd=work,env=env,check=True)
    ran=subprocess.run([str(work/'policy-tests.exe')],cwd=work,env=env,capture_output=True,text=True)
    if ran.returncode:
        raise RuntimeError(ran.stderr or ran.stdout or f'Host test exited {ran.returncode}')
    results.append(json.loads(ran.stdout)); print(ran.stdout.strip())
work=ROOT/'.local/host-policy-tests/register-reader'; work.mkdir(parents=True,exist_ok=True)
shutil.copy2(ROOT/'firmware/include/ina219_checked.h',work/'ina219_checked.h')
shutil.copy2(ROOT/'simulations/ina219_register_tests.cpp',work/'tests.cpp')
env=os.environ.copy();env['PATH']=str(compiler.parent)+os.pathsep+env.get('PATH','')
subprocess.run([str(compiler),'-std=c++11','-O2','-Wall','-Wextra','-static-libgcc','-static-libstdc++','tests.cpp','-o','register-tests.exe'],cwd=work,env=env,check=True)
ran=subprocess.run([str(work/'register-tests.exe')],cwd=work,env=env,capture_output=True,text=True)
if ran.returncode: raise RuntimeError(ran.stderr or ran.stdout)
register_result=json.loads(ran.stdout); print(ran.stdout.strip())
assert (ROOT/'firmware/include/config.h').read_text()==production
result={'scope':'Host execution of production C++ policy and register decoder with a fake transaction source. Not ESP32, electrical I2C, GPIO or timing emulation.','results':results,'register_reader':register_result,
        'compiler':subprocess.check_output([str(compiler),'--version'],text=True).splitlines()[0],
        'production_hardware_confirmed':False,'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'firmware/include/controller.h',ROOT/'firmware/include/config.h',ROOT/'firmware/include/ina219_checked.h',ROOT/'simulations/firmware_policy_tests.cpp',ROOT/'simulations/ina219_register_tests.cpp']}}
(ROOT/'simulations/results/firmware-host-summary.json').write_text(json.dumps(result,indent=2))
