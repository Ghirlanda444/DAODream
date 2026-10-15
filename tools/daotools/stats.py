"""Creature stats from the game's data tables, as the scripts compute them.

A port of sys_autoscale_h (AS_CommenceAutoScaling, AS_AddClassLevels),
sys_chargen_h (Chargen_ApplyClassStatModifiers) and combat_damage_h /
combat_h (Combat_Damage_GetAttackDamage, Combat_GetAttackResult), reading:

  packages_base  a creature's Package: StartingClass, Strategy, MinLevel
  autoscale      per rank: fscale, fHealthScale, nBonusPoints, nLevelScale, fDamageScale
  as_data        per strategy: s1..s6, levels per point of each attribute
  cla_data       per class: BaseHealth, HealthPerLevel, BaseAttack, BaseDefense,
                 DamagePerLevel, Str/Dex/Will/Mag/Int/ConAdjust
  race_base      per race: the same six adjustments (the player only)
  itemstats      per base item: Damage, DamageRange
  difficulty     DmgScalingThresh (Normal)

What the engine adds on top (attribute bonuses to attack, defense and health,
armour, item materials, talents) is not in the scripts and not included.
"""

from __future__ import annotations

from pathlib import Path

from .erf import ERF
from .gda import GDA
from .gff4 import GFF4

ATTRIBUTES = ("Str", "Dex", "Will", "Mag", "Int", "Con")  # creature properties 1-6
BASE_ATTRIBUTE = 10.0  # CHARGEN_BASE_ATTRIBUTE_VALUE, RULES_ATTRIBUTE_MODIFIER
POINTS_PER_LEVEL = 3.0  # AS_POINTS_PER_LEVEL
UNARMED_DAMAGE = 3.0  # COMBAT_DEFAULT_UNARMED_DAMAGE
UNARMED_ATTRIBUTE_FACTOR = 1.25  # UNARMED_ATTRIBUTE_BONUS_FACTOR
HIT_BIAS = 4.0  # ATTACK_HIT_BIAS
ATTACK_ROLL = 50.0
RANK_PLAYER = 100
NORMAL = 1  # difficulty row

_COLUMNS = {
    "packages_base.gda": ["ID", "label", "Strategy", "StartingClass", "MinLevel", "LevelsPerAbility"],
    "autoscale.gda": ["ID", "fscale", "fHealthScale", "nBonusPoints", "nLevelScale", "fDamageScale"],
    "as_data.gda": ["ID", "label", "s1", "s2", "s3", "s4", "s5", "s6"],
    "cla_data.gda": ["ID", "label", "BaseHealth", "HealthPerLevel", "BaseAttack", "BaseDefense", "DefensePerLevel",
                     "DamagePerLevel", "StrAdjust", "DexAdjust", "WillAdjust", "MagAdjust", "IntAdjust", "ConAdjust"],
    "race_base.gda": ["ID", "label", "StrAdjust", "DexAdjust", "WillAdjust", "MagAdjust", "IntAdjust", "ConAdjust"],
    "itemstats.gda": ["ID", "label", "Damage", "DamageRange", "Attribute0", "Attribute1"],
    "difficulty.gda": ["ID", "label", "DmgScalingThresh"],
}


def load_tables(game_dir: str | Path) -> dict[str, dict[int, dict]]:
    """The tables above, by name and row ID, from packages/core/data/2da.erf."""
    out = {}
    with ERF.open(Path(game_dir) / "packages" / "core" / "data" / "2da.erf") as erf:
        for name, columns in _COLUMNS.items():
            out[name[:-4]] = {r["ID"]: r for r in GDA(GFF4(erf.read(name)), columns).records()}
    return out


def weapon_base_item(equip: list[dict], items: dict[str, dict], itemstats: dict[int, dict]) -> int | None:
    """The base item type of the first equipped item that is a weapon (its base type
    has weapon damage in itemstats), or None: unarmed."""
    for e in equip or []:
        uti = items.get(str(e.get("TemplateResRef") or "").lower())
        base = int((uti or {}).get("BaseItem") or 0)
        if base and float(itemstats.get(base, {}).get("Damage") or 0) > 0:
            return base
    return None


