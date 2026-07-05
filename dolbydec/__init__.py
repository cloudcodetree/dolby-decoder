"""dolbydec — a DIY matrix surround decoder in pure-stdlib Python.

The software companion to the hardware build guide in ``docs/``. Decodes a
stereo Lt/Rt signal into L / C / R / S (or a 5.1 bus) using the same
sum-and-difference matrix the analog circuit implements.

Quick start::

    from dolbydec import decode_stereo, read_wav, write_wav

    (lt, rt), fs = read_wav("input.wav")[0][:2], read_wav("input.wav")[1]
    channels = decode_stereo(lt, rt, fs)

Or from the command line::

    python3 -m dolbydec decode input.wav -o out_5_1.wav
"""

from .decode import DecodeConfig, MatrixDecoder, decode_stereo
from .encode import encode
from .wavio import read_wav, write_wav

__all__ = [
    "DecodeConfig",
    "MatrixDecoder",
    "decode_stereo",
    "encode",
    "read_wav",
    "write_wav",
]

__version__ = "0.1.0"
