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

## Tools

- `tools/daotools`: Python 3.10+, standard library only. Install with
  `pip install -e tools`.
- Tests: `cd tools && PYTHONPATH=.:tests python -m unittest discover -s tests`.
  They build synthetic files with `tests/builders.py`; add a builder case rather
  than a real game file when covering a new format detail.
- GFF4 field IDs live in `tools/daotools/fields.py`. The conversation layout
  (`cnv.py`) is still unconfirmed against retail files: when real output looks
  wrong, run `daotools gff dump` on the `.cnv` and fix the mapping from that.
