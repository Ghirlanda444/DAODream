"""python loot.py [assets|setup|defaults|patch|graphs|bind|input|save|all] [first graph]: loot, the inventory and
potions in the Blueprints (docs/LOOT.md). Play/Simulate stopped; tactics_run.py must have run. The graphs come from
dsl/loot/<Blueprint>/ (written by loot_dsl.py: run it first) and the patched dsl/*.dsl.

BP_PlotManager: SetLootData takes the export's item catalogue (Item*), treasure tables (TreasureRanges, TreasureRows),
carried items (Bag), rules and the hero's starting items into the party's inventory (Inv, InvN; copper is Money).
GenLoot(loot fields, bag) rolls TreasureGenerate (daotools treasure.generate) into GItems, GCounts, GMoney: the
target's carried items, a reactive potion, the global money chance, TS_ItemNum draws from the low or high table, an
equipped piece by chance. FillBox does a container's at spawn; DropFor a fallen creature's (BP_DlgNPC.KnockOut ->
DropLoot), into a bag (a BP_Container, look 5) where it fell. A right click on a container walks the hero to it
(CommandThing, PickBoxOf, UseRoute -> OpenBox): locked, it needs its key or a rogue's lockpicking (PLockpick); then the
loot window (WBP_Loot: an item, the money, Take all). I (IA_Inventory) shows the inventory (WBP_Inventory): a click on
a poultice or a lyrium potion uses it on the one in control (UseItem: (50 + spellpower) x its power in health; a
lyrium potion gives a mage mana; 5 s cooldown each). Tactics: Use item and the four potion commands (TacItem, in
combat: the dearest or the cheapest potion of the party's stock, _AI_GetPotionByFilter).

BP_Container: its look (Meshes, Scales on the class defaults: chest, sack, barrel, cabinet, rubble, bag), name, lock,
key, items and money. BP_AreaLoader spawns the export's containers (GiveLoot -> BoxOne) and hands each creature its
loot fields and carried items (GiveNpcRules -> SetLootInfo, SetBagInfo).
"""
import json
import os
import sys

import combat_rules as cr

import ue

PM, NPC, AL = cr.PM, cr.NPC, cr.AL
NPC_CLASS, A, PM_CLASS = cr.NPC_CLASS, cr.ACTOR, cr.PM + "_C"
BOX = "/Game/Cousland/Areas/BP_Container.BP_Container"
BOX_CLASS = BOX + "_C"
WLOOT = "/Game/Cousland/Combat/WBP_Loot.WBP_Loot"
WINV = "/Game/Cousland/Combat/WBP_Inventory.WBP_Inventory"
BPS = {"PM": PM, "NPC": NPC, "AL": AL, "BOX": BOX, "WLOOT": WLOOT, "WINV": WINV}
F, I, B, STR, VEC = "float", "int", "bool", "string", "vector"
TEXT, BUTTON = "/Script/UMG.TextBlock", "/Script/UMG.Button"
UMG = "UMGToolSet.UMGToolSet"
HERE = os.path.dirname(os.path.abspath(__file__))
LOOT_ROWS, INV_ROWS = 12, 20
PROPS = "/Game/ThirdParty/Megascans/Props/%s/SM_%s.SM_%s"
# a container's look -> (prop, scale): chest, sack, crate (a barrel), weapon or armour stand (a cabinet), rubble, a bag
LOOKS = [("WoodenChest", 1.0), ("BurlapSack", 1.0), ("WoodenBarrel", 1.0), ("MedievalCabinet", 1.0),
         ("LimestoneRubble", 0.5), ("BurlapSack", 0.8)]

