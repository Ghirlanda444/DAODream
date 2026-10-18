# Run inside the editor (py "<this file>") after every Duncan assembly: the build regenerates
# BP_MHC_Duncan with MetaHuman's own hair; this puts the custom groom back on it.
import unreal
OUT = {}
NAME = "DuncanV2"                    # the MetaHuman built for hm_gen_duncan
GROOM = "/Game/MetaHumans/Duncan/Hair/Groom_DuncanHair8"
eal = unreal.EditorAssetLibrary
groom = unreal.load_asset(GROOM)
face = unreal.load_asset("/Game/MetaHumans/MHC_%s/Face/SKM_MHC_%s_FaceMesh" % (NAME, NAME))
mi = unreal.load_asset("/Game/MetaHumans/Duncan/Hair/MI_DuncanHair")
BIND = GROOM + "_Binding_" + NAME
if eal.does_asset_exist(BIND):
    eal.delete_asset(BIND)
b = unreal.GroomLibrary.create_new_groom_binding_asset_with_path(BIND, groom, face, 100, None, 0)
OUT["binding"] = str(b)
eal.save_asset(BIND, only_if_is_dirty=False)
BP = "/Game/MetaHumans/MHC_%s/BP_MHC_%s" % (NAME, NAME)
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
# The binding set together with the groom does not always survive the compile: set it again and check.
for h in sds.k2_gather_subobject_data_for_blueprint(bp):
    d = lib.get_data(h); o = lib.get_object(d)
    if isinstance(o, unreal.GroomComponent) and str(lib.get_variable_name(d)) == "Hair":
        o.modify()
        o.set_editor_property("binding_asset", b)
        OUT.setdefault("bound", []).append(str(o.binding_asset.get_name()) if o.binding_asset else None)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
OUT["saved"] = eal.save_asset(BP, only_if_is_dirty=False)
print(OUT)
