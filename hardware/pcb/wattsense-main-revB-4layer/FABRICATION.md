# Prototype fabrication specification

Board: Wattsense main, revision B, FOUR COPPER LAYERS. Status: engineering prototype; assembly and electrical validation pending. Do not merge with revision A files.

| Parameter | Specification |
| --- | --- |
| Finished outline | 100.00 x 90.00 mm, rectangular, no internal cutouts |
| Layers | 4 copper layers, in order F.Cu / In1.Cu / In2.Cu / B.Cu |
| Material | FR-4 |
| Board thickness | 1.6 mm nominal |
| Outer copper | 1 oz nominal (35 um); do not reduce copper weight |
| Inner copper | At least 0.5 oz nominal (17.5 um), two GND planes |
| Reference-plane layout | Both internal layers are unsplit GND; retain both files |
| Solder mask | Both sides; green suggested |
| Silkscreen | Top; white suggested. Bottom silk file is intentionally empty |
| Finish | ENIG selected in CAD stackup; lead-free HASL alternative requires agreed quote/spec update |
| Minimum designed signal width | 0.25 mm |
| Minimum configured copper clearance | 0.20 mm |
| Via | 0.70 mm pad / 0.35 mm finished plated drill |
| Other plated drills | 0.80, 1.00 and 1.30 mm |
| Mounting holes | Four 3.20 mm unplated holes |
| Controlled impedance | None |
| Blind/buried vias | None |
| Intentional via-in-pad | None |
| Components | Top side; mixed SMD and through-hole; intended for lab hand assembly |

Use `exports/wattsense-main-revB-4layer-prototype.zip` for the board quote. It contains nine Gerber layers, a Gerber job file, separate PTH/NPTH Excellon drill files, this specification and two source/track-path validation JSON records. It does not constitute an order or assembly purchase.

Nominal CAD stackup, top to bottom: 0.01 mm mask / 0.035 mm F.Cu / 0.18 mm prepreg / 0.0175 mm In1.Cu / 1.115 mm core / 0.0175 mm In2.Cu / 0.18 mm prepreg / 0.035 mm B.Cu / 0.01 mm mask. Total is 1.60 mm in this illustrative stack. Dielectric constants in CAD are placeholders, not a controlled-impedance prescription. The supplier's standard symmetric 1.6 mm four-layer FR4 stackup is acceptable after confirmation, maintaining the copper minima and close outer-layer-to-ground-plane spacing (target <=0.25 mm). Actual stackup and delivered cost remain unquoted.

This revision contains 104 plated through vias (0.35 mm drill), 137 total plated holes and four unplated mounting holes. All vias go through the entire stack. There are no microvias, blind vias or buried vias. Confirm counts against the regenerated drill report if the design changes. Ground is directly connected, so hand-soldering ground terminals may need preheating or a suitable iron.

The Gerber edge layer is the outline authority. Drill coordinates use the same absolute origin as Gerbers, in millimetres. Do not mirror the copper files. Ask the fabricator to confirm dimensions, layer order and drill interpretation in its normal preview.

Use `exports/assembly-top-1to1.svg` or KiCad's print dialog for footprint checks. Print at actual size / 100%, disable fit-to-page, and measure the board outline to confirm it is 100 x 90 mm before comparing components. A browser may automatically rescale SVG printing; the ruler check is mandatory.

For assembly, use BOM.csv and ASSEMBLY_AND_BRINGUP.md. JP1 is a header whose removable shorting cap is **not fitted by default**. The battery pack, near-pack fuse, disconnect, charger, converter, ESP32 and external buttons/probe/loads are not on-board purchased components.

Do not replace a footprint's component with a similar-looking part without checking its manufacturer's dimensions and pinout. Any source-board edit requires new checks and new exports. The source hashes in reports/connectivity-audit.json identify the checked native design.
