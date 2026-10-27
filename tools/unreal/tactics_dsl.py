"""python tactics_dsl.py: writes dsl/tactics/*.dsl, WBP_Tactics' graphs (tactics_screen.py builds them in). They are
many small functions alike, so they are written from here: edit this, not the .dsl files."""
from pathlib import Path

OUT = Path(__file__).resolve().parent / "dsl" / "tactics"
OUT.mkdir(exist_ok=True)
ROWS, OPTS, TABS = 12, 32, 4


def V(n):  # one of the widget's own variables
    return "(Variabili|Predefinito|Ottieni%s)" % n


def S(n, x):
    return "(Variabili|Predefinito|Imposta%s %s)" % (n, x)


def W(n):  # a widget of the tree
    return "(Variabili|WBP_Tactics|Ottieni%s)" % n


def get(arr, i):
    return "(Utilità|Array|Ottieni(unacopia) %s %s)" % (arr, i)


def add(a, b):
    return "(Utility|Operatori|Aggiungi %s %s)" % (a, b)


def mul(a, b):
    return "(Utility|Operatori|Moltiplica %s %s)" % (a, b)


def sub(a, b):
    return "(Utility|Operatori|Sottrai %s %s)" % (a, b)


def div(a, b):
    return "(Utility|Operatori|Dividi %s %s)" % (a, b)


def NOT(a):
    return "(Matematica|Booleano|NOTBoolean %s)" % a


def eq(a, b):
    return "(Utility|Operatori|Uguale(==) %s %s)" % (a, b)


def lt(a, b):
    return "(Utility|Operatori|Minore(<) %s %s)" % (a, b)


def gt(a, b):
    return "(Utility|Operatori|Maggiore(>) %s %s)" % (a, b)


def AND(*xs):
    out = xs[0]
    for x in xs[1:]:
        out = "(Matematica|Booleano|ANDBoolean %s %s)" % (out, x)
    return out


def OR(*xs):
    out = xs[0]
    for x in xs[1:]:
        out = "(Matematica|Booleano|ORBoolean %s %s)" % (out, x)
    return out


def length(a):
    return "(Utilità|Array|Length %s)" % a


def last(a):
    return sub(length(a), 1)


def call(fn, **kw):
    return "(Funzionedichiamata|%s%s)" % (fn, "".join(" :%s %s" % (k, v) for k, v in kw.items()))


def text(widget, s):
    return "(Widget|SetText(Text) %s (Utilità|Testo|ToText(String) %s))" % (widget, s)


def vis(widget, on):
    return '(Widget|SetVisibility %s "%s")' % (widget, "Visible" if on else "Collapsed")


def branch(cond, then=None, els=None, ind="  "):
    s = "%s(Utilità|ControlloDiFlusso|Ramo %s" % (ind, cond)
    if then:
        s += "\n%s  (:then\n%s)" % (ind, "\n".join(ind + "    " + x for x in then))
    if els:
        s += "\n%s  (:else\n%s)" % (ind, "\n".join(ind + "    " + x for x in els))
    return s + ")"


def loop(last_index, body, ind="  ", done=None):
    s = "%s(Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex %s\n%s  (:LoopBody\n%s    %s)" % (
        ind, last_index, ind, ind, body)
    if done:
        s += "\n%s  (:Completed\n%s)" % (ind, "\n".join(ind + "    " + x for x in done))
    return s + ")"


def fn(name, params, *lines):
    src = "(fn %s (%s)\n%s)\n" % (name, " ".join(params), "\n".join(l if l.startswith(" ") else "  " + l for l in lines))
    (OUT / (name + ".dsl")).write_text(src, encoding="utf-8")


def row(n, r="R"):  # cell n of row r of the working copy
    return get(V("Rows"), add(mul(r, 6), n))


def set_cell(n, value, r=None):
    r = r or V("EditRow")
    return "(Utilità|Array|SetArrayElem %s %s %s)" % (V("Rows"), add(mul(r, 6), n), value)


CH = gt(row(5), 0.0)  # the row is used: its chance

