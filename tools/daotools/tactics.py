"""The enemies' talents and how they choose them (combat stage 4; docs/COMBAT.md, "Enemy talents").

A creature's talents come from its package (packages_base Ability1-12, AS_AssignAbilities): as many as its level /
LevelsPerAbility, + 1, + 2 more when LevelsPerAbility is 1 or more, in the table's order. Its tactics table is its
template's PackageAI, an id in m2da_base naming an aip_*.gda (aip_weapon_shield_human...), one row per tactic: target
type, condition (tacticsconditions: a ConditionBase and a parameter), command, sub-command (an ability, or for a jump
the row to go on from) and a chance in percent.

Each combat round (AI_DetermineCombatRound, _AI_ExecuteTactic) the creature goes down its rows: a row fires when its
chance roll passes, its condition holds and its command can run (an ability it has, can pay for, that is off
cooldown, and for a mode not already on); a jump row goes on from the row it names (-1: no more rows). When no row
fires it attacks its most hated enemy (AI_ExecuteDefaultAction).

Conditions handled (the rest never hold yet): any (16); health level (2: a negative parameter means below that
percent, a positive one at least that), of the target; mana or stamina level (14), of the target (the creature
itself for a self row); the target using an attack type (23, 36: melee or ranged, by its weapon in hand); being
attacked by an attack type (22: by an enemy that has it as its target, in melee or at range); the target at a
range band (29: short within 3.5 m, medium to 12, long to 80); surrounded by at least n enemies (31); the
nearest enemy it sees (6: the foe in hand, here).

The hero's tactics (hero_tactics): at character creation the game gives the hero his class's preset (sys_chargen:
a warrior Tank, a rogue Damage Dealer, a mage Nuker; tacticsuserpresets' TacticsTable) and fills it at each
level-up (Chargen_PopulateTacticsForPreset -> Chargen_LoadPresetsTable): the preset's rows in order, a row
whose command uses an ability (commandtypes UseType not 0) only when the hero has it, as many as his tactic
slots (exptable Tactics: 2 at levels 1 and 2, 3 from 3). They run when another party member is in control.
"""

from __future__ import annotations

import random
from pathlib import Path

from .erf import ERF
from .gda import GDA
from .gff4 import GFF4

ATTACK, WAIT, USE_ABILITY, ACTIVATE_MODE, DEACTIVATE_MODE, MOVE, JUMP = 2, 3, 4, 5, 6, 9, 10  # AI_COMMAND_*
SELF, MOST_HATED = 1, 7
NEAREST_VISIBLE = 6
HERO_PRESET = {1: 1, 3: 2, 2: 5}  # sys_chargen: core class -> tacticsuserpresets row (Tank, Damage Dealer, Nuker)  # tacticstargettypes rows: Self, Enemy: Most Hated (the rest: some enemy)
ANY, HP, STAMINA, ATTACKED_BY, USING_ATTACK, AT_RANGE, SURROUNDED, USING_ATTACK_FOLLOWER = 16, 2, 14, 22, 23, 29, 31, 36
MELEE, RANGED = 1, 2  # attack type bits
RANGE_SHORT, RANGE_MEDIUM, RANGE_LONG = 3.5, 12.0, 80.0  # AI_MELEE_RANGE, AI_RANGE_MEDIUM, AI_RANGE_LONG
MAX_TACTICS = 40  # rows a creature's table may have in the export (NpcTactics): the longest aip table has 39
FIELDS = ("Target", "Base", "Param", "Command", "Sub", "Chance")  # NpcTactics, per row
MAX_TALENTS = 6  # talents a creature may have in the export (NpcTalents)
_COLUMNS = ["ID", "TargetType", "Condition", "Command", "SubCommand", "UseChance"]


def load_tables(game_dir: str | Path) -> dict:
    """{"tactics": {PackageAI id: [rows]}, "packages": {package: row}} from 2da.erf; rows as FIELDS dicts with the
    condition resolved to its base and parameter."""
    out = {"tactics": {}, "packages": {}, "presets": {}, "use_types": {}, "slots": {}}
    with ERF.open(Path(game_dir) / "packages" / "core" / "data" / "2da.erf") as erf:
        names = {e.name.lower() for e in erf.entries}
        cond = {r["ID"]: r for r in GDA(GFF4(erf.read("tacticsconditions.gda")),
                                         ["ID", "label", "ConditionBase", "ConditionParameter"]).records()}
        index = GDA(GFF4(erf.read("m2da_base.gda")), ["ID", "Label", "Worksheet"]).records()
        sheets = {int(r["ID"]): str(r.get("Worksheet") or "").lower() for r in index}

        def rows_of(sheet, chance=None):  # chance: for a sheet without UseChance (the presets: always)
            rows = []
            for t in GDA(GFF4(erf.read(sheet + ".gda")), _COLUMNS).records():
                c = cond.get(int(t.get("Condition") or 0), {})
                rows.append({"Target": int(t.get("TargetType") or 0), "Base": int(c.get("ConditionBase") or 0),
                             "Param": float(c.get("ConditionParameter") or 0), "Command": int(t.get("Command") or 0),
                             "Sub": int(t.get("SubCommand") or 0),
                             "Chance": float(t.get("UseChance") or 0) if chance is None else chance})
            return rows

        for i, sheet in sheets.items():
            if sheet.startswith("aip_") and sheet + ".gda" in names:
                out["tactics"][i] = rows_of(sheet)
        for r in GDA(GFF4(erf.read("tacticsuserpresets.gda")), ["ID", "label", "TacticsTable"]).records():
            sheet = sheets.get(int(r.get("TacticsTable") or 0), "")
            if sheet and sheet + ".gda" in names:
                out["presets"][int(r["ID"])] = rows_of(sheet, 100.0)
        out["use_types"] = {int(r["ID"]): int(r.get("UseType") or 0)
                            for r in GDA(GFF4(erf.read("commandtypes.gda")), ["ID", "label", "UseType"]).records()}
        out["slots"] = {int(r["ID"]): int(r.get("Tactics") or 0)
                        for r in GDA(GFF4(erf.read("exptable.gda")), ["ID", "Tactics"]).records()}
        cols = ["ID", "label", "LevelsPerAbility"] + ["Ability%d" % i for i in range(1, 13)]
        out["packages"] = {r["ID"]: r for r in GDA(GFF4(erf.read("packages_base.gda")), cols).records()}
    return out


