"""The level kit: walls, props, blockers and ceilings as boxes, and the rooms'
lights, for Unreal.

A Dragon Age area layout is made of rooms (`.rml`, one per room of the `.arl`).
Each room places models from a building kit ("FCA_Wall01_0", "blk_01_0",
"prp_barrel01_0"...) with a position and a rotation. A model's physics file
(`.phy`) lists its collision shapes, almost all boxes. Blockers (`blk_*`) have
no physics: the bounding box in their model hierarchy (`.mmh`) is the blocking
volume. Ceilings (`FCA_Ceiling*`, `FCA_CorrTop*`) have neither: they are fade
meshes, drawn from below and hidden from above, and their bounding box stands in
for them. This turns all of it into oriented boxes in Unreal coordinates. Only
box sizes and poses come out; no model geometry.

Each room also places a light model (`<layout>_<room>_ll`, its `.mmh` in the
layout's room archive) whose point-light nodes are the room's lamps, fireplaces
and fill lights; `lights` places them like any other model.

GFF4 fields (observed on the Castle Cousland layout, hrt201d):
  RML  root 4 position, 5 orientation (quaternion x y z w), 3050 placed models
  MDL  4 position, 5 orientation, 3059 scale, 3063 model name (both relative to
       the room)
  PHY  struct "shap": 6058 shape type (2 box), 6060 orientation, 6061 position;
       child "boxs" 6071 half extents
  MMH  struct "bbox": 6054 min, 6055 max; struct "nplt" (point light): 6000 name,
       6007 colour (rgba, above 1 for bright lamps), 6008 radius, child "trsl"
       6047 position
Game coordinates are metres, right-handed, Z up; see area.py for Unreal's.
"""

from __future__ import annotations

import json
from pathlib import Path

from .erf import ERF
from .gff4 import GFF4, to_jsonable

WALL, PROP, BLOCKER, CEILING = 0, 1, 2, 3
BOX_SHAPE = 2
MIN_PROP_HALF = 0.25  # m; smaller props (cups, candles, bottles) are not obstacles
MIN_CEILING_HALF = 0.1  # m; some ceiling pieces are flat sheets (the vaults' end arches)
MAX_LIGHT_RADIUS = 50.0  # m; larger "lights" (sun_fake) stand in for the sun over a whole level
_CEILING_WORDS = ("ceiling", "corrtop")
_SKIP_WORDS = ("floor", "fxe_", "fx_")


def kind(model: str) -> int | None:
    """WALL, PROP, BLOCKER, CEILING, or None for pieces that are not solid (floors,
    effects). Floors come from the navigation grid instead."""
    name = model.lower()
    if name.startswith("blk_"):
        return BLOCKER
    if any(word in name for word in _CEILING_WORDS):
        return CEILING
    if any(word in name for word in _SKIP_WORDS):
        return None
    if name.startswith("prp_"):
        return PROP
    return WALL


def placed_models(rml_roots: list[dict]) -> set[str]:
    return {str(m.get("3063") or "").lower() for r in rml_roots for m in r.get("3050") or [] if m.get("3063")}


def pull(game_dir: str | Path, names: set[str], out_dir: str | Path) -> dict:
    """Dump the .phy and .mmh of every named model as JSON into out_dir. The core
    model archive first, then the core patches (later ones win)."""
    data = Path(game_dir) / "packages" / "core"
    archives = [data / "data" / "modelhierarchies.erf", *sorted((data / "patch").glob("*.erf"))]
    wanted = {f"{n}{ext}" for n in names for ext in (".phy", ".mmh")}
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    found: dict[str, Path] = {}
    for archive in archives:
        if not archive.exists():
            continue
        with ERF.open(archive) as erf:
            for e in erf.entries:
                if e.name.lower() in wanted:
                    path = out / f"{e.name.lower()}.json"
                    path.write_text(json.dumps(to_jsonable(GFF4(erf.read(e)).root, {})), encoding="utf-8")
                    found[e.name.lower()] = path
    missing = sorted(n for n in names if f"{n}.phy" not in found and f"{n}.mmh" not in found)
    return {"Files": len(found), "Missing": missing}


