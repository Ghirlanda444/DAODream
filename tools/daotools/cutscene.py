"""What a cutscene says, so Unreal can convey it without the game's cinematics.

A cutscene (.cut, GFF4 "CUT ") is a list of actors, each with a list of tracks.
Spoken lines are ASLN tracks: the conversation the line belongs to, its start
and end time and the line itself (a talk-table string). The Human Noble
cutscenes take all their lines, in order, from one conversation each
(`bhn200dg_farewell_cutscene` for the family farewell), which `daotools unreal
origin` already exports with voice. Unreal plays that conversation on its own,
without choices, where the script loads the cutscene.

A cutscene with no spoken line (night falls: the hero wakes to the dog, no one
speaks) gets a caption instead: a few lines of our own words, written below
and exported as a small conversation with no voice, so it plays the same way.
"""

from __future__ import annotations

import math
from pathlib import Path

from . import fields as F
from .gff4 import GFF4
from .unreal import FORMAT


def _ue_point(x, y, z):
    from .area import ue_point
    return ue_point(x, y, z)


def _ue_yaw(qx, qy, qz, qw):
    from .area import ue_yaw
    return ue_yaw(qx, qy, qz, qw)

_LINE_TEXT = 22  # ASLN: the spoken line (a talk-table string)

# Our own summaries of what a voiceless cutscene shows, for the player who
# cannot see it: {cutscene: (title shown as the speaker, lines)}.
CAPTIONS: dict[str, tuple[str, list[str]]] = {
    "bhn200cs_night_falls": ("Night falls", [
        "Night falls on Castle Cousland. Fergus has ridden south with most of the castle's soldiers, "
        "and your father has stayed behind to wait for Arl Howe's men.",
        "Howe's soldiers came, but not to march. In the dark they turn on the household, "
        "cutting down guards and servants, while more of his men storm the gates.",
        "You wake to your mabari growling at the door.",
    ]),
}
CAPTION_SPEAKER = "caption"


def lines(gff: GFF4) -> list[dict]:
    """The spoken lines in time order: {"Start", "End", "Actor", "Conversation", "Strref", "Text"}."""
    out = []
    for actor in gff.root.get(F.CUT_ACTOR_LIST, []) or []:
        if actor is None:
            continue
        for track in actor.get(F.CUT_TRACK_LIST, []) or []:
            if getattr(track, "label", "") != "ASLN":
                continue
            text = track.get(_LINE_TEXT)
            out.append({
                "Start": round(track.get(F.CUT_TRACK_START, 0.0), 3),
                "End": round(track.get(F.CUT_TRACK_END, 0.0), 3),
                "Actor": actor.get(F.CUT_ACTOR_TAG, "") or "",
                "Conversation": track.get(F.CUT_LINE_CONVERSATION, "") or "",
                "Strref": getattr(text, "strref", -1),
                "Text": getattr(text, "text", ""),
            })
    return sorted(out, key=lambda l: l["Start"])


def summary(gff: GFF4) -> dict:
    """Length, area, the conversation its lines come from ("" for none) and the lines."""
    spoken = lines(gff)
    convs = []
    for l in spoken:
        if l["Conversation"] and l["Conversation"] not in convs:
            convs.append(l["Conversation"])
    return {
        "Length": round(gff.root.get(F.CUT_LENGTH, 0.0), 3),
        "Area": gff.root.get(F.CUT_AREA, "") or "",
        "Conversation": convs[0] if convs else "",
        "Conversations": convs,
        "Lines": spoken,
    }


# --- staging: where the characters stand and what the camera sees -------------------------------------
#
# Every actor has tracks of curves: position (kind 17, x, y, z in the area's metres) and rotation (18, degrees:
# yaw about z, then pitch about y, then roll about x), each a base value and keys (time, value); a camera
# also has its field of view (13, vertical degrees). A camera can carry a baked animation (AANI) instead of
# keys: per frame an offset and a rotation from its base, in the animation's own y-up frame. The MASTER's
# kind 11 tracks cut between cameras by actor id. Conventions fitted to the Human Noble cutscenes: the free
# camera of the family farewell frames a character within 15 degrees on average, the keyed camera of night
# falls within 25 (it also shows empty rooms).

