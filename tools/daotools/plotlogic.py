"""Plot scripts translated into actions Unreal can run.

A plot's script (NWScript source from the toolset, see toolset.py) handles
EVENT_TYPE_SET_PLOT with `switch(nFlag)`: one case per flag of its plot. Most
cases are a short list of helper calls. This turns each case into actions:

  1 jump      UT_LocalJump(oCreature, WAYPOINT)        target tag, waypoint tag
  2 talk      UT_Talk(oCreature, ...)                  target tag
  3 active    WR_SetObjectActive(oObject, TRUE/FALSE)  target tag, 1/0
  4 setflag   WR_SetPlotFlag(PLT_NAME, FLAG, TRUE/FALSE)   "GUID:FLAG", 1/0
  5 autosave  DoAutoSave()
  6 walk      AddCommand/WR_AddCommand(oCreature, CommandMoveToObject(oWP, bRun))   target tag,
              CommandMoveToLocation(GetLocation(oWP), bRun), UT_QuickMoveObject    waypoint tag, run 1/0
  8 party     UT_HireFollower, SetFollowerRecruited, SetFollowerInParty,       target tag, 1 join
              AddNonPartyFollower / UT_FireFollower, Party_SetFollowerInCamp     0 leave
  7 door      SetPlaceableActionResult(oDoor, PLACEABLE_ACTION_X, TRUE)        target tag, verb:
              SetPlaceableState(oDoor, PLC_STATE_DOOR_X)                        open, open2, close,
                                                                                lock, unlock, break

Teams: UT_TeamAppears(TEAM, bool) and UT_TeamMove(TEAM, WAYPOINT, bRun) become
`active` and `walk` with the target "team:<id>"; Unreal tags every spawned
creature with its team (area.py exports TeamId).

Events: a creature script's EVENT_TYPE_DEATH branches `if (sTag == CONST)` become
the key "death:<tag>", and an area script's EVENT_TYPE_TEAM_DESTROYED cases
(`switch (nTeamID)`) the key "teamdead:<id>", in the same table; Unreal runs
them when that creature dies or the last member of that team does.

Case fall-through (a case without `break`) is followed, as the game does.
Anything else in a case is listed under "Skipped" so coverage is visible.
Creatures are resolved from `object oX = UT_GetNearestCreatureByTag(..., CONST)`
lines and string constants from every exported script; `PLT_<NAME>` is the
plot named <name> and flag constants are the plot's flag names. A move's
destination may go through a `location` or `command` variable first; a run
flag that is only known at runtime counts as walking.
"""

from __future__ import annotations

import fnmatch
import re
from pathlib import Path

FORMAT = "DAODream.PlotActions 1"
JUMP, TALK, ACTIVE, SETFLAG, AUTOSAVE, WALK, DOOR, PARTY = 1, 2, 3, 4, 5, 6, 7, 8
_KIND_NAMES = {JUMP: "jump", TALK: "talk", ACTIVE: "active", SETFLAG: "setflag", AUTOSAVE: "autosave", WALK: "walk",
               DOOR: "door", PARTY: "party"}
_PARTY_CALLS = {"UT_HireFollower": 1, "SetFollowerRecruited": 1, "SetFollowerInParty": 1, "AddNonPartyFollower": 1,
                "UT_FireFollower": 0, "Party_SetFollowerInCamp": 0}
# What a door does for each placeable action / door state the scripts use.
_DOOR_ACTIONS = {"PLACEABLE_ACTION_OPEN": "open", "PLACEABLE_ACTION_CLOSE": "close",
                 "PLACEABLE_ACTION_UNLOCK": "unlock", "PLACEABLE_ACTION_LOCK": "lock"}
_DOOR_STATES = {"PLC_STATE_DOOR_UNLOCKED": "close", "PLC_STATE_DOOR_LOCKED": "lock", "PLC_STATE_DOOR_OPEN": "open",
                "PLC_STATE_DOOR_OPEN_2": "open2", "PLC_STATE_DOOR_DEAD": "break", "PLC_STATE_DOOR_DEAD_2": "break"}

_COMMENTS = re.compile(r"//[^\n]*|/\*.*?\*/", re.S)
_CONST = re.compile(r"const\s+(string|int)\s+(\w+)\s*=\s*(\"[^\"]*\"|-?\d+)\s*;")
_OBJECT = re.compile(r"object\s+(\w+)\s*=\s*(?:UT_GetNearestCreatureByTag|UT_GetNearestObjectByTag|GetObjectByTag"
                     r"|Party_GetFollowerByTag)"
                     r"\s*\(\s*(?:\w+(?:\(\s*\))?\s*,\s*)?(\w+|\"[^\"]*\")")
_LOCATION = re.compile(r"location\s+(\w+)\s*=\s*GetLocation\s*\(\s*(\w+)\s*\)")
_COMMAND = re.compile(r"command\s+(\w+)\s*=\s*(CommandMoveTo(?:Object|Location)\s*\(.*?\))\s*;")
_DECLARATION = re.compile(r"^(object|location|command)\s+(\w+)\s*=")
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


