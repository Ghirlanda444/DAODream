"""Play-in-editor helpers on top of ue.py.

python pie.py start | stop | cmd "<console>" | props <obj> [names,..] | shot <file.png> | log <pattern> [n]
"""
import base64, json, sys, time
import ue

EA = "EditorToolset.EditorAppToolset"
SL = "SlateInspectorToolset.SlateInspectorToolset"
OT = "editor_toolset.toolsets.object.ObjectTools"
LG = "EditorToolset.LogsToolset"
W = "/Game/Cousland/Maps/UEDPIE_0_L_CastleNight.L_CastleNight:PersistentLevel."


PLAY = {"refPath": "/Script/UnrealEd.Default__LevelEditorPlaySettings"}


def start(simulate=False):
    """Play or Simulate, always with the game's sound off: the voices and music woke the user's
    household (2026-10-23), and the user asked for no sound in game at all. The setting is also saved
    off in the editor's per-user config (EnableGameSound=False)."""
    ue.call(OT, "set_properties", {"instance": PLAY, "values": json.dumps({"EnableGameSound": False})})
    return ue.call(EA, "StartPIE", {"options": {"bSimulate": simulate, "playMode": "PlayMode_InViewPort"}})


def stop():
    return ue.call(EA, "StopPIE", {})


_BOX = []


def cmd(text):
    import pyrun
    for attempt in range(2):
        if not _BOX:
            _BOX.append(pyrun.cmd_box())
        ue.call(SL, "Click", {"ref": _BOX[0]})
        r = ue.call(SL, "Type", {"ref": _BOX[0], "text": text, "submit": True})
        if '"returnValue":true' in r:
            return r
        _BOX.clear()
    return r


def props(obj, names=None):
    if not obj.startswith("/"):
        obj = W + obj
    a = {"instance": {"refPath": obj}}
    if names:
        a["properties"] = names
    return ue.call(OT, "get_properties", a)


def shot(path):
    r = ue.call(EA, "CaptureEditorImage", {})
    d = json.loads(r)["returnValue"]
    open(path, "wb").write(base64.b64decode(d["data"]))
    return path


def log(pattern, n=40):
    return ue.call(LG, "GetLogEntries", {"category": "", "pattern": pattern, "maxEntries": n})


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    ue.init()
    c, a = sys.argv[1], sys.argv[2:]
    if c == "start":
        print(start(bool(a and a[0] == "sim")))
    elif c == "stop":
        print(stop())
    elif c == "cmd":
        print(cmd(a[0]))
    elif c == "props":
        print(props(a[0], a[1].split(",") if len(a) > 1 else None))
    elif c == "shot":
        print(shot(a[0]))
    elif c == "log":
        print(log(a[0], int(a[1]) if len(a) > 1 else 40))


def main_window():
    """The Slate ref of the editor's main window (refs change when the editor restarts)."""
    import re
    t = json.loads(ue.call(SL, "Snapshot", {"ref": "", "maxDepth": 1}))["returnValue"]
    m = re.search(r'window "[^"]*Unreal Editor" .*\[ref=(\w+)\]', t)
    return m.group(1) if m else "w1"


def dlg():
    """Visible dialogue: (lines, [(label, ref)])."""
    import re
    t = json.loads(ue.call(SL, "Snapshot", {"ref": main_window(), "maxDepth": 80}))["returnValue"]
    lines, opts = [], []
    for l in t.split("\n"):
        m = re.search(r'(text|button) "(.*)" \[pos=(\d+),(\d+) .*\[ref=(\w+)\]', l)
        if not m or m.group(3) == "0":
            continue
        y = int(m.group(4))
        if 700 < y < 1000 and int(m.group(3)) < 4200:
            if m.group(1) == "button" and re.match(r"\d+\. ", m.group(2)):
                opts.append((m.group(2), m.group(5)))
            elif m.group(1) == "text":
                lines.append(m.group(2))
    return lines, opts


def choose(n=1):
    lines, opts = dlg()
    if not opts:
        return lines, None
    ue.call(SL, "Click", {"ref": opts[n - 1][1]})
    return lines, opts[n - 1][0]


def close_popups():
    """Close the floating Message Log / Diagnostics windows that cover the game view."""
    import re
    t = json.loads(ue.call(SL, "Snapshot", {"ref": "", "maxDepth": 60}))["returnValue"]
    closed = []
    cur = None
    pending_no = False
    for l in t.split("\n"):
        m = re.match(r'window "(.*?)"', l.strip())
        if m:
            cur = m.group(1)
            continue
        if "erano aperti quando l'editor si" in l:  # "reopen asset editors?" after a crash: No
            pending_no = True
        if 'button "No"' in l and locals().get("pending_no"):
            m = re.search(r"\[ref=(\w+)\]", l)
            if m:
                ue.call(SL, "Click", {"ref": m.group(1)}); closed.append("reopen prompt"); pending_no = False
        if cur and cur in ("Registro dei messaggi", "Diagnostica editor"):
            m = re.search(r'button "Chiudi" .*\[ref=(\w+)\]', l)
            if m:
                ue.call(SL, "Click", {"ref": m.group(1)})
                closed.append(cur)
                cur = None
    return closed
