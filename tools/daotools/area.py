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
import hashlib
from pathlib import Path

from . import ambient

FORMAT = "DAODream.Area 1"
WALL_HEIGHT = 3.0  # m above the highest neighbouring floor
FLOOR_THICKNESS = 0.2  # m
RACE_DWARF, RACE_HUMAN, RACE_ANIMAL = 1, 3, 5  # RACE_* in the game's constants (2 is elf)
CROWD_FACES = {"m": 6, "f": 2}  # generic MetaHuman faces for humans without a look of their own
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


FLOOR_FILL_CELLS = 6  # blocked cells within 3 m of the floor get floor under them too


def _filled_floor(nav: dict, fill: int = FLOOR_FILL_CELLS) -> list:
    """Floor height per cell (1/16 m), or None: walkable cells keep theirs, and blocked
    cells up to FLOOR_FILL_CELLS from the floor take their lowest walkable neighbour's.
    Blocked cells are under walls, furniture and door frames; when the level kit has no
    solid there (a dropped prop, a cut doorway) the player would otherwise fall through."""
    w, h = nav[NAV_WIDTH], nav[NAV_HEIGHT]
    cls, fz = nav[NAV_CLASS], nav[NAV_FLOOR_Z]
    filled = [fz[k] if cls[k] >= 0 else None for k in range(w * h)]
    for _ in range(fill):
        ring = {}
        for j in range(h):
            for i in range(w):
                if filled[j * w + i] is not None:
                    continue
                near = [filled[b * w + a] for a, b in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1))
                        if 0 <= a < w and 0 <= b < h and filled[b * w + a] is not None]
                if near:
                    ring[j * w + i] = min(near)
        if not ring:
            break
        for k, z in ring.items():
            filled[k] = z
    return filled


def floor_plan(nav: dict, fill: int = FLOOR_FILL_CELLS) -> list[float]:
    """Boxes as a flat list, 7 numbers each: x0, y0, z0, x1, y1, z1 (Unreal cm)
    and kind (0 floor, 1 wall). Floors also cover blocked cells near the floor
    (see _filled_floor)."""
    w, h, cell = nav[NAV_WIDTH], nav[NAV_HEIGHT], nav[NAV_CELL]
    ox, oy = nav[NAV_ORIGIN][0], nav[NAV_ORIGIN][1]
    cls, fz = nav[NAV_CLASS], nav[NAV_FLOOR_Z]
    filled = _filled_floor(nav, fill)

    def walkable(i, j):
        return 0 <= i < w and 0 <= j < h and cls[j * w + i] >= 0

    def floor_key(i, j):
        return filled[j * w + i] if 0 <= i < w and 0 <= j < h else None

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


CHILD_SCALE = 0.67  # children (head morphs kn_*) stand about 120 cm against the 180 cm mannequin


def stand_in_scale(race, rank: int, morph: str) -> float:
    """Scale of a creature's greybox stand-in (and the MetaHuman look that follows it): smaller for
    dwarves, children and animals (critters such as giant rats smallest, others such as the mabari bigger)."""
    if race == RACE_ANIMAL:
        return 0.35 if rank == RANK_CRITTER else 0.6
    if race == RACE_DWARF:
        return 0.8
    return CHILD_SCALE if morph.startswith("kn_") else 1.0


def look_keys(look: dict, race, tag: str) -> tuple[str, str]:
    """(head morph name, crowd face key) for a creature's MetaHuman look. Crowd faces go to adult
    humans only (children's heads are kn_*); the key is a stable hash of the tag and position, so a
    guard keeps his face between runs, and guards sharing a tag still get different faces."""
    morph = str(look.get("HeadMorph") or "").lower()
    morph = morph[:-4] if morph.endswith(".mor") else morph
    if race not in (RACE_HUMAN, None) or morph.startswith("kn_"):
        return morph, ""
    g = "f" if look.get("Gender") == 2 else "m"
    h = int(hashlib.md5(tag.lower().encode()).hexdigest()[:8], 16)
    return morph, "crowd_%s_%d" % (g, h % CROWD_FACES[g])


