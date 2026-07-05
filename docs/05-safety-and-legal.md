# 5 · Safety & legal

Read this before you plug anything in. None of it is scary, but two areas — **mains power** and
**copy protection / patents** — deserve a clear head.

## Electrical safety

The decoder itself is a **low-voltage, signal-level** project (±9–12 V, line-level audio ≈1–2 V).
That part is safe. The risks come from what you connect it to.

- **Never open a mains-powered amplifier or AVR** to tap signals unless you know what you're
  doing. Line voltage (120/230 V AC) and large filter capacitors inside can injure or kill even
  when unplugged. Everything in this guide is designed to work from **external line-level
  connections (RCA/optical)** and its own **low-voltage supply**, so you should never need to.
- **Passive Hafler wiring** ([Stage 1](01-analog-matrix-decoder.md#stage-1--the-passive-hafler-matrix))
  touches **speaker terminals only** — safe voltages. But:
  - **Do not connect the amplifier's `−` (negative) speaker terminals together.** Bridged (BTL)
    and many class-D amps have "hot" negative outputs; commoning them shorts the output stage and
    can destroy the amp. Use the **hot (+) terminals** as shown, and if your amp is bridged,
    **skip the passive trick** and use the [active line-level matrix](01-analog-matrix-decoder.md#stage-2--the-active-op-amp-matrix)
    instead.
- **Power supply:** if you build a mains-fed ±12 V supply rather than using batteries/wall-warts,
  treat the primary side with respect — proper fusing, strain relief, insulation, and an earthed
  metal enclosure. If unsure, use a **pre-made wall-wart** and only handle the low-voltage side.
- **Grounding & hum:** tie all signal grounds to one point (star ground); a metal enclosure
  bonded to signal ground reduces hum and shields the high-impedance matrix nodes.
- **Heat:** the PT2399 and op-amps run cool at these levels; multichannel class-D amp boards do
  not — heatsink them per their datasheets.

## Copy protection (HDCP)

The [digital front end](02-digital-formats-rpi.md) can involve **HDMI**, and commercial HDMI
sources are protected by **HDCP** (High-bandwidth Digital Content Protection).

- Using an **HDCP-*compliant*** audio extractor to get a *downmixed* or S/PDIF output is normal
  and fine.
- Using a device or method that **strips/circumvents HDCP** to expose the raw protected
  bitstream is a different matter: **circumventing an access-control measure on content you're
  not authorized to** is illegal in many jurisdictions (in the US, the DMCA §1201 anti-
  circumvention provisions; the EU Copyright Directive and others elsewhere).
- **Safe, unambiguous inputs:** analog line-level, and **optical/coax S/PDIF** (Dolby Digital
  AC-3), which is unencrypted. Start there — it covers the most common Dolby content with no
  legal gray area.
- Decode content you **own or are licensed to play**, for your **own use**. Don't build this to
  redistribute or strip protection from others' content.

## Patents & licensing

The Dolby formats aren't just file formats — they're **patented technologies**, and "Dolby",
"Dolby Digital", "Pro Logic", "TrueHD", and "Atmos" are **trademarks of Dolby Laboratories**.

- **Building one decoder for personal, non-commercial use** is a hobby-electronics activity.
  The **analog matrix** ([§1](01-analog-matrix-decoder.md)) implements decades-old,
  now-unencumbered *matrix* math (sum/difference) — that's just op-amp arithmetic and is not
  itself a licensing problem.
- **The digital codecs** (AC-3, E-AC-3, TrueHD) are decoded here by **FFmpeg**, an existing
  open-source project — you're *running* it, not shipping a product. If you ever wanted to
  **sell** a decoder or **distribute** decoding software commercially, you would need the
  relevant **Dolby (and codec) licenses**. This guide is for personal builds.
- **Atmos object rendering** is licensed and closed; see [§3](03-atmos-reality.md). Don't claim a
  DIY build "does Atmos" when it's decoding the bed.
- **Trademarks:** don't label a homemade unit "Dolby" or sell it using Dolby marks — that's a
  trademark issue independent of patents.

## Hearing & speakers

- **Level-match at low volume first.** The matrix has calibration steps that involve test tones;
  keep them quiet to protect your ears and drivers.
- A miswired difference/sum stage can briefly produce full-scale output — bring levels up
  **gradually** the first time you power the outputs into amps.

## The short version

- The circuit is low-voltage and safe; **respect mains** if you build a mains supply, and
  **never common amp `−` terminals**.
- **Optical/analog inputs are legally clean**; **don't circumvent HDCP**.
- **Personal use is fine; selling a "Dolby" decoder is not** without licenses.
- **Decode content you're entitled to play.**

---

← Back to the [README](../README.md) · [§1 Analog build](01-analog-matrix-decoder.md) ·
[§2 Digital front end](02-digital-formats-rpi.md) · [§3 Atmos reality](03-atmos-reality.md)
