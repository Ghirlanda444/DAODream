"""Plot scripts translated into actions Unreal can run.

A plot's script (NWScript source from the toolset, see toolset.py) handles
EVENT_TYPE_SET_PLOT with `switch(nFlag)`: one case per flag of its plot. Most
cases are a short list of helper calls. This turns each case into actions:

  1 jump      UT_LocalJump(oCreature, WAYPOINT)        target tag, waypoint tag
  2 talk      UT_Talk(oCreature, ...)                  target tag
  3 active    WR_SetObjectActive(oObject, TRUE/FALSE)  target tag, 1/0
  4 setflag   WR_SetPlotFlag(PLT_NAME, FLAG, TRUE/FALSE)   "GUID:FLAG", 1/0
  5 autosave  DoAutoSave()

Case fall-through (a case without `break`) is followed, as the game does.
Anything else in a case is listed under "Skipped" so coverage is visible.
Creatures are resolved from `object oX = UT_GetNearestCreatureByTag(..., CONST)`
lines and string constants from every exported script; `PLT_<NAME>` is the
plot named <name> and flag constants are the plot's flag names.
"""

from __future__ import annotations

import fnmatch
import re
from pathlib import Path

FORMAT = "DAODream.PlotActions 1"
JUMP, TALK, ACTIVE, SETFLAG, AUTOSAVE = 1, 2, 3, 4, 5
_KIND_NAMES = {JUMP: "jump", TALK: "talk", ACTIVE: "active", SETFLAG: "setflag", AUTOSAVE: "autosave"}

_COMMENTS = re.compile(r"//[^\n]*|/\*.*?\*/", re.S)
_CONST = re.compile(r"const\s+(string|int)\s+(\w+)\s*=\s*(\"[^\"]*\"|-?\d+)\s*;")
_OBJECT = re.compile(r"object\s+(\w+)\s*=\s*(?:UT_GetNearestCreatureByTag|UT_GetNearestObjectByTag|GetObjectByTag)"
                     r"\s*\(\s*(?:\w+\s*,\s*)?(\w+|\"[^\"]*\")")
_CALL = re.compile(r"^(\w+)\s*\((.*)\)$", re.S)
_IGNORED = {"break", "Log_Plot", "Log_Trace", "LogTrace", "plot_GlobalPlotHandler"}


def load_constants(src_dir: str | Path) -> dict[str, object]:
    consts: dict[str, object] = {}
    for p in sorted(Path(src_dir).glob("*.nss")):
        for kind, name, value in _CONST.findall(_COMMENTS.sub("", p.read_text(encoding="utf-8", errors="replace"))):
            consts.setdefault(name, value.strip('"') if kind == "string" else int(value))
    return consts


def _block(text: str, start: int) -> str:
    """The text inside the braces that open at or after `start`."""
    i = text.index("{", start)
    depth = 0
    for j in range(i, len(text)):
        depth += {"{": 1, "}": -1}.get(text[j], 0)
        if depth == 0:
            return text[i + 1:j]
    raise ValueError("unbalanced braces")


def _args(s: str) -> list[str]:
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
            continue
        depth += {"(": 1, ")": -1}.get(ch, 0)
        cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def _cases(switch_body: str) -> list[tuple[str, list[str], bool]]:
    """(label, statements, ends with break) in source order."""
    parts = re.split(r"\bcase\s+(\w+)\s*:", switch_body)
    cases = []
    for label, body in zip(parts[1::2], parts[2::2]):
        statements = [s.strip() for s in body.replace("{", ";").replace("}", ";").split(";")]
        statements = [s for s in statements if s]
        cases.append((label, statements, "break" in statements))
    return cases