# --- the widgets in arrays ---------------------------------------------------------------------------------------
lines = []
for r in range(ROWS):
    for arr, w in (("TgtTs", "TgtT"), ("CndTs", "CndT"), ("ActTs", "ActT"), ("NumTs", "NumT"), ("RowBs", "Row")):
        lines.append("(Utilità|Array|Add %s %s)" % (V(arr), W("%s%d" % (w, r))))
for k in range(OPTS):
    lines += ["(Utilità|Array|Add %s %s)" % (V("OptTs"), W("OptT%d" % k)),
              "(Utilità|Array|Add %s %s)" % (V("OptBs"), W("Opt%d" % k))]
for k in range(TABS):
    lines += ["(Utilità|Array|Add %s %s)" % (V("MemTs"), W("MemT%d" % k)),
              "(Utilità|Array|Add %s %s)" % (V("MemBs"), W("Mem%d" % k))]
fn("Collect", [], *lines)
fn("CollectOnce", [], branch(eq(length(V("TgtTs")), 0), [call("Collect")]))

# --- opening: the menu's lists, the party, the hero first ------------------------------------------------------
M = V("Mgr")
fn("Open", ["InMgr"], S("Mgr", "InMgr"), call("CollectOnce"), call("LoadMenu"), call("ListMembers"),
   call("DrawTabs"), call("ShowMember", K=0))
fn("LoadMenu", [],
   *[S(a, "(Classe|BPPlotManager|Ottieni%s %s)" % (b, M)) for a, b in (
       ("TTargets", "TTargets"), ("TTargetNames", "TTargetNames"), ("TBases", "TBases"), ("TBaseNames", "TBaseNames"),
       ("TConds", "TConds"), ("TCondNames", "TCondNames"), ("TCmds", "TCommands"), ("TCmdNames", "TCommandNames"),
       ("TPresets", "TPresets"), ("TPresetRows", "TPresetRows"), ("TPresetNames", "TPresetNames"),
       ("TBehavNames", "TBehaviorNames"))],
   S("AttackName", '"Attack"'),
   branch(gt(length("(Classe|BPPlotManager|OttieniTCommandNames %s)" % M), 0),
          [S("AttackName", get("(Classe|BPPlotManager|OttieniTCommandNames %s)" % M, 0))]))
fn("ListMembers", [], "(Utilità|Array|Clear %s)" % V("Members"),
   '(bind _all (Attore|GetAllActorsOfClass "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"))',
   "(for _a _all\n    %s)" % call("MemberOffer", A="_a"))
fn("MemberOffer", ["A"], branch(AND(AND("(Classe|BPDlgNPC|OttieniInParty A)", "(Matematica|Booleano|NOTBoolean (Classe|BPDlgNPC|OttieniDead A))"),
                                    lt(length(V("Members")), TABS - 1)),
                                ["(Utilità|Array|Add %s A)" % V("Members")]))
fn("TabName", ["K"], branch(eq("K", 0), [S("MName", '"Hero"')],
                            [S("MName", "(Classe|BPDlgNPC|OttieniDisplayName %s)" % get(V("Members"), sub("K", 1)))]))
fn("DrawTabs", [], loop(TABS - 1, call("DrawTab", K="_index")))
fn("DrawTab", ["K"],
   branch("(Utility|Operatori|Minoreuguale(<=) K %s)" % length(V("Members")),
          [call("TabName", K="K"), vis(get(V("MemBs"), "K"), True), text(get(V("MemTs"), "K"), V("MName"))],
          [vis(get(V("MemBs"), "K"), False)]))

# --- a member: its rows, its slots, its talents --------------------------------------------------------------------
fn("ShowMember", ["K"], branch(lt("K", add(length(V("Members")), 1)), [
    S("MemberIdx", "K"), call("TabName", K="K"), call("LoadRows"), call("LoadTalents"), call("LoadSetup"),
    call("ClosePick"), call("Redraw")]))
NPC = get(V("Members"), sub(V("MemberIdx"), 1))
fn("LoadRows", [], branch(eq(V("MemberIdx"), 0),
                          [S("Rows", "(Classe|BPPlotManager|OttieniPTactics %s)" % M), S("Slots", "(Classe|BPPlotManager|OttieniPSlots %s)" % M)],
                          [S("Rows", "(Classe|BPDlgNPC|OttieniNTactics %s)" % NPC), S("Slots", "(Classe|BPDlgNPC|OttieniTacticSlots %s)" % NPC)]))
