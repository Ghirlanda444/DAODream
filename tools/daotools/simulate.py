"""A headless fight between the party and its foes, many times over, with the game's hit rules (stats.py: the
same rules BP_PlotManager plays in Unreal), to measure balance without the editor (docs/COMBAT_DESIGN.md, 5).

The fighters come from an area export (`daotools unreal area`): the player from PlayerStats, everyone else by tag
from the Npc* arrays (health, attack, defense, damage, rank scale, and NpcRules: armour, armour penetration,
critical chance, most flanking, damage bonus). Exports with and without a rebalance mod's tables
(`--mod-tables`) compare the two.

The fight follows the Unreal prototype (docs/COMBAT.md), not positions: everyone is engaged from the start.
Each fighter strikes on its own clock: the game's attack timing from the export (a humanoid's weapon and wield
style, an animal's attack animations; stats.attack_interval), else INTERVAL (the prototype: the player once a
second, party members every 1.5 s, hostiles every 2 s). A hostile goes for a standing member of the party (the nearest, in the game; here one at random,
kept until it falls); a party member goes for the foe the fewest of its side are fighting. With flanking on, an
attacker its target is not fighting stands behind it and gets its full flanking bonus. Foes come in waves: the
first `wave` are in the fight and each death brings the next one in (the larder's rats: each of the first six
brings in a seventh to twelfth, each of those a thirteenth to eighteenth). A party member at 0 health falls; the
fight is lost when the whole party is down, won when no foe is left.

Talents (stage 2, abilities.py): the player has a stamina pool that regenerates REGEN_COMBAT a second, and uses its
talents from the export's PlayerTalents in their order, one in place of an attack whenever one is off cooldown and
affordable (cost raised by fatigue): a sustained one is switched on (its upkeep lowers the pool's maximum, its
fatigue raises costs, its bonuses count while on), a buff is taken when not already on, a stun or knockdown goes to
a target not already down (stuns rank-adjusted and longer for each missing party member; a knockdown can be
resisted), an attack talent rolls with its attack bonus. A stunned or knocked down foe loses its turns. The
threat talents and Feign Death are not used (stage 4). Passives: Bravery's critical chance per foe on the player
past two, Death Blow's stamina from kills, Evasion's misses; a rogue backstabs (critical damage) when flanking, or
a stunned target with Coup de Grace.

Threat (stage 4, threat.py): a foe coming into the fight sees every standing party member (their seen threat:
NpcStatus, PlayerStats[19]) and fights the one it hates most, switching by its switch timer; every attack on it
adds threat for the attacker (damage as a percentage of its health, x0.8 from a rogue, x2 with Threaten on), a
fallen party member is forgotten. The player uses Taunt when a foe is on someone else (+310 on every foe, which
may switch at once) and Disengage when two or more are on it (-99 on every foe). `use_threat` False brings back
the prototype's rule (a foe keeps a random standing party member).

Enemy talents (stage 4, tactics.py): a foe with talents (NpcTalents) runs its tactics table (NpcTactics) on each
of its turns and uses the talent the first firing row names, on itself or on its target, else attacks. The talents'
effects are the same for everyone: Shield Pummel strikes three times and stuns, Sunder Weapon strikes twice at 60%
and takes the target's attack away for 6 s, Sunder Armor strikes twice at 70% (and, as Reborn wrote it, adds 30% to
the target's armour), Critical Strike kills a target at 25% health or less, Pommel Strike
knocks down, Indomitable and Precise Striking are sustained, Below the Belt keeps the player from talents for 10 s.
A debuff on a party member is not lengthened for missing party members and party members resist nothing (their
physical resistance is 0).

Ranged (stage 4b): a foe with a bow (NpcStatus' optimum range) shoots from RANGED_DISTANCE metres: -1 attack a metre
past its bow's optimum range (none at 10 m), the target's missile shield added to its defense, no flanking or
backstab; its talents' aiming time adds to its shots' interval; it may switch target any time (threat). Pinning
Shot's root changes nothing here (nobody moves); Shattering Shot takes 10 armour for 20 s and knocks down.

The party (stage 6): a party member other than the player with talents and a tactics table (the Teyrna, the dog)
takes its combat rounds as a foe does (tactics.choose), against its own target; the Teyrna shoots from
RANGED_DISTANCE like an archer. The dogs' talents (abilities.EFFECTS): Growl takes 15 defense for 30 s unless
resisted, Charge knocks down, Shred is a critical whose bleed is dealt at once here, Overwhelm pins for 2 s with
two bites that land, Mabari Howl stuns every foe not a boss for 5 s (nobody is out of its 10 m here).

Spells (stage 3): a mage's staff bolt always hits, for the staff's damage and part of his spellpower, without
armour, criticals or the damage bonus. Lightning and Shock deal (100 + spellpower) x their factor, no roll, no
armour (nobody here resists electricity). Shock's cone and Mind Blast's 5 m catch the target and everyone fighting
the caster at close quarters (no geometry here); Mind Blast stuns them 3 s, rank-adjusted. "Target at short range"
holds for a caster someone is on in melee.
"""

