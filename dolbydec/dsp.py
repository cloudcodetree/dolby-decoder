"""DSP building blocks — pure standard library.

These mirror the analog stages in docs/01-analog-matrix-decoder.md:

* :class:`Biquad`  -> the op-amp Sallen-Key filters (7 kHz LPF, 100 Hz HPF).
* :class:`Delay`   -> the PT2399 / BBD delay line on the surround channel.

Everything processes plain Python lists of floats, sample by sample, so there
are no third-party dependencies.
"""

from __future__ import annotations

import math


class Biquad:
    """A Direct-Form-I biquad filter (RBJ audio-EQ-cookbook coefficients).

    Use :meth:`low_pass` / :meth:`high_pass` to construct one, then call
    :meth:`process` on a signal.
    """

    def __init__(self, b0: float, b1: float, b2: float,
                 a1: float, a2: float) -> None:
        # Coefficients are pre-normalized by a0.
        self.b0, self.b1, self.b2 = b0, b1, b2
        self.a1, self.a2 = a1, a2

    @classmethod
    def low_pass(cls, fs: float, fc: float, q: float = 0.70710678) -> "Biquad":
        return cls._design(fs, fc, q, kind="lp")

    @classmethod
    def high_pass(cls, fs: float, fc: float, q: float = 0.70710678) -> "Biquad":
        return cls._design(fs, fc, q, kind="hp")

    @classmethod
    def _design(cls, fs: float, fc: float, q: float, kind: str) -> "Biquad":
        w0 = 2.0 * math.pi * fc / fs
        cos_w0 = math.cos(w0)
        alpha = math.sin(w0) / (2.0 * q)
        if kind == "lp":
            b0 = (1.0 - cos_w0) / 2.0
            b1 = 1.0 - cos_w0
            b2 = (1.0 - cos_w0) / 2.0
        elif kind == "hp":
            b0 = (1.0 + cos_w0) / 2.0
            b1 = -(1.0 + cos_w0)
            b2 = (1.0 + cos_w0) / 2.0
        else:  # pragma: no cover - guarded by callers
            raise ValueError(kind)
        a0 = 1.0 + alpha
        a1 = -2.0 * cos_w0
        a2 = 1.0 - alpha
        return cls(b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0)

    def process(self, x: list[float]) -> list[float]:
        b0, b1, b2, a1, a2 = self.b0, self.b1, self.b2, self.a1, self.a2
        x1 = x2 = y1 = y2 = 0.0
        out = [0.0] * len(x)
        for i, xn in enumerate(x):
            yn = b0 * xn + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
            out[i] = yn
            x2, x1 = x1, xn
            y2, y1 = y1, yn
        return out


def band_pass(signal: list[float], fs: float,
              low_hz: float, high_hz: float) -> list[float]:
    """Cascade a high-pass and a low-pass to band-limit a signal.

    Dolby Surround band-limits the surround channel to roughly 100 Hz - 7 kHz.
    """
    hp = Biquad.high_pass(fs, low_hz).process(signal)
    return Biquad.low_pass(fs, high_hz).process(hp)


class Delay:
    """A simple fixed integer-sample delay line (the surround delay)."""

    def __init__(self, delay_samples: int) -> None:
        if delay_samples < 0:
            raise ValueError("delay must be non-negative")
        self.n = delay_samples

    def process(self, x: list[float]) -> list[float]:
        if self.n == 0:
            return list(x)
        # Prepend n zeros (the delay) and keep the original length.
        return ([0.0] * self.n + x)[: len(x)]


def ms_to_samples(ms: float, fs: float) -> int:
    return int(round(ms * 1e-3 * fs))
