"""python tactics_run_dsl.py: writes dsl/tacrun/*.dsl, the graphs tactics_run.py builds in: who a tactic row is aimed
at (BP_PlotManager.TacPick, the port of daotools tactics.pick_target), and what the party members and the hero do
with it. They are many small functions alike, so they are written from here: edit this, not the .dsl files.

Distances are in centimetres: the original's metres x 100."""
from pathlib import Path

OUT = Path(__file__).resolve().parent / "dsl" / "tacrun"
OUT.mkdir(exist_ok=True)
for old in OUT.glob("*.dsl"):
    old.unlink()

P = "(Gioco|GetPlayerPawn 0)"
NOW = "(Utilità|Testo|GetGameTimeinSeconds)"
NPC_CLASS = "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"
HEAL = 10104


def V(n):
    return "(Variabili|Predefinito|Ottieni%s)" % n


def S(n, x=None):
    return "(Variabili|Predefinito|Imposta%s%s)" % (n, "" if x is None else " " + str(x))


def get(arr, i):
    return "(Utilità|Array|Ottieni(unacopia) %s %s)" % (arr, i)


def op(name, a, b):
    return "(Utility|Operatori|%s %s %s)" % (name, a, b)


def add(a, b):
    return op("Aggiungi", a, b)


def mul(a, b):
    return op("Moltiplica", a, b)


def sub(a, b):
    return op("Sottrai", a, b)


def div(a, b):
    return op("Dividi", a, b)


def eq(a, b):
    return op("Uguale(==)", a, b)


def lt(a, b):
    return op("Minore(<)", a, b)


def gt(a, b):
    return op("Maggiore(>)", a, b)


def le(a, b):
    return op("Minoreuguale(<=)", a, b)


def ge(a, b):
    return op("Maggioreuguale(>=)", a, b)


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


def NOT(a):
    return "(Matematica|Booleano|NOTBoolean %s)" % a


def valid(a):
    return "(Utilità|IsValid %s)" % a


def length(a):
    return "(Utilità|Array|Length %s)" % a


def last(a):
    return sub(length(a), 1)


def F(x):  # an integer as a float
    return "(Matematica|Conversioni|ToFloat(Integer) %s)" % x


def trunc(x):
    return "(Matematica|Float|Truncate %s)" % x


def self_(_, a, b, cond):  # SelectFloat: a when cond
    return "(Matematica|Float|SelectFloat %s %s %s)" % (a, b, cond)


def seli(a, b, cond):
    return "(Matematica|Intero|SelectInt %s %s %s)" % (a, b, cond)


def dist(a, b):  # along the ground, as the original's creatures stand (the player's origin is a metre up)
    return "(Trasformazione|GetHorizontalDistanceTo %s %s)" % (a, b)


def npc(field, n):
    return "(Classe|BPDlgNPC|Ottieni%s %s)" % (field, n)


def pm(field):  # the manager's variable, from a BP_DlgNPC
    return "(Classe|BPPlotManager|Ottieni%s %s)" % (field, V("Mgr"))


def arr_add(arr, x):
    return "(Utilità|Array|Add %s %s)" % (arr, x)


def call(fn, **kw):
    return "(Funzionedichiamata|%s%s)" % (fn, "".join(" :%s %s" % (k, v) for k, v in kw.items()))


def branch(cond, then=None, els=None, ind="  "):
    s = "%s(Utilità|ControlloDiFlusso|Ramo %s" % (ind, cond)
    if then:
        s += "\n%s  (:then\n%s)" % (ind, "\n".join(_indent(x, ind + "    ") for x in then))
    if els:
        s += "\n%s  (:else\n%s)" % (ind, "\n".join(_indent(x, ind + "    ") for x in els))
    return s + ")"


def _indent(x, ind):
    return x if x.startswith(" ") else ind + x


def loop(last_index, body, done=None, ind="  "):
    s = "%s(Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex %s\n%s  (:LoopBody\n%s    %s)" % (
        ind, last_index, ind, ind, body)
    if done:
        s += "\n%s  (:Completed\n%s)" % (ind, "\n".join(_indent(x, ind + "    ") for x in done))
    return s + ")"


WROTE = {}


def fn(name, params, *lines, bp="PM"):
    """A graph: dsl/<name>.dsl when it replaces one written before, else dsl/tacrun/<name>.dsl."""
    src = "(fn %s (%s)\n%s)\n" % (name, " ".join(params), "\n".join(_indent(l, "  ") for l in lines))
    older = OUT.parent / (name + ".dsl")
    (older if older.exists() else OUT / (name + ".dsl")).write_text(src, encoding="utf-8")
    WROTE[name] = bp


def peek(a):
    return call("TrPeek", A=a)


# --- what a creature is, as the conditions ask (Pk*) ------------------------------------------------------------
fn("TrPeek", ["A"],
   S("PkAlive", '"false"'), S("PkVis", '"false"'), S("PkSide", -1), S("PkTgt"), S("PkAtk", 1), S("PkHp", 0.0),
   S("PkMax", 1.0), S("PkPct", 0.0), S("PkSta", 0.0), S("PkStun", '"false"'), S("PkKnock", '"false"'),
   S("PkRoot", '"false"'), S("PkSlow", '"false"'), S("PkClass", 0), S("PkRace", 0), S("PkGender", 0),
   S("PkRank", 0), S("PkArmor", 0),
   branch(eq("A", P), [call("TrPeekPlayer")], [branch(valid("A"), [call("TrPeekCast", A="A")])]))
fn("TrPeekCast", ["A"], "(bind _n (Utilità|Casting|CastToBP_DlgNPC A))", call("TrPeekNpc", N="_n"))
LIVE = lambda until: gt(until, NOW)
fn("TrPeekPlayer", [],
   S("PkAlive", NOT(OR(V("PlayerDown"), V("GameOver")))), S("PkVis", '"true"'), S("PkSide", 0),
   S("PkHp", V("PlayerHealth")), S("PkMax", "(Matematica|Float|Max(Float) %s 1.0)" % V("PlayerMaxHealth")),
   S("PkPct", mul(div(V("PkHp"), V("PkMax")), 100.0)),
   S("PkSta", mul(div(V("PStamina"), "(Matematica|Float|Max(Float) %s 1.0)" % V("PPool")), 100.0)),
   S("PkTgt", V("HeroTarget")), S("PkAtk", seli(2, 1, V("BowOn"))),
   S("PkStun", AND(LIVE(V("PStunUntil")), NOT(V("PFall")))), S("PkKnock", AND(LIVE(V("PStunUntil")), V("PFall"))),
   S("PkRoot", LIVE(V("PRootUntil"))), S("PkLoc", "(Trasformazione|GetActorLocation %s)" % P),
   call("TrTraits", T=V("PTraits")))
