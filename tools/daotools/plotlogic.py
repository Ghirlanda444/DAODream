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
  9 ambient   Ambient_Start(oCreature, ..., nAnimPattern), Ambient_StartTeam,  target tag or team,
              Ambient_StartTag / Ambient_Stop(oCreature)                       pattern (-1 its own), 0 stop

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
JUMP, TALK, ACTIVE, SETFLAG, AUTOSAVE, WALK, DOOR, PARTY, AMBIENT = 1, 2, 3, 4, 5, 6, 7, 8, 9
HOSTILE, EXIT, KILL, TRANSITION, COND, SKIP = 10, 11, 12, 13, 14, 15
_KIND_NAMES = {JUMP: "jump", TALK: "talk", ACTIVE: "active", SETFLAG: "setflag", AUTOSAVE: "autosave", WALK: "walk",
               DOOR: "door", PARTY: "party", AMBIENT: "ambient", HOSTILE: "hostile", EXIT: "exit", KILL: "kill",
               TRANSITION: "transition", COND: "if", SKIP: "skip"}
_GROUPS = {"GROUP_HOSTILE": 1, "GROUP_HOSTILE_ON_GROUND": 1, "GROUP_NEUTRAL": 0, "GROUP_FRIENDLY": 0, "GROUP_PC": 0}
_PARTY_CALLS = {"UT_HireFollower": 1, "SetFollowerRecruited": 1, "SetFollowerInParty": 1, "AddNonPartyFollower": 1,
                "UT_FireFollower": 0, "Party_SetFollowerInCamp": 0}
# What a door does for each placeable action / door state the scripts use.
_DOOR_ACTIONS = {"PLACEABLE_ACTION_OPEN": "open", "PLACEABLE_ACTION_CLOSE": "close",
                 "PLACEABLE_ACTION_UNLOCK": "unlock", "PLACEABLE_ACTION_LOCK": "lock"}
_DOOR_STATES = {"PLC_STATE_DOOR_UNLOCKED": "close", "PLC_STATE_DOOR_LOCKED": "lock", "PLC_STATE_DOOR_OPEN": "open",
                "PLC_STATE_DOOR_OPEN_2": "open2", "PLC_STATE_DOOR_DEAD": "break", "PLC_STATE_DOOR_DEAD_2": "break"}

_COMMENTS = re.compile(r"//[^\n]*|/\*.*?\*/", re.S)
_CONST = re.compile(r"const\s+(string|int)\s+(\w+)\s*=\s*(\"[^\"]*\"|-?\d+)\s*;")
_GETTERS = r"(?:UT_GetNearestCreatureByTag|UT_GetNearestObjectByTag|GetObjectByTag|Party_GetFollowerByTag)"
_ASSIGN = re.compile(r"^(?:object\s+)?(\w+)\s*=\s*" + _GETTERS +
                     r"\s*\(\s*(?:\w+(?:\(\s*\))?\s*,\s*)?(\w+|\"[^\"]*\")")
_HELPER = re.compile(r"\bvoid\s+(\w+)\s*\(\s*\)\s*\{")
_DEBUG_ELSE = re.compile(r"if\s*\(\s*(?:nDebug\s*==\s*FALSE|!\s*nDebug)\s*\)\s*\{")
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


def _cases(switch_body: str) -> list[tuple[str, list[str], bool, str]]:
    """(label, statements, ends with break, raw body) in source order."""
    parts = re.split(r"\bcase\s+(\w+)\s*:", switch_body)
    cases = []
    for label, body in zip(parts[1::2], parts[2::2]):
        statements = [s.strip() for s in body.replace("{", ";").replace("}", ";").split(";")]
        statements = [s for s in statements if s]
        cases.append((label, statements, "break" in statements, body))
    return cases


def _paren_end(text: str, i: int) -> int:
    """Index of the ')' matching the '(' at i."""
    depth = 0
    for k in range(i, len(text)):
        depth += {"(": 1, ")": -1}.get(text[k], 0)
        if depth == 0:
            return k
    return len(text) - 1


