"""python flame_build.py: build the castle's fire effects, NS_Fire{Small,Medium,Large,Candle,Wall} in /Game/Cousland/Fixtures,
through the editor's Niagara tools (unreal-mcp). Each is two emitters from Epic's Fountain template: flame
tongues (M_Flame sprites rising and fading) and embers (M_Spark) drifting up on curl noise. Run after
fixtures_build.body.py, which makes the materials."""
import json
import sys
import time

import ue

NS = "NiagaraToolsets.NiagaraToolset_System"
DIR = "/Game/Cousland/Fixtures"
FOUNTAIN = {"refPath": "/Niagara/DefaultAssets/Templates/Emitters/Fountain.Fountain"}
CURL = {"refPath": "/Niagara/Modules/Update/Forces/CurlNoiseForce.CurlNoiseForce"}
# name: (flame height scale, spread radius cm, spawn scale, brightness); wall fires spread wide and low
# over a burning wall, candle flames are tiny and need to be brighter to read
SIZES = {"NS_FireSmall": (1.4, 6.0, 1.2, 1.0), "NS_FireMedium": (2.0, 16.0, 2.6, 1.0), "NS_FireLarge": (2.6, 26.0, 4.0, 1.0),
         "NS_FireCandle": (0.22, 0.4, 0.35, 4.0), "NS_FireWall": (1.3, 38.0, 3.0, 1.0)}


def fl(v):
    return {"struct": {"refPath": "/Script/Niagara.NiagaraFloat"}, "value": {"value": v}}


def vec(x, y, z):
    return {"struct": {"refPath": "/Script/CoreUObject.Vector3f"}, "value": {"x": x, "y": y, "z": z}}


def colour(r, g, b, a):
    return {"struct": {"refPath": "/Script/CoreUObject.LinearColor"}, "value": {"r": r, "g": g, "b": b, "a": a}}


def check(r):
    if r.startswith("TOOL ERROR") or r.startswith("RPC ERROR"):
        raise RuntimeError(r[:800])
    return r


def settled(tool, args):
    """Call a Niagara tool that refuses to run while the system compiles: retry until it is done."""
    for _ in range(60):
        r = ue.call(NS, tool, args)
        if "OnSystemCompiled" not in r:
            return check(r)
        time.sleep(2)
    raise RuntimeError(r[:800])


def issues(S):
    return json.loads(settled("GetStackIssues", {"system": S}))["returnValue"]


