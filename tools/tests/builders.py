"""Builders for synthetic DAO-format files, so the readers can be tested
without shipping (or needing) any real game data."""

from __future__ import annotations

import struct
import zlib

from daotools import fields as F
from daotools.gff4 import (FIELD_SIZES, FLAG_LIST, FLAG_REFERENCE, FLAG_STRUCT, NULL, T_SINT32,
                           T_STRING, T_TLKSTRING, T_UINT8, T_UINT32)


# --- ERF --------------------------------------------------------------------

def build_erf(files: dict[str, bytes], version: str = "V2.0", compression: int = 0, encryption: int = 0) -> bytes:
    names = list(files)
    if version == "V2.0":
        header = ("ERF " + version).encode("utf-16-le") + struct.pack("<IIII", len(names), 109, 300, NULL)
        entry_size = 72
    else:
        flags = (encryption << 4) | (compression << 29)
        header = ("ERF " + version).encode("utf-16-le") + struct.pack(
            "<IIIIII", len(names), 109, 300, NULL, flags, 7) + b"\0" * 16
        entry_size = 76
    data_start = len(header) + entry_size * len(names)
    table, blob = b"", b""
    for name in names:
        raw = files[name]
        packed = raw
        if compression == 1:
            c = zlib.compressobj(9, zlib.DEFLATED, -15)
            packed = b"\xf0" + c.compress(raw) + c.flush()
        elif compression == 7:
            c = zlib.compressobj(9, zlib.DEFLATED, -15)
            packed = c.compress(raw) + c.flush()
        entry = name.encode("utf-16-le").ljust(64, b"\0")
        if version == "V2.0":
            entry += struct.pack("<II", data_start + len(blob), len(raw))
        else:
            entry += struct.pack("<III", data_start + len(blob), len(packed), len(raw))
        table += entry
        blob += packed
    return header + table + blob


# --- GFF4 -------------------------------------------------------------------

class Tmpl:
    """A struct template. fields: list of (field_id, kind) where kind is one of
    a scalar type code, "string", "tlk", ("struct", Tmpl), ("list", type code),
    ("structlist", Tmpl) or ("reflist", Tmpl)."""

    def __init__(self, label: str, fields: list):
        self.label = label.ljust(4)[:4]
        self.fields = fields
        self.index = -1
        self.offsets = []
        self.size = 0

    def layout(self) -> None:
        off = 0
        self.offsets = []
        for _fid, kind in self.fields:
            self.offsets.append(off)
            off += _inline_size(kind)
        self.size = off


def _inline_size(kind) -> int:
    if isinstance(kind, int):
        return FIELD_SIZES[kind]
    if kind == "string":
        return 4
    if kind == "tlk":
        return 8
    if kind[0] == "struct":
        return kind[1].size
    return 4  # every list kind is a pointer


def _type_flags(kind) -> int:
    if isinstance(kind, int):
        return kind
    if kind == "string":
        return T_STRING
    if kind == "tlk":
        return T_TLKSTRING
    k, arg = kind
    if k == "struct":
        return arg.index | FLAG_STRUCT << 16
    if k == "list":
        return arg | FLAG_LIST << 16
    if k == "structlist":
        return arg.index | (FLAG_STRUCT | FLAG_LIST) << 16
    if k == "reflist":
        return arg.index | (FLAG_STRUCT | FLAG_LIST | FLAG_REFERENCE) << 16
    raise ValueError(kind)


_FMT = {0: "B", 1: "b", 2: "H", 3: "h", 4: "I", 5: "i", 6: "Q", 7: "q", 8: "f", 9: "d"}


