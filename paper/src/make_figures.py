"""Original manuscript figures from local Wattsense source/results only.

Run with the project's Python environment. Outputs are draft SVG/PNG figures;
no external images, new simulations, or physical measurements are introduced.
"""
from pathlib import Path
import csv
import datetime as dt
import hashlib
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "paper/figures"
OUT.mkdir(parents=True, exist_ok=True)
RESULTS = ROOT / "simulations/results"
summary = json.loads((RESULTS / "hardware-summary.json").read_text())
assert summary["status"] == "CHECKS_PASS" and summary["hardware_tested"] is False

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8,
    "axes.titlesize": 8.5, "axes.labelsize": 8,
    "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
    "legend.fontsize": 7.2, "svg.fonttype": "path",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": .7, "savefig.facecolor": "white",
    "svg.hashsalt": "wattsense-paper-figures-v1",
})
INK = "#172b3a"
BLUE = "#12609a"
ORANGE = "#bd592b"
GREEN = "#467863"
LIGHT = "#edf3f7"
GRAY = "#647079"
figures = []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def register(fig, name, caption, alt, source_files, transformations, width):
    fig.savefig(OUT / f"{name}.svg", metadata={"Date": "2026-09-30"})
    fig.savefig(OUT / f"{name}.png", dpi=300)
    figures.append({
        "figure_id": name,
        "files": [f"paper/figures/{name}.{ext}" for ext in ("svg", "png")],
        "intended_width_inches": width,
        "caption": caption, "alt_text": alt,
        "source_files": [{"path": str(p.relative_to(ROOT)).replace("\\", "/"),
                          "sha256": sha(p)} for p in source_files],
        "transformations": transformations,
        "agent_created": True, "human_review_pending": True,
        "physical_measurements": False,
        "external_image_assets": [],
        "output_sha256": {ext: sha(OUT / f"{name}.{ext}") for ext in ("svg", "png")},
    })
    plt.close(fig)


def box(ax, xy, width, height, text, color=INK, fill=LIGHT, fontsize=8, dashed=False):
    x, y = xy
    p = FancyBboxPatch((x-width/2, y-height/2), width, height,
                      boxstyle="round,pad=0.04,rounding_size=0.09",
                      linewidth=.9, edgecolor=color, facecolor=fill,
                      linestyle="--" if dashed else "-")
    ax.add_patch(p)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
            color=INK, linespacing=1.3)


def arrow(ax, points, color=INK, dashed=False, head=True, width=1.05):
    for start, end in zip(points[:-2], points[1:-1]):
        ax.plot([start[0], end[0]], [start[1], end[1]],
                color=color, linewidth=width, linestyle="--" if dashed else "-")
    p = FancyArrowPatch(points[-2], points[-1],
                        arrowstyle="-|>" if head else "-", mutation_scale=8,
                        linewidth=width, color=color,
                        linestyle="--" if dashed else "-")
    ax.add_patch(p)


# Figure 1: conceptual topology, not an assembly wiring substitute.
fig, ax = plt.subplots(figsize=(7.0, 3.95))
fig.subplots_adjust(left=.025, right=.99, top=.985, bottom=.045)
ax.set(xlim=(0, 14), ylim=(0, 8)); ax.axis("off")
box(ax, (1.25, 6.75), 2.2, 1.15, "Protected 4S pack\ncommercial BMS\n(proposed)")
box(ax, (3.65, 6.75), 1.6, 1.15, "External fuse\n+ disconnect")
box(ax, (5.75, 6.75), 1.5, 1.15, "U1 + R1\nbattery ±I\n0x40")
box(ax, (8.45, 6.75), 1.5, 1.15, "U2 + R2\nload input\n0x41")
box(ax, (10.95, 6.75), 2.2, 1.15, "External buck\nregulated 5 V")
for start, end in [(2.35, 2.85), (4.45, 5.0), (6.5, 7.7), (9.2, 9.85)]:
    arrow(ax, [(start, 6.75), (end, 6.75)])