def armed_ally(utc: dict, template: str = "") -> bool:
    """Whether a creature fights on the player's side: not hostile, with a weapon and
    chest armour equipped (the castle's guards and knights; servants and nobles wear
    clothes, the panicked servant only has a dagger). Howe's men (templates named
    *howe*) are excluded: some start out neutral and turn on you later."""
    if utc.get("GroupId") in (GROUP_HOSTILE, GROUP_HOSTILE_ON_GROUND) or "howe" in template.lower():
        return False
    refs = [str(e.get("TemplateResRef") or "").lower() for e in utc.get("Equip_ItemList") or []
            if isinstance(e, dict)]
    return any(r.startswith("gen_im_wep_") for r in refs) and any(r.startswith("gen_im_arm_cht") for r in refs)


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


def trigger_templates(json_dir: str | Path) -> dict[str, dict]:
    """Every .utt dump under a pull folder, by template name (lower case)."""
    found = {}
    for p in sorted(Path(json_dir).rglob("*.utt.json")):
        found.setdefault(p.name[:-len(".utt.json")].lower(), json.loads(p.read_text(encoding="utf-8"))["root"])
    return found


TALK_TRIGGER = "gen00tr_talk"
TRIGGER_HEIGHT = 300.0  # cm above the polygon's lowest point
TRIGGER_BELOW = 50.0


def _flag_key(local: dict, plot: str, flag: str) -> str:
    """"GUID:FLAG" from a plot GUID variable and a flag variable, or "" when unset."""
    guid, fid = str(local.get(plot) or ""), local.get(flag)
    if not guid or guid.upper() == "NONE" or fid is None or int(fid) < 0:
        return ""
    return f"{guid}:{int(fid)}"


def triggers(are_root: dict, templates: dict[str, dict]) -> dict:
    """Trigger volumes: tag, box (UE min and max corner of the polygon, from a bit below it
    to 3 m above), the event key its script runs on entering ("enter:<script>"), and for the
    generic talk trigger (gen00tr_talk) who speaks and the flags that gate it and that it sets:
    [speaker, active for, inactive for, inactive for 2, sets, sets 2] (flag keys "GUID:FLAG")."""
    tags, boxes, keys, talk, repeat = [], [], [], [], []
    for t in are_root.get("TriggerList") or []:
        utt = templates.get(str(t.get("TemplateResRef") or "").lower())
        if utt is None or not t.get("Geometry"):
            continue
        local = {v["Name"]: v.get("Value") for src in (utt, t) for v in src.get("VarTable") or [] if v.get("Name")}
        qx, qy, qz, qw = (t.get(k, 0.0) for k in ("XOrientation", "YOrientation", "ZOrientation", "WOrientation"))
        pts = []
        for g in t["Geometry"]:
            v = (g["XPoint"], g["YPoint"], g["ZPoint"])
            # rotate by the trigger's quaternion, then move to its position
            ix = qw * v[0] + qy * v[2] - qz * v[1]
            iy = qw * v[1] + qz * v[0] - qx * v[2]
            iz = qw * v[2] + qx * v[1] - qy * v[0]
            iw = -qx * v[0] - qy * v[1] - qz * v[2]
            rx = ix * qw + iw * -qx + iy * -qz - iz * -qy
            ry = iy * qw + iw * -qy + iz * -qx - ix * -qz
            rz = iz * qw + iw * -qz + ix * -qy - iy * -qx
            pts.append(ue_point(t["XPosition"] + rx, t["YPosition"] + ry, t["ZPosition"] + rz))
        xs, ys, zs = zip(*pts)
        script = str(utt.get("EventScript") or "")
        tags.append(t.get("Tag") or "")
        boxes.extend([min(xs), min(ys), round(min(zs) - TRIGGER_BELOW, 1),
                      max(xs), max(ys), round(min(zs) + TRIGGER_HEIGHT, 1)])
        keys.append(f"enter:{script}" if script and script != TALK_TRIGGER else "")
        speaker = str(local.get("TRIG_TALK_SPEAKER") or "") if script == TALK_TRIGGER else ""
        talk.extend([speaker if speaker.upper() != "NONE" else "",
                     _flag_key(local, "TRIG_TALK_ACTIVE_FOR_PLOT", "TRIG_TALK_ACTIVE_FOR_FLAG"),
                     _flag_key(local, "TRIG_TALK_INACTIVE_FOR_PLOT", "TRIG_TALK_INACTIVE_FOR_FLAG"),
                     _flag_key(local, "TRIG_TALK_INACTIVE_FOR_PLOT2", "TRIG_TALK_INACTIVE_FOR_FLAG2"),
                     _flag_key(local, "TRIG_TALK_SET_PLOT", "TRIG_TALK_SET_FLAG"),
                     _flag_key(local, "TRIG_TALK_SET_PLOT2", "TRIG_TALK_SET_FLAG2")]
                    if script == TALK_TRIGGER else [""] * 6)
        repeat.append(int(local.get("TRIG_TALK_REPEAT") or 0) if script == TALK_TRIGGER else 0)
    return {"TriggerTags": tags, "TriggerBox": boxes, "TriggerKey": keys, "TriggerTalk": talk,
            "TriggerRepeat": repeat}


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


