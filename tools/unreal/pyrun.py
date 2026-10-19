"""Run Python inside the Unreal editor through its console (`py <file>`) and return what the
script puts in OUT. python pyrun.py script.py [timeout_s]"""
import json, os, re, sys, time, uuid
import ue

sys.stdout.reconfigure(encoding="utf-8")
STAGE = "E:/DAODream/Unreal/Cousland/Saved/claude"
SL = "SlateInspectorToolset.SlateInspectorToolset"
WRAP = '''import json, traceback, unreal
OUT = {}
try:
%s
except Exception as e:
    OUT["error"] = traceback.format_exc()
with open(%r, "w", encoding="utf-8") as f:
    json.dump(OUT, f, default=str, indent=1)
'''


def restore_editor():
    """Un-minimise the editor: a minimised editor shows no Slate windows, so the console box is not found."""
    import ctypes, subprocess
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "(Get-Process UnrealEditor -ErrorAction SilentlyContinue | Select-Object -First 1).MainWindowHandle"],
                         capture_output=True, text=True).stdout.strip()
    if out.isdigit() and int(out):
        ctypes.windll.user32.ShowWindow(ctypes.c_void_p(int(out)), 9)
        time.sleep(2)


def cmd_box():
    for attempt in range(2):
        t = json.loads(ue.call(SL, "Snapshot", {"ref": "", "maxDepth": 60}))["returnValue"]
        lines = t.split("\n")
        for i, l in enumerate(lines):
            if 'text "Cmd"' in l or 'text "Python"' in l:
                for l2 in lines[i:i + 6]:
                    m = re.search(r"textbox .*\[ref=(\w+)\]", l2)
                    if m:
                        return m.group(1)
        restore_editor()   # a minimised editor hides the console
    raise RuntimeError("console box not found")


def run(body, timeout=600):
    ue.init()
    tag = uuid.uuid4().hex[:8]
    out = "%s/py_out_%s.json" % (STAGE, tag)
    src = "%s/py_run_%s.py" % (STAGE, tag)
    indented = "\n".join("    " + l for l in body.splitlines())
    open(src, "w", encoding="utf-8").write(WRAP % (indented, out))
    import pie
    ref = None
    for attempt in range(8):
        try:
            pie.close_popups()
            ref = cmd_box()
            break
        except Exception:
            time.sleep(5)
    if ref is None:
        ref = cmd_box()
    ue.call(SL, "Click", {"ref": ref})
    r = ue.call(SL, "Type", {"ref": ref, "text": 'py "%s"' % src, "submit": True})
    if '"returnValue":true' not in r:
        print("typing failed:", r[:200], file=sys.stderr)
    t0 = time.time()
    while time.time() - t0 < timeout:
        if os.path.exists(out):
            time.sleep(0.3)
            return json.load(open(out, encoding="utf-8"))
        time.sleep(1)
    return {"error": "no result after %ds" % timeout}


if __name__ == "__main__":
    body = open(sys.argv[1], encoding="utf-8").read()
    r = run(body, float(sys.argv[2]) if len(sys.argv) > 2 else 600)
    print(json.dumps(r, indent=1, ensure_ascii=False)[:20000])
