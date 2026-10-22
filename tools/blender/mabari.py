"""The mabari, Ferelden's war hound, reshaped from the wolf of Epic's free Animal Variety Pack (Blender 5.2,
run headless):

blender -b --factory-startup -P mabari.py -- <SK_Wolf.fbx> <out.fbx> [preview_prefix]

<SK_Wolf.fbx> is /Game/AnimalVarietyPack/Wolf/Meshes/SK_Wolf exported from Unreal. The wolf's skeleton and
skin weights stay as they are, so all its animations (bites, hits, death, walk, run, rest) still play on
the mabari; only the body changes, from a lean, furry wolf to a heavy mastiff: the fur cards go (a short
coat), neck, chest and legs grow thicker round the line from each joint to the next, the chest deepens,
the bushy tail thins to a whip, the muzzle is shortened and broadened, the skull widened and the ears
cropped short. Vertex colour R marks the kaddis, the red war paint: a blaze down the head, a stripe along
the spine and slashes over the shoulders. Exported in centimetres (bones and vertices alike).
Blender frame: metres, the wolf faces -y, +x is its left; the back is at z ~0.61, the floor at 0.
"""
import math
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.geometry import intersect_point_line

ARGS = sys.argv[sys.argv.index("--") + 1:]
WOLF, OUT = ARGS[:2]
PREVIEW = ARGS[2] if len(ARGS) > 2 else ""

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=WOLF)
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
body = next(o for o in bpy.data.objects if o.type == "MESH")
for o in [o for o in bpy.data.objects if o.type == "EMPTY"]:  # Unreal's centimetre empty: work in metres
    for c in o.children:
        mw = c.matrix_world.copy()
        c.parent = None
        c.matrix_world = mw
    bpy.data.objects.remove(o)
bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
body.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


def joint(name):
    return arm.matrix_world @ arm.data.bones["Wolf_ " + name].head_local


# Each bone thickens round the line from its joint to the next one (the bones' own axes do not follow the
# limbs): (from, to, factor). Factors above 1 thicken, below 1 thin.
SEGMENTS = {}
for s in ("L", "R"):
    SEGMENTS.update({
        "%s Thigh" % s: (joint("%s Thigh" % s), joint("%s Calf" % s), 1.42),
        "%s Calf" % s: (joint("%s Calf" % s), joint("%s HorseLink" % s), 1.38),
        "%s HorseLink" % s: (joint("%s HorseLink" % s), joint("%s Foot" % s), 1.25),
        "%s Foot" % s: (joint("%s Foot" % s), joint("%s Foot" % s) + Vector((0, -0.12, 0)), 1.25),
        "%s Clavicle" % s: (joint("%s Clavicle" % s), joint("%s UpperArm" % s), 1.30),
        "%s UpperArm" % s: (joint("%s UpperArm" % s), joint("%s Forearm" % s), 1.55),
        "%s Forearm" % s: (joint("%s Forearm" % s), joint("%s Hand" % s), 1.48),
        "%s Hand" % s: (joint("%s Hand" % s), joint("%s Finger0" % s), 1.30),
        "%s Finger0" % s: (joint("%s Finger0" % s), joint("%s Finger0" % s) + Vector((0, -0.10, 0)), 1.25),
    })
SEGMENTS.update({
    "Neck": (joint("Neck"), joint("Neck1"), 1.25),
    "Neck1": (joint("Neck1"), joint("Neck2"), 1.22),
    "Neck2": (joint("Neck2"), joint("Head"), 1.15),
    "Tail": (joint("Tail"), joint("Tail1"), 0.55),
    "Tail1": (joint("Tail1"), joint("Tail2"), 0.40),
    "Tail2": (joint("Tail2"), joint("Tail3"), 0.32),
    "Tail3": (joint("Tail3"), joint("Tail4"), 0.30),
    "Tail4": (joint("Tail4"), joint("Tail5"), 0.30),
    "Tail5": (joint("Tail5"), joint("Tail5") + Vector((0, 0.08, -0.08)), 0.30),
})
# The trunk: wider (x) and deeper below the spine (z down), the back barely raised.
TRUNK = {"Pelvis": (1.22, 1.12), "Spine": (1.30, 1.25), "Spine1": (1.42, 1.45), "Wolf_": (1.18, 1.08)}
BACK_Z = joint("Spine").z

HEAD = joint("Head")
STOP_Y = HEAD.y - 0.075  # in front of the eyes: the muzzle starts here
MUZZLE = 0.50  # muzzle length kept
EAR_Z = HEAD.z + 0.075  # ears above this are cropped
EAR = 0.70

me = body.data
mats = [s.material.name if s.material else "" for s in body.material_slots]
groups = {g.index: g.name.replace("Wolf_ ", "") for g in body.vertex_groups}

bm = bmesh.new()
bm.from_mesh(me)
fur = mats.index("M_WolfFur") if "M_WolfFur" in mats else -1
bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index == fur], context="FACES")
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
# The wolf's mesh is split along its UV seams: weld the copies, or reshaping opens the seams into cracks.
bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.0002)
deform = bm.verts.layers.deform.active
mw = body.matrix_world
mwi = mw.inverted()

