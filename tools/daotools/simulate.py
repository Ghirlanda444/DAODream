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
"""

from __future__ import annotations

import fnmatch
import random
import statistics
from dataclasses import dataclass, field

from . import abilities, stats

FORMAT = "DAODream.Simulation 1"
PLAYER = "player"
# Seconds between attacks: the export's (NpcInterval, PlayerStats[12]: the game's timing) when it has them,
# else the Unreal prototype's fixed ones; "export": False always uses the fixed ones.
INTERVAL = {"player": 1.0, "party": 1.5, "foe": 2.0, "export": True}
TIME_LIMIT = 600.0
RULES = ("Armour", "Penetration", "Crit", "Flanking", "DamageBonus")  # area.RULES
SLOTS = 0  # foes attacking the same party member at once (0: no limit; BP_PlotManager.Slots in Unreal)


@dataclass
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

    def __post_init__(self):
        self.max_health = self.health
        self.pool = self.stamina

    def own(self, key: str, now: float) -> float:
        """What its buffs and sustained talents add to TALENT_FIELDS' key."""
        return sum(r[key] for until, r in self.buffs if until > now) + sum(r[key] for r in self.sustained)


def _rules(values: list, i: int) -> dict:
    return dict(zip(RULES, values[i * len(RULES):(i + 1) * len(RULES)])) if values else {}


def player_fighter(area: dict, talents: bool = True) -> Fighter:
    """PlayerStats (area.player_stats): health, attack, defense, damage min and max, threshold, RULES, stamina,
    seconds between attacks (INTERVAL["player"] when the export has none), fatigue, level, displacement, rogue,
    the shield's damage; PlayerTalents and PlayerPassives unless `talents` is False."""
    p = list(area["PlayerStats"]) + [0.0] * 8
    r = dict(zip(RULES, p[6:11]))
    f = Fighter(PLAYER, "party", p[0], p[1], p[2], (p[3], p[4]), 1.0, p[5], r["Armour"], r["Penetration"], r["Crit"],
                r["Flanking"], r["DamageBonus"],
                p[12] if p[12] and INTERVAL.get("export", True) else INTERVAL["player"], stamina=p[11], fatigue=p[13],
                level=p[14] or 1.0, displacement=p[15], rogue=bool(p[16]), offhand=(p[17], p[18]))
    if talents:
        n = len(abilities.TALENT_FIELDS)
        rows = area.get("PlayerTalents") or []
        f.talents = [dict(zip(abilities.TALENT_FIELDS, rows[k:k + n])) for k in range(0, len(rows), n)]
        f.passives = tuple(int(x) for x in area.get("PlayerPassives") or [])
    return f


def npc_fighter(area: dict, i: int, side: str) -> Fighter:
    r = _rules(area.get("NpcRules") or [], i)
    threshold = area["PlayerStats"][5] if area.get("PlayerStats") else 0.0
    status = (area.get("NpcStatus") or [])[3 * i:3 * i + 3] or [1.0, 1.0, 0.0]
    return Fighter(area["NpcTags"][i], side, area["NpcHealth"][i], area["NpcAttack"][i], area["NpcDefense"][i],
                   (area["NpcDamage"][2 * i], area["NpcDamage"][2 * i + 1]), area["NpcDamageScale"][i], threshold,
                   r.get("Armour", 0.0), r.get("Penetration", 0.0), r.get("Crit", 0.0), r.get("Flanking", 0.0),
                   r.get("DamageBonus", 0.0), _interval(area, i, side), level=status[0], duration_scale=status[1],
                   resist=status[2])


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
           talent: bool = False) -> tuple[float | None, bool]:
    """One attack: (damage, critical), damage None for a miss. ResolveHit, RollHit and Mitigate in Unreal.
    `bonus`: a talent's attack bonus; `offhand`: with the shield's damage; `extra_crit`: Bravery's. The target's
    displacement (Evasion) makes it miss outright first. A rogue's plain attack on a flanked (or, with Coup de
    Grace, stunned) target that hits is a backstab: critical damage."""
    if d.displacement and rng.random() * 100.0 < d.displacement:
        return None, False
    crit = rng.random() * 100.0 < stats.crit_chance(a.crit + a.own("Crit", now) + extra_crit, flanking)
    if rng.random() * 100.0 >= stats.hit_chance(a.attack + a.own("Attack", now) + bonus, d.defense, flanking):
        return None, False
    if a.rogue and not talent and (flanking > 0 or abilities.COUP_DE_GRACE in a.passives and d.disabled > now):
        crit = True  # Combat_CheckBackstab: COMBAT_RESULT_BACKSTAB, critical damage
    rolled = rng.uniform(*(a.offhand if offhand else a.damage))
    return stats.hit_damage(rolled, crit=crit, armour=d.armour, armour_roll=rng.random(),
                            penetration=a.penetration + a.own("Penetration", now), bonus=a.bonus, scale=a.scale,
                            threshold=a.threshold), crit


def regen(f: Fighter, now: float) -> None:
    f.stamina = min(f.pool, f.stamina + abilities.REGEN_COMBAT * (now - f.regen_at))
    f.regen_at = now