VARIABLES = {
    PM: [(n, STR, "ARRAY") for n in ("ItemTags", "ItemNames", "ItemDescs")]
        + [(n, F, "ARRAY") for n in ("ItemStats", "TRanges", "TRows", "LBag", "LRules", "LReactive", "GLoot", "CdAb",
                                     "CdUntil")]
        + [(n, I, "ARRAY") for n in ("Inv", "InvN", "GItems", "GCounts", "GEquip")]
        + [(n, F) for n in ("PLockpick", "PSpell", "GLim", "GChance", "GF", "GR", "GSf", "GBest", "UseAmt", "UseSPv")]
        + [(n, I) for n in ("Money", "InvAt", "GH", "GMoney", "GHc", "GMn", "GTier", "GIdx", "GN", "GNMax", "GTbl",
                            "GRow", "GSn", "GAt", "ItemK", "TIt")]
        + [(n, B) for n in ("GCarry", "GHost", "GBool", "LootOpen", "InvOpen")]
        + [("MText", STR), ("LootBox", BOX_CLASS), ("PickBox", BOX_CLASS), ("WLoot", WLOOT + "_C"),
           ("WInv", WINV + "_C"), ("CdWho", A, "ARRAY")],
    NPC: [("NLoot", F, "ARRAY"), ("NBagS", I), ("NBagN", I), ("Dropped", B)],
    AL: [(n, STR, "ARRAY") for n in ("ItemTags", "ItemNames", "ItemDescs", "ContainerTags", "ContainerNames", "ContainerKeys")]
        + [(n, F, "ARRAY") for n in ("ItemStats", "TreasureRanges", "TreasureRows", "Bag", "LootRules", "ReactivePotions",
                                     "PlayerItems", "NpcLoot", "NpcBag", "ContainerPose", "ContainerInfo", "ContainerLoot",
                                     "ContainerBag")]
        + [("PlayerLockpick", F), ("PlayerSpellPower", F)],
    BOX: [("Look", I), ("CName", STR), ("Locked", B), ("LockLevel", F), ("KeyTag", STR), ("KeyReq", B), ("Usable", B),
          ("LItems", I, "ARRAY"), ("LCounts", I, "ARRAY"), ("LMoney", I), ("Meshes", "/Script/Engine.StaticMesh", "ARRAY"),
          ("Scales", VEC, "ARRAY")],
    WLOOT: [("Mgr", PM_CLASS), ("Box", BOX_CLASS), ("ItTs", TEXT, "ARRAY"), ("ItBs", BUTTON, "ARRAY")],
    WINV: [("Mgr", PM_CLASS), ("RowTs", TEXT, "ARRAY"), ("RowBs", BUTTON, "ARRAY")],
}
K = [("K", I)]
FUNCTIONS = {
    PM: dict([("SetLootData", [(n, "string[]") for n in ("InTags", "InNames", "InDescs")]
                              + [(n, "float[]") for n in ("InStats", "InRanges", "InRows", "InBag", "InRules", "InReactive")]
                              + [("InLockpick", F), ("InSpell", F), ("InPlayerItems", "float[]")]),
              ("PlayerItemOne", [("InPlayerItems", "float[]"), ("K", I)]),
              ("InvAdd", [("Item", I), ("N", I)]), ("InvFind", [("Item", I)]), ("InvFindOne", [("K", I), ("Item", I)]),
              ("InvAddGo", [("Item", I), ("N", I)]), ("InvTake", [("Slot", I), ("N", I)]), ("CountKind", [("Kind", F)]),
              ("CountKindOne", [("K", I), ("Kind", F)]), ("MoneyText", [("Bits", I)]),
              ("GenLoot", [("InLoot", "float[]"), ("O", I), ("BStart", I), ("BCount", I), ("bHost", B)]),
              ("GCopy", [("InLoot", "float[]"), ("O", I), ("J", I)]), ("GenBag", [("BStart", I), ("BCount", I)]),
              ("GenBagOne", K), ("GAdd", [("Item", I), ("N", I)]), ("GFindOne", [("K", I), ("Item", I)]),
              ("GAddGo", [("Item", I), ("N", I)]), ("GenPut", [("Item", I), ("Size", F)]), ("GenStack", [("Size", F)]),
              ("DropFor", [("Npc", NPC_CLASS)]), ("DropBag", [("Npc", NPC_CLASS)]),
              ("FillBox", [("Box", BOX_CLASS), ("InLoot", "float[]"), ("K", I), ("BStart", I), ("BCount", I)]),
              ("OpenBox", [("Box", BOX_CLASS)]), ("TryUnlock", [("Box", BOX_CLASS)]),
              ("KeyOne", [("K", I), ("Box", BOX_CLASS)]), ("TryUnlock2", [("Box", BOX_CLASS)]),
              ("ShowLoot", [("Box", BOX_CLASS)]), ("LootTake", K), ("UseFromInv", [("Slot", I)]),
              ("UseItem", [("Who", A), ("Slot", I)]), ("CdCheck", [("Who", A), ("Ab", F)]),
              ("CdOne", [("K", I), ("Who", A), ("Ab", F)]), ("UseGo", [("Who", A), ("Slot", I)]), ("UseSP", [("Who", A)]),
              ("UseSPCast", [("A", A)]), ("HealAny", [("Who", A)]), ("HealAnyCast", [("A", A)]), ("ManaAny", [("Who", A)]),
              ("ManaCast", [("A", A)]), ("TacItem", [("Me", A), ("Cmd", F), ("Sub", F)]),
              ("TacItem2", [("Me", A), ("Cmd", F), ("Sub", F)]), ("TacItemOne", [("K", I), ("Cmd", F), ("Sub", F)]),
              ("TacItemUse", [("Me", A)]), ("PickBoxOf", [("What", A)]), ("HeroItem", [("I", I)])]
             + [(n, []) for n in ("GenReactive", "GenReact2", "GenReact3", "GenFirst", "GenDraws", "GenNumOne", "GenDraws2",
                                  "GenDrawOne", "GenDrawTbl", "GenEquip", "LootMake", "CloseLootUI", "CloseLoot", "BagGone",
                                  "LootMoney", "LootAll", "InvMake", "ToggleInventory", "OpenInv", "CloseInv")]),
    NPC: {"SetLootInfo": [("InLoot", "float[]"), ("InBag", "float[]"), ("K", I)],
          "LootOne": [("InLoot", "float[]"), ("K", I), ("J", I)], "SetBagInfo": [("InBag", "float[]"), ("K", I)],
          "DropLoot": [], "GainStamina": [("Amount", F)], "TacItemRow": [("Cmd", F), ("Sub", F)]},
    AL: {"GiveLoot": [], "BoxOne": [("K", I), ("Pm", PM_CLASS)]},
    BOX: {"Setup": [("InLook", I), ("InName", STR), ("bLocked", B), ("InLevel", F), ("InKey", STR), ("bKeyReq", B),
                    ("bUsable", B)],
          "SetLoot": [("InItems", "int[]"), ("InCounts", "int[]"), ("InMoney", I)], "TakeOut": K, "TakeMoney": [],
          "Unlock": []},
    WLOOT: {"Collect": [], "CollectOnce": [], "Open": [("InMgr", PM_CLASS), ("InBox", BOX_CLASS)], "Redraw": [], "DrawIt": K, "ClickIt": K,
            "ClickMoney": [], "ClickAll": [], "ClickClose": []},
    WINV: {"Collect": [], "CollectOnce": [], "Open": [("InMgr", PM_CLASS)], "Redraw": [], "DrawRow": K, "ClickRow": K, "ClickClose": []},
}
# graphs of dsl/*.dsl patched for loot (patch()), by Blueprint
PATCHED = [(PM, n) for n in ("PickBoxOf", "CommandThing", "HeroUseNow", "UseRoute", "HeroTacticUse", "HeroItem")] + \
          [(NPC, n) for n in ("KnockOut", "TacticAct")] + [(AL, n) for n in ("GiveNpcRules", "BuildFixtures")]


