"""Threat: how a hostile creature picks whom to fight (ai_threat_h, with Dragon Age Reborn's changes; combat stage 4,
docs/COMBAT.md, "Threat").

Every hostile keeps a threat value per enemy it knows (the engine's threat table) and fights the one it hates most,
switching only when its switch timer allows. What adds threat:

  seen         AI_Threat_UpdateEnemyAppeared: 10, +5 for light armour or +10 for medium, heavy or massive, +5 for a
               melee weapon (the script tests the chest piece's base type against the bows, so every creature gets
               it below nightmare): seen_threat
  damage       AI_Threat_UpdateDamage: damage as a percentage of the hostile's own max health; x0.8 from a rogue,
               x2 while the attacker sustains Threaten (x3 with Frightening, Reborn)
  attacked     AI_Threat_UpdateEnemyAttacked: up to 1 when attacked at all
  talents      Reborn's ability_core: the talent's threat_impact on its target (on every creature in the area for an
               area talent); Taunt +300 more and its switch timer cleared, Disengage -100
  gone         an enemy dead, or unseen (Feign Death turns stealth on): forgotten (AI_Threat_UpdateEnemyDisappeared)

AI_Threat_UpdateCreatureThreat clamps a change (at least 1 when positive; never down to 0 or below: 1 is the floor;
at most 1000 in all) and then retargets: the first target is the most hated; later the most hated takes over only
when the creature may switch (seconds since the last switch >= its switch timer, which grows by 5 a switch and goes
back to 0 past 25; ranged attackers always may), unless the enemy whose threat just changed is at 20% health or less
(kept half the time) or 10% or less (kept 9 times in 10).
"""

from __future__ import annotations

import random

MAX = 1000.0  # AI_THREAT_MAX
MIN_CHANGE = 1.0  # AI_THREAT_MIN_CHANGE
SEEN = 10.0  # AI_THREAT_VALUE_ENEMY_PERCEIVED
SEEN_ARMOUR = {"light": 5.0, "medium": 10.0, "heavy": 10.0, "massive": 10.0}  # AI_THREAT_PERCEIVED_ARMOR_*
SEEN_MELEE = 5.0  # AI_THREAT_PERCEIVED_WEAPON_MELEE
ATTACKED = 1.0  # AI_THREAT_VALUE_ATTACKED
ROGUE_DAMAGE = 0.8  # AI_THREAT_ROGUE_DAMAGE_RATIO
THREATEN_DAMAGE = 2.0  # while Threaten is sustained (3.0 with Frightening, Reborn)
SWITCH_JUMP, SWITCH_MAX = 5, 25  # AI_THREAT_SWITCH_TIMER_JUMP, AI_THREAT_SWITCH_TIME_MAX
KEEP_20, KEEP_10 = 50, 90  # AI_THREAT_CHANCE_KEEP_TARGET_20_HEALTH, _10_HEALTH
TAUNT = 300.0  # TAUNT_THREAT_INCREASE
DISENGAGE = -100.0  # DISENGAGE_THREAT_DECREASE
AREA = 10.0  # m: Taunt's and Disengage's aoe_param1, the radius around the user
# Reborn's ability_core adds each talent's abi_base threat_impact to its target (to all in the area for Taunt and
# Disengage); talents aimed at their user (Perfect Strike, Threaten...) add none.
IMPACT = {3041: 10.0, 3016: 1.0, 603: 2.0, 617: 2.0, 3026: 1.0, 1: 2.0, 3: 8.0, 4: 3.0, 3024: 2.0, 3025: 2.0}
# What a talent adds besides: Taunt also clears the switch timer.
SCRIPTED = {3041: TAUNT, 3016: DISENGAGE}