from __future__ import annotations

import fnmatch
import random
import statistics
from dataclasses import dataclass, field

from . import abilities, stats, tactics as ai, threat as th

FORMAT = "DAODream.Simulation 1"
PLAYER = "player"
# Seconds between attacks: the export's (NpcInterval, PlayerStats[12]: the game's timing) when it has them,
# else the Unreal prototype's fixed ones; "export": False always uses the fixed ones.
INTERVAL = {"player": 1.0, "party": 1.5, "foe": 2.0, "export": True}
TIME_LIMIT = 600.0
RULES = ("Armour", "Penetration", "Crit", "Flanking", "DamageBonus")  # area.RULES
SLOTS = 0  # foes attacking the same party member at once (0: no limit; BP_PlotManager.Slots in Unreal)
RANGED_DISTANCE = 10.0  # m an archer shoots from (in the castle's halls and corridors)


@dataclass(eq=False)  # by identity: fighters key threat tables
class Fighter:
    tag: str
    side: str  # "party" or "foe"
    health: float
    attack: float
    defense: float
    damage: tuple[float, float]
    scale: float = 1.0
    threshold: float = 0.0
    armour: float = 0.0
    penetration: float = 0.0
    crit: float = 0.0
    flanking: float = 0.0
    bonus: float = 0.0
    interval: float = 2.0
    stamina: float = 0.0
    fatigue: float = 0.0
    level: float = 1.0
    displacement: float = 0.0
    rogue: bool = False
    offhand: tuple[float, float] = (0.0, 0.0)
    talents: list = field(default_factory=list)  # TALENT_FIELDS dicts
    passives: tuple = ()
    duration_scale: float = 1.0  # NpcStatus: the rank's effect duration scale
    resist: float = 0.0  # NpcStatus: percent it resists the player's knockdown
    seen: float = 15.0  # the threat it draws when seen (NpcStatus, PlayerStats[19]; threat.seen_threat)
    threat: "th.Threat | None" = None  # a foe's threat table
    max_health: float = field(init=False)
    pool: float = field(init=False)  # the stamina pool's maximum, less upkeep
    down: bool = False
    target: "Fighter | None" = None
    next_attack: float = 0.0
    dealt: float = 0.0
    disabled: float = 0.0  # stunned or knocked down until
    ready: dict = field(default_factory=dict)  # talent id -> off cooldown at
    buffs: list = field(default_factory=list)  # (until, talent row)
    sustained: list = field(default_factory=list)
    regen_at: float = 0.0
    used: dict = field(default_factory=dict)  # talent id -> uses
    tactics: list = field(default_factory=list)  # a foe's tactics rows (tactics.FIELDS dicts)
    boss: bool = False
    range: float = 0.0  # its bow's optimum range (0: melee)
    missile: float = 0.0  # missile shield: defense against arrows (a shield's MissileDeflection)
    disarm: tuple[float, float] = (0.0, 0.0)  # (until, attack taken away): Sunder Weapon
    spellpower: float = 0.0  # NpcSpell
    staff: bool = False  # NpcSpell: its bolt always hits (stats.is_staff)
    locked: float = 0.0  # no talents until (Below the Belt)

    def __post_init__(self):
        self.max_health = self.health
        self.pool = self.stamina

    def own(self, key: str, now: float) -> float:
        """What its buffs and sustained talents add to TALENT_FIELDS' key."""
        return sum(r.get(key, 0.0) for until, r in self.buffs if until > now) + \
            sum(r.get(key, 0.0) for r in self.sustained)


def _rules(values: list, i: int) -> dict:
    return dict(zip(RULES, values[i * len(RULES):(i + 1) * len(RULES)])) if values else {}


