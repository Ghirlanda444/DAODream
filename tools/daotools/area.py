"""Areas: where the walkable floor is and who stands where, for Unreal.

An area (.are, GFF3) places creatures, placeables and waypoints; its layout
(.arl, GFF4 "ARL ", loose under packages/core/env) holds a navigation grid.
From the two this builds a greybox the Unreal project spawns at runtime:
floor and wall boxes from the grid, and the creatures that have a
conversation or belong to a team (plot scripts show, hide and move teams), at
their places, plus every waypoint (where plot scripts move people) and every
door. Nothing here is a game model: the boxes come from the
walkable/blocked cells, and doors are sized by kind (see door_size).

Navigation grid (field IDs observed on hrt201d, Castle Cousland):
3086/3087 width/height in cells, 3088 cell size (m), 3090 origin (m),
3093 floor height per cell in 1/16 m, 3114 cell class (-1 blocked, >= 0
walkable). Cells are row-major, rows along +Y. One height per cell.

Coordinates: the game is right-handed Z-up in metres with yaw 0 facing +Y.
Unreal is left-handed Z-up in centimetres with yaw 0 facing +X, so
x' = 100 x, y' = -100 y, z' = 100 z and yaw' = -(yaw + 90).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

FORMAT = "DAODream.Area 1"
WALL_HEIGHT = 3.0  # m above the highest neighbouring floor
FLOOR_THICKNESS = 0.2  # m
RACE_DWARF, RACE_ANIMAL = 1, 5  # RACE_* in the game's constants; 3 is human
RANK_CRITTER = 1  # CREATURE_RANK_*
GROUP_HOSTILE, GROUP_HOSTILE_ON_GROUND = 1, 36  # GROUP_*
NO_TEAM = -1

# Navigation grid fields.
NAV_WIDTH, NAV_HEIGHT, NAV_CELL, NAV_ORIGIN = "3086", "3087", "3088", "3090"
NAV_FLOOR_Z, NAV_CLASS = "3093", "3114"


def ue_point(x: float, y: float, z: float) -> tuple[float, float, float]:
    return round(x * 100, 1), round(-y * 100, 1), round(z * 100, 1)


def ue_yaw(qx: float, qy: float, qz: float, qw: float) -> float:
    """Unreal yaw (degrees) for a game orientation quaternion."""
    yaw = math.degrees(math.atan2(2 * (qw * qz + qx * qy), 1 - 2 * (qy * qy + qz * qz)))
    return round((-(yaw + 90) + 180) % 360 - 180, 1)


def navigation(layout_root: dict) -> dict:
    """The navigation grid struct from an .arl dump (`daotools gff dump`)."""
    for value in layout_root.values():
        if isinstance(value, dict):
            for inner in value.values():
                if isinstance(inner, dict) and inner.get("_struct") == "NAVI":
                    return inner
    raise ValueError("no navigation grid (NAVI) in this layout")


def _runs(width: int, height: int, key) -> list[tuple[int, int, int, int, object]]:
    """Merge cells with the same key into rectangles: (i0, j0, i1, j1, key),
    end-exclusive. Cells whose key is None are skipped."""
    open_runs: dict[tuple[int, int, object], list[int]] = {}
    rects = []
    for j in range(height):
        row_runs = []
        i = 0
        while i < width:
            k = key(i, j)
            if k is None:
                i += 1
                continue
            start = i
            while i < width and key(i, j) == k:
                i += 1
            row_runs.append((start, i, k))
        current = {}
        for start, end, k in row_runs:
            prev = open_runs.pop((start, end, k), None)
            current[(start, end, k)] = prev if prev is not None else [j]
        for (start, end, k), (j0,) in open_runs.items():
            rects.append((start, j0, end, j, k))
        open_runs = current
    for (start, end, k), (j0,) in open_runs.items():
        rects.append((start, j0, end, height, k))
    return rects


def floor_plan(nav: dict) -> list[float]:
    """Boxes as a flat list, 7 numbers each: x0, y0, z0, x1, y1, z1 (Unreal cm)
    and kind (0 floor, 1 wall)."""
    w, h, cell = nav[NAV_WIDTH], nav[NAV_HEIGHT], nav[NAV_CELL]
    ox, oy = nav[NAV_ORIGIN][0], nav[NAV_ORIGIN][1]
    cls, fz = nav[NAV_CLASS], nav[NAV_FLOOR_Z]

    def walkable(i, j):
        return 0 <= i < w and 0 <= j < h and cls[j * w + i] >= 0

    def floor_key(i, j):
        return fz[j * w + i] if walkable(i, j) else None

    def wall_key(i, j):
        if walkable(i, j):
            return None
        near = [fz[b * w + a] for a, b in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)) if walkable(a, b)]
        return (min(near), max(near)) if near else None

    boxes: list[float] = []

    def add(i0, j0, i1, j1, z0, z1, kind):
        x0, y0 = ox + i0 * cell, oy + j0 * cell
        x1, y1 = ox + i1 * cell, oy + j1 * cell
        a, b = ue_point(x0, y1, z0), ue_point(x1, y0, z1)  # the Y flip swaps the ends
        boxes.extend([a[0], a[1], a[2], b[0], b[1], b[2], kind])

    for i0, j0, i1, j1, z in _runs(w, h, floor_key):
        add(i0, j0, i1, j1, z / 16 - FLOOR_THICKNESS, z / 16, 0)
    for i0, j0, i1, j1, (lo, hi) in _runs(w, h, wall_key):
        add(i0, j0, i1, j1, lo / 16 - FLOOR_THICKNESS, hi / 16 + WALL_HEIGHT, 1)
    return boxes


# Door states (PLC_STATE_DOOR_* in the game's constants).
DOOR_CLOSED, DOOR_LOCKED, DOOR_OPEN, DOOR_BROKEN, DOOR_OPEN_2, DOOR_BROKEN_2 = range(6)


def is_door(tag: str, template: str) -> bool:
    name = f"{tag} {template}".lower()
    return "door" in name or "_dr_" in name


def door_size(template: str) -> tuple[float, float]:
    """Width and height (Unreal cm) for a greybox door. The templates only name a
    model, and the navigation grid is too coarse to show the doorway, so small
    doors (`sm`, the pantry) are 1.6 x 2.6 m and all others 3 x 3.6 m."""
    name = template.lower()
    return (160.0, 260.0) if "_sm_" in name or "pantry" in name else (300.0, 360.0)


def _text(value) -> str:
    if isinstance(value, dict):
        return value.get("text") or ""
    return value if isinstance(value, str) else ""


def creature_templates(json_dir: str | Path) -> dict[str, dict]:
    """Every .utc dump under a pull folder, by template name (lower case)."""
    found = {}
    for p in sorted(Path(json_dir).rglob("*.utc.json")):
        found.setdefault(p.name[:-len(".utc.json")].lower(), json.loads(p.read_text(encoding="utf-8"))["root"])
    return found


def area(are_root: dict, layout_root: dict, templates: dict[str, dict], *, start: str = "") -> dict:
    """The runtime area file."""
    warnings: list[str] = []
    npc_tags, npc_names, npc_convs, npc_female, npc_pose, npc_active = [], [], [], [], [], []
    npc_team, npc_scale, npc_hostile, npc_rank = [], [], [], []
    others = 0
    for c in are_root.get("CreatureList") or []:
        utc = templates.get(str(c.get("TemplateResRef", "")).lower())
        if utc is None:
            warnings.append(f"creature {c.get('Tag')}: template {c.get('TemplateResRef')} not found")
            continue
        conversation = utc.get("DialogResRef") or ""
        team = int(c.get("TeamId", NO_TEAM))
        if not conversation and team == NO_TEAM:
            others += 1
            continue
        look = utc.get("Appearance Data") if isinstance(utc.get("Appearance Data"), dict) else {}
        npc_tags.append(c.get("Tag") or "")
        npc_names.append(_text(utc.get("LocName")))
        npc_convs.append(conversation.lower())
        npc_female.append(1 if look.get("Gender") == 2 else 0)
        npc_active.append(1 if c.get("Active") else 0)  # inactive ones wait for a plot to show them
        npc_team.append(team)
        # Greybox stand-ins: a mannequin, smaller for dwarves and animals (critters such as
        # giant rats smallest, other animals such as the mabari bigger).
        race, rank = utc.get("Race"), int(utc.get("Rank") or 0)
        npc_scale.append((0.35 if rank == RANK_CRITTER else 0.6) if race == RACE_ANIMAL
                         else 0.8 if race == RACE_DWARF else 1.0)
        npc_hostile.append(1 if utc.get("GroupId") in (GROUP_HOSTILE, GROUP_HOSTILE_ON_GROUND) else 0)
        npc_rank.append(rank)
        npc_pose.extend([*ue_point(c["XPosition"], c["YPosition"], c["ZPosition"]),
                         ue_yaw(c["XOrientation"], c["YOrientation"], c["ZOrientation"], c["WOrientation"])])

    door_tags, door_pose, door_state, door_size_wh, door_active = [], [], [], [], []
    for d in are_root.get("PlaceableList") or []:
        template = str(d.get("TemplateResRef") or "")
        if not is_door(d.get("Tag") or "", template):
            continue
        door_tags.append(d.get("Tag") or "")
        door_pose.extend([*ue_point(d["XPosition"], d["YPosition"], d["ZPosition"]),
                          ue_yaw(d["XOrientation"], d["YOrientation"], d["ZOrientation"], d["WOrientation"])])
        door_state.append(int(d.get("InitialState") or 0))
        door_size_wh.extend(door_size(template))
        door_active.append(1 if d.get("Active") else 0)

    labels, label_pos = [], []
    wp_tags, wp_pose = [], []
    start_pose: list[float] = []
    for wp in are_root.get("WaypointList") or []:
        pos = ue_point(wp["XPosition"], wp["YPosition"], wp["ZPosition"])
        pose = [*pos, ue_yaw(wp["XOrientation"], wp["YOrientation"], wp["ZOrientation"], wp["WOrientation"])]
        wp_tags.append(wp.get("Tag") or "")
        wp_pose.extend(pose)
        if wp.get("Tag") == start:
            start_pose = pose
        if wp.get("HasMapNote") and _text(wp.get("MapNote")):
            labels.append(_text(wp.get("MapNote")))
            label_pos.extend(pos)
    if start and not start_pose:
        warnings.append(f"start waypoint {start} not found")

    boxes = floor_plan(navigation(layout_root))
    return {
        "Format": FORMAT,
        "Area": are_root.get("Tag") or "",
        "Layout": are_root.get("Layout") or "",
        "Start": start_pose,
        "Boxes": boxes,
        "NpcTags": npc_tags,
        "NpcNames": npc_names,
        "NpcConversations": npc_convs,
        "NpcFemale": npc_female,
        "NpcPose": npc_pose,
        "NpcActive": npc_active,
        "NpcTeam": npc_team,
        "NpcScale": npc_scale,
        "NpcHostile": npc_hostile,
        "NpcRank": npc_rank,
        "WaypointTags": wp_tags,
        "WaypointPose": wp_pose,
        "DoorTags": door_tags,
        "DoorPose": door_pose,
        "DoorState": door_state,
        "DoorSize": door_size_wh,
        "DoorActive": door_active,
        "Labels": labels,
        "LabelPos": label_pos,
        "Summary": {"Floors": sum(1 for k in boxes[6::7] if k == 0), "Walls": sum(1 for k in boxes[6::7] if k == 1),
                    "TalkingCreatures": sum(1 for c in npc_convs if c), "TeamOnly": sum(1 for c in npc_convs if not c),
                    "Teams": len({t for t in npc_team if t != NO_TEAM}),
                    "Inactive": npc_active.count(0), "OtherCreatures": others,
                    "Waypoints": len(wp_tags), "Doors": len(door_tags)},
        "Warnings": warnings,
    }
