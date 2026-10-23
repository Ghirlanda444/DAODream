"""An outfit fitted to one MetaHuman body (Blender 5.2, run headless):

blender -b --factory-startup -P outfit.py -- <body.fbx> <default.fbx> <out.fbx> <kind> [f|m]

<body.fbx> is the character's body mesh exported from Unreal (its skeleton, skin weights and UVs come
with it) and <default.fbx> its default clothes (the build's T-shirt and shorts, MHC_<Name>_Outfits):
the build cuts the body away under those, so together they are the whole figure; <kind> is a recipe below, named after the game item it stands for (the chest item's name
without "gen_im_", e.g. arm_cht_med_chn). The outfit is built from the body itself, so it fits:

- shells: the body's surface over some regions (by the bone that moves each vertex most: torso, arms,
  hands, legs, feet) pushed out along its normals, smoothed and given thickness;
- lofts: skirts, coat tails and mail skirts, rings around both legs from a top height down to a hem,
  each ring the convex outline of the body at that height plus an offset and a flare;
- weights: copied from the body (nearest face), and smoothed on lofts so a skirt does not split
  between the legs; UVs at the body's texel density (shells keep the body's UVs);
- vertex colour R: 1 within TRIM cm of an open edge (hems, cuffs, collars), for the trim band.

Material slots: 0 main cloth, 1 second cloth, 2 leather, 3 metal. The result is exported with the
body's armature, for import onto the MetaHuman skeleton (metahuman_base_skel).
Blender frame: metres, the character faces -y, +x is its left; A-pose."""
import bpy, bmesh, math, sys
from collections import defaultdict, deque
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ARGS = sys.argv[sys.argv.index("--") + 1:]
BODY, DEFAULT, OUT, KIND = ARGS[:4]
FEMALE = len(ARGS) > 4 and ARGS[4].lower().startswith("f")  # the same item can dress a man or a woman
TRIM = 0.035  # m
MAIN, SECOND, LEATHER, METAL = 0, 1, 2, 3


# --- the body -------------------------------------------------------------------------------------------

def region(bone: str) -> str:
    b = bone.lower()
    if b.startswith(("head", "neck_02", "face")):
        return "head"
    if b.startswith("neck_01"):
        return "neck"
    if b.startswith(("hand_", "thumb", "index", "middle", "ring", "pinky")):
        return "hand"
    if b.startswith(("lowerarm", "wrist")):
        return "forearm"
    if b.startswith("upperarm"):
        return "upperarm"
    if b.startswith(("thigh",)):
        return "thigh"
    if b.startswith(("calf",)):
        return "calf"
    if b.startswith(("foot", "ball", "toe", "bigtoe", "indextoe", "middletoe", "ringtoe", "littletoe")):
        return "foot"
    return "torso"  # pelvis, spine, clavicles


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=BODY)
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
body = next(o for o in bpy.data.objects if o.type == "MESH")
bpy.ops.import_scene.fbx(filepath=DEFAULT)
extra = [o for o in bpy.data.objects if o.type in ("MESH", "ARMATURE") and o not in (arm, body)]
bpy.ops.object.select_all(action="DESELECT")
for o in extra:
    if o.type == "MESH":
        o.select_set(True)
body.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.join()  # one reference surface; vertex groups merge by bone name
for o in [o for o in bpy.data.objects if o.type == "ARMATURE" and o is not arm]:
    bpy.data.objects.remove(o)
# Unreal's FBX puts the armature under an empty scaled 0.01 (centimetres): work in plain metres, with the
# armature at scale 1, so the outfit can be parented to it as it is.
bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
for o in [o for o in bpy.data.objects if o.type == "EMPTY"]:
    bpy.data.objects.remove(o)
names = {g.index: g.name for g in body.vertex_groups}
BM = bmesh.new()
BM.from_mesh(body.data)
BM.transform(body.matrix_world)
BM.verts.ensure_lookup_table()
BM.faces.ensure_lookup_table()
BM.normal_update()
REG = []
for v in body.data.vertices:
    best = max(v.groups, key=lambda g: g.weight, default=None)
    REG.append(region(names[best.group]) if best else "torso")