fn("TrPeekNpc", ["N"],
   S("PkAlive", AND(NOT(npc("Dead", "N")), NOT(npc("Down", "N")))),
   "(Classe|BPDlgNPC|HidCheck N)", S("PkVis", NOT(npc("Hid", "N"))),
   S("PkSide", seli(0, seli(1, seli(2, -1, npc("AllyOn", "N")), npc("Hostile", "N")), npc("InParty", "N"))),
   S("PkHp", npc("Health", "N")), S("PkMax", "(Matematica|Float|Max(Float) %s 1.0)" % npc("MaxHealth", "N")),
   S("PkPct", mul(div(V("PkHp"), V("PkMax")), 100.0)),
   S("PkSta", mul(div(npc("NStamina", "N"), "(Matematica|Float|Max(Float) %s 1.0)" % npc("NPool", "N")), 100.0)),
   S("PkTgt", npc("Foe", "N")), S("PkAtk", seli(4, seli(2, 1, gt(npc("NRange", "N"), 0.0)), npc("Staff", "N"))),
   S("PkStun", LIVE(npc("StunUntil", "N"))), S("PkKnock", LIVE(npc("KnockUntil", "N"))),
   S("PkRoot", LIVE(npc("RootUntil", "N"))), S("PkSlow", LIVE(npc("SlowUntil", "N"))),
   S("PkLoc", "(Trasformazione|GetActorLocation N)"), call("TrTraits", T=npc("NTraits", "N")))
fn("TrTraits", ["T"], branch(ge(length("T"), 5), [
    S("PkClass", trunc(get("T", 0))), S("PkRace", trunc(get("T", 1))), S("PkGender", trunc(get("T", 2))),
    S("PkRank", trunc(get("T", 3))), S("PkArmor", trunc(get("T", 4)))]))
IS_FOE = OR(AND(eq(V("TMeSide"), 1), OR(eq(V("PkSide"), 0), eq(V("PkSide"), 2))),
            AND(OR(eq(V("TMeSide"), 0), eq(V("TMeSide"), 2)), eq(V("PkSide"), 1)))
fn("TrFoeTest", ["A"], S("BFoe", '"false"'), branch(valid("A"), [peek("A"), S("BFoe", AND(V("PkAlive"), IS_FOE))]))

# --- the lists, once a round for whoever runs its tactics (TMe) -------------------------------------------------
fn("TrCtrl", [], S("TCtrl", P), branch(valid(V("Selected")), [S("TCtrl", V("Selected"))]))
fn("TrFlag", ["B", "Fl"], branch(lt(add(mul("B", 10), add("Fl", 1)), length(V("TBehaviors"))),
                                 [S("BF", gt(get(V("TBehaviors"), add(mul("B", 10), add("Fl", 1))), 0.0))],
                                 [S("BF", OR(eq("Fl", 0), eq("Fl", 1), eq("Fl", 7), eq("Fl", 8)))]))
fn("TrGather", ["Me"],
   *["(Utilità|Array|Clear %s)" % V(a) for a in ("AllyL", "AllyD", "EnL", "EnD", "EnAll", "NearD", "NearDead")],
   S("RingN", 0), S("DeadN", 0), S("TMe", "Me"), peek("Me"), S("TMeSide", V("PkSide")), S("TMeTgt", V("PkTgt")),
   S("TMeParty", eq(V("PkSide"), 0)), call("TrCtrl"), call("TrMeInfo", A="Me"), call("TrFlag", B=V("TMeBeh"), Fl=1),
   S("TMeChase", V("BF")),
   '(bind _all (Attore|GetAllActorsOfClass "%s"))' % NPC_CLASS,
   "(for _a _all\n    %s)" % call("TrGatherOne", A="_a"),
   call("TrGatherOne", A=P), call("TrCutEn5"), call("TrCutAlly5"), call("TrCountDead"), call("TrEngage"))
fn("TrMeInfo", ["A"], branch(eq("A", P), [S("TMeHated", V("HeroTarget")), S("TMeBeh", V("PBehavior"))],
                             [call("TrMeInfoCast", A="A")]))
fn("TrMeInfoCast", ["A"], "(bind _n (Utilità|Casting|CastToBP_DlgNPC A))", call("TrMeInfoNpc", N="_n"))
fn("TrMeInfoNpc", ["N"], S("TMeBeh", npc("Behavior", "N")), S("TMeHated", npc("Foe", "N")),
   branch(valid(npc("Hated", "N")), [S("TMeHated", npc("Hated", "N"))]))
fn("TrGatherOne", ["A"], branch(eq("A", V("TMe")), els=[peek("A"), branch(V("PkVis"), [call("TrSort", A="A")])]))
fn("TrSort", ["A"], "(bind _d %s)" % dist(V("TMe"), "A"), call("TrInsNear", D="_d"),
   branch(V("PkAlive"), [branch(AND(eq(V("PkSide"), V("TMeSide")), ge(V("TMeSide"), 0)),
                                [call("TrInsAlly", A="A", D="_d")],
                                [branch(IS_FOE, [call("TrInsEn", A="A", D="_d")])])]))


def insert_sorted(name, arrs, items, dists, pre=()):
    """name(A, D): A (and D) into the arrays at the place that keeps `dists` rising."""
    less = name + "Less"
    fn(less, ["K", "D"], S("PkIns", seli(add(V("PkIns"), 1), V("PkIns"), le(get(V(dists), "K"), "D"))))  # ties: first come first
    fn(name, ["A", "D"] if "A" in items else ["D"], *pre, S("PkIns", 0),
       loop(last(V(dists)), call(less, K="_index", D="D"),
            done=["(Utilità|Array|Insert %s %s %s)" % (V(a), x, V("PkIns")) for a, x in zip(arrs, items)]))


insert_sorted("TrInsNear", ("NearD", "NearDead"), ("D", NOT(V("PkAlive"))), "NearD")
insert_sorted("TrInsAlly", ("AllyL", "AllyD"), ("A", "D"), "AllyD")
insert_sorted("TrInsEn", ("EnL", "EnD"), ("A", "D"), "EnD",
              pre=(arr_add(V("EnAll"), "A"), S("RingN", seli(add(V("RingN"), 1), V("RingN"), le("D", 250.0)))))
for side in ("En", "Ally"):
    fn("TrCut%s5" % side, [], branch(gt(length(V(side + "L")), 5), [
        "(Utilità|Array|Resize %s 5)" % V(side + "L"), "(Utilità|Array|Resize %s 5)" % V(side + "D")]))
