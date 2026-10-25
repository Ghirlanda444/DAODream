"""python pause.py [assets|setup|graphs|input|save|all]: real-time with pause and orders to the party in the Blueprints
(docs/COMBAT.md, "Pause and party orders"). Play/Simulate stopped; party.py must have run.

Keys (IMC_Dialogue): Space pauses and resumes (IA_Pause; the template's jump loses Space, Dragon Age has none);
F1 gives orders to the hero, F2-F4 to the party members in the order the level lists them (IA_Party1-4); H holds
position (IA_Hold). These, the attack and talent keys, Q and the mouse look trigger while paused.

BP_PlotManager: TogglePause sets the game paused (SetGamePaused: every actor stops, game time too, so cooldowns and
effects wait) unless a conversation or the game over is up; resuming runs what was queued. PlayerAttack and
UseTalent route the keys: with a party member selected they give it an order (OrderAttack: the hostile nearest the
player within 15 m, FindOrderTarget; OrderTalent: that, OrderOnTarget, and its talent in the slot); else, paused, they queue the
hero's attack or talent (QueuedAttack, QueuedSlot; RunQueuedAttack, RunQueuedTalent on resuming); else they act at
once (PlayerAttackNow, UseTalentNow: the old bodies). SelectMember asks each creature (SelectOffer -> MemberOffer)
and keeps the K-th standing party member (Selected). ToggleHold: the selected member, or with the hero selected the
whole party (HoldAll). AssignTarget keeps a member's ordered target while it stands (OrderTarget), else bids as
before (AssignByBid). ShowTalents puts PAUSED first while paused, and shows the selected member's line (SelLine, a copy
of its OrderLine, and SelName, kept by the manager so nothing reads through an empty Selected) instead of the
hero's.

BP_DlgNPC: OrderAttack sets OrderTarget and Target; OrderTalent sets PendingSlot (the slot + 1) and OrderMsg.
CombatRound runs an ordered talent first (DoOrder: UsableCheck, DoTalent, or "Not now" and the round as before);
else TacticsRound (the old body). Held (bHold, SetHold): ChaseFoe stands still and PartyAct does not follow the
player, so a held member strikes only what reaches it and an archer shoots only what is in range. MakeOrderLine and
AddOrderSlot write OrderLine: its name, "(holding)", each talent ([slot] name, ON for a mode on, * for an order
waiting); NameOf gives a slot's talent name (SayTalent's names).
"""
import os
import sys

import combat_rules as cr

import ue

PM, NPC = cr.PM, cr.NPC
NPC_CLASS, PM_CLASS = cr.NPC_CLASS, cr.PM + "_C"
I, B, STR = "int", "bool", "string"

VARIABLES = {
    PM: [("bPaused", B), ("bQueuedAttack", B), ("QueuedSlot", I), ("Selected", NPC_CLASS), ("SelectCount", I),
         ("SelectWanted", I), ("bHoldAll", B), ("SelLine", STR), ("SelName", STR)],
    NPC: [("OrderTarget", NPC_CLASS), ("PendingSlot", I), ("bHold", B), ("OrderLine", STR), ("OrderMsg", STR),
          ("TName", STR)],
}
FUNCTIONS = {
    PM: {"PlayerAttackNow": [], "UseTalentNow": [("Slot", I)], "TogglePause": [], "RunQueuedAttack": [],
         "RunQueuedTalent": [], "SelectMember": [("K", I)], "MemberOffer": [("Npc", NPC_CLASS)],
         "FindOrderTarget": [], "OrderOnTarget": [], "OrderAttack": [], "OrderTalent": [("Slot", I)], "ToggleHold": [],
         "AssignByBid": [("Follower", NPC_CLASS)]},
    NPC: {"SelectOffer": [("InMgr", PM_CLASS)], "OrderAttack": [("Foe", NPC_CLASS)], "OrderTalent": [("Slot", I)],
          "TacticsRound": [], "DoOrder": [], "SetHold": [("bOn", B)], "MakeOrderLine": [], "AddOrderSlot": [("K", I)],
          "NameOf": [("K", I)]},
}
# (blueprint, graph, dsl file): the creature's OrderAttack and OrderTalent share names with the manager's
GRAPHS = [
    (NPC, [("SelectOffer",), ("OrderAttack", "OrderAttack_NPC"), ("NameOf",), ("OrderTalent", "OrderTalent_NPC"),
           ("TacticsRound",), ("DoOrder",), ("CombatRound",), ("SetHold",), ("AddOrderSlot",), ("MakeOrderLine",),
           ("ChaseFoe",), ("PartyAct",)]),
    (PM, [("PlayerAttackNow",), ("UseTalentNow",), ("RunQueuedAttack",), ("RunQueuedTalent",), ("ShowTalents",),
          ("TogglePause",), ("MemberOffer",), ("SelectMember",), ("FindOrderTarget",), ("OrderOnTarget",), ("OrderAttack",),
          ("OrderTalent",), ("PlayerAttack",), ("UseTalent",), ("ToggleHold",), ("AssignByBid",), ("AssignTarget",)]),
]
ACTIONS = {"IA_Pause": "SpaceBar", "IA_Party1": "F1", "IA_Party2": "F2", "IA_Party3": "F3", "IA_Party4": "F4",
           "IA_Hold": "H"}
