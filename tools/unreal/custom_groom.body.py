# Inside the editor (via pyrun): put a custom groom (Alembic made in Blender, e.g. tools/blender/iona_hair.py)
# on a built MetaHuman in place of its MetaHuman groom.
# NAME: MetaHuman name. ABC: Alembic file. SLOT: groom component (default "Hair"). WIDTH: strand width in cm.
# The groom's material is a copy of the slot's current one, so the recipe's hair colours carry over.
# The batch maker runs this after the strands step for recipes with "custom_hair" (a rebuild resets the slot).
SLOT = globals().get("SLOT", "Hair")
WIDTH = globals().get("WIDTH", 0.012)
eal = unreal.EditorAssetLibrary
D = "/Game/MetaHumans/%s/Custom" % NAME
gname = "Groom_%s_%s" % (NAME, SLOT)
t = unreal.AssetImportTask()
t.filename = ABC; t.destination_path = D; t.destination_name = gname
t.automated = True; t.replace_existing = True; t.save = True
opt = unreal.GroomImportOptions()
cs = opt.get_editor_property("conversion_settings")
cs.set_editor_property("rotation", unreal.Vector(90, 0, 0))     # Blender (metres, -y forward) to Unreal
cs.set_editor_property("scale", unreal.Vector(100, -100, 100))
opt.set_editor_property("conversion_settings", cs)
t.options = opt; t.factory = unreal.HairStrandsFactory()
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
g = unreal.load_asset("%s/%s" % (D, gname))
rg = list(g.get_editor_property("hair_groups_rendering"))
for i, x in enumerate(rg):
    gs = x.get_editor_property("geometry_settings")
    gs.set_editor_property("hair_width_override", True); gs.set_editor_property("hair_width", WIDTH)
    gs.set_editor_property("hair_tip_scale", 0.6)
    x.set_editor_property("geometry_settings", gs); rg[i] = x
g.modify(); g.set_editor_property("hair_groups_rendering", rg)
eal.save_asset(g.get_path_name().split(".")[0], only_if_is_dirty=False)

sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem); lib = unreal.SubobjectDataBlueprintFunctionLibrary
BP = "/Game/MetaHumans/MHC_%s/BP_MHC_%s" % (NAME, NAME)
bp = unreal.load_asset(BP)


def comps():
    for h in sds.k2_gather_subobject_data_for_blueprint(bp):
        d = lib.get_data(h); o = lib.get_object(d)
        if o is not None:
            yield str(lib.get_variable_name(d)), o


comp = next(o for n, o in comps() if n == SLOT and isinstance(o, unreal.GroomComponent))
mats = list(comp.get_editor_property("override_materials"))
src_mat = mats[0] if mats and mats[0] else None
if src_mat is None:   # fall back to the build's own hair material (it carries the recipe's colours)
    cands = [a.split(".")[0] for a in eal.list_assets("/Game/MetaHumans/MHC_%s/Grooms" % NAME, recursive=False, include_folder=False)
             if a.rsplit("/", 1)[1].startswith("MI_WI_%s_" % SLOT) and a.split(".")[0].endswith("_Hair")]
    src_mat = unreal.load_asset(cands[0])
mp = "%s/MI_%s" % (D, gname)
if src_mat.get_path_name().split(".")[0] == mp:   # run again: the slot already wears our copy
    mi = src_mat
else:
    if eal.does_asset_exist(mp):
        eal.delete_asset(mp)
    mi = eal.duplicate_asset(src_mat.get_path_name().split(".")[0], mp)
face = unreal.load_asset("/Game/MetaHumans/MHC_%s/Face/SKM_MHC_%s_FaceMesh" % (NAME, NAME))
bind = "%s/%s_Binding" % (D, gname)
if eal.does_asset_exist(bind):
    eal.delete_asset(bind)
b = unreal.GroomLibrary.create_new_groom_binding_asset_with_path(bind, g, face, 100, None, 0)
eal.save_asset(bind, only_if_is_dirty=False)
for rnd in range(2):   # a binding set together with its groom does not always survive the compile
    for n, o in comps():
        if n == SLOT and isinstance(o, unreal.GroomComponent):
            o.modify()
            o.set_editor_property("groom_asset", g); o.set_editor_property("binding_asset", b)
            o.set_editor_property("override_materials", [mi])
        elif o.get_class().get_name() == "LODSyncComponent":
            m = dict(o.get_editor_property("custom_lod_mapping"))
            for k in list(m):
                if str(k) == SLOT:   # the custom groom has strands only
                    d = m[k]; d.set_editor_property("mapping", [0] * len(list(d.get_editor_property("mapping")))); m[k] = d
            o.modify(); o.set_editor_property("custom_lod_mapping", m)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
o = next(o for n, o in comps() if n == SLOT and isinstance(o, unreal.GroomComponent))
OUT["custom"] = [o.groom_asset.get_name(), o.binding_asset.get_name() if o.binding_asset else None,
                 [i.get_editor_property("num_curves") for i in g.get_editor_property("hair_groups_info")]]
OUT["saved"] = eal.save_asset(BP, only_if_is_dirty=False)
