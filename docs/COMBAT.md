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

Then the starting points (2026-10-24), from the scripts:

- **The hero**: character creation skipped spends the 5 free points by the class's auto level-up table
  (`AL_DoAutoLevelUp` with `alwarrior_default`'s `AttInit`: strength +3, dexterity +1, willpower +1). The
  Human Noble warrior starts at strength 18, dexterity 15, willpower 11, magic 11, cunning 11, constitution
  13 (the wiki's 15/14/10/11/11/13 before the points): attack 66.5, damage 9-14.5.
- **Talents**: the same table's first picks for 2 talent points are Shield Bash (activated) and Precise
  Striking (sustained: +5 attack with Reborn, +10 in the game, a crit bonus, slower swings, stamina upkeep);
  the class adds the hidden passive Hidden Warrior, which changes no numbers. So the talents change nothing
  until stage 2 brings abilities and stamina.
- **Every other creature** (`AS_CommenceAutoScaling`, party members included): `Chargen_InitializeCharacter`
  gives it the same 5 points and its race first; each attribute its strategy weighs is then set to 10 + its
  share of the rank's bonus points, the 5 points and (rank scale x 3 + 5) per level above 1, so the race
  counts only where the strategy does not weigh; class adjustments last. The port had missed the 5 points
  and scaled no player-rank creature (Gilmore, the mabari) at all. Now: a rat 60 health, attack 64.5,
  defense 49; Gilmore 136 health, attack 66.5, damage 8.75-14; the mabari 140 health, bite 7-9.5.

With all of it the larder fight is still lost (2,000 fights each, by how often a rat bites):

| Rat bites every | Won | Player falls | Gilmore falls | Mabari falls |
| --- | --- | --- | --- | --- |
| 0.63 s (its bite animation) | 0% | 100% | 100% | 100% |
| 1.6 s (bite and pause) | 0% | 100% | 100% | 100% |
| 2.0 s | 1% | 100% | 100% | 100% |
| 3.0 s | 82% | 62% | 19% | 74% |

**Checked against the original game's own numbers** (2026-10-24): a Dragon Age save (`.das`, GFF4 `SAVE`)
keeps every area the character has visited with its creatures' stored properties (`ARE1` → `CRE1`: `ATTR`
base attributes by property id, `DPLT` depletables with base and total, field 16612 the rank). A save of the
owner's (Aedan, Korcari Wilds, 153 areas) holds Castle Cousland with Eleanor and Gilmore as the engine left
them:

- Eleanor (autoscaled, never hired): 15/14/11/10/10/14, health 100 → 120, stamina 100 → 105; the port gives
  exactly that.
- Gilmore (hired): 16/16/15/11/11/13 at level 2, health 106 → 121, stamina 105 → 130. A follower is rebuilt
  when it joins (`EVENT_TYPE_PARTY_MEMBER_HIRED` → `AL_DoAutoLevelUp`): 10 + race + class, then 5 points
  plus 3 a level above 1, attribute by attribute up to 14 + level x its table's `AttWeight`
  (`alwarrior_default`; the mabari `aldog`). `stats.follower_attributes` does this for `area.FOLLOWERS`; the
  port now gives Gilmore exactly the save's numbers.
- Health from constitution: across the save's living creatures at full health the commonest result by far is
  exactly 5 health per constitution point above 10, at every rank, critters included (79 rank 1
  creatures); the rest have constitution from equipment the stored base leaves out. So a level 1 giant rat's
  60 health is right.

The rats themselves are not in it (killed creatures are not saved), but level 1 critters of the same kind
are (rank 1, the default warrior package, damage bonus 0.4 = level 1): a raven on the road to Denerim
(`ran401ar_highway_zevran1`) has STR 15, DEX 14, WIL 11, MAG 10, CUN 10, CON 14, base attack 60, base defense
45, health 40 → 60, exactly the port's giant rat (the save keeps base attack and defense, not their totals
with the attributes' bonus). With every creature's numbers now
confirmed, the larder fight is still lost in simulation unless rats bite only about every 3 s (won 65%).
What remains is the engine's pacing: simple creatures run the AI's light round (`AI_DetermineCombatRound_Light`:
a random enemy from the threat list, one `CommandAttack`), and how often that command lands a bite is
decided inside the engine, so neither the scripts, the tables nor a save show it. The fight's shape (rats
running in from the larder's corners) plays a part too. That needs the original running: counted by hand,
or from a recording of the fight.

**From recordings of the original** (2026-10-24; two YouTube playthroughs of the fight, "Let's Play Dragon
Age: Origins Episode 2 - Defending The Pantry" by Zamidge and "Origin Quest (Human Noble) 1/3" by
DragonAgez, read by a video model since YouTube refused a download): a rat bites about every 2 s (5 bites in
10 s, in both), a bite takes 2-3 off the player, the player's hits on a rat read 12-13 in the first; the
fight lasts 20-35 s, rats run in in waves, and the player ends it 15-20% down, Gilmore and the mabari 5-10%,
nobody falls. The model's exact counts were not reliable (rats killed and damage numbers changed between
passes over the same clip), so only what the passes agree on is used: an animal's attack round is now at
least 2 s (`stats.attack_interval`; the rat 2.0, the mabari 2.07). With it the simulator still loses the
fight: it has all six rats biting from the first second, where the recordings show far less damage taken
than that, so fewer rats bite at any moment in the game (they arrive in waves and run in from the corners).
That is the fight's shape, which needs positions; a playtest in Unreal measures it.

