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

from pathlib import Path

from . import fields as F
from .gff4 import GFF4
from .unreal import FORMAT

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
