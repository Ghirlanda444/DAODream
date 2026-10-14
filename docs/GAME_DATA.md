# Game data layout (Steam "Dragon Age Ultimate Edition")

Recorded from `daotools scan` and `daotools find ... "bhn*"` on the real
install. File names and counts only; no game content.

## Whole install

- 10,488 ERF archives: 10,142 V2.0 (readable), 346 V2.2 (all encrypted, all
  DLC under `Addins/` and `Offers/`). The base game is fully readable.
- Talk tables load cleanly: `modules/single player/.../singleplayer_en-us.tlk`
  (146,065 strings) and `packages/core/data/talktables/core_en-us.tlk`
  (51,845 strings), plus one per DLC.
- Largest resource types: `fxe` 74,528 (facial animation), `dds` 48,361
  (textures), `mmh` 29,983 / `msh` 16,493 (models), `phy` 21,810, `mao` 16,272
  (materials), `ncs` 10,284 (compiled scripts), `utc` 7,810 (creatures),
  `gda` 4,502 (data tables), `dlg` 4,037 (conversations), `plo` 1,386 (plots).
- Loose files: voice and sound banks (`fsb` 2,449 / `fev` 2,417), talk tables,
  cinematics (`bik` 57), area layouts (`arl` 216).

## Formats in the Human Noble set

| Extension | Format | What it is |
|---|---|---|
| `dlg` | GFF4 `CONV V0.1` | conversation tree |
| `stg` | GFF4 `STG V1.0` | conversation stage (where actors and cameras stand) |
| `cut` | GFF4 `CUT V1.0` | cutscene |
| `dlb`, `cub` | GFF4 `ANBT V1.0` | animation banks for conversations / cutscenes |
| `utc`, `utp`, `utt`, `uti`, `are` | GFF3 V3.2 | creature, placeable, trigger, item, area templates |
| `ncs` | compiled script | not readable yet (source comes with the toolset) |
| `fsb` / `fev` | FMOD `FSB4` / `FEV1` | voice and sound banks |
| `lst` | unknown (`LST `) | |

## Conversations (`.dlg`), confirmed on `bhn100cr_father`

- Root: starting list (plain line indices; one per entry point), line list,
  end flag, VO bank.
- Lines are structs labelled `NTRY` (NPC line) or `RPLY` (player reply).
  Children are plain indices into the line list; a child that was already
  visited is a jump back, as the game uses for shared branches.
- Speaker is `OWNER` (the character the conversation belongs to), `PLAYER`,
  or another creature's tag (e.g. `bhn100cr_mother`).
- Player lines with empty text are silent "continue" clicks.
- Condition and action are `PLOT` structs: plot GUID, flag, test, script,
  script parameter. An empty GUID and empty script means the slot is unused.
- Each line also carries its stage name and a `CUT ` struct with the line's
  cinematic: duration, the `.dlb` animation bank, cameras and animation tracks.

## Human Noble origin (`bhn*`, 817 resources)

Where they live (all under `modules/single player/`):

| Archive | Resources |
|---|---|
| `data/al_bhn02al_castle_after_sie.rim` | 208 (castle after the siege) |
| `data/al_bhn01al_castle_cousland.rim` | 200 (castle, day) |
| loose files | 76 (voice banks and similar) |
| `data/designercreatures.erf` | 52 |
| `data/designerscripts.erf` | 51 |
| `data/designerdialogs.erf` | 47 |
| `data/designerplaceables.erf` | 45 |
| `data/designertriggers.erf` | 35 |
| `data/al_zz_hnoble_night_cutscene.rim` | 28 |
| `data/designercutscenes.erf` | 25 |
| `patch/patch002.erf`, `patch/patch003.erf` | 18 each (official patches) |

By type: `ncs` 195, `utp` 148, `utc` 148, `utt` 89, `dlg` 84, `stg` 39,
`fev`/`fsb` 38, `dlb` 15, `cut` 8, `are` 6, `cub` 6, `lst` 2, `uti` 1.
Many resources appear in two or three archives; the patch copies are
presumably the ones the game uses.

Naming: `bhn100*` is the castle by day, `bhn200*` the siege night. Suffixes:
`cr` creature conversation, `dg` dialogue scene, `cs` cutscene, `st` stage,
`ip` interactive placeable, `ar` area.

Conversations: `bhn100cr_arlhowe`, `cardguards`, `cook`, `dairren`, `duncan`,
`father`, `fergus`, `gilmore`, `guard`/`guard2`/`guard3`, `howe_guard`, `iona`,
`library_browser`, `mallol`, `mother`, `oren`, `oriana`, `scribe`,
`servant_f`/`servant_m`, `squire`, `bhn100dg_introduction`; and for the night:
`bhn200cr_fearful_f`/`_m`, `hall_guard`, `hrandom`, `hsoldier`, `panicked`,
`bhn200dg_bryce_cutscene`, `bhn200dg_farewell_cutscene`, `bhn200ip_hallway`.

Voice: one FMOD bank per conversation with the same name
(e.g. `bhn100cr_father.fsb`), plus cutscene banks and `bhn_day_extra`/
`bhn_night_extra` ambient banks.

Areas: `bhn100ar_castle_cousland.are`, `bhn200ar_castle_after_siege.are`.
Cutscenes: `bhn100cs_intro`, `bhn100cs_intropt01`, `bhn100cs_familyfarewel`,
`bhn100cs_finding_byron`, `bhn200cs_night_falls`.