def seen_threat(chest_label: str = "", nightmare: bool = False) -> float:
    """AI_Threat_UpdateEnemyAppeared for an enemy wearing a chest piece of this itemstats label ("Armor - Light"...)."""
    if nightmare:
        return SEEN
    kind = chest_label.lower().replace("armor - ", "").replace("armour - ", "").strip()
    return SEEN + SEEN_ARMOUR.get(kind, 0.0) + SEEN_MELEE


def damage_threat(damage: float, max_health: float, rogue: bool = False, threaten: bool = False) -> float:
    """AI_Threat_UpdateDamage: what a hit adds to the struck hostile's threat for its attacker."""
    if max_health <= 0:
        return 0.0
    change = damage / max_health * 100.0
    if rogue:
        change *= ROGUE_DAMAGE
    if threaten:
        change *= THREATEN_DAMAGE
    return change


def talent_threat(ability: int) -> float:
    """A talent's threat on each hostile it reaches (its scripted part first, then Reborn's threat_impact)."""
    return SCRIPTED.get(ability, 0.0) + IMPACT.get(ability, 0.0)


class Threat:
    """One hostile's threat table and target. Enemies are any hashable objects; `alive(enemy)` and `health(enemy)`
    (current / max, 0-1) come from the caller."""

    def __init__(self):
        self.table: dict = {}
        self.target = None
        self.switched = 0.0  # AI_THREAT_TARGET_SWITCH_COUNTER: when it last switched
        self.wait = 0  # AI_THREAT_SWITCH_TIMER_MIN: seconds it must keep a target before switching

    def most_hated(self, alive):
        live = [(v, i) for i, (e, v) in enumerate(self.table.items()) if alive(e)]
        if not live:
            return None
        best = max(live, key=lambda x: (x[0], -x[1]))  # the first one added wins a tie
        return list(self.table)[best[1]]

    def change(self, enemy, amount: float, now: float, rng: random.Random, alive=lambda e: True,
               health=lambda e: 1.0, ranged: bool = False) -> None:
        """AI_Threat_UpdateCreatureThreat: add `amount` for `enemy` (None: only retarget), then retarget."""
        if enemy is not None and alive(enemy):
            current = self.table.get(enemy, 0.0)
            if 0.0 < amount < MIN_CHANGE:
                amount = MIN_CHANGE
            if amount < 0.0 and current + amount <= 0.0:
                amount = -(current - 1.0)
            if amount > 0.0 and current + amount > MAX:
                amount = MAX - current
            self.table[enemy] = current + amount
        most = self.most_hated(alive)
        if self.target is None:  # the first target
            self.target, self.switched = most, now
            return
        if most is self.target:
            return
        if enemy is not None and keep_wounded(health(enemy), rng):
            return
        if ranged or now - self.switched >= self.wait or not alive(self.target):
            self.switched, self.target = now, most
            self.wait += SWITCH_JUMP
            if self.wait > SWITCH_MAX:
                self.wait = 0

    def attacked(self, enemy, now: float, rng: random.Random, **kw) -> None:
        """AI_Threat_UpdateEnemyAttacked: struck at (hit or not), up to 1."""
        if self.table.get(enemy, 0.0) < ATTACKED:
            self.change(enemy, ATTACKED, now, rng, **kw)

    def forget(self, enemy, alive=lambda e: True) -> None:
        """AI_Threat_UpdateEnemyDisappeared: dead or unseen."""
        self.table.pop(enemy, None)
        if self.target is enemy:
            self.target = self.most_hated(alive)

    def taunted(self) -> None:
        """Taunt: may switch at once."""
        self.switched = -1e9


def keep_wounded(health: float, rng: random.Random) -> bool:
    """AI_Threat_KeepWoundedTarget (on the enemy whose threat changed): at 20% health or less, kept half the time;
    at 10% or less, 9 times in 10."""
    health = max(0.0, health)
    if 0.1 < health <= 0.2:
        return rng.randint(1, 100) <= KEEP_20
    if health <= 0.1:
        return rng.randint(1, 100) <= KEEP_10
    return False
