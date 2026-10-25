"""python ranged.py [arrow|assets|setup|graphs|input|save|all]: ranged combat in the Blueprints (docs/COMBAT.md,
"Ranged combat"; the rules: tools/daotools/stats.py, simulate.py). Play/Simulate stopped; talents.py, threat.py and
enemies.py must have run.

The export brings NpcStatus 9-10 (each creature's bow range, 0 for melee, and missile shield), talent rows of 18
fields (damage bonus and aiming seconds last) and PlayerStats 20-26 (missile shield and the shortbow of the other
weapon set: damage min and max, penetration, critical chance, seconds between shots, range).

BP_DlgNPC: CombatStep sends an archer (NRange > 0) to RangedStep: within its bow's range (and 15 m) with a clear shot
(ClearShot: a Visibility trace from 1.4 m up to 60 cm short of its foe hits nothing) it stops, faces and shoots
(Bite); else it closes in. Melee creatures: MeleeStep (the old CombatStep). HitFoe shoots an arrow (ShootFx:
/Game/Cousland/Combat/BP_Arrow, a thin cylinder flying 0.3 s: Launch, Fly), takes 1 attack a metre past max(8 m,
the bow's range) and never flanks. Its sustained talents add penetration, damage bonus and aiming time (NAddOwn:
Aim). Pinning Shot roots (EffPin: RootFoe; a rooted creature does not chase), Shattering Shot takes 10 armour for
20 s and knocks down (EffShatter: ArmourFoe, StunFoe).

BP_PlotManager: AttackerState says whether the attacker shoots (ARanged: the player with the bow out, a creature
with NRange): a shot meets the target's missile shield (StrikeNpc: NMissile; StrikePlayer: PMissile). RootPlayer
(input off while rooted), ArmourPlayer. The player: Q (IA_SwitchWeapon) -> SwitchWeapon between sword and shield
and the shortbow (BowOn; PBaseInterval to BowInterval); PlayerAttack swings (MeleeAttack, as before) or shoots the
nearest visible hostile within the bow's range and 15 m (BowAttack, TalentBid), and PlayerStrikeGo uses the bow's
numbers, the range penalty, no flanking and no backstab.
"""
import os
import sys

import combat_rules as cr

import ue

PM, NPC, AL = cr.PM, cr.NPC, cr.AL
ARROW = "/Game/Cousland/Combat/BP_Arrow.BP_Arrow"
F, ACTOR, NPC_CLASS = "float", cr.ACTOR, cr.NPC_CLASS
VEC = "vector"

VARIABLES = {
    ARROW: [("AFrom", VEC), ("ATo", VEC), ("AT", F)],
    NPC: [("NRange", F), ("NMissile", F), ("bShotClear", "bool"), ("RootUntil", F), ("NArmourAdd", F),
          ("NArmourUntil", F), ("NOwnPen", F), ("NOwnBonus", F), ("NOwnAim", F), ("HFlank", F)],
    PM: [("PRootUntil", F), ("PArmourAdd", F), ("PArmourUntil", F), ("bARanged", "bool"), ("bBowOn", "bool"),
         ("PMissile", F), ("BowMin", F), ("BowMax", F), ("BowPen", F), ("BowCrit", F), ("BowInterval", F),
         ("BowRange", F), ("PMeleeInterval", F)],
}
S, K = ("Seconds", F), ("K", "int")
FUNCTIONS = {
    ARROW: {"Launch": [("From", VEC), ("To", VEC)], "Fly": []},
    NPC: {"ClearShot": [], "RangedStep": [("Dt", F), ("Dist", F)], "StopChase": [], "MeleeStep": [("Dt", F), ("Dist", F)],
          "ShootFx": [], "EffPin": [K], "EffShatter": [K], "RootFoe": [S], "RootNpcFoe": [S], "Root": [S],
          "ArmourFoe": [("Amount", F), S], "ArmourNpcFoe": [("Amount", F), S], "ArmourDebuff": [("Amount", F), S],
          "TalentEffect3": [K]},
    PM: {"RootPlayer": [S], "ArmourPlayer": [("Amount", F), S], "SetPlayerBow": [("InStats", "float[]")],
         "SwitchWeapon": [], "PlayerStrikeGo": [("Target", NPC_CLASS), ("Def", F), ("Armour", F)],
         "MeleeAttack": [], "BowAttack": []},
}
GRAPHS = [
    (ARROW, ["Fly", "Launch"]),
    (PM, ["RootPlayer", "ArmourPlayer", "PlayerRecover", "NpcAttackerState", "AttackerState", "StrikeNpc",
          "StrikePlayer", "SetPlayerBow", "SetPlayerStats", "SwitchWeapon", "LoadTalent", "AddOwn", "EndFeignSlot",
          "PlayerPummel", "PlayerStrikeGo", "PlayerStrike", "MeleeAttack", "BowAttack", "PlayerAttack"]),
    (NPC, ["SetStatus", "SetNpcTalents", "FindOne", "UsableCheck", "ClearShot", "StopChase", "ChaseFoe", "Root",
           "ArmourDebuff", "RootNpcFoe", "ArmourNpcFoe", "RootFoe", "ArmourFoe", "ShootFx", "NAddOwn", "NSumOwn",
           "HitNpcFoe", "HitFoe", "EffPummel", "EffSunder", "EffBelt", "EffPin", "EffShatter", "TalentEffect3",
           "TalentEffect2", "TalentEffect", "SayTalent", "DoTalent", "MeleeStep", "RangedStep", "CombatStep",
           "TakeStrike", "TakeAttack"]),
    (AL, ["GiveNpcRules"]),
]


