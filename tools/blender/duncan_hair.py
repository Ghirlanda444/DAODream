"""Duncan's hair groom (Blender 5.2, run headless): slicked back, low ponytail, loose front locks.

blender -b --factory-startup -P duncan_hair.py
Input: duncan_head.fbx (Duncan's MetaHuman head, exported from Unreal into HERE).
Output: duncan_hair7.abc + previews in HERE. Import in Unreal as a groom (AlembicHairImporter,
HairStrandsFactory, rotation (90,0,0), scale (100,-100,100)), set hair width override 0.011 cm,
then run tools/unreal/duncan_groom_apply.py after every Duncan build (docs/CHARACTERS.md)."""
import bpy, bmesh, math, random, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = r"E:/DAODream/Unreal/Cousland/Saved/claude/hair"
N = int(os.environ.get("HAIR_N", "22000"))
random.seed(7)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=HERE + "/duncan_head.fbx")
head = next(o for o in bpy.data.objects if o.type == "MESH")
mw = head.matrix_world
dg = bpy.context.evaluated_depsgraph_get()
bm = bmesh.new(); bm.from_object(head, dg); bm.transform(mw)
bm.faces.ensure_lookup_table()
skin = [f for f in bm.faces if f.material_index == 0]
bvh = BVHTree.FromBMesh(bm)

C = Vector((0.0, -0.025, 1.755))           # head centre
TIE = Vector((0.0, 0.088, 1.700))          # ponytail tie at the back of the head

def hairline(p):
    y, ax, z = p.y, abs(p.x), p.z
    if ax > 0.082 and 1.70 < z < 1.787 and -0.022 < y < 0.034:
        return 9.0                          # the ear itself
    if y < -0.065:                          # forehead, temples a little lower
        return 1.826 - 0.036 * min(max((ax - 0.025) / 0.045, 0.0), 1.0)
    if ax < 0.05:                           # crown between the temples
        return 1.80
    if y < -0.045:                          # temple, sloping down towards the sideburn
        return 1.798 - 0.035 * (y + 0.065) / 0.02
    if y < -0.020:                          # sideburn in front of the ear
        return 1.705
    if y < 0.034:                           # just above the ear
        return 1.789
    if y < 0.065:                           # behind the ear
        return 1.705
    return 1.705 - (1.705 - 1.640) * min((y - 0.065) / 0.03, 1.0)

EDGE = 0.016   # roots thin out over this height above the hairline

def weight(p):
    d = p.z - hairline(p)
    w = max(0.0, min(1.0, (d + 0.003) / (0.008 if p.y < -0.065 else EDGE)))
    return w * w * (3 - 2 * w)

def on_scalp(p):
    return p.z > hairline(p) - 0.006 and p.z > 1.62

def surface(d):
    """Scalp point along direction d, cast from the centre outward so the ears are skipped."""
    hit = bvh.ray_cast(C, d, 0.3)
    return hit[0] if hit[0] is not None else C + d * 0.11

tris = []
for f in skin:
    cen = f.calc_center_median()
    if on_scalp(cen):
        tris.append((f, f.calc_area()))
tot = sum(a for _, a in tris)
print("scalp faces", len(tris), "area m2", round(tot, 4))

def sample_root():
    while True:
        p, n = _sample_root()
        if random.random() < weight(p):
            return p, n

def _sample_root():
    r = random.random() * tot
    for f, a in tris:
        r -= a
        if r <= 0:
            break
    vs = [v.co for v in f.verts]
    u, v = random.random(), random.random()
    if u + v > 1: u, v = 1 - u, 1 - v
    p = vs[0] + (vs[1] - vs[0]) * u + (vs[2] - vs[0]) * v if len(vs) == 3 else f.calc_center_median()
    return p, f.normal.copy()

def slerp(a, b, t):
    a, b = a.normalized(), b.normalized()
    om = math.acos(max(-1.0, min(1.0, a.dot(b))))
    if om < 1e-4: return a
    return (a * math.sin((1 - t) * om) + b * math.sin(t * om)) / math.sin(om)

