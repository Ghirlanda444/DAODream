# Scaling to the whole game

The Human Noble origin plays start to finish after ten days (2026-10-14 to 10-23), but much of that
time went into things done once per character or per room. The whole game is six origins, Ostagar,
and then the main campaign with its many areas, so the rule from here on is: **build the system once,
then feed it the game's data.** This page says what is already like that, what is not, and the order
to fix it. The roadmap (`ROADMAP.md`) stays the list of what plays; this is how we get there faster.

## Already reusable for any module

| System | How it scales | Where |
| --- | --- | --- |
| Areas | any `.are` + layout exports to one JSON; `BP_AreaLoader` spawns floors, walls (from the level kit's collision), doors, triggers, lights, fires, everyone in it | `daotools unreal area`, `GAME_DATA.md` |
| Conversations | every `.dlg` converts with voice, conditions and actions | `daotools unreal conv` |
| Plot logic | script patterns are translated to 16 action kinds that `BP_PlotManager` runs; a new module only needs the patterns it uses for the first time | `daotools unreal plots`, `SCRIPTS.md` |
| Stats | health, attack, defense, damage, armour from the game's own tables and scripts, for any creature | `stats.py`, `COMBAT.md` |
| Recurring characters | a look is keyed by the head morph (`hm_gen_duncan` is Duncan in every area), so a character made once appears wherever the game puts them | `CHARACTERS.md` |
| Crowds | per race and sex (humans, elves), varied in skin, hair and clothes per NPC | `area.look_keys`, `area.variety` |
| Outfits | made from what each creature wears (its chest item), with family fallbacks for items not seen before | `outfit_make.py` |
| Checking | `playtest.py` pictures of the running game; `commit_guard.py` on every commit | `.claude/skills/playtest` |

## Where the time goes, and the fix

1. **Rooms are boxes.** Every area is built from the game's level kits, and the export already knows
   every kit piece and where it stands. Fix: a *kit mapping*, one table from each kit piece (wall,
   floor, arch, stair, pillar, door frame) to a modular Unreal mesh, so every area that uses that kit
   gets real walls in one go, Castle Cousland, Ostagar, Redcliffe alike. Pieces without a match keep
   their box. This is the single largest gain: hundreds of areas, a few dozen kits.
2. **Outfits multiply.** Today an outfit is fitted per face *and* item (the elves alone needed 11).
   Fix: a handful of shared body types (man, woman, elf man, elf woman, dwarf, child) that every crowd
   face and most named characters use, so an item is fitted once per body type. Named characters with
   unusual builds keep their own.
3. **Combat is placeholder.** Hits, to-hit rolls and stats are the game's, but there are no talents,
   spells, sustained modes, status effects or tactics. Fix: Unreal's Gameplay Ability System (GAS),
   which is built for exactly this (abilities as data, effects with durations and stacking, tags for
   states such as stunned or knocked down), fed from the game's ability tables (`ABI_base` and its
   2DAs) the way stats are fed today. One system for every class, creature and module. Before that,
   the cheap fixes: armour in hits, a game over, one-hit kills off. The plan, with Dragon Age Reborn as the
   balance base and Awakening's specializations in the main campaign: `docs/COMBAT_DESIGN.md`.
4. **Cutscenes are captions.** Most are a few shots of characters talking or walking. Fix: play the
   cutscene's own tracks (who moves where, who speaks, camera cuts) with the dialogue camera and the
   walk system we already have, rather than a hand-made sequence each. Started 2026-10-24: characters
   now stand and move where the cutscene puts them (`docs/SCRIPTS.md`, Staging); the cutscene's own
   camera paths and body animations are next.
5. **Levels load as one world each.** Fine for a castle; the campaign needs many areas and day/night
   or before/after states of the same place. Fix: World Partition with Data Layers for area states
   (Cousland by day and by night is the same castle), loaded by the area loader.
6. **The player character** is a mannequin by design for now: DAO's character creator (race, sex,
   class, face) is a system of its own, built later on MetaHuman's scriptable API; until then a
   filler.

## How I (Claude) get faster

- Fixed rules live in the repo, not in chat: `CLAUDE.md`, the project skills (`unreal-editor`,
  `playtest`), and these docs. New lessons go into the skills.
- The editor starts its MCP server by itself (`bAutoStartServer`), and batch jobs launch it without
  taking focus, so long builds run unattended.
- Work in batches by system, never one character or room at a time: all elves, all kit pieces of a
  kit, all abilities of a class.
- Parallel sessions for independent work (code that doesn't touch the editor runs beside editor work).
- Every change a player sees gets a `playtest.py` check before it is called done.

What we learned from others (2026, write-ups and tests of Claude on Unreal 5.8; X threads need a login
and could not be read): Claude in Unreal works well for greyboxing, Blueprint logic and batch editor
work, and badly when asked to invent things it cannot see (input setups, PCG graphs from nothing,
widget bindings). Hand-made templates that Claude then fills with data beat asking it to author
complex assets from scratch, which is the approach above. Epic's MetaHuman 5.7/5.8 Python API and the
experimental MetaHuman crowd plugin are the route to many faces; Clair Obscur: Expedition 33 (a small
team, mostly Blueprints, Fab assets, Nanite) is the closest precedent for a small-team UE5 RPG.

## Art style: would cel shading be faster?

Short answer: it would not remove the slow parts. What costs time is geometry (rooms, props),
outfits, animation, combat and porting scripts, and a toon shader changes none of those: a cel-shaded
castle still needs its walls, a cel-shaded fight still needs its abilities. Full toon rendering also
fights MetaHumans (realistic skin and strands under hard banded light read uncanny unless the faces
are restyled too), and Hi-Fi Rush, the reference for toon in Unreal, needed a custom renderer.

Where a style *does* help is consistency: MetaHumans, Megascans, Fab packs and greybox pieces come
from different sources, and a single post-process look (a painterly or "stylized realism" grade:
palette, soft outlines, film grain, a little edge darkening, as in DAO's own concept paintings) hides
the seams for the price of one material, without touching any asset. That can be tried on a copy of a
level in an hour and judged from pictures, and removed as easily. Recommendation: keep realistic
assets, add a unified post-process look later as an experiment, and spend the effort on the kit
mapping and the shared body types, which are what make the game buildable.