def player_fighter(area: dict, talents: bool = True) -> Fighter:
    """PlayerStats (area.player_stats): health, attack, defense, damage min and max, threshold, RULES, stamina,
    seconds between attacks (INTERVAL["player"] when the export has none), fatigue, level, displacement, rogue,
    the shield's damage; PlayerTalents and PlayerPassives unless `talents` is False."""
    p = list(area["PlayerStats"]) + [0.0] * 10
    r = dict(zip(RULES, p[6:11]))
    f = Fighter(PLAYER, "party", p[0], p[1], p[2], (p[3], p[4]), 1.0, p[5], r["Armour"], r["Penetration"], r["Crit"],
                r["Flanking"], r["DamageBonus"],
                p[12] if p[12] and INTERVAL.get("export", True) else INTERVAL["player"], stamina=p[11], fatigue=p[13],
                level=p[14] or 1.0, displacement=p[15], rogue=bool(p[16]), offhand=(p[17], p[18]),
                seen=p[19] or 15.0)
    f.missile = p[20]
    if talents:
        n = len(abilities.TALENT_FIELDS)
        rows = area.get("PlayerTalents") or []
        f.talents = [dict(zip(abilities.TALENT_FIELDS, rows[k:k + n])) for k in range(0, len(rows), n)]
        f.passives = tuple(int(x) for x in area.get("PlayerPassives") or [])
    return f


def npc_fighter(area: dict, i: int, side: str) -> Fighter:
    r = _rules(area.get("NpcRules") or [], i)
    threshold = area["PlayerStats"][5] if area.get("PlayerStats") else 0.0
    n = len(area.get("NpcStatus") or []) // max(1, len(area["NpcTags"]))  # 11 (3, 5 and 9 in older exports)
    status = list((area.get("NpcStatus") or [])[n * i:n * i + n]) if n else []
    status += [1.0, 1.0, 0.0, 15.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0][len(status):]
    f = Fighter(area["NpcTags"][i], side, area["NpcHealth"][i], area["NpcAttack"][i], area["NpcDefense"][i],
                (area["NpcDamage"][2 * i], area["NpcDamage"][2 * i + 1]), area["NpcDamageScale"][i], threshold,
                r.get("Armour", 0.0), r.get("Penetration", 0.0), r.get("Crit", 0.0), r.get("Flanking", 0.0),
                r.get("DamageBonus", 0.0), _interval(area, i, side), level=status[0], duration_scale=status[1],
                resist=status[2], seen=status[3], rogue=bool(status[4]), stamina=status[5], fatigue=status[6],
                offhand=(status[7], status[8]), range=status[9], missile=status[10])
    spell = (area.get("NpcSpell") or [])[2 * i:2 * i + 2]
    if len(spell) == 2:
        f.spellpower, f.staff = spell[0], bool(spell[1])
    k, t = len(abilities.TALENT_FIELDS), ai.MAX_TALENTS
    rows = (area.get("NpcTalents") or [])[i * k * t:(i + 1) * k * t]
    f.talents = [dict(zip(abilities.TALENT_FIELDS, rows[j:j + k])) for j in range(0, len(rows), k) if rows[j]]
    k, t = len(ai.FIELDS), ai.MAX_TACTICS
    rows = (area.get("NpcTactics") or [])[i * k * t:(i + 1) * k * t]
    f.tactics = [dict(zip(ai.FIELDS, rows[j:j + k])) for j in range(0, len(rows), k) if rows[j + 5] > 0]
    return f


def _interval(area: dict, i: int, side: str) -> float:
    """NpcInterval (the game's attack timing, stats.attack_interval) when the export has it and INTERVAL["export"]
    is not False; else the prototype's fixed timing."""
    found = area.get("NpcInterval") or []
    if i < len(found) and INTERVAL.get("export", True):
        return found[i]
    return INTERVAL["party" if side == "party" else "foe"]


def fighters(area: dict, party: list[str], foes: list[str],
             talents: bool = True) -> tuple[list[Fighter], list[Fighter]]:
    """The player and the party members named by tag; the foes matching the patterns (fnmatch), in tag order.
    A tag the area has more than once counts each creature. `talents` False leaves the player's out."""
    tags = area["NpcTags"]
    ours = [player_fighter(area, talents)] + [npc_fighter(area, i, "party") for t in party for i, x in enumerate(tags) if x == t]
    picked = sorted((t, i) for i, t in enumerate(tags) if any(fnmatch.fnmatch(t, p) for p in foes))
    return ours, [npc_fighter(area, i, "foe") for _, i in picked]


