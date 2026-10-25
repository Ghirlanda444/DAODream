"""python party.py [setup|graphs|save|all]: the party fights by its talents and tactics in the Blueprints
(docs/COMBAT.md, "The party's talents"; the rules: tools/daotools/abilities.py follower_talents, simulate.py).
Play/Simulate stopped; talents.py, threat.py, enemies.py and ranged.py must have run.

The export gives the followers (the Teyrna, the dog) their talents and tactics the way the game rebuilds them when
they join, and the Teyrna her longbow and night armour (NpcTalents, NpcTactics, NpcStatus as for hostiles).

BP_DlgNPC: a party member's PartyAct gets back a second of stamina a second, stands while stunned or knocked down
(StunUntil, KnockUntil; Recover gets it up), then fights its assigned target (PartyFight: it becomes its Foe and
FoeStep runs the hostiles' CombatStep: an archer keeps its range and shoots, the rest close in; each attack round
ChooseTactic, DoTalent or StrikeFoe) or follows the player. The dogs' talents (TalentEffect4): Growl (EffGrowl:
DefenseFoe, its defense change for its seconds: DefenseDebuff on a creature, unless it resists; DefensePlayer on the
player), Charge (EffCharge: a blow, and a hit knocks down: KnockResist on a creature, unless it resists;
StunPlayer on the player); Rapid Shot is a mode (its aiming time and no criticals through NSumOwn). A creature's
debuffed defense counts when it is struck (TakeStrike, TakeAttack: NDefAdd until NDefUntil), the player's in
StrikePlayer (PDefAdd until PDefUntil). SayTalent names them.
"""
import os
import sys

import combat_rules as cr

import ue

PM, NPC = cr.PM, cr.NPC
F = "float"

VARIABLES = {
    NPC: [("NDefAdd", F), ("NDefUntil", F)],
    PM: [("PDefAdd", F), ("PDefUntil", F)],
}
S, K, A = ("Seconds", F), ("K", "int"), ("Amount", F)
FUNCTIONS = {
    NPC: {"TalentEffect4": [K], "EffGrowl": [K], "EffCharge": [K], "KnockResist": [S], "DefenseFoe": [A, S],
          "DefenseDebuff": [A, S]},
    PM: {"DefensePlayer": [A, S]},
}
GRAPHS = [
    (PM, ["DefensePlayer", "StrikePlayer"]),
    (NPC, ["DefenseDebuff", "KnockResist", "DefenseFoe", "EffGrowl", "EffCharge", "TalentEffect4", "TalentEffect3",
           "SayTalent", "TakeStrike", "TakeAttack", "PartyFight", "PartyAct"]),
]


def setup():
    cr.setup(VARIABLES, FUNCTIONS, compile_all_after=False)
    for bp in (PM, NPC):
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
                "/Game/Cousland/Dialogue/BP_DlgNPC")]
''', 300))


if __name__ == "__main__":
    ue.init()
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, f in (("setup", setup), ("graphs", graphs), ("save", save)):
        if phase in (name, "all"):
            f()