PTR = "(Classe|BPPlotManager|OttieniPTraits %s)" % M
NTR = "(Classe|BPDlgNPC|OttieniNTraits %s)" % NPC
fn("LoadSetup", [], S("MClass", 0), branch(eq(V("MemberIdx"), 0), [call("SetupHero")], [call("SetupNpc")]))
fn("SetupHero", [], S("MBeh", "(Classe|BPPlotManager|OttieniPBehavior %s)" % M), call("DrawSetup"),
   branch(gt(length(PTR), 0), [S("MClass", "(Matematica|Float|Truncate %s)" % get(PTR, 0))]))
fn("SetupNpc", [], S("MBeh", "(Classe|BPDlgNPC|OttieniBehavior %s)" % NPC), call("DrawSetup"),
   branch(gt(length(NTR), 0), [S("MClass", "(Matematica|Float|Truncate %s)" % get(NTR, 0))]))
fn("DrawSetup", [], text(W("PresetT"), '"Load a preset"'),
   branch(AND("(Utility|Operatori|Maggioreuguale(>=) %s 0)" % V("MBeh"), lt(V("MBeh"), length(V("TBehavNames")))),
          [text(W("BehavT"), '(Utilità|Stringa|Append "Behaviour: " %s)' % get(V("TBehavNames"), V("MBeh")))],
          [text(W("BehavT"), '"Behaviour"')]))
fn("LoadTalents", [], "(Utilità|Array|Clear %s)" % V("TalIds"), "(Utilità|Array|Clear %s)" % V("TalUse"),
   "(Utilità|Array|Clear %s)" % V("TalNames"),
   branch(eq(V("MemberIdx"), 0), [call("HeroTalents")], [call("NpcTalents")]))
HT = "(Classe|BPPlotManager|OttieniTalents %s)" % M
fn("HeroTalents", [], loop(last("(Classe|BPPlotManager|OttieniTalentNames %s)" % M), call("HeroTal", K="_index")))
fn("HeroTal", ["K"], "(Utilità|Array|Add %s %s)" % (V("TalIds"), get(HT, mul("K", 18))),
   "(Utilità|Array|Add %s %s)" % (V("TalUse"), get(HT, add(mul("K", 18), 1))),
   "(Utilità|Array|Add %s %s)" % (V("TalNames"), get("(Classe|BPPlotManager|OttieniTalentNames %s)" % M, "K")))
fn("NpcTalents", [], loop(5, call("NpcTal", K="_index")))
NT = "(Classe|BPDlgNPC|OttieniNTalents %s)" % NPC
fn("NpcTal", ["K"], branch(AND(lt(mul("K", 18), length(NT)), gt(get(NT, mul("K", 18)), 0.0)), [
    "(Classe|BPDlgNPC|NameOf %s :K K)" % NPC,
    "(Utilità|Array|Add %s %s)" % (V("TalIds"), get(NT, mul("K", 18))),
    "(Utilità|Array|Add %s %s)" % (V("TalUse"), get(NT, add(mul("K", 18), 1))),
    "(Utilità|Array|Add %s (Classe|BPDlgNPC|OttieniTName %s))" % (V("TalNames"), NPC)]))

# --- drawing --------------------------------------------------------------------------------------------------------
SHOWN = "(Matematica|Intero|Min(Integer) %s %d)" % (V("Slots"), ROWS)
fn("Redraw", [], text(W("Title"), '(Utilità|Stringa|Append (Utilità|Stringa|Append (Utilità|Stringa|Append "Tactics: " %s) (Utilità|Stringa|Append "   (" (Utilità|Stringa|ToString(Integer) %s))) " slots)")' % (V("MName"), V("Slots"))),
   loop(ROWS - 1, call("DrawRow", R="_index")))