def umg(tool, args):
    r = ue.call(UMG, tool, args)
    if r.startswith("TOOL ERROR"):
        raise RuntimeError(tool + ": " + r[:600])
    return r


def assets():
    """BP_Container (an Actor: a box to click and a mesh), WBP_Loot and WBP_Inventory, IA_Inventory on I."""
    import pyrun
    print(pyrun.run('''
EAL = unreal.EditorAssetLibrary
path = "/Game/Cousland/Areas/BP_Container"
if not EAL.does_asset_exist(path):
    f = unreal.BlueprintFactory()
    f.set_editor_property("parent_class", unreal.Actor)
    bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset("BP_Container", "/Game/Cousland/Areas", unreal.Blueprint, f)
    sub = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    root = sub.k2_gather_subobject_data_for_blueprint(bp)[0]
    h, fail = sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.BoxComponent, blueprint_context=bp))
    box = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h))
    box.set_editor_property("box_extent", unreal.Vector(45.0, 45.0, 40.0))
    box.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 40.0))
    box.set_collision_profile_name("BlockAll")
    h, fail = sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.StaticMeshComponent, blueprint_context=bp))
    mesh = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h))
    mesh.set_collision_profile_name("NoCollision")
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    EAL.save_asset(path, only_if_is_dirty=False)
factory = getattr(unreal, "InputAction_Factory", None) or getattr(unreal, "InputActionFactory")
ipath = "/Game/Cousland/Combat/IA_Inventory"
ia = EAL.load_asset(ipath) if EAL.does_asset_exist(ipath) else unreal.AssetToolsHelpers.get_asset_tools().create_asset("IA_Inventory", "/Game/Cousland/Combat", unreal.InputAction, factory())
imc = EAL.load_asset("/Game/Cousland/Dialogue/IMC_Dialogue")
have = {(m.action.get_name() if m.action else "", str(m.key.get_editor_property("key_name"))) for m in imc.get_editor_property("default_key_mappings").get_editor_property("mappings")}
OUT["I taken"] = [a for a, k in have if k == "I"]
if ("IA_Inventory", "I") not in have:
    k = unreal.Key()
    k.set_editor_property("key_name", "I")
    imc.map_key(ia, k)
EAL.save_asset(ipath, only_if_is_dirty=False)
EAL.save_asset("/Game/Cousland/Dialogue/IMC_Dialogue", only_if_is_dirty=False)
OUT["box"] = EAL.does_asset_exist(path)
''', 300))
    window(WLOOT, "WBP_Loot", loot_tree(), (430, 560), (0.72, 0.5), "")
    window(WINV, "WBP_Inventory", inv_tree(), (500, 680), (0.28, 0.5), "Inventory")