ax.plot(7.05, 6.75, "o", color=INK, ms=3)
ax.text(7.08, 7.58, "System\njunction", ha="center", va="center", fontsize=7.5)
ax.text(3.65, 5.91, "+I: discharge", ha="center", fontsize=7.3)

box(ax, (4.1, 4.35), 2.3, 1.22, "Matched charger /\nsolar controller\n(not raw panel)", dashed=True, fill="#f7f7f7")
box(ax, (7.05, 4.35), 1.85, 1.22, "U3 + R3\ncharge input\n0x44", dashed=True, fill="#f7f7f7")
arrow(ax, [(5.25, 4.35), (6.12, 4.35)], color=GRAY, dashed=True)
arrow(ax, [(7.05, 4.96), (7.05, 6.72)], color=GRAY, dashed=True)
ax.text(4.1, 3.05, "Charge input not exercised;\nU3 readout disabled", fontsize=7.3, color=GRAY,
        ha="center", va="center")

box(ax, (11.35, 4.95), 2.85, 1.0, "Essential lamp\nunswitched")
box(ax, (11.35, 3.35), 2.85, 1.0, "Optional fan\nQ1 switches its return")
arrow(ax, [(12.05, 6.75), (13.25, 6.75), (13.25, 4.95), (12.78, 4.95)])
arrow(ax, [(13.25, 4.95), (13.25, 3.35), (12.78, 3.35)])
ax.text(13.45, 5.65, "5 V", fontsize=7.5, rotation=90, ha="center")

box(ax, (2.3, 1.3), 2.3, 1.0, "DS18B20\npack-surface sensor")
box(ax, (5.95, 1.3), 2.65, 1.0, "Classic ESP32\nestimator + control")
box(ax, (10.65, 1.3), 3.15, 1.0, "Local dashboard + CSV\nhardware view is read-only")
arrow(ax, [(3.45, 1.3), (4.625, 1.3)], BLUE, dashed=True)
ax.text(3.97, 1.55, "data", fontsize=7.1, ha="center", color=BLUE)
# Shared I2C bus; U3 is physically present but not read by default.
for x, y in [(5.75, 6.17), (8.45, 6.17), (7.05, 3.74)]:
    arrow(ax, [(x, y), (x, 2.63)], BLUE, dashed=True, head=False)
arrow(ax, [(5.75, 2.63), (8.45, 2.63)], BLUE, dashed=True, head=False)
arrow(ax, [(5.95, 2.63), (5.95, 1.8)], BLUE, dashed=True)
ax.text(6.6, 2.12, "I²C", color=BLUE, fontsize=7.5)
arrow(ax, [(7.275, 1.3), (9.075, 1.3)], BLUE, dashed=True)
ax.text(8.2, 1.6, "serial telemetry", color=BLUE, fontsize=7.2, ha="center")
arrow(ax, [(6.9, 1.8), (6.9, 2.08), (8.95, 2.08), (8.95, 3.35), (9.925, 3.35)], ORANGE)
ax.text(8.82, 3.66, "GPIO25", color=ORANGE, fontsize=7.2)
ax.text(.17, .08, "Power: solid dark    Data: dashed blue    Q1 command: orange    Shared protected ground/5 V ESP32 feed omitted", fontsize=7.2, color=GRAY)
register(fig, "fig1_architecture",
    "Proposed Wattsense topology. U1 and U2 monitor signed battery current and load-branch input; U3 provides an unexercised charge-input interface and its readout is disabled in the supplied production configuration. The protected pack, matched charging device, converter and ESP32 are external to the custom board. Power arrows show discharge and charging directions; only the fan return is switched by Q1. The figure omits ground returns, 5 V fuse details and the alternative USB/isolated-data supply arrangements. The principal discharge simulations include battery-powered controller consumption. No assembled hardware is pictured or claimed.",
    "Power flows from a proposed protected battery through an external fuse, U1, a system junction, U2 and an external 5 V buck to an unswitched lamp and a fan with Q1 on its return. A dashed, untested charger-to-U3 path joins the system junction. Sensor data enter the ESP32; GPIO25 controls Q1; serial telemetry feeds a read-only local hardware dashboard.",
    [ROOT / "hardware/REFERENCE_WIRING.md", ROOT / "firmware/src/main.cpp", ROOT / "firmware/include/config.h"],
    ["Original conceptual diagram drawn with Matplotlib primitives; schematic topology summarized without component-scale geometry.",
     "No measured waveforms, source images or third-party diagram fragments used."], 7.0)


