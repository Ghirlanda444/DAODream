"""The enemies' talents and how they choose them (combat stage 4; docs/COMBAT.md, "Enemy talents").

A creature's talents come from its package (packages_base Ability1-12, AS_AssignAbilities): as many as its level /
LevelsPerAbility, + 1, + 2 more when LevelsPerAbility is 1 or more, in the table's order. Its tactics table is its
template's PackageAI, an id in m2da_base naming an aip_*.gda (aip_weapon_shield_human...), one row per tactic: target
type, condition (tacticsconditions: a ConditionBase and a parameter), command, sub-command (an ability, or for a jump
the row to go on from) and a chance in percent.

Each combat round (AI_DetermineCombatRound, _AI_ExecuteTactic) the creature goes down its rows: a row fires when its
chance roll passes, its condition holds and its command can run (an ability it has, can pay for, that is off
cooldown, and for a mode not already on); an attack row attacks; a jump row goes on from the row it names (-1:
no more rows). When no row
fires it attacks its most hated enemy (AI_ExecuteDefaultAction).

Conditions handled (the rest never hold yet): any (16); health level (2: a negative parameter means below that
percent, a positive one at least that), of the target; mana or stamina level (14), of the target (the creature
itself for a self row); its own health or mana and stamina whatever the target (33, 34); the target using an attack type (23, 36: melee or ranged, by its weapon in hand); being
attacked by an attack type (22: by an enemy that has it as its target, in melee or at range); the target at a
range band (29, and the followers' 35: short within 3.5 m, medium to 12, long to 80); surrounded by at least n enemies (31); the
nearest enemy it sees (6: the foe in hand, here).

The hero's tactics (hero_tactics): at character creation the game gives the hero his class's preset (sys_chargen:
a warrior Tank, a rogue Damage Dealer, a mage Nuker; tacticsuserpresets' TacticsTable) and fills it at each
level-up (Chargen_PopulateTacticsForPreset -> Chargen_LoadPresetsTable): the preset's rows in order, a row
whose command uses an ability (commandtypes UseType not 0) only when the hero has it, as many as his tactic
slots (exptable Tactics: 2 at levels 1 and 2, 3 from 3). They run when another party member is in control.

A follower's (follower_tactics): party members run their own tactic slots, not their package's AI table
(var_module AI_USE_GUI_TABLES_FOR_FOLLOWERS, on: _AI_UseGUITables). When one is hired (player_core,
EVENT_TYPE_PARTY_MEMBER_HIRED) its package's FollowerTacticsTable is loaded into them the same way, after its
level-up (Chargen_SetNumTactics: exptable Tactics, + 1, 2, 4 or 6 with Combat Tactics); a package with none (-1:
Ser Gilmore's) leaves them empty, for the player to fill on the tactics screen.

The tactics screen (menu): the game's own lists, as its GUI shows them: the target types, base conditions,
conditions and commands it offers the player (their 0x2a1af533 column: 1 for the player's menu, 0 for the enemy AI's
rows) with their names (StrRef, in the talk table); its presets (tacticsuserpresets: a name, the classes it is for
and a table of rows, loaded as the hero's is) and behaviours (aibehaviors).

Who a row is aimed at (pick_target, ai_conditions_h): each base condition is a search that returns a creature or
nothing. The target type gives the list it searches: Self; Ally (the five nearest living creatures of its group, not
itself, those beyond 15 m only when fighting: _AI_GetAllies); Enemy (the five nearest living hostiles; a party
member's stop at the first one too far from the one in control: 30 m, 15 for a behaviour that does not chase:
_AI_GetEnemies); Most hated; the hero, the one in control, or one party member by name (the screen's own entries,
type 6). The search keeps the nearest that qualifies, so "Ally: Health < 50%" is the nearest party member below half
health. Some answer for the creature itself whatever the list (surrounded, most enemies...), and a party member's
"Enemy: Any" or "nearest visible" is its own target while it has one.
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
COMBAT_TACTICS = {100113: 6, 100112: 4, 100111: 2, 100110: 1}  # ABILITY_SKILL_COMBAT_TACTICS_4..1: more slots
IN_MENU = "0x2a1af533"  # the player's menu offers it (the column's name is not known, only its hash)
SELF_HP, SELF_STAMINA, FOLLOWER_RANGE = 33, 34, 35  # base conditions the player's menu has
# Target types (tacticstargettypes, AI_TARGET_TYPE_*). FOLLOWER is the screen's entry for one party member by name;
# the export writes such a row's target as FOLLOWER_BASE + that creature's index in the area.
ALLY, ENEMY, HERO, FOLLOWER, CONTROLLED = 2, 3, 5, 6, 18
FOLLOWER_BASE = 100
# Base conditions (tacticsbaseconditions, AI_BASE_CONDITION_*), those not named above.
STATUS, LOWEST_HP, CLUSTERED, MOST_HATED_ENEMY = 1, 3, 4, 5
NEAREST_RACE, NEAREST_CLASS, NEAREST_GENDER, ATTACKING_MEMBER, MEMBERS_TARGET, ANY_BUFF = 7, 8, 9, 10, 11, 12
ARMOR_TYPE, MOST_ARMOR, ALL_ARMOR, RANK = 18, 19, 20, 21
MOST_USING, ALL_USING, ENEMIES_ALIVE, CREATURES_DEAD, ALLIES_ALIVE = 24, 25, 26, 27, 28
FLANK, RANGED_AT_RANGE = 30, 32
MAGIC = 4  # AI_ATTACK_TYPE_MAGIC
# AI statuses (AI_STATUS_*, _AI_HasAIStatus) and the effects behind the three that group others
CHARM, PARALYZE, STUN, SLEEP, ROOT, DAZE, SLOW, KNOCKDOWN, GRABBED, GRABBING = 2, 3, 4, 5, 7, 8, 9, 16, 17, 18
CANT_ATTACK, IMMOBILIZED, MOVEMENT_IMPAIRED = 97, 98, 99
_GROUPS = {CANT_ATTACK: {PARALYZE, STUN, SLEEP, KNOCKDOWN, GRABBED, GRABBING},  # EFFECT_FLAG_DISABLE_COMBAT
           IMMOBILIZED: {PARALYZE, STUN, SLEEP, ROOT, KNOCKDOWN, GRABBED, GRABBING},  # EFFECT_FLAG_DISABLE_MOVEMENT
           MOVEMENT_IMPAIRED: {PARALYZE, STUN, SLEEP, ROOT, KNOCKDOWN, GRABBED, GRABBING, SLOW}}
MAX_NEAREST = 5  # AI_MAX_CREATURES_NEAREST: the lists hold the five nearest
ALLY_HELP = 15.0  # AI_RANGE_MAX_ALLY_HELP: an ally further away is left out unless fighting
ENGAGE_LONG, ENGAGE_CLOSE = 30.0, 15.0  # AI_FOLLOWER_ENGAGE_DISTANCE_*: from the one in control
RING = 2.5  # metres: the melee ring (CountAround, AroundOffer in Unreal)
CLUSTER_RADIUS = 5.0  # the cluster's centre must be within 5 m of a creature (and its spread, the spell's area)
HEAL = 10104  # ABILITY_SPELL_HEAL: only on the wounded (_AI_IsTargetValidForBeneficialAbility)
# The screen leaves out what the Unreal side cannot run: using a placeable.
MENU_LATER = (8,)
USE_ITEM, HEALTH_MOST, HEALTH_LEAST, LYRIUM_MOST, LYRIUM_LEAST = 7, 15, 16, 17, 18  # AI_COMMAND_USE_*
BEHAVIOR_FLAGS = ("AttackBack", "ChaseEnemy", "AttackOnCombatStart", "PreferRange", "PreferMelee",
                  "AvoidNearbyEnemies", "AvoidMeleeEnemies", "DefaultAttack", "AvoidAOE")
_BEHAVIOR_NAME, _BEHAVIOR_TEXT = "0xa77dbfd8", "0x50a903b6"  # aibehaviors: name and description StrRefs
_PRESET_NAME, _PRESET_CLASSES = "0x3273f70d", ("0x68391730", "0x431444f3", "0x5a0f75b2")  # tacticsuserpresets


def load_tables(game_dir: str | Path) -> dict:
    """{"tactics": {PackageAI id: [rows]}, "packages": {package: row}} from 2da.erf; rows as FIELDS dicts with the
    condition resolved to its base and parameter."""
    out = {"tactics": {}, "packages": {}, "presets": {}, "use_types": {}, "slots": {}, "gui": {}, "menu": {},
           "preset_info": {}, "behaviors": [], "buffs": []}
    with ERF.open(Path(game_dir) / "packages" / "core" / "data" / "2da.erf") as erf:
        names = {e.name.lower() for e in erf.entries}
        cond = {r["ID"]: r for r in GDA(GFF4(erf.read("tacticsconditions.gda")),
                                         ["ID", "label", "ConditionBase", "ConditionParameter", "StrRef"]).records()}
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
        for r in GDA(GFF4(erf.read("tacticsuserpresets.gda")),
                     ["ID", "label", "TacticsTable", _PRESET_NAME, *_PRESET_CLASSES]).records():
            sheet = sheets.get(int(r.get("TacticsTable") or 0), "")
            if sheet and sheet + ".gda" in names:
                out["presets"][int(r["ID"])] = rows_of(sheet, 100.0)
                out["preset_info"][int(r["ID"])] = {"label": r.get("label") or "", "StrRef": r.get(_PRESET_NAME) or 0,
                                                    "Classes": [int(r.get(c) or 0) for c in _PRESET_CLASSES]}
        out["behaviors"] = GDA(GFF4(erf.read("aibehaviors.gda")),
                               ["ID", "label", _BEHAVIOR_NAME, _BEHAVIOR_TEXT, *BEHAVIOR_FLAGS]).records()
        out["buffs"] = [int(r["ID"]) for r in GDA(GFF4(erf.read("ai_abilities_cond.gda")), ["ID", "MagicalBuff"]).records()
                        if int(r.get("MagicalBuff") or 0) == 1]
        out["use_types"] = {int(r["ID"]): int(r.get("UseType") or 0)
                            for r in GDA(GFF4(erf.read("commandtypes.gda")), ["ID", "label", "UseType"]).records()}
        out["slots"] = {int(r["ID"]): int(r.get("Tactics") or 0)
                        for r in GDA(GFF4(erf.read("exptable.gda")), ["ID", "Tactics"]).records()}
        cols = ["ID", "label", "LevelsPerAbility", "FollowerTacticsTable"] + ["Ability%d" % i for i in range(1, 13)]
        out["packages"] = {r["ID"]: r for r in GDA(GFF4(erf.read("packages_base.gda")), cols).records()}
        for r in out["packages"].values():  # a follower's table: no chance, its rows always tried
            t = int(r.get("FollowerTacticsTable") or 0)
            if t > 0 and sheets.get(t, "") + ".gda" in names:
                out["gui"][t] = rows_of(sheets[t], 100.0)
        named = ["ID", "label", "StrRef", "Type", "ValidForTarget", IN_MENU]
        out["menu"] = {
            "targets": GDA(GFF4(erf.read("tacticstargettypes.gda")), named).records(),
            "bases": GDA(GFF4(erf.read("tacticsbaseconditions.gda")), named).records(),
            "conditions": GDA(GFF4(erf.read("tacticsconditions.gda")),
                              named + ["ConditionBase", "ConditionParameter"]).records(),
            "commands": GDA(GFF4(erf.read("commandtypes.gda")), named).records()}
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


def slots(tables: dict, level: int, known=()) -> int:
    """Chargen_SetNumTactics: tactic slots at `level` (exptable Tactics), more with Combat Tactics."""
    return tables.get("slots", {}).get(level, 2) + next((n for a, n in COMBAT_TACTICS.items() if a in known), 0)


def hero_tactics(tables: dict, player_class: int, level: int, known: list[int]) -> list[dict]:
    """The hero's tactics at `level` with the talents `known`: his class's preset (HERO_PRESET) loaded into his
    tactic slots (exptable Tactics)."""
    rows = tables.get("presets", {}).get(HERO_PRESET.get(player_class, 1), [])
    return preset_rows(rows, known, slots(tables, level, known), tables.get("use_types", {}))


def follower_tactics(tables: dict, package: int, level: int, known: list[int]) -> list[dict]:
    """A party member's tactics when hired: its package's FollowerTacticsTable loaded into its slots (none for a
    package without one)."""
    t = int((tables.get("packages", {}).get(package) or {}).get("FollowerTacticsTable") or 0)
    return preset_rows(tables.get("gui", {}).get(t, []), known, slots(tables, level, known), tables.get("use_types", {}))


def menu(tables: dict, name=None) -> dict:
    """The tactics screen's lists (the export's Tactic* keys): the targets, base conditions, conditions and commands
    the player's menu offers, each with its name (`name(strref)`, the talk table; the table's label when there is
    none), the presets and behaviours. Left out: conditions without a name or of a cut base, and MENU_LATER's
    commands."""
    m = tables.get("menu") or {}

    def label(r, col="StrRef"):
        ref = int(r.get(col) or 0)
        return (name(ref) if name and ref else "") or str(r.get("label") or "")

    def shown(r):
        return int(r.get(IN_MENU) or 0) == 1

    targets = [r for r in m.get("targets", []) if shown(r)]
    cut = {int(r["ID"]) for r in m.get("bases", []) if str(r.get("label") or "").startswith("CUT")}
    conds = [r for r in m.get("conditions", []) if shown(r) and int(r.get("StrRef") or 0)
             and int(r.get("ConditionBase") or 0) not in cut]
    used = {int(r["ConditionBase"]) for r in conds}  # a base whose conditions the menu has (Self, Health is one)
    bases = [r for r in m.get("bases", []) if int(r["ID"]) in used]
    commands = [r for r in m.get("commands", []) if shown(r) and int(r.get("StrRef") or 0)
                and int(r["ID"]) not in MENU_LATER]

    def valid(r):  # 1 or 0 for each target above: valid for it (ValidForTarget has its type bit)
        return [1 if int(r.get("ValidForTarget") or 0) & int(g.get("Type") or 0) else 0 for g in targets]

    info = tables.get("preset_info") or {}
    presets, preset_rows_flat = [], []
    for i in sorted(info):
        rows = tables.get("presets", {}).get(i, [])
        presets += [float(i), *map(float, info[i]["Classes"]), float(len(preset_rows_flat) // len(FIELDS)),
                    float(len(rows))]
        preset_rows_flat += [float(r[k]) for r in rows for k in FIELDS]
    behaviors = tables.get("behaviors") or []
    return {
        # [id, target type bit] each
        "TacticTargets": [float(x) for r in targets for x in (r["ID"], r.get("Type") or 0)],
        "TacticTargetNames": [label(r) for r in targets],
        # [id, then valid for each target] each
        "TacticBases": [float(x) for r in bases for x in [r["ID"]] + valid(r)],
        "TacticBaseNames": [label(r) for r in bases],
        # [id, base, parameter] each
        "TacticConds": [float(x) for r in conds for x in (r["ID"], r["ConditionBase"], r.get("ConditionParameter") or 0)],
        "TacticCondNames": [label(r) for r in conds],
        # [id, then valid for each target] each
        "TacticCommands": [float(x) for r in commands for x in [r["ID"]] + valid(r)],
        "TacticCommandNames": [label(r) for r in commands],
        # [id, three classes (0: none), first row, rows] each, the rows (FIELDS) in TacticPresetRows
        "TacticPresets": presets,
        "TacticPresetRows": preset_rows_flat,
        "TacticPresetNames": [label({"label": info[i]["label"], "StrRef": info[i]["StrRef"]}) for i in sorted(info)],
        # [id, BEHAVIOR_FLAGS] each
        "TacticBehaviors": [float(x) for r in behaviors for x in [r["ID"]] + [r.get(f) or 0 for f in BEHAVIOR_FLAGS]],
        "TacticBehaviorNames": [label(r, _BEHAVIOR_NAME) for r in behaviors],
        "TacticBehaviorTexts": [label(r, _BEHAVIOR_TEXT) for r in behaviors],
        # abilities whose effects are magical buffs (ai_abilities_cond MagicalBuff): "Has any buff"
        "TacticBuffs": [float(x) for x in tables.get("buffs") or []],
    }


def traits(core_class: int, race: int, gender: int, rank: int, chest_label: str | None) -> list[float]:
    """What the conditions ask of a creature (NpcTraits, PlayerTraits): its core class, race, gender, rank and armour
    type (_AI_GetArmorType: light 1, medium 2, heavy and above 4; nothing worn on the chest counts as light, clothing
    as none)."""
    if not chest_label:
        armor = 1
    elif chest_label.startswith("Armor - Light"):
        armor = 1
    elif chest_label.startswith("Armor - Medium"):
        armor = 2
    elif chest_label.startswith(("Armor - Heavy", "Armor - Massive", "Armor - Super")):
        armor = 4
    else:
        armor = 0
    return [float(core_class), float(race), float(gender), float(rank), float(armor)]


def _dist(a: dict, b: dict) -> float:
    return ((a["Pos"][0] - b["Pos"][0]) ** 2 + (a["Pos"][1] - b["Pos"][1]) ** 2) ** 0.5


HOSTILE = 1  # a creature's Side: 0 the party, 1 hostile, 2 an ally outside the party, -1 a bystander


def hostile(a: dict, b: dict) -> bool:
    """One of them hostile and the other on the party's side (bystanders are neither)."""
    return a["Side"] >= 0 and b["Side"] >= 0 and (a["Side"] == HOSTILE) != (b["Side"] == HOSTILE)


