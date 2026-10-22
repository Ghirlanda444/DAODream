# Runs inside the editor (pyrun; Play/Simulate stopped): the mabari, from tools/blender/mabari.py's FBX (MABARI_FBX).
#   /Game/Cousland/Mabari/M_Mabari                     committed: a short dark coat with brindle and red kaddis
#   /Game/ThirdParty/Mabari/SK_Mabari, MI_Mabari       git-ignored: made from the Animal Variety Pack's wolf
# M_Mabari takes the coat texture as a parameter (MI_Mabari gives it the wolf's dark coat, which keeps the
# teeth, tongue and eyes coloured), darkens it, adds brindle stripes from the pre-skinned position (so they
# stay on the body as it moves) and paints the kaddis where the mesh's vertex colour R is 1.
if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world():
    raise RuntimeError("stop Play/Simulate first")
AT = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
P = unreal.MaterialProperty
F1, F3 = unreal.CustomMaterialOutputType.CMOT_FLOAT1, unreal.CustomMaterialOutputType.CMOT_FLOAT3
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


def expr(m, cls, x, y):
    return MEL.create_material_expression(m, cls, x, y)


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


def texparam(m, name, default, sampler, x, y):
    e = expr(m, unreal.MaterialExpressionTextureSampleParameter2D, x, y)
    e.set_editor_property("parameter_name", name)
    e.set_editor_property("texture", EAL.load_asset(default))
    e.set_editor_property("sampler_type", sampler)
    return e


def vec(m, name, rgb, x, y):
    e = expr(m, unreal.MaterialExpressionVectorParameter, x, y)
    e.set_editor_property("parameter_name", name)
    e.set_editor_property("default_value", unreal.LinearColor(*rgb, 1.0))
    return e


path = "/Game/Cousland/Mabari/M_Mabari"
if EAL.does_asset_exist(path):
    m = EAL.load_asset(path)
    MEL.delete_all_material_expressions(m)
else:
    m = AT.create_asset("M_Mabari", "/Game/Cousland/Mabari", unreal.Material, unreal.MaterialFactoryNew())
m.set_editor_property("used_with_skeletal_mesh", True)
tex = texparam(m, "Coat", "/Engine/EngineMaterials/DefaultDiffuse", unreal.MaterialSamplerType.SAMPLERTYPE_COLOR, -1400, 0)
nrm = texparam(m, "CoatNormal", "/Engine/EngineMaterials/DefaultNormal", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL, -1400, 300)
pos0 = expr(m, unreal.MaterialExpressionPreSkinnedPosition, -1700, 600)
pos = expr(m, unreal.MaterialExpressionVertexInterpolator, -1400, 600)  # pre-skinned position is vertex-only
MEL.connect_material_expressions(pos0, "", pos, "")
vc = expr(m, unreal.MaterialExpressionVertexColor, -1400, 750)
brindle = vec(m, "Brindle", (0.075, 0.055, 0.038), -1400, 900)
paint = vec(m, "Kaddis", (0.30, 0.018, 0.012), -1400, 1050)
base = custom(m, "float3 p = P * float3(0.03, 0.22, 0.02); float n;" + NOISE + """
float b = smoothstep(0.62, 0.78, n) * 0.6;        // brindle: faint, irregular stripes across the flanks
float l = dot(T, float3(0.3, 0.59, 0.11));
float3 coat = T * 0.55;                               // the wolf's dark coat, darker still
coat = lerp(coat, B * (0.6 + l), b * saturate(1.0 - abs(l - 0.08) * 6.0));  // stripes only on the coat, not teeth/eyes
p = P * 0.25 + 7.0;""" + NOISE + """
float k = step(0.5, VC) * smoothstep(0.25, 0.45, n);  // kaddis, brushed: ragged where the paint thins
return lerp(coat, K, k);""", [("T", (tex, "RGB")), ("P", pos), ("VC", (vc, "R")), ("B", (brindle, "RGB")), ("K", (paint, "RGB"))], F3, -900, 0)
rough = custom(m, "return lerp(0.55, 0.8, step(0.5, VC));", [("VC", (vc, "R"))], F1, -900, 300)
MEL.connect_material_property(base, "", P.MP_BASE_COLOR)
MEL.connect_material_property(nrm, "RGB", P.MP_NORMAL)
MEL.connect_material_property(rough, "", P.MP_ROUGHNESS)
MEL.recompile_material(m)
EAL.save_loaded_asset(m)

mi_path = "/Game/ThirdParty/Mabari/MI_Mabari"
mi = EAL.load_asset(mi_path) if EAL.does_asset_exist(mi_path) else AT.create_asset(
    "MI_Mabari", "/Game/ThirdParty/Mabari", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
mi.set_editor_property("parent", m)
MEL.set_material_instance_texture_parameter_value(mi, "Coat", EAL.load_asset("/Game/AnimalVarietyPack/Wolf/Textures/T_WolfDark_BaseColorAlpha"))
MEL.set_material_instance_texture_parameter_value(mi, "CoatNormal", EAL.load_asset("/Game/AnimalVarietyPack/Wolf/Textures/T_Wolf_Nml"))
EAL.save_loaded_asset(mi)

# The mesh, on the wolf's skeleton (its animations play on it), vertex colours kept.
unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX False")
ui = unreal.FbxImportUI()
ui.import_mesh = True
ui.import_as_skeletal = True
ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH
ui.skeleton = EAL.load_asset("/Game/AnimalVarietyPack/Wolf/Meshes/SK_Wolf_Skeleton")
ui.physics_asset = EAL.load_asset("/Game/AnimalVarietyPack/Wolf/Meshes/SK_Wolf_PhysicsAsset")
ui.create_physics_asset = False
ui.import_materials = False
ui.import_textures = False
ui.import_animations = False
d = ui.skeletal_mesh_import_data
d.vertex_color_import_option = unreal.VertexColorImportOption.REPLACE
d.normal_import_method = unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS
t = unreal.AssetImportTask()
t.filename = MABARI_FBX
t.destination_path = "/Game/ThirdParty/Mabari"
t.destination_name = "SK_Mabari"
t.automated = True
t.replace_existing = True
t.save = True
t.options = ui
AT.import_asset_tasks([t])
sk = EAL.load_asset("/Game/ThirdParty/Mabari/SK_Mabari")
mats = list(sk.materials)
for i, s in enumerate(mats):
    s.material_interface = mi
    mats[i] = s
sk.set_editor_property("materials", mats)
EAL.save_loaded_asset(sk)
b = sk.get_bounds()
OUT["mesh"] = [str(sk.get_path_name()), round(b.box_extent.x, 1), round(b.box_extent.y, 1), round(b.box_extent.z, 1)]
OUT["slots"] = [str(s.material_slot_name) for s in sk.materials]