def use_talent(rng: random.Random, a: Fighter, d: Fighter, now: float, party_size: int, flanking: float,
               extra_crit: float = 0.0) -> tuple[bool, float | None, bool]:
    """The first of `a`'s talents it can use now (in PlayerTalents' order), used on `d`: (used, damage, critical),
    damage None when nothing struck."""
    regen(a, now)
    for r in a.talents:
        i = int(r["Id"])
        if i in abilities.THREAT or a.ready.get(i, 0.0) > now:
            continue
        sustained = int(r["Use"]) == abilities.SUSTAINED
        disable = abilities.DISABLES.get(i)
        buff = not sustained and not r["AttackBonus"] and not disable
        if sustained:
            if r in a.sustained or a.pool - r["Upkeep"] < 0:
                continue
            a.sustained.append(r)
            a.pool -= r["Upkeep"]
            a.stamina = min(a.stamina, a.pool)
            a.fatigue += r["Fatigue"]
        else:
            cost = abilities.ability_cost(r["Cost"], a.fatigue)
            if a.stamina < cost or disable and d.disabled > now or buff and any(
                    b is r and until > now for until, b in a.buffs):
                continue
            a.stamina -= cost
        a.ready[i] = now + r["Cooldown"]
        a.used[i] = a.used.get(i, 0) + 1
        if sustained:
            return True, None, False
        if buff:
            a.buffs.append((now + r["Seconds"], r))
            return True, None, False
        if disable == "Stun":  # Dirty Fighting: no attack roll; GetRankAdjustedEffectDuration
            seconds = r["Seconds"] + max(0, abilities.PARTY_SLOTS - party_size) if r["Seconds"] >= 1.0 else r["Seconds"]
            d.disabled = now + seconds * d.duration_scale
            return True, None, False
        damage, crit = strike(rng, a, d, flanking, now, r["AttackBonus"], offhand=disable == "Knockdown",
                              extra_crit=extra_crit, talent=True)
        if damage is not None and disable == "Knockdown" and rng.random() * 100.0 >= d.resist:
            d.disabled = max(d.disabled, now + r["Seconds"] + rng.random() * abilities.KNOCKDOWN_RANDOM)
        return True, damage, crit
    return False, None, False


def fight(party: list[Fighter], foes: list[Fighter], rng: random.Random, wave: int = 0,
          flank: bool = True, slots: int = 0) -> dict:
    """One fight to the end. The fighters are changed (health, down): pass fresh ones. `slots` (provisional,
    docs/COMBAT.md): at most that many foes attack the same party member at once; a foe finding every
    standing party member taken waits for its next turn (0: no limit)."""
    wave = wave or len(foes)
    active, reserve = list(foes[:wave]), list(foes[wave:])
    for f in party + active:
        f.next_attack = rng.uniform(0.0, f.interval)
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
        a.next_attack += abilities.attack_interval(a.interval, 1.0 + a.own("Speed", now))
        if a.target is None or a.target.down:
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
        used, damage, crit = use_talent(rng, a, d, now, len(party), flanking, bravery) if a.talents \
            else (False, None, False)
        if used and damage is None:
            continue
        if not used:
            damage, crit = strike(rng, a, d, flanking, now, extra_crit=bravery)
        t = tally[a.side]
        if damage is None:
            t[1] += 1
            continue
        t[0] += 1
        t[2] += crit
        d.health -= damage
        a.dealt += damage
        if a.side == "foe":
            taken.append(damage)
        if d.health <= 0:
            d.down = True
            if abilities.DEATH_BLOW in a.passives:
                regen(a, now)
                a.stamina = min(a.pool, a.stamina + abilities.DEATH_BLOW_STAMINA * d.max_health)
            if d.side == "foe" and reserve:
                n = reserve.pop(0)
                n.next_attack = now + rng.uniform(0.0, n.interval)
                active.append(n)
    won = all(f.down for f in foes)
    return {"Won": won, "Lost": all(f.down for f in party), "Time": round(now, 2),
            "Party": {f.tag: {"Health": round(max(0.0, f.health), 1), "Max": f.max_health, "Down": f.down,
                              "Dealt": round(f.dealt, 1)} for f in party},
            "Talents": dict(party[0].used) if party else {},
            "Tally": tally, "Taken": taken}


def simulate(area: dict, party: list[str], foes: list[str], runs: int = 1000, seed: int = 1, wave: int = 0,
             flank: bool = True, slots: int = 0, talents: bool = True) -> dict:
    """`runs` fights; the share won and lost, fight time, and per party member how often they fell, the health
    they had left and their share of the damage dealt; hit, miss and critical rates per side."""
    rng = random.Random(seed)
    results = []
    for _ in range(runs):
        ours, theirs = fighters(area, party, foes, talents)
        results.append(fight(ours, theirs, rng, wave, flank, slots))
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
    if sim.get("Talents"):
        lines.append("  the player's talents a fight: " + ", ".join(f"{k} {v}" for k, v in sim["Talents"].items()))
    for t, p in sim["Party"].items():
        lines.append(f"  {t}: fell {p['Fell']:.0%}, health left {p['HealthLeft']:.0%}, damage dealt {p['DamageShare']:.0%}")
    return "\n".join(lines)
