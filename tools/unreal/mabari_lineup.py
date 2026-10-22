"""python mabari_lineup.py <tag> [animation path]: every coat in mabari_coats.COATS side by side in the portrait
booth (the level is not saved), pictures from the front and three-quarter front: ml_<tag>_front/_q.png."""
import base64, json, math, sys, time
import ue, pie, pyrun
from mabari_coats import COATS


def capture(path, x, y, z, yaw, pitch=0.0):
    r = ue.call(pie.EA, "CaptureViewport", {"captureTransform": {"location": {"x": x, "y": y, "z": z},
        "rotation": {"pitch": pitch, "yaw": yaw, "roll": 0}, "scale": {"x": 1, "y": 1, "z": 1}}, "annotations": [], "bShowUI": False})
    open(path, "wb").write(base64.b64decode(json.loads(r)["returnValue"]["image"]["data"]))


ue.init()
for flag in ("BillboardSprites", "LightRadius", "Grid", "Volumes"):
    pie.cmd("ShowFlag.%s 0" % flag)
tag = sys.argv[1]
anim = sys.argv[2] if len(sys.argv) > 2 else "/Game/AnimalVarietyPack/Wolf/Animations/ANIM_Wolf_IdleBreathe"
coats = [(name, list(c) + [b, k]) for name, (c, b, k) in COATS.items()]
r = pyrun.run('''
COATS = %r; ANIM = %r
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if "L_PortraitBooth" not in unreal.EditorLevelLibrary.get_editor_world().get_path_name():
    les.load_level("/Game/Cousland/Dev/L_PortraitBooth")
for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith("ZZ_"):
        eas.destroy_actor(a)
mesh = unreal.load_asset("/Game/ThirdParty/Mabari/SK_Mabari")
for i, (name, data) in enumerate(COATS):
    # in a row along X, each dog facing -Y... spaced 70 cm apart
    a = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector((i - (len(COATS) - 1) / 2) * 70, 0, 0), unreal.Rotator(0, 0, 0))
    a.set_actor_label("ZZ_Mabari_" + name)
    c = a.skeletal_mesh_component
    c.set_skeletal_mesh_asset(mesh)
    for k, v in enumerate(data):
        c.set_custom_primitive_data_float(k, v)
    c.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    c.override_animation_data(unreal.load_asset(ANIM), True, False, 0.4, 1.0)
eas.select_nothing()
OUT["n"] = len(COATS)
''' % (coats, anim), 300)
print(r)
time.sleep(10)
n = r["n"]
half = (n - 1) / 2 * 70
qx, qy = half + 220, 330  # the dogs face +Y
views = {"front": (0, 560, 75, -90, -4), "q": (qx, qy, 110, math.degrees(math.atan2(-qy, -qx)), -10)}
for nm, (x, y, z, yaw, pitch) in views.items():
    for i in range(2):
        capture("ml_%s_%s.png" % (tag, nm), x, y, z, yaw, pitch)
        time.sleep(1.5)
print("ok", [c[0] for c in coats])
