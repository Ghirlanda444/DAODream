"""python dsl_lint.py <folder or file>...: graphs that write_graph_dsl would refuse: a statement after a branch
(Ramo) in the same list, a wildcard operator (Utility|Operatori) given a literal first, or unbalanced parentheses."""
import re
import sys
from pathlib import Path


def parse(s, i=0):
    """The s-expression at s[i] (lists of strings), and where it ends."""
    while s[i].isspace():
        i += 1
    if s[i] == "(":
        out, i = [], i + 1
        while True:
            while s[i].isspace():
                i += 1
            if s[i] == ")":
                return out, i + 1
            x, i = parse(s, i)
            out.append(x)
    if s[i] == '"':
        j = s.index('"', i + 1)
        return s[i:j + 1], j + 1
    j = i
    while j < len(s) and not s[j].isspace() and s[j] not in "()":
        j += 1
    return s[i:j], j


def statements(node):
    """The statement lists in a graph: the fn body, and each branch's :then/:else, each loop's bodies."""
    if not isinstance(node, list) or not node:
        return
    head = node[0] if isinstance(node[0], str) else ""
    if head == "fn":
        yield node[3:]
    if head in (":then", ":else", ":LoopBody", ":Completed") or head == "for":
        yield node[1:] if head != "for" else node[3:]
    for x in node:
        yield from statements(x)


def is_branch(x):
    return isinstance(x, list) and x and isinstance(x[0], str) and x[0].endswith("|Ramo")


def check(path):
    s = path.read_text(encoding="utf-8")
    try:
        tree, _ = parse(s)
    except (IndexError, ValueError):
        return ["unbalanced"]
    bad = ["literal first: " + m.group(0) for m in re.finditer(r"\(Utility\|Operatori\|[^ ]+ -?[0-9][0-9.]*[ )]", s)]
    for body in statements(tree):
        for k, x in enumerate(body[:-1]):
            if is_branch(x):
                bad.append("statement after a branch (#%d of %d)" % (k + 1, len(body)))
    return bad


if __name__ == "__main__":
    files = []
    for a in sys.argv[1:]:
        p = Path(a)
        files += sorted(p.rglob("*.dsl")) if p.is_dir() else [p]
    n = 0
    for f in files:
        for b in check(f):
            print(f, b)
            n += 1
    print(n, "problems in", len(files), "graphs")