fn("DrawRow", ["R"], call("RowVis", R="R"), call("FindTarget", R="R"), call("FindCond", R="R"), call("FindAct", R="R"),
   text(get(V("NumTs"), "R"), "(Utilità|Stringa|ToString(Integer) %s)" % add("R", 1)),
   text(get(V("TgtTs"), "R"), V("STgt")), text(get(V("CndTs"), "R"), V("SCnd")), text(get(V("ActTs"), "R"), V("SAct")))
fn("RowVis", ["R"], branch(lt("R", SHOWN), [vis(get(V("RowBs"), "R"), True)], [vis(get(V("RowBs"), "R"), False)]))
fn("FindTarget", ["R"], S("STgt", '(Utilità|Stringa|SelectString "?" "(empty)" %s)' % CH),
   loop(last(V("TTargetNames")), call("MatchTarget", R="R", K="_index"), done=[call("FindMemberTgt", R="R")]))
fn("FindMemberTgt", ["R"], branch(AND(CH, "(Utility|Operatori|Maggioreuguale(>=) %s 100.0)" % row(0)),
                                  [loop(last(V("Members")), call("MatchMemberTgt", R="R", K="_index"))]))
fn("MatchMemberTgt", ["R", "K"], branch(eq(add("(Matematica|Conversioni|ToFloat(Integer) (Classe|BPDlgNPC|OttieniNIndex %s))" % get(V("Members"), "K"), 100.0), row(0)),
                                        [S("STgt", "(Classe|BPDlgNPC|OttieniDisplayName %s)" % get(V("Members"), "K"))]))
fn("MatchTarget", ["R", "K"], branch(AND(CH, eq(get(V("TTargets"), mul("K", 2)), row(0))),
                                     [S("STgt", get(V("TTargetNames"), "K"))]))
fn("FindCond", ["R"], S("SCnd", '(Utilità|Stringa|SelectString "(other)" "" %s)' % CH),
   loop(last(V("TCondNames")), call("MatchCond", R="R", K="_index")))
fn("MatchCond", ["R", "K"], branch(AND(AND(CH, eq(get(V("TConds"), add(mul("K", 3), 1)), row(1))),
                                       eq(get(V("TConds"), add(mul("K", 3), 2)), row(2))),
                                   [S("SCnd", get(V("TCondNames"), "K"))]))
CS = add(length(V("TTargetNames")), 1)  # a command's stride: its id, then a flag per target
fn("FindAct", ["R"], S("SCmd", '"?"'), loop(sub(div(length(V("TCmds")), CS), 1),
                                            call("MatchCmd", C=row(3), K="_index"),
                                            done=[S("SAct", '(Utilità|Stringa|SelectString %s "" %s)' % (V("SCmd"), CH)),
                                                  call("ActDetail", R="R")]))
fn("MatchCmd", ["C", "K"], branch(eq(get(V("TCmds"), mul("K", CS)), "C"), [S("SCmd", get(V("TCmdNames"), "K"))]))
fn("ActDetail", ["R"], branch(AND(CH, eq(row(3), 10.0)), [
    S("SAct", '(Utilità|Stringa|Append (Utilità|Stringa|Append %s " ") (Utilità|Stringa|ToString(Integer) (Matematica|Float|Truncate %s)))' % (V("SCmd"), row(4)))],
    [branch(AND(CH, eq(row(3), 7.0)), [loop(last("(Classe|BPPlotManager|OttieniItemNames %s)" % M), call("MatchItemAb", R="R", K="_index"))],
            [loop(last(V("TalNames")), call("MatchAct", R="R", K="_index"))])]))
fn("MatchItemAb", ["R", "K"], branch(eq(get("(Classe|BPPlotManager|OttieniItemStats %s)" % M, add(mul("K", 6), 1)), row(4)),
                                     [S("SAct", '(Utilità|Stringa|Append "Use item: " %s)' % get("(Classe|BPPlotManager|OttieniItemNames %s)" % M, "K"))]))
fn("MatchAct", ["R", "K"], branch(AND(AND(CH, OR(eq(row(3), 4.0), eq(row(3), 5.0), eq(row(3), 6.0))), eq(get(V("TalIds"), "K"), row(4))),
                                  [S("SAct", '(Utilità|Stringa|SelectString (Utilità|Stringa|Append "Deactivate: " %s) %s %s)' % (
                                      get(V("TalNames"), "K"), get(V("TalNames"), "K"), eq(row(3), 6.0)))]))