def bone_z(name: str) -> float:
    return (arm.matrix_world @ arm.data.bones[name].head_local).z


def bone_pos(name: str) -> Vector:
    return arm.matrix_world @ arm.data.bones[name].head_local


Z_HIP = bone_z("pelvis")
Z_KNEE = (bone_z("calf_l") + bone_z("calf_r")) / 2
Z_ANKLE = (bone_z("foot_l") + bone_z("foot_r")) / 2
Z_CHEST = bone_z("spine_05")
Z_FLOOR = min(v.co.z for v in BM.verts)
CENTRE = bone_pos("pelvis")
SURFACE = BVHTree.FromBMesh(BM)
uv_layer = BM.loops.layers.uv.active


def uv_density() -> float:
    """UV units per metre on the body, for lofts to match."""
    total_uv = total_m = 0.0
    for f in BM.faces[:3000]:
        for l in f.loops:
            n = l.link_loop_next
            total_m += (l.vert.co - n.vert.co).length
            total_uv += (Vector(l[uv_layer].uv) - Vector(n[uv_layer].uv)).length
    return total_uv / max(total_m, 1e-6)


UVD = uv_density()


# --- building blocks ------------------------------------------------------------------------------------

class Part:
    """Geometry of one material, gathered into one bmesh (then one object per part)."""
    def __init__(self, name, mat, loft=False):
        self.name, self.mat, self.loft = name, mat, loft
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UV")


def shell(name, regions, offset, mat, z_min=-1.0, z_max=9.0, smooth=6, thickness=0.004):
    """The body's faces over `regions` (and between z_min and z_max), pushed out `offset` m."""
    p = Part(name, mat)
    keep = [f for f in BM.faces if all(REG[v.index] in regions and z_min <= v.co.z <= z_max for v in f.verts)]
    vmap = {}
    for f in keep:
        for v in f.verts:
            if v.index not in vmap:
                vmap[v.index] = p.bm.verts.new(v.co + v.normal * offset)
    for f in keep:
        try:
            nf = p.bm.faces.new([vmap[v.index] for v in f.verts])
        except ValueError:
            continue
        for nl, l in zip(nf.loops, f.loops):
            nl[p.uv].uv = l[uv_layer].uv
    bmesh.ops.remove_doubles(p.bm, verts=list(p.bm.verts), dist=0.001)  # the body's UV seams
    # Smooth away the body's small detail (navel, ribs, knuckles), and relax the cut edges, which follow
    # the body's triangles, into smooth hems.
    for _ in range(smooth):
        bmesh.ops.smooth_vert(p.bm, verts=[v for v in p.bm.verts if not v.is_boundary], factor=0.5,
                              use_axis_x=True, use_axis_y=True, use_axis_z=True)
    relax_edges(p.bm, 2 * smooth + 4)
    p.thickness = thickness
    p.offset = offset
    return p


def relax_edges(bm, iterations):
    """Move each open-edge vertex towards the middle of its two neighbours along the edge."""
    for _ in range(iterations):
        moves = {}
        for v in bm.verts:
            if not v.is_boundary:
                continue
            ns = [e.other_vert(v) for e in v.link_edges if e.is_boundary]
            if len(ns) == 2:
                moves[v] = v.co * 0.5 + (ns[0].co + ns[1].co) * 0.25
        for v, co in moves.items():
            v.co = co


def keep_outside(bm, offset):
    """Push vertices that are inside the body, or nearer than `offset`, out to `offset` from it."""
    for v in bm.verts:
        loc, nor, _, _ = SURFACE.find_nearest(v.co)
        if loc is not None and (v.co - loc).dot(nor) < offset * 0.8:
            v.co = loc + nor * offset


