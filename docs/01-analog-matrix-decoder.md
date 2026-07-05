# 1 · The analog matrix decoder ⭐

This is the real hardware project — a decoder you build from scratch that recovers **Center**
and **Surround** channels from an ordinary **Lt/Rt** stereo signal, exactly the way early
Dolby Surround and quadraphonic decoders did. You'll build it in three stages, each usable on
its own:

1. **[Passive Hafler matrix](#stage-1--the-passive-hafler-matrix)** — no power, no parts but
   speaker wire. A surround effect tonight.
2. **[Active op-amp matrix](#stage-2--the-active-op-amp-matrix)** — buffered L/C/R/S outputs
   with proper levels, drives line inputs.
3. **[Full Dolby-Surround-style processing](#stage-3--dolby-surround-style-surround-processing)** —
   band-limit + delay + noise reduction on the surround channel, the things that make a bare
   matrix sound like an actual Dolby decoder.

> ⚠️ **Signal-level project.** Everything here runs at **line level** (≈1–2 V) from a ±9–12 V
> supply. You do **not** open a mains-powered amplifier for Stage 1 unless you follow
> [the safety doc](05-safety-and-legal.md) — the Hafler trick touches speaker terminals, which
> are safe, but the chassis and mains inside an amp are not.

---

## The math you're implementing

From the [primer](00-formats-primer.md), the encoder produced:

```
Lt = L + 0.707·C + 0.707·S(+90°)
Rt = R + 0.707·C − 0.707·S(−90°)
```

A **passive/basic matrix decoder** inverts this with four simple combinations:

| Output | Formula | Recovered by |
|---|---|---|
| Left | `L = Lt` | pass-through |
| Right | `R = Rt` | pass-through |
| **Center** | `C = 0.5·(Lt + Rt)` | **summing** amplifier |
| **Surround** | `S = 0.5·(Lt − Rt)` | **difference** amplifier |

That's the whole idea: **sum → center, difference → surround.** Stages 2 and 3 just do this
cleanly and then treat the surround channel the way Dolby specifies.

---

## Stage 1 · The passive Hafler matrix

*(30 minutes · no power · no active parts)*

The single cheapest way to hear matrix surround, invented by David Hafler and sold by Dynaco as
the **QD-1 Quadaptor** in the early 1970s. It exploits the fact that if you wire a speaker
*between* the two amplifier hot terminals, it sees **L − R** — precisely the surround difference
signal.

### Wiring (two rear speakers, "series" Hafler)

You need a stereo power amp already driving your front L/R speakers. Add two rear speakers wired
in **series across the two hot (+) terminals**:

```
   Amp L(+) ─────────────► Front Left  (+)      (normal)
   Amp L(−) ─────────────► Front Left  (−)
   Amp R(+) ─────────────► Front Right (+)      (normal)
   Amp R(−) ─────────────► Front Right (−)

   Rear matrix (the Hafler add-on):
   Amp L(+) ──► Rear Left (+)
               Rear Left (−) ──► Rear Right (+)     ◄─ two rears in SERIES
                                 Rear Right (−) ──► Amp R(+)
```

The two rear speakers in series now carry the voltage **L(+) − R(+) = L − R = the surround
difference**. Because it's a single mono difference signal split across two speakers, there's
**zero separation** between the two rears — that's expected and fine for ambience.

> ✅ **Do:** use the *hot* terminals only. **Never** connect an amp's `−` terminals together —
> many amps (bridged/BTL, class-D) have "hot" negative outputs and you'll short the output stage.
> If your amp is bridged, **do not use the passive Hafler trick at all** — go straight to
> [Stage 2](#stage-2--the-active-op-amp-matrix), which taps the *line-level* signal instead.

### Optional level control

Put a **~50 Ω, ≥5 W wirewound potentiometer** (or an L-pad) in series with the rear pair to
trim rear volume. Wirewound because it carries speaker power.

### What you'll hear

Reverb, crowd noise, applause, hall ambience, and encoded Pro Logic surround effects move
behind you; centered dialog and mono bass largely cancel in the rears (they're equal in L and
R, so `L − R ≈ 0`). This is the "aha" moment that proves the matrix idea before you solder
anything.

---

## Stage 2 · The active op-amp matrix

*(an afternoon · ±9–12 V · four op-amps)*

The passive trick is amp-dependent and has no center channel. The active version takes a
**line-level Lt/Rt** input (from a preamp, DAC, TV line-out, or the stereo downmix of your
[Pi digital front end](02-digital-formats-rpi.md)) and produces **four buffered line outputs**
— L, C, R, S — that you feed to four power-amp channels.

### Power supply

A **dual-rail ±9 V to ±12 V** supply. Easiest options:

- Two 9 V batteries (one for +9, one for −9, commoned in the middle) — great for a first test,
  no mains.
- A wall-wart + a **TLE2426 "rail splitter"** to make a virtual ground from a single supply.
- A small ±12 V linear supply if you want it permanent.

Decouple every op-amp with **100 nF** across its supply pins.

### Op-amp choice

Any decent dual audio op-amp: **NE5532** (cheap, quiet, classic), **TL072** (FET input, fine),
or **OPA2134** (audiophile). You need **4 op-amp sections = 2 dual packages** for the core matrix
(L buffer, R buffer, C sum, S difference).

### Core matrix schematic

All resistors **10 kΩ, 1% metal film** unless noted. Non-inverting buffers for L/R; a summing
inverter for C; a difference amp for S. (Inversions don't matter audibly for the derived
channels — but keep L and R non-inverted so they stay in phase with the fronts.)

```
                 LEFT  buffer (unity gain)
 Lt ──┬──────────►│+\
      │           │  >───────────────► L out
      │        ┌─►│−/
      │        └──────────────┘  (direct feedback, gain = 1)
      │
      │         RIGHT buffer (unity gain)
 Rt ──┼──┬──────►│+\
      │  │       │  >───────────────► R out
      │  │    ┌─►│−/
      │  │    └──────────────┘
      │  │
      │  │      CENTER = −(Lt + Rt)/2 · 2  ... (summing inverter, gain set to ~0.7)
      │  │     Rc                     Rf
 Lt ──┼──┴──[10k]──┐        ┌──[10k]──┐
      │            │        │         │
 Rt ──┴─────[10k]──┼───►│−\ │         │
                   └────┤  >┴─────────┴──► C out
      Vref(gnd)───►│+/
                        (Rf/Rin sets level; 10k/10k → sum then trim, see calibration)

      SURROUND = (Lt − Rt)/2   ... (classic difference amplifier)
                    R1=10k        R2=10k
 Lt ───────────────[10k]────►│−\
                             │  >───────────► S out (raw)
 Rt ──[10k]──┬───────────────│+/
             │
            [10k]
             │
            GND
```

**How the difference amp works:** the standard 4-resistor instrumentation-style difference
amplifier with all resistors equal gives `Vout = Rt_in(+) − Lt_in(−) = Rt − Lt = −(Lt − Rt)`.
Sign is irrelevant for a mono surround feed. With all four resistors equal (10 kΩ) the gain is
1; the `0.5` factor is handled in calibration so you don't lose headroom.

**Center summing amp:** two 10 kΩ input resistors into a virtual-ground inverter with a 10 kΩ
(or 7.5 kΩ for the −3 dB Dolby weighting) feedback resistor gives `C = −(Lt + Rt)·(Rf/10k)`.
Use a following inverter or just accept the inversion.

### Outputs

Each output through a **1 kΩ** series resistor and a **10 µF** DC-blocking cap (electrolytic,
+ toward the op-amp) to an RCA jack. Add a **100 kΩ** resistor to ground after the cap to
define the DC level.

At the end of Stage 2 you have a **4-channel passive-equivalent matrix**: L, C, R, and a raw
(full-bandwidth, undelayed) surround. It already sounds like surround. Stage 3 makes the
surround *correct*.

---

## Stage 3 · Dolby-Surround-style surround processing

A bare `Lt − Rt` surround is too bright, too "present," and arrives at the wrong time. Real
Dolby Surround decoders do three things to the surround channel. Add them in this order:

### 3a. Band-limit: 100 Hz – 7 kHz

The surround channel is defined as band-limited. Roll off the extremes so front-channel bleed
and hiss don't leak to the rears:

- **High-pass ~100 Hz:** 1.6 µF in series + 1 kΩ to ground (or an active 2nd-order Sallen-Key).
- **Low-pass ~7 kHz:** classic Dolby surround top end. Simple 1st-order: series **2.2 kΩ** +
  shunt **10 nF** (`f = 1/(2π·2.2k·10n) ≈ 7.2 kHz`). Better: a 2nd-order Sallen-Key low-pass at
  7 kHz using one more op-amp section.

### 3b. Delay: ~15–30 ms

The defining Dolby Surround feature. The surround is **delayed** so that, by the precedence
(Haas) effect, front sounds bleeding into the rears are masked and localize forward. Dolby
specs an *adjustable* delay set so surround arrives ~15–30 ms after the fronts (tuned to your
seating distance). Two ways to build it:

**Option A — PT2399 digital delay (recommended today).** The PT2399 is a cheap
(~$1–2) single-chip echo/delay IC. Its usable delay starts around **30 ms** and goes up from
there — right at the top of the Dolby window and easy to dial in. Use the standard PT2399 delay
circuit (datasheet/ElectroSmash reference), set the delay resistor for ~20–30 ms, and take the
**delayed (wet) output only** (we want pure delay, not echo — so no feedback path). Follow it
with the PT2399's recommended reconstruction low-pass, which conveniently also helps the 7 kHz
band-limit.

```
 S(raw) ──► [ 100Hz HPF ] ──► [ PT2399 delay, wet-only, ~25 ms ] ──► [ 7 kHz LPF ] ──► S out
```

**Option B — BBD (bucket-brigade) for the analog purist.** A **MN3005** (4096-stage) clocked
around 10 kHz gives ~205 ms max; clocked faster it lands in the 15–30 ms range. BBDs need a
clock generator (MN3101) and companding (NE570) for noise, and the chips are now expensive
(the MN3005 runs €10–20+). Authentic to the era, but the PT2399 is cheaper, quieter, and
simpler. Choose this only if you specifically want an all-analog delay.

### 3c. Noise reduction (optional, for authenticity)

Genuine Dolby Surround applies **modified Dolby B** noise reduction to the surround channel
(encode complement on decode). True Dolby B/NR is a licensed circuit; the hobbyist-honest
substitute is a **dynamic (audio) noise reduction** stage or simply relying on the 7 kHz
low-pass, which already tames hiss. For a faithful clone you can build a Dolby-B-style
companding NR around an **NE570/571** compander, but this is optional and most DIY builders skip
it once the low-pass is in place.

### 3d. (Optional) active steering → "Pro Logic"

Everything above is a **passive matrix** (fixed coefficients). Real **Pro Logic** adds *active
steering*: it senses the dominant direction and uses **VCAs** (e.g. THAT2180/2181 or the classic
NJM/Motorola surround chips) to boost separation — pulling dialog to center, ducking the
surround when the front is dominant. Building full analog steering is a significant project
(direction detectors + VCAs + control smoothing). If you want steering, the *modern* DIY answer
is to do it in **DSP** — a Teensy Audio board or an ADAU1701 SigmaDSP can implement Pro
Logic II–style steering logic far more easily than analog VCAs. Treat this as the "Stage 4"
stretch goal.

---

## Full signal flow

```
                 ┌──────────► L (buffer) ─────────────────────────────► L out
 Lt ────┬────────┤
        │        └──► (+) ┐
        │                 ├─► Σ  C = 0.7·(Lt+Rt) ──────────────────────► C out
 Rt ────┼────────┬──► (+) ┘
        │        └──────► R (buffer) ─────────────────────────────────► R out
        │
        └──► Δ  S = (Lt−Rt) ─► [100Hz HPF] ─► [~25ms delay] ─► [7kHz LPF] ─► S out
```

Feed the four outputs to four amplifier channels: **L, C** across the front, **R** front, and
**S** to *both* rear speakers in parallel (mono surround). Add a subwoofer off a summed
low-pass of L+R if you want a ".1".

---

## Calibration & test

You'll want a multimeter and, ideally, a phone signal-generator app.

1. **Center null test.** Feed the *same* mono tone to both Lt and Rt (in phase). Center output
   should be full level; **surround output should null to near-zero** (adjust the S difference
   resistors / add a trimpot in one input leg until it nulls deepest). A deep null = a clean
   matrix.
2. **Surround test.** Feed the same tone but **invert one channel** (out of phase). Now
   **surround should be full level and center should null.** This confirms the sum/difference is
   correct.
3. **Level match.** Play pink noise; with an SPL meter (phone app is fine) set all four
   speakers to equal loudness at the listening position. Center is typically run ~0 to +1 dB,
   surround −3 dB.
4. **Delay tune.** Sit in your seat, play material with strong front transients, and increase
   the surround delay until front sounds stop "leaking" to the rear and clearly localize
   forward — usually 15–25 ms depending on how far the rears are behind you.

## Bill of materials (analog build)

See the [consolidated BOM](04-bom-and-tools.md) for a shopping list and cost. Core parts:

- 3× dual op-amp (NE5532 or TL072) — matrix + filters
- 1× **PT2399** delay IC (+ its support R/C from the datasheet)
- ~20× 10 kΩ 1% metal-film resistors, assorted filter R/C
- 2–3× 10 kΩ trimpots (null/level calibration)
- ±9–12 V supply (batteries or wall-wart + TLE2426)
- RCA jacks, protoboard/PCB, enclosure

## TODO / stretch goals

- [ ] KiCad schematic + PCB Gerbers for Stages 2–3.
- [ ] Sallen-Key 7 kHz LPF values table.
- [ ] DSP steering (Teensy/ADAU1701) reference sketch for Pro Logic II behavior.
- [ ] NE570 Dolby-B-style NR sub-board (optional authenticity).

---

**Next:** [§2 · Digital formats on a Raspberry Pi →](02-digital-formats-rpi.md)

## Sources

- Sound On Sound, *Surround Sound Explained, Part 2*:
  <https://www.soundonsound.com/techniques/surround-sound-explained-part-2>
- Wikipedia, *Hafler circuit* (passive matrix wiring):
  <https://en.wikipedia.org/wiki/Hafler_circuit>
- ElectroSmash, *PT2399 Analysis* (delay circuit reference):
  <https://www.electrosmash.com/pt2399-analysis>
- Anasounds, *The alternative to BBD delays: the PT2399*:
  <https://anasounds.com/the-alternative-to-bbd-delays-the-pt2399/>
- Hackaday, *The PT2399 datasheet you never had*:
  <https://hackaday.com/2018/07/07/the-pt2399-delay-echo-chip-data-sheet-you-never-had/>
- *Pro Logic Surround Decoder: Principles of Operation*:
  <https://headwizememorial.wordpress.com/2018/03/15/pro-logic-surround-decoder-principles-of-operation/>