fn("TrCountDead", [], loop(sub("(Matematica|Intero|Min(Integer) %s 5)" % length(V("NearDead")), 1),
                           call("TrDeadOne", K="_index")))
fn("TrDeadOne", ["K"], S("DeadN", seli(add(V("DeadN"), 1), V("DeadN"), get(V("NearDead"), "K"))))
fn("TrEngage", [], branch(V("TMeParty"), [
    S("PkN", length(V("EnL"))), S("TReach", self_(0, 3000.0, 1500.0, V("TMeChase"))),
    loop(last(V("EnL")), call("TrEngOne", K="_index"),
         done=["(Utilità|Array|Resize %s %s)" % (V("EnL"), V("PkN")), "(Utilità|Array|Resize %s %s)" % (V("EnD"), V("PkN"))])]))
fn("TrEngOne", ["K"], branch(AND(lt("K", V("PkN")), gt(dist(get(V("EnL"), "K"), V("TCtrl")), V("TReach"))),
                             [S("PkN", "K")]))

# --- the row's list (CL) ----------------------------------------------------------------------------------------
TT, TB, TP, TC, TS = V("TT"), V("TB"), V("TP"), V("TC"), V("TS")
CL = V("CL")
fn("TrAddValid", ["A"], branch(valid("A"), [peek("A"), branch(V("PkAlive"), [arr_add(CL, "A")])]))
fn("TrAddFollower", ["Idx"], '(bind _all (Attore|GetAllActorsOfClass "%s"))' % NPC_CLASS,
   "(for _a _all\n    %s)" % call("TrFolOne", A="_a", Idx="Idx"))
fn("TrFolOne", ["A", "Idx"], branch(AND(eq(npc("NIndex", "A"), "Idx"), npc("InParty", "A"), NOT(npc("Dead", "A"))),
                                    [arr_add(CL, "A")]))
fn("TrList", [], "(Utilità|Array|Clear %s)" % CL,
   branch(eq(TT, 1.0), [arr_add(CL, V("TMe"))], [
       branch(eq(TT, 2.0), [S("CL", V("AllyL"))], [
           branch(eq(TT, 3.0), [S("CL", V("EnL"))], [
               branch(eq(TT, 7.0), [call("TrAddValid", A=V("TMeHated"))], [
                   branch(eq(TT, 5.0), [call("TrAddValid", A=P)], [
                       branch(eq(TT, 18.0), [call("TrAddValid", A=V("TCtrl"))], [
                           branch(ge(TT, 100.0), [call("TrAddFollower", Idx=trunc(sub(TT, 100.0)))])])])])])])]))
fn("TrHealFilter", [], branch(AND(eq(TC, 4.0), eq(TS, float(HEAL))), [
    "(Utilità|Array|Clear %s)" % V("CL2"),
    loop(last(CL), call("TrWound", K="_index"), done=[S("CL", V("CL2"))])]))
fn("TrWound", ["K"], peek(get(CL, "K")), branch(lt(V("PkHp"), V("PkMax")), [arr_add(V("CL2"), get(CL, "K"))]))
fn("TrPostHeal", [], branch(AND(eq(TT, 1.0), eq(TC, 4.0), eq(TS, float(HEAL)), valid(V("PkWho"))),
                            [peek(V("TMe")), branch(ge(V("PkHp"), V("PkMax")), [S("PkWho")])]))

# --- the conditions -----------------------------------------------------------------------------------------------
LEVEL = lambda v: OR(AND(lt(TP, 0.0), lt(v, mul(TP, -1.0))), AND(ge(TP, 0.0), ge(v, TP)))
BITS = lambda x: gt("(Matematica|Intero|BitwiseAND %s %s)" % (x, trunc(TP)), 0)
STATUS = OR(AND(eq(TP, 4.0), V("PkStun")), AND(eq(TP, 16.0), V("PkKnock")), AND(eq(TP, 7.0), V("PkRoot")),
            AND(eq(TP, 9.0), V("PkSlow")), AND(eq(TP, 97.0), OR(V("PkStun"), V("PkKnock"))),
            AND(eq(TP, 98.0), OR(V("PkStun"), V("PkKnock"), V("PkRoot"))),
            AND(eq(TP, 99.0), OR(V("PkStun"), V("PkKnock"), V("PkRoot"), V("PkSlow"))))
RK = V("PkRank")
RANK = OR(AND(gt(TP, 0.0), eq(F(RK), TP)),
          AND(eq(TP, -1.0), ge(RK, 2), le(RK, 5)),
          AND(eq(TP, -2.0), OR(eq(RK, 1), eq(RK, 2), eq(RK, 11), eq(RK, 12))),
          AND(eq(TP, -3.0), OR(eq(RK, 1), eq(RK, 2), eq(RK, 3), eq(RK, 11), eq(RK, 12))),
          AND(eq(TP, -4.0), ge(RK, 3), le(RK, 5)), AND(eq(TP, -5.0), ge(RK, 4), le(RK, 5)))
BAND = lambda d: OR(AND(eq(TP, 1.0), le(d, 350.0)), AND(eq(TP, 2.0), gt(d, 350.0), le(d, 1200.0)),
                    AND(eq(TP, 3.0), gt(d, 1200.0), le(d, 8000.0)))
REACH = self_(0, 350.0, self_(0, 1200.0, self_(0, 8000.0, 1000000.0, eq(TP, 3.0)), eq(TP, 2.0)), eq(TP, 1.0))
WHO = V("PkWho")


def tryer(name, arr, pred, keep_first=True, params=("K",), item=None, peek_it=True, extra=()):
    """name(K): arr[K] becomes PkWho when `pred` holds of it (Pk*, after TrPeek), the first one (keep_first) or the
    last."""
    it = item or get(V(arr), "K")
    body = ([peek(it)] if peek_it else []) + list(extra) + [branch(pred, [S("PkWho", it)])]
    if keep_first:
        fn(name, list(params), branch(valid(WHO), els=body))
    else:
        fn(name, list(params), *body)


def over(arr, name):
    return loop(last(V(arr)), call(name, K="_index"))


tryer("TrTryStatus", "CL", STATUS)
tryer("TrTryHp", "CL", LEVEL(V("PkPct")))
tryer("TrTrySta", "CL", LEVEL(V("PkSta")))
fn("TrTryLow", ["K"], peek(get(CL, "K")),
   branch(OR(AND(eq(TP, 0.0), lt(V("PkHp"), V("PkBest"))), AND(eq(TP, 1.0), gt(V("PkHp"), V("PkBest")))),
          [S("PkBest", V("PkHp")), S("PkWho", get(CL, "K"))]))
