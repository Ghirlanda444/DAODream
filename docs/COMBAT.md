# Combat prototype: the larder fight

The first fight of the Human Noble origin, playable in
`/Game/Cousland/Maps/L_CastleCousland`: the mabari in the larder, three waves of
giant rats, and what the castle does once they are dead. It is a prototype of
the loop (hostiles chase and bite, the player strikes, deaths drive the plot).
Health, attack, defense and damage come from the game's data tables, computed
the way its scripts do (see "Stats" below); abilities, talents and armour are
not there yet.

## How the fight is put together

All of it is the game's own logic, translated:

1. Ser Gilmore joins the party in his conversation (`BHN_GILMORE_IN_PARTY`,
   whose handler calls `UT_HireFollower`) and comes along to the larder.
2. Talking to the mabari (`gen00fl_dog`, conversation `dog00cr_main`) in the
   larder plays Gilmore's lines and sets `BHN_COOK_RAT_FIGHT_BEGINS`.
3. The cook's plot script (`bhn100pt_cook`) handles that flag: the pantry door
   locks and team 1 (`BHN_TEAM_RATS`, six giant rats) appears. It also sets
   `BHN_DOG_IN_PARTY`, which sets the general party plot's `GEN_DOG_RECRUITED`
   (`gen00pt_party`), whose handler recruits the dog: it joins and fights.
4. Each rat's death script (`bhn100cr_rat_giant`) brings in its replacement:
   rats 1-6 activate 7-12, rats 7-12 activate 13-18. Rats 7-18 are team 25.
5. When team 25 is destroyed, the area script (`bhn100ar_castle_cousland`)
   unlocks the pantry and upstairs doors, sets `BHN_COOK_RATS_KILLED` and has
   Gilmore talk. At the end of that conversation he leaves the party
   (`BHN_GILMORE_LEAVES_PARTY`, `UT_FireFollower`) and opens the pantry door;
   the dog stays.

Steps 4 and 5 come from `daotools unreal plots`, which now also translates
creature death branches (key `death:<tag>`) and area team-destroyed cases (key
`teamdead:<id>`) into the same action table as the plot scripts (see
`docs/SCRIPTS.md`).

## Getting the mabari

The larder dog uses a generic template outside the `bhn*` resources, so it is
pulled on its own; its conversation and voice go next to the others:

```powershell
py -m daotools pull "<game>" "gen00fl_dog*" --out extracted/dog
py -m daotools pull "<game>" "dog00cr_main*" --out extracted/dog
py -m daotools fsb extract extracted/dog/raw/loose/dog00cr_main.fsb --out extracted/ue/vo/dog00cr_main
py -m daotools unreal conv extracted/dog/json/al_bhn01al_castle_cousland/dog00cr_main.dlg.conv.json `
  --names extracted/human_noble/json --plots extracted/plots/raw --true-flag GEN_GENDER_MALE `
  --vo extracted/dog/raw/loose/dog00cr_main.fsb --out extracted/ue/conversations/dog00cr_main.json
```

`daotools unreal area ... --pull extracted` then finds its template too.

## In Unreal

- `daotools unreal area` exports, per creature, whether it is hostile
  (`GroupId` 1 or 36, `GROUP_HOSTILE*`) and its rank (`CREATURE_RANK_*`).
- `BP_DlgNPC` (every spawned creature): `SetupCombat` takes its stats from the
  area file and shows a hostile's health over its head. In `CombatTick`
  a visible hostile within 15 m turns to the player, jogs to 1.1 m at 3 m/s and
  attacks every 2 s (`BP_PlotManager.AttackPlayer` rolls it). `TakeAttack`
  rolls an attack against it (a hit, or "Miss" over its head); `TakeHit` and
  `Die` hide the creature, drop its `team:<id>` tag and tell the plot manager.
- `BP_PlotManager`: the player's stats (`SetPlayerStats`, health shown top
  left), the attack on F or the left mouse button
  (`/Game/Cousland/Combat/IA_Attack`, mapped in `IMC_Dialogue`): an attack on
  the nearest live hostile within 2.3 m, at most once a second. Every creature bids its distance (`Bid` → `Offer`) and the
  nearest is hit. On a death it runs `death:<tag>`, and `teamdead:<id>` when no
  creature with that team tag is left. Fighting pauses during conversations.
  At 0 health the player is "knocked down" and healed (there is no game over
  yet).
