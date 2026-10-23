"""Helmets for the castle's soldiers (Blender 5.2, headless):
blender -b --factory-startup -P helmet.py -- <face.fbx> <out_dir>

The face is a MetaHuman face mesh exported from Unreal (tools/unreal/helmet_make.py). The helmets are
built on an ellipsoid fitted to its skull, in the face's own frame, so in game each sits on the head
when attached to the head bone with the inverse of that bone's reference pose (helmet_make.py measures
it). One FBX per kind of helmet item (gen_im_arm_hel_<kind>), two material slots, Metal and Leather:
  med_hel  steel nasal helm: a dome, a brow band, a crest from front to back and a nose guard
  lgt_ltr  leather cap with a rolled brow band
  lgt_rlr  the leather cap reinforced with a steel brow band and a steel crest
The hair groom is hidden in game under a helmet (BP_DlgNPC.ApplyHelmet), so the dome sits close."""
import bpy, bmesh, json, math, os, sys
from mathutils import Vector

METAL, LEATHER = 0, 1


def skull(face_path):
    """The skull of a face mesh FBX, as an ellipsoid (metres, Blender frame): centre x, y (the head bone's,
    front and back fitted apart: the forehead is nearer than the occiput), z (the eyes'), the radii across,
    to the front, to the back and up, and which way the face looks (-1: along -y)."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=face_path)
    arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    face = max((o for o in bpy.data.objects if o.type == "MESH"), key=lambda o: len(o.data.vertices))
    pts = [face.matrix_world @ v.co for v in face.data.vertices]

    def bone(name):
        return (arm.matrix_world @ arm.data.bones[name].matrix_local).translation

    eye_z = (bone("FACIAL_L_Eye").z + bone("FACIAL_R_Eye").z) / 2
    front = -1.0 if bone("FACIAL_C_Nose").y < bone("head").y else 1.0
    top = [p for p in pts if p.z > eye_z + 0.01 and abs(p.x) < 0.11]
    cx = sum(p.x for p in top) / len(top)
    cy = bone("head").y
    crown = [p for p in top if p.z > eye_z + 0.045]  # the width above the ears (elves' reach up)
    return {"centre": [cx, cy, eye_z], "rx": max(abs(p.x - cx) for p in crown),
            "front": max((p.y - cy) * front for p in top), "back": max((cy - p.y) * front for p in top),
            "rz": max(p.z for p in top) - eye_z, "facing": front, "pts": pts}


if "--fit" in sys.argv:
    # blender ... -P helmet.py -- --fit <out.json> <name=face.fbx>...: every face's skull, for helmet_make.py
    args = sys.argv[sys.argv.index("--fit") + 1:]
    fits = {}
    for job in args[1:]:
        name, path = job.split("=", 1)
        k = skull(path)
        k.pop("pts")
        fits[name] = k
    with open(args[0], "w") as f:
        json.dump(fits, f, indent=1)
    print("HELMET fits", len(fits), "->", args[0])
    sys.exit(0)

FACE, OUT = sys.argv[-2:]
K = skull(FACE)
pts = K["pts"]
CX, CY, CZ = K["centre"]
EYE_Z = CZ
FRONT = K["facing"]
RX, R_FRONT, R_BACK, RZ = K["rx"], K["front"], K["back"], K["rz"]
print("HELMET skull centre", [round(v, 3) for v in (CX, CY, CZ)], "radii", [round(v, 3) for v in (RX, R_FRONT, R_BACK, RZ)])
PAD = 0.012  # helmet off the scalp (lining, and the hair is hidden)


def cut_z(a, front, side, back):
    """Rim height at azimuth a (0 = straight ahead): front, side and back heights blended round the head."""
    f = math.cos(a)
    return side + f * (front - side) if f > 0 else side + (-f) * (back - side)


def surface(a, z, extra=0.0):
    """The padded ellipsoid's point at azimuth a and height z, pushed out `extra` more."""
    t = max(-0.999, min(1.0, (z - CZ) / (RZ + PAD)))
    s = math.sqrt(max(0.0, 1.0 - t * t))
    ry = (R_FRONT if math.cos(a) > 0 else R_BACK) + PAD + extra
    return Vector((CX + (RX + PAD + extra) * s * math.sin(a), CY + FRONT * ry * s * math.cos(a), z))


