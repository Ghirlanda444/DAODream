"""Data tables (.gda): DAO's spreadsheets for items, abilities, appearances...

A GDA is a GFF4 of type "G2DA". Columns are identified only by the CRC32 of
their lower-cased name encoded as UTF-16LE; the names themselves are not
stored. Pass known column names (e.g. from the toolset's source 2DA
spreadsheets) to resolve them; unresolved columns are shown as hashes.
"""

from __future__ import annotations

import zlib
from pathlib import Path

from . import fields as F
from .gff4 import GFF4, TlkString

COLUMN_TYPES = {-1: "empty", 0: "string", 1: "int", 2: "float", 3: "bool", 4: "resource"}


class GDAError(Exception):
    pass


def column_hash(name: str) -> int:
    return zlib.crc32(name.lower().encode("utf-16-le")) & 0xFFFFFFFF


class GDA:
    def __init__(self, gff: GFF4, known_names: list[str] | None = None):
        if gff.file_type != "G2DA":
            raise GDAError(f"not a GDA (GFF type {gff.file_type!r})")
        lookup = {column_hash(n): n for n in (known_names or [])}
        self.columns: list[dict] = []
        for i, col in enumerate(gff.root.get(F.G2DA_COLUMN_LIST, [])):
            h = col.get(F.G2DA_COLUMN_HASH, 0) if col else 0
            ctype = col.get(F.G2DA_COLUMN_TYPE) if col else None
            self.columns.append({
                "hash": h,
                "name": lookup.get(h, f"0x{h:08x}"),
                "type": COLUMN_TYPES.get(ctype, "unknown") if ctype is not None else "unknown",
            })
        self.rows: list[list] = []
        for row in gff.root.get(F.G2DA_ROW_LIST, []):
            values = []
            for i in range(len(self.columns)):
                v = row.get(F.G2DA_COLUMN_1 + i) if row else None
                values.append(v.strref if isinstance(v, TlkString) else v)
            self.rows.append(values)

    @classmethod
    def open(cls, path: str | Path, known_names: list[str] | None = None) -> "GDA":
        return cls(GFF4.open(path), known_names)

    @property
    def column_names(self) -> list[str]:
        return [c["name"] for c in self.columns]

    def records(self) -> list[dict]:
        names = self.column_names
        return [dict(zip(names, row)) for row in self.rows]
