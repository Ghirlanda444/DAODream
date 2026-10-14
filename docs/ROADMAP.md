# Roadmap: the Human Noble origin

The first goal is one complete origin, playable start to finish in UE5: Castle
Cousland on the night of Howe's betrayal. It is small (one castle, roughly a
dozen named characters, one short combat quest, one scripted siege) but it
touches every system the rest of the game needs: dialogue, plot flags,
companions (the mabari), combat and cutscenes.

Each phase ends with something you can see running.

## Phase 0: Data pipeline (in progress)

- [x] Readers for ERF archives, GFF4, talk tables, data tables, conversations
- [x] Run `daotools scan` on the real install and record the archive layout (`docs/GAME_DATA.md`)
- [x] Confirm the Human Noble resource prefix (`bhn`, 817 resources)
- [x] `daotools pull` the origin; conversation layout confirmed on
      `bhn100cr_father` (see `docs/GAME_DATA.md`)
- [x] Creature, placeable and area templates (GFF3): all 394 Human Noble
      files parse on the real install
- [ ] Plot files (`.plo`): flag names, so conditions read as "QUEST_DONE"
      rather than numbers
- [ ] Voice-over: locate the Human Noble VO banks and map conversation lines
      to audio files

## Phase 1: Talking heads (first visible milestone)

- [ ] UE5 project, the main hall as a rough first build (greybox)
- [ ] Dialogue system in UE5 driven by the exported JSON: list-style replies,
      conditions and actions on plot flags, voice-over playback
- [ ] The opening scene: Bryce and Howe in the main hall, playable with the
      original dialogue tree and voice

## Phase 2: Castle Cousland

- [ ] Area layouts from the game's area/level data, used as the blueprint for
      rebuilt UE5 rooms (new art, original floor plan)
- [ ] Characters: rebuilt models (MetaHuman or custom), the original ones as
      proportion and costume reference
- [ ] Exploration: Fergus, Oriana and Oren, Nan in the kitchen, Ser Gilmore,
      the guests

## Phase 3: First fight

- [ ] The larder quest with the mabari: first combat prototype
- [ ] Real-time with pause, tactics slots, DAO's stats and abilities from the
      data tables

## Phase 4: The siege

- [ ] Night attack, fighting through the castle, the escape, Duncan
- [ ] Origin complete: start to finish without debug tools

## Later

The other five origins, then Ostagar. Every origin reuses the Phase 0–3 systems,
so later origins should mostly be content work.

## What is not reused

Original models and animations are reference only: the point of the remake is
a new look. Dialogue text, voice and plot logic are reused as-is from your
install, at runtime.
