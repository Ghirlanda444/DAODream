# The night castle

Castle Cousland after Howe's betrayal: area `bhn200ar_castle_after_siege` on
layout `hrt201n` (the same castle, its night version), playable in
`/Game/Cousland/Maps/L_CastleNight`.

## Building it

```powershell
py -m daotools pull "<game>" "hrt201n*" --out extracted/layouts/hrt201n_pull
py -m daotools pull "<game>" "dog_mabari_*" --out extracted/dog
py -m daotools unreal area extracted/human_noble/json/al_bhn02al_castle_after_sie/bhn200ar_castle_after_siege.are.json `
  --layout "<game>/packages/core/env/hrt201n.arl" --pull extracted --start bhn200wp_pc_bedroom `
  --rooms extracted/layouts/hrt201n_pull/json --kit extracted/kit/json --game "<game>" `
  --add-creature gen00fl_dog@bhn200wp_dog_bedroom --fill-lights 0.25 `
  --out extracted/ue/areas/bhn200ar_castle_after_siege.json
```

Howe's war dogs use generic templates (`dog_mabari_*`), pulled on their own.
The mabari is a party member the game brings from the day, not part of the
night area, so `--add-creature` puts him in your bedroom. The export has 1,377
floor boxes, 7,596 kit solids (328 kit ceilings and 4,801 lids among them),
130 lights, 95 creatures (71 hidden until the scripts call
them, most of them Howe's soldiers in 22 teams), 50 waypoints, 26 doors and
15 triggers. Every creature is spawned now, also those with no conversation,
team or ambient behaviour (the warning servant, the bodies): plots move and
kill them. The game's bodies (`bhn200cr_guard_dead`, `bhn200cr_servant_*_dead`)
are templates with `CREATURE_SPAWN_DEAD` set; the export lists them in
`NpcDead` and the loader kills them once spawned (`KillDead`). A killed
creature goes limp: its capsule stops colliding, its mesh becomes a ragdoll
(the mannequin's death clips are only the start of a fall) with a push at the
chest so it topples, and its name is hidden.

`L_CastleNight` is a copy of `L_CastleCousland` whose `BP_AreaLoader` loads
the night area, lit by a dim blue moon (directional light 0.6 at 35 degrees,
lighting the atmosphere, so the sky is a deep blue) and a blue sky light that
keeps the shadows readable. An unbound post-process volume (`NightGrade`)
fixes the exposure at -1.5 EV, so the eye does not adapt the night into day,
and takes some colour out. Under the roofs (`docs/ART.md`) the moon only
reaches what is still open; the rooms are lit by the game's 130 night lights,
mostly torches, at `LightScale` 20. The game also lit its areas with baked
ambient light, which we do not have: about half the walkable floor gets
nothing from the 130 lamps, and corridors there were black. `--fill-lights
0.25` adds 166 dim, cool fill lights (9 m radius, no shadows, 2.2 m up) on a
5 m grid wherever the lamps do not reach the floor (`area.fill_lights`).
Checked in Play: 27 sample spots with no lamp light went from a mean
brightness of about 2-12 (of 255) to 30-90, the lit rooms barely changed.
Lumen's sky light leaking and local exposure were tried first and lift the
dark spots by only a few points, since at night there is almost no sky light
to leak. Its loader's
`StartFlags` (`BHN_MAIN_BATTLE_BEGUN`, `BHN_MOTHER_BATTLE_BEGUN`) are added
quietly at load, so the level also plays when started on its own; arriving
from the day castle they are already set.

## Getting there

`BHN_MAIN_BATTLE_BEGUN` (`bhn000pt_main`) ends with
`UT_DoAreaTransition(bhn200ar_castle_after_siege, bhn200wp_pc_bedroom)`:
action 13. `BP_PlotManager.Transition` stores the flag set in a SaveGame
(`/Game/Cousland/Plots/BP_FlagSave`, slot "transition") and opens the level;
the next level's manager restores and deletes it on load. Checked: a flag set
in the day castle is there in the night castle.

## What plays

Checked in Play:

1. Load (`load:bhn200ar_castle_after_siege`): the game's opening cutscene
   (`CUTSCENE_BHN_NIGHT_FALLS`) has no spoken line, so a caption card titled
   "Night falls" says what has happened: Fergus has ridden south, Howe's
   soldiers turn on the household in the dark while more storm the gates,
   and the mabari wakes you (`docs/SCRIPTS.md`, Cutscenes). It advances by
   itself (about 25 s); a click skips a line, Escape the rest. Oren,
   Oriana, Nan and Aldous lie dead; the dog is taken out of the party.
2. When the caption ends the mabari talks, as the cutscene's script asks
   (before, you had to talk to him): "(Angry barking and growling)" (his
   night line, `DOG_DEFINED_AFTER_BATTLE_BEGUN_AND_PRELUDE_NOT_STARTED`, a
   defined flag now computed), then a servant bursts in
   (`BHN_DOG_WARNING_SERVANT_ENTERS`) and is killed as two of Howe's men appear
   and attack (`BHN_DOG_WARNING_SERVANT_DIES`: team 16, `KillCreature`); the
   dog joins your party (also when arriving from the day, where "dog
   recruited" is already set: the script forces it to run again).
3. The two soldiers dead (team 16 destroyed): Mother comes out and talks
   ("Darling! I heard fighting outside...").
4. Walking upstairs into `bhn200tr_howe_upstairs`: the two soldiers at
   Mother's door turn hostile (`UT_TeamGoesHostile`) and one shouts.
5. Opening the larder (pantry) door, the first time: the finding-Bryce
   cutscene plays as its voiced lines (Bryce, wounded, and Eleanor's cry),
   then Bryce talks to you (`open:bhn000ip_door_pantry@bhn200ar_castle_after_siege`,
   `docs/SCRIPTS.md`, Cutscenes). Duncan's conversation sets
   `BHN_MAIN_CUTSCENE_FAMILY_FAREWELL`, and the farewell plays the same way
   and ends the night (`BHN_MAIN_START_PRELUDE`); the scene from Bryce to
   Duncan has not been played through yet.

Opening the bedroom hall door (unlocked when Mother tells you to go
downstairs) brings out Howe's men by Landra's room; when they are dead, the
bedroom hall exit and Landra's door unlock (`teamdead:9`). Opening the dining
hall, chapel and main hall doors starts those fights (`open:<tag>`, see
`docs/SCRIPTS.md`). Further on, the triggers and team events bring out Howe's men in the east
hall, the kitchen, the main hall and the chapel, servants flee
(`UT_ExitDestroy`), and Mother remarks on the rooms you pass (talk triggers).

## Not there yet

The cinematics themselves (cutscenes are shown as captions or voiced
conversations without a camera), changing clothes and the chests (`Siege_UnequipPlayer`), immortal NPCs, fear effects, the dining and
chapel triggers (their scripts exist but no trigger in the area uses them),
Howe's soldiers hacking at doors (`AMBIENT_COMMAND`), and hostiles fighting
anyone but the player and party (the castle's guards fight them, see
`docs/COMBAT.md`, Allies, but nobody hits the guards back). The soldiers hit hard: without armour the
player loses about 5 per hit.