# every hostile in the fight (GetClusterCenter is not held to the five nearest): the one with most others within 5 m,
# at least n of them; the nearest on a tie
fn("TrTryClus", ["K"], S("PkN", 0), loop(last(V("EnAll")), call("TrClusOne", K="K", J="_index"),
                                          done=[branch(AND(ge(F(V("PkN")), TP),
                                                           OR(gt(F(V("PkN")), V("PkBest")),
                                                              AND(eq(F(V("PkN")), V("PkBest")),
                                                                  lt(dist(V("TMe"), get(V("EnAll"), "K")), V("PkBestD"))))),
                                                       [S("PkBest", F(V("PkN"))), S("PkBestD", dist(V("TMe"), get(V("EnAll"), "K"))),
                                                        S("PkWho", get(V("EnAll"), "K"))])]))
fn("TrClusOne", ["K", "J"], S("PkN", seli(add(V("PkN"), 1), V("PkN"),
                                         le(dist(get(V("EnAll"), "K"), get(V("EnAll"), "J")), 500.0))))
fn("TrHated", [], branch(valid(V("TMeHated")), [peek(V("TMeHated")), branch(V("PkAlive"), [S("PkWho", V("TMeHated"))])]))
fn("TrOwnChk", [], branch(valid(V("TMeTgt")), [peek(V("TMeTgt")), branch(AND(V("PkAlive"), IS_FOE), [S("PkWho", V("TMeTgt"))])]))
fn("TrOwn", [], branch(AND(eq(TT, 3.0), V("TMeParty")), [call("TrOwnChk")]))
for name, key in (("Race", "PkRace"), ("Class", "PkClass"), ("Gender", "PkGender")):
    tryer("TrTry" + name, "CL", eq(F(V(key)), TP))
tryer("TrTryAtkMem", "EnL", AND(valid(V("PkMem")), eq(V("PkTgt"), V("PkMem"))))
fn("TrMember", [], S("PkMem"), branch(eq(TP, 5.0), [S("PkMem", P)], [branch(eq(TP, 18.0), [S("PkMem", V("TCtrl"))])]))
fn("TrBuffOf", ["A"], S("PkBuff", '"false"'), branch(eq("A", P), [loop(last(V("TalentNames")), call("TrBuffP", K="_index"))],
                                                     [call("TrBuffCast", A="A")]))
fn("TrBuffP", ["K"], branch(AND(gt(get(V("TUntil"), "K"), 100000000.0),
                                "(Utilità|Array|ContainsItem %s %s)" % (V("TBuffs"), get(V("Talents"), mul("K", 18)))),
                            [S("PkBuff", '"true"')]))
fn("TrBuffCast", ["A"], "(bind _n (Utilità|Casting|CastToBP_DlgNPC A))", call("TrBuffNpc", N="_n"))
fn("TrBuffNpc", ["N"], loop(5, call("TrBuffN", N="N", K="_index")))
fn("TrBuffN", ["N", "K"], branch(AND(lt("K", length(npc("NOn", "N"))), lt(mul("K", 18), length(npc("NTalents", "N")))),
                                [branch(AND(gt(get(npc("NOn", "N"), "K"), 0.0),
                                            "(Utilità|Array|ContainsItem %s %s)" % (V("TBuffs"), get(npc("NTalents", "N"), mul("K", 18)))),
                                        [S("PkBuff", '"true"')])]))
fn("TrBuffOwn", [], branch(AND(V("TMeParty"), valid(V("TMeTgt"))), [
    peek(V("TMeTgt")), call("TrBuffOf", A=V("TMeTgt")),
    branch(AND(V("PkAlive"), IS_FOE, V("PkBuff")), [S("PkWho", V("TMeTgt"))])]))
tryer("TrTryBuff", "CL", AND(V("PkBuff"), OR(eq(TP, 0.0), le(dist(V("TMe"), get(CL, "K")), REACH))),
      extra=[call("TrBuffOf", A=get(CL, "K"))])
fn("TrArmorH", [], branch(valid(V("TMeHated")), [peek(V("TMeHated")), branch(AND(V("PkAlive"), BITS(V("PkArmor"))), [
    S("PkWho", V("TMeHated")), branch(eq(TT, 1.0), [S("PkWho", V("TMe"))])])]))
fn("TrUsingH", [], branch(valid(V("TMeHated")), [peek(V("TMeHated")), branch(AND(V("PkAlive"), BITS(V("PkAtk"))), [
    S("PkWho", V("TMeHated")), branch(eq(TT, 1.0), [S("PkWho", V("TMe"))])])]))
tryer("TrTryArmor", "EnL", BITS(V("PkArmor")))
tryer("TrTryUsing", "CL", BITS(V("PkAtk")))
for arr in ("EnAll", "EnL"):
    fn("TrCntArmor" + arr, ["K"], peek(get(V(arr), "K")), S("PkN", seli(add(V("PkN"), 1), V("PkN"), BITS(V("PkArmor")))))
    fn("TrCntAtk" + arr, ["K"], peek(get(V(arr), "K")), S("PkN", seli(add(V("PkN"), 1), V("PkN"), BITS(V("PkAtk")))))
tryer("TrTryRank", "EnL", RANK, keep_first=False)
ON = lambda attacker, victim: AND(eq(V("PkTgt"), victim), BITS(V("PkAtk")),
                                  OR(NOT(eq(TP, 1.0)), le(dist(attacker, victim), 350.0)))
fn("TrAtkSelf", ["K"], branch(valid(WHO), els=[peek(get(V("EnL"), "K")),
                                               branch(ON(get(V("EnL"), "K"), V("TMe")), [S("PkWho", V("TMe"))])]))
fn("TrAtkEn", ["K"], branch(valid(WHO), els=[S("PkMem", get(V("EnL"), "K")), over("AllyL", "TrAtkEnA")]))
fn("TrAtkEnA", ["K"], branch(valid(WHO), els=[peek(get(V("AllyL"), "K")),
                                              branch(ON(get(V("AllyL"), "K"), V("PkMem")), [S("PkWho", V("PkMem"))])]))
fn("TrAtkAl", ["K"], branch(valid(WHO), els=[S("PkMem", get(V("AllyL"), "K")), over("EnL", "TrAtkAlE")]))
fn("TrAtkAlE", ["K"], branch(valid(WHO), els=[peek(get(V("EnL"), "K")),
                                              branch(ON(get(V("EnL"), "K"), V("PkMem")), [S("PkWho", V("PkMem"))])]))