- The party: plot actions of kind 8 (`party`, from `UT_HireFollower`,
  `SetFollowerRecruited`, `SetFollowerInParty`, `AddNonPartyFollower` and their
  opposites `UT_FireFollower`, `Party_SetFollowerInCamp`) call
  `BP_DlgNPC.SetInParty`. A party member (`PartyTick`) follows the player and
  stops 3 m away, reappears 2 m behind the player when more than 25 m off (the
  game puts a hired follower at your side), and every 0.5 s asks the plot
  manager for the nearest live hostile within 12 m of itself (`AssignTarget`,
  the same distance bids as the player's attack). It goes to that target and
  attacks every 1.5 s with its own stats. Party members stand still during conversations;
  you can still talk to them.

Played through (with the placeholder numbers that came before the stats):
Gilmore joins and follows, the mabari's conversation starts the fight and the
dog joins; Gilmore and the dog kill all 18 rats, the castle reacts as above,
and Gilmore leaves the party at the end of his conversation.

## Stats

`tools/daotools/stats.py` ports the scripts that set a creature's numbers
(`sys_autoscale_h`, `sys_chargen_h`, `combat_damage_h`, `combat_h`) and reads
the tables they use from `packages/core/data/2da.erf`: `packages_base` (a
creature's class, strategy and minimum level), `autoscale` (per rank: level
offset, attribute, health and damage scales), `as_data` (how a strategy spends
attribute points), `cla_data` (class base health, attack, defense, health and
damage per level, attribute adjustments), `race_base`, `itemstats` (weapon
damage) and `difficulty` (the damage scaling threshold on Normal).

- Level: the area's level plus the rank's offset, at least 1 and the package's
  minimum. Attributes: 10, plus the points autoscaling spends by strategy, plus
  the class's adjustments (and the race's, for the player).
- Health: class base health x the rank's health scale, plus health per level
  for each level above 1.
- Damage: the equipped weapon's damage to damage x range (unarmed 3 to 4.5,
  with strength counting 1.25 times), plus 25-50% of strength above 10, plus
  damage per level. A hit above the threshold (7 on Normal) is multiplied by
  the rank's damage scale: critters and normal creatures deal 0.4 of it.
- To hit: attack + 50 + 4 - the target's defense, in percent.

`daotools unreal area ... --game "<game>"` writes `NpcHealth`, `NpcAttack`,
`NpcDefense`, `NpcDamage` (min and max per creature), `NpcDamageScale` and the
player's `PlayerStats` (a level 1 human warrior with a longsword). Weapons
come from the item templates, pulled once with
`py -m daotools pull "<game>" "gen_im_wep*" --out extracted/items`;
`--area-level` sets the level the area scales to (1 by default).
`BP_AreaLoader.LoadStatData` reads them.

At level 1 a giant rat has 40 health, attack 60, defense 45 and bites for
4.7-7.4 (scaled to 3 above 7); Gilmore has 106 health and hits for 8.8-13.3;
the mabari has 100 health; the player has 100 health and hits for 8.7-13.4,
69% of the time against a rat. Checked in Play: a rat dies after four hits
(one miss in five), and its bites take the player from 100 to 72 in eight.

Not included, because the engine adds them outside the scripts: the
attributes' bonuses to attack, defense and health, armour, item materials and
talents. Both sides are missing the same pieces, so the fight keeps its shape,
but the player is weaker than in the game, where armour soaks most rat bites.

## Path finding

`L_CastleCousland` has a `NavMeshBoundsVolume` (`CastleNavBounds`) over the
whole castle, and its `RecastNavMesh-Default` builds at runtime
(`RuntimeGeneration` Dynamic), because the walls, floors and furniture only
exist once `BP_AreaLoader` has spawned them. Every mover in `BP_DlgNPC`
(companions following and fighting, hostiles chasing, scripted walks) goes
through `FollowPath`: it asks the navigation system for a path
(`FindPathToLocationSynchronously`) at most every 0.6 s or when the goal moves
more than 1.5 m, and walks the path's points. Without a path (no nav mesh, as in
L_GreatHall) it walks straight. Checked: Gilmore, following the player from the
corridor into the kitchen 20 m away, takes a 7-point path round the walls.
Movers still don't push against each other or the player.

## Reading the fight

- Your health: `/Game/Cousland/Combat/WBP_CombatHUD`, top left (a bar and
  "Health n/100"), created by `BP_PlotManager.InitCombat`. The same widget
  shows short messages in the middle of the screen for 3 s: "Fight over" when
  the last visible hostile dies, and "Knocked down" at 0 health.
- Hostiles: a red bar over their head (`WBP_HealthBar` in a screen-space
  widget component on `BP_DlgNPC`) instead of the name, which got in the way
  when several rats crowd together.
- Hits: the target is pushed back 25 cm and a damage number rises from it
  (`/Game/Cousland/Combat/BP_FloatText`, gone after 0.9 s).
- Attacks: your character swings (`MM_Attack_01` played on the template's
  `DefaultSlot`), and rats and party members play the same attack once per
  bite or strike, then return to idle.
- Room names from the area's map notes float over each room
  (`/Game/Cousland/Areas/BP_RoomLabel`, spawned by `BP_AreaLoader`): Main
  Hall, Pantry, Kitchen and so on.

## Not there yet

Abilities, talents, armour and the attributes' bonuses; real-time with pause
and tactics; hostiles only ever attack the player, never party members; party
members cannot be hurt or switched to; proper animations (everyone is a
mannequin, the rats are small ones, and the attack is a generic punch);
a game over.
