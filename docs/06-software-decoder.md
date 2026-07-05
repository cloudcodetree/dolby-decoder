# 6 · The software decoder (`dolbydec/`)

The `dolbydec/` package is a **working matrix surround decoder in pure-stdlib Python** — the
software twin of [the analog circuit in §1](01-analog-matrix-decoder.md). Same math, same signal
chain, no soldering. It's the fastest way to *hear* the matrix idea and a reference you can read
line-by-line to understand what the op-amps are doing.

It decodes a stereo **Lt/Rt** signal into **L / C / R / S** (or a 5.1 bus). It is a *matrix*
decoder — it does **not** decode Dolby Digital / TrueHD / Atmos bitstreams (those need the
[Raspberry Pi + FFmpeg path](02-digital-formats-rpi.md); Atmos objects are unavailable to any
DIY tool — see [§3](03-atmos-reality.md)).

## Why pure standard library

No numpy, no scipy, no ffmpeg. It runs on a bare Python 3.9+ install — a Raspberry Pi, a laptop,
a locked-down machine. That portability is worth more than raw speed for a reference decoder, and
it means the DSP is written out explicitly (you can see every filter coefficient and every matrix
sum) rather than hidden behind a library call.

## Module → circuit map

Each module corresponds to a block of the [analog build](01-analog-matrix-decoder.md):

| Module | Does | Analog equivalent (§1) |
|---|---|---|
| `wavio.py` | read/write 16/24/32-bit PCM WAV as float channels | the ADC/DAC and I/O jacks |
| `dsp.py` · `Biquad` | high-pass / low-pass filters | the 100 Hz HPF & 7 kHz LPF op-amp stages |
| `dsp.py` · `Delay` | fixed-sample delay line | the PT2399 / MN3005 delay ([§3b](01-analog-matrix-decoder.md#3b-delay-1530-ms)) |
| `decode.py` · `MatrixDecoder` | the L/C/R/S sum-and-difference matrix + surround chain | the whole matrix + surround processing |
| `encode.py` · `encode` | fold L/C/R/S → Lt/Rt (for tests/demos) | a Dolby Surround *encoder* |
| `__main__.py` | the CLI | the front panel |

## The core: the matrix

`MatrixDecoder.decode()` implements exactly the formulas from
[§1](01-analog-matrix-decoder.md#the-math-youre-implementing):

```python
left     = Lt
right    = Rt
center   = 0.707 * (Lt + Rt)   # in-phase  content -> center   (summing amp)
surround = 0.707 * (Lt - Rt)   # anti-phase content -> surround (difference amp)
```

Then the surround channel gets the three real-decoder treatments, in order:

1. **Band-limit** to 100 Hz – 7 kHz (`dsp.band_pass`, a high-pass then a low-pass biquad).
2. **Delay** ~20 ms (`dsp.Delay`) — the Haas/precedence trick so front bleed localizes forward.
3. **Trim** −3 dB (`surround_trim_db`).

An optional `steering` parameter (0…1) mimics active Pro-Logic steering by pulling a fraction of
the derived center back out of L/R, tightening the phantom images. `0` = pure passive matrix.

## How it's verified

`tests/test_decode.py` proves the decoder actually separates channels, not just that it runs:

- **Center → center, not surround:** feed identical (in-phase) L/R; the surround output nulls to
  <1 % of the center. That deep null *is* the matrix working.
- **Surround → surround, not center:** feed anti-phase L/R; the center nulls instead.
- **Round-trip separation:** encode four distinct tones (220/440/660/330 Hz for L/C/R/S), decode,
  and confirm — with an exact-frequency (DFT-bin) detector — that each tone dominates its intended
  channel. Center content cancels in surround by >20× and vice-versa.
- **Band-limit works:** a 12 kHz surround tone is attenuated to <20 % by the 7 kHz low-pass.
- **Delay works:** a 20 ms delay leaves exactly 20 ms of leading silence in the surround output.

Measured separation on the reference signal is **~40 dB** — comparable to a well-calibrated
passive analog matrix.

```bash
python3 tests/test_decode.py
# PASS test_center_content_goes_to_center_not_surround
# PASS test_surround_content_goes_to_surround_not_center
# PASS test_encode_decode_round_trip_separation
# ... 7/7 passed
```

## Using it

### As a CLI

```bash
python3 -m dolbydec demo -o demo.wav                    # synthesize test material
python3 -m dolbydec decode demo.wav -o out_5_1.wav      # -> 6-ch 5.1 (FL FR FC LFE SL SR)
python3 -m dolbydec decode demo.wav --layout 4.0 -o q.wav
python3 -m dolbydec decode demo.wav --split out/        # separate L/C/R/S WAVs
python3 -m dolbydec decode in.wav --delay 25 --steering 0.4   # tune the surround
python3 -m dolbydec encode L.wav C.wav R.wav S.wav -o Lt_Rt.wav
```

Decode flags: `--delay` (ms), `--surround-low` / `--surround-high` (Hz band-limit),
`--steering` (0…1), `--layout` (`5.1` or `4.0`), `--split DIR`.

### As a library

```python
from dolbydec import read_wav, write_wav, MatrixDecoder, DecodeConfig

channels, fs = read_wav("stereo.wav")
lt, rt = channels[0], channels[1]

dec = MatrixDecoder(fs, DecodeConfig(surround_delay_ms=20.0, steering=0.3))
bus = dec.decode_to_51(lt, rt)          # [FL, FR, FC, LFE, SL, SR]
write_wav("out_5_1.wav", bus, fs)

# or get named channels:
ch = dec.decode(lt, rt)                 # {"L":..., "C":..., "R":..., "S":...}
```

## Bridging to the digital formats

This decoder handles the *matrix* half. For Dolby Digital / DD+ / TrueHD you decode the bitstream
to stereo/multichannel PCM first (FFmpeg, [§2](02-digital-formats-rpi.md)) — and you can then
feed that stereo downmix **into this decoder** to derive extra ambience/surround from any source,
including the stereo fold-down of a modern digital track. The two halves compose.

## TODO / stretch goals

- [ ] Fractional-sample (interpolated) delay for finer surround timing.
- [ ] A proper Pro-Logic-II-style 2-channel surround matrix (stereo surrounds, not mono).
- [ ] Active steering with a real dominance detector, not just the passive `steering` blend.
- [ ] Optional numpy fast-path (auto-detected) for real-time / long files.
- [ ] Streaming/block processing so filters and delay carry state across chunks (today it
      processes a whole file at once).

---

← Back to the [README](../README.md) · [§1 Analog build](01-analog-matrix-decoder.md)
