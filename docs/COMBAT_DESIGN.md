# Combat design: the original's rules, Dragon Age Reborn's balance, our fixes

Decided 2026-10-24 with the owner: combat plays exactly like Dragon Age: Origins (real-time with
pause, a party of four, tactics, the same attributes, classes and talents), but better balanced and
fresher. The balance base is **Dragon Age Reborn** (v1.1.2, Tyragon, Nexus mod 5173): it reworks about
130 abilities of Origins and Awakening so that every specialization is viable and builds diversify
(shapeshifter tanks, sword-and-shield damage dealers, warrior and crossbow archers), with nerfs as well as
buffs, its changes applying to enemies too, and every change documented in detail. Awakening's
specializations come with it into the main campaign. Combat Tweaks (v3.23, Dennis Lee, Nexus mod 354),
the older and more conservative rebalance, stays a reference for vanilla bug fixes. This page is the
plan; `docs/COMBAT.md` describes what is built.

Dragon Age Reborn's rules are imported as the starting point (the owner's decision for this
non-commercial remake); its files stay out of the repository and are read from the install
(`docs/COMBAT_BALANCE.md`, which also says how its numbers are read).

## 1. The original's rules (kept as they are)

From the game's own scripts (`extracted/scripts/src`, BioWare's source):

- **To hit** (`combat_h` `Combat_GetAttackResult`): hit if `rand(100) < attack + 50 + flanking -
  range penalty - defense`. Attack is the creature's attack rating plus the weapon's attack stat plus
  the difficulty's bonus; defense adds missile deflection against ranged attacks. Staves always hit;
  every metre beyond the weapon's optimum range is -1. Displacement can turn any attack into a miss.
- **Criticals**: rolled separately against the critical chance (melee or ranged), raised by flanking
  (x1 + flanking/5) and Bravery (+3.5 per enemy beyond two in melee); attacks out of stealth, against
  a Death Hex, or under an autocrit effect always threaten a critical; Dual Weapon Double Strike and
  Rapid Shot never do; critical-immune creatures cannot be crit. Misdirection Hex turns hits into
  misses and criticals into hits.
- **Flanking** (`Combat_GetFlankingBonus`): up to +15 attack (+20 with Combat Movement) for
  attacking from behind within the attacker's flanking angle; rogues get all of it, everyone else
  half. Shield Tactics (with a shield) and flank immunity cancel it; Shield Block covers the left.
- **Backstab**: a rogue's melee hit while flanking (or Coup de Grace on a stunned or paralysed
  target) is an automatic critical, plus Exploit Weakness (cunning/3).
- **Damage** (`combat_damage_h` `Combat_Damage_GetAttackDamage`): weapon damage + attribute bonus x
  the weapon's attribute factor + difficulty bonus; x the critical modifier on a critical; minus
  (armour - armour penetration), armour rolled 70% fixed / 30% random; plus flat damage bonuses and
  talent bonuses (Blood Frenzy, Shattering Blows); x the creature rank's damage scale when above the
  threshold; at least 1. Two-handed armour penetration +25% with Strong.
- **Everything else stays**: stamina and mana with combat and exploration regeneration, sustained
  (modal) abilities with upkeep and cooldowns, threat (`ai_threat_h`), tactics slots, friendly fire on
  hard and nightmare, the difficulty settings (`core_difficulty_h`), creature ranks and area level
  scaling, death and injuries, and **real-time with pause**: pausing freezes the world while orders
  (move, attack, ability) can still be queued for each party member.

Stage 1 is built (`docs/COMBAT.md`, "Stats" and "Rules"): the attributes' derived stats, to-hit,
criticals, flanking, armour and penetration, the damage bonus and rank scaling, with Dragon Age Reborn's
tables, and a game over. Stage 2 is under way: stamina, costs, cooldowns, upkeep and the warrior's and
rogue's basic talents in `daotools` and the simulator (`docs/COMBAT.md`, "Talents"); Unreal next. Still to
come: spells and effects, threat, pause and tactics.

## 2. Dragon Age Reborn as the balance base

Dragon Age Reborn keeps the original's rules and reworks the abilities (its documentation lists every
change; its source scripts are published). Its main lines, from its description:

- **Every specialization usable in melee and at range**, crossbow archery made real, warriors decent
  archers.
- **Tanks and damage dealers from unexpected builds**: shapeshifters, arcane warriors and two-handed
  warriors can tank; weapon-and-shield warriors can deal damage.
- **No must-have or must-avoid abilities**: talent trees allow several approaches by attribute, so
  builds and itemisation differ; repetitive or useless abilities are replaced by new ones.