WHEN_PAUSED = ["/Game/Cousland/Combat/" + n for n in ACTIONS] + [
    "/Game/Cousland/Combat/IA_Attack", "/Game/Cousland/Combat/IA_SwitchWeapon"] + [
    "/Game/Cousland/Combat/IA_Talent%d" % k for k in range(1, 7)]


def assets():
    """The input actions on their keys in IMC_Dialogue, Space off the template's jump, and the keys that work
    while paused (trigger_when_paused; the mouse look too)."""
    import pyrun
    print(pyrun.run('''
EAL = unreal.EditorAssetLibrary
factory = getattr(unreal, "InputAction_Factory", None) or getattr(unreal, "InputActionFactory")
imc = EAL.load_asset("/Game/Cousland/Dialogue/IMC_Dialogue")
have = {(m.action.get_name() if m.action else "", str(m.key.get_editor_property("key_name"))) for m in imc.get_editor_property("default_key_mappings").get_editor_property("mappings")}
for name, key in %r.items():
    path = "/Game/Cousland/Combat/" + name
    ia = EAL.load_asset(path) if EAL.does_asset_exist(path) else unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, "/Game/Cousland/Combat", unreal.InputAction, factory())
    if (name, key) not in have:
        k = unreal.Key()
        k.set_editor_property("key_name", key)
        imc.map_key(ia, k)
    EAL.save_asset(path, only_if_is_dirty=False)
EAL.save_asset("/Game/Cousland/Dialogue/IMC_Dialogue", only_if_is_dirty=False)
# the template's jump gives Space up
found = [a for a in EAL.list_assets("/Game", recursive=True) if a.split(".")[0].endswith("/IMC_Default")]
for path in found:
    d = EAL.load_asset(path)
    for m in list(d.get_editor_property("default_key_mappings").get_editor_property("mappings")):
        if m.action and m.action.get_name() == "IA_Jump" and str(m.key.get_editor_property("key_name")) == "SpaceBar":
            d.unmap_key(m.action, m.key)
            OUT["unmapped"] = path
    EAL.save_asset(path, only_if_is_dirty=False)
paths = %r
look = [a for a in EAL.list_assets("/Game", recursive=True) if a.split(".")[0].split("/")[-1] in ("IA_MouseLook", "IA_Look")]
missing = []
for path in paths + [a.split(".")[0] for a in look]:
    if not EAL.does_asset_exist(path):
        missing.append(path)
        continue
    ia = EAL.load_asset(path)
    ia.set_editor_property("trigger_when_paused", True)
    EAL.save_asset(path, only_if_is_dirty=False)
OUT["missing"] = missing
''' % (ACTIONS, WHEN_PAUSED), 300))


def setup():
    cr.setup(VARIABLES, FUNCTIONS, compile_all_after=False)
    for bp in (PM, NPC):
        cr.call("compile_blueprint", {"blueprint": {"refPath": bp}})


def graphs():
    for bp, names in GRAPHS:
        for entry in names:
            fn, src = entry[0], entry[-1]
            code = open(os.path.join(cr.HERE, "dsl", src + ".dsl"), encoding="utf-8").read()
            r = cr.call("write_graph_dsl", {"graph": {"refPath": "%s:%s" % (bp, fn)}, "code": code})
            print(fn, str(r)[:300])
        cr.call("compile_blueprint", {"blueprint": {"refPath": bp}})


def input_events():
    """In BP_PlotManager's event graph: IA_Pause -> TogglePause, IA_Party<k> -> SelectMember(k - 1), IA_Hold ->
    ToggleHold, each on Started."""
    g = {"refPath": PM + ":EventGraph"}
    wiring = [("IA_Pause", "TogglePause", None), ("IA_Hold", "ToggleHold", None)] + [
        ("IA_Party%d" % k, "SelectMember", k - 1) for k in range(1, 5)]
    for n, (action, fn, arg) in enumerate(wiring):
        if cr.call("find_nodes", {"graph": g, "title": action}):
            print(action, "already there")
            continue
        types = cr.call("find_node_types", {"graph": g, "type_id_filter": action, "context_pins": []})
        ids = [t.get("type_id", t) if isinstance(t, dict) else t for t in types]
        pos = {"x": 1600, "y": 5200 + 260 * n}
        ev = cr.call("create_node", {"graph": g, "type_id": next(i for i in ids if i.endswith(action)), "pos": pos})
        call = cr.call("create_node", {"graph": g, "type_id": "Funzionedichiamata|" + fn,
                                       "pos": {"x": pos["x"] + 420, "y": pos["y"]}})
        started = next(p for p in cr.pins(ev)["output_pins"] if p["name"] == "Started")
        ins = {p["name"]: p["pin_id"] for p in cr.pins(call)["input_pins"]}
        cr.call("connect_pins", {"output_pin": started["pin_id"], "input_pin": ins["execute"]})
        if arg is not None:
            cr.call("set_pin_value", {"pin": ins["K"], "value": str(arg)})
        print(action, "->", fn, "" if arg is None else arg)
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