def stats(tables: dict, *, package: int, rank: int, area_level: int = 1, race: int | None = None,
          base_item: int | None = None, player_class: int | None = None) -> dict:
    """Level, attributes, max health, attack, defense and damage range (min, max)
    for one creature. `race` is applied for the player only, as character creation
    does; creatures get their attributes from the autoscale strategy."""
    pkg = tables["packages_base"].get(package, {})
    cls_id = player_class or int(pkg.get("StartingClass") or 1)
    cls = tables["cla_data"].get(cls_id, {})
    auto = tables["autoscale"].get(rank) or tables["autoscale"].get(RANK_PLAYER, {})
    strategy = tables["as_data"].get(int(pkg.get("Strategy") or cls_id), {})

    # AS_GetCreatureLevelToScale: area level plus the rank's offset, at least 1 and the package minimum
    level = max(1, area_level + int(auto.get("nLevelScale") or 0), int(pkg.get("MinLevel") or 0))
    fscale = float(auto.get("fscale") or 1.0)
    bonus = float(auto.get("nBonusPoints") or 0)

    attrs = {}
    for i, name in enumerate(ATTRIBUTES, 1):
        per = float(strategy.get(f"s{i}") or 0.0)
        value = BASE_ATTRIBUTE
        if per > 0 and rank != RANK_PLAYER:
            weight = (1 / per) / POINTS_PER_LEVEL
            value = int((level - 1) * fscale * POINTS_PER_LEVEL * weight + weight * bonus + BASE_ATTRIBUTE + 0.5)
        value += float(cls.get(f"{name}Adjust") or 0)  # Chargen_ApplyClassAttributeModifiers at level 1
        if race is not None:
            value += float(tables["race_base"].get(race, {}).get(f"{name}Adjust") or 0)
        attrs[name] = value

    health_scale = float(auto.get("fHealthScale") or 1.0)
    health = float(cls.get("BaseHealth") or 0) * health_scale + \
        float(cls.get("HealthPerLevel") or 0) * health_scale * (level - 1)
    attack = float(cls.get("BaseAttack") or 0)
    defense = float(cls.get("BaseDefense") or 0)
    damage_bonus = float(cls.get("DamagePerLevel") or 0) * level

    # Combat_Damage_GetAttackDamage against no armour: weapon + strength bonus, rank-scaled above
    # the difficulty's threshold; the strength bonus is 25-50% of (STR - 10), x1.25 unarmed.
    item = tables["itemstats"].get(base_item or -1)
    if item:
        low = float(item.get("Damage") or 0)
        high = low * max(1.0, float(item.get("DamageRange") or 1.0))
        factor = 1.0
    else:
        low, high, factor = UNARMED_DAMAGE, UNARMED_DAMAGE * 1.5, UNARMED_ATTRIBUTE_FACTOR
    strength = max(0.0, attrs["Str"] - BASE_ATTRIBUTE)
    threshold = float(tables["difficulty"].get(NORMAL, {}).get("DmgScalingThresh") or 0)
    scale = float(auto.get("fDamageScale") or 1.0)
    return {"Level": level, "Class": cls.get("label", ""), "Attributes": attrs, "Health": round(health, 1),
            "Attack": attack, "Defense": defense,
            # Before rank scaling: each hit rolls in this range, then damage_after_scaling() applies.
            "Damage": (round(low + strength * 0.25 * factor + damage_bonus, 2),
                       round(high + strength * 0.5 * factor + damage_bonus, 2)),
            "DamageScale": scale, "DamageThreshold": threshold}


def damage_after_scaling(rolled: float, scale: float, threshold: float) -> float:
    """The rank's damage scale applies to hits above the difficulty's threshold."""
    if scale > 0 and rolled > threshold:
        rolled *= scale
    return max(1.0, rolled)


def hit_chance(attack: float, defense: float) -> float:
    """Combat_GetAttackResult for a melee attack at point blank: percent to hit."""
    return max(0.0, min(100.0, attack + ATTACK_ROLL + HIT_BIAS - defense))
