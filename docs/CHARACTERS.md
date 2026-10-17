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
  morph `hm_gen_duncan` gives his own hair and beard (tied back, short full
  beard), black hair, a near-black beard, dark brown eyes, a tanned skin tint
  and an age blend of 0.45. Built from Victor's face blended half and half with
  Walter's, Walter's older skin (texture 121) tanned (u 0.42, v 0.45),
  `Hair_S_LowPonytail`, `Beard_S_Full`, `Mustache_S_Full`; 183 cm, fit; a dark
  blue shirt until the Grey Warden outfit exists. To fix: in game his skin
  pokes through the shirt at the chest and shoulder (not in the Creator, so it
  comes from following the mannequin's skeleton), and the beard reads thinner
  and browner than the original's.

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

Baseline with the mannequins, Howe's soldiers standing in the night
castle's main hall around the player (Play in the editor, not throttled):
10, 20 and 40 soldiers all run at about 116-120 fps (the editor seems to cap
near 120), with the editor at about 2 GB and 1.7-2.0 GB of RAM free. One
sample dropped to about 20 fps for a few seconds with nothing changed; with so
little RAM free, Windows may have been paging.