# --- clicking a field: the picker -----------------------------------------------------------------------------------
fn("ClickCell", ["R", "C"], S("EditRow", "R"), call("InitIfEmpty", R="R"), call("FindTI"),
   S("Stage", "(Matematica|Intero|SelectInt 1 (Matematica|Intero|SelectInt 2 4 %s) %s)" % (eq("C", 1), eq("C", 0))),
   call("FillPick"))
fn("InitIfEmpty", ["R"], branch("(Utility|Operatori|Minoreuguale(<=) %s 0.0)" % row(5), [
    set_cell(0, 3.0, "R"), set_cell(1, 16.0, "R"), set_cell(2, 0.0, "R"), set_cell(3, 2.0, "R"), set_cell(4, 0.0, "R"),
    set_cell(5, 100.0, "R"), call("Commit"), call("DrawRow", R="R")]))
fn("FindTI", [], S("TI", 0), loop(last(V("TTargetNames")), call("MatchTI", K="_index")))
fn("MatchTI", ["K"], branch(eq(get(V("TTargets"), mul("K", 2)),
                                 "(Matematica|Float|SelectFloat 6.0 %s %s)" % (row(0, V("EditRow")), "(Utility|Operatori|Maggioreuguale(>=) %s 100.0)" % row(0, V("EditRow")))),
                              [S("TI", "K")]))
fn("FillPick", [], "(Utilità|Array|Clear %s)" % V("OptIds"), "(Utilità|Array|Clear %s)" % V("OptNames"),
   "(Utilità|Array|Clear %s)" % V("OptCmd"), "(Utilità|Array|Clear %s)" % V("OptSub"),
   call("FillTargets"), call("FillBases"), call("FillConds"), call("FillActs"), call("FillPresets"), call("FillBehavs"),
   call("DrawPick"))
fn("FillTargets", [], branch(eq(V("Stage"), 1), [loop(last(V("TTargetNames")), call("AddTargetOpt", K="_index"), "")]))
fn("AddTargetOpt", ["K"], branch(eq(get(V("TTargets"), mul("K", 2)), 6.0),
                                [loop(last(V("Members")), call("AddMemberOpt", K="_index"))], [
    "(Utilità|Array|Add %s (Matematica|Float|Truncate %s))" % (V("OptIds"), get(V("TTargets"), mul("K", 2))),
    "(Utilità|Array|Add %s %s)" % (V("OptNames"), get(V("TTargetNames"), "K"))]))
fn("AddMemberOpt", ["K"], branch(eq("K", sub(V("MemberIdx"), 1)), els=[
    "(Utilità|Array|Add %s %s)" % (V("OptIds"), add("(Classe|BPDlgNPC|OttieniNIndex %s)" % get(V("Members"), "K"), 100)),
    "(Utilità|Array|Add %s (Classe|BPDlgNPC|OttieniDisplayName %s))" % (V("OptNames"), get(V("Members"), "K"))]))
BS = add(length(V("TTargetNames")), 1)  # a base's stride: its id, then a flag per target
fn("FillBases", [], branch(eq(V("Stage"), 2), [loop(last(V("TBaseNames")), call("AddBaseOpt", K="_index"), "")]))
fn("AddBaseOpt", ["K"], branch(gt(get(V("TBases"), add(add(mul("K", BS), 1), V("TI"))), 0.0), [
    "(Utilità|Array|Add %s (Matematica|Float|Truncate %s))" % (V("OptIds"), get(V("TBases"), mul("K", BS))),
    "(Utilità|Array|Add %s %s)" % (V("OptNames"), get(V("TBaseNames"), "K"))]))
fn("FillConds", [], branch(eq(V("Stage"), 3), [loop(last(V("TCondNames")), call("AddCondOpt", K="_index"), "")]))
fn("AddCondOpt", ["K"], branch(eq(get(V("TConds"), add(mul("K", 3), 1)), V("BaseId")), [
    "(Utilità|Array|Add %s K)" % V("OptIds"), "(Utilità|Array|Add %s %s)" % (V("OptNames"), get(V("TCondNames"), "K"))]))
