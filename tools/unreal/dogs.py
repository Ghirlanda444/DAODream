"""python dogs.py [setup|graphs|save|all]: the dogs' Shred, Mabari Howl and Overwhelm in the Blueprints (docs/COMBAT.md,
"The party's talents"; the rules: tools/daotools/abilities.py EFFECTS). Play/Simulate stopped; party.py must have run.

BP_DlgNPC, TalentEffect4 -> TalentEffect5:
- Shred (EffShred): a blow whose critical chance is raised past certain, then, if it struck, the damage again over
  the row's seconds (BleedFoe: Bleed on a creature, BP_PlotManager.BleedPlayer on the player; BleedTick from
  HostileTick and PartyAct, PlayerBleedTick from HeroTick, take it a second at a time).
- Mabari Howl (EffHowl): every creature hostile to the dog within 10 m (HowlHit: a party dog's are the hostiles, a
  war dog's the party and the player) and not of a special rank (its effect duration scale, the rank's, 0.78 or
  more: lieutenants 0.75 and bosses 0.6 are spared) stunned the row's seconds, no resistance, no rank adjustment.
- Overwhelm (EffOverwhelm): a humanoid (BP_PlotManager.CheckBeast: not a creature whose look is the mabari's or the
  giant rat's, by the look actor's name: a cast would tie BP_DlgNPC to the third-party assets kept out of the repo)
  is held the row's seconds (OverwhelmHold, PinFoe: Pin, or StunPlayer) while the dog bites twice, blows that land
  and are never critical; an animal just gets a bite (the original's AI would not try).
SayTalent names them.
"""
import os
import sys

import combat_rules as cr

import ue

PM, NPC = cr.PM, cr.NPC
F, B, K = "float", "bool", ("K", "int")
S, A = ("Seconds", F), ("Amount", F)

VARIABLES = {
    NPC: [("BleedRate", F), ("BleedUntil", F)],
    PM: [("PBleedRate", F), ("PBleedUntil", F), ("bBeastFoe", B)],
}
FUNCTIONS = {
    NPC: {"TalentEffect5": [K], "EffShred": [K], "BleedFoe": [A, S], "Bleed": [A, S], "BleedTick": [("Dt", F)],
          "EffHowl": [K], "HowlHit": [("From", cr.ACTOR), ("bPartySide", B), S], "EffOverwhelm": [K],
          "OverwhelmHold": [K], "PinFoe": [S], "Pin": [S]},
    PM: {"BleedPlayer": [A, S], "PlayerBleedTick": [("Dt", F)], "CheckBeast": [("Who", cr.ACTOR)],
         "CheckBeastLook": [("Look", cr.ACTOR)]},
}
GRAPHS = [
    (PM, ["BleedPlayer", "PlayerBleedTick", "HeroTick", "CheckBeastLook", "CheckBeast"]),
    (NPC, ["Bleed", "BleedTick", "BleedFoe", "EffShred", "HowlHit", "EffHowl", "Pin", "PinFoe", "OverwhelmHold", "EffOverwhelm",
           "TalentEffect5", "TalentEffect4", "SayTalent", "HostileTick", "PartyAct"]),
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
