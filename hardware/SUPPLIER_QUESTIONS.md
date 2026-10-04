# Quote and compatibility requests

Drafts for the team to send manually. Prepared 28 September 2026; no messages sent, quote forms submitted or Gerbers uploaded.

## Four-layer prototype PCB quote

Please quote a student-project bare PCB delivered to Pune, PIN 411048. Please provide total payable costs for your minimum quantity and for five boards, showing GST, shipping and any setup fees separately.

- Board: Wattsense revision B, 100 × 90 mm, four copper layers, nominal 1.6 mm FR-4.
- Stack order: front signals/power; internal GND; internal GND; back signals/GND. Target copper: 1 oz outer, at least 0.5 oz inner. Please state your actual symmetric production stackup and copper weights; outer-layer-to-GND spacing target is no more than 0.25 mm.
- Minimum track 0.25 mm; clearance 0.20 mm; via pad 0.70 mm / finished drill 0.35 mm. Conventional plated through vias only.
- 104 vias; 137 total plated holes plus four 3.2 mm non-plated mounting holes. Please verify against supplied drills.
- Solder mask both sides; front silkscreen; ENIG as specified in the current CAD. Please also quote lead-free HASL as a budget alternative; selecting that alternative requires updating our agreed fabrication specification before production. No controlled impedance, blind vias or via-in-pad.
- Bare boards only initially; no component procurement or assembly. Please identify any missing manufacturing requirement, DFM issue or requested change before production.
- State production lead time, expected dispatch and estimated delivery to 411048 from the actual order date. Is electrical testing included? Are tooling, stencil or courier charges additional?

Candidate archive: `pcb/wattsense-main-revB-4layer/exports/wattsense-main-revB-4layer-prototype.zip`, with `FABRICATION.md`. Use the latest regenerated archive and confirm all four copper layers are present. A quote request is not an instruction to fabricate. Do not accept a changed stackup or modified board without reviewing it against the design.

## Protected battery and matched charger

We need a small, commercially assembled **4S LiFePO4 pack, 12.8 V nominal, around 6 Ah**, for a laboratory project. Initial charger current should be **no more than 1 A**. Our PCB's maximum battery-path current is 2 A; this does not specify or validate the pack's fault current.

Please confirm:

1. Exact pack model, chemistry, capacity, cell configuration, datasheet and included BMS protection functions.
2. Does it expose a **common protected charge/discharge port P+/P-**, or separate charge and discharge ports? Provide the connection diagram, connector type, mating connector and polarity.
3. Exact enclosed charger model recommended for this pack, its 14.6 V CC/CV behaviour, termination/restart behaviour, maximum output current and connector/polarity. Is the proposed 1 A charging rate supported by your pack specification?
4. Manufacturer's full-charge procedure, normal operating voltage/temperature limits and warranty. Do not substitute a 12.6 V 3S lithium-ion charger or a lead-acid charger.
5. Delivered pack-plus-matched-charger price including GST and freight, present stock, dispatch date and estimated delivery to Pune 411048.

The project has external series current shunts (0.1 ohm each; charge path crosses two). We will verify actual terminal voltage and completion with the selected charger. Please flag any incompatibility; we will not raise charger voltage to compensate by guesswork.

## Component order checks

Use the exact revision B grouped BOM. For INA219 request three **INA219AIDR in SOIC-8**, supplied as cut tape. Ask for the exact manufacturer part, package and stock; avoid substitutions based only on the family name. For any terminal substitution, request a mechanical drawing before approval. Quote small quantities, GST and freight; do not assume the manufacturer's full-reel quantity is the required purchase quantity.
