"""Reader for BioWare GFF V4.0/V4.1, the generic container behind most DAO data.

Conversations (.cnv), talk tables (.tlk), data tables (.gda), plots (.plo)
and many others are GFF4 files. Unlike the older GFF3, field labels are
numeric IDs (see fields.py), and a struct's layout is described once by a
"struct template" that every struct of that kind shares.

Layout (little-endian on PC):
  0x00  "GFF "  "V4.0"  platform("PC  ")  type("CNV ")  type version
  0x14  struct template count
        [V4.1 only: shared string count, shared string offset]
        data offset (all pointers in the data section are relative to it)
  then  struct templates, 16 bytes each: label, field count, field offset, struct size
        field declarations, 12 bytes each: label, type | flags << 16, offset in struct

Field flags: 0x8000 list, 0x4000 struct (type is then a template index),
0x2000 reference (the slot holds a pointer rather than the value).
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path

NULL = 0xFFFFFFFF

T_UINT8, T_SINT8, T_UINT16, T_SINT16, T_UINT32, T_SINT32, T_UINT64, T_SINT64 = range(8)
T_FLOAT32, T_FLOAT64, T_VECTOR3F = 8, 9, 10
T_VECTOR4F, T_QUATERNIONF, T_STRING, T_COLOR4F, T_MATRIX4X4F, T_TLKSTRING = 12, 13, 14, 15, 16, 17
T_NDSFIXED, T_ASCIISTRING = 18, 20
T_STRUCT, T_GENERIC = 65534, 65535

FLAG_LIST, FLAG_STRUCT, FLAG_REFERENCE = 0x8000, 0x4000, 0x2000

_SCALAR = {T_UINT8: "B", T_SINT8: "b", T_UINT16: "H", T_SINT16: "h", T_UINT32: "I", T_SINT32: "i",
           T_UINT64: "Q", T_SINT64: "q", T_FLOAT32: "f", T_FLOAT64: "d", T_NDSFIXED: "i"}
_FLOATS = {T_VECTOR3F: 3, T_VECTOR4F: 4, T_QUATERNIONF: 4, T_COLOR4F: 4, T_MATRIX4X4F: 16}
FIELD_SIZES = {T_STRING: 4, T_ASCIISTRING: 4, T_TLKSTRING: 8}
FIELD_SIZES.update({t: struct.calcsize(f) for t, f in _SCALAR.items()})
FIELD_SIZES.update({t: 4 * n for t, n in _FLOATS.items()})


class GFF4Error(Exception):
    pass


@dataclass
class TlkString:
    """A reference into the talk table, optionally with an inline override."""
    strref: int
    text: str = ""


@dataclass
class FieldDecl:
    label: int
    type: int
    flags: int
    offset: int


@dataclass
class Template:
    label: str
    size: int
    fields: list[FieldDecl]


@dataclass(eq=False)
class Struct:
    label: str
    fields: dict = field(default_factory=dict)
    # label -> (type, flags, absolute offset); needed for raw list access
    meta: dict = field(default_factory=dict)

    def get(self, label: int, default=None):
        value = self.fields.get(label, default)
        return default if value is None else value

    def __contains__(self, label: int) -> bool:
        return label in self.fields


class GFF4:
    def __init__(self, data: bytes, path: str | None = None):
        self.data = data
        self.path = path
        self._cache: dict[tuple[int, int], Struct] = {}
        self._parse_header()
        self.root = self._read_struct(self.data_offset, 0)

    @classmethod
    def open(cls, path: str | Path) -> "GFF4":
        return cls(Path(path).read_bytes(), str(path))

    # --- header -------------------------------------------------------------

    def _parse_header(self) -> None:
        d = self.data
        if len(d) < 28 or d[:4] != b"GFF ":
            raise GFF4Error("not a GFF4 file")
        self.version = d[4:8].decode("ascii")
        if self.version not in ("V4.0", "V4.1"):
            raise GFF4Error(f"unsupported GFF version {self.version}")
        self.platform = d[8:12].decode("ascii", "replace")
        self.big_endian = self.platform in ("PS3 ", "X360")
        self._e = ">" if self.big_endian else "<"
        self._text_encoding = "utf-16-be" if self.big_endian else "utf-16-le"
        self.file_type = d[12:16].decode("ascii", "replace")
        self.type_version = d[16:20].decode("ascii", "replace")
        pos = 20
        struct_count = self._u32(pos)
        pos += 4
        self.shared_strings: list[str] | None = None
        if self.version == "V4.1":
            string_count, string_offset = self._u32(pos), self._u32(pos + 4)
            pos += 8
            if string_count > 0 or string_offset != NULL:
                self.shared_strings = self._read_shared_strings(string_count, string_offset)
        self.data_offset = self._u32(pos)
        pos += 4
        if struct_count == 0:
            raise GFF4Error("GFF4 has no struct templates")

        self.templates: list[Template] = []
        for i in range(struct_count):
            t = pos + i * 16
            label = d[t:t + 4].decode("ascii", "replace")
            field_count, field_offset, size = struct.unpack_from(self._e + "III", d, t + 4)
            fields = []
            if field_offset != NULL:
                for j in range(field_count):
                    lbl, type_flags, off = struct.unpack_from(self._e + "III", d, field_offset + j * 12)
                    fields.append(FieldDecl(lbl, type_flags & 0xFFFF, type_flags >> 16, off))
            elif field_count:
                raise GFF4Error(f"template {i}: no field offset but {field_count} fields")
            self.templates.append(Template(label, size, fields))

    def _read_shared_strings(self, count: int, offset: int) -> list[str]:
        out, p = [], offset
        for _ in range(count):
            end = self.data.index(b"\0", p)
            out.append(self.data[p:end].decode("utf-8", "replace"))
            p = end + 1
        return out

    # --- primitives ---------------------------------------------------------

    def _u32(self, off: int) -> int:
        return struct.unpack_from(self._e + "I", self.data, off)[0]

    def _deref(self, is_ref: bool, off: int) -> int:
        if not is_ref or off == NULL:
            return off
        p = self._u32(off)
        return NULL if p == NULL else self.data_offset + p

    def _list_start(self, off: int) -> tuple[int, int]:
        """The slot at off points at a list: return (count, first element offset)."""
        lo = self._u32(off)
        if lo == NULL:
            return 0, NULL
        p = self.data_offset + lo
        return self._u32(p), p + 4

    def _string_at(self, p: int) -> str:
        n = self._u32(p)
        raw = self.data[p + 4:p + 4 + 2 * n]
        return raw.decode(self._text_encoding, "replace").split("\0", 1)[0]

    # --- structs and fields -------------------------------------------------

    def _read_struct(self, offset: int, tidx: int) -> Struct:
        key = (offset, tidx)
        if key in self._cache:
            return self._cache[key]
        tmpl = self.templates[tidx]
        s = Struct(tmpl.label)
        self._cache[key] = s
        for f in tmpl.fields:
            off = NULL if offset == NULL or f.offset == NULL else offset + f.offset
            s.meta[f.label] = (f.type, f.flags, off)
            s.fields[f.label] = self._read_field(f.type, f.flags, off, generic=False)
        return s

    def _read_field(self, ftype: int, flags: int, off: int, generic: bool):
        is_list = bool(flags & FLAG_LIST)
        is_ref = bool(flags & FLAG_REFERENCE)
        if flags & FLAG_STRUCT:
            return self._read_struct_field(ftype, is_list, is_ref, off)
        if ftype == T_GENERIC:
            return self._read_generic(is_list, is_ref, off)
        if ftype == T_STRING:
            is_ref = False  # strings are always stored behind a pointer already
        if off == NULL:
            return [] if is_list else None
        data_off = self._deref(is_ref, off)
        if data_off == NULL:
            return [] if is_list else None
        if is_list:
            count, p = self._list_start(data_off)
            out = []
            for _ in range(count):
                value, p = self._read_value(ftype, p, generic)
                out.append(value)
            return out
        return self._read_value(ftype, data_off, generic)[0]

    def _read_value(self, ftype: int, p: int, generic: bool):
        if ftype in _SCALAR:
            fmt = self._e + _SCALAR[ftype]
            return struct.unpack_from(fmt, self.data, p)[0], p + struct.calcsize(fmt)
        if ftype in _FLOATS:
            n = _FLOATS[ftype]
            return list(struct.unpack_from(f"{self._e}{n}f", self.data, p)), p + 4 * n
        if ftype == T_STRING:
            if self.shared_strings is not None:
                idx = self._u32(p)
                return ("" if idx == NULL else self.shared_strings[idx]), p + 4
            if generic:
                return self._string_at(p), p + 4
            ptr = self._u32(p)
            return ("" if ptr == NULL else self._string_at(self.data_offset + ptr)), p + 4
        if ftype == T_TLKSTRING:
            strref, o = self._u32(p), self._u32(p + 4)
            text = ""
            if o != NULL:
                if self.shared_strings is not None:
                    text = self.shared_strings[o]
                elif o != 0:
                    text = self._string_at(self.data_offset + o)
            return TlkString(strref, text), p + 8
        if ftype == T_ASCIISTRING:
            n = self._u32(p)
            return self.data[p + 4:p + 4 + n].decode("ascii", "replace"), p + 4
        raise GFF4Error(f"unknown field type {ftype} at 0x{p:x}")

    def _read_struct_field(self, tidx: int, is_list: bool, is_ref: bool, off: int):
        if off == NULL:
            return [] if is_list else None
        if tidx >= len(self.templates):
            raise GFF4Error(f"struct template {tidx} out of range")
        tmpl = self.templates[tidx]
        if is_list:
            count, start = self._list_start(off)
        else:
            count, start = 1, off
        size = 4 if is_ref else tmpl.size
        items = []
        for i in range(count):
            so = self._deref(is_ref, start + i * size)
            items.append(None if so == NULL else self._read_struct(so, tidx))
        return items if is_list else items[0]

    def _read_generic(self, is_list: bool, is_ref: bool, off: int):
        if off == NULL:
            return [] if is_list else None
        go = self._deref(is_list, off)  # a generic list's slot holds a pointer
        if go == NULL:
            return [] if is_list else None
        if is_list:
            count, start = self._u32(go), go + 4
        else:
            count, start = 1, go
        values = []
        for i in range(count):
            ep = start + i * 8
            type_flags = self._u32(ep)
            vo = self._deref(is_ref, ep + 4)
            if vo == NULL:
                values.append(None)
                continue
            values.append(self._read_field(type_flags & 0xFFFF, type_flags >> 16, vo, generic=True))
        return values if is_list else values[0]

    # --- raw access ---------------------------------------------------------

    def list_bytes(self, s: Struct, label: int) -> bytes:
        """Raw bytes of a scalar list field (e.g. the Huffman tree of a V0.5 TLK)."""
        if label not in s.meta:
            return b""
        ftype, flags, off = s.meta[label]
        if off == NULL or ftype not in FIELD_SIZES:
            return b""
        data_off = self._deref(bool(flags & FLAG_REFERENCE), off)
        if data_off == NULL:
            return b""
        if flags & FLAG_LIST:
            count, start = self._list_start(data_off)
        else:
            count, start = 1, data_off
        if start == NULL:
            return b""
        return self.data[start:start + count * FIELD_SIZES[ftype]]


def to_jsonable(value, names: dict[int, str] | None = None, _stack: set | None = None, resolve=None):
    """Convert a parsed GFF4 tree into plain JSON-friendly Python objects.

    resolve, if given, maps a string ref to its talk-table text.
    """
    names = names or {}
    _stack = _stack if _stack is not None else set()
    if isinstance(value, Struct):
        if id(value) in _stack:
            return {"$cycle": value.label}
        _stack.add(id(value))
        out = {"_struct": value.label}
        for label, v in value.fields.items():
            out[names.get(label, str(label))] = to_jsonable(v, names, _stack, resolve)
        _stack.discard(id(value))
        return out
    if isinstance(value, TlkString):
        text = value.text or (resolve(value.strref) if resolve and value.strref != NULL else "")
        return {"strref": value.strref, "text": text}
    if isinstance(value, list):
        return [to_jsonable(v, names, _stack, resolve) for v in value]
    return value
