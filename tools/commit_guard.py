"""Commit guard: refuse a commit that carries game data or third-party assets (CLAUDE.md, "Hard rules").

    python tools/commit_guard.py            check what is staged (exit 1 and say why when something is wrong)
    python tools/commit_guard.py --install  run it before every commit (.git/hooks/pre-commit)

It looks at every staged file (added, copied, modified or renamed):
- where it is: extracted/, and the git-ignored Unreal folders for MetaHumans, Fab packs and outfits
  (a `git add -f` would get past .gitignore);
- what it is: the game's own formats by extension, and by their first bytes whatever the name
  (GFF, ERF, talk tables, FMOD banks, DDS);
- what it says: the area, plot, conversation and origin exports `daotools unreal` writes into extracted/
  (their Format field naming a DAODream format; tools/tests builds synthetic ones and is allowed), and names
  the owner keeps out of public files (listed in .git/info/commit-guard-names, never committed).
`git commit --no-verify` skips it, for the owner only, when a file is certainly fine.
Standard library only, like tools/daotools.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

FOLDERS = [
    ("extracted/", "extracted game data"),
    ("/Content/MetaHumans/", "MetaHuman assets"),
    ("/Content/ThirdParty/", "third-party (Fab) assets"),
    ("/Content/Outfits/", "MetaHuman or Fab outfits"),
    ("/Content/AnimalVarietyPack/", "a Fab pack"),
]
# The game's formats (GAME_DATA.md): archives, talk tables, GFF resources, scripts, models, textures, sound.
EXTENSIONS = {
    ".erf", ".rim", ".tlk", ".cnv", ".gda", ".plo", ".ncs", ".nss", ".fsb", ".fev", ".dds", ".tga",
    ".msh", ".mmh", ".mao", ".phy", ".ani", ".gad", ".dlg", ".utc", ".utp", ".utt", ".uti", ".are",
    ".arl", ".mor", ".mop", ".mfx", ".mat", ".bnk", ".lvl", ".stg", ".gff",
}
MAGIC = [
    (b"GFF ", "a GFF resource"), (b"ERF ", "an ERF archive"), (b"E\x00R\x00F\x00", "an ERF archive"),
    (b"TLK ", "a talk table"), (b"FSB4", "an FMOD sound bank"), (b"FEV1", "an FMOD event file"),
    (b"DDS ", "a DDS texture"),
]
EXPORT = re.compile(rb'"Format"\s*:\s*"DAODream\.')
# Names kept out of public files at the owner's request: one per line in .git/info/commit-guard-names,
# which is never committed (so the list itself stays private).


def private_names():
    path = subprocess.run(["git", "rev-parse", "--git-path", "info/commit-guard-names"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()
    path = os.path.join(ROOT, path)
    if not os.path.exists(path):
        return []
    return [re.compile(re.escape(l.strip().encode()), re.I) for l in open(path, encoding="utf-8") if l.strip()]
TEXT = {".md", ".txt", ".py", ".json", ".dsl", ".ini", ".yaml", ".yml", ".csv", ".html", ".cfg", ".toml"}


def staged():
    out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"],
                         cwd=ROOT, capture_output=True, check=True).stdout
    return [p for p in out.decode("utf-8").split("\0") if p]


def blob(path):
    """The staged content (what will be committed, not the working copy)."""
    r = subprocess.run(["git", "show", ":" + path], cwd=ROOT, capture_output=True)
    return r.stdout if r.returncode == 0 else b""


def problems(path, data, private=()):
    p = "/" + path.replace("\\", "/")
    for folder, what in FOLDERS:
        if folder in p or p.startswith("/" + folder):
            yield what + " (" + folder.strip("/") + ")"
    ext = os.path.splitext(path)[1].lower()
    if ext in EXTENSIONS:
        yield "a game file by its extension (%s)" % ext
    if path.lower().endswith(".uasset") or path.lower().endswith(".umap"):
        return  # Unreal's own packages: checked by folder only
    for magic, what in MAGIC:
        if data.startswith(magic):
            yield what + " by its content"
    if ext in TEXT:
        if EXPORT.search(data) and not p.startswith("/tools/tests/"):
            yield "an export from daotools (its Format field names a DAODream format): game data belongs in extracted/"
        for rx in private:
            if rx.search(data):
                yield "a name kept out of public files (.git/info/commit-guard-names)"


def check():
    bad, private = [], private_names()
    for path in staged():
        for why in problems(path, blob(path), private):
            bad.append((path, why))
    if bad:
        print("commit_guard: this commit would publish what must stay out of the repo (CLAUDE.md, Hard rules):")
        for path, why in bad:
            print("  %s: %s" % (path, why))
        print("Unstage them (git restore --staged <file>); if one is certainly fine, the owner can commit with --no-verify.")
        return 1
    return 0


HOOK = """#!/bin/sh
# Installed by tools/commit_guard.py --install: no game data or third-party assets in commits.
for py in python3 python py; do
    if command -v "$py" >/dev/null 2>&1 && "$py" -c "import sys" >/dev/null 2>&1; then
        exec "$py" "$(git rev-parse --show-toplevel)/tools/commit_guard.py"
    fi
done
echo "commit_guard: no Python found, commit not checked" >&2
"""


def install():
    hooks = subprocess.run(["git", "rev-parse", "--git-path", "hooks"], cwd=ROOT, capture_output=True,
                           text=True, check=True).stdout.strip()
    path = os.path.join(ROOT, hooks, "pre-commit")
    if os.path.exists(path) and "commit_guard" not in open(path, encoding="utf-8", errors="replace").read():
        print("a different pre-commit hook is installed at %s: add a call to tools/commit_guard.py to it" % path)
        return 1
    with open(path, "w", newline="\n") as f:
        f.write(HOOK)
    os.chmod(path, 0o755)
    print("installed", path)
    return 0


if __name__ == "__main__":
    sys.exit(install() if "--install" in sys.argv[1:] else check())
