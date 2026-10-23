"""The giant rat, reshaped from the fox of Epic's free Animal Variety Pack (Blender 5.2, run headless), as
tools/blender/mabari.py makes the mabari from its wolf:

blender -b --factory-startup -P rat.py -- <SK_Fox.fbx> <out.fbx> [preview_prefix]

<SK_Fox.fbx> is /Game/AnimalVarietyPack/Fox/Meshes/SK_Fox exported from Unreal. The fox's skeleton and skin
weights stay as they are, so all its animations (bites, hits, death, walk, run, rest) still play on the rat;
only the body changes: the fur cards go, the bushy tail thins to a bare tapering rat's tail, the tall ears
shrink to short round ones, the back hunches, the haunches and neck grow heavy, the lower legs thin, and the
muzzle gets longer and narrower. Vertex colour R marks the bare pink skin (tail, ears, paws, the tip
of the nose), which M_Mabari paints in its "Kaddis" colour (MI_GiantRat sets it to flesh pink). Exported in
centimetres (bones and vertices alike). Blender frame: metres, the fox faces -y, +x is its left; the back is
at z ~0.32, the floor at 0.
"""
import math
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.geometry import intersect_point_line

ARGS = sys.argv[sys.argv.index("--") + 1:]
FOX, OUT = ARGS[:2]
PREVIEW = ARGS[2] if len(ARGS) > 2 else ""

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FOX)
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
    return arm.matrix_world @ arm.data.bones["Fox_ " + name].head_local


# Each bone thickens or thins round the line from its joint to the next one: (from, to, factor).
SEGMENTS = {}
for s in ("L", "R"):
    SEGMENTS.update({
        "%s Thigh" % s: (joint("%s Thigh" % s), joint("%s Calf" % s), 1.50),
        "%s Calf" % s: (joint("%s Calf" % s), joint("%s HorseLink" % s), 1.15),
        "%s HorseLink" % s: (joint("%s HorseLink" % s), joint("%s Foot" % s), 0.80),
        "%s Foot" % s: (joint("%s Foot" % s), joint("%s Foot" % s) + Vector((0, -0.06, 0)), 0.85),
        "%s Clavicle" % s: (joint("%s Clavicle" % s), joint("%s UpperArm" % s), 1.12),
        "%s UpperArm" % s: (joint("%s UpperArm" % s), joint("%s Forearm" % s), 1.30),
        "%s Forearm" % s: (joint("%s Forearm" % s), joint("%s Hand" % s), 0.85),
        "%s Hand" % s: (joint("%s Hand" % s), joint("%s Finger0" % s), 0.85),
        "%s Finger0" % s: (joint("%s Finger0" % s), joint("%s Finger0" % s) + Vector((0, -0.05, 0)), 0.85),
    })
SEGMENTS.update({
    "Neck": (joint("Neck"), joint("Neck1"), 1.45),
    "Neck1": (joint("Neck1"), joint("Neck2"), 1.38),
    "Neck2": (joint("Neck2"), joint("Head"), 1.20),
    # a bare tail: thick at the root, thin as a cord at the tip
    "Tail": (joint("Tail"), joint("Tail1"), 0.38),
    "Tail1": (joint("Tail1"), joint("Tail2"), 0.26),
    "Tail2": (joint("Tail2"), joint("Tail3"), 0.20),
    "Tail3": (joint("Tail3"), joint("Tail4"), 0.16),
    "Tail4": (joint("Tail4"), joint("Tail5"), 0.13),
    "Tail5": (joint("Tail5"), joint("Tail5") + Vector((0, 0.08, 0)), 0.10),
})
# The trunk: much wider (x) and deeper below the spine (z down), so the belly hangs low and the long fox legs
# look short; the back hunches up over the loins.
TRUNK = {"Pelvis": (1.50, 1.60), "Spine": (1.55, 1.70), "Spine1": (1.40, 1.50), "": (1.35, 1.40)}
BACK_Z = joint("Spine").z
HUNCH = 0.06  # metres the back rises at the top of the hunch (over Spine)

HEAD = joint("Head")
STOP_Y = HEAD.y - 0.05  # in front of the eyes: the muzzle starts here
MUZZLE = 1.12  # muzzle length: a rat's is longer and narrower than the fox's
EAR_Z = HEAD.z + 0.045  # ears above this shrink
EAR = 0.22

me = body.data
mats = [s.material.name if s.material else "" for s in body.material_slots]
groups = {g.index: g.name.replace("Fox_ ", "").replace("Fox_", "") for g in body.vertex_groups}

bm = bmesh.new()
bm.from_mesh(me)
fur = mats.index("M_FoxFur") if "M_FoxFur" in mats else -1
bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index == fur], context="FACES")
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.0002)  # weld the UV seams
deform = bm.verts.layers.deform.active
mw = body.matrix_world
mwi = mw.inverted()
ear_x = {1: [], -1: []}
for v in bm.verts:
    p = mw @ v.co
    if p.z > EAR_Z and p.y > HEAD.y - 0.06:
        ear_x[1 if p.x > 0 else -1].append(p.x)
EAR_CX = {s: (sum(xs) / len(xs) if xs else 0.04 * s) for s, xs in ear_x.items()}


