# Combat design: the original's rules, Combat Tweaks' balance, our fixes

Decided 2026-10-24 with the owner: combat plays exactly like Dragon Age: Origins (real-time with
pause, a party of four, tactics, the same attributes, classes and talents), but better balanced. The
balance base is the community's best-known rebalance, **Combat Tweaks** (v3.23, Dennis Lee, Nexus
mod 354), plus Awakening's specializations in the main campaign, plus our own pass on the classes
that stay too weak or too strong (Shapeshifter first). This page is the plan; `docs/COMBAT.md`
describes what is built.

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

Our prototype already follows the to-hit and damage rules and exports armour per creature
(`docs/COMBAT.md`); it lacks attributes' derived stats, abilities, effects, threat, pause and tactics.

## 2. Combat Tweaks as the balance base

Combat Tweaks keeps vanilla play and changes numbers and fixes bugs; we take its design as our
balance (its public tweak list; its full ReadMe has every number). Its themes:

- **Fixes to vanilla bugs**: spellpower wrongly taking a -10 modifier in many calculations, Shock
  never electrifying, Virulent Walking Bomb not spreading, Glyph of Neutralization only spell-warding,
  Cone of Cold's freeze never resisted, Crow Poison's stun never applying, Soldier's Bane and Magebane
  refilling the target, slow and paralyse runes not scaling with rank, +healing received items doing
  nothing, item set bonuses lost when party members change.
- **A smoother talent curve and obscure talents made worthwhile**: dual weapon, archery and duelist
  lines reworked (resistance checks, innate attack bonuses, cooldowns, rank effects), two-handed
  weapons getting 65-90% of the strength bonus instead of 50-75%, daggers and shortbows 165% on
  criticals, Combat Tactics giving 1/2/3/4 slots and tactic slots growing with level.
- **Threat reworked**: every ability's threat revised, a modifier range of -50% to +200%, shield
  attacks as single-target taunts, fear clearing the threat table.
- **Status effects**: knockdown -25 defense, fear -10 defense and a 20% chance to wake when hit, root
  only 50% likely to break on damage.
- **Poisons, coatings, bombs and runes**: shared cooldowns, power scaling with Poison-Making rank,
  each element doing something distinct (fire extra damage, cold freezes, electricity drains stamina,
  nature lowers armour, spirit lowers resistances).
- **Shapeshifting**: enchantments work on spider and bear, forms no longer drop when out of mana, a
  stronger Flying Swarm with Master Shapeshifter.
- **Optional creature scaling**: enemies' attributes, health and damage scale harder with rank.

What we do not take: Combat Tweaks' companion mods that bring in content from outside Dragon Age
(JX – Dragon Age Extended adds Baldur's Gate II spells, Final Fantasy jobs and Magic: The Gathering
classes). Classes stay Dragon Age's.

## 3. Classes and specializations

- Warrior, Rogue, Mage, as in Origins, with their four specializations each: Berserker, Champion,
  Reaver, Templar; Assassin, Bard, Duelist, Ranger; Arcane Warrior, Blood Mage, Shapeshifter, Spirit
  Healer.
- **Awakening's six in the main campaign**: Guardian and Spirit Warrior; Legionnaire Scout and
  Shadow; Battlemage and Keeper. Their rules are already in the install's scripts (the "GXA"
  overrides in `combat_damage_h`, for instance) and their abilities in its tables, so they are read
  like the rest. Awakening's third specialization slot (level 22) comes with them.
- **Our balance pass**, after Combat Tweaks, on what the community still finds off:
  - **Shapeshifter (too weak)**: forms scale with spellpower and level instead of fixed stats, keep
    a share of armour and attributes from gear, form talents get proper cooldowns and damage, and
    changing form is fast. Target: a shapeshifter in bear form tanks like a warrior of the same
    level, in spider form controls like a rogue.
  - **Too strong**: Arcane Warrior (Combat Magic turning magic into attack, heavy armour without
    fatigue), Blood Mage (Blood Magic's health-for-mana loop), and the mage crowd-control combos
    (Force Field, Crushing Prison, Mana Clash) are measured first and toned down only where they
    trivialise fights.
- Balance is measured, not argued: see 5.

## 4. How it is built (once, for every area)

- **Data from the game**: attributes per class and level (`cla_*` tables), every ability
  (`ABI_base` and the Awakening tables: cost, upkeep, cooldown, range, area, effects), items' stats,
  creatures' stats (already exported), threat values. `daotools` exports them; Combat Tweaks' changes
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
  (7) Combat Tweaks' and our balance overrides.

## 5. Balance by simulation

A headless combat simulator in `daotools` uses the same formulas as Unreal (one implementation of the
rules, tested): it runs each class and specialization build, at levels 1 to 25, against the game's
encounters (the castle's rats and Howe's men first, then Ostagar's darkspawn) many times and reports
damage per second, time to kill, damage taken and how often the party dies. Vanilla, Combat Tweaks
and our pass are compared side by side, and a change ships when it brings an outlier into line
without moving the rest.

## Sources

- Combat Tweaks v3.23 (Dennis Lee): https://www.nexusmods.com/dragonage/mods/354
- JX – Dragon Age Extended (Jake Zahn), built on Combat Tweaks: https://www.nexusmods.com/dragonage/mods/3316
- The game's scripts in the install (`extracted/scripts/src`): `combat_h`, `combat_damage_h`,
  `attributes_h`, `ai_threat_h`, `core_difficulty_h`.