class Mesh:
    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UV")

    def grid(self, rows, mat):
        """rows: lists of (point, uv) of equal length, closed round (each row a ring)."""
        vs = [[(self.bm.verts.new(p), uv) for p, uv in row] for row in rows]
        n = len(rows[0])
        for i in range(len(rows) - 1):
            for j in range(n):
                k = (j + 1) % n
                quad = [vs[i][j], vs[i][k], vs[i + 1][k], vs[i + 1][j]]
                f = self.bm.faces.new([q[0] for q in quad])
                f.material_index = mat
                for l, q in zip(f.loops, quad):
                    l[self.uv].uv = q[1]

    def strip(self, rows, mat):
        """rows: lists of (point, uv), not closed."""
        vs = [[(self.bm.verts.new(p), uv) for p, uv in row] for row in rows]
        for i in range(len(rows) - 1):
            for j in range(len(rows[0]) - 1):
                quad = [vs[i][j], vs[i][j + 1], vs[i + 1][j + 1], vs[i + 1][j]]
                f = self.bm.faces.new([q[0] for q in quad])
                f.material_index = mat
                for l, q in zip(f.loops, quad):
                    l[self.uv].uv = q[1]


SEG = 64


def dome(m, mat, front, side, back, rings=16, extra=0.0):
    """The cap from the crown down to the rim (a ring of quads closed at the top by a small cap ring)."""
    top = CZ + RZ + PAD + extra
    rows = []
    for i in range(1, rings + 1):
        u = i / rings
        row = []
        for j in range(SEG):
            a = 2 * math.pi * j / SEG
            z = top + (cut_z(a, front, side, back) - top) * (u ** 0.85)
            row.append((surface(a, z, extra), (j / SEG, 1.0 - u)))
        rows.append(row)
    m.grid(rows, mat)
    centre = m.bm.verts.new(Vector((CX, CY, top + 0.002)))
    ring = rows[0]
    first = [v for v in m.bm.verts][:SEG]
    for j in range(SEG):
        f = m.bm.faces.new([centre, first[j], first[(j + 1) % SEG]])
        f.material_index = mat
        for l, uv in zip(f.loops, ((0.5, 1.0), ring[j][1], ring[(j + 1) % SEG][1])):
            l[m.uv].uv = uv


def band(m, mat, front, side, back, width, extra):
    """A band round the rim, `width` high, standing `extra` off the dome."""
    rows = []
    for k, dz in enumerate((0.0, width)):
        row = []
        for j in range(SEG):
            a = 2 * math.pi * j / SEG
            row.append((surface(a, cut_z(a, front, side, back) + dz, extra), (j / SEG * 8, k * 0.2)))
        rows.append(row)
    m.grid(rows, mat)


def meridian(m, mat, a0, width, extra, z_from, z_to, steps=24):
    """A strip over the top of the head along azimuth a0 (and a0 + pi), from height z_from on one side up
    over the crown and down to z_to on the other."""
    top = CZ + RZ + PAD
    half = width / 2
    rows = []
    path = []
    for i in range(steps + 1):  # up the a0 side
        z = z_from + (top - 0.004 - z_from) * i / steps
        path.append((a0, z))
    for i in range(steps, -1, -1):  # down the far side
        z = z_to + (top - 0.004 - z_to) * i / steps
        path.append((a0 + math.pi, z))
    for side in (-1, 1):
        row = []
        for n, (a, z) in enumerate(path):
            p = surface(a, z, extra)
            across = Vector((math.cos(a), FRONT * -math.sin(a), 0.0)).normalized()  # sideways round the head
            if n > len(path) // 2:
                across = -across
            row.append((p + across * half * side, (n / len(path) * 4, (side + 1) / 2 * 0.1)))
        rows.append(row)
    m.strip(rows, mat)


