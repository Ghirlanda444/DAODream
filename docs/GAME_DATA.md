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
| `utc`, `utp`, `utt`, `uti`, `are`, `lst` | GFF3 V3.2 | creature, placeable, trigger, item, area templates; `lst` is a per-area list |
| `ncs` | compiled script | not readable yet (source comes with the toolset) |
| `fsb` / `fev` | FMOD `FSB4` / `FEV1` | voice and sound banks |

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

## Conversations in Unreal

`daotools unreal conv` turns a `.dlg.conv.json` from `pull` into the flat
format the Unreal project reads at runtime (`daotools/unreal.py` documents the
keys and rules). The output goes under `extracted/ue/`, so it stays out of git
like all game data; Unreal reads it from there when you press Play.

A whole origin in one command (16 s for Human Noble):

```powershell
py -m daotools unreal origin extracted/human_noble --plots extracted/plots/raw `
  --true-flag GEN_GENDER_MALE --true-flag GEN_CLASS_WARRIOR --out extracted/ue
```

It writes `extracted/ue/conversations/<name>.json` for every conversation,
the voice to `extracted/ue/vo/<VoBank>/<Vo>.wav`, and
`extracted/ue/conversations/index.json` (owner, the creatures that use the
conversation, line and voice counts, warnings). Rules:

- A conversation found in several archives is taken from the newest
  `patch*` folder, otherwise the first copy; copies that differ are reported.
  In Human Noble every copy is identical.
- The owner (who "OWNER" lines are spoken by) is the creature whose
  `DialogResRef` is the conversation, preferring the one whose tag matches
  its name. Guards share conversations (`bhn100cr_guard` is used by the
  praying guards, for instance).
- Result for Human Noble: 32 conversations, 941 of 951 spoken lines voiced.
  `bhn200ip_hallway` (one line, an interactive placeable) has no bank.

One conversation at a time, the same thing by hand:

```powershell
py -m daotools unreal conv extracted/human_noble/json/al_bhn01al_castle_cousland/bhn100cr_father.dlg.conv.json `
  --names extracted/human_noble/json --plots extracted/plots/raw `
  --vo extracted/human_noble/raw/loose/bhn100cr_father.fsb `
  --true-flag GEN_GENDER_MALE --true-flag GEN_CLASS_WARRIOR `
  --out extracted/ue/conversations/bhn100cr_father.json
py -m daotools fsb extract extracted/human_noble/raw/loose/bhn100cr_father.fsb `
  --out extracted/ue/vo/bhn100cr_father
```

With `--plots`, `--true-flag` takes flag names, and the output gains
`FlagNames`: every "GUID:FLAG" key the conversation uses, with its name.
With `--vo`, each line's `Vo` names its voice-over file; Unreal plays
`extracted/ue/vo/<VoBank>/<Vo>.wav` when the line is shown. An action with
plot test 0 clears its flag (`ActionNot`); 9 lines in Human Noble do this.

What the opening scene needs, from `bhn100cr_father`:

- Starting entries are tried in order. Four are gated on plot flags; the last
  has no condition, so with no flags set the conversation opens on Bryce and
  Howe in the hall. Bryce's first line sets `BHN_TALKED_TO_FATHER`, which gates
  start 38 ("Shouldn't you be off to your brother?"), so talking to him again
  never replays the opening.
- Plot flags 256 and up are computed by the plot's script rather than stored.
  The player-character plot `gen00pt_class_race_gend` gates the gendered lines:
  `GEN_GENDER_MALE` (260) picks "my son" over "my daughter", and
  `GEN_CLASS_WARRIOR` (258) picks the "prowess as a warrior" lines. These are
  passed in with `--true-flag`.
- A plot test of 0 means "flag is not set"; no other test value occurs here.

## Voice-over (`.fsb`)

Loose FMOD banks in `modules/single player/audio/vo/en-us/vo/`, one per
conversation with the same name (the conversation's VO bank), plus a `.fev`
event file each. `daotools fsb list` shows a bank's samples.

- FSB4: a 48-byte header, one 80-byte header per sample (name, length,
  mode, rate, channels), then the sample data back to back. FMOD pads each
  sample with zero bytes after its last frame.
- A line's sample is `<strref>_m.wav`, after the talk table string of its
  text. The `_m` is on every conversation sample, not the player's gender:
  gendered lines are separate lines with their own strings.
- Conversation VO is MPEG-2 layer III, 24 kHz mono. Player lines are not
  voiced. In `bhn100cr_father`, all 100 spoken lines have a sample and every
  sample belongs to a line; across the 32 Human Noble conversations, 941 of
  951 spoken lines are voiced.
- How Unreal plays it: a Media Player (WmfMedia) opens the file and, with
  `NativeAudioOut=True` under `[/Script/WmfMediaFactory.WmfMediaSettings]` in
  `Config/DefaultEngine.ini`, sends it straight to the Windows mixer. Without
  that setting the audio goes through a Media Sound component, which stayed
  silent here (no samples reached it, even for a PCM test tone).
- In native mode WmfMedia refuses `.mp3` and plays an MP3 wrapped in a
  `.wav` as silence, so it needs PCM. `fsb extract` therefore decodes each
  sample to a 16-bit PCM `.wav` with Windows' own MP3 decoder (Media
  Foundation, called through ctypes; Windows only). `--mp3` writes plain
  `.mp3` instead. The father's 100 lines come to 24 MB.
