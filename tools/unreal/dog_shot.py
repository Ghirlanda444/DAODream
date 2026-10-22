"""Portrait-booth pictures of an animal: python dog_shot.py <SkeletalMesh path> <tag> [animation path] [seconds]

Loads /Game/Cousland/Dev/L_PortraitBooth without saving it, stands the mesh in the middle (posed by the
animation at that time, if one is given) and writes ds_<tag>_<angle>.png from six directions round it."""
import base64, json, math, sys, time
import ue, pie, pyrun


def capture(path, x, y, z, yaw, pitch=0.0):
    r = ue.call(pie.EA, "CaptureViewport", {"captureTransform": {"location": {"x": x, "y": y, "z": z},
        "rotation": {"pitch": pitch, "yaw": yaw, "roll": 0}, "scale": {"x": 1, "y": 1, "z": 1}}, "annotations": [], "bShowUI": False})
    open(path, "wb").write(base64.b64decode(json.loads(r)["returnValue"]["image"]["data"]))


ue.init()
for flag in ("BillboardSprites", "LightRadius", "Grid", "Volumes"):
    pie.cmd("ShowFlag.%s 0" % flag)
mesh, tag = sys.argv[1], sys.argv[2]
anim = sys.argv[3] if len(sys.argv) > 3 else ""
at = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
r = pyrun.run('''
MESH = %r; ANIM = %r; AT = %r
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if "L_PortraitBooth" not in unreal.EditorLevelLibrary.get_editor_world().get_path_name():
    les.load_level("/Game/Cousland/Dev/L_PortraitBooth")
for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith("ZZ_"):
        eas.destroy_actor(a)
a = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
a.set_actor_label("ZZ_Animal")
c = a.skeletal_mesh_component
c.set_skeletal_mesh_asset(unreal.load_asset(MESH))
if ANIM:
    c.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    c.override_animation_data(unreal.load_asset(ANIM), True, False, AT, 1.0)
o, e, _ = unreal.SystemLibrary.get_component_bounds(c)
OUT["bounds"] = [o.x, o.y, o.z, e.x, e.y, e.z]
eas.select_nothing()
''' % (mesh, anim, at), 300)
print(r)
ox, oy, oz, ex, ey, ez = r["bounds"]
time.sleep(10)
d = max(ex, ey) * 1.6 + 40
for ang in (0, 60, 120, 180, 240, 300):
    a = math.radians(ang)
    for i in range(2):
        capture("ds_%s_%03d.png" % (tag, ang), ox + d * math.cos(a), oy + d * math.sin(a), oz + 15, ang + 180, -6)
        time.sleep(1.5)
print("ok")
