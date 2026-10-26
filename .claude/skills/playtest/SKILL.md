---
name: playtest
description: Check a DAODream change in the running game, not just in the editor - pictures of characters, conversations, deaths, from Simulate or Play in L_CastleCousland / L_CastleNight. Use after any change a player would see (looks, outfits, animation, lights, cameras, dialogue, combat) and before saying it works.
---

# Playtest: look at the game running

A change a player sees is not done until it has been seen running in the level, with a picture kept.
Compile success, a read-back graph or a variable value are not enough.

## The kit (tools/unreal)

- `playtest.py`: one command per kind of check, pictures plus a contact sheet in
  `Unreal/Cousland/Saved/claude/playtest/<command>-<time>/` (git-ignored), and the script errors logged
  during the run. Characters are named by tag (`NpcTags` in `extracted/ue/areas/<area>.json`).
  - `py playtest.py look night <tag>...`: Simulate, face and full-length pictures (hidden ones shown).
    `--dog` for side and front at dog height.
  - `py playtest.py dialogue day --lines 8`: Play, a picture of each line of the opening
    conversation (or the one running), always option 1.
  - `py playtest.py kill night <tag>`: Simulate, wake a creature, hit it for 1000, pictures as it dies.
  - `py playtest.py fight day --count 2 --fall`: Play, click through the opening, wake larder rats and
    fight them with the hit rules; prints the rules' tally (`Hits`, `Misses`, `Crits` on the plot
    manager) and health, then lets the player fall (game over, the level reloads 5 s later, which
    resets the tally).
  - `py playtest.py larder day`: Play, the whole larder fight as the game stages it (all 18 rats in their
    waves) with the game's attack timing; samples rats biting, health and who is down, then a RESULT line.
    Measured in game time (it may run slower than real time when the PC is busy).
  - `py playtest.py talents night`: Play, the player gets six talents (rows from `daotools.abilities`)
    and uses them in turn on a soldier woken at night (`--tag`), each use and its result read in one
    editor call (a call takes seconds of game time): stamina spent, upkeep, buffs, stun, knockdown, slow,
    refusals on cooldown or without stamina. The soldier is topped up with `TakeHit(-600)` so the mabari
    does not finish it first.
  - `py playtest.py threat night`: Play, two soldiers woken by the player and the mabari; prints each
    soldier's target and threat table at the start, while fighting, after Threaten, Taunt, Feign Death
    on and off, and Disengage. Player and soldiers are topped up so nobody falls.
  - `py playtest.py enemytalents night --tags <hostile tags>`: Play, soldiers brought together and woken
    by the player and the mabari; every few seconds each soldier's stamina, talent cooldowns and modes, and
    the player's stun, disarm and talent lock. Pick tags hostile from the start (`NpcHostile`): the
    Teyrna's room soldiers turn hostile only through a plot.
  - `py playtest.py ranged night`: Play, the mabari knocked out and an archer woken 8 m off: whether it
    stands and shoots, its talents, the player's pin and armour; then the player switches to the shortbow
    and shoots it six times from 8 m (each shot read in one editor call).
  - `py playtest.py partytalents night`: Play, the Teyrna woken and in the party beside the player and
    the mabari against the panicked servant's three soldiers and war dog: per fighter its foe, stamina,
    talents cooling down and modes on, Growl's debuff and knockdowns; RESULT lists the talents each used.
  - `py playtest.py clickcheck [night|day] [--tag TAG|--tag ""]`: Play, the original's mouse: a right click
    (the cursor put on the spot's screen point, when the cursor is really on what is meant; else CommandAt)
    on the floor, on a hostile woken 8 m off (the mabari knocked out, the hostile kept above 40 health), and
    on the nearest friendly character with a conversation. The night's only one runs off on a script: check
    talking with `day --tag ""`.
  - `py playtest.py pausecheck night`: Play, the Teyrna and the mabari in the party; three hostiles woken
    and the game paused in the same editor call (each call lets some 10 s of game go by). It checks that game
    time and places stand still; queues the hero's attack and talent; orders F2's member to use a talent (--slot)
    and F3's to hold; then resumes and samples what went off.
  - `py playtest.py party day --wipe`: Play, Gilmore and the mabari join against six larder rats; the
    player is dropped, the test wins the fight and checks everyone gets up, then knocks all out (game
    over). Winning starts Gilmore's end-of-fight conversation, as the castle's script does.
  - The user may be watching a test run in the editor: clicks and attacks there mix into what it
    measures, so say what a run will do (e.g. "it drops your health on purpose") before it starts.
- `game.py`: play like a player in Play (`g = game.Game("night")`): `talk_to`, `converse`, `use_door`,
  `fight`, `flags()` / `has(...)` by flag name, `where()`, `errors()`. For a new kind of check, add a
  command to `playtest.py` built on `Run` and `game.Game` rather than a one-off script.
- `pie.py` (start/stop, `cmd` for console commands such as `ke * Choose 0`, `shot`, `dlg`, `log`) and
  `pyrun.py` (Python inside the editor; `unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()`
  is the running world) underneath.

Run from `tools/unreal` in Git Bash with `export MSYS_NO_PATHCONV=1`. A run takes 2-5 minutes (the
loader needs ~100 s to build the castle): run it in the background or with a long timeout.

## Simulate or Play

- Simulate: free camera (`SetCameraTransform` then capture), no player pawn, so nothing that needs the
  player works (party following, the dialogue camera, `GetPlayerPawn`). Good for looks and set pieces.
- Play: the player's camera and the dialogue panel; `CaptureEditorImage` (`pie.shot`) shows the game
  viewport with its UI. Needed for conversations, cameras, combat with the player.
- The night opens with the dog's conversation and the day with Bryce's; characters stand still during
  conversations, so click through first (`game.converse()` or `ke * Choose 0`).
- Inactive NPCs (waiting for a plot) are hidden and do not tick: `call_method("SetPlotActive", (True,))`
  wakes one. Python cannot spawn into the running world or add components to its actors.

## Framing

- An NPC actor's origin is at its feet; a human head is ~158 cm up, a mabari's ~80 cm.
- `playtest.Run.around(act, dist, height, pitch, turn)` builds a camera around an NPC from its facing.
  Interiors are tight: if a picture shows a wall, try another `turn` (90 for the side) or a shorter `dist`.
- A camera jump blurs the next frame (motion blur): `Run.shot` waits 3 s after moving the camera.

## Before you start

- One session drives the editor at a time: check for other running sessions using it (Play started by
  one stops the other's). Ask the user before bringing the editor window to the front.
- The editor must be open with its MCP server up (the unreal-editor skill: "Connecting").
- `playtest.py` turns off background throttling for the run and restores it after.
- Tests are silent (the voices and music woke the user's household): `pie.start` turns
  `EnableGameSound` and the editor's own sounds (`bEnableEditorSounds`: a chime as Play or Simulate
  starts and stops) off and mutes the editor in the Windows volume mixer (`mute.ps1`: the house heard a
  test with both switches off) before every test Play or Simulate; `pie.stop` turns them back on, so the
  user's own Play keeps its sound. Never start Play or Simulate any other way. When the user asks to
  hear a test, pass `--sound` to `playtest.py` (or `pie.start(sound=True)`).
- Send the user the sheet (SendUserFile) and say what was and was not seen.