- Checked by metering the default playback device during Play: silence
  before, speech-level peaks while a line plays, silence after Esc.

## Plots (`.plo`)

GFF4 `PLTS V1.0`, one plot per file, in `designerplots.erf`: 597 in
`modules/single player/data/`, 301 in `packages/core/data/` (898 plots,
8,708 flags). Extract them with:

```powershell
py -m daotools erf extract "<game>/modules/single player/data/designerplots.erf" --out extracted/plots/raw/singleplayer --pattern "*.plo"
py -m daotools erf extract "<game>/packages/core/data/designerplots.erf" --out extracted/plots/raw/core --pattern "*.plo"
py -m daotools plo list extracted/plots/raw --out extracted/plots/plots.json
```

- The root holds a list (field 13016) with one `PLOT` struct: name (field 3,
  always the file name without `plt_`), GUID (13007), script (13009) and the
  flag list (13000) of `FLAG` structs with ID and name.
- Defined flags (256 and up) are listed like stored ones; the script computes
  them.
- Every plot GUID in `bhn100cr_father` resolves. The Human Noble plots are
  `plt_bhn*` in the single player archive; the player-character and codex
  plots it also uses are in core.

## Areas and layouts (`.are`, `.arl`)

An area (`.are`, GFF3, in the area archive) places things; its `Layout`
field names the level it is built on, whose files are in
`packages/core/env/<Layout>/` (one `.rim` per room chunk, plus loose
`<Layout>.arl` and `.opf` next to that folder). Castle Cousland by day is
`bhn100ar_castle_cousland` on layout `hrt201d` ("Castle Cousland Main Floor").

- `.are` lists: `CreatureList` (57 here: tag, template, position, orientation
  quaternion, `Active`; the rats start inactive), `PlaceableList` (56),
  `TriggerList` (46, with geometry), `WaypointList` (33; those with a map note
  name the rooms: Main Hall, Kitchen, Chapel, Your Room...), `StageList`
  (18), `SoundList` (74).
- Positions are metres, right-handed, Z up, yaw 0 facing +Y (Bryce at
  (-39.4, -4.6) faces Howe with yaw -80). The game's start waypoint is
  `bhn100wp_start`, next to Bryce.
- `.arl` (GFF4 `ARL V4.0`): 59 `ROOM` structs with bounding boxes (render
  chunks; they overlap and some cover the whole castle, so they are no use as
  a floor plan) and a navigation grid (`NAVI`): 299 x 276 cells of 0.5 m from
  (-131.1, -74.7). Per cell, field 3093 is the floor height in 1/16 m and field
  3114 is -1 for blocked cells and >= 0 for walkable ones. Checked against all
  35 placed characters: each stands on a walkable cell at exactly that height
  (from -6 m in the cellars to 12 m in the family quarters).
- A creature's template (`.utc`) gives its conversation (`DialogResRef`),
  name and gender (`Appearance Data/Gender`: 1 male, 2 female).

`daotools unreal area` turns this into what Unreal spawns at runtime: floor
and wall boxes (walkable cells merged into rectangles per height; walls on
blocked cells next to walkable ones, 3 m tall), the creatures that have a
conversation (inactive ones too, spawned hidden until a plot shows them) and
every waypoint (where plot scripts move people), in Unreal coordinates
(x' = 100x, y' = -100y, z' = 100z,
yaw' = -(yaw + 90)):

```powershell
py -m daotools unreal area extracted/human_noble/json/al_bhn01al_castle_cousland/bhn100ar_castle_cousland.are.json `
  --layout "<game>/packages/core/env/hrt201d.arl" --pull extracted/human_noble/json `
  --start bhn100wp_start --out extracted/ue/areas/bhn100ar_castle_cousland.json
```

Castle Cousland: 1,003 floor boxes, 606 wall boxes, 35 talking characters,
18 giant rats in two teams (hidden at first)
(the dog and cat use templates outside the Human Noble pull), 33 waypoints, 27 doors.
Plot scripts act on these through `BP_PlotManager` (`docs/SCRIPTS.md`). In Unreal,
`/Game/Cousland/Maps/L_CastleCousland` holds one `BP_AreaLoader` that builds
it on Play; the level itself holds no game data.