class GFF4Writer:
    def __init__(self, file_type: str, type_version: str, templates: list[Tmpl]):
        self.file_type = file_type.ljust(4)[:4]
        self.type_version = type_version
        self.templates = templates  # root first; nested templates must come later
        for i, t in enumerate(templates):
            t.index = i
        for t in reversed(templates):
            t.layout()

    def build(self, values: dict) -> bytes:
        self.heap = bytearray()
        root = self.templates[0]
        self._write_struct(self._alloc(root.size), root, values)

        header_size = 28 + 16 * len(self.templates)
        decls = b""
        tmpl_bytes = b""
        for t in self.templates:
            field_off = header_size + len(decls) if t.fields else NULL
            tmpl_bytes += t.label.encode("ascii") + struct.pack("<III", len(t.fields), field_off, t.size)
            for (fid, kind), off in zip(t.fields, t.offsets):
                decls += struct.pack("<III", fid, _type_flags(kind), off)
        data_offset = header_size + len(decls)
        head = (b"GFF V4.0PC  " + self.file_type.encode("ascii") + self.type_version.encode("ascii")
                + struct.pack("<II", len(self.templates), data_offset))
        return head + tmpl_bytes + decls + bytes(self.heap)

    def _alloc(self, n: int) -> int:
        off = len(self.heap)
        self.heap.extend(b"\0" * n)
        return off

    def _string(self, s: str) -> int:
        raw = s.encode("utf-16-le")
        off = self._alloc(4 + len(raw))
        struct.pack_into("<I", self.heap, off, len(raw) // 2)
        self.heap[off + 4:off + 4 + len(raw)] = raw
        return off

    def _write_struct(self, off: int, tmpl: Tmpl, values: dict) -> None:
        for (fid, kind), foff in zip(tmpl.fields, tmpl.offsets):
            p = off + foff
            v = values.get(fid)
            if isinstance(kind, int):
                if v is not None and kind in _FMT:
                    struct.pack_into("<" + _FMT[kind], self.heap, p, v)
                elif v is not None:  # float vectors, quaternions, colours, matrices
                    struct.pack_into(f"<{len(v)}f", self.heap, p, *v)
            elif kind == "string":
                struct.pack_into("<I", self.heap, p, NULL if v is None else self._string(v))
            elif kind == "tlk":
                strref, text = v if isinstance(v, tuple) else (NULL if v is None else v, None)
                struct.pack_into("<II", self.heap, p, strref, NULL if text is None else self._string(text))
            elif kind[0] == "struct":
                self._write_struct(p, kind[1], v or {})
            elif v is None:
                struct.pack_into("<I", self.heap, p, NULL)
            elif kind[0] == "list":
                size = FIELD_SIZES[kind[1]]
                lo = self._alloc(4 + size * len(v))
                struct.pack_into("<I", self.heap, lo, len(v))
                for i, item in enumerate(v):
                    struct.pack_into("<" + _FMT[kind[1]], self.heap, lo + 4 + i * size, item)
                struct.pack_into("<I", self.heap, p, lo)
            elif kind[0] == "structlist":
                sub = kind[1]
                lo = self._alloc(4 + sub.size * len(v))
                struct.pack_into("<I", self.heap, lo, len(v))
                for i, item in enumerate(v):
                    self._write_struct(lo + 4 + i * sub.size, sub, item)
                struct.pack_into("<I", self.heap, p, lo)
            elif kind[0] == "reflist":
                sub = kind[1]
                lo = self._alloc(4 + 4 * len(v))
                struct.pack_into("<I", self.heap, lo, len(v))
                for i, item in enumerate(v):
                    if item is None:
                        struct.pack_into("<I", self.heap, lo + 4 + 4 * i, NULL)
                        continue
                    so = self._alloc(sub.size)
                    self._write_struct(so, sub, item)
                    struct.pack_into("<I", self.heap, lo + 4 + 4 * i, so)
                struct.pack_into("<I", self.heap, p, lo)


# --- talk tables --------------------------------------------------------------

def build_tlk_v02(strings: dict[int, str]) -> bytes:
    entry = Tmpl("STRN", [(F.TALK_STRING_ID, T_UINT32), (F.TALK_STRING, "string")])
    root = Tmpl("TLK ", [(F.TALK_STRING_LIST, ("structlist", entry))])
    w = GFF4Writer("TLK ", "V0.2", [root, entry])
    return w.build({F.TALK_STRING_LIST: [
        {F.TALK_STRING_ID: k, F.TALK_STRING: v} for k, v in strings.items()]})


def build_tlk_v05(strings: dict[int, str]) -> bytes:
    units = {0}
    for s in strings.values():
        units.update(struct.unpack(f"<{len(s.encode('utf-16-le')) // 2}H", s.encode("utf-16-le")))
    nodes: list[int] = []  # flat pairs; root ends up last
    codes: dict[int, list[int]] = {}

    def build(syms, prefix):
        if len(syms) == 1:
            codes[syms[0]] = prefix
            return ~syms[0]
        mid = len(syms) // 2
        left = build(syms[:mid], prefix + [0])
        right = build(syms[mid:], prefix + [1])
        nodes.extend([left, right])
        return len(nodes) // 2 - 1

    build(sorted(units), [])
    bits, offsets = [], {}
    for strref, s in strings.items():
        offsets[strref] = len(bits)
        raw = s.encode("utf-16-le")
        for u in list(struct.unpack(f"<{len(raw) // 2}H", raw)) + [0]:
            bits.extend(codes[u])
    words = [0] * ((len(bits) + 31) // 32)
    for i, b in enumerate(bits):
        words[i >> 5] |= b << (i & 31)

    entry = Tmpl("HSTR", [(F.HUFF_TALK_STRING_ID, T_UINT32), (F.HUFF_TALK_STRING_BIT_OFFSET, T_UINT32)])
    root = Tmpl("TLK ", [(F.HUFF_TALK_STRING_LIST, ("structlist", entry)),
                         (F.HUFF_TALK_STRING_HUFF_TREE, ("list", T_SINT32)),
                         (F.HUFF_TALK_STRING_BIT_STREAM, ("list", T_UINT32))])
    w = GFF4Writer("TLK ", "V0.5", [root, entry])
    return w.build({
        F.HUFF_TALK_STRING_LIST: [{F.HUFF_TALK_STRING_ID: k, F.HUFF_TALK_STRING_BIT_OFFSET: o}
                                  for k, o in offsets.items()],
        F.HUFF_TALK_STRING_HUFF_TREE: nodes,
        F.HUFF_TALK_STRING_BIT_STREAM: words,
    })


# --- conversations --------------------------------------------------------------

def build_cnv(lines: list[dict], starts: list[int], children_as_structs: bool = True,
              file_type: str = "DLG ") -> bytes:
    """lines: dicts with text (strref or (strref, text)), speaker, children, action_flag."""
    link = Tmpl("LINK", [(F.CONV_STARTING_INDEX, T_UINT32)])
    plot = Tmpl("PLOT", [(F.CONV_PLOT_FLAG, T_SINT32), (F.CONV_SCRIPT, "string")])
    child_kind = ("structlist", link) if children_as_structs else ("list", T_UINT32)
    line = Tmpl("LINE", [(F.CONV_LINE_TEXT, "tlk"), (F.CONV_LINE_SPEAKER, "string"),
                         (F.CONV_LINE_LISTENER, "string"), (F.CONV_LINE_ACTION, ("struct", plot)),
                         (F.CONV_LINE_SKIP, T_UINT8), (F.CONV_LINE_CHILDREN_LIST, child_kind)])
    root = Tmpl("CONV", [(F.CONV_STARTING_LIST, ("structlist", link) if children_as_structs else ("list", T_UINT32)),
                         (F.CONV_LINE_LIST, ("structlist", line)), (F.CONV_VO_BANK, "string")])
    # nested templates must be laid out before the ones that embed them
    w = GFF4Writer(file_type, "V0.2", [root, line, plot, link])

    def links(idx):
        return [{F.CONV_STARTING_INDEX: i} for i in idx] if children_as_structs else list(idx)

    return w.build({
        F.CONV_STARTING_LIST: links(starts),
        F.CONV_VO_BANK: "vo_bank_test",
        F.CONV_LINE_LIST: [{
            F.CONV_LINE_TEXT: l.get("text"),
            F.CONV_LINE_SPEAKER: l.get("speaker", ""),
            F.CONV_LINE_LISTENER: l.get("listener", ""),
            F.CONV_LINE_ACTION: {F.CONV_PLOT_FLAG: l.get("action_flag", -1), F.CONV_SCRIPT: l.get("script", "")},
            F.CONV_LINE_SKIP: 0,
            F.CONV_LINE_CHILDREN_LIST: links(l.get("children", [])),
        } for l in lines],
    })


# --- GFF3 ---------------------------------------------------------------------

def build_gff3(file_type: str, root: dict) -> bytes:
    """root: {label: (type, value)}; a STRUCT value is a dict, a LIST value a
    list of dicts, a LOCSTRING value (strref, {lang_id: text})."""
    structs, fields, labels = [], [], []
    fdata, findices, lindices = bytearray(), bytearray(), bytearray()
    inline = {0: "<B", 1: "<b", 2: "<H", 3: "<h", 4: "<I", 5: "<i", 8: "<f"}

    def label(name):
        if name not in labels:
            labels.append(name)
        return labels.index(name)

    def add_struct(d, stype=0):
        idx = len(structs)
        structs.append(None)
        fids = [add_field(k, t, v) for k, (t, v) in d.items()]
        if len(fids) == 1:
            structs[idx] = (stype, fids[0], 1)
        else:
            structs[idx] = (stype, len(findices), len(fids))
            findices.extend(struct.pack(f"<{len(fids)}I", *fids))
        return idx

    def add_field(name, t, v):
        if t in inline:
            raw = struct.unpack("<I", struct.pack(inline[t], v).ljust(4, b"\0"))[0]
        elif t == 14:
            raw = add_struct(v)
        elif t == 15:
            idxs = [add_struct(x, 7) for x in v]
            raw = len(lindices)
            lindices.extend(struct.pack(f"<{len(idxs) + 1}I", len(idxs), *idxs))
        else:
            raw = len(fdata)
            if t == 10:
                enc = v.encode("cp1252")
                fdata.extend(struct.pack("<I", len(enc)) + enc)
            elif t == 11:
                enc = v.encode("cp1252")
                fdata.extend(bytes([len(enc)]) + enc)
            elif t == 12:
                strref, texts = v
                body = b"".join(struct.pack("<iI", k, len(x.encode("cp1252"))) + x.encode("cp1252")
                                for k, x in texts.items())
                fdata.extend(struct.pack("<3I", 8 + len(body), strref, len(texts)) + body)
            elif t == 17:
                fdata.extend(struct.pack("<3f", *v))
            elif t == 18:
                fdata.extend(struct.pack("<II", 4, v))
            elif t == 6:
                fdata.extend(struct.pack("<Q", v))
            else:
                raise ValueError(t)
        fields.append((t, label(name), raw))
        return len(fields) - 1

    add_struct(root, 0xFFFFFFFF)
    sections = [
        b"".join(struct.pack("<3I", *x) for x in structs),
        b"".join(struct.pack("<3I", *x) for x in fields),
        b"".join(n.encode("ascii").ljust(16, b"\0") for n in labels),
        bytes(fdata), bytes(findices), bytes(lindices),
    ]
    counts = [len(structs), len(fields), len(labels), len(fdata), len(findices), len(lindices)]
    header_size = 56
    offsets, off = [], header_size
    for sec in sections:
        offsets.append(off)
        off += len(sec)
    header = file_type.ljust(4).encode("ascii") + b"V3.2"
    for o, c in zip(offsets, counts):
        header += struct.pack("<II", o, c)
    return header + b"".join(sections)
