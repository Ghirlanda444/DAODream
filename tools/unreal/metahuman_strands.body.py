# Inside the editor (via pyrun): give a built MetaHuman real hair strands.
#
# The Optimized assembly copies each groom into MHC_<Name>/Grooms with its strands stripped (1 curve
# instead of tens of thousands) and maps LODSync to card LODs, so beards and hair always render as hair
# cards: black, speckled, dithered patches in close-ups. This points the Hair/Beard/Mustache/Eyebrows
# components back at Epic's original groom (strands for LOD 0-1, cards and meshes after), optionally with
# wider strands (THICKEN factors), binds it to the character's face mesh, keeps the assembly's material
# overrides (same slot names), and maps LODSync so its closest level uses strands:
#   3 levels (named characters): strands -> cards -> meshes;  2 levels (crowd faces): strands -> cards.
# NAMES: list of MetaHuman names (BP_MHC_<Name>); THICKEN: {name: {slot: factor}} (optional);
# LAYERS: {name: {component: [groom, like_slot]}} (optional, see below).
SLOTS = ("Hair", "Beard", "Mustache", "Eyebrows")
MAPS = {3: [0, 3, 7], 2: [0, 3]}
CARDS = {3: [3, 5, 7], 2: [5, 7]}   # the assembly's own mapping (cards and meshes only)
ORIG = "/MetaHumanCharacter/Optional/Grooms/GroomAssets"
TEMPLATES = "/MetaHumanCharacter/Optional/Grooms/Bindings"   # <Type>/<Groom>_Binding, fitted to a template head
eal = unreal.EditorAssetLibrary
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem); lib = unreal.SubobjectDataBlueprintFunctionLibrary
originals = {a.rsplit("/", 1)[1].split(".")[0]: a.split(".")[0] for a in eal.list_assets(ORIG, recursive=True, include_folder=False)
             if "/GroomAssets/" in a and a.rsplit("/", 1)[1].split(".")[0] == a.rsplit("/", 2)[1]}
templates = {}   # groom name -> template binding (named <Groom>_Binding, or just <Groom> for a few)
for a in eal.list_assets(TEMPLATES, recursive=True, include_folder=False):
    n = a.rsplit("/", 1)[1].split(".")[0]
    if not n.startswith("WI_"):
        templates[n[:-len("_Binding")] if n.endswith("_Binding") else n] = a.split(".")[0]
THICKEN = globals().get("THICKEN") or {}
LAYERS = globals().get("LAYERS") or {}
report = {}


def comps(bp):
    for h in sds.k2_gather_subobject_data_for_blueprint(bp):
        d = lib.get_data(h); o = lib.get_object(d)
        if o is not None:
            yield str(lib.get_variable_name(d)), o


