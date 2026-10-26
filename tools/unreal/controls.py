"""python controls.py [assets|setup|graphs|input|save|all]: Dragon Age: Origins' PC controls (docs/COMBAT.md,
"Controls"; the original's own bindings: Documents/BioWare/Dragon Age/Settings/KeyBindings.ini). Play/Simulate
stopped; pause.py must have run.

Keys: W/S run, Q/E strafe (IMC_Default's IA_Move: A and D become Q and E), A/D turn the camera (IA_TurnCamera),
/ swaps weapon sets (IA_SwitchWeapon, was Q), E no longer talks (the original talks by clicking). The mouse: the
cursor shows; holding the right button turns the camera (IA_MouseLook chorded on IA_CameraHold); a right click
(IA_Command, a tap) gives an order at the cursor; the left button selects (IA_Select) and no longer attacks (F
still does: a shortcut the original lacks).

BP_PlotManager: InitControls (from EventoBeginPlay after InitCombat, and KeepCursor whenever the cursor is hidden
outside a conversation: the dialogue hides it) shows the cursor, game and UI input.
TurnCamera turns the view at 90 degrees a second. Command takes what is under the cursor (GetHitResultUnderCursor
by Visibility; a creature within a metre of the point counts as clicked: PickNpcNear asks each, ClickOffer,
not hidden or dead, and PickOffer keeps the nearest): a hostile -> HeroTarget (the
hero walks into reach and keeps attacking it, HeroAttackStep; the attacks and talents prefer it, PreferTarget); a
creature not in the party -> HeroUse (walk up, then its Interact: talk); a door -> its TryUse (a cast that fails ends its function, so each
lives alone: PickClicked, PickDoorOf; UseRoute); else the ground ->
MoveGoal (HeroMoveStep). HeroTick runs the order each tick; HeroWalk asks the nav mesh for a path every 0.4 s and
walks towards its next point. Moving with the keys drops the order (CancelOrders on IA_Move, which no longer
consumes its input so the hero still gets it).
"""
import os
import sys

import combat_rules as cr

import ue

PM, NPC = cr.PM, cr.NPC
NPC_CLASS, ACTOR = cr.NPC_CLASS, cr.ACTOR
F, B, VEC = "float", "bool", "vector"

VARIABLES = {
    PM: [("HeroTarget", NPC_CLASS), ("HeroUse", ACTOR), ("MoveGoal", VEC), ("bMoving", B),
         ("HeroPath", VEC, "ARRAY"), ("PathTimer", F), ("NextPoint", VEC), ("PickNpc", NPC_CLASS), ("PickDist", F),
         ("PickDoor", "/Game/Cousland/Areas/BP_Door.BP_Door_C")],
}
FUNCTIONS = {
    PM: {"InitControls": [], "TurnCamera": [("Value", F)], "Command": [],
         "CommandAt": [("Where", VEC), ("What", ACTOR)], "PickClicked": [("What", ACTOR)],
         "CommandRoute": [("Where", VEC), ("What", ACTOR)], "CommandNpc": [("Where", VEC)],
         "CommandThing": [("Where", VEC), ("What", ACTOR)], "PickNpcNear": [("Where", VEC)],
         "PickOffer": [("Npc", NPC_CLASS), ("Where", VEC)], "CancelOrders": [], "HeroTick": [("Dt", F)],
         "HeroOrderStep": [("Dt", F)], "HeroAttackStep": [("Dt", F)], "HeroStrike": [], "HeroUseStep": [("Dt", F)],
         "HeroUseNow": [], "UseRoute": [], "PickDoorOf": [("What", ACTOR)], "KeepCursor": [], "HeroMoveStep": [("Dt", F)], "HeroWalk": [("Goal", VEC), ("Dt", F)], "HeroRepath": [("Goal", VEC), ("Dt", F)],
         "HeroNext": [("Goal", VEC)], "PreferTarget": [("Reach", F)], "HeroReach": []},
    NPC: {"ClickOffer": [("InMgr", cr.PM + "_C"), ("Where", VEC)]},
}
GRAPHS = [
    (NPC, ["ClickOffer"]),
    (PM, ["InitControls", "KeepCursor", "TurnCamera", "PickDoorOf", "PickOffer", "PickNpcNear", "CancelOrders", "CommandThing", "CommandNpc",
          "PickClicked", "CommandRoute", "CommandAt", "Command", "PreferTarget", "HeroNext", "HeroRepath", "HeroWalk", "HeroReach", "HeroStrike",
          "HeroAttackStep", "UseRoute", "HeroUseNow", "HeroUseStep", "HeroMoveStep", "HeroOrderStep", "HeroTick", "MeleeAttack",
          "BowAttack", "FindTarget"]),
]
NEW_ACTIONS = {  # name: (value type, [(key, negate)], trigger)
    "IA_TurnCamera": ("AXIS1D", [("A", True), ("D", False)], None),
    "IA_CameraHold": ("BOOLEAN", [("RightMouseButton", False)], None),
    "IA_Command": ("BOOLEAN", [("RightMouseButton", False)], "tap"),
    "IA_Select": ("BOOLEAN", [("LeftMouseButton", False)], None),
}


