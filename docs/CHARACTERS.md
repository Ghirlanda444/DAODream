# Characters: replacing the mannequins

Every creature is still the UE5 mannequin (Manny, Quinn for women, smaller ones
for dwarves and animals). Phase 2 gives them a real look. The original models
are reference only (`docs/ROADMAP.md`, "What is not reused"); the new ones come
from Epic's tools and Fab.

## Approach (hybrid)

| Who | Placements | Source |
| --- | --- | --- |
| The named cast: Bryce, Eleanor, Fergus, Oriana, Oren, Gilmore, Duncan, Howe, Nan, Landra, Dairren, Iona, Aldous, Mother Mallol, the squires and the librarian; the player | ~17 characters, 1-2 placements each | MetaHumans, made in MetaHuman Creator in the editor (plugin `MetaHumanCharacter`, enabled in `Cousland.uproject`) |
| Howe's soldiers, archers, guards, knight and mage | ~56 | MetaHumans if the slice's memory test allows (a dozen faces reused, one outfit per faction), else a Fab pack |
| Cousland guards | 31 | the same, in Cousland colours |
| Servants | 13 | MetaHumans in simple outfits |
| The mabari, giant rats | 3 + 18 | Fab animals |

Faces matter in dialogue, so MetaHumans go where the camera lingers. Whether
they also carry the armoured crowds depends on this PC (16 GB of RAM, up to ~90
characters at once in the night castle), which the first slice measures.
MetaHuman Creator's own wardrobe is modern, so medieval clothing and armour are
modelled by us or come from Fab, as MetaHuman outfits.

## Assets stay out of git

The repository is public, and MetaHuman and Fab content may not be
redistributed as raw assets. Like the game data in `extracted/`, they live in
git-ignored folders (`Unreal/.gitignore`):

- `Content/MetaHumans/`: MetaHuman Creator's characters and assembled output.
- `Content/ThirdParty/`: Fab packs (move a pack here in the Content Browser
  after adding it; references follow).
- `Content/Outfits/`: MetaHuman outfits (the MetaHuman SDK's default Outfits
  path in Project Settings), Fab ones included.

What is committed is ours: the Blueprints and data that pick a look for each
creature and drive it. A fresh clone needs the same assets re-created or
re-downloaded; this file lists them.

## First slice: Bryce and a MetaHuman soldier of Howe's

Both as MetaHumans, so the slice also tests whether MetaHumans can carry the
crowds: Bryce, and one of Howe's soldiers in a simple outfit, working end to
end in Play before the rest of the cast (look, animations: idle, walk, jog,
attack, death ragdoll; dialogue; combat), then several soldiers at once in the
night castle to measure the frame rate and memory on this PC.

MetaHuman Creator makes faces, bodies and hair, and dresses them in outfits
that refit to any body ("parametric" outfits, Epic's
[parametric asset setup](https://dev.epicgames.com/documentation/metahuman/parametric-asset-setup-for-metahuman)).
It does not model clothes: armour (gambeson, tabard, mail, helmets) has to be
modelled elsewhere (Blender) and brought in through that outfit pipeline, or
bought. The slice uses free outfits; armour comes after it.

### What you do (editor and Epic Games Launcher)

1. Close the editor completely. The project now enables MetaHuman Creator
   (`MetaHumanCharacter`) and the outfit plugins (`ChaosClothAsset`,
   `ChaosClothAssetEditor`).
2. In the Epic Games Launcher, Unreal Engine library, 5.8: the arrow next to
   Launch > Options, tick **MetaHuman Creator Core Data**, Apply, wait for the
   download. Then open the project again.
3. From Fab, free (Personal licence), into the project:
   [Poor man Outfit](https://www.fab.com/listings/ebeea391-8264-44ef-8cb0-f4801ffea4a6)
   and [Medieval Old Shoes](https://www.fab.com/listings/d9e8b9a5-718e-4385-8d46-f480a2c22b6c).
   MetaHuman outfits go to `Content/Outfits` (Project Settings > Plugins >
   MetaHuman SDK shows the path); they then appear in MetaHuman Creator's
   Clothing section.
4. Bryce: Content Browser, right-click in `Content/MetaHumans/Bryce`,
   MetaHuman > MetaHuman Character, name it `MHC_Bryce`. Brief, in our own
   words (check against the original in the game):
   - a man in his late fifties, tall and broad, a soldier gone grey;
   - weathered, warm face, strong nose and brow, laugh lines;
   - dark hair going grey at the temples and receding, worn short;
   - a short full beard, greyer than his hair;
   - clothing: the plainest pieces for now (the Old Shoes, dark plain top and
     trousers); a noble's clothes come later.
5. A soldier of Howe's: `Content/MetaHumans/HoweSoldier`, `MHC_HoweSoldier`:
   - a man in his thirties, lean and hard, plain features, stubble or a short
     beard, short dark hair;
   - the Poor man Outfit and the Old Shoes.
6. Assemble both with the lighter, game-ready option (not cinematic), output
   in `Content/MetaHumans`. Texture downloads may ask you to sign in to Epic.

Tell Claude when both are assembled.

### What gets wired (Claude)

- A looks table (our data, committed): creature tag or template -> MetaHuman.
- `BP_DlgNPC`: a creature with a look hides its mannequin but keeps it
  animating; the MetaHuman follows it (retargeted from the UE5 mannequin), so
  walking, fighting, talking and the ragdoll keep working unchanged.
- Checks in Play: Bryce's opening and night scenes, a fight with the soldier;
  then 10, 20 and 40 soldiers in the night castle, recording the frame rate,
  the editor's memory and free RAM each time, to decide how far MetaHumans can
  go for the crowds (LODs, fewer variants, or a lighter source for them).

Baseline with today's mannequins, Howe's soldiers standing in the night
castle's main hall around the player (Play in the editor, not throttled):
10, 20 and 40 soldiers all run at about 116-120 fps (the editor seems to cap
near 120), with the editor at about 2 GB and 1.7-2.0 GB of RAM free. One
sample dropped to about 20 fps for a few seconds with nothing changed; with so
little RAM free, Windows may have been paging.
