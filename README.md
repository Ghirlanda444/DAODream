# DAODream

A personal, non-commercial fan remake of *Dragon Age: Origins* in Unreal Engine 5,
starting with the **Human Noble origin** (Castle Cousland).

The remake reads the original game's data (dialogue trees, talk tables, data
tables, later models and audio) from **your own installed copy** and rebuilds
the game around it. Nothing from the game is ever committed here; see
[the ground rules](#ground-rules).

## Status

| Piece | State |
|---|---|
| `tools/daotools`: ERF archive reader (V2.0, V2.2 incl. compression, V3.0) | done, unit-tested on synthetic files |
| GFF4 reader (the container behind `.cnv`, `.tlk`, `.gda`, `.plo`, ...) | done, unit-tested on synthetic files |
| Talk tables (plain V0.2 and Huffman V0.5) | done, unit-tested on synthetic files |
| Data tables (`.gda`) with column-name resolution | done, unit-tested on synthetic files |
| Conversations (`.cnv`) to JSON and a readable script | done, **field layout still to confirm on real files** |
| Validation against the real install | **next step, needs your PC** |
| UE5 project, models, animation, combat | not started; see [docs/ROADMAP.md](docs/ROADMAP.md) |

## Quick start (on your PC)

You need Python 3.10+ and DAO installed (Steam or EA app, PC version).

```bash
pip install -e tools

# 1. Inventory the install: which archives exist and what's inside them.
#    The report holds only file names and counts, no game content.
daotools scan "C:/Program Files (x86)/Steam/steamapps/common/Dragon Age Ultimate Edition" --out extracted/scan.json

# 2. Look for the Human Noble resources (prefix to be confirmed by the scan).
daotools find "<DAO folder>" "bhn*"

# 3. Pull them out and convert: raw files plus JSON, and a .txt script per conversation.
daotools pull "<DAO folder>" "bhn*" --out extracted/human_noble
```

`extracted/` is git-ignored. Other commands: `daotools erf list|extract`,
`gff dump`, `tlk dump`, `gda dump`, `cnv export [--transcript]`. Run
`daotools <command> --help` for details.

Run the tests with:

```bash
cd tools && PYTHONPATH=.:tests python -m unittest discover -s tests
```

## Ground rules

- **No game files in git.** Archives, talk tables, conversations, textures,
  models, audio and decompiled or toolset scripts stay in `extracted/` or the
  game folder. `.gitignore` blocks the usual extensions; check `git status`
  before committing anything new.
- **Converters, not copies.** The repo holds code that reads your install, so
  anyone who wants to run it needs their own copy of the game.
- **Personal project.** No builds containing BioWare/EA assets are distributed.

## Credits

The file-format knowledge comes from the Dragon Age modding community: the
Dragon Age Toolset wiki and the [xoreos](https://github.com/xoreos/xoreos)
project's documentation of BioWare's Aurora/Eclipse formats. The code here is
an independent implementation.