def loot_tree():
    t = [("Root", "CanvasPanel", None), ("Panel", "Border", "Root"), ("Main", "VerticalBox", "Panel"),
         ("Title", "TextBlock", "Main"), ("MoneyB", "Button", "Main"), ("MoneyT", "TextBlock", "MoneyB"),
         ("List", "VerticalBox", "Main")]
    for k in range(LOOT_ROWS):
        t += [("It%d" % k, "Button", "List"), ("ItT%d" % k, "TextBlock", "It%d" % k)]
    t += [("Foot", "HorizontalBox", "Main"), ("AllB", "Button", "Foot"), ("AllT", "TextBlock", "AllB"),
          ("CloseB", "Button", "Foot"), ("CloseT", "TextBlock", "CloseB")]
    return t


def inv_tree():
    t = [("Root", "CanvasPanel", None), ("Panel", "Border", "Root"), ("Main", "VerticalBox", "Panel"),
         ("Title", "TextBlock", "Main"), ("MoneyT", "TextBlock", "Main"), ("List", "ScrollBox", "Main")]
    for k in range(INV_ROWS):
        t += [("Row%d" % k, "Button", "List"), ("RowT%d" % k, "TextBlock", "Row%d" % k)]
    t += [("Desc", "TextBlock", "Main"), ("Foot", "HorizontalBox", "Main"), ("CloseB", "Button", "Foot"),
          ("CloseT", "TextBlock", "CloseB")]
    return t


