"""Make MetaHumans from recipes, one fresh editor session each:
create (preset mix, grooms, skin, sculpt) -> Creator: colours, body -> face rig -> textures -> picture -> assemble.

python mh_make.py recipes.json Name [Name ...]
A recipe: {"name", "mix": {preset: weight}, "grooms": {slot: groom}, "skin": {"idx", "u", "v"},
           "colours": {slot: {param: value}}, "body": {measure: cm}, "sculpt": {landmark: [dx,dy,dz]},
           "passes": n, "quality": "MEDIUM"|"LOW"}
"existing": true builds a character already in /Game/MetaHumans/<name> (e.g. a hand-fitted face):
no create and no look step, only face rig, textures, assembly and strands.
"""
import json, os, subprocess, sys, time, urllib.request
import ue, pyrun

sys.stdout.reconfigure(encoding="utf-8")
LOG = "E:/DAODream/Unreal/Cousland/Saved/Logs/Cousland.log"
EDITOR = r"E:\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe"
PROJECT = r"E:\DAODream\Unreal\Cousland\Cousland.uproject"
G = "/MetaHumanCharacter/Optional/Grooms/Bindings/"
FOLDER = {"Hair": "Hair", "Beard": "Beards", "Mustache": "Mustaches", "Eyebrows": "Eyebrows"}


def log_lines():
    with open(LOG, encoding="utf-8", errors="replace") as f:
        return f.readlines()


def editor_running():
    out = subprocess.run(["tasklist"], capture_output=True, text=True).stdout
    return "UnrealEditor.exe" in out


def mcp_up():
    try:
        urllib.request.urlopen("http://localhost:8000/mcp", timeout=3)
    except urllib.error.HTTPError:
        return True
    except Exception:
        return False
    return True


def restart():
    if editor_running():
        try:
            pyrun.run("unreal.SystemLibrary.quit_editor()\nOUT['q'] = 1", 20)
        except Exception:
            pass
        for _ in range(30):
            if not editor_running():
                break
            time.sleep(4)
    if editor_running():  # stuck behind a dialog: everything was saved before this point
        subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name UnrealEditor -Force -ErrorAction SilentlyContinue"])
        time.sleep(8)
    rd = "E:/DAODream/Unreal/Cousland/Saved/Autosaves/PackageRestoreData.json"
    if os.path.exists(rd):
        os.replace(rd, rd + ".skipped")
    subprocess.Popen([EDITOR, PROJECT])
    for _ in range(120):
        time.sleep(5)
        if mcp_up():
            break
    for _ in range(30):
        try:
            if "ok" in pyrun.run("OUT['ok'] = 1", 30):
                break
        except Exception:
            pass
        time.sleep(6)
    ue.init()
    ue.call("editor_toolset.toolsets.object.ObjectTools", "set_properties", {
        "instance": {"refPath": "/Script/UnrealEd.Default__EditorPerformanceSettings"},
        "values": json.dumps({"bThrottleCPUWhenNotForeground": False})})


def wait_log(start, needles, fail, timeout):
    t0 = time.time()
    while time.time() - t0 < timeout:
        new = log_lines()[start:]
        for l in new:
            if any(f in l for f in fail):
                return "FAIL: " + l.strip()[:200]
        if all(any(n in l for l in new) for n in needles):
            return "ok"
        time.sleep(5)
    return "timeout"