def strike(rng: random.Random, a: Fighter, d: Fighter, flanking: float = 0.0, now: float = 0.0,
           bonus: float = 0.0, offhand: bool = False, extra_crit: float = 0.0,
           talent: bool = False, mul: float = 1.0, sure: bool = False,
           force_crit: bool | None = None) -> tuple[float | None, bool]:
    """One attack: (damage, critical), damage None for a miss. ResolveHit, RollHit and Mitigate in Unreal.
    `bonus`: a talent's attack bonus; `offhand`: with the shield's damage; `extra_crit`: Bravery's. The target's
    displacement (Evasion) makes it miss outright first. A rogue's plain attack on a flanked (or, with Coup de
    Grace, stunned) target that hits is a backstab: critical damage. `mul`: the talent's damage multiplier; `sure`:
    a blow that lands whatever the roll (Shield Pummel's shield blows); `force_crit`: True or False decides the
    critical (Shred's, Overwhelm's bites) instead of the roll. Indomitable's defense and armour count for
    the defender, its damage scale for the attacker; a disarmed attacker (Sunder Weapon) lost its attack rating."""
    if d.displacement and rng.random() * 100.0 < d.displacement and not sure:
        return None, False
    if a.staff and not talent:  # Combat_GetAttackResult: staves always hit; their own damage, no armour or critical
        return rng.uniform(*a.damage), False
    ranged = a.range > 0
    if ranged:
        flanking = 0.0
    crit = rng.random() * 100.0 < stats.crit_chance(a.crit + a.own("Crit", now) + extra_crit, flanking)
    attack = a.attack + a.own("Attack", now) + bonus - (a.disarm[1] if a.disarm[0] > now else 0.0)
    defense = d.defense + d.own("Defense", now)
    if ranged:  # Combat_GetAttackResult: the range penalty, the target's missile shield
        attack -= stats.range_penalty(RANGED_DISTANCE, a.range)
        defense += d.missile
    if not sure and rng.random() * 100.0 >= stats.hit_chance(attack, defense, flanking):
        return None, False
    if a.rogue and not talent and not ranged and (flanking > 0 or abilities.COUP_DE_GRACE in a.passives and d.disabled > now):
        crit = True  # Combat_CheckBackstab: COMBAT_RESULT_BACKSTAB, critical damage
    if force_crit is not None:
        crit = force_crit
    rolled = rng.uniform(*(a.offhand if offhand else a.damage)) * mul * (1.0 + a.own("DamageScale", now))
    return stats.hit_damage(rolled, crit=crit, armour=d.armour + d.own("Armour", now), armour_roll=rng.random(),
                            penetration=a.penetration + a.own("Penetration", now),
                            bonus=a.bonus + a.own("DamageBonus", now), scale=a.scale,
                            threshold=a.threshold), crit


def regen(f: Fighter, now: float) -> None:
    f.stamina = min(f.pool, f.stamina + abilities.REGEN_COMBAT * (now - f.regen_at))
    f.regen_at = now


def use_talent(rng: random.Random, a: Fighter, d: Fighter, now: float, party_size: int, flanking: float,
               extra_crit: float = 0.0, foes: list | None = None) -> tuple[bool, float | None, bool]:
    """The first of `a`'s talents it can use now (in PlayerTalents' order), used on `d`: (used, damage, critical),
    damage None when nothing struck. `foes`: the live foes with threat tables (Taunt, Disengage; none: the threat
    talents are not used)."""
    regen(a, now)
    if a.locked > now:  # Below the Belt
        return False, None, False
    for r in a.talents:
        i = int(r["Id"])
        if i == 3023 or a.ready.get(i, 0.0) > now:  # Feign Death: not used here
            continue
        if i in abilities.THREAT:
            if not foes or not _wants(i, a, foes):
                continue
            cost = abilities.ability_cost(r["Cost"], a.fatigue)
            if int(r["Use"]) != abilities.SUSTAINED:
                if a.stamina < cost:
                    continue
                a.stamina -= cost
                a.ready[i] = now + r["Cooldown"]
                a.used[i] = a.used.get(i, 0) + 1
                for f in foes:
                    f.threat.change(a, th.talent_threat(i), now, rng, _alive, _health)
                    if i == 3041:
                        f.threat.taunted()
                        f.threat.change(None, 0.0, now, rng, _alive, _health)
                return True, None, False
        if not affordable(a, d, r, now):
            continue
        damage, crit = perform(rng, a, d, r, now, party_size, flanking, extra_crit)
        return True, damage, crit
    return False, None, False