fn("TrAtkHated", [], branch(valid(V("TMeHated")), [peek(V("TMeHated")), branch(AND(BITS(V("PkAtk")), eq(V("PkTgt"), V("TMe"))),
                                                                               [S("PkWho", V("TMe"))])]))
fn("TrAtkMem", ["K"], branch(valid(WHO), els=[peek(get(V("EnL"), "K")),
                                              branch(ON(get(V("EnL"), "K"), V("PkMem")), [S("PkWho", V("PkMem"))])]))
tryer("TrTryBand", "CL", BAND(dist(V("TMe"), get(CL, "K"))), peek_it=False)
tryer("TrTryRgd", "CL", AND(OR(eq(V("PkAtk"), 2), eq(V("PkAtk"), 4)), BAND(dist(V("TMe"), get(CL, "K")))))
fn("TrWhoFor", [], branch(eq(TT, 1.0), [S("PkWho", V("TMe"))], [
    branch(eq(TT, 3.0), [branch(gt(length(V("EnL")), 0), [S("PkWho", get(V("EnL"), 0))])],
           [branch(eq(TT, 7.0), [call("TrHated")])])]))
FIRST = branch(gt(length(CL), 0), [S("PkWho", get(CL, 0))])
B = {
    1: [over("CL", "TrTryStatus")],
    2: [over("CL", "TrTryHp")],
    14: [over("CL", "TrTrySta")],
    3: [branch(OR(eq(TT, 2.0), eq(TT, 3.0)), [S("PkBest", self_(0, 1000000000.0, 0.0, eq(TP, 0.0))), over("CL", "TrTryLow")])],
    4: [branch(gt(length(V("EnAll")), 0), [S("PkBest", 0.0), S("PkBestD", 1000000000.0), over("EnAll", "TrTryClus")])],
    5: [call("TrHated")],
    6: [call("TrOwn"), branch(valid(WHO), els=[branch(AND(OR(eq(TT, 2.0), eq(TT, 3.0)), ge(TP, 1.0), le(TP, F(length(CL)))),
                                                    [S("PkWho", get(CL, sub(trunc(TP), 1)))])])],
    7: [call("TrOwn"), branch(valid(WHO), els=[branch(OR(eq(TT, 2.0), eq(TT, 3.0)), [over("CL", "TrTryRace")])])],
    8: [call("TrOwn"), branch(valid(WHO), els=[branch(OR(eq(TT, 2.0), eq(TT, 3.0)), [over("CL", "TrTryClass")])])],
    9: [call("TrOwn"), branch(valid(WHO), els=[branch(OR(eq(TT, 2.0), eq(TT, 3.0)), [over("CL", "TrTryGender")])])],
    10: [call("TrMember"), over("EnL", "TrTryAtkMem")],
    11: [call("TrMember"), branch(valid(V("PkMem")), [peek(V("PkMem")), branch(valid(V("PkTgt")), [S("PkWho", V("PkTgt"))])])],
    12: [call("TrBuffOwn"), branch(valid(WHO), els=[branch(OR(eq(TT, 3.0), eq(TT, 7.0)), [over("CL", "TrTryBuff")])])],
    16: [branch(eq(TT, 3.0), [branch(V("TMeParty"), [call("TrOwnChk")], [call("TrHated")])], [FIRST])],
    18: [branch(OR(eq(TT, 1.0), eq(TT, 7.0)), [call("TrArmorH")], [branch(eq(TT, 3.0), [over("EnL", "TrTryArmor")])])],
    19: [S("PkN", 0), loop(last(V("EnAll")), call("TrCntArmorEnAll", K="_index"),
                          done=[branch(ge(mul(V("PkN"), 2), length(V("EnAll"))), [S("PkWho", V("TMe"))])])],
    20: [S("PkN", 0), loop(last(V("EnAll")), call("TrCntArmorEnAll", K="_index"),
                          done=[branch(eq(V("PkN"), length(V("EnAll"))), [S("PkWho", V("TMe"))])])],
    24: [S("PkN", 0), loop(last(V("EnL")), call("TrCntAtkEnL", K="_index"),
                          done=[branch(gt(V("PkN"), sub(length(V("EnL")), V("PkN"))), [S("PkWho", V("TMe"))])])],
    25: [S("PkN", 0), loop(last(V("EnAll")), call("TrCntAtkEnAll", K="_index"),
                          done=[branch(eq(V("PkN"), length(V("EnAll"))), [S("PkWho", V("TMe"))])])],
    21: [over("EnL", "TrTryRank")],
    22: [branch(eq(TT, 1.0), [over("EnL", "TrAtkSelf")], [
        branch(eq(TT, 3.0), [over("EnL", "TrAtkEn")], [
            branch(eq(TT, 2.0), [over("AllyL", "TrAtkAl")], [
                branch(eq(TT, 7.0), [call("TrAtkHated")], [
                    branch(gt(length(CL), 0), [S("PkMem", get(CL, 0)), over("EnL", "TrAtkMem")])])])])])],
    23: [branch(OR(eq(TT, 1.0), eq(TT, 7.0)), [call("TrUsingH")], [branch(OR(eq(TT, 2.0), eq(TT, 3.0)), [over("CL", "TrTryUsing")])])],
    26: [call("TrWhoFor"), branch(lt(F(length(V("EnAll"))), TP), [S("PkWho")])],
    27: [call("TrWhoFor"), branch(lt(F(V("DeadN")), TP), [S("PkWho")])],
    28: [call("TrWhoFor"), branch(lt(F(length(V("AllyL"))), TP), [S("PkWho")])],
    29: [branch(OR(eq(TT, 2.0), eq(TT, 3.0)), [over("CL", "TrTryBand")], [call("TrBandH")])],
    31: [branch(OR(AND(eq(TP, 0.0), eq(V("RingN"), 0)), AND(gt(TP, 0.0), ge(F(V("RingN")), TP))), [S("PkWho", V("TMe"))])],
    32: [branch(OR(eq(TT, 3.0), eq(TT, 7.0)), [over("CL", "TrTryRgd")])],
    33: [peek(V("TMe")), branch(AND(LEVEL(V("PkPct")), OR(eq(TT, 2.0), eq(TT, 3.0), eq(TT, 7.0))), [FIRST])],
    34: [peek(V("TMe")), branch(AND(LEVEL(V("PkSta")), OR(eq(TT, 2.0), eq(TT, 3.0), eq(TT, 7.0))), [FIRST])],
}
B[35], B[36] = B[29], B[23]
fn("TrBandH", [], branch(valid(V("TMeHated")), [branch(BAND(dist(V("TMe"), V("TMeHated"))), [
    S("PkWho", V("TMeHated")), branch(eq(TT, 1.0), [S("PkWho", V("TMe"))])])]))
