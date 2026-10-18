"""Medieval base outfit grown on a MetaHuman body (Blender 5.2, run headless):
a quilted gambeson with a short skirt, trousers and boots.

blender -b --factory-startup -P outfit.py -- <body.fbx> <out.fbx> [preview_prefix]

The body comes from Unreal (SKM_MHC_<Name>_BodyMesh exported as FBX, with its skeleton). Each garment
is a copy of part of the body surface, chosen by the bone that drives each vertex most, smoothed and
pushed out by the garment's thickness. Copies keep the body's skin weights, so the outfit bends with the
same skeleton (metahuman_base_skel) and needs no weight painting. Output: one skeletal mesh with three
material slots (Gambeson, Trousers, Boots), to import onto metahuman_base_skel (docs/CHARACTERS.md).
"""
import sys
import bmesh
import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
BODY, OUT = args[0], args[1]
PREVIEW = args[2] if len(args) > 2 else ""

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=BODY)
arm = next(o for o in bpy.context.scene.objects if o.type == "ARMATURE")
body = next(o for o in bpy.context.scene.objects if o.type == "MESH")
names = {g.index: g.name for g in body.vertex_groups}


def dominant(v):
    best = max(v.groups, key=lambda g: g.weight, default=None)
    return names.get(best.group, "") if best else ""


def bone_part(n):
    if n.startswith(("hand_", "thumb", "index", "middle", "ring", "pinky", "wrist")):
        return "hand"
    if n.startswith(("head", "neck_02", "FACIAL")):
        return "head"
    if n.startswith(("foot", "ball", "bigtoe", "indextoe", "middletoe", "ringtoe", "littletoe")):
        return "foot"
    if n.startswith(("calf", "knee")):
        return "calf"
    if n.startswith("thigh"):
        return "thigh"
    return "torso"  # pelvis, spine, clavicle, neck_01, upper/lower arm and their correctives


mw = body.matrix_world


def joint(name):
    return (arm.matrix_world @ arm.data.bones[name].head_local).z


NECK = joint("neck_01")                       # collar height
PELVIS = joint("pelvis")
KNEE = (joint("calf_l") + joint("calf_r")) / 2
ANKLE = (joint("foot_l") + joint("foot_r")) / 2
SKIRT = KNEE + 0.45 * (PELVIS - KNEE)         # gambeson hem: about mid-thigh
BOOT = ANKLE + 0.55 * (KNEE - ANKLE)          # boot top: below the calf
H = NECK                                      # scale reference for the flare
print("LEVELS neck %.3f pelvis %.3f knee %.3f ankle %.3f skirt %.3f boot %.3f" % (NECK, PELVIS, KNEE, ANKLE, SKIRT, BOOT))

part = {}
for v in body.data.vertices:
    p, z = bone_part(dominant(v)), (mw @ v.co).z
    part[v.index] = p
    if p == "torso" and z > NECK + 0.015:   # neck above the collar stays bare
        part[v.index] = "head"


