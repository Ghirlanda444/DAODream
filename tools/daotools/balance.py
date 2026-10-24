"""A rebalance mod's numbers against the game's own, for the combat system (docs/COMBAT_BALANCE.md).

A DAO mod changes data tables by shipping override tables (`abi_base_ao.gda` overrides rows of
`abi_base.gda`, matched by ID) and changes rules by replacing scripts. This reads the game's tables
and the mod's overrides, and writes for every table the rows the mod changes (each changed column as
[game, mod]) and the rows it adds, with the mod's names and descriptions for them from its talk table.
Unreal's combat data then loads the game's tables with these changes applied, and the game's numbers
stay visible next to the mod's.

Column names are not stored in a GDA (only their hashes); the scripts read columns by name
(`GetM2DAInt(TABLE, "Cost", nRow)`), so `script_column_names` collects them from the game's and the
mod's sources.
"""

from __future__ import annotations

import re
from pathlib import Path

from .gda import GDA
from .tlk import TalkTable

FORMAT = "DAODream.Balance 1"
# The game's tables a mod may override; an override is named <table>_<suffix>.gda
TABLES = ("abi_base", "abi_gxa", "shapechange", "autoscale", "difficulty", "itemprps", "itemstats",
          "passive_abilities", "passive_abilities_gxa", "persistent", "properties", "anim_combat")
# Common columns the scripts never name, but the tables have.
BASE_NAMES = ("ID", "Label", "Name", "Desc", "Namestrref", "DescStrRef", "Icon", "Cost", "Cooldown", "Range",
              "Upkeep", "Script", "Type")
_COLUMN = re.compile(r'GetM2DA(?:Int|Float|String|Resource)\s*\([^,]+,\s*"([^"]+)"')
_TEXT_COLUMNS = {"namestrref": "Name", "descstrref": "Desc"}


def script_column_names(*dirs: str | Path) -> list[str]:
    """Every column name the scripts under `dirs` read from a table, plus BASE_NAMES."""
    names = set(BASE_NAMES)
    for d in dirs:
        for p in Path(d).rglob("*.nss"):
            names.update(_COLUMN.findall(p.read_text(encoding="utf-8", errors="replace")))
    return sorted(names)


def _by_id(table: GDA) -> dict:
    key = table.column_names[0]  # the ID column comes first
    return {r[key]: r for r in table.records()}


def diff(game: GDA, mod: GDA) -> dict:
    """{"Columns", "Changed": {id: {column: [game, mod]}}, "New": {id: row}} of a mod's override table."""
    base, over = _by_id(game), _by_id(mod)
    changed, new = {}, {}
    for i, row in over.items():
        if i not in base:
            new[i] = row
            continue
        d = {k: [base[i].get(k), v] for k, v in row.items() if base[i].get(k) != v}
        if d:
            changed[i] = d
    return {"Columns": game.column_names, "Changed": changed, "New": new}


def export(game_dir: str | Path, mod_dir: str | Path, names: list[str], talk: TalkTable | None = None,
           source: str = "") -> dict:
    """The changes of every override table in `mod_dir` (`<table>_*.gda`) against `game_dir/<table>.gda`,
    with the mod's names and descriptions ("Text": {table: {id: {"Name", "Desc"}}}) when its talk table is
    given."""
    out = {"Format": FORMAT, "Source": source, "Tables": {}, "Text": {}}
    for table in TABLES:
        game_path = Path(game_dir) / f"{table}.gda"
        # abi_base_ao.gda, not passive_abilities_gxa_ao.gda for passive_abilities
        overrides = sorted(p for p in Path(mod_dir).glob(f"{table}_*.gda") if p.stem[len(table) + 1:].isalnum())
        if not game_path.exists() or not overrides:
            continue
        game = GDA.open(game_path, names)
        merged = {"Columns": game.column_names, "Changed": {}, "New": {}}
        for p in overrides:
            d = diff(game, GDA.open(p, names))
            merged["Changed"].update(d["Changed"])
            merged["New"].update(d["New"])
        out["Tables"][table] = merged
        if talk is not None:
            text = {}
            for i, row in list(merged["Changed"].items()) + list(merged["New"].items()):
                entry = {}
                for col, value in row.items():
                    label = _TEXT_COLUMNS.get(col.lower())
                    ref = value[1] if isinstance(value, list) else value
                    if label and isinstance(ref, int) and ref > 0:
                        entry[label] = talk.get(ref, "")
                if entry:
                    text[i] = entry
            if text:
                out["Text"][table] = text
    return out
