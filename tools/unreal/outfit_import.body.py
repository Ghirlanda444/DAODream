# Runs inside the editor (pyrun) with FBX = path, DEST = package folder, NAME = asset name: imports an outfit
# made by tools/blender/outfit.py onto the MetaHuman skeleton (legacy FBX importer: it takes an existing
# skeleton), keeping its vertex colours (the trim mask).
unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX False")
skel = unreal.EditorAssetLibrary.load_asset("/Game/MetaHumans/Common/Female/Medium/NormalWeight/Body/metahuman_base_skel")
ui = unreal.FbxImportUI()
ui.import_mesh = True
ui.import_as_skeletal = True
ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH
ui.skeleton = skel
ui.import_materials = False
ui.import_textures = False
ui.import_animations = False
ui.create_physics_asset = False
d = ui.skeletal_mesh_import_data
d.vertex_color_import_option = unreal.VertexColorImportOption.REPLACE
d.normal_import_method = unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS
d.reorder_material_to_fbx_order = True
t = unreal.AssetImportTask()
t.filename = FBX
t.destination_path = DEST
t.destination_name = NAME
t.automated = True
t.replace_existing = True
t.save = True
t.options = ui
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
OUT["imported"] = list(t.imported_object_paths)