def build(name, height, spread, rate, bright):
    path = "%s/%s.%s" % (DIR, name, name)
    S = {"refPath": path}
    if not json.loads(ue.call("editor_toolset.toolsets.asset.AssetTools", "exists", {"path": "%s/%s" % (DIR, name)}))["returnValue"]:
        check(ue.call(NS, "CreateNiagaraSystem", {"assetName": name, "assetPath": DIR,
                                                  "templateSystem": {"refPath": "/Niagara/DefaultAssets/DefaultSystem.DefaultSystem"}}))
    summary = json.loads(ue.call(NS, "GetSystemSummary", {"system": S}))["returnValue"]
    have = [e["emitterName"] for e in summary["emitters"]]

    def ref(em, script="", module="", renderer=-1, stack=()):
        return {"system": S, "emitterName": em, "scriptName": script, "moduleName": module, "rendererIndex": renderer,
                "inputNameStack": list(stack)}

    for em in have:
        if em not in ("Flame", "Embers"):
            check(ue.call(NS, "RemoveEmitter", {"emitterToRemove": ref(em)}))
    for em in ("Flame", "Embers"):
        if em not in have:
            check(ue.call(NS, "AddEmitter", {"system": S, "templateEmitter": FOUNTAIN, "emitterName": em}))

    def put(em, script, module, stack, data):
        check(ue.call(NS, "SetStackInputData", {"stackInputRef": ref(em, script, module, -1, stack), "inputData": data}))

    E, PS, PU = "EmitterUpdateScript", "ParticleSpawnScript", "ParticleUpdateScript"
    # Flame tongues: short-lived, rising on buoyancy, fading out (the template's alpha curve).
    put("Flame", E, "SpawnRate", ["SpawnRate"], fl(28.0 * rate))
    put("Flame", PS, "InitializeParticle", ["Lifetime Min"], fl(0.45))
    put("Flame", PS, "InitializeParticle", ["Lifetime Max"], fl(0.8))
    put("Flame", PS, "InitializeParticle", ["Color"], colour(bright, 0.92 * bright, 0.82 * bright, 1.0))
    put("Flame", PS, "InitializeParticle", ["Uniform Sprite Size Min"], fl(16.0 * height))
    put("Flame", PS, "InitializeParticle", ["Uniform Sprite Size Max"], fl(26.0 * height))
    put("Flame", PS, "ShapeLocation", ["Sphere Radius"], fl(spread))
    put("Flame", PS, "AddVelocity", ["Velocity Speed", "Minimum"], fl(25.0 * height))
    put("Flame", PS, "AddVelocity", ["Velocity Speed", "Maximum"], fl(45.0 * height))
    put("Flame", PU, "GravityForce", ["Gravity"], vec(0.0, 0.0, 90.0 * height))
    put("Flame", PU, "Drag", ["Drag"], fl(2.0))
    # Embers: a few bright specks drifting up and wandering.
    put("Embers", E, "SpawnRate", ["SpawnRate"], fl(3.0 * rate))
    put("Embers", PS, "InitializeParticle", ["Lifetime Min"], fl(1.2))
    put("Embers", PS, "InitializeParticle", ["Lifetime Max"], fl(2.4))
    put("Embers", PS, "InitializeParticle", ["Color"], colour(1.0, 0.8, 0.6, 1.0))
    put("Embers", PS, "InitializeParticle", ["Uniform Sprite Size Min"], fl(0.8))
    put("Embers", PS, "InitializeParticle", ["Uniform Sprite Size Max"], fl(1.8))
    put("Embers", PS, "ShapeLocation", ["Sphere Radius"], fl(spread * 1.3))
    put("Embers", PS, "AddVelocity", ["Velocity Speed", "Minimum"], fl(50.0 * height))
    put("Embers", PS, "AddVelocity", ["Velocity Speed", "Maximum"], fl(110.0 * height))
    put("Embers", PU, "GravityForce", ["Gravity"], vec(0.0, 0.0, 20.0))
    put("Embers", PU, "Drag", ["Drag"], fl(0.8))
    topo = json.loads(ue.call(NS, "GetEmitterTopology", {"emitterRef": ref("Embers")}))["returnValue"]
    if not any(m["moduleName"].startswith("CurlNoiseForce") for m in topo["particleUpdateScript"]["modules"]):
        check(ue.call(NS, "AddModule", {"moduleLocationRef": ref("Embers", PU), "moduleAsset": CURL}))
    for em, mat in (("Flame", "M_Flame"), ("Embers", "M_Spark")):
        check(ue.call(NS, "SetRendererData", {"renderer": ref(em, renderer=0), "rendererData": {"propertyValues": json.dumps(
            {"Material": {"refPath": "%s/%s.%s" % (DIR, mat, mat)}, "bCastShadows": False})}}))
    # Apply the stack's own fixes (an added force module goes before SolveForcesAndVelocity).
    for _ in range(10):  # one fix can clear or renumber the others: re-read after each
        fixable = [i for i in issues(S)["issues"] if i["severity"] == "Error" and i.get("fixes")]
        if not fixable:
            break
        try:
            settled("ApplyStackIssueFix", {"system": S, "issueId": fixable[0]["issueId"], "fixId": fixable[0]["fixes"][0]["fixId"]})
        except RuntimeError:  # its id went stale while the system recompiled: read the issues again
            time.sleep(2)
    check(ue.call("editor_toolset.toolsets.asset.AssetTools", "save_assets", {"asset_paths": ["%s/%s" % (DIR, name)]}))
    left = issues(S)
    return "%d errors, %d warnings" % (left["numErrors"], left["numWarnings"])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    ue.init()
    for name, args in SIZES.items():
        print(name, build(name, *args))
