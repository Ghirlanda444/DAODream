"""Loot: the original's treasure system (sys_treasure_h) and its items (docs/LOOT.md).

What drops (TreasureGenerate, when a container spawns or a creature dies): a target's treasure rank (a creature's
Rank, a placeable's Rank field) and category (TreasureCategory: ts_category's Prefix, TS_Ferelden...) pick its
tables, ts_<prefix><Cre|Plc><table>, the table named by autoscale's TS_LowTable for the rank, or TS_HighTable with
the rank's TS_HighChance. It draws TS_ItemNum items (a fraction is a chance of one more: TS_GetItemNum; a container
always has at least one), each a random row of the table: an item and a stack (80-100% of the row's, rounded up),
or copper, scaled to the target's level (6 x level^2 x the row's stack, 80-120%). A creature first has a 30%
chance of the table's first row when it is copper; then money and other items exclude each other. A hostile
creature carrying no potions may drop a poultice or a lyrium potion when the party has few (the reactive drops:
difficulty ReactiveLimit and ReactiveChance), and one of its equipped pieces becomes droppable with the rank's
TS_EquipmentChance (bitm_base DoNotDrop excepted). Its backpack and droppable equipment come too.

Items (catalog): a template's name, its base item (bitm_base: Type, StackSize), value (Cost, copper), the ability
it uses (AbilityID: the poultices 200010-200013 heal (50 + spellpower) x 1-4; the lyrium potions 200030-200033
give a mage 50-200 + spellpower x 0.5 mana; item_singletarget) and the properties the AI looks for
(ITEM_PROPERTY_IS_HEALING_POTION 6116, IS_MANA_POTION 6117: _AI_GetPotionByFilter picks the dearest or the cheapest).

Containers (Placeable_HandleUsed): a locked one (InitialState 1) opens with its key or to a rogue whose disable
device level (cunning modifier + 10 a rank of Lockpicking) reaches its PickLock.
"""

from __future__ import annotations

import random
from pathlib import Path

from .erf import ERF
from .gda import GDA
from .gff4 import GFF4

MONEY = "gen_im_copper"
MONEY_MULTIPLIER = 6  # TS_MONEY_MULTIPLIER
GLOBAL_MONEY_CHANCE = 30  # TS_GLOBAL_MONEY_DROP_CHANCE, percent
HEALING, MANA = 6116, 6117  # ITEM_PROPERTY_IS_HEALING_POTION, ITEM_PROPERTY_IS_MANA_POTION
# the reactive drops' potions by tier (REACTIVE_TIER<n>_HEALTH / _MANA)
REACTIVE_HEALTH = ("gen_im_qck_health_101", "gen_im_qck_health_201", "gen_im_qck_health_301", "gen_im_qck_health_401")
REACTIVE_MANA = ("gen_im_qck_mana_101", "gen_im_qck_mana_201", "gen_im_qck_mana_301", "gen_im_qck_mana_401")
REACTIVE_HEALTH_BASE_CHANCE = 0.1
NORMAL = 1  # difficulty
# item abilities (item_constants_h) and what they do: (kind, base, factor)
HEALTH_SALVE_BASE = 50.0
POULTICES = {200010: 1.0, 200011: 2.0, 200012: 3.0, 200013: 4.0}  # x (50 + spellpower)
LYRIUM = {200030: 50.0, 200031: 100.0, 200032: 150.0, 200033: 200.0}  # + spellpower x 0.5, magic users only
LYRIUM_MAGIC_FACTOR = 0.5
KIND_MISC, KIND_HEALTH, KIND_MANA, KIND_GEAR, KIND_MONEY = 0, 1, 2, 3, 4
CHEST_TYPES = (2,)  # placeable_basetypes Chest: the containers TreasureGenerate fills at spawn
LOCKED = 1  # PLC_STATE_CONTAINER_LOCKED
_NAME = "0x3273f70d"  # bitm_base: the base item's name StrRef


