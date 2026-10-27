# Loot and the inventory

The original's treasure system (`sys_treasure_h`) ported: what creatures and
containers drop, the party's inventory and money, the poultices and lyrium
potions, by hand and by tactics. daotools `tools/daotools/treasure.py` (and its
tests) holds the rules; `tools/unreal/loot.py` builds them into the Blueprints
(graphs from `loot_dsl.py`).

## What drops

`TreasureGenerate` runs when a container spawns (`Placeable_HandleSpawned`: chests,
sacks, crates, rubble: `placeable_types` BaseType 2) and when a creature dies
(`sys_treasure`, EVENT_TYPE_DYING):

- **Its tables**: the target's treasure category (TreasureCategory: Ferelden for
  Howe's men and the castle's guards, Circle for the mage, Generic for the
  castle's containers) and rank (a creature's Rank, a container's Rank field)
  name a table, `ts_<category><Cre|Plc><table>`. The rank's autoscale row gives
  the low and high tables (TS_LowTable, TS_HighTable: a soldier of rank 1
  Critter, the knight of rank 3 Lieutenant and Boss), how many draws (TS_ItemNum:
  0.25 for a soldier, 1.5 for the knight; the fraction is a chance of one more)
  and the chance of the high table (TS_HighChance).
- **Each draw** is a random row: an item and a stack (80-100% of the row's), or
  copper: 6 x level² x the row's size, 80-120%. A container holds one thing at
  least.
- **Money or things**: a creature first has a 30% chance of its low table's
  first row when that is copper; after that, a creature with money gets no other
  treasure and one with things gets no money.
- **Reactive potions**: a hostile carrying no potion may drop one when the party
  holds fewer than 12 health or mana potions (Normal's ReactiveLimit): a chance of
  (1 - the fewer / 12) / 4 x 0.75 x max(1, TS_ItemNum), a poultice of the rank's
  tier (lyrium the more likely the more poultices the party has).
- **Equipment**: with the rank's TS_EquipmentChance (none for a soldier, 20% for
  the knight) one equipped piece drops, unless its base item never does
  (`bitm_base` DoNotDrop); pieces marked droppable always do (the mace of the
  soldier in the Teyrna's room, the bowman's shortbow in the hero's).
- **What it carries**: its backpack (the knight's injury kit and belt, the mage's
  amulet and belt).

Not ported: item materials scaled to the level (TS_ScaleItem: only weapons and
armour from the tables, none here) and stealing.

## Containers

The area export lists them (`ContainerTags`, `ContainerPose`, `ContainerInfo`:
look, locked, lock level, key required, usable, active; their loot fields and
fixed items). At night most of the castle's chests are the original's "looted"
ones (empty), with the treasury's racks, the family chest and two piles of
rubble with healing things in them.

- **Looks**: Megascans props (git-ignored, `docs/ART.md`): a chest, a sack, a
  barrel for a crate, a cabinet for a weapon or armour stand, rubble, and a sack
  for a fallen creature's bag.
- **Locks** (`Placeable_HandleUsed`): a locked chest opens with its key, or to a
  rogue whose disable device level (cunning above 10, + 10 a rank of
  Lockpicking) reaches its lock (PickLock). A warrior hero cannot pick one, as in
  the original.
- **A right click** walks the hero to it and opens it (the loot window).

Human bodies leave the scene when they fall, so a creature's loot lies in a bag
where it fell (the original's body bags, `statecnt_bodybag`); a bag goes once
emptied.

## The inventory

The party's, as in the original: the hero's starting backpack (three Lesser
Health Poultices), what is looted, and money (100 bits a silver, 100 silver a
gold).

- **I** opens it (IA_Inventory). A click on a poultice or a lyrium potion uses
  it on the one in control; on anything else, shows its description.
- **Poultices** (`item_singletarget`): (50 + spellpower) x 1, 2, 3 or 4 health
  (lesser to potent). **Lyrium potions**: 50-200 + spellpower x 0.5 mana, to a
  magic user only. Each has a 5 s cooldown (`abi_base`).

## Tactics

The tactics screen now offers Use item (each kind of potion the party carries)
and the four potion commands: Use health poultice: most / least powerful, Use
lyrium potion: most / least powerful. They work as `_AI_GetPotionByFilter`: in
combat only, from the party's stock (the leader's inventory), the dearest or the
cheapest potion of the kind; a health poultice only when not at full health.

## Checked in Play

Silent, `py playtest.py lootcheck night`, 2026-10-27:
- the hero started with three Lesser Health Poultices; the loader spawned the
  night's 19 containers;
- the trunk opened in the loot window (its four weapons) and Take all moved them
  into the inventory; a locked chest refused the warrior;
- the bowman killed in the opening fight left "Howe Archer (remains)": his
  shortbow and 5 bits; the knight felled left 1 silver 13 bits, his two injury
  kits, his belt and a Greater Lyrium Potion (a reactive drop), all taken;
- the inventory window (I) listed them with the money; a Lesser Health Poultice
  drunk from it healed the hero 60.5 to 111.5 (50 + spellpower 1);
- the Teyrna, with the row "Self: Health < 50%: Use health poultice: least
  powerful", drank one from the party's stock in a fight;
- the tactics screen offered Use item for each potion carried and the four potion
  commands;
- the treasure rolled in the Blueprints against daotools: the knight drops money
  30% of the time (daotools 29.9%: only his low table's first row, his backpack
  stopping the rest) and 4.1 things on average (4.1); a soldier money 32-44% in
  three runs, 35.4% over the 1,600 rolls (daotools 35.6%);
- no script errors.

The first comparison found daotools leaving out what a creature carries: the
original counts its backpack, so the knight's draws never give money.

