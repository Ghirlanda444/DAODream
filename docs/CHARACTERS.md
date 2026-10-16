# Characters: replacing the mannequins

Every creature is still the UE5 mannequin (Manny, Quinn for women, smaller ones
for dwarves and animals). Phase 2 gives them a real look. The original models
are reference only (`docs/ROADMAP.md`, "What is not reused"); the new ones come
from Epic's tools and Fab.

## Approach (hybrid)

| Who | Placements | Source |
| --- | --- | --- |
| The named cast: Bryce, Eleanor, Fergus, Oriana, Oren, Gilmore, Duncan, Howe, Nan, Landra, Dairren, Iona, Aldous, Mother Mallol, the squires and the librarian; the player | ~17 characters, 1-2 placements each | MetaHumans, made in MetaHuman Creator in the editor (plugin `MetaHumanCharacter`, enabled in `Cousland.uproject`) |
| Howe's soldiers, archers, guards, knight and mage | ~56 | a Fab medieval soldier pack, a few variants |
| Cousland guards | 31 | the same pack, Cousland colours |
| Servants | 13 | the same pack or MetaHuman crowd variants |
| The mabari, giant rats | 3 + 18 | Fab animals |

Faces matter in dialogue, so MetaHumans go where the camera lingers; armoured
crowds come from a pack, which is also lighter on this PC (16 GB of RAM, up to
~90 characters at once in the night castle). MetaHuman Creator's own wardrobe is
modern, so medieval clothing and armour come from Fab as well.

## Assets stay out of git

The repository is public, and MetaHuman and Fab content may not be
redistributed as raw assets. Like the game data in `extracted/`, they live in
git-ignored folders (`Unreal/.gitignore`):

- `Content/MetaHumans/`: MetaHuman Creator's characters and assembled output.
- `Content/ThirdParty/`: Fab packs (move a pack here in the Content Browser
  after adding it; references follow).

What is committed is ours: the Blueprints and data that pick a look for each
creature and drive it. A fresh clone needs the same assets re-created or
re-downloaded; this file lists them.

## First slice: Bryce and one of Howe's soldiers

One named MetaHuman and one pack soldier, working end to end in Play before the
rest of the cast: look, animations (idle, walk, jog, attack, death ragdoll),
dialogue, combat, and the frame rate and memory with them in the night castle.

### What you do in the editor

1. Restart the editor (the MetaHuman plugin loads at start-up).
2. Bryce in MetaHuman Creator: Content Browser, right-click in
   `Content/MetaHumans/Bryce`, MetaHuman > MetaHuman Character, name it
   `MHC_Bryce`. Brief, in our own words (check against the original in the
   game):
   - a man in his late fifties, tall and broad, a soldier gone grey;
   - weathered, warm face, strong nose and brow, laugh lines;
   - dark hair going grey at the temples and receding, worn short;
   - a short full beard, greyer than his hair;
   - any clothing for now: medieval clothes come with the Fab assets.
   Assemble with the lighter, game-ready option (not cinematic) into
   `Content/MetaHumans`. Texture downloads may ask you to sign in to Epic.
3. A soldier from Fab: a free, rigged medieval soldier or knight (light armour
   and helmet; a skeletal mesh on the UE5 mannequin skeleton, or one with an IK
   rig, so our animations retarget). Add it to the project, then move it to
   `Content/ThirdParty/<pack>`.

Tell Claude the asset paths when both are in.

### What gets wired (Claude)

- A looks table (our data, committed): creature tag or template -> look asset.
- `BP_DlgNPC`: a creature with a look hides its mannequin but keeps it
  animating; the look's meshes follow it through an IK retargeter (Manny to
  MetaHuman, Manny to the pack's skeleton), so walking, fighting, talking and
  the ragdoll keep working unchanged.
- Checks in Play: Bryce's opening and night scenes, a fight with the soldier,
  the frame rate and memory in the night castle.
