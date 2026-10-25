"""Stage 2 of the combat port: stamina, ability costs, cooldowns and upkeep, and the warrior's and rogue's basic
talents (docs/COMBAT.md, "Talents"), from the game's tables with a rebalance mod's overrides on top, and the
talents' effects as the scripts apply them.

  abi_base           per ability: usetype (2 sustained, 3 passive, 4 activated), cost, cooldown, costupkeep,
                     fatigue (added while sustained), prereqability, prereqlevel, prereqattribute and the value it
                     needs (an unnamed column), passive_id
  passive_abilities  per passive_id: up to three creature properties and what each adds
  al<class>_default  InitialTalentID: the talents character creation picks when it is skipped
  autoscale          per rank: fEffectDur<difficulty>, fResistanceModifier, fResistanceMaximum

Stamina and mana are one pool (PROPERTY_DEPLETABLE_MANA_STAMINA), so these rules serve spells in stage 3 too.
What a talent does beyond its table row lives in the scripts (talent_singletarget, talent_modal, combat_h,
effect_death_h, core_h); EFFECTS and the constants below port it, with Dragon Age Reborn's changes. The threat
parts (Taunt, Threaten, Disengage, Feign Death dropping its user) wait for stage 4.
"""

from __future__ import annotations

from pathlib import Path

from . import stats

# Stage 2's talents: the warrior and rogue class trees, each in its prerequisite order, and Shield Bash.
WARRIOR = (14, 808, 17, 3021, 19, 3041, 3016, 20)  # Powerful .. Perfect Strike
ROGUE = (603, 21, 3002, 3023, 3026, 40003, 777, 3069)  # Dirty Fighting .. Evasion
SHIELD_BASH = 617
STAGE = WARRIOR + ROGUE + (SHIELD_BASH,)
# The talents Howe's men have at night (their packages' first abilities; tactics.package_talents) and use in melee:
# Shield Pummel, Sunder Weapon, Sunder Armor, Critical Strike, Pommel Strike, Indomitable, Shield Block (no numbers
# of its own).
ENEMY = (1, 3025, 4, 3, 3024, 28, 3074)
SUSTAINED, PASSIVE, ACTIVATED = 2, 3, 4  # abi_base usetype
CHARGEN_TALENT_POINTS = 2  # sys_chargen_h: PROPERTY_SIMPLE_TALENT_POINTS
# Creature properties (properties.gda) the passive and scripted effects change, by name.
PROPERTIES = {7: "Health", 8: "Stamina", 9: "Attack", 10: "Defense", 11: "Armour", 16: "Displacement",
              20: "FlankingAngle", 21: "Crit", 23: "RangedCrit", 31: "AttackSpeed", 32: "MentalResistance",
              33: "PhysicalResistance", 39: "DamageBonus", 41: "Fatigue", 53: "Penetration", 54: "CritDamage"}
# A passive's third property and value have no names the scripts use.
_PROP3, _VALUE3 = "0x9d400320", "0x9a632889"
_ATTRIBUTE_VALUE = "0x7cfe85d1"  # abi_base: the value prereqattribute needs

REGEN_COMBAT = 1.0  # REGENERATION_STAMINA_COMBAT_DEFAULT, a second
REGEN_EXPLORE = 17.5  # REGENERATION_STAMINA_EXPLORE_DEFAULT
SPEED_RANGE = (0.5, 1.5)  # CalculateAttackTiming caps the attack speed modifier
RESISTANCE_LEVEL = 5.0  # RESISTANCE_LEVEL_MODIFIER, per level the attacker is above the defender
PARTY_SLOTS = 4  # GetRankAdjustedEffectDuration: +1 s a missing party member on non-party creatures
BRAVERY_CRIT = 3.5  # per enemy in melee range past the first two
COMBAT_MOVEMENT_FLANKING = 20.0  # the most flanking gives, 15 without
DEATH_BLOW_STAMINA = 0.2  # of the slain creature's base health, back as stamina
EVASION_IMMUNITY = 20.0  # percent chance to shrug off a stun or knockdown
LETHALITY = 777
COUP_DE_GRACE = 3002

