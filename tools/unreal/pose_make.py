"""python pose_make.py [pose...]: held poses for the mannequin body (docs/CHARACTERS.md, "Poses").

Exports /Game/Characters/Mannequins/Meshes/SKM_Manny_Simple, runs tools/blender/poses.py on it for each pose
(default: all of POSES) and imports the result as /Game/Cousland/Anims/<pose> (committed: our own poses on Epic's
template skeleton), animations for SK_Mannequin. A BP_DlgNPC idles in A_WoundedSlump when the area export names it
in NpcIdle; a fallen player or party member lies in A_Fallen (docs/COMBAT.md).
"""
import os
import subprocess
import sys

import pyrun

BLENDER = r"E:/Tools/blender-5.2.2-windows-x64/blender.exe"
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = "E:/DAODream/Unreal/Cousland/Saved/claude/poses"
DEST = "/Game/Cousland/Anims"
POSES = ("A_WoundedSlump", "A_Fallen")

EXPORT = r'''
t = unreal.AssetExportTask()
t.object = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple")
t.filename = WORK + "/SKM_Manny_Simple.fbx"
t.automated = True; t.prompt = False; t.replace_identical = True
o = unreal.FbxExportOption(); o.export_morph_targets = False; o.level_of_detail = False; o.collision = False
t.options = o
OUT["mesh"] = unreal.Exporter.run_asset_export_task(t)
'''

IMPORT = r'''
unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX False")
ui = unreal.FbxImportUI()
ui.import_mesh = False
ui.import_animations = True
ui.import_materials = False
ui.import_textures = False
ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_ANIMATION
ui.skeleton = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Mannequins/Meshes/SK_Mannequin")
t = unreal.AssetImportTask()
t.filename = FBX; t.destination_path = DEST; t.destination_name = NAME
t.automated = True; t.replace_existing = True; t.save = True; t.options = ui
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
a = unreal.EditorAssetLibrary.load_asset(DEST + "/" + NAME)
OUT["anim"] = a.get_path_name() if a else None
OUT["length"] = unreal.AnimationLibrary.get_sequence_length(a) if a else None
'''


def main(poses):
    os.makedirs(WORK, exist_ok=True)
    print("export", pyrun.run("WORK = %r\n" % WORK + EXPORT, 300))
    for pose in poses:
        out = "%s/%s.fbx" % (WORK, pose)
        r = subprocess.run([BLENDER, "-b", "--factory-startup", "-P", os.path.join(HERE, "..", "blender", "poses.py"),
                            "--", WORK + "/SKM_Manny_Simple.fbx", out, pose], capture_output=True, text=True)
        print(pose, "blender:", [l for l in r.stdout.splitlines() if l.startswith("POSE") or "Traceback" in l][-3:])
        print(pose, "import:", pyrun.run("FBX = %r\nDEST = %r\nNAME = %r\n" % (out, DEST, pose) + IMPORT, 300))


if __name__ == "__main__":
    main(sys.argv[1:] or POSES)