# Figure 2: state flow is organized in actual sample-update order.
fig, ax = plt.subplots(figsize=(7.0, 4.65))
fig.subplots_adjust(left=.018, right=.992, top=.985, bottom=.015)
ax.set(xlim=(0, 14), ylim=(0, 10)); ax.axis("off")
ax.text(.25, 9.75, "(a) Repeated measurement / policy update (~10 Hz)", weight="bold", fontsize=8.5)
left_x = 3.35; w = 5.25
nodes = [
    (8.75, "Valid sample and 0 < Δt ≤ 2 s?"),
    (7.55, "Charge reference known this boot?"),
    (6.35, "Integrate SOC; estimate usable energy\nand no-future-charge runtime $T_{\\mathrm{est}}$"),
    (5.10, "Hardware armed; temperature < 45 °C?"),
    (3.85, "11.6 V < V ≤ 14.7 V and SOC > 20%?"),
    (2.60, "Manual OFF not requested?"),
    (1.35, "$T_{\\mathrm{est}}$ < setting continuously for 3 s?"),
]
for y, text in nodes:
    box(ax, (left_x, y), w, .82, text, fontsize=8)
for (upper, _), (lower, _) in zip(nodes[:-1], nodes[1:]):
    arrow(ax, [(left_x, upper-.41), (left_x, lower+.41)])
box(ax, (9.82, 8.75), 5.85, .82, "Invalid sample / gap: fan OFF; SOC unknown", fill="#f8eeea")
arrow(ax, [(5.975, 8.75), (6.895, 8.75)], ORANGE)
ax.text(6.43, 8.98, "No", fontsize=7.1, ha="center")
box(ax, (9.82, 7.55), 5.85, .82, "Unknown reference: fan OFF\nmanual full-reference confirmation required", fill="#f8eeea")
arrow(ax, [(5.975, 7.55), (6.895, 7.55)], ORANGE)
ax.text(6.43, 7.78, "No", fontsize=7.1, ha="center")
box(ax, (9.82, 5.10), 5.85, .82, "Locked / hot: fan OFF", fill="#f8eeea")
box(ax, (9.82, 3.85), 5.85, .82, "Reserve / voltage limit: fan OFF\nessential load remains connected", fill="#f8eeea")
box(ax, (9.82, 2.60), 5.85, .82, "Manual OFF: fan OFF", fill="#f8eeea")
for y in [5.10, 3.85, 2.60]:
    arrow(ax, [(5.975, y), (6.895, y)], ORANGE)
    ax.text(6.43, y+.23, "No", fontsize=7.1, ha="center")
box(ax, (9.82, 1.35), 5.85, .82, "Yes: shed fan and latch OFF\nNo: retain state; never auto-restore", fill="#f8eeea")
arrow(ax, [(5.975, 1.35), (6.895, 1.35)], ORANGE)
ax.text(.75, .37, "Boot: fan OFF, SOC unknown. Passed checks continue downward. Each outcome returns to sampling.", fontsize=7.5, color=GRAY)
ax.text(.75, .02, "(b) Explicit restore: armed + valid reference/sample + limits passed + prospective runtime ≥ setting + 0.25 h → fan ON.", fontsize=7.5, color=BLUE)
register(fig, "fig2_control_flow",
    "Simplified control sequence matching the firmware's ordered checks. The no-future-charge estimate is an energy/power heuristic, not a guaranteed lower runtime bound. A below-threshold condition lasting three seconds sheds the optional load; a shorter condition enters WATCH. OFF outcomes latch until an explicit restore request is accepted. Restore tests the prospective consumption with the fan on and an additional 0.25 h margin. Manual full-reference confirmation follows a verified charge procedure and does not automatically enable the fan. The distributed production firmware is hardware-locked. Only the fan is switched, so supervised physical trials require an external/operator stop at the agreed reserve endpoint.",
    "A vertical sample-update sequence checks valid timing and readings, current-boot charge reference, estimator update, hardware enable and temperature, reserve/voltage, manual request and sustained runtime threshold. Failed gates command fan off. An explicit restore rule with prospective runtime margin is listed below; essential-load stopping remains external.",
    [ROOT / "firmware/include/controller.h", ROOT / "firmware/src/main.cpp", ROOT / "firmware/include/config.h"],
    ["Ordered checks transcribed from controller.update and restore; repeated-loop arrows omitted to keep diagram legible.",
     "Simplified flow includes no new controller states or unimplemented automatic restoration."], 7.0)


