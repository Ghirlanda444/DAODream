"""python tactics_run.py [setup|graphs|save|all] [first graph]: the tactics as the original runs them (docs/COMBAT.md,
"Tactics in full"). Play/Simulate stopped; tactics_screen.py must have run. The graphs come from dsl/ and dsl/tacrun/
(written by tactics_run_dsl.py: run it first).

BP_PlotManager.TacPick(target, base, parameter, command, ability) is daotools tactics.pick_target: who a row is aimed
at (PkWho, none when its condition does not hold). TrGather(Me) first lists, once a round, the creatures around
whoever runs its tactics: its group's five nearest (AllyL), the five nearest hostiles (EnL, a party member's cut at
the first one too far from the one in control: 30 m, 15 for a behaviour that does not chase), every hostile in the
fight (EnAll), the hostiles within reach (RingN) and the dead among the five nearest creatures (DeadN). TrPeek(A)
reads one creature (Pk*: alive, side, health, stamina, target, attack type, traits, statuses). The base conditions
are TrB<base>, each a search over the row's list (TrList: Self, Ally, Enemy, Most hated, the hero, the one in
control, a party member by name: FOLLOWER_BASE + its area index, NIndex).

BP_DlgNPC: ChooseTactic gathers, TacticRow asks TacPick (TacticPick), TacticAct acts on TacWho: an attack or a talent
on a hostile makes it the foe (TacRetarget: too far, and the round strikes nothing while it walks there; a party
member's Target too), a talent on a friend goes to it (TacOn: Heal, EffHeal); Wait spends the round, Deactivate mode
turns a mode off (ModeOff). Party members out of reach of a foe run their rows each attack interval all the same
(PartyAct -> SupportTick -> SupportRound): a talent on a friend at once, a hostile becomes the target (an ability
row queued as an order, PendingSlot). Behaviours (Behavior, the hero's PBehavior; aibehaviors' flags, TrFlag):
AttackOnCombatStart off keeps members out of the fight until the one in control attacks or a party member is hurt
(PartyMayAttack: MayAttack, cleared when no hostile is left around the one in control, MayAttackTick); DefaultAttack off: no new target from the
bids (BidChoose), AttackBack picks one attacking it; ChaseEnemy; AvoidNearbyEnemies and AvoidMeleeEnemies step 5 m
away (Behave, BackAway: FleeGoal). The hero's rows run the same way (HeroTactics, HeroTacticPick, HeroTacticUse:
Wait, Jump, weapon sets, Deactivate mode).

BP_AreaLoader reads NpcTraits (SetTraits: NTraits, NIndex), PlayerTraits and the menu's commands, presets,
behaviours and buff list (SetTacticExtra).
"""
import os
import sys

import combat_rules as cr

import ue

PM, NPC, AL = cr.PM, cr.NPC, cr.AL
NPC_CLASS, A = cr.NPC_CLASS, cr.ACTOR
F, I, B, STR, VEC = "float", "int", "bool", "string", "vector"
HERE = os.path.dirname(os.path.abspath(__file__))