# The scripted effects (Reborn's talent_singletarget and talent_modal):
#   Stun: seconds before rank adjustment; Knockdown: as long as the engine's animations (KNOCKDOWN_SECONDS and
#     a random KNOCKDOWN_RANDOM); AttackBonus: added to the talent's one attack roll; Damage: the attack deals
#     its weapon damage (Offhand: the shield's); Resist: the attribute a ResistanceCheck against physical resistance uses
#     (resisted: no knockdown); Slow: movement speed multiplier; DisableTalents: the target cannot use talents;
#     DropModal: ends the target's sustained abilities (not on bosses); Duration: of the debuff or buff;
#     Self: properties added to the user while it lasts (a sustained talent: while active); CritPerLevel: added
#     to Crit and RangedCrit per level; RegenHealth: of max health a second in combat (x1.5 out of it).
EFFECTS = {
    603: {"Stun": 4.0},  # Dirty Fighting: no attack roll (DIRTY_FIGHTING_STUN_DURATION)
    3026: {"AttackBonus": 5.0, "Damage": True, "Slow": 0.5, "DisableTalents": True, "DropModal": True,
           "Duration": 10.0},  # Below the Belt: Reborn drops the defense penalty and the resistance check
    617: {"AttackBonus": 10.0, "Damage": True, "Offhand": True, "Knockdown": True, "Resist": "Str"},  # Shield Bash
    20: {"Self": {"Attack": 100.0, "Penetration": 10.0}, "Duration": 10.0},  # Perfect Strike: Reborn adds the AP
    40003: {"Tricks": True, "Duration": 10.0},  # Tricks of the Trade (Reborn): by the highest attribute, tricks()
    19: {"Self": {"Attack": 5.0, "AttackSpeed": 0.1, "Crit": 2.5, "RangedCrit": 2.5},
         "CritPerLevel": 0.5},  # Precise Striking: Reborn halves the attack bonus
    3023: {"DisableTalents": True, "RegenHealth": 0.04},  # Feign Death; foes forget its user (threat.py)
    # The enemies' (stage 4): Howe's men at night (packages 42, 43, 49, 53; stage 2b for the player)
    1: {"AttackBonus": 10.0, "Damage": True, "Hits": 3, "Stun": 4.0, "Resist": "Str",
        "StrengthDamage": 0.01},  # Shield Pummel: the weapon at +10, then two shield blows that always land, each
    #   x (1 + 1% a point of strength above 10); the third stuns 4 s (SHIELD_PUMMEL_DURATION) unless resisted
    3025: {"Damage": True, "Hits": 2, "DamageMul": 0.6, "Duration": 6.0, "Resist": "Str",
           "Disarm": True},  # Sunder Weapon (Reborn): two blows at 60%; the second, unless resisted, takes the
    #   target's whole attack rating away for 6 s (SUNDER_WEAPON_DURATION, 10 in the game)
    3: {"Damage": True, "Execute": 0.25},  # Critical Strike (Reborn): a hit kills a non-boss target at 25% health
    #   or less (CRITICAL_STRIKE_DEATHBLOW_PERCENTAGE, 0.2 in the game), x1.5 damage on a boss there
    4: {"Damage": True, "Hits": 2, "DamageMul": 0.7, "Duration": 10.0, "Resist": "Str",
        "ArmourChange": 0.3},  # Sunder Armor (Reborn; its row is relabelled CRITICAL_STRIKE): two blows at 70%; the
    #   second, unless resisted, changes the target's armour by +30% for 10 s (SUNDER_ARMOR_DURATION): the script
    #   passes a positive amount to EffectDecreaseProperty, which applies it as given; ported as written
    3024: {"Knockdown": True, "Resist": "Str"},  # Pommel Strike: no attack roll; knocked down unless resisted
    28: {"Self": {"DamageScale": -0.3}, "Indomitable": True},  # Indomitable (Reborn): +30% armour, defense +0.6
    #   a point of strength above 10, -30% damage dealt (and missile shield 10)
}
# The talents that take their target out of the fight for a while: a stun lasts its seconds rank-adjusted
# (effect_duration), a knockdown as long as the engine's animations (no rank adjustment).
DISABLES = {603: "Stun", 617: "Knockdown", 1: "Stun", 3024: "Knockdown"}
THREAT = (808, 3041, 3016, 3023)  # Threaten, Taunt, Disengage, Feign Death: their point is threat (stage 4)
NAMES = {14: "Powerful", 808: "Threaten", 17: "Bravery", 3021: "Death Blow", 19: "Precise Striking", 3041: "Taunt",
         3016: "Disengage", 20: "Perfect Strike", 603: "Dirty Fighting", 21: "Combat Movement",
         3002: "Coup de Grace", 3023: "Feign Death", 3026: "Below the Belt", 40003: "Tricks of the Trade",
         777: "Lethality", 3069: "Evasion", 617: "Shield Bash", 1: "Shield Pummel", 3025: "Sunder Weapon",
         3: "Critical Strike", 4: "Sunder Armor", 3024: "Pommel Strike", 28: "Indomitable", 3074: "Shield Block", 500: "Aim",
         33: "Defensive Fire", 803: "Pinning Shot", 3072: "Shattering Shot", 100075: "Stealth",
         6: "Dual Weapon Training"}