def _structs(value, tag: str):
    if isinstance(value, dict):
        if value.get("_struct") == tag:
            yield value
        for v in value.values():
            yield from _structs(v, tag)
    elif isinstance(value, list):
        for v in value:
            yield from _structs(v, tag)


def _bbox(mmh: dict | None) -> tuple | None:
    for b in _structs(mmh or {}, "bbox"):
        lo, hi = b["6054"][:3], b["6055"][:3]
        return ([(a + c) / 2 for a, c in zip(lo, hi)], [0.0, 0.0, 0.0, 1.0], [(c - a) / 2 for a, c in zip(lo, hi)])
    return None


def local_boxes(name: str, phy: dict | None, mmh: dict | None, piece: int) -> tuple[list[tuple], int]:
    """(center, orientation, half extents) boxes in model space, and how many
    collision shapes were not boxes. Physics boxes where there are any; the model's
    bounding box for blockers, for walls and pillars without box collision (some
    corridor walls have none, a few use a collision mesh), and for props whose
    collision is round (barrels) or missing, unless they are small (cups, candles).
    Decorative pieces without collision (arch fades, beams) stay open. Ceilings
    are their bounding box, at least 2 x MIN_CEILING_HALF thick."""
    if piece == BLOCKER:
        box = _bbox(mmh)
        return ([box] if box else []), 0
    if piece == CEILING:
        box = _bbox(mmh)
        if not box:
            return [], 0
        center, orient, half = box
        return [(center, orient, [max(h, MIN_CEILING_HALF) for h in half])], 0
    boxes, other = [], 0
    for shape in _structs(phy or {}, "shap"):
        box = next(_structs(shape, "boxs"), None)
        if shape.get("6058") != BOX_SHAPE or box is None:
            other += 1
            continue
        boxes.append((shape["6061"][:3], shape["6060"], box["6071"]))
    fallback = None
    if piece == WALL and not boxes and ("wall" in name or "pillar" in name):
        fallback = _bbox(mmh)
    elif piece == PROP and (other or not boxes):
        box = _bbox(mmh)
        if box and max(box[2]) >= MIN_PROP_HALF:
            fallback = box
    return ([fallback] if fallback else boxes), other


def _qmul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz)


def _qrot(q, v):
    x, y, z = _qmul(_qmul(q, (v[0], v[1], v[2], 0.0)), (-q[0], -q[1], -q[2], q[3]))[:3]
    return x, y, z


def solids(rml_roots: list[dict], kit: dict[str, tuple[dict | None, dict | None]]) -> dict:
    """{"Solids": flat list, 13 numbers per box: center xyz, half extents xyz (Unreal
    cm), the box's X axis and Z axis (unit vectors in Unreal space) and kind (0 wall,
    1 prop, 2 blocker, 3 ceiling); "Summary": counts}. `kit` maps model name ->
    (phy, mmh)."""
    out: list[float] = []
    summary = {"Walls": 0, "Props": 0, "Blockers": 0, "Ceilings": 0, "Skipped": 0, "NotBoxes": 0,
               "NoCollision": 0}
    for room in rml_roots:
        room_pos, room_rot = room.get("4") or [0, 0, 0], room.get("5") or [0, 0, 0, 1]
        for m in room.get("3050") or []:
            name = str(m.get("3063") or "").lower()
            piece = kind(name)
            if piece is None:
                summary["Skipped"] += 1
                continue
            phy, mmh = kit.get(name, (None, None))
            boxes, other = local_boxes(name, phy, mmh, piece)
            summary["NotBoxes"] += other
            if not boxes:
                summary["NoCollision"] += 1
                continue
            scale = float(m.get("3059") or 1.0)
            rot = _qmul(room_rot, m.get("5") or [0, 0, 0, 1])
            for center, orient, half in boxes:
                local = _qrot(m.get("5") or [0, 0, 0, 1], [c * scale for c in center])
                c = [m["4"][i] + local[i] for i in range(3)]
                world = [room_pos[i] + v for i, v in enumerate(_qrot(room_rot, c))]
                q = _qmul(rot, orient)
                xa, za = _qrot(q, (1.0, 0.0, 0.0)), _qrot(q, (0.0, 0.0, 1.0))
                # Unreal flips Y; mirroring both axes keeps the rotation proper (the box
                # is symmetric, so its local Y can flip with it).
                out += [round(world[0] * 100, 1), round(-world[1] * 100, 1), round(world[2] * 100, 1),
                        *(round(h * scale * 100, 1) for h in half),
                        round(xa[0], 4), round(-xa[1], 4), round(xa[2], 4),
                        round(za[0], 4), round(-za[1], 4), round(za[2], 4), piece]
                summary[("Walls", "Props", "Blockers", "Ceilings")[piece]] += 1
    return {"Solids": out, "Summary": summary}


