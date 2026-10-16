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
  --add-creature gen00fl_dog@bhn200wp_dog_bedroom --out extracted/ue/areas/bhn200ar_castle_after_siege.json
```

Howe's war dogs use generic templates (`dog_mabari_*`), pulled on their own.
The mabari is a party member the game brings from the day, not part of the
night area, so `--add-creature` puts him in your bedroom. The export has 967
floor boxes, 7,596 kit solids (328 kit ceilings and 4,801 lids among them),
130 lights, 95 creatures (71 hidden until the scripts call
them, most of them Howe's soldiers in 22 teams), 50 waypoints, 26 doors and
15 triggers. Every creature is spawned now, also those with no conversation,
team or ambient behaviour (the warning servant, the bodies): plots move and
kill them.

`L_CastleNight` is a copy of `L_CastleCousland` whose `BP_AreaLoader` loads
the night area, lit by a dim blue moon (directional light 0.6 at 35 degrees,
lighting the atmosphere, so the sky is a deep blue) and a blue sky light that
keeps the shadows readable. An unbound post-process volume (`NightGrade`)
fixes the exposure at -1.5 EV, so the eye does not adapt the night into day,
and takes some colour out. Under the roofs (`docs/ART.md`) the moon only
reaches what is still open; the rooms are lit by the game's 130 night lights,
mostly torches, at `LightScale` 20. Its loader's
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

1. Load (`load:bhn200ar_castle_after_siege`): Oren, Oriana, Nan and Aldous
   lie dead; the dog is taken out of the party.
2. Talking to the mabari in your room: "(Angry barking and growling)" (his
   night line, `DOG_DEFINED_AFTER_BATTLE_BEGUN_AND_PRELUDE_NOT_STARTED`, a
   defined flag now computed), then a servant bursts in
   (`BHN_DOG_WARNING_SERVANT_ENTERS`) and is killed as two of Howe's men appear
   and attack (`BHN_DOG_WARNING_SERVANT_DIES`: team 16, `KillCreature`); the
   dog joins your party.
3. The two soldiers dead (team 16 destroyed): Mother comes out and talks
   ("Darling! I heard fighting outside...").
4. Walking upstairs into `bhn200tr_howe_upstairs`: the two soldiers at
   Mother's door turn hostile (`UT_TeamGoesHostile`) and one shouts.

Further on, the triggers and team events bring out Howe's men in the east
hall, the kitchen, the main hall and the chapel, servants flee
(`UT_ExitDestroy`), and Mother remarks on the rooms you pass (talk triggers).

## Not there yet

The opening cutscene (`CUTSCENE_BHN_NIGHT_FALLS`), changing clothes and the
chests (`Siege_UnequipPlayer`), immortal NPCs, fear effects, the dining and
chapel triggers (their scripts exist but no trigger in the area uses them),
Howe's soldiers hacking at doors (`AMBIENT_COMMAND`), and hostiles fighting
anyone but the player and party. The soldiers hit hard: without armour the
player loses about 5 per hit.