def rows(name):
    with (RESULTS / name).open(newline="") as f:
        return list(csv.DictReader(f))


# Figure 3: recorded SOC, no resimulation or smoothing.
baseline = rows("hardware-runtime-baseline.csv")
priority = rows("hardware-runtime-priority.csv")
fig, ax = plt.subplots(figsize=(3.4, 2.72))
fig.subplots_adjust(left=.165, right=.96, bottom=.19, top=.97)
for data, color, style, label in [(baseline, BLUE, "-", "Both loads retained"),
                                   (priority, ORANGE, "--", "Priority control")]:
    t = [0.] + [float(r["time_s"])/3600 for r in data]
    s = [summary["baseline"]["initial_soc_pct"]] + [float(r["true_soc_pct"]) for r in data]
    ax.plot(t, s, color=color, linestyle=style, lw=1.5, label=label)
shed = summary["priority"]["shed_h"]
shed_row = next(r for r in priority if r["state"] == "PRIORITY")
shed_soc = float(shed_row["true_soc_pct"])
ax.plot(shed, shed_soc, "o", color=ORANGE, markersize=3.5)
ax.annotate(f"Fan OFF\n{shed:.2f} h", xy=(shed, shed_soc), xytext=(4.65, 55),
            fontsize=7.4, ha="center", arrowprops={"arrowstyle": "->", "lw": .7, "color": GRAY})
ax.axhline(20, color=GRAY, linestyle=":", lw=.9)
for case, color, xoff in [("baseline", BLUE, -.1), ("priority", ORANGE, -.05)]:
    runtime = summary[case]["runtime_to_common_endpoint_h"]
    ax.plot(runtime, 20, "s" if case == "baseline" else "^", ms=3.5, color=color)
    ax.text(runtime+xoff, 18.15, f"{runtime:.2f} h", ha="right", va="center", fontsize=7.1, color=color)
ax.set(xlim=(0, 8.4), ylim=(15, 73), xlabel="Elapsed time (h)", ylabel="True state of charge (%)")
ax.set_xticks([0, 2, 4, 6, 8]); ax.set_yticks([20, 30, 40, 50, 60, 70])
ax.legend(loc="upper right", frameon=False, handlelength=2.2)
ax.grid(alpha=.18, linewidth=.5)
register(fig, "fig3_runtime",
    "Simulated true-SOC trajectories with 6 Ah known capacity, 68% initial SOC, 20% common true-SOC endpoint, 90% converter efficiency, 0.10 Ω battery/BMS resistance, 2.5 W lamp, 2.5 W fan and 0.8 W controller/sensors. Both-load operation supplies the lamp and fan for 5.476 h. Priority control sheds the fan at 2.494 h and supplies the lamp for 7.884 h: 43.96% more lamp service accompanies 54.47% less fan service. This reallocates service rather than increasing battery capacity. Straight segments join stored approximately one-minute samples and state-transition records; the integration step was one second.",
    "The two SOC curves overlap until the fan is shed at 2.49 hours and approximately 46.31% SOC. The retained-load curve reaches 20% after 5.48 hours; the lower-power priority curve reaches the same true-SOC endpoint after 7.88 hours.",
    [RESULTS / "hardware-runtime-baseline.csv", RESULTS / "hardware-runtime-priority.csv", RESULTS / "hardware-summary.json"],
    ["Converted elapsed seconds to hours; prepended documented t=0, SOC=68% initial point.",
     "Plotted true_soc_pct without smoothing; endpoints and service percentages taken from source summary."], 3.4)