def load_tables(game_dir: str | Path, overrides: str | Path | None = None) -> dict:
    """{"categories": {id: prefix}, "ranks": {rank: autoscale row}, "tables": {name: [(resref, stack)]},
    "bitm": {base item: row}, "difficulty": {id: row}, "placeable_types": {appearance: BaseType}}; a rebalance
    mod's autoscale (`overrides`, autoscale_<suffix>.gda) on top."""
    from .stats import override_files
    out = {"categories": {}, "ranks": {}, "tables": {}, "bitm": {}, "difficulty": {}, "placeable_types": {}}
    rank_cols = ["ID", "TS_LowTable", "TS_HighTable", "TS_Money", "TS_ItemNum", "TS_HighChance", "TS_EquipmentChance",
                 "nReactiveTier", "nLevelScale"]
    with ERF.open(Path(game_dir) / "packages" / "core" / "data" / "2da.erf") as erf:
        out["categories"] = {int(r["ID"]): str(r.get("Prefix") or "")
                             for r in GDA(GFF4(erf.read("ts_category.gda")), ["ID", "Label", "Prefix"]).records()}
        out["ranks"] = {int(r["ID"]): r for r in GDA(GFF4(erf.read("autoscale.gda")), rank_cols).records()}
        for e in erf.entries:
            name = e.name.lower()
            if name.startswith("ts_") and name.endswith(".gda") and name != "ts_category.gda":
                rows = GDA(GFF4(erf.read(e.name)), ["ID", "Resource", "StackSize"]).records()
                out["tables"][name[:-4]] = [(str(r.get("Resource") or "").lower().removesuffix(".uti"),
                                             int(r.get("StackSize") or 1)) for r in rows]
        out["bitm"] = {int(r["ID"]): r for r in GDA(GFF4(erf.read("bitm_base.gda")),
                                                   ["ID", "label", _NAME, "Type", "StackSize", "DoNotDrop"]).records()}
        out["difficulty"] = {int(r["ID"]): r for r in GDA(GFF4(erf.read("difficulty.gda")),
                                                         ["ID", "label", "ReactiveLimit", "ReactiveChance"]).records()}
        out["placeable_types"] = {int(r["ID"]): int(r.get("BaseType") or 0)
                                  for r in GDA(GFF4(erf.read("placeable_types.gda")), ["ID", "Label", "BaseType"]).records()}
    if overrides:
        for p in override_files(overrides, "autoscale"):
            for r in GDA.open(p, rank_cols).records():
                out["ranks"].setdefault(int(r["ID"]), {}).update({k: v for k, v in r.items() if v not in (None, "")})
    return out


def table_name(tables: dict, category: int, rank: int, placeable: bool, high: bool) -> str:
    """The treasure table a draw comes from: ts_<prefix><cre|plc><TS_LowTable or TS_HighTable>, lower case."""
    prefix = tables["categories"].get(category, "")
    row = tables["ranks"].get(rank) or {}
    return (prefix + ("Plc" if placeable else "Cre") + str(row.get("TS_HighTable" if high else "TS_LowTable") or "")).lower()


def item_num(f: float, placeable: bool, rng: random.Random) -> int:
    """TS_GetItemNum: up to int(f) + 1 draws, each kept with the chance left; a container has one at least."""
    n = 0
    for _ in range(int(f) + 1):
        r = rng.random()
        if r <= f:
            f -= r
            n += 1
        f -= 1.0
        if f <= 0.0:
            break
    return max(n, 1) if placeable else n


def scaled_money(level: int, size: int, rng: random.Random) -> int:
    """TS_GetScaledMoney: 6 x level^2 x the drop's size, 80-120%."""
    return int(MONEY_MULTIPLIER * level * level * size * (0.8 + rng.random() * 0.4))


def stack(size: int, rng: random.Random) -> int:
    """A treasure row's stack: 80-100% of it, rounded up, at least 1."""
    if size <= 1:
        return 1
    f = rng.random() * 0.2 + 0.8
    n = max(1, int(f * size))
    if n < size * f:
        n += 1
    return max(n, 1)


def level_of(tables: dict, level: int, rank: int, area_level: int) -> int:
    """TS_GetLevel: the target's level, or for a placeable the area's plus the rank's nLevelScale (at least 1)."""
    if level >= 1:
        return level
    return max(1, area_level + int((tables["ranks"].get(rank) or {}).get("nLevelScale") or 0))


