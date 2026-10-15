# Game logic in compiled scripts (Human Noble survey)

What the conversations cannot do on their own lives in compiled scripts
(`.ncs`). This records how much there is and how it could be read. File names,
sizes and counts only; no script content.

## What is there

- 195 `.ncs` resources in the `bhn*` pull, 51 distinct scripts (the same
  script sits in several archives). About 620 KB of bytecode in total.
- By kind (from the name): 16 plot scripts (`*pt_*`, 401 KB), 19 trigger
  scripts (`*tr_*`, 53 KB), 9 placeable scripts (`*ip_*`, 78 KB), 5 creature
  scripts (`*cr_*`, 33 KB) and 2 area scripts (`bhn100ar_castle_cousland`,
  `bhn200ar_castle_after_siege`, 58 KB).
- The smallest plot scripts are 17-19 KB, which is mostly shared code compiled
  into each one (plot flag get/set, reward and XP handling). The story logic is
  what comes on top: e.g. about 9 KB for `bhn100pt_father`, 34 KB for
  `bhn100pt_gilmore`.
- The names the scripts reference show what kind of logic it is:
  - moving characters to waypoints when a flag is set (`bhn100pt_father`
    references `bhn100wp_father_upstairs` and `bhn100wp_mother_upstairs`:
    after the opening, Bryce and Eleanor go up to Fergus' room),
  - doors and placeables (`bhn000ip_door_pantry`, `bhn100ip_door_upstairs`),
  - switching to the night castle (`bhn000pt_main` references
    `bhn200ar_castle_after_siege`),
  - setting flags in other plots (codex entries, achievements, the party),
  - rewards and XP.
- Defined plot flags (256 and up, e.g. `GEN_GENDER_MALE`) are computed by these
  scripts too; for now they are passed in as true flags.

So Phase 1 needed none of it, but the castle only "plays" once the plot
scripts' effects exist: parents moving upstairs, the dog quest, the night.

## How to read it

The header is `NCS V1.0B`, the same bytecode family as Neverwinter Nights
scripts (NWScript), which is documented by the community (xoreos). Two ways:

1. **The official Dragon Age: Origins toolset** (free from BioWare/EA). It
   ships the script source (`.nss`) for the game's scripts, so the logic could
   be read and ported by hand. It is not installed on this PC. Best option if it
   still installs.
2. **A disassembler in daotools**: NWScript bytecode is simple; the hard part is
   the table of engine functions Dragon Age adds (several hundred), which would
   have to come from community documentation. Gives readable but low-level
   output.

Either way the logic gets rewritten in Unreal (Blueprints), plot by plot,
driven by the same "GUID:FLAG" keys the dialogue runner already uses.

A per-script list (name, kind, size, referenced tags and plots) can be
regenerated into `extracted/scripts/` from the pull; it is not committed.
