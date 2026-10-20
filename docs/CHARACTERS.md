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

### All the humans of the castle (2026-10-18)

Every look is keyed by who the creature is, so it is reused in later modules:
the area export writes each creature's head morph (`NpcMorph`, e.g.
`hm_gen_duncan`, the same in every module that has Duncan) and a crowd face
(`NpcCrowd`, `crowd_m_0`-`5` / `crowd_f_0`-`1`, a stable hash of tag and
position, adult humans only). The loader applies the morph's MetaHuman first,
then the crowd face (`GiveNpcLook`).

Faces are made in batches by `tools/unreal/metahuman_make.py` from
`tools/unreal/metahuman_recipes.json`: one fresh editor per character
(assembling two in one session runs the GPU out of memory), preset mix,
grooms (`""` removes the preset's), colours, skin texture and tone, body,
optional landmark sculpting, face rig, textures, assembly (named characters
MEDIUM, crowd faces LOW), and a Creator picture for review.

Ferelden is medieval England (its war with Orlais is the Hundred Years' War):
everyone in the castle but Duncan is white, mostly North European. Only these
presets are used for them: Orlando (the best North European base), Bruce and
Walter, with Lorenzo and Victor for a Mediterranean touch; Vivian and Jelena
for women (Celeste reads East Asian next to them; only Oriana, an Antivan,
keeps a share). Age comes from older skin textures (121, 151) toned pale
(u 0.22-0.27), never from the older Asian presets. Reference pictures from
the user (front portraits) steer individual faces: Arl Howe has combed-back
grey hair, a narrow hollow-cheeked face and the soul patch his son Sebastian
shares (`Goatee_S_SoulpatchStrip`).

Made: Duncan (V2, Fergus's square jaw, custom hair), Fergus, Eleanor, Gilmore, Dairren, Arl Howe, Aldous, the librarian,
Howe's knight, Landra, Oriana, Mother Mallol, the cook, and crowd faces
`CrowdM1`-`5`, `CrowdF0`-`1` (the first Howe soldier is `crowd_m_0`).

Still to do in this castle, each needing more than MetaHuman: elves (Iona,
the servants, Howe's mage) need pointed ears made in Blender; children (Oren,
the squires) need a child body. Later modules will also need dwarves (a short,
stocky MetaHuman body) and Qunari (tall, grey skin, horns made in Blender).

Two kinds of faces (the user's direction, 2026-10-18). DAO built its NPCs from shared
parts (hairstyles, noses, mouths, skin tones mixed per head), so:
- Minor characters and crowds (servants, guards, soldiers, the elven servants, Howe's
  mage): made from templates and varied by combining parts (preset mix, hair, beard,
  skin), as the crowd faces are.
- Main characters (Bryce, Eleanor, Fergus, Oren, Iona, Duncan, the player, antagonists
  such as Howe): unique, each from a reference the user gives (a realistic reimagining of
  the original portrait, kept in git-ignored `extracted/refs/`). Quick previews first
  (`"preview_only": true` in a recipe: no rig, textures or assembly), then the full build.
  Done one at a time: Bryce, then Duncan (V3: MetaHuman ponytail and beard, nose and brows from preset weights, brown eyes copied from a preset with `"eyes_from"`). Strong landmark sculpting distorts the face; small moves only.
  Duncan in game was `DuncanH` (2026-10-19), now `DuncanS` (below): a copy of DuncanV3 whose face the Creator fitted
  (`conform_to_target_meshes`, head only, brows to under the nose) to a 3D head generated locally
  from the user's front reference; the generator and its meshes stay outside the repo. The photo
  was projected onto that head and tracked from a front camera. The fit matched the front but gave
  a sloped forehead and a protruding mouth and chin, so the profile line (forehead, brows, nose,
  lips, chin) was moved back to DuncanV3's depths with landmark moves, the ring around mouth and
  nose halfway. Built with `"existing": true` in its recipe (no create or look step, so the fitted
  face survives; its `grooms`, `colours` and `body` are still applied). Grooms from the same
  reference, chosen by trying candidates side by side on the built Blueprint: `Beard_L_Full` (the
  scan's beard is about 2 cm thick on the jaw and hangs 3-4 cm below the chin), `Mustache_L_Full`
  (thickened 1.15), `Eyebrows_M_Dense`, `Hair_S_LowPonytail`, all dark brown (melanin 0.85-0.88,
  redness 0.2). DuncanV3, the raw fit (`DuncanFit`) and the scan level stay for reference.
  A second fit, `DuncanS`, used a clean-shaven version of the same reference (front, side): its
  generated head shows the real jaw and chin, so the fit took the mouth, chin and jaw too; its profile
  matched the shaved side view except the brow ridge, pushed 0.4-0.8 cm forward (the face model
  stops there). Same grooms and colours as DuncanH. Compared in the portrait booth
  (`tools/unreal/booth_shot.py`); the user chose it, and `hm_gen_duncan` now loads `DuncanS`.
  Bryce in game is now `BryceW` (2026-10-19), made the same way from the user's Bryce sheet.
  Fitting Bryce's own character failed: it uses an older 125-point landmark layout and the solver
  shifted the head off the neck, so the fit starts from DuncanV3 (79 points) and takes Bryce's
  skin, eyes, body and grooms; the fit area leaves out the hair hanging beside his cheeks, then the
  chin and brow are pushed toward the side view. Ash grey-brown hair and a stubble layer.
  Fergus (`FergusW`) and Eleanor (`EleanorS`) followed on 2026-10-20, each from the user's sheet
  (front, three-quarter, side). Fergus also has the 125-point layout, so he is fitted on DuncanV3's
  base (fit area clear of his fringe and side hair), with his skin and body, brown eyes, a chestnut
  low ponytail and a short beard over stubble. Eleanor fitted on her own copy (81-point layout,
  small shift); grey hair pulled back to a low ponytail (no MetaHuman groom has her low braided bun),
  darker brows, and makeup set on the character with `commit_makeup_settings`: soft smoky
  green-grey eyes and natural mauve lips. The looks table loads both.

Unreal's local cache (Zen) is moved to `E:/UnrealDDC` in `DefaultEngine.ini`: with C:
full, groom bindings and shaders silently failed to cache (Duncan's hair stayed in its rest
pose, floating above his head). The custom groom's binding must be set again after the
Blueprint compiles (`tools/unreal/duncan_groom_apply.py` does).

### Hair strands in close-ups (2026-10-18)

Beards rendered as black, speckled, dithered patches in dialogue. The cause was not the
bindings (all matched their face mesh) but the Optimized assembly: it copies each groom
into `MHC_<Name>/Grooms` with the strands stripped (1 curve instead of tens of thousands)
and maps LODSync to groom LODs 3/5/7 (named characters) or 5/7 (crowd faces), i.e. hair
cards and meshes only. Epic's grooms hold strands at LOD 0-1, cards at 2-4, meshes at 5-7.

- `tools/unreal/metahuman_strands.body.py` (run by `metahuman_make.py` after every build)
  points Hair/Beard/Mustache/Eyebrows back at Epic's original grooms, binds each to the
  character's face with a transfer from the template head the groom was authored on
  (`SKM_Groom_Head_Legacy01/02` or `MH_Groom_Head`, read from Epic's template binding;
  without it the roots land in the wrong place), keeps the assembly's material overrides,
  and maps LODSync to 0/3/7 (strands, cards, meshes) or 0/3 for crowd faces. A recipe's
  `"thicken"` factors widen the strands of a copy in `/Game/MetaHumans/<Name>/Strands`.
  Applied to all 22 faces in use (not the unused drafts `Duncan`, `DuncanV2`).
- Dialogue: `BP_PlotManager.ConversationStarted/Ended` call `BP_DlgNPC.DialogueLOD` on
  every NPC, which sets the look's LODSync `ForcedLOD` to 0 (strands) for looks within
  25 m of the player while a conversation runs and back to -1 (automatic) when it ends.
  It also switches on two hidden rect lights on looks within 6 m (`DlgKey`, `DlgRim` on
  BP_DlgNPC, found by name at runtime): a soft key from the viewer's left and a rim behind,
  placed from the head toward the player camera at the conversation's start, off at its end.
  The effect is modest while conversations use the normal third-person camera (about 5 m
  away) under the bright blockout light; close-up dialogue cameras would make it count.
- Groom layers: a recipe's `"layers"` adds extra groom components (e.g. Duncan's
  `BeardBase`, `Beard_S_Stubble` under `Beard_L_Full`, so skin does not show through the
  beard); `metahuman_strands.body.py` binds them like the others.
- `DefaultEngine.ini [SystemSettings]`: strands on, 8 visibility samples per pixel with a
  full sample budget, and TSR's flicker rejection kept on at every scalability level.
  Also `r.HairStrands.RasterizationScale=1.0` (strands at least a pixel wide, default 0.5),
  `Voxelization=1`, `DeepShadow.Resolution=4096` and `DeepShadow.SuperSampling=1` (cleaner hair
  self-shadows). Anti-aliasing is not a post-process or camera setting in UE 5.8 (it is the global
  `r.AntiAliasingMethod`; post-process screen percentage is deprecated), so
  `BP_PlotManager.ConversationStarted/Ended` switch to TAA at 100% screen percentage for the
  conversation and back to TSR after: side by side, TAA gave the cleanest beard.
- Groom tuning per recipe (2026-10-19): `"thicken"` takes `{"width", "tip", "density"}` per groom
  (wider strands, fuller tips, fewer strands close up, so hair reads as a volume, not specks) and
  `"groom_material"` sets roughness/specular on the groom materials (softer, less shiny). Duncan:
  beard x1.3 width, tips 0.7, 75% of strands; hair x1.2, 85%; roughness 0.72, Spec0/1 0.3/0.5.
  The dialogue key light is a large soft source (110 cm, intensity 18) with the rim behind.
  The same tuning is the batch maker's default (`DEFAULT_THICKEN`, `DEFAULT_GROOM_MATERIAL`),
  applied to all 22 MetaHumans in use on 2026-10-19; a recipe's own values replace it.
- Under the very bright blockout light, the edge strands facing it read white (strong
  specular); the shaded side is clean. To revisit when the castle gets its real lighting.

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
