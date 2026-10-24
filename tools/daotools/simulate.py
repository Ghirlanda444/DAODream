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
"""

from __future__ import annotations

import fnmatch
import random
import statistics
from dataclasses import dataclass, field

from . import stats

FORMAT = "DAODream.Simulation 1"
PLAYER = "player"
# Seconds between attacks: the export's (NpcInterval, PlayerStats[12]: the game's timing) when it has them,
# else the Unreal prototype's fixed ones; "export": False always uses the fixed ones.
INTERVAL = {"player": 1.0, "party": 1.5, "foe": 2.0, "export": True}
TIME_LIMIT = 600.0
RULES = ("Armour", "Penetration", "Crit", "Flanking", "DamageBonus")  # area.RULES


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
    max_health: float = field(init=False)
    down: bool = False
    target: "Fighter | None" = None
    next_attack: float = 0.0
    dealt: float = 0.0

    def __post_init__(self):
        self.max_health = self.health


def _rules(values: list, i: int) -> dict:
    return dict(zip(RULES, values[i * len(RULES):(i + 1) * len(RULES)])) if values else {}


def player_fighter(area: dict) -> Fighter:
    """PlayerStats: health, attack, defense, damage min and max, threshold, RULES, stamina, seconds between
    attacks (INTERVAL["player"] when the export has none)."""
    p = area["PlayerStats"]
    r = dict(zip(RULES, p[6:11])) if len(p) > 10 else {}
    return Fighter(PLAYER, "party", p[0], p[1], p[2], (p[3], p[4]), 1.0, p[5], r.get("Armour", 0.0),
                   r.get("Penetration", 0.0), r.get("Crit", 0.0), r.get("Flanking", 0.0), r.get("DamageBonus", 0.0),
                   p[12] if len(p) > 12 and INTERVAL.get("export", True) else INTERVAL["player"])


def npc_fighter(area: dict, i: int, side: str) -> Fighter:
    r = _rules(area.get("NpcRules") or [], i)
    threshold = area["PlayerStats"][5] if area.get("PlayerStats") else 0.0
    return Fighter(area["NpcTags"][i], side, area["NpcHealth"][i], area["NpcAttack"][i], area["NpcDefense"][i],
                   (area["NpcDamage"][2 * i], area["NpcDamage"][2 * i + 1]), area["NpcDamageScale"][i], threshold,
                   r.get("Armour", 0.0), r.get("Penetration", 0.0), r.get("Crit", 0.0), r.get("Flanking", 0.0),
                   r.get("DamageBonus", 0.0), _interval(area, i, side))


def _interval(area: dict, i: int, side: str) -> float:
    """NpcInterval (the game's attack timing, stats.attack_interval) when the export has it and INTERVAL["export"]
    is not False; else the prototype's fixed timing."""
    found = area.get("NpcInterval") or []
    if i < len(found) and INTERVAL.get("export", True):
        return found[i]
    return INTERVAL["party" if side == "party" else "foe"]


def fighters(area: dict, party: list[str], foes: list[str]) -> tuple[list[Fighter], list[Fighter]]:
    """The player and the party members named by tag; the foes matching the patterns (fnmatch), in tag order.
    A tag the area has more than once counts each creature."""
    tags = area["NpcTags"]
    ours = [player_fighter(area)] + [npc_fighter(area, i, "party") for t in party for i, x in enumerate(tags) if x == t]
    picked = sorted((t, i) for i, t in enumerate(tags) if any(fnmatch.fnmatch(t, p) for p in foes))
    return ours, [npc_fighter(area, i, "foe") for _, i in picked]


def strike(rng: random.Random, a: Fighter, d: Fighter, flanking: float = 0.0) -> tuple[float | None, bool]:
    """One attack: (damage, critical), damage None for a miss. ResolveHit, RollHit and Mitigate in Unreal."""
    crit = rng.random() * 100.0 < stats.crit_chance(a.crit, flanking)
    if rng.random() * 100.0 >= stats.hit_chance(a.attack, d.defense, flanking):
        return None, False
    rolled = rng.uniform(*a.damage)
    return stats.hit_damage(rolled, crit=crit, armour=d.armour, armour_roll=rng.random(), penetration=a.penetration,
                            bonus=a.bonus, scale=a.scale, threshold=a.threshold), crit


def fight(party: list[Fighter], foes: list[Fighter], rng: random.Random, wave: int = 0,
          flank: bool = True) -> dict:
    """One fight to the end. The fighters are changed (health, down): pass fresh ones."""
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
        a.next_attack += a.interval
        if a.target is None or a.target.down:
            if a.side == "foe":
                a.target = rng.choice(standing)
            else:
                count = {id(f): 0 for f in live}
                for f in standing:
                    if f is not a and f.target is not None and id(f.target) in count:
                        count[id(f.target)] += 1
                least = min(count.values())
                a.target = rng.choice([f for f in live if count[id(f)] == least])
        d = a.target
        damage, crit = strike(rng, a, d, a.flanking if flank and d.target is not a else 0.0)
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
            if d.side == "foe" and reserve:
                n = reserve.pop(0)
                n.next_attack = now + rng.uniform(0.0, n.interval)
                active.append(n)
    won = all(f.down for f in foes)
    return {"Won": won, "Lost": all(f.down for f in party), "Time": round(now, 2),
            "Party": {f.tag: {"Health": round(max(0.0, f.health), 1), "Max": f.max_health, "Down": f.down,
                              "Dealt": round(f.dealt, 1)} for f in party},
            "Tally": tally, "Taken": taken}


def simulate(area: dict, party: list[str], foes: list[str], runs: int = 1000, seed: int = 1, wave: int = 0,
             flank: bool = True) -> dict:
    """`runs` fights; the share won and lost, fight time, and per party member how often they fell, the health
    they had left and their share of the damage dealt; hit, miss and critical rates per side."""
    rng = random.Random(seed)
    results = []
    for _ in range(runs):
        ours, theirs = fighters(area, party, foes)
        results.append(fight(ours, theirs, rng, wave, flank))
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
    }


def report(sim: dict, label: str = "") -> str:
    """A few readable lines."""
    lines = [f"{label or sim['Area']}: {sim['Runs']} fights against {sim['Foes']} foes"
             f"{' in waves of %d' % sim['Wave'] if sim['Wave'] else ''}: won {sim['Won']:.0%}, lost {sim['Lost']:.0%}, "
             f"{sim['Time']['Mean']} s on average",
             f"  party hits {sim['Sides']['party']['Hit']:.0%} (criticals {sim['Sides']['party']['Crit']:.0%}), "
             f"foes hit {sim['Sides']['foe']['Hit']:.0%} for {sim['DamagePerHitTaken']} a hit"]
    for t, p in sim["Party"].items():
        lines.append(f"  {t}: fell {p['Fell']:.0%}, health left {p['HealthLeft']:.0%}, damage dealt {p['DamageShare']:.0%}")
    return "\n".join(lines)
