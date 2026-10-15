# Ambient life

What the castle's people do while nobody talks to them: the game's ambient
behaviour system (`sys_ambient_h`), driven by the same data, acted out with
the mannequin.

## In the game

A creature's local variables (on its template, overridden by the area's
instance) turn the system on and pick what it does:

- `AMBIENT_SYSTEM_STATE`: bit 1 switches it on (31 creatures in the day castle).
- `AMBIENT_MOVE_PATTERN` and `AMBIENT_MOVE_PREFIX`: how it walks between
  waypoints tagged `<prefix>_01`, `<prefix>_02`, ... (or all tagged `<prefix>`):
  patrol back and forth, loop, warp back to the first, random, wander, or walk
  the list once. `<tag>` in the prefix is the creature's own tag.
- `AMBIENT_ANIM_PATTERN`: a row of `ambient_anim_patterns.gda`, up to twelve
  actions written `animation.loops` (animation IDs from `anim_base.gda`;
  animation 1 is a pause of that many seconds, 99 loops means hold).
- `AMBIENT_ANIM_FREQ`: -1 plays the whole pattern in order.

The creature alternates a move phase (go to the next waypoint) with an
animation phase (play the pattern). Plot scripts change patterns with
`Ambient_Start` and friends, which `daotools unreal plots` translates into
action kind 9 (`docs/SCRIPTS.md`).

## In the remake

The remake has none of the game's animations, so `tools/daotools/ambient.py`
turns each into one of nine things the mannequin can do, chosen by the
animation's name (our own table, `_BY_NAME`):

| Action | Game animations | Mannequin |
| --- | --- | --- |
| idle | pauses, arms crossed, hands behind back, servant pose | stands |
| fidget | idle twitches, wiping eyes, headache, inspecting nails | turns up to 15 degrees |
| look left / right | `wanderwest` / `wandereast` | turns 55 degrees |
| gesture | talking and pointing | turns up to 30 degrees, leans in a little |
| kneel | praying, crouching, sitting, sleeping | bows, hands together (a held frame of `MM_Death_Front_01`) |
| cower | scared, weeping, writhing | the same, leaning further |
| lean | pushing doors, leaning on tables | leans 12 degrees |
| bend | picking up, browsing, rummaging, cleaning | leans 30 degrees |

A looping animation lasts 2.5 s per loop and a single one 2.5 s.

`daotools unreal area ... --game "<game>"` writes, per creature, `NpcAmbient`
(state, move pattern, animation pattern, frequency) and `NpcAmbientDest`
(its waypoints, as a range of `AmbientDest`), plus every pattern
(`AmbientPatterns`: pattern, first action, count; `AmbientActions`: action,
seconds). Creatures with ambient behaviour are now spawned even when they have
no conversation or team (Lady Landra, for one).

In Unreal:

- `BP_AreaLoader.LoadAmbientData` reads the arrays; `SpawnNpcs` gives each
  creature its settings (`GiveNpcAmbient` → `BP_DlgNPC.SetupAmbient`), and the
  pattern table goes to the plot manager (`SetAmbientTable`).
- `BP_PlotManager.GiveAmbient` copies a pattern's actions to a creature
  (`SetAmbientActs`); `AmbientAct` runs plot action 9 on every creature with
  the tag; `AmbientWalkTo` sends a creature to a waypoint.
- `BP_DlgNPC.AmbientTick` (from `AnimTick`): while ambient is on and the
  creature is not in the party, walking a plot's walk or dead, it plays the
  pattern's actions in order (`AmbientNextAction` → `ApplyPose`), then moves
  (`AmbientMove`: patrol, loop, random, once; warp walks back instead of
  jumping). Turns and leans rotate the mesh and blend in (`AmbientTurn`);
  kneeling freezes a frame (`Crouch`, `CrouchAnim`/`CrouchPos` on the
  Blueprint). Everything pauses during conversations. Hostiles never start it.

Checked in Play: all 31 run. Guards on duty look left and right and fidget;
Aldous, Fergus, Nan and Lady Landra gesture; Mother Mallol walks to her place
in the chapel and kneels in prayer next to the two praying guards; the library
browser walks between its two waypoints and bends over the shelves. Setting the
cook's pattern from the plot action (`AmbientAct bhn100cr_cook 19`) switches
him to arms crossed, and 0 stops him.

Not done: wandering (moves 5 and 6, which no castle creature uses), placeable
interactions (negative actions), and starting only when the player comes into
view (the game pauses ambient creatures out of sight).