def _resolver(text: str, plots_by_name: dict[str, dict], consts: dict):
    """action(statement) -> action dict, None (nothing to do) or ("skip", why), for one script
    (comments already stripped)."""
    objects = {}
    for var, ref in _OBJECT.findall(text):
        objects[var] = ref.strip('"') if ref.startswith('"') else consts.get(ref, ref)
    locations = {var: objects[obj] for var, obj in _LOCATION.findall(text) if obj in objects}
    commands = dict(_COMMAND.findall(text))

    def value(token: str):
        token = token.strip()
        if token in ("TRUE", "FALSE"):
            return 1 if token == "TRUE" else 0
        if token.startswith('"'):
            return token.strip('"')
        return consts.get(token, token)

    def move(cmd: str):
        """(waypoint tag, run) for a CommandMoveTo... expression, or None."""
        m = _CALL.match(commands.get(cmd.strip(), cmd.strip()))
        if not m or m.group(1) not in ("CommandMoveToObject", "CommandMoveToLocation"):
            return None
        args = _args(m.group(2))
        where = (objects if m.group(1) == "CommandMoveToObject" else locations).get(args[0]) if args else None
        if where is None:
            return None
        return where, int(len(args) > 1 and value(args[1]) == 1)

    def obj(token: str):
        """The tag an object argument names, or None when it is only known at runtime."""
        token = token.strip()
        if token in objects:
            return objects[token]
        return token.strip('"') if token.startswith('"') else None

    def action(stmt: str):
        d = _DECLARATION.match(stmt)
        if d and (d.group(2) in objects or d.group(2) in locations or d.group(2) in commands):
            return None  # resolved where it is used
        m = _CALL.match(stmt)
        if not m:
            return None if stmt in _IGNORED else ("skip", stmt)
        fn, args = m.group(1), _args(m.group(2))
        if fn in _IGNORED:
            return None
        if (fn in ("UT_LocalJump", "UT_Talk", "WR_SetObjectActive") or fn in _PARTY_CALLS) and args                 and obj(args[0]) is None:
            return ("skip", f"{fn}({args[0]}): object only known at runtime")
        if fn == "UT_LocalJump" and len(args) >= 2:
            return {"kind": JUMP, "target": obj(args[0]), "arg": str(value(args[1])), "value": 1}
        if fn == "UT_Talk" and args:
            return {"kind": TALK, "target": obj(args[0]), "arg": "", "value": 1}
        if fn == "WR_SetObjectActive" and len(args) >= 2:
            return {"kind": ACTIVE, "target": obj(args[0]), "arg": "", "value": int(value(args[1]) == 1)}
        if fn == "WR_SetPlotFlag" and len(args) >= 3 and args[0].startswith("PLT_"):
            target = plots_by_name.get(args[0][4:].lower())
            fid = {n: f for f, n in target["flags"].items()}.get(args[1]) if target else None
            if fid is None:
                return ("skip", f"{fn}({args[0]}, {args[1]}): unknown plot or flag")
            return {"kind": SETFLAG, "target": "", "arg": f"{target['guid']}:{fid}", "value": int(value(args[2]) == 1)}
        if fn == "DoAutoSave":
            return {"kind": AUTOSAVE, "target": "", "arg": "", "value": 1}
        if fn in ("AddCommand", "WR_AddCommand") and len(args) >= 2 and args[0] in objects:
            dest = move(args[1])
            if dest is None:
                return ("skip", f"{fn}: not a move to a known waypoint")
            return {"kind": WALK, "target": objects[args[0]], "arg": dest[0], "value": dest[1]}
        if fn == "SetPlaceableActionResult" and len(args) >= 2 and args[0] in objects:
            verb = _DOOR_ACTIONS.get(args[1])
            if verb is None or (len(args) > 2 and value(args[2]) != 1):
                return ("skip", f"{fn}({args[1]})")
            return {"kind": DOOR, "target": objects[args[0]], "arg": verb, "value": 1}
        if fn == "SetPlaceableState" and len(args) >= 2 and args[0] in objects and args[1] in _DOOR_STATES:
            return {"kind": DOOR, "target": objects[args[0]], "arg": _DOOR_STATES[args[1]], "value": 1}
        if fn in ("UT_TeamAppears", "UT_TeamMove") and args:
            team = value(args[0])
            if not isinstance(team, int):
                return ("skip", f"{fn}({args[0]}): unknown team")
            if fn == "UT_TeamAppears":
                if len(args) > 2 and args[2] != "OBJECT_TYPE_CREATURE":
                    return ("skip", f"{fn}: {args[2]} teams")
                return {"kind": ACTIVE, "target": f"team:{team}", "arg": "",
                        "value": int(len(args) < 2 or value(args[1]) == 1)}
            if len(args) < 2:
                return ("skip", f"{fn}: no destination")
            return {"kind": WALK, "target": f"team:{team}", "arg": str(value(args[1])),
                    "value": int(len(args) > 2 and value(args[2]) == 1)}
        if fn in _PARTY_CALLS and args:
            return {"kind": PARTY, "target": obj(args[0]), "arg": "", "value": _PARTY_CALLS[fn]}
        if fn == "UT_QuickMoveObject" and len(args) >= 2 and args[0] in objects:
            return {"kind": WALK, "target": objects[args[0]], "arg": str(value(args[1])),
                    "value": int(len(args) > 2 and value(args[2]) == 1)}
        return ("skip", fn)

    return action, value


