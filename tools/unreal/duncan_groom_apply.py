# Run inside the editor (py "<this file>") after every Duncan assembly: the build regenerates
# BP_MHC_Duncan with MetaHuman's own hair; this puts the custom groom back on it.
import unreal
OUT = {}
eal = unreal.EditorAssetLibrary
groom = unreal.load_asset("/Game/MetaHumans/Duncan/Hair/Groom_DuncanHair7")
face = unreal.load_asset("/Game/MetaHumans/MHC_Duncan/Face/SKM_MHC_Duncan_FaceMesh")
mi = unreal.load_asset("/Game/MetaHumans/Duncan/Hair/MI_DuncanHair")
BIND = "/Game/MetaHumans/Duncan/Hair/Groom_DuncanHair7_Binding"
if eal.does_asset_exist(BIND):
    eal.delete_asset(BIND)
b = unreal.GroomLibrary.create_new_groom_binding_asset_with_path(BIND, groom, face, 100, None, 0)
OUT["binding"] = str(b)
eal.save_asset(BIND, only_if_is_dirty=False)
BP = "/Game/MetaHumans/MHC_Duncan/BP_MHC_Duncan"
bp = unreal.load_asset(BP)
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib = unreal.SubobjectDataBlueprintFunctionLibrary
done = []
for h in sds.k2_gather_subobject_data_for_blueprint(bp):
    d = lib.get_data(h)
    o = lib.get_object(d)
    if isinstance(o, unreal.GroomComponent) and str(lib.get_variable_name(d)) == "Hair":
        o.set_editor_property("groom_asset", groom)
        o.set_editor_property("binding_asset", b)
        o.set_editor_property("override_materials", [mi])
        done.append(o.get_path_name())
OUT["set"] = done
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
OUT["saved"] = eal.save_asset(BP, only_if_is_dirty=False)
print(OUT)