def _extent(text: str, j: int) -> int:
    """End (exclusive) of the statement or construct starting at j: a block, an
    if/else chain, a loop, or a plain statement up to its ';'."""
    n = len(text)
    while j < n and text[j].isspace():
        j += 1
    if j < n and text[j] == "{":
        return j + len(_block(text, j)) + 2
    m = re.match(r"(if|while|for|switch)\s*\(", text[j:])
    if m:
        e = _extent(text, _paren_end(text, j + m.end() - 1) + 1)
        if m.group(1) == "if":
            k = e
            while k < n and text[k].isspace():
                k += 1
            if re.match(r"else\b", text[k:]):
                e = _extent(text, k + 4)
        return e
    depth = 0
    for k in range(j, n):
        ch = text[k]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == ";" and depth == 0:
            return k + 1
        elif ch == "}" and depth == 0:
            return k
    return n


def _items(text: str) -> list:
    """Statements in order, with `if` kept as ("if", condition, then items, else items);
    other blocks and loops are opened up (their bodies run once, as before)."""
    items, i, n = [], 0, len(text)
    while True:
        while i < n and (text[i].isspace() or text[i] in ";}"):
            i += 1
        if i >= n:
            return items
        e = _extent(text, i)
        c = text[i:e].strip()
        i = max(e, i + 1)
        if c.startswith("{"):
            items.extend(_items(_block(c, 0)))
            continue
        m = re.match(r"(if|while|for|switch)\s*\(", c)
        if m:
            close = _paren_end(c, m.end() - 1)
            body_end = _extent(c, close + 1)
            body = c[close + 1:body_end]
            if m.group(1) == "if":
                rest = c[body_end:].strip()
                els = _items(rest[4:]) if re.match(r"else\b", rest) else []
                items.append(("if", c[m.end():close], _items(body), els))
            else:
                items.extend(_items(body))
            continue
        c = re.sub(r"^(case\s+\w+|default)\s*:\s*", "", c.rstrip(";").strip())
        if c:
            items.append(c)


def _unwrap(c: str) -> str:
    c = c.strip()
    while c.startswith("(") and _paren_end(c, 0) == len(c) - 1:
        c = c[1:-1].strip()
    return c


