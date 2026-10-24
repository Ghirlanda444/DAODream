"""python combat_rules.py [setup|graphs|party|save|all]: the original's hit rules in the Blueprints
(docs/COMBAT.md, "Rules"). Play/Simulate stopped.

One rule for every attack, in BP_PlotManager: FlankBonus (the attacker's angle behind the target, 120-180
degrees, scales the most flanking can add), ResolveHit (critical threatened against crit x (1 + flanking/5),
hit if rand(100) < attack + 54 + flanking - defense), RollHit (the weapon roll, x1.5 on a critical), Mitigate
(minus armour rolled 70% fixed / 30% random less armour penetration, plus the damage bonus, x the rank's damage
scale above the threshold) and FloorDamage (at least 1). LastDamage holds the outcome (-1: a miss); Hits, Misses
and Crits count them for tests. StrikeNpc applies it to a creature (TakeHit or MissFeedback), StrikePlayer to
the player (HurtPlayer; at 0 health GameOver, then Restart reloads the level), PlayerStrike is the player's
attack. BP_DlgNPC: SetRules (its armour, penetration, crit, flanking and damage bonus from the area file's
NpcRules, given by BP_AreaLoader.GiveNpcRules), TakeStrike (struck by a party member: PartyFight calls it on its
target), TakeAttack (struck by the player). Graph code: dsl/<function>.dsl.

Hostiles fight the party too: every 0.5 s a hostile asks PickFoe for the nearest of the player and the standing
party members within 15 m (OfferPlayer, and FoeBid from each BP_DlgNPC to FoeOffer), chases it (ChaseFoe) and
strikes it every 2 s (Bite -> StrikeFoe: StrikePlayer on the player, else StrikeNpcFoe: TakeStrike on the
party member; the cast to BP_DlgNPC only on that branch, since a failed cast leaves by its unwired exit). A party member
at 0 health falls (KnockOut: A_Fallen, bDead and bDown) instead of dying; the player falls the same way while a
party member stands (PlayerFalls -> PlayerDown), and when nobody stands the fight is lost (MemberDown or
PlayerFalls -> GameOver). RegenTick (every 0.5 s, started by SetPlayerStats): 4 s after the last blow
(LastCombat, stamped by ResolveHit) the fallen get up with 1 health (RevivePlayer, GetUp) and everyone regains
10 health a second (RegenAll, Regen), as the game's ResurrectPartyMembers and REGENERATION_HEALTH_EXPLORE_DEFAULT.
The mabari's animation Blueprint stands it up again when its BP_DlgNPC is no longer dead (dsl/BeastWatchDeath.dsl).

Phases: setup adds variables, functions and their parameters (only to functions it creates) and compiles;
graphs writes the graphs, callees first; party points PartyFight's attack at TakeStrike (node surgery: the
graph reads back with ids the DSL cannot write); beasts writes the animals' WatchDeath; save turns the one-hit
test switch off and saves. pace (on its own) gives everyone the game's attack timing: BP_DlgNPC.Interval from the
export's NpcInterval (SetInterval, via GiveNpcRules; default 2 s) for Bite and PartyFight, the player's
PInterval from PlayerStats[12] (SetPlayerPace; default 1 s) for PlayerAttack.
"""
import json
import os
import sys

import ue

HERE = os.path.dirname(os.path.abspath(__file__))
BT = "editor_toolset.toolsets.blueprint.BlueprintTools"
PM = "/Game/Cousland/Plots/BP_PlotManager.BP_PlotManager"
NPC = "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC"
AL = "/Game/Cousland/Areas/BP_AreaLoader.BP_AreaLoader"
ACTOR = "/Script/Engine.Actor"
NPC_CLASS = NPC + "_C"

