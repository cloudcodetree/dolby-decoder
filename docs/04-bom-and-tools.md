# 4 · Bill of materials & tools — with prices & buy links

Two shopping lists — the **analog matrix decoder** ([§1](01-analog-matrix-decoder.md)) and the
**digital front end** ([§2](02-digital-formats-rpi.md)) — each line with a best-value source and
a typical price.

> ⚠️ **Prices change — verify before you buy.** Figures below are typical US hobby-quantity
> prices as of **July 2026** and are meant for budgeting, not quoting. Component pricing moves
> (the Raspberry Pi in particular is volatile right now — see its note). Links point at a
> *representative* listing, not a guaranteed lowest price.

## How to source cheaply (read this first)

Where you buy matters more than which exact listing you pick:

- **Passives & jellybean ICs** (op-amps, PT2399, resistors, caps) — cheapest at
  **[Tayda Electronics](https://www.taydaelectronics.com)** (single pieces, pennies each) or in
  bulk kits on Amazon/AliExpress. Buying a **resistor kit + cap kit** once is far cheaper than
  buying values individually.
- **Authoritative/genuine parts** (datasheets, guaranteed-real chips) —
  **[Mouser](https://www.mouser.com)** / **[DigiKey](https://www.digikey.com)**. Worth it for
  the rail-splitter and any op-amp you're fussy about; overkill for a 10 kΩ resistor.
- **Modules & tools** (Pi, DACs, amp boards, meters, irons) — **Amazon** for speed,
  **AliExpress** for ~30–50 % less if you'll wait for shipping.
- **BBD / boutique audio chips** (MN3005 etc.) — **[Guitar Pedal Parts](https://guitarpedalparts.com)**
  or Xvive reissues.
- **Teensy** — buy direct from **[PJRC](https://www.pjrc.com)**; it's the cheapest and it funds
  the project.

A first-time builder with an empty parts bin spends most of the money on the **kits and tools**,
which then cover many future projects. The decoder-specific parts are cheap.

---

## Analog matrix decoder

### Core electronics

| Part | Purpose | Best-value source | ~Price |
|---|---|---|---|
| **NE5532** dual op-amp ×3 | L/R buffers, C sum, S difference, filters | [Tayda](https://www.taydaelectronics.com/ne5532-5532-ic-dual-low-noise-op-amp.html) ~$0.45 ea · [Amazon 20-pk](https://www.amazon.com/NE5532-Low-Noise-High-Speed-Operational-Amplifier/dp/B01EAWJ996) | $1.50 / $9 pk |
| **PT2399** delay IC ×1 (+ support R/C) | ~20–30 ms surround delay | [Tayda](https://www.taydaelectronics.com/pt2399-2399-echo-audio-processor-guitar-ic.html) · [StompboxParts](https://stompboxparts.com/semiconductors/pt2399-digital-delay-ic/) | ~$1.20 |
| **TLE2426** rail splitter (single-supply builds) | virtual ground for ±rails | [DigiKey TLE2426CP](https://www.digikey.com/en/products/detail/texas-instruments/TLE2426CP/371936) | ~$2.20 |
| **10 kΩ 1% metal-film** resistors (+ filter values) | matrix + filters | [Aniann 1280-pc 1% kit](https://www.amazon.com/Resistor-Assorted-Resistors-Assortment-Experiments/dp/B07L851T3V) | ~$13 (kit) |
| **Ceramic caps** (100 nF decoupling, 10 nF filter) | supply decoupling, 7 kHz LPF | [BOJACK/2100-pc ceramic kit](https://www.amazon.com/Value-2100-Ceramic-Capacitor-Assortment/dp/B019G8GJ24) | ~$13 (kit) |
| **Electrolytic caps** (10 µF DC-block, 1.6 µF) | I/O coupling, 100 Hz HPF | [electrolytic assortment kit](https://www.amazon.com/electrolytic-capacitor-assortment-kit/s?k=electrolytic+capacitor+assortment+kit) | ~$14 (kit) |
| **10 kΩ trimpots** ×3 | null & level calibration | [Amazon 10k trimpot pack](https://www.amazon.com/s?k=10k+trimmer+potentiometer+3296) · Tayda ~$0.30 ea | ~$8 (pk) |
| **RCA jacks** (2 in, 4–6 out) | I/O | [Amazon panel-mount RCA pack](https://www.amazon.com/s?k=panel+mount+rca+jack) | ~$8 (pk) |
| **Protoboard / perfboard** | build substrate | [Amazon perfboard pack](https://www.amazon.com/s?k=double+sided+prototype+pcb+board) | ~$10 (pk) |
| **Enclosure** (metal preferred for shielding) | housing | [ELECTRONIX EXPRESS ABS box](https://www.amazon.com/Plastic-Enclosure-EX-ELECTRONIX-EXPRESS/dp/B094NWJ7W5) · metal on [Amazon](https://www.amazon.com/s?k=aluminum+project+enclosure) | $9–18 |

**Analog core subtotal: ~$35–55** (most of it the reusable resistor/cap kits).

### Power

| Option | Parts | Source | ~Price |
|---|---|---|---|
| Batteries (first test) | 2× 9 V + clips | [9V battery clip pack](https://www.amazon.com/s?k=9v+battery+clip+connector) | ~$6 |
| Wall-wart + rail splitter | 12 V DC adapter + TLE2426 | [12V DC adapter](https://www.amazon.com/s?k=12v+2a+dc+power+adapter+5.5mm) + DigiKey TLE2426 | ~$10 |
| Linear ±12 V (permanent) | dual-rail supply module | [±12V linear PSU module](https://www.amazon.com/s?k=dual+rail+%C2%B112v+linear+power+supply) | $15–30 |

### Optional / stretch

| Part | Purpose | Source | ~Price |
|---|---|---|---|
| **MN3005** (+ MN3101 clock, NE570 compander) | authentic all-analog BBD delay instead of PT2399 | [Guitar Pedal Parts](https://guitarpedalparts.com/products/mn3005-bbd-bucket-brigade-delay-chip) · [Xvive 4-pk](https://www.amazon.com/Xvive-MN3005-Bucket-Brigade-Genuine/dp/B0BWHBDXTB) | $25–30 ea |
| **NE570/571** compander | Dolby-B-style surround noise reduction | [DigiKey / Mouser](https://www.mouser.com/c/?q=NE570) | ~$3 |
| **Teensy 4.0** + **Audio Adapter (Rev D)** | DSP Pro-Logic-II steering / upmix | [PJRC Teensy 4.0](https://www.pjrc.com/store/teensy40.html) $23.80 + [Audio Adapter](https://www.pjrc.com/store/teensy3_audio.html) $14.25 | ~$38 |
| **ADAU1701 SigmaDSP** board | alternative DSP steering | [AliExpress ADAU1701](https://www.aliexpress.com/w/wholesale-adau1701.html) | $8–15 |
| **OPA2134** op-amp | audiophile upgrade over NE5532 | [Mouser OPA2134](https://www.mouser.com/c/?q=OPA2134PA) · Tayda | ~$3.50 ea |
| **50 Ω ≥5 W wirewound pot** or L-pad | passive Hafler rear level ([Stage 1](01-analog-matrix-decoder.md#stage-1--the-passive-hafler-matrix)) | [Parts Express L-pad](https://www.parts-express.com/cat/l-pads) | $6–13 |

---

## Digital front end (Raspberry Pi)

| Part | Purpose | Best-value source | ~Price |
|---|---|---|---|
| **Raspberry Pi 5** (4 GB) + PSU + SD | runs FFmpeg decode | [raspberrypi.com](https://www.raspberrypi.com/products/raspberry-pi-5/) · [PiShop US](https://www.pishop.us/product-category/raspberry-pi/raspberry-pi-5/raspberry-pi-5-boards/) | **~$65** board ⚠️ |
| **USB S/PDIF / TOSLINK capture** | legal AC-3/optical input | [Cubilux USB SPDIF-in](https://www.amazon.com/Cubilux-Receiver-Interface-Suitable-Dell%E3%80%90ONLY/dp/B0BQQLFQ59) | $20–25 |
| **USB 5.1/7.1 DAC** (or I2S HAT) | multichannel analog out | [Optimal Shop 6-ch USB card](https://www.amazon.com/Optimal-Shop-External-Recording-Compatible/dp/B07BGS2BS1) | $15–30 |
| **HDMI audio extractor** (HDCP-2.2) — optional | HDMI-borne formats (with caveats) | [OREI HDA-912](https://www.amazon.com/OREI-HDA-912-Audio-Converter-Extractor/dp/B07BHYXVTY) · [HDA-913](https://www.orei.com/products/orei-hdmi-18gbps-audio-extractor-with-audio-downmix-hda-913) | $40–55 |
| Cabling (TOSLINK / RCA / speaker) | interconnect | Amazon / Monoprice | $10–20 |

**Digital front-end subtotal: ~$110–200** depending on DAC and whether you add HDMI.

> ⚠️ **Two caveats that don't show up on the price tag:**
> 1. **Raspberry Pi pricing is unstable in 2026** — memory-cost-driven rises pushed the 4 GB to
>    ~$65; the 1 GB model is still ~$45 and is plenty for audio decode. Check current price
>    before ordering. ([Raspberry Pi price news](https://www.raspberrypi.com/news/more-memory-driven-price-rises/))
> 2. **Cheap USB S/PDIF dongles often capture 2-channel PCM only**, not the raw AC-3
>    (IEC 61937) bitstream FFmpeg needs to decode 5.1. Confirm the device presents *encoded
>    passthrough* before relying on it, or feed FFmpeg from **files** instead. And the HDMI
>    extractor still **can't** give you Atmos objects ([§3](03-atmos-reality.md)).

---

## Amps & speakers (shared)

You need amplification and speakers for however many channels you decode (front L/R you likely
already own; add center, surround, and optionally a sub).

| Part | Purpose | Source | ~Price |
|---|---|---|---|
| **TPA3116 4-/5.1-ch class-D amp board** | drive center + surround (+ sub) | [4.1 board (4×50 W+100 W)](https://www.amazon.com/TPA3116-digital-power-amplifier-Assembled/dp/B07Z4Q5YK3) · [5.1 board](https://www.amazon.com/TPA3116-Amplifier-Channel-Digital-DC12-24V/dp/B07NPS2MZT) | $18–30 |
| Bookshelf/center/surround speakers | reproduce derived channels | thrift/used or [Parts Express](https://www.parts-express.com) | varies |

---

## Tools

| Tool | For | Source | ~Price |
|---|---|---|---|
| **Digital multimeter** | rails, null calibration, continuity | [AstroAI 2000-count](https://www.amazon.com/AstroAI-Digital-Multimeter-Voltage-Tester/dp/B01ISAMUA6) | $12–17 |
| **Soldering iron kit** (adjustable temp) | assembly | [60 W adjustable kit](https://www.amazon.com/Soldering-Electronics-Adjustable-Temperature-Desoldering/dp/B0756VKPTB) | $20–30 |
| **Breadboard + jumper kit** | prototype Stages 1–2 | [830-pt breadboard + wires](https://www.amazon.com/Solderless-Breadboard-jumper-supply-connector/dp/B01M11AVG8) | $10–13 |
| Wire strippers / flush cutters | general | [Amazon](https://www.amazon.com/s?k=wire+stripper+flush+cutter+set) | $10–15 |
| Phone signal-gen + SPL-meter apps | test tones, level match, null depth | free (app store) | $0 |
| Oscilloscope (nice-to-have) | verify delay/filter/phase | [budget DSO](https://www.amazon.com/s?k=fnirsi+dso) | $40–70 |

---

## Total cost snapshot

| Build | Rough total (parts only) |
|---|---|
| Passive Hafler only ([Stage 1](01-analog-matrix-decoder.md#stage-1--the-passive-hafler-matrix)) | **~$5–15** (speaker wire + 2 rear speakers you may own) |
| Full analog matrix decoder (Stages 2–3) | **~$40–70** + amp/speakers |
| Digital front end (Pi + optical + DAC) | **~$110–200** + amp/speakers |
| Everything (analog + digital + a TPA3116 amp) | **~$170–320** + speakers |
| **Tools** (one-time, reused forever) | **~$50–90** |

Software costs nothing — the [`dolbydec` decoder](06-software-decoder.md) runs on hardware you
already have, so you can build and hear the matrix *before* buying a single component.

---

**Next:** [§5 · Safety & legal →](05-safety-and-legal.md)

## Sources (pricing & vendors, retrieved July 2026)

- Tayda Electronics — [PT2399](https://www.taydaelectronics.com/pt2399-2399-echo-audio-processor-guitar-ic.html),
  [NE5532](https://www.taydaelectronics.com/ne5532-5532-ic-dual-low-noise-op-amp.html)
- DigiKey — [TLE2426CP rail splitter](https://www.digikey.com/en/products/detail/texas-instruments/TLE2426CP/371936)
- Raspberry Pi — [Pi 5 product page](https://www.raspberrypi.com/products/raspberry-pi-5/),
  [2026 price-rise news](https://www.raspberrypi.com/news/more-memory-driven-price-rises/)
- PJRC — [Teensy 4.0](https://www.pjrc.com/store/teensy40.html) & [Audio Adapter](https://www.pjrc.com/store/teensy3_audio.html)
- Guitar Pedal Parts — [MN3005 BBD](https://guitarpedalparts.com/products/mn3005-bbd-bucket-brigade-delay-chip)
- OREI — [HDA-912 HDMI audio extractor](https://www.amazon.com/OREI-HDA-912-Audio-Converter-Extractor/dp/B07BHYXVTY)
- Amazon listings for kits/tools (resistor, capacitor, breadboard, multimeter, soldering iron,
  TPA3116, USB DAC, USB S/PDIF capture) — linked inline above.
