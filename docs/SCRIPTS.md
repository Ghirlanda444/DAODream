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
  --only "bhn*,gen00pt_party" --true-flag GEN_GENDER_MALE --cutscenes extracted/human_noble `
  --out extracted/ue/plots.json
```

| Kind | Script call | Unreal |
| --- | --- | --- |
| 1 jump | `UT_LocalJump(creature, waypoint)` | teleport the creature to the waypoint's pose |
| 2 talk | `UT_Talk(creature, ...)` | start its conversation, after the current one ends; a speaker more than 6 m away first jogs over to 1.5 m from the player (the game placed extra copies of Gilmore at each doorway for this), and if another conversation is running when it arrives its talk waits for that one; a creature with no conversation does nothing, as in the game (the Howe soldier at the second servants' door) |
| 3 active | `WR_SetObjectActive(object, bool)` | show or hide it (hidden: no collision, cannot talk) |
| 4 setflag | `WR_SetPlotFlag(PLT_X, FLAG, bool)` | set another flag, running that flag's actions the first time it becomes true; when the call asks for the plot's script (4th argument `TRUE`, target `force`) its actions run again even if it is already set, as in the game (the night's "dog recruited" was already true from the day) |
| 5 autosave | `DoAutoSave()` | logged only; there are no saves yet |
| 6 walk | `AddCommand`/`WR_AddCommand(creature, CommandMoveToObject/Location(...))`, `UT_QuickMoveObject` | walk (or jog, when the script runs) to the waypoint, then face its direction |
| 8 party | `UT_HireFollower`, `SetFollowerRecruited`, `SetFollowerInParty`, `AddNonPartyFollower` / `UT_FireFollower`, `Party_SetFollowerInCamp` | join or leave the party: follow the player and fight beside them (`docs/COMBAT.md`) |
| 7 door | `SetPlaceableActionResult(door, PLACEABLE_ACTION_OPEN/CLOSE/LOCK/UNLOCK, TRUE)`, `SetPlaceableState(door, PLC_STATE_DOOR_*)` | open, open the other way, close, lock, unlock (only if locked), break |
| 10 hostile | `UT_CombatStart(attacker, ...)`, `UT_TeamGoesHostile(team)`, `SetGroupId(creature, GROUP_*)` | turn hostile (it attacks) or back |
| 11 exit | `UT_ExitDestroy(creature, run, waypoint)` | walk or run to the waypoint, then vanish |
| 12 kill | `KillCreature(creature)` | lie dead where it stands (a held frame of a death animation), no longer talks |
| 13 transition | `UT_DoAreaTransition(area, waypoint)` | save the flags and open that area's level (`L_CastleCousland`, `L_CastleNight`) |
| 14 if | `if (WR_GetPlotFlag(PLT_X, FLAG) == TRUE/FALSE)`, `if (nVar)` with `int nVar = WR_GetPlotFlag(...)`, `!...` | skip the next actions (its then-branch) unless the flag is as tested |
| 15 skip | the `else` of such an `if` | skip the else-branch after the then-branch ran |
| 9 ambient | `Ambient_Start(creature, ..., pattern)`, `Ambient_StartTeam`, `Ambient_StartTag` / `Ambient_Stop(creature)` | switch its ambient behaviour to that animation pattern, or stop it (`docs/AMBIENT.md`) |
| 16 cutscene | `CS_LoadCutscene(CUTSCENE_X, PLT_Y, FLAG, speaker)` | play the cutscene's lines as a conversation without choices, then set the flag; the speaker's talk follows as a kind 2 (see Cutscenes below) |

Creatures are found by tag (`object oX = UT_GetNearestCreatureByTag(...)` plus
the string constants of every script); `PLT_<NAME>` is the plot named `<name>`
and its flag constants are that plot's flag names. Anything else is listed as
skipped, so coverage is visible in the command's output.

Coverage on the Human Noble plots (16 scripts): `bhn100pt_father` is complete
apart from gore level and achievement tracking. All 14 single-character moves
translate (the cook, the kitchen servants, the gambling guards, the scribe,
the panicked soldiers), and so do all 8 door calls (in the day castle, the
pantry door; the rest are night-castle doors) and all 12 team calls, and every party join and leave (Gilmore, Eleanor, and the
companions in the general party plot `gen00pt_party`, which recruits the mabari). The rest
is still skipped: making a door non-plot
(`SetPlot`), items, combat and area transitions.

### Cutscenes

The scripts load four Human Noble cutscenes with `CS_LoadCutscene(cutscene,
plot, flag, speaker)`: when the cutscene ends the game sets `flag` and the
`speaker` starts talking to the player. Unreal has none of the cinematics, so
`daotools unreal plots --cutscenes <pull folder>` reads the `.cut` files
(`daotools/cutscene.py`) to say what each one tells:

| Cutscene | Loaded by | Length | Plays |
| --- | --- | --- | --- |
| `bhn200cs_night_falls` | the night castle's load event; then the mabari talks | 27 s | no one speaks: a caption |
| `bhn100cs_familyfarewel` | `BHN_MAIN_CUTSCENE_FAMILY_FAREWELL`; then sets `BHN_MAIN_START_PRELUDE` | 34 s | `bhn200dg_farewell_cutscene`, 5 voiced lines |
| `bhn100cs_finding_byron` | the night pantry door (`bhn000ip_door_pantry`, used) | 18 s | `bhn200dg_bryce_cutscene`, 3 voiced lines |
| `bhn100cs_intro` | nothing (the call is commented out in `bhn100ar_castle_cousland`) | 56 s | `bhn100dg_introduction` |

A cutscene is a list of actors (characters, cameras, the `MASTER` track),
each with a generic list of tracks: animations (`AANI`), sounds (`ACSP`,
an FMOD event), camera shakes, fades, and spoken lines (`ASLN`: start and end
time, the conversation the line belongs to and the line as a talk-table
string). Every spoken line of a Human Noble cutscene comes from one
conversation, in order, and `daotools unreal origin` already exports those
conversations with voice. So the action is kind 16 with the conversation as
target and the flag key as argument. A cutscene with no spoken line gets a
caption: a few lines of our own words in `cutscene.CAPTIONS`, which
`daotools unreal origin` writes as a conversation named after the cutscene
(`extracted/ue/conversations/bhn200cs_night_falls.json`, speaker shown as
"Night falls", no voice). A cutscene with neither is skipped.

In Unreal, `BP_PlotManager.Cutscene` plays it on its own `CutRunner`
(`BPC_DialogueRunner` component) through the usual dialogue panel, or queues
it while another conversation runs, like a talk. The runner's `PlayCutscene`
loads the conversation and starts a 0.25 s timer (`AutoTick`) that clicks
"Continue" by itself: when the line's voice has finished and at least 1.2 s
have passed, or for a line without voice after 2 s plus 0.06 s per
character. The player can click ahead or press Escape to skip it.
`ConversationEnded` then sets the cutscene's flag (`FinishCut`), starts a
queued cutscene, and only then a queued talk, so the mabari speaks after the
night caption, as in the game.

Checked in Play on `L_CastleNight`: the night opens on the three caption
lines (about 10, 10 and 5 s), then the mabari's
barking line. `BHN_MAIN_CUTSCENE_FAMILY_FAREWELL` set from the console during
the caption queued the farewell: it played after the caption, each line
advancing when its voice ended (Bryce's first two lines: 8.7 s for 8.1 s of
voice), and at its end set `BHN_MAIN_START_PRELUDE`, whose transition to
Ostagar is not built yet (the end-of-origin message, `docs/NIGHT.md`).

The finding-Bryce cutscene hangs on the pantry door: its script
(`bhn000ip_door_pantry`) has no tag test but checks the door's area when it
is used. In the night castle, the first time, it loads the cutscene (then
`BHN_FATHER_GORE_LEVEL`, then Bryce talks); in the day castle, Gilmore's
pantry, the mabari talks while he is not in your party. These become
`open:bhn000ip_door_pantry@<area>` (see Death and team events below).
Checked in Play on `L_CastleNight`: opening the pantry door plays
`bhn200dg_bryce_cutscene` (its three voiced lines), sets
`BHN_FATHER_GORE_LEVEL`, and Bryce comes over and his conversation opens on
its night start line; closing and reopening the door does not replay it.

### Death and team events

Besides plot scripts, `daotools unreal plots` reads creature and area scripts
whose names match `--only`. A creature script's `EVENT_TYPE_DEATH` branches
`if (sTag == CONST) { ... }` become the key `death:<tag>`, and an area
script's `EVENT_TYPE_TEAM_DESTROYED` cases (`switch (nTeamID)`) the key
`teamdead:<id>`, with the same action kinds. `BP_PlotManager` runs them when a
creature dies or the last member of a team does (`docs/COMBAT.md`). Objects
known only at runtime (array elements in loops, used by the night castle's
Howe soldiers) are skipped, not guessed.

Two more events: an area script's `EVENT_TYPE_AREALOAD_PRELOADEXIT` and
`POSTLOADEXIT` cases become `load:<area>`, which `BP_AreaLoader` runs once the
area is built (in the day castle, Bryce starts talking to you; at night, the
people Howe's men have killed lie where they fell). A load handler
that branches on game state (anything but its "once" and debug checks) is left
out whole, since run unconditionally it would misplace people. A trigger
script's `EVENT_TYPE_ENTER` case becomes `enter:<script>` (see Triggers below).
A door's script (`bhn000ip_door_large_break`) gives `open:<tag>` for each
`if (sTag == X)` in its `DoorOpened` helper, which `BP_Door` runs when the
player opens that door (opening the bedroom hall releases Howe's men by
Landra's room, whose deaths unlock the way down; the dining hall, chapel and
main hall doors release their fights; the servants' doors start their scenes),
and `unlock:<tag>` for each one under `PLACEABLE_ACTION_UNLOCK`, run when the
player tries that door while it is locked (the treasury door starts Mother's
talk). Several door scripts share these events; the first one is kept.
A door script with no tag test whose `EVENT_TYPE_USE` branches on
`GetTag(GetArea(OBJECT_SELF)) == AREA` gives `open:<script>@<area>` per
area, keeping any plot-flag test of the same `if` as a kind 14 and dropping
its `!GetLocalInt(OBJECT_SELF, ...)` do-once test. The script's name stands
for the door's tag (the pantry door's template, tag and script share one
name). `BP_Door`, after `open:<tag>`, sets `open:<tag>@<AreaName>` as a flag
(`BP_AreaLoader.AreaName`), so it runs only the first time the door is
opened in that area, and is remembered across the area transition like any
flag. For the day's dog line, which the game repeats, that means once.
`UT_QuickMove(TAG, WAYPOINT, bRun)` is a walk.
Calls to helper functions defined in the same script (`HoweWarriorStartMother()`)
are expanded in place, objects re-assigned from one tag to the next
(`oSoldier = GetObjectByTag(...)`) are followed statement by statement, and of
`if (nDebug == FALSE) {...} else {...}` only the game's branch is kept.

### Triggers

An area's `TriggerList` places trigger polygons (geometry relative to the
trigger's position). Their template (`.utt`) names the script
(`EventScript`). `daotools unreal area` exports each as a box around its
polygon, from 0.5 m below to 3 m above, with either the key of its script's
enter event, or, for the game's generic talk trigger (`gen00tr_talk`), its
variables: who speaks (`TRIG_TALK_SPEAKER`), the flag that must be set
(`TRIG_TALK_ACTIVE_FOR_*`), the flags that must not be (`TRIG_TALK_INACTIVE_FOR_*`,
two), the flags it sets (`TRIG_TALK_SET_*`, two) and whether it repeats.
`BP_AreaLoader.SpawnTriggers` places a `/Game/Cousland/Areas/BP_Trigger` for
each; four times a second it checks whether the player is inside, and on
stepping in runs the event once, or for a talk trigger checks the flags, sets
its flags and has the speaker talk. Sound and reverb zones (no template) are
skipped. A trigger script that removes the other triggers it finds by tag (the
day castle's two doorway pairs: `bhn100tr_jump_gilmore` moves Gilmore to
`bhn100wp_gilmore_south` and removes the other jump trigger, `bhn100tr_start`
has him talk and removes every start trigger) ends with the flag
`done:enter:<script>`, and `BP_Trigger` skips any trigger whose event has it.
Before, the second doorway moved Gilmore back to the south waypoint and had him
talk again, even with him in your party. Both the game's jump branches send
him to the south waypoint (so from the north doorway he jogs about 27 m to
you); that is the game's script, kept as is. The day castle has 22 (Fergus, the cook and the gambling guard
calling out as you pass, the night transition), the night castle 15 (Mother
remarking on each room, Howe's men waiting upstairs, in the kitchen and the
east hall).

### Defined flags

Conversations also test *defined* flags (IDs 256 and up), which the game
computes on request in a plot script's `EVENT_TYPE_GET_PLOT` handler (written
as the `else` of the SET handler in most scripts). Where a case only reads
plot flags into variables and returns a boolean of them, `daotools unreal plots`
turns it into OR-of-AND clauses over real flags (from the truth table, merged):
`DOG_DEFINED_AFTER_BATTLE_BEGUN_AND_PRELUDE_NOT_STARTED` is
`BHN_MAIN_BATTLE_BEGUN & !BHN_MAIN_START_PRELUDE`. 275 defined flags across
all plots come out this way; the rest test injuries, items, gender or local
variables and stay false. `--true-flag` adds flags that are always true
(`GEN_GENDER_MALE`, as for the conversations). `BP_PlotManager` keeps them in
its flag set: `RecomputeDefined` runs before every flag's actions and on load.
It clears them and checks them once, in the file's order, so the export puts
the always-true flags first and every defined flag after the defined flags it
tests. Before, `GEN_GENDER_MALE` came last and the 15 flags that test it
(Gilmore's night greeting `BHN_MAIN_BATTLE_BEGUN_AND_PC_MALE` among them)
were always false, so Gilmore greeted you at night with his day line.

### Teams

Creatures in an area carry a `TeamId` (-1 for none); scripts show, hide and
move whole teams with `UT_TeamAppears(team, bool)` and
`UT_TeamMove(team, waypoint, bRun)`. The team numbers are `BHN_TEAM_*` in
`bhn_constants_h`. `daotools unreal area` now also exports creatures that
have no conversation but belong to a team, with their team and a stand-in
size (`NpcTeam`, `NpcScale`: animals such as the giant rats are 35% mannequins,
dwarves 80%). The translator turns the team calls into the existing `active`
and `walk` actions with the target `team:<id>`, and `BP_AreaLoader` tags every
spawned team member with `team:<id>`, so `BP_PlotManager` needed no change.
`UT_TeamAppears` on placeable teams (the mouse holes) is still skipped, and
team members walk to the exact waypoint, so they end up on one spot where the
game spreads them around it.

In the day castle the teams are the giant rats: 6 in the larder (team 1,
`BHN_TEAM_RATS`) and 12 more (team 25), all hidden at first. Every other team
(Howe's soldiers, the castle guards, the servants at night) is in the night
castle, which is not built in Unreal yet.

### Doors

`daotools unreal area` exports every door in the area (placeables whose tag
or template names a door): tag, pose, initial state and whether it is active.
The game's door states are 0 closed, 1 locked, 2 open, 3 broken, 4 open the
other way, 5 broken the other way (`PLC_STATE_DOOR_*`). Castle Cousland has 27.

In Unreal each one is a `/Game/Cousland/Areas/BP_Door`, spawned by
`BP_AreaLoader`: a brown greybox panel (`MI_Greybox_Door`) on a hinge, which
swings 90 degrees when open and disappears when broken. The templates only
name a model and the navigation grid is too coarse to show doorways, so the
size comes from the door's model when `unreal area` gets `--game` (see
`docs/GAME_DATA.md`), otherwise from the kind of door: small ones 1.6 x 2.6 m,
all others 3 x 3.6 m. The panel spans across the door's facing
direction; closed, it sits in the wall line between the greybox walls.
Within 2.5 m the player sees "E: open", "E: close" or "Locked", and E opens or
closes it. When a door and people you can talk to are all in reach, E goes to
the closest one; party members count as 2.5 m further away than they are, so
a door or a stranger wins over the companion at your side, and you talk to a
companion only when nothing else is near. A locked door runs its `unlock:`
event instead of opening. Plot
actions find doors by tag; several ordinary doors share one tag
(`bhn100ip_dr_lg_pt`), but every door a plot script names has its own.

Walking is at 1.6 m/s (jogging 3.8 m/s) with the mannequin's walk or jog
loop, done in `BP_DlgNPC`'s Tick (`WalkTo`, `StepWalk`), along a path from the
castle's navigation mesh (see `docs/COMBAT.md`, Path finding).

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
Doors: E opens and closes a closed door in the main hall and does nothing on
a locked one. Gilmore's conversation, played with `BHN_COOK_RATS_KILLED` set
by hand (the larder fight does not exist yet), sets
`BHN_GILMORE_LEAVES_PARTY`, and the pantry door swings open.
Teams: no conversation we have sets `BHN_COOK_RAT_FIGHT_BEGINS` (likely the
mabari's, which is outside the Human Noble pull), so it was set from the
editor's console during Play (`ke * SetFlag <GUID:FLAG> true`): the six larder
rats appear and the other twelve stay hidden. `ke * WalkNpc team:1
<waypoint> true` sends all six jogging to a waypoint.
