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
  daotools fsb list <bank.fsb>
  daotools fsb extract <bank.fsb> --out <folder>
  daotools unreal conv <name.dlg.conv.json> --names <pull json dir> --plots <plo dir> --vo <bank.fsb>
                       --out runtime.json
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import sys
from collections import Counter
from pathlib import Path

from . import cnv, fsb, gda, plo, unreal
from .erf import ERF, ERFError, is_erf
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
        (out / f"{s.stem}.mp3").write_bytes(s.data[:fsb.mpeg_end(s.data)] or s.data)
        written += 1
    print(f"wrote {written} .mp3 files to {out}"
          + "".join(f"; skipped {n} {codec}" for codec, n in skipped.items()), file=sys.stderr)
    return 0


def cmd_unreal_conv(args) -> int:
    conv = json.loads(Path(args.file).read_text(encoding="utf-8"))
    plots = plo.load_dir(args.plots) if args.plots else None
    vo_samples = fsb.FSB.open(args.vo).names() if args.vo else None
    true_flags = []
    for flag in args.true_flag or []:
        if ":" not in flag:
            if plots is None:
                raise ValueError(f"--true-flag {flag}: flag names need --plots")
            flag = plo.flag_key(plots, flag)
        true_flags.append(flag)
    out = unreal.conversation(conv, owner=args.owner, names_dir=args.names, true_flags=true_flags,
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
    s.add_argument("--owner", help="tag of the creature that owns the conversation "
                                   "(default: the conversation name)")
    s.add_argument("--names", help="folder searched for <tag>.utc.json to name the speakers")
    s.add_argument("--true-flag", action="append", metavar="GUID:FLAG|NAME",
                   help="plot flag that starts out set, e.g. GEN_GENDER_MALE (names need --plots); repeatable")
    s.add_argument("--plots", help="folder of extracted .plo files, to name the flags (FlagNames)")
    s.add_argument("--vo", help="the conversation's VO bank (.fsb), to fill each line's Vo")
    s.add_argument("--out")
    s.set_defaults(func=cmd_unreal_conv)

    f = sub.add_parser("fsb", help="FMOD sound banks (voice-over)").add_subparsers(
        dest="fsb_command", required=True)
    s = f.add_parser("list", help="samples in a bank: name, codec, rate, channels, length")
    s.add_argument("file")
    s.set_defaults(func=cmd_fsb_list)
    s = f.add_parser("extract", help="write every MPEG sample as <name>.mp3")
    s.add_argument("file")
    s.add_argument("--out", required=True)
    s.set_defaults(func=cmd_fsb_extract)

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
    except (ERFError, GFF3Error, GFF4Error, fsb.FSBError, OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
