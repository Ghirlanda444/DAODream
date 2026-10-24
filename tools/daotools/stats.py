"""Creature stats from the game's data tables, as the scripts compute them.

A port of sys_autoscale_h (AS_CommenceAutoScaling, AS_AddClassLevels),
sys_chargen_h (Chargen_ApplyClassStatModifiers) and combat_damage_h /
combat_h (Combat_Damage_GetAttackDamage, Combat_GetAttackResult), reading:

  packages_base  a creature's Package: StartingClass, Strategy, MinLevel
  autoscale      per rank: fscale, fHealthScale, nBonusPoints, nLevelScale, fDamageScale
  as_data        per strategy: s1..s6, levels per point of each attribute
  cla_data       per class: BaseHealth, HealthPerLevel, BaseAttack, BaseDefense,
                 DamagePerLevel, BaseManaStamina, DepletableProgression,
                 Str/Dex/Will/Mag/Int/ConAdjust
  race_base      per race: the same six adjustments (the player only)
  itemstats      per base item: Damage, DamageRange, ArmorPenetration, CritChanceModifier,
                 AttributeMod, Attribute0/1, Armor, Defense, MissileDeflection
  materialtypes  per material: Armor (the multiplier of an armour piece's Armor)
  difficulty     DmgScalingThresh (Normal)

The attributes' derived stats are the engine's, not the scripts' (DERIVED: per point
above 10, as the game's character sheet shows them). Armour is summed from the
equipped pieces as the engine does (`equipment`); combat_damage_h subtracts it
from each hit (`hit_damage`). Talents are not included yet.

`load_tables(..., overrides=dir)` puts a rebalance mod's override tables on top
(docs/COMBAT_BALANCE.md): Dragon Age Reborn's raise most ranks' health by 30%.
"""

from __future__ import annotations

from pathlib import Path

from .balance import override_files
from .erf import ERF
from .gda import GDA
from .gff4 import GFF4

ATTRIBUTES = ("Str", "Dex", "Will", "Mag", "Int", "Con")  # creature properties 1-6
BASE_ATTRIBUTE = 10.0  # CHARGEN_BASE_ATTRIBUTE_VALUE, RULES_ATTRIBUTE_MODIFIER
POINTS_PER_LEVEL = 3.0  # AS_POINTS_PER_LEVEL
CHARGEN_POINTS = 5.0  # PROPERTY_SIMPLE_ATTRIBUTE_POINTS from Chargen_InitializeCharacter
# The class's auto level-up table: how character creation spends the hero's 5 points when it is skipped.
HERO_LEVELUP = {1: "alwarrior_default", 2: "alwizard_default", 3: "alrogue_default"}
UNARMED_DAMAGE = 3.0  # COMBAT_DEFAULT_UNARMED_DAMAGE
UNARMED_ATTRIBUTE_FACTOR = 1.25  # UNARMED_ATTRIBUTE_BONUS_FACTOR
HIT_BIAS = 4.0  # ATTACK_HIT_BIAS
ATTACK_ROLL = 50.0
RANK_PLAYER = 100
NORMAL = 1  # difficulty row
CLASS_ROGUE = 3
CRIT_CHANCE = 3.0  # sys_autoscale_h: melee and ranged critical chance, x the rank's fscale
FLANKING_MAX = 15.0  # Combat_GetFlankingBonus (20 with Combat Movement); rogues get all of it, others half
# The engine's derived stats, per attribute point above 10 (the game's character sheet): melee attack
# from strength and dexterity, defense from dexterity, health from constitution, mana or stamina from
# willpower, armour penetration from cunning.
DERIVED = {"AttackStr": 0.5, "AttackDex": 0.5, "DefenseDex": 1.0, "HealthCon": 5.0, "StaminaWill": 5.0,
           "PenetrationInt": 1.0 / 7.0}

