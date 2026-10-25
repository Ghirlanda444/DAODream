"""python enemies.py [setup|graphs|save|all]: combat stage 4's enemy talents in the Blueprints (docs/COMBAT.md, "Enemy
talents"; the rules: tools/daotools/tactics.py, abilities.py). Play/Simulate stopped; talents.py and threat.py must
have run.

The export brings NpcTalents (per creature tactics.MAX_TALENTS rows of abilities.TALENT_FIELDS), NpcTactics (its
aip_* table, tactics.MAX_TACTICS rows of tactics.FIELDS) and NpcStatus 5-8 (stamina, fatigue, shield damage).
BP_AreaLoader.GiveNpcRules hands each creature its share (BP_DlgNPC.SetNpcTalents, SetStatus).

BP_DlgNPC: each attack round (Bite -> CombatRound) a hostile gets back a second of stamina per second of the round,
then ChooseTactic goes down its rows: TacticRow skips rows before a jump's target (TacNext) and after a row fired
(TacDone), rolls the row's chance, checks its condition (TacticCond: any; health or stamina level of itself or its
foe; its foe in melee) and runs its command (TacticAct: a jump; using a talent or switching a mode on when
TacticUsable finds it has the talent, can pay and has it off cooldown). DoTalent pays (a mode: upkeep off the pool,
fatigue, NSumOwn; else the cost x (1 + fatigue/100), rounded), says the talent's name over its head (SayTalent) and
applies it (TalentEffect): Dirty Fighting stuns, Pommel Strike knocks down, Shield Pummel (EffPummel), Sunder
Weapon and Sunder Armor (EffSunder), Critical Strike (EffCritical), Below the Belt (EffBelt), any other a blow with
the talent's numbers (HitFoe: its attack bonus, damage multiplier, the shield's damage; a sure blow for Shield
Pummel's shield). No row: StrikeFoe (HitFoe 0 1). Its modes' defense and armour count when it is struck (TakeStrike,
TakeAttack). The effects reach a creature foe through its own functions (KnockFor, Stun, Disarm, Slow) and the
player through BP_PlotManager: StunPlayer (input off until PStunUntil; PlayerRecover gives it back), DisarmPlayer,
LockPlayer (no talents). The player's own Shield Pummel (a level-2 warrior's automatic pick): PlayerPummel (its
blows through TakeAttack with TBonus, TOff and PTMul, the damage multiplier), then PummelStun. AttackerState: a stunned or knocked down attacker strikes nobody
(StrikeNpc, StrikePlayer), a disarmed one has lost its attack rating. CombatTick lets any creature get up from a
knockdown (Recover).
"""
import os
import sys

import combat_rules as cr
import ue

PM, NPC, AL = cr.PM, cr.NPC, cr.AL
F, ACTOR = "float", cr.ACTOR
ARR = "ARRAY"

VARIABLES = {
    NPC: [("NTalents", F, ARR), ("NTactics", F, ARR), ("NReady", F, ARR), ("NOn", F, ARR), ("NStamina", F),
          ("NPool", F), ("NFatigue", F), ("NOffMin", F), ("NOffMax", F), ("NBaseInterval", F), ("NOwnAtk", F),
          ("NOwnSpeed", F), ("NOwnCrit", F), ("NOwnDef", F), ("NOwnArmour", F), ("NOwnScale", F), ("FoeHp", F),
          ("FoeSta", F), ("bCondOk", "bool"), ("TFound", "int"), ("NCostNow", F), ("TacSlot", "int"),
          ("TacNext", F), ("bTacDone", "bool"), ("RB", "int"), ("HAtk", F), ("HMin", F), ("HMax", F),
          ("DisarmUntil", F), ("DisarmAmt", F)],
    PM: [("PStunUntil", F), ("bPStunned", "bool"), ("PDisarmUntil", F), ("PDisarmAmt", F), ("PLockUntil", F),
         ("bAStunned", "bool"), ("APen", F), ("PTMul", F)],
    AL: [("NpcTalents", F, ARR), ("NpcTactics", F, ARR)],
}
S, I, B = ("Seconds", F), ("I", "int"), ("bFall", "bool")
STRIKE = [("Attacker", ACTOR), ("Target", cr.NPC_CLASS), ("Atk", F), ("Def", F), ("DmgMin", F), ("DmgMax", F),
          ("Scale", F), ("Crit", F), ("Pen", F), ("Bonus", F), ("Flank", F), ("Armour", F)]
