"""python kit_props.py: import the free Megascans props the kit map uses (docs/ART.md, "Kit meshes").

Each prop is a scan unpacked from its Fab zip into extracted/fab/props/<pack>/ (git-ignored; FBX plus
4K JPEG maps). It is imported to /Game/ThirdParty/Megascans/Props/<Name>/ (git-ignored) as SM_<Name>
(Nanite, simple box collision so the castle's boxes can go) with its BaseColor, Normal, Roughness and
AO capped at 2K, and MI_<Name>, an instance of /Game/Cousland/Materials/M_ScanProp (committed, made
here too). Its bounds (centre and half extents, cm) and the RULES below (which kit pieces become which
prop) are written into tools/unreal/kitmap.json, which the area export uses to fit props to pieces.
Props already imported are only measured again. Maps are cut to 2K before import and the batch stops
when memory runs low (a 4K import froze this 16 GB PC once).
"""
import json
import os

import pyrun

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(ROOT, "extracted", "fab", "props").replace("\\", "/")
KITMAP = os.path.join(HERE, "kitmap.json")

# name -> (pack folder, scan folder or "" for a single scan, FBX file)
PROPS = {
    "WoodenBarrel": ("wooden_barrel_tmgpcg2fa", "", "Wooden_Barrel_tmgpcg2fa_High.fbx"),
    "WoodenChair": ("wooden_chair_uknjbb2bw", "", None),
    "WoodenTable": ("wooden_table_uc1kebzfa", "", None),
    "WoodenBench": ("wooden_bench_wjfjahl", "", None),
    "WoodenShelf": ("wooden_shelf_vlwmahl", "", None),
    "WoodenBookshelf": ("wooden_bookshelf_vmhndfu", "", None),
    "WoodenBucket": ("old_wooden_bucket_xgihfgbqx", "", None),
    "WoodenPot": ("old_wooden_pot_wgxobac", "", None),
    "OldBook": ("old_book_wldocam", "", None),
    "WineBottle": ("medieval_banquet", "tjuhabova", None),
    "Jug": ("medieval_banquet", "tl2qbdffa", None),
    "Tankard": ("medieval_banquet", "xfphbfb", None),
    "Goblet": ("medieval_banquet", "xfphcey", None),
    "Plate": ("medieval_banquet", "xixlcj1mw", None),
    "Bowl": ("medieval_banquet", "wgwneir", None),
    "BigBowl": ("medieval_banquet", "wh0ncbf", None),
    "Knife": ("medieval_banquet", "xiyoaab", None),
    "Bread": ("medieval_banquet", "whplfip", None),
    "Pie": ("medieval_banquet", "wfzjegjs", None),
    "Fish": ("medieval_banquet", "weflciqaa", None),
    "Squash": ("medieval_banquet", "ve3kadgjw", None),
    "Apple": ("medieval_banquet", "tefadiqla", None),
    "Grapes": ("medieval_banquet", "xk4gejl", None),
    "Chicken": ("medieval_banquet", "wktnfbds", None),
    "LongTable": ("medieval_banquet", "ulzrcgoaw", None),
    "BanquetBench": ("medieval_banquet", "wjfjahl", None),
    "BarrelStand": ("medieval_banquet", "udmmfbpqx", None),
    "Urn": ("medieval_banquet", "wccvabgaw", None),
}

# Which kit pieces become which prop: model name pattern -> mesh, fitted to the piece's bounding box
# ("uniform": scaled to its height; "stretch": to all three sizes, for furniture whose footprint
# matters). First match wins. The game's lamps, candles and torches are fixtures (kit.FIXTURE_MODELS).
RULES = [
    ("prp_barrel*", "WoodenBarrel", "uniform"), ("prp_brrl*", "WoodenBarrel", "uniform"),
    ("prp_chair*", "WoodenChair", "stretch"),
    ("prp_fertbllng*", "LongTable", "stretch"),  # the great hall's long table
    # "Wooden Table" is a small square table (78 cm, 52 cm high): the long banquet table suits the castle's
    # tables (1.6 x 0.9 m) better
    ("prp_table*", "LongTable", "stretch"), ("prp_tabletall*", "LongTable", "stretch"),
    ("prp_desklarge*", "LongTable", "stretch"), ("prp_roundtable*", "WoodenTable", "stretch"),
    ("prp_benchlog*", "WoodenBench", "stretch"), ("prp_bnchlng*", "BanquetBench", "stretch"),
    # "Wooden Shelf" is a small wall shelf: it suits the long wall shelves; standing shelves are bookshelves
    ("prp_sngleshlve*", "WoodenShelf", "stretch"),
    ("prp_smshelf*", "WoodenBookshelf", "stretch"), ("prp_shelf*", "WoodenBookshelf", "stretch"),
    ("prp_lrgbkslf*", "WoodenBookshelf", "stretch"), ("prp_bkslf*", "WoodenBookshelf", "stretch"),
    ("prp_bucket*", "WoodenBucket", "uniform"),
    ("prp_pot0*", "WoodenPot", "uniform"), ("prp_potweathered*", "WoodenPot", "uniform"),
    ("prp_cupwood*", "Tankard", "uniform"), ("prp_bottlewine*", "WineBottle", "uniform"),
    ("prp_jugofwater*", "Jug", "uniform"),
    ("prp_bowlwood*", "Bowl", "uniform"), ("prp_bowlfruit*", "Bowl", "uniform"),
    ("prp_fdbrd*", "Bread", "uniform"), ("prp_foodpie*", "Pie", "uniform"), ("prp_foodfish*", "Fish", "uniform"),
    ("prp_fdvgsquash*", "Squash", "uniform"), ("prp_fdvgtomato*", "Apple", "uniform"),
    ("prp_tlckknife*", "Knife", "uniform"),
    ("prp_ferbook0*", "OldBook", "uniform"), ("prp_ferbookopn*", "OldBook", "uniform"),
]