def generate(tables: dict, category: int, rank: int, level: int, placeable: bool, rng: random.Random,
             party_potions: tuple[int, int] = (99, 99), hostile: bool = False, carries_potions: bool = False,
             hero_level: int = 1, difficulty: int = NORMAL,
             carried: list[tuple[str, int]] = ()) -> tuple[int, list[tuple[str, int]]]:
    """TreasureGenerate's draws for one target: (copper, [(item, count)]), what it `carried` (its backpack and
    droppable equipment) first: a creature carrying anything gets no money from its draws. `party_potions`: the
    party's health and mana potions (the reactive drops); `hostile` and `carries_potions`: a hostile creature
    without potions of its own may drop one."""
    items: list[tuple[str, int]] = list(carried)
    money = 0
    row = tables["ranks"].get(rank) or {}
    if rank <= 0:
        return 0, []
    if not placeable and hostile and not carries_potions:
        potion = reactive(tables, rank, party_potions, hero_level, difficulty, rng)
        if potion:
            items.append((potion, 1))
    if category <= 0:
        return 0, items
    n = item_num(float(row.get("TS_ItemNum") or 0.0), placeable, rng)
    high = float(row.get("TS_HighChance") or 0.0)
    low_name = table_name(tables, category, rank, placeable, False)
    if not placeable:  # the global money chance, when the low table's first row is copper
        first = (tables["tables"].get(low_name) or [("", 0)])[0]
        if first[0] == MONEY and rng.randint(1, 100) <= GLOBAL_MONEY_CHANCE:
            money += scaled_money(level, first[1], rng)
    for _ in range(n):
        name = table_name(tables, category, rank, placeable, rng.random() <= high)
        rows = tables["tables"].get(name) or []
        if not rows:
            continue
        ref, size = rows[rng.randrange(len(rows))]
        if ref == MONEY:
            if not placeable and items:  # other items already: no money
                continue
            money += scaled_money(level, size, rng)
        else:
            if not placeable and money > 0:  # money already: no other treasure
                continue
            items.append((ref, stack(size, rng)))
    return money, items


def reactive(tables: dict, rank: int, party_potions: tuple[int, int], hero_level: int, difficulty: int,
             rng: random.Random) -> str | None:
    """The reactive drop: when the party holds fewer than ReactiveLimit health or mana potions, a chance
    ((1 - fewest / limit) / 4 x ReactiveChance x max(1, TS_ItemNum)) of a potion of the rank's tier (one more at
    hero levels 10 and 15 now and then), health more likely the fewer health potions there are."""
    health, mana = party_potions
    d = tables["difficulty"].get(difficulty) or {}
    limit = int(d.get("ReactiveLimit") or 0)
    if not (health < limit or mana < limit):
        return None
    limit = max(limit, 1)
    row = tables["ranks"].get(rank) or {}
    chance = (1.0 - min(health, mana) / limit) / 4.0 * float(d.get("ReactiveChance") or 0.0) * \
        max(float(row.get("TS_ItemNum") or 0.0), 1.0)
    if rng.random() >= chance:
        return None
    tier = int(row.get("nReactiveTier") or 0)
    if tier <= 0:
        return None
    health_chance = max((1.0 - health / limit) / 2.0, REACTIVE_HEALTH_BASE_CHANCE)
    mana_pick = rng.random() > health_chance
    if 10 <= hero_level < 15 and rng.randint(1, 100) <= 50 or hero_level >= 15 and rng.randint(1, 100) <= 75:
        tier += 1
    ref = (REACTIVE_MANA if mana_pick else REACTIVE_HEALTH)[min(tier, 4) - 1]
    if (mana if mana_pick else health) >= limit:
        return None
    return ref


def equipment_drop(tables: dict, rank: int, equipped: list[int], rng: random.Random) -> int | None:
    """TS_GenerateEquipment: with the rank's TS_EquipmentChance, one equipped piece (its index in `equipped`, a
    list of base items) becomes droppable, unless its base item may not drop."""
    if not equipped:
        return None
    if rng.random() > float((tables["ranks"].get(rank) or {}).get("TS_EquipmentChance") or 0.0):
        return None
    k = rng.randrange(len(equipped))
    return None if int((tables["bitm"].get(equipped[k]) or {}).get("DoNotDrop") or 0) else k