F = "float"
VARIABLES = {
    PM: [("LastDamage", F), ("LastCrit", "bool"), ("LastFlank", F), ("Hits", "int"), ("Misses", "int"),
         ("Crits", "int"), ("PArmour", F), ("PPen", F), ("PCrit", F), ("PFlank", F), ("PBonus", F),
         ("bGameOver", "bool"), ("bPlayerDown", "bool"), ("FoeBest", ACTOR), ("FoeDist", F), ("Standing", "int"),
         ("LastCombat", F), ("PInterval", F)],
    NPC: [("Armour", F), ("Pen", F), ("Crit", F), ("Flank", F), ("DmgBonus", F), ("Foe", ACTOR), ("FoeTimer", F),
          ("bDown", "bool"), ("Interval", F)],
    AL: [("NpcRules", F, "ARRAY"), ("NpcInterval", F, "ARRAY")],
}
# function -> parameters: (name, type) with type a primitive, "float[]", or an object class path
FUNCTIONS = {
    PM: {
        "FloorDamage": [],
        "Mitigate": [("Scale", F), ("Pen", F), ("Bonus", F), ("Armour", F)],
        "RollHit": [("DmgMin", F), ("DmgMax", F), ("Scale", F), ("Pen", F), ("Bonus", F), ("Armour", F)],
        "FlankBonus": [("Attacker", ACTOR), ("Target", ACTOR), ("Most", F)],
        "ResolveHit": [("Atk", F), ("Def", F), ("DmgMin", F), ("DmgMax", F), ("Scale", F), ("Crit", F), ("Pen", F),
                       ("Bonus", F), ("Armour", F)],
        "StrikeNpc": [("Attacker", ACTOR), ("Target", NPC_CLASS), ("Atk", F), ("Def", F), ("DmgMin", F),
                      ("DmgMax", F), ("Scale", F), ("Crit", F), ("Pen", F), ("Bonus", F), ("Flank", F), ("Armour", F)],
        "StrikePlayer": [("Attacker", ACTOR), ("Atk", F), ("DmgMin", F), ("DmgMax", F), ("Scale", F), ("Crit", F),
                         ("Pen", F), ("Bonus", F), ("Flank", F)],
        "PlayerStrike": [("Target", NPC_CLASS), ("Def", F), ("Armour", F)],
        "SetPlayerRules": [("InStats", "float[]")],
        "Restart": [],
        "GameOver": [],
        "FoeOffer": [("Cand", ACTOR), ("Dist", F)],
        "OfferPlayer": [("Hostile", ACTOR)],
        "PickFoe": [("Hostile", NPC_CLASS)],
        "CountStanding": [],
        "PlayerDown": [],
        "PlayerFalls": [],
        "MemberDown": [],
        "RevivePlayer": [],
        "ReviveMembers": [],
        "RegenAll": [],
        "RegenTick": [],
        "SetPlayerPace": [("InStats", "float[]")],
    },
    NPC: {
        "SetRules": [("InRules", "float[]"), ("K", "int")],
        "SetInterval": [("InInterval", F)],
        "TakeStrike": [("Attacker", ACTOR), ("InAttack", F), ("InMin", F), ("InMax", F), ("InScale", F),
                       ("InCrit", F), ("InPen", F), ("InBonus", F), ("InFlank", F)],
        "SetFoe": [("InFoe", ACTOR)],
        "FoeBid": [("InMgr", PM + "_C"), ("Hostile", ACTOR)],
        "ChaseFoe": [("Dt", F)],
        "StrikeNpcFoe": [],
        "StrikeFoe": [],
        "FoeStep": [("Dt", F)],
        "HostileTick": [("Dt", F)],
        "ShowPartyBar": [],
        "KnockOut": [],
        "Wounded": [],
        "GetUp": [],
        "Regen": [("Amount", F)],
    },
    AL: {
        "GiveNpcRules": [("Npc", NPC_CLASS), ("K", "int")],
    },
}
# Graphs written from dsl/, in order: a call's keyword pins exist only once the callee is compiled.
GRAPHS = [
    (PM, ["FloorDamage", "Mitigate", "RollHit", "FlankBonus", "ResolveHit", "StrikeNpc", "Restart", "GameOver",
          "FoeOffer", "OfferPlayer", "CountStanding", "PlayerDown", "PlayerFalls", "MemberDown", "HurtPlayer",
          "StrikePlayer", "PlayerStrike", "RevivePlayer"]),
    (NPC, ["SetRules", "SetInterval", "TakeStrike", "TakeAttack", "SetFoe", "FoeBid", "ChaseFoe", "StrikeNpcFoe", "StrikeFoe", "Bite", "CombatStep",
           "ShowPartyBar", "KnockOut", "Wounded", "TakeHit", "GetUp", "Regen"]),
    (PM, ["PickFoe", "ReviveMembers", "RegenAll", "RegenTick", "SetPlayerRules", "SetPlayerPace", "SetPlayerStats"]),
    (NPC, ["FoeStep", "HostileTick", "CombatTick"]),
    (AL, ["GiveNpcRules", "GiveNpcAlly", "BuildFixtures"]),
]
BEASTS = ("/Game/ThirdParty/Mabari/ABP_Mabari.ABP_Mabari", "/Game/ThirdParty/GiantRat/ABP_GiantRat.ABP_GiantRat")