MASTER = r'''
AT = unreal.AssetToolsHelpers.get_asset_tools(); EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary
path = "/Game/Cousland/Materials/M_ScanProp"
# rebuilt in place every run (instances keep it as their parent)
if EAL.does_asset_exist(path):
    m = EAL.load_asset(path)
    MEL.delete_all_material_expressions(m)
else:
    m = AT.create_asset("M_ScanProp", "/Game/Cousland/Materials", unreal.Material, unreal.MaterialFactoryNew())
def tex(name, default, sampler, y):
    e = MEL.create_material_expression(m, unreal.MaterialExpressionTextureSampleParameter2D, -600, y)
    e.set_editor_property("parameter_name", name)
    e.set_editor_property("texture", EAL.load_asset(default))
    e.set_editor_property("sampler_type", sampler)
    return e
S = unreal.MaterialSamplerType
base = tex("BaseColor", "/Engine/EngineMaterials/DefaultDiffuse", S.SAMPLERTYPE_COLOR, 0)
nrm = tex("Normal", "/Engine/EngineMaterials/DefaultNormal", S.SAMPLERTYPE_NORMAL, 250)
# linear maps: the placeholder must be linear too, or the material fails to compile (2026-10-23)
rough = tex("Roughness", "/Engine/EngineMaterials/T_Default_Material_Grid_M", S.SAMPLERTYPE_LINEAR_COLOR, 500)
ao = tex("AO", "/Engine/EngineMaterials/T_Default_Material_Grid_M", S.SAMPLERTYPE_LINEAR_COLOR, 750)
tint = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -600, -200)
tint.set_editor_property("parameter_name", "Tint")
tint.set_editor_property("default_value", unreal.LinearColor(1, 1, 1, 1))
mul = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -250, 0)
MEL.connect_material_expressions(base, "RGB", mul, "A")
MEL.connect_material_expressions(tint, "RGB", mul, "B")
P = unreal.MaterialProperty
MEL.connect_material_property(mul, "", P.MP_BASE_COLOR)
MEL.connect_material_property(nrm, "RGB", P.MP_NORMAL)
MEL.connect_material_property(rough, "R", P.MP_ROUGHNESS)
MEL.connect_material_property(ao, "R", P.MP_AMBIENT_OCCLUSION)
m.set_editor_property("used_with_instanced_static_meshes", True)
m.set_editor_property("used_with_nanite", True)
MEL.recompile_material(m)
EAL.save_loaded_asset(m)
OUT["master"] = EAL.does_asset_exist(path)
'''