What the game's files say about a rat's rhythm (2026-10-25): its bite (`c_rat.attk_v1.ani`) lasts 0.63 s with
the impact at 0.40 s (`.evt`, event type 1; the mabari's at 0.70 of 2.3 s); its combat stance between moves
(`pause`, `c_rat.pause.ani`) 0.97 s; `anim_combat.gda` only chains the moves. Each `CommandAttack` makes one
swing (`Combat_HandleCommandAttack` returns after it, setting a duration only for humanoids); on completion
`rules_core` runs the AI round at once (`AI_DetermineCombatRound_Light`: a random enemy, the next
`CommandAttack`, timeout 5 s, 1 s the first time). What the engine plays between two commands is compiled into
`DAOrigins.exe`, which names no combat timing setting; its code section is encrypted by Steam's DRM
wrapper (a `.bind` section, entropy 8.0 across `.text`), and decrypting it would be circumventing copy
protection, so it is not analysed. The toolset wiki's engine pages (`SetAttackDuration`, the event editor's
event types, the blend tree editor) document no default either; a rat's bite carries only an impact event
(0.40 s) and a sound, no "animation done" or blend marker. A bite and a stance (0.63 + 0.97 = 1.6 s) is the
reading the files allow, and fits the recordings' 5 bites in 10 s; the export keeps the 2 s round.

**The game's timing in Unreal and the fight's shape** (2026-10-25). `combat_rules.py pace`: every creature
attacks every `BP_DlgNPC.Interval` seconds (the export's `NpcInterval`, given by `GiveNpcRules` →
`SetInterval`; 2 s by default) in `Bite` and `PartyFight`, and the player swings at most every `PInterval`
(`PlayerStats[12]`, `SetPlayerPace`: 1.9 s with the longsword and shield). Measuring this found a bug that
had hidden the player from every bite since hostiles began fighting the party: `StrikeFoe` cast its foe to
`BP_DlgNPC` and branched on the result, but a failed impure cast leaves by its own unwired exit, so a bite on
the player did nothing; it now compares the foe with the player first and casts only on the other branch
(`StrikeNpcFoe`).

`py playtest.py larder day` plays the whole fight as the game stages it (Gilmore and the mabari join, the first
six rats wake, each death brings the next) and samples it every few seconds: rats biting (alive, visible, within
1.5 m of their foe), health, who is down. With the game's numbers and real positions, 4.8 rats bite at once on
average (6 at most): what the simulator assumed. The player went from 115 to 34 in the first 12 s and fell at
about 40 s, the mabari at 55 s, Gilmore last; the level reloaded. In the recordings the player ends the fight
15-20% down, roughly an eighth of the bites landing here. Nothing in the game's data accounts for that (every
creature's numbers are confirmed against a save), so the next evidence has to be exact: a recording of the
original's fight that can be counted frame by frame (the YouTube readings were too loose), or the owner's own
count in the original.

**Solved: the larder's rats are one-shot creatures** (2026-10-25). A provisional tuning (one attacker per
target, animals every 3 s) briefly stood in for the answer; then the owner's own screen recording of the
original's fight showed a full-health rat dying from a single 5-damage hit. The scripts say why:
`AS_InitCreature` never scales a creature whose appearance has `OneShotKills` (`IsOneShotKillCreature`;
`apr_base`: "Squirel", "Rat, Large", "Rat, Small"); it only gives it level 1 and 1 health. So a giant rat
keeps no attributes, attack, defense, critical chance or damage bonus of its own (they are never set), only
its natural bite (3 damage, armour penetration 2, critical chance 1.5) and its hide. Every hit that lands
kills it, and its own attack (0 + 54 against the player's 51.5 defense) lands about one bite in forty, or
one in thirteen from behind. `stats.stats(..., one_shot=True)` and `stats.is_one_shot` do this; the
export applies it to such appearances.

With it the provisional tuning is undone: the animal round is 2 s again (`stats.ANIMAL_ROUND`, the
recordings' rhythm), the simulator has no cap by default (`simulate.SLOTS` = 0), and Unreal's
`BP_PlotManager.Slots` is 99 (the cap stays available: `combat_rules.py slots`). Simulated (2,000 fights):
won every time in about 11 s with every party hit a kill, the party losing about 1% of its health; in the
game the rats' running in and the fighters' moving make it longer, as in the recordings.

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
