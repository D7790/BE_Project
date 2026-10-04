"""Export standalone figures and a result table from the saved hardware model."""
from pathlib import Path
import csv
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'simulations/results'
D = json.loads((OUT / 'hardware-summary.json').read_text())
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                     'axes.spines.top': False, 'axes.spines.right': False})


def read(name):
    with (OUT / (name + '.csv')).open() as f:
        return list(csv.DictReader(f))


def col(rows, key, factor=1):
    return [float(row[key]) * factor for row in rows]


def finish(fig, name):
    fig.savefig(OUT / (name + '.png'), dpi=180, bbox_inches='tight')
    fig.savefig(OUT / (name + '.svg'), bbox_inches='tight')
    plt.close(fig)


fig, axes = plt.subplots(2, 1, figsize=(9, 7), sharex=True, layout='constrained')
for name, label, color in [('hardware-runtime-baseline', 'Both loads retained', '#a64931'),
                            ('hardware-runtime-priority', 'Priority: fan shed', '#007d87')]:
    rows = read(name)
    x = col(rows, 'time_s', 1 / 3600)
    axes[0].plot(x, col(rows, 'true_soc_pct'), label=label, color=color, lw=2.3)
    axes[1].step(x, col(rows, 'delivered_w'), where='pre', color=color, lw=2.3)
axes[0].axhline(D['baseline']['reserve_pct'], color='#707780', ls='--')
axes[0].set_ylabel('Model charge (%)')
axes[0].legend()
axes[1].set(xlabel='Elapsed model time (hours)', ylabel='Delivered load power (W)')
for ax in axes:
    ax.grid(alpha=.2)
b, p = D['baseline'], D['priority']
fig.suptitle(f"Loss-aware simulation: lamp service {b['runtime_to_common_endpoint_h']:.2f} h → {p['runtime_to_common_endpoint_h']:.2f} h", fontweight='bold')
fig.supxlabel(f"SIMULATION ONLY · {b['lamp_delivered_w']:g} W lamp + {b['fan_delivered_w']:g} W fan + {b['controller_delivered_w']:g} W controller; {b['capacity_ah']:g} Ah; "
              f"{b['initial_soc_pct']:g}% start → {b['reserve_pct']:g}% reserve\n"
              f"{100*b['efficiency']:g}% assumed converter efficiency, illustrative battery curve and resistances. Fan service is sacrificed.", fontsize=9)
finish(fig, 'hardware-runtime')

fig, axes = plt.subplots(2, 1, figsize=(9, 7), layout='constrained')
series = [
    ('startup_starter_2x_2A', 'Starter: 1.0 A start / 2 A source / 470 µF', '#007d87', '-'),
    ('startup_2x_2A', '1.2 A start / 2 A source / 470 µF', '#5b4a91', '-'),
    ('startup_3x_1_5A', '1.8 A start / 1.5 A source / 470 µF', '#b14a31', '-'),
    ('startup_3x_1_5A_large_cap', '1.8 A start / 1.5 A source / 2200 µF', '#a57b18', '--'),
    ('startup_3x_3A', '1.8 A start / 3 A source / 470 µF', '#527643', ':')]
for name, label, color, style in series:
    rows = read(name)
    x = [(float(row['time']) - .01) * 1000 for row in rows]
    for ax in axes:
        ax.plot(x, col(rows, 'v(rail)'), label=label, color=color, ls=style, lw=2)
axes[0].legend(fontsize=8.5, loc='lower right')
axes[0].set(xlim=(-5, 130), ylabel='5 V common rail (V)', xlabel='Time after fan command (ms)')
axes[1].set(xlim=(-.2, 4), ylabel='5 V common rail (V)', xlabel='Startup detail (ms)')
for ax in axes:
    ax.axhline(4.75, color='#707780', ls='--', lw=1)
    ax.grid(alpha=.2)
fig.suptitle('Fan startup can pull down the shared supply', fontweight='bold')
fig.supxlabel('BEHAVIOURAL SPICE ONLY · Assumed 100 ms surge; dashed horizontal line = provisional 4.75 V screen\nThis does not predict an actual fan, converter loop, fuse trip or ESP32 brownout threshold.', fontsize=9)
finish(fig, 'hardware-startup')

row = next(r for r in D['dc_cases'] if r['case'] == 'starter_2_5W_each')
keys = ['converter_loss_w', 'output_path_loss_w', 'two_shunts_loss_w', 'battery_internal_loss_w', 'hv_wire_loss_w', 'hv_copper_loss_w']
labels = ['Converter', '5 V wiring + fuses + copper + MOSFET', 'Two current-sense shunts', 'Battery/BMS equivalent resistance', 'Battery-side wiring and external fuse', 'Battery-side selected copper paths']
fig, ax = plt.subplots(figsize=(9, 4.7), layout='constrained')
bars = ax.barh(labels, [row[k] for k in keys], color='#007d87')
ax.invert_yaxis()
ax.bar_label(bars, labels=[f'{row[k]:.3f} W' for k in keys], padding=5)
ax.set(xlim=(0, max(row[k] for k in keys) * 1.25), xlabel='Calculated dissipation (W)', title='Where modeled losses occur with the starter loads')
fig.supxlabel('SIMULATION ONLY · 2.5 W lamp + 2.5 W fan + 0.8 W controller, initial 68% charge\nDissipation is calculated. Component temperature and thermal safety are not predicted.', fontsize=9)
finish(fig, 'hardware-losses')
print('Saved hardware-runtime, hardware-startup and hardware-losses as PNG and SVG.')