def has_status(c: dict, status: int) -> bool:
    """_AI_HasAIStatus: c["Status"] holds the AI statuses its effects give; the last three group others."""
    own = set(c.get("Status") or ())
    return status in own or bool(own & _GROUPS.get(status, set()))


def _alive(c: dict) -> bool:
    return not c.get("Dead") and c.get("Health", 1.0) > 0


def _active(c: dict, ability: int) -> bool:
    return ability in (c.get("Active") or ())


def _beneficial_ok(c: dict, ability: int) -> bool:
    """_AI_IsTargetValidForBeneficialAbility: Heal only on the wounded; the rest anyone."""
    return c["Health"] < c["MaxHealth"] if ability == HEAL else True


def allies_of(world: dict, me, command: int = -1, sub: int = -1) -> list:
    """_AI_GetAllies: the five nearest living creatures of my group but me, those beyond ALLY_HELP only when
    fighting; for an ability, not those it is already on or that it would not help."""
    cs, m = world["Creatures"], world["Creatures"][me]
    near = sorted((i for i, c in cs.items() if i != me and c["Side"] == m["Side"] and _alive(c)),
                  key=lambda i: _dist(m, cs[i]))[:MAX_NEAREST]
    out = []
    for i in near:
        c = cs[i]
        if _dist(m, c) > ALLY_HELP and not c.get("Fighting", True):
            continue
        if command == USE_ABILITY and (_active(c, sub) or not _beneficial_ok(c, sub)):
            continue
        out.append(i)
    return out


