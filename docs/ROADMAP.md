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
- [x] Plot files (`.plo`): flag names, so conditions read as "QUEST_DONE"
      rather than numbers (`daotools plo list`, `unreal conv --plots`)
- [x] Voice-over: locate the Human Noble VO banks and map conversation lines
      to audio files (`daotools fsb`, `unreal conv --vo`)

## Phase 1: Talking heads (first visible milestone)

- [x] UE5 project, the main hall as a rough first build (greybox):
      `/Game/Cousland/Maps/L_GreatHall`, walked end to end in Play
- [x] Dialogue system in UE5 driven by the exported JSON: list-style replies,
      conditions and actions on plot flags, voice-over playback
      (`/Game/Cousland/Dialogue`, Bryce on the dais in L_GreatHall)
- [x] The opening scene: Bryce and Howe in the main hall, playable with the
      original dialogue tree and voice (played through and heard in Play)

## Phase 2: Castle Cousland

- [ ] Area layouts from the game's area/level data, used as the blueprint for
      rebuilt UE5 rooms (new art, original floor plan). Started: the castle's
      walkable floor plan and everyone who talks are spawned at runtime in
      `/Game/Cousland/Maps/L_CastleCousland` (`daotools unreal area`). Walls,
      pillars, furniture and blockers now come from the level kit's collision
      boxes, so the castle has its real rooms and corridors; all still greybox
      boxes
- [ ] Characters: rebuilt models (MetaHuman or custom), the original ones as
      proportion and costume reference. Started: the plan is MetaHumans for
      the named cast and Fab packs for soldiers, guards, servants and animals,
      kept out of the public repo. First slice done: Bryce and Howe's soldiers
      are MetaHumans in Play, 40 on screen at about 60 fps
      (`docs/CHARACTERS.md`); next medieval outfits and the named cast
- [ ] Exploration: Fergus, Oriana and Oren, Nan in the kitchen, Ser Gilmore,
      the guests. All 35 talking characters already stand in place and talk
      (with voice) in L_CastleCousland
- [ ] Plot logic: what the 16 plot scripts do when a flag is set (parents
      moving upstairs, doors, the night). The source of all 2,079 scripts comes
      out of the official toolset (`daotools toolset scripts`, `docs/SCRIPTS.md`).
      Started: the scripts are translated into actions (`daotools unreal plots`)
      that `BP_PlotManager` runs on one shared set of flags. Bryce's plot
      (`bhn100pt_father`) is fully ported and played through (parents move
      upstairs after Fergus' farewell, Bryce talks; Duncan joins after the
      opening). Characters walk to waypoints (Aldous after his talk), and the
      castle's 27 doors open, close and lock, by hand or from a plot (the
      pantry door when Gilmore leaves the party). Teams appear and move
      together (the larder rats appear when the rat fight begins). Castle
      folk live their ambient routines from the scripts' settings: guards look
      about, Mother Mallol and two guards pray in the chapel, a browser walks
      the library (`docs/AMBIENT.md`)

## Phase 3: First fight

- [ ] The larder quest with the mabari: first combat prototype. Started: the
      larder fight plays start to finish with the game's own logic (the
      mabari's conversation starts it, three waves of rats, the castle reacts
      when they are dead), with placeholder numbers (`docs/COMBAT.md`).
      Gilmore and the mabari join the party when the scripts say so, follow
      you and fight beside you, but only against hostiles near you; the
      castle's armed guards fight Howe's men too, without joining the party.
      A test switch (`bOneShot`, on for now) makes the player kill in one hit
- [ ] Real-time with pause, tactics slots, DAO's stats and abilities from the
      data tables. Started: health, attack, defense and damage come from the
      tables, as the scripts compute them, and every attack rolls to hit

## Phase 4: The siege

- [ ] Night attack, fighting through the castle, the escape, Duncan. Started:
      the night castle (`bhn200ar_castle_after_siege`) is
      `/Game/Cousland/Maps/L_CastleNight`, reached from the day castle by the
      scripts' area transition with all flags carried over. The night opens
      as in the game: a caption for its cutscene (cutscenes play as captions
      or voiced conversations), then the mabari growls, a servant runs in and
      is cut down, Howe's men attack, the dog joins you, Mother comes out; and
      the castle's triggers bring out Howe's soldiers as you go
      (`docs/NIGHT.md`). Played through by hand to Duncan in the larder: Eleanor
      fights beside you and remarks once on each room (the conversations'
      "show once" setting), the servants' scenes play, fill lights stand in
      for the game's baked ambient light so no corridor is black
- [x] Origin complete: start to finish without debug tools. Played from the
      day castle's opening to Duncan's farewell with no flag set by hand; it
      ends on an "End of the Human Noble origin" message (`docs/NIGHT.md`).
      Still placeholder: greybox rooms and mannequins, cutscenes as captions,
      no game over, Howe's men only attack you and your party

## Later

The other five origins, then Ostagar. Every origin reuses the Phase 0–3 systems,
so later origins should mostly be content work.

## What is not reused

Original models and animations are reference only: the point of the remake is
a new look. Dialogue text, voice and plot logic are reused as-is from your
install, at runtime.