CL = 260
TAILC = 34
tail_clumps = [(random.random() * 2 * math.pi, 0.017 * math.sqrt(random.random()), random.random() * 6.28, random.uniform(0.095, 0.15)) for _ in range(TAILC)]
clumps = [sample_root()[0] for _ in range(CL)]
strands = []
for s in range(N):
    root, nrm = sample_root()
    cj = min(clumps, key=lambda q: (q - root).length_squared)
    pull = random.uniform(0.25, 0.6)
    loose = False
    side = 1.0 if root.x > 0 else -1.0
    low_side = abs(root.x) > 0.05 and -0.050 < root.y < -0.016 and root.z < 1.772
    if low_side:
        burn = root.y > -0.047 and root.y < -0.018 and root.z < 1.775
        dvec = Vector((0.0, 0.25, -1.0)) if burn else Vector((0.0, 1.0, -0.45))
        dvec.normalize()
        L = random.uniform(0.010, 0.022) if burn else random.uniform(0.018, 0.035)
        q = root.copy(); pts = [q.copy()]
        for k in range(6):
            q = q + dvec * (L / 6)
            hit = bvh.find_nearest(q)
            if hit[0] is not None:
                q = hit[0] + hit[1] * 0.0012
            pts.append(q.copy())
        strands.append(pts)
        continue
    d0, d1 = root - C, TIE - C
    over_ear = abs(root.x) > 0.045 and root.z < 1.82 and root.y < 0.034
    dmid = Vector((side * 0.085, 0.012, 1.808)) - C
    top = max(0.0, min(1.0, (root.z - 1.78) / 0.09))
    vol = 0.005 + 0.017 * top * (1.0 if root.y < 0.03 else 0.55)    # volume on top
    jit = Vector((random.gauss(0, 1), random.gauss(0, 1), random.gauss(0, 1))) * 0.0015
    pts = [root.copy()]
    K = 18
    for k in range(1, K + 1):
        t = k / K
        if over_ear:
            d = slerp(d0, dmid, t / 0.45) if t < 0.45 else slerp(dmid, d1, (t - 0.45) / 0.55)
        else:
            d = slerp(d0, d1, t)
        base = surface(d)
        rise = min(1.0, t / 0.18)
        off = vol * math.sin(rise * math.pi / 2) * (1 - 0.75 * t) + 0.0025
        pc = surface(slerp(cj - C, d1, t))
        pt = base + d.normalized() * off + jit * math.sin(t * math.pi)
        pt = pt + (pc + d.normalized() * off - pt) * pull * math.sin(min(t * 1.4, 1.0) * math.pi / 2) * 0.35
        pts.append(pt)
        if loose and t > 0.25:
            break
    if loose:  # a strand that slipped out: falls down beside the temple
        side = 1 if root.x > 0 else -1
        p0 = pts[-1]
        for k in range(1, 9):
            u = k / 8
            pts.append(p0 + Vector((side * 0.012 * u, -0.01 * u, -0.10 * u + 0.015 * math.sin(u * math.pi))))
        strands.append(pts)
        continue
    # ponytail: tied tight, round, falls in clumps with a slight wave; shorter
    ci = random.randrange(TAILC)
    cang, crr, cph, clen = tail_clumps[ci]
    ang = random.random() * 2 * math.pi
    rr = 0.0045 * math.sqrt(random.random())
    bundle = Vector((math.cos(cang) * crr + math.cos(ang) * rr, 0.9 * (math.sin(cang) * crr + math.sin(ang) * rr), 0.0))
    pts[-1] = TIE + bundle * 0.55
    L = clen * random.uniform(0.85, 1.05)
    M = 12
    for k in range(1, M + 1):
        u = k / M
        spread = 0.55 + 1.05 * math.sin(min(u / 0.45, 1.0) * math.pi / 2) - 0.55 * max(0.0, u - 0.55) / 0.45
        wave = 0.005 * math.sin(u * math.pi * 1.6 + cph) * u
        q = TIE + Vector((bundle.x * spread + wave, 0.010 + bundle.y * spread + 0.028 * u - 0.012 * u * u, -L * u))
        hit = bvh.find_nearest(q)                   # keep the tail off the neck
        if hit[0] is not None and (q - hit[0]).length < 0.009 and (q - hit[0]).dot(hit[1]) >= 0:
            q = hit[0] + hit[1] * 0.009
        q += Vector((random.gauss(0, 0.0012), random.gauss(0, 0.0012), 0)) * u
        pts.append(q)
    strands.append(pts)


