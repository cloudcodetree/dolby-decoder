"""Round-trip and separation tests for the matrix decoder.

Run with:  python3 -m pytest tests/   (or: python3 tests/test_decode.py)

No third-party deps beyond pytest; the tests themselves are plain asserts so the
file also runs standalone.
"""

from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dolbydec import DecodeConfig, MatrixDecoder, encode  # noqa: E402
from dolbydec.dsp import Biquad  # noqa: E402

FS = 48000


def _tone(freq: float, n: int, amp: float = 0.5) -> list[float]:
    return [amp * math.sin(2.0 * math.pi * freq * i / FS) for i in range(n)]


def _rms(sig: list[float]) -> float:
    if not sig:
        return 0.0
    return math.sqrt(sum(x * x for x in sig) / len(sig))


def _mag_at(sig: list[float], freq: float) -> float:
    """Magnitude of a single frequency component (DFT at one exact bin).

    Correlating against sin/cos at ``freq`` isolates one tone far more sharply
    than a gentle band-pass, which is what we need to verify channel separation.
    """
    n = len(sig)
    if n == 0:
        return 0.0
    w = 2.0 * math.pi * freq / FS
    re = sum(sig[i] * math.cos(w * i) for i in range(n))
    im = sum(sig[i] * math.sin(w * i) for i in range(n))
    return 2.0 * math.sqrt(re * re + im * im) / n


# Decode with no surround delay/band-limit so we test the *matrix* math cleanly.
_RAW = DecodeConfig(surround_delay_ms=0.0, surround_low_hz=1.0,
                    surround_high_hz=20000.0, surround_trim_db=0.0)


def test_center_content_goes_to_center_not_surround():
    """In-phase (mono) content must land in C and null in S."""
    n = FS // 2
    lt = _tone(440.0, n)
    rt = list(lt)  # identical -> pure center
    ch = MatrixDecoder(FS, _RAW).decode(lt, rt)
    assert _rms(ch["C"]) > 0.3
    # Surround should be far below center (deep matrix null).
    assert _rms(ch["S"]) < 0.01 * _rms(ch["C"])


def test_surround_content_goes_to_surround_not_center():
    """Anti-phase content must land in S and null in C."""
    n = FS // 2
    lt = _tone(440.0, n)
    rt = [-x for x in lt]  # opposite phase -> pure surround
    ch = MatrixDecoder(FS, _RAW).decode(lt, rt)
    assert _rms(ch["S"]) > 0.3
    assert _rms(ch["C"]) < 0.01 * _rms(ch["S"])


def test_encode_decode_round_trip_separation():
    """Encode 4 distinct tones, decode, and check each lands in its channel."""
    n = FS  # 1 second
    left = _tone(220.0, n)
    center = _tone(440.0, n)
    right = _tone(660.0, n)
    surround = _tone(330.0, n)

    lt, rt = encode(left, center, right, surround)
    ch = MatrixDecoder(FS, _RAW).decode(lt, rt)

    # Each output channel should carry real energy...
    for name in ("L", "C", "R", "S"):
        assert _rms(ch[name]) > 0.1, f"{name} too quiet"

    # ...and each source tone should dominate its intended channel. The passive
    # matrix's defining property: center content (440) cancels exactly in the
    # surround channel, and surround content (330) cancels exactly in center.
    assert _mag_at(ch["S"], 330.0) > 20.0 * _mag_at(ch["S"], 440.0)  # no C in S
    assert _mag_at(ch["C"], 440.0) > 20.0 * _mag_at(ch["C"], 330.0)  # no S in C
    # The dominant tone in L is its own 220 Hz source.
    assert _mag_at(ch["L"], 220.0) > _mag_at(ch["L"], 660.0)


def test_left_only_is_present_left_and_absent_right():
    n = FS // 2
    left = _tone(220.0, n)
    silence = [0.0] * n
    lt, rt = encode(left, silence, silence, silence)
    ch = MatrixDecoder(FS, _RAW).decode(lt, rt)
    assert _rms(ch["L"]) > 0.2
    assert _rms(ch["R"]) < 0.01 * _rms(ch["L"])


def test_surround_is_band_limited():
    """A 12 kHz surround tone must be strongly attenuated by the 7 kHz LPF."""
    n = FS // 2
    lt = _tone(12000.0, n)
    rt = [-x for x in lt]
    # Default config: band-limit active.
    ch = MatrixDecoder(FS).decode(lt, rt)
    # Compare to raw (no band-limit) surround energy.
    raw = MatrixDecoder(FS, _RAW).decode(lt, rt)
    assert _rms(ch["S"]) < 0.2 * _rms(raw["S"])


def test_surround_delay_shifts_signal():
    """A delay of D ms should push the first D ms of surround toward silence."""
    n = FS // 2
    lt = _tone(440.0, n)
    rt = [-x for x in lt]
    cfg = DecodeConfig(surround_delay_ms=20.0, surround_low_hz=1.0,
                       surround_high_hz=20000.0, surround_trim_db=0.0)
    ch = MatrixDecoder(FS, cfg).decode(lt, rt)
    d = int(round(0.020 * FS))
    assert _rms(ch["S"][:d]) < 1e-9          # leading silence == the delay
    assert _rms(ch["S"][d: d + 1000]) > 0.2  # signal resumes after the delay


def test_biquad_lowpass_passes_dc_blocks_high():
    n = 4096
    lp = Biquad.low_pass(FS, 1000.0)
    low = lp.process(_tone(100.0, n))
    lp2 = Biquad.low_pass(FS, 1000.0)
    high = lp2.process(_tone(10000.0, n))
    assert _rms(low) > 5.0 * _rms(high)


def _run_standalone() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as exc:
            failures += 1
            print(f"FAIL {t.__name__}: {exc}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_run_standalone())
