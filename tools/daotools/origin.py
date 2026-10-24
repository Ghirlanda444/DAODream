"""Prepare every conversation of an origin for Unreal in one go.

Works on the output of `daotools pull`: the conversation exports under
<pull>/json and the voice banks under <pull>/raw. For each conversation it
writes the runtime JSON (unreal.conversation) and the PCM voice files, and an
index of what was written, so a whole origin is one command. Cutscenes with no
spoken lines get their caption (cutscene.CAPTIONS) as a conversation too.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import cutscene, fsb, mfdecode, unreal
from .gff4 import GFF4


def pick_conversations(json_dir: str | Path) -> tuple[dict[str, Path], list[str]]:
    """One .dlg.conv.json per conversation name, and warnings.

    The same conversation is often in several archives (the area archives and
    designerdialogs). Official patch archives win, the newest first;
    otherwise the first copy in path order. Copies that differ are reported.
    """
    copies: dict[str, list[Path]] = {}
    for p in sorted(Path(json_dir).rglob("*.dlg.conv.json")):
        copies.setdefault(p.name[:-len(".dlg.conv.json")].lower(), []).append(p)

    def rank(p: Path) -> tuple:
        folder = p.parent.name.lower()
        if folder.startswith("patch"):
            return (0, -int("".join(c for c in folder if c.isdigit()) or 0), "")
        return (1, 0, str(p).lower())

    picked, warnings = {}, []
    for name, paths in sorted(copies.items()):
        paths.sort(key=rank)
        picked[name] = paths[0]
        lines = {json.dumps(json.loads(p.read_text(encoding="utf-8"))["lines"], sort_keys=True) for p in paths}
        if len(lines) > 1:
            warnings.append(f"{name}: the {len(paths)} copies differ; using {paths[0].parent.name}")
    return picked, warnings


def conversation_owners(json_dir: str | Path) -> dict[str, list[str]]:
    """Creature tags that use each conversation (DialogResRef in their .utc)."""
    owners: dict[str, list[str]] = {}
    for p in sorted(Path(json_dir).rglob("*.utc.json")):
        root = json.loads(p.read_text(encoding="utf-8"))["root"]
        dialog, tag = root.get("DialogResRef"), root.get("Tag")
        if isinstance(dialog, str) and dialog and isinstance(tag, str) and tag:
            tags = owners.setdefault(dialog.lower(), [])
            if tag not in tags:
                tags.append(tag)
    return owners


def pick_owner(name: str, tags: list[str]) -> str:
    """The creature whose tag matches the conversation, else the first user."""
    for tag in tags:
        if tag.lower() == name:
            return tag
    return tags[0] if tags else name


def export(pull_dir: str | Path, out_dir: str | Path, *, plots: dict[str, dict] | None = None,
           true_flags: list[str] | None = None, voice: bool = True, names: list | None = None) -> dict:
    """Write <out>/conversations/<name>.json, <out>/vo/<bank>/*.wav and
    <out>/conversations/index.json. Returns the index. `names`: more folders of
    creature templates for speaker names (a speaker pulled on its own, the mabari)."""
    pull, out = Path(pull_dir), Path(out_dir)
    json_dir = pull / "json"
    picked, warnings = pick_conversations(json_dir)
    owners = conversation_owners(json_dir)
    banks = {p.stem.lower(): p for p in pull.rglob("*.fsb")}
    (out / "conversations").mkdir(parents=True, exist_ok=True)

    index = {"Conversations": {}, "Warnings": warnings}
    for name, path in picked.items():
        conv = json.loads(path.read_text(encoding="utf-8"))
        bank_name = conv.get("vo_bank") if isinstance(conv.get("vo_bank"), str) else ""
        bank_path = banks.get(bank_name.lower()) if bank_name else None
        bank = fsb.FSB.open(bank_path) if bank_path else None
        owner = pick_owner(name, owners.get(name, []))
        rt = unreal.conversation(conv, owner=owner, names_dir=[json_dir, *(names or [])], true_flags=true_flags,
                                 plots=plots,
                                 vo_samples=bank.names() if bank else None)
        if bank_name and not bank:
            rt["Warnings"].append(f"voice bank {bank_name}.fsb not found")
        (out / "conversations" / f"{name}.json").write_text(
            json.dumps(rt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        voiced = [l["Vo"] for l in rt["Lines"] if l["Vo"]]
        if voice and bank and voiced:
            vo_dir = out / "vo" / rt["VoBank"]
            vo_dir.mkdir(parents=True, exist_ok=True)
            wanted = set(voiced)
            for s in bank.samples:
                if s.stem not in wanted or s.codec != "mpeg":
                    continue
                mp3_path = vo_dir / f"{s.stem}.mp3"
                mp3_path.write_bytes(fsb.mp3(s))
                rate, channels, bits, pcm = mfdecode.decode(str(mp3_path.resolve()))
                (vo_dir / f"{s.stem}.wav").write_bytes(mfdecode.pcm_wav(rate, channels, bits, pcm))
                mp3_path.unlink()

        spoken = [l for l in rt["Lines"] if not l["IsPlayer"] and l["Text"]]
        index["Conversations"][name] = {
            "Owner": owner,
            "OwnerName": rt["SpeakerNames"].get("OWNER", ""),
            "UsedBy": owners.get(name, []),
            "Source": path.parent.name,
            "Lines": len(rt["Lines"]),
            "SpokenLines": len(spoken),
            "VoicedLines": len(voiced),
            "Warnings": rt["Warnings"],
        }
    index["Cutscenes"] = {}
    cut_files = {}
    for p in sorted(Path(pull).rglob("*.cut")):
        cut_files.setdefault(p.stem.lower(), p)
    (out / "cutscenes").mkdir(parents=True, exist_ok=True)
    for name, cut in cutscene.scan(pull).items():
        caption = not cut["Conversation"] and name in cutscene.CAPTIONS
        conv = cutscene.conversation_for(name, {name: cut}) or ""
        staged = 0
        if conv and name in cut_files:  # where its characters stand, by the conversation Unreal plays for it
            stage = cutscene.staging(GFF4.open(cut_files[name]))
            if stage["ActorTags"]:
                stage.update({"Format": cutscene.STAGE_FORMAT, "Cutscene": name, "Conversation": conv})
                (out / "cutscenes" / f"{conv}.json").write_text(json.dumps(stage) + "\n", encoding="utf-8")
                staged = len(stage["ActorTags"])
        if caption:
            (out / "conversations" / f"{name}.json").write_text(
                json.dumps(cutscene.caption_conversation(name), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        index["Cutscenes"][name] = {"Length": cut["Length"], "Area": cut["Area"], "Lines": len(cut["Lines"]),
                                    "Conversation": conv, "Caption": caption, "Staged": staged}
    (out / "conversations" / "index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return index
