---
paths:
  - "tools/**"
---

# daotools (Python pipeline)

- Python 3.10+, standard library only. No third-party imports, including in tests.
- Never commit game data or text dumped from it: archives, talk tables,
  conversations, data tables, textures, models, audio, scripts. Output goes to
  git-ignored `extracted/`. A test that needs a format detail builds a synthetic
  file with `tests/builders.py`; add a builder case, never a real game file.
- GFF4 field IDs belong in `daotools/fields.py`, not as literals in readers.
- When converted output looks wrong, compare it with the full dump `daotools pull`
  writes next to it (`<name>.json`) and fix the mapping from that, rather than
  patching the output.
- Run the suite before calling a change done:
  `cd tools && PYTHONPATH=.:tests python -m unittest discover -s tests`.
- Format facts are sourced from `docs/GAME_DATA.md` and the real install, not from
  memory of other BioWare games: a format detail you cannot confirm is written down
  as unconfirmed.