BRAVERY, DEATH_BLOW, EVASION = 17, 3021, 3069
# A human knocked down (Shield Bash) is out of the fight while the engine plays the fall (mh_c.rct_kbck: 1.2 and
# 1.37 s; which one, or how the engine blends it, is not in the data), lies for the effect's RandomFloat() seconds
# (KNOCKDOWN_RANDOM, rolled at use) and gets up (mh_c.rct_kdwn_up_v1: 2.13 s).
KNOCKDOWN_SECONDS = 1.3 + 2.13
KNOCKDOWN_RANDOM = 1.0


def load_tables(game_dir: str | Path, overrides: str | Path | None = None) -> dict[str, dict[int, dict]]:
    """stats' tables plus abi_base and passive_abilities, with a mod's override tables on top."""
    return stats.load_tables(game_dir, overrides)


def passive_properties(row: dict) -> dict[str, float]:
    """A passive_abilities row: {property name: what it adds}."""
    out = {}
    for prop, value in (("Prop1", "modifier1"), ("Prop2", "modifier2"), (_PROP3, _VALUE3)):
        p = int(row.get(prop) or 0)
        if p:
            name = PROPERTIES.get(p, f"Property{p}")
            out[name] = out.get(name, 0.0) + float(row.get(value) or 0.0)
    return out


def talents(tables: dict, ids: tuple[int, ...] = STAGE + ENEMY) -> dict[int, dict]:
    """Each talent's table row, read: Name, Use (SUSTAINED, PASSIVE, ACTIVATED), Cost, Cooldown, Upkeep, Fatigue,
    Prereq (ability), Level, Attribute (1 strength, 2 dexterity...) and Value it needs, Passive {property: value},
    Effect (EFFECTS)."""
    abi, passive = tables.get("abi_base", {}), tables.get("passive_abilities", {})
    out = {}
    for i in ids:
        r = abi.get(i)
        if not r:
            continue
        pid = int(r.get("passive_id") or 0)
        out[i] = {"Name": str(r.get("label") or i).replace("_", " ").title(), "Use": int(r.get("usetype") or 0),
                  "Cost": float(r.get("cost") or 0.0), "Cooldown": float(r.get("cooldown") or 0.0),
                  "Upkeep": float(r.get("costupkeep") or 0.0), "Fatigue": float(r.get("fatigue") or 0.0),
                  "Prereq": int(r.get("prereqability") or 0), "Level": int(r.get("prereqlevel") or 0),
                  "Attribute": int(r.get("prereqattribute") or 0), "Value": float(r.get(_ATTRIBUTE_VALUE) or 0.0),
                  "Passive": passive_properties(passive.get(pid, {})) if pid else {},
                  "Effect": EFFECTS.get(i, {})}
    return out


def starting_talents(tables: dict, player_class: int) -> list[int]:
    """AL_SpendTalentPoints at character creation (skipped): the class table's InitialTalentID picks, in order,
    for CHARGEN_TALENT_POINTS (a warrior: Shield Bash and Precise Striking; a rogue: Stealth and Dual Weapon
    Training)."""
    table = tables.get(stats.HERO_LEVELUP.get(player_class, ""), {})
    picks = [int(table[i].get("InitialTalentID") or 0) for i in sorted(table) if i > 0]
    return [p for p in picks if p][:CHARGEN_TALENT_POINTS]


