"""daotools: inspect and convert Dragon Age: Origins data from your own install.

Examples:
  daotools scan  "C:/Program Files (x86)/Steam/steamapps/common/Dragon Age Ultimate Edition"
  daotools find  <game_dir> "bhn*"
  daotools pull  <game_dir> "bhn*" --out extracted/human_noble
  daotools erf list <archive.erf>
  daotools gff dump <file> [--out file.json]
  daotools tlk dump <file.tlk> --out strings.json
  daotools gda dump <file.gda> [--names columns.txt] --out table.json
  daotools cnv export <file.cnv> --tlk core_en-us.tlk --out conv.json
  daotools plo list <folder of .plo files> --out plots.json
  daotools toolset scripts --pattern "bhn*" --out extracted/scripts/src
  daotools fsb list <bank.fsb>
  daotools fsb extract <bank.fsb> --out <folder>
  daotools unreal conv <name.dlg.conv.json> --names <pull json dir> --plots <plo dir> --vo <bank.fsb>
                       --out runtime.json
  daotools unreal origin <pull dir> --plots <plo dir> --true-flag GEN_GENDER_MALE --out extracted/ue
  daotools unreal plots --src extracted/scripts/src --plots <plo dir> --only "bhn*,gen00pt_party"
                        --cutscenes <pull dir> --out extracted/ue/plots.json
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import sys
from collections import Counter
from pathlib import Path

from . import abilities, ambient, area, balance, cnv, cutscene, fsb, gda, kit, mfdecode, origin, plo, plotlogic, simulate, stats, tactics, threat, toolset, unreal
from .erf import ERF, ERFError, is_erf
from .gda import GDA
from .fields import NAMES
from .gff3 import GFF3, GFF3Error, is_gff3
from .gff4 import GFF4, GFF4Error, to_jsonable
from .tlk import TalkTable, TalkTables

def _write(text: str, out: str | None) -> None:
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(text, encoding="utf-8")
        print(f"wrote {out}", file=sys.stderr)
    else:
        sys.stdout.write(text)


def _json(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def _walk(game_dir: str):
    for dirpath, _dirs, files in os.walk(game_dir):
        for f in files:
            yield Path(dirpath) / f


def _archives(game_dir: str):
    for p in _walk(game_dir):
        if is_erf(p):
            yield p


def _ext(name: str) -> str:
    return name.rsplit(".", 1)[1].lower() if "." in name else ""


# --- scan / find / pull -----------------------------------------------------

def cmd_scan(args) -> int:
    report = {"game_dir": args.game_dir, "archives": [], "loose_by_extension": {}, "talk_tables": []}
    loose = Counter()
    archive_paths = set()
    for p in _archives(args.game_dir):
        archive_paths.add(p)
        try:
            with ERF.open(p) as erf:
                by_ext = Counter(e.extension for e in erf.entries)
                report["archives"].append({
                    "path": str(p), "version": erf.version, "resources": len(erf.entries),
                    "encrypted": erf.encrypted, "by_extension": dict(by_ext.most_common()),
                })
        except ERFError as e:
            report["archives"].append({"path": str(p), "error": str(e)})
    for p in _walk(args.game_dir):
        if p in archive_paths:
            continue
        loose[p.suffix.lower().lstrip(".")] += 1
        if p.suffix.lower() == ".tlk":
            report["talk_tables"].append(str(p))
    report["loose_by_extension"] = dict(loose.most_common())

    total = Counter()
    for a in report["archives"]:
        total.update(a.get("by_extension", {}))
    print(f"{len(report['archives'])} archives, {sum(total.values())} archived resources, "
          f"{sum(loose.values())} loose files, {len(report['talk_tables'])} talk tables", file=sys.stderr)
    print("archived resources by type: " + ", ".join(f"{k or '?'}={v}" for k, v in total.most_common(15)),
          file=sys.stderr)
    _write(_json(report), args.out)
    return 0


def _matches(game_dir: str, pattern: str):
    """Yield (archive path or None, resource name, size, loader) for every match."""
    pat = pattern.lower()
    for p in _archives(game_dir):
        try:
            erf = ERF.open(p)
        except ERFError as e:
            print(f"skip {p}: {e}", file=sys.stderr)
            continue
        with erf:
            for entry in erf.entries:
                if fnmatch.fnmatch(entry.name.lower(), pat):
                    yield p, entry.name, entry.size, (lambda erf=erf, entry=entry: erf.read(entry))
    for p in _walk(game_dir):
        if fnmatch.fnmatch(p.name.lower(), pat) and not is_erf(p):
            yield None, p.name, p.stat().st_size, (lambda p=p: p.read_bytes())


def cmd_find(args) -> int:
    n = 0
    for archive, name, size, _load in _matches(args.game_dir, args.pattern):
        print(f"{archive or '(loose)'} :: {name} ({size} bytes)")
        n += 1
    print(f"{n} matches", file=sys.stderr)
    return 0


def _find_talk_tables(game_dir: str, lang: str) -> list[Path]:
    found = [p for p in _walk(game_dir) if p.suffix.lower() == ".tlk" and lang.lower() in p.name.lower()]

    # The base game's single player module first, then the core game, then DLC.
    def rank(p: Path) -> tuple:
        rel = str(p.relative_to(game_dir)).lower().replace("\\", "/")
        if rel.startswith("modules/single player/"):
            return (0, rel)
        if rel.startswith("packages/core/"):
            return (1, rel)
        return (2, rel)

    return sorted(found, key=rank)


def cmd_pull(args) -> int:
    out = Path(args.out)
    raw_dir, json_dir = out / "raw", out / "json"
    tlk = None
    if not args.no_tlk:
        paths = [Path(t) for t in args.tlk] if args.tlk else _find_talk_tables(args.game_dir, args.lang)
        tables = []
        for p in paths:
            try:
                tables.append(TalkTable.open(p))
            except Exception as e:  # keep going without that table
                print(f"skip talk table {p}: {e}", file=sys.stderr)
        tlk = TalkTables(tables)
        print(f"loaded {len(tables)} talk tables, {sum(len(t) for t in tables)} strings", file=sys.stderr)

    counts, formats, failures = Counter(), Counter(), []
    summary = {}
    for archive, name, _size, load in _matches(args.game_dir, args.pattern):
        where = archive.stem if archive else "loose"
        try:
            data = load()
        except ERFError as e:
            failures.append(f"{where}/{name}: {e}")
            continue
        target = raw_dir / where / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        counts[_ext(name)] += 1
        fmt = _format(data)
        summary[f"{where}/{name}"] = fmt
        formats[f"{_ext(name)}: {fmt}"] += 1
        if fmt.startswith(("GFF V4", "GFF3")):
            try:
                _convert(data, name, json_dir / where, tlk)
            except Exception as e:
                failures.append(f"{where}/{name}: {type(e).__name__}: {e}")
                summary[f"{where}/{name}"] = f"{fmt} (FAILED: {type(e).__name__}: {e})"
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(_json({"formats": dict(formats.most_common()), "files": summary}),
                                      encoding="utf-8")
    print("extracted: " + (", ".join(f"{k}={v}" for k, v in counts.most_common()) or "nothing"), file=sys.stderr)
    print("formats:", file=sys.stderr)
    for k, v in sorted(formats.items()):
        print(f"  {k} x{v}", file=sys.stderr)
    for f in failures:
        print(f"FAILED {f}", file=sys.stderr)
    print(f"{len(failures)} conversion failures; details in {out / 'summary.json'}", file=sys.stderr)
    return 1 if failures and not counts else 0


def _format(data: bytes) -> str:
    """A short label for what a resource is, from its header."""
    if is_gff3(data):
        return f"GFF3 {data[:4].decode('ascii', 'replace').strip()} {data[4:8].decode('ascii')}"
    if data[:4] == b"GFF ":
        if data[4:6] == b"V4" and len(data) >= 20:
            kind = data[12:16].decode("ascii", "replace").strip()
            return f"GFF {data[4:8].decode('ascii', 'replace')} {kind} {data[16:20].decode('ascii', 'replace')}"
        return f"GFF {data[4:8].decode('ascii', 'replace')} {data[8:12].decode('ascii', 'replace').strip()}"
    if not data:
        return "empty"
    head = data[:4]
    if all(32 <= b < 127 for b in head):
        return f"other ({head.decode('ascii')})"
    return "other (binary)"


def _convert(data: bytes, name: str, out_dir: Path, tlk: TalkTables | None) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    if is_gff3(data):
        (out_dir / f"{name}.json").write_text(_json(_gff_doc(GFF3(data, name), tlk)), encoding="utf-8")
        return
    gff = GFF4(data, name)
    # The full field-by-field dump is always written: it is what the
    # specialised exporters below are checked against.
    (out_dir / f"{name}.json").write_text(_json(_gff_doc(gff, tlk)), encoding="utf-8")
    if cnv.is_conversation(gff):
        conv = cnv.export(gff, tlk, Path(name).stem)
        (out_dir / f"{name}.conv.json").write_text(_json(conv), encoding="utf-8")
        (out_dir / f"{name}.txt").write_text(cnv.transcript(conv), encoding="utf-8")
    elif gff.file_type == "G2DA":
        table = gda.GDA(gff)
        (out_dir / f"{name}.table.json").write_text(
            _json({"columns": table.columns, "rows": table.rows}), encoding="utf-8")


def _gff_doc(gff, tlk: TalkTables | None = None) -> dict:
    resolve = tlk.get if tlk else None
    if isinstance(gff, GFF3):
        fmt = f"GFF3 {gff.file_type.strip()} {gff.version}"
    else:
        fmt = f"{gff.version} {gff.platform.strip()} {gff.file_type.strip()} {gff.type_version}"
    return {"format": fmt, "root": to_jsonable(gff.root, NAMES, resolve=resolve)}


def _open_gff(path: str):
    data = Path(path).read_bytes()
    return GFF3(data, path) if is_gff3(data) else GFF4(data, path)


# --- single-file commands ---------------------------------------------------

def cmd_erf_list(args) -> int:
    with ERF.open(args.archive) as erf:
        print(f"{args.archive}: ERF {erf.version}, {len(erf.entries)} resources, "
              f"encrypted={erf.encrypted}, compression={erf.compression}", file=sys.stderr)
        for e in erf.entries:
            print(f"{e.name}\t{e.size}")
    return 0


def cmd_erf_extract(args) -> int:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    with ERF.open(args.archive) as erf:
        for e in erf.entries:
            if args.pattern and not fnmatch.fnmatch(e.name.lower(), args.pattern.lower()):
                continue
            (out / e.name).write_bytes(erf.read(e))
            n += 1
    print(f"extracted {n} files to {out}", file=sys.stderr)
    return 0


def cmd_gff_dump(args) -> int:
    tlk = TalkTables.open(args.tlk) if args.tlk else None
    _write(_json(_gff_doc(_open_gff(args.file), tlk)), args.out)
    return 0


def cmd_tlk_dump(args) -> int:
    t = TalkTable.open(args.file)
    _write(_json({str(k): v for k, v in sorted(t.strings.items())}), args.out)
    return 0


def cmd_gda_dump(args) -> int:
    names = Path(args.names).read_text(encoding="utf-8").split() if args.names else None
    table = gda.GDA.open(args.file, names)
    _write(_json({"columns": table.columns, "rows": table.rows}), args.out)
    return 0


def cmd_cnv_export(args) -> int:
    tlk = TalkTables.open(args.tlk) if args.tlk else None
    conv = cnv.export(GFF4.open(args.file), tlk)
    _write(cnv.transcript(conv) if args.transcript else _json(conv), args.out)
    return 0


def cmd_plo_list(args) -> int:
    plots = plo.load_dir(args.folder)
    print(f"{len(plots)} plots, {sum(len(p['flags']) for p in plots.values())} flags", file=sys.stderr)
    _write(_json({guid: {"name": p["name"], "script": p["script"],
                         "flags": {str(k): v for k, v in sorted(p["flags"].items())}}
                  for guid, p in sorted(plots.items(), key=lambda kv: kv[1]["name"])}), args.out)
    return 0


def cmd_fsb_list(args) -> int:
    bank = fsb.FSB.open(args.file)
    print(f"{args.file}: {len(bank.samples)} samples", file=sys.stderr)
    for s in bank.samples:
        print(f"{s.name}\t{s.codec}\t{s.frequency} Hz\t{s.channels} ch\t{s.seconds:.2f} s")
    return 0


def cmd_fsb_extract(args) -> int:
    bank = fsb.FSB.open(args.file)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    written, skipped = 0, Counter()
    for s in bank.samples:
        if s.codec != "mpeg":
            skipped[s.codec] += 1
            continue
        mp3_path = out / f"{s.stem}.mp3"
        mp3_path.write_bytes(fsb.mp3(s))
        if not args.mp3:
            # Unreal's media player only plays PCM through the system mixer.
            rate, channels, bits, pcm = mfdecode.decode(str(mp3_path.resolve()))
            (out / f"{s.stem}.wav").write_bytes(mfdecode.pcm_wav(rate, channels, bits, pcm))
            mp3_path.unlink()
        written += 1
    print(f"wrote {written} .{'mp3' if args.mp3 else 'wav'} files to {out}"
          + "".join(f"; skipped {n} {codec}" for codec, n in skipped.items()), file=sys.stderr)
    return 0


def _true_flags(flags: list[str] | None, plots: dict | None) -> list[str]:
    keys = []
    for flag in flags or []:
        if ":" not in flag:
            if plots is None:
                raise ValueError(f"--true-flag {flag}: flag names need --plots")
            flag = plo.flag_key(plots, flag)
        keys.append(flag)
    return keys


def cmd_unreal_origin(args) -> int:
    plots = plo.load_dir(args.plots) if args.plots else None
    index = origin.export(args.pull, args.out, plots=plots, true_flags=_true_flags(args.true_flag, plots),
                          voice=not args.no_vo, names=args.names)
    convs = index["Conversations"]
    for name, c in convs.items():
        print(f"{name}: {c['Lines']} lines, {c['VoicedLines']}/{c['SpokenLines']} spoken lines voiced, "
              f"owner {c['Owner']}" + (f", {len(c['Warnings'])} warnings" if c["Warnings"] else ""),
              file=sys.stderr)
    for name, c in index.get("Cutscenes", {}).items():
        print(f"cutscene {name}: {c['Length']} s, plays " + (c["Conversation"] or "nothing (no lines, no caption)")
              + (" (caption)" if c["Caption"] else ""), file=sys.stderr)
    for w in index["Warnings"]:
        print(f"warning: {w}", file=sys.stderr)
    print(f"{len(convs)} conversations, {sum(c['VoicedLines'] for c in convs.values())} of "
          f"{sum(c['SpokenLines'] for c in convs.values())} spoken lines voiced; "
          f"index in {Path(args.out) / 'conversations' / 'index.json'}", file=sys.stderr)
    return 0


def cmd_toolset_scripts(args) -> int:
    index = toolset.export(args.out, args.pattern)
    print(f"wrote {len(index)} scripts ({sum(s['bytes'] for s in index.values()) // 1024} KB) to {args.out}",
          file=sys.stderr)
    return 0


def cmd_unreal_area(args) -> int:
    are_root = json.loads(Path(args.file).read_text(encoding="utf-8"))["root"]
    layout_root = to_jsonable(GFF4.open(args.layout).root, NAMES)
    solids, lights, fixtures = None, None, None
    if args.rooms:
        rooms = [json.loads(f.read_text(encoding="utf-8"))["root"] for f in sorted(Path(args.rooms).rglob("*.rml.json"))]
        names = kit.placed_models(rooms)
        if args.game:
            got = kit.pull(args.game, names, args.kit)
            print(f"kit: {got['Files']} files, {len(got['Missing'])} models without any", file=sys.stderr)
        pieces = kit.load_kit(args.kit, names)
        kit_map = json.loads(Path(args.kit_map).read_text(encoding="utf-8")) if Path(args.kit_map).exists() else {}
        content = Path(args.content)
        meshes = kit.kit_meshes(rooms, pieces, kit_map,
                                lambda path: (content / (path.removeprefix("/Game/") + ".uasset")).exists())
        solids = kit.solids(rooms, pieces, skip=meshes["Mapped"])
        print(f"kit: {solids['Summary']}; {len(meshes['KitPlaced']) // 13} pieces as {len(meshes['KitMeshes'])} meshes "
              f"({len(meshes['Mapped'])} models mapped)", file=sys.stderr)
        lights = kit.lights(rooms, kit.load_light_models(args.rooms))
        fixtures = kit.fixtures(rooms)
    door_models = None
    if args.game or args.placeable_types:
        if args.game:
            with ERF.open(Path(args.game) / "packages" / "core" / "data" / "2da.erf") as erf:
                gda_records = GDA(GFF4(erf.read("placeable_types.gda")), ["ID", "Label", "ModelName"]).records()
        else:
            gda_records = GDA.open(args.placeable_types, ["ID", "Label", "ModelName"]).records()
        doors = {n: t for n, t in area.placeable_templates(args.pull).items() if area.is_door(n, n)}
        models = kit.door_model_names(doors, gda_records)
        if args.game:
            kit.pull(args.game, models, args.kit)
        door_models = kit.door_models(doors, gda_records, kit.load_kit(args.kit, models))
        print(f"doors: {len(door_models)} door templates sized from their models", file=sys.stderr)
    creature_stats, player, ambient_tables, tactic_menu = None, None, None, None
    if args.game:
        ambient_tables = ambient.load_tables(args.game)
        tables = stats.load_tables(args.game, overrides=args.mod_tables)
        items = {p.name[:-len(".uti.json")].lower(): json.loads(p.read_text(encoding="utf-8"))["root"]
                 for p in sorted(Path(args.items).rglob("*.uti.json"))} if Path(args.items).exists() else {}

        templates = area.creature_templates(args.pull)
        appearance = lambda utc: int((utc.get("Appearance Data") or {}).get("Appearance_Type") or 0)
        anims = stats.attack_anims(args.game, tables, {appearance(u) for u in templates.values()})
        ai_tables = tactics.load_tables(args.game)
        table = abilities.talents(tables)

        def chest_label(equip):
            """The itemstats label of the chest piece worn ("Armor - Light"...), for the threat it draws."""
            ref = stats.equipment(equip, items, tables)["Outfit"].get("chest", "")
            return str(tables["itemstats"].get(int((items.get(ref) or {}).get("BaseItem") or -1), {}).get("label") or "")

        area_name = Path(args.file).name.split(".")[0]

        def creature_stats(utc):
            # what it wears (the look) from its template; its natural bite and hide count for the numbers, and so
            # do what the area's script puts on it and a follower's weapon (area.AREA_EQUIP, stats.FOLLOWER_WEAPONS)
            tag = str(utc.get("Tag") or "")
            worn = utc.get("Equip_ItemList") or []
            extra = [{"TemplateResRef": r} for r in area.AREA_EQUIP.get(area_name, {}).get(tag, [])
                     + ([stats.FOLLOWER_WEAPONS[tag]] if tag in stats.FOLLOWER_WEAPONS else [])]
            fighting = extra + worn
            equip = fighting + stats.natural_equipment(appearance(utc), fighting, items, tables)
            st = stats.stats(tables, package=int(utc.get("Package") or 0), rank=int(utc.get("Rank") or 0),
                             area_level=args.area_level, race=int(utc.get("Race") or 0) or None,
                             base_item=stats.weapon_base_item(equip, items, tables["itemstats"]),
                             weapon_material=int((stats.weapon_item(equip, items, tables["itemstats"]) or {}).get("Material") or 0),
                             follower=utc.get("Tag") if utc.get("Tag") in area.FOLLOWERS else "",
                             one_shot=stats.is_one_shot(appearance(utc), tables))
            st["Interval"] = stats.attack_interval(equip, items, tables, anims.get(appearance(utc)))
            rank = int(utc.get("Rank") or 0)
            st["Status"] = [float(st["Level"]), abilities.effect_duration(1.0, rank, tables, abilities.PARTY_SLOTS),
                            abilities.resist_chance(rank, tables, attribute=player["Attributes"]["Str"],
                                                    level_difference=player["Level"] - st["Level"]),
                            threat.seen_threat(chest_label(fighting)), 1.0 if st.get("Class") == "Rogue" else 0.0]
            numbers = stats.equipment(equip, items, tables)
            st = {**st, **numbers, "Outfit": stats.equipment(worn, items, tables)["Outfit"]}
            # its package's talents at its level, or a follower's (passives folded in), and its tactics table
            # (stage 4); a follower in the party runs its tactic slots instead, filled from its package's
            # FollowerTacticsTable
            package = int(utc.get("Package") or 0)
            cls_id = int(tables["packages_base"].get(package, {}).get("StartingClass") or 1)
            if tag in area.FOLLOWERS:
                known = abilities.follower_talents(
                    tables, stats.FOLLOWER_LEVELUP.get(tag) or stats.HERO_LEVELUP.get(cls_id, ""), int(st["Level"]),
                    st.get("Attributes") or {}, cls_id, area.HIRED_AT.get(tag, 0))
            else:
                known = tactics.package_talents(ai_tables, package, int(st["Level"]))
            st = abilities.with_passives(st, known, table, stats.CLASS_ROGUE if st.get("Class") == "Rogue" else 1)
            st["TalentRows"] = [abilities.talent_row(i, table[i], st) for i in known
                                if i in table and table[i]["Use"] != abilities.PASSIVE][:tactics.MAX_TALENTS]
            st["Tactics"] = ai_tables["tactics"].get(int(utc.get("PackageAI") or 0), [])
            st["Traits"] = tactics.traits(cls_id, int(utc.get("Race") or 0),
                                          int((utc.get("Appearance Data") or {}).get("Gender") or 0), rank,
                                          chest_label(fighting))
            if tag in area.FOLLOWERS:
                st["PartyTactics"] = tactics.follower_tactics(ai_tables, package, int(st["Level"]), known)
                st["TacticSlots"] = tactics.slots(ai_tables, int(st["Level"]), known)
            shield = int((items.get(st["Outfit"].get("shield", "")) or {}).get("BaseItem") or 0)
            offhand = stats.stats(tables, package=int(utc.get("Package") or 0), rank=rank, area_level=args.area_level,
                                  race=int(utc.get("Race") or 0) or None, base_item=shield)["Damage"] if shield \
                else (0.0, 0.0)
            bow = tables["itemstats"].get(stats.weapon_base_item(equip, items, tables["itemstats"]) or -1) or {}
            st["Status"] += [st.get("Stamina", 0.0), st.get("Fatigue", 0.0), *offhand,
                             float(bow.get("OptimumRange") or 0.0), st.get("MissileDeflection", 0.0)]
            return st

        # The Human Noble starts as a level 1 human warrior (background_defaults row 3105: its template's
        # equipment), with a longsword (base item 2) when the template is not given.
        equip = (json.loads(Path(args.player_template).read_text(encoding="utf-8"))["root"].get("Equip_ItemList")
                 if args.player_template else [])
        cls = stats.CLASS_ROGUE if args.player_class == "rogue" else 1
        gear = stats.equipment(equip, items, tables)
        known = abilities.known_talents(tables, cls, args.talents, "shield" in gear["Outfit"])
        player = stats.stats(tables, package=0, rank=stats.RANK_PLAYER, area_level=args.area_level, race=3,
                             base_item=stats.weapon_base_item(equip, items, tables["itemstats"]) or 2, player_class=cls,
                             hero=True, lethality=abilities.LETHALITY in known,
                             weapon_material=int((stats.weapon_item(equip, items, tables["itemstats"]) or {}).get("Material") or 0))
        player.update(gear)
        player["Interval"] = stats.attack_interval(equip, items, tables)
        shield = int((items.get(gear["Outfit"].get("shield", "")) or {}).get("BaseItem") or 0)
        if shield:  # Shield Bash strikes with the shield: no damage of its own, the strength bonus
            player["Offhand"] = stats.stats(tables, package=0, rank=stats.RANK_PLAYER, area_level=args.area_level,
                                            race=3, base_item=shield, player_class=cls, hero=True)["Damage"]
        if args.talents == "start":  # and the automatic level-ups' picks, those stage 2 and 4 have
            picks = abilities.levelup_talents(tables, cls, int(player["Level"]), known, player["Attributes"])
            known += [i for i in picks if i in abilities.STAGE + abilities.ENEMY]
            if [i for i in picks if i not in known]:
                print("level-up talents not ported yet:", [abilities.NAMES.get(i, i) for i in picks if i not in known],
                      file=sys.stderr)
        player = abilities.with_passives(player, known, table, cls)
        player["Rogue"] = cls == stats.CLASS_ROGUE
        player["SeenThreat"] = threat.seen_threat(chest_label(equip))
        bow = stats.weapon_base_item(equip, items, tables["itemstats"], weapon_set=1)
        if bow and stats.is_ranged(tables["itemstats"].get(bow, {})):  # the other weapon set: the Human Noble's shortbow
            b = stats.stats(tables, package=0, rank=stats.RANK_PLAYER, area_level=args.area_level, race=3, base_item=bow,
                            player_class=cls, hero=True, weapon_material=int(
                                (stats.weapon_item(equip, items, tables["itemstats"], 1) or {}).get("Material") or 0))
            player["Bow"] = [*b["Damage"], b["Penetration"], b["Crit"],
                             stats.attack_interval(equip, items, tables, weapon_set=1),
                             float(tables["itemstats"][bow].get("OptimumRange") or 0.0)]
        player["TalentRows"] = [abilities.talent_row(i, table[i], player) for i in known
                                if i in table and table[i]["Use"] != abilities.PASSIVE]
        player["Passives"] = [i for i in known if i in table and table[i]["Use"] == abilities.PASSIVE]
        player["Tactics"] = tactics.hero_tactics(ai_tables, cls, int(player["Level"]), known)
        player["TacticSlots"] = tactics.slots(ai_tables, int(player["Level"]), known)
        hm = json.loads(Path(args.player_template).read_text(encoding="utf-8"))["root"] if args.player_template else {}
        gender = int((hm.get("Appearance Data") or {}).get("Gender") or 1)  # the template's; male without one
        player["Traits"] = tactics.traits(cls, 3, gender, stats.RANK_PLAYER, chest_label(equip))
        talk = TalkTables([TalkTable.open(p) for p in _find_talk_tables(args.game, "en-us")])
        tactic_menu = tactics.menu(ai_tables, talk.get)
        print(f"talents: {', '.join(table[i]['Name'] for i in known if i in table) or 'none'}; fatigue "
              f"{player['Fatigue']}%", file=sys.stderr)
        print(f"player: {player['Attributes']}, {player['Health']} health, attack {player['Attack']}, defense {player['Defense']} "
              f"+ {player['ShieldDefense']}, damage {player['Damage']} + {player['DamageBonus']}, "
              f"armour {player['Armour']}, an attack every {player['Interval']} s", file=sys.stderr)
    out = area.area(are_root, layout_root, area.creature_templates(args.pull), start=args.start or "",
                    solids=solids, door_models=door_models, creature_stats=creature_stats, player=player,
                    ambient_tables=ambient_tables, trigger_templates=area.trigger_templates(args.pull),
                    extra_creatures=[tuple(x.split("@", 1)) for x in args.add_creature or []], lights=lights,
                    fill=args.fill_lights,
                    fill_tint=area.WARM_FILL_COLOUR if args.warm_fills else area.FILL_COLOUR, fixtures=fixtures,
                    soften=0.3 if args.warm_fills else None, tactic_menu=tactic_menu)
    s = out["Summary"]
    print(f"{out['Area']}: {s['Floors']} floor boxes, {s['Walls']} grid walls, {s['Solids']} kit solids "
          f"({s['DoorwaysCut']} doorways cut, {s['DoorFrames']} door frames, "
          f"{s['HangingPropsDropped']} hanging props dropped, {s['Ceilings']} ceilings, {s['Lids']} of them lids), "
          f"{s['Lights']} lights ({s['FillLights']} of them fills, {s['LightsTucked']} moved under a ceiling), "
          f"{s['Fixtures']} lamps, {s['Fires']} fires ({s['CandleLightsDimmed']} candle lights dimmed), {s['TalkingCreatures']} talking "
          f"creatures and {s['TeamOnly']} more in {s['Teams']} teams ({s['Inactive']} hidden at first, "
          f"{s['OtherCreatures']} others, {s['Ambient']} with ambient behaviour), "
          f"{s['Waypoints']} waypoints, {s['Doors']} doors, {len(out['Labels'])} room labels", file=sys.stderr)
    for w in out["Warnings"]:
        print(f"warning: {w}", file=sys.stderr)
    if args.rooms:
        out["KitMeshes"], out["KitPlaced"] = meshes["KitMeshes"], meshes["KitPlaced"]
    _write(json.dumps(out, ensure_ascii=False) + "\n", args.out)
    return 0


def cmd_unreal_plots(args) -> int:
    plots = plo.load_dir(args.plots)
    cuts = cutscene.scan(args.cutscenes) if args.cutscenes else None
    out = plotlogic.export(args.src, plots, only=args.only, true_flags=_true_flags(args.true_flag, plots),
                           cutscenes=cuts)
    for name, p in out["Plots"].items():
        print(f"{name}: {sum(1 for a in p['Cases'].values() if a)} flags with actions, "
              f"{len(p['Skipped'])} skipped", file=sys.stderr)
        for skip in p["Skipped"]:
            print(f"  skipped {skip}", file=sys.stderr)
    for name, e in out["Events"].items():
        print(f"{name}: {len(e['Cases'])} death/team events, {len(e['Skipped'])} skipped", file=sys.stderr)
        for skip in e["Skipped"]:
            print(f"  skipped {skip}", file=sys.stderr)
    _write(_json(out), args.out)
    return 0


def cmd_unreal_balance(args) -> int:
    names = balance.script_column_names(*args.scripts)
    talk = TalkTable.open(args.tlk) if args.tlk else None
    out = balance.export(args.game_tables, args.mod_tables, names, talk, source=args.source)
    for table, t in out["Tables"].items():
        print(f"{table}: {len(t['Changed'])} rows changed, {len(t['New'])} new", file=sys.stderr)
    _write(_json(out), args.out)
    return 0


def cmd_unreal_simulate(args) -> int:
    out = []
    for path in args.area:
        a = json.loads(Path(path).read_text(encoding="utf-8"))
        sim = simulate.simulate(a, args.party, args.foes, runs=args.runs, seed=args.seed, wave=args.wave,
                                flank=not args.no_flanking, slots=args.slots, talents=not args.no_talents,
                                use_threat=not args.no_threat, allies=args.allies)
        sim["File"] = Path(path).name
        print(simulate.report(sim, Path(path).name))
        out.append(sim)
    if args.out:
        _write(_json(out), args.out)
    return 0


def cmd_unreal_conv(args) -> int:
    conv = json.loads(Path(args.file).read_text(encoding="utf-8"))
    plots = plo.load_dir(args.plots) if args.plots else None
    vo_samples = fsb.FSB.open(args.vo).names() if args.vo else None
    true_flags = _true_flags(args.true_flag, plots)
    owner = args.owner
    if not owner and args.names:
        name = (conv.get("conversation") or "").lower()
        users: list[str] = []
        for d in args.names:
            users += [t for t in origin.conversation_owners(d).get(name, []) if t not in users]
        owner = origin.pick_owner(name, users)
    out = unreal.conversation(conv, owner=owner, names_dir=args.names, true_flags=true_flags,
                              plots=plots, vo_samples=vo_samples)
    for w in out["Warnings"]:
        print(f"warning: {w}", file=sys.stderr)
    _write(_json(out), args.out)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="daotools", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("scan", help="inventory every archive and loose file in the install")
    s.add_argument("game_dir")
    s.add_argument("--out", help="write the JSON report here instead of stdout")
    s.set_defaults(func=cmd_scan)

    s = sub.add_parser("find", help="find resources by name pattern, e.g. 'bhn*' or '*.cnv'")
    s.add_argument("game_dir")
    s.add_argument("pattern")
    s.set_defaults(func=cmd_find)

    s = sub.add_parser("pull", help="extract every matching resource and convert what we can to JSON")
    s.add_argument("game_dir")
    s.add_argument("pattern")
    s.add_argument("--out", required=True)
    s.add_argument("--lang", default="en-us", help="talk table language to auto-detect (default en-us)")
    s.add_argument("--tlk", action="append", help="talk table(s) to use instead of auto-detecting")
    s.add_argument("--no-tlk", action="store_true", help="skip loading talk tables")
    s.set_defaults(func=cmd_pull)

    erf = sub.add_parser("erf", help="ERF archives").add_subparsers(dest="erf_command", required=True)
    s = erf.add_parser("list")
    s.add_argument("archive")
    s.set_defaults(func=cmd_erf_list)
    s = erf.add_parser("extract")
    s.add_argument("archive")
    s.add_argument("--out", required=True)
    s.add_argument("--pattern")
    s.set_defaults(func=cmd_erf_extract)

    gff = sub.add_parser("gff", help="any GFF file (V3 or V4)").add_subparsers(dest="gff_command", required=True)
    s = gff.add_parser("dump")
    s.add_argument("file")
    s.add_argument("--tlk", action="append", help="talk table(s) for resolving text; repeatable")
    s.add_argument("--out")
    s.set_defaults(func=cmd_gff_dump)

    tlk = sub.add_parser("tlk", help="talk tables").add_subparsers(dest="tlk_command", required=True)
    s = tlk.add_parser("dump")
    s.add_argument("file")
    s.add_argument("--out")
    s.set_defaults(func=cmd_tlk_dump)

    g = sub.add_parser("gda", help="data tables").add_subparsers(dest="gda_command", required=True)
    s = g.add_parser("dump")
    s.add_argument("file")
    s.add_argument("--names", help="text file of known column names, whitespace separated")
    s.add_argument("--out")
    s.set_defaults(func=cmd_gda_dump)

    c = sub.add_parser("cnv", help="conversations (.dlg/.cnv)").add_subparsers(dest="cnv_command", required=True)
    s = c.add_parser("export")
    s.add_argument("file")
    s.add_argument("--tlk", action="append", help="talk table(s) for resolving text; repeatable")
    s.add_argument("--transcript", action="store_true", help="readable script instead of JSON")
    s.add_argument("--out")
    s.set_defaults(func=cmd_cnv_export)

    u = sub.add_parser("unreal", help="files for the Unreal project").add_subparsers(
        dest="unreal_command", required=True)
    s = u.add_parser("conv", help="a .dlg.conv.json from pull, in the shape Unreal reads at runtime")
    s.add_argument("file")
    s.add_argument("--owner", help="tag of the creature that owns the conversation (default: the "
                                   "creature in --names whose DialogResRef is it, else its name)")
    s.add_argument("--names", action="append",
                   help="folder searched for <tag>.utc.json to name the speakers; repeatable")
    s.add_argument("--true-flag", action="append", metavar="GUID:FLAG|NAME",
                   help="plot flag that starts out set, e.g. GEN_GENDER_MALE (names need --plots); repeatable")
    s.add_argument("--plots", help="folder of extracted .plo files, to name the flags (FlagNames)")
    s.add_argument("--vo", help="the conversation's VO bank (.fsb), to fill each line's Vo")
    s.add_argument("--out")
    s.set_defaults(func=cmd_unreal_conv)
    s = u.add_parser("origin", help="every conversation in a pull folder, with voice, plus an index")
    s.add_argument("pull", help="folder written by `daotools pull` (json/ and raw/)")
    s.add_argument("--plots", help="folder of extracted .plo files, to name the flags")
    s.add_argument("--true-flag", action="append", metavar="GUID:FLAG|NAME",
                   help="plot flag that starts out set, e.g. GEN_GENDER_MALE; repeatable")
    s.add_argument("--no-vo", action="store_true", help="skip decoding the voice-over")
    s.add_argument("--names", action="append", help="another folder of creature templates (.utc.json) for "
                                                     "speaker names, e.g. extracted/dog/json; repeatable")
    s.add_argument("--out", required=True, help="e.g. extracted/ue")
    s.set_defaults(func=cmd_unreal_origin)
    s = u.add_parser("area", help="an area's walkable floor (from its layout's navigation grid) and "
                                  "talking creatures, for Unreal to spawn")
    s.add_argument("file", help="the area's .are.json from pull")
    s.add_argument("--layout", required=True, help="the area's layout .arl (packages/core/env/<Layout>.arl)")
    s.add_argument("--pull", required=True, help="pull json folder, for the creature templates")
    s.add_argument("--start", help="waypoint tag where the player starts")
    s.add_argument("--rooms", help="folder of the layout's room files (.rml.json, from pull) for walls, props, "
                                   "blockers and ceilings from the level kit instead of the navigation grid, "
                                   "and the rooms' lights (*_ll.mmh.json)")
    s.add_argument("--kit", default="extracted/kit/json", help="folder for the kit pieces' physics and hierarchy JSON")
    s.add_argument("--kit-map", default=str(Path(__file__).resolve().parents[1] / "unreal" / "kitmap.json"),
                   help="model name patterns -> Unreal meshes (default tools/unreal/kitmap.json)")
    s.add_argument("--content", default=str(Path(__file__).resolve().parents[2] / "Unreal" / "Cousland" / "Content"),
                   help="the Unreal project's Content folder: kit meshes not in it leave their pieces as boxes")
    s.add_argument("--game", help="game folder: pull the kit pieces the rooms use into --kit first")
    s.add_argument("--items", default="extracted/items/json", help="item templates (.uti.json, from pull "
                                                                    "'gen_im_wep*'), for the creatures' weapons")
    s.add_argument("--add-creature", action="append", metavar="TEMPLATE@WAYPOINT",
                   help="spawn a creature the game brings along (a party member) at a waypoint; repeatable")
    s.add_argument("--area-level", type=int, default=1, help="the level the area scales creatures to (default 1)")
    s.add_argument("--mod-tables", help="a rebalance mod's override tables (<table>_<suffix>.gda), applied over the "
                                        "game's for the combat numbers (docs/COMBAT_BALANCE.md)")
    s.add_argument("--player-class", choices=("warrior", "rogue"), default="warrior",
                   help="the hero's class (give the rogue template default_hm_noble_r with --player-template)")
    s.add_argument("--talents", default="start", help="the player's talents: start (character creation's and the "
                   "automatic level-ups' up to the area level), all "
                   "(the class's stage 2 tree, and Shield Bash with a shield), or ability ids separated by commas")
    s.add_argument("--player-template", help="the player's template (.utc.json, from pull 'default_hm_noble*'): "
                                             "the starting equipment; without it a longsword and nothing worn")
    s.add_argument("--fill-lights", type=float, default=0.0, metavar="BRIGHTNESS",
                   help="add dim fill lights (cool, see --warm-fills) of this brightness (e.g. 0.25) where the rooms' lights do not "
                        "reach the floor, standing in for the game's baked ambient light (night areas)")
    s.add_argument("--warm-fills", action="store_true",
                   help="make those fill lights warm (candle- and hearth-lit rooms by day) instead of cool, and turn "
                        "the game's own cool fills toward warm white too (area.soften_fills)")
    s.add_argument("--placeable-types", help="placeable_types.gda (else read from --game), to size doors from "
                                             "their models")
    s.add_argument("--out")
    s.set_defaults(func=cmd_unreal_area)
    s = u.add_parser("plots", help="what each plot's script does when a flag is set, as actions Unreal runs")
    s.add_argument("--src", required=True, help="script source folder from 'toolset scripts'")
    s.add_argument("--plots", required=True, help="folder of extracted .plo files")
    s.add_argument("--only", default="*", help="plot/script name patterns, comma separated, e.g. 'bhn*,gen00pt_party' (default: all)")
    s.add_argument("--true-flag", action="append", help="a flag that is always true (name or GUID:FLAG), e.g. "
                                                        "GEN_GENDER_MALE, as for 'unreal conv'; repeatable")
    s.add_argument("--cutscenes", help="folder with the .cut files (a pull folder), so a loaded cutscene plays "
                                       "the conversation its lines come from; without it only captions play")
    s.add_argument("--out")
    s.set_defaults(func=cmd_unreal_plots)

    s = u.add_parser("balance", help="a rebalance mod's data table changes against the game's tables, for combat")
    s.add_argument("--game-tables", required=True, help="folder of the game's .gda tables (abi_base.gda...)")
    s.add_argument("--mod-tables", required=True, help="folder of the mod's override tables (abi_base_ao.gda...)")
    s.add_argument("--scripts", action="append", required=True,
                   help="script source folder to read column names from; repeatable (the game's, the mod's)")
    s.add_argument("--tlk", help="the mod's talk table, for its names and descriptions")
    s.add_argument("--source", default="", help="the mod's name and version, written into the file")
    s.add_argument("--out")
    s.set_defaults(func=cmd_unreal_balance)

    s = u.add_parser("simulate", help="fight the party against foes many times with the game's hit rules")
    s.add_argument("area", nargs="+", help="area exports (daotools unreal area) to compare, e.g. with and without "
                                           "a rebalance mod's tables")
    s.add_argument("--party", action="append", default=[], metavar="TAG", help="a party member's tag; repeatable")
    s.add_argument("--allies", action="append", default=[], metavar="PATTERN",
                   help="creatures fighting on the party's side without being in it (fnmatch); repeatable")
    s.add_argument("--foes", action="append", required=True, metavar="PATTERN",
                   help="the foes' tags (fnmatch, e.g. 'bhn100cr_rat_giant_*'); repeatable")
    s.add_argument("--wave", type=int, default=0, help="foes in the fight at once; each death brings the next in")
    s.add_argument("--runs", type=int, default=1000)
    s.add_argument("--seed", type=int, default=1)
    s.add_argument("--no-flanking", action="store_true", help="never count an attacker as behind its target")
    s.add_argument("--no-talents", action="store_true", help="the player uses no talents (PlayerTalents ignored)")
    s.add_argument("--no-threat", action="store_true", help="foes keep a random party member instead of threat")
    s.add_argument("--slots", type=int, default=simulate.SLOTS,
                   help="foes attacking the same party member at once (provisional default %d; 0: no limit)" % simulate.SLOTS)
    s.add_argument("--out", help="write the results (JSON) here")
    s.set_defaults(func=cmd_unreal_simulate)

    f = sub.add_parser("fsb", help="FMOD sound banks (voice-over)").add_subparsers(
        dest="fsb_command", required=True)
    s = f.add_parser("list", help="samples in a bank: name, codec, rate, channels, length")
    s.add_argument("file")
    s.set_defaults(func=cmd_fsb_list)
    s = f.add_parser("extract", help="write every MPEG sample as a PCM <name>.wav for Unreal "
                                     "(decoded by Windows Media Foundation)")
    s.add_argument("file")
    s.add_argument("--out", required=True)
    s.add_argument("--mp3", action="store_true", help="write plain .mp3 files instead")
    s.set_defaults(func=cmd_fsb_extract)

    ts = sub.add_parser("toolset", help="the official toolset's database").add_subparsers(
        dest="toolset_command", required=True)
    s = ts.add_parser("scripts", help="copy script source (.nss) out of the toolset database")
    s.add_argument("--pattern", default="*", help="script name pattern, e.g. 'bhn*' (default: all)")
    s.add_argument("--out", required=True, help="e.g. extracted/scripts/src")
    s.set_defaults(func=cmd_toolset_scripts)

    pl = sub.add_parser("plo", help="plot files").add_subparsers(dest="plo_command", required=True)
    s = pl.add_parser("list", help="every plot under a folder: GUID, name, script and flag names")
    s.add_argument("folder")
    s.add_argument("--out")
    s.set_defaults(func=cmd_plo_list)
    return p


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 20000))
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (ERFError, GFF3Error, GFF4Error, fsb.FSBError, mfdecode.DecodeError, toolset.ToolsetError, OSError,
            ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