moves = {}
for v in bm.verts:
    p0 = p = mw @ v.co
    w = {groups[k]: x for k, x in v[deform].items() if k in groups}
    total = sum(w.values()) or 1.0
    delta = Vector()
    for name, wt in w.items():
        wt /= total
        if name in SEGMENTS:
            a, b, f = SEGMENTS[name]
            q, t = intersect_point_line(p, a, b)
            q = a + (b - a) * min(max(t, 0.0), 1.0)
            d = (p - q) * (f - 1.0) * wt
            if "Clavicle" in name or "UpperArm" in name:
                d.z = min(d.z, 0.0)  # shoulders grow out and down, not into a hump: the back stays level
            delta += d
        elif name in TRUNK:
            sx, sz = TRUNK[name]
            d = Vector((p.x, 0.0, min(p.z - BACK_Z, 0.0)))
            delta += Vector((d.x * (sx - 1.0), 0.0, d.z * (sz - 1.0))) * wt
    p = p + delta
    head_w = (w.get("Head", 0.0) + w.get("Ponytail1", 0.0)) / total
    if head_w > 0.0:
        h = p.copy()
        if h.y < STOP_Y:  # shorter, broader muzzle and heavier flews
            h.y = STOP_Y + (h.y - STOP_Y) * MUZZLE
            h.x *= 1.38
            h.z -= 0.018 * min(1.0, (STOP_Y - p.y) / 0.06)  # deep, square flews
        else:  # broader skull
            h.x *= 1.25
        if h.z > EAR_Z:  # cropped ears
            h.z = EAR_Z + (h.z - EAR_Z) * EAR
        p = p.lerp(h, head_w)
    moves[v] = p - p0

for v, d in moves.items():
    v.co = mwi @ ((mw @ v.co) + d)
# A light smoothing so regions reshaped by different amounts meet without creases.
for _ in range(2):
    bmesh.ops.smooth_vert(bm, verts=[v for v in bm.verts if not v.is_boundary], factor=0.25,
                          use_axis_x=True, use_axis_y=True, use_axis_z=True)

bm.to_mesh(me)
bm.free()
if fur >= 0:
    body.data.materials.pop(index=fur)
sub = body.modifiers.new("subdivide", "SUBSURF")  # smoother body, finer war paint; weights follow
sub.levels = 1
bpy.context.view_layer.objects.active = body
bpy.ops.object.modifier_apply(modifier=sub.name)
me = body.data


def kaddis(p):
    """1 inside the war paint (rest pose, metres): a blaze from the brow down the nose, a stripe along the
    spine to the tail, and two slashes over each shoulder."""
    blaze = abs(p.x) < 0.035 and p.y < HEAD.y + 0.02 and p.z > HEAD.z - 0.03
    stripe = abs(p.x) < 0.05 and -0.30 < p.y < 0.45 and p.z > BACK_Z - 0.02
    slash = False
    for k in (0, 1):
        y0 = -0.24 + 0.09 * k
        # slanting bands down the shoulder, both sides
        if abs(p.x) > 0.08 and 0.40 < p.z < BACK_Z + 0.04:
            along = p.y - y0 - (p.z - BACK_Z) * 0.6
            slash = slash or abs(along) < 0.022
    return 1.0 if (blaze or stripe or slash) else 0.0


for c in list(me.color_attributes):  # the wolf's own (white) colours would be exported first
    me.color_attributes.remove(c)
col = me.color_attributes.new("Col", "BYTE_COLOR", "CORNER")
for poly in me.polygons:
    for li in poly.loop_indices:
        p = mw @ me.vertices[me.loops[li].vertex_index].co
        col.data[li].color = (kaddis(p), 0.0, 0.0, 1.0)
me.color_attributes.active_color = col
me.color_attributes.render_color_index = me.color_attributes.active_color_index
for f in me.polygons:
    f.use_smooth = True

if PREVIEW:
    sc = bpy.context.scene
    for s in body.material_slots:  # preview colour only (the slots keep their names for Unreal)
        if s.material:
            s.material.diffuse_color = (0.45, 0.43, 0.42, 1.0)
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.color_type = "VERTEX" if "paint" in PREVIEW else "MATERIAL"
    sc.render.resolution_x, sc.render.resolution_y = 800, 500
    sc.render.film_transparent = True
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 2.3
    for name, yaw in (("side", 90), ("front", 0), ("q", 45)):
        a = math.radians(yaw)
        cam.location = Vector((5 * math.sin(a), -5 * math.cos(a), 0.5))
        cam.rotation_euler = (math.radians(90), 0, a)
        sc.render.filepath = "%s_%s.png" % (PREVIEW, name)
        bpy.ops.render.render(write_still=True)

# Export in centimetres, bones and vertices alike, as Unreal wrote the wolf.
bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True)
body.select_set(True)
bpy.context.view_layer.objects.active = arm
arm.scale = (100.0, 100.0, 100.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.context.scene.unit_settings.scale_length = 0.01
bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, object_types={"ARMATURE", "MESH"}, add_leaf_bones=False,
                         bake_anim=False, mesh_smooth_type="FACE", colors_type="LINEAR")
print("MABARI", len(me.vertices), "verts ->", OUT)