_COLUMNS = {
    "packages_base.gda": ["ID", "label", "Strategy", "StartingClass", "MinLevel", "LevelsPerAbility"],
    "autoscale.gda": ["ID", "fscale", "fHealthScale", "nBonusPoints", "nLevelScale", "fDamageScale"],
    "as_data.gda": ["ID", "label", "s1", "s2", "s3", "s4", "s5", "s6"],
    "cla_data.gda": ["ID", "label", "BaseHealth", "HealthPerLevel", "BaseAttack", "BaseDefense", "DefensePerLevel",
                     "DamagePerLevel", "BaseManaStamina", "DepletableProgression",
                     "StrAdjust", "DexAdjust", "WillAdjust", "MagAdjust", "IntAdjust", "ConAdjust"],
    "race_base.gda": ["ID", "label", "StrAdjust", "DexAdjust", "WillAdjust", "MagAdjust", "IntAdjust", "ConAdjust"],
    "itemstats.gda": ["ID", "label", "Damage", "DamageRange", "ArmorPenetration", "CritChanceModifier", "AttributeMod",
                      "Attribute0", "Attribute1", "Armor", "Defense", "MissileDeflection", "dspeed"],
    "materialtypes.gda": ["ID", "label", "Armor"],
    "difficulty.gda": ["ID", "label", "DmgScalingThresh"],
    "apr_base.gda": ["ID", "label", "creature_type", "DefaultWeapon", "DefaultArmor", "MovementTree"],
    "alwarrior_default.gda": ["ID", "AttInit"],
    "alwizard_default.gda": ["ID", "AttInit"],
    "alrogue_default.gda": ["ID", "AttInit"],
}
# CalculateAttackTiming (core_h): a humanoid's seconds per attack by how it wields its weapons (BASE_TIMING_*),
# plus the weapon's dspeed; anything else attacks as fast as its attack animations play.
BASE_TIMING = {"single": 2.0, "dual": 1.5, "twohanded": 2.5}
_TWO_HANDED = ("Weapon - Greatsword", "Weapon - Battleaxe", "Weapon - Maul", "Weapon - Staff")
ANIM_LENGTH = 4009  # an animation's length in seconds (.ani, GFF4)


def load_tables(game_dir: str | Path, overrides: str | Path | None = None) -> dict[str, dict[int, dict]]:
    """The tables above, by name and row ID, from packages/core/data/2da.erf, and a mod's override
    tables from `overrides` on top (apply_overrides)."""
    out = {}
    with ERF.open(Path(game_dir) / "packages" / "core" / "data" / "2da.erf") as erf:
        for name, columns in _COLUMNS.items():
            out[name[:-4]] = {r["ID"]: r for r in GDA(GFF4(erf.read(name)), columns).records()}
    return apply_overrides(out, overrides) if overrides else out


def apply_overrides(tables: dict[str, dict[int, dict]], overrides: str | Path) -> dict[str, dict[int, dict]]:
    """Put the rows of the override tables in `overrides` (<table>_<suffix>.gda) in place of `tables`' rows."""
    for name, columns in _COLUMNS.items():
        for p in override_files(overrides, name[:-4]):
            tables.setdefault(name[:-4], {}).update({r["ID"]: r for r in GDA.open(p, columns).records()})
    return tables


def weapon_base_item(equip: list[dict], items: dict[str, dict], itemstats: dict[int, dict]) -> int | None:
    """The base item type of the first equipped item that is a weapon (its base type
    has weapon damage in itemstats), or None: unarmed."""
    for e in equip or []:
        uti = items.get(str(e.get("TemplateResRef") or "").lower())
        base = int((uti or {}).get("BaseItem") or 0)
        if base and float(itemstats.get(base, {}).get("Damage") or 0) > 0:
            return base
    return None


def natural_equipment(appearance: int, equip: list[dict], items: dict[str, dict], tables: dict) -> list[dict]:
    """creature_core's EquipDefaultItem at spawn: the appearance's DefaultWeapon (a rat's or a dog's bite) when no
    weapon is equipped, its DefaultArmor when no chest piece is. Returned as extra Equip_ItemList entries; they
    count for the numbers, not for the look."""
    apr = tables.get("apr_base", {}).get(appearance) or {}
    extra = []
    if weapon_base_item(equip, items, tables["itemstats"]) is None and apr.get("DefaultWeapon"):
        extra.append({"TemplateResRef": str(apr["DefaultWeapon"]).rsplit(".", 1)[0]})
    if "chest" not in equipment(equip, items, tables)["Outfit"] and apr.get("DefaultArmor"):
        extra.append({"TemplateResRef": str(apr["DefaultArmor"]).rsplit(".", 1)[0]})
    return extra