for b, lines in B.items():
    fn("TrB%d" % b, [], *lines)
bases = sorted(B)


def chain(i):
    if i == len(bases):
        return []
    return [branch(eq(TB, float(bases[i])), [call("TrB%d" % bases[i])], chain(i + 1) or None)]


# the switch, in two halves so no graph gets too deep
half = len(bases) // 2
fn("TrSwitch", [], branch(lt(TB, float(bases[half])), [call("TrSwitchLo")], [call("TrSwitchHi")]))
saved = bases
bases = saved[:half]
fn("TrSwitchLo", [], *chain(0))
bases = saved[half:]
fn("TrSwitchHi", [], *chain(0))
bases = saved

fn("TacPick", ["Tgt", "Base", "Param", "Cmd", "Sub"],
   S("TT", "Tgt"), S("TB", "Base"), S("TP", "Param"), S("TC", "Cmd"), S("TS", "Sub"), S("PkWho"), S("PkBest", 0.0),
   call("TrList"), call("TrHealFilter"), call("TrSwitch"), call("TrPostHeal"))

# --- the party may attack (behaviours' AttackOnCombatStart) -----------------------------------------------------
fn("MayAttack", [], S("PartyMayAttack", '"true"'), S("MayAttackAt", NOW))
# the original clears it when combat ends: here, once a second, when no hostile is left within reach of the one
# in control (his EnL: 30 m, 15 for a behaviour that does not chase)
fn("MayAttackTick", [], branch(AND(V("PartyMayAttack"), gt(NOW, V("MayCheckAt"))), [
    S("MayCheckAt", add(NOW, 1.0)), call("TrCtrl"), call("TrGather", Me=V("TCtrl")),
    branch(eq(length(V("EnL")), 0), [S("PartyMayAttack", '"false"')])]))
fn("HealPlayer", ["Amount"], S("PlayerHealth", "(Matematica|Float|Min(Float) %s %s)" % (add(V("PlayerHealth"), "Amount"), V("PlayerMaxHealth"))),
   call("ShowHealth"))

# --- the hero: his rows through TacPick -------------------------------------------------------------------------
PT = V("PTactics")
prow = lambda n, i="I": get(PT, add(mul(i, 6), n))
fn("HeroTacticPick", ["I"], "(Funzionedichiamata|TacPick :Tgt %s :Base %s :Param %s :Cmd %s :Sub %s)" % tuple(prow(n) for n in range(5)),
   S("HTWho", V("PkWho")), S("HTCond", valid(V("PkWho"))))
fn("HeroTactics", [], S("HTDone", '"false"'), S("HTStop", '"false"'), S("HTNext", 0.0), call("TrGather", Me=P),
   loop(sub(div(length(PT), 6), 1), call("HeroTacticRow", I="_index")))
fn("HeroTacticRow", ["I"],
   branch(OR(V("HTDone"), V("HTStop"), le(prow(5), 0.0), lt(F("I"), V("HTNext"))), els=[
       call("HeroTacticPick", I="I"),
       branch(AND(V("HTCond"), lt(mul("(Matematica|Casuale|RandomFloat)", 100.0), prow(5))),
              [call("HeroTacticUse", I="I")])]))
fn("HeroAim", [], call("TrFoeTest", A=V("HTWho")),
   branch(V("BFoe"), [S("HeroTarget", "(Utilità|Casting|CastToBP_DlgNPC %s)" % V("HTWho"))]))
fn("HeroTacticUse", ["I"], call("HeroAim"),
   branch(eq(prow(3), 2.0), [S("HTStop", '"true"')], [
       branch(eq(prow(3), 3.0), [S("HTDone", '"true"')], [
           branch(eq(prow(3), 10.0), [call("HeroJump", I="I")], [
               branch(OR(eq(prow(3), 11.0), eq(prow(3), 12.0)), [call("HeroSwitchSet", I="I")], [
                   branch(eq(prow(3), 6.0), [call("HeroModeOff", I="I")], [call("HeroTacticTalent", I="I")])])])])]))
fn("HeroJump", ["I"], S("HTStop", eq(prow(4), -1.0)),
   S("HTNext", "(Matematica|Float|Max(Float) %s %s)" % (V("HTNext"), self_(0, sub(prow(4), 1.0), 0.0, gt(prow(4), add(F("I"), 1.0))))))
fn("HeroSwitchSet", ["I"], branch(OR(AND(eq(prow(3), 11.0), V("BowOn")), AND(eq(prow(3), 12.0), NOT(V("BowOn")))),
                                  [call("SwitchWeapon"), S("HTDone", '"true"')]))
fn("HeroTacticTalent", ["I"], S("HTFound", -1), S("HTStop", '"false"'),
   loop(sub(length(V("TalentNames")), 1), call("HeroFindTalent", K="_index", Sub=prow(4)),
        done=[branch(ge(V("HTFound"), 0), [call("HeroTacticFire", bMode=eq(prow(3), 5.0))])]))
fn("HeroModeOff", ["I"], S("HTFound", -1),
   loop(sub(length(V("TalentNames")), 1), call("HeroFindTalent", K="_index", Sub=prow(4)),
        done=[branch(AND(ge(V("HTFound"), 0), gt(get(V("TUntil"), V("HTFound")), 100000000.0)),
                     [S("TSlot", V("HTFound")), call("ToggleSustained"), S("HTDone", '"true"')])]))

# --- a party member's rows (BP_DlgNPC) --------------------------------------------------------------------------
NT = V("NTactics")
nrow = lambda n: get(NT, add(V("RB"), n))
MGR = V("Mgr")
fn("TacticPick", [], "(Classe|BPPlotManager|TacPick %s :Tgt %s :Base %s :Param %s :Cmd %s :Sub %s)" % (
    MGR, nrow(0), nrow(1), nrow(2), nrow(3), nrow(4)),
   S("TacWho", pm("PkWho")), S("CondOk", valid(V("TacWho"))), bp="NPC")
fn("ChooseTactic", [], S("TacSlot", -1), S("TacNext", 0.0), S("TacDone", '"false"'), S("TacOn"),
   "(Classe|BPPlotManager|TrGather %s :Me (Variabili|Ottieniunriferimentoasestesso))" % MGR,
   call("ChooseRows"), bp="NPC")
