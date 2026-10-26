"""python spells.py [setup|graphs|save|all]: combat stage 3's spells in the Blueprints (docs/COMBAT.md, "Spells"; the rules:
tools/daotools/abilities.py SPELLS, stats.spellpower, stats.is_staff). Play/Simulate stopped; dogs.py must have run.

The export brings NpcSpell (per creature: spellpower, a staff in hand) and whole tactics tables (NpcTactics: 40 rows
of 6, was 12): BP_AreaLoader.BuildFixtures reads NpcSpell, GiveNpcRules hands each creature its share (SetSpell),
SetNpcTactics copies 240 floats a creature.

BP_DlgNPC:
- A staff's bolt (StrikeFoe with bStaff) always hits, for a roll between the export's damage (the staff's and part
  of spellpower), no armour or critical: SpellHitFoe, TakeHit on a creature, BP_PlotManager.SpellHitPlayer on the
  player (not while talking, at the game over or with the player down).
- The spells (TalentEffect5 -> TalentEffect6), (100 + SpellPower) x the row's factor (field 15), no roll:
  Lightning on its foe (SpellHitFoe); Shock on everyone hostile to the caster within 10 m and 35 degrees either side
  of where it faces, turned to its foe (EffShock, ShockHit: GetHorizontalDotProductTo; abi_base's 35 taken as the
  half-angle); Mind Blast stuns everyone hostile within 5 m for the row's seconds, rank-adjusted (EffMindBlast,
  BlastHit -> Stun; the player at the player rank's 0.8).
- Tactics: condition 31, surrounded by at least n (CountAround before the rows: AroundOffer and AroundPlayer count
  the hostiles within 2.5 m through BP_PlotManager's AroundCount), and 6, the nearest seen (the foe in hand), join
  TacticCond; command 9, move (TacticMove: sub 6, AI_MOVE_AWAY_FROM_ENEMY_MEDIUM: from a foe closer than 13 m to
  13 m away, FleeGoal, for up to 3 s; the round strikes nothing, TacSlot -2). CombatStep backs off first
  (FleeStep), else steps as before (CombatStepOn).
SayTalent names the spells.
"""
import os
import sys

import combat_rules as cr

import ue

PM, NPC, AL = cr.PM, cr.NPC, cr.AL
F, B, VEC, I = "float", "bool", "vector", "int"
PM_CLASS = PM + "_C"

VARIABLES = {
    NPC: [("SpellPower", F), ("bStaff", B), ("Around", I), ("FleeGoal", VEC), ("FleeUntil", F)],
    PM: [("AroundCount", I)],
    AL: [("NpcSpell", F, "ARRAY")],
}
FUNCTIONS = {
    NPC: {"SetSpell": [("InSpell", "float[]"), ("K", I)], "SpellHitFoe": [("Amount", F)], "TalentEffect6": [("K", I)],
          "EffShock": [("K", I)], "ShockHit": [("From", cr.ACTOR), ("bPartySide", B), ("Amount", F)],
          "EffMindBlast": [("K", I)], "BlastHit": [("From", cr.ACTOR), ("bPartySide", B), ("Seconds", F)],
          "CountAround": [], "AroundOffer": [("From", cr.ACTOR), ("bPartySide", B), ("InMgr", PM_CLASS)],
          "AroundPlayer": [], "TacticMove": [("Sub", F)], "FleeStep": [("Dt", F)],
          "CombatStepOn": [("Dt", F), ("Dist", F)]},
    PM: {"SpellHitPlayer": [("Amount", F)], "ResetAround": [], "AroundOne": []},
}
GRAPHS = [
    (PM, ["SpellHitPlayer", "ResetAround", "AroundOne"]),
    (NPC, ["SetSpell", "SpellHitFoe", "StrikeFoe", "ShockHit", "EffShock", "BlastHit", "EffMindBlast", "TalentEffect6",
           "TalentEffect5", "AroundOffer", "AroundPlayer", "CountAround", "ChooseTactic", "TacticCond", "TacticMove",
           "TacticAct", "TacticsRound", "FleeStep", "CombatStepOn", "CombatStep", "SetNpcTactics", "SayTalent"]),
    (AL, ["GiveNpcRules", "BuildFixtures"]),
]


def setup():
    cr.setup(VARIABLES, FUNCTIONS, compile_all_after=False)
    for bp in (PM, NPC, AL):
        cr.call("compile_blueprint", {"blueprint": {"refPath": bp}})


def graphs(start=None):
    todo = [(bp, fn) for bp, names in GRAPHS for fn in names]
    if start:
        todo = todo[[fn for bp, fn in todo].index(start):]
    for bp, fn in todo:
        code = open(os.path.join(cr.HERE, "dsl", fn + ".dsl"), encoding="utf-8").read()
        cr.call("write_graph_dsl", {"graph": {"refPath": "%s:%s" % (bp, fn)}, "code": code})
        print(fn, "ok")
    for bp in (PM, NPC, AL):
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
    if phase == "graphs" and len(sys.argv) > 2:
        graphs(sys.argv[2])
    else:
        for name, f in (("setup", setup), ("graphs", graphs), ("save", save)):
            if phase in (name, "all"):
                f()