def call(tool, args):
    r = ue.call(BT, tool, args)
    if r.startswith("TOOL ERROR"):
        raise RuntimeError(tool + ": " + r[:800])
    return json.loads(r)["returnValue"] if r.startswith("{") else r


def compile_all():
    for bp in (PM, NPC, AL):
        call("compile_blueprint", {"blueprint": {"refPath": bp}})


def setup():
    for bp, variables in VARIABLES.items():
        for v in variables:
            args = {"blueprint": {"refPath": bp}, "name": v[0], "type_name": v[1]}
            if len(v) > 2:
                args["container_type"] = v[2]
            try:
                if v[1].startswith("/"):
                    call("add_object_variable", {"blueprint": {"refPath": bp}, "name": v[0],
                                                 "object_class": {"refPath": v[1]}})
                else:
                    call("add_variable", args)
            except RuntimeError as e:  # already there from an earlier run
                print("variable", v[0], str(e)[:160])
    for bp, functions in FUNCTIONS.items():
        have = {g["refPath"].split(":")[-1] for g in call("list_graphs", {"blueprint": {"refPath": bp}})}
        for fn, params in functions.items():
            if fn in have:
                continue
            g = call("add_function_graph", {"blueprint": {"refPath": bp}, "graph_name": fn})
            for name, kind in params:
                if kind.startswith("/"):
                    call("add_object_function_param", {"graph": g, "param_name": name, "input_param": True,
                                                       "object_class": {"refPath": kind}})
                elif kind.endswith("[]"):
                    call("add_function_param", {"graph": g, "param_name": name, "param_type": kind[:-2],
                                                "input_param": True, "container_type": "ARRAY"})
                else:
                    call("add_function_param", {"graph": g, "param_name": name, "param_type": kind, "input_param": True})
            print("function", fn)
    compile_all()


def graphs():
    for bp, names in GRAPHS:
        for fn in names:
            code = open(os.path.join(HERE, "dsl", fn + ".dsl"), encoding="utf-8").read()
            r = call("write_graph_dsl", {"graph": {"refPath": "%s:%s" % (bp, fn)}, "code": code})
            print(fn, str(r)[:300])
        call("compile_blueprint", {"blueprint": {"refPath": bp}})


def pins(node):
    return call("get_node_infos", {"nodes": [node]})[0]


def party():
    """PartyFight's TakeAttack(target, attack, damage...) becomes TakeStrike(target: attacker self, the same
    attack and damage, and its crit, penetration, damage bonus and flanking)."""
    g = {"refPath": NPC + ":PartyFight"}
    old = [n for n in call("find_nodes", {"graph": g, "title": "TakeAttack"})]
    if not old:
        print("PartyFight: no TakeAttack left")
        return
    old = old[0]
    sources = {p["name"]: p["connected_pins"] for p in pins(old)["input_pins"]}
    pos = {"x": 0, "y": 600}
    new = call("create_node", {"graph": g, "type_id": "Funzionedichiamata|TakeStrike", "pos": pos})
    ins = {p["name"]: p["pin_id"] for p in pins(new)["input_pins"]}
    for name in ("execute", "self", "InAttack", "InMin", "InMax", "InScale"):
        for src in sources.get(name, []):
            call("connect_pins", {"output_pin": src, "input_pin": ins[name]})
    me = call("create_node", {"graph": g, "type_id": "Variabili|Ottieniunriferimentoasestesso", "pos": pos})
    call("connect_pins", {"output_pin": pins(me)["output_pins"][0]["pin_id"], "input_pin": ins["Attacker"]})
    for name, var in (("InCrit", "Crit"), ("InPen", "Pen"), ("InBonus", "DmgBonus"), ("InFlank", "Flank")):
        get = call("create_node", {"graph": g, "type_id": "Variabili|Predefinito|Ottieni" + var, "pos": pos})
        call("connect_pins", {"output_pin": pins(get)["output_pins"][0]["pin_id"], "input_pin": ins[name]})
    call("delete_node", {"node": old})
    call("compile_blueprint", {"blueprint": {"refPath": NPC}})
    print("PartyFight: TakeAttack -> TakeStrike")


