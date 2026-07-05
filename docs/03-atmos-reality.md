# 3 · The Atmos reality — why you can't DIY object audio (and what you *can* do)

You asked for "all the formats, even Atmos." Here's the straight answer, because it's the part
of this project where wishful thinking meets a hard wall.

## Why Atmos is different

Every format before Atmos was **channel-based**: the mix is a fixed set of speaker feeds
(2.0, 5.1, 7.1). Whether matrixed ([§1](01-analog-matrix-decoder.md)) or discrete
([§2](02-digital-formats-rpi.md)), decoding means recovering *those channels*.

**Atmos is object-based.** The mix is:

- a **bed** — a conventional 5.1 or 7.1 channel mix, *plus*
- up to ~118 **audio objects** — individual sounds, each tagged with **3D position metadata**
  (where it should be in the room, moment to moment), *plus*
- instructions for a **renderer** to place those objects onto *your* actual speaker layout
  (5.1.2, 7.1.4, a soundbar, or binaural headphones).

The intelligence isn't in the audio — it's in the **metadata + renderer**. And that renderer is
**proprietary, patented, and licensed by Dolby**. There is **no open-source Atmos renderer**,
and no combination of op-amps, FFmpeg, or a Raspberry Pi will produce one.

## What actually happens if you feed Atmos to open tools

Atmos is always carried *on top of* a normal Dolby stream:

- **Streaming:** Dolby Digital Plus with **JOC** (Joint Object Coding) — `E-AC-3 (Atmos)`.
- **Blu-ray:** Dolby TrueHD with embedded Atmos metadata — `TrueHD (Atmos)`.

When you decode one of those with FFmpeg (from [§2](02-digital-formats-rpi.md)):

```bash
ffmpeg -i movie_atmos.mkv -map 0:a:0 -c:a pcm_s24le decoded.wav
```

…FFmpeg decodes the **underlying TrueHD or E-AC-3 core** — i.e. the **5.1 or 7.1 bed** — and
**silently discards the Atmos objects and height information.** You get a perfectly good
surround mix; you do **not** get the "sounds moving overhead" object experience. As practitioners
put it bluntly: Atmos is *metadata that doesn't get converted* — no non-Dolby-licensed software
decodes it.

So on the DIY bench, **"decoding Atmos" collapses to "decoding its 5.1/7.1 bed."** That's the
honest ceiling.

## The three things blocking a true DIY Atmos decoder

1. **No open renderer.** The object-to-speaker rendering math and metadata format are not
   published in a form you can implement, and Dolby licenses it per-device. Nothing in FFmpeg,
   GStreamer, or any hobbyist toolchain renders objects.
2. **HDCP on the input.** To even get a TrueHD+Atmos bitstream off a Blu-ray/streaming source
   you must pass HDCP-protected HDMI. Compliant extractors downmix it; stripping HDCP to grab the
   raw stream is legally restricted ([safety & legal](05-safety-and-legal.md)).
3. **Patents & licensing.** The codecs and the Atmos system are patented. Reimplementing a
   *decoder* has been done for the older channel codecs (FFmpeg); reimplementing the *Atmos
   renderer* has not, and doing so commercially would require a Dolby license.

## What you *can* realistically do

Ranked from most-DIY to least:

### A. Decode and enjoy the bed (fully DIY, honest)

Use the [Pi + FFmpeg path](02-digital-formats-rpi.md) to decode the TrueHD/DD+ **core** to
5.1/7.1 PCM and play it on your speakers. You lose height/objects but get the full surround bed —
which is the majority of the energy in most mixes. **This is the achievable DIY endpoint for
"Atmos" content.**

### B. Fake height/immersion with a matrix (fully DIY, fun)

Feed the decoded bed (or any stereo/5.1 signal) into an **upmixing matrix** — your
[analog matrix from §1](01-analog-matrix-decoder.md), or a DSP upmixer (Teensy/ADAU1701) — and
derive **extra ambience channels**, including height, from the difference/reverberant content.
It is **not** true Atmos rendering (there's no object metadata driving it), but a well-tuned
upmixer with height speakers gives a convincing "bigger, taller" effect from ordinary material.
This is the spiritual DIY answer to "I want overhead sound."

### C. Let a licensed device do the render (not DIY, but complete)

If you genuinely need *real* Atmos object rendering, the only route is a **Dolby-licensed
renderer**: an AVR/soundbar, or software like the Dolby Reference Player / a licensed media
app. You can still DIY *around* it (amps, speakers, wiring, room), but the object decode itself
must be licensed. There's no shame in this — it's the same reason you buy a Blu-ray drive rather
than machining one.

### D. Author/monitor Atmos yourself (adjacent, legit)

If your interest is *creating* Atmos, the **Dolby Atmos Renderer** software and DAWs (with the
Dolby production suite) let you author and monitor object mixes on your own speakers under a
production license. Different goal from "decode a movie," but a fully legitimate way to work with
objects hands-on.

## Summary

| Goal | DIY-achievable? | How |
|---|---|---|
| Play the 5.1/7.1 **bed** of Atmos content | ✅ yes | [Pi + FFmpeg](02-digital-formats-rpi.md) |
| Derive extra/height ambience from any source | ✅ yes | [matrix](01-analog-matrix-decoder.md) or DSP upmix |
| **True object rendering** (real Atmos) | ❌ no (DIY) | requires a Dolby-licensed renderer |
| Author/monitor your own Atmos mix | ✅ (licensed prod tools) | Dolby Atmos Renderer + DAW |

**The honest headline:** you can build a great surround system that *plays* Atmos content and
*sounds* immersive, but you cannot build the Atmos *object renderer* itself. Anyone claiming a
from-scratch DIY Atmos decoder is either decoding the bed and calling it Atmos, or relying on a
licensed component.

---

**Next:** [§4 · Bill of materials & tools →](04-bom-and-tools.md)

## Sources

- VideoHelp Forum, *Is conversion of Atmos to DTS/EAC3 possible?* — "Atmos is metadata that
  doesn't get converted": <https://forum.videohelp.com/threads/404898-Is-conversion-of-Atmos-to-DTS-EAC3-possible>
- GitHub / Tdarr, *Transcode TrueHD Atmos → EAC-3/AC3* (objects lost on transcode):
  <https://github.com/HaveAGitGat/Tdarr/issues/891>
- AVS Forum, *TrueHD → E-AC-3 with FFmpeg* (open decoders handle the core, not objects):
  <https://www.avsforum.com/threads/audio-conversion-of-a-truehd-video-to-e-ac3-dd-using-ffmpeg-to-convert.3189351/>