def weights(v):
    w = {groups[k]: x for k, x in v[deform].items() if k in groups}
    total = sum(w.values()) or 1.0
    return {k: x / total for k, x in w.items()}


moves = {}
for v in bm.verts:
    p0 = p = mw @ v.co
    w = weights(v)
    delta = Vector()
    for name, wt in w.items():
        if name in SEGMENTS:
            a, b, f = SEGMENTS[name]
            q, t = intersect_point_line(p, a, b)
            q = a + (b - a) * min(max(t, 0.0), 1.0)
            delta += (p - q) * (f - 1.0) * wt
        elif name in TRUNK:
            sx, sz = TRUNK[name]
            d = Vector((p.x, 0.0, min(p.z - BACK_Z, 0.0)))
            delta += Vector((d.x * (sx - 1.0), 0.0, d.z * (sz - 1.0))) * wt
            if p.z > BACK_Z - 0.04:  # the hunch: highest over Spine, fading towards neck and tail
                along = 1.0 - min(1.0, abs(p.y - joint("Spine").y) / 0.22)
                delta.z += HUNCH * along * wt
    p = p + delta
    head_w = w.get("Head", 0.0) + w.get("Queue de cheval 1", 0.0)
    if head_w > 0.0:
        h = p.copy()
        if h.y < STOP_Y:  # a longer, narrower muzzle
            h.y = STOP_Y + (h.y - STOP_Y) * MUZZLE
            h.x *= 0.92
        else:
            h.x *= 1.08
        if h.z > EAR_Z and h.y > HEAD.y - 0.06:  # short round ears
            side = 1 if h.x > 0 else -1
            h.z = EAR_Z + (h.z - EAR_Z) * EAR
            h.x = EAR_CX[side] + (h.x - EAR_CX[side]) * 1.35
        p = p.lerp(h, min(head_w, 1.0))
    moves[v] = p - p0

for v, d in moves.items():
    v.co = mwi @ ((mw @ v.co) + d)
for _ in range(2):  # regions reshaped by different amounts meet without creases
    bmesh.ops.smooth_vert(bm, verts=[v for v in bm.verts if not v.is_boundary], factor=0.25,
                          use_axis_x=True, use_axis_y=True, use_axis_z=True)
bm.to_mesh(me)
bm.free()
if fur >= 0:
    body.data.materials.pop(index=fur)
sub = body.modifiers.new("subdivide", "SUBSURF")
sub.levels = 1
bpy.context.view_layer.objects.active = body
bpy.ops.object.modifier_apply(modifier=sub.name)
me = body.data
names = {g.index: g.name.replace("Fox_ ", "").replace("Fox_", "") for g in body.vertex_groups}


def bare(v, p):
    """1 on the bare pink skin: the tail, the ears, the paws, the tip of the nose."""
    w = {names[g.group]: g.weight for g in v.groups if g.group in names}
    total = sum(w.values()) or 1.0
    tail = sum(x for k, x in w.items() if k.startswith("Tail")) / total
    side = 1 if p.x > 0 else -1
    ear = p.z > EAR_Z + 0.004 and abs(p.x - EAR_CX[side]) < 0.032 and w.get("Head", 0.0) / total > 0.5
    if tail > 0.5 or ear:
        return 1.0
    return 1.0 if p.z < 0.03 or p.y < HEAD.y - 0.085 else 0.0


for c in list(me.color_attributes):
    me.color_attributes.remove(c)
col = me.color_attributes.new("Col", "BYTE_COLOR", "CORNER")
for poly in me.polygons:
    for li in poly.loop_indices:
        v = me.vertices[me.loops[li].vertex_index]
        col.data[li].color = (bare(v, mw @ v.co), 0.0, 0.0, 1.0)
me.color_attributes.active_color = col
me.color_attributes.render_color_index = me.color_attributes.active_color_index
for f in me.polygons:
    f.use_smooth = True

if PREVIEW:
    sc = bpy.context.scene
    for s in body.material_slots:
        if s.material:
            s.material.diffuse_color = (0.30, 0.27, 0.24, 1.0)
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.color_type = "VERTEX" if "paint" in PREVIEW else "MATERIAL"
    sc.render.resolution_x, sc.render.resolution_y = 800, 500
    sc.render.film_transparent = True
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 1.3
    for name, yaw in (("side", 90), ("front", 0), ("q", 45)):
        a = math.radians(yaw)
        cam.location = Vector((3 * math.sin(a), -3 * math.cos(a) + 0.1, 0.25))
        cam.rotation_euler = (math.radians(90), 0, a)
        sc.render.filepath = "%s_%s.png" % (PREVIEW, name)
        bpy.ops.render.render(write_still=True)

bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True)
body.select_set(True)
bpy.context.view_layer.objects.active = arm
arm.scale = (100.0, 100.0, 100.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.context.scene.unit_settings.scale_length = 0.01
bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, object_types={"ARMATURE", "MESH"}, add_leaf_bones=False,
                         bake_anim=False, mesh_smooth_type="FACE", colors_type="LINEAR")
print("RAT", len(me.vertices), "verts ->", OUT)
