"""Talk tables: every line of text in DAO lives here, keyed by a string ref.

DAO's .tlk files are GFF4 (type "TLK "). Version V0.2 stores plain strings;
V0.4/V0.5 store all text as one Huffman-coded bit stream.
"""

from __future__ import annotations

import struct
from pathlib import Path

from . import fields as F
from .gff4 import GFF4, NULL


class TLKError(Exception):
    pass


class TalkTable:
    def __init__(self, gff: GFF4):
        if gff.file_type != "TLK ":
            raise TLKError(f"not a talk table (GFF type {gff.file_type!r})")
        self.version = gff.type_version
        self.strings: dict[int, str] = {}
        if self.version == "V0.2":
            self._load_plain(gff)
        elif self.version in ("V0.4", "V0.5"):
            self._load_huffman(gff)
        else:
            raise TLKError(f"unsupported talk table version {self.version}")

    @classmethod
    def open(cls, path: str | Path) -> "TalkTable":
        return cls(GFF4.open(path))

    def __len__(self) -> int:
        return len(self.strings)

    def get(self, strref: int, default: str = "") -> str:
        return self.strings.get(strref, default)

    def _load_plain(self, gff: GFF4) -> None:
        for s in gff.root.get(F.TALK_STRING_LIST, []):
            if s is None:
                continue
            strref = s.get(F.TALK_STRING_ID, NULL)
            if strref != NULL:
                self.strings.setdefault(strref, s.get(F.TALK_STRING, ""))

    def _load_huffman(self, gff: GFF4) -> None:
        root = gff.root
        tree = gff.list_bytes(root, F.HUFF_TALK_STRING_HUFF_TREE)
        bits = gff.list_bytes(root, F.HUFF_TALK_STRING_BIT_STREAM)
        if not tree or not bits:
            return
        e = gff._e
        nodes = struct.unpack(f"{e}{len(tree) // 4}i", tree)
        words = struct.unpack(f"{e}{len(bits) // 4}I", bits)
        for s in root.get(F.HUFF_TALK_STRING_LIST, []):
            if s is None:
                continue
            strref = s.get(F.HUFF_TALK_STRING_ID, NULL)
            if strref != NULL:
                self.strings.setdefault(strref, decode_huffman(nodes, words, s.get(F.HUFF_TALK_STRING_BIT_OFFSET, 0)))


def decode_huffman(nodes, words, bit_offset: int) -> str:
    """Decode one null-terminated UTF-16 string.

    The tree is an array of node pairs; the root is the last pair. Following
    bit b from node n leads to nodes[2n + b]: a value >= 0 is the next node,
    a negative value v is a leaf holding the code unit ~v. Bits are consumed
    least-significant first from 32-bit words.
    """
    index, shift = bit_offset >> 5, bit_offset & 31
    root = len(nodes) // 2 - 1
    units = []
    while True:
        n = root
        while n >= 0:
            if index >= len(words):
                raise TLKError("Huffman bit stream ended mid-string")
            bit = (words[index] >> shift) & 1
            n = nodes[2 * n + bit]
            shift += 1
            index += shift >> 5
            shift &= 31
        unit = (~n) & 0xFFFF
        if unit == 0:
            break
        units.append(unit)
    return struct.pack(f"<{len(units)}H", *units).decode("utf-16-le", "replace")


class TalkTables:
    """Several talk tables searched in order (e.g. core + single player module)."""

    def __init__(self, tables: list[TalkTable] | None = None):
        self.tables = tables or []

    @classmethod
    def open(cls, paths) -> "TalkTables":
        return cls([TalkTable.open(p) for p in paths])

    def get(self, strref: int, default: str = "") -> str:
        for t in self.tables:
            if strref in t.strings:
                return t.strings[strref]
        return default
