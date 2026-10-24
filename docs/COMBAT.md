# Combat prototype: the larder fight

The first fight of the Human Noble origin, playable in
`/Game/Cousland/Maps/L_CastleCousland`: the mabari in the larder, three waves of
giant rats, and what the castle does once they are dead. It is a prototype of
the loop (hostiles chase and bite, the player strikes, deaths drive the plot).
Health, attack, defense, damage, armour, criticals and flanking come from the
game's data tables with Dragon Age Reborn's overrides, computed the way its
scripts and engine do (see "Stats" and "Rules" below); abilities and talents
are not there yet.

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
  --names extracted/human_noble/json --names extracted/dog/json --plots extracted/plots/raw --true-flag GEN_GENDER_MALE `
  --vo extracted/dog/raw/loose/dog00cr_main.fsb --out extracted/ue/conversations/dog00cr_main.json
```

`daotools unreal area ... --pull extracted` then finds its template too.

## In Unreal

- `daotools unreal area` exports, per creature, whether it is hostile
  (`GroupId` 1 or 36, `GROUP_HOSTILE*`) and its rank (`CREATURE_RANK_*`).
- `BP_DlgNPC` (every spawned creature): `SetupCombat` takes its stats from the
  area file and shows a hostile's health over its head. In `CombatTick`
  (`HostileTick`) a visible hostile picks its foe every 0.5 s
  (`BP_PlotManager.PickFoe`): the nearest of the player and the standing party
  members within 15 m (the player offers itself, each party member bids with
  `FoeBid` → `FoeOffer`). It jogs to 1.1 m of its foe at 3 m/s (`ChaseFoe`) and
  attacks every 2 s (`Bite` → `StrikeFoe`: `TakeStrike` on a party member,
  `BP_PlotManager.StrikePlayer` on the player). `TakeAttack`
  (the player's attack) and `TakeStrike` (a party member's) roll an attack
  against it with the rules below (a hit, or "Miss" over its head); `TakeHit` and
  `Die` hide the creature, drop its `team:<id>` tag and tell the plot manager.
