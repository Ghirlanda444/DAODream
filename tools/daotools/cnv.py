"""Conversations: DAO's dialogue trees (.dlg in the retail game, GFF4).

The field IDs come from community reverse engineering, but how starting
entries and child links are laid out has not been checked against retail
files yet. The exporter therefore accepts either plain indices or structs
holding an index, and keeps every field it does not understand under "extra"
so a real file can be inspected and the mapping tightened.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import fields as F
from .gff4 import GFF4, Struct, TlkString, to_jsonable
from .tlk import TalkTables

_LINE_FLAGS = {
    F.CONV_LINE_AMBIENT: "ambient",
    F.CONV_LINE_SKIP: "skip",
    F.CONV_LINE_FAST_PATH: "fast_path",
    F.CONV_LINE_NO_VO_INGAME: "no_vo_ingame",
    F.CONV_LINE_REVERT_ANIM: "revert_anim",
    F.CONV_LINE_ACTIVE: "active",
}
_LINE_FIELDS = {
    F.CONV_LINE_TEXT, F.CONV_LINE_SPEAKER, F.CONV_LINE_LISTENER, F.CONV_LINE_COND,
    F.CONV_LINE_ACTION, F.CONV_LINE_CHILDREN_LIST, F.CONV_LINE_ANIMATION,
    F.CONV_LINE_ICON, F.CONV_LINE_CUT_RESREF, F.CONV_LINE_CUT, F.CONV_LINE_CUT_MAP,
    *_LINE_FLAGS,
}
_INDEX_FIELDS = (F.CONV_STARTING_INDEX,)


class CNVError(Exception):
    pass


def _plain(value):
    """Any GFF value as plain JSON data: retail files nest structs in places
    where a plain value would be expected."""
    return to_jsonable(value, F.NAMES)


def _index_of(entry) -> int | None:
    """A start/child entry is either a bare index or a struct holding one."""
    if isinstance(entry, int):
        return entry
    if isinstance(entry, Struct):
        for fid in _INDEX_FIELDS:
            if isinstance(entry.get(fid), int):
                return entry.get(fid)
        ints = [v for v in entry.fields.values() if isinstance(v, int) and not isinstance(v, bool)]
        if len(ints) == 1:
            return ints[0]
    return None


def _links(entries) -> tuple[list[int], list]:
    indices, unresolved = [], []
    for e in entries or []:
        i = _index_of(e)
        if i is None:
            unresolved.append(to_jsonable(e, F.NAMES))
        else:
            indices.append(i)
    return indices, unresolved


def _text(value, tlk: TalkTables | None) -> tuple[int | None, str]:
    if isinstance(value, TlkString):
        text = value.text or (tlk.get(value.strref) if tlk else "")
        return value.strref, text
    if isinstance(value, str):
        return None, value
    return None, ""


CONVERSATION_TYPES = ("DLG ", "CNV ", "CONV")


def is_conversation(gff: GFF4) -> bool:
    return gff.file_type in CONVERSATION_TYPES or F.CONV_LINE_LIST in gff.root


def export(gff: GFF4, tlk: TalkTables | None = None, name: str | None = None) -> dict:
    if not is_conversation(gff):
        raise CNVError(f"not a conversation (GFF type {gff.file_type!r})")
    root = gff.root
    starts, bad_starts = _links(root.get(F.CONV_STARTING_LIST, []))
    lines = []
    for i, line in enumerate(root.get(F.CONV_LINE_LIST, [])):
        if line is None:
            lines.append({"index": i, "missing": True})
            continue
        strref, text = _text(line.get(F.CONV_LINE_TEXT), tlk)
        children, bad_children = _links(line.get(F.CONV_LINE_CHILDREN_LIST, []))
        entry = {
            "index": i,
            "strref": strref,
            "text": text,
            "speaker": _plain(line.get(F.CONV_LINE_SPEAKER, "")),
            "listener": _plain(line.get(F.CONV_LINE_LISTENER, "")),
            "children": children,
        }
        if F.CONV_LINE_COND in line:
            entry["condition"] = to_jsonable(line.get(F.CONV_LINE_COND), F.NAMES)
        if F.CONV_LINE_ACTION in line:
            entry["action"] = to_jsonable(line.get(F.CONV_LINE_ACTION), F.NAMES)
        if F.CONV_LINE_ANIMATION in line:
            entry["animation"] = to_jsonable(line.get(F.CONV_LINE_ANIMATION), F.NAMES)
        raw_text = line.get(F.CONV_LINE_TEXT)
        if raw_text is not None and not isinstance(raw_text, (TlkString, str)):
            entry["text_raw"] = _plain(raw_text)
        flags = {n: _plain(line.get(fid)) for fid, n in _LINE_FLAGS.items() if fid in line}
        if flags:
            entry["flags"] = flags
        if bad_children:
            entry["unresolved_children"] = bad_children
        extra = {F.NAMES.get(k, str(k)): to_jsonable(v, F.NAMES)
                 for k, v in line.fields.items() if k not in _LINE_FIELDS}
        if extra:
            entry["extra"] = extra
        lines.append(entry)

    out = {
        "conversation": name or (Path(gff.path).stem if gff.path else None),
        "format": f"{gff.version} {gff.file_type.strip()} {gff.type_version}",
        "vo_bank": _plain(root.get(F.CONV_VO_BANK)),
        "starts": starts,
        "lines": lines,
    }
    if bad_starts:
        out["unresolved_starts"] = bad_starts
    extra = {F.NAMES.get(k, str(k)): to_jsonable(v, F.NAMES) for k, v in root.fields.items()
             if k not in (F.CONV_STARTING_LIST, F.CONV_LINE_LIST, F.CONV_VO_BANK)}
    if extra:
        out["extra"] = extra
    return out


def transcript(conv: dict) -> str:
    """Render an exported conversation as an indented, readable script."""
    lines = conv["lines"]
    out = [f"# {conv.get('conversation') or 'conversation'}", ""]
    seen: set[int] = set()

    def walk(idx: int, depth: int) -> None:
        pad = "  " * depth
        if idx < 0 or idx >= len(lines) or lines[idx].get("missing"):
            out.append(f"{pad}[missing line {idx}]")
            return
        if idx in seen:
            out.append(f"{pad}-> (back to line {idx})")
            return
        seen.add(idx)
        line = lines[idx]
        who = line.get("speaker") or "(owner)"
        if not isinstance(who, str):
            who = json.dumps(who, ensure_ascii=False, separators=(",", ":"))
        text = line.get("text") or (f"<strref {line['strref']}>" if line.get("strref") is not None else "<no text>")
        tags = []
        if line.get("condition"):
            tags.append("if")
        if line.get("action"):
            tags.append("do")
        suffix = f"  [{', '.join(tags)}]" if tags else ""
        out.append(f"{pad}{idx:>4} {who}: {text}{suffix}")
        for child in line.get("children", []):
            walk(child, depth + 1)

    for start in conv.get("starts", []):
        walk(start, 0)
        out.append("")
    orphans = [l["index"] for l in lines if l["index"] not in seen and not l.get("missing")]
    if orphans:
        out.append(f"# lines not reached from any start: {orphans}")
    return "\n".join(out).rstrip() + "\n"
