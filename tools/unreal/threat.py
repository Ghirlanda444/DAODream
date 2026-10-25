"""python threat.py [setup|graphs|save|all]: combat stage 4's threat in the Blueprints (docs/COMBAT.md, "Threat"; the
rules: tools/daotools/threat.py). Play/Simulate stopped; talents.py must have run.

Each hostile BP_DlgNPC keeps a threat table (ThreatWho, ThreatVal) and fights its most hated enemy (Foe). Every
0.5 s, in place of BP_PlotManager.PickFoe, ThreatPick sees the player and the party members within 15 m it does not
know yet (SeePlayer, SeeMember: + the export's seen threat, PlayerStats[19] / NpcStatus), re-evaluates its target
(Retarget) and drops a fallen one. AddThreat clamps a change (ClampThreat: at least 1, never to 0 or below, at most
1000) and retargets: the first target is the most hated (MostHated, over enemies still up: WhoUp); after that
MaySwitch lets the most hated take over once TWait seconds have passed since the last switch (TSwitched; TWait grows
by 5 a switch and goes back to 0 past 25) or the target is down, unless the enemy whose threat changed is badly
wounded (KeepWounded: at 20% health or less half the time, at 10% or less 9 times in 10).

BP_PlotManager.StrikeNpc tells the struck creature its attacker (ThreatFromStrike): up to 1 for being attacked
(AttackedBy), and the damage as a percentage of its max health (DamageThreat; AttackerMul: x0.8 from a rogue, x2
while the player sustains Threaten). The player's talents: Taunt +310 and Disengage -99 on every hostile within
10 m (AreaThreat -> TauntedBy; Taunt lets them switch at once), Dirty Fighting and Shield Bash +2 and Below the
Belt +1 on their target (ImpactThreat). Feign Death hides the player: switched on, every hostile forgets them
(FeignChange -> ForgetPlayerAll -> ForgetThreat) and no hostile sees them while it lasts; other talents are refused,
health comes back 4% a second in combat (6% out of it), and any attack of the player's ends it (EndFeign).
SumOwn keeps ThreatenOn and Feign from the talents that are on. A creature cannot read another creature's variables
(its own class), so it asks BP_PlotManager.Inspect, which answers through its TakeState (WhoOk, WhoHp, InspSeen,
TMul, InspParty).
"""
import os
import sys

import combat_rules as cr
import ue

PM, NPC, AL = cr.PM, cr.NPC, cr.AL
F, ACTOR, NPC_CLASS = "float", cr.ACTOR, cr.NPC_CLASS

VARIABLES = {
    NPC: [("ThreatWho", ACTOR, "ARRAY"), ("ThreatVal", F, "ARRAY"), ("TSwitched", F), ("TWait", F), ("Seen", F),
          ("bRogueN", "bool"), ("bWhoOk", "bool"), ("WhoHp", F), ("TIdx", "int"), ("TCur", F), ("TAmt", F),
          ("HateBest", F), ("Hated", ACTOR), ("bKeep", "bool"), ("TMul", F), ("InspSeen", F),
          ("bInspParty", "bool")],
    PM: [("PSeen", F), ("bFeign", "bool"), ("bWasFeign", "bool"), ("bFeignStart", "bool"), ("bThreatenOn", "bool")],
}
FUNCTIONS = {
    NPC: {"WhoUp": [("Who", ACTOR)], "NpcUp": [("Who", ACTOR)], "WhoHealth": [("Who", ACTOR)],
          "NpcHealth": [("Who", ACTOR)], "ThreatSlot": [("Who", ACTOR)], "ClampThreat": [],
          "AddThreat": [("Who", ACTOR), ("Amount", F)], "HateCheck": [("I", "int")], "MostHated": [],
          "KeepWounded": [("Who", ACTOR)], "SwitchTo": [], "MaySwitch": [("Changed", ACTOR)],
          "Retarget": [("Changed", ACTOR)], "ForgetFoe": [("Who", ACTOR)], "ForgetThreat": [("Who", ACTOR)],
          "SeePlayer": [], "SeeMember": [("Npc", NPC_CLASS)], "DropDownFoe": [], "ThreatPick": [],
          "AttackerMul": [("Who", ACTOR)], "NpcMul": [("Who", ACTOR)], "AttackedBy": [("Who", ACTOR)],
          "DamageThreat": [("Who", ACTOR), ("Damage", F)], "ThreatFromStrike": [("Attacker", ACTOR), ("Damage", F)],
          "TauntedBy": [("Who", ACTOR), ("Amount", F), ("bTaunt", "bool")],
          "TakeState": [("bOk", "bool"), ("Hp", F), ("SeenAmt", F), ("Mul", F), ("bParty", "bool")]},
    PM: {"SetPlayerSeen": [("InStats", "float[]")], "AreaThreat": [("Amount", F), ("bTaunt", "bool")],
         "ForgetPlayerAll": [], "ImpactThreat": [], "FeignChange": [], "EndFeignSlot": [("Slot", "int")],
         "EndFeign": [], "Inspect": [("Npc", NPC_CLASS), ("Asker", NPC_CLASS)]},
}
GRAPHS = [
    (NPC, ["TakeState"]),
    (PM, ["Inspect"]),
    (NPC, ["SetStatus", "NpcUp", "WhoUp", "NpcHealth", "WhoHealth", "ThreatSlot", "ClampThreat", "HateCheck",
           "MostHated", "KeepWounded", "SwitchTo", "MaySwitch", "Retarget", "AddThreat", "ForgetFoe", "ForgetThreat",
           "SeePlayer", "SeeMember", "DropDownFoe", "ThreatPick", "HostileTurn", "NpcMul", "AttackerMul",
           "AttackedBy", "DamageThreat", "ThreatFromStrike", "TauntedBy"]),
    (PM, ["SetPlayerSeen", "SetPlayerTalentStats", "AreaThreat", "ForgetPlayerAll", "ImpactThreat", "FeignChange",
          "AddOwn", "SumOwn", "AfterTalent", "EndFeignSlot", "EndFeign", "StrikeNpc", "PlayerStrike",
          "ActivateTalent", "TargetTalent", "TalentCheck", "StaminaTick"]),
    (AL, ["GiveNpcRules"]),
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
