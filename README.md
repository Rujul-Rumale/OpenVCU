<div align="center">

# OpenVCU

### Open Vehicle Control Unit — one board, every vehicle.

**Quad · Plane · Rover · Boat — configurable STM32H7 controller for anything that moves.**

![Status](https://img.shields.io/badge/status-WIP-yellow?style=for-the-badge)
![STM32](https://img.shields.io/badge/STM32H743VIT6-03234B?style=for-the-badge&logo=stmicroelectronics&logoColor=white)
![KiCad](https://img.shields.io/badge/KiCad-314CB0?style=for-the-badge&logo=kicad&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

*Open hardware. Designed from scratch. Built to be flashed for whatever you bolt it to.*

</div>

---

## What is this?

OpenVCU is an **open-source vehicle control unit** built around the **STM32H743VIT6** (480&nbsp;MHz Cortex-M7, 2&nbsp;MB flash, 1&nbsp;MB RAM).

Off-the-shelf F4 flight controllers run out of headroom when you fuse RTK GPS + IMU at high rates for EKF-heavy work like 3D photogrammetry surveys. OpenVCU is my answer: H7-class compute, a clean sensor set, and one PCB that can be configured as a **quad, fixed-wing, rover, or boat** controller.

> ⚠️ **WIP — hardware in progress.** Schematic + 4-layer layout are done and DRC-clean. The board has **not been manufactured or tested on real hardware yet**. Firmware lives out-of-tree for now and is intentionally **not in this repo**.

---

## One board, four vehicles

| Vehicle | What OpenVCU gives you |
| :--- | :--- |
| 🚁 **Quad** | 4× PWM motor outputs (TIM1), 6-axis IMU + baro, SD logging |
| ✈️ **Plane** | PWM for elevon / tail / throttle + UART GPS + I2C compass header |
| 🚗 **Rover** | PWM for steering + throttle, battery sensing, FRAM for params |
| 🚤 **Boat** | Same as rover + sealed-box-friendly USB-C + SD blackbox |

All vehicle personalities share the same core: **IMU → EKF → PWM + telemetry + log**. The difference is just configuration and wiring.

---

## Hardware at a glance

| Block | Part | Notes |
| :--- | :--- | :--- |
| MCU | **STM32H743VIT6** | 480&nbsp;MHz M7, LQFP-100, 8&nbsp;MHz HSE + 32.768&nbsp;kHz LSE |
| IMU | **ICM-42688-P** | 6-axis, SPI, 32&nbsp;kHz ODR |
| Baro | **DPS310** | I2C `0x76`, interrupt pin routed |
| Logging | **FM25V02A** FRAM 256&nbsp;KB (SPI) + **microSD** over SDMMC1 4-bit | Params + blackbox |
| Power | LiPo → **MP1584EN** buck (5&nbsp;V) → **AP2112K** 3.3&nbsp;V LDO | Fused + reverse-protected input |
| USB | **USB-C** + USBLC6-2SC6 ESD | 5.1&nbsp;kΩ CC pull-downs |
| Compass | External via I2C header | For real heading on rovers / boats / planes |

---

## Interfaces

### PWM motor / servo outputs

| Output | MCU pin | Timer |
| :--- | :--- | :--- |
| OUT 1 | PE9 | TIM1_CH1 |
| OUT 2 | PE11 | TIM1_CH2 |
| OUT 3 | PE13 | TIM1_CH3 |
| OUT 4 | PE14 | TIM1_CH4 |

Quads take all four. Planes / rovers / boats just remap them (e.g. steering + throttle).

### Comms & storage

| Bus | Use |
| :--- | :--- |
| UART1 / UART3 / UART6 | GPS, telemetry radio, RC |
| I2C1 / I2C2 | Onboard DPS310 + external compass |
| SPI1 | ICM-42688-P |
| SPI2 / SPI3 | Expansion + FM25V02A FRAM |
| SDMMC1 | microSD 4-bit |
| USB OTG_FS | USB-C (PA11/PA12) |

### SWD debug header

| Pin | Signal |
| :--- | :--- |
| 1 | +3V3 |
| 2 | SWDIO (PA13) |
| 3 | SWCLK (PA14) |
| 4 | GND |

Flash with ST-Link + STM32CubeProgrammer once firmware lands.

---

## Repo structure

```
OpenVCU/
├── PCB/          # KiCad 10 — schematic + 4-layer layout
│   ├── OpenVCU.kicad_sch      # root sheet
│   ├── Power.kicad_sch
│   ├── Sensors.kicad_sch
│   ├── Peripherals.kicad_sch
│   └── OpenVCU.kicad_pcb      # 4-layer layout
├── bom/          # BOM CSV + interactive BOM
├── docs/
│   └── datasheets/            # vendor datasheets for every key part
├── tools/        # schematic verification helpers
├── LICENSE
├── CONTRIBUTING.md
└── README.md
```

> Firmware (`hwdef`, bootloader, binaries) is **deliberately excluded** from git right now. It'll land as `Firmware/` once the board is validated.

---

## Status & roadmap

- ✅ Schematic complete (hierarchical: Power / Sensors / Peripherals)
- ✅ 4-layer layout complete, DRC clean (9 benign USB-C pad-spacing warnings)
- ✅ BOM + interactive BOM exported
- ✅ Gerbers exported (`PCB/gerber_*.zip`)
- ⏳ **Manufacture rev A**
- ⏳ Bring-up: power rails → SWD → IMU/baro probe → SD + FRAM
- ⏳ Firmware bring-up (out-of-tree until hardware is proven)
- ⏳ Vehicle configs: quad → plane → rover → boat

---

## Getting started

### 1. Open the hardware

```bash
git clone https://github.com/<you>/OpenVCU.git
cd OpenVCU
# open PCB/OpenVCU.kicad_pro in KiCad 10
```

You need **KiCad 10** (project symbols live in `OpenVCU.kicad_sym`, footprints in `OpenVCU.pretty/`).

### 2. Review the BOM

- `bom/bom.csv` — orderable line items
- `bom/ibom.html` — interactive BOM, open in a browser

### 3. Manufacturing

Gerbers are under `PCB/gerber_JLCPCB.zip` / `PCB/gerber_PCBway.zip`. Always re-export from the checked-in `.kicad_pcb` before ordering — don't trust stale zips blindly.

---

## Design notes

- **VCAP1/VCAP2 need exactly 2.2&nbsp;µF ceramic** or the H7 internal LDO goes unstable.
- **USB-C CC pins need 5.1&nbsp;kΩ to GND** or chargers won't enumerate the board.
- Crystal section sits over an **isolated GND island** to keep noise out of the oscillator.
- Bottom copper is a **GND pour**; 4-layer stack keeps power integrity sane for the H7's transient load.

---

## Contributing

WIP hardware — reviews welcome, especially on power, crystal, and sensor routing. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## ⚠️ Caution

Nothing here has touched real copper yet. Double-check every pin against the schematic before you fab or flash, and expect rev-A debugging.

---

## Credits

- Designed by **Rujul**
- [KiCad](https://www.kicad.org/) for schematic + layout
- Datasheets in `docs/datasheets/` belong to their respective vendors