def _resolver(text: str, plots_by_name: dict[str, dict], consts: dict):
    """action(statement) -> action dict, None (nothing to do) or ("skip", why), for one script
    (comments already stripped)."""
    objects = {}
    for var, ref in _OBJECT.findall(text):
        objects[var] = ref.strip('"') if ref.startswith('"') else consts.get(ref, ref)
    locations = {var: objects[obj] for var, obj in _LOCATION.findall(text) if obj in objects}
    helpers = {m.group(1): _block(text, m.end() - 1) for m in _HELPER.finditer(text)}
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

    def ambient_action(fn: str, args: list[str]):
        """Ambient_Start/StartTeam/StartTag(who, state, move, prefix, animation pattern, ...):
        value is the animation pattern (-1: start with the one it has), 0 for Ambient_Stop."""
        if fn == "Ambient_StartTeam":
            team = value(args[0]) if args else None
            target = f"team:{team}" if isinstance(team, int) else None
        elif fn == "Ambient_StartTag":
            known = args and (args[0].startswith('"') or isinstance(consts.get(args[0]), str))
            target = value(args[0]) if known else None
        else:
            target = obj(args[0]) if args else None
        if target is None:
            return ("skip", f"{fn}({args[0] if args else ''}): object only known at runtime")
        if fn == "Ambient_Stop":
            return {"kind": AMBIENT, "target": target, "arg": "", "value": 0}
        pattern = value(args[4]) if len(args) > 4 else 0
        if isinstance(pattern, str) and pattern.lstrip("-").isdigit():
            pattern = int(pattern)
        if not isinstance(pattern, int):
            return ("skip", f"{fn}: animation pattern {args[4]}")
        return {"kind": AMBIENT, "target": target, "arg": "", "value": pattern or -1}

    def action(stmt: str, depth: int = 0):
        a = _ASSIGN.match(stmt)
        if a:  # (re)assigning an object variable: later statements see the new object
            ref = a.group(2)
            objects[a.group(1)] = ref.strip('"') if ref.startswith('"') else consts.get(ref, ref)
            return None
        c = _CALL.match(stmt)
        if c and c.group(1) in helpers and not c.group(2).strip() and depth < 4:
            return [action(s, depth + 1) for s in _statements(helpers[c.group(1)])]  # inline a local helper
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
        if fn in ("Ambient_Start", "Ambient_StartTeam", "Ambient_StartTag", "Ambient_Stop"):
            return ambient_action(fn, args)
        if fn in ("UT_CombatStart", "SetGroupId", "KillCreature", "UT_ExitDestroy") and args \
                and obj(args[0]) is None:
            return ("skip", f"{fn}({args[0]}): object only known at runtime")
        if fn == "UT_CombatStart":
            return {"kind": HOSTILE, "target": obj(args[0]), "arg": "", "value": 1}
        if fn == "SetGroupId" and len(args) >= 2 and args[1] in _GROUPS:
            return {"kind": HOSTILE, "target": obj(args[0]), "arg": "", "value": _GROUPS[args[1]]}
        if fn == "UT_TeamGoesHostile" and args and isinstance(value(args[0]), int):
            return {"kind": HOSTILE, "target": f"team:{value(args[0])}", "arg": "", "value": 1}
        if fn == "KillCreature":
            return {"kind": KILL, "target": obj(args[0]), "arg": "", "value": 1}
        if fn == "UT_ExitDestroy":
            wp = value(args[2]) if len(args) > 2 else "generic_exit"
            return {"kind": EXIT, "target": obj(args[0]), "arg": str(wp),
                    "value": int(len(args) > 1 and value(args[1]) == 1)}
        if fn == "UT_DoAreaTransition" and len(args) >= 2:
            area, wp = value(args[0]), value(args[1])
            if not (isinstance(area, str) and isinstance(wp, str)) or area == args[0] or wp == args[1]:
                return ("skip", f"{fn}({args[0]}, {args[1]}): unknown area or waypoint")
            return {"kind": TRANSITION, "target": wp, "arg": area, "value": 1}
        if fn == "UT_QuickMoveObject" and len(args) >= 2 and args[0] in objects:
            return {"kind": WALK, "target": objects[args[0]], "arg": str(value(args[1])),
                    "value": int(len(args) > 2 and value(args[2]) == 1)}
        return ("skip", fn)

    flag_vars = {m.group(1): m.group(2)
                 for m in re.finditer(r"\bint\s+(\w+)\s*=\s*(WR_GetPlotFlag\s*\([^;]*\))\s*;", text)}

    def cond(c: str):
        """("GUID:FLAG", 1/0) when a condition only tests one plot flag, else None."""
        c = _unwrap(c)
        expected = True
        if c.startswith("!") and not c.startswith("!="):
            expected, c = False, _unwrap(c[1:])
        m = re.fullmatch(r"(.+?)\s*(==|!=)\s*(TRUE|FALSE)", c, re.S)
        if m:
            c = _unwrap(m.group(1))
            expected = expected == ((m.group(3) == "TRUE") == (m.group(2) == "=="))
        g = _GET_FLAG.fullmatch(flag_vars.get(c, c).strip())
        target = plots_by_name.get(g.group(1)[4:].lower()) if g else None
        fid = {n: f for f, n in target["flags"].items()}.get(g.group(2)) if target else None
        return None if fid is None else (f"{target['guid']}:{fid}", int(expected))

    action.cond = cond
    return action, value


def _statements(body: str) -> list[str]:
    return [s for s in (s.strip() for s in body.replace("{", ";").replace("}", ";").split(";")) if s]


def _collect(a, label: str, acts: list[dict], skipped: list[str]) -> None:
    """Add one action() result: an action, nothing, a skip, or a list of them (an inlined helper)."""
    if isinstance(a, list):
        for x in a:
            _collect(x, label, acts, skipped)
    elif isinstance(a, tuple):
        skipped.append(f"{label}: {a[1]}")
    elif a is not None:
        acts.append(a)


def _run(action, statements: list[str], label: str, skipped: list[str]) -> list[dict]:
    acts: list[dict] = []
    for stmt in statements:
        _collect(action(stmt), label, acts, skipped)
    return acts


