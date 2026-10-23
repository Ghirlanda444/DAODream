# Runs inside the editor (pyrun; Play/Simulate stopped): the castle's Megascans surfaces (docs/ART.md).
#   /Game/Cousland/Materials/M_CastleScan   committed, engine functions only: a texture set projected on
#       the three world planes (no UVs needed on the scaled cubes the castle is made of), and its
#       displacement map as Nanite displacement, so walls, floors and ceilings get real relief
#       (Nanite tessellation, on by default in UE 5.8). Parameters: TexBaseColor/Normal/Roughness/
#       AO/Displacement, TileSize (cm per repeat), Tint, RoughnessScale, DisplacementAmount (0 flat .. 1),
#       EdgeFade (cm over which the relief fades out toward a box edge).
#   /Game/Cousland/Areas/SM_NaniteCube      committed: the engine cube with Nanite on, for BP_AreaLoader's
#       boxes (displacement only moves Nanite meshes).
#   /Game/ThirdParty/Megascans/Castle/<Kind>/  git-ignored: the free surfaces' textures and MI_Castle_<Kind>,
#       from the 2K zips unpacked in extracted/fab/ (SURFACES).
# Rebuilds the material in place (its instances keep it) and is safe to run again.
if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world():
    raise RuntimeError("stop Play/Simulate first")
import os
AT = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
FAB = os.path.join(os.path.dirname(unreal.Paths.project_dir().rstrip("/")), "..", "extracted", "fab")
D = "/Game/ThirdParty/Megascans/Castle"
# kind -> (unpacked surface folder, tile size cm, roughness scale, displacement amount)
SURFACES = {
    "Wall": ("stone_wall_tinifauaw_2k", 200.0, 1.0, 1.0),
    "Floor": ("stone_floor_xbmgeba_2k", 200.0, 1.0, 0.4),  # feet stand on the box top: shallow
    "Ceiling": ("wooden_planks_wckqdbvs_2k", 200.0, 1.0, 0.4),
    "Door": ("wooden_planks_vjisagn_2k", 120.0, 1.0, 0.0),  # doors move: kept flat
    "Prop": ("wooden_planks_vlzhdbwdy_2k", 150.0, 1.0, 0.0),  # props left as boxes stay flat
    "Plaster": ("damaged_wall_plaster_uc2lddzcw_2k", 200.0, 1.0, 0.5),
}
report = {}

# --- the material --------------------------------------------------------------------------------
P = "/Game/Cousland/Materials/M_CastleScan"
if EAL.does_asset_exist(P):
    m = EAL.load_asset(P)
    MEL.delete_all_material_expressions(m)
else:
    m = AT.create_asset("M_CastleScan", "/Game/Cousland/Materials", unreal.Material, unreal.MaterialFactoryNew())
m.set_editor_property("used_with_instanced_static_meshes", True)
m.set_editor_property("used_with_nanite", True)
m.set_editor_property("use_material_attributes", True)
try:
    m.set_editor_property("enable_tessellation", True)
except Exception as e:  # not exposed in every version: displacement still needs it in the material
    report["enable_tessellation"] = str(e)[:120]
ds = m.get_editor_property("displacement_scaling")
ds.magnitude = 6.0  # cm at DisplacementAmount 1
ds.center = 1.0  # relief only inward: a cube's faces move apart along their own normals, and outward they'd crack at the edges
m.set_editor_property("displacement_scaling", ds)
WAT = unreal.load_asset("/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedTexture")
WAN = unreal.load_asset("/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedNormal")


def E(cls, x, y):
    return MEL.create_material_expression(m, cls, x, y)


def scalar(name, value, x, y):
    e = E(unreal.MaterialExpressionScalarParameter, x, y)
    e.set_editor_property("parameter_name", name)
    e.set_editor_property("default_value", value)
    return e


def mask_r(src, x, y):
    e = E(unreal.MaterialExpressionComponentMask, x, y)
    for c in "gba":
        e.set_editor_property(c, False)
    e.set_editor_property("r", True)
    MEL.connect_material_expressions(src, "XYZ Texture", e, "")
    return e