fn("FillActs", [], branch(eq(V("Stage"), 4), [loop(sub(div(length(V("TCmds")), CS), 1),
                                                    call("AddCmdOpts", K="_index"))]))
fn("AddOpt", ["Name", "Cmd", "Sub"], "(Utilità|Array|Add %s %s)" % (V("OptIds"), length(V("OptNames"))),
   "(Utilità|Array|Add %s Name)" % V("OptNames"), "(Utilità|Array|Add %s Cmd)" % V("OptCmd"), "(Utilità|Array|Add %s Sub)" % V("OptSub"))
fn("AddCmdOpts", ["K"], S("CmdId", get(V("TCmds"), mul("K", CS))),
   branch(gt(get(V("TCmds"), add(add(mul("K", CS), 1), V("TI"))), 0.0), [call("AddCmdKind", K="K")]))
fn("AddCmdKind", ["K"], branch(OR(eq(V("CmdId"), 2.0), eq(V("CmdId"), 3.0)), [call("AddOpt", Name=get(V("TCmdNames"), "K"), Cmd=V("CmdId"), Sub=0.0)], [
    branch(OR(eq(V("CmdId"), 4.0), eq(V("CmdId"), 5.0), eq(V("CmdId"), 6.0)), [loop(last(V("TalNames")), call("AddTalOpt", K="_index"))], [
        branch(eq(V("CmdId"), 10.0), [S("JumpName", get(V("TCmdNames"), "K")), loop(sub(V("Slots"), 1), call("AddJumpOpt", K="_index"))], [
            branch(eq(V("CmdId"), 7.0), [loop(last("(Classe|BPPlotManager|OttieniInv %s)" % M), call("AddInvOpt", K="_index"))], [
                branch(OR(eq(V("CmdId"), 11.0), eq(V("CmdId"), 12.0)),
                       [branch(eq(V("MemberIdx"), 0), [call("AddOpt", Name=get(V("TCmdNames"), "K"), Cmd=V("CmdId"), Sub=0.0)])],
                       [call("AddOpt", Name=get(V("TCmdNames"), "K"), Cmd=V("CmdId"), Sub=0.0)])])])])]))
# Use item: each kind of potion the party carries, once
INV = lambda k: get("(Classe|BPPlotManager|OttieniInv %s)" % M, k)
IST = lambda item, n: get("(Classe|BPPlotManager|OttieniItemStats %s)" % M, add(mul(item, 6), n))
fn("AddInvOpt", ["K"], branch(AND(OR(eq(IST(INV("K"), 0), 1.0), eq(IST(INV("K"), 0), 2.0)),
                                  NOT("(Utilità|Array|ContainsItem %s %s)" % (V("OptSub"), IST(INV("K"), 1)))), [
    call("AddOpt", Name='(Utilità|Stringa|Append "Use item: " %s)' % get("(Classe|BPPlotManager|OttieniItemNames %s)" % M, INV("K")),
         Cmd=7.0, Sub=IST(INV("K"), 1))]))
fn("AddTalOpt", ["K"], branch(OR(AND(eq(V("CmdId"), 4.0), NOT(eq(get(V("TalUse"), "K"), 2.0))),
                                  AND(OR(eq(V("CmdId"), 5.0), eq(V("CmdId"), 6.0)), eq(get(V("TalUse"), "K"), 2.0))), [
    call("AddOpt", Name='(Utilità|Stringa|SelectString (Utilità|Stringa|Append "Deactivate: " %s) %s %s)' % (
        get(V("TalNames"), "K"), get(V("TalNames"), "K"), eq(V("CmdId"), 6.0)), Cmd=V("CmdId"), Sub=get(V("TalIds"), "K"))]))
fn("AddJumpOpt", ["K"], branch(eq("K", V("EditRow")), els=[
    call("AddOpt", Name='(Utilità|Stringa|Append (Utilità|Stringa|Append %s " ") (Utilità|Stringa|ToString(Integer) %s))' % (V("JumpName"), add("K", 1)),
         Cmd=10.0, Sub="(Matematica|Conversioni|ToFloat(Integer) %s)" % add("K", 1))]))