def package_talents(tables: dict, package: int, level: int) -> list[int]:
    """AS_AssignAbilities: the package's first abilities, level / LevelsPerAbility + 1 of them (+2 when
    LevelsPerAbility is 1 or more), stopping at the first empty slot."""
    pkg = tables["packages"].get(package) or {}
    per = float(pkg.get("LevelsPerAbility") or 0.0)
    if per <= 0.0:
        per = 1.0  # the class's own rule (TABLE_RULES_CLASSES) is not read here
    count = int(level / per) + 1 + (2 if per >= 1.0 else 0)
    out = []
    for i in range(1, 13):
        a = int(pkg.get("Ability%d" % i) or 0)
        if a <= 0 or len(out) >= count:
            break
        out.append(a)
    return out


def preset_rows(rows: list[dict], known: list[int], slots: int, use_types: dict[int, int]) -> list[dict]:
    """Chargen_LoadPresetsTable: the preset's rows in order, one using an ability only when it is known, at most
    `slots` of them."""
    out = []
    for r in rows:
        if len(out) >= slots:
            break
        if use_types.get(int(r["Command"]), 0) == 0 or int(r["Sub"]) in known:
            out.append(r)
    return out


def hero_tactics(tables: dict, player_class: int, level: int, known: list[int]) -> list[dict]:
    """The hero's tactics at `level` with the talents `known`: his class's preset (HERO_PRESET) loaded into his
    tactic slots (exptable Tactics)."""
    rows = tables.get("presets", {}).get(HERO_PRESET.get(player_class, 1), [])
    return preset_rows(rows, known, tables.get("slots", {}).get(level, 2), tables.get("use_types", {}))


def level_holds(value_percent: float, param: float) -> bool:
    """_AI_HasStatLevel: a negative parameter asks for less than that percent, a positive one for at least it."""
    return value_percent < -param if param < 0 else value_percent >= param


def condition_holds(row: dict, me: dict, target: dict) -> bool:
    """`me` and `target`: "Health" and "Stamina" in percent; me's "AttackedInMelee" (some enemy has it as its
    target), "Beside" (its foe within reach), "Surrounding" (enemies on it)."""
    base, param = int(row["Base"]), row["Param"]
    if base in (ANY, NEAREST_VISIBLE):  # the nearest enemy it sees: the foe in hand
        return True
    if base == HP:
        return level_holds(target["Health"], param)
    if base == STAMINA:
        return level_holds(target["Stamina"], param)
    if base in (USING_ATTACK, USING_ATTACK_FOLLOWER):
        return bool(int(param) & (RANGED if target.get("Ranged") else MELEE))
    if base == ATTACKED_BY:
        return (bool(int(param) & MELEE) and me.get("AttackedInMelee", False)
                or bool(int(param) & RANGED) and me.get("AttackedAtRange", False))
    if base == AT_RANGE:  # _AI_GetRangeFromID: short within 3.5 m, medium to 12, long to 80
        d = me.get("Distance", 1.0)
        lo, hi = {1: (0.0, RANGE_SHORT), 2: (RANGE_SHORT, RANGE_MEDIUM), 3: (RANGE_MEDIUM, RANGE_LONG)}.get(
            int(param), (0.0, -1.0))
        return lo <= d <= hi
    if base == SURROUNDED:
        return me.get("Surrounding", 0) >= param
    return False


def choose(rows: list[dict], me: dict, foe: dict, can_use, rng: random.Random) -> tuple[int, int]:
    """One combat round: (command, ability) of the first row that fires, (ATTACK, 0) when none does. `can_use(ability,
    mode)` says whether the creature has the ability, can pay for it and has it off cooldown (and for a mode, not on)."""
    i = 0
    while i < len(rows):
        row = rows[i]
        if rng.randint(1, 100) > row["Chance"]:
            i += 1
            continue
        target = me if int(row["Target"]) == SELF else foe
        if not condition_holds(row, me, target):
            i += 1
            continue
        cmd, sub = int(row["Command"]), int(row["Sub"])
        if cmd == JUMP:
            if sub == -1:
                break
            if sub > i + 1:
                i = sub - 1  # rows are numbered from 1
                continue
            i += 1
            continue
        if cmd in (USE_ABILITY, ACTIVATE_MODE) and can_use(sub, cmd == ACTIVATE_MODE):
            return cmd, sub
        i += 1
    return ATTACK, 0


def flat_rows(rows: list[dict]) -> list[float]:
    """A tactics table as MAX_TACTICS x FIELDS floats (NpcTactics); empty rows have chance 0."""
    out = []
    for row in (rows or [])[:MAX_TACTICS]:
        out += [float(row[k]) for k in FIELDS]
    return out + [0.0] * (len(FIELDS) * MAX_TACTICS - len(out))
