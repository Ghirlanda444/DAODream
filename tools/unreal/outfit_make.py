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
CHAIN = {"Main": "MI_Cloth_CouslandBlue", "Second": "MI_Cloth_GreyWool", "Leather": "MI_Leather_Brown",
         "Metal": "MI_Metal_Chain"}
HOWE_LEATHER = {"Main": "MI_Cloth_HoweRed", "Second": "MI_Cloth_BrownWool", "Leather": "MI_Leather_Brown",
                "Metal": "MI_Metal_Chain"}


def clothes(main, second="MI_Cloth_BrownWool", leather="MI_Leather_Brown", metal="MI_Metal_Gold"):
    return {"Main": main, "Second": second, "Leather": leather, "Metal": metal}


MATERIALS = {
    "arm_cht_med_chn": CHAIN,  # castle guards, Gilmore
    "arm_cht_hvy_hch": CHAIN,  # Fergus
    "arm_cht_med_scl": {"Main": "MI_Cloth_HoweRed", "Second": "MI_Cloth_BlackWool", "Leather": "MI_Leather_Dark",
                        "Metal": "MI_Metal_Scale"},  # Howe's knight
    "arm_cht_lgt_ltr": HOWE_LEATHER, "arm_cht_lgt_rlr": HOWE_LEATHER,  # Howe's soldiers and archers
    "cth_nob_c01": clothes("MI_Cloth_BryceBlue", leather="MI_Leather_Dark"),  # Bryce
    "cth_nob_af0": clothes("MI_Cloth_EleanorWine", leather="MI_Leather_Dark"),  # Eleanor
    "cth_nob_b02": clothes("MI_Cloth_HoweRed", "MI_Cloth_BlackWool", "MI_Leather_Dark"),  # Arl Howe
    "cth_nob_c00": clothes("MI_Cloth_NobleGreen", leather="MI_Leather_Dark"),  # Dairren
    "cth_nob_e01": clothes("MI_Cloth_NobleGreen", leather="MI_Leather_Dark"),  # Lady Landra
    "cth_nob_b00": clothes("MI_Cloth_NobleGold", leather="MI_Leather_Dark"),  # Oriana
    "cth_nob_f01": clothes("MI_Cloth_PaleBlue", leather="MI_Leather_Dark", metal="MI_Metal_Silver"),  # Iona
    "cth_com_a00": clothes("MI_Cloth_Undyed"), "cth_com_c00": clothes("MI_Cloth_RustWool", "MI_Cloth_Undyed"),
    "cth_com_c02": clothes("MI_Cloth_BlueGrey"), "cth_com_b00": clothes("MI_Cloth_MossWool"),
    "cth_mag_tra": clothes("MI_Cloth_ScholarBrown", leather="MI_Leather_Dark"),  # Aldous
    "cth_cha_a00": clothes("MI_Cloth_ChantryWhite", "MI_Cloth_ChantryRed"),  # Mother Mallol
    "duncan_robe": clothes("MI_Cloth_WardenBlue", "MI_Cloth_GreyWool", "MI_Leather_Dark"),  # Duncan
}
# Looks that are women: the same common clothes make a dress for them (tools/blender/outfit.py).
FEMALE = {"EleanorS", "Cook", "Mallol", "Oriana", "Landra", "Iona", "CrowdF0", "CrowdF1"}

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
    if os.path.exists(out):
        os.remove(out)  # so a failed Blender run cannot leave an old outfit to import
    r = subprocess.run([BLENDER, "-b", "--factory-startup", "-P", os.path.join(HERE, "..", "blender", "outfit.py"), "--",
                        "%s/%s_body.fbx" % (WORK, look), "%s/%s_default.fbx" % (WORK, look), out, kind,
                        "f" if look in FEMALE else "m"],
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
    failed = []
    for job in sys.argv[1:]:
        try:
            make(*job.split(":"))
        except Exception as e:  # keep going: report at the end
            failed.append((job, str(e)[-300:]))
    print("FAILED", failed if failed else "none")
