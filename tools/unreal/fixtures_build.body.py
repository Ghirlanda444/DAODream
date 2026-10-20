# Runs inside the editor (pyrun): builds the castle's lamp and fire assets in /Game/Cousland/Fixtures from
# primitives and procedural materials, no textures. Re-running updates the assets in place.
import math

# Asset lookups report nothing while Play/Simulate runs, and this would then try to re-create (overwrite) them.
if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world():
    raise RuntimeError("stop Play/Simulate first")

DIR = "/Game/Cousland/Fixtures"
AT = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
P = unreal.GeometryScript_Primitives
IRON, WOOD, WAX, EMBERS = 0, 1, 2, 3
report = {}

# --- materials ---------------------------------------------------------------------------------------------

# Value noise at p into n (declare float n first); a block, so it can be used twice.
NOISE = r"""
{
    float3 i = floor(p); float3 f = frac(p); f = f * f * (3.0 - 2.0 * f);
    n = 0;
    for (int k = 0; k < 8; k++) {
        float3 o = float3(k & 1, (k >> 1) & 1, (k >> 2) & 1);
        float h = frac(sin(dot(i + o, float3(12.9898, 78.233, 37.719))) * 43758.5453);
        float3 w = lerp(1.0 - f, f, o);
        n += h * w.x * w.y * w.z;
    }
}
"""


def material(name, setup):
    path = DIR + "/" + name
    if EAL.does_asset_exist(path):
        m = EAL.load_asset(path)
        MEL.delete_all_material_expressions(m)
    else:
        m = AT.create_asset(name, DIR, unreal.Material, unreal.MaterialFactoryNew())
    setup(m)
    MEL.recompile_material(m)
    EAL.save_loaded_asset(m)
    report[name] = "ok"
    return m


def const3(m, rgb, x, y):
    e = MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, x, y)
    e.set_editor_property("constant", unreal.LinearColor(*rgb, 1.0))
    return e


def const(m, v, x, y):
    e = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, x, y)
    e.set_editor_property("r", v)
    return e


def scalar(m, name, v, x, y):
    e = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, x, y)
    e.set_editor_property("parameter_name", name)
    e.set_editor_property("default_value", v)
    return e


def custom(m, code, inputs, out_type, x, y):
    e = MEL.create_material_expression(m, unreal.MaterialExpressionCustom, x, y)
    e.set_editor_property("code", code)
    e.set_editor_property("output_type", out_type)
    ins = []
    for n, _ in inputs:
        ci = unreal.CustomInput()
        ci.set_editor_property("input_name", n)
        ins.append(ci)
    e.set_editor_property("inputs", ins)
    for n, src in inputs:
        src, pin = src if isinstance(src, tuple) else (src, "")
        MEL.connect_material_expressions(src, pin, e, n)
    return e


def solid(rgb, rough, metal):
    def setup(m):
        m.set_editor_property("used_with_instanced_static_meshes", True)
        wp = MEL.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -900, 0)
        # Two tints, mottled by world-space noise (rust and soot on iron, grain on wood).
        code = "float3 p = WP * 0.045; float n;" + NOISE + "return lerp(A, B, saturate(n * 1.6 - 0.3));"
        c = custom(m, code, [("WP", wp), ("A", const3(m, rgb[0], -900, 150)), ("B", const3(m, rgb[1], -900, 300))],
                   unreal.CustomMaterialOutputType.CMOT_FLOAT3, -500, 0)
        MEL.connect_material_property(c, "", unreal.MaterialProperty.MP_BASE_COLOR)
        MEL.connect_material_property(const(m, rough, -500, 200), "", unreal.MaterialProperty.MP_ROUGHNESS)
        MEL.connect_material_property(const(m, metal, -500, 300), "", unreal.MaterialProperty.MP_METALLIC)
    return setup