def window(path, name, tree, size, anchor, title):
    """A window like the tactics screen's: a dark panel at `anchor` (fractions of the screen), its texts and buttons
    styled, the texts and buttons made variables."""
    import pyrun
    folder = path.rsplit("/", 1)[0]
    made = pyrun.run('OUT["exists"] = unreal.EditorAssetLibrary.does_asset_exist(%r)' % path.split(".")[0], 60)
    if not made.get("exists"):
        umg("CreateWidgetBlueprint", {"folderPath": folder, "assetName": name,
                                      "parentClass": {"refPath": "/Script/UMG.UserWidget"}})
    have = umg("GetWidgets", {"widgetBlueprint": {"refPath": path}})
    for w, cls, parent in tree:
        if '"%s"' % w in have or "WidgetTree.%s\"" % w in have:
            continue
        args = {"widgetBlueprint": {"refPath": path}, "widgetClass": {"refPath": "/Script/UMG." + cls}, "widgetDisplayName": w}
        if parent:
            args["parentWidget"] = {"refPath": path + ":WidgetTree." + parent}
        umg("AddWidget", args)
    for w, cls, parent in tree:
        if cls in ("TextBlock", "Button"):
            umg("ToggleWidgetAsVariable", {"widgetBlueprint": {"refPath": path},
                                           "widget": {"refPath": path + ":WidgetTree." + w}, "bIsVariable": True})
    texts = {"Title": (20, "GOLD", title), "MoneyT": (15, "INK", ""), "AllT": (15, "INK", "Take all"),
             "CloseT": (15, "INK", "Close"), "Desc": (13, "GREY", "")}
    print(pyrun.run('''
P = "%s:WidgetTree."
def get(n):
    return unreal.find_object(None, P + n)
COL = {"INK": unreal.LinearColor(0.93, 0.88, 0.75, 1.0), "GOLD": unreal.LinearColor(0.85, 0.68, 0.38, 1.0), "GREY": unreal.LinearColor(0.6, 0.57, 0.5, 1.0)}
def text(n, size, colour, s=None):
    t = get(n)
    f = t.get_editor_property("font")
    f.set_editor_property("size", size)
    t.set_editor_property("font", f)
    t.set_editor_property("color_and_opacity", unreal.SlateColor(COL[colour]))
    if s is not None:
        t.set_editor_property("text", s)
panel = get("Panel")
panel.set_editor_property("brush_color", unreal.LinearColor(0.025, 0.02, 0.016, 0.93))
panel.set_editor_property("padding", unreal.Margin(20, 16, 20, 16))
s = panel.slot
s.set_anchors(unreal.Anchors(unreal.Vector2D(%f, %f), unreal.Vector2D(%f, %f)))
s.set_alignment(unreal.Vector2D(0.5, 0.5))
s.set_position(unreal.Vector2D(0, 0))
s.set_size(unreal.Vector2D(%d, %d))
for n, (size, colour, label) in %r.items():
    if get(n):
        text(n, size, colour, label)
for n in [w for w, c, p in %r if c == "TextBlock" and (w.startswith("ItT") or w.startswith("RowT"))]:
    text(n, 14, "INK", "Item")
for n in [w for w, c, p in %r if c == "Button"]:
    get(n).set_editor_property("background_color", unreal.LinearColor(0.2, 0.16, 0.11, 1.0))
    get(n).slot.set_padding(unreal.Margin(0, 1, 6, 1))
if get("Desc"):
    get("Desc").set_editor_property("auto_wrap_text", True)
OUT["styled"] = True
''' % (path, anchor[0], anchor[1], anchor[0], anchor[1], size[0], size[1], texts, tree, tree), 300))
    print(umg("CompileWidgetBlueprint", {"widgetBlueprint": {"refPath": path}})[:200])