- `BP_PlotManager`: the player's stats (`SetPlayerStats`, health shown top
  left), the attack on F or the left mouse button
  (`/Game/Cousland/Combat/IA_Attack`, mapped in `IMC_Dialogue`): an attack on
  the nearest live hostile within 2.3 m, at most once a second. Every creature bids its distance (`Bid` → `Offer`) and the
  nearest is hit. On a death it runs `death:<tag>`, and `teamdead:<id>` when no
  creature with that team tag is left. Fighting pauses during conversations.
  Falling, as in the game (`player_core`, `effect_resurrection_h`): a party
  member at 0 health falls instead of dying (`Wounded` → `KnockOut`: it lies
  in `/Game/Cousland/Anims/A_Fallen`, the mabari in its death pose, with
  `bDead` and `bDown` set, and its health bar shows over it once hurt). The
  player at 0 falls the same way while a party member still stands
  (`PlayerFalls` → `PlayerDown`: "You have fallen", the input stops, the
  player's mesh plays `A_Fallen`, hostiles leave them be). When nobody stands
  the fight is lost (`GameOver`: "Your party has fallen", and 5 s later
  `Restart` reloads the level). `RegenTick` (every 0.5 s): 4 s after the last
  blow anywhere (`LastCombat`, stamped by `ResolveHit`) the fallen get up with
  1 health (`RevivePlayer`, `BP_DlgNPC.GetUp`; the game's
  `ResurrectPartyMembers`, which also gives an injury: injuries come with
  effects in stage 3), and the player and party members regain 10 health a
  second (`RegenAll`; `REGENERATION_HEALTH_EXPLORE_DEFAULT`). Test switch: with
  `bOneShot` set (off by default) the player's attack kills any hostile in
  reach outright, without the to-hit roll; `ke * ToggleOneShot` in the
  editor's console switches it during Play.
- The party: plot actions of kind 8 (`party`, from `UT_HireFollower`,
  `SetFollowerRecruited`, `SetFollowerInParty`, `AddNonPartyFollower` and their
  opposites `UT_FireFollower`, `Party_SetFollowerInCamp`) call
  `BP_DlgNPC.SetInParty`. A party member (`PartyTick`) follows the player and
  stops 3 m away, reappears 2 m behind the player when more than 25 m off (the
  game puts a hired follower at your side), and every 0.5 s asks the plot
  manager for the nearest live hostile within 12 m of itself and 15 m of the
  player (`AssignTarget`; without the second limit the dog went from one kill
  to the next soldier near it and ended up across the castle;
  the same distance bids as the player's attack; a hostile another party member
  is already fighting bids 3 m further away, so the dog and Gilmore pick
  different rats when there is a choice). Party members within 1.1 m of each
  other step apart (`Separate`). It goes to that target and
  attacks every 1.5 s with its own stats. A party member on a scripted walk
  (jogging over to talk, a plot's walk) finishes it before following or
  fighting again; before, the walk and the fight pulled the same character
  each frame and Eleanor jogged on the spot instead of fighting. Party members stand still during conversations;
  you can still talk to them.
- Allies: friendly creatures that carry a weapon and chest armour (the
  castle's guards and knights, Gilmore; not servants or nobles, and never
  Howe's men, some of whom start out neutral) are exported with `NpcAlly`
  (`area.armed_ally`). Without joining the party they fight like party
  members (`AllyTick`, the same target bids and `PartyFight`), so only
  hostiles within 15 m of the player, and they stand where the fight ended.
  Checked in Play: the chapel's two guards kill Howe's four chapel soldiers.

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
attribute points), `cla_data` (class base health, stamina, attack, defense,
health, stamina and damage per level, attribute adjustments), `race_base`,
`itemstats` (weapon damage, armour penetration, critical chance, attribute
factor and attributes) and `difficulty` (the damage scaling threshold on
Normal). With `--mod-tables` the export puts a rebalance mod's override tables
on top: Dragon Age Reborn's (`docs/COMBAT_BALANCE.md`) raise the health of
ranks 2-5 and 11 by 30%.

- Level: the area's level plus the rank's offset, at least 1 and the package's
  minimum. Attributes: 10, plus the points autoscaling spends by strategy, plus
  the class's adjustments (and the race's, for the player).
- The attributes' derived stats are the engine's (not in the scripts), per
  point above 10 as the game's character sheet gives them: melee attack +0.5
  for strength and for dexterity, defense +1 for dexterity, health +5 for
  constitution, stamina or mana +5 for willpower, armour penetration +1/7 for
  cunning.
- Health: class base health x the rank's health scale, plus health per level
  for each level above 1, plus constitution's. Stamina: base plus per level, x
  the rank's scale, plus willpower's (exported for stage 2).
- Attack and defense: the class's base plus the attributes'; a shield adds its
  defense.
- Damage: the equipped weapon's damage to damage x range (unarmed 3 to 4.5,
  with the attribute counting 1.25 times), plus 25-50% of the weapon's
  attribute above 10 (strength; the mean of strength and dexterity for bows) x
  its attribute factor (a dagger 0.85, a greatsword 1.1). Damage per level is a
  separate bonus added after armour.
- Armour penetration: the weapon's plus cunning's. Critical chance: 3% x the
  rank's scale, plus the weapon's (a longsword 2, a dagger 3). Flanking: up to
  15 for rogues, 7.5 for everyone else.

`daotools unreal area ... --game "<game>" --mod-tables extracted/mods/da_reborn/erf
--player-template extracted/player/json/chargen/default_hm_noble.utc.json`
writes `NpcHealth`, `NpcAttack`, `NpcDefense`, `NpcDamage` (min and max per
creature), `NpcDamageScale`, `NpcRules` (per creature: armour, armour
penetration, critical chance, most flanking, damage bonus) and the player's
`PlayerStats` (health, attack, defense, damage min and max, threshold, the same
five rules, stamina). The player is a level 1 human warrior with the
template the game starts the Human Noble from (`background_defaults` row
3105: `default_hm_noble`, pulled with
`py -m daotools pull "<game>" "default_hm_noble*" --out extracted/player`):
longsword, small wooden shield, rolled-leather light armour, boots and gloves.
Weapons and armour come from the item templates, pulled once with
`py -m daotools pull "<game>" "gen_im_wep*" --out extracted/items`;
`--area-level` sets the level the area scales to (1 by default).
`BP_AreaLoader.LoadStatData` reads them; `BuildFixtures` reads `NpcRules`
and `GiveNpcRules` hands each creature its five (`BP_DlgNPC.SetRules`).

At level 1, with Dragon Age Reborn's tables: a giant rat has 55 health,
attack 63.5, defense 48, no armour and bites for 4.2-7.0 (+0.4); Gilmore has
121 health and armour 6; the mabari 130 health; Bryce 275; the player 115
health, attack 64.5, defense 50.5 (1.5 from the shield), armour 4.25, armour
penetration 2.1, critical chance 5%, and hits for 8.3-13.0 (+0.4), 71% of the
time against a rat. Armour now soaks most of a rat's bite (1.5-4.5 gets
through), as in the game.

