"""Iona's hair groom (Blender 5.2, run headless): straight, centre-parted, shoulder length, tucked behind
pointed elf ears, a braid on each side from the front hairline round the back to one hanging braid, and two
thin braids in front of the ears, tied off with short tassels.

blender -b --factory-startup -P iona_hair.py
Input: iona_head.fbx (Iona's MetaHuman head, exported from Unreal into HERE; the export has round ears, so
the pointed ears added later by tools/unreal/elf_ears.body.py are modelled here as capsules to avoid).
Output: iona_hair.abc + previews in HERE. Import in Unreal as a groom (AlembicHairImporter, HairStrandsFactory,
rotation (90,0,0), scale (100,-100,100)), hair width override 0.011 cm (docs/CHARACTERS.md).
Blender frame: metres, face toward -y, -x is her right."""
import bpy, bmesh, math, random, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = r"E:/DAODream/Unreal/Cousland/Saved/claude/hair"
N = int(os.environ.get("HAIR_N", "42000"))
END_Z = float(os.environ.get("HAIR_END", "1.42"))   # blunt cut, a little above the shoulders
random.seed(11)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=HERE + "/iona_head.fbx")
head = next(o for o in bpy.data.objects if o.type == "MESH")
bm = bmesh.new(); bm.from_object(head, bpy.context.evaluated_depsgraph_get()); bm.transform(head.matrix_world)
bm.faces.ensure_lookup_table()
bvh = BVHTree.FromBMesh(bm)
V = [v.co for v in bm.verts]
TOP = max(v.z for v in V)
FRONT = min(V, key=lambda v: v.y)                     # nose tip
C = Vector((0.0, -0.025, TOP - 0.095))                # head centre
EAR = 0.088
HAIRLINE = TOP - 0.042                                 # forehead hairline height
DOWN = Vector((0, 0, -1))
print("TOP %.3f FRONT %s" % (TOP, tuple(round(c, 3) for c in FRONT)))

# pointed ears (after elf_ears.body.py): capsule from the ear's middle to its raised, swept-back tip
EARS = [(Vector((s * 0.084, 0.000, TOP - 0.115)), Vector((s * 0.101, 0.036, TOP - 0.060)), 0.016) for s in (1, -1)]


