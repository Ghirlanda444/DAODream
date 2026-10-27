"""Helpers for the generated Blueprint graphs (the Italian DSL of write_graph_dsl): expressions as strings, and
Writer, which writes each graph to a folder and remembers its Blueprint. Used by loot_dsl.py."""
from pathlib import Path

P = "(Gioco|GetPlayerPawn 0)"
NOW = "(Utilità|Testo|GetGameTimeinSeconds)"
SELF = "(Variabili|Ottieniunriferimentoasestesso)"
NPC_CLASS = "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"


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




def randf():
    return "(Matematica|Casuale|RandomFloat)"


def randi(lo, hi):  # an integer from lo to hi, both included
    return "(Matematica|Casuale|RandomIntegerinRange %s %s)" % (lo, hi)


def get_any(cls, field, obj):  # another Blueprint's variable
    return "(Classe|%s|Ottieni%s %s)" % (cls, field, obj)


class Writer:
    """fn(name, params, *lines, bp=...) writes <out>/<bp>/<name>.dsl; wrote lists (bp, name) in order."""

    def __init__(self, out: Path, clear=True):
        self.out = out
        out.mkdir(parents=True, exist_ok=True)
        if clear:
            for old in out.rglob("*.dsl"):
                old.unlink()
        self.wrote = []

    def __call__(self, name, params, *lines, bp="PM"):
        body = "\n".join(_indent(line, "  ") for line in lines)
        src = "(fn %s (%s)\n%s)\n" % (name, " ".join(params), body)
        (self.out / bp).mkdir(exist_ok=True)
        (self.out / bp / (name + ".dsl")).write_text(src, encoding="utf-8")
        self.wrote.append((bp, name))

    def path(self, bp, name):
        return self.out / bp / (name + ".dsl")