def setup():
    """Variables (only those missing) and functions."""
    variables = {}
    for bp, vs in VARIABLES.items():
        have = set(cr.call("list_variables", {"blueprint": {"refPath": bp}}))
        variables[bp] = [v for v in vs if v[0] not in have]
        print(bp.split(".")[-1], "already has", [v[0] for v in vs if v[0] in have])
    cr.setup(variables, FUNCTIONS, compile_all_after=False)
    for bp in (BOX, WLOOT, WINV, PM, NPC, AL):
        cr.call("compile_blueprint", {"blueprint": {"refPath": bp}})


def defaults():
    """BP_Container's looks: Meshes and Scales on its class defaults."""
    import pyrun
    print(pyrun.run('''
EAL = unreal.EditorAssetLibrary
cdo = unreal.get_default_object(EAL.load_blueprint_class("/Game/Cousland/Areas/BP_Container"))
meshes = [EAL.load_asset(p) if EAL.does_asset_exist(p.split(".")[0]) else None for p in %r]
cdo.set_editor_property("Meshes", [])
cdo.set_editor_property("Meshes", meshes)
cdo.set_editor_property("Scales", [])
cdo.set_editor_property("Scales", [unreal.Vector(s, s, s) for s in %r])
OUT["meshes"] = [m.get_name() if m else None for m in cdo.get_editor_property("Meshes")]
OUT["sizes"] = [[round(x) for x in (m.get_bounds().box_extent.x * 2, m.get_bounds().box_extent.y * 2, m.get_bounds().box_extent.z * 2)] if m else None for m in meshes]
EAL.save_asset("/Game/Cousland/Areas/BP_Container", only_if_is_dirty=False)
''' % ([PROPS % (n, n, n) for n, _ in LOOKS], [s for _, s in LOOKS]), 120))


def patch():
    """The hooks: a fallen creature's drop (KnockOut), the loader (GiveNpcRules, BuildFixtures), right clicks on
    containers (PickBoxOf, CommandThing, HeroUseNow, UseRoute)."""
    d = os.path.join(HERE, "dsl")

    def edit(name, old, new):
        p = os.path.join(d, name + ".dsl")
        s = open(p, encoding="utf-8").read()
        if new in s:
            return
        assert s.count(old) == 1, (name, s.count(old))
        open(p, "w", encoding="utf-8").write(s.replace(old, new))
        print("patched", name)

    open(os.path.join(d, "PickBoxOf.dsl"), "w", encoding="utf-8").write(
        "(fn PickBoxOf (What)\n  (Variabili|Predefinito|ImpostaPickBox)\n"
        "  (bind _box (Utilità|Casting|CastToBP_Container What))\n  (Variabili|Predefinito|ImpostaPickBox _box))\n")
    edit("KnockOut", "  (Classe|BPPlotManager|MemberDown (Variabili|Predefinito|OttieniMgr)))",
         "  (Classe|BPPlotManager|MemberDown (Variabili|Predefinito|OttieniMgr))\n  (Funzionedichiamata|DropLoot))")
    edit("CommandThing", "  (Funzionedichiamata|PickDoorOf :What What)\n  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniPickDoor))",
         "  (Funzionedichiamata|PickDoorOf :What What)\n  (Funzionedichiamata|PickBoxOf :What What)\n"
         "  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Utilità|IsValid (Variabili|Predefinito|OttieniPickDoor)) (Utilità|IsValid (Variabili|Predefinito|OttieniPickBox)))")
    edit("HeroUseNow", "  (Funzionedichiamata|PickDoorOf :What (Variabili|Predefinito|OttieniHeroUse))\n",
         "  (Funzionedichiamata|PickDoorOf :What (Variabili|Predefinito|OttieniHeroUse))\n"
         "  (Funzionedichiamata|PickBoxOf :What (Variabili|Predefinito|OttieniHeroUse))\n")
    edit("UseRoute", "        (:then\n          (Classe|BPDoor|TryUse (Variabili|Predefinito|OttieniPickDoor)))))))",
         "        (:then\n          (Classe|BPDoor|TryUse (Variabili|Predefinito|OttieniPickDoor)))\n"
         "        (:else\n          (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniPickBox))\n"
         "            (:then\n              (Funzionedichiamata|OpenBox :Box (Variabili|Predefinito|OttieniPickBox)))))))))")
    edit("GiveNpcRules", "  (Classe|BPDlgNPC|SetTraits Npc :InTraits (Variabili|Predefinito|OttieniNpcTraits) :K K)\n",
         "  (Classe|BPDlgNPC|SetTraits Npc :InTraits (Variabili|Predefinito|OttieniNpcTraits) :K K)\n"
         "  (Classe|BPDlgNPC|SetLootInfo Npc :InLoot (Variabili|Predefinito|OttieniNpcLoot) :InBag (Variabili|Predefinito|OttieniNpcBag) :K K)\n"
         "  (Classe|BPDlgNPC|SetBagInfo Npc :InBag (Variabili|Predefinito|OttieniNpcBag) :K K)\n")
    fields = ["ItemTags", "ItemNames", "ItemDescs", "ItemStats", "TreasureRanges", "TreasureRows", "Bag", "LootRules",
              "ReactivePotions", "PlayerItems", "PlayerLockpick", "PlayerSpellPower", "NpcLoot", "NpcBag", "ContainerTags",
              "ContainerNames", "ContainerKeys", "ContainerPose", "ContainerInfo", "ContainerLoot", "ContainerBag"]
    edit("BuildFixtures", "  (Funzionedichiamata|GiveTalents)\n",
         "".join('  (Variabili|Predefinito|Imposta%s (Json|GetField _json "%s"))\n' % (f, f) for f in fields)
         + "  (Funzionedichiamata|GiveTalents)\n  (Funzionedichiamata|GiveLoot)\n")


