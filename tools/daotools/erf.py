"""Reader for BioWare ERF archives as shipped with Dragon Age: Origins.

Supported versions:
  V2.0  unencrypted, uncompressed data (DAO PC)
  V2.2  per-archive flags for encryption/compression (DAO PC, mostly DLC)
  V3.0  hashed names with a string table (Dragon Age II, read for completeness)

The magic and version are stored as UTF-16LE for V2.x/V3.0 ("ERF V2.0").
Encrypted archives (Blowfish) are listed but not extracted.
"""

from __future__ import annotations

import mmap
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path

NULL = 0xFFFFFFFF

ENCRYPTION_NAMES = {0: "none", 1: "xor", 2: "blowfish-dao", 3: "blowfish-da2"}
COMPRESSION_NONE = 0
COMPRESSION_BIOWARE_ZLIB = 1  # one header byte (window size), then raw deflate
COMPRESSION_HEADERLESS_ZLIB = 7  # raw deflate
COMPRESSION_NAMES = {0: "none", 1: "bioware-zlib", 2: "lzma", 3: "xbox-lzx", 7: "headerless-zlib"}


class ERFError(Exception):
    pass


@dataclass
class ERFEntry:
    name: str
    offset: int
    packed_size: int
    size: int
    name_hash: int | None = None

    @property
    def extension(self) -> str:
        return self.name.rsplit(".", 1)[1].lower() if "." in self.name else ""


class ERF:
    def __init__(self, data: bytes, path: str | None = None):
        self.data = data
        self.path = path
        self.entries: list[ERFEntry] = []
        self.encryption = 0
        self.compression = COMPRESSION_NONE
        self.build_year = 0
        self.build_day = 0
        self.module_id = 0
        self._parse()

    @classmethod
    def open(cls, path: str | Path) -> "ERF":
        """Memory-map the archive: DAO's texture and audio ERFs run to gigabytes."""
        f = open(path, "rb")
        try:
            data = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        except ValueError:  # empty file
            f.close()
            raise ERFError("empty file")
        try:
            erf = cls(data, str(path))
        except Exception:
            data.close()
            f.close()
            raise
        erf._file = f
        return erf

    def close(self) -> None:
        if isinstance(self.data, mmap.mmap):
            self.data.close()
        f = getattr(self, "_file", None)
        if f:
            f.close()

    def __enter__(self) -> "ERF":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def _u32(self, off: int) -> int:
        return struct.unpack_from("<I", self.data, off)[0]

    def _parse(self) -> None:
        if len(self.data) < 16:
            raise ERFError("file too small to be an ERF")
        try:
            header = self.data[:16].decode("utf-16-le")
        except UnicodeDecodeError as e:
            raise ERFError("not a UTF-16 ERF (V1.x archives are not used by DAO)") from e
        if not header.startswith("ERF "):
            raise ERFError(f"not an ERF file (magic {header[:4]!r})")
        self.version = header[4:8]

        if self.version == "V2.0":
            count, year, day = struct.unpack_from("<III", self.data, 16)
            self._set_build(year, day)
            self._read_v2_entries(count, 0x20, with_packed=False)
        elif self.version == "V2.2":
            count, year, day, _unk, flags, module_id = struct.unpack_from("<IIIIII", self.data, 16)
            self._set_build(year, day)
            self.module_id = module_id
            self.encryption = (flags >> 4) & 0xF
            self.compression = (flags >> 29) & 0x7
            self._read_v2_entries(count, 0x38, with_packed=True)
        elif self.version == "V3.0":
            self._parse_v30()
        else:
            raise ERFError(f"unsupported ERF version {self.version}")

    def _set_build(self, year: int, day: int) -> None:
        self.build_year = year + 1900
        self.build_day = day

    def _read_v2_entries(self, count: int, start: int, with_packed: bool) -> None:
        entry_size = 76 if with_packed else 72
        if start + count * entry_size > len(self.data):
            raise ERFError("resource table runs past end of file")
        for i in range(count):
            off = start + i * entry_size
            name = self.data[off:off + 64].decode("utf-16-le").split("\0", 1)[0]
            if with_packed:
                offset, packed, size = struct.unpack_from("<III", self.data, off + 64)
            else:
                offset, size = struct.unpack_from("<II", self.data, off + 64)
                packed = size
            self.entries.append(ERFEntry(name, offset, packed, size))

    def _parse_v30(self) -> None:
        string_size, count, flags, module_id = struct.unpack_from("<IIII", self.data, 16)
        self.module_id = module_id
        self.encryption = (flags >> 4) & 0xF
        self.compression = (flags >> 29) & 0x7
        strings = self.data[0x30:0x30 + string_size]
        start = 0x30 + string_size
        for i in range(count):
            off = start + i * 28
            name_off, name_hash, _type_hash, offset, packed, size = struct.unpack_from("<iQIIII", self.data, off)
            name = ""
            if name_off >= 0:
                name = strings[name_off:].split(b"\0", 1)[0].decode("utf-8", "replace")
            self.entries.append(ERFEntry(name or f"{name_hash:016x}", offset, packed, size, name_hash))

    @property
    def encrypted(self) -> bool:
        return self.encryption != 0

    def find(self, name: str) -> ERFEntry | None:
        name = name.lower()
        for e in self.entries:
            if e.name.lower() == name:
                return e
        return None

    def read(self, entry: ERFEntry | str) -> bytes:
        if isinstance(entry, str):
            found = self.find(entry)
            if found is None:
                raise ERFError(f"no resource named {entry!r}")
            entry = found
        if self.encrypted:
            raise ERFError(
                f"{entry.name}: archive is encrypted ({ENCRYPTION_NAMES.get(self.encryption, self.encryption)}); not supported"
            )
        raw = self.data[entry.offset:entry.offset + entry.packed_size]
        if len(raw) != entry.packed_size:
            raise ERFError(f"{entry.name}: data runs past end of file")
        return _decompress(raw, self.compression, entry.size, entry.name)


def is_erf(path: str | Path) -> bool:
    """Cheap check by magic, since DAO uses several extensions (.erf, .rim...)."""
    try:
        with open(path, "rb") as f:
            head = f.read(16)
    except OSError:
        return False
    return head[:10] == "ERF V".encode("utf-16-le")


def _decompress(raw: bytes, method: int, size: int, name: str) -> bytes:
    if method == COMPRESSION_NONE:
        return raw[:size]
    if method == COMPRESSION_BIOWARE_ZLIB:
        out = zlib.decompressobj(-15).decompress(raw[1:])
    elif method == COMPRESSION_HEADERLESS_ZLIB:
        out = zlib.decompressobj(-15).decompress(raw)
    else:
        raise ERFError(f"{name}: unsupported compression {COMPRESSION_NAMES.get(method, method)}")
    if len(out) != size:
        raise ERFError(f"{name}: decompressed to {len(out)} bytes, expected {size}")
    return out
