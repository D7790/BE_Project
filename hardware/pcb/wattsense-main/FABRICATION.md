# Prototype fabrication specification

Board: Wattsense main, revision A. Status: engineering prototype; assembly and electrical validation pending.

| Parameter | Specification |
| --- | --- |
| Finished outline | 100.00 x 90.00 mm, rectangular, no internal cutouts |
| Layers | 2 copper layers |
| Material | FR-4 |
| Board thickness | 1.6 mm nominal |
| Outer copper | 1 oz nominal (35 um); do not reduce copper weight |
| Solder mask | Both sides; green suggested |
| Silkscreen | Top; white suggested. Bottom silk file is intentionally empty |
| Finish | Lead-free HASL or ENIG; obtain a quote |
| Minimum designed signal width | 0.25 mm |
| Minimum configured copper clearance | 0.20 mm |
| Via | 0.70 mm pad / 0.35 mm finished plated drill |
| Other plated drills | 0.80, 1.00 and 1.30 mm |
| Mounting holes | Four 3.20 mm unplated holes |
| Controlled impedance | None |
| Blind/buried vias | None |
| Intentional via-in-pad | None |
| Components | Top side; mixed SMD and through-hole; intended for lab hand assembly |

Use `exports/wattsense-main-revA-prototype.zip` for the board quote. It contains seven Gerber layers, a Gerber job file, separate PTH/NPTH Excellon drill files and this specification. It does not constitute an order or assembly purchase.

The Gerber edge layer is the outline authority. Drill coordinates use the same absolute origin as Gerbers, in millimetres. Do not mirror the copper files. Ask the fabricator to confirm dimensions, layer order and drill interpretation in its normal preview.

Use `exports/assembly-top-1to1.svg` or KiCad's print dialog for footprint checks. Print at actual size / 100%, disable fit-to-page, and measure the board outline to confirm it is 100 x 90 mm before comparing components. A browser may automatically rescale SVG printing; the ruler check is mandatory.

For assembly, use BOM.csv and ASSEMBLY_AND_BRINGUP.md. JP1 is a header whose removable shorting cap is **not fitted by default**. The battery pack, near-pack fuse, disconnect, charger, converter, ESP32 and external buttons/probe/loads are not on-board purchased components.

Do not replace a footprint's component with a similar-looking part without checking its manufacturer's dimensions and pinout. Any source-board edit requires new checks and new exports. The source hashes in reports/connectivity-audit.json identify the checked native design.