def affordable(a: Fighter, d: Fighter | None, r: dict, now: float) -> bool:
    """`a` can use talent row `r` on `d` now: off cooldown, the stamina (or for a sustained one, room in the pool
    for its upkeep, and not on already), a buff not already running, a target not already down for a stun or
    knockdown."""
    i = int(r["Id"])
    if a.ready.get(i, 0.0) > now:
        return False
    if int(r["Use"]) == abilities.SUSTAINED:
        return r not in a.sustained and a.pool - r["Upkeep"] >= 0
    disable = abilities.DISABLES.get(i)
    buff = not disable and i not in _STRIKES
    if a.stamina < abilities.ability_cost(r["Cost"], a.fatigue):
        return False
    if disable and d is not None and d.disabled > now:
        return False
    return not (buff and any(b is r and until > now for until, b in a.buffs))


_STRIKES = (3, 4, 3025, 3026, 617, 1, 803, 3072, 90016, 90047, 90015)  # talents that strike their target (the rest of the non-sustained: buffs, 603)


def perform(rng: random.Random, a: Fighter, d: Fighter, r: dict, now: float, party_size: int, flanking: float = 0.0,
            extra_crit: float = 0.0, enemies: list | None = None) -> tuple[float | None, bool]:
    """Pay for talent row `r` and apply it (abilities.EFFECTS): (damage dealt, critical), damage None when nothing
    was struck. `enemies`: `a`'s standing enemies (Mabari Howl's)."""
    i = int(r["Id"])
    e = abilities.EFFECTS.get(i, {})
    a.ready[i] = now + r["Cooldown"]
    a.used[i] = a.used.get(i, 0) + 1
    if int(r["Use"]) == abilities.SUSTAINED:
        a.sustained.append(r)
        a.pool -= r["Upkeep"]
        a.stamina = min(a.stamina, a.pool)
        a.fatigue += r["Fatigue"]
        return None, False
    a.stamina -= abilities.ability_cost(r["Cost"], a.fatigue)
    party = d.side == "party"

    def seconds(base):  # GetRankAdjustedEffectDuration
        if not party and base >= 1.0:
            base += max(0, abilities.PARTY_SLOTS - party_size)
        return base * d.duration_scale

    def resisted():
        return rng.random() * 100.0 < (0.0 if party else d.resist)

    if i == 603:  # Dirty Fighting: a stun, no attack roll
        d.disabled = max(d.disabled, now + seconds(r["Seconds"]))
        result = (None, False)
    elif i == 3024:  # Pommel Strike: a knockdown, no attack roll
        if not resisted():
            d.disabled = max(d.disabled, now + r["Seconds"] + rng.random() * abilities.KNOCKDOWN_RANDOM)
        result = (None, False)
    elif i == 90017:  # Growl: no attack roll; -15 defense for 30 s unless resisted
        if not resisted():
            d.buffs.append((now + r["Seconds"], {"Defense": r["Defense"]}))
        result = (None, False)
    elif i in (abilities.LIGHTNING, abilities.SHOCK):  # no roll: (100 + spellpower) x the factor, no armour
        amount = (100.0 + a.spellpower) * (r.get("DamageMul") or 0.0)
        if i == abilities.SHOCK:  # the cone: the others close by, here those fighting the caster
            for f in enemies or []:
                if f is not d and not f.down and f.target is a and not f.range:
                    f.health -= amount
                    f.down = f.health <= 0
        result = (amount, False)
    elif i == abilities.MIND_BLAST:  # every hostile close by stunned, rank-adjusted
        for f in [d] + [f for f in enemies or [] if f is not d and f.target is a and not f.range]:
            if not f.down:
                lasting = r["Seconds"] + (0 if f.side == "party" else max(0, abilities.PARTY_SLOTS - party_size))
                f.disabled = max(f.disabled, now + lasting * f.duration_scale)
                if f.threat is not None:
                    f.threat.forget(a, _alive)
        result = (None, False)
    elif i == 90048:  # Mabari Howl: every enemy not a boss stunned, no resistance, no rank adjustment
        for f in enemies or [d]:
            if not f.down and not f.boss:
                f.disabled = max(f.disabled, now + r["Seconds"])
        result = (None, False)
    elif i not in _STRIKES:  # a buff on itself
        a.buffs.append((now + r["Seconds"], r))
        return None, False
    else:
        hits = int(e.get("Hits", 1))
        mul = r.get("DamageMul", 1.0) or 1.0
        total, crit, landed = 0.0, False, True
        for h in range(1, hits + 1):
            if i == 1 and h > 1:  # Shield Pummel's shield blows always land
                damage, c = strike(rng, a, d, flanking, now, offhand=True, extra_crit=extra_crit, talent=True,
                                   mul=mul, sure=True)
            elif i == 90015:  # Overwhelm's bites: hits, never critical
                damage, c = strike(rng, a, d, flanking, now, talent=True, sure=True, force_crit=False)
            elif i == 90047:  # Shred: a hit is critical
                damage, c = strike(rng, a, d, flanking, now, r["AttackBonus"], talent=True, force_crit=True)
                if damage is not None:
                    damage *= 1.0 + e["Bleed"]  # its bleed, dealt at once here
            else:
                damage, c = strike(rng, a, d, flanking, now, r["AttackBonus"], offhand=i == 617,
                                   extra_crit=extra_crit, talent=True, mul=mul)
            landed = damage is not None
            if landed:
                if i == 3 and _health(d) - (total / d.max_health) <= e["Execute"] and not d.boss:
                    damage = max(0.0, d.health - total) + 1.0  # Critical Strike: a death blow
                total += damage
                crit = crit or c
        if i == 90015:
            d.disabled = max(d.disabled, now + r["Seconds"])
        if i in (617, 90016) and landed and not resisted():
            d.disabled = max(d.disabled, now + r["Seconds"] + rng.random() * abilities.KNOCKDOWN_RANDOM)
        if i == 1 and not resisted():
            d.disabled = max(d.disabled, now + seconds(r["Seconds"]))
        if i == 3025 and landed and not resisted():
            d.disarm = (now + r["Seconds"], d.attack)
        if i == 3072 and landed:  # Shattering Shot: 10 armour off for 20 s, a knockdown on non-special ranks
            d.buffs.append((now + r["Seconds"], {"Armour": e["ArmourFlat"]}))
            if not d.boss:
                d.disabled = max(d.disabled, now + abilities.KNOCKDOWN_SECONDS)
        if i == 4 and landed and not resisted():
            d.buffs.append((now + r["Seconds"], {"Armour": e["ArmourChange"] * d.armour}))
        if i == 3026 and landed:
            d.locked = max(d.locked, now + seconds(r["Seconds"]))
        result = (total if total > 0 or landed else None, crit)
    if d.threat is not None:
        d.threat.change(a, th.talent_threat(i), now, rng, _alive, _health)
    return result