def outline(z, regions, samples=48, slab=0.025):
    """Distance from the centre line to the body's convex outline at height z, per angle."""
    pts = [v.co for v in BM.verts if abs(v.co.z - z) < slab and REG[v.index] in regions]
    if not pts:
        return None
    out = []
    for i in range(samples):
        a = 2 * math.pi * i / samples
        u = Vector((math.cos(a), math.sin(a), 0.0))
        out.append(max((Vector((q.x - CENTRE.x, q.y - CENTRE.y, 0.0))).dot(u) for q in pts))
    return out


def loft(name, z_top, z_hem, offset, mat, flare=0.0, samples=48, step=0.02, regions=("torso", "thigh", "calf", "foot"),
         thickness=0.004, arc=None):
    """A tube round the body from z_top down to z_hem: each ring the body's outline plus `offset`,
    widening by `flare` (m) towards the hem, never narrower than the ring above (cloth hangs). With
    `arc` (degrees from +x, anticlockwise; the front is 270) only that part of the tube: an apron."""
    p = Part(name, mat, loft=True)
    zs = []
    z = z_top
    while z > z_hem:
        zs.append(z)
        z -= step
    zs.append(z_hem)
    rings, prev = [], None
    for k, z in enumerate(zs):
        r = outline(z, regions, samples) or prev
        if r is None:
            continue
        t = (z_top - z) / max(z_top - z_hem, 1e-6)
        mean = sum(r) / len(r)
        # rounder as it hangs, but never inside the body's outline
        r = [max(x + (mean - x) * 0.6 * t, x) + offset + flare * t for x in r]
        if prev and z < Z_HIP:  # below the hips cloth hangs: no narrower than the ring above
            r = [max(a, b) for a, b in zip(r, prev)]
        prev = r
        rings.append((z, r))
    # Smooth each ring round the body, so it hangs as cloth rather than following every bulge.
    sm = []
    for z, r in rings:
        n = len(r)
        sm.append((z, [(r[i - 1] + 2 * r[i] + r[(i + 1) % n]) / 4 for i in range(n)]))
    grid = []
    for z, r in sm:
        row = []
        for i, d in enumerate(r):
            a = 2 * math.pi * i / samples
            row.append(p.bm.verts.new((CENTRE.x + d * math.cos(a), CENTRE.y + d * math.sin(a), z)))
        grid.append(row)
    for j in range(len(grid) - 1):
        circ = sum(sm[j][1]) / samples * 2 * math.pi  # u: around, v: down, at the body's UV density
        for i in range(samples):
            if arc and not (arc[0] <= 360.0 * i / samples and 360.0 * (i + 1) / samples <= arc[1]):
                continue
            corners = ((j, i), (j + 1, i), (j + 1, i + 1), (j, i + 1))
            f = p.bm.faces.new([grid[jj][ii % samples] for jj, ii in corners])
            for l, (jj, ii) in zip(f.loops, corners):
                l[p.uv].uv = (ii / samples * circ * UVD, (z_top - sm[jj][0]) * UVD)
    bmesh.ops.delete(p.bm, geom=[v for v in p.bm.verts if not v.link_faces], context="VERTS")
    p.thickness = thickness
    p.offset = offset
    return p


def band(name, z, width, offset, mat, regions=("torso", "thigh")):
    """A belt or girdle: a short loft."""
    return loft(name, z + width / 2, z - width / 2, offset, mat, step=width / 2, regions=regions, thickness=0.006)


# --- recipes --------------------------------------------------------------------------------------------

def mid_thigh():
    return Z_HIP - 0.55 * (Z_HIP - Z_KNEE)


