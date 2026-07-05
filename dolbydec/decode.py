"""Matrix surround decoder — the software twin of the analog circuit.

Implements the classic Dolby-Surround / Pro-Logic-style 4:2:4 *passive matrix*
decode described in docs/01-analog-matrix-decoder.md:

    L =  Lt
    R =  Rt
    C =  k * (Lt + Rt)      # in-phase content  -> center  (summing amp)
    S =  k * (Lt - Rt)      # anti-phase content -> surround (difference amp)

The surround channel then gets the three treatments a real decoder applies:
band-limiting (~100 Hz - 7 kHz), a delay (~20 ms, the Haas/precedence trick),
and a level trim. Optional *passive steering* sharpens separation the way an
active Pro-Logic decoder does, without needing full logic-steering hardware.

This is a passive matrix (fixed coefficients). It is honest about what that is:
it derives L/C/R and a single mono surround. It does not, and cannot, decode
Dolby Digital / TrueHD / Atmos bitstreams — see docs/03-atmos-reality.md.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import dsp

# Center/surround summing weight. 0.5 keeps a mono (identical L/R) input from
# clipping the center; the classic -3 dB matrix weight is 1/sqrt(2).
SQRT1_2 = 0.7071067811865476


@dataclass
class DecodeConfig:
    surround_low_hz: float = 100.0     # surround band-limit, low edge
    surround_high_hz: float = 7000.0   # surround band-limit, high edge (classic 7 kHz)
    surround_delay_ms: float = 20.0    # Haas delay on the surround channel
    center_weight: float = SQRT1_2     # C = w * (Lt + Rt)
    surround_weight: float = SQRT1_2   # S = w * (Lt - Rt)
    surround_trim_db: float = -3.0     # surround level trim
    steering: float = 0.0              # 0 = pure passive; up to ~1 = more separation


def _db_to_gain(db: float) -> float:
    return 10.0 ** (db / 20.0)


class MatrixDecoder:
    """Decode a stereo Lt/Rt pair into L, C, R, S channels."""

    def __init__(self, sample_rate: int, config: DecodeConfig | None = None) -> None:
        self.fs = sample_rate
        self.cfg = config or DecodeConfig()

    def decode(self, lt: list[float], rt: list[float]) -> dict[str, list[float]]:
        """Return a dict with keys ``L``, ``C``, ``R``, ``S``.

        ``lt`` and ``rt`` are the two input channels (equal length).
        """
        if len(lt) != len(rt):
            raise ValueError("Lt and Rt must be the same length")

        cw = self.cfg.center_weight
        sw = self.cfg.surround_weight

        left = list(lt)
        right = list(rt)
        center = [cw * (a + b) for a, b in zip(lt, rt)]
        surround = [sw * (a - b) for a, b in zip(lt, rt)]

        # Optional passive steering: subtract a fraction of the derived center
        # out of L/R and vice-versa, tightening the phantom images the way an
        # active Pro-Logic decoder does. 0 leaves the pure passive matrix.
        s = self.cfg.steering
        if s > 0.0:
            left = [l - s * 0.5 * c for l, c in zip(left, center)]
            right = [r - s * 0.5 * c for r, c in zip(right, center)]

        # Surround processing chain: band-limit -> delay -> trim.
        surround = dsp.band_pass(
            surround, self.fs, self.cfg.surround_low_hz, self.cfg.surround_high_hz
        )
        delay = dsp.Delay(dsp.ms_to_samples(self.cfg.surround_delay_ms, self.fs))
        surround = delay.process(surround)
        trim = _db_to_gain(self.cfg.surround_trim_db)
        surround = [x * trim for x in surround]

        return {"L": left, "C": center, "R": right, "S": surround}

    def decode_to_51(self, lt: list[float], rt: list[float]) -> list[list[float]]:
        """Decode and lay the channels out as a 6-channel 5.1 bus.

        Order follows the common WAV/FFmpeg 5.1 layout:
        ``[FL, FR, FC, LFE, SL, SR]``. The mono surround feeds both surrounds;
        LFE is a low-passed sum of the fronts (simple bass management).
        """
        ch = self.decode(lt, rt)
        n = len(ch["L"])
        # LFE: low-pass the front sum below ~120 Hz.
        front_sum = [0.5 * (a + b) for a, b in zip(ch["L"], ch["R"])]
        lfe = dsp.Biquad.low_pass(self.fs, 120.0).process(front_sum)
        surround = ch["S"]
        return [
            ch["L"],          # FL
            ch["R"],          # FR
            ch["C"],          # FC
            lfe,              # LFE
            list(surround),   # SL
            list(surround),   # SR (mono surround duplicated)
        ]


def decode_stereo(lt: list[float], rt: list[float], sample_rate: int,
                  config: DecodeConfig | None = None) -> dict[str, list[float]]:
    """Convenience one-shot: build a decoder and decode a stereo pair."""
    return MatrixDecoder(sample_rate, config).decode(lt, rt)
