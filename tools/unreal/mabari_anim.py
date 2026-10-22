"""python mabari_anim.py [folder]: the mabari's animation and look actor, in the git-ignored folder
(default /Game/ThirdParty/Mabari, next to SK_Mabari from mabari_build.body.py). Play/Simulate stopped.

  BS_MabariMove  blend space by Speed: the wolf's IdleBreathe (0), Walk (93 cm/s) and Run (444 cm/s),
                 the speeds their root-motion versions cover.
  ABP_Mabari     AnimGraph: the blend space, then the DefaultSlot (bites and flinches), then a blend by Fallen
                 to the wolf's Death at DeathTime (it holds the last frame: the body stays), to the output pose.
                 Each update (UpdateSpeed) measures how far the dog moved (the stand-in is moved by script,
                 not physics), and WatchNpc reads the BP_DlgNPC the dog is attached to: when its AttackTimer
                 is reset upward (an attack) the wolf's Bite plays, when its Health drops GetHitFront, and once
                 it is dead (WatchDeath) the dog falls; one already dead when first seen lies there at once.
  BP_Mabari      a SkeletalMeshActor with SK_Mabari and ABP_Mabari, no collision, always at scale 1 (its
                 construction script), whatever the stand-in's scale. BP_DlgNPC's look "mabari" spawns it.

Builds from scratch: delete the three assets first to rebuild them. Graph code: dsl/Mabari*.dsl. Build only
in the one folder: graph nodes find the blend space and functions by name, so a second copy elsewhere
would be wired to the first.
"""
import json
import os
import sys

import pyrun
import ue

HERE = os.path.dirname(os.path.abspath(__file__))
BT = "editor_toolset.toolsets.blueprint.BlueprintTools"
WOLF = "/Game/AnimalVarietyPack/Wolf"

ASSETS = r'''
AT = unreal.AssetToolsHelpers.get_asset_tools(); EAL = unreal.EditorAssetLibrary
if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world():
    raise RuntimeError("stop Play/Simulate first")
for n in ("BS_MabariMove", "ABP_Mabari", "BP_Mabari"):
    if EAL.does_asset_exist(D + "/" + n):
        raise RuntimeError(D + "/" + n + " exists: delete it to rebuild")
sk = EAL.load_asset(WOLF + "/Meshes/SK_Wolf_Skeleton")
f = unreal.BlendSpaceFactory1D(); f.set_editor_property("target_skeleton", sk)
bs = AT.create_asset("BS_MabariMove", D, unreal.BlendSpace1D, f)
bp = list(bs.get_editor_property("blend_parameters"))
bp[0].set_editor_property("display_name", "Speed"); bp[0].set_editor_property("min", 0.0)
bp[0].set_editor_property("max", 600.0); bp[0].set_editor_property("grid_num", 12)
bs.set_editor_property("blend_parameters", bp)
samples = []
for anim, v in (("IdleBreathe", 0.0), ("Walk", 93.0), ("Run", 444.0)):
    s = unreal.BlendSample()
    s.set_editor_property("animation", EAL.load_asset(WOLF + "/Animations/ANIM_Wolf_" + anim))
    s.set_editor_property("sample_value", unreal.Vector(v, 0, 0))
    samples.append(s)
bs.set_editor_property("sample_data", samples)
bs.set_editor_property("axis_to_scale_animation", unreal.BlendSpaceAxis.BSA_X)
EAL.save_loaded_asset(bs)
f = unreal.AnimBlueprintFactory()
f.set_editor_property("target_skeleton", sk)
f.set_editor_property("parent_class", unreal.AnimInstance)
EAL.save_loaded_asset(AT.create_asset("ABP_Mabari", D, unreal.AnimBlueprint, f))
f = unreal.BlueprintFactory(); f.set_editor_property("parent_class", unreal.SkeletalMeshActor)
EAL.save_loaded_asset(AT.create_asset("BP_Mabari", D, unreal.Blueprint, f))
'''

LOOK = r'''
EAL = unreal.EditorAssetLibrary
bp = EAL.load_asset(D + "/BP_Mabari")
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
c = unreal.get_default_object(bp.generated_class()).skeletal_mesh_component
c.set_editor_property("skeletal_mesh_asset", EAL.load_asset(D + "/SK_Mabari"))
c.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
c.set_editor_property("anim_class", EAL.load_asset(D + "/ABP_Mabari").generated_class())
c.set_editor_property("visibility_based_anim_tick_option", unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE)
c.set_collision_profile_name("NoCollision")
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
OUT["saved"] = [EAL.save_asset(D + "/" + n, only_if_is_dirty=False) for n in ("ABP_Mabari", "BP_Mabari")]
'''


