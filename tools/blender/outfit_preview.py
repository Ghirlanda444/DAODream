"""Front, side and back pictures of a body wearing an outfit (Blender 5.2, headless, Workbench):
blender -b --factory-startup -P outfit_preview.py -- <body.fbx> <outfit.fbx> <out_prefix>
Skin is pink; the outfit's material slots blue (main), brown (second), tan (leather), grey (metal)."""
import bpy, math, sys
from mathutils import Vector
BODY, OUTFIT, PRE = sys.argv[-3:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=BODY)
body = [o for o in bpy.data.objects if o.type == "MESH"]
bpy.ops.import_scene.fbx(filepath=OUTFIT)
outfit = [o for o in bpy.data.objects if o.type == "MESH" and o not in body]
COL = [(0.12, 0.18, 0.45), (0.25, 0.2, 0.15), (0.35, 0.22, 0.12), (0.6, 0.6, 0.62)]
for o in outfit:
    for i, slot in enumerate(o.material_slots):
        m = bpy.data.materials.new("prev%d" % i)
        m.diffuse_color = (*COL[i % 4], 1.0)
        slot.material = m
for o in body:
    m = bpy.data.materials.new("skin")
    m.diffuse_color = (0.85, 0.6, 0.55, 1.0)
    for slot in o.material_slots:
        slot.material = m
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sc.display.shading.light = "STUDIO"
sc.display.shading.color_type = "MATERIAL"
sc.render.resolution_x, sc.render.resolution_y = 500, 900
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.type = "ORTHO"
cam.data.ortho_scale = 2.0
for name, yaw in (("front", 0), ("side", 90), ("back", 180)):
    a = math.radians(yaw)
    cam.location = Vector((4 * math.sin(a), -4 * math.cos(a), 0.9))
    cam.rotation_euler = (math.radians(90), 0, a)
    sc.render.filepath = "%s_%s.png" % (PRE, name)
    bpy.ops.render.render(write_still=True)
print("PREVIEW done")