def guard_chain(long=False):
    """Mail (gen_im_arm_cht_med_chn, castle guards and Gilmore; long for heavy mail and scale, Fergus and
    Howe's knight): a hauberk with sleeves to the wrist and a skirt to mid-thigh (to the knee when long),
    a sleeveless surcoat in the house's colour, belt, hose, leather boots and gloves."""
    return [shell("hauberk", {"torso", "upperarm", "forearm", "neck"}, 0.010, METAL, z_min=Z_HIP - 0.04),
            loft("mail_skirt", Z_HIP + 0.02, Z_KNEE + 0.03 if long else mid_thigh(), 0.012, METAL, flare=0.03),
            shell("surcoat_top", {"torso"}, 0.019, MAIN, z_min=Z_HIP - 0.02, z_max=Z_CHEST + 0.10),
            loft("surcoat_skirt", Z_HIP + 0.06, Z_KNEE - (0.06 if long else -0.02), 0.026, MAIN, flare=0.07),
            band("belt", Z_HIP + 0.03, 0.045, 0.030, LEATHER),
            shell("hose", {"thigh", "calf"}, 0.005, SECOND, z_min=Z_ANKLE + 0.06),
            shell("boots", {"thigh", "calf", "foot"}, 0.012, LEATHER, z_max=Z_KNEE - 0.08, smooth=12),
            shell("gloves", {"hand"}, 0.004, LEATHER, smooth=3)]


def leather(reinforced=False):
    """Howe's men (gen_im_arm_cht_lgt_ltr, _rlr): a padded gambeson in the house's colour with a skirt to
    mid-thigh, a sleeveless leather jerkin over it, belt, hose, boots and gloves; reinforced leather adds
    mail on the forearms and metal shoulders."""
    parts = [shell("gambeson", {"torso", "upperarm", "forearm", "neck"}, 0.009, MAIN, z_min=Z_HIP - 0.04),
             loft("gambeson_skirt", Z_HIP + 0.02, mid_thigh(), 0.014, MAIN, flare=0.04),
             shell("jerkin", {"torso"}, 0.018, LEATHER, z_min=Z_HIP - 0.03, z_max=Z_CHEST + 0.12),
             loft("jerkin_skirt", Z_HIP + 0.05, Z_HIP - 0.16, 0.022, LEATHER, flare=0.03),
             band("belt", Z_HIP + 0.03, 0.04, 0.028, LEATHER),
             shell("hose", {"thigh", "calf"}, 0.005, SECOND, z_min=Z_ANKLE + 0.06),
             shell("boots", {"thigh", "calf", "foot"}, 0.012, LEATHER, z_max=Z_KNEE - 0.08, smooth=12),
             shell("gloves", {"hand"}, 0.004, LEATHER, smooth=3)]
    if reinforced:
        parts += [shell("mail_sleeves", {"forearm"}, 0.013, METAL),
                  shell("shoulders", {"upperarm", "torso"}, 0.026, METAL, z_min=Z_CHEST + 0.04, smooth=8)]
    return parts


def noble_man():
    """A nobleman (gen_im_cth_nob_*: Bryce, Howe, Dairren): a long-sleeved doublet, a coat to the knee
    over it, belt, hose and boots."""
    return [shell("doublet", {"torso", "upperarm", "forearm", "neck"}, 0.007, SECOND, z_min=Z_HIP - 0.04),
            shell("coat_top", {"torso", "upperarm"}, 0.014, MAIN, z_min=Z_HIP - 0.02, z_max=Z_CHEST + 0.12),
            loft("coat_skirt", Z_HIP + 0.06, Z_KNEE - 0.02, 0.020, MAIN, flare=0.06),
            band("belt", Z_HIP + 0.03, 0.040, 0.024, LEATHER),
            shell("hose", {"thigh", "calf"}, 0.005, SECOND, z_min=Z_ANKLE + 0.06),
            shell("boots", {"thigh", "calf", "foot"}, 0.012, LEATHER, z_max=Z_KNEE - 0.06, smooth=12)]


def noble_woman():
    """A noblewoman (gen_im_cth_nob_*: Eleanor, Oriana, Landra, Iona): a gown with long sleeves, a
    fitted bodice and a full skirt to the floor, a girdle, and shoes."""
    return [shell("bodice", {"torso", "upperarm", "forearm", "neck"}, 0.006, MAIN, z_min=Z_HIP - 0.06),
            loft("skirt", Z_HIP + 0.05, Z_FLOOR + 0.03, 0.015, MAIN, flare=0.16),
            band("girdle", Z_HIP + 0.04, 0.030, 0.020, METAL),
            shell("shoes", {"foot"}, 0.010, LEATHER, smooth=12)]