def _top(b: list[float]) -> float:
    return b[2] + sum(abs(ax[2]) * b[3 + j] for j, ax in enumerate(_axes(b)))


class _Grid:
    """Boxes (13 numbers each) bucketed by their horizontal reach, for point tests."""
    CELL = 500.0

    def __init__(self, boxes: list[list[float]]):
        self.cells: dict[tuple[int, int], list[list[float]]] = {}
        for b in boxes:
            r = math.sqrt(sum(h * h for h in b[3:6]))
            for gx in range(int((b[0] - r) // self.CELL), int((b[0] + r) // self.CELL) + 1):
                for gy in range(int((b[1] - r) // self.CELL), int((b[1] + r) // self.CELL) + 1):
                    self.cells.setdefault((gx, gy), []).append(b)

    def at(self, x: float, y: float) -> list[list[float]]:
        return self.cells.get((int(x // self.CELL), int(y // self.CELL)), [])


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


LID_TILE = 200.0  # cm
LID_REACH = 6000.0  # cm
LID_MIN_WALL = 400.0  # cm over the floor; lower walls (benches, screens) don't bound a room
LID_PILLAR = 75.0  # cm; narrower boxes (pillars, posts) are looked past
LID_THICK = 30.0  # cm
LID_OVERLAP = 50.0  # cm; lids reach this far past their tile, over the walls' tops beside them


def lids(floor_boxes: list[float], solids: list[float]) -> tuple[list[float], int]:
    """Ceilings (kind 3) where the kit's leave the sky showing. The game leaves its
    tallest rooms (the main hall, the chapel, the family quarters) open above: its
    camera looks down from above and the sky there is dark. And the walls drawn
    here are the kit's collision boxes, mostly 4.5 to 6 m tall, below many kit
    ceilings (corridor tops start 6 to 8 m up). Floor boxes (7 numbers, see
    floor_plan) are cut into LID_TILE tiles; from each tile, rays at 1.5 m look
    for a wall (kind 0, at least LID_MIN_WALL over the floor, pillars looked past)
    along +-X and +-Y. Where at least three find one within LID_REACH, the tile is
    indoors and gets a slab at the lowest of those walls' tops, snapped down to
    25 cm, unless a kit ceiling already starts no higher: no gap opens between wall
    and ceiling. Tiles of a floor box at the same height are merged along its Y,
    and each lid reaches LID_OVERLAP past its tiles to close the slits over walls."""
    boxes = [solids[i:i + 13] for i in range(0, len(solids), 13)]
    grid = _Grid([b for b in boxes if b[12] == 3 or (b[12] == 0 and max(
        b[3 + j] for j, ax in enumerate(_axes(b)) if abs(ax[2]) < 0.5) >= LID_PILLAR)])

    def ceiling(x: float, y: float, z: float) -> float | None:
        under = [_bottom(b) for b in grid.at(x, y) if b[12] == 3 and b[2] > z and _inside(b, (x, y, b[2]))]
        return min(under) if under else None

    def wall_top(x: float, y: float, z: float, dx: float, dy: float) -> float | None:
        t = 25.0
        while t < LID_REACH:
            px, py = x + dx * t, y + dy * t
            for b in grid.at(px, py):
                if b[12] == 0 and _inside(b, (px, py, z + 150)) and _top(b) - z >= LID_MIN_WALL:
                    return _top(b)
            t += 25.0
        return None

    out: list[float] = []
    count = 0
    for i in range(0, len(floor_boxes), 7):
        x0, y0, _, x1, y1, z, kind = floor_boxes[i:i + 7]
        if kind != 0:
            continue
        nx, ny = max(1, math.ceil((x1 - x0) / LID_TILE)), max(1, math.ceil((y1 - y0) / LID_TILE))
        for a in range(nx):
            ax0, ax1 = x0 + (x1 - x0) * a / nx, x0 + (x1 - x0) * (a + 1) / nx
            run: list[tuple[float, float, float]] = []  # (y from, y to, lid height) along this column
            for c in range(ny):
                ay0, ay1 = y0 + (y1 - y0) * c / ny, y0 + (y1 - y0) * (c + 1) / ny
                cx, cy = (ax0 + ax1) / 2, (ay0 + ay1) / 2
                tops = [t for t in (wall_top(cx, cy, z, dx, dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                        if t is not None]
                h = math.floor(min(tops) / 25) * 25 if len(tops) >= 3 else None
                kit_ceiling = ceiling(cx, cy, z)
                if h is not None and kit_ceiling is not None and kit_ceiling <= h + 25:
                    h = None
                if h is not None and run and run[-1][2] == h and abs(run[-1][1] - ay0) < 1:
                    run[-1] = (run[-1][0], ay1, h)
                elif h is not None:
                    run.append((ay0, ay1, h))
            for ry0, ry1, h in run:
                out += [round((ax0 + ax1) / 2, 1), round((ry0 + ry1) / 2, 1), round(h + LID_THICK / 2, 1),
                        round((ax1 - ax0) / 2 + LID_OVERLAP, 1), round((ry1 - ry0) / 2 + LID_OVERLAP, 1), LID_THICK / 2,
                        1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 3]
                count += 1
    return out, count


def tuck_lights(lights: list[float], solids: list[float], below: float = 30.0) -> tuple[list[float], int]:
    """Move lights (7 numbers each, see kit.lights) that sit inside or just above a
    ceiling box (kind 3) to `below` cm under it, so they light the room and not the
    roof: the greybox ceilings are flat at the vaults' springing and the lids sit at
    the walls' tops, lower than the game's lamps in places."""
    grid = _Grid([solids[i:i + 13] for i in range(0, len(solids), 13) if solids[i + 12] == 3])
    out: list[float] = []
    moved = 0
    for i in range(0, len(lights), 7):
        light = list(lights[i:i + 7])
        under = [_bottom(b) for b in grid.at(light[0], light[1])
                 if _inside(b, (light[0], light[1], b[2])) and _bottom(b) < light[2] <= _top(b) + 50]
        if under:
            light[2] = round(min(under) - below, 1)
            moved += 1
        out += light
    return out, moved


CANDLE_LIGHT = 0.25  # candles' own lights, scaled: the game lights each lit candle like a torch


def dim_candle_lights(lights: list[float], fires: list[float], scale: float = CANDLE_LIGHT,
                      near: float = 50.0) -> tuple[list[float], int]:
    """Scale the colour (and so the brightness) of lights within `near` cm of a
    candle fire (size 3, see kit.fixtures). The game gives each lit candle a light
    as bright as a torch's (1.62) 27 cm above the flame; candles stand by walls,
    and at that strength the wall beside one burns white. Scaled, they also drop
    under 0.8 and stop casting shadows like the lamps."""
    candles = [fires[i:i + 3] for i in range(0, len(fires), 4) if fires[i + 3] == 3]
    out: list[float] = []
    dimmed = 0
    for i in range(0, len(lights), 7):
        light = list(lights[i:i + 7])
        if any(math.dist(light[:3], c) < near for c in candles):
            light[4:7] = [round(v * scale, 3) for v in light[4:7]]
            dimmed += 1
        out += light
    return out, dimmed


CHAIN = 209.0  # cm; the game's hanging lamp model reaches 2.09 m above its bowl
CHAIN_MAX = 600.0  # cm; chains reach a ceiling up to this far above the bowl (the game's vaults are higher)


def hang_fixtures(fixtures: list[float], fires: list[float], solids: list[float],
                  below: float = 30.0) -> tuple[list[float], list[float]]:
    """Fixtures (5 numbers each, see kit.fixtures) gain a sixth: the chain length,
    for hanging lamps, from the bowl up to the ceiling box (kind 3) above it, at
    most CHAIN_MAX, or CHAIN with no ceiling there (0 for other fixtures). A fixture that sits inside or just above
    a ceiling is moved `below` cm under it like the lights (tuck_lights), and so are
    fires within 30 cm of it, which burn in its bowl."""
    grid = _Grid([solids[i:i + 13] for i in range(0, len(solids), 13) if solids[i + 12] == 3])
    fires = list(fires)
    out: list[float] = []
    for i in range(0, len(fixtures), 5):
        x, y, z, yaw, kind = fixtures[i:i + 5]
        over = [_bottom(b) for b in grid.at(x, y) if _inside(b, (x, y, b[2])) and _bottom(b) < z + CHAIN_MAX]
        ceiling = min(over) if over else None
        if ceiling is not None and z > ceiling - below:
            nz = round(ceiling - below, 1)
            for j in range(0, len(fires), 4):
                if math.dist(fires[j:j + 3], (x, y, z)) < 30.0:
                    fires[j + 2] = round(fires[j + 2] + nz - z, 1)
            z = nz
        chain = 0.0
        if kind == 0:
            chain = round(ceiling - z, 1) if ceiling is not None else CHAIN
        out += [x, y, z, yaw, kind, chain]
    return out, fires


FILL_COLOUR = (0.6, 0.7, 1.0)  # a cool, moonlit tint; scaled by the brightness asked for
WARM_FILL_COLOUR = (1.0, 0.8, 0.6)  # candle- and hearth-lit rooms by day


def light_reach(lights: list[float], x: float, y: float, z: float) -> float:
    """How much of the lights (7 numbers each) reaches a point: per light, its
    brightness (luminance of its colour) times an inverse-square-like falloff that
    is 1 at the light and 0 at its radius."""
    total = 0.0
    for i in range(0, len(lights), 7):
        lx, ly, lz, r, cr, cg, cb = lights[i:i + 7]
        d2 = (x - lx) ** 2 + (y - ly) ** 2 + (z - lz) ** 2
        if d2 < r * r:
            total += (1 - d2 / (r * r)) ** 2 * (0.2126 * cr + 0.7152 * cg + 0.0722 * cb)
    return total


def fill_lights(lights: list[float], floors: list[float], brightness: float, *, spacing: float = 500.0,
                height: float = 220.0, radius: float = 900.0, enough: float = 0.03,
                tint: tuple[float, float, float] = FILL_COLOUR) -> list[float]:
    """Dim fill lights for the walkable floor the area's lights do not reach.
    The game lit its areas with baked ambient light as well as its lamps; without it
    corridors with no lamp are black at night. Every `spacing` cm on each floor box
    (7 numbers each, kind 0), a point 1 m up that gets less than `enough` from the
    lights (and the fills placed so far) gets a fill light `height` cm above the
    floor, of `radius` cm, coloured `tint` (FILL_COLOUR, or WARM_FILL_COLOUR by day)
    x `brightness`."""
    fills: list[float] = []
    colour = [round(c * brightness, 3) for c in tint]
    for i in range(0, len(floors), 7):
        x0, y0, _, x1, y1, z, kind = floors[i:i + 7]
        if kind != 0:
            continue
        nx, ny = max(1, round((x1 - x0) / spacing)), max(1, round((y1 - y0) / spacing))
        for a in range(nx):
            for b in range(ny):
                x, y = x0 + (a + 0.5) * (x1 - x0) / nx, y0 + (b + 0.5) * (y1 - y0) / ny
                if light_reach(lights, x, y, z + 100) + light_reach(fills, x, y, z + 100) < enough:
                    fills += [round(x, 1), round(y, 1), round(z + height, 1), radius, *colour]
    return fills


def area(are_root: dict, layout_root: dict, templates: dict[str, dict], *, start: str = "",
         solids: dict | None = None, door_models: dict[str, tuple[float, float, float]] | None = None,
         creature_stats=None, player: dict | None = None, ambient_tables: dict | None = None,
         trigger_templates: dict[str, dict] | None = None, extra_creatures: list[tuple[str, str]] = (),
         lights: list[float] | None = None, fill: float = 0.0, fill_tint=FILL_COLOUR,
         fixtures: dict | None = None) -> dict:
    """The runtime area file. `solids` (kit.solids, from the layout's rooms) replaces
    the navigation grid's walls with the level kit's walls, props, blockers and
    ceilings; `lights` (kit.lights) are the rooms' point lights, and `fill` above 0
    adds dim fill lights of that brightness and `fill_tint` where they do not reach
    (fill_lights). `fixtures` (kit.fixtures) are the rooms' lamps and fires
    (hang_fixtures).
    `creature_stats` (utc -> stats.stats() dict) and `player` add the game's combat
    numbers (see stats.py). `ambient_tables` (ambient.load_tables) adds what each
    creature does on its own (see ambient.py); creatures with ambient behaviour are
    kept even without a conversation or team.
    `door_models` (template -> the door model's min and max along its width and its
    height, metres; see kit.door_models) places and sizes doors like the game: the
    door's origin is its hinge and the panel runs along its local X."""
    warnings: list[str] = []
    npc_tags, npc_names, npc_convs, npc_female, npc_pose, npc_active = [], [], [], [], [], []
    npc_team, npc_scale, npc_hostile, npc_rank, npc_dead, npc_ally = [], [], [], [], [], []
    npc_morph, npc_crowd = [], []
    npc_health, npc_attack, npc_defense, npc_damage, npc_dscale = [], [], [], [], []
    npc_outfit, npc_chest, npc_armour, npc_shield = [], [], [], []
    npc_ambient, npc_ambient_prefix = [], []
    creatures = list(are_root.get("CreatureList") or [])
    waypoints = {w.get("Tag"): w for w in are_root.get("WaypointList") or []}
    for template, wp in extra_creatures:  # party members the game brings along into this area
        w = waypoints.get(wp)
        utc = templates.get(template.lower())
        if w is None or utc is None:
            warnings.append(f"added creature {template}@{wp}: template or waypoint not found")
            continue
        creatures.append({**{k: w[k] for k in ("XPosition", "YPosition", "ZPosition", "XOrientation",
                                                 "YOrientation", "ZOrientation", "WOrientation")},
                          "TemplateResRef": template, "Tag": utc.get("Tag") or template, "Active": 1,
                          "TeamId": NO_TEAM})
    for c in creatures:
        utc = templates.get(str(c.get("TemplateResRef", "")).lower())
        if utc is None:
            warnings.append(f"creature {c.get('Tag')}: template {c.get('TemplateResRef')} not found")
            continue
        conversation = utc.get("DialogResRef") or ""
        team = int(c.get("TeamId", NO_TEAM))
        amb = ambient.settings(ambient.variables(utc, c), c.get("Tag") or "")
        npc_ambient.extend([amb["State"], amb["Move"], amb["Pattern"], amb["Freq"]])
        npc_ambient_prefix.append(amb["Prefix"])
        look = utc.get("Appearance Data") if isinstance(utc.get("Appearance Data"), dict) else {}
        npc_tags.append(c.get("Tag") or "")
        npc_names.append(_text(utc.get("LocName")))
        npc_convs.append(conversation.lower())
        npc_female.append(1 if look.get("Gender") == 2 else 0)
        npc_active.append(1 if c.get("Active") else 0)  # inactive ones wait for a plot to show them
        npc_team.append(team)
        # Bodies: the game kills a creature whose template or instance sets CREATURE_SPAWN_DEAD.
        spawn_dead = {v.get("Name"): v.get("Value") for src in (utc, c) for v in src.get("VarTable") or []}
        npc_dead.append(1 if spawn_dead.get("CREATURE_SPAWN_DEAD") == 1 else 0)
        # Greybox stand-ins: a mannequin, scaled by stand_in_scale.
        race, rank = utc.get("Race"), int(utc.get("Rank") or 0)
        # Look keys: the head morph names the same character in every module (hm_gen_duncan), so a
        # MetaHuman made once is found again later; other adult humans get a stable crowd face.
        morph, crowd = look_keys(look, race, "%s@%d,%d" % (c.get("Tag") or "", round(float(c.get("XPosition") or 0)), round(float(c.get("YPosition") or 0))))
        npc_scale.append(stand_in_scale(race, rank, morph))
        npc_hostile.append(1 if utc.get("GroupId") in (GROUP_HOSTILE, GROUP_HOSTILE_ON_GROUND) else 0)
        npc_ally.append(1 if armed_ally(utc, str(c.get("TemplateResRef", ""))) else 0)
        npc_morph.append(morph)
        npc_crowd.append(crowd)
        npc_rank.append(rank)
        if creature_stats is not None:  # stats.stats() for this template (see the CLI)
            st = creature_stats(utc)
            npc_health.append(st["Health"])
            npc_attack.append(st["Attack"])
            npc_defense.append(st["Defense"])
            npc_damage.extend(st["Damage"])
            npc_dscale.append(st["DamageScale"])
            outfit = st.get("Outfit") or {}
            npc_outfit.append(",".join("%s=%s" % (k, outfit[k]) for k in sorted(outfit)))
            npc_chest.append(outfit.get("chest", "").removeprefix("gen_im_"))
            npc_armour.append(st.get("Armour", 0.0))
            npc_shield.append(st.get("ShieldDefense", 0.0))
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
    solid_boxes, cut, dropped, fitted, lidded = [], 0, 0, 0, 0
    if solids is not None:
        boxes = [v for i in range(0, len(boxes), 7) if boxes[i + 6] == 0 for v in boxes[i:i + 7]]  # floors only
        solid_boxes, dropped = drop_hanging(solids["Solids"], navigation(layout_root))
        doors = [(door_pose[i * 4:i * 4 + 3], door_size_wh[i * 2] / 2) for i in range(len(door_tags))]
        solid_boxes, cut = cut_doorways(solid_boxes, doors)
        frames, fitted = frame_doors(door_pose, door_size_wh, solid_boxes)
        solid_boxes += frames
        lid_boxes, lidded = lids(boxes, solid_boxes)
        solid_boxes += lid_boxes
    lights = list(lights or [])
    filled = fill_lights(lights, boxes, fill, tint=fill_tint) if fill > 0 else []
    lights, tucked = tuck_lights(lights + filled, solid_boxes)
    hung, fires = hang_fixtures((fixtures or {}).get("Fixtures", []), (fixtures or {}).get("Fires", []), solid_boxes)
    lights, candle_lights = dim_candle_lights(lights, fires)
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
        "NpcDead": npc_dead,
        "NpcTeam": npc_team,
        "NpcScale": npc_scale,
        "NpcHostile": npc_hostile,
        # 1: fights hostiles near the player without joining the party (armed_ally).
        "NpcAlly": npc_ally,
        "NpcMorph": npc_morph,
        "NpcCrowd": npc_crowd,
        "NpcRank": npc_rank,
        "NpcHealth": npc_health,
        "NpcAttack": npc_attack,
        "NpcDefense": npc_defense,
        "NpcDamage": npc_damage,
        "NpcDamageScale": npc_dscale,
        # What each one wears ("chest=<item>,helmet=<item>,..."), and its armour and shield defense (stats.equipment).
        "NpcOutfit": npc_outfit,
        # The chest item without "gen_im_" (e.g. cth_nob_c01): the outfit a look wears (BP_DlgNPC.ApplyOutfit).
        "NpcChest": npc_chest,
        "NpcArmour": npc_armour,
        "NpcShieldDefense": npc_shield,
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
        # Per light: position xyz, radius (cm), colour rgb (the game's, may exceed 1).
        "Lights": lights,
        "Fixtures": hung,
        "Fires": fires,
        **triggers(are_root, trigger_templates or {}),
        "Labels": labels,
        "LabelPos": label_pos,
        "Summary": {"Floors": sum(1 for k in boxes[6::7] if k == 0), "Walls": sum(1 for k in boxes[6::7] if k == 1),
                    "TalkingCreatures": sum(1 for c in npc_convs if c), "TeamOnly": sum(1 for c, t in zip(npc_convs, npc_team) if not c and t != NO_TEAM),
                    "Ambient": sum(1 for f in npc_ambient[0::4] if int(f) & ambient.ENABLED) if ambient_tables else 0,
                    "Teams": len({t for t in npc_team if t != NO_TEAM}),
                    "Inactive": npc_active.count(0), "Dead": sum(npc_dead),
                    "OtherCreatures": sum(1 for c, t in zip(npc_convs, npc_team) if not c and t == NO_TEAM),
                    "Waypoints": len(wp_tags), "Doors": len(door_tags),
                    "Solids": len(solid_boxes) // 13, "DoorwaysCut": cut,
                    "HangingPropsDropped": dropped, "DoorFrames": fitted,
                    "Ceilings": sum(1 for k in solid_boxes[12::13] if k == 3), "Lids": lidded,
                    "Lights": len(lights) // 7, "FillLights": len(filled) // 7, "LightsTucked": tucked,
                    "Fixtures": len(hung) // 6, "Fires": len(fires) // 4,
                    "CandleLightsDimmed": candle_lights},
        "Warnings": warnings,
    }
