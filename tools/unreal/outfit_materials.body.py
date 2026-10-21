# Runs inside the editor (pyrun; Play/Simulate stopped): the outfit materials in /Game/Cousland/Outfits, all
# procedural from the outfit's UVs (the body's, ~0.7 UV units per metre) and its vertex colour R (1 along
# hems and cuffs: the trim band). Re-running updates them in place.
DIR = "/Game/Cousland/Outfits"
AT = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world():
    raise RuntimeError("stop Play/Simulate first")
report = {}

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
    m.set_editor_property("used_with_skeletal_mesh", True)
    setup(m)
    MEL.recompile_material(m)
    EAL.save_loaded_asset(m)
    report[name] = "ok"
    return m


def expr(m, cls, x, y):
    return MEL.create_material_expression(m, cls, x, y)


def scalar(m, name, v, x, y):
    e = expr(m, unreal.MaterialExpressionScalarParameter, x, y)
    e.set_editor_property("parameter_name", name)
    e.set_editor_property("default_value", v)
    return e


def colour(m, name, rgb, x, y):
    e = expr(m, unreal.MaterialExpressionVectorParameter, x, y)
    e.set_editor_property("parameter_name", name)
    e.set_editor_property("default_value", unreal.LinearColor(*rgb, 1.0))
    return e


def custom(m, code, inputs, out_type, x, y):
    e = expr(m, unreal.MaterialExpressionCustom, x, y)
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


F1, F3 = unreal.CustomMaterialOutputType.CMOT_FLOAT1, unreal.CustomMaterialOutputType.CMOT_FLOAT3
P = unreal.MaterialProperty


def cloth(m):
    """Woven wool or silk: a twill rib, a mottle of two tones, and a trim band along hems and cuffs."""
    uv = expr(m, unreal.MaterialExpressionTextureCoordinate, -1200, 0)
    vc = expr(m, unreal.MaterialExpressionVertexColor, -1200, 150)
    s = scalar(m, "Weave", 140.0, -1200, 300)  # repeats per UV unit (~1 cm)
    a, b = colour(m, "ColorA", (0.03, 0.05, 0.18), -1200, 450), colour(m, "ColorB", (0.05, 0.08, 0.24), -1200, 600)
    t = colour(m, "Trim", (0.75, 0.55, 0.2), -1200, 750)
    base = custom(m, "float2 q = UV * S; float3 p = float3(q * 0.04, 0.0); float n;" + NOISE + """
float rib = sin((q.x + q.y) * 6.2831853);
float3 c = lerp(A, B, saturate(n * 1.4 - 0.2)) * (0.9 + 0.1 * rib);
return lerp(c, T, step(0.5, VC));""", [("UV", uv), ("VC", (vc, "R")), ("S", s), ("A", a), ("B", b), ("T", t)], F3, -700, 0)
    nrm = custom(m, """float2 q = UV * S; float g = cos((q.x + q.y) * 6.2831853) * 0.18 * (1.0 - step(0.5, VC));
return normalize(float3(g, g, 1.0));""", [("UV", uv), ("VC", (vc, "R")), ("S", s)], F3, -700, 250)
    trim_metal = scalar(m, "TrimMetallic", 0.0, -1200, 900)
    met = custom(m, "return step(0.5, VC) * M;", [("VC", (vc, "R")), ("M", trim_metal)], F1, -700, 400)
    rough = custom(m, "return lerp(0.85, 0.45, step(0.5, VC));", [("VC", (vc, "R"))], F1, -700, 500)
    MEL.connect_material_property(base, "", P.MP_BASE_COLOR)
    MEL.connect_material_property(nrm, "", P.MP_NORMAL)
    MEL.connect_material_property(met, "", P.MP_METALLIC)
    MEL.connect_material_property(rough, "", P.MP_ROUGHNESS)


def leather(m):
    """Leather: two tones mottled by grain, worn lighter in patches, satin."""
    uv = expr(m, unreal.MaterialExpressionTextureCoordinate, -1200, 0)
    a, b = colour(m, "ColorA", (0.07, 0.04, 0.022), -1200, 200), colour(m, "ColorB", (0.14, 0.085, 0.045), -1200, 350)
    base = custom(m, "float3 p = float3(UV * 18.0, 0.0); float n;" + NOISE + """
float g = n; p = float3(UV * 160.0, 1.0);""" + NOISE + """
return lerp(A, B, saturate(g * 1.5 - 0.3)) * (0.85 + 0.15 * n);""", [("UV", uv), ("A", a), ("B", b)], F3, -700, 0)
    rough = custom(m, "float3 p = float3(UV * 160.0, 2.0); float n;" + NOISE + "return 0.55 + 0.2 * n;", [("UV", uv)], F1, -700, 250)
    MEL.connect_material_property(base, "", P.MP_BASE_COLOR)
    MEL.connect_material_property(rough, "", P.MP_ROUGHNESS)


