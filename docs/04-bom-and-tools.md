# 4 · Bill of materials & tools

Two shopping lists: the **analog matrix decoder** ([§1](01-analog-matrix-decoder.md)) and the
**digital front end** ([§2](02-digital-formats-rpi.md)). Prices are rough 2026 hobby-quantity
estimates in USD and vary by supplier/region.

## Analog matrix decoder

### Core electronics

| Qty | Part | Purpose | ~Cost |
|---|---|---|---|
| 3 | Dual op-amp **NE5532** (or TL072 / OPA2134) | L/R buffers, C sum, S difference, filters | $2–6 |
| 1 | **PT2399** delay IC + support R/C (per datasheet) | ~20–30 ms surround delay | $2 |
| 1 | **TLE2426** rail splitter (if single-supply) | virtual ground for ±rails | $2 |
| ~20 | 10 kΩ 1% metal-film resistors | matrix + filters | $2 |
| — | Assorted R/C for filters (2.2 kΩ, 10 nF, 1.6 µF, etc.) | 100 Hz HPF / 7 kHz LPF | $3 |
| 3 | 10 kΩ trimpots | null & level calibration | $3 |
| 8+ | 10 µF electrolytic caps | DC blocking on I/O | $2 |
| many | 100 nF ceramic caps | op-amp supply decoupling | $2 |
| 5 | RCA jacks (2 in, up to 4–6 out) | I/O | $4 |
| 1 | Protoboard / perfboard (or a future PCB) | build substrate | $3–8 |
| 1 | Enclosure (metal preferred, shielding) | housing | $8–20 |

**Subtotal: ~$35–60.**

### Power

| Option | Parts | ~Cost |
|---|---|---|
| Batteries (first test) | 2× 9 V + clips | $6 |
| Wall-wart + rail splitter | 12 V DC adapter + TLE2426 | $10 |
| Linear ±12 V supply (permanent) | transformer/regulators or a module | $15–30 |

### Optional / stretch

| Part | Purpose |
|---|---|
| **MN3005 + MN3101 + NE570** | authentic all-analog BBD delay instead of PT2399 |
| **NE570/571** compander | Dolby-B-style surround noise reduction |
| **Teensy 4.x + Audio Adapter** *or* **ADAU1701 SigmaDSP board** | DSP Pro Logic II–style active steering / upmix |
| 50 Ω ≥5 W wirewound pot | passive Hafler rear level ([Stage 1](01-analog-matrix-decoder.md#stage-1--the-passive-hafler-matrix)) |

## Digital front end (Raspberry Pi)

| Qty | Part | Purpose | ~Cost |
|---|---|---|---|
| 1 | **Raspberry Pi 4 or 5** (+ PSU, SD card) | runs FFmpeg decode | $45–80 |
| 1 | **USB S/PDIF / TOSLINK capture** input | legal AC-3 input from optical | $15–30 |
| 1 | **USB 5.1/7.1 DAC** (or I2S DAC HAT) | multichannel analog out | $20–60 |
| 1 (opt) | **HDMI audio extractor** (HDCP-2.2 compliant) | HDMI-borne formats — see caveats | $25–60 |
| — | TOSLINK / RCA / speaker cabling | interconnect | $10–20 |

**Subtotal: ~$90–200** depending on DAC and whether you add HDMI.

> ⚠️ The HDMI extractor route has **HDCP and legal caveats** and still **cannot** give you Atmos
> objects — see [§2](02-digital-formats-rpi.md) and [§3](03-atmos-reality.md).

## Amps & speakers (shared)

You need amplification and speakers for however many channels you decode:

- **Front L/R:** you likely already have these.
- **Center:** 1 channel + 1 speaker.
- **Surround:** 1 channel (mono) → both rears, or 2 channels for stereo surround (Pro Logic II /
  digital 5.1).
- **Subwoofer (.1):** powered sub off a summed low-pass, optional.

A cheap multichannel class-D amp board (TPA3116-based 4-/6-channel boards) is a common DIY
choice, ~$15–40.

## Tools

| Tool | For |
|---|---|
| Soldering iron + solder | assembly |
| Multimeter | supply rails, null calibration, continuity |
| Breadboard | prototype Stages 1–2 before soldering |
| Phone signal generator + SPL-meter apps | test tones, level matching, null depth |
| Oscilloscope (nice-to-have) | verifying delay, filter response, phase |
| Wire strippers, helping hands, flush cutters | general |

## Total cost snapshot

| Build | Rough total |
|---|---|
| Passive Hafler only ([Stage 1](01-analog-matrix-decoder.md#stage-1--the-passive-hafler-matrix)) | **~$5–15** (speaker wire + 2 rear speakers you may own) |
| Full analog matrix decoder (Stages 2–3) | **~$40–70** + amp/speakers |
| Digital front end (Pi + optical + DAC) | **~$90–200** + amp/speakers |
| Everything | **~$150–300** + amps/speakers |

---

**Next:** [§5 · Safety & legal →](05-safety-and-legal.md)