def enemies_of(world: dict, me, command: int = -1, sub: int = -1) -> list:
    """_AI_GetEnemies: the five nearest living hostiles; a party member's list ends at the first one too far from
    the one in control (ENGAGE_LONG, ENGAGE_CLOSE without ChaseEnemy). For an ability, not those it is on."""
    cs, m = world["Creatures"], world["Creatures"][me]
    near = sorted((i for i, c in cs.items() if hostile(m, c) and _alive(c)),
                  key=lambda i: _dist(m, cs[i]))[:MAX_NEAREST]
    out = []
    lead = cs.get(world.get("Controlled"))
    reach = ENGAGE_LONG if m.get("Chase", True) else ENGAGE_CLOSE
    for i in near:
        c = cs[i]
        if m.get("Party") and lead is not None and _dist(c, lead) > reach:
            break
        if command == USE_ABILITY and _active(c, sub):
            continue
        out.append(i)
    return out


def _hated(world: dict, me, command: int, sub: int):
    """_AI_Condition_GetMostHatedEnemy: its threat target, not one an ability is already on."""
    h = world["Creatures"][me].get("Hated")
    if h is None or h not in world["Creatures"] or not _alive(world["Creatures"][h]):
        return None
    return None if command == USE_ABILITY and _active(world["Creatures"][h], sub) else h