def levelup_talents(tables: dict, player_class: int, level: int, known: list[int],
                    attributes: dict[str, float]) -> list[int]:
    """AL_SpendTalentPoints at each level-up from 2 to `level`: one talent point a level (cla_data LevelsPerAbility
    1 for warriors and rogues), spent on the first talent of the class table's TalentID list the hero can learn
    (IsAbilityAvailable: can_learn; the class's starting abilities, such as Hidden Warrior, count as known). Returns
    the new talents, in the order learnt."""
    table = tables.get(stats.HERO_LEVELUP.get(player_class, ""), {})
    picks = [int(table[i].get("TalentID") or 0) for i in sorted(table) if i > 0]
    rows = talents(tables, tuple(p for p in picks if p))
    cls = tables.get("cla_data", {}).get(player_class, {})  # the class's hidden abilities (Hidden Warrior...)
    have = set(known) | {int(cls.get(k) or 0) for k in ("StartingAbility1", "StartingAbility2")}
    new = []
    for lv in range(2, level + 1):
        for p in picks:
            if p and p not in have and p in rows and can_learn(rows[p], have, lv, attributes):
                have.add(p)
                new.append(p)
                break
    return new


def can_learn(talent: dict, known: set[int], level: int, attributes: dict[str, float]) -> bool:
    """Its prerequisite ability known, the level reached and the attribute high enough."""
    attr = stats.ATTRIBUTES[talent["Attribute"] - 1] if 0 < talent["Attribute"] <= len(stats.ATTRIBUTES) else ""
    return ((not talent["Prereq"] or talent["Prereq"] in known) and level >= talent["Level"]
            and (not attr or attributes.get(attr, 0.0) >= talent["Value"]))


def ability_cost(cost: float, fatigue: float = 0.0, use_mod: float = 1.0) -> float:
    """Ability_GetAbilityCost: the cost raised by fatigue (armour's and sustained abilities', in percent), rounded,
    over the difficulty's use modifier (1 for the party, critters and weak creatures). Upkeep is not raised."""
    if cost <= 0:
        return 0.0
    return float(int(cost * (1.0 + fatigue * 0.01) + 0.5)) / (use_mod or 1.0)


def max_stamina(stamina: float, upkeeps: list[float]) -> float:
    """Effects_HandleApplyEffectUpkeep: each sustained ability lowers the pool's maximum by its upkeep."""
    return stamina - sum(upkeeps)


def attack_interval(base: float, speed: float = 1.0) -> float:
    """CalculateAttackTiming: seconds between attacks x the attack speed modifier (1 by default, Precise Striking
    +0.1), capped to SPEED_RANGE."""
    return base * min(SPEED_RANGE[1], max(SPEED_RANGE[0], speed))


def effect_duration(seconds: float, rank: int, tables: dict, party_size: int = PARTY_SLOTS,
                    party_member: bool = False) -> float:
    """GetRankAdjustedEffectDuration: on a creature outside the party a debuff of a second or more lasts a second
    longer per missing party member, then x the rank's fEffectDur (Normal difficulty: critters 1.5, lieutenants
    0.75, bosses 0.6)."""
    if not party_member and seconds >= 1.0:
        seconds += max(0, PARTY_SLOTS - party_size)
    auto = tables["autoscale"].get(rank) or {}
    mod = float(auto.get("fEffectDurNormal") or 0.0)
    return seconds * mod if mod > 0 else seconds


def resist_chance(rank: int, tables: dict, *, attribute: float, level_difference: int,
                  resistance: float = 0.0) -> float:
    """ResistanceCheck: percent the defender resists. Its resistance (0 for creatures, as saves show) less the
    attacker's attribute above 10 and 5 a level the attacker is above it, plus its rank's fResistanceModifier,
    capped at the rank's fResistanceMaximum."""
    auto = tables["autoscale"].get(rank) or {}
    value = resistance - max(0.0, attribute - stats.BASE_ATTRIBUTE) - RESISTANCE_LEVEL * level_difference
    value += float(auto.get("fResistanceModifier") or 0.0)
    return max(0.0, min(value, float(auto.get("fResistanceMaximum") or 0.0)))


def tricks(attributes: dict[str, float], attack: float) -> dict[str, float]:
    """Tricks of the Trade (Reborn) by the user's highest attribute: cunning, a fifth more attack; dexterity,
    -0.2 critical damage range (property 54, read as a hundredth: -0.002 critical damage); strength, +20 attack
    speed modifier, which the cap turns into attacks 1.5 times slower. Ported as written."""
    s, d, c = attributes.get("Str", 0.0), attributes.get("Dex", 0.0), attributes.get("Int", 0.0)
    if c >= d and c >= s:
        return {"Attack": attack * 0.2}
    if d >= c and d >= s:
        return {"CritDamage": -0.2}
    return {"AttackSpeed": 20.0}