def assets():
    import pyrun
    print(pyrun.run('''
EAL = unreal.EditorAssetLibrary
factory = getattr(unreal, "InputAction_Factory", None) or getattr(unreal, "InputActionFactory")
def find(name):
    hits = [a.split(".")[0] for a in EAL.list_assets("/Game", recursive=True) if a.split(".")[0].endswith("/" + name)]
    return EAL.load_asset(hits[0]) if hits else None
def key(name):
    k = unreal.Key(); k.set_editor_property("key_name", name); return k
def mappings(imc):
    return list(imc.get_editor_property("default_key_mappings").get_editor_property("mappings"))
def put(imc, maps):
    d = imc.get_editor_property("default_key_mappings"); d.set_editor_property("mappings", maps)
    imc.set_editor_property("default_key_mappings", d)
done = []
# IMC_Default: A and D strafe no more, Q and E do
imc = find("IMC_Default")
maps = mappings(imc)
for m in maps:
    if m.action and m.action.get_name() == "IA_Move":
        k = str(m.key.get_editor_property("key_name"))
        if k in ("A", "D"):
            m.set_editor_property("key", key("Q" if k == "A" else "E")); done.append("move " + k)
put(imc, maps)
EAL.save_loaded_asset(imc, False)
# IMC_Dialogue: E no longer talks, / swaps weapons, the left button no longer attacks
dlg = find("IMC_Dialogue")
maps = [m for m in mappings(dlg) if not (m.action and (m.action.get_name(), str(m.key.get_editor_property("key_name"))) in
        (("IA_Interact", "E"), ("IA_Attack", "LeftMouseButton")))]
for m in maps:
    if m.action and m.action.get_name() == "IA_SwitchWeapon" and str(m.key.get_editor_property("key_name")) == "Q":
        m.set_editor_property("key", key("Slash")); done.append("swap on /")
have = {(m.action.get_name() if m.action else "", str(m.key.get_editor_property("key_name"))) for m in maps}
for name, (vt, keys, trig) in %r.items():
    path = "/Game/Cousland/Combat/" + name
    ia = EAL.load_asset(path) if EAL.does_asset_exist(path) else unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, "/Game/Cousland/Combat", unreal.InputAction, factory())
    ia.set_editor_property("value_type", getattr(unreal.InputActionValueType, vt))
    ia.set_editor_property("trigger_when_paused", True)
    if trig == "tap":
        t = unreal.InputTriggerTap(); t.set_editor_property("tap_release_time_threshold", 0.25)
        ia.set_editor_property("triggers", [t])
    EAL.save_loaded_asset(ia, False)
    for k, neg in keys:
        if (name, k) in have:
            continue
        m = unreal.EnhancedActionKeyMapping()
        m.set_editor_property("action", ia); m.set_editor_property("key", key(k))
        if neg:
            m.set_editor_property("modifiers", [unreal.InputModifierNegate()])
        maps.append(m); done.append(name + " " + k)
put(dlg, maps)
EAL.save_loaded_asset(dlg, False)
# the mouse look only while the right button is held
ml = find("IMC_MouseLook")
hold = EAL.load_asset("/Game/Cousland/Combat/IA_CameraHold")
maps = mappings(ml)
for m in maps:
    if m.action and m.action.get_name() == "IA_MouseLook":
        if not any(isinstance(t, unreal.InputTriggerChordAction) for t in m.get_editor_property("triggers")):
            c = unreal.InputTriggerChordAction(); c.set_editor_property("chord_action", hold)
            m.set_editor_property("triggers", list(m.get_editor_property("triggers")) + [c]); done.append("look chorded")
put(ml, maps)
EAL.save_loaded_asset(ml, False)
# the manager hears the movement keys too (to drop click orders)
mv = find("IA_Move")
mv.set_editor_property("consume_input", False)
EAL.save_loaded_asset(mv, False)
OUT["done"] = done
''' % (NEW_ACTIONS,), 300))