Not included yet: item materials' effect on weapon damage, talents and
abilities, and the unarmed damage range (the script gives a flat 3; the game's
creatures may carry natural weapons the templates do not list).

## Rules

`tools/unreal/combat_rules.py` builds the hit rules into the Blueprints (graph
code in `tools/unreal/dsl`); `stats.py` has the same rules in Python
(`hit_chance`, `flanking_bonus`, `crit_chance`, `hit_damage`) for the
balance simulator to come. Every attack goes through `BP_PlotManager`:

1. `FlankBonus`: the attacker's angle seen from the way the target faces;
   120-180 degrees (behind it) gives up to the attacker's most flanking.
2. `ResolveHit`: a critical is threatened when rand(100) < critical chance x
   (1 + flanking / 5); the attack hits when rand(100) < attack + 54 +
   flanking - defense (50 for the roll, 4 the game's bias towards hits).
3. `RollHit`: the weapon's damage roll, x1.5 on a critical.
4. `Mitigate`: minus the target's armour (70% fixed, 30% rolled) less the
   attacker's armour penetration, plus the damage bonus, x the rank's damage
   scale when above the threshold; `FloorDamage`: at least 1.

`StrikeNpc` applies the outcome to a creature, `StrikePlayer` to the player,
`PlayerStrike` is the player's attack. `LastDamage` (-1 for a miss),
`LastCrit` and the counters `Hits`, `Misses` and `Crits` are there for tests:
`py playtest.py fight day --fall` fights the larder's rats and reports them,
then lets the player fall; `py playtest.py party day --wipe` fights them with
Gilmore and the mabari, drops the player, wins the fight and checks that
everyone gets up, then knocks everyone out.

Checked in Play (silent), with Gilmore and the mabari against the first six
rats: the rats went for all three; the mabari fell (down, not dead) while
Gilmore fought on from 121 to 49; the dropped player lay in `A_Fallen` among
the rats while the party fought on. Left alone, Gilmore fell too and the level
reloaded (the whole party down). When the test struck down the remaining rats
and the next wave, the player and the mabari were up again a few seconds later
in the same world, and everyone regenerated to full within 9 s; Gilmore's
conversation for the end of the rat fight then started, as the castle's
script has it.

Checked in Play (silent), sampling `ResolveHit` 400 times with known numbers:
attack 64.5 against defense 48 hit 72.5% (70.5% expected); a 20% critical
chance gave 19.5% criticals at 1.5 times the damage; with the attacker behind
the target `FlankBonus` gave 7.5 and the hits and criticals rose to 80% and
12% (78% and 12.5% expected); armour 10 let 1 to 2.97 of a 10-damage hit
through. The player's stats arrive as exported, ten strikes killed a rat
(11-13 a hit), rats bit through the player's armour for about 3, and at 0
health the level reloaded. The test's own swings are slow (one console command
every few seconds), so alone against two rats the player falls there; in play
a swing a second kills a rat in about 7 s while two rats take about 2 health a
second.

### Armour

What each creature wears is its template's `Equip_ItemList`; `stats.equipment`
sorts the items into pieces by their base item (`itemstats` label: chest armour
or clothing, helmet, gloves, boots, shield) and sums their armour as the engine
does: a piece's `Armor` (itemstats, per base item: light chest 3.0, medium
4.25, heavy 6.25, helmets 1.0, gloves 0.75, boots 1.0) times its material's
`Armor` multiplier (`materialtypes`, by the item's `Material`: iron 1.0, steel
1.25; the hide and leather rows have none and count as 1). Shields give no
armour but `Defense` and `MissileDeflection` (a kite shield 4 and 3). The area
export writes `NpcOutfit` ("chest=<item>,helmet=<item>,..."), `NpcArmour` and
`NpcShieldDefense` per creature. Castle guards in medium chainmail have 7,
Howe's men in leather 5 or 6, the nobles and servants 0.

combat_damage_h takes the armour off every hit (`Mitigate` above). The
armour and clothing templates come from
`py -m daotools pull "<game>" "gen_im_arm_*" --out extracted/items` (and
`gen_im_cth_*`, `gen_im_duncan_robe*`).

## Balance simulator