def item_info(uti: dict, tables: dict, name=None) -> dict:
    """What the game shows and uses of an item template: Name, Description, Kind (KIND_*), Ability, Value
    (copper), Stack (its base item's), Power (a poultice's factor, a lyrium potion's base)."""
    base = int(uti.get("BaseItem") or 0)
    b = tables["bitm"].get(base) or {}
    props = {int(p.get("PropertyID") or 0) for p in uti.get("PropertiesList") or []}
    ability = int(uti.get("AbilityID") or -1)
    ref = str(uti.get("TemplateResRef") or "").lower()
    if ref == MONEY:
        kind = KIND_MONEY
    elif HEALING in props:
        kind = KIND_HEALTH
    elif MANA in props:
        kind = KIND_MANA
    elif int(b.get("Type") or 1) in (2, 3):  # weapons, armour and shields
        kind = KIND_GEAR
    else:
        kind = KIND_MISC

    def text(v):
        if isinstance(v, dict):
            return v.get("text") or (name(v["strref"]) if name and v.get("strref") else "") or ""
        return str(v or "")
    return {"Name": text(uti.get("LocalizedName")) or ref, "Description": text(uti.get("Description")), "Kind": kind,
            "Ability": ability, "Value": int(uti.get("Cost") or 0), "Stack": int(b.get("StackSize") or 1),
            "Power": POULTICES.get(ability, LYRIUM.get(ability, 0.0)), "Base": base}


def potion_effect(ability: int, spellpower: float, magic_user: bool) -> tuple[float, float]:
    """(health, mana) an item ability gives (item_singletarget): a poultice (50 + spellpower) x its factor, a
    lyrium potion its base + spellpower x 0.5 to a magic user."""
    if ability in POULTICES:
        return (HEALTH_SALVE_BASE + spellpower) * POULTICES[ability], 0.0
    if ability in LYRIUM and magic_user:
        return 0.0, LYRIUM[ability] + spellpower * LYRIUM_MAGIC_FACTOR
    return 0.0, 0.0


def pick_potion(inventory: list[tuple[dict, int]], kind: int, most: bool) -> int | None:
    """_AI_GetPotionByFilter: of the inventory's (item info, count) entries of `kind`, the index of the dearest
    (`most`) or the cheapest, the first of equals for the dearest and the last for the cheapest."""
    best, value = None, 0
    for i, (info, count) in enumerate(inventory):
        if count <= 0 or info["Kind"] != kind:
            continue
        v = info["Value"]
        if most and v > value or not most and (v <= value or value == 0):
            best, value = i, v
    return best


def disable_device(cunning: float, lockpicking_rank: int, rogue: bool) -> float:
    """GetDisableDeviceLevel: a rogue's cunning modifier + 10 a rank of Lockpicking; nobody else picks locks."""
    return max(cunning - 10.0, 0.0) + 10.0 * lockpicking_rank if rogue else -1.0  # GetAttributeModifier: above 10


LOOT_FIELDS = ("Low", "High", "ItemNum", "HighChance", "EquipChance", "ReactiveTier", "FirstMoney", "Level",
               "Placeable")
BACKPACK, DROPPABLE, EQUIPPED = 0, 1, 2  # how a carried item comes to the body: always, always, by chance
CONTAINER_LOOKS = (("chest", 0), ("sack", 1), ("crate", 2), ("weapon", 3), ("armor", 3), ("rubble", 4))  # placeable_types label -> its look


