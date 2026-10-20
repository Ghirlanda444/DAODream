# Inside the editor (via pyrun): give a built MetaHuman pointed elf ears.
#
# MetaHuman has no elf ears, so after the build this pulls the top of each ear up, back and a little
# outward into a point, on every LOD of the character's face mesh (SKM_MHC_<Name>_FaceMesh). The ears are
# found from the Creator's face landmarks 38/39 (left ear) and 54/56 (right ear); vertices near each ear on
# its outer side move, more the higher they sit on the ear, so the root stays put and the tip grows.
# Skin weights and UVs come along (Geometry Script read/write); a rebuild undoes it, so the batch maker
# runs this after every build of a recipe with "elf_ears": true.
# NAME: the MetaHuman's name. Optional: LIFT, BACK, OUTWARD (cm at the tip), RADIUS (cm around the ear).
import math
LIFT = globals().get("LIFT", 2.8)
BACK = globals().get("BACK", 1.4)
OUTWARD = globals().get("OUTWARD", 0.8)
RADIUS = globals().get("RADIUS", 3.4)
GS = unreal.GeometryScript_AssetUtils
LU = unreal.GeometryScript_List
sub = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
c = unreal.load_asset("/Game/MetaHumans/%s/MHC_%s" % (NAME, NAME))
sub.try_add_object_to_edit(c)
lm = sub.get_face_landmarks(c)
ears = []
for a, b in ((38, 39), (54, 56)):   # left, right
    p = (lm[a] + lm[b]) * 0.5
    ears.append((p, 1.0 if p.x > 0 else -1.0))
skm = unreal.load_asset("/Game/MetaHumans/MHC_%s/Face/SKM_MHC_%s_FaceMesh" % (NAME, NAME))
report = {}
for lod in range(8):
    dm = unreal.DynamicMesh()
    read = unreal.GeometryScriptMeshReadLOD(); read.lod_index = lod
    dm, outcome = GS.copy_mesh_from_skeletal_mesh(skm, dm, unreal.GeometryScriptCopyMeshFromAssetOptions(), read)
    if outcome != unreal.GeometryScriptOutcomePins.SUCCESS:
        break
    dm, pts, _ = unreal.GeometryScript_MeshQueries.get_all_vertex_positions(dm, False)
    vl = list(LU.convert_vector_list_to_array(pts))
    moved = 0
    for centre, side in ears:
        sel = [i for i, v in enumerate(vl)
               if (v - centre).length() < RADIUS and v.x * side > abs(centre.x) - 1.0]
        if not sel:
            continue
        top = max(vl[i].z for i in sel); base = centre.z - 0.5
        for i in sel:
            v = vl[i]
            w = max(0.0, min(1.0, (v.z - base) / max(top - base, 0.1))) ** 1.7
            if w > 0:
                vl[i] = unreal.Vector(v.x + side * OUTWARD * w, v.y - BACK * w, v.z + LIFT * w)
                moved += 1
    pts = LU.convert_array_to_vector_list(vl)
    dm = unreal.GeometryScript_MeshEdits.set_all_mesh_vertex_positions(dm, pts)
    write = unreal.GeometryScriptMeshWriteLOD(); write.lod_index = lod
    opts = unreal.GeometryScriptCopyMeshToAssetOptions()
    dm, outcome = GS.copy_mesh_to_skeletal_mesh(dm, skm, opts, write)
    report[lod] = [moved, str(outcome).split(".")[-1]]
unreal.EditorAssetLibrary.save_asset(skm.get_path_name().split(".")[0], only_if_is_dirty=False)
OUT["ears"] = report
