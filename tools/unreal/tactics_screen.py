"""python tactics_screen.py [widget|setup|graphs|bind|input|save|all]: the tactics screen (docs/COMBAT.md, "The tactics
screen"). Play/Simulate stopped; controls.py and allies.py must have run. The widget's graphs come from
dsl/tactics/ (written by tactics_dsl.py).

The original's tactics panel (the \\ key, KeyBindings.ini ToggleTactics): one tab per party member, one row per tactic
slot, each a target, a condition and an action, picked from the game's own lists. Here: \\ (IA_Tactics) ->
BP_PlotManager.ToggleTactics: OpenTactics (not in a conversation) makes WBP_Tactics once (TacMake), shows it and
pauses the game (TacShow, as the original's panels do); CloseTactics removes it and resumes unless it was paused
before.

The lists: the export's Tactic* keys (daotools tactics.menu: the targets, base conditions, conditions and commands
the player's menu offers and this side runs, with the talk table's names), read by BP_AreaLoader.BuildFixtures and
handed to the manager (GiveTalents -> SetTacticMenu), with the hero's slots (PlayerTacticSlots -> PSlots).

Party members: a follower keeps its AI table (NTactics) while outside the party; in it, it runs its tactic slots
(NpcPartyTactics: its package's FollowerTacticsTable in its slots, NpcTacticSlots; GiveNpcAlly -> GiveNpcParty ->
SetPartyTactics). CombatTick -> PartyRowsTick swaps them when it joins (JoinRows: the AI table kept in AiTactics)
or leaves (LeaveRows: the slots kept with the player's edits). Conditions added on both sides: its own health or
stamina whatever the target (33, 34), the followers' range bands (35, TacticCondMore; the hero's in
HeroTacticCond), and an attack row attacks (TacticAct; the hero's HTStop).

WBP_Tactics: Open(manager) reads the lists (LoadMenu), the party (ListMembers: in the party and standing, at most
three, after the hero), draws the tabs and shows the hero (ShowMember: Rows, a working copy of PTactics or the
member's NTactics, its Slots and talents: TalIds, TalUse, TalNames). Redraw names each shown row's target, condition
and action (FindTarget, FindCond, FindAct: (empty) for an unused row). Clicking a field (ClickCell: an empty row
starts as Enemy / Any / Attack) fills the picker (FillPick): the targets; the base conditions valid for the row's
target, then that base's conditions (one alone is taken at once); Attack and the member's talents (a mode's
command is Activate mode). PickOption writes the row (a new target resets the condition to Any), then Done: Commit
(SetPlayerTactics, or the member's SetTacticRows) and Redraw. Up moves a row above the one before it, X clears it.
"""
import os
import sys

import combat_rules as cr

import ue

PM, NPC, AL = cr.PM, cr.NPC, cr.AL
NPC_CLASS, PM_CLASS = cr.NPC_CLASS, cr.PM + "_C"
WBP = "/Game/Cousland/Combat/WBP_Tactics.WBP_Tactics"
WBP_CLASS = WBP + "_C"
UMG = "UMGToolSet.UMGToolSet"
F, I, B, STR = "float", "int", "bool", "string"
TEXT, BUTTON, HBOX = "/Script/UMG.TextBlock", "/Script/UMG.Button", "/Script/UMG.HorizontalBox"
ROWS, OPTS, TABS = 12, 32, 4