def _party_target(world: dict, target: int, command: int, sub: int):
    """_AI_GetPartyTarget: the hero, the one in control, or the party member a FOLLOWER_BASE row names."""
    if target == HERO:
        who = world.get("Hero")
    elif target == CONTROLLED:
        who = world.get("Controlled")
    elif target >= FOLLOWER_BASE:
        who = world.get("Followers", {}).get(target - FOLLOWER_BASE)
    else:
        who = None
    c = world["Creatures"].get(who)
    if c is None or not _alive(c) or command == USE_ABILITY and _active(c, sub):
        return None
    return who


def _own_target(world: dict, me):
    """A party member's target while it is a living hostile (GetAttackTarget, _AI_IsHostileTargetValid)."""
    m = world["Creatures"][me]
    t = world["Creatures"].get(m.get("Target"))
    return m["Target"] if m.get("Party") and t is not None and hostile(m, t) and _alive(t) else None


def _list(world, me, target, command, sub) -> list:
    """The creatures a row's target type searches, nearest first."""
    if target == SELF:
        return [me] if command != USE_ABILITY or not _active(world["Creatures"][me], sub) else []
    if target == ALLY:
        return allies_of(world, me, command, sub)
    if target == ENEMY:
        return enemies_of(world, me, command, sub)
    if target == MOST_HATED:
        h = _hated(world, me, command, sub)
        return [h] if h is not None else []
    t = _party_target(world, target, command, sub)
    return [t] if t is not None else []