STAGE_FORMAT = "DAODream.Cutscene 1"
STAGE_RATE = 30.0  # samples per second
_ASPECT = 16.0 / 9.0


def _curve(c, t: float) -> float:
    """A curve's value at t: the base until the first key (a key is where it changes), linear between keys."""
    keys = [(k.get(F.CUT_KEY_TIME, 0.0), k.get(F.CUT_KEY_VALUE, 0.0)) for k in (c.get(F.CUT_CURVE_KEYS) or [])]
    if not keys or t < keys[0][0]:
        return c.get(F.CUT_CURVE_BASE, 0.0)
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            return v0 + (v1 - v0) * (t - t0) / max(t1 - t0, 1e-6)
    return keys[-1][1]


def _tracks(actor, kind: int) -> list:
    return [t for t in (actor.get(F.CUT_TRACK_LIST) or []) if t is not None and t.get(F.CUT_TRACK_KIND) == kind]


def _value(actor, kind: int, t: float) -> list[float] | None:
    tr = _tracks(actor, kind)
    return [_curve(c, t) for c in tr[0].get(F.CUT_TRACK_CURVES) or []] if tr else None


def _rot(axis: str, deg: float) -> list[list[float]]:
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return {"x": [[1, 0, 0], [0, c, -s], [0, s, c]], "y": [[c, 0, s], [0, 1, 0], [-s, 0, c]],
            "z": [[c, -s, 0], [s, c, 0], [0, 0, 1]]}[axis]


def _mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def _apply(m, v):
    return [sum(m[i][k] * v[k] for k in range(3)) for i in range(3)]


def _quat(q):
    x, y, z, w = q
    return [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]


def _frame(rows: list, width: int, t: float) -> list[float] | None:
    """The baked frame nearest time t (rows: flat floats, `width` per frame, time first)."""
    best = None
    for i in range(0, len(rows) - width + 1, width):
        if best is None or abs(rows[i] - t) < abs(rows[best] - t):
            best = i
    return rows[best + 1:best + width] if best is not None else None


def camera_at(actor, t: float) -> tuple[list[float], list[float], float]:
    """A camera's position (metres), forward vector and vertical field of view at t, in the area's frame."""
    pos = _value(actor, 17, t) or [0.0, 0.0, 0.0]
    yaw, pitch, roll = _value(actor, 18, t) or [0.0, 0.0, 0.0]
    m = _mul(_mul(_rot("z", yaw), _rot("y", -pitch)), _rot("x", roll))
    for anim in _tracks(actor, 4):
        start, end = anim.get(F.CUT_TRACK_START, 0.0), anim.get(F.CUT_TRACK_END, 0.0)
        if not (start <= t <= end):
            continue
        p = _frame(anim.get(F.CUT_ANIM_POSITIONS) or [], 4, t - start)
        q = _frame(anim.get(F.CUT_ANIM_ROTATIONS) or [], 5, t - start)
        base = m
        if p:  # y-up offsets: (x, z, -y) in the area's z-up frame, turned with the camera
            off = _apply(base, [p[0], p[2], -p[1]])
            pos = [pos[i] + off[i] for i in range(3)]
        if q:
            r = _quat([q[0], q[2], -q[1], q[3]])
            m = _mul([[r[j][i] for j in range(3)] for i in range(3)], base)
        break
    fov = (_value(actor, 13, t) or [45.0])[0]
    return pos, _apply(m, [1.0, 0.0, 0.0]), fov


# Keys come in two frames: most are positions in the area (metres, near the cutscene's origin), but some
# actors jump to small values for a while (relative to something not yet decoded: an animation's own
# reference). Only area positions are kept; between them an actor holds its last one.
WORLD_RANGE = 40.0  # metres from the cutscene's origin within which a key is an area position
FRAME_CHECK = 30.0  # degrees: a camera sample frames someone when a head is this close to its view's centre
FRAME_SHARE = 0.7  # the share of samples a camera path must frame someone in to be played


