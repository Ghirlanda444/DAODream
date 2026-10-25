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

Conditions handled (the rest never hold, as their situations do not come up in melee yet): any (16); health level
(2: a negative parameter means below that percent, a positive one at least that), of the target; mana or stamina
level (14), of the target (the creature itself for a self row); the target using an attack type (23, 36: everyone
fights in melee here); being attacked by an attack type (22: melee when an enemy has it as its target); an enemy at
short range (29 1: the creature's foe is beside it); surrounded by at least n enemies (31).
"""

from __future__ import annotations

import random
from pathlib import Path

from .erf import ERF
from .gda import GDA
from .gff4 import GFF4

ATTACK, WAIT, USE_ABILITY, ACTIVATE_MODE, DEACTIVATE_MODE, MOVE, JUMP = 2, 3, 4, 5, 6, 9, 10  # AI_COMMAND_*
SELF, MOST_HATED = 1, 7  # tacticstargettypes rows: Self, Enemy: Most Hated (the rest: some enemy)
ANY, HP, STAMINA, ATTACKED_BY, USING_ATTACK, AT_RANGE, SURROUNDED, USING_ATTACK_FOLLOWER = 16, 2, 14, 22, 23, 29, 31, 36
MELEE = 1  # attack type bit
MAX_TACTICS = 12  # rows a creature's table may have in the export (NpcTactics)
FIELDS = ("Target", "Base", "Param", "Command", "Sub", "Chance")  # NpcTactics, per row
MAX_TALENTS = 6  # talents a creature may have in the export (NpcTalents)
_COLUMNS = ["ID", "TargetType", "Condition", "Command", "SubCommand", "UseChance"]


def load_tables(game_dir: str | Path) -> dict:
    """{"tactics": {PackageAI id: [rows]}, "packages": {package: row}} from 2da.erf; rows as FIELDS dicts with the
    condition resolved to its base and parameter."""
    out = {"tactics": {}, "packages": {}}
    with ERF.open(Path(game_dir) / "packages" / "core" / "data" / "2da.erf") as erf:
        names = {e.name.lower() for e in erf.entries}
        cond = {r["ID"]: r for r in GDA(GFF4(erf.read("tacticsconditions.gda")),
                                         ["ID", "label", "ConditionBase", "ConditionParameter"]).records()}
        index = GDA(GFF4(erf.read("m2da_base.gda")), ["ID", "Label", "Worksheet"]).records()
        for r in index:
            sheet = str(r.get("Worksheet") or "").lower()
            if not sheet.startswith("aip_") or sheet + ".gda" not in names:
                continue
            rows = []
            for t in GDA(GFF4(erf.read(sheet + ".gda")), _COLUMNS).records():
                c = cond.get(int(t.get("Condition") or 0), {})
                rows.append({"Target": int(t.get("TargetType") or 0), "Base": int(c.get("ConditionBase") or 0),
                             "Param": float(c.get("ConditionParameter") or 0), "Command": int(t.get("Command") or 0),
                             "Sub": int(t.get("SubCommand") or 0), "Chance": float(t.get("UseChance") or 0)})
            out["tactics"][int(r["ID"])] = rows
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


def level_holds(value_percent: float, param: float) -> bool:
    """_AI_HasStatLevel: a negative parameter asks for less than that percent, a positive one for at least it."""
    return value_percent < -param if param < 0 else value_percent >= param


def condition_holds(row: dict, me: dict, target: dict) -> bool:
    """`me` and `target`: "Health" and "Stamina" in percent; me's "AttackedInMelee" (some enemy has it as its
    target), "Beside" (its foe within reach), "Surrounding" (enemies on it)."""
    base, param = int(row["Base"]), row["Param"]
    if base == ANY:
        return True
    if base == HP:
        return level_holds(target["Health"], param)
    if base == STAMINA:
        return level_holds(target["Stamina"], param)
    if base in (USING_ATTACK, USING_ATTACK_FOLLOWER):
        return bool(int(param) & MELEE)
    if base == ATTACKED_BY:
        return bool(int(param) & MELEE) and me.get("AttackedInMelee", False)
    if base == AT_RANGE:
        return int(param) == 1 and me.get("Beside", True)
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