FUNCTIONS = {
    NPC: {"CopyTalent": [("InTalents", "float[]"), I, ("K", "int")], "CopyTactic": [("InTactics", "float[]"), I, ("K", "int")],
          "SetNpcTalents": [("InTalents", "float[]"), ("InTactics", "float[]"), ("K", "int")],
          "SetNpcTactics": [("InTactics", "float[]"), ("K", "int")], "ClearSlots": [], "NAddOwn": [("K", "int")],
          "NSumOwn": [], "ReadFoe": [], "TacticCond": [], "FindOne": [("K", "int"), ("Ability", F)],
          "TacticUsable": [("Ability", F), ("bMode", "bool")], "UsableCheck": [("bMode", "bool")],
          "TacticAct": [I], "TacticRow": [I], "ChooseTactic": [],
          "HitFoe": [("Bonus", F), ("Mul", F), ("bOff", "bool"), ("bSure", "bool")], "HitNpcFoe": [],
          "StunFoe": [S, B], "StunNpcFoe": [S, B], "DisarmFoe": [S], "DisarmNpcFoe": [S], "Disarm": [S],
          "LockFoe": [S], "SlowNpcFoe": [S], "KillFoe": [], "KillNpcFoe": [], "KnockFor": [S],
          "EffPummel": [("K", "int")], "EffSunder": [("K", "int")], "EffCritical": [("K", "int")],
          "EffBelt": [("K", "int")], "TalentEffect": [("K", "int")], "TalentEffect2": [("K", "int")],
          "DoTalent": [], "SayTalent": [], "CombatRound": []},
    PM: {"StunPlayer": [S, B], "DisarmPlayer": [S], "LockPlayer": [S], "PlayerRecover": [],
         "AttackerState": [("Attacker", ACTOR)], "NpcAttackerState": [("Attacker", ACTOR)], "StrikeNpcGo": STRIKE,
         "StrikeOnce": [], "PlayerPummel": [], "PummelStun": []},
}
GRAPHS = [
    (PM, ["StunPlayer", "DisarmPlayer", "LockPlayer", "PlayerRecover", "NpcAttackerState", "AttackerState",
          "StrikeNpcGo", "StrikeNpc", "StrikePlayer", "UseTalent", "StaminaTick", "SetPlayerTalentStats",
          "PlayerStrike", "StrikeOnce", "PummelStun", "PlayerPummel", "StrikeTalent"]),
    (NPC, ["SetStatus", "CopyTalent", "CopyTactic", "ClearSlots", "SetNpcTactics", "SetNpcTalents", "NAddOwn",
           "NSumOwn", "ReadFoe", "TacticCond", "FindOne", "UsableCheck", "TacticUsable", "TacticAct", "TacticRow",
           "ChooseTactic", "HitNpcFoe", "HitFoe", "StrikeFoe", "KnockFor", "Knock", "Recover", "Disarm",
           "StunNpcFoe", "StunFoe", "DisarmNpcFoe", "DisarmFoe", "SlowNpcFoe", "LockFoe", "KillNpcFoe", "KillFoe",
           "EffPummel", "EffSunder", "EffCritical", "EffBelt", "TalentEffect2", "TalentEffect", "SayTalent",
           "DoTalent", "CombatRound", "Bite", "TakeStrike", "TakeAttack", "CombatTick"]),
    (AL, ["GiveNpcRules", "BuildFixtures"]),
]


def setup():
    cr.setup(VARIABLES, FUNCTIONS, compile_all_after=False)
    for bp in (PM, NPC, AL):
        cr.call("compile_blueprint", {"blueprint": {"refPath": bp}})


def graphs():
    for bp, names in GRAPHS:
        for fn in names:
            code = open(os.path.join(cr.HERE, "dsl", fn + ".dsl"), encoding="utf-8").read()
            r = cr.call("write_graph_dsl", {"graph": {"refPath": "%s:%s" % (bp, fn)}, "code": code})
            print(fn, str(r)[:300])
        cr.call("compile_blueprint", {"blueprint": {"refPath": bp}})


def save():
    import pyrun
    print(pyrun.run('''
EAL = unreal.EditorAssetLibrary
OUT["saved"] = [EAL.save_asset(p, only_if_is_dirty=False) for p in ("/Game/Cousland/Plots/BP_PlotManager",
                "/Game/Cousland/Dialogue/BP_DlgNPC", "/Game/Cousland/Areas/BP_AreaLoader")]
''', 300))


if __name__ == "__main__":
    ue.init()
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, f in (("setup", setup), ("graphs", graphs), ("save", save)):
        if phase in (name, "all"):
            f()
