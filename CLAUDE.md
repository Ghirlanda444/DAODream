# DAODream: notes for Claude

Personal, non-commercial fan remake of Dragon Age: Origins in UE5, starting with
the Human Noble origin. Roadmap: `docs/ROADMAP.md`.

## Hard rules

- Never commit game data: archives, talk tables, conversations, data tables,
  textures, models, audio, compiled or toolset scripts, or text dumped from them.
  Extracted data lives in `extracted/` (git-ignored). Before committing, check
  `git status` for anything that came out of the install.
- Exception: `daotools scan` reports (file names and counts only) may be
  summarised in `docs/` to record the archive layout.
- Never commit third-party character assets either (MetaHumans, Fab packs): they
  live in git-ignored `Content/MetaHumans/` and `Content/ThirdParty/`, because
  the repo is public (`docs/CHARACTERS.md`).

## Tools

- `tools/daotools`: Python 3.10+, standard library only. Install with
  `pip install -e tools`.
- Tests: `cd tools && PYTHONPATH=.:tests python -m unittest discover -s tests`.
  They build synthetic files with `tests/builders.py`; add a builder case rather
  than a real game file when covering a new format detail.
- GFF4 field IDs live in `tools/daotools/fields.py`. Retail conversations are `.dlg`;
  their layout is confirmed (`docs/GAME_DATA.md`). When converted output looks
  wrong, compare with the full dump `daotools pull` writes next to it
  (`<name>.json`) and fix the mapping from that.
- GFF3 (`gff3.py`) covers `.utc/.utp/.utt/.uti/.are`; field labels are text.
- Install layout and Human Noble resource list: `docs/GAME_DATA.md`.

## Unreal

- The UE 5.8 project lives in `Unreal/Cousland`; setup and session rules are in
  `docs/UNREAL_SETUP.md`. Assets go through Git LFS (`.gitattributes`).
- Work one system per prompt, report every actor and asset created, and stop
  rather than silently work around a missing tool.