CREATE = r'''
R = __R__
eal = unreal.EditorAssetLibrary
sub = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
A = "/Game/MetaHumans/%s/MHC_%s" % (R["name"], R["name"])
if eal.does_asset_exist(A):
    if not R.get("replace"):
        raise RuntimeError("exists: " + A)
    for d in ("/Game/MetaHumans/" + R["name"], "/Game/MetaHumans/MHC_" + R["name"]):
        if eal.does_directory_exist(d):
            OUT.setdefault("deleted", []).append((d, eal.delete_directory(d)))
base = next(iter(R["mix"]))
eal.duplicate_asset("/MetaHumanCharacter/Optional/Presets/" + base, A)
c = unreal.load_asset(A)
coll = c.internal_collection
inst = coll.default_instance
for slot, name in R.get("grooms", {}).items():
    path = "__G__" + {"Hair": "Hair", "Beard": "Beards", "Mustache": "Mustaches", "Eyebrows": "Eyebrows"}[slot] + "/WI_" + name
    if not name:  # remove the preset's groom (clean-shaven)
        try:
            inst.set_single_slot_selection(slot, unreal.MetaHumanPaletteItemKey())
        except Exception as e:
            OUT.setdefault("unset_failed", []).append(slot + ": " + str(e)[:80])
        continue
    wi = unreal.load_asset(path + ".WI_" + name)
    if wi is None:
        raise RuntimeError("no groom " + name)
    inst.set_single_slot_selection(slot, coll.try_add_item_from_wardrobe_item(slot, wi))
co = {}
for n in R["mix"]:
    p = unreal.load_asset("/MetaHumanCharacter/Optional/Presets/%s.%s" % (n, n))
    sub.try_add_object_to_edit(p)
    try:
        co[n] = list(sub.get_face_model_coefficients(p))
    finally:
        sub.remove_object_to_edit(p)
sub.try_add_object_to_edit(c)
try:
    tot = sum(R["mix"].values())
    if len(R["mix"]) > 1:
        sub.set_face_model_coefficients(c, [sum(co[n][i] * w for n, w in R["mix"].items()) / tot for i in range(len(co[base]))])
        sub.commit_face_state(c)
    for _ in range(R.get("passes", 1) if R.get("sculpt") else 0):
        sub.translate_face_landmarks(character=c, landmark_indices=[int(k) for k in R["sculpt"]], deltas=[unreal.Vector(*v) for v in R["sculpt"].values()])
        sub.commit_face_state(character=c)
    if R.get("skin"):
        s = c.get_editor_property("skin_settings"); sk = s.skin
        sk.face_texture_index = R["skin"].get("idx", sk.face_texture_index)
        sk.u = R["skin"].get("u", sk.u); sk.v = R["skin"].get("v", sk.v)
        s.skin = sk
        sub.commit_skin_settings(c, s)
    if R.get("eyes_from"):
        src = unreal.load_asset("/MetaHumanCharacter/Optional/Presets/%s.%s" % (R["eyes_from"], R["eyes_from"]))
        sub.commit_eyes_settings(c, src.get_editor_property("eyes_settings"))
finally:
    sub.remove_object_to_edit(c)
OUT["saved"] = eal.save_asset(A, only_if_is_dirty=False)
'''.replace("__G__", G)

OPEN = r'''
R = __R__
aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
c = unreal.load_asset("/Game/MetaHumans/%s/MHC_%s" % (R["name"], R["name"]))
vs = c.get_editor_property("viewport_settings"); vs.camera_frame = unreal.MetaHumanCharacterCameraFrame.FACE
c.set_editor_property("viewport_settings", vs)
try:
    aes.open_editor_for_assets(assets=[c])
except Exception as e:
    OUT["logged"] = str(e)[:100]
OUT["editing"] = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem).is_object_added_for_editing(c)
'''

HERE = os.path.dirname(os.path.abspath(__file__))
LOOK = open(os.path.join(HERE, "mh_look.body.py"), encoding="utf-8").read()

RIG = r'''
sub = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
c = unreal.load_asset("__A__")
p = unreal.MetaHumanCharacterAutoRiggingRequestParams() if __RIG__ else unreal.MetaHumanCharacterTextureRequestParams()
p.blocking = False; p.report_progress = True
if __RIG__:
    p.rig_type = unreal.MetaHumanRigType.JOINTS_ONLY
    sub.request_auto_rigging(c, p)
else:
    sub.request_texture_sources(c, p)
OUT["ok"] = 1
'''

