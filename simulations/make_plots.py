"""Standalone figures from saved simulation CSVs. Requires matplotlib."""
from pathlib import Path
import csv,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent; OUT=ROOT/'results'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
def read(name):
    with (OUT/(name+'.csv')).open() as f:return list(csv.DictReader(f))
def column(rows,name):return [float(r[name]) for r in rows]
def finish(fig,name):
    fig.savefig(OUT/(name+'.png'),dpi=180,bbox_inches='tight')
    fig.savefig(OUT/(name+'.svg'),bbox_inches='tight');plt.close(fig)

base=read('runtime_baseline');priority=read('runtime_priority')
fig,axes=plt.subplots(2,1,figsize=(9,7),sharex=True,layout='constrained')
for rows,label,color in [(base,'All loads retained','#b9553c'),(priority,'Priority controller','#087e8b')]:
    x=[t/3600 for t in column(rows,'time_s')]
    axes[0].plot(x,column(rows,'true_soc_pct'),label=label,color=color,lw=2.2)
    axes[1].step(x,column(rows,'load_input_W'),where='post',label=label,color=color,lw=2.2)
axes[0].axhline(20,ls='--',color='#7a8190');axes[0].set_ylabel('Model charge (%)');axes[0].legend()
axes[1].set_ylabel('Converter input power (W)');axes[1].set_xlabel('Elapsed model time (hours)')
for ax in axes:ax.grid(alpha=.2)
fig.suptitle('Wattsense runtime comparison — SIMULATION ONLY',fontweight='bold')
fig.supxlabel('6 Ah, 12.8 V ideal battery; 68% initial charge; 20% reserve; 90% converter efficiency\n3 W lamp + 3 W optional fan + 0.8 W controller. Longer lamp service comes from switching off the fan.',fontsize=9)
finish(fig,'runtime-comparison')

fig,ax=plt.subplots(figsize=(9,5),layout='constrained')
for resistance,color in [(4700,'#b9553c'),(2200,'#087e8b')]:
    data=read(f'i2c_rise_{resistance}ohm_400pF')
    ax.plot([(t-1e-6)*1e6 for t in column(data,'time')],column(data,'v(sda)'),color=color,lw=2,label=f'{resistance/1000:g} kΩ / 400 pF')
ax.axhline(.3*3.3,ls=':',color='#7a8190');ax.axhline(.7*3.3,ls=':',color='#7a8190')
ax.set(xlim=(0,5),xlabel='Time after releasing SDA (µs)',ylabel='Bus voltage (V)',title='I²C pull-up revision — ngspice reduced RC model')
ax.legend();ax.grid(alpha=.2)
fig.supxlabel('30%–70% rise: Rev A 1.593 µs; Rev B 0.746 µs. Standard-mode limit: 1.000 µs.\nAssumed total capacitance, not measured cable performance.',fontsize=9)
finish(fig,'i2c-pullup-comparison')

data=read('fan_switch_transient');x=[t*1000 for t in column(data,'time')]
fig,axes=plt.subplots(2,1,figsize=(9,6),sharex=True,layout='constrained')
axes[0].plot(x,column(data,'v(fan_gate)'),label='Gate',color='#087e8b');axes[0].plot(x,column(data,'v(fan_return)'),label='Drain',color='#b9553c');axes[0].legend();axes[0].set_ylabel('Voltage (V)')
axes[1].plot(x,column(data,'i(lfan)'),color='#5a46a0');axes[1].set(xlabel='Time (ms)',ylabel='Load current (A)')
for ax in axes:ax.grid(alpha=.2)
fig.suptitle('Fan switching and flyback — behavioural SPICE model',fontweight='bold')
fig.supxlabel('48 mΩ switch; assumed 1 nF gate, 1 mH / 8.333 Ω load and generic diode.\nNot an AO3400A vendor model or BLDC fan model; parasitic spikes and temperature are not predicted.',fontsize=9)
finish(fig,'fan-transient')

print('Generated PNG and SVG figures: runtime-comparison, i2c-pullup-comparison, fan-transient.')