def commoner():
    """Servants, the cook, the librarian (gen_im_cth_com_*). A man: a wool tunic with long sleeves to
    mid-thigh, belt, hose and short boots. A woman: a long dress, an apron, belt and shoes."""
    if FEMALE:
        return [shell("bodice", {"torso", "upperarm", "forearm", "neck"}, 0.007, MAIN, z_min=Z_HIP - 0.06),
                loft("skirt", Z_HIP + 0.05, Z_FLOOR + 0.05, 0.015, MAIN, flare=0.10),
                loft("apron", Z_HIP + 0.04, Z_KNEE - 0.12, 0.028, SECOND, flare=0.06, arc=(215, 325)),
                band("belt", Z_HIP + 0.04, 0.03, 0.032, LEATHER),
                shell("shoes", {"foot"}, 0.010, LEATHER, smooth=12)]
    return [shell("tunic", {"torso", "upperarm", "forearm", "neck"}, 0.008, MAIN, z_min=Z_HIP - 0.04),
            loft("tunic_skirt", Z_HIP + 0.04, mid_thigh() - 0.04, 0.014, MAIN, flare=0.05),
            band("belt", Z_HIP + 0.03, 0.035, 0.022, LEATHER),
            shell("hose", {"thigh", "calf"}, 0.005, SECOND, z_min=Z_ANKLE + 0.06),
            shell("boots", {"thigh", "calf", "foot"}, 0.011, LEATHER, z_max=Z_ANKLE + 0.14, smooth=12)]


def robe(stole=False, gloves=False):
    """A long robe (gen_im_cth_mag_tra Aldous, gen_im_cth_cha_a00 Mother Mallol, gen_im_duncan_robe):
    long sleeves, a skirt from the waist to the floor, a cord belt, shoes; a Chantry stole over the
    shoulders, or (Duncan) leather gloves."""
    parts = [shell("robe_top", {"torso", "upperarm", "forearm", "neck"}, 0.010, MAIN, z_min=Z_HIP - 0.06),
             loft("robe_skirt", Z_HIP + 0.10, Z_FLOOR + 0.03, 0.018, MAIN, flare=0.12),
             band("cord", Z_HIP + 0.05, 0.022, 0.026, LEATHER),
             shell("shoes", {"foot"}, 0.010, LEATHER, smooth=12)]
    if stole:
        parts.append(shell("stole", {"torso", "neck"}, 0.017, SECOND, z_min=Z_CHEST - 0.02, smooth=8))
    if gloves:
        parts.append(shell("gloves", {"hand"}, 0.004, LEATHER, smooth=3))
    return parts


RECIPES = {"arm_cht_med_chn": guard_chain, "arm_cht_hvy_hch": lambda: guard_chain(long=True),
           "arm_cht_med_scl": lambda: guard_chain(long=True), "arm_cht_lgt_ltr": leather,
           "arm_cht_lgt_rlr": lambda: leather(reinforced=True),
           "cth_mag_tra": robe, "cth_cha_a00": lambda: robe(stole=True), "duncan_robe": lambda: robe(gloves=True)}


def recipe(kind):
    """By item; noble and common clothes not listed go to the general recipes, by sex."""
    if kind in RECIPES:
        return RECIPES[kind]()
    if kind.startswith("cth_nob_"):
        return noble_woman() if FEMALE else noble_man()
    if kind.startswith("cth_com_"):
        return commoner()
    if kind.startswith("cth_mag_"):  # mage and apprentice robes
        return robe()
    raise SystemExit("no recipe for " + kind)


# --- assemble -------------------------------------------------------------------------------------------

def to_object(p: Part):
    if not p.loft:  # lofts stay outside by construction (the outline)
        keep_outside(p.bm, p.offset)
    me = bpy.data.meshes.new(p.name)
    p.bm.normal_update()
    p.bm.to_mesh(me)
    ob = bpy.data.objects.new(p.name, me)
    bpy.context.collection.objects.link(ob)
    for m in MATS:
        me.materials.append(m)
    for f in me.polygons:
        f.material_index = p.mat
        f.use_smooth = True
    ob["loft"] = p.loft
    ob["thickness"] = p.thickness
    return ob