def embers(m):
    # Charred wood or coals whose cracks glow and flicker: world-space noise drifting upward over time.
    m.set_editor_property("used_with_instanced_static_meshes", True)
    wp = MEL.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -900, 0)
    t = MEL.create_material_expression(m, unreal.MaterialExpressionTime, -900, 150)
    glow = scalar(m, "Glow", 12.0, -900, 300)
    code = ("float3 p = WP * 0.09 + float3(0, 0, -T * 0.35); float n;" + NOISE +
            "float a = n; p = WP * 0.21 + float3(0, T * 0.5, 0);" + NOISE +
            "float c = saturate((a * 0.65 + n * 0.35 - 0.52) * 7.0);"
            "return float3(1.0, 0.32, 0.06) * c * c * G;")
    e = custom(m, code, [("WP", wp), ("T", t), ("G", glow)], unreal.CustomMaterialOutputType.CMOT_FLOAT3, -500, 0)
    MEL.connect_material_property(e, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.connect_material_property(const3(m, (0.025, 0.018, 0.014), -500, 200), "", unreal.MaterialProperty.MP_BASE_COLOR)
    MEL.connect_material_property(const(m, 0.9, -500, 300), "", unreal.MaterialProperty.MP_ROUGHNESS)


def flame(m):
    # A camera-facing flame tongue for Niagara sprites: a teardrop that licks and wavers over time (each
    # particle out of phase), white-yellow at the core and orange-red at the edges. Particle colour tints
    # it and its alpha fades it; additive, so overlapping tongues build a fire.
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE)
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    m.set_editor_property("two_sided", True)
    m.set_editor_property("used_with_niagara_sprites", True)
    uv = MEL.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -900, 0)
    t = MEL.create_material_expression(m, unreal.MaterialExpressionTime, -900, 100)
    pc = MEL.create_material_expression(m, unreal.MaterialExpressionParticleColor, -900, 200)
    pr = MEL.create_material_expression(m, unreal.MaterialExpressionParticleRandom, -900, 300)
    glow = scalar(m, "Glow", 7.0, -900, 400)
    code = r"""
float2 p = UV * 2.0 - 1.0; p.y = -p.y;
float h = saturate(p.y * 0.5 + 0.5);
p.x += (sin(p.y * 5.0 - T * 9.0 + R * 40.0) * 0.6 + sin(p.y * 11.0 - T * 15.0 + R * 17.0) * 0.4) * 0.16 * h;
float w = lerp(0.62, 0.04, saturate((p.y + 0.75) / 1.65));
float body = saturate(1.0 - abs(p.x) / max(w, 0.02)) * saturate((p.y + 0.97) * 4.0) * saturate((0.98 - p.y) * 2.0);
body = pow(body, 1.4);
float core = pow(body, 3.0) * (1.0 - h * 0.6);
float3 c = lerp(float3(1.0, 0.16, 0.02), float3(1.0, 0.5, 0.14), saturate(core * 1.4));
return c * PC * body * PA * G;
"""
    e = custom(m, code, [("UV", uv), ("T", t), ("PC", pc), ("PA", (pc, "A")), ("R", pr), ("G", glow)],
               unreal.CustomMaterialOutputType.CMOT_FLOAT3, -500, 0)
    MEL.connect_material_property(e, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)


def spark(m):
    # A soft round ember for Niagara sprites.
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE)
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    m.set_editor_property("used_with_niagara_sprites", True)
    uv = MEL.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -900, 0)
    pc = MEL.create_material_expression(m, unreal.MaterialExpressionParticleColor, -900, 200)
    glow = scalar(m, "Glow", 16.0, -900, 400)
    code = "float d = saturate(1.0 - length(UV * 2.0 - 1.0)); return float3(1.0, 0.45, 0.12) * PC * d * d * PA * G;"
    e = custom(m, code, [("UV", uv), ("PC", pc), ("PA", (pc, "A")), ("G", glow)], unreal.CustomMaterialOutputType.CMOT_FLOAT3, -500, 0)
    MEL.connect_material_property(e, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)


mats = [material("M_FixtureIron", solid(((0.03, 0.028, 0.026), (0.09, 0.055, 0.035)), 0.55, 0.85)),
        material("M_FixtureWood", solid(((0.10, 0.06, 0.03), (0.16, 0.10, 0.055)), 0.8, 0.0)),
        material("M_FixtureWax", solid(((0.80, 0.74, 0.60), (0.86, 0.80, 0.68)), 0.45, 0.0)),
        material("M_FixtureEmbers", embers)]
material("M_Flame", flame)
material("M_Spark", spark)

# --- meshes ------------------------------------------------------------------------------------------------


def opts(mat):
    o = unreal.GeometryScriptPrimitiveOptions()
    o.material_id = mat
    return o


def xf(loc=(0, 0, 0), rot=None, scale=(1, 1, 1)):
    return unreal.Transform(unreal.Vector(*loc), rot or unreal.Rotator(0, 0, 0), unreal.Vector(*scale))


def rod(dm, a, b, radius, mat, steps=6):
    """A cylinder from point a to point b."""
    a, b = unreal.Vector(*a), unreal.Vector(*b)
    d = b - a
    rot = unreal.MathLibrary.make_rot_from_z(d.normal())
    P.append_cylinder(dm, opts(mat), unreal.Transform(a, rot, unreal.Vector(1, 1, 1)), radius, d.length(), steps, 0, True)


def revolve(dm, profile, mat, z=0.0, steps=24):
    ro = unreal.GeometryScriptRevolveOptions()
    ro.revolve_degrees = 360.0
    P.append_revolve_path(dm, opts(mat), xf((0, 0, z)), [unreal.Vector2D(r, h) for r, h in profile], ro, steps, False)


def torus(dm, loc, rot, major, minor, mat, steps=(16, 6)):
    ro = unreal.GeometryScriptRevolveOptions()
    ro.revolve_degrees = 360.0
    P.append_torus(dm, opts(mat), xf(loc, rot), ro, major, minor, steps[0], steps[1], unreal.GeometryScriptPrimitiveOriginMode.CENTER)


BOWL = [(0.1, -15.0), (9, -15.0), (19, -11.0), (25, -3.0), (27.5, 3.0), (26.2, 4.2), (23.5, 0.8), (17.5, -7.5),
        (8.5, -11.5), (0.1, -11.5)]