BUILD = r'''
import time
sub = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
N = __N__; Q = __Q__
A = "/Game/MetaHumans/%s/MHC_%s" % (N, N)
c = unreal.load_asset(A)
unreal.EditorAssetLibrary.save_asset(A, only_if_is_dirty=False)
bp = unreal.MetaHumanCharacterEditorBuildParameters()
bp.pipeline_type = unreal.MetaHumanDefaultPipelineType.OPTIMIZED
bp.pipeline_quality = getattr(unreal.MetaHumanQualityLevel, Q)
bp.absolute_build_path = "/Game/MetaHumans"
bp.common_folder_path = "/Game/MetaHumans/Common"
t = time.time()
try:
    sub.build_meta_human(c, bp)
except Exception as e:
    OUT["build_logged"] = str(e)[:300]
OUT["secs"] = round(time.time() - t, 1)
pk = [p for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages() if p.get_name().startswith("/Game/MetaHumans")]
OUT["saved"] = unreal.EditorLoadingAndSavingUtils.save_packages(pk, only_dirty=False)
OUT["bp"] = unreal.EditorAssetLibrary.does_asset_exist("/Game/MetaHumans/MHC_%s/BP_MHC_%s" % (N, N))
unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(c)
'''


def make(R):
    name = R["name"]
    A = "/Game/MetaHumans/%s/MHC_%s" % (name, name)
    print("==", name, flush=True)
    restart()
    if not R.get("existing"):
        r = pyrun.run(CREATE.replace("__R__", repr(R)), 900)
        print("  create", r, flush=True)
        if "error" in r:
            return False
    r = pyrun.run(OPEN.replace("__R__", repr(R)), 300)
    print("  open", r, flush=True)
    time.sleep(12)
    if not R.get("existing"):
        look = {"asset": A, "params": R.get("colours", {}), "body": R.get("body", {})}
        body = LOOK.replace("__LOOK__", repr(look)) + '\nsub.on_edit_preview_collection(c)\nOUT["saved"] = unreal.EditorAssetLibrary.save_asset(LOOK["asset"], only_if_is_dirty=False)\n'
        r = pyrun.run(body, 300)
        print("  look", "error" not in r, r.get("error", "")[:300], flush=True)
    time.sleep(8)
    try:
        import wshot
        wshot.shot("mh_%s.png" % name, "window \"MHC_%s\"" % name)
    except Exception as e:
        print("  shot failed", e)
    if R.get("preview_only"):
        return True
    for rig in (True, False):
        start = len(log_lines())
        pyrun.run(RIG.replace("__A__", A).replace("__RIG__", repr(rig)), 120)
        if rig:
            res = wait_log(start, ["Auto-Rigging terminato"], ["non riuscito", "PinGrant", "LaunchAccountPortal", "Login failed"], 600)
        else:
            res = wait_log(start, ["texture della faccia di origine completato", "texture del corpo di origine completato"],
                           ["LogMetaHumanCharacterEditor: Error"], 600)
        print("  rig" if rig else "  textures", res, flush=True)
        if res != "ok":
            return False
    r = pyrun.run(BUILD.replace("__N__", repr(name)).replace("__Q__", repr(R.get("quality", "MEDIUM"))), 1500)
    print("  build", r, flush=True)
    if r.get("bp"):  # the build's groom copies are cards only: put the strand grooms back (and thicken them)
        body = "NAMES = [%r]\nTHICKEN = {%r: %r}\n" % (name, name, R.get("thicken") or {}) + \
            open(os.path.join(HERE, "metahuman_strands.body.py"), encoding="utf-8").read()
        print("  strands", str(pyrun.run(body, 900).get("strands"))[:300], flush=True)
    return bool(r.get("bp"))


if __name__ == "__main__":
    recipes = {r["name"]: r for r in json.load(open(sys.argv[1], encoding="utf-8"))}
    done = []
    fails = 0
    for n in sys.argv[2:]:
        try:
            ok = make(recipes[n])
        except Exception as e:
            print("  EXCEPTION", repr(e)[:300], flush=True)
            ok = False
        done.append((n, ok))
        print("RESULT", n, ok, flush=True)
        fails = 0 if ok else fails + 1
        if fails >= 2:
            break
    print("SUMMARY", done)
