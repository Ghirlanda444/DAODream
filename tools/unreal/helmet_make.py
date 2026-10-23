"""python helmet_make.py: build the soldiers' helmets and put them in the project (docs/CHARACTERS.md, "Helmets").

Exports a MetaHuman face (CrowdM1) for its skull, runs tools/blender/helmet.py, imports one static mesh per
helmet kind to /Game/Cousland/Outfits/Helmets/SM_Helmet_<kind> (committed: built from an ellipsoid, no
MetaHuman geometry in it) with the outfit materials, and sets BP_DlgNPC's HelmetOffset: the inverse of the
face's head bone in its reference pose, which carries a helmet built in the face's frame onto the head bone.
"""
import json
import os
import subprocess

import pyrun

BLENDER = r"E:/Tools/blender-5.2.2-windows-x64/blender.exe"
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = "E:/DAODream/Unreal/Cousland/Saved/claude/helmets"
FACE = "/Game/MetaHumans/MHC_CrowdM1/Face/SKM_MHC_CrowdM1_FaceMesh"
DEST = "/Game/Cousland/Outfits/Helmets"
KINDS = ("med_hel", "lgt_ltr", "lgt_rlr")

EXPORT = r'''
t = unreal.AssetExportTask()
t.object = unreal.EditorAssetLibrary.load_asset(FACE)
t.filename = WORK + "/face.fbx"
t.automated = True; t.prompt = False; t.replace_identical = True
o = unreal.FbxExportOption(); o.export_morph_targets = False; o.level_of_detail = False; o.collision = False
t.options = o
OUT["face"] = unreal.Exporter.run_asset_export_task(t)
'''

IMPORT = r'''
EAL = unreal.EditorAssetLibrary
AT = unreal.AssetToolsHelpers.get_asset_tools()
# steel: the outfit metal without its rings
steel = DEST + "/MI_Metal_Steel"
if not EAL.does_asset_exist(steel):
    mi = AT.create_asset("MI_Metal_Steel", DEST, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    unreal.MaterialEditingLibrary.set_material_instance_parent(mi, EAL.load_asset("/Game/Cousland/Outfits/M_OutfitMetal"))
    unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(mi, "Rings", 0.0)
    EAL.save_asset(steel, only_if_is_dirty=False)
MATS = {"Metal": EAL.load_asset(steel), "Leather": EAL.load_asset("/Game/Cousland/Outfits/MI_Leather_Brown")}
done = {}
for kind in KINDS:
    t = unreal.AssetImportTask()
    t.filename = WORK + "/SM_Helmet_%s.fbx" % kind
    t.destination_path = DEST; t.destination_name = "SM_Helmet_" + kind
    t.automated = True; t.replace_existing = True; t.save = False
    ui = unreal.FbxImportUI()
    ui.import_mesh = True; ui.import_as_skeletal = False; ui.import_materials = False; ui.import_textures = False
    ui.static_mesh_import_data.combine_meshes = True
    ui.static_mesh_import_data.auto_generate_collision = False
    t.options = ui
    AT.import_asset_tasks([t])
    path = DEST + "/SM_Helmet_" + kind
    sm = EAL.load_asset(path)
    mats = list(sm.static_materials)
    for i, m in enumerate(mats):
        key = "Leather" if "leather" in str(m.material_slot_name).lower() else "Metal"
        m.material_interface = MATS[key]
        mats[i] = m
    sm.set_editor_property("static_materials", mats)
    EAL.save_asset(path, only_if_is_dirty=False)
    b = sm.get_bounds()
    done[kind] = [round(v, 1) for v in (b.origin.x, b.origin.y, b.origin.z, b.box_extent.x, b.box_extent.y, b.box_extent.z)]
OUT["helmets"] = done
# the head bone's pose on this face mesh, in its component space (an unanimated component shows the mesh's
# own bind pose; the shared face skeleton's reference pose puts the head 30 cm lower); its inverse carries the
# helmets onto the bone
a = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, -100000))
a.skeletal_mesh_component.set_skinned_asset_and_update(EAL.load_asset(FACE), False)
head = a.skeletal_mesh_component.get_socket_transform("head", unreal.RelativeTransformSpace.RTS_COMPONENT)
a.destroy_actor()
inv = head.inverse()
OUT["head"] = [round(v, 2) for v in (head.translation.x, head.translation.y, head.translation.z)] + [round(v, 1) for v in (head.rotation.rotator().roll, head.rotation.rotator().pitch, head.rotation.rotator().yaw)]
bp = EAL.load_asset("/Game/Cousland/Dialogue/BP_DlgNPC")
cdo = unreal.get_default_object(bp.generated_class())
cdo.set_editor_property("HelmetOffset", inv)
EAL.save_asset("/Game/Cousland/Dialogue/BP_DlgNPC", only_if_is_dirty=False)
OUT["offset"] = [round(v, 2) for v in (inv.translation.x, inv.translation.y, inv.translation.z)] + [round(v, 1) for v in (inv.rotation.rotator().roll, inv.rotation.rotator().pitch, inv.rotation.rotator().yaw)]
'''


