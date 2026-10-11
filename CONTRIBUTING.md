# Contributing to OpenVCU

OpenVCU is WIP open hardware. Reviews and corrections are very welcome.

## How to help right now

1. **Schematic review** — power tree, decoupling, crystal load caps, sensor wiring.
2. **BOM sanity** — availability, substitutes, footprint mismatches.
3. **Docs** — vehicle wiring diagrams (quad / plane / rover / boat).

## Ground rules

- This repo is **schematics + libraries only**. Do not open PRs adding layout (`.kicad_pcb`), gerbers, or firmware binaries (`*.bin`, `*.apj`, `*.hex`, `*.elf`) — all are git-ignored.
- KiCad version: **10**. Keep project-local symbols (`OpenVCU.kicad_sym`) and footprints (`OpenVCU.pretty/`) — don't swap in global-library parts silently.
- One logical change per commit. Follow the existing style: `Power: ...`, `Sensors: ...`, `Peripherals: ...`, `docs: ...`, `bom: ...`.
- Run ERC before pushing a schematic change and note the result in the commit message.
- Re-export `bom/bom.csv` + `bom/ibom.html` if you touch the schematic.

## PR checklist

- [ ] ERC clean (or warnings explained)
- [ ] BOM still matches schematic
- [ ] No layout files, gerbers, firmware binaries, editor noise, or local-only dumps

## Reporting issues

Include: what you looked at (`Power` / `Sensors` / `Peripherals` / layout), KiCad version, and what you expected vs what you found. A screenshot or net name beats a paragraph.