# Figure 4: all 18 deterministic pairs, no confidence interval representation.
pairs = summary["sensitivity_pairs"]
fig, axes = plt.subplots(2, 1, figsize=(3.4, 3.65), sharex=True)
fig.subplots_adjust(left=.15, right=.965, bottom=.31, top=.95, hspace=.20)
Rstyles = [(0.05, BLUE, "o"), (0.10, ORANGE, "s"), (0.20, GREEN, "^")]
for ax, capacity in zip(axes, [4.8, 6.0]):
    for resistance, color, marker in Rstyles:
        subset = sorted([r for r in pairs if r["capacity_ah"] == capacity and r["battery_r_ohm"] == resistance], key=lambda r: r["efficiency"])
        x = [100*r["efficiency"] for r in subset]
        for key, ls in [("baseline_h", "--"), ("priority_h", "-")]:
            ax.plot(x, [r[key] for r in subset], color=color, marker=marker,
                    markerfacecolor="white", ms=4.0, lw=.8, linestyle=ls, mew=.75)
    ax.set_ylabel("Lamp service (h)")
    ax.text(.04, .91, f"Capacity: {capacity:g} Ah", transform=ax.transAxes, fontsize=7.5, va="top",
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 1})
    ax.grid(alpha=.2, lw=.5)
axes[0].set_ylim(3.45, 7.5); axes[0].set_yticks([4, 5, 6, 7])
axes[1].set_ylim(4.4, 8.65); axes[1].set_yticks([5, 6, 7, 8])
axes[1].set(xlabel="Assumed converter efficiency (%)", xlim=(79, 96))
axes[1].set_xticks([80, 90, 95])
handles = [Line2D([0], [0], color=c, marker=m, markerfacecolor="white", lw=.8,
                  label=f"{r:.2f} Ω") for r, c, m in Rstyles]
fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.54, .085), ncol=3,
           frameon=False, title="Assumed battery/BMS resistance", title_fontsize=7.2,
           columnspacing=.9, handlelength=1.6)
fig.legend(handles=[Line2D([0], [0], color=INK, lw=.9, ls="--", label="Both loads retained"),
                    Line2D([0], [0], color=INK, lw=.9, ls="-", label="Priority control")],
           loc="lower center", bbox_to_anchor=(.54, .00), ncol=2, frameon=False,
           handlelength=2., columnspacing=1.0)
register(fig, "fig4_sensitivity",
    "All 18 deterministic paired discharge scenarios: capacity 4.8/6 Ah, efficiency 80/90/95%, and assumed battery/BMS resistance 0.05/0.10/0.20 Ω. Dashed lines retain both loads; solid lines use priority control. Resistance-series symbols nearly overlap because its influence is small within these selected ranges. Capacity is known exactly to the estimator in each run, other assumptions match the starter case, and lines connect the three sampled efficiencies only. These are scenario results, not statistical confidence intervals or robustness bounds against calibration error. Fan service is not shown here and is reduced by the priority policy.",
    "Two stacked plots separate 4.8 Ah and 6 Ah capacity. Each shows retained-load and priority lamp-service hours at 80, 90 and 95 percent efficiency, with distinct color and marker shapes for three selected battery resistances. Priority lamp service is higher in all 18 paired scenarios; resistance traces nearly coincide.",
    [RESULTS / "hardware-summary.json", RESULTS / "hardware-runtime-sensitivity.csv", ROOT / "simulations/hardware-assumptions.json"],
    ["Selected all sensitivity_pairs; grouped by capacity, resistance and operating policy.",
     "Converted efficiency to percent; connected existing discrete points without regression, interpolation claims or uncertainty bars."], 3.4)