def trim_mask(me):
    """Vertex colour R: 1 at open edges fading to 0 at TRIM metres, by distance along the mesh."""
    bm = bmesh.new()
    bm.from_mesh(me)
    dist = {v.index: (0.0 if v.is_boundary else 1e9) for v in bm.verts}
    q = deque(v for v in bm.verts if v.is_boundary)
    while q:
        v = q.popleft()
        for e in v.link_edges:
            w = e.other_vert(v)
            d = dist[v.index] + e.calc_length()
            if d < dist[w.index] and d < TRIM * 1.5:
                dist[w.index] = d
                q.append(w)
    bm.free()
    col = me.color_attributes.new("Col", "BYTE_COLOR", "CORNER")
    for poly in me.polygons:
        for li in poly.loop_indices:
            d = dist[me.loops[li].vertex_index]
            t = max(0.0, 1.0 - d / TRIM)
            col.data[li].color = (t, 0.0, 0.0, 1.0)


MATS = [bpy.data.materials.new(n) for n in ("Main", "Second", "Leather", "Metal")]
parts = [to_object(p) for p in recipe(KIND)]
for ob in parts:
    trim_mask(ob.data)
    # thickness, weights from the body
    so = ob.modifiers.new("solid", "SOLIDIFY")
    so.thickness = ob["thickness"]
    so.offset = 1.0
    so.use_rim = True
    for g in body.vertex_groups:
        ob.vertex_groups.new(name=g.name)
    dt = ob.modifiers.new("weights", "DATA_TRANSFER")
    dt.object = body
    dt.use_vert_data = True
    dt.data_types_verts = {"VGROUP_WEIGHTS"}
    dt.vert_mapping = "POLYINTERP_NEAREST"
    dt.layers_vgroup_select_src = "ALL"
    dt.layers_vgroup_select_dst = "NAME"
    bpy.context.view_layer.objects.active = ob
    for m in list(ob.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)
    if ob["loft"]:  # skirts: blend the legs' weights so the cloth does not split between them
        ob.select_set(True)
        bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
        bpy.ops.object.vertex_group_smooth(group_select_mode="ALL", factor=0.8, repeat=12, expand=0.2)
        bpy.ops.object.mode_set(mode="OBJECT")
        ob.select_set(False)
    # drop empty groups, keep at most 8 influences
    bpy.ops.object.vertex_group_clean(group_select_mode="ALL", limit=0.01)
    bpy.ops.object.vertex_group_limit_total(group_select_mode="ALL", limit=8)

bpy.ops.object.select_all(action="DESELECT")
for ob in parts:
    ob.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
outfit = bpy.context.view_layer.objects.active
outfit.name = "Outfit_" + KIND
cols = outfit.data.color_attributes
cols.active_color = cols["Col"]  # the FBX exporter writes the active colour attribute
cols.render_color_index = cols.active_color_index
mod = outfit.modifiers.new("Armature", "ARMATURE")
mod.object = arm
outfit.parent = arm
outfit.matrix_parent_inverse = arm.matrix_world.inverted()
bpy.data.objects.remove(body)
# Export in centimetres, bones and vertices alike (as Unreal wrote the body): scale the rig up 100 times,
# apply, and declare 1 unit = 1 cm. With the bones left in metres the outfit's bind pose would not match
# the skeleton it follows in game, and it would be drawn a hundred times too big.
bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True)
outfit.select_set(True)
bpy.context.view_layer.objects.active = arm
arm.scale = (100.0, 100.0, 100.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.context.scene.unit_settings.scale_length = 0.01
bpy.ops.object.select_all(action="DESELECT")
outfit.select_set(True)
arm.select_set(True)
bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, object_types={"ARMATURE", "MESH"}, add_leaf_bones=False,
                         bake_anim=False, mesh_smooth_type="FACE", colors_type="LINEAR")
print("OUTFIT", KIND, len(outfit.data.vertices), "verts", "->", OUT)