fn("ChooseRows", [], loop(sub(div(length(NT), 6), 1), call("TacticRow", I="_index")), bp="NPC")
fn("TacticRow", ["I"], S("RB", mul("I", 6)),
   branch(AND(NOT(V("TacDone")), ge("I", V("TacNext")), gt(nrow(5), 0.0)), [
       call("TacticPick"),
       branch(AND(V("CondOk"), le(mul("(Matematica|Casuale|RandomFloat)", 100.0), nrow(5))), [call("TacticAct", I="I")])]),
   bp="NPC")
REACH_NPC = self_(0, 1500.0, self_(0, mul(V("NRange"), 100.0), 250.0, gt(V("NRange"), 0.0)), V("Staff"))
fn("TacAim", [], branch(AND(V("TacDone"), valid(V("TacWho"))), [
    S("TacOn", V("TacWho")), "(Classe|BPPlotManager|TrFoeTest %s :A %s)" % (MGR, V("TacWho")),
    branch(pm("BFoe"), [call("TacRetarget")])]), bp="NPC")
fn("TacRetarget", [], S("Foe", V("TacWho")), call("TacTooFar"), branch(V("InParty"), [call("TacSetTarget")]), bp="NPC")
fn("TacTooFar", [], branch(gt(dist("(Variabili|Ottieniunriferimentoasestesso)", V("TacWho")), REACH_NPC), [S("TacSlot", -2)]),
   bp="NPC")
fn("TacSetTarget", [], "(bind _n (Utilità|Casting|CastToBP_DlgNPC %s))" % V("TacWho"),
   call("SetTarget", InTarget="_n"), bp="NPC")
fn("TacticAct", ["I"],
   branch(eq(nrow(3), 10.0), [
       S("TacDone", eq(nrow(4), -1.0)),
       S("TacNext", "(Matematica|Float|Max(Float) %s %s)" % (V("TacNext"), self_(0, sub(nrow(4), 1.0), 0.0, gt(nrow(4), add(F("I"), 1.0)))))], [
       branch(OR(eq(nrow(3), 4.0), eq(nrow(3), 5.0)), [
           call("TacticUsable", Ability=nrow(4), bMode=eq(nrow(3), 5.0)), call("TacAim")], [
           branch(eq(nrow(3), 9.0), [call("TacticMove", Sub=nrow(4))], [
               branch(eq(nrow(3), 2.0), [S("TacDone", '"true"'), call("TacAim")], [
                   branch(eq(nrow(3), 3.0), [S("TacDone", '"true"'), S("TacSlot", -2)], [
                       branch(eq(nrow(3), 6.0), [call("ModeOff", Ability=nrow(4))])])])])])]),
   bp="NPC")
fn("ModeOff", ["Ability"], S("TFound", -1), loop(5, call("FindOne", K="_index", Ability="Ability"), done=[call("ModeOffGo")]),
   bp="NPC")
NTL = V("NTalents")
fn("ModeOffGo", [], branch(AND(ge(V("TFound"), 0), lt(V("TFound"), length(V("NOn")))), [
    branch(gt(get(V("NOn"), V("TFound")), 0.0), [
        "(Utilità|Array|SetArrayElem %s %s 0.0)" % (V("NOn"), V("TFound")),
        S("NPool", add(V("NPool"), get(NTL, add(mul(V("TFound"), 18), 4)))),
        S("NFatigue", sub(V("NFatigue"), get(NTL, add(mul(V("TFound"), 18), 5)))),
        call("NSumOwn"), call("SayText", Txt='"Mode off"'), S("TacDone", '"true"'), S("TacSlot", -2)])]), bp="NPC")

# Heal: (100 + spellpower) x the row's factor on TacOn (itself without one)
fn("EffHeal", ["K"], S("HealAmt", mul(add(V("SpellPower"), 100.0), get(NTL, add(mul("K", 18), 15)))),
   branch(valid(V("TacOn")), [call("HealWho", A=V("TacOn"))], [call("HealWho", A="(Variabili|Ottieniunriferimentoasestesso)")]),
   bp="NPC")
fn("HealWho", ["A"], branch(eq("A", P), ["(Classe|BPPlotManager|HealPlayer %s :Amount %s)" % (MGR, V("HealAmt"))],
                            [call("HealCast", A="A")]), bp="NPC")
fn("HealCast", ["A"], "(bind _n (Utilità|Casting|CastToBP_DlgNPC A))", "(Funzionedichiamata|GainHealth _n :Amount %s)" % V("HealAmt"),
   bp="NPC")
fn("GainHealth", ["Amount"], branch(V("Dead"), els=[
    S("Health", "(Matematica|Float|Min(Float) %s %s)" % (add(V("Health"), "Amount"), V("MaxHealth"))),
    call("ShowHealthText"), call("SayText", Txt='(Utilità|Stringa|Append "+" (Utilità|Stringa|ToString(Integer) %s))' % trunc("Amount"))]),
   bp="NPC")

# --- behaviours and the support round (party members not fighting in reach) ------------------------------------
fn("NFlag", ["Fl"], "(Classe|BPPlotManager|TrFlag %s :B %s :Fl Fl)" % (MGR, V("Behavior")), S("BFlag", pm("BF")), bp="NPC")
fn("SupportTick", ["Dt"], S("SupportTimer", sub(V("SupportTimer"), "Dt")),
   branch(OR(V("Controlled"), gt(V("SupportTimer"), 0.0)), els=[S("SupportTimer", V("Interval")), call("SupportRound")]),
   bp="NPC")
fn("SupportRound", [], "(Classe|BPPlotManager|TrGather %s :Me (Variabili|Ottieniunriferimentoasestesso))" % MGR,
   branch(gt(length(pm("EnAll")), 0), [call("Behave"), call("SupportGo")]), bp="NPC")
ENGAGED = AND(valid(V("Foe")), le(dist("(Variabili|Ottieniunriferimentoasestesso)", V("Foe")), add(REACH_NPC, 50.0)))
fn("SupportGo", [], branch(ENGAGED, els=[
    S("TacSlot", -1), S("TacNext", 0.0), S("TacDone", '"false"'), S("TacOn"), call("ChooseRows"), call("SupportAct")]),
   bp="NPC")
fn("MayFight", [], call("NFlag", Fl=2), S("BMay", OR(pm("PartyMayAttack"), V("BFlag"))), bp="NPC")
fn("SupportAct", [], call("MayFight"), "(Classe|BPPlotManager|TrFoeTest %s :A %s)" % (MGR, V("TacWho")),
   branch(ge(V("TacSlot"), 0), [
       branch(pm("BFoe"), [branch(V("BMay"), [call("TacSetTarget"), S("PendingSlot", add(V("TacSlot"), 1))])],
              [call("DoTalent")])], [
       branch(AND(V("TacDone"), pm("BFoe"), V("BMay")), [call("TacSetTarget")], [call("AttackBackCheck")])]),
   bp="NPC")
