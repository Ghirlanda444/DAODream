"""python talents.py [assets|hud|setup|graphs|input|defaults|save|all]: combat stage 2 in the Blueprints, stamina and
the player's talents (docs/COMBAT.md, "Talents"; the rules: tools/daotools/abilities.py). Play/Simulate stopped.

The area export brings PlayerTalents (abilities.TALENT_FIELDS, 12 floats a talent), PlayerPassives (ids),
PlayerTalentNames, NpcStatus (per creature: level, effect duration scale, percent it resists the player's
knockdown) and PlayerStats 13-18 (fatigue, level, displacement, rogue, shield damage). BP_AreaLoader.BuildFixtures
reads them: GiveTalents hands the talents to BP_PlotManager.SetPlayerTalents, GiveNpcRules each creature its status
(BP_DlgNPC.SetStatus); SetPlayerStats -> SetPlayerTalentStats fills the stamina pool.

BP_PlotManager: keys 1-6 (IA_Talent1-6 in IMC_Dialogue) call UseTalent(slot). TalentCheck: off cooldown (TReady),
then a sustained talent toggles (ToggleSustained: upkeep off the pool's maximum PPool, fatigue added, TUntil
1e9 while on), an activated one costs its cost x (1 + fatigue/100), rounded (TryActivated): Taunt and Disengage
only cost (threat: stage 4), Perfect Strike and Tricks of the Trade are buffs for their seconds (TUntil), the rest
need a target: the nearest visible live hostile within 2.3 m (FindTarget, TalentBid -> BP_DlgNPC.TalentOffer; PlayerAttack's own pick
also keeps away from foes a party member fights): Dirty Fighting stuns it (BP_DlgNPC.Stun: seconds + 1 a missing
party member, x its DurScale), Shield Bash and Below the Belt strike it through TakeAttack -> PlayerStrike with
their attack bonus (TBonus; Shield Bash with the shield's damage, TOff), and on a hit knock it down (Knock:
resisted at its Resist percent; A_Fallen for the seconds and up to one more) or slow it (Slow: half chase speed).
SumOwn adds up what the running talents give (OwnAtk, OwnPen, OwnCrit; OwnSpeed scales PInterval from
PBaseInterval, capped 0.5-1.5); StaminaTick (every 0.5 s) brings back 1 stamina a second in combat (4 s after the
last blow) and 17.5 out of it and redraws the HUD (WBP_CombatHUD.SetStamina, SetTalents). PlayerStrike adds
Bravery's critical chance (3.5 a hostile on the player past two; PlayerAttackers leaves out the hostile that
counted, so PlayerAttackers - 1), a rogue's backstab (ResolveHit: Backstab with flanking, or StunStab on a
stunned target with Coup de Grace, makes a hit critical) and Death Blow's stamina from a kill; StrikePlayer
lets Evasion's displacement (PDisplace) make a hostile's attack miss outright. A stunned or knocked down
hostile skips its turn (HostileTick; the old body is HostileTurn) and gets up when it ends (Recover).
"""
import os
import sys

import combat_rules as cr
import ue

PM, NPC, AL = cr.PM, cr.NPC, cr.AL
HUD = "/Game/Cousland/Combat/WBP_CombatHUD.WBP_CombatHUD"
F, ACTOR, NPC_CLASS = "float", cr.ACTOR, cr.NPC_CLASS
SLOTS = 6  # hotkeys 1-6