def _emit(action, items: list, label: str, skipped: list[str]) -> list[dict]:
    """Actions for structured items. An `if` on one plot flag becomes an `if` action that
    skips the then-actions when the flag is not as tested (and a `skip` over the else);
    other conditions are not known here, so both branches run, as before."""
    acts: list[dict] = []
    for it in items:
        if isinstance(it, str):
            _collect(action(it), label, acts, skipped)
            continue
        _, condition, then_items, else_items = it
        ta = _emit(action, then_items, label, skipped)
        ea = _emit(action, else_items, label, skipped)
        c = action.cond(condition)
        if c is None:
            acts += ta + ea
            continue
        key, expected = c
        if ea:
            acts.append({"kind": COND, "target": str(expected), "arg": key, "value": len(ta) + 1})
            acts += ta
            acts.append({"kind": SKIP, "target": "", "arg": "", "value": len(ea)})
            acts += ea
        elif ta:
            acts.append({"kind": COND, "target": str(expected), "arg": key, "value": len(ta)})
            acts += ta
    return acts


def _run_text(action, text: str, label: str, skipped: list[str]) -> list[dict]:
    return _emit(action, _items(text), label, skipped)


def _drop_debug(text: str) -> str:
    """Keep the game's path of `if (nDebug == FALSE) {...} else {...}`: drop the else."""
    out, pos = [], 0
    for m in _DEBUG_ELSE.finditer(text):
        if m.start() < pos:
            continue
        end = m.end() - 1 + len(_block(text, m.end() - 1)) + 2  # past the closing brace
        e = re.match(r"\s*else\s*\{", text[end:])
        if e:
            out.append(text[pos:end])
            pos = end + e.end() - 1 + len(_block(text, end + e.end() - 1)) + 2
    out.append(text[pos:])
    return "".join(out)


def translate_events(script: str, plots_by_name: dict[str, dict], consts: dict, name: str = "") -> dict:
    """{"cases": {"death:<tag>" / "teamdead:<id>" / "load:<name>" / "enter:<name>": [action dicts]},
    "skipped": [...]} for a creature, area or trigger script called `name`."""
    text = _drop_debug(_COMMENTS.sub("", script))
    action, value = _resolver(text, plots_by_name, consts)
    cases: dict[str, list] = {}
    skipped: list[str] = []
    m = re.search(r"case\s+EVENT_TYPE_DEATH\s*:", text)
    if m:
        body = _block(text, m.end())
        for branch in re.finditer(r"if\s*\(\s*sTag\s*==\s*(\w+)\s*\)", body):
            tag = value(branch.group(1))
            label = f"death:{tag}"
            cases[label] = cases.get(label, []) + _run_text(action, _block(body, branch.end()), label, skipped)
    m = re.search(r"case\s+EVENT_TYPE_TEAM_DESTROYED\s*:", text)
    switch = m and re.search(r"switch\s*\(\s*nTeamID\s*\)", text[m.end():])
    if switch:
        for label, statements, _, raw in _cases(_block(text, m.end() + switch.end())):
            team = value(label)
            if not isinstance(team, int):
                skipped.append(f"team {label}: unknown team")
                continue
            cases[f"teamdead:{team}"] = _run_text(action, raw, f"teamdead:{team}", skipped)
    # The area's set-up once everything has loaded, and a trigger being walked into.
    for key, events in ((f"load:{name}", ("EVENT_TYPE_AREALOAD_PRELOADEXIT", "EVENT_TYPE_AREALOAD_POSTLOADEXIT")),
                        (f"enter:{name}", ("EVENT_TYPE_ENTER",))):
        for event in events:
            m = re.search(rf"case\s+{event}\s*:", text)
            if not m:
                continue
            statements = _statements(_block(text, m.end()))
            branches = [s for s in statements if re.match(r"(if|else|switch|while|for)\b", s)
                        and not re.match(r"if\s*\(\s*\w*(Once|Debug)\w*\s*==\s*FALSE\s*\)", s)
                        and not (s.startswith("if") and "(" in s
                                 and action.cond(s[s.index("(") + 1:s.rindex(")")]))]
            if key.startswith("load:") and branches:
                # what it does depends on the game's state; run unconditionally it would misplace people
                skipped.append(f"{key}: {event} branches on game state ({branches[0]}), left out")
                continue
            cases[key] = cases.get(key, []) + _run_text(action, _block(text, m.end()), key, skipped)
    return {"cases": cases, "skipped": skipped}


