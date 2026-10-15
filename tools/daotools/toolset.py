"""Script source from the official Dragon Age toolset's database.

The toolset keeps the game's script source (NWScript, .nss) in its SQL Server
Express database (`bw_dragonage_content` on `.\\BWDATOOLSET`): table
`t_Script` (`ModuleResRefVersionID`, `Text`) joined to `t_ModuleResRefVersion`
(`ID`, `Name`, `Folder`). Each script has an empty placeholder version and a
version with the text; the newest non-empty one is used.

The database is read through the toolset's own `sqlcmd`, so nothing beyond the
standard library is needed. Windows only, and the toolset's database must have
been restored (see docs/SCRIPTS.md).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

SERVER = r".\BWDATOOLSET"
DATABASE = "bw_dragonage_content"
MARK = "@@@DAODREAM-SCRIPT@@@"
_SQLCMD_PATHS = [r"C:\Program Files (x86)\Microsoft SQL Server\90\Tools\Binn\SQLCMD.EXE",
                 r"C:\Program Files\Microsoft SQL Server\90\Tools\Binn\SQLCMD.EXE"]


class ToolsetError(Exception):
    pass


def find_sqlcmd() -> str:
    for p in _SQLCMD_PATHS:
        if os.path.exists(p):
            return p
    found = shutil.which("sqlcmd")
    if not found:
        raise ToolsetError("sqlcmd not found; is the Dragon Age toolset (and its SQL Server Express) installed?")
    return found


def query(pattern: str) -> str:
    """SQL that prints every matching script as a marker line then its text."""
    like = pattern.replace("'", "''").replace("*", "%")
    return ("SET NOCOUNT ON; "
            f"SELECT '{MARK}' + v.Name + '|' + ISNULL(v.Folder, '') + '|' + CAST(v.ID AS varchar(20)) "
            "+ CHAR(10) + CAST(s.Text AS varchar(max)) "
            "FROM t_Script s JOIN t_ModuleResRefVersion v ON v.ID = s.ModuleResRefVersionID "
            f"WHERE DATALENGTH(s.Text) > 0 AND v.Name LIKE '{like}' ORDER BY v.Name, v.ID;")


def parse(dump: str) -> dict[str, dict]:
    """Scripts from sqlcmd output: {name: {"folder", "version", "text"}}; the
    highest version wins when a name appears twice."""
    scripts: dict[str, dict] = {}
    for block in dump.split(MARK)[1:]:
        head, _, text = block.partition("\n")
        name, folder, version = (head.strip().split("|") + ["", "", "0"])[:3]
        entry = {"folder": folder, "version": int(version or 0), "text": text.rstrip() + "\n"}
        if name and (name not in scripts or entry["version"] > scripts[name]["version"]):
            scripts[name] = entry
    return scripts


def read_scripts(pattern: str = "*", server: str = SERVER, database: str = DATABASE) -> dict[str, dict]:
    sqlcmd = find_sqlcmd()
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "dump.txt"
        result = subprocess.run([sqlcmd, "-S", server, "-E", "-d", database, "-h", "-1", "-y", "0", "-u",
                                 "-b", "-o", str(out), "-Q", query(pattern)], capture_output=True, text=True)
        dump = out.read_text(encoding="utf-16") if out.exists() else ""
    if result.returncode != 0:
        raise ToolsetError(f"sqlcmd failed: {(dump or result.stdout or result.stderr).strip()[:500]}")
    return parse(dump)


def export(out_dir: str | Path, pattern: str = "*") -> dict[str, dict]:
    """Write <out>/<name>.nss for every matching script and <out>/index.json
    (name -> toolset folder). Returns the index."""
    scripts = read_scripts(pattern)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    index = {}
    for name, s in sorted(scripts.items()):
        (out / f"{name}.nss").write_text(s["text"], encoding="utf-8")
        index[name] = {"folder": s["folder"], "bytes": len(s["text"])}
    (out / "index.json").write_text(json.dumps(index, indent=1) + "\n", encoding="utf-8")
    return index