# presets for the member's class, and behaviours
fn("FillPresets", [], branch(eq(V("Stage"), 5), [loop(last(V("TPresetNames")), call("AddPresetOpt", K="_index"))]))
PR = lambda n: get(V("TPresets"), add(mul("K", 6), n))
fn("AddPresetOpt", ["K"], branch(OR(eq(PR(1), "(Matematica|Conversioni|ToFloat(Integer) %s)" % V("MClass")),
                                    eq(PR(2), "(Matematica|Conversioni|ToFloat(Integer) %s)" % V("MClass")),
                                    eq(PR(3), "(Matematica|Conversioni|ToFloat(Integer) %s)" % V("MClass"))), [
    "(Utilità|Array|Add %s K)" % V("OptIds"), "(Utilità|Array|Add %s %s)" % (V("OptNames"), get(V("TPresetNames"), "K"))]))
fn("FillBehavs", [], branch(eq(V("Stage"), 6), [loop(last(V("TBehavNames")), call("AddBehavOpt", K="_index"))]))
fn("AddBehavOpt", ["K"], "(Utilità|Array|Add %s K)" % V("OptIds"), "(Utilità|Array|Add %s %s)" % (V("OptNames"), get(V("TBehavNames"), "K")))
fn("ClickPreset", [], S("Stage", 5), call("FillPick"))
fn("ClickBehav", [], S("Stage", 6), call("FillPick"))
fn("DrawPick", [], text(W("PickTitle"), '(Utilità|Stringa|SelectString "Behaviour" (Utilità|Stringa|SelectString "Preset (fills the slots)" (Utilità|Stringa|SelectString "Target" (Utilità|Stringa|SelectString "Condition" (Utilità|Stringa|SelectString "Action" "Click a field to change it" %s) %s) %s) %s) %s)' % (
    eq(V("Stage"), 4), OR(eq(V("Stage"), 2), eq(V("Stage"), 3)), eq(V("Stage"), 1), eq(V("Stage"), 5), eq(V("Stage"), 6))),
   loop(OPTS - 1, call("DrawOpt", K="_index")))
fn("DrawOpt", ["K"], branch(lt("K", length(V("OptNames"))),
                            [vis(get(V("OptBs"), "K"), True), text(get(V("OptTs"), "K"), get(V("OptNames"), "K"))],
                            [vis(get(V("OptBs"), "K"), False)]))
fn("ClosePick", [], S("Stage", 0), "(Utilità|Array|Clear %s)" % V("OptIds"), "(Utilità|Array|Clear %s)" % V("OptNames"),
   call("DrawPick"))

# --- choosing an option ---------------------------------------------------------------------------------------------
OK = lambda stage: AND(eq(V("StageNow"), stage), lt("K", length(V("OptIds"))))
OPT = get(V("OptIds"), "K")
fn("PickOption", ["K"], S("StageNow", V("Stage")), call("PickTarget", K="K"), call("PickCond", K="K"),
   call("PickBase", K="K"), call("PickAct", K="K"), call("PickPreset", K="K"), call("PickBehav", K="K"))
fn("PickTarget", ["K"], branch(OK(1), [call("SetTargetRow", V="(Matematica|Conversioni|ToFloat(Integer) %s)" % OPT), call("Done")]))
fn("SetTargetRow", ["V"], branch(eq(row(0, V("EditRow")), "V"), els=[set_cell(0, "V"), set_cell(1, 16.0), set_cell(2, 0.0)]))
fn("PickCond", ["K"], branch(OK(3), [set_cell(1, get(V("TConds"), add(mul(OPT, 3), 1))),
                                     set_cell(2, get(V("TConds"), add(mul(OPT, 3), 2))), call("Done")]))