def with_passives(st: dict, known: list[int], table: dict[int, dict], player_class: int = 1) -> dict:
    """A creature's stats (stats.stats) with its passive talents: their table properties (Powerful +25 health and
    -10 fatigue, Bravery +1 damage bonus, Combat Movement +30 flanking angle...), Combat Movement's 20 flanking,
    and flags for the scripted ones (Bravery, Death Blow, Coup de Grace, Lethality, Evasion). Lethality's damage
    by cunning needs stats.stats(..., lethality=True)."""
    out = dict(st)
    out.setdefault("FlankingAngle", 60.0)  # Chargen_InitializeCharacter
    for i in known:
        t = table.get(i)
        if not t or t["Use"] != PASSIVE:
            continue
        for name, value in t["Passive"].items():
            out[name] = round(out.get(name, 0.0) + value, 3)
    if 21 in known:
        out["Flanking"] = COMBAT_MOVEMENT_FLANKING * (1.0 if player_class == stats.CLASS_ROGUE else 0.5)
    out["Talents"] = sorted(known)
    return out


# Per talent the player can use, flat for Blueprint (area export PlayerTalents, TALENT_FIELDS floats each):
# its id, use, stamina cost and upkeep, cooldown, fatigue while sustained, the attack bonus of its attack roll,
# its seconds (stun, knockdown, or how long the debuff or buff lasts), and what it adds to its user while it
# lasts: attack, armour penetration, attack speed modifier, critical chance, defense, armour, damage scale; and
# its damage multiplier (Shield Pummel's strength bonus, Sunder Weapon's 60%).
TALENT_FIELDS = ("Id", "Use", "Cost", "Cooldown", "Upkeep", "Fatigue", "AttackBonus", "Seconds", "Attack",
                 "Penetration", "Speed", "Crit", "Defense", "Armour", "DamageScale", "DamageMul")


def talent_row(i: int, talent: dict, player: dict) -> list[float]:
    """A talent as TALENT_FIELDS for `player` (stats.stats; a creature's too): its level sets Precise Striking's
    critical bonus, its attributes pick Tricks of the Trade's (tricks: the dexterity one, a fiftieth of a percent
    of critical damage, is left out), its strength and armour Indomitable's and Shield Pummel's."""
    e = talent["Effect"]
    own = dict(e.get("Self") or {})
    if e.get("Tricks"):
        own = {k: v for k, v in tricks(player.get("Attributes") or {}, float(player.get("Attack") or 0)).items()
               if k != "CritDamage"}
    crit = own.get("Crit", 0.0) + e.get("CritPerLevel", 0.0) * float(player.get("Level") or 1)
    seconds = e.get("Stun") or (KNOCKDOWN_SECONDS if e.get("Knockdown") else 0.0) or e.get("Duration", 0.0)
    strength = float((player.get("Attributes") or {}).get("Str", stats.BASE_ATTRIBUTE))
    if e.get("Indomitable"):  # from the user's strength and armour
        own["Defense"] = round((strength - stats.BASE_ATTRIBUTE) * 0.6, 3)
        own["Armour"] = round(float(player.get("Armour") or 0.0) * 0.3, 3)
    mul = e.get("DamageMul", 1.0) * (1.0 + e.get("StrengthDamage", 0.0) * (strength - stats.BASE_ATTRIBUTE))
    return [float(i), float(talent["Use"]), talent["Cost"], talent["Cooldown"], talent["Upkeep"], talent["Fatigue"],
            float(e.get("AttackBonus", 0.0)), float(seconds), own.get("Attack", 0.0), own.get("Penetration", 0.0),
            own.get("Speed", own.get("AttackSpeed", 0.0)), round(crit, 3), own.get("Defense", 0.0),
            own.get("Armour", 0.0), own.get("DamageScale", 0.0), round(mul, 3)]


def known_talents(tables: dict, player_class: int, choice: str, shield: bool) -> list[int]:
    """The player's talents: "start" (character creation's picks that stage 2 has), "all" (the class's stage 2
    tree, and Shield Bash with a shield), or ids separated by commas."""
    if choice == "start":
        return [i for i in starting_talents(tables, player_class) if i in STAGE]
    if choice == "all":
        tree = list(ROGUE if player_class == stats.CLASS_ROGUE else WARRIOR)
        return tree + ([SHIELD_BASH] if shield else [])
    return [int(x) for x in choice.split(",") if x.strip()]