def fire_bowl(dm, apex):
    """An iron bowl of glowing coals, its fire at the origin, hung from three rods meeting `apex` cm above."""
    revolve(dm, BOWL, IRON)
    torus(dm, (0, 0, 3.6), None, 26.8, 1.3, IRON, (24, 6))
    P.append_cone(dm, opts(EMBERS), xf((0, 0, -11.0)), 22.0, 7.0, 9.0, 16, 1, True)
    for k in range(3):
        a = math.radians(90 + k * 120)
        rod(dm, (26 * math.cos(a), 26 * math.sin(a), 4), (0, 0, apex), 0.7, IRON)
    torus(dm, (0, 0, apex + 2.4), unreal.Rotator(90, 0, 0), 2.4, 0.6, IRON, (12, 5))


def chain(dm, length=100.0, pitch=3.6):
    for k in range(int(length / pitch)):
        torus(dm, (0, 0, k * pitch + 2.2), unreal.Rotator(90, 0, 90 * (k % 2)), 2.1, 0.5, IRON, (10, 4))


def wall_lamp(dm):
    """A fire bowl on a bracket: the wall is at +X (the export's yaw turns +X to the fixture's back)."""
    fire_bowl(dm, 40.0)
    rod(dm, (0, 0, 44.8), (43, 0, 44.8), 1.2, IRON)
    rod(dm, (43, 0, 8), (16, 0, 44.8), 1.0, IRON)
    P.append_box(dm, opts(IRON), xf((42, 0, 26)), 2.0, 10.0, 46.0, 0, 0, 0, unreal.GeometryScriptPrimitiveOriginMode.CENTER)


def torch(dm):
    """A wall torch: plate on the wall (+X), an arm and ring holding a wooden torch that leans out."""
    P.append_box(dm, opts(IRON), xf((-1, 0, 0)), 2.0, 9.0, 18.0, 0, 0, 0, unreal.GeometryScriptPrimitiveOriginMode.CENTER)
    rod(dm, (-1, 0, 0), (-15, 0, 0), 0.9, IRON)
    torus(dm, (-16, 0, 0), None, 3.4, 0.7, IRON, (12, 5))
    bottom, top = (-10.0, 0.0, -24.0), (-26.0, 0.0, 22.0)
    rod(dm, bottom, top, 2.0, WOOD, 8)
    d = unreal.Vector(top[0] - bottom[0], 0, top[2] - bottom[2]).normal()
    rot = unreal.MathLibrary.make_rot_from_z(d)
    P.append_cone(dm, opts(EMBERS), unreal.Transform(unreal.Vector(*top) - d * 4.0, rot, unreal.Vector(1, 1, 1)),
                  3.6, 2.6, 13.0, 10, 1, True)


def candle_holder(dm):
    P.append_cylinder(dm, opts(IRON), xf((0, 0, 0)), 5.0, 1.0, 16, 0, True)
    P.append_cylinder(dm, opts(IRON), xf((0, 0, 1)), 1.2, 9.0, 8, 0, True)
    P.append_cylinder(dm, opts(IRON), xf((0, 0, 10)), 3.0, 2.0, 12, 0, True)
    P.append_cylinder(dm, opts(WAX), xf((0, 0, 12)), 1.7, 14.0, 12, 0, True)
    P.append_cylinder(dm, opts(EMBERS), xf((0, 0, 26)), 0.25, 1.2, 4, 0, True)


def logs(dm):
    """A hearth fire's logs: a bed of coals and four logs leaning into a cone, base at the origin."""
    P.append_cone(dm, opts(EMBERS), xf((0, 0, -2)), 38.0, 20.0, 7.0, 20, 1, True)
    for k in range(4):
        a = math.radians(45 + k * 90)
        rod(dm, (34 * math.cos(a), 34 * math.sin(a), 2), (6 * math.cos(a), 6 * math.sin(a), 30), 6.5, EMBERS, 10)
    rod(dm, (-36, -8, 5), (36, 10, 6), 7.0, EMBERS, 10)


MESHES = {"SM_FireBowl": lambda dm: fire_bowl(dm, 45.0), "SM_Chain": chain, "SM_WallLamp": wall_lamp,
          "SM_Torch": torch, "SM_CandleHolder": candle_holder, "SM_HearthLogs": logs}
for name, build in MESHES.items():
    dm = unreal.DynamicMesh()
    build(dm)
    path = DIR + "/" + name
    o = unreal.GeometryScriptCreateNewStaticMeshAssetOptions()
    o.enable_recompute_normals = False
    o.enable_collision = False
    if EAL.does_asset_exist(path):
        sm = EAL.load_asset(path)
        w = unreal.GeometryScriptCopyMeshToAssetOptions()
        w.enable_recompute_normals = False
        w.replace_materials = False
        unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(dm, sm, w, unreal.GeometryScriptMeshWriteLOD())
    else:
        sm, outcome = unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(dm, path, o)
    sm.set_editor_property("static_materials", [unreal.StaticMaterial(material_interface=mats[i], material_slot_name="S%d" % i)
                                                for i in range(4)])
    EAL.save_loaded_asset(sm)
    b = sm.get_bounding_box()
    report[name] = [round(v, 1) for v in (b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z)]
OUT.update(report)