def setup():
    cr.setup(VARIABLES, FUNCTIONS, compile_all_after=False)
    cr.call("compile_blueprint", {"blueprint": {"refPath": PM}})


def graphs():
    for bp, names in GRAPHS:
        for fn in names:
            code = open(os.path.join(cr.HERE, "dsl", fn + ".dsl"), encoding="utf-8").read()
            r = cr.call("write_graph_dsl", {"graph": {"refPath": "%s:%s" % (bp, fn)}, "code": code})
            print(fn, str(r)[:300])
        cr.call("compile_blueprint", {"blueprint": {"refPath": bp}})


def _event(g, action, fn, pos, trigger="Started", value_pin=None):
    """An input event in BP_PlotManager's event graph calling fn on `trigger` (and its ActionValue into
    `value_pin`)."""
    if cr.call("find_nodes", {"graph": g, "title": action}):
        print(action, "already there")
        return
    types = cr.call("find_node_types", {"graph": g, "type_id_filter": action, "context_pins": []})
    ids = [t.get("type_id", t) if isinstance(t, dict) else t for t in types]
    ev = cr.call("create_node", {"graph": g, "type_id": next(i for i in ids if i.endswith(action)), "pos": pos})
    call = cr.call("create_node", {"graph": g, "type_id": "Funzionedichiamata|" + fn,
                                   "pos": {"x": pos["x"] + 420, "y": pos["y"]}})
    outs = {p["name"]: p["pin_id"] for p in cr.pins(ev)["output_pins"]}
    ins = {p["name"]: p["pin_id"] for p in cr.pins(call)["input_pins"]}
    cr.call("connect_pins", {"output_pin": outs[trigger], "input_pin": ins["execute"]})
    if value_pin:
        cr.call("connect_pins", {"output_pin": outs["ActionValue"], "input_pin": ins[value_pin]})
    print(action, trigger, "->", fn)


def _after(g, title, fn, args=()):
    """Calls fn after the node titled `title` in the event graph (its exec out), passing the event's pins named in
    args from the event the node hangs off."""
    calls = [n for n in cr.call("find_nodes", {"graph": g, "title": fn})]
    if calls:
        print(fn, "already called")
        return None
    node = cr.call("find_nodes", {"graph": g, "title": title})[0]
    pins = cr.pins(node)
    then = next(p for p in pins["output_pins"] if p["type_id"] == "Exec")
    call = cr.call("create_node", {"graph": g, "type_id": "Funzionedichiamata|" + fn, "pos": {"x": 2400, "y": 0}})
    ins = {p["name"]: p["pin_id"] for p in cr.pins(call)["input_pins"]}
    cr.call("connect_pins", {"output_pin": then["pin_id"], "input_pin": ins["execute"]})
    print(title, "->", fn)
    return ins


def input_events():
    g = {"refPath": PM + ":EventGraph"}
    _event(g, "IA_TurnCamera", "TurnCamera", {"x": 1600, "y": 7000}, "Triggered", "Value")
    _event(g, "IA_Command", "Command", {"x": 1600, "y": 7300}, "Triggered")
    _event(g, "IA_Move", "CancelOrders", {"x": 1600, "y": 7600}, "Triggered")
    _after(g, "InitCombat", "InitControls")
    ins = _after(g, "MsgTick", "HeroTick")
    if ins:  # the tick's delta: the same pin MsgTick takes
        tick = cr.call("find_nodes", {"graph": g, "title": "Tick"})
        ev = next(n for n in tick if "Event" in str(n))
        dt = next(p for p in cr.pins(ev)["output_pins"] if p["name"] == "DeltaSeconds")
        cr.call("connect_pins", {"output_pin": dt["pin_id"], "input_pin": ins["Dt"]})
    cr.call("compile_blueprint", {"blueprint": {"refPath": PM}})


def save():
    import pyrun
    print(pyrun.run('''
EAL = unreal.EditorAssetLibrary
OUT["saved"] = [EAL.save_asset(p, only_if_is_dirty=False) for p in ("/Game/Cousland/Plots/BP_PlotManager",
                "/Game/Cousland/Dialogue/BP_DlgNPC")]
''', 300))


if __name__ == "__main__":
    ue.init()
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, f in (("assets", assets), ("setup", setup), ("graphs", graphs), ("input", input_events),
                    ("save", save)):
        if phase in (name, "all"):
            f()