VARIABLES = {
    PM: [("PStamina", F), ("PPool", F), ("PFatigue", F), ("PLevel", F), ("PDisplace", F), ("bRogue", "bool"),
         ("POffMin", F), ("POffMax", F), ("PBaseInterval", F), ("Talents", F, "ARRAY"), ("TReady", F, "ARRAY"),
         ("TUntil", F, "ARRAY"), ("Passives", F, "ARRAY"), ("TalentNames", "string", "ARRAY"), ("TSlot", "int"),
         ("TId", F), ("TUse", F), ("TCost", F), ("TCool", F), ("TUpkeep", F), ("TFatigue", F), ("TAtkBonus", F),
         ("TSeconds", F), ("TCostNow", F), ("TBonus", F), ("bTOff", "bool"), ("OwnAtk", F), ("OwnPen", F),
         ("OwnSpeed", F), ("OwnCrit", F), ("BraveryCrit", F), ("bBackstab", "bool"), ("bStunStab", "bool"),
         ("PartySize", "int"), ("TalentText", "string")],
    NPC: [("StunUntil", F), ("KnockUntil", F), ("SlowUntil", F), ("NLevel", F), ("DurScale", F), ("Resist", F),
          ("bKnocked", "bool")],
    AL: [("NpcStatus", F, "ARRAY"), ("PlayerTalents", F, "ARRAY"), ("PlayerPassives", F, "ARRAY"),
         ("PlayerTalentNames", "string", "ARRAY")],
}
FUNCTIONS = {
    HUD: {"SetStamina": [("Pct", F), ("Txt", "string")], "SetTalents": [("Txt", "string")]},
    NPC: {"SetStatus": [("InStatus", "float[]"), ("K", "int")], "Stun": [("Seconds", F), ("PartySize", "int")],
          "Slow": [("Seconds", F), ("PartySize", "int")], "Knock": [("Seconds", F)], "Recover": [],
          "SayText": [("Txt", "string")], "HostileTurn": [("Dt", F)], "TalentOffer": [("InMgr", PM + "_C")]},
    PM: {"SetPlayerTalentStats": [("InStats", "float[]")],
         "SetPlayerTalents": [("InTalents", "float[]"), ("InPassives", "float[]"), ("InNames", "string[]")],
         "LoadTalent": [("Slot", "int")], "UseTalent": [("Slot", "int")], "TalentCheck": [("Slot", "int")],
         "AfterTalent": [("Txt", "string")], "ToggleSustained": [], "TryActivated": [], "PayTalent": [],
         "ActivateTalent": [], "FindTarget": [], "TalentBid": [("Npc", NPC_CLASS)], "TargetTalent": [], "CountParty": [],
         "CountMember": [("Npc", NPC_CLASS)], "HitTalent": [], "StrikeTalent": [], "TalentAfterHit": [],
         "Bravery": [], "DeathBlow": [("Target", NPC_CLASS)], "SumOwn": [], "AddOwn": [("Slot", "int")],
         "StaminaTick": [], "ShowStamina": [], "ShowTalents": [], "AddTalentLine": [("Slot", "int")]},
    AL: {"GiveTalents": []},
}
# Written from dsl/, callees first.
GRAPHS = [
    (HUD, ["SetStamina", "SetTalents"]),
    (NPC, ["SetStatus", "SayText", "Stun", "Slow", "Knock", "Recover", "HostileTurn", "HostileTick", "ChaseFoe",
          "TalentOffer"]),
    (PM, ["SetPlayerTalentStats", "AddOwn", "SumOwn", "ShowStamina", "AddTalentLine", "ShowTalents", "AfterTalent",
          "LoadTalent", "PayTalent", "CountMember", "CountParty", "TalentBid", "FindTarget", "ToggleSustained", "Bravery",
          "DeathBlow", "ResolveHit", "StrikePlayer", "PlayerStrike", "TalentAfterHit", "StrikeTalent", "HitTalent",
          "TargetTalent", "ActivateTalent", "TryActivated", "TalentCheck", "UseTalent", "SetPlayerTalents",
          "StaminaTick", "SetPlayerStats"]),
    (AL, ["GiveTalents", "GiveNpcRules", "BuildFixtures"]),
]
KEYS = ["One", "Two", "Three", "Four", "Five", "Six"]


def assets():
    """IA_Talent1-6 (digital) and their keys 1-6 in IMC_Dialogue, next to IA_Attack."""
    import pyrun
    print(pyrun.run('''
EAL = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
factory = getattr(unreal, "InputAction_Factory", None) or getattr(unreal, "InputActionFactory")
imc = EAL.load_asset("/Game/Cousland/Dialogue/IMC_Dialogue")
have = {(m.action.get_name() if m.action else "", str(m.key.get_editor_property("key_name")))
        for m in imc.get_editor_property("default_key_mappings").get_editor_property("mappings")}
done = []
for k, key in enumerate(%r, 1):
    path = "/Game/Cousland/Combat/IA_Talent%%d" %% k
    ia = EAL.load_asset(path) if EAL.does_asset_exist(path) else tools.create_asset("IA_Talent%%d" %% k, "/Game/Cousland/Combat", unreal.InputAction, factory())
    if (ia.get_name(), key) not in have:
        kk = unreal.Key()
        kk.set_editor_property("key_name", key)
        imc.map_key(ia, kk)
    EAL.save_asset(path, only_if_is_dirty=False)
    done.append(path)
EAL.save_asset("/Game/Cousland/Dialogue/IMC_Dialogue", only_if_is_dirty=False)
OUT["assets"] = done
''' % KEYS, 300))