def _attack_type(c: dict) -> int:
    return int(c.get("Attack") or MELEE)


def _band(d: float, band: int) -> bool:
    """_AI_GetRangeFromID's bands: short to 3.5 m, medium to 12, long to 80."""
    lo, hi = {1: (-1.0, RANGE_SHORT), 2: (RANGE_SHORT, RANGE_MEDIUM), 3: (RANGE_MEDIUM, RANGE_LONG)}.get(band, (0.0, -1.0))
    return lo < d <= hi


def _rank_fits(rank: int, want: int) -> bool:
    """A rank, or a span of them (AI_RANK_RANGE_*: negative)."""
    if want > 0:
        return rank == want
    return rank in {-1: (2, 3, 4, 5), -2: (2, 1, 12, 11), -3: (3, 2, 1, 12, 11), -4: (3, 4, 5), -5: (4, 5)}.get(want, ())


def melee_ring(world: dict, me) -> list:
    """GetCreaturesInMeleeRing(0, 360, hostile): the hostiles within reach (RING metres, as Unreal's CountAround)."""
    cs, m = world["Creatures"], world["Creatures"][me]
    return [i for i, c in cs.items() if hostile(m, c) and _alive(c) and _dist(m, c) <= RING]


def _member(world: dict, param: int):
    return world.get("Hero") if param == HERO else world.get("Controlled") if param == CONTROLLED else None