def _statements(body: str) -> list[str]:
    return [s for s in (s.strip() for s in body.replace("{", ";").replace("}", ";").split(";")) if s]


def _run(action, statements: list[str], label: str, skipped: list[str]) -> list[dict]:
    acts = []
    for stmt in statements:
        a = action(stmt)
        if isinstance(a, tuple):
            skipped.append(f"{label}: {a[1]}")
        elif a is not None:
            acts.append(a)
    return acts


def translate_events(script: str, plots_by_name: dict[str, dict], consts: dict) -> dict:
    """{"cases": {"death:<tag>" / "teamdead:<id>": [action dicts]}, "skipped": [...]} for a
    creature or area script."""
    text = _COMMENTS.sub("", script)
    action, value = _resolver(text, plots_by_name, consts)
    cases: dict[str, list] = {}
    skipped: list[str] = []
    m = re.search(r"case\s+EVENT_TYPE_DEATH\s*:", text)
    if m:
        body = _block(text, m.end())
        for branch in re.finditer(r"if\s*\(\s*sTag\s*==\s*(\w+)\s*\)", body):
            tag = value(branch.group(1))
            label = f"death:{tag}"
            cases[label] = cases.get(label, []) + _run(action, _statements(_block(body, branch.end())), label, skipped)
    m = re.search(r"case\s+EVENT_TYPE_TEAM_DESTROYED\s*:", text)
    switch = m and re.search(r"switch\s*\(\s*nTeamID\s*\)", text[m.end():])
    if switch:
        for label, statements, _ in _cases(_block(text, m.end() + switch.end())):
            team = value(label)
            if not isinstance(team, int):
                skipped.append(f"team {label}: unknown team")
                continue
            cases[f"teamdead:{team}"] = _run(action, statements, f"teamdead:{team}", skipped)
    return {"cases": cases, "skipped": skipped}


def translate(script: str, plot: dict, plots_by_name: dict[str, dict], consts: dict) -> dict:
    """{"cases": {flag name: [action dicts]}, "skipped": [...]} for one plot script."""
    text = _COMMENTS.sub("", script)
    action, _ = _resolver(text, plots_by_name, consts)
    flag_ids = {name: fid for fid, name in plot["flags"].items()}
    skipped: list[str] = []

    m = re.search(r"EVENT_TYPE_SET_PLOT", text)
    if not m:
        return {"cases": {}, "skipped": ["no EVENT_TYPE_SET_PLOT handler"]}
    switch = re.search(r"switch\s*\(\s*n(?:Bit)?Flag\s*\)", text[m.end():])
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


def _matches(name: str, only: str) -> bool:
    """`only` is one or more name patterns separated by commas, e.g. "bhn*,gen00pt_party"."""
    return any(fnmatch.fnmatch(name.lower(), pattern.strip().lower()) for pattern in only.split(","))


def export(src_dir: str | Path, plots: dict[str, dict], only: str = "*") -> dict:
    """The runtime file: flat arrays keyed by "GUID:FLAG" (plus "death:<tag>" and
    "teamdead:<id>" from creature and area scripts whose name matches `only`), and a
    readable report."""
    consts = load_constants(src_dir)
    by_name = {p["name"].lower(): p for p in plots.values()}
    keys, starts, counts = [], [], []
    kinds, targets, args, values = [], [], [], []
    report = {}
    for guid, plot in sorted(plots.items(), key=lambda kv: kv[1]["name"]):
        script = plot.get("script") or ""
        path = Path(src_dir) / f"{script}.nss"
        if not script or not _matches(plot["name"], only) or not path.exists():
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
    events = {}
    for path in sorted(Path(src_dir).glob("*.nss")):
        if not _matches(path.stem, only):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if "EVENT_TYPE_DEATH" not in text and "EVENT_TYPE_TEAM_DESTROYED" not in text:
            continue
        t = translate_events(text, by_name, consts)
        if not t["cases"]:
            continue
        for key, acts in t["cases"].items():
            if not acts:
                continue
            keys.append(key)
            starts.append(len(kinds))
            counts.append(len(acts))
            for a in acts:
                kinds.append(a["kind"])
                targets.append(a["target"])
                args.append(a["arg"])
                values.append(a["value"])
        events[path.stem] = {
            "Cases": {key: [f"{_KIND_NAMES[a['kind']]} {a['target']} {a['arg']} {a['value']}".strip()
                            for a in acts] for key, acts in t["cases"].items()},
            "Skipped": t["skipped"],
        }
    return {"Format": FORMAT, "Keys": keys, "Start": starts, "Count": counts, "Kind": kinds, "Target": targets,
            "Arg": args, "Value": values, "Plots": report, "Events": events}