# the bridge of the nose: the face's most forward point between the eyes
BRIDGE = max((p for p in pts if abs(p.x - CX) < 0.01 and abs(p.z - (EYE_Z - 0.005)) < 0.012), key=lambda p: p.y * FRONT)


def nasal(m, mat, z_top, length=0.07, width=0.022, extra=0.006, steps=6):
    """A nose guard from the brow band at the front down to just in front of the bridge of the nose."""
    top = surface(0.0, z_top, extra)
    bottom = Vector((CX, BRIDGE.y + FRONT * 0.012, z_top - length))
    rows = []
    for side in (-1, 1):
        row = []
        for k in range(steps + 1):
            t = k / steps
            row.append((top.lerp(bottom, t) + Vector((side * width / 2, 0, 0)), ((side + 1) / 2 * 0.1, t * 0.5)))
        rows.append(row)
    m.strip(rows, mat)


def finish(m, name, thickness):
    me = bpy.data.meshes.new(name)
    m.bm.normal_update()
    m.bm.to_mesh(me)
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    for n in ("Metal", "Leather"):
        me.materials.append(bpy.data.materials.get(n) or bpy.data.materials.new(n))
    for f in me.polygons:
        f.use_smooth = True
    me.validate()
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    so = ob.modifiers.new("solid", "SOLIDIFY")
    so.thickness = thickness
    so.offset = -1.0  # inward: the outer surface stays where it was built
    so.use_rim = True
    bpy.ops.object.modifier_apply(modifier="solid")
    return ob


# rim heights: front just above the brows, sides above the ears, back over the nape
FRONT_Z, SIDE_Z, BACK_Z = EYE_Z + 0.032, EYE_Z + 0.012, EYE_Z - 0.035

helmets = {}
m = Mesh()  # med_hel: steel nasal helm
dome(m, METAL, FRONT_Z, SIDE_Z, BACK_Z)
band(m, METAL, FRONT_Z, SIDE_Z, BACK_Z, 0.028, 0.004)
meridian(m, METAL, 0.0, 0.022, 0.004, FRONT_Z + 0.02, BACK_Z + 0.02)
nasal(m, METAL, FRONT_Z + 0.004)
helmets["med_hel"] = finish(m, "Helmet_med_hel", 0.004)

m = Mesh()  # lgt_ltr: leather cap, a little lower all round
dome(m, LEATHER, FRONT_Z - 0.004, SIDE_Z - 0.006, BACK_Z - 0.01)
band(m, LEATHER, FRONT_Z - 0.004, SIDE_Z - 0.006, BACK_Z - 0.01, 0.022, 0.005)
helmets["lgt_ltr"] = finish(m, "Helmet_lgt_ltr", 0.006)

m = Mesh()  # lgt_rlr: the leather cap with steel bands
dome(m, LEATHER, FRONT_Z - 0.004, SIDE_Z - 0.006, BACK_Z - 0.01)
band(m, METAL, FRONT_Z - 0.004, SIDE_Z - 0.006, BACK_Z - 0.01, 0.024, 0.005)
meridian(m, METAL, 0.0, 0.02, 0.004, FRONT_Z + 0.015, BACK_Z + 0.01)
helmets["lgt_rlr"] = finish(m, "Helmet_lgt_rlr", 0.006)

os.makedirs(OUT, exist_ok=True)
for kind, ob in helmets.items():
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    path = os.path.join(OUT, "SM_Helmet_%s.fbx" % kind)
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"MESH"}, mesh_smooth_type="FACE")
    print("HELMET", kind, len(ob.data.vertices), "verts ->", path)
