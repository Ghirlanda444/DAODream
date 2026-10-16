"""Conversations in the shape the Unreal project reads at runtime.

Unreal parses this with the Json Blueprint Utilities plugin into Blueprint
structs, which match JSON keys to struct field names. So the format is flat
and fully typed: PascalCase keys, no nulls, no nested condition structs.
Plot flags are written as "GUID:FLAG" strings so a Blueprint can keep the
flags that are set in a plain Set of strings.

Runtime rules (see docs/GAME_DATA.md for how they were derived):
- Starts are tried in order; the first whose condition holds is used.
- A condition holds when its flag is set (or not set, with CondNot).
  Script conditions cannot run yet and are treated as holding.
- An action sets its flag, or clears it with ActionNot (plot test 0 on an
  action, as on a condition). Script actions are ignored for now.
- Show is the toolset's "show once" setting (conv_line_visibility): 0 always,
  1 once per conversation, 2 once per game. A line already shown that way is
  skipped like one whose condition fails.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from . import fsb, plo

FORMAT = "DAODream.Conversation 1"

# DAO marks stage directions with <desc> and stress with <emp>.
_DESC = re.compile(r"<desc>(.*?)</desc>", re.S)
_TAG = re.compile(r"</?\w+>")


def display_text(text: str | None) -> str:
    """Line text as it should appear on screen: stage directions in
    parentheses, other markup dropped."""
    text = _DESC.sub(lambda m: f"({m.group(1).strip()})", text or "")
    return _TAG.sub("", text).strip()


def flag_key(plot: str, flag: int) -> str:
    return f"{plot}:{flag}"


def _plot_slot(ref: dict | None, warnings: list[str], where: str) -> tuple[str, bool, str]:
    """(flag key, negated, script) for a condition or action slot."""
    if not isinstance(ref, dict):
        return "", False, ""
    key = flag_key(ref["plot"], ref["flag"]) if ref.get("plot") else ""
    test = ref.get("test")
    if test not in (None, 0):
        warnings.append(f"{where}: unknown plot test {test}, read as 'flag is set'")
    return key, test == 0, ref.get("script") or ""


def speaker_names(tags, owner: str, search_dir) -> dict[str, str]:
    """Display names for speaker tags, from <tag>.utc.json files written by
    `daotools pull` under one folder or a list of them (the first folder that
    has a tag wins). OWNER is the conversation owner's tag."""
    names: dict[str, str] = {}
    dirs = [search_dir] if isinstance(search_dir, (str, Path)) else list(search_dir or [])
    files: dict[str, Path] = {}
    for d in dirs:
        for p in Path(d).rglob("*.utc.json"):
            files.setdefault(p.name.lower(), p)
    for tag in sorted(set(tags) | {owner}):
        path = files.get(f"{tag.lower()}.utc.json")
        if not path:
            continue
        loc = json.loads(path.read_text(encoding="utf-8"))["root"].get("LocName")
        name = loc.get("text") if isinstance(loc, dict) else loc
        if name:
            names[tag] = name
    if owner in names:
        names["OWNER"] = names[owner]
    return names


def conversation(conv: dict, *, owner: str | None = None, names_dir=None,
                 true_flags: list[str] | None = None, plots: dict[str, dict] | None = None,
                 vo_samples: set[str] | None = None) -> dict:
    """Turn a `cnv.export` result into the runtime format.

    With `plots` (from `plo.load_dir`), FlagNames maps every flag key the
    conversation uses to its plot flag name, for reading and debugging.
    With `vo_samples` (the sample names in the VO bank), each line's Vo is the
    file stem of its voice-over ("" when it has none), as written by
    `daotools fsb extract`.
    """
    owner = owner or conv.get("conversation") or ""
    warnings: list[str] = []
    lines = []
    for line in conv["lines"]:
        i = line["index"]
        if line.get("missing"):
            warnings.append(f"line {i}: missing")
        speaker = line.get("speaker", "")
        if not isinstance(speaker, str):
            warnings.append(f"line {i}: speaker is not a tag")
            speaker = ""
        cond_key, cond_not, cond_script = _plot_slot(line.get("condition"), warnings, f"line {i} condition")
        act_key, act_not, act_script = _plot_slot(line.get("action"), warnings, f"line {i} action")
        text = display_text(line.get("text"))
        show = (line.get("extra") or {}).get("conv_line_visibility", 0)
        if show not in (0, 1, 2):
            warnings.append(f"line {i}: unknown visibility {show}, shown always")
            show = 0
        vo = ""
        if vo_samples is not None:
            sample = fsb.vo_sample(line.get("strref"))
            if sample in vo_samples:
                vo = sample.rsplit(".", 1)[0]
            elif text and line.get("kind") == "npc":
                warnings.append(f"line {i}: no voice-over sample {sample or '(no strref)'}")
        lines.append({
            "Index": i,
            "IsPlayer": line.get("kind") == "player",
            "Speaker": speaker,
            "Text": text,
            "Children": list(line.get("children", [])),
            "Stage": line.get("stage") if isinstance(line.get("stage"), str) else "",
            "CondKey": cond_key,
            "CondNot": cond_not,
            "CondScript": cond_script,
            "ActionKey": act_key,
            "ActionNot": act_not,
            "ActionScript": act_script,
            "Vo": vo,
            "Show": show,
        })
    tags = {l["Speaker"] for l in lines if l["Speaker"] and l["Speaker"] not in ("OWNER", "PLAYER")}
    flag_names: dict[str, str] = {}
    if plots is not None:
        keys = {k for l in lines for k in (l["CondKey"], l["ActionKey"]) if k} | set(true_flags or [])
        for key in sorted(keys):
            name = plo.flag_name(plots, key)
            if name:
                flag_names[key] = name
            else:
                warnings.append(f"plot flag {key}: not found in the plot files")
    vo_bank = conv.get("vo_bank")
    return {
        "Format": FORMAT,
        "Conversation": conv.get("conversation") or "",
        "Owner": owner,
        "VoBank": vo_bank if isinstance(vo_bank, str) else "",
        "Starts": list(conv.get("starts", [])),
        "SpeakerNames": speaker_names(tags, owner, names_dir),
        "TrueFlags": list(true_flags or []),
        "FlagNames": flag_names,
        "Lines": lines,
        "Warnings": warnings,
    }
