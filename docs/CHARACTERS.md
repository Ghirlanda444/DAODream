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

### What you do (Epic Games Launcher)

MetaHuman Creator has a Python API (`unreal.MetaHumanCharacterEditorSubsystem`,
with Epic's examples in the engine under
`Engine/Plugins/MetaHuman/MetaHumanCharacter/Content/Python/examples`): creating
the asset, body measurements, face sculpting, skin, hair and beard grooms,
clothing and colours, the face rig and textures (Epic's cloud services) and the
assembly. Claude runs it from the editor's console (`py <script>`), so only the
Launcher step is manual:

1. Close the editor completely (it then loads `MetaHumanCharacter`,
   `ChaosClothAsset` and `ChaosClothAssetEditor` on the next start).
2. Epic Games Launcher: Unreal Engine > Library > the 5.8 engine tile > the
   arrow next to Launch > Options > tick **MetaHuman Creator Core Data** >
   Apply, and wait for the download. It installs the hair, beards, clothing and
   presets (`/MetaHumanCharacter/Optional/...`) the scripts use.
3. Open the project again. If the editor asks you to sign in to Epic for the
   face rig or textures, sign in.

### What Claude scripted (done)

- `MHC_Bryce` in `/Game/MetaHumans/Bryce`, from the Lorenzo preset: a man in
  his late fifties, tall and broad (186 cm), a soldier gone grey; slicked-back
  dark hair going grey, a full grey beard and moustache; dark green shirt.
- `MHC_HoweSoldier` in `/Game/MetaHumans/HoweSoldier`, from the Bruce preset: a
  man in his thirties, lean and hard (180 cm), brush-cut dark hair, stubble;
  rust-red shirt (Howe's colour).
- Clothing for this test: the Core Data's default garment (shirt and shorts,
  barefoot). Medieval outfits come next, from Fab or our own.
- Face rig (joints only) and textures from Epic's cloud services, then an
  optimized, medium-quality assembly: `BP_MHC_Bryce` and `BP_MHC_HoweSoldier`
  in `/Game/MetaHumans/MHC_<name>/`, shared assets in `/Game/MetaHumans/Common`
  (about 0.8 GB on disk, git-ignored).

Notes for the next characters: the rig and textures ask for an Epic sign-in the
first time (a device-code page opens in the default browser; only the newest
page works, and the code expires in 10 minutes; the sign-in then lasts months).
Assembling a second character in the same editor session ran the GPU out of
memory and crashed the editor, so restart between assemblies. The GPU skinning
settings MetaHumans need (`r.GPUSkin.Support16BitBoneIndex`,
`r.GPUSkin.UnlimitedBoneInfluences`) are in `Config/DefaultEngine.ini`.

### The named cast, from the original's data

Each character's look in the game is a head morph (`hm_gen_<name>.mor` in
`packages/core/data/face.erf`, a GFF4 `MORP` file `daotools pull` converts to
JSON into git-ignored `extracted/faces/`). It names the hair and beard models,
the skin, eye and hair textures and colours, an age blend, and holds the
sculpted face mesh. Original models are reference only (`docs/ROADMAP.md`), so
the mesh is only looked at (rendered as front and side point clouds); the
MetaHuman is built from presets and the colours and styles the morph lists.

Per character: pick the nearest preset(s) by face shape, blend their face
models (`get_face_model_coefficients` / `set_face_model_coefficients`), choose
an older or younger skin texture (`skin_settings.skin.face_texture_index`) to
match the age blend, and the nearest Core Data grooms; then rig, textures, a
fresh editor, assembly, and one line in the looks table.

