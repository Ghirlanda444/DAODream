"""Ambient behaviour: what castle folk do while nobody talks to them.

A port of the data side of sys_ambient_h. A creature's local variables
(template VarTable, overridden by the area's instance) switch the system on
(AMBIENT_SYSTEM_STATE bit 1) and pick a movement pattern between waypoints
(AMBIENT_MOVE_PATTERN, AMBIENT_MOVE_PREFIX) and an animation pattern
(AMBIENT_ANIM_PATTERN, a row of ambient_anim_patterns.gda: up to twelve actions
written animation.loops, with anim_base.gda naming each animation).

The remake has none of the game's animations, so each one becomes one of a
few poses the mannequin can strike (ACTIONS below), chosen by the animation's
name. The creature then alternates, as in the game, between a move phase and an
animation phase.
"""

from __future__ import annotations

from pathlib import Path

from .erf import ERF
from .gda import GDA
from .gff4 import GFF4

ENABLED = 0x01  # AMBIENT_SYSTEM_ENABLED
# AMBIENT_MOVE_*: none, patrol, loop, warp, random, wander (10 m), wander far (30 m), path patrol, path loop, once
MOVE_NONE, MOVE_PATROL, MOVE_LOOP, MOVE_WARP, MOVE_RANDOM, MOVE_WANDER, MOVE_WANDER_FAR = 0, 1, 2, 3, 4, 5, 6
MOVE_PATH_PATROL, MOVE_PATH_LOOP, MOVE_ONCE = 7, 8, 9
FREQ_ORDERED = -1.0  # AMBIENT_ANIM_FREQ_ORDERED: play the whole pattern in order
LOOP_FOREVER = 90  # AMBIENT_LOOP_FOREVER: more loops than this hold the pose until something else happens

# What the mannequin does for an animation.
IDLE, FIDGET, LOOK_LEFT, LOOK_RIGHT, GESTURE, KNEEL, COWER, LEAN, BEND = range(9)
ACTIONS = {IDLE: "idle", FIDGET: "fidget", LOOK_LEFT: "look left", LOOK_RIGHT: "look right", GESTURE: "gesture",
           KNEEL: "kneel", COWER: "cower", LEAN: "lean", BEND: "bend"}
# By the animation's name (anim_base AnimName), first match wins.
_BY_NAME = [
    ("wanderwest", LOOK_LEFT), ("wandereast", LOOK_RIGHT), ("lookleft", LOOK_LEFT), ("lookright", LOOK_RIGHT),
    ("pry", KNEEL), ("pray", KNEEL), ("kneel", KNEEL), ("crouch", KNEEL), ("sitground", KNEEL), ("sleep", KNEEL),
    ("scared", COWER), ("cower", COWER), ("weep", COWER), ("writh", COWER),
    ("door_push", LEAN), ("lean", LEAN), ("table", LEAN),
    ("pickup", BEND), ("brows", BEND), ("rummag", BEND), ("clean", BEND), ("customer", BEND),
    ("_tk_", GESTURE), ("point", GESTURE), ("beckon", GESTURE), ("bless", GESTURE), ("salute", GESTURE),
    ("twitch", FIDGET), ("wipe", FIDGET), ("headache", FIDGET), ("nails", FIDGET), ("lost", FIDGET),
    ("scratch", FIDGET), ("stretch", FIDGET),
]
SECONDS_PER_LOOP = 2.5  # the game's ambient loops run a couple of seconds each
ONE_SHOT = 2.5  # a non-looping animation
HOLD = -1.0  # seconds for a pose held until the pattern changes


def load_tables(game_dir: str | Path) -> dict[str, dict[int, dict]]:
    """ambient_anim_patterns and anim_base, by row ID."""
    cols = ["ID", "label", "NoPlayNext", "ActionTotal"] + [f"Action{i}" for i in range(12)]
    with ERF.open(Path(game_dir) / "packages" / "core" / "data" / "2da.erf") as erf:
        patterns = {r["ID"]: r for r in GDA(GFF4(erf.read("ambient_anim_patterns.gda")), cols).records()}
        anims = {r["ID"]: r for r in GDA(GFF4(erf.read("anim_base.gda")), ["ID", "AnimName"]).records()}
    return {"patterns": patterns, "anims": anims}


def classify(anim_name: str) -> int:
    name = (anim_name or "").lower()
    for key, action in _BY_NAME:
        if key in name:
            return action
    return IDLE


def actions(pattern: dict, anims: dict[int, dict]) -> list[tuple[int, float]]:
    """(action, seconds) for each action of a pattern row, in order. Animation 1 is a
    pause of `loops` seconds; HOLD (-1) keeps the pose."""
    out = []
    for i in range(int(pattern.get("ActionTotal") or 0)):
        f = float(pattern.get(f"Action{i}") or 0.0)
        if f <= 0.0:  # a placeable interaction, which the castle's patterns don't use
            continue
        anim = int(f)
        loops = int(round((f - anim) * 100))
        if anim == 1:
            out.append((IDLE, float(max(1, loops))))
            continue
        seconds = HOLD if loops >= LOOP_FOREVER else loops * SECONDS_PER_LOOP if loops else ONE_SHOT
        out.append((classify(anims.get(anim, {}).get("AnimName", "")), seconds))
    return out


def variables(template: dict, instance: dict | None = None) -> dict[str, object]:
    """A creature's local variables: the template's, overridden by the area instance's."""
    out = {}
    for src in (template, instance or {}):
        for v in src.get("VarTable") or []:
            if v.get("Name"):
                out[v["Name"]] = v.get("Value")
    return out


def settings(local: dict, tag: str) -> dict:
    """The ambient settings a creature starts with."""
    return {"State": int(local.get("AMBIENT_SYSTEM_STATE") or 0),
            "Move": int(local.get("AMBIENT_MOVE_PATTERN") or 0),
            "Prefix": str(local.get("AMBIENT_MOVE_PREFIX") or "").replace("<tag>", tag),
            "Pattern": int(local.get("AMBIENT_ANIM_PATTERN") or 0),
            "Freq": float(local.get("AMBIENT_ANIM_FREQ") if local.get("AMBIENT_ANIM_FREQ") is not None
                          else FREQ_ORDERED)}


def destinations(prefix: str, waypoint_tags: list[str]) -> list[int]:
    """Indices into the area's waypoints a creature walks between: <prefix>_01,
    <prefix>_02, ... in order, else every waypoint tagged <prefix>
    (Ambient_GetDestinations)."""
    if not prefix:
        return []
    lower = [t.lower() for t in waypoint_tags]
    found = []
    n = 1
    while f"{prefix}_{n:02d}".lower() in lower:
        found.append(lower.index(f"{prefix}_{n:02d}".lower()))
        n += 1
    return found or [i for i, t in enumerate(lower) if t == prefix.lower()]


def pattern_table(tables: dict) -> tuple[list[float], list[float]]:
    """Every pattern with actions, flat for Blueprint: [id, first action, action count]
    per pattern, and [action, seconds] per action."""
    index, flat = [], []
    for pid in sorted(tables["patterns"]):
        acts = actions(tables["patterns"][pid], tables["anims"])
        if not acts:
            continue
        index.extend([float(pid), float(len(flat) // 2), float(len(acts))])
        for a, s in acts:
            flat.extend([float(a), s])
    return index, flat