def lights(rml_roots: list[dict], light_models: dict[str, dict]) -> list[float]:
    """The rooms' point lights, 7 numbers each: position xyz and radius (Unreal cm),
    then the game's colour rgb (its brightness too: above 1 for bright lamps).
    `light_models` maps model name -> its .mmh (the rooms' `_ll` models); each
    light sits in its model like a kit piece's box. Level-wide stand-ins for the
    sun (radius over MAX_LIGHT_RADIUS) are left out."""
    out: list[float] = []
    for room in rml_roots:
        room_pos, room_rot = room.get("4") or [0, 0, 0], room.get("5") or [0, 0, 0, 1]
        for m in room.get("3050") or []:
            mmh = light_models.get(str(m.get("3063") or "").lower())
            for light in _structs(mmh or {}, "nplt"):
                radius = float(light.get("6008") or 0.0)
                pos = next(_structs(light, "trsl"), {}).get("6047")
                if not pos or not 0 < radius <= MAX_LIGHT_RADIUS:
                    continue
                local = _qrot(m.get("5") or [0, 0, 0, 1], pos[:3])
                c = [m["4"][i] + local[i] for i in range(3)]
                world = [room_pos[i] + v for i, v in enumerate(_qrot(room_rot, c))]
                out += [round(world[0] * 100, 1), round(-world[1] * 100, 1), round(world[2] * 100, 1),
                        round(radius * 100, 1), *(round(v, 3) for v in (light.get("6007") or [1, 1, 1])[:3])]
    return out


def load_light_models(rooms_dir: str | Path) -> dict[str, dict]:
    """The rooms' light models (`*_ll.mmh.json` under a pulled layout's JSON)."""
    return {p.name[:-len(".mmh.json")].lower(): json.loads(p.read_text(encoding="utf-8"))
            for p in Path(rooms_dir).rglob("*_ll.mmh.json")}


def load_kit(kit_dir: str | Path, names: set[str]) -> dict[str, tuple[dict | None, dict | None]]:
    def load(path: Path):
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
    d = Path(kit_dir)
    return {n: (load(d / f"{n}.phy.json"), load(d / f"{n}.mmh.json")) for n in names}


def door_model_names(templates: dict[str, dict], gda_records: list[dict]) -> set[str]:
    """The models (placeable_types.gda ModelName) of the given placeable templates."""
    rows = {r.get("ID"): r for r in gda_records}
    return {str(rows[t.get("Appearance")].get("ModelName")).lower() for t in templates.values()
            if t.get("Appearance") in rows and rows[t.get("Appearance")].get("ModelName")}


def door_models(templates: dict[str, dict], gda_records: list[dict], kit: dict[str, tuple[dict | None, dict | None]]
                ) -> dict[str, tuple[float, float, float]]:
    """Door template -> (min, max) of its model along the model's X (the panel's
    width; the hinge is at 0) and its height, metres. A placeable template's
    `Appearance` is a row of placeable_types.gda, whose ModelName is the model; the
    model hierarchy's bounding box gives the size."""
    rows = {r.get("ID"): r for r in gda_records}
    out = {}
    for name, utp in templates.items():
        row = rows.get(utp.get("Appearance"))
        model = str((row or {}).get("ModelName") or "").lower()
        box = _bbox(kit.get(model, (None, None))[1])
        if box:
            (cx, _, _), _, (hx, _, hz) = box
            out[name] = (cx - hx, cx + hx, 2 * hz)
    return out