VARIABLES = {
    NPC: [("AiTactics", F, "ARRAY"), ("PartyTactics", F, "ARRAY"), ("TacticSlots", I), ("bPartyRows", B)],
    PM: [("bTacOpen", B), ("bTacPaused", B), ("PSlots", I), ("bHTStop", B), ("TTargets", F, "ARRAY"),
         ("TTargetNames", STR, "ARRAY"), ("TBases", F, "ARRAY"), ("TBaseNames", STR, "ARRAY"), ("TConds", F, "ARRAY"),
         ("TCondNames", STR, "ARRAY"), ("TCommandNames", STR, "ARRAY"), ("Tac", WBP_CLASS)],
    AL: [("NpcPartyTactics", F, "ARRAY"), ("NpcTacticSlots", I, "ARRAY"), ("PlayerTacticSlots", I),
         ("TacticTargets", F, "ARRAY"), ("TacticTargetNames", STR, "ARRAY"), ("TacticBases", F, "ARRAY"),
         ("TacticBaseNames", STR, "ARRAY"), ("TacticConds", F, "ARRAY"), ("TacticCondNames", STR, "ARRAY"),
         ("TacticCommandNames", STR, "ARRAY")],
    WBP: [("Mgr", PM_CLASS), ("Members", NPC_CLASS, "ARRAY"), ("MemberIdx", I), ("Slots", I), ("Rows", F, "ARRAY"),
          ("EditRow", I), ("Stage", I), ("StageNow", I), ("BaseId", F), ("TI", I), ("NB", I), ("LastCK", I),
          ("Tmp", F), ("MName", STR), ("STgt", STR), ("SCnd", STR), ("SAct", STR), ("AttackName", STR),
          ("TTargets", F, "ARRAY"), ("TTargetNames", STR, "ARRAY"), ("TBases", F, "ARRAY"), ("TBaseNames", STR, "ARRAY"),
          ("TConds", F, "ARRAY"), ("TCondNames", STR, "ARRAY"), ("TalIds", F, "ARRAY"), ("TalUse", F, "ARRAY"),
          ("TalNames", STR, "ARRAY"), ("OptIds", I, "ARRAY"), ("OptNames", STR, "ARRAY"),
          ("TCmds", F, "ARRAY"), ("TCmdNames", STR, "ARRAY"), ("TPresets", F, "ARRAY"), ("TPresetRows", F, "ARRAY"),
          ("TPresetNames", STR, "ARRAY"), ("TBehavNames", STR, "ARRAY"), ("OptCmd", F, "ARRAY"), ("OptSub", F, "ARRAY"),
          ("MClass", I), ("MBeh", I), ("PresetIdx", I), ("Added", I), ("CmdId", F), ("SCmd", STR), ("JumpName", STR)] + [
        (n, TEXT, "ARRAY") for n in ("TgtTs", "CndTs", "ActTs", "NumTs", "OptTs", "MemTs")] + [
        ("RowBs", HBOX, "ARRAY"), ("OptBs", BUTTON, "ARRAY"), ("MemBs", BUTTON, "ARRAY")],
}
FUNCTIONS = {
    NPC: {"SetPartyTactics": [("InTactics", "float[]"), ("K", I), ("Slots", I)],
          "CopyPartyTactic": [("InTactics", "float[]"), ("I", I), ("K", I)], "SetTacticRows": [("InRows", "float[]")],
          "JoinRows": [], "LeaveRows": [], "PartyRowsTick": [], "TacticCondMore": []},
    PM: {"SetTacticMenu": [("InTargets", "float[]"), ("InTargetNames", "string[]"), ("InBases", "float[]"),
                           ("InBaseNames", "string[]"), ("InConds", "float[]"), ("InCondNames", "string[]"),
                           ("InCommandNames", "string[]"), ("InSlots", I)],
         "ToggleTactics": [], "OpenTactics": [], "TacMake": [], "TacShow": [], "CloseTactics": []},
    AL: {"GiveNpcParty": [("Npc", NPC_CLASS), ("K", I)]},
    WBP: dict([("Open", [("InMgr", PM_CLASS)]), ("MemberOffer", [("A", NPC_CLASS)]), ("SetTargetRow", [("V", F)]),
               ("ClickCell", [("R", I), ("C", I)]), ("MatchCmd", [("C", F), ("K", I)]),
               ("AddOpt", [("Name", STR), ("Cmd", F), ("Sub", F)])] +
              [(n, [("K", I)]) for n in ("TabName", "DrawTab", "ShowMember", "HeroTal", "NpcTal", "MatchTI",
                                         "AddTargetOpt", "AddBaseOpt", "AddCondOpt", "DrawOpt",
                                         "PickOption", "PickTarget", "PickCond", "PickBase", "CountOne", "PickAct",
                                         "AddMemberOpt", "AddCmdOpts", "AddCmdKind", "AddTalOpt", "AddJumpOpt",
                                         "AddPresetOpt", "AddBehavOpt", "PickPreset", "PickBehav")] +
              [(n, [("R", I)]) for n in ("DrawRow", "RowVis", "FindTarget", "FindCond", "FindAct", "InitIfEmpty",
                                         "ClearRow", "MoveUp", "FindMemberTgt", "ActDetail")] +
              [(n, [("R", I), ("K", I)]) for n in ("MatchTarget", "MatchCond", "MatchAct", "MatchMemberTgt")] +
              [(n, [("J", I)]) for n in ("ZeroCell", "SwapCell", "ZeroAt", "PresetRow")] +
              [(n, []) for n in ("Collect", "CollectOnce", "LoadMenu", "ListMembers", "DrawTabs", "LoadRows",
                                 "LoadTalents", "HeroTalents", "NpcTalents", "Redraw", "FindTI", "FillPick",
                                 "FillTargets", "FillBases", "FillConds", "FillActs", "DrawPick", "ClosePick",
                                 "CountBase", "BaseNext", "Done", "SwapRows", "Commit", "CloseScreen", "LoadSetup",
                                 "SetupHero", "SetupNpc", "DrawSetup", "FillPresets", "FillBehavs", "ClickPreset",
                                 "ClickBehav", "FillPreset", "SetBehOf")]),
}
GRAPHS = [
    (NPC, ["SetPartyTactics", "CopyPartyTactic", "SetTacticRows", "JoinRows", "LeaveRows", "PartyRowsTick",
           "TacticCondMore", "TacticRow", "TacticAct", "CombatTick"]),
    (PM, ["SetTacticMenu", "CloseTactics", "TacMake", "TacShow", "OpenTactics", "ToggleTactics", "HeroTactics",
          "HeroTacticRow", "HeroTacticUse", "HeroTacticPct", "HeroTacticCond"]),
    (AL, ["GiveNpcParty", "GiveNpcAlly", "BuildFixtures", "GiveTalents"]),
]