IMPORT = r'''
AT = unreal.AssetToolsHelpers.get_asset_tools(); EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary
if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world():
    raise RuntimeError("stop Play/Simulate first")
unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX False")
dest = "/Game/ThirdParty/Megascans/Props/" + NAME
mesh_path = dest + "/SM_" + NAME
if not EAL.does_asset_exist(mesh_path):
    ui = unreal.FbxImportUI()
    ui.import_mesh = True; ui.import_as_skeletal = False; ui.import_materials = False; ui.import_textures = False
    ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
    d = ui.static_mesh_import_data
    d.combine_meshes = True; d.auto_generate_collision = False
    t = unreal.AssetImportTask()
    t.filename = FBX; t.destination_path = dest; t.destination_name = "SM_" + NAME
    t.automated = True; t.replace_existing = True; t.save = False; t.options = ui
    AT.import_asset_tasks([t])
    textures = {}
    for key, kind in MAPS.items():
        if not kind:
            continue
        ti = unreal.AssetImportTask()
        ti.filename = kind; ti.destination_path = dest; ti.destination_name = "T_%s_%s" % (NAME, key)
        ti.automated = True; ti.replace_existing = True; ti.save = False
        AT.import_asset_tasks([ti])
        tex = EAL.load_asset(dest + "/T_%s_%s" % (NAME, key))
        tex.set_editor_property("max_texture_size", 2048)
        if key == "Normal":
            tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
            tex.set_editor_property("srgb", False)
        elif key != "BaseColor":  # linear, default compression: what M_ScanProp's linear samplers take
            tex.set_editor_property("srgb", False)
        textures[key] = tex
    mi = AT.create_asset("MI_" + NAME, dest, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mi.set_editor_property("parent", EAL.load_asset("/Game/Cousland/Materials/M_ScanProp"))
    for key, tex in textures.items():
        MEL.set_material_instance_texture_parameter_value(mi, key, tex)
    sm = EAL.load_asset(mesh_path)
    for i in range(len(sm.static_materials)):
        sm.set_material(i, mi)
    ns = sm.get_editor_property("nanite_settings")
    ns.enabled = True
    sm.set_editor_property("nanite_settings", ns)
    unreal.EditorStaticMeshLibrary.remove_collisions(sm)
    unreal.EditorStaticMeshLibrary.add_simple_collisions(sm, unreal.ScriptingCollisionShapeType.BOX)
    for p in EAL.list_assets(dest, recursive=False):
        EAL.save_asset(p.split(".")[0], only_if_is_dirty=False)
sm = EAL.load_asset(mesh_path)
b = sm.get_bounding_box()
OUT["bounds"] = [round((b.min.x + b.max.x) / 2, 2), round((b.min.y + b.max.y) / 2, 2), round((b.min.z + b.max.z) / 2, 2),
                 round((b.max.x - b.min.x) / 2, 2), round((b.max.y - b.min.y) / 2, 2), round((b.max.z - b.min.z) / 2, 2)]
OUT["path"] = mesh_path
'''


def shrink(path, size=2048):
    """The map at most `size` pixels wide, in a 2k folder beside it: the scans' 4K JPEGs decoded in the
    editor ran this 16 GB PC out of memory (2026-10-23), so the editor only ever sees 2K files."""
    from PIL import Image
    out = os.path.join(os.path.dirname(path), "2k", os.path.basename(path))
    if not os.path.exists(out):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with Image.open(path) as im:
            im.thumbnail((size, size), Image.LANCZOS)
            im.save(out, quality=92)
    return out.replace("\\", "/")


def files(pack, scan, fbx):
    folder = os.path.join(SRC, pack, scan) if scan else os.path.join(SRC, pack)
    names = os.listdir(folder)
    if fbx is None:
        fbxs = sorted(f for f in names if f.lower().endswith(".fbx"))
        fbx = next((f for f in fbxs if "lod0" in f.lower() and "varb" not in f.lower()), None) or fbxs[0]

    def find(*words):
        f = next((f for f in sorted(names) if f.lower().endswith(".jpg") and
                  any(f.lower().endswith("_" + w + ".jpg") for w in words)), None)
        return shrink(os.path.join(folder, f)) if f else ""
    maps = {"BaseColor": find("basecolor", "albedo"), "Normal": find("normal"), "Roughness": find("roughness"),
            "AO": find("ao")}
    return os.path.join(folder, fbx).replace("\\", "/"), maps


def free_gb():
    """Free physical memory (Windows)."""
    import ctypes

    class Status(ctypes.Structure):
        _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong)] + \
                   [(n, ctypes.c_ulonglong) for n in ("total", "avail", "pagetotal", "pageavail", "virtual", "virtualavail", "ext")]
    s = Status()
    s.length = ctypes.sizeof(Status)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(s))
    return s.avail / 2 ** 30


def main(only=None):
    kit_map = json.load(open(KITMAP, encoding="utf-8")) if os.path.exists(KITMAP) else {"meshes": {}, "pieces": []}
    print("master", pyrun.run(MASTER, 300))
    for name, (pack, scan, fbx) in PROPS.items():
        if only and name not in only:
            continue
        if free_gb() < 1.5:  # stop before the PC runs out (a 4K import froze it, 2026-10-23)
            print("stopping: only %.1f GB of memory free" % free_gb())
            break
        path, maps = files(pack, scan, fbx)
        r = pyrun.run("NAME = %r\nFBX = %r\nMAPS = %r\n" % (name, path, maps) + IMPORT, 900)
        print(name, r)
        if "bounds" in r:
            kit_map["meshes"][name] = {"path": r["path"], "bounds": r["bounds"]}
    kit_map["pieces"] = [{"match": m, "mesh": mesh, "fit": fit} for m, mesh, fit in RULES]
    with open(KITMAP, "w", encoding="utf-8") as f:
        json.dump(kit_map, f, indent=1)
        f.write("\n")


if __name__ == "__main__":
    import sys
    main(set(sys.argv[1:]) or None)