def beasts():
    code = open(os.path.join(HERE, "dsl", "BeastWatchDeath.dsl"), encoding="utf-8").read()
    for abp in BEASTS:
        print(abp, call("write_graph_dsl", {"graph": {"refPath": abp + ":WatchDeath"}, "code": code}))
        call("compile_blueprint", {"blueprint": {"refPath": abp}})


# The game's attack timing (the export's NpcInterval and PlayerStats[12], stats.attack_interval): written graphs
# and the two fixed waits the read-back graphs hold, wired to the variables instead.
PACE_GRAPHS = [(NPC, ["SetInterval", "Bite"]), (PM, ["SetPlayerPace", "SetPlayerStats"]),
               (AL, ["GiveNpcRules", "BuildFixtures"])]
PACE_WIRES = [(NPC, "PartyFight", "1.5", "Variabili|Predefinito|OttieniInterval"),  # SetAttackTimer 1.5
              (PM, "PlayerAttack", "1.0", "Variabili|Predefinito|OttieniPInterval")]  # at most once a second


def pace():
    setup()
    for bp, names in PACE_GRAPHS:
        for fn in names:
            code = open(os.path.join(HERE, "dsl", fn + ".dsl"), encoding="utf-8").read()
            print(fn, str(call("write_graph_dsl", {"graph": {"refPath": "%s:%s" % (bp, fn)}, "code": code}))[:200])
        call("compile_blueprint", {"blueprint": {"refPath": bp}})
    for bp, graph, literal, getter in PACE_WIRES:
        g = {"refPath": "%s:%s" % (bp, graph)}
        wired = 0
        for node in call("find_nodes", {"graph": g, "title": ""}):
            for p in pins(node)["input_pins"]:
                if p["value"] == literal and not p["connected_pins"] and "Float" in p["type_id"]:
                    get = call("create_node", {"graph": g, "type_id": getter, "pos": {"x": 0, "y": 900}})
                    call("connect_pins", {"output_pin": pins(get)["output_pins"][0]["pin_id"], "input_pin": p["pin_id"]})
                    wired += 1
        print(graph, "wired", wired)
        call("compile_blueprint", {"blueprint": {"refPath": bp}})
    import pyrun
    print(pyrun.run('''
EAL = unreal.EditorAssetLibrary
for path, var, value in (("/Game/Cousland/Dialogue/BP_DlgNPC", "Interval", 2.0), ("/Game/Cousland/Plots/BP_PlotManager", "PInterval", 1.0)):
    unreal.get_default_object(EAL.load_asset(path).generated_class()).set_editor_property(var, value)
OUT["ok"] = 1
''', 120))
    save()


def save():
    import pyrun
    print(pyrun.run('''
EAL = unreal.EditorAssetLibrary
pm = EAL.load_asset("/Game/Cousland/Plots/BP_PlotManager")
unreal.get_default_object(pm.generated_class()).set_editor_property("bOneShot", False)
OUT["saved"] = [EAL.save_asset(p, only_if_is_dirty=False) for p in ("/Game/Cousland/Plots/BP_PlotManager",
                "/Game/Cousland/Dialogue/BP_DlgNPC", "/Game/Cousland/Areas/BP_AreaLoader",
                "/Game/ThirdParty/Mabari/ABP_Mabari", "/Game/ThirdParty/GiantRat/ABP_GiantRat")]
''', 300))


if __name__ == "__main__":
    ue.init()
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    if phase == "pace":
        pace()
    for name, f in (("setup", setup), ("graphs", graphs), ("party", party), ("beasts", beasts), ("save", save)):
        if phase in (name, "all"):
            f()
