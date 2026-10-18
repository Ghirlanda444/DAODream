# Inside the editor (via pyrun): thicken the grooms of a built MetaHuman so beards and brows read denser.
# NAME and FACTORS are filled in by metahuman_make.py: {"Beard": 1.6, ...} multiplies the strand width.
eal = unreal.EditorAssetLibrary
BP = "/Game/MetaHumans/MHC_%s/BP_MHC_%s" % (NAME, NAME)
DST = "/Game/MetaHumans/%s/Grooms" % NAME
face = unreal.load_asset("/Game/MetaHumans/MHC_%s/Face/SKM_MHC_%s_FaceMesh" % (NAME, NAME))
bp = unreal.load_asset(BP)
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem); lib = unreal.SubobjectDataBlueprintFunctionLibrary
def comps():
    for h in sds.k2_gather_subobject_data_for_blueprint(bp):
        d = lib.get_data(h); o = lib.get_object(d)
        if isinstance(o, unreal.GroomComponent):
            yield str(lib.get_variable_name(d)), o
made = {}
for slot, o in list(comps()):
    if slot not in FACTORS or not o.groom_asset or slot in made:
        continue
    src = o.groom_asset
    path = "%s/%s_Thick" % (DST, src.get_name())
    if eal.does_asset_exist(path):
        eal.delete_asset(path)
    g = eal.duplicate_asset(src.get_path_name().split(".")[0], path)
    rg = list(g.get_editor_property("hair_groups_rendering"))
    for i, r in enumerate(rg):
        gs = r.get_editor_property("geometry_settings")
        gs.set_editor_property("hair_width_override", True)
        gs.set_editor_property("hair_width", gs.hair_width * FACTORS[slot])
        r.set_editor_property("geometry_settings", gs); rg[i] = r
    g.modify(); g.set_editor_property("hair_groups_rendering", rg)
    eal.save_asset(path, only_if_is_dirty=False)
    bind = path + "_Binding"
    if eal.does_asset_exist(bind):
        eal.delete_asset(bind)
    b = unreal.GroomLibrary.create_new_groom_binding_asset_with_path(bind, g, face, 100, None, 0)
    eal.save_asset(bind, only_if_is_dirty=False)
    made[slot] = (g, b)
for rnd in range(2):  # bindings set with the groom do not always survive a compile: set, compile, set again
    for slot, o in comps():
        if slot in made:
            o.modify()
            o.set_editor_property("groom_asset", made[slot][0])
            o.set_editor_property("binding_asset", made[slot][1])
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
OUT["thickened"] = {s: [str(o.groom_asset.get_name()), str(o.binding_asset.get_name()) if o.binding_asset else None] for s, o in comps() if s in made}
OUT["saved"] = eal.save_asset(BP, only_if_is_dirty=False)