def umg(tool, args):
    r = ue.call(UMG, tool, args)
    if r.startswith("TOOL ERROR"):
        raise RuntimeError(tool + ": " + r[:600])
    return r


def widget():
    """WBP_Tactics' tree: a panel in the middle of the screen with the title, the tabs, the rows (number, target,
    condition, action, up, clear) beside the picker (its title and a list of options), and a hint with Close."""
    import pyrun
    made = pyrun.run('''
EAL = unreal.EditorAssetLibrary
OUT["exists"] = EAL.does_asset_exist("/Game/Cousland/Combat/WBP_Tactics")
''', 60)
    if not made.get("exists"):
        umg("CreateWidgetBlueprint", {"folderPath": "/Game/Cousland/Combat", "assetName": "WBP_Tactics",
                                      "parentClass": {"refPath": "/Script/UMG.UserWidget"}})
    have = umg("GetWidgets", {"widgetBlueprint": {"refPath": WBP}})
    tree = []  # (name, class, parent)

    def w(name, cls, parent):
        tree.append((name, "/Script/UMG." + cls, parent))

    w("Root", "CanvasPanel", None)
    w("Panel", "Border", "Root")
    w("Main", "VerticalBox", "Panel")
    w("Title", "TextBlock", "Main")
    w("Tabs", "HorizontalBox", "Main")
    for k in range(TABS):
        w("Mem%d" % k, "Button", "Tabs")
        w("MemT%d" % k, "TextBlock", "Mem%d" % k)
    w("SetupBox", "HorizontalBox", "Main")
    for b in ("PresetB", "BehavB"):
        w(b, "Button", "SetupBox")
        w(b[:-1] + "T", "TextBlock", b)
    w("Body", "HorizontalBox", "Main")
    w("RowList", "VerticalBox", "Body")
    for r in range(ROWS):
        w("Row%d" % r, "HorizontalBox", "RowList")
        w("NumT%d" % r, "TextBlock", "Row%d" % r)
        for b in ("Tgt", "Cnd", "Act", "Up", "Clr"):
            w("%s%d" % (b, r), "Button", "Row%d" % r)
            w("%sT%d" % (b, r), "TextBlock", "%s%d" % (b, r))
    w("Picker", "VerticalBox", "Body")
    w("PickTitle", "TextBlock", "Picker")
    w("PickList", "ScrollBox", "Picker")
    for k in range(OPTS):
        w("Opt%d" % k, "Button", "PickList")
        w("OptT%d" % k, "TextBlock", "Opt%d" % k)
    w("Foot", "HorizontalBox", "Main")
    w("Hint", "TextBlock", "Foot")
    w("Close", "Button", "Foot")
    w("CloseT", "TextBlock", "Close")
    added = 0
    for name, cls, parent in tree:
        if '"%s"' % name in have or "WidgetTree.%s\"" % name in have:
            continue
        args = {"widgetBlueprint": {"refPath": WBP}, "widgetClass": {"refPath": cls}, "widgetDisplayName": name}
        if parent:
            args["parentWidget"] = {"refPath": WBP + ":WidgetTree." + parent}
        umg("AddWidget", args)
        added += 1
    for name, cls, parent in tree:
        if cls.endswith(("TextBlock", "Button", "HorizontalBox")) and name not in ("Tabs", "Body", "Foot", "SetupBox"):
            umg("ToggleWidgetAsVariable", {"widgetBlueprint": {"refPath": WBP},
                                           "widget": {"refPath": WBP + ":WidgetTree." + name}, "bIsVariable": True})
    print("widgets added", added)
    print(pyrun.run('''
P = "%s:WidgetTree."
ROWS, OPTS, TABS = %d, %d, %d
def get(n):
    return unreal.find_object(None, P + n)
INK, GOLD, GREY = unreal.LinearColor(0.93, 0.88, 0.75, 1.0), unreal.LinearColor(0.85, 0.68, 0.38, 1.0), unreal.LinearColor(0.6, 0.57, 0.5, 1.0)
def text(n, size, colour=INK, s=None):
    t = get(n)
    f = t.get_editor_property("font")
    f.set_editor_property("size", size)
    t.set_editor_property("font", f)
    t.set_editor_property("color_and_opacity", unreal.SlateColor(colour))
    if s is not None:
        t.set_editor_property("text", s)
def button(n, tint=(0.2, 0.16, 0.11)):
    b = get(n)
    b.set_editor_property("background_color", unreal.LinearColor(tint[0], tint[1], tint[2], 1.0))
def fill(n, value):
    get(n).slot.set_size(unreal.SlateChildSize(value, unreal.SlateSizeRule.FILL))
def auto(n):
    get(n).slot.set_size(unreal.SlateChildSize(1.0, unreal.SlateSizeRule.AUTOMATIC))
def pad(n, l, t, r, b):
    get(n).slot.set_padding(unreal.Margin(l, t, r, b))
panel = get("Panel")
panel.set_editor_property("brush_color", unreal.LinearColor(0.025, 0.02, 0.016, 0.93))
panel.set_editor_property("padding", unreal.Margin(24, 18, 24, 18))
s = panel.slot
s.set_anchors(unreal.Anchors(unreal.Vector2D(0.5, 0.5), unreal.Vector2D(0.5, 0.5)))
s.set_alignment(unreal.Vector2D(0.5, 0.5))
s.set_position(unreal.Vector2D(0, 0))
s.set_size(unreal.Vector2D(1240, 780))
text("Title", 22, GOLD, "Tactics")
pad("Title", 0, 0, 0, 10)
pad("Tabs", 0, 0, 0, 12)
for k in range(TABS):
    text("MemT%%d" %% k, 15, INK, "Member")
    button("Mem%%d" %% k, (0.28, 0.2, 0.12))
    pad("Mem%%d" %% k, 0, 0, 8, 0)
pad("SetupBox", 0, 0, 0, 10)
for b, label in (("Preset", "Load a preset"), ("Behav", "Behaviour: Default")):
    text(b + "T", 14, INK, label)
    button(b + "B", (0.24, 0.18, 0.11))
    pad(b + "B", 0, 0, 10, 0)
fill("Body", 1.0)
fill("RowList", 2.7)
fill("Picker", 1.0)
pad("Picker", 18, 0, 0, 0)
for r in range(ROWS):
    pad("Row%%d" %% r, 0, 2, 0, 2)
    text("NumT%%d" %% r, 15, GREY, str(r + 1))
    auto("NumT%%d" %% r)
    pad("NumT%%d" %% r, 0, 6, 10, 0)
    for b, value, label in (("Tgt", 1.0, "Enemy"), ("Cnd", 2.2, "Any"), ("Act", 1.6, "Attack"), ("Up", 0.0, "Up"), ("Clr", 0.0, "X")):
        text("%%sT%%d" %% (b, r), 14, INK, label)
        button("%%s%%d" %% (b, r))
        if value:
            fill("%%s%%d" %% (b, r), value)
        else:
            auto("%%s%%d" %% (b, r))
        pad("%%s%%d" %% (b, r), 3, 0, 0, 0)
text("PickTitle", 16, GOLD, "Click a field to change it")
pad("PickTitle", 0, 0, 0, 8)
fill("PickList", 1.0)
for k in range(OPTS):
    text("OptT%%d" %% k, 14, INK, "Option")
    button("Opt%%d" %% k, (0.14, 0.12, 0.09))
    pad("Opt%%d" %% k, 0, 1, 0, 1)
pad("Foot", 0, 12, 0, 0)
text("Hint", 13, GREY, "Rows run from the top: the first whose condition holds is used. Up moves a tactic up, X clears it. \\\\ or Close to return.")
fill("Hint", 1.0)
text("CloseT", 15, INK, "Close")
button("Close", (0.28, 0.2, 0.12))
OUT["styled"] = True
''' % (WBP, ROWS, OPTS, TABS), 300))
    print(umg("CompileWidgetBlueprint", {"widgetBlueprint": {"refPath": WBP}})[:300])