def sources():
    sys.path.insert(0, HERE)
    import loot_dsl as gen  # writes the graphs
    order = ["BOX", "WLOOT", "WINV", "PM", "NPC", "AL"]
    out = [(BPS[b], n, str(gen.fn.path(b, n))) for k in order for b, n in gen.fn.wrote if b == k]
    def where(n):  # dsl/, or dsl/tacrun/ for a graph tactics_run_dsl.py writes
        p = os.path.join(HERE, "dsl", n + ".dsl")
        return p if os.path.exists(p) else os.path.join(HERE, "dsl", "tacrun", n + ".dsl")
    return out + [(bp, n, where(n)) for bp, n in PATCHED]


def graphs(start=None):
    todo = sources()
    if start:
        todo = todo[[n for _, n, _ in todo].index(start):]
    last = None
    for bp, name, path in todo:
        if last and bp != last:
            cr.call("compile_blueprint", {"blueprint": {"refPath": last}})
        last = bp
        r = cr.call("write_graph_dsl", {"graph": {"refPath": "%s:%s" % (bp, name)}, "code": open(path, encoding="utf-8").read()})
        print(name, "ERROR " + str(r)[:400] if "error" in str(r).lower() else "ok", flush=True)
    for bp in (BOX, WLOOT, WINV, PM, NPC, AL):
        print(bp.split(".")[-1], cr.call("compile_blueprint", {"blueprint": {"refPath": bp}}))