def metal(m):
    """Mail of riveted rings in staggered rows (Rings 1), or plain worked metal (Rings 0: buckles, girdles)."""
    uv = expr(m, unreal.MaterialExpressionTextureCoordinate, -1200, 0)
    s = scalar(m, "RingScale", 110.0, -1200, 150)
    rings = scalar(m, "Rings", 1.0, -1200, 300)
    c = colour(m, "Color", (0.56, 0.56, 0.58), -1200, 450)
    ring = """float2 q = UV * S; q.x += 0.5 * fmod(floor(q.y), 2.0);
float2 f = frac(q) - 0.5; float d = abs(length(f) - 0.33); float ring = saturate(1.0 - d / 0.11);
ring = lerp(1.0, ring, R);"""
    base = custom(m, ring + "return C * lerp(0.05, 1.0, ring);", [("UV", uv), ("S", s), ("R", rings), ("C", c)], F3, -700, 0)
    nrm = custom(m, ring + "float2 g = f * sign(length(f) - 0.33) * 2.2 * ring * R; return normalize(float3(g, 1.0));",
                 [("UV", uv), ("S", s), ("R", rings)], F3, -700, 200)
    met = custom(m, ring + "return ring;", [("UV", uv), ("S", s), ("R", rings)], F1, -700, 400)
    rough = custom(m, ring + "return lerp(0.9, 0.32, ring);", [("UV", uv), ("S", s), ("R", rings)], F1, -700, 500)
    MEL.connect_material_property(base, "", P.MP_BASE_COLOR)
    MEL.connect_material_property(nrm, "", P.MP_NORMAL)
    MEL.connect_material_property(met, "", P.MP_METALLIC)
    MEL.connect_material_property(rough, "", P.MP_ROUGHNESS)


M = {"M_OutfitCloth": material("M_OutfitCloth", cloth), "M_OutfitLeather": material("M_OutfitLeather", leather),
     "M_OutfitMetal": material("M_OutfitMetal", metal)}

# Colour sets. Cousland's colours are a deep blue with silver; Bryce's coat the same blue with gold trim.
INSTANCES = {
    "MI_Cloth_CouslandBlue": ("M_OutfitCloth", {"ColorA": (0.025, 0.045, 0.16), "ColorB": (0.04, 0.065, 0.21), "Trim": (0.72, 0.72, 0.66)}, {}),
    "MI_Cloth_BryceBlue": ("M_OutfitCloth", {"ColorA": (0.03, 0.05, 0.19), "ColorB": (0.05, 0.08, 0.26), "Trim": (0.8, 0.56, 0.2)}, {"TrimMetallic": 0.7}),
    "MI_Cloth_BrownWool": ("M_OutfitCloth", {"ColorA": (0.08, 0.055, 0.035), "ColorB": (0.115, 0.08, 0.05), "Trim": (0.1, 0.07, 0.045)}, {}),
    "MI_Cloth_GreyWool": ("M_OutfitCloth", {"ColorA": (0.09, 0.09, 0.085), "ColorB": (0.13, 0.125, 0.115), "Trim": (0.12, 0.115, 0.105)}, {}),
    "MI_Cloth_EleanorWine": ("M_OutfitCloth", {"ColorA": (0.2, 0.025, 0.04), "ColorB": (0.28, 0.045, 0.06), "Trim": (0.8, 0.58, 0.22)}, {"TrimMetallic": 0.7}),
    "MI_Leather_Brown": ("M_OutfitLeather", {}, {}),
    "MI_Leather_Dark": ("M_OutfitLeather", {"ColorA": (0.03, 0.02, 0.015), "ColorB": (0.07, 0.045, 0.03)}, {}),
    "MI_Metal_Chain": ("M_OutfitMetal", {}, {}),
    "MI_Metal_Gold": ("M_OutfitMetal", {"Color": (0.83, 0.62, 0.3)}, {"Rings": 0.0}),
}
for name, (parent, vectors, scalars) in INSTANCES.items():
    path = DIR + "/" + name
    mi = EAL.load_asset(path) if EAL.does_asset_exist(path) else AT.create_asset(
        name, DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mi.set_editor_property("parent", M[parent])
    for k, v in vectors.items():
        unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(mi, k, unreal.LinearColor(*v, 1.0))
    for k, v in scalars.items():
        unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(mi, k, v)
    EAL.save_loaded_asset(mi)
    report[name] = "ok"
OUT.update(report)