def attack_anims(game_dir: str | Path, tables: dict, appearances) -> dict[int, float]:
    """Per appearance, the mean length of its attack animations (seconds): the attack nodes ("attk..." or
    "atk...") of its combat tree in anims.erf, named like its MovementTree with _cbt for _expmvt (C_DOGa_expmvt.anb
    -> C_DOGa_cbt.anb). A creature without a humanoid's weapon attacks once per animation."""
    out = {}
    with ERF.open(Path(game_dir) / "packages" / "core" / "data" / "anims.erf") as erf:
        names = {e.name.lower(): e.name for e in erf.entries}

        def root(name):
            return GFF4(erf.read(names[name.lower()])).root

        for a in set(appearances):
            tree = str((tables["apr_base"].get(a) or {}).get("MovementTree") or "").lower().replace("_expmvt", "_cbt")
            if tree not in names:
                continue
            anims = [n.get(4025) for n in root(tree).get(4021) or [] if str(n.get(4024) or "").startswith(("attk", "atk"))]
            lengths = [float(root(x).get(ANIM_LENGTH) or 0) for x in anims if x and str(x).lower() in names]
            if lengths:
                out[a] = round(sum(lengths) / len(lengths), 3)
    return out


def attack_interval(equip: list[dict], items: dict[str, dict], tables: dict, anim: float | None = None) -> float:
    """Seconds between attacks (CalculateAttackTiming): with a weapon ("Weapon - ..." in itemstats), the wield
    style's base timing plus the weapon's dspeed: two weapons and no shield 1.5, a two-handed one 2.5, else 2.0;
    otherwise `anim` (attack_anims), or 2.0 if unknown."""
    weapons = []
    shield = False
    for e in equip or []:
        uti = items.get(str(e.get("TemplateResRef") or "").lower()) or {}
        row = tables["itemstats"].get(int(uti.get("BaseItem") or -1)) or {}
        label = str(row.get("label") or "")
        shield = shield or piece(label) == "shield"
        if label.startswith("Weapon - ") and float(row.get("Damage") or 0) > 0 and not label.endswith("bow"):
            weapons.append(row)
    if not weapons:
        return anim or BASE_TIMING["single"]
    main = weapons[0]
    if str(main.get("label")).startswith(_TWO_HANDED):
        style = "twohanded"
    elif len(weapons) > 1 and not shield:
        style = "dual"
    else:
        style = "single"
    return round(BASE_TIMING[style] + float(main.get("dspeed") or 0.0), 3)


# What an equipped item is, from its base item's label in itemstats.
_PIECES = (("Armor -", "chest"), ("Clothing", "chest"), ("Helmet", "helmet"), ("Gloves", "gloves"),
           ("Boots", "boots"), ("Shield", "shield"), ("Ambient - Shield", "shield"))


def piece(label: str) -> str | None:
    return next((p for prefix, p in _PIECES if label.startswith(prefix)), None)


def equipment(equip: list[dict], items: dict[str, dict], tables: dict) -> dict:
    """What a creature wears and the armour it gives: {"Outfit": {piece: item
    template}, "Armour", "ShieldDefense", "MissileDeflection"}. A piece's armour is
    its base item's Armor times its material's Armor multiplier; the leather and
    hide materials have none (0) and count as 1. Shields give defense and missile
    deflection, not armour."""
    outfit: dict[str, str] = {}
    armour = defense = deflection = 0.0
    for e in equip or []:
        ref = str(e.get("TemplateResRef") or "").lower()
        uti = items.get(ref)
        base = tables["itemstats"].get(int((uti or {}).get("BaseItem") or -1))
        kind = piece(str(base.get("label") or "")) if base else None
        if kind is None or kind in outfit:
            continue
        outfit[kind] = ref
        material = float(tables["materialtypes"].get(int(uti.get("Material") or 0), {}).get("Armor") or 0.0)
        armour += float(base.get("Armor") or 0.0) * (material or 1.0)
        defense += float(base.get("Defense") or 0.0)
        deflection += float(base.get("MissileDeflection") or 0.0)
    return {"Outfit": outfit, "Armour": round(armour, 3), "ShieldDefense": round(defense, 3),
            "MissileDeflection": round(deflection, 3)}


