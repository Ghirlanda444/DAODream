# Game logic in compiled scripts (Human Noble survey)

What the conversations cannot do on their own lives in compiled scripts
(`.ncs`). This records how much there is and how it could be read. File names,
sizes and counts only; no script content.

## What is there

- 195 `.ncs` resources in the `bhn*` pull, 51 distinct scripts (the same
  script sits in several archives). About 620 KB of bytecode in total.
- By kind (from the name): 16 plot scripts (`*pt_*`, 401 KB), 19 trigger
  scripts (`*tr_*`, 53 KB), 9 placeable scripts (`*ip_*`, 78 KB), 5 creature
  scripts (`*cr_*`, 33 KB) and 2 area scripts (`bhn100ar_castle_cousland`,
  `bhn200ar_castle_after_siege`, 58 KB).
- The smallest plot scripts are 17-19 KB, which is mostly shared code compiled
  into each one (plot flag get/set, reward and XP handling). The story logic is
  what comes on top: e.g. about 9 KB for `bhn100pt_father`, 34 KB for
  `bhn100pt_gilmore`.
- The names the scripts reference show what kind of logic it is:
  - moving characters to waypoints when a flag is set (`bhn100pt_father`
    references `bhn100wp_father_upstairs` and `bhn100wp_mother_upstairs`:
    after the opening, Bryce and Eleanor go up to Fergus' room),
  - doors and placeables (`bhn000ip_door_pantry`, `bhn100ip_door_upstairs`),
  - switching to the night castle (`bhn000pt_main` references
    `bhn200ar_castle_after_siege`),
  - setting flags in other plots (codex entries, achievements, the party),
  - rewards and XP.
- Defined plot flags (256 and up, e.g. `GEN_GENDER_MALE`) are computed by these
  scripts too; for now they are passed in as true flags.

So Phase 1 needed none of it, but the castle only "plays" once the plot
scripts' effects exist: parents moving upstairs, the dog quest, the night.

## How to read it

The header is `NCS V1.0B`, the same bytecode family as Neverwinter Nights
scripts (NWScript), which is documented by the community (xoreos). Two ways:

1. **The official Dragon Age: Origins toolset** (`DragonAgeToolset1.01Setup.exe`).
   This is what we use: its database holds the source (`.nss`) of 2,079
   scripts, the whole game, 11.6 MB.
2. **A disassembler in daotools**: no longer needed. NWScript bytecode is
   simple, but Dragon Age adds several hundred engine functions that would have
   to come from community documentation.

The logic gets rewritten in Unreal (Blueprints), plot by plot, driven by the
same "GUID:FLAG" keys the dialogue runner already uses.

### Getting the source

Installing the toolset on Windows 11 with the Steam game took four fixes:

1. **"Dragon Age: Origins game install not found."** Steam does not write the
   registry key the installer reads. Add
   `HKLM\SOFTWARE\WOW6432Node\BioWare\Dragon Age` with `Path` (string, the game
   folder with a trailing backslash), `Installed` (DWORD 1) and `Version`
   ("1.05").
2. **"Error opening file for writing ... Common Files\BioWare\Uninstall Dragon
   Age Toolset.exe"**: run the installer as administrator, and create
   `C:\Program Files (x86)\Common Files\BioWare` by hand first (the installer
   does not create it).
3. **SQL Server**: the installer sets up SQL Server 2005 Express, instance
   `BWDATOOLSET`, under `C:\Program Files (x86)\DAODB`. On a second run, untick
   "Install MS SQL Express".
4. **The content database is not restored** even with "Restore the default
   database" ticked. Restore the shipped backup by hand, as administrator,
   moving the files into the instance's own data folder, then give your Windows
   account access:

   ```bat
   sqlcmd -S .\BWDATOOLSET -E -Q "RESTORE DATABASE bw_dragonage_content FROM DISK = N'<game>\tools\dbbak\bw_dragonage_content.bak' WITH MOVE N'bw_dragonage_content' TO N'C:\Program Files (x86)\DAODB\MSSQL.1\MSSQL\Data\bw_dragonage_content.mdf', MOVE N'bw_dragonage_content_log' TO N'C:\Program Files (x86)\DAODB\MSSQL.1\MSSQL\Data\bw_dragonage_content.ldf'"
   sqlcmd -S .\BWDATOOLSET -E -d bw_dragonage_content -Q "CREATE USER [<PC>\<user>] FOR LOGIN [<PC>\<user>]; EXEC sp_addrolemember N'db_owner', N'<PC>\<user>';"
   ```

   Other folders (e.g. `DAODB\Data`) fail with "Accesso negato": the server
   runs as Network Service.

Then copy the source out (2 s, into git-ignored `extracted/`):

```powershell
py -m daotools toolset scripts --out extracted/scripts/src
py -m daotools toolset scripts --pattern "bhn*" --out extracted/scripts/bhn
```

Source is in `t_Script.Text`, named through `t_ModuleResRefVersion`
(`Name`, `Folder`); each script also has an empty placeholder version.

### What a plot script looks like

`bhn100pt_father` is a switch over its flags, run when a flag is set
(`EVENT_TYPE_SET_PLOT`) or read (`EVENT_TYPE_GET_PLOT`, for defined flags).
Each case uses a small set of helpers: `UT_LocalJump` (move a creature to a
waypoint), `UT_Talk` (start a conversation), `WR_SetObjectActive` (show or
hide a creature), `WR_SetPlotFlag` (set another flag) and `DoAutoSave`.
Waypoint and object names come from `bhn_constants_h`. Porting a plot means
implementing those helpers once in Unreal and the cases per plot.

## Plot logic in Unreal

The cases are not rewritten by hand: `daotools unreal plots` reads each plot's
script and turns every `case` of its SET handler into actions, following
fall-through the way the game does. It writes them to git-ignored `extracted/`,
since they come from the scripts:

```powershell
py -m daotools unreal plots --src extracted/scripts/src --plots extracted/plots/raw `
  --only "bhn*" --out extracted/ue/plots.json
```

| Kind | Script call | Unreal |
| --- | --- | --- |
| 1 jump | `UT_LocalJump(creature, waypoint)` | teleport the creature to the waypoint's pose |
| 2 talk | `UT_Talk(creature, ...)` | start its conversation, after the current one ends |
| 3 active | `WR_SetObjectActive(object, bool)` | show or hide it (hidden: no collision, cannot talk) |
| 4 setflag | `WR_SetPlotFlag(PLT_X, FLAG, bool)` | set another flag, running that flag's actions too |
| 5 autosave | `DoAutoSave()` | logged only; there are no saves yet |
| 6 walk | `AddCommand`/`WR_AddCommand(creature, CommandMoveToObject/Location(...))`, `UT_QuickMoveObject` | walk (or jog, when the script runs) to the waypoint, then face its direction |

Creatures are found by tag (`object oX = UT_GetNearestCreatureByTag(...)` plus
the string constants of every script); `PLT_<NAME>` is the plot named `<name>`
and its flag constants are that plot's flag names. Anything else is listed as
skipped, so coverage is visible in the command's output.

Coverage on the Human Noble plots (16 scripts): `bhn100pt_father` is complete
apart from gore level and achievement tracking. All 14 single-character moves
translate (the cook, the kitchen servants, the gambling guards, the scribe,
the panicked soldiers). The rest is still skipped: moves of whole teams
(`UT_TeamMove`, `UT_TeamAppears`, which need team membership from the area),
ambient animations, party hire/fire, doors (`SetPlaceableActionResult`),
items, combat and area transitions.

Walking is a straight line at 1.6 m/s (jogging 3.8 m/s) with the mannequin's
walk or jog loop, done in `BP_DlgNPC`'s Tick (`WalkTo`, `StepWalk`). The
characters are plain actors, not pawns, so there is no navigation mesh or path
finding yet; the moves in these plots are short and within one room.

At runtime `/Game/Cousland/Plots/BP_PlotManager` holds the flags for the whole
level (before, each dialogue runner had its own set, so a flag set in one
conversation was invisible to the others). It loads `plots.json` on BeginPlay,
and `SetFlag` runs a flag's actions the first time it becomes true.
`BPC_DialogueRunner` reads and sets flags through it and reports when a
conversation starts and ends; `BP_AreaLoader` gives it the area's waypoints and
tags each spawned character with its creature tag. Whichever needs the manager
first finds it or spawns it, so levels need no setup.

Tested in Play on L_CastleCousland: Fergus' farewell, played to the end, sets
`BHN_FATHER_PARENTS_JOIN`; Bryce and Eleanor move to their upstairs
waypoints, and Bryce's conversation opens on the start line that requires that
flag as soon as Fergus' ends. Played to its end, Bryce's sets
`BHN_FATHER_READY_FOR_NIGHT_TRANSITION`, which sets `BHN_FATHER_READY_TO_GO`
and logs the autosave. Bryce's opening with Howe, played to its end, sets
`BHN_FATHER_DUNCAN_JOINS`: Duncan moves to his waypoint in the hall and his
conversation opens after Bryce's. Aldous' conversation, played to the end,
sets `BHN_SCRIBE_MOVES_AWAY` and he walks 5.4 m to his waypoint.
`DUNCAN_APPEARS` is translated but not reachable from a fresh start.