def foe_turn(rng: random.Random, a: Fighter, d: Fighter, now: float, enemies: list, party_size: int,
             flanking: float) -> tuple[bool, float | None, bool]:
    """A combat round by tactics (tactics.choose), a foe's or a party member's: (used a talent, damage,
    critical). `enemies`: the other side's fighters."""
    regen(a, now)
    me = {"Health": _health(a) * 100.0, "Stamina": a.stamina / a.pool * 100.0 if a.pool else 0.0,
          "AttackedInMelee": any(f.target is a and not f.range for f in enemies if not f.down),
          "AttackedAtRange": any(f.target is a and f.range for f in enemies if not f.down),
          "Distance": 1.0 if not a.range or any(f.target is a and not f.range for f in enemies if not f.down)
          else RANGED_DISTANCE,
          "Surrounding": sum(1 for f in enemies if not f.down and f.target is a)}
    them = {"Health": _health(d) * 100.0, "Ranged": d.range > 0,
            "Stamina": d.stamina / d.pool * 100.0 if d.pool else 0.0}
    rows = {int(r["Id"]): r for r in a.talents}

    def can_use(ability, mode):
        r = rows.get(ability)
        return r is not None and (int(r["Use"]) == abilities.SUSTAINED) == mode and affordable(a, d, r, now)

    command, ability = ai.choose(a.tactics, me, them, can_use, rng)
    if command == ai.ATTACK:
        return False, None, False
    damage, crit = perform(rng, a, d, rows[ability], now, party_size, flanking,
                           enemies=[f for f in enemies if not f.down])
    return True, damage, crit


def _alive(f: Fighter) -> bool:
    return not f.down


def _health(f: Fighter) -> float:
    return max(0.0, f.health) / f.max_health if f.max_health else 0.0


def _wants(ability: int, a: Fighter, foes: list) -> bool:
    """When the simulated player uses a threat talent: Taunt when a foe is on someone else, Disengage when two or
    more are on it, Threaten (sustained) whenever it can."""
    if ability == 3041:
        return any(f.threat.target is not a for f in foes)
    if ability == 3016:
        return sum(1 for f in foes if f.threat.target is a) >= 2
    return True


def threatens(a: Fighter) -> bool:
    return any(int(r["Id"]) == 808 for r in a.sustained)


