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

## Studio framework (Claude Code Game Studios)

The `.claude/` agents, skills, hooks and rules come from
[Claude Code Game Studios](https://github.com/Donchitos/Claude-Code-Game-Studios)
v1.2.0 (MIT, `.claude/CCGS-LICENSE`). The hard rules above win over anything
in the framework. Start with `/help` (what to do next) or `/adopt` (audit what
exists against the framework); `/settings` shows the effective config.

- **Engine**: Unreal Engine 5.8, Blueprint-primary (`Unreal/Cousland`). Only the
  Unreal agent set is installed.
- **Pipeline tools**: Python 3.10+, standard library only (`tools/daotools`).
- **Version control**: Git, assets through Git LFS.

`project.yaml` at the repo root is the primary config store (engine, modes,
naming, commands); skills resolve it via `resolve_config`
(`.claude/docs/config-resolution.md`). `modes.rigor` is `minimal`: no GDDs
required, the design record is `design/game-brief.md`, and the original game is
the spec. Raise it per system with `workflow_overrides.system_overrides`.

### Project structure

@.claude/docs/directory-structure.md

### Engine version reference

@docs/engine-reference/unreal/VERSION.md

### Coordination rules

@.claude/docs/coordination-rules.md

### Collaboration protocol

**User-driven collaboration, not autonomous execution.**
Every task follows: **Question -> Options -> Decision -> Draft -> Approval**

- Agents MUST ask "May I write this to [filepath]?" before using Write/Edit tools
  (exempt: `active.md` appends, agent memory, a subagent's new file at the path
  its orchestrating skill named; see `.claude/rules/agent-memory.md`)
- Agents MUST show drafts or summaries before requesting approval
- Multi-file changes require explicit approval for the full changeset
- No commits without user instruction
- A skipped or dismissed question is not an answer: act on nothing, re-ask in
  plain text and wait
- Started outside this file's folder? Warn first: hooks, deny rules and the
  ask-first mode load only when Claude Code starts here

See `docs/COLLABORATIVE-DESIGN-PRINCIPLE.md` for the full protocol.

### Coding standards

@.claude/docs/coding-standards.md

### Context management

Read `.claude/docs/context-management.md` on demand. Two conventions are
load-bearing:

- **`production/session-state/active.md` is the session checkpoint.** The file is
  the memory, not the conversation. Read it first after any compaction, crash, or
  `/clear`.
- **Helpers in `.claude/scripts/` emit observations, never verdicts.**