# no target and no tactic: a behaviour that attacks by default leaves it to the bids; one that does not fights back
# (AttackBack) the nearest enemy attacking it
fn("AttackBackCheck", [], call("NFlag", Fl=7), branch(AND(NOT(V("BFlag")), NOT(valid(V("Target")))), [
    call("NFlag", Fl=0), branch(V("BFlag"), [S("TacWho"), loop(last(pm("EnL")), call("BackOne", K="_index"),
                                                               done=[branch(valid(V("TacWho")), [call("TacSetTarget")])])])]),
   bp="NPC")
fn("BackOne", ["K"], branch(valid(V("TacWho")), els=[
    "(Classe|BPPlotManager|TrPeek %s :A %s)" % (MGR, get(pm("EnL"), "K")),
    branch(eq(pm("PkTgt"), "(Variabili|Ottieniunriferimentoasestesso)"), [S("TacWho", get(pm("EnL"), "K"))])]), bp="NPC")
# AvoidNearbyEnemies: the nearest enemy within 3.5 m -> 5 m away; AvoidMeleeEnemies: one attacking it in melee
fn("Behave", [], call("NFlag", Fl=5), branch(AND(V("BFlag"), gt(length(pm("EnD")), 0)), [
    branch(lt(get(pm("EnD"), 0), 350.0), [call("BackAway", From=get(pm("EnL"), 0))])], [call("BehaveMelee")]), bp="NPC")
fn("BehaveMelee", [], call("NFlag", Fl=6), branch(AND(V("BFlag"), gt(pm("RingN"), 0), gt(length(pm("EnL")), 0)), [
    branch(le(get(pm("EnD"), 0), 250.0), [call("BackAway", From=get(pm("EnL"), 0))])]), bp="NPC")
fn("BackAway", ["From"],
   "(bind (_x _y _z) (Matematica|Vettore|BreakVector %s))" % sub("(Trasformazione|GetActorLocation (Variabili|Ottieniunriferimentoasestesso))",
                                                                 "(Trasformazione|GetActorLocation From)"),
   S("FleeGoal", add("(Trasformazione|GetActorLocation (Variabili|Ottieniunriferimentoasestesso))",
                     mul("(Matematica|Vettore|Normalize (Matematica|Vettore|MakeVector _x _y 0.0))", "(Matematica|Vettore|MakeVector 500.0 500.0 0.0)"))),
   S("FleeUntil", add(NOW, 1.5)), bp="NPC")

# who fights: a member's bid gives way to its behaviour (BP_PlotManager)
fn("AssignByBid", ["Follower"], S("BestDist", 1200.0), S("BestTarget"),
   '(bind _all (Attore|GetAllActorsOfClass "%s"))' % NPC_CLASS,
   "(for _a _all\n    (Classe|BPDlgNPC|Bid _a :InMgr (Variabili|Ottieniunriferimentoasestesso) :From Follower))",
   call("BidChoose", Follower="Follower"))
fn("BidChoose", ["Follower"], "(Classe|BPDlgNPC|MayFight Follower)", call("TrCtrl"),
   branch(AND(npc("BMay", "Follower"), valid(V("BestTarget"))), [call("BidAttack", Follower="Follower")],
          ["(Classe|BPDlgNPC|SetTarget Follower)"]))
fn("BidAttack", ["Follower"], "(Classe|BPDlgNPC|NFlag Follower :Fl 7)",
   branch(npc("BFlag", "Follower"), [call("BidReach", Follower="Follower")], [call("BidKeep", Follower="Follower")]))
fn("BidReach", ["Follower"], "(Classe|BPDlgNPC|NFlag Follower :Fl 1)",
   branch(le(dist(V("BestTarget"), V("TCtrl")), self_(0, 3000.0, 1500.0, npc("BFlag", "Follower"))),
          ["(Classe|BPDlgNPC|SetTarget Follower :InTarget (Utilità|Casting|CastToBP_DlgNPC %s))" % V("BestTarget")],
          ["(Classe|BPDlgNPC|SetTarget Follower)"]))
fn("BidKeep", ["Follower"], branch(AND(valid(npc("Target", "Follower")), NOT(npc("Dead", npc("Target", "Follower")))),
                                   els=["(Classe|BPDlgNPC|SetTarget Follower)"]))
fn("HeroBidGate", [], call("TrFlag", B=V("PBehavior"), Fl=2), S("BMayH", OR(V("PartyMayAttack"), V("BF"))),
   call("TrFlag", B=V("PBehavior"), Fl=7), branch(OR(NOT(V("BMayH")), NOT(V("BF"))), [S("HeroTarget")]))
fn("CtrlMay", [], branch(V("Controlled"), ["(Classe|BPPlotManager|MayAttack %s)" % MGR]), bp="NPC")
fn("PartyHurt", [], branch(V("InParty"), ["(Classe|BPPlotManager|MayAttack %s)" % MGR]), bp="NPC")
# each creature's traits and its place in the area (rows aimed at one party member: FOLLOWER_BASE + it)
fn("SetTraits", ["InTraits", "K"], S("NIndex", "K"), "(Utilità|Array|Clear %s)" % V("NTraits"),
   branch(ge(length("InTraits"), mul(add("K", 1), 5)), [loop(4, call("TraitOne", InTraits="InTraits", I="_index", K="K"))]),
   bp="NPC")
fn("TraitOne", ["InTraits", "I", "K"], arr_add(V("NTraits"), get("InTraits", add(mul("K", 5), "I"))), bp="NPC")
fn("SetTacticExtra", ["InCommands", "InPresets", "InPresetRows", "InPresetNames", "InBehaviors", "InBehaviorNames",
                      "InBehaviorTexts", "InBuffs", "InTraits"],
   S("TCommands", "InCommands"), S("TPresets", "InPresets"), S("TPresetRows", "InPresetRows"),
   S("TPresetNames", "InPresetNames"), S("TBehaviors", "InBehaviors"), S("TBehaviorNames", "InBehaviorNames"),
   S("TBehaviorTexts", "InBehaviorTexts"), S("TBuffs", "InBuffs"), S("PTraits", "InTraits"))

fn("SetPBehavior", ["B"], S("PBehavior", "B"))
fn("HidCheck", [], S("Hid", "(Variabili|Rendering|OttieniActorHiddenInGame)"), bp="NPC")
fn("SetBehavior", ["B"], S("Behavior", "B"), bp="NPC")

if __name__ == "__main__":
    print(len(WROTE), "graphs:", sorted(WROTE))