def _world_keys(actor, origin, length: float) -> list[tuple[float, list[float], float]]:
    """(time, position, yaw) at the actor's base (time -1) and at every key in the scene that is an area
    position. Keys before the start and in its last half second put actors back where they were before the
    cutscene (the farewell's Eleanor at the larder door, where she kneels by Bryce in the scene): left out."""
    pos_tr, rot_tr = _tracks(actor, 17), _tracks(actor, 18)
    if not pos_tr:
        return []
    curves = pos_tr[0].get(F.CUT_TRACK_CURVES) or []
    if len(curves) < 3:
        return []
    near = lambda v: math.hypot(v[0] - origin[0], v[1] - origin[1]) < WORLD_RANGE
    yaw_at = lambda t: (_value(actor, 18, t) or [0.0])[0] if rot_tr else 0.0
    out = []
    base = [c.get(F.CUT_CURVE_BASE, 0.0) for c in curves[:3]]
    rot_base = [c.get(F.CUT_CURVE_BASE, 0.0) for c in (rot_tr[0].get(F.CUT_TRACK_CURVES) or [])][:1] if rot_tr else [0.0]
    if near(base):
        out.append((-1.0, base, rot_base[0] if rot_base else 0.0))
    times = sorted({k.get(F.CUT_KEY_TIME, 0.0) for k in (curves[0].get(F.CUT_CURVE_KEYS) or [])})
    for t in times:
        v = [_curve(c, t) for c in curves[:3]]
        if 0.0 <= t <= length - 0.5 and near(v):
            out.append((t, v, yaw_at(t)))
    return out


def _pose(keys, t: float) -> tuple[list[float], float]:
    """Position and yaw at t from (time, position, yaw) keys: linear between keys a second or less apart (a
    walk), held over longer gaps and over keys that were left out (a cut, or a frame we do not read)."""
    prev = keys[0]
    for k in keys[1:]:
        if k[0] > t:
            if k[0] - prev[0] <= 1.0 and prev[0] >= 0.0:
                f = (t - prev[0]) / max(k[0] - prev[0], 1e-6)
                yaw = prev[2] + ((k[2] - prev[2] + 180.0) % 360.0 - 180.0) * f
                return [prev[1][i] + (k[1][i] - prev[1][i]) * f for i in range(3)], yaw
            return prev[1], prev[2]
        prev = k
    return prev[1], prev[2]


def _ue_yaw_deg(yaw: float) -> float:
    a = math.radians(yaw)
    return _ue_yaw(0.0, 0.0, math.sin(a / 2), math.cos(a / 2))


