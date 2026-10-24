# Combat balance: Dragon Age Reborn's numbers against the game's

The combat plan (`docs/COMBAT_DESIGN.md`) takes its balance from **Dragon Age Reborn** (v1.1.2, Tyragon,
https://www.nexusmods.com/dragonage/mods/5173). This page says how its numbers are read and where they
stay. Credit: Tyragon, with fixes from dainbramage's Dain's Fixes that the mod includes.

## Permission

The mod's Nexus permissions allow using its assets with credit, never in anything sold, forbid
uploading its files elsewhere, and say it may not be converted to other games. The owner decided
(2026-10-24) to import its rule system into this non-commercial fan remake as the starting point, then
tune it to our own balance. Its files, the tables read from them and its texts stay out of this public
repository (git-ignored `extracted/`, read from the owner's install like the game's own data); what is
committed is our code that reads them and our own implementation of the rules, with credit here.

## Where the files are

The owner had the mod installed through Vortex; its downloads were in
`%APPDATA%\Vortex\downloads\dragonage` (main file 1.1.2, Documentation, Source Files). They were copied to
`extracted/mods/da_reborn/zips/` and unpacked there: `main/DA_Reborn.dazip`, `docs/` (its PDF listing
every change), `source/` (the 38 game scripts it changes), `erf/` (its two archives' contents: override
tables, compiled scripts, talk tables).

## Reading its numbers

The mod changes data by override tables (`abi_base_ao.gda` overrides rows of the game's
`abi_base.gda` by ID) and rules by replacing scripts. `daotools unreal balance` (`daotools/balance.py`)
diffs the overrides against the game's tables (extracted from `packages/core/data/2da.erf`, its
`patch002.erf` and `packages/core_ep1/data/2da.erf` into `extracted/gda_vanilla`) and writes every
changed column as [game, mod], every new row, and the mod's names and descriptions for them:

```powershell
py -m daotools unreal balance --game-tables extracted/gda_vanilla --mod-tables extracted/mods/da_reborn/erf `
  --scripts extracted/scripts/src --scripts extracted/mods/da_reborn/source `
  --tlk extracted/mods/da_reborn/erf/da_reborn_en-us.tlk --source "Dragon Age Reborn 1.1.2 (Tyragon)" `
  --out extracted/ue/combat/balance_reborn.json
```

Column names are not stored in the tables (only hashes); the scripts read columns by name, so they are
collected from the game's and the mod's sources. What it found:

| Table | Rows changed | New |
| --- | --- | --- |
| `abi_base` (abilities) | 101 | 6 |
| `abi_gxa` (Awakening abilities) | 4 | 1 |
| `passive_abilities` (+ Awakening's) | 7 | 2 |
| `autoscale` (creature rank scaling) | 5 | 0 |
| `shapechange` (shapeshift forms) | 2 | 0 |
| `difficulty`, `itemprps`, `itemstats`, `properties`, `anim_combat`, `persistent` | 1-2 each | 1 |

In outline: enemies have 30% more health at every rank; on Nightmare healing is weaker and enemies use
abilities at the normal rate; the bear form trades damage for armour and the spider the reverse (the
bear the tank, the spider the damage dealer); many talents get new costs, cooldowns and effects (some
renamed and remade). Its rule changes are in the scripts it replaces: `combat_damage_h` (186 lines
differ: Shattering Blows fixed, two-handed hits on stunned targets adding the weapon's armour
penetration, Blood Frenzy's cap growing with strength, new bonuses such as the spider form's poison),
`combat_h` (151), `effect_damage_h` (53), and small changes to threat, player rules and shapeshifting.