def hud():
    """Under the health bar: a stamina label and bar (green), and a line of talents with their keys."""
    widget = {"refPath": HUD}
    tree = ue.call("UMGToolSet.UMGToolSet", "GetWidgets", {"widgetBlueprint": widget})
    if "StaminaBar" in tree:
        print("hud: already there")
        return
    box = {"refPath": HUD + ":WidgetTree.HealthBox"}
    for cls, name in (("/Script/UMG.TextBlock", "StaminaLabel"), ("/Script/UMG.ProgressBar", "StaminaBar"),
                      ("/Script/UMG.TextBlock", "TalentLabel")):
        r = ue.call("UMGToolSet.UMGToolSet", "AddWidget", {"widgetBlueprint": widget, "widgetClass": {"refPath": cls},
                                                          "widgetDisplayName": name, "parentWidget": box,
                                                          "childIndex": -1})
        print(name, r[:200])
        ue.call("UMGToolSet.UMGToolSet", "ToggleWidgetAsVariable", {
            "widgetBlueprint": widget, "widget": {"refPath": HUD + ":WidgetTree." + name}, "bIsVariable": True})
    import pyrun
    print(pyrun.run('''
p = "/Game/Cousland/Combat/WBP_CombatHUD.WBP_CombatHUD:WidgetTree."
bar = unreal.find_object(None, p + "StaminaBar")
bar.set_editor_property("fill_color_and_opacity", unreal.LinearColor(0.2, 0.65, 0.2, 1.0))
bar.set_editor_property("percent", 1.0)
unreal.find_object(None, p + "StaminaLabel").set_editor_property("text", "Stamina")
talents = unreal.find_object(None, p + "TalentLabel")
talents.set_editor_property("text", "")
talents.set_editor_property("auto_wrap_text", True)
slot = unreal.find_object(None, p + "Root.CanvasPanelSlot_0")
layout = slot.get_editor_property("layout_data")
offsets = layout.get_editor_property("offsets")
offsets.set_editor_property("right", 520.0)
offsets.set_editor_property("bottom", 180.0)
layout.set_editor_property("offsets", offsets)
slot.set_editor_property("layout_data", layout)
OUT["ok"] = 1
''', 120))
    print(ue.call("UMGToolSet.UMGToolSet", "CompileWidgetBlueprint", {"widgetBlueprint": widget})[:200])


def setup():
    cr.setup(VARIABLES, FUNCTIONS, compile_all_after=False)
    for bp in (HUD, NPC, PM, AL):
        cr.call("compile_blueprint", {"blueprint": {"refPath": bp}})


def graphs():
    for bp, names in GRAPHS:
        for fn in names:
            code = open(os.path.join(cr.HERE, "dsl", fn + ".dsl"), encoding="utf-8").read()
            r = cr.call("write_graph_dsl", {"graph": {"refPath": "%s:%s" % (bp, fn)}, "code": code})
            print(fn, str(r)[:300])
        cr.call("compile_blueprint", {"blueprint": {"refPath": bp}})


def input_events():
    """In BP_PlotManager's event graph: IA_Talent<k> Started -> UseTalent(k - 1)."""
    g = {"refPath": PM + ":EventGraph"}
    have = {n["refPath"] for n in cr.call("find_nodes", {"graph": g, "title": "IA_Talent"})}
    if have:
        print("input: %d talent events already there" % len(have))
        return
    for k in range(1, SLOTS + 1):
        types = cr.call("find_node_types", {"graph": g, "type_id_filter": "IA_Talent%d" % k, "context_pins": []})
        ids = [t.get("type_id", t) if isinstance(t, dict) else t for t in types]
        event_id = next(i for i in ids if i.endswith("IA_Talent%d" % k))
        pos = {"x": 1600, "y": 2400 + 260 * k}
        ev = cr.call("create_node", {"graph": g, "type_id": event_id, "pos": pos})
        use = cr.call("create_node", {"graph": g, "type_id": "Funzionedichiamata|UseTalent",
                                      "pos": {"x": pos["x"] + 420, "y": pos["y"]}})
        started = next(p for p in cr.pins(ev)["output_pins"] if p["name"] == "Started")
        ins = {p["name"]: p["pin_id"] for p in cr.pins(use)["input_pins"]}
        cr.call("connect_pins", {"output_pin": started["pin_id"], "input_pin": ins["execute"]})
        cr.call("set_pin_value", {"pin": ins["Slot"], "value": str(k - 1)})
        print("IA_Talent%d -> UseTalent(%d)" % (k, k - 1))
    cr.call("compile_blueprint", {"blueprint": {"refPath": PM}})


def defaults():
    """A creature without a status from the export keeps durations as they are (DurScale 1)."""
    import pyrun
    print(pyrun.run('''
cls = unreal.EditorAssetLibrary.load_asset("/Game/Cousland/Dialogue/BP_DlgNPC").generated_class()
unreal.get_default_object(cls).set_editor_property("DurScale", 1.0)
OUT["ok"] = 1
''', 120))


def save():
    import pyrun
    print(pyrun.run('''
EAL = unreal.EditorAssetLibrary
OUT["saved"] = [EAL.save_asset(p, only_if_is_dirty=False) for p in ("/Game/Cousland/Plots/BP_PlotManager",
                "/Game/Cousland/Dialogue/BP_DlgNPC", "/Game/Cousland/Areas/BP_AreaLoader",
                "/Game/Cousland/Combat/WBP_CombatHUD")]
''', 300))


if __name__ == "__main__":
    ue.init()
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, f in (("assets", assets), ("hud", hud), ("setup", setup), ("graphs", graphs),
                    ("input", input_events), ("defaults", defaults), ("save", save)):
        if phase in (name, "all"):
            f()