def staging(gff: GFF4, require_framing: bool = True) -> dict:
    """Where a cutscene's characters stand and what its camera does, in Unreal's terms (centimetres, degrees),
    sampled CamRate times a second over its length: {"Length", "CamRate", "ActorTags", "ActorFrames": per
    actor, per sample, x, y, z, yaw (its feet), "Cam": per sample x, y, z, pitch, yaw, horizontal field of view
    (empty when the camera path does not frame its characters: Unreal then frames each speaker), "Framed": the
    share of samples the path frames someone in}. Tags: the creature's tag, "PLAYER", the hero's dog's
    template; actors with no area positions are left out (night falls is all in a frame of its own)."""
    root = gff.root
    length = root.get(F.CUT_LENGTH, 0.0) or 0.0
    origin = list(root.get(5014) or [0.0, 0.0, 0.0])
    actors = [a for a in root.get(F.CUT_ACTOR_LIST, []) or [] if a is not None]
    n = int(length * STAGE_RATE) + 1
    times = [i / STAGE_RATE for i in range(n)]
    tags, frames, heads = [], [], []
    for a in actors:
        tag = (a.get(F.CUT_ACTOR_TAG, "") or "").split(":")[-1] or (a.get(F.CUT_ACTOR_TEMPLATE, "") or "")
        if not tag or _tracks(a, 13) or "ip_" in tag:
            continue  # cameras, effects and sounds (no tag), placeables (doors: not moved)
        keys = _world_keys(a, origin, length)
        if not keys:
            continue
        tags.append(tag)
        track = []
        for t in times:
            p, yaw = _pose(keys, t)
            track += [*_ue_point(*p), _ue_yaw_deg(yaw)]
            heads.append((t, p))
        frames += track
    cameras = {a.get(F.CUT_ACTOR_ID, -1): a for a in actors if _tracks(a, 13)}
    cuts = sorted((c.get(F.CUT_TRACK_START, 0.0), c.get(F.CUT_CAMERA_ACTOR, -1)) for a in actors for c in _tracks(a, 11))
    cam, framed = [], 0
    if cameras and tags:
        first = next(iter(cameras))
        by_time = {}
        for t, p in heads:
            by_time.setdefault(t, []).append(p)
        for t in times:
            current = first
            for at, who in cuts:
                if at <= t and who in cameras:
                    current = who
            pos, fwd, vfov = camera_at(cameras[current], t)
            best = 180.0
            for p in by_time.get(t, []):
                d = [p[0] - pos[0], p[1] - pos[1], p[2] + 1.5 - pos[2]]
                L = math.sqrt(sum(x * x for x in d)) or 1.0
                best = min(best, math.degrees(math.acos(max(-1.0, min(1.0, sum(fwd[i] * d[i] for i in range(3)) / L)))))
            framed += best < FRAME_CHECK
            f = [fwd[0], -fwd[1], fwd[2]]  # Unreal's y is the game's -y
            hfov = math.degrees(2 * math.atan(math.tan(math.radians(vfov) / 2) * _ASPECT))
            cam += [*_ue_point(*pos), round(math.degrees(math.asin(max(-1.0, min(1.0, f[2])))), 2),
                    round(math.degrees(math.atan2(f[1], f[0])), 2), round(hfov, 1)]
    share = framed / n if cam else 0.0
    return {"Length": round(length, 3), "CamRate": STAGE_RATE, "ActorTags": tags, "ActorFrames": frames,
            "Cam": cam if share >= FRAME_SHARE or not require_framing else [], "Framed": round(share, 2)}


def scan(directory: str | Path) -> dict[str, dict]:
    """{cutscene name: summary} for every .cut file under `directory` (first copy wins)."""
    out: dict[str, dict] = {}
    for p in sorted(Path(directory).rglob("*.cut")):
        name = p.stem.lower()
        if name not in out:
            out[name] = summary(GFF4.open(p))
    return out


def conversation_for(name: str, cutscenes: dict[str, dict] | None) -> str | None:
    """The conversation Unreal plays for cutscene `name`: its own conversation, else its
    caption (named after the cutscene), else None."""
    name = name.lower()
    conv = (cutscenes or {}).get(name, {}).get("Conversation")
    if conv:
        return conv
    return name if name in CAPTIONS else None


def caption_conversation(name: str) -> dict:
    """A caption as a runtime conversation (unreal.conversation's format): one line per
    caption sentence, each followed by a silent player click, no voice."""
    title, texts = CAPTIONS[name]
    n = len(texts)
    out = []
    for i, text in enumerate(texts):
        out.append({"Index": i, "IsPlayer": False, "Speaker": CAPTION_SPEAKER, "Text": text,
                    "Children": [n + i]})
    for i in range(n):
        out.append({"Index": n + i, "IsPlayer": True, "Speaker": "PLAYER", "Text": "",
                    "Children": [i + 1] if i + 1 < n else []})
    for line in out:
        line.update({"Stage": "", "CondKey": "", "CondNot": False, "CondScript": "",
                     "ActionKey": "", "ActionNot": False, "ActionScript": "", "Vo": "", "Show": 0})
    return {
        "Format": FORMAT,
        "Conversation": name,
        "Owner": CAPTION_SPEAKER,
        "VoBank": "",
        "Starts": [0],
        "SpeakerNames": {CAPTION_SPEAKER: title},
        "TrueFlags": [],
        "FlagNames": {},
        "Lines": out,
        "Warnings": [],
    }