for name in NAMES:
    BP = "/Game/MetaHumans/MHC_%s/BP_MHC_%s" % (name, name)
    bp = unreal.load_asset(BP)
    face = unreal.load_asset("/Game/MetaHumans/MHC_%s/Face/SKM_MHC_%s_FaceMesh" % (name, name))
    dst = "/Game/MetaHumans/%s/Strands" % name
    made, r = {}, {}
    for slot, o in list(comps(bp)):
        if not isinstance(o, unreal.GroomComponent) or slot not in SLOTS or slot in made or not o.groom_asset:
            continue
        # The original's name: the groom's own, minus our "_Thick" suffix, or the binding's (the assembly
        # sometimes names the groom copy GroomAsset_0 but keeps the groom's name on its binding).
        n = o.groom_asset.get_name()
        cands = [n, n[:-len("_Thick")] if n.endswith("_Thick") else None,
                 o.binding_asset.get_name().replace("_Binding", "") if o.binding_asset else None]
        base = next((c for c in cands if c and c in originals), None)
        src = originals.get(base)
        if not src:
            r[slot] = "no original for " + n
            continue
        factor = THICKEN.get(name, {}).get(slot)
        if factor:
            path = "%s/%s_Thick" % (dst, base)
            if eal.does_asset_exist(path):
                eal.delete_asset(path)
            g = eal.duplicate_asset(src, path)
            rg = list(g.get_editor_property("hair_groups_rendering"))
            for i, x in enumerate(rg):
                gs = x.get_editor_property("geometry_settings")
                gs.set_editor_property("hair_width_override", True)
                gs.set_editor_property("hair_width", gs.hair_width * factor)
                x.set_editor_property("geometry_settings", gs); rg[i] = x
            g.modify(); g.set_editor_property("hair_groups_rendering", rg)
            eal.save_asset(path, only_if_is_dirty=False)
        else:
            g = unreal.load_asset(src)
        bind = "%s/%s_Binding" % (dst, g.get_name())
        if eal.does_asset_exist(bind):
            eal.delete_asset(bind)
        # Epic's grooms are authored on a template head (SKM_Groom_Head_Legacy01/02, named by the template
        # binding): binding straight to the character's face misplaces the roots, so transfer from that head.
        tb = templates.get(base)
        head = unreal.load_asset(tb).get_editor_property("target_skeletal_mesh") if tb else None
        b = unreal.GroomLibrary.create_new_groom_binding_asset_with_path(bind, g, face, 100, head, 0)
        eal.save_asset(bind, only_if_is_dirty=False)
        made[slot] = (g, b)
        r[slot + "_source"] = head.get_name() if head else None
    for rnd in range(2):  # a binding set together with its groom does not always survive the compile
        for slot, o in comps(bp):
            if slot in made:
                o.modify()
                o.set_editor_property("groom_asset", made[slot][0])
                o.set_editor_property("binding_asset", made[slot][1])
            elif o.get_class().get_name() == "LODSyncComponent":
                n = int(o.get_editor_property("num_lods"))
                m = dict(o.get_editor_property("custom_lod_mapping"))
                for k in list(m):   # slots left on a cards-only copy keep the assembly's mapping
                    if str(k) in SLOTS and n in MAPS:
                        d = m[k]; d.set_editor_property("mapping", (MAPS if str(k) in made else CARDS)[n]); m[k] = d
                o.modify(); o.set_editor_property("custom_lod_mapping", m)
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    # Extra groom layers (LAYERS = {name: {component: [groom, like_slot]}}), e.g. dense stubble under a full
    # beard so skin does not show through it: a new groom component on the face, bound like the others and
    # wearing the like_slot's first material (its colours). Strands only, so it is left out of LODSync.
    for comp, (gname, like) in LAYERS.get(name, {}).items():
        handles = {str(lib.get_variable_name(lib.get_data(h))): h for h in sds.k2_gather_subobject_data_for_blueprint(bp)}
        if comp not in handles:
            h, fail = sds.add_new_subobject(unreal.AddNewSubobjectParams(
                parent_handle=handles["Face"], new_class=unreal.GroomComponent, blueprint_context=bp))
            sds.rename_subobject(h, unreal.Text(comp))
            handles[comp] = h
        g = unreal.load_asset(originals[gname])
        bind = "%s/%s_Binding" % (dst, gname)
        if eal.does_asset_exist(bind):
            eal.delete_asset(bind)
        head = unreal.load_asset(templates[gname]).get_editor_property("target_skeletal_mesh")
        b = unreal.GroomLibrary.create_new_groom_binding_asset_with_path(bind, g, face, 100, head, 0)
        eal.save_asset(bind, only_if_is_dirty=False)
        mat = [o for s, o in comps(bp) if s == like][0].get_editor_property("override_materials")[0]
        for rnd in range(2):
            o = lib.get_object(lib.get_data(handles[comp]))
            o.modify()
            o.set_editor_property("groom_asset", g); o.set_editor_property("binding_asset", b)
            o.set_editor_property("override_materials", [mat])
            unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        made[comp] = (g, b)
    for slot, o in comps(bp):
        if slot in made:
            r[slot] = [o.groom_asset.get_name(), o.binding_asset.get_name() if o.binding_asset else None]
        elif o.get_class().get_name() == "LODSyncComponent":
            r["lodsync"] = {str(k): list(v.get_editor_property("mapping")) for k, v in dict(o.get_editor_property("custom_lod_mapping")).items() if str(k) in SLOTS}
    r["saved"] = eal.save_asset(BP, only_if_is_dirty=False)
    report[name] = r
OUT["strands"] = report