VARIABLES = {
    PM: [(n, A) for n in ("TMe", "TMeTgt", "TMeHated", "TCtrl", "PkTgt", "PkWho", "PkMem", "HTWho")]
        + [(n, A, "ARRAY") for n in ("AllyL", "EnL", "EnAll", "CL", "CL2")]
        + [(n, F, "ARRAY") for n in ("AllyD", "EnD", "NearD", "TCommands", "TPresets", "TPresetRows", "TBehaviors",
                                     "TBuffs", "PTraits")]
        + [("NearDead", B, "ARRAY")]
        + [(n, STR, "ARRAY") for n in ("TPresetNames", "TBehaviorNames", "TBehaviorTexts")]
        + [(n, I) for n in ("TMeSide", "TMeBeh", "PkSide", "PkAtk", "PkClass", "PkRace", "PkGender", "PkRank", "PkArmor",
                            "PkN", "PkIns", "RingN", "DeadN", "PBehavior")]
        + [(n, F) for n in ("TReach", "PkHp", "PkMax", "PkPct", "PkSta", "PkBest", "TT", "TB", "TP", "TC", "TS",
                            "MayAttackAt", "HTNext", "MayCheckAt", "PkBestD")]
        + [(n, B) for n in ("TMeParty", "TMeChase", "PkAlive", "PkVis", "PkStun", "PkKnock", "PkRoot", "PkSlow",
                            "PkBuff", "BF", "BFoe", "PartyMayAttack", "PFall", "BMayH")]
        + [("PkLoc", VEC)],
    NPC: [("TacWho", A), ("TacOn", A), ("NTraits", F, "ARRAY"), ("Behavior", I), ("NIndex", I), ("SupportTimer", F),
          ("HealAmt", F), ("BFlag", B), ("BMay", B), ("Hid", B)],
    AL: [(n, F, "ARRAY") for n in ("NpcTraits", "PlayerTraits", "TacticCommands", "TacticPresets", "TacticPresetRows",
                                   "TacticBehaviors", "TacticBuffs")]
        + [(n, STR, "ARRAY") for n in ("TacticPresetNames", "TacticBehaviorNames", "TacticBehaviorTexts")],
}
K = [("K", I)]
FUNCTIONS = {
    PM: dict([(n, [("A", A)]) for n in ("TrPeek", "TrPeekCast", "TrFoeTest", "TrMeInfo", "TrMeInfoCast", "TrGatherOne",
                                         "TrSort", "TrAddValid", "TrBuffOf", "TrBuffCast")]
             + [(n, [("K", I), ("D", F)]) for n in ("TrInsNearLess", "TrInsAllyLess", "TrInsEnLess")]
             + [(n, K) for n in ("TrDeadOne", "TrEngOne", "TrWound",
                                 "TrTryStatus", "TrTryHp", "TrTrySta", "TrTryLow", "TrTryClus", "TrTryRace", "TrTryClass",
                                 "TrTryGender", "TrTryAtkMem", "TrBuffP", "TrTryBuff", "TrTryArmor", "TrTryUsing",
                                 "TrCntArmorEnAll", "TrCntArmorEnL", "TrCntAtkEnAll", "TrCntAtkEnL", "TrTryRank",
                                 "TrAtkSelf", "TrAtkEn", "TrAtkEnA", "TrAtkAl", "TrAtkAlE", "TrAtkMem", "TrTryBand",
                                 "TrTryRgd")]
             + [(n, [("I", I)]) for n in ("HeroTacticPick", "HeroTacticRow", "HeroTacticUse", "HeroJump", "HeroSwitchSet",
                                         "HeroTacticTalent", "HeroModeOff", "HeroItem")]
             + [(n, [("Follower", NPC_CLASS)]) for n in ("AssignByBid", "BidChoose", "BidAttack", "BidReach", "BidKeep")]
             + [(n, []) for n in ("TrPeekPlayer", "TrCtrl", "TrCutEn5", "TrCutAlly5", "TrCountDead", "TrEngage", "TrList",
                                  "TrHealFilter", "TrPostHeal", "TrHated", "TrOwnChk", "TrOwn", "TrMember", "TrBuffOwn",
                                  "TrArmorH", "TrUsingH", "TrAtkHated", "TrWhoFor", "TrBandH", "TrSwitch", "TrSwitchLo",
                                  "TrSwitchHi", "MayAttack", "MayAttackTick", "HeroTactics", "HeroAim", "HeroBidGate")]
             + [("TrB%d" % b, []) for b in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 19, 20, 21, 22, 23, 24,
                                             25, 26, 27, 28, 29, 31, 32, 33, 34, 35, 36)]
             + [("TrPeekNpc", [("N", NPC_CLASS)]), ("TrMeInfoNpc", [("N", NPC_CLASS)]), ("TrBuffNpc", [("N", NPC_CLASS)]),
                ("TrBuffN", [("N", NPC_CLASS), ("K", I)]), ("TrTraits", [("T", "float[]")]),
                ("TrFlag", [("B", I), ("Fl", I)]), ("TrGather", [("Me", A)]), ("TrInsNear", [("D", F)]),
                ("TrInsAlly", [("A", A), ("D", F)]), ("TrInsEn", [("A", A), ("D", F)]), ("TrAddFollower", [("Idx", I)]),
                ("TrFolOne", [("A", NPC_CLASS), ("Idx", I)]), ("TrClusOne", [("K", I), ("J", I)]),
                ("TacPick", [(n, F) for n in ("Tgt", "Base", "Param", "Cmd", "Sub")]), ("HealPlayer", [("Amount", F)]),
                ("SetPBehavior", [("B", I)]),
                ("SetTacticExtra", [(n, "float[]") for n in ("InCommands", "InPresets", "InPresetRows")]
                 + [("InPresetNames", "string[]"), ("InBehaviors", "float[]"), ("InBehaviorNames", "string[]"),
                    ("InBehaviorTexts", "string[]"), ("InBuffs", "float[]"), ("InTraits", "float[]")])]),
    NPC: dict([(n, []) for n in ("TacticPick", "ChooseRows", "TacAim", "TacRetarget", "TacTooFar", "TacSetTarget",
                                 "ModeOffGo", "SupportRound", "SupportGo", "MayFight", "SupportAct", "AttackBackCheck",
                                 "Behave", "BehaveMelee", "CtrlMay", "PartyHurt", "HidCheck")]
              + [("ModeOff", [("Ability", F)]), ("EffHeal", K), ("HealWho", [("A", A)]), ("HealCast", [("A", A)]),
                 ("GainHealth", [("Amount", F)]), ("NFlag", [("Fl", I)]), ("SupportTick", [("Dt", F)]),
                 ("BackOne", K), ("BackAway", [("From", A)]), ("SetTraits", [("InTraits", "float[]"), ("K", I)]),
                 ("TraitOne", [("InTraits", "float[]"), ("I", I), ("K", I)]), ("SetBehavior", [("B", I)])]),
}


