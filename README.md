# dolby-decoder

A DIY hardware build guide for decoding the Dolby family of surround formats — from a
genuinely home-buildable analog **matrix** decoder up to what's realistically possible with
**Dolby Digital, TrueHD, and Atmos**.

> **Read this first — the honest scope.** "Build a Dolby decoder" spans two very different
> worlds. One half (the analog *matrix* surround formats) is a rewarding weekend electronics
> project you can build from op-amps and a delay chip. The other half (the digital, discrete,
> and object-based formats — Dolby Digital, DD+, TrueHD, **Atmos**) cannot be legally or
> practically *decoded from scratch* by a hobbyist: the bitstreams are patented and the
> decoders are licensed. This guide is honest about that line and shows you the best
> *practical* path on each side of it. See [What you can and can't build](#what-you-can-and-cant-build).

## What you can and can't build

| Format | Era | How it's coded | DIY-buildable decoder? |
|---|---|---|---|
| **Dolby Surround / Pro Logic** | 1982– | 4:2:4 **analog matrix** (phase/amplitude) | ✅ **Yes — build it from scratch.** This is the core project. |
| **Pro Logic II / IIx** | 2000– | Active **matrix** + steering | 🟡 Passive/basic active version buildable; full logic-steering is complex but doable in DSP. |
| **Dolby Digital (AC-3)** | 1991– | **Discrete** compressed bitstream (patented) | 🟡 Not from scratch — but decodable in software (FFmpeg) on a Pi. |
| **Dolby Digital Plus (E-AC-3)** | 2004– | Discrete, extended | 🟡 Software-decodable (FFmpeg). |
| **Dolby TrueHD (MLP)** | 2006– | **Lossless** discrete | 🟡 Software-decodable (FFmpeg) — core audio only. |
| **Dolby Atmos** | 2012– | **Object-based** metadata on a TrueHD/DD+ core | ❌ **No open decoder exists.** You get the bed/core, not the objects. |

The rule of thumb: **matrix = buildable electronics; discrete/object = licensed software you
run, not build.** This guide covers both honestly.

## Guide contents

1. **[Formats primer](docs/00-formats-primer.md)** — how each Dolby format actually encodes
   audio, and why that determines whether you can decode it yourself.
2. **[The analog matrix decoder](docs/01-analog-matrix-decoder.md)** — ⭐ the main hardware
   build. Passive Hafler matrix → active op-amp matrix → full Dolby-Surround-style processing
   (band-limit, delay, noise reduction). Schematics, part values, assembly, calibration.
3. **[Digital formats on a Raspberry Pi](docs/02-digital-formats-rpi.md)** — the practical path
   for Dolby Digital / DD+ / TrueHD: HDMI audio extraction, HDCP realities, FFmpeg decode to
   multichannel PCM, feeding your amps.
4. **[The Atmos reality](docs/03-atmos-reality.md)** — why object audio can't be DIY-decoded,
   what you actually get from the core, and the closest legitimate approaches.
5. **[Bill of materials & tools](docs/04-bom-and-tools.md)** — consolidated shopping list and
   cost estimate for the analog build and the digital build.
6. **[Safety & legal](docs/05-safety-and-legal.md)** — mains safety, patents, HDCP, and what
   "DIY" does and doesn't entitle you to.

## Suggested build order

1. Start with the **passive Hafler matrix** ([§1](docs/01-analog-matrix-decoder.md#stage-1--the-passive-hafler-matrix)) —
   zero power, 30 minutes, an audible surround effect you can hear tonight.
2. Move to the **active op-amp matrix + center channel**.
3. Add the **surround processing chain** (7 kHz low-pass, ~20 ms delay, NR) to turn a bare
   matrix into a proper Dolby-Surround-style decoder.
4. Once the analog side works, tackle the **Raspberry Pi digital front end** for the modern
   formats.

## Status

Documentation / build guide. No firmware or PCB files yet — schematics are given as
buildable breadboard/protoboard designs with real part numbers. PCB Gerbers and a Pi decode
script are natural next steps (see the TODO at the end of each build doc).