- **Duncan** (`bhn100cr_duncan`, `MHC_Duncan` in `/Game/MetaHumans/Duncan`):
  morph `hm_gen_duncan` gives tied-back black hair, a near-black full beard,
  dark brown eyes, a tanned skin and an age blend of 0.45; a realistic
  reimagining of his portrait (made by the user) set the target. Face ("E3"):
  Bruce 0.4, Victor 0.3, Dominic 0.2, Walter 0.1, then four passes of landmark
  moves widening the jaw (landmarks 92/91/46/68/43/63 out by 1.5/0.8) and
  lengthening the nose (6/64); skin texture 70 at u 0.62, v 0.47;
  `Beard_L_Full`, `Mustache_L_Full`, `Eyebrows_M_FlatThick`, all black; body
  185 cm, chest 114, shoulders 41, biceps 37. A clean copy is kept as
  `MHC_Duncan_E3_safe`.
  - Hair is our own groom, not a MetaHuman one: `tools/blender/duncan_hair.py`
    grows it on his exported head in Blender (slicked back with a soft
    hairline, sideburns into the beard, a short round ponytail, loose locks
    that leave the hair and fall over the temple and forehead). In Unreal it is
    `Groom_DuncanHair7` (enable `AlembicHairImporter`; hair width override
    0.011 cm) with `MI_DuncanHair` (black). The build always puts MetaHuman's
    own hair back, so run `tools/unreal/duncan_groom_apply.py` in the editor
    after every Duncan assembly: it binds the groom to his face mesh and sets
    it on `BP_MHC_Duncan`.
  - Tried and dropped: fitting the face to a 3D head made from the portrait
    (TripoSG, run locally; Hunyuan3D's licence excludes the EU) with
    `conform_to_target_meshes`. The solver either twisted the body or fell
    back to an average face. Hand sculpting in the Creator is the way to push
    the likeness further.
  - To fix: in game his skin pokes through the placeholder shirt at the right
    shoulder (it follows the mannequin's skeleton; outfits and retargeting
    will fix it).

### How a look is worn (done)

- The looks table lives on `BP_DlgNPC` (class defaults, committed):
  `LookTags` holds creature tag prefixes and `LookClasses` the MetaHuman
  Blueprint for each, as soft paths. Today: `bhn100cr_father` (Bryce),
  `bhn200cr_howe_` (every Howe soldier at night, knight and mage included) and
  `bhn100cr_howe_guard` (Howe's two guards by day) to the soldier;
  `bhn100cr_duncan` (Duncan).
- `SetupCombat` calls `ApplyLook` with the creature's tag. On a match it loads
  the class, spawns the MetaHuman (collision off), attaches it to the
  mannequin, and `FollowMesh` makes the MetaHuman's `Body` copy the
  mannequin's pose bone by bone (leader pose; the face and clothes follow the
  body). The mannequin is hidden but keeps animating
  (`AlwaysTickPoseAndRefreshBones`), so walking, attacks and the ragdoll work
  unchanged. `SetPlotActive` shows and hides the look with the creature.
- A fresh clone without the MetaHumans loads nothing and keeps the mannequins.
- The body takes the mannequin's proportions (no retargeting yet), which suits
  average builds; very tall, short or broad characters will need an IK
  retargeter.

### Checks in Play (2026-10-17)

- Day castle: Bryce opens the origin as a MetaHuman (face, hair and beard
  render, the idle plays); Howe's two guards wear the soldier; killing a guard
  drops him in a ragdoll.
- Night castle: the soldiers' first wave fights and dies as MetaHumans.
- Crowd: all 55 of Howe's night soldiers wear the look, so the cost of loading
  is paid at once; then 10, 20 and 40 of them stand in the main hall around
  the player (Play in the editor, not throttled):

| Soldiers in view | Frame rate | Editor memory | Free RAM |
| --- | --- | --- | --- |
| none (all spawned) | 110 fps | 3.95 GB | 1.3 GB |
| 10 | 82 fps | 3.96 GB | 1.5 GB |
| 20 | 73 fps | 3.76 GB | 2.0 GB |
| 40 | 62 fps | 3.75 GB | 1.8 GB |

Against the mannequin baseline below, the MetaHumans roughly double the
editor's memory (2 GB to 4 GB, one face and one outfit shared by every soldier)
and cost about a quarter to a half of the frame rate with 10 to 40 in view.
That is playable on this PC, so MetaHumans can carry the crowds with a few
reused faces; each extra variant adds its own textures, so keep the variants
per faction few and check memory as they are added. Next: medieval outfits,
then the rest of the named cast.

### Outfits (started, parked)

`tools/blender/outfit.py` grows a medieval base outfit on a MetaHuman's full
body: a padded gambeson with long sleeves, a belt and a flared skirt to
mid-thigh, trousers and boots. Each piece is cut from the body surface by the
bone that drives it, smoothed and pushed out, so it keeps the body's skin
weights; the skirt and belt are tubes sized from the hips' outline. Input is
the uncut body (`export_geometry` with `body_skeletal_mesh`, since the
assembled body has the skin under the default clothes removed); output is one
skeletal mesh on `metahuman_base_skel` with three slots. Howe's soldier has
one imported (`/Game/Outfits/HoweSoldier/SKM_HoweSoldier_Outfit`) with
`M_Cloth` (colour, roughness, quilting lines) and Howe's red, brown and dark
leather instances. Not yet worn: the remaining step is to swap it into the
built Blueprint's clothing component after each build. Parked so that all the
humans are made first.

Armour and weapons should also drive combat: `stats.py` already takes damage
from the equipped weapon's base item, but armour is not modelled yet (hits are
computed against no armour). Outfits will follow each creature's equipped
chest item, and its armour value will go into the hit and damage rolls.

Baseline with the mannequins, Howe's soldiers standing in the night
castle's main hall around the player (Play in the editor, not throttled):
10, 20 and 40 soldiers all run at about 116-120 fps (the editor seems to cap
near 120), with the editor at about 2 GB and 1.7-2.0 GB of RAM free. One
sample dropped to about 20 fps for a few seconds with nothing changed; with so
little RAM free, Windows may have been paging.