tile = scalar("TileSize", 200.0, -1500, 0)
LINEAR = "/Engine/EngineMaterials/T_Default_Material_Grid_M"  # linear placeholder for the linear maps
maps = {}
for name, default, sampler, y in (
        ("BaseColor", "/Engine/EngineResources/DefaultTexture", unreal.MaterialSamplerType.SAMPLERTYPE_COLOR, -400),
        ("Normal", "/Engine/EngineMaterials/FlatNormal", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL, 0),
        ("Roughness", LINEAR, unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR, 400),
        ("AO", LINEAR, unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR, 800),
        ("Displacement", LINEAR, unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR, 1200)):
    tp = E(unreal.MaterialExpressionTextureObjectParameter, -1200, y)
    tp.set_editor_property("parameter_name", "Tex" + name)
    tp.set_editor_property("texture", unreal.load_asset(default))
    tp.set_editor_property("sampler_type", sampler)
    fc = E(unreal.MaterialExpressionMaterialFunctionCall, -800, y)
    fc.set_material_function(WAN if name == "Normal" else WAT)
    MEL.connect_material_expressions(tp, "", fc, "TextureObject")
    MEL.connect_material_expressions(tile, "", fc, "TextureSize")
    maps[name] = fc
attrs = E(unreal.MaterialExpressionMakeMaterialAttributes, 0, 200)
tint = E(unreal.MaterialExpressionVectorParameter, -500, -600)
tint.set_editor_property("parameter_name", "Tint")
tint.set_editor_property("default_value", unreal.LinearColor(1, 1, 1, 1))
base = E(unreal.MaterialExpressionMultiply, -300, -400)
MEL.connect_material_expressions(maps["BaseColor"], "XYZ Texture", base, "A")
MEL.connect_material_expressions(tint, "", base, "B")
MEL.connect_material_expressions(base, "", attrs, "BaseColor")
MEL.connect_material_expressions(maps["Normal"], "XYZ Texture", attrs, "Normal")
rough = E(unreal.MaterialExpressionMultiply, -300, 400)
MEL.connect_material_expressions(mask_r(maps["Roughness"], -500, 400), "", rough, "A")
MEL.connect_material_expressions(scalar("RoughnessScale", 1.0, -500, 520), "", rough, "B")
MEL.connect_material_expressions(rough, "", attrs, "Roughness")
MEL.connect_material_expressions(mask_r(maps["AO"], -500, 800), "", attrs, "AmbientOcclusion")


def custom(code, names, x, y):
    e = E(unreal.MaterialExpressionCustom, x, y)
    e.set_editor_property("code", code)
    e.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    ins = []
    for n in names:
        ci = unreal.CustomInput()
        ci.set_editor_property("input_name", n)
        ins.append(ci)
    e.set_editor_property("inputs", ins)
    return e


def to_world(axis, x, y):
    """The instance's axis in world space: its length is the instance's scale on that axis."""
    c = E(unreal.MaterialExpressionConstant3Vector, x - 200, y)
    c.set_editor_property("constant", unreal.LinearColor(*axis, 0))
    t = E(unreal.MaterialExpressionTransform, x, y)
    t.set_editor_property("transform_source_type", unreal.MaterialVectorCoordTransformSource.TRANSFORMSOURCE_INSTANCE)
    t.set_editor_property("transform_type", unreal.MaterialVectorCoordTransform.TRANSFORM_WORLD)
    MEL.connect_material_expressions(c, "", t, "")
    return t


# Edge fade: 0 at the box's edges, 1 from EdgeFade cm in. Each face is displaced along its own normal, so
# without it neighbouring faces part at the box's edges and corners and show dark slits.
wp = E(unreal.MaterialExpressionWorldPosition, -1400, 1500)
ip = E(unreal.MaterialExpressionTransformPosition, -1200, 1500)
ip.set_editor_property("transform_source_type", unreal.MaterialPositionTransformSource.TRANSFORMPOSSOURCE_WORLD)
ip.set_editor_property("transform_type", unreal.MaterialPositionTransformSource.TRANSFORMPOSSOURCE_INSTANCE)
MEL.connect_material_expressions(wp, "", ip, "")
nw = E(unreal.MaterialExpressionVertexNormalWS, -1400, 1800)
ni = E(unreal.MaterialExpressionTransform, -1200, 1800)
ni.set_editor_property("transform_source_type", unreal.MaterialVectorCoordTransformSource.TRANSFORMSOURCE_WORLD)
ni.set_editor_property("transform_type", unreal.MaterialVectorCoordTransform.TRANSFORM_INSTANCE)
MEL.connect_material_expressions(nw, "", ni, "")
edge = custom("""float3 s = float3(length(SX), length(SY), length(SZ));
float3 d = (50 - abs(P)) * s;  // cm to the cube's faces (the engine cube spans -50..50)
float3 n = abs(N);
if (n.x >= n.y && n.x >= n.z) d.x = 1e5; else if (n.y >= n.z) d.y = 1e5; else d.z = 1e5;  // not the face's own axis
return saturate(min(d.x, min(d.y, d.z)) / max(F, 0.01));""", ("P", "N", "SX", "SY", "SZ", "F"), -800, 1600)
MEL.connect_material_expressions(ip, "", edge, "P")
MEL.connect_material_expressions(ni, "", edge, "N")
for i, (pin, axis) in enumerate((("SX", (1, 0, 0)), ("SY", (0, 1, 0)), ("SZ", (0, 0, 1)))):
    MEL.connect_material_expressions(to_world(axis, -1200, 2000 + 150 * i), "", edge, pin)