def setup():
    """Variables (only those missing: adding one twice makes a copy with a suffix) and functions."""
    variables = {}
    for bp, vs in VARIABLES.items():
        have = set(cr.call("list_variables", {"blueprint": {"refPath": bp}}))
        variables[bp] = [v for v in vs if v[0] not in have]
    cr.setup(variables, FUNCTIONS, compile_all_after=False)
    for bp in (WBP, PM, NPC, AL):
        cr.call("compile_blueprint", {"blueprint": {"refPath": bp}})


def graphs():
    here = os.path.join(cr.HERE, "dsl")
    names = sorted(os.path.splitext(n)[0] for n in os.listdir(os.path.join(here, "tactics")))
    for bp, fns, folder in [(bp, fns, here) for bp, fns in GRAPHS] + [(WBP, names, os.path.join(here, "tactics"))]:
        for fn in fns:
            code = open(os.path.join(folder, fn + ".dsl"), encoding="utf-8").read()
            try:
                r = cr.call("write_graph_dsl", {"graph": {"refPath": "%s:%s" % (bp, fn)}, "code": code})
            except RuntimeError as e:
                r = e
            if "rror" in str(r) or "arning" in str(r):
                print(fn, str(r)[:600], flush=True)
        print(bp.split(".")[-1], cr.call("compile_blueprint", {"blueprint": {"refPath": bp}}))