# Every MetaHuman look's face, exported for its skull (heads differ: one soldier's sits 4 cm lower on its head
# bone than CrowdM1's, which buried the helmet in it).
FACES = r'''
import os
looks = []
for p in unreal.EditorAssetLibrary.list_assets("/Game/MetaHumans", recursive=True, include_folder=False):
    n = p.split(".")[0]
    if n.endswith("_FaceMesh") and "/Face/SKM_MHC_" in n:
        look = n.rsplit("/SKM_MHC_", 1)[1][:-len("_FaceMesh")]
        if look.startswith("test_"):
            continue
        out = WORK + "/faces/" + look + ".fbx"
        if not os.path.exists(out):
            t = unreal.AssetExportTask()
            t.object = unreal.EditorAssetLibrary.load_asset(n)
            t.filename = out
            t.automated = True; t.prompt = False; t.replace_identical = True
            o = unreal.FbxExportOption(); o.export_morph_targets = False; o.level_of_detail = False; o.collision = False
            t.options = o
            unreal.Exporter.run_asset_export_task(t)
        looks.append((look, n))
OUT["looks"] = looks
'''

# Per look, the helmet's placement on its head bone: the helmet is built on CrowdM1's skull, in its face's
# component space; it is moved and scaled (per axis) from that skull's ellipsoid onto the look's, then carried
# by the inverse of the look's own head bone (bind pose). BP_DlgNPC.AttachHelmet uses HelmetFits[look] when the
# look is in HelmetFitLooks, HelmetOffset (CrowdM1's) when not.
FITS = r'''
EAL = unreal.EditorAssetLibrary
def ue(c):  # Blender metres (the face looks along -y) to Unreal centimetres
    return unreal.Vector(c[0] * 100.0, -c[1] * 100.0, c[2] * 100.0)
def ellipsoid(k):
    cy = k["centre"][1] + k["facing"] * (k["front"] - k["back"]) / 2.0  # the middle between brow and occiput
    return ue([k["centre"][0], cy, k["centre"][2] + k["rz"] * 0.5]), unreal.Vector(k["rx"], (k["front"] + k["back"]) / 2.0, k["rz"])
base_c, base_r = ellipsoid(FIT_DATA[BASE])
names, fits = [], []
for look, path in LOOKS:
    if look not in FIT_DATA:
        continue
    c, r = ellipsoid(FIT_DATA[look])
    s = unreal.Vector(r.x / base_r.x, r.y / base_r.y, r.z / base_r.z)
    fit = unreal.Transform(c - unreal.Vector(base_c.x * s.x, base_c.y * s.y, base_c.z * s.z), unreal.Rotator(0, 0, 0), s)
    a = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, -100000))
    a.skeletal_mesh_component.set_skinned_asset_and_update(EAL.load_asset(path), False)
    head = a.skeletal_mesh_component.get_socket_transform("head", unreal.RelativeTransformSpace.RTS_COMPONENT)
    a.destroy_actor()
    names.append(look)
    fits.append(fit * head.inverse())
bp = EAL.load_asset("/Game/Cousland/Dialogue/BP_DlgNPC")
cdo = unreal.get_default_object(bp.generated_class())
cdo.set_editor_property("HelmetFitLooks", []); cdo.set_editor_property("HelmetFitLooks", names)
cdo.set_editor_property("HelmetFits", []); cdo.set_editor_property("HelmetFits", fits)
EAL.save_asset("/Game/Cousland/Dialogue/BP_DlgNPC", only_if_is_dirty=False)
OUT["fits"] = {n: [round(f.translation.z, 1), round(f.scale3d.x, 3), round(f.scale3d.z, 3)] for n, f in zip(names, fits)}
'''


def main():
    os.makedirs(WORK + "/faces", exist_ok=True)
    print("face", pyrun.run("FACE = %r\nWORK = %r\n" % (FACE, WORK) + EXPORT, 300))
    r = subprocess.run([BLENDER, "-b", "--factory-startup", "-P", os.path.join(HERE, "..", "blender", "helmet.py"), "--",
                        WORK + "/face.fbx", WORK], capture_output=True, text=True)
    print("blender:", [l for l in r.stdout.splitlines() if l.startswith("HELMET") or "Error" in l][-5:])
    print("import:", pyrun.run("WORK = %r\nDEST = %r\nKINDS = %r\nFACE = %r\n" % (WORK, DEST, KINDS, FACE) + IMPORT, 600))
    looks = pyrun.run("WORK = %r\n" % WORK + FACES, 900)["looks"]
    fits_json = WORK + "/fits.json"
    jobs = ["%s=%s/faces/%s.fbx" % (look, WORK, look) for look, _ in looks]
    r = subprocess.run([BLENDER, "-b", "--factory-startup", "-P", os.path.join(HERE, "..", "blender", "helmet.py"), "--",
                        "--fit", fits_json] + jobs, capture_output=True, text=True)
    print("fit:", [l for l in r.stdout.splitlines() if l.startswith("HELMET") or "Error" in l][-3:])
    data = json.load(open(fits_json))
    print("fits:", pyrun.run("FIT_DATA = %r\nLOOKS = %r\nBASE = 'CrowdM1'\n" % (data, looks) + FITS, 900))


if __name__ == "__main__":
    main()
