"""Command-line interface for the matrix surround decoder.

    python3 -m dolbydec decode  input.wav -o out_5_1.wav          # 5.1 output
    python3 -m dolbydec decode  input.wav -o out_quad.wav --layout 4.0
    python3 -m dolbydec decode  input.wav --split out/            # one WAV per channel
    python3 -m dolbydec encode  L.wav C.wav R.wav S.wav -o Lt_Rt.wav
    python3 -m dolbydec demo    -o demo_encoded.wav               # synthesize test material
"""

from __future__ import annotations

import argparse
import os
import sys

from .encode import encode as encode_ltrt
from .decode import DecodeConfig, MatrixDecoder
from .wavio import read_wav, write_wav


def _cmd_decode(args: argparse.Namespace) -> int:
    channels, fs = read_wav(args.input)
    if len(channels) < 2:
        print("error: input must be a 2-channel (stereo Lt/Rt) WAV", file=sys.stderr)
        return 2
    lt, rt = channels[0], channels[1]

    cfg = DecodeConfig(
        surround_delay_ms=args.delay,
        surround_low_hz=args.surround_low,
        surround_high_hz=args.surround_high,
        steering=args.steering,
    )
    dec = MatrixDecoder(fs, cfg)

    if args.split:
        os.makedirs(args.split, exist_ok=True)
        ch = dec.decode(lt, rt)
        for name, sig in ch.items():
            path = os.path.join(args.split, f"{name}.wav")
            write_wav(path, [sig], fs)
            print(f"wrote {path}")
        return 0

    if args.layout == "5.1":
        bus = dec.decode_to_51(lt, rt)
    else:  # 4.0 -> FL, FR, FC, S(mono)
        ch = dec.decode(lt, rt)
        bus = [ch["L"], ch["R"], ch["C"], ch["S"]]

    out = args.output or _default_out(args.input, args.layout)
    write_wav(out, bus, fs)
    print(f"wrote {out}  ({len(bus)} channels, {fs} Hz, {args.layout})")
    return 0


def _cmd_encode(args: argparse.Namespace) -> int:
    def mono(path: str) -> tuple[list[float], int]:
        ch, fs = read_wav(path)
        return ch[0], fs

    l, fs = mono(args.left)
    c, _ = mono(args.center)
    r, _ = mono(args.right)
    s, _ = mono(args.surround)
    lt, rt = encode_ltrt(l, c, r, s)
    out = args.output or "Lt_Rt.wav"
    write_wav(out, [lt, rt], fs)
    print(f"wrote {out}  (stereo Lt/Rt, {fs} Hz)")
    return 0


def _cmd_demo(args: argparse.Namespace) -> int:
    """Synthesize a matrix-encoded test signal with distinct content per channel."""
    import math

    fs = args.rate
    dur = args.seconds
    n = int(fs * dur)

    def tone(freq: float, amp: float = 0.5) -> list[float]:
        return [amp * math.sin(2.0 * math.pi * freq * i / fs) for i in range(n)]

    # Four clearly-separable sources so you can hear the decode work.
    left = tone(220.0)      # A3  -> front left
    center = tone(440.0)    # A4  -> center (dialog stand-in)
    right = tone(660.0)     # E5  -> front right
    surround = tone(330.0)  # E4  -> surround (within the 100 Hz-7 kHz band)

    lt, rt = encode_ltrt(left, center, right, surround)
    out = args.output or "demo_encoded.wav"
    write_wav(out, [lt, rt], fs)
    print(f"wrote {out}  (stereo Lt/Rt demo, {fs} Hz, {dur}s)")
    print("decode it with:  python3 -m dolbydec decode "
          f"{out} --split demo_out/")
    return 0


def _default_out(input_path: str, layout: str) -> str:
    base = os.path.splitext(os.path.basename(input_path))[0]
    suffix = "5_1" if layout == "5.1" else "quad"
    return f"{base}_{suffix}.wav"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dolbydec",
        description="DIY matrix surround decoder (Dolby-Surround / Pro-Logic style).",
    )
    sub = p.add_subparsers(dest="command", required=True)

    d = sub.add_parser("decode", help="decode a stereo Lt/Rt WAV to surround")
    d.add_argument("input", help="stereo (Lt/Rt) WAV file")
    d.add_argument("-o", "--output", help="output WAV path")
    d.add_argument("--layout", choices=["5.1", "4.0"], default="5.1",
                   help="output channel layout (default: 5.1)")
    d.add_argument("--split", metavar="DIR",
                   help="instead of one file, write L/C/R/S as separate WAVs here")
    d.add_argument("--delay", type=float, default=20.0,
                   help="surround delay in ms (default: 20)")
    d.add_argument("--surround-low", type=float, default=100.0,
                   help="surround band-limit low edge in Hz (default: 100)")
    d.add_argument("--surround-high", type=float, default=7000.0,
                   help="surround band-limit high edge in Hz (default: 7000)")
    d.add_argument("--steering", type=float, default=0.0,
                   help="passive steering amount 0..1 (default: 0 = pure passive)")
    d.set_defaults(func=_cmd_decode)

    e = sub.add_parser("encode", help="encode L/C/R/S WAVs into a stereo Lt/Rt WAV")
    e.add_argument("left")
    e.add_argument("center")
    e.add_argument("right")
    e.add_argument("surround")
    e.add_argument("-o", "--output", help="output WAV path (default: Lt_Rt.wav)")
    e.set_defaults(func=_cmd_encode)

    m = sub.add_parser("demo", help="synthesize a matrix-encoded test signal")
    m.add_argument("-o", "--output", help="output WAV path (default: demo_encoded.wav)")
    m.add_argument("--rate", type=int, default=48000, help="sample rate (default: 48000)")
    m.add_argument("--seconds", type=float, default=3.0, help="duration (default: 3.0)")
    m.set_defaults(func=_cmd_demo)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
