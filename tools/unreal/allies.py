"""python allies.py [setup|graphs|save|all]: allies in the fights (docs/COMBAT.md, "Allies"; the rules: tools/daotools/
simulate.py allies). Play/Simulate stopped; spells.py must have run.

The castle's guards and Gilmore at night fight on the player's side without joining the party (NpcAlly: AllyTick,
AllyFight, the party's code: tactics, talents, keeping range). Here hostiles get to fight them too: an ally keeps its
own AllyOn (an ally, not dead, not hostile, not hidden; the manager cannot see a creature's hidden flag), and
BP_PlotManager.Inspect counts it as one of the party's side (bParty) when a hostile looks around for threat
(SeeMember), so it draws threat, is picked and struck as party members are.

Immortal (NpcImmortal: the template's flag, Gilmore; the area script's, the main hall's two guards): BuildFixtures
reads it, GiveNpcAlly -> GiveNpcImmortal -> SetImmortal; TakeHit keeps such a creature at 1 health at least.
"""
import os
import sys

import combat_rules as cr

import ue

PM, NPC, AL = cr.PM, cr.NPC, cr.AL
B = "bool"

VARIABLES = {
    NPC: [("bAllyOn", B), ("bImmortal", B)],
    AL: [("NpcImmortal", "int", "ARRAY")],
}
FUNCTIONS = {
    NPC: {"SetImmortal": [("bOn", B)]},
    AL: {"GiveNpcImmortal": [("Npc", cr.NPC_CLASS), ("K", "int")]},
}
GRAPHS = [
    (NPC, ["SetImmortal", "TakeHit", "AllyTick"]),
    (PM, ["Inspect"]),
    (AL, ["GiveNpcImmortal", "GiveNpcAlly", "BuildFixtures"]),
]


def setup():
    cr.setup(VARIABLES, FUNCTIONS, compile_all_after=False)
    for bp in (PM, NPC, AL):
        cr.call("compile_blueprint", {"blueprint": {"refPath": bp}})


def graphs():
    for bp, names in GRAPHS:
        for fn in names:
            code = open(os.path.join(cr.HERE, "dsl", fn + ".dsl"), encoding="utf-8").read()
            cr.call("write_graph_dsl", {"graph": {"refPath": "%s:%s" % (bp, fn)}, "code": code})
            print(fn, "ok")
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
