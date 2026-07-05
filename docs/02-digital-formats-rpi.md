# 2 · Digital formats on a Raspberry Pi — Dolby Digital / DD+ / TrueHD

You **cannot build** a Dolby Digital (AC-3), Dolby Digital Plus (E-AC-3), or TrueHD decoder from
components — they're patented perceptual/lossless codecs, not analog relationships. What you
*can* do is **run** an existing decoder. FFmpeg's `libavcodec` contains open reimplementations
of the `ac3`, `eac3`, and `truehd` decoders, so a Raspberry Pi can take a Dolby bitstream and
output **decoded multichannel PCM** to feed your amplifiers (or the analog matrix from
[§1](01-analog-matrix-decoder.md)).

This section is the DIY *plumbing*: getting the bitstream in, decoding it, and getting analog
out. It's honest about the two hard walls — **HDCP** on the input and **Atmos objects** on the
"advanced" formats (Atmos gets its [own section](03-atmos-reality.md)).

## Architecture

```
 ┌─────────────┐   S/PDIF or       ┌───────────────┐  decoded    ┌──────────────┐
 │  Source     │   HDMI audio      │ Raspberry Pi  │  PCM        │ Multichannel │
 │ (player,    │──────────────────►│  + FFmpeg     │────────────►│ USB DAC /    │──► amps
 │  TV, etc.)  │   AC-3 / EAC3 /   │  decode → PCM │  (5.1/7.1)  │ HDMI / I2S   │
 └─────────────┘   TrueHD stream   └───────────────┘             └──────────────┘
```

The two input paths differ a lot in what they can carry:

| Input | Carries | Notes |
|---|---|---|
| **Optical / coax S/PDIF** | AC-3 and DTS 5.1 (compressed), or 2.0 PCM | Bandwidth-limited: **no** TrueHD/DD+/Atmos, no HDCP issue. Simplest, most reliable. |
| **HDMI (via extractor)** | Up to TrueHD/DD+/Atmos bitstream | **HDCP-encrypted** from commercial sources — see below. |

## Getting the bitstream in

### Easy, legal path: optical S/PDIF (start here)

Most TVs, disc players, and consoles have an **optical (TOSLINK) out** that emits **Dolby
Digital (AC-3) 5.1**. Feed it to the Pi with a cheap **USB S/PDIF / TOSLINK capture** input.
S/PDIF has no encryption and carries AC-3 fine. This decodes the single most common Dolby format
with zero legal ambiguity. Limitation: S/PDIF bandwidth **cannot** carry DD+, TrueHD, or Atmos —
those only travel over HDMI.

### Advanced path: HDMI audio extractor — and the HDCP wall

An **HDMI audio extractor** splits an HDMI signal and breaks out the audio (often as S/PDIF plus
sometimes 7.1). To carry the *high-bitrate* formats (DD+, TrueHD, Atmos) you need one that
passes them and a way to capture them.

**The catch — HDCP.** Commercial HDMI sources (Blu-ray players, streaming sticks) encrypt the
link with **HDCP**. A *compliant* extractor (e.g. HDMI 2.0 / HDCP 2.2 devices like the OREI
HDA-913) will pass the picture but typically **downmixes** the advanced bitstream to 2-channel
or basic AC-3 for its analog/optical outputs, and will **not** hand you the raw TrueHD/Atmos
bitstream. Devices that *strip* HDCP to expose the raw stream exist, but **circumventing HDCP on
content you don't own the rights to is illegal in many jurisdictions** (DMCA §1201 in the US and
equivalents elsewhere). See [safety & legal](05-safety-and-legal.md).

> **Bottom line on inputs:** for a clean, legal DIY build, target **AC-3 over optical** (covers
> DVDs, broadcast, consoles, most TVs). Treat DD+/TrueHD/Atmos capture as a gray/blocked area
> that depends entirely on your source and local law — and even when you *can* capture it, Atmos
> objects are still lost ([§3](03-atmos-reality.md)).

## Decoding with FFmpeg

Once the Pi has a Dolby bitstream (from a file, or a capture device presenting it as an input),
FFmpeg does the decode. Install:

```bash
sudo apt update && sudo apt install ffmpeg
ffmpeg -decoders | grep -Ei 'ac3|eac3|truehd|mlp'   # confirm ac3, eac3, truehd present
```

### Decode a Dolby Digital file to 6-channel PCM (5.1)

```bash
# AC-3 (Dolby Digital) → raw interleaved 5.1 float PCM at 48 kHz
ffmpeg -i input.ac3 -c:a pcm_f32le -ac 6 -ar 48000 -f wav out_5_1.wav
```

