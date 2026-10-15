"""FMOD sound banks (.fsb, "FSB4"): the voice-over for conversations.

Each conversation has a bank of the same name (e.g. bhn100cr_father.fsb).
A sample is named "<strref>_m.wav" after the talk table string of the line it
voices, and holds MPEG layer III audio (24 kHz mono for conversation VO).
It is written out as a clean .mp3 (without FMOD's trailing padding); `mfdecode`
turns that into the PCM .wav Unreal plays. Checked on the 38 Human Noble banks.

Layout: a 48-byte header (magic, sample count, size of the sample headers,
size of the data, version, mode, 8 zero bytes, 16-byte hash), then one
header per sample (2-byte size, 30-byte name, then lengths, mode and format),
then the sample data back to back in the same order.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path

# FMOD sample mode bits that say how the data is encoded.
MODE_MPEG = 0x200
MODE_IMAADPCM = 0x400000
MODE_STEREO = 0x40


class FSBError(Exception):
    pass


@dataclass
class Sample:
    name: str
    length: int  # in samples
    mode: int
    frequency: int
    channels: int
    data: bytes

    @property
    def codec(self) -> str:
        if self.mode & MODE_MPEG:
            return "mpeg"
        if self.mode & MODE_IMAADPCM:
            return "imaadpcm"
        return "pcm"

    @property
    def seconds(self) -> float:
        return self.length / self.frequency if self.frequency else 0.0

    @property
    def stem(self) -> str:
        return self.name.rsplit(".", 1)[0] if "." in self.name else self.name


def is_fsb(data: bytes) -> bool:
    return data[:4] == b"FSB4"


class FSB:
    def __init__(self, data: bytes, path: str | None = None):
        if not is_fsb(data):
            raise FSBError(f"{path or 'file'} is not an FSB4 bank")
        if len(data) < 48:
            raise FSBError("truncated FSB4 header")
        self.path = path
        count, header_size, data_size, self.version, self.mode = struct.unpack_from("<iiiII", data, 4)
        pos, offset = 48, 48 + header_size
        if offset + data_size > len(data):
            raise FSBError("FSB4 data runs past the end of the file")
        self.samples: list[Sample] = []
        for _ in range(count):
            size, = struct.unpack_from("<H", data, pos)
            name = data[pos + 2:pos + 32].split(b"\0")[0].decode("ascii", "replace")
            length, packed, _loop_start, _loop_end, mode, freq = struct.unpack_from("<IIIIIi", data, pos + 32)
            channels, = struct.unpack_from("<H", data, pos + 62)
            if size < 64 or offset + packed > len(data):
                raise FSBError(f"sample {name!r}: bad header")
            self.samples.append(Sample(name, length, mode, freq, channels, data[offset:offset + packed]))
            pos += size
            offset += packed

    @classmethod
    def open(cls, path: str | Path) -> "FSB":
        return cls(Path(path).read_bytes(), str(path))

    def names(self) -> set[str]:
        return {s.name for s in self.samples}


# MPEG audio frame sizes: bitrate index -> kbps for MPEG-1 and MPEG-2/2.5 layer III.
_BITRATES = {3: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320],
             2: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160]}
_RATES = {3: [44100, 48000, 32000], 2: [22050, 24000, 16000], 0: [11025, 12000, 8000]}


def mpeg_end(data: bytes) -> int:
    """Where the last whole MPEG layer III frame ends. FMOD pads each sample
    with zero bytes after it; cutting there leaves a clean .mp3."""
    pos = 0
    while pos + 4 <= len(data):
        h = int.from_bytes(data[pos:pos + 4], "big")
        version, bitrate, rate = (h >> 19) & 3, (h >> 12) & 15, (h >> 10) & 3
        if (h >> 21) & 0x7FF != 0x7FF or version == 1 or (h >> 17) & 3 != 1 or bitrate in (0, 15) or rate == 3:
            break
        kbps = _BITRATES[3 if version == 3 else 2][bitrate]
        size = (144 if version == 3 else 72) * kbps * 1000 // _RATES[version][rate] + ((h >> 9) & 1)
        if pos + size > len(data):
            break
        pos += size
    return pos


def mp3(sample: Sample) -> bytes:
    """An MPEG sample as a clean .mp3 (FMOD's trailing padding cut)."""
    return sample.data[:mpeg_end(sample.data)] or sample.data


def vo_sample(strref: int | None) -> str:
    """Sample name for a conversation line, from its talk table string."""
    return f"{strref}_m.wav" if isinstance(strref, int) and strref >= 0 else ""