def translate(script: str, plot: dict, plots_by_name: dict[str, dict], consts: dict) -> dict:
    """{"cases": {flag name: [action dicts]}, "skipped": [...]} for one plot script."""
    text = _drop_debug(_COMMENTS.sub("", script))
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
    for label, statements, _, raw in cases:
        acts = _run_text(action, raw, label, skipped)
        if any(s.startswith(("if", "else", "while", "for")) for s in statements):
            skipped.append(f"{label}: has conditional logic (plot-flag tests kept, others run unconditionally)")
        own[label] = acts
    result = {}
    for i, (label, _, has_break, _raw) in enumerate(cases):
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


_GET_FLAG = re.compile(r"WR_GetPlotFlag\s*\(\s*(PLT_\w+)\s*,\s*(\w+)\s*(?:,\s*\w+\s*)?\)")
_FLAG_VAR = re.compile(r"^int\s+(\w+)\s*=\s*(WR_GetPlotFlag\s*\(.*\))$")
_BOOL_EXPR = re.compile(r"^[\w\s()!&|=]+$")


def _clauses(expr: str, names: list[str]) -> list[list[tuple[int, bool]]] | None:
    """The boolean expression over `names` as OR-of-AND clauses: [[(name index, negated)]],
    from its truth table with terms differing in one variable merged; None if it isn't one."""
    py = expr.replace("&&", " and ").replace("||", " or ")
    py = re.sub(r"==\s*TRUE\b", "== 1", py)
    py = re.sub(r"==\s*FALSE\b", "== 0", py)
    py = re.sub(r"!=\s*TRUE\b", "== 0", py)
    py = re.sub(r"!=\s*FALSE\b", "== 1", py)
    py = re.sub(r"!(?!=)", " not ", py)
    py = py.replace("TRUE", "1").replace("FALSE", "0")
    if set(re.findall(r"[A-Za-z_]\w*", py)) - set(names) - {"and", "or", "not"}:
        return None
    rows = []
    for bits in range(1 << len(names)):
        env = {n: (bits >> i) & 1 for i, n in enumerate(names)}
        try:
            if eval(py, {"__builtins__": {}}, env):  # only names, digits and boolean operators remain
                rows.append(tuple((bits >> i) & 1 for i in range(len(names))))
        except Exception:
            return None
    terms = {tuple(r) for r in rows}
    merged = True
    while merged:  # Quine-McCluskey style: merge terms that differ in one known variable
        merged, out, used = False, set(), set()
        terms_list = sorted(terms, key=str)
        for a in terms_list:
            for b in terms_list:
                diff = [i for i in range(len(a)) if a[i] != b[i]]
                if len(diff) == 1 and None not in (a[diff[0]], b[diff[0]]):
                    out.add(tuple(None if i == diff[0] else a[i] for i in range(len(a))))
                    used.update((a, b))
                    merged = True
        terms = out | (terms - used)
    return [[(i, v == 0) for i, v in enumerate(t) if v is not None] for t in sorted(terms, key=str)]


