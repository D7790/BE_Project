"""Small synchronous ctypes adapter for KiCad's installed ngspice shared DLL.
API reference: https://ngspice.sourceforge.io/shared.html and sharedspice.h.
No hardware access. One library instance per process; copy vectors before destroy.
"""
import ctypes as c
import os
from pathlib import Path

class Vector(c.Structure):
    _fields_=[('name',c.c_char_p),('type',c.c_int),('flags',c.c_short),
              ('real',c.POINTER(c.c_double)),('complex',c.c_void_p),('length',c.c_int)]

class Spice:
    def __init__(self, dll=None):
        dll=Path(dll or os.environ.get('NGSPICE_DLL',r'C:\Program Files\KiCad\10.0\bin\ngspice.dll'))
        self.directory=os.add_dll_directory(str(dll.parent))
        self.lib=c.CDLL(str(dll)); self.log=[]; self.exits=[]
        output=c.CFUNCTYPE(c.c_int,c.c_char_p,c.c_int,c.c_void_p)
        exit_type=c.CFUNCTYPE(c.c_int,c.c_int,c.c_bool,c.c_bool,c.c_int,c.c_void_p)
        def receive(s,ident,user):
            self.log.append(s.decode(errors='replace')); return 0
        def exited(status,immediate,quit,ident,user):
            self.exits.append((status,quit)); return 0
        self.output=output(receive); self.status=output(lambda *args:0); self.exit=exit_type(exited)
        self.lib.ngSpice_Init.argtypes=[c.c_void_p]*7
        self.lib.ngSpice_Init.restype=c.c_int
        assert self.lib.ngSpice_Init(self.output,self.status,self.exit,None,None,None,None)==0
        self.lib.ngSpice_Command.argtypes=[c.c_char_p]; self.lib.ngSpice_Command.restype=c.c_int
        self.lib.ngSpice_Circ.argtypes=[c.POINTER(c.c_char_p)]; self.lib.ngSpice_Circ.restype=c.c_int
        self.lib.ngGet_Vec_Info.argtypes=[c.c_char_p]; self.lib.ngGet_Vec_Info.restype=c.POINTER(Vector)
        self.command('set noaskquit'); self.command('version')
        self.version_log=list(self.log)

    def command(self,command):
        code=self.lib.ngSpice_Command(command.encode())
        if code: raise RuntimeError(f'ngspice command failed ({code}): {command}\n'+ '\n'.join(self.log[-20:]))

    def run(self,netlist,vectors):
        self.command('destroy all'); self.log=[]; self.exits=[]
        lines=[line.encode() for line in netlist.strip().splitlines()]
        data=(c.c_char_p*(len(lines)+1))(*lines,None)
        assert self.lib.ngSpice_Circ(data)==0, '\n'.join(self.log)
        self.command('run')
        errors=[s for s in self.log if any(t in s.lower() for t in ['error:', 'timestep too small','fatal error','simulation interrupted'])]
        if errors or self.exits: raise RuntimeError('\n'.join(self.log))
        result={}
        for name in vectors:
            ptr=self.lib.ngGet_Vec_Info(name.encode())
            if not ptr or ptr.contents.length<1 or not ptr.contents.real:
                raise RuntimeError('Missing real vector '+name+'\n'+'\n'.join(self.log))
            vec=ptr.contents
            result[name]=[vec.real[i] for i in range(vec.length)]
        return result