# Figure 5: show all startup cases, common rail and fan terminal separately.
startup = summary["startup_cases"]
labels = ["S1: no surge", "S2: 2× start", "S3: 3× start", "S4: larger C", "S5: 3 A source", "S6: starter"]
fig, ax = plt.subplots(figsize=(3.4, 2.85))
fig.subplots_adjust(left=.32, right=.97, top=.84, bottom=.24)
for i, row in enumerate(startup):
    y = 5-i
    rail, fan = row["min_rail_v"], row["min_fan_terminal_v"]
    ax.plot([fan, rail], [y, y], color="#a8adb0", lw=1.)
    ax.plot(rail, y, "s", ms=4.2, color=BLUE)
    ax.plot(fan, y, "^", ms=4.3, markerfacecolor="white", markeredgecolor=ORANGE, mew=.9)
ax.axvline(4.75, color=GRAY, ls=":", lw=1.)
ax.text(4.69, 5.53, "4.75 V rail screen", fontsize=7.0, ha="right", color=GRAY)
ax.set_yticks(range(6), labels[::-1]); ax.tick_params(axis="y", length=0)
ax.set(xlim=(2.6, 5.02), ylim=(-.55, 5.85), xlabel="Simulated minimum voltage (V)")
ax.set_xticks([3., 4., 5.]); ax.grid(axis="x", alpha=.2, lw=.5)
fig.legend(handles=[Line2D([0], [0], color=BLUE, marker="s", linestyle="none", ms=4, label="Common rail"),
                    Line2D([0], [0], color=ORANGE, marker="^", markerfacecolor="white", linestyle="none", ms=4, label="Fan terminal")],
           loc="lower center", bbox_to_anchor=(.57, .035), ncol=2, frameon=False,
           columnspacing=1., handletextpad=.4)
register(fig, "fig5_startup",
    "Minimum common-rail and fan-terminal voltage in six separate behavioural SPICE startup scenarios. S1–S5 use a nominal 0.6 A lamp/fan running demand; S6 uses 0.5 A each. Fan starting demand at 5 V / source current limit / capacitance are: S1 0.6 A/2 A/470 µF; S2 1.2 A/2 A/470 µF; S3 1.8 A/1.5 A/470 µF; S4 1.8 A/1.5 A/2200 µF; S5 1.8 A/3 A/470 µF; S6 1.0 A/2 A/470 µF. Increased demand lasts an assumed 100 ms and decreases with terminal voltage. The dotted 4.75 V criterion applies to the common rail only; it is neither a fan-start specification nor an ESP32 reset limit. Three cases fail that screen. These equivalent-source/load models do not represent a purchased converter control loop or an actual BLDC fan.",
    "Six horizontal paired markers compare minimum common-rail voltage with the lower fan-terminal voltage. S3 and S4 fall to about 3.00 V common rail and 2.74 V at the fan, despite increased capacitance in S4. S5 also misses the 4.75 V common-rail screen. S1, S2 and S6 pass only that provisional model screen.",
    [RESULTS / "hardware-summary.json", ROOT / "simulations/run_hardware.py", ROOT / "simulations/hardware-assumptions.json"],
    ["Used stored minimum voltages from all six startup_cases, without exclusion or smoothing.",
     "Connected each scenario's two different measurement locations; segment is not an error bar."], 3.4)


manifest = {
    "status": "DRAFT_FIGURES_AGENT_CHECKED_HUMAN_REVIEW_PENDING",
    "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    "creator": "Codex assistant using local Matplotlib",
    "script": "paper/src/make_figures.py",
    "script_sha256": sha(Path(__file__)),
    "matplotlib_version": matplotlib.__version__,
    "processing_boundary": "Local source/results only; no network or image-generation service",
    "svg_text": "Outlined local DejaVu Sans glyphs for portable vector rendering; captions/alt text remain in this manifest",
    "data_source_run_finished_utc": summary.get("finished_utc"),
    "source_scope": summary["scope"],
    "scientific_review_status": "Agent consistency review complete; accountable human review pending",
    "third_party_image_permissions": "Not applicable: all figures drawn locally from project topology/data",
    "figures": figures,
}
(OUT / "figure-provenance.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Created {len(figures)} original SVG + PNG figures and provenance manifest in {OUT}")
