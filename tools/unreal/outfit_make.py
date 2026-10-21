"""python outfit_make.py <Look>:<kind> [...]: build outfits for MetaHuman looks (docs/CHARACTERS.md, "Outfits").

For each look (the MetaHuman's name, e.g. BryceW, CrowdM1) and kind (a chest item without "gen_im_", e.g.
cth_nob_c01): export the look's body and default clothes from the editor, fit the outfit to them in Blender
(tools/blender/outfit.py), import it as /Game/MetaHumans/MHC_<Look>/DAO/SKM_<Look>_<kind> on the MetaHuman
skeleton, and give its material slots the kind's colours (MATERIALS). The outfits are shaped from the
MetaHuman bodies, so like them they stay out of git; BP_DlgNPC.ApplyOutfit puts them on in game.
"""
import os
import subprocess
import sys

import pyrun

BLENDER = r"E:/Tools/blender-5.2.2-windows-x64/blender.exe"
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = "E:/DAODream/Unreal/Cousland/Saved/claude/outfits"
O = "/Game/Cousland/Outfits/"
MATERIALS = {
    "arm_cht_med_chn": {"Main": "MI_Cloth_CouslandBlue", "Second": "MI_Cloth_GreyWool", "Leather": "MI_Leather_Brown",
                        "Metal": "MI_Metal_Chain"},
    "cth_nob_c01": {"Main": "MI_Cloth_BryceBlue", "Second": "MI_Cloth_BrownWool", "Leather": "MI_Leather_Dark",
                    "Metal": "MI_Metal_Gold"},
    "cth_nob_af0": {"Main": "MI_Cloth_EleanorWine", "Second": "MI_Cloth_BrownWool", "Leather": "MI_Leather_Dark",
                    "Metal": "MI_Metal_Gold"},
}

EXPORT = r'''
for name, path in ((LOOK + "_body", "/Game/MetaHumans/MHC_%s/Body/SKM_MHC_%s_BodyMesh" % (LOOK, LOOK)),
                   (LOOK + "_default", "/Game/MetaHumans/MHC_%s/Clothing/MHC_%s_Outfits" % (LOOK, LOOK))):
    t = unreal.AssetExportTask()
    t.object = unreal.EditorAssetLibrary.load_asset(path)
    t.filename = WORK + "/" + name + ".fbx"
    t.automated = True; t.prompt = False; t.replace_identical = True
    o = unreal.FbxExportOption(); o.export_morph_targets = False; o.level_of_detail = False; o.collision = False
    t.options = o
    OUT[name] = unreal.Exporter.run_asset_export_task(t)
'''

ASSIGN = r'''
sk = unreal.EditorAssetLibrary.load_asset(DEST + "/" + NAME)
mats = list(sk.materials)
for i, m in enumerate(mats):
    mi = MATS.get(str(m.material_slot_name))
    if mi:
        m.material_interface = unreal.EditorAssetLibrary.load_asset(mi)
        mats[i] = m
sk.set_editor_property("materials", mats)
unreal.EditorAssetLibrary.save_loaded_asset(sk)
OUT["slots"] = [(str(m.material_slot_name), m.material_interface.get_name() if m.material_interface else None) for m in sk.materials]
'''


def make(look: str, kind: str):
    print(look, kind, pyrun.run("LOOK = %r\nWORK = %r\n" % (look, WORK) + EXPORT, 300))
    out = "%s/%s_%s.fbx" % (WORK, look, kind)
    r = subprocess.run([BLENDER, "-b", "--factory-startup", "-P", os.path.join(HERE, "..", "blender", "outfit.py"), "--",
                        "%s/%s_body.fbx" % (WORK, look), "%s/%s_default.fbx" % (WORK, look), out, kind],
                       capture_output=True, text=True)
    line = [l for l in r.stdout.splitlines() if l.startswith("OUTFIT") or "Error" in l or "Traceback" in l]
    print("  blender:", line[-3:])
    if not os.path.exists(out):
        raise RuntimeError(r.stdout[-2000:] + r.stderr[-2000:])
    dest, name = "/Game/MetaHumans/MHC_%s/DAO" % look, "SKM_%s_%s" % (look, kind)
    imp = open(os.path.join(HERE, "outfit_import.body.py"), encoding="utf-8").read()
    print("  import:", pyrun.run("FBX = %r\nDEST = %r\nNAME = %r\n" % (out, dest, name) + imp, 600))
    mats = {slot: O + mi for slot, mi in MATERIALS[kind].items()}
    print("  materials:", pyrun.run("DEST = %r\nNAME = %r\nMATS = %r\n" % (dest, name, mats) + ASSIGN, 300))


if __name__ == "__main__":
    for job in sys.argv[1:]:
        make(*job.split(":"))