### Decode the Dolby track out of a video, keeping 5.1

```bash
# Pull the Dolby Digital / DD+ / TrueHD track and decode to multichannel PCM
ffmpeg -i movie.mkv -map 0:a:0 -c:a pcm_s24le -ac 6 decoded_5_1.wav
```

### Live decode from a capture input to a multichannel DAC (ALSA)

```bash
# Take AC-3 from an S/PDIF capture, decode, and play out a 6-channel USB DAC
ffmpeg -f alsa -i spdif_capture \
       -c:a pcm_s16le -ac 6 \
       -f alsa surround51:CARD=USBDAC
```

FFmpeg decodes **AC-3, E-AC-3, and TrueHD** to PCM. It does **not** re-render Atmos objects — a
TrueHD+Atmos or DD+Atmos stream decodes to its **channel bed** (5.1 or 7.1) with the objects
discarded. That's a limitation of every open decoder, not of FFmpeg specifically.

## Getting multichannel analog out

The Pi's own outputs are stereo. To get 5.1/7.1 analog you need one of:

- **USB multichannel DAC** (e.g. a 5.1/7.1 USB sound card) — simplest, appears as an ALSA
  `surround51`/`surround71` device.
- **HDMI to an AVR** — but then the AVR is doing the decoding, defeating the DIY purpose.
- **I2S multichannel DAC HAT** — cleanest audio, more wiring; good if you want a permanent unit.

Route FFmpeg's channels to the DAC and the DAC's line outs to your power amps (or to the
[analog matrix's](01-analog-matrix-decoder.md) inputs if you want to derive extra channels).

## Channel mapping

FFmpeg's 5.1 channel order (default) is: **FL, FR, FC, LFE, BL, BR**. Make sure your DAC's
physical outputs match — remap with FFmpeg's `pan`/`channelmap` filter if not:

```bash
# Example: reorder to FL FR FC LFE SL SR for a DAC that expects that layout
ffmpeg -i in.ac3 -af "channelmap=channel_layout=5.1" -ac 6 -f wav out.wav
```

## Putting it together — a practical DIY unit

1. **Raspberry Pi 4/5** running Raspberry Pi OS.
2. **Input:** USB S/PDIF/TOSLINK capture for AC-3 (legal, reliable) — or an HDMI extractor if
   your source and law allow the advanced formats.
3. **Decode:** an FFmpeg service/script (systemd unit) that decodes the incoming stream to PCM.
4. **Output:** 6- or 8-channel USB DAC → power amps.
5. Optionally feed the DAC's front L/R into the [analog matrix](01-analog-matrix-decoder.md) to
   derive extra ambience channels from any 2-channel source.

## What each format gives you here

| Source format | Over optical? | FFmpeg decodes to | You get |
|---|---|---|---|
| Dolby Digital (AC-3) | ✅ yes | 5.1 PCM | full 5.1 ✅ |
| Dolby Digital Plus (E-AC-3) | ❌ HDMI only | up to 7.1 PCM | full bed ✅ (if you can capture it) |
| Dolby TrueHD | ❌ HDMI only | lossless 5.1/7.1 PCM | full bed ✅ (if you can capture it) |
| Dolby Atmos (DD+/TrueHD JOC) | ❌ HDMI only | the **bed** only | ⚠️ objects **lost** — [§3](03-atmos-reality.md) |

## TODO / stretch goals

- [ ] `scripts/decode.sh` + a systemd unit for hands-off live decode.
- [ ] Auto-detect codec from the S/PDIF stream and switch decode params.
- [ ] Bass management / crossover in FFmpeg (LFE + redirected lows) for small speakers.

---

**Next:** [§3 · The Atmos reality →](03-atmos-reality.md)

## Sources

- Raspberry Pi Forums, *HDMI Audio Extractor*:
  <https://forums.raspberrypi.com/viewtopic.php?t=292376>
- AVS Forum, *Converting TrueHD to E-AC-3 with FFmpeg* (codec support/limits):
  <https://www.avsforum.com/threads/audio-conversion-of-a-truehd-video-to-e-ac3-dd-using-ffmpeg-to-convert.3189351/>
- VideoHelp Forum, *Is conversion of Atmos to DTS/EAC3 possible?* (Atmos = metadata, not
  converted): <https://forum.videohelp.com/threads/404898-Is-conversion-of-Atmos-to-DTS-EAC3-possible>
- OREI HDA-913 (example HDCP-2.2 compliant extractor/downmixer):
  <https://www.orei.com/products/orei-hdmi-18gbps-audio-extractor-with-audio-downmix-hda-913>
