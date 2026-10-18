"""Tiny HTTP client for the Unreal MCP server (localhost:8000).

usage:
  python ue.py list
  python ue.py describe <Toolset>
  python ue.py call <Toolset> <tool> '<json args>'   (or @file.json)
"""
import json, sys, urllib.request

URL = "http://localhost:8000/mcp"
_sid = None


def rpc(method, params, timeout=600):
    global _sid
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if _sid:
        h["Mcp-Session-Id"] = _sid
    req = urllib.request.Request(URL, body, h)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        _sid = r.headers.get("Mcp-Session-Id") or _sid
        raw = r.read().decode("utf-8", "replace")
    if raw.lstrip().startswith("data:") or "\ndata:" in raw:
        raw = "\n".join(l[5:] for l in raw.splitlines() if l.startswith("data:"))
    return json.loads(raw)


def init():
    rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                       "clientInfo": {"name": "claude-http", "version": "0"}})


def tool(name, args):
    res = rpc("tools/call", {"name": name, "arguments": args})
    if "error" in res:
        return "RPC ERROR: " + json.dumps(res["error"])
    out = []
    for c in res["result"].get("content", []):
        out.append(c.get("text", json.dumps(c)[:2000]))
    if res["result"].get("isError"):
        out.insert(0, "TOOL ERROR:")
    return "\n".join(out)


def call(ts, tn, args):
    return tool("call_tool", {"toolset_name": ts, "tool_name": tn, "arguments": args})


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    init()
    cmd = sys.argv[1]
    if cmd == "list":
        print(tool("list_toolsets", {}))
    elif cmd == "describe":
        print(tool("describe_toolset", {"toolset_name": sys.argv[2]}))
    elif cmd == "call":
        a = sys.argv[4] if len(sys.argv) > 4 else "{}"
        if a.startswith("@"):
            a = open(a[1:], encoding="utf-8").read()
        print(call(sys.argv[2], sys.argv[3], json.loads(a)))