def sources():
    """(blueprint, graph) in build order: the manager's, then the creatures', then the loader's."""
    sys.path.insert(0, HERE)
    import tactics_run_dsl as gen  # writes the graphs
    bp_of = {"PM": PM, "NPC": NPC}
    out = [(bp_of[b], n) for n, b in gen.WROTE.items() if b == "PM"] + [(bp_of[b], n) for n, b in gen.WROTE.items() if b == "NPC"]
    out += [(PM, n) for n in ("PlayerAttackNow", "HurtPlayer", "StunPlayer", "HeroTick", "HeroBid")]
    out += [(NPC, n) for n in ("TalentEffect6", "SayTalent", "PartyAct", "TakeHit", "CombatRound")]
    out += [(AL, n) for n in ("GiveNpcRules", "BuildFixtures", "GiveTalents")]
    return out


def path_of(name):
    p = os.path.join(HERE, "dsl", name + ".dsl")
    return p if os.path.exists(p) else os.path.join(HERE, "dsl", "tacrun", name + ".dsl")


def setup():
    """Variables (only those missing: adding one twice makes a copy with a suffix) and functions."""
    variables = {}
    for bp, vs in VARIABLES.items():
        have = set(cr.call("list_variables", {"blueprint": {"refPath": bp}}))
        variables[bp] = [v for v in vs if v[0] not in have]
    cr.setup(variables, FUNCTIONS, compile_all_after=False)
    for bp in (PM, NPC, AL):
        cr.call("compile_blueprint", {"blueprint": {"refPath": bp}})


def graphs(start=None):
    todo = sources()
    if start:
        todo = todo[[n for _, n in todo].index(start):]
    done_bp = None
    for bp, name in todo:
        if done_bp and bp != done_bp:
            cr.call("compile_blueprint", {"blueprint": {"refPath": done_bp}})
        done_bp = bp
        code = open(path_of(name), encoding="utf-8").read()
        r = cr.call("write_graph_dsl", {"graph": {"refPath": "%s:%s" % (bp, name)}, "code": code})
        bad = "error" in str(r).lower()
        print(name, "ERROR " + str(r)[:400] if bad else "ok", flush=True)
    for bp in (PM, NPC, AL):
        cr.call("compile_blueprint", {"blueprint": {"refPath": bp}})


def save():
    import pyrun
    print(pyrun.run('''
EAL = unreal.EditorAssetLibrary
OUT["saved"] = [EAL.save_asset(p, only_if_is_dirty=False) for p in ("/Game/Cousland/Plots/BP_PlotManager",
                "/Game/Cousland/Dialogue/BP_DlgNPC", "/Game/Cousland/Areas/BP_AreaLoader")]
''', 300))


if __name__ == "__main__":
    ue.init()
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    if phase == "graphs" and len(sys.argv) > 2:
        graphs(sys.argv[2])
    else:
        for name, f in (("setup", setup), ("graphs", graphs), ("save", save)):
            if phase in (name, "all"):
                f()