def seg_closest(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
    return a + ab * t


def keep_out(p, off):
    """Push a point out of the head (by off) and out of the ear capsules (towards the back)."""
    loc, nrm, _, dist = bvh.find_nearest(p)
    if loc is not None:
        d = p - loc
        out = d.normalized() if d.length > 1e-6 else nrm
        if out.dot(nrm) < 0:                           # inside the mesh
            p = loc + nrm * off
        elif d.length < off:
            p = loc + out * off
    for a, b, r in EARS:
        q = seg_closest(p, a, b)
        d = p - q
        if d.length < r + off:
            dirn = (d.normalized() if d.length > 1e-6 else Vector((math.copysign(1, a.x), 0, 0)))
            dirn = (dirn + Vector((0, 0.8, 0))).normalized()   # behind the ear rather than in front
            p = q + dirn * (r + off)
    if p.y < FRONT.y + 0.075 and abs(p.x) < 0.082 and p.z < HAIRLINE - 0.012:   # never across the face
        p = Vector((math.copysign(0.082, p.x if p.x else 1), p.y, p.z))
    return p


def hairline(p):
    ax = abs(p.x)
    if p.y < -0.055:                                   # forehead; temples a little lower
        return HAIRLINE - 0.02 * min(max((ax - 0.025) / 0.04, 0.0), 1.0)
    if p.y < 0.035 and ax > 0.06:                      # above the ear: keep the ear clear
        return TOP - 0.06
    if p.y < 0.06:
        return TOP - 0.11
    return TOP - 0.165                                 # nape


def weight(p):
    d = p.z - hairline(p)
    w = max(0.0, min(1.0, (d + 0.002) / 0.010))
    return w * w * (3 - 2 * w)


skin = [f for f in bm.faces if f.material_index == 0 and f.calc_center_median().z > TOP - 0.18]
tris = [(f, f.calc_area()) for f in skin if f.calc_center_median().z > hairline(f.calc_center_median()) - 0.006]
tot = sum(a for _, a in tris)
print("scalp faces", len(tris), "area m2", round(tot, 4))


def sample_root():
    while True:
        r = random.random() * tot
        for f, a in tris:
            r -= a
            if r <= 0:
                break
        vs = [v.co for v in f.verts]
        u, v = random.random(), random.random()
        if u + v > 1: u, v = 1 - u, 1 - v
        p = vs[0] + (vs[1] - vs[0]) * u + (vs[2] - vs[0]) * v
        if random.random() < weight(p):
            return p, f.normal.copy()


def resample(pts, n):
    L = [0.0]
    for a, b in zip(pts, pts[1:]):
        L.append(L[-1] + (b - a).length)
    out, j = [], 0
    for k in range(n):
        s = L[-1] * k / (n - 1)
        while j < len(L) - 2 and L[j + 1] < s:
            j += 1
        t = (s - L[j]) / max(L[j + 1] - L[j], 1e-9)
        out.append(pts[j].lerp(pts[j + 1], t))
    return out


EAR_TOP = TOP - 0.05      # the pointed tips reach about here


def grow(root, nrm, off, end_z, step=0.004):
    """Hug the skull (at a fixed height off above it) down to the ears, then hang straight.
    Hair heads away from the centre parting, and in front of the ears it is tucked back behind them."""
    side = 1.0 if root.x >= 0 else -1.0
    if root.y < -0.05:
        d = Vector((side, 0.5, 0))
    elif root.y < 0.02 and abs(root.x) < 0.04:
        d = Vector((side, 0.10, -0.2))
    else:
        d = (root - C); d.z = -0.3 * d.length
    p = root.copy(); pts = [p.copy()]; s = 0.0; hug = True
    while p.z > end_z and s < 0.5:
        if hug:
            loc, n, _, _ = bvh.find_nearest(p)
            tuck = Vector((0, 1.0, 0)) if (p.y < 0.045 and abs(p.x) > 0.05 and p.z < EAR_TOP + 0.03) else Vector()
            if p.y < -0.05 and p.z > EAR_TOP:          # forehead: combed sideways and back, never down the face
                d = d * 0.5 + Vector((side, 0.6, 0)) * 0.6
            else:
                d = d * 0.6 + DOWN * 0.45 + tuck * 0.7
            d = (d - n * d.dot(n)).normalized()
            q = p + d * step
            loc, n, _, _ = bvh.find_nearest(q)
            q = loc + n * off
            if (n.z < -0.15 or q.z < EAR_TOP - 0.075) and (q.y > 0.04 or abs(q.x) < 0.05):
                hug = False                            # past the widest point, or below and behind the ears
        else:
            flare = Vector((side * 0.10, -0.05, 0)) if abs(p.x) > 0.05 else Vector((side * 0.03, 0, 0))
            d = (d * 0.55 + DOWN * 0.45 + flare * max(0.0, 1.0 - (EAR_TOP - p.z) / 0.15)).normalized()
            q = keep_out(p + d * step, off)
        q = keep_out(q, off)
        d = (q - p).normalized() if (q - p).length > 1e-6 else d
        p = q; pts.append(p.copy()); s += step
    return resample(pts, 30)


strands = []
for k in range(N):
    root, nrm = sample_root()
    layer = random.random()
    off = 0.0025 + 0.013 * layer * (0.45 + 0.55 * min(1.0, max(0.0, (root.z - (TOP - 0.10)) / 0.08)))   # volume, most on top
    end = END_Z + random.gauss(0, 0.004) + 0.006 * layer
    pts = grow(root + nrm * 0.0005, nrm, off, end)
    jit = Vector((random.gauss(0, 1), random.gauss(0, 1), 0)) * 0.0012
    strands.append([q + jit * (i / len(pts)) for i, q in enumerate(pts)])
print("hair", len(strands))


# ---- braids -------------------------------------------------------------------------------------
def on_head(az, el, lift):
    """Point lift above the scalp in direction (azimuth from the front, elevation) from the centre."""
    d = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    hit = bvh.ray_cast(C + d * 0.3, -d, 0.3)
    p = hit[0] if hit[0] is not None else C + d * 0.1
    return p + d * lift


def braid(path, width, hairs, end_tassel=0.0):
    """Three interlaced bundles along a path (list of Vectors); a tie and a short tassel at the end."""
    path = resample(path, max(12, int(sum((b - a).length for a, b in zip(path, path[1:])) / 0.002)))
    out = []
    T = [(path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized() for i in range(len(path))]
    plen = sum((b - a).length for a, b in zip(path, path[1:]))
    turns = plen / (width * 1.25)                      # one crossing every ~1.25 widths
    for b in range(3):
        ph = 2 * math.pi * b / 3
        for h in range(hairs):
            r = width * 0.22 * math.sqrt(random.random()); a = random.random() * 6.283
            pts = []
            for i, (c, t) in enumerate(zip(path, T)):
                side = t.cross(Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))).normalized()
                up = side.cross(t).normalized()
                u = 2 * math.pi * turns * i / (len(path) - 1) + ph
                taper = 1.0 - 0.35 * (i / (len(path) - 1))
                cen = c + side * (width * 0.38 * math.sin(u) * taper) + up * (width * 0.18 * math.sin(2 * u) * taper)
                pts.append(cen + side * (r * math.cos(a)) * taper + up * (r * math.sin(a)) * taper)
            if end_tassel:
                e = pts[-1]
                spread = Vector((random.gauss(0, 1), random.gauss(0, 1), 0)) * width * 0.25
                for k in range(1, 6):
                    pts.append(e + DOWN * (end_tassel * k / 5) + spread * (k / 5))
            out.append(pts)
    return out