def bind():
    """Each button's OnClicked in WBP_Tactics' event graph calls its function: a row's fields ClickCell(row,
    0 target / 1 condition / 2 action), Up MoveUp, X ClearRow, an option PickOption, a tab ShowMember, Close
    CloseScreen."""
    g = {"refPath": WBP + ":EventGraph"}
    wiring = [("Close", "CloseScreen", {}), ("PresetB", "ClickPreset", {}), ("BehavB", "ClickBehav", {})] + [
        ("Mem%d" % k, "ShowMember", {"K": k}) for k in range(TABS)] + [
        ("Opt%d" % k, "PickOption", {"K": k}) for k in range(OPTS)]
    for r in range(ROWS):
        wiring += [("Tgt%d" % r, "ClickCell", {"R": r, "C": 0}), ("Cnd%d" % r, "ClickCell", {"R": r, "C": 1}),
                   ("Act%d" % r, "ClickCell", {"R": r, "C": 2}), ("Up%d" % r, "MoveUp", {"R": r}),
                   ("Clr%d" % r, "ClearRow", {"R": r})]
    def events():  # the bound events there: {node: its type id, "Aggiungievento|OnClicked(<button>)"}
        ns = [n for n in cr.call("find_nodes", {"graph": g, "title": ""}) if "ComponentBoundEvent" in n["refPath"]]
        return {i["node"]["refPath"]: i["type_id"] for i in cr.call("get_node_infos", {"nodes": ns})} if ns else {}

    have = events()
    bound = {t.split("(")[-1].rstrip(")") for t in have.values()}
    done = 0
    for n, (button, fn, pins) in enumerate(wiring):
        if button in bound:
            continue
        umg("BindToEventProperty", {"widgetBlueprint": {"refPath": WBP}, "eventName": "OnClicked",
                                    "propertyName": button, "propertyClass": {"refPath": BUTTON}})
        now = events()
        new = [k for k in now if k not in have]
        have = now
        if not new:
            print("no event node for", button, flush=True)
            continue
        ev = {"refPath": new[0]}
        pos = {"x": 400 + 700 * (n // 40), "y": 200 * (n % 40)}
        call = cr.call("create_node", {"graph": g, "type_id": "Funzionedichiamata|" + fn,
                                       "pos": {"x": pos["x"] + 360, "y": pos["y"]}})
        out = [p for p in cr.pins(ev)["output_pins"] if p["name"] == "then"]
        ins = {p["name"]: p["pin_id"] for p in cr.pins(call)["input_pins"]}
        cr.call("connect_pins", {"output_pin": out[0]["pin_id"], "input_pin": ins["execute"]})
        for k, v in pins.items():
            cr.call("set_pin_value", {"pin": ins[k], "value": str(v)})
        done += 1
        print("bound", button, "->", fn, pins, flush=True)
    print("bound", done, "more;", len(bound), "were there, of", len(wiring))
    print(umg("CompileWidgetBlueprint", {"widgetBlueprint": {"refPath": WBP}})[:300])


def input_events():
    """IA_Tactics on \\ in IMC_Dialogue, working while paused, and BP_PlotManager's IA_Tactics -> ToggleTactics."""
    import pyrun
    print(pyrun.run('''
EAL = unreal.EditorAssetLibrary
factory = getattr(unreal, "InputAction_Factory", None) or getattr(unreal, "InputActionFactory")
imc = EAL.load_asset("/Game/Cousland/Dialogue/IMC_Dialogue")
have = {(m.action.get_name() if m.action else "", str(m.key.get_editor_property("key_name"))) for m in imc.get_editor_property("default_key_mappings").get_editor_property("mappings")}
path = "/Game/Cousland/Combat/IA_Tactics"
ia = EAL.load_asset(path) if EAL.does_asset_exist(path) else unreal.AssetToolsHelpers.get_asset_tools().create_asset("IA_Tactics", "/Game/Cousland/Combat", unreal.InputAction, factory())
ia.set_editor_property("trigger_when_paused", True)
if ("IA_Tactics", "Backslash") not in have:
    k = unreal.Key()
    k.set_editor_property("key_name", "Backslash")
    imc.map_key(ia, k)
OUT["saved"] = [EAL.save_asset(path, only_if_is_dirty=False), EAL.save_asset("/Game/Cousland/Dialogue/IMC_Dialogue", only_if_is_dirty=False)]
''', 120))
    g = {"refPath": PM + ":EventGraph"}
    if cr.call("find_nodes", {"graph": g, "title": "IA_Tactics"}):
        print("IA_Tactics already there")
        return
    types = cr.call("find_node_types", {"graph": g, "type_id_filter": "IA_Tactics", "context_pins": []})
    ids = [t.get("type_id", t) if isinstance(t, dict) else t for t in types]
    ev = cr.call("create_node", {"graph": g, "type_id": next(i for i in ids if i.endswith("IA_Tactics")),
                                 "pos": {"x": 1600, "y": 7200}})
    call = cr.call("create_node", {"graph": g, "type_id": "Funzionedichiamata|ToggleTactics", "pos": {"x": 2020, "y": 7200}})
    started = next(p for p in cr.pins(ev)["output_pins"] if p["name"] == "Started")
    ins = {p["name"]: p["pin_id"] for p in cr.pins(call)["input_pins"]}
    cr.call("connect_pins", {"output_pin": started["pin_id"], "input_pin": ins["execute"]})
    print("IA_Tactics -> ToggleTactics", cr.call("compile_blueprint", {"blueprint": {"refPath": PM}}))


def save():
    import pyrun
    print(pyrun.run('''
EAL = unreal.EditorAssetLibrary
OUT["saved"] = [EAL.save_asset(p, only_if_is_dirty=False) for p in ("/Game/Cousland/Combat/WBP_Tactics",
                "/Game/Cousland/Plots/BP_PlotManager", "/Game/Cousland/Dialogue/BP_DlgNPC", "/Game/Cousland/Areas/BP_AreaLoader")]
''', 300))


if __name__ == "__main__":
    ue.init()
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, f in (("widget", widget), ("setup", setup), ("graphs", graphs), ("bind", bind), ("input", input_events),
                    ("save", save)):
        if phase in (name, "all"):
            f()