def bind():
    """The windows' buttons: WBP_Loot's items ClickIt(k), MoneyB ClickMoney, AllB ClickAll, CloseB ClickClose;
    WBP_Inventory's rows ClickRow(k), CloseB ClickClose."""
    for path, wiring in ((WLOOT, [("It%d" % k, "ClickIt", {"K": k}) for k in range(LOOT_ROWS)]
                          + [("MoneyB", "ClickMoney", {}), ("AllB", "ClickAll", {}), ("CloseB", "ClickClose", {})]),
                         (WINV, [("Row%d" % k, "ClickRow", {"K": k}) for k in range(INV_ROWS)] + [("CloseB", "ClickClose", {})])):
        g = {"refPath": path + ":EventGraph"}

        def events():
            ns = [n for n in cr.call("find_nodes", {"graph": g, "title": ""}) if "ComponentBoundEvent" in n["refPath"]]
            return {i["node"]["refPath"]: i["type_id"] for i in cr.call("get_node_infos", {"nodes": ns})} if ns else {}

        have = events()
        bound = {t.split("(")[-1].rstrip(")") for t in have.values()}
        for n, (button, fn, pins) in enumerate(wiring):
            if button in bound:
                continue
            umg("BindToEventProperty", {"widgetBlueprint": {"refPath": path}, "eventName": "OnClicked",
                                        "propertyName": button, "propertyClass": {"refPath": BUTTON}})
            now = events()
            new = [k for k in now if k not in have]
            have = now
            if not new:
                print("no event node for", button, flush=True)
                continue
            pos = {"x": 760, "y": 200 * n}
            call = cr.call("create_node", {"graph": g, "type_id": "Funzionedichiamata|" + fn, "pos": pos})
            out = [p for p in cr.pins({"refPath": new[0]})["output_pins"] if p["name"] == "then"]
            ins = {p["name"]: p["pin_id"] for p in cr.pins(call)["input_pins"]}
            cr.call("connect_pins", {"output_pin": out[0]["pin_id"], "input_pin": ins["execute"]})
            for k, v in pins.items():
                cr.call("set_pin_value", {"pin": ins[k], "value": str(v)})
            print("bound", path.split(".")[-1], button, "->", fn, pins, flush=True)
        print(umg("CompileWidgetBlueprint", {"widgetBlueprint": {"refPath": path}})[:200])


def input_events():
    """BP_PlotManager's IA_Inventory -> ToggleInventory."""
    g = {"refPath": PM + ":EventGraph"}
    if cr.call("find_nodes", {"graph": g, "title": "IA_Inventory"}):
        print("IA_Inventory already there")
        return
    types = cr.call("find_node_types", {"graph": g, "type_id_filter": "IA_Inventory", "context_pins": []})
    ids = [t.get("type_id", t) if isinstance(t, dict) else t for t in types]
    ev = cr.call("create_node", {"graph": g, "type_id": next(i for i in ids if i.endswith("IA_Inventory")),
                                 "pos": {"x": 1600, "y": 7600}})
    call = cr.call("create_node", {"graph": g, "type_id": "Funzionedichiamata|ToggleInventory", "pos": {"x": 2020, "y": 7600}})
    started = next(p for p in cr.pins(ev)["output_pins"] if p["name"] == "Started")
    ins = {p["name"]: p["pin_id"] for p in cr.pins(call)["input_pins"]}
    cr.call("connect_pins", {"output_pin": started["pin_id"], "input_pin": ins["execute"]})
    print("IA_Inventory -> ToggleInventory", cr.call("compile_blueprint", {"blueprint": {"refPath": PM}}))


def save():
    import pyrun
    print(pyrun.run('''
EAL = unreal.EditorAssetLibrary
OUT["saved"] = [EAL.save_asset(p, only_if_is_dirty=False) for p in ("/Game/Cousland/Areas/BP_Container",
                "/Game/Cousland/Combat/WBP_Loot", "/Game/Cousland/Combat/WBP_Inventory", "/Game/Cousland/Plots/BP_PlotManager",
                "/Game/Cousland/Dialogue/BP_DlgNPC", "/Game/Cousland/Areas/BP_AreaLoader", "/Game/Cousland/Combat/WBP_Tactics")]
''', 300))


if __name__ == "__main__":
    ue.init()
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    if phase == "graphs" and len(sys.argv) > 2:
        graphs(sys.argv[2])
    else:
        for name, f in (("assets", assets), ("setup", setup), ("defaults", defaults), ("patch", patch), ("graphs", graphs),
                        ("bind", bind), ("input", input_events), ("save", save)):
            if phase in (name, "all"):
                f()