def stats(tables: dict, *, package: int, rank: int, area_level: int = 1, race: int | None = None,
          base_item: int | None = None, player_class: int | None = None, hero: bool = False) -> dict:
    """Level, attributes, max health, stamina (or mana), attack, defense, the damage
    range (min, max) before armour and the flat damage bonus after it, armour
    penetration, critical chance and the most flanking can add, for one creature.

    Attributes: the hero (`hero`) as character creation leaves them when skipped: 10, plus race and class
    adjustments, plus the class's default spending of the 5 free points (al<class>_default AttInit,
    AL_DoAutoLevelUp). Every other creature, party members too, as AS_CommenceAutoScaling sets them:
    Chargen_InitializeCharacter gives it the same 5 points (CHARGEN_POINTS) and its race; each attribute its
    strategy weighs is then set afresh to 10 + its share of the rank's bonus points, the 5 points, and
    (rank scale x 3 + 5) for each level above 1 (so the race counts only for attributes the strategy does not
    weigh); the class adjustments come last (AS_AddClassLevels)."""
    pkg = tables["packages_base"].get(package, {})
    cls_id = player_class or int(pkg.get("StartingClass") or 1)
    cls = tables["cla_data"].get(cls_id, {})
    auto = tables["autoscale"].get(rank) or tables["autoscale"].get(RANK_PLAYER, {})
    strategy = tables["as_data"].get(int(pkg.get("Strategy") or cls_id), {})

    # AS_GetCreatureLevelToScale: area level plus the rank's offset, at least 1 and the package minimum
    level = max(1, area_level + int(auto.get("nLevelScale") or 0), int(pkg.get("MinLevel") or 0))
    fscale = float(auto.get("fscale") or 1.0)
    bonus = float(auto.get("nBonusPoints") or 0)
    effective = fscale * POINTS_PER_LEVEL + CHARGEN_POINTS  # fEffectivePoints
    free = tables.get(HERO_LEVELUP.get(cls_id, ""), {})

    attrs = {}
    for i, name in enumerate(ATTRIBUTES, 1):
        per = float(strategy.get(f"s{i}") or 0.0)
        racial = float(tables["race_base"].get(race, {}).get(f"{name}Adjust") or 0) if race is not None else 0.0
        if hero:
            value = BASE_ATTRIBUTE + racial + float(free.get(i, {}).get("AttInit") or 0)
        elif per > 0:
            weight = (1 / per) / POINTS_PER_LEVEL
            value = float(int((level - 1) * effective * weight + weight * bonus + weight * CHARGEN_POINTS
                              + BASE_ATTRIBUTE + 0.5))
        else:
            value = BASE_ATTRIBUTE + racial
        value += float(cls.get(f"{name}Adjust") or 0)  # Chargen_ApplyClassAttributeModifiers at level 1
        attrs[name] = value

    mod = {k: max(0.0, v - BASE_ATTRIBUTE) for k, v in attrs.items()}  # GetAttributeModifier
    health_scale = float(auto.get("fHealthScale") or 1.0)
    health = float(cls.get("BaseHealth") or 0) * health_scale + \
        float(cls.get("HealthPerLevel") or 0) * health_scale * (level - 1) + DERIVED["HealthCon"] * mod["Con"]
    # Mana and stamina scale with the rank's fscale (Chargen_ApplyClassStatModifiers, AS_AddClassLevels).
    stamina = (float(cls.get("BaseManaStamina") or 0) + float(cls.get("DepletableProgression") or 0) * (level - 1)) \
        * fscale + DERIVED["StaminaWill"] * mod["Will"]
    attack = float(cls.get("BaseAttack") or 0) + DERIVED["AttackStr"] * mod["Str"] + DERIVED["AttackDex"] * mod["Dex"]
    defense = float(cls.get("BaseDefense") or 0) + DERIVED["DefenseDex"] * mod["Dex"]
    damage_bonus = float(cls.get("DamagePerLevel") or 0) * level  # PROPERTY_ATTRIBUTE_DAMAGE_BONUS, after armour

    # Combat_Damage_GetAttackDamage: weapon + attribute bonus, then armour, then the damage bonus, rank-scaled
    # above the difficulty's threshold. The attribute bonus is 25-50% of the weapon's attribute above 10
    # (Attribute0, or the mean of Attribute0 and 1: strength and dexterity for bows), x its AttributeMod
    # (1.25 unarmed).
    item = tables["itemstats"].get(base_item or -1)
    if item:
        low = float(item.get("Damage") or 0)
        high = low * max(1.0, float(item.get("DamageRange") or 1.0))
        factor = float(item.get("AttributeMod") or 1.0)
        a0, a1 = int(item.get("Attribute0") or 1), int(item.get("Attribute1") or 0)
        bonus = (mod[ATTRIBUTES[a0 - 1]] + mod[ATTRIBUTES[a1 - 1]]) / 2 if a1 else mod[ATTRIBUTES[a0 - 1]]
        penetration = float(item.get("ArmorPenetration") or 0)
        weapon_crit = float(item.get("CritChanceModifier") or 0)
    else:
        low, high, factor = UNARMED_DAMAGE, UNARMED_DAMAGE * 1.5, UNARMED_ATTRIBUTE_FACTOR
        bonus, penetration, weapon_crit = mod["Str"], 0.0, 0.0
    threshold = float(tables["difficulty"].get(NORMAL, {}).get("DmgScalingThresh") or 0)
    scale = float(auto.get("fDamageScale") or 1.0)
    return {"Level": level, "Class": cls.get("label", ""), "Attributes": attrs, "Health": round(health, 1),
            "Stamina": round(stamina, 1), "Attack": attack, "Defense": defense,
            # Each hit rolls in this range, then hit_damage() applies criticals, armour, the bonus and rank scaling.
            "Damage": (round(low + bonus * 0.25 * factor, 2), round(high + bonus * 0.5 * factor, 2)),
            "DamageBonus": round(damage_bonus, 2),
            "Penetration": round(penetration + DERIVED["PenetrationInt"] * mod["Int"], 2),
            "Crit": round(CRIT_CHANCE * fscale + weapon_crit, 2),
            "Flanking": FLANKING_MAX * (1.0 if cls_id == CLASS_ROGUE else 0.5),
            "DamageScale": scale, "DamageThreshold": threshold}


