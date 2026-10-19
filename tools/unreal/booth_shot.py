"""Portrait-booth pictures of a built MetaHuman: python booth_shot.py <Name> <tag> [exposure]

Loads /Game/Cousland/Dev/L_PortraitBooth (grey backdrop, key/fill/rim lights, fixed exposure), spawns
BP_MHC_<Name> there without saving the level, hides everything below the head and writes
bt_<tag>_f.png (front), bt_<tag>_q.png (three-quarter) and bt_<tag>_s.png (side, nose to the left).
Run it with nothing else using the GPU (a parallel AI job crashed the editor once)."""
import base64, json, math, sys, time
import ue, pie, pyrun


def capture(path, x, y, z, yaw, pitch=0.0):
    r = ue.call(pie.EA, "CaptureViewport", {"captureTransform": {"location": {"x": x, "y": y, "z": z},
        "rotation": {"pitch": pitch, "yaw": yaw, "roll": 0}, "scale": {"x": 1, "y": 1, "z": 1}}, "annotations": [], "bShowUI": False})
    open(path, "wb").write(base64.b64decode(json.loads(r)["returnValue"]["image"]["data"]))


ue.init()
for flag in ("BillboardSprites", "LightRadius", "Grid", "Volumes"):
    pie.cmd("ShowFlag.%s 0" % flag)   # no editor icons or outlines in the pictures
name, tag = sys.argv[1], sys.argv[2]
expo = float(sys.argv[3]) if len(sys.argv) > 3 else None
body = '''
N = %r; EXPO = %r
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if "L_PortraitBooth" not in unreal.EditorLevelLibrary.get_editor_world().get_path_name():
    les.load_level("/Game/Cousland/Dev/L_PortraitBooth")
for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith("ZZ_") or "MetaHumanDefaultEditorPipelineActor" in a.get_class().get_name():
        eas.destroy_actor(a)
    elif EXPO is not None and a.get_actor_label() == "Booth_Exposure":
        s = a.settings; s.set_editor_property("auto_exposure_bias", EXPO); a.set_editor_property("settings", s)
cls = unreal.load_asset("/Game/MetaHumans/MHC_%%s/BP_MHC_%%s" %% (N, N)).generated_class()
a = eas.spawn_actor_from_class(cls, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0)); a.set_actor_label("ZZ_Sitter")
for c in a.get_components_by_class(unreal.LODSyncComponent):
    c.set_editor_property("forced_lod", 0)
fc = [c for c in a.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name() == "Face"][0]
h = fc.get_socket_location("head"); OUT["head"] = [h.x, h.y, h.z]
eas.select_nothing()
for c in a.get_components_by_class(unreal.SkeletalMeshComponent):
    if c.get_name() != "Face": c.set_visibility(False, False)
''' % (name, expo)
r = pyrun.run(body, 300)
hx, hy, hz = r["head"]
time.sleep(15)
E = (hx, hy + 1, hz + 7)
for nm, ang in (("f", 90), ("q", 45), ("s", 180)):   # side from his right (the +X side is blocked), mirrored below
    a = math.radians(ang); d = 60
    for i in range(2):
        capture("bt_%s_%s.png" % (tag, nm), E[0] + d * math.cos(a), E[1] + d * math.sin(a), E[2], ang + 180, 0); time.sleep(2)
from PIL import Image, ImageOps
ImageOps.mirror(Image.open("bt_%s_s.png" % tag)).save("bt_%s_s.png" % tag)
print("ok", r["head"])