`tools/daotools/simulate.py` fights the party against foes many times over without Unreal, with the same
rules (`stats.py`'s `hit_chance`, `crit_chance`, `hit_damage`) and the prototype's fight: everyone engaged
from the start, the player striking once a second, party members every 1.5 s, hostiles every 2 s; a hostile
keeps to one standing party member, a party member goes for the foe its side is fighting least, an
attacker its target is not fighting gets its flanking bonus; foes in waves, each death bringing the next
in; party members fall at 0 and the fight is lost when all are down. The fighters' numbers come from the
area export, so exports with and without `--mod-tables` compare vanilla and Dragon Age Reborn:

```powershell
py -m daotools unreal simulate extracted/ue/areas/bhn100ar_castle_cousland.json `
  --party bhn100cr_gilmore --party gen00fl_dog --foes "bhn100cr_rat_giant_*" --wave 6 --runs 2000
```

First finding (2026-10-24): with the numbers now in the game, the larder fight (the player, Gilmore and
the mabari against 18 rats in waves of six) is won only 55% of the time, and the mabari falls in 89% of
fights; in the game it is an easy first fight. Dragon Age Reborn changes neither critters nor the player,
so its tables give the same. What moves it (2,000 fights each):

| Change | Won | Mabari falls |
| --- | --- | --- |
| None (as exported) | 55% | 89% |
| Rats without constitution's +15 health (40 instead of 55) | 99% | 64% |
| The mabari biting like a longsword (9-13.5 instead of 3.6-5.8) | 82% | 76% |
| Both | 100% | 45% |
| Rats biting every 3 s instead of 2 | 100% | 51% |

So three assumptions decided it. Checked against the game's data (2026-10-24):

- **Natural weapons and armour** (settled): at spawn `creature_core` equips each creature with its
  appearance's `DefaultWeapon` and `DefaultArmor` (`apr_base`) when its template has none. The giant rat
  (appearance 37) bites with `gen_im_cweapon_rat` ("Creature - Claw, Quick": 3 damage, half the strength
  bonus, armour penetration 2) and wears light rolled leather (armour 3); the party mabari (35) bites with
  `gen_im_cweapon_dog_party` ("Creature - Claw, Medium": 6-7.5, penetration 3). The export now adds them
  (`stats.natural_equipment`; they count for the numbers, not the look): rat bites 3.5-4.0 (+0.4), the
  mabari's 6.5-8.5 (+1.0).
- **Attack timing** (partly settled): `CalculateAttackTiming` gives a humanoid with a weapon 2.0 s per attack
  with one weapon or a shield, 1.5 s with two, 2.5 s two-handed, plus the weapon's `dspeed` (a longsword
  -0.1: the player and Gilmore 1.9 s, not the prototype's 1.0 and 1.5). Anything else is timed by the engine
  from its attack animations (`stats.attack_anims`, from `anims.erf`): a rat's bite (`c_rat.attk_v1`) lasts
  0.63 s and its pause between moves 0.97 s; the mabari's attacks 1.6 and 2.3 s (2.07 on average). The
  export writes `NpcInterval` and the player's interval (`PlayerStats[12]`); the simulator uses them. What
  the engine does between two creature attacks (straight into the next, or a pause) is not in the data.
- **Constitution for critters** (open): the scripts never add constitution to health and no table holds
  the per-point bonus; it is the engine's, and whether it applies to critters as to the player is not in
  the data.

With the data-backed numbers the fight gets harder, not easier: the player's and Gilmore's slower swings
and the rats' hides outweigh the mabari's real bite. Sweeping the two open numbers (2,000 fights each):

| Rat bites every | Rat health | Won | Player falls | Mabari falls |
| --- | --- | --- | --- | --- |
| 0.63 s (bite only) | 55 or 40 | 0% | 100% | 100% |
| 1.6 s (bite and pause) | 55 / 40 | 0% / 2% | 100% / 99% | 100% / 99% |
| 2.0 s | 55 / 40 | 0% / 43% | 100% / 78% | 100% / 86% |

Since the fight is easy in the game, something on the party's side is still missing from the port, or the
engine paces creatures more slowly than their animations. Not yet in the port and worth checking next:
the warrior's starting talents and the player's five free attribute points at character creation, and the
original game itself (how many sword hits a rat takes, how often rats bite) as the ground truth. Unreal
still uses the prototype's fixed timers; it reads `NpcInterval` once this is settled.

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

Abilities, talents, stamina use; real-time with pause and tactics; threat
(hostiles go for the nearest foe, not the one they hate most); allies outside
the party (the castle's guards) cannot be struck yet; injuries; switching to a
party member; proper animations (the attack is a generic punch, the fall and
getting up are instant). The plan: `docs/COMBAT_DESIGN.md`.