CRIT_DAMAGE = 1.5  # COMBAT_CRITICAL_DAMAGE_MODIFIER
ARMOUR_RANDOM = 0.3  # COMBAT_ARMOR_RANDOM_ELEMENT: armour is 70% fixed, 30% rolled


def hit_damage(rolled: float, *, crit: bool = False, armour: float = 0.0, armour_roll: float = 1.0,
               penetration: float = 0.0, bonus: float = 0.0, scale: float = 1.0, threshold: float = 0.0) -> float:
    """Combat_Damage_GetAttackDamage after the weapon roll: x1.5 on a critical, minus the target's armour
    (`armour_roll`, 0-1, picks the random 30%) less armour penetration, plus the flat damage bonus, x the
    rank's damage scale when above the difficulty's threshold, at least 1."""
    damage = rolled * (CRIT_DAMAGE if crit else 1.0)
    armour_rolled = armour * armour_roll * ARMOUR_RANDOM + armour * (1.0 - ARMOUR_RANDOM)
    damage = damage - max(0.0, armour_rolled - penetration) + bonus
    return damage_after_scaling(damage, scale, threshold)


def damage_after_scaling(rolled: float, scale: float, threshold: float) -> float:
    """The rank's damage scale applies to hits above the difficulty's threshold."""
    if scale > 0 and rolled > threshold:
        rolled *= scale
    return max(1.0, rolled)


def hit_chance(attack: float, defense: float, flanking: float = 0.0) -> float:
    """Combat_GetAttackResult for a melee attack at point blank: percent to hit."""
    return max(0.0, min(100.0, attack + ATTACK_ROLL + HIT_BIAS + flanking - defense))


def flanking_bonus(angle: float, most: float, flanking_angle: float = 60.0) -> float:
    """Combat_GetFlankingBonus: `angle` is where the attacker stands seen from the target, in degrees
    from the way the target faces (180: right behind it). Within `flanking_angle` of right behind, the
    bonus grows to `most` (stats()["Flanking"]) at 180."""
    off = abs(180.0 - abs(angle))
    return most * (flanking_angle - off) / flanking_angle if off <= flanking_angle else 0.0


def crit_chance(crit: float, flanking: float = 0.0) -> float:
    """Combat_GetAttackResult: flanking multiplies the critical chance by 1 + a fifth of its bonus."""
    return crit * (1.0 + flanking / 5.0) if flanking > 0 else crit
