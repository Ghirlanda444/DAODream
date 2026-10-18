"""python wshot.py out.png [window title substring]: full-res screenshot of one editor window."""
import base64, json, re, sys
import ue
SL = "SlateInspectorToolset.SlateInspectorToolset"
def shot(path, title="MHC_"):
    t = json.loads(ue.call(SL, "Snapshot", {"ref": "", "maxDepth": 1}))["returnValue"]
    ref = next(re.search(r"\[ref=(\w+)\]", l).group(1) for l in t.split("\n") if l.startswith("window") and (title in l))
    r = json.loads(ue.call(SL, "Screenshot", {"ref": ref}))["returnValue"]
    d = r if isinstance(r, str) else (r.get("data") or r.get("image", {}).get("data"))
    if isinstance(r, dict) and not d:
        raise RuntimeError(str(r)[:300])
    open(path, "wb").write(base64.b64decode(d))
    return path
if __name__ == "__main__":
    ue.init()
    print(shot(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "MHC_"))