def call(tool, args):
    r = ue.call(BT, tool, args)
    if r.startswith("TOOL ERROR"):
        raise RuntimeError(tool + ": " + r[:600])
    return json.loads(r)["returnValue"]


def dsl(bp, graph, name):
    code = open(os.path.join(HERE, "dsl", name), encoding="utf-8").read()
    call("write_graph_dsl", {"graph": {"refPath": "%s:%s" % (bp, graph)}, "code": code})


def pin(node, out, i):
    return {"direction": "EGPD_Output" if out else "EGPD_Input", "index_id": i, "node": node}


def connect(a, b):
    call("connect_pins", {"output_pin": a, "input_pin": b})


def build(d):
    print("assets", pyrun.run("D = %r\nWOLF = %r\n" % (d, WOLF) + ASSETS, 300))
    abp = {"refPath": "%s/ABP_Mabari.ABP_Mabari" % d}
    for name, kind in (("Speed", "float"), ("LastPos", "Vector"), ("LastAttack", "float"), ("LastHealth", "float"),
                       ("Fallen", "bool"), ("DeathTime", "float")):
        call("add_variable", {"blueprint": abp, "name": name, "type_name": kind})
    g = call("add_function_graph", {"blueprint": abp, "graph_name": "UpdateSpeed"})
    call("add_function_param", {"graph": g, "param_name": "Dt", "param_type": "float", "input_param": True})
    call("add_function_graph", {"blueprint": abp, "graph_name": "WatchNpc"})
    for fn in ("WatchBite", "WatchHit", "WatchDeath"):
        g = call("add_function_graph", {"blueprint": abp, "graph_name": fn})
        call("add_object_function_param", {"graph": g, "param_name": "Npc", "input_param": True,
                                           "object_class": {"refPath": "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"}})
    call("compile_blueprint", {"blueprint": abp})
    # callees first: a call's keyword pins exist only once the callee is compiled
    for fn in ("WatchBite", "WatchHit", "WatchDeath", "WatchNpc", "UpdateSpeed"):
        dsl(abp["refPath"], fn, "Mabari%s.dsl" % fn)
    # AnimGraph: blend space player (X = Speed) -> DefaultSlot -> blend by Fallen (true: Death at DeathTime) -> output
    ag = {"refPath": abp["refPath"] + ":AnimGraph"}
    node = lambda g, t, x: call("create_node", {"graph": g, "type_id": t, "pos": {"x": x, "y": 0}})
    player = node(ag, "Animazione|Spazidifusione|GiocatoreBlendspace'BS_MabariMove'", -600)
    slot = node(ag, "Animation|Montage|Slot'DefaultSlot'", -250)
    speed = node(ag, "Variabili|Predefinito|OttieniSpeed", -900)
    root = [n for n in call("find_nodes", {"graph": ag, "title": ""}) if "Root" in n["refPath"]][0]
    connect(pin(speed, True, 0), pin(player, False, 0))
    connect(pin(player, True, 0), pin(slot, False, 0))
    blend = node(ag, "Animation|Blends|Fusioneposeperbool", 100)
    death = node(ag, "Animazione|Sequenze|Valuta'ANIM_Wolf_Death'", -250)
    fallen = node(ag, "Variabili|Predefinito|OttieniFallen", -250)
    time = node(ag, "Variabili|Predefinito|OttieniDeathTime", -550)
    connect(pin(time, True, 0), pin(death, False, 0))
    connect(pin(death, True, 0), pin(blend, False, 0))  # BlendPose_0: true
    connect(pin(slot, True, 0), pin(blend, False, 1))
    connect(pin(fallen, True, 0), pin(blend, False, 4))
    call("set_pin_value", {"pin": pin(blend, False, 2), "value": "0.2"})
    connect(pin(blend, True, 0), pin(root, False, 0))
    # EventGraph: Blueprint Update Animation -> UpdateSpeed(DeltaTimeX)
    eg = {"refPath": abp["refPath"] + ":EventGraph"}
    event = call("find_nodes", {"graph": eg, "title": "", "entry_points_only": True})[0]
    upd = node(eg, "Funzionedichiamata|UpdateSpeed", 400)
    connect(pin(event, True, 1), pin(upd, False, 0))
    connect(pin(event, True, 2), pin(upd, False, 2))
    call("compile_blueprint", {"blueprint": abp})
    dsl("%s/BP_Mabari.BP_Mabari" % d, "UserConstructionScript", "MabariConstruction.dsl")
    print("look", pyrun.run("D = %r\n" % d + LOOK, 300))


if __name__ == "__main__":
    ue.init()
    build(sys.argv[1] if len(sys.argv) > 1 else "/Game/ThirdParty/Mabari")
