"""Reader for BioWare GFF V3.2/V3.3, the older generic format.

DAO still uses it for some toolset-era templates: creatures (.utc),
placeables (.utp), triggers (.utt), items (.uti) and area properties (.are).
Unlike GFF4, fields carry text labels ("Tag", "FirstName"...).

Layout: a 56-byte header (type, version, then offset/count pairs for structs,
fields, labels, field data, field indices and list indices), followed by
those six sections. Values of 4 bytes or less sit inline in the field entry;
larger ones live in the field data section.
"""

from __future__ import annotations

import struct
from pathlib import Path

from .gff4 import NULL, Struct, TlkString

BYTE, CHAR, WORD, SHORT, DWORD, INT, DWORD64, INT64 = range(8)
FLOAT, DOUBLE, EXOSTRING, RESREF, LOCSTRING, VOID, STRUCT, LIST = range(8, 16)
ORIENTATION, VECTOR, STRREF = 16, 17, 18

_INLINE = {BYTE: "B", CHAR: "b", WORD: "H", SHORT: "h", DWORD: "I", INT: "i", FLOAT: "f"}
# DAO's English text in GFF3 is Windows-1252 (xoreos uses the same).
TEXT_ENCODING = "cp1252"


class GFF3Error(Exception):
    pass


def is_gff3(data: bytes) -> bool:
    return len(data) >= 56 and data[4:8] in (b"V3.2", b"V3.3")


class GFF3:
    def __init__(self, data: bytes, path: str | None = None):
        if not is_gff3(data):
            raise GFF3Error("not a GFF3 file")
        self.data = data
        self.path = path
        self.file_type = data[0:4].decode("ascii", "replace")
        self.version = data[4:8].decode("ascii")
        (self.struct_off, self.struct_count, self.field_off, self.field_count,
         self.label_off, self.label_count, self.fdata_off, _fdata_size,
         self.findex_off, _findex_size, self.lindex_off, _lindex_size) = struct.unpack_from("<12I", data, 8)
        if self.struct_count == 0:
            raise GFF3Error("GFF3 has no structs")
        self.labels = [data[self.label_off + 16 * i:self.label_off + 16 * (i + 1)].split(b"\0", 1)[0]
                       .decode("ascii", "replace") for i in range(self.label_count)]
        self._depth = 0
        self.root = self._read_struct(0)

    @classmethod
    def open(cls, path: str | Path) -> "GFF3":
        return cls(Path(path).read_bytes(), str(path))

    def _u32(self, off: int) -> int:
        return struct.unpack_from("<I", self.data, off)[0]

    def _read_struct(self, index: int) -> Struct:
        if index >= self.struct_count:
            raise GFF3Error(f"struct {index} out of range")
        self._depth += 1
        if self._depth > 500:
            raise GFF3Error("structs nested too deeply (loop?)")
        stype, field_ref, count = struct.unpack_from("<3I", self.data, self.struct_off + 12 * index)
        s = Struct(str(stype))
        if count == 1:
            field_indices = [field_ref]
        else:
            field_indices = struct.unpack_from(f"<{count}I", self.data, self.findex_off + field_ref) if count else ()
        for fi in field_indices:
            label, value = self._read_field(fi)
            s.fields[label] = value
        self._depth -= 1
        return s

    def _read_field(self, index: int):
        if index >= self.field_count:
            raise GFF3Error(f"field {index} out of range")
        ftype, label_index, raw = struct.unpack_from("<3I", self.data, self.field_off + 12 * index)
        label = self.labels[label_index] if label_index < len(self.labels) else f"label_{label_index}"
        return label, self._value(ftype, raw)

    def _value(self, ftype: int, raw: int):
        if ftype in _INLINE:
            fmt = "<" + _INLINE[ftype]
            return struct.unpack_from(fmt, struct.pack("<I", raw))[0]
        if ftype == STRUCT:
            return self._read_struct(raw)
        if ftype == LIST:
            p = self.lindex_off + raw
            count = self._u32(p)
            return [self._read_struct(i) for i in struct.unpack_from(f"<{count}I", self.data, p + 4)]
        p = self.fdata_off + raw
        d = self.data
        if ftype in (DWORD64, INT64, DOUBLE):
            return struct.unpack_from({DWORD64: "<Q", INT64: "<q", DOUBLE: "<d"}[ftype], d, p)[0]
        if ftype == EXOSTRING:
            n = self._u32(p)
            return d[p + 4:p + 4 + n].decode(TEXT_ENCODING, "replace").rstrip("\0")
        if ftype == RESREF:
            n = d[p]
            return d[p + 1:p + 1 + n].decode(TEXT_ENCODING, "replace").rstrip("\0")
        if ftype == LOCSTRING:
            _size, strref, count = struct.unpack_from("<3I", d, p)
            q, by_lang = p + 12, {}
            for _ in range(count):
                lang_id, n = struct.unpack_from("<iI", d, q)
                by_lang[lang_id] = d[q + 8:q + 8 + n].decode(TEXT_ENCODING, "replace").rstrip("\0")
                q += 8 + n
            # ids are language * 2 + gender; prefer English, else whatever is there
            text = by_lang.get(0) or by_lang.get(1) or next(iter(by_lang.values()), "")
            return TlkString(strref, text)
        if ftype == VOID:
            n = self._u32(p)
            blob = d[p + 4:p + 4 + n]
            return blob.hex() if n <= 64 else {"void_bytes": n}
        if ftype == ORIENTATION:
            return list(struct.unpack_from("<4f", d, p))
        if ftype == VECTOR:
            return list(struct.unpack_from("<3f", d, p))
        if ftype == STRREF:
            return TlkString(self._u32(p + 4))
        raise GFF3Error(f"unknown GFF3 field type {ftype}")
