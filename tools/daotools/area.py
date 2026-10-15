"""Areas: where the walkable floor is and who stands where, for Unreal.

An area (.are, GFF3) places creatures, placeables and waypoints; its layout
(.arl, GFF4 "ARL ", loose under packages/core/env) holds a navigation grid.
From the two this builds a greybox the Unreal project spawns at runtime:
floor and wall boxes from the grid, and the creatures that have a
conversation or belong to a team (plot scripts show, hide and move teams), at
their places, plus every waypoint (where plot scripts move people) and every
door. Nothing here is a game model: floors come from the
walkable cells, walls either from the blocked cells or, with the layout's rooms,
from the level kit's collision boxes (kit.py), and doors are sized by kind
(see door_size).

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

from . import ambient

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


def placeable_templates(json_dir: str | Path) -> dict[str, dict]:
    """Every .utp dump under a pull folder, by template name (lower case)."""
    found = {}
    for p in sorted(Path(json_dir).rglob("*.utp.json")):
        found.setdefault(p.name[:-len(".utp.json")].lower(), json.loads(p.read_text(encoding="utf-8"))["root"])
    return found


def creature_templates(json_dir: str | Path) -> dict[str, dict]:
    """Every .utc dump under a pull folder, by template name (lower case)."""
    found = {}
    for p in sorted(Path(json_dir).rglob("*.utc.json")):
        found.setdefault(p.name[:-len(".utc.json")].lower(), json.loads(p.read_text(encoding="utf-8"))["root"])
    return found


def _axes(b: list[float]):
    xa, za = b[6:9], b[9:12]
    ya = (za[1] * xa[2] - za[2] * xa[1], za[2] * xa[0] - za[0] * xa[2], za[0] * xa[1] - za[1] * xa[0])
    return xa, ya, za


def _inside(b: list[float], p) -> bool:
    d = [p[k] - b[k] for k in range(3)]
    return all(abs(sum(d[k] * ax[k] for k in range(3))) <= b[3 + j] for j, ax in enumerate(_axes(b)))


def _bottom(b: list[float]) -> float:
    return b[2] - sum(abs(ax[2]) * b[3 + j] for j, ax in enumerate(_axes(b)))


def drop_hanging(solids: list[float], nav: dict, above: float = 100.0) -> tuple[list[float], int]:
    """Drop props (kind 1) whose box starts more than `above` cm over the floor
    under it: lamps, banners, wall displays, shelves' contents. You walk under them,
    and as greybox they only look like boxes floating in the room."""
    w, h, cell = nav[NAV_WIDTH], nav[NAV_HEIGHT], nav[NAV_CELL]
    ox, oy = nav[NAV_ORIGIN][0], nav[NAV_ORIGIN][1]
    cls, fz = nav[NAV_CLASS], nav[NAV_FLOOR_Z]

    def floor_under(x: float, y: float, z: float) -> float | None:
        gi, gj = int((x / 100 - ox) / cell), int((-y / 100 - oy) / cell)
        best = None
        for j in range(gj - 2, gj + 3):
            for i in range(gi - 2, gi + 3):
                if 0 <= i < w and 0 <= j < h and cls[j * w + i] >= 0:
                    f = fz[j * w + i] / 16 * 100
                    if f <= z + 50 and (best is None or f > best):
                        best = f
        return best

    out: list[float] = []
    dropped = 0
    for i in range(0, len(solids), 13):
        b = solids[i:i + 13]
        if b[12] == 1:
            bottom = _bottom(b)
            floor = floor_under(b[0], b[1], bottom)
            if floor is None or bottom - floor > above:
                dropped += 1
                continue
        out += b
    return out, dropped


MAX_FRAME = 260.0  # cm


def frame_doors(door_pose: list[float], door_size: list[float], solids: list[float]) -> tuple[list[float], int]:
    """Wall boxes that close the rest of each doorway. Measured at 1.5 m up, along
    the door's width (its local Y), from the door's centre to the nearest wall or
    blocker on each side: where the gap is wider than the door (the frame pieces
    have no collision at walking height), the space between the door's edges and the
    walls is filled up to the lintel (or 4 m). Doors standing inside a wall piece
    (cut_doorways opens those) are left alone, and so is any side wider than
    MAX_FRAME: there the door stands beside a corridor or an open room, not in a
    wall."""
    walls = [solids[i:i + 13] for i in range(0, len(solids), 13) if solids[i + 12] in (0, 2)]
    out: list[float] = []
    framed = 0
    for d in range(len(door_pose) // 4):
        x, y, z, yaw = door_pose[d * 4:d * 4 + 4]
        width = door_size[d * 2]
        r = math.radians(yaw)
        side = (-math.sin(r), math.cos(r))
        fwd = (math.cos(r), math.sin(r))
        near = [b for b in walls if abs(b[0] - x) < 1200 and abs(b[1] - y) < 1200]

        def hit(t: float, up: float = 150.0) -> bool:
            return any(_inside(b, (x + side[0] * t, y + side[1] * t, z + up)) for b in near)

        if hit(0):
            continue
        lo = next((-t for t in range(5, 805, 5) if hit(-t)), None)
        hi = next((t for t in range(5, 805, 5) if hit(t)), None)
        if lo is None or hi is None:
            continue
        top = next((u for u in range(int(door_size[d * 2 + 1]), 800, 10) if hit(0, u)), 400)
        for a, b in ((lo, -width / 2), (width / 2, hi)):
            if 5 < b - a <= MAX_FRAME:
                mid = (a + b) / 2
                out += [round(x + side[0] * mid, 1), round(y + side[1] * mid, 1), round(z + top / 2, 1),
                        20.0, round((b - a) / 2, 1), round(top / 2, 1),
                        round(fwd[0], 4), round(fwd[1], 4), 0.0, 0.0, 0.0, 1.0, 0]
                framed += 1
    return out, framed


def cut_doorways(solids: list[float], doors: list[tuple[list[float], float]]) -> tuple[list[float], int]:
    """Split wall boxes (kind 0, 13 numbers each, see kit.solids) that a door stands
    in, so the doorway stays open: the wall is cut along its longer horizontal side
    around the door (door position in Unreal cm, half width in cm). Some doors sit
    inside an outer-wall piece whose collision covers the opening."""
    out: list[float] = []
    cuts = 0
    for i in range(0, len(solids), 13):
        b = solids[i:i + 13]
        c, half, xa, za = b[0:3], b[3:6], b[6:9], b[9:12]
        ya = (za[1] * xa[2] - za[2] * xa[1], za[2] * xa[0] - za[0] * xa[2], za[0] * xa[1] - za[1] * xa[0])
        axes = (xa, ya, za)
        pieces = [b]
        for pos, door_half in doors if b[12] == 0 else []:
            p = (pos[0], pos[1], pos[2] + 100)  # 1 m above the door's base
            d = [p[k] - c[k] for k in range(3)]
            local = [sum(d[k] * ax[k] for k in range(3)) for ax in axes]
            if not all(abs(local[j]) <= half[j] for j in range(3)):
                continue
            # the box's longer horizontal axis (smallest vertical component, larger half extent)
            j = max((0, 1, 2), key=lambda a: (abs(axes[a][2]) < 0.5, half[a]))
            lo, hi = -half[j], half[j]
            gap_lo, gap_hi = local[j] - door_half - 10, local[j] + door_half + 10
            pieces = []
            for a, z in ((lo, gap_lo), (gap_hi, hi)):
                if z - a > 1:
                    mid = (a + z) / 2
                    nh = list(half)
                    nh[j] = (z - a) / 2
                    nc = [round(c[k] + axes[j][k] * mid, 1) for k in range(3)]
                    pieces.append([*nc, *(round(h, 1) for h in nh), *xa, *za, b[12]])
            cuts += 1
            break
        for piece in pieces:
            out += piece
    return out, cuts


def area(are_root: dict, layout_root: dict, templates: dict[str, dict], *, start: str = "",
         solids: dict | None = None, door_models: dict[str, tuple[float, float, float]] | None = None,
         creature_stats=None, player: dict | None = None, ambient_tables: dict | None = None) -> dict:
    """The runtime area file. `solids` (kit.solids, from the layout's rooms) replaces
    the navigation grid's walls with the level kit's walls, props and blockers.
    `creature_stats` (utc -> stats.stats() dict) and `player` add the game's combat
    numbers (see stats.py). `ambient_tables` (ambient.load_tables) adds what each
    creature does on its own (see ambient.py); creatures with ambient behaviour are
    kept even without a conversation or team.
    `door_models` (template -> the door model's min and max along its width and its
    height, metres; see kit.door_models) places and sizes doors like the game: the
    door's origin is its hinge and the panel runs along its local X."""
    warnings: list[str] = []
    npc_tags, npc_names, npc_convs, npc_female, npc_pose, npc_active = [], [], [], [], [], []
    npc_team, npc_scale, npc_hostile, npc_rank = [], [], [], []
    npc_health, npc_attack, npc_defense, npc_damage, npc_dscale = [], [], [], [], []
    npc_ambient, npc_ambient_prefix = [], []
    others = 0
    for c in are_root.get("CreatureList") or []:
        utc = templates.get(str(c.get("TemplateResRef", "")).lower())
        if utc is None:
            warnings.append(f"creature {c.get('Tag')}: template {c.get('TemplateResRef')} not found")
            continue
        conversation = utc.get("DialogResRef") or ""
        team = int(c.get("TeamId", NO_TEAM))
        amb = ambient.settings(ambient.variables(utc, c), c.get("Tag") or "")
        if not conversation and team == NO_TEAM and not (ambient_tables and amb["State"] & ambient.ENABLED):
            others += 1
            continue
        npc_ambient.extend([amb["State"], amb["Move"], amb["Pattern"], amb["Freq"]])
        npc_ambient_prefix.append(amb["Prefix"])
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
        if creature_stats is not None:  # stats.stats() for this template (see the CLI)
            st = creature_stats(utc)
            npc_health.append(st["Health"])
            npc_attack.append(st["Attack"])
            npc_defense.append(st["Defense"])
            npc_damage.extend(st["Damage"])
            npc_dscale.append(st["DamageScale"])
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
        model = (door_models or {}).get(template.lower())
        if model:
            lo, hi, height = model
            yaw = math.radians(door_pose[-1])
            # the game's local X is the actor's +Y in Unreal; centre the panel between lo and hi
            mid = (lo + hi) / 2 * 100
            door_pose[-4] = round(door_pose[-4] - math.sin(yaw) * mid, 1)
            door_pose[-3] = round(door_pose[-3] + math.cos(yaw) * mid, 1)
            door_size_wh.extend((round((hi - lo) * 100, 1), round(height * 100, 1)))
        else:
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

    # Ambient destinations: [first, count] per creature into a flat list of waypoint indices.
    amb_dest, npc_amb_dest = [], []
    for prefix in npc_ambient_prefix:
        found = ambient.destinations(prefix, wp_tags)
        npc_amb_dest.extend([len(amb_dest), len(found)])
        amb_dest.extend(found)
    amb_patterns, amb_actions = ambient.pattern_table(ambient_tables) if ambient_tables else ([], [])

    boxes = floor_plan(navigation(layout_root))
    solid_boxes, cut, dropped, fitted = [], 0, 0, 0
    if solids is not None:
        boxes = [v for i in range(0, len(boxes), 7) if boxes[i + 6] == 0 for v in boxes[i:i + 7]]  # floors only
        solid_boxes, dropped = drop_hanging(solids["Solids"], navigation(layout_root))
        doors = [(door_pose[i * 4:i * 4 + 3], door_size_wh[i * 2] / 2) for i in range(len(door_tags))]
        solid_boxes, cut = cut_doorways(solid_boxes, doors)
        frames, fitted = frame_doors(door_pose, door_size_wh, solid_boxes)
        solid_boxes += frames
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
        "NpcHealth": npc_health,
        "NpcAttack": npc_attack,
        "NpcDefense": npc_defense,
        "NpcDamage": npc_damage,
        "NpcDamageScale": npc_dscale,
        "Player": player or {},
        # Flat for Blueprint: health, attack, defense, damage min and max, damage scaling threshold.
        "PlayerStats": ([player["Health"], player["Attack"], player["Defense"], *player["Damage"],
                         player["DamageThreshold"]] if player else []),
        # Per creature: ambient state flags, move pattern, animation pattern, animation frequency.
        "NpcAmbient": npc_ambient if ambient_tables else [],
        "NpcAmbientDest": npc_amb_dest if ambient_tables else [],
        "AmbientDest": amb_dest if ambient_tables else [],
        # [pattern, first action, count] and [action, seconds]; see ambient.ACTIONS.
        "AmbientPatterns": amb_patterns,
        "AmbientActions": amb_actions,
        "WaypointTags": wp_tags,
        "WaypointPose": wp_pose,
        "DoorTags": door_tags,
        "DoorPose": door_pose,
        "DoorState": door_state,
        "DoorSize": door_size_wh,
        "DoorActive": door_active,
        "Solids": solid_boxes,
        "Labels": labels,
        "LabelPos": label_pos,
        "Summary": {"Floors": sum(1 for k in boxes[6::7] if k == 0), "Walls": sum(1 for k in boxes[6::7] if k == 1),
                    "TalkingCreatures": sum(1 for c in npc_convs if c), "TeamOnly": sum(1 for c, t in zip(npc_convs, npc_team) if not c and t != NO_TEAM),
                    "Ambient": sum(1 for f in npc_ambient[0::4] if int(f) & ambient.ENABLED) if ambient_tables else 0,
                    "Teams": len({t for t in npc_team if t != NO_TEAM}),
                    "Inactive": npc_active.count(0), "OtherCreatures": others,
                    "Waypoints": len(wp_tags), "Doors": len(door_tags),
                    "Solids": len(solid_boxes) // 13, "DoorwaysCut": cut,
                    "HangingPropsDropped": dropped, "DoorFrames": fitted},
        "Warnings": warnings,
    }