def translate(script: str, plot: dict, plots_by_name: dict[str, dict], consts: dict) -> dict:
    """{"cases": {flag name: [action dicts]}, "skipped": [...]} for one plot script."""
    text = _COMMENTS.sub("", script)
    objects = {}
    for var, ref in _OBJECT.findall(text):
        objects[var] = ref.strip('"') if ref.startswith('"') else consts.get(ref, ref)
    flag_ids = {name: fid for fid, name in plot["flags"].items()}
    skipped: list[str] = []

    def value(token: str):
        token = token.strip()
        if token in ("TRUE", "FALSE"):
            return 1 if token == "TRUE" else 0
        if token.startswith('"'):
            return token.strip('"')
        return consts.get(token, token)

    def action(stmt: str):
        m = _CALL.match(stmt)
        if not m:
            return None if stmt in _IGNORED else ("skip", stmt)
        fn, args = m.group(1), _args(m.group(2))
        if fn in _IGNORED:
            return None
        if fn == "UT_LocalJump" and len(args) >= 2:
            return {"kind": JUMP, "target": objects.get(args[0], args[0]), "arg": str(value(args[1])), "value": 1}
        if fn == "UT_Talk" and args:
            return {"kind": TALK, "target": objects.get(args[0], args[0]), "arg": "", "value": 1}
        if fn == "WR_SetObjectActive" and len(args) >= 2:
            return {"kind": ACTIVE, "target": objects.get(args[0], args[0]), "arg": "", "value": int(value(args[1]) == 1)}
        if fn == "WR_SetPlotFlag" and len(args) >= 3 and args[0].startswith("PLT_"):
            target = plots_by_name.get(args[0][4:].lower())
            fid = {n: f for f, n in target["flags"].items()}.get(args[1]) if target else None
            if fid is None:
                return ("skip", f"{fn}({args[0]}, {args[1]}): unknown plot or flag")
            return {"kind": SETFLAG, "target": "", "arg": f"{target['guid']}:{fid}", "value": int(value(args[2]) == 1)}
        if fn == "DoAutoSave":
            return {"kind": AUTOSAVE, "target": "", "arg": "", "value": 1}
        return ("skip", fn)

    m = re.search(r"EVENT_TYPE_SET_PLOT", text)
    if not m:
        return {"cases": {}, "skipped": ["no EVENT_TYPE_SET_PLOT handler"]}
    switch = re.search(r"switch\s*\(\s*nFlag\s*\)", text[m.end():])
    if not switch:
        return {"cases": {}, "skipped": ["no switch(nFlag) for SET events"]}
    body = _block(text, m.end() + switch.end())
    cases = _cases(body)

    own: dict[str, list] = {}
    for label, statements, _ in cases:
        acts = []
        for s in statements:
            a = action(s)
            if a is None:
                continue
            if isinstance(a, tuple):
                skipped.append(f"{label}: {a[1]}")
            else:
                acts.append(a)
        if any(s.startswith(("if", "else", "while", "for")) for s in statements):
            skipped.append(f"{label}: has conditional logic, ported as unconditional")
        own[label] = acts
    result = {}
    for i, (label, _, has_break) in enumerate(cases):
        acts = list(own[label])
        j = i
        while not cases[j][2] and j + 1 < len(cases):  # fall through until a break
            j += 1
            acts += own[cases[j][0]]
        if label not in flag_ids:
            skipped.append(f"{label}: not a flag of {plot['name']}")
            continue
        result[label] = acts
    return {"cases": result, "skipped": skipped}


def export(src_dir: str | Path, plots: dict[str, dict], only: str = "*") -> dict:
    """The runtime file: flat arrays keyed by "GUID:FLAG", plus a readable report."""
    consts = load_constants(src_dir)
    by_name = {p["name"].lower(): p for p in plots.values()}
    keys, starts, counts = [], [], []
    kinds, targets, args, values = [], [], [], []
    report = {}
    for guid, plot in sorted(plots.items(), key=lambda kv: kv[1]["name"]):
        script = plot.get("script") or ""
        path = Path(src_dir) / f"{script}.nss"
        if not script or not fnmatch.fnmatch(plot["name"].lower(), only.lower()) or not path.exists():
            continue
        t = translate(path.read_text(encoding="utf-8", errors="replace"), plot, by_name, consts)
        flag_ids = {name: fid for fid, name in plot["flags"].items()}
        for label, acts in t["cases"].items():
            if not acts:
                continue
            keys.append(f"{guid}:{flag_ids[label]}")
            starts.append(len(kinds))
            counts.append(len(acts))
            for a in acts:
                kinds.append(a["kind"])
                targets.append(a["target"])
                args.append(a["arg"])
                values.append(a["value"])
        report[plot["name"]] = {
            "Script": script,
            "Cases": {label: [f"{_KIND_NAMES[a['kind']]} {a['target']} {a['arg']} {a['value']}".strip()
                              for a in acts] for label, acts in t["cases"].items()},
            "Skipped": t["skipped"],
        }
    return {"Format": FORMAT, "Keys": keys, "Start": starts, "Count": counts, "Kind": kinds, "Target": targets,
            "Arg": args, "Value": values, "Plots": report}
