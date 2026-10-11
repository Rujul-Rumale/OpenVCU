# Contributing to OpenVCU

OpenVCU is WIP open hardware. Reviews and corrections are very welcome.

## How to help right now

1. **Schematic review** — power tree, decoupling, crystal load caps, sensor wiring.
2. **Layout review** — GND strategy, crystal island, USB impedance, mounting.
3. **BOM sanity** — availability, substitutes, footprint mismatches.
4. **Docs** — vehicle wiring diagrams (quad / plane / rover / boat).

## Ground rules

- This repo is **hardware-only for now**. Do not open PRs adding firmware binaries (`*.bin`, `*.apj`, `*.hex`, `*.elf`) — `Firmware/` is git-ignored.
- KiCad version: **10**. Keep project-local symbols (`OpenVCU.kicad_sym`) and footprints (`OpenVCU.pretty/`) — don't swap in global-library parts silently.
- One logical change per commit. Follow the existing style: `Power: ...`, `Sensors: ...`, `Peripherals: ...`, `docs: ...`, `bom: ...`.
- Run ERC/DRC before pushing a PCB change and note the result in the commit message.
- Re-export `bom/bom.csv` + `bom/ibom.html` if you touch the schematic.

## PR checklist

- [ ] ERC clean (or warnings explained)
- [ ] DRC clean (or warnings explained)
- [ ] BOM still matches schematic
- [ ] No firmware binaries, no editor noise, no local-only dumps
- [ ] Screenshots for layout changes help a lot

## Reporting issues

Include: what you looked at (`Power` / `Sensors` / `Peripherals` / layout), KiCad version, and what you expected vs what you found. A screenshot or net name beats a paragraph.