def drape(p0, end_z, lift):
    """From p0 straight down along the outside of the hair to end_z."""
    pts = [p0.copy()]; p = p0.copy()
    while p.z > end_z:
        p = keep_out(p + DOWN * 0.004, lift); pts.append(p.copy())
    return pts


braids = []
EL = math.radians(22)
for s in (1, -1):
    # side braid: from the front hairline, above the ear, round to the back of the head
    side_path = [on_head(s * math.radians(a), math.radians(e), 0.010)
                 for a, e in ((38, 30), (60, 26), (85, 22), (110, 18), (135, 14), (158, 10), (176, 8))]
    braids += braid([q + (q - C).normalized() * 0.010 for q in side_path], 0.013, 90)   # on top of the hair
    # front braid: from the hairline beside the parting, down in front of the ear, tied at the chin
    top_ = on_head(s * math.radians(30), math.radians(38), 0.016)
    temple = keep_out(Vector((s * 0.084, FRONT.y + 0.075, HAIRLINE - 0.03)), 0.016)
    front_path = [top_, temple] + drape(temple, FRONT.z - 0.09, 0.016)[1:]
    braids += braid(front_path, 0.009, 60, end_tassel=0.03)
# the side braids meet at the back and hang as one
back0 = on_head(math.pi, math.radians(8), 0.021)
braids += braid([back0] + drape(back0, END_Z + 0.03, 0.021)[1:], 0.014, 100, end_tassel=0.03)
print("braid hairs", len(braids))

def curves_object(name, cs, colour):
    hc = bpy.data.hair_curves.new(name)
    hc.add_curves([len(p) for p in cs])
    hc.attributes["position"].data.foreach_set("vector", [c for p in cs for v in p for c in v])
    ob = bpy.data.objects.new(name, hc); ob.color = colour
    bpy.context.collection.objects.link(ob)
    return ob

allc = strands + braids
obj = curves_object("IonaHair", allc, (0.75, 0.55, 0.3, 1))
print("strands", len(allc))
for o in bpy.context.scene.objects: o.select_set(False)
obj.select_set(True); bpy.context.view_layer.objects.active = obj
bpy.ops.wm.alembic_export(filepath=HERE + "/iona_hair.abc", selected=True, start=1, end=1)
# previews: braids darker so they read
obj.hide_render = True
curves_object("PrevHair", strands, (0.78, 0.6, 0.35, 1)); curves_object("PrevBraids", braids, (0.35, 0.2, 0.1, 1))
bpy.context.scene.display.shading.color_type = "OBJECT"
print("ABC", os.path.getsize(HERE + "/iona_hair.abc"))

scn = bpy.context.scene
scn.render.engine = "BLENDER_WORKBENCH"
scn.render.resolution_x, scn.render.resolution_y = 640, 760
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); cam.data.lens = 85
scn.collection.objects.link(cam); scn.camera = cam
aim = Vector((0, -0.02, TOP - 0.13))
for name, (x, y) in (("front", (0, -1.0)), ("q34", (0.7, -0.7)), ("side", (1.0, 0.0)), ("back", (0, 1.0))):
    cam.location = aim + Vector((x, y, 0.01))
    cam.rotation_euler = (aim - cam.location).to_track_quat("-Z", "Y").to_euler()
    scn.render.filepath = HERE + "/iona_preview_%s.png" % name
    bpy.ops.render.render(write_still=True)
print("DONE")