def fight(party: list[Fighter], foes: list[Fighter], rng: random.Random, wave: int = 0,
          flank: bool = True, slots: int = 0, use_threat: bool = True) -> dict:
    """One fight to the end. The fighters are changed (health, down): pass fresh ones. `slots` (provisional,
    docs/COMBAT.md; without threat only): at most that many foes attack the same party member at once; a foe
    finding every standing party member taken waits for its next turn (0: no limit)."""
    wave = wave or len(foes)
    active, reserve = list(foes[:wave]), list(foes[wave:])

    def comes_in(f, now):
        if use_threat:
            f.threat = th.Threat()
            for m in party:
                if not m.down:
                    f.threat.change(m, m.seen, now, rng, _alive, _health)

    for f in party + active:
        f.next_attack = rng.uniform(0.0, f.interval)
    for f in active:
        comes_in(f, 0.0)
    tally = {"party": [0, 0, 0], "foe": [0, 0, 0]}  # hits, misses, criticals
    taken: list[float] = []
    now = 0.0
    while now < TIME_LIMIT:
        standing = [f for f in party if not f.down]
        live = [f for f in active if not f.down]
        if not standing or not live and not reserve:
            break
        a = min((f for f in standing + live), key=lambda f: f.next_attack)
        now = a.next_attack
        if a.disabled > now:  # stunned or knocked down: its next turn when it is up
            a.next_attack = a.disabled
            continue
        a.next_attack += abilities.attack_interval(a.interval, 1.0 + a.own("Speed", now)) + a.own("AimDelay", now)
        if a.side == "foe" and use_threat:
            a.threat.change(None, 0.0, now, rng, _alive, _health, ranged=a.range > 0)  # AI_Threat_GetThreatTarget
            a.target = a.threat.target
            if a.target is None or a.target.down:
                continue
        elif a.target is None or a.target.down:
            if a.side == "foe":
                taken_by = {id(f): sum(1 for x in live if x is not a and x.target is f) for f in standing}
                free = [f for f in standing if not slots or taken_by[id(f)] < slots]
                if not free:
                    a.target = None
                    continue
                a.target = rng.choice(free)
            else:
                count = {id(f): 0 for f in live}
                for f in standing:
                    if f is not a and f.target is not None and id(f.target) in count:
                        count[id(f.target)] += 1
                least = min(count.values())
                a.target = rng.choice([f for f in live if count[id(f)] == least])
        d = a.target
        flanking = a.flanking if flank and (d.target is not a or d.disabled > now) else 0.0
        bravery = abilities.BRAVERY_CRIT * max(0, sum(1 for x in live if x.target is a) - 2) \
            if abilities.BRAVERY in a.passives else 0.0
        if a.side == "foe" or a.tag != PLAYER and a.tactics and a.talents:
            used, damage, crit = foe_turn(rng, a, d, now, party if a.side == "foe" else live, len(party),
                                          flanking) if a.tactics and a.talents else (False, None, False)
        else:
            used, damage, crit = use_talent(rng, a, d, now, len(party), flanking, bravery,
                                            [f for f in live if f.threat] if use_threat else None) if a.talents \
                else (False, None, False)
        if used and damage is None:
            continue
        if not used:
            damage, crit = strike(rng, a, d, flanking, now, extra_crit=bravery)
        t = tally[a.side]
        if d.threat is not None:
            d.threat.attacked(a, now, rng, alive=_alive, health=_health)
        if damage is None:
            t[1] += 1
            continue
        t[0] += 1
        t[2] += crit
        d.health -= damage
        a.dealt += damage
        if d.threat is not None and d.health > 0:
            d.threat.change(a, th.damage_threat(damage, d.max_health, a.rogue, threatens(a)), now, rng, _alive, _health)
        if a.side == "foe":
            taken.append(damage)
        if d.health <= 0:
            d.down = True
            if d.side == "party":
                for f in live:
                    if f.threat:
                        f.threat.forget(d, _alive)
            if abilities.DEATH_BLOW in a.passives:
                regen(a, now)
                a.stamina = min(a.pool, a.stamina + abilities.DEATH_BLOW_STAMINA * d.max_health)
            if d.side == "foe" and reserve:
                n = reserve.pop(0)
                n.next_attack = now + rng.uniform(0.0, n.interval)
                active.append(n)
                comes_in(n, now)
    won = all(f.down for f in foes)
    return {"Won": won, "Lost": all(f.down for f in party), "Time": round(now, 2),
            "Party": {f.tag: {"Health": round(max(0.0, f.health), 1), "Max": f.max_health, "Down": f.down,
                              "Dealt": round(f.dealt, 1)} for f in party},
            "Talents": dict(party[0].used) if party else {},
            "PartyTalents": {k: sum(f.used.get(k, 0) for f in party[1:]) for k in {k for f in party[1:] for k in f.used}},
            "FoeTalents": {k: sum(f.used.get(k, 0) for f in foes) for k in {k for f in foes for k in f.used}},
            "Tally": tally, "Taken": taken}