def translate_defined(script: str, plot: dict, plots_by_name: dict[str, dict]) -> dict:
    """A plot's defined flags (EVENT_TYPE_GET_PLOT cases) that are a boolean of other plot
    flags: {flag name: [[("GUID:FLAG", negated), ...], ...]}, OR of ANDs. Cases that look at
    anything else (injuries, items, local variables) are left out."""
    text = _COMMENTS.sub("", script)
    body = None
    m = re.search(r"EVENT_TYPE_GET_PLOT", text)
    if m:
        body = text[m.end():]
    else:  # if (nType == EVENT_TYPE_SET_PLOT) {...} else {GET handler}
        s = re.search(r"if\s*\(\s*nType\s*==\s*EVENT_TYPE_SET_PLOT\s*\)\s*\{", text)
        if s:
            end = s.end() - 1 + len(_block(text, s.end() - 1)) + 2
            e = re.match(r"\s*else\s*\{", text[end:])
            body = "{" + _block(text, end + e.end() - 1) + "}" if e else None
    switch = body and re.search(r"switch\s*\(\s*n(?:Bit)?Flag\s*\)", body)
    if not switch:
        return {}
    text, m = body, re.match("", body)

    def key(plt: str, flag: str):
        target = plots_by_name.get(plt[4:].lower())
        fid = {n: f for f, n in target["flags"].items()}.get(flag) if target else None
        return None if fid is None else f"{target['guid']}:{fid}"

    out = {}
    for label, statements, _, _raw in _cases(_block(text, m.end() + switch.end())):
        names, keys, expr = [], [], None
        ok = True
        for s in statements:
            v = _FLAG_VAR.match(s)
            if v:
                g = _GET_FLAG.fullmatch(v.group(2).strip())
                k = g and key(g.group(1), g.group(2))
                if not k:
                    ok = False
                    break
                names.append(v.group(1))
                keys.append(k)
                continue
            c = re.match(r"^if\s*\((.*)\)$", s, re.S)
            r = re.match(r"^nResult\s*=\s*(.*)$", s, re.S)
            if c and expr is None:
                expr = c.group(1)
            elif s in ("nResult = TRUE", "break"):
                continue
            elif r and expr is None:
                expr = r.group(1)
            else:
                ok = False
                break
        if not ok or expr is None:
            continue
        for g in _GET_FLAG.finditer(expr):  # inline WR_GetPlotFlag(...) in the condition
            k = key(g.group(1), g.group(2))
            if not k:
                ok = False
                break
            names.append(f"_f{len(names)}")
            keys.append(k)
            expr = expr.replace(g.group(0), names[-1], 1)
        if not ok or not _BOOL_EXPR.match(expr) or len(names) > 6:
            continue
        clauses = _clauses(expr, names)
        if clauses:
            out[label] = [[(keys[i], neg) for i, neg in clause] for clause in clauses]
    return out


def _matches(name: str, only: str) -> bool:
    """`only` is one or more name patterns separated by commas, e.g. "bhn*,gen00pt_party"."""
    return any(fnmatch.fnmatch(name.lower(), pattern.strip().lower()) for pattern in only.split(","))


def export(src_dir: str | Path, plots: dict[str, dict], only: str = "*", true_flags: list[str] | None = None) -> dict:
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
        if not any(e in text for e in ("EVENT_TYPE_DEATH", "EVENT_TYPE_TEAM_DESTROYED", "EVENT_TYPE_ENTER",
                                        "EVENT_TYPE_AREALOAD_PRELOADEXIT", "EVENT_TYPE_AREALOAD_POSTLOADEXIT")):
            continue
        t = translate_events(text, by_name, consts, path.stem)
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
    # Defined flags from every plot (conversations everywhere test them): one entry per clause.
    def_key, def_start, def_count, term_key, term_not = [], [], [], [], []
    defined = {}
    for guid, plot in sorted(plots.items(), key=lambda kv: kv[1]["name"]):
        path = Path(src_dir) / f"{plot.get('script') or ''}.nss"
        if not plot.get("script") or not path.exists():
            continue
        found = translate_defined(path.read_text(encoding="utf-8", errors="replace"), plot, by_name)
        flag_ids = {name: fid for fid, name in plot["flags"].items()}
        for label, clauses in found.items():
            if label not in flag_ids:
                continue
            defined[f"{plot['name']}.{label}"] = [" & ".join(("!" if n else "") + k for k, n in c) for c in clauses]
            for clause in clauses:
                def_key.append(f"{guid}:{flag_ids[label]}")
                def_start.append(len(term_key))
                def_count.append(len(clause))
                for k, n in clause:
                    term_key.append(k)
                    term_not.append(int(n))
    for k in true_flags or []:  # always true: a clause with no terms
        def_key.append(k)
        def_start.append(len(term_key))
        def_count.append(0)
    return {"Format": FORMAT, "Keys": keys, "Start": starts, "Count": counts, "Kind": kinds, "Target": targets,
            "Arg": args, "Value": values,
            "DefKey": def_key, "DefStart": def_start, "DefCount": def_count, "TermKey": term_key, "TermNot": term_not,
            "Plots": report, "Events": events, "Defined": defined}