- **Examples**: Below the Belt strips sustained abilities and silences for 10 s; Destroyer turns
  excess armour penetration into crushing criticals with an injury; Curse of Mortality becomes Life
  Shift (swap health percentages with an ally); Shield Defense, Shield Wall and Shield Cover become
  stances against melee, ranged or mixed foes; Crippling Shot knocks down a target rooted by Pinning
  Shot; shapeshifting is instant and no longer cancels sustained spells, bears are dexterity tanks
  with an area taunt and spiders strength damage dealers; Arcane Warrior's 50% fatigue becomes a
  spellpower penalty, with a taunt for shield users; Captivating Song becomes an area taunt that slows
  and stuns those who hit the bard; most archery talents fire at auto-attack speed; Drain Life and
  Death Magic bypass Blood Magic's healing penalty.
- **Difficulty adjusted** to the higher power, and **bugs purged** from abilities, items, combat and
  stats (Swift Salve, Magebane, Soldier's Bane, ranged aim speed, +healing on items among them).

What we do not take: content from outside Dragon Age (JX – Dragon Age Extended, built on Combat
Tweaks, adds Baldur's Gate II spells, Final Fantasy jobs and Magic: The Gathering classes).

## 3. Classes and specializations

- Warrior, Rogue, Mage, as in Origins, with their four specializations each: Berserker, Champion,
  Reaver, Templar; Assassin, Bard, Duelist, Ranger; Arcane Warrior, Blood Mage, Shapeshifter, Spirit
  Healer.
- **Awakening's six in the main campaign**: Guardian and Spirit Warrior; Legionnaire Scout and
  Shadow; Battlemage and Keeper. Their rules are already in the install's scripts (the "GXA"
  overrides in `combat_damage_h`, for instance) and their abilities in its tables, so they are read
  like the rest. Awakening's third specialization slot (level 22) comes with them.
- **Our balance pass**, after Dragon Age Reborn, only where measurements still show an outlier:
  Reborn already makes the Shapeshifter a tank or a damage dealer and turns Arcane Warrior's fatigue
  into a spellpower penalty; Blood Mage loops and the mage crowd-control combos (Force Field,
  Crushing Prison, Mana Clash) are measured first.
- Balance is measured, not argued: see 5.

## 4. How it is built (once, for every area)

- **Data from the game**: attributes per class and level (`cla_*` tables), every ability
  (`ABI_base` and the Awakening tables: cost, upkeep, cooldown, range, area, effects), items' stats,
  creatures' stats (already exported), threat values. `daotools` exports them; Dragon Age Reborn's changes
  and ours are applied as a separate, readable overrides file on top (`docs/COMBAT_BALANCE.md` will
  list each one and why), so the original numbers stay visible.
- **Unreal's Gameplay Ability System**: attributes as an attribute set (strength, dexterity,
  willpower, magic, cunning, constitution and the derived attack, defense, health, mana, stamina,
  armour, armour penetration, spellpower, resistances), each ability as a data-driven ability, each
  effect (stun, knockdown, root, slow, fear, sleep, paralyse, freeze, damage over time, sustained
  upkeep) as a gameplay effect with tags, so a status works the same for everyone.
- **Pause and tactics**: pause sets the world's time dilation to zero while the UI queues orders;
  tactics are condition/action rows read every half second, as the original.
- **Stages, small and testable**: (1) attributes and derived stats, armour in hits, a game over, the
  one-hit kills off; (2) stamina, mana, cooldowns and the warrior's and rogue's basic talents;
  (3) spells and status effects; (4) threat and enemy AI; (5) specializations; (6) tactics;
  (7) Dragon Age Reborn's and our balance overrides.

## 5. Balance by simulation

A headless combat simulator in `daotools` uses the same formulas as Unreal (one implementation of the
rules, tested): it runs each class and specialization build, at levels 1 to 25, against the game's
encounters (the castle's rats and Howe's men first, then Ostagar's darkspawn) many times and reports
damage per second, time to kill, damage taken and how often the party dies. Vanilla, Dragon Age Reborn
and our pass are compared side by side, and a change ships when it brings an outlier into line
without moving the rest.

The first version is built (`daotools/simulate.py`, `daotools unreal simulate`; `docs/COMBAT.md`,
"Balance simulator"): the stage 1 rules and the prototype's fight, from an area export. Builds, levels and
abilities come with the later stages.

## Sources

- Dragon Age Reborn v1.1.2 (Tyragon): https://www.nexusmods.com/dragonage/mods/5173
- Combat Tweaks v3.23 (Dennis Lee), reference for bug fixes: https://www.nexusmods.com/dragonage/mods/354
- JX – Dragon Age Extended (Jake Zahn), built on Combat Tweaks: https://www.nexusmods.com/dragonage/mods/3316
- The game's scripts in the install (`extracted/scripts/src`): `combat_h`, `combat_damage_h`,
  `attributes_h`, `ai_threat_h`, `core_difficulty_h`.