def arrow():
    """BP_Arrow: an Actor with a thin cylinder lying along X (2 cm thick, 70 cm long)."""
    import pyrun
    print(pyrun.run('''
EAL = unreal.EditorAssetLibrary
path = "/Game/Cousland/Combat/BP_Arrow"
if not EAL.does_asset_exist(path):
    f = unreal.BlueprintFactory()
    f.set_editor_property("parent_class", unreal.Actor)
    bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset("BP_Arrow", "/Game/Cousland/Combat", unreal.Blueprint, f)
    sub = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    root = sub.k2_gather_subobject_data_for_blueprint(bp)[0]
    handle, fail = sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.StaticMeshComponent, blueprint_context=bp))
    data = unreal.SubobjectDataBlueprintFunctionLibrary.get_data(handle)
    comp = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(data)
    comp.set_editor_property("static_mesh", EAL.load_asset("/Engine/BasicShapes/Cylinder"))
    comp.set_editor_property("relative_scale3d", unreal.Vector(0.02, 0.02, 0.7))
    comp.set_editor_property("relative_rotation", unreal.Rotator(roll=0.0, pitch=-90.0, yaw=0.0))
    comp.set_collision_profile_name("NoCollision")
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    EAL.save_asset(path, only_if_is_dirty=False)
    OUT["made"] = fail.is_empty() if hasattr(fail, "is_empty") else str(fail)
OUT["exists"] = EAL.does_asset_exist(path)
''', 300))


def assets():
    """IA_SwitchWeapon on Q in IMC_Dialogue."""
    import pyrun
    print(pyrun.run('''
EAL = unreal.EditorAssetLibrary
factory = getattr(unreal, "InputAction_Factory", None) or getattr(unreal, "InputActionFactory")
path = "/Game/Cousland/Combat/IA_SwitchWeapon"
ia = EAL.load_asset(path) if EAL.does_asset_exist(path) else unreal.AssetToolsHelpers.get_asset_tools().create_asset("IA_SwitchWeapon", "/Game/Cousland/Combat", unreal.InputAction, factory())
imc = EAL.load_asset("/Game/Cousland/Dialogue/IMC_Dialogue")
have = {(m.action.get_name() if m.action else "", str(m.key.get_editor_property("key_name"))) for m in imc.get_editor_property("default_key_mappings").get_editor_property("mappings")}
if ("IA_SwitchWeapon", "Q") not in have:
    k = unreal.Key()
    k.set_editor_property("key_name", "Q")
    imc.map_key(ia, k)
EAL.save_asset(path, only_if_is_dirty=False)
EAL.save_asset("/Game/Cousland/Dialogue/IMC_Dialogue", only_if_is_dirty=False)
OUT["ok"] = 1
''', 120))


def setup():
    cr.setup(VARIABLES, FUNCTIONS, compile_all_after=False)
    for bp in (ARROW, PM, NPC, AL):
        cr.call("compile_blueprint", {"blueprint": {"refPath": bp}})


def graphs():
    for bp, names in GRAPHS:
        for fn in names:
            code = open(os.path.join(cr.HERE, "dsl", fn + ".dsl"), encoding="utf-8").read()
            r = cr.call("write_graph_dsl", {"graph": {"refPath": "%s:%s" % (bp, fn)}, "code": code})
            print(fn, str(r)[:300])
        cr.call("compile_blueprint", {"blueprint": {"refPath": bp}})


def input_events():
    """In BP_PlotManager's event graph: IA_SwitchWeapon Started -> SwitchWeapon."""
    g = {"refPath": PM + ":EventGraph"}
    if cr.call("find_nodes", {"graph": g, "title": "IA_SwitchWeapon"}):
        print("input: already there")
        return
    types = cr.call("find_node_types", {"graph": g, "type_id_filter": "IA_SwitchWeapon", "context_pins": []})
    ids = [t.get("type_id", t) if isinstance(t, dict) else t for t in types]
    ev = cr.call("create_node", {"graph": g, "type_id": next(i for i in ids if i.endswith("IA_SwitchWeapon")),
                                 "pos": {"x": 1600, "y": 4400}})
    use = cr.call("create_node", {"graph": g, "type_id": "Funzionedichiamata|SwitchWeapon", "pos": {"x": 2020, "y": 4400}})
    started = next(p for p in cr.pins(ev)["output_pins"] if p["name"] == "Started")
    ins = {p["name"]: p["pin_id"] for p in cr.pins(use)["input_pins"]}
    cr.call("connect_pins", {"output_pin": started["pin_id"], "input_pin": ins["execute"]})
    cr.call("compile_blueprint", {"blueprint": {"refPath": PM}})
    print("IA_SwitchWeapon -> SwitchWeapon")


def save():
    import pyrun
    print(pyrun.run('''
EAL = unreal.EditorAssetLibrary
OUT["saved"] = [EAL.save_asset(p, only_if_is_dirty=False) for p in ("/Game/Cousland/Plots/BP_PlotManager",
                "/Game/Cousland/Dialogue/BP_DlgNPC", "/Game/Cousland/Areas/BP_AreaLoader", "/Game/Cousland/Combat/BP_Arrow")]
''', 300))


if __name__ == "__main__":
    ue.init()
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, f in (("arrow", arrow), ("assets", assets), ("setup", setup), ("graphs", graphs),
                    ("input", input_events), ("save", save)):
        if phase in (name, "all"):
            f()