fn("PickBase", ["K"], branch(OK(2), [S("BaseId", "(Matematica|Conversioni|ToFloat(Integer) %s)" % OPT), call("CountBase"), call("BaseNext")]))
fn("CountBase", [], S("NB", 0), loop(last(V("TCondNames")), call("CountOne", K="_index")))
fn("CountOne", ["K"], branch(eq(get(V("TConds"), add(mul("K", 3), 1)), V("BaseId")), [S("NB", add(V("NB"), 1)), S("LastCK", "K")]))
fn("BaseNext", [], branch(eq(V("NB"), 1), [set_cell(1, get(V("TConds"), add(mul(V("LastCK"), 3), 1))),
                                           set_cell(2, get(V("TConds"), add(mul(V("LastCK"), 3), 2))), call("Done")],
                          [S("Stage", 3), call("FillPick")]))
fn("PickAct", ["K"], branch(OK(4), [set_cell(3, get(V("OptCmd"), "K")), set_cell(4, get(V("OptSub"), "K")), call("Done")]))
# a preset (Chargen_LoadPresetsTable): its rows in order, one using a talent only when the member knows it, as many
# as its slots; the rest emptied
fn("PickPreset", ["K"], branch(OK(5), [S("PresetIdx", OPT), loop(last(V("Rows")), call("ZeroAt", J="_index"),
                                                                 done=[call("FillPreset")])]))
fn("ZeroAt", ["J"], "(Utilità|Array|SetArrayElem %s J 0.0)" % V("Rows"))
PP = lambda n: get(V("TPresets"), add(mul(V("PresetIdx"), 6), n))
fn("FillPreset", [], S("Added", 0), loop(sub("(Matematica|Float|Truncate %s)" % PP(5), 1), call("PresetRow", J="_index"),
                                         done=[call("Done")]))
PRW = lambda n: get(V("TPresetRows"), add(mul(add("(Matematica|Float|Truncate %s)" % PP(4), "J"), 6), n))
fn("PresetRow", ["J"], branch(AND(lt(V("Added"), V("Slots")),
                                  OR(NOT(OR(eq(PRW(3), 4.0), eq(PRW(3), 5.0), eq(PRW(3), 6.0))),
                                     "(Utilità|Array|ContainsItem %s %s)" % (V("TalIds"), PRW(4)))), [
    *["(Utilità|Array|SetArrayElem %s %s %s)" % (V("Rows"), add(mul(V("Added"), 6), n), PRW(n)) for n in range(6)],
    S("Added", add(V("Added"), 1))]))
fn("PickBehav", ["K"], branch(OK(6), [S("MBeh", OPT), call("SetBehOf"), call("DrawSetup"), call("ClosePick")]))
fn("SetBehOf", [], branch(eq(V("MemberIdx"), 0), ["(Classe|BPPlotManager|SetPBehavior %s :B %s)" % (M, V("MBeh"))],
                          ["(Classe|BPDlgNPC|SetBehavior %s :B %s)" % (NPC, V("MBeh"))]))
fn("Done", [], call("ClosePick"), call("Commit"), call("Redraw"))

# --- clearing, moving, saving, closing ------------------------------------------------------------------------------
fn("ClearRow", ["R"], S("EditRow", "R"), loop(5, call("ZeroCell", J="_index"), done=[call("Done")]))
fn("ZeroCell", ["J"], set_cell("J", 0.0))
fn("MoveUp", ["R"], branch(AND(gt("R", 0), lt("R", SHOWN)), [S("EditRow", "R"), call("SwapRows")]))
fn("SwapRows", [], loop(5, call("SwapCell", J="_index"), done=[call("Done")]))
fn("SwapCell", ["J"], S("Tmp", row("J", sub(V("EditRow"), 1))),
   "(Utilità|Array|SetArrayElem %s %s %s)" % (V("Rows"), add(mul(sub(V("EditRow"), 1), 6), "J"), row("J", V("EditRow"))),
   set_cell("J", V("Tmp")))
fn("Commit", [], branch(eq(V("MemberIdx"), 0), ["(Classe|BPPlotManager|SetPlayerTactics %s :InTactics %s)" % (M, V("Rows"))],
                        ["(Classe|BPDlgNPC|SetTacticRows %s :InRows %s)" % (NPC, V("Rows"))]))
fn("CloseScreen", [], "(Classe|BPPlotManager|CloseTactics %s)" % M)
print(sorted(p.stem for p in OUT.glob("*.dsl")))