def garment(name, keep, offset, smooth=4, flare=None):
    """Copy the body faces whose vertices all satisfy keep(index, z), smooth and push them out."""
    ob = body.copy()
    ob.data = body.data.copy()
    ob.name = ob.data.name = name
    bpy.context.scene.collection.objects.link(ob)
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.verts.ensure_lookup_table()
    gone = [f for f in bm.faces if not all(keep(v.index, (mw @ v.co).z) for v in f.verts)]
    bmesh.ops.delete(bm, geom=gone, context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    for _ in range(smooth):
        bmesh.ops.smooth_vert(bm, verts=[v for v in bm.verts if not v.is_boundary], factor=0.5,
                              use_axis_x=True, use_axis_y=True, use_axis_z=True)
    bm.normal_update()
    for v in bm.verts:
        d = offset if flare is None else offset + flare((mw @ v.co).z)
        v.co += v.normal * d
    bm.to_mesh(ob.data)
    bm.free()
    sol = ob.modifiers.new("thickness", "SOLIDIFY")
    sol.thickness = 0.004
    sol.offset = -1.0
    return ob


BELT = PELVIS + 0.03                          # gambeson body stops here; the skirt hangs from it
coat = garment("Gambeson", lambda i, z: part[i] == "torso" and z > BELT - 0.02, 0.016, smooth=30)
legs = garment("Trousers", lambda i, z: (part[i] in ("thigh", "calf") or (part[i] == "torso" and z < BELT + 0.02))
               and z > BOOT - 0.04, 0.006, smooth=10)
boots = garment("Boots", lambda i, z: part[i] == "foot" or (part[i] == "calf" and z < BOOT), 0.010, smooth=30)


def bands():
    """Tube garments around hips and thighs, sized from the body's outer outline (arms left out):
    a flared skirt hanging from the waist and a leather belt over the seam."""
    import math
    from mathutils.bvhtree import BVHTree
    from mathutils.kdtree import KDTree
    dg = bpy.context.evaluated_depsgraph_get()
    bm0 = bmesh.new(); bm0.from_object(body, dg); bm0.transform(mw)
    ARMS = ("upperarm", "lowerarm", "hand", "thumb", "index", "middle", "ring", "pinky", "clavicle", "wrist")
    armv = {v.index for v in body.data.vertices if dominant(v).startswith(ARMS)}
    bm0.verts.ensure_lookup_table()
    bmesh.ops.delete(bm0, geom=[f for f in bm0.faces if any(v.index in armv for v in f.verts)], context="FACES")
    bvh = BVHTree.FromBMesh(bm0)
    verts = body.data.vertices
    kd = KDTree(len(verts))
    for v in verts:
        kd.insert(mw @ v.co, v.index)
    kd.balance()
    axis = arm.matrix_world @ arm.data.bones["pelvis"].head_local
    A = 48

    def outline(z):
        c = Vector((axis.x, axis.y, z))
        rads, dirs = [], []
        for k in range(A):
            ang = 2 * math.pi * k / A
            d = Vector((math.cos(ang), math.sin(ang), 0))
            hit = bvh.ray_cast(c + d * 0.6, -d, 0.6)
            rads.append((hit[0] - c).length if hit[0] is not None else 0.15)
            dirs.append(d)
        rads = [max(rads[(k + j) % A] for j in range(-5, 6)) for k in range(A)]   # bridge the gap between legs
        for _ in range(3):                                                         # and round off the dips
            rads = [max(rads[k], sum(rads[(k + j) % A] for j in range(-4, 5)) / 9) for k in range(A)]
        return c, rads, dirs

    def tube(name, z0, z1, rings, extra, material, weight_floor):
        rows = []
        for r in range(rings + 1):
            t = r / rings
            c, rads, dirs = outline(z0 + (z1 - z0) * t)
            rows.append([c + dirs[k] * (rads[k] + extra(t)) for k in range(A)])
        vs = [p for row in rows for p in row]
        fs = [(r * A + k, (r + 1) * A + k, (r + 1) * A + (k + 1) % A, r * A + (k + 1) % A)
              for r in range(rings) for k in range(A)]
        me = bpy.data.meshes.new(name)
        me.from_pydata([tuple(v) for v in vs], [], fs)
        bm = bmesh.new(); bm.from_mesh(me); bm.normal_update()
        inward = [f for f in bm.faces if f.normal.dot(f.calc_center_median() - Vector((axis.x, axis.y, f.calc_center_median().z))) < 0]
        if len(inward) > len(bm.faces) / 2:
            bmesh.ops.reverse_faces(bm, faces=bm.faces)
        bm.to_mesh(me); bm.free()
        for poly in me.polygons:
            poly.use_smooth = True
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)
        ob.parent = arm
        ob.matrix_parent_inverse = arm.matrix_world.inverted()
        for g in body.vertex_groups:
            ob.vertex_groups.new(name=g.name)
        for i, p in enumerate(vs):
            co, idx, dist = kd.find(Vector((p.x, p.y, max(p.z, weight_floor))))
            for g in verts[idx].groups:
                ob.vertex_groups[names[g.group]].add([i], g.weight, "REPLACE")
        md = ob.modifiers.new("Armature", "ARMATURE"); md.object = arm
        sol = ob.modifiers.new("thickness", "SOLIDIFY"); sol.thickness = 0.005; sol.offset = -1.0
        ob.data.materials.append(bpy.data.materials.get(material) or bpy.data.materials.new(material))
        return ob

    sk = tube("Skirt", BELT + 0.05, SKIRT - 0.03, 12, lambda t: 0.020 + 0.05 * t ** 1.4, "Gambeson", SKIRT + 0.04)
    belt = tube("Belt", BELT - 0.012, BELT + 0.032, 2, lambda t: 0.030, "Boots", BELT - 0.03)
    bm0.free()
    return sk, belt


for ob in (coat, legs, boots):
    ob.data.materials.clear()
    m = bpy.data.materials.get(ob.name) or bpy.data.materials.new(ob.name)
    ob.data.materials.append(m)
    for poly in ob.data.polygons:
        poly.material_index = 0
    for md in ob.modifiers:
        if md.type == "ARMATURE":
            md.object = arm

sk, belt = bands()
# one skeletal mesh: join the garments (each keeps its own material slot)
for o in bpy.context.scene.objects:
    o.select_set(False)
for ob in (coat, legs, boots, sk, belt):
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.modifier_apply(modifier="thickness")
    ob.select_set(False)
coat.select_set(True); legs.select_set(True); boots.select_set(True); sk.select_set(True); belt.select_set(True)
bpy.context.view_layer.objects.active = coat
bpy.ops.object.join()
coat.name = coat.data.name = "Outfit"
bpy.data.objects.remove(body)
print("OUTFIT verts", len(coat.data.vertices), "materials", [m.name for m in coat.data.materials])

if PREVIEW:
    scn = bpy.context.scene
    scn.render.engine = "BLENDER_WORKBENCH"
    scn.display.shading.light = "STUDIO"
    scn.display.shading.color_type = "MATERIAL"
    for m, c in (("Gambeson", (0.35, 0.08, 0.06, 1)), ("Trousers", (0.15, 0.11, 0.08, 1)), ("Boots", (0.06, 0.04, 0.03, 1))):
        bpy.data.materials[m].diffuse_color = c
    scn.render.resolution_x, scn.render.resolution_y = 500, 900
    cd = bpy.data.cameras.new("cam"); cd.lens = 50
    cam = bpy.data.objects.new("cam", cd); scn.collection.objects.link(cam); scn.camera = cam
    aim = Vector((0, 0, 0.55 * NECK))
    for name, loc in (("front", (0, -4.2, 0.6 * NECK)), ("side", (4.2, 0, 0.6 * NECK)), ("back", (0, 4.2, 0.6 * NECK))):
        cam.location = loc
        cam.rotation_euler = (aim - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        scn.render.filepath = "%s_%s.png" % (PREVIEW, name)
        bpy.ops.render.render(write_still=True)

for o in bpy.context.scene.objects:
    o.select_set(o in (arm, coat))
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, object_types={"ARMATURE", "MESH"},
                         add_leaf_bones=False, bake_anim=False, mesh_smooth_type="FACE",
                         use_armature_deform_only=False, apply_unit_scale=True)
print("DONE", OUT)