def simulate(area: dict, party: list[str], foes: list[str], runs: int = 1000, seed: int = 1, wave: int = 0,
             flank: bool = True, slots: int = 0, talents: bool = True, use_threat: bool = True) -> dict:
    """`runs` fights; the share won and lost, fight time, and per party member how often they fell, the health
    they had left and their share of the damage dealt; hit, miss and critical rates per side."""
    rng = random.Random(seed)
    results = []
    for _ in range(runs):
        ours, theirs = fighters(area, party, foes, talents)
        results.append(fight(ours, theirs, rng, wave, flank, slots, use_threat))
    tags = list(results[0]["Party"])
    totals = {s: [sum(r["Tally"][s][k] for r in results) for k in range(3)] for s in ("party", "foe")}
    dealt = {t: sum(r["Party"][t]["Dealt"] for r in results) for t in tags}
    all_dealt = sum(dealt.values()) or 1.0
    taken = [x for r in results for x in r["Taken"]]
    return {
        "Format": FORMAT, "Area": area.get("Area", ""), "Runs": runs, "Seed": seed, "Wave": wave, "Flanking": flank,
        "Foes": len(fighters(area, party, foes)[1]),
        "Won": round(sum(r["Won"] for r in results) / runs, 3),
        "Lost": round(sum(r["Lost"] for r in results) / runs, 3),
        "Time": {"Mean": round(statistics.mean(r["Time"] for r in results), 1),
                 "Median": round(statistics.median(r["Time"] for r in results), 1)},
        "Party": {t: {"Fell": round(sum(r["Party"][t]["Down"] for r in results) / runs, 3),
                      "HealthLeft": round(statistics.mean(r["Party"][t]["Health"] / r["Party"][t]["Max"]
                                                          for r in results), 3),
                      "DamageShare": round(dealt[t] / all_dealt, 3)} for t in tags},
        "Sides": {s: {"Hit": round(h / max(1, h + m), 3), "Crit": round(c / max(1, h), 3)}
                  for s, (h, m, c) in totals.items()},
        "DamagePerHitTaken": round(statistics.mean(taken), 2) if taken else 0.0,
        "FoeTalents": {abilities.NAMES.get(i, str(i)): round(sum(r["FoeTalents"].get(i, 0) for r in results) / runs, 2)
                       for i in sorted({i for r in results for i in r["FoeTalents"]})},
        "PartyTalents": {abilities.NAMES.get(i, str(i)): round(sum(r["PartyTalents"].get(i, 0) for r in results) / runs, 2)
                         for i in sorted({i for r in results for i in r["PartyTalents"]})},
        # the player's talent uses a fight, by name
        "Talents": {abilities.NAMES.get(i, str(i)): round(sum(r["Talents"].get(i, 0) for r in results) / runs, 2)
                    for i in sorted({i for r in results for i in r["Talents"]})},
    }


def report(sim: dict, label: str = "") -> str:
    """A few readable lines."""
    lines = [f"{label or sim['Area']}: {sim['Runs']} fights against {sim['Foes']} foes"
             f"{' in waves of %d' % sim['Wave'] if sim['Wave'] else ''}: won {sim['Won']:.0%}, lost {sim['Lost']:.0%}, "
             f"{sim['Time']['Mean']} s on average",
             f"  party hits {sim['Sides']['party']['Hit']:.0%} (criticals {sim['Sides']['party']['Crit']:.0%}), "
             f"foes hit {sim['Sides']['foe']['Hit']:.0%} for {sim['DamagePerHitTaken']} a hit"]
    if sim.get("FoeTalents"):
        lines.append("  the foes' talents a fight: " + ", ".join(f"{k} {v}" for k, v in sim["FoeTalents"].items()))
    if sim.get("Talents"):
        lines.append("  the player's talents a fight: " + ", ".join(f"{k} {v}" for k, v in sim["Talents"].items()))
    if sim.get("PartyTalents"):
        lines.append("  the party's talents a fight: " + ", ".join(f"{k} {v}" for k, v in sim["PartyTalents"].items()))
    for t, p in sim["Party"].items():
        lines.append(f"  {t}: fell {p['Fell']:.0%}, health left {p['HealthLeft']:.0%}, damage dealt {p['DamageShare']:.0%}")
    return "\n".join(lines)
