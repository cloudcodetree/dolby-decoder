# 0 · Formats primer — how Dolby actually encodes sound

Before you build anything, understand *how* each format packs surround information into a
signal. This single fact — **matrix vs. discrete vs. object** — decides whether you can decode
it with a soldering iron, a Raspberry Pi, or not at all.

## The three families

### 1. Matrix (analog, "encoded into stereo")

**Dolby Surround** (1982) and **Dolby Pro Logic** (1987) are *4:2:4 matrix* systems. Four
channels — **L**eft, **C**enter, **R**ight, and a single mono **S**urround — are folded
("encoded") into an ordinary two-channel signal called **Lt/Rt** (Left-total / Right-total):

```
Lt = L + 0.707·C + 0.707·(surround, +90° phase, band-limited)
Rt = R + 0.707·C − 0.707·(surround, −90° phase, band-limited)
```

The magic is entirely in **phase and amplitude relationships**:

- **Center** is sent equally and *in phase* to both Lt and Rt (at −3 dB each). A decoder
  recovers it by *adding*: `C ≈ Lt + Rt`.
- **Surround** is sent equally but *in opposite phase* (±90°, giving 180° between the two) and
  band-limited to roughly **100 Hz – 7 kHz**. A decoder recovers it by *subtracting*:
  `S ≈ Lt − Rt`.

Because it's just sums and differences of two analog channels, **you can decode this with a
handful of op-amps** — or even *passively* with nothing but speaker wire (the Hafler trick).
That's the entire basis of [the analog build](01-analog-matrix-decoder.md).

Dolby Surround is itself a movie-theater adaptation of 1970s quadraphonic matrix systems
(Sansui QS, CBS SQ, and the Dynaco/Hafler passive matrix). The math is the same lineage.

**Pro Logic** adds *active steering*: it continuously measures the dominant sound direction and
uses voltage-controlled amplifiers (VCAs) to enhance separation — pulling dialog to the center,
pushing effects to the surround. **Pro Logic II** extends the surround to stereo (two rear
channels) with a more sophisticated matrix and better steering.

> **Buildability:** passive matrix — trivial. Active op-amp matrix + center + delayed
> surround — a weekend. Full Pro Logic steering logic — hard in pure analog, but a natural fit
> for a DSP/microcontroller if you want to go further.

### 2. Discrete (digital, "separate channels in a bitstream")

Starting with **Dolby Digital (AC-3)** in 1991, channels stopped being folded together. Each
channel (up to 5.1: L, C, R, Ls, Rs, LFE) is coded **separately** and compressed using a
perceptual codec (a modified DCT / "AC-3" transform, psychoacoustic bit allocation, Huffman-ish
mantissa coding). The result is a compressed **bitstream**, not an analog waveform.

- **Dolby Digital (AC-3)**: 5.1 channels, ~384–640 kbps. The DVD/broadcast workhorse.
- **Dolby Digital Plus (E-AC-3)**: extends AC-3 to more channels (7.1+) and higher/variable
  bitrates. The streaming-service workhorse.
- **Dolby TrueHD**: **lossless** — based on **MLP** (Meridian Lossless Packing). Bit-for-bit
  identical to the studio master, up to 7.1+, used on Blu-ray.

To decode these you must **parse a patented bitstream and run the inverse transform**. This is
software, and the underlying patents/decoders are licensed by Dolby. The good news: the
formats have been reverse-engineered and reimplemented in **FFmpeg/libavcodec** (`ac3`,
`eac3`, `truehd` decoders), so on a Raspberry Pi you can *run* a decoder even though you'd never
*build* one from scratch. See [digital formats on a Pi](02-digital-formats-rpi.md).

> **Buildability:** you don't build a discrete decoder — you run one. The DIY work is the
> *plumbing*: getting the bitstream out of an HDMI/optical source and the decoded PCM into your
> amplifiers.

### 3. Object-based (Atmos)

**Dolby Atmos** (2012) is a different paradigm again. Instead of a fixed set of channels, it
carries **audio objects** — individual sounds *plus metadata describing where each one should
be in 3D space* (x, y, z coordinates over time). A **renderer** in the playback device places
each object onto whatever speakers you actually have (5.1.2, 7.1.4, a soundbar, headphones…).

For distribution, Atmos rides **on top of** an existing discrete format:

- **Dolby Digital Plus + Atmos (E-AC-3 JOC)** — streaming. "Joint Object Coding" metadata.
- **Dolby TrueHD + Atmos** — Blu-ray. Atmos metadata inside the TrueHD stream.

Crucially, the **object metadata and the spatial renderer are proprietary and licensed** —
there is **no open-source Atmos renderer**. FFmpeg will happily decode the *underlying*
TrueHD or E-AC-3 core (the "bed" — typically a 5.1 or 7.1 mix), but it **discards the Atmos
objects**. You cannot DIY the height/object experience. See
[the Atmos reality](03-atmos-reality.md).

> **Buildability:** ❌ not decodable by any hobbyist tool. You get the channel bed underneath,
> never the objects.

## Why this matters for your build

| If the source is… | The surround info lives in… | Your decoder is… |
|---|---|---|
| VHS Hi-Fi, old TV, analog Pro Logic, a stereo mix | **phase/amplitude of 2 analog channels** | **the op-amp matrix you build** ([§1](01-analog-matrix-decoder.md)) |
| DVD, broadcast, most streaming (Dolby Digital) | **a discrete compressed bitstream** | **FFmpeg on a Pi** ([§2](02-digital-formats-rpi.md)) |
| Blu-ray (TrueHD), 4K streaming (DD+/Atmos) | **discrete bitstream + object metadata** | **FFmpeg for the bed; objects are lost** ([§3](03-atmos-reality.md)) |

A pleasant surprise: the analog matrix decoder is not obsolete. Because *any* stereo signal has
an L−R difference component, a matrix decoder extracts a listenable "ambience" surround from
**everything** — including the stereo downmix of a modern digital source. So the hardware you
build in §1 is useful even when you're playing Netflix.

---

**Next:** [§1 · The analog matrix decoder →](01-analog-matrix-decoder.md)

## Sources & further reading

- Sound On Sound, *Surround Sound Explained, Part 2* (matrix encode/decode):
  <https://www.soundonsound.com/techniques/surround-sound-explained-part-2>
- David Griesinger, *Multichannel matrix surround decoders for two-eared listeners* (PDF):
  <http://www.davidgriesinger.com/sur.pdf>
- *Pro Logic Surround Decoder: Principles of Operation* (HeadWize):
  <https://headwizememorial.wordpress.com/2018/03/15/pro-logic-surround-decoder-principles-of-operation/>
- MATLAB, *Surround Sound Matrix Encoding and Decoding*:
  <https://www.mathworks.com/help/audio/ug/surround-sound-matrix-encoding-and-decoding.html>
- Wikipedia, *Hafler circuit*: <https://en.wikipedia.org/wiki/Hafler_circuit>
