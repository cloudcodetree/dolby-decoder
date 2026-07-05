"""Minimal WAV I/O — pure standard library, no numpy.

Reads/writes PCM WAV files as lists of float channels in the range [-1.0, 1.0].
Supports 16-, 24-, and 32-bit integer PCM (the formats you actually get from
consumer sources). Keeping this dependency-free means the decoder runs on a bare
Python 3 install — a Raspberry Pi, a laptop, anywhere.
"""

from __future__ import annotations

import wave


def read_wav(path: str) -> tuple[list[list[float]], int]:
    """Read a PCM WAV file.

    Returns ``(channels, sample_rate)`` where ``channels`` is a list of channel
    signals, each a list of floats in [-1.0, 1.0].
    """
    with wave.open(path, "rb") as w:
        n_channels = w.getnchannels()
        sampwidth = w.getsampwidth()
        sample_rate = w.getframerate()
        n_frames = w.getnframes()
        raw = w.readframes(n_frames)

    samples = _bytes_to_floats(raw, sampwidth)
    # De-interleave: frame i, channel c lives at samples[i * n_channels + c].
    channels: list[list[float]] = [[] for _ in range(n_channels)]
    for i in range(0, len(samples), n_channels):
        for c in range(n_channels):
            channels[c].append(samples[i + c])
    return channels, sample_rate


def write_wav(path: str, channels: list[list[float]], sample_rate: int,
              sampwidth: int = 3) -> None:
    """Write channel float signals to a PCM WAV file.

    ``sampwidth`` is in bytes: 2 = 16-bit, 3 = 24-bit (default), 4 = 32-bit.
    Channels are hard-clipped to [-1.0, 1.0] before quantization.
    """
    if not channels:
        raise ValueError("no channels to write")
    n_channels = len(channels)
    n_frames = max(len(ch) for ch in channels)

    # Interleave, padding short channels with silence.
    interleaved: list[float] = []
    for i in range(n_frames):
        for ch in channels:
            interleaved.append(ch[i] if i < len(ch) else 0.0)

    raw = _floats_to_bytes(interleaved, sampwidth)
    with wave.open(path, "wb") as w:
        w.setnchannels(n_channels)
        w.setsampwidth(sampwidth)
        w.setframerate(sample_rate)
        w.writeframes(raw)


def _bytes_to_floats(raw: bytes, sampwidth: int) -> list[float]:
    if sampwidth == 2:
        import array
        a = array.array("h")  # signed 16-bit
        a.frombytes(raw)
        _swap_if_big_endian(a)
        return [s / 32768.0 for s in a]
    if sampwidth == 4:
        import array
        a = array.array("i")  # signed 32-bit
        a.frombytes(raw)
        _swap_if_big_endian(a)
        return [s / 2147483648.0 for s in a]
    if sampwidth == 3:
        # 24-bit little-endian signed, 3 bytes per sample.
        out: list[float] = []
        for i in range(0, len(raw), 3):
            b0, b1, b2 = raw[i], raw[i + 1], raw[i + 2]
            val = b0 | (b1 << 8) | (b2 << 16)
            if val & 0x800000:  # sign-extend
                val -= 1 << 24
            out.append(val / 8388608.0)
        return out
    raise ValueError(f"unsupported sample width: {sampwidth} bytes")


def _floats_to_bytes(samples: list[float], sampwidth: int) -> bytes:
    def clip(x: float) -> float:
        return -1.0 if x < -1.0 else 1.0 if x > 1.0 else x

    if sampwidth == 2:
        import array
        a = array.array("h", (int(clip(x) * 32767.0) for x in samples))
        _swap_if_big_endian(a)
        return a.tobytes()
    if sampwidth == 4:
        import array
        a = array.array("i", (int(clip(x) * 2147483647.0) for x in samples))
        _swap_if_big_endian(a)
        return a.tobytes()
    if sampwidth == 3:
        out = bytearray()
        for x in samples:
            val = int(clip(x) * 8388607.0)
            if val < 0:
                val += 1 << 24
            out.append(val & 0xFF)
            out.append((val >> 8) & 0xFF)
            out.append((val >> 16) & 0xFF)
        return bytes(out)
    raise ValueError(f"unsupported sample width: {sampwidth} bytes")


def _swap_if_big_endian(a) -> None:
    import sys
    if sys.byteorder == "big":
        a.byteswap()
