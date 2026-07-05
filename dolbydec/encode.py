"""Matrix surround *encoder* — the inverse of decode.py.

Folds four channels (L, C, R, S) down to a two-channel Lt/Rt pair, the way a
Dolby Surround encoder does:

    Lt = L + k*C + k*S
    Rt = R + k*C - k*S      # surround sent anti-phase between Lt and Rt

This is a simplified encoder: a real Dolby encoder applies a +/-90 degree phase
shift (not a plain sign flip) plus band-limiting and noise reduction to the
surround. The plain anti-phase version here is exactly invertible by the passive
matrix decoder, which makes it ideal for round-trip tests and demo material.
"""

from __future__ import annotations

from .decode import SQRT1_2


def encode(l: list[float], c: list[float], r: list[float], s: list[float],
           center_weight: float = SQRT1_2,
           surround_weight: float = SQRT1_2) -> tuple[list[float], list[float]]:
    """Encode L, C, R, S into an (Lt, Rt) stereo pair."""
    n = max(len(l), len(c), len(r), len(s))

    def pad(x: list[float]) -> list[float]:
        return x + [0.0] * (n - len(x))

    l, c, r, s = pad(l), pad(c), pad(r), pad(s)
    cw, sw = center_weight, surround_weight
    lt = [l[i] + cw * c[i] + sw * s[i] for i in range(n)]
    rt = [r[i] + cw * c[i] - sw * s[i] for i in range(n)]
    return lt, rt