MEL.connect_material_expressions(scalar("EdgeFade", 10.0, -1000, 2450), "", edge, "F")
# 1 + (height - 1) * DisplacementAmount * edge fade: 1 is the box's own surface (DisplacementAmount 0: flat)
disp = custom("return 1 + (H - 1) * A * F;", ("H", "A", "F"), -300, 1200)
MEL.connect_material_expressions(mask_r(maps["Displacement"], -500, 1200), "", disp, "H")
MEL.connect_material_expressions(scalar("DisplacementAmount", 0.0, -500, 1320), "", disp, "A")
MEL.connect_material_expressions(edge, "", disp, "F")
report["displacement_pin"] = MEL.connect_material_expressions(disp, "", attrs, "Displacement")
MEL.connect_material_property(attrs, "", unreal.MaterialProperty.MP_MATERIAL_ATTRIBUTES)
MEL.recompile_material(m)
EAL.save_asset(P, only_if_is_dirty=False)

# --- the Nanite cube ------------------------------------------------------------------------------
CUBE = "/Game/Cousland/Areas/SM_NaniteCube"
if not EAL.does_asset_exist(CUBE):
    EAL.duplicate_asset("/Engine/BasicShapes/Cube", CUBE)
cube = EAL.load_asset(CUBE)
ns = cube.get_editor_property("nanite_settings")
ns.enabled = True
cube.set_editor_property("nanite_settings", ns)
EAL.save_asset(CUBE, only_if_is_dirty=False)

# --- the surfaces ---------------------------------------------------------------------------------
for kind, (folder, tile_cm, rough, amount) in SURFACES.items():
    dest = "%s/%s" % (D, kind)
    src = os.path.normpath(os.path.join(FAB, folder))
    if not os.path.isdir(src):
        report[kind] = "missing " + src
        continue
    textures = {}
    for key in ("BaseColor", "Normal", "Roughness", "AO", "Displacement"):
        asset = "%s/T_%s_%s" % (dest, kind, key)
        if not EAL.does_asset_exist(asset):
            f = next((os.path.join(src, n) for n in os.listdir(src) if n.lower().endswith("_%s.jpg" % key.lower())), None)
            if not f:
                continue
            t = unreal.AssetImportTask()
            t.filename = f; t.destination_path = dest; t.destination_name = "T_%s_%s" % (kind, key)
            t.automated = True; t.replace_existing = True; t.save = False
            AT.import_asset_tasks([t])
        tex = EAL.load_asset(asset)
        if key == "Normal":
            tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
            tex.set_editor_property("srgb", False)
        elif key != "BaseColor":  # linear, default compression: what the linear samplers take
            tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_DEFAULT)
            tex.set_editor_property("srgb", False)
        EAL.save_asset(asset, only_if_is_dirty=False)
        textures[key] = tex
    mi_path = "%s/MI_Castle_%s" % (D, kind)
    mi = EAL.load_asset(mi_path) if EAL.does_asset_exist(mi_path) else AT.create_asset(
        "MI_Castle_" + kind, D, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, m)
    for key, tex in textures.items():
        MEL.set_material_instance_texture_parameter_value(mi, "Tex" + key, tex)
    MEL.set_material_instance_scalar_parameter_value(mi, "TileSize", tile_cm)
    MEL.set_material_instance_scalar_parameter_value(mi, "RoughnessScale", rough)
    MEL.set_material_instance_scalar_parameter_value(mi, "DisplacementAmount", amount)
    EAL.save_asset(mi_path, only_if_is_dirty=False)
    report[kind] = sorted(textures)
OUT.update(report)