def pick_target(row: dict, me, world: dict):
    """The creature a tactic row is aimed at (_AI_ExecuteTactic's switch over the base condition), or None when its
    condition does not hold. `world`: {"Creatures": {id: creature}, "Hero": id, "Controlled": id, "Followers":
    {area index: id}, "Dead": how many lie dead nearby}; a creature: Side (its group: HOSTILE, hostile()), Pos (x, y in metres), Health
    and MaxHealth, Stamina (percent), Dead, Target (who it attacks), Attack (1 melee, 2 ranged, 4 magic), Class,
    Race, Gender, Rank, Armor (traits()), Status (its AI statuses), Active (abilities on it), Buffs (one of them a
    magical buff), Party (a party member), Chase (its behaviour chases), Hated (its most hated), Fighting."""
    cs = world["Creatures"]
    m = cs[me]
    target, base, param = int(row["Target"]), int(row["Base"]), int(row["Param"])
    cmd, sub = int(row["Command"]), int(row["Sub"])

    def first(ids, test):
        return next((i for i in ids if test(cs[i])), None)

    def pct(c):
        return c["Health"] / max(c["MaxHealth"], 1e-6) * 100.0

    who = None
    if base == STATUS:
        who = first(_list(world, me, target, cmd, sub), lambda c: has_status(c, param))
    elif base in (HP, STAMINA):
        who = first(_list(world, me, target, cmd, sub),
                    lambda c: level_holds(pct(c) if base == HP else c["Stamina"], param))
    elif base == LOWEST_HP:  # _AI_GetNthDamagedCreatureInArray: the lowest or highest current health, the first on a tie
        ids = _list(world, me, target, cmd, sub) if target in (ALLY, ENEMY) else []
        if ids and param == 0:
            who = min(ids, key=lambda i: cs[i]["Health"])
        elif ids and param == 1:
            top = max(cs[i]["Health"] for i in ids)
            who = next(i for i in ids if cs[i]["Health"] == top) if top > 0 else None
    elif base == CLUSTERED:  # GetClusterCenter: the enemy with most others within the radius, at least n of them
        if m.get("Fighting", True):
            foes = [i for i in cs if hostile(m, cs[i]) and _alive(cs[i])]
            counts = {i: sum(1 for j in foes if _dist(cs[i], cs[j]) <= CLUSTER_RADIUS) for i in foes}
            fits = [i for i in foes if counts[i] >= param]
            if fits:
                who = min(fits, key=lambda i: (-counts[i], _dist(m, cs[i])))
    elif base == MOST_HATED_ENEMY:
        who = _hated(world, me, cmd, sub)
    elif base in (NEAREST_VISIBLE, NEAREST_RACE, NEAREST_CLASS, NEAREST_GENDER):
        own = _own_target(world, me) if target == ENEMY else None
        if own is not None:
            return own
        ids = _list(world, me, target, cmd, sub) if target in (ALLY, ENEMY) else []
        if base == NEAREST_VISIBLE:
            who = ids[param - 1] if 0 < param <= len(ids) else None
        else:
            key = {NEAREST_RACE: "Race", NEAREST_CLASS: "Class", NEAREST_GENDER: "Gender"}[base]
            who = first(ids, lambda c: int(c.get(key) or 0) == param)
    elif base == ATTACKING_MEMBER:
        member = _member(world, param)
        who = first(enemies_of(world, me, cmd, sub), lambda c: member is not None and c.get("Target") == member)
    elif base == MEMBERS_TARGET:
        who = (cs.get(_member(world, param)) or {}).get("Target")
    elif base == ANY_BUFF:
        own = _own_target(world, me)
        if own is not None and cs[own].get("Buffs"):
            return own
        ids = enemies_of(world, me, cmd, sub) if target == ENEMY else \
            _list(world, me, target, cmd, sub) if target == MOST_HATED else []
        reach = {1: RANGE_SHORT, 2: RANGE_MEDIUM, 3: RANGE_LONG}.get(param)
        who = first(ids, lambda c: c.get("Buffs") and (reach is None or _dist(m, c) <= reach))
    elif base == ANY:
        own = _own_target(world, me) if target == ENEMY else None
        if own is not None:
            return own
        if target == ENEMY:  # outside the party: the foe in hand, its most hated
            who = _hated(world, me, cmd, sub)
        else:
            ids = _list(world, me, target, cmd, sub)
            who = ids[0] if ids else None
    elif base == ARMOR_TYPE:
        if target in (SELF, MOST_HATED):
            h = _hated(world, me, cmd, sub)
            if h is not None and int(cs[h].get("Armor") or 0) & param:
                who = me if target == SELF else h
        elif target == ENEMY:
            who = first(enemies_of(world, me, cmd, sub), lambda c: int(c.get("Armor") or 0) & param)
    elif base in (MOST_ARMOR, ALL_ARMOR, MOST_USING, ALL_USING):
        if base == MOST_USING:
            foes = [cs[i] for i in enemies_of(world, me)]
        else:  # its threat table: every hostile in the fight
            foes = [c for c in cs.values() if hostile(m, c) and _alive(c) and c.get("Fighting", True)]
        if base in (MOST_ARMOR, ALL_ARMOR):
            n = sum(1 for c in foes if int(c.get("Armor") or 0) & param)
        else:
            n = sum(1 for c in foes if _attack_type(c) & param)
        ok = n >= len(foes) / 2 if base == MOST_ARMOR else n > len(foes) - n if base == MOST_USING else n == len(foes)
        who = me if ok else None
    elif base == RANK:  # the last (furthest) of the five that fits
        fits = [i for i in enemies_of(world, me, cmd, sub) if _rank_fits(int(cs[i].get("Rank") or 0), param)]
        who = fits[-1] if fits else None
    elif base == ATTACKED_BY:
        enemies, allies = enemies_of(world, me, cmd, sub), allies_of(world, me, cmd, sub)

        def on(attacker, victim):
            a = cs[attacker]
            return a.get("Target") == victim and bool(_attack_type(a) & param) and \
                (param != MELEE or _dist(a, cs[victim]) <= RANGE_SHORT)
        if target == SELF:
            who = me if any(on(e, me) for e in enemies) else None
        elif target == ENEMY:
            who = next((e for e in enemies if any(on(a, e) for a in allies)), None)
        elif target == ALLY:
            who = next((a for a in allies if any(on(e, a) for e in enemies)), None)
        elif target == MOST_HATED:
            h = _hated(world, me, cmd, sub)
            who = me if h is not None and _attack_type(cs[h]) & param and cs[h].get("Target") == me else None
        else:
            t = _party_target(world, target, cmd, sub)
            who = t if t is not None and any(on(e, t) for e in enemies) else None
    elif base in (USING_ATTACK, USING_ATTACK_FOLLOWER):
        if target in (SELF, MOST_HATED):
            h = _hated(world, me, cmd, sub)
            if h is not None and _attack_type(cs[h]) & param:
                who = me if target == SELF else h
        elif target in (ENEMY, ALLY):
            who = first(_list(world, me, target, cmd, sub), lambda c: _attack_type(c) & param)
    elif base in (ENEMIES_ALIVE, CREATURES_DEAD, ALLIES_ALIVE):
        if target == SELF:
            who = me
        elif target == ENEMY:
            who = (enemies_of(world, me) or [None])[0]
        elif target == MOST_HATED:
            who = _hated(world, me, -1, -1)
        if base == ENEMIES_ALIVE:
            n = sum(1 for c in cs.values() if hostile(m, c) and _alive(c) and c.get("Fighting", True))
        elif base == CREATURES_DEAD:
            n = int(world.get("Dead", 0))
        else:
            n = len(allies_of(world, me))
        who = who if n >= param else None
    elif base in (AT_RANGE, FOLLOWER_RANGE):
        if target in (ALLY, ENEMY):
            ids = _list(world, me, target, cmd, sub)
        else:  # Self and Most hated: its most hated
            ids = [x for x in [_hated(world, me, cmd, sub)] if x is not None]
        found = first(ids, lambda c: _band(_dist(m, c), param))
        who = me if target == SELF and found is not None else found
    elif base == FLANK:  # the arcs come from the appearance (apr_base AttackFR...): none for people and dogs
        who = None
    elif base == SURROUNDED:
        n = len(melee_ring(world, me))
        who = me if (param == 0 and n == 0) or (param != 0 and n >= param) else None
    elif base == RANGED_AT_RANGE:
        if target == ENEMY:
            ids = enemies_of(world, me, cmd, sub)
        else:
            ids = [x for x in [_hated(world, me, cmd, sub)] if x is not None]
        who = first(ids, lambda c: _attack_type(c) in (RANGED, MAGIC) and _band(_dist(m, c), param))
    elif base in (SELF_HP, SELF_STAMINA):
        level = pct(m) if base == SELF_HP else m["Stamina"]
        if level_holds(level, param) and target in (ENEMY, ALLY, MOST_HATED):
            ids = _list(world, me, target, cmd, sub)
            who = ids[0] if ids else None
    if who is not None and target == SELF and cmd == USE_ABILITY and not _beneficial_ok(m, sub):
        return None
    return who


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
    if base == SELF_HP:  # the creature's own, whoever the target
        return level_holds(me["Health"], param)
    if base == SELF_STAMINA:
        return level_holds(me["Stamina"], param)
    if base in (USING_ATTACK, USING_ATTACK_FOLLOWER):
        return bool(int(param) & (RANGED if target.get("Ranged") else MELEE))
    if base == ATTACKED_BY:
        return (bool(int(param) & MELEE) and me.get("AttackedInMelee", False)
                or bool(int(param) & RANGED) and me.get("AttackedAtRange", False))
    if base in (AT_RANGE, FOLLOWER_RANGE):  # _AI_GetRangeFromID: short within 3.5 m, medium to 12, long to 80
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
        if cmd == ATTACK:
            break
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
