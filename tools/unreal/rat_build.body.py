# Runs inside the editor (pyrun; Play/Simulate stopped): the giant rat, from tools/blender/rat.py's FBX (RAT_FBX).
#   /Game/ThirdParty/GiantRat/SK_GiantRat, MI_GiantRat   git-ignored: made from the Animal Variety Pack's fox
# The rat shares the mabari's material (/Game/Cousland/Mabari/M_Mabari, tools/unreal/mabari_build.body.py):
# MI_GiantRat gives it the fox's coat texture, tinted a dirty brown-grey (CoatColor, a parameter the component's
# custom primitive data can override per rat), with faint mottling for the brindle, and the "kaddis" colour,
# painted where the mesh's vertex colour R is 1, set to the bare pink skin of the tail, ears, paws and nose.
# Then python beast_anim.py GiantRat builds its animation and look actor.
if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world():
    raise RuntimeError("stop Play/Simulate first")
AT = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
D = "/Game/ThirdParty/GiantRat"
FOX = "/Game/AnimalVarietyPack/Fox"

mi_path = D + "/MI_GiantRat"
mi = EAL.load_asset(mi_path) if EAL.does_asset_exist(mi_path) else AT.create_asset(
    "MI_GiantRat", D, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
mi.set_editor_property("parent", EAL.load_asset("/Game/Cousland/Mabari/M_Mabari"))
MEL.set_material_instance_texture_parameter_value(mi, "Coat", EAL.load_asset(FOX + "/Textures/T_Fox_BaseColor"))
MEL.set_material_instance_texture_parameter_value(mi, "CoatNormal", EAL.load_asset(FOX + "/Textures/T_Fox_Nml"))
MEL.set_material_instance_vector_parameter_value(mi, "CoatColor", unreal.LinearColor(0.085, 0.07, 0.055, 0.35))
MEL.set_material_instance_vector_parameter_value(mi, "Brindle", unreal.LinearColor(0.04, 0.035, 0.03, 1.0))
MEL.set_material_instance_vector_parameter_value(mi, "Kaddis", unreal.LinearColor(0.42, 0.20, 0.18, 1.0))
EAL.save_loaded_asset(mi)

# The mesh, on the fox's skeleton (its animations play on it), vertex colours kept.
unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX False")
ui = unreal.FbxImportUI()
ui.import_mesh = True
ui.import_as_skeletal = True
ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH
ui.skeleton = EAL.load_asset(FOX + "/Meshes/SK_Fox_Skeleton")
ui.physics_asset = EAL.load_asset(FOX + "/Meshes/SK_Fox_PhysicsAsset")
ui.create_physics_asset = False
ui.import_materials = False
ui.import_textures = False
ui.import_animations = False
d = ui.skeletal_mesh_import_data
d.vertex_color_import_option = unreal.VertexColorImportOption.REPLACE
d.normal_import_method = unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS
t = unreal.AssetImportTask()
t.filename = RAT_FBX
t.destination_path = D
t.destination_name = "SK_GiantRat"
t.automated = True
t.replace_existing = True
t.save = True
t.options = ui
AT.import_asset_tasks([t])
sk = EAL.load_asset(D + "/SK_GiantRat")
mats = list(sk.materials)
for i, s in enumerate(mats):
    s.material_interface = mi
    mats[i] = s
sk.set_editor_property("materials", mats)
EAL.save_loaded_asset(sk)
b = sk.get_bounds()
OUT["mesh"] = [str(sk.get_path_name()), round(b.box_extent.x, 1), round(b.box_extent.y, 1), round(b.box_extent.z, 1)]