# loose locks that slipped out of the slicked hair and fall by the face (mostly on his right, -x)
def bez(P, t):
    n = len(P) - 1
    pts = list(P)
    for r in range(n):
        pts = [pts[i] * (1 - t) + pts[i + 1] * t for i in range(len(pts) - 1)]
    return pts[0]

LOCKS = [  # rooted inside the hair, run forward over the hairline, then fall
    (Vector((-0.034, -0.080, 1.866)), [Vector((-0.038, -0.110, 1.852)), Vector((-0.062, -0.120, 1.820)), Vector((-0.083, -0.085, 1.760)), Vector((-0.086, -0.066, 1.705))], 260),
    (Vector((-0.050, -0.072, 1.858)), [Vector((-0.056, -0.100, 1.842)), Vector((-0.078, -0.104, 1.800)), Vector((-0.087, -0.070, 1.748)), Vector((-0.089, -0.058, 1.722))], 200),
    (Vector((-0.016, -0.088, 1.871)), [Vector((-0.020, -0.120, 1.858)), Vector((-0.032, -0.137, 1.830)), Vector((-0.044, -0.133, 1.798)), Vector((-0.050, -0.128, 1.784))], 160),
    (Vector((0.044, -0.076, 1.860)), [Vector((0.050, -0.102, 1.846)), Vector((0.073, -0.106, 1.812)), Vector((0.083, -0.080, 1.770))], 130),
]
nl = 0
for root0, ctrl, cnt in LOCKS:
    h = bvh.find_nearest(root0)
    base = h[0] if h[0] is not None else root0
    for s_ in range(cnt):
        off = Vector((random.gauss(0, 0.0022), random.gauss(0, 0.0018), random.gauss(0, 0.0012)))
        rt = bvh.find_nearest(base + off)[0] or base + off
        P = [rt] + [c + off * max(0.35, 1.0 - 0.18 * i) + Vector((random.gauss(0, 0.0008), random.gauss(0, 0.0008), random.gauss(0, 0.002))) * i for i, c in enumerate(ctrl, 1)]
        endt = random.uniform(0.7, 1.0)
        pts = []
        for k in range(16):
            q = bez(P, endt * k / 15)
            hh = bvh.find_nearest(q)
            if k > 1 and hh[0] is not None and (q - hh[0]).length < 0.007:
                q = hh[0] + hh[1] * 0.007
            pts.append(q)
        strands.append(pts)
        nl += 1
print("locks", nl)

curves = bpy.data.hair_curves.new("DuncanHair")
curves.add_curves([len(p) for p in strands])
flat = [c for p in strands for v in p for c in v]
curves.attributes["position"].data.foreach_set("vector", flat)
obj = bpy.data.objects.new("DuncanHair", curves)
bpy.context.collection.objects.link(obj)
print("strands", len(strands), "points", len(flat) // 3)

for o in bpy.context.scene.objects: o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.wm.alembic_export(filepath=HERE + "/duncan_hair7.abc", selected=True, start=1, end=1)
print("ABC", os.path.getsize(HERE + "/duncan_hair7.abc"))

# quick preview: workbench render front and side
scn = bpy.context.scene
scn.render.engine = "BLENDER_WORKBENCH"
scn.render.resolution_x, scn.render.resolution_y = 700, 700
cam_data = bpy.data.cameras.new("cam"); cam_data.lens = 85
cam = bpy.data.objects.new("cam", cam_data); scn.collection.objects.link(cam); scn.camera = cam
for name, loc in (("front", (0, -1.0, 1.75)), ("side", (1.0, 0.0, 1.74)), ("q34", (0.7, -0.7, 1.75))):
    cam.location = loc
    dvec = Vector((0, -0.01, 1.72)) - Vector(loc)
    cam.rotation_euler = dvec.to_track_quat("-Z", "Y").to_euler()
    scn.render.filepath = HERE + "/preview7_%s.png" % name
    bpy.ops.render.render(write_still=True)
print("DONE")