class Export:
    """The loot keys of an area export: the item catalogue (Item*), the treasure tables the area's targets use
    (TreasureRows, TreasureRanges), each target's LOOT_FIELDS and what it carries (Bag rows: item, count, how),
    the reactive potions and the rules. Items are added as they are met; unknown templates are reported."""

    def __init__(self, tables: dict, items: dict[str, dict], area_level: int, name=None, labels=None):
        self.tables, self.items, self.area_level, self.name = tables, items, area_level, name
        self.labels = labels or {}  # placeable_types: appearance -> label
        self.index: dict[str, int] = {}
        self.info: list[dict] = []
        self.tags: list[str] = []
        self.table_index: dict[str, int] = {}
        self.rows: list[float] = []
        self.ranges: list[float] = []
        self.bag: list[float] = []
        self.missing: set[str] = set()

    def item(self, ref: str) -> int:
        ref = ref.lower().removesuffix(".uti")
        if ref not in self.index:
            uti = self.items.get(ref)
            if uti is None:
                self.missing.add(ref)
                return -1
            self.index[ref] = len(self.tags)
            self.tags.append(ref)
            self.info.append(item_info(uti, self.tables, self.name))
        return self.index[ref]

    def table(self, name: str) -> int:
        if name not in self.table_index:
            rows = self.tables["tables"].get(name)
            if rows is None:
                return -1
            self.table_index[name] = len(self.ranges) // 2
            start = len(self.rows) // 2
            kept = [(self.item(ref), size) for ref, size in rows]
            kept = [(i, s) for i, s in kept if i >= 0]
            self.rows += [float(x) for i, s in kept for x in (i, s)]
            self.ranges += [float(start), float(len(kept))]
        return self.table_index[name]

    def fields(self, category: int, rank: int, level: int, placeable: bool) -> list[float]:
        """LOOT_FIELDS for a target; no tables (-1) without a category, nothing at all without a rank."""
        row = self.tables["ranks"].get(rank) or {}
        if rank <= 0 or not row:
            return [-1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, float(placeable)]
        low_name = table_name(self.tables, category, rank, placeable, False)
        low = self.table(low_name) if category > 0 else -1
        high = self.table(table_name(self.tables, category, rank, placeable, True)) if category > 0 else -1
        first = (self.tables["tables"].get(low_name) or [("", 0)])[0] if category > 0 else ("", 0)
        return [float(low), float(high), float(row.get("TS_ItemNum") or 0.0), float(row.get("TS_HighChance") or 0.0),
                float(row.get("TS_EquipmentChance") or 0.0), float(row.get("nReactiveTier") or 0),
                float(first[1]) if first[0] == MONEY else 0.0,
                float(level_of(self.tables, level, rank, self.area_level)), float(placeable)]

    def carried(self, backpack: list[dict], equipped: list[dict]) -> list[float]:
        """[start, count] of the target's Bag rows: its backpack, its droppable equipment, the rest of its equipment
        (one piece may drop by chance) unless its base item never drops."""
        start = len(self.bag) // 3
        for e in backpack or []:
            i = self.item(str(e.get("TemplateResRef") or ""))
            if i >= 0:
                self.bag += [float(i), float(e.get("StackSize") or 1), float(BACKPACK)]
        for e in equipped or []:
            i = self.item(str(e.get("TemplateResRef") or ""))
            if i < 0:
                continue
            if e.get("Droppable"):
                self.bag += [float(i), 1.0, float(DROPPABLE)]
            elif not int((self.tables["bitm"].get(self.info[i]["Base"]) or {}).get("DoNotDrop") or 0):
                self.bag += [float(i), 1.0, float(EQUIPPED)]
        return [float(start), float(len(self.bag) // 3 - start)]

    def look(self, appearance: int) -> int:
        label = str(self.labels.get(appearance, "")).lower()
        return next((k for word, k in CONTAINER_LOOKS if word in label), 0)

    def keys(self) -> dict:
        reactive = [float(self.item(r)) for r in REACTIVE_HEALTH + REACTIVE_MANA]
        d = self.tables["difficulty"].get(NORMAL) or {}
        return {
            # per item: its template, name, description and KIND_*, ability, value (copper), stack, power, base item
            "ItemTags": list(self.tags),
            "ItemNames": [i["Name"] for i in self.info],
            "ItemDescs": [i["Description"] for i in self.info],
            "ItemStats": [float(x) for i in self.info for x in (i["Kind"], i["Ability"], i["Value"], i["Stack"],
                                                                 i["Power"], i["Base"])],
            # treasure tables: [first row, rows] each; rows [item, stack]
            "TreasureRanges": list(self.ranges),
            "TreasureRows": list(self.rows),
            # carried items: [item, count, how (BACKPACK, DROPPABLE, EQUIPPED)]
            "Bag": list(self.bag),
            # the reactive drops' potions (health tiers 1-4, then mana) and the rules: ReactiveLimit,
            # ReactiveChance (Normal), the global money chance, the money multiplier, the health base chance
            "ReactivePotions": reactive,
            "LootRules": [float(d.get("ReactiveLimit") or 0), float(d.get("ReactiveChance") or 0.0),
                          float(GLOBAL_MONEY_CHANCE), float(MONEY_MULTIPLIER), REACTIVE_HEALTH_BASE_CHANCE],
        }
