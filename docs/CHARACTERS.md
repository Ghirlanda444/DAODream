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
    (TripoSG, run locally) with
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

Crowd variety (2026-10-22): so the few crowd faces don't read as twins, the
export also writes `NpcVariety`, 11 floats per creature from the same key
(`area.variety`): a skin multiply between fair and light brown (most fair;
Ferelden has no darker crowd), hair melanin and redness (flaxen, dark blond,
brown, near black, one in ten auburn or ginger), and for servants' clothes
(`cth_com_*`) a dye for the outfit's main and second cloth from plain wools
and linens (undyed, oatmeal, walnut, russet, madder, weld, moss, woad,
blue-grey, grey, dark; the second layer brown, grey or dark). Uniforms and the
nobles' colours stay as made. After the outfit, `GiveNpcLook` calls
`BP_DlgNPC.ApplyVariety`, which acts only on crowd looks (`MHC_Crowd*`,
`MHC_HoweSoldier`), so named characters keep their designed looks: it sets
`Basecolor Global Multiply Post-Bake` on the Face and Body materials,
`hairMelanin` and `hairRedness` on every groom (white from age is kept), and
dyes the outfit's `Main` and `Second` slots through dynamic instances
(`DyeSlot`: ColorA the dye, ColorB 1.35 times it, Trim 0.75 times).

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

Elves (2026-10-23) have crowd faces of their own: the export gives every adult elf
without a look of its own `crowd_elf_m_<n>` / `crowd_elf_f_<n>` (`area.CROWD_FACES`),
made by `CrowdElfM0`-`1` and `CrowdElfF0`-`1` (young, slim, beardless, hair back so the
`"elf_ears"` show, as for Iona) and varied like the human crowd. That dresses the
castle's elven servants and Howe's mage (a female elf in an apprentice robe), and any
elf of a later module. Children (Oren,
the squires) stand at 67% in game (`area.CHILD_SCALE`, from their `kn_*` heads), since
MetaHuman has no child body; Oren's face (recipe `Oren`) is a young adult mix, and landmark
sculpting toward child proportions read as an adult, so it was dropped. The user chose this face for now;
the looks table maps `kn_bhn100_oren` to it (2026-10-20). Later modules will also need dwarves (a short,
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
  Iona (`Iona`, 2026-10-20) is an elf: a slim young preset mix (Jelena/Vivian, jaw slimmed; a fit
  to her sheet read too heavy and was dropped), green eyes, and pointed ears shaped on the built
  face mesh by `tools/unreal/elf_ears.body.py` (MetaHuman has no elf ears). Her hair is a custom
  groom from `tools/blender/iona_hair.py`, after the user's sheet: straight, centre-parted,
  shoulder length, hugging the skull and tucked behind the ears, side braids meeting in a hanging
  back braid, and two front braids with tassels; `tools/unreal/custom_groom.body.py` puts it on
  her Hair slot after every build (recipe `"custom_hair"`). Under the castle's dim blockout light,
  hair (MetaHuman grooms too) goes almost black where no light reaches it; the dialogue key and rim
  lights fix it during conversations. Fixed for all characters by `r.HairStrands.SkyLighting.
  IntegrationType=1` (uniform ambient integration, DefaultEngine.ini); MetaHuman's hair-material
  "fill light" was tried first and has no effect on strands (it is for hair cards).

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
- Dialogue camera (2026-10-22): every spoken line cuts to a close-up of its speaker.
  `BPC_DialogueRunner.ShowNode` calls `FocusLine` after the line's voice starts: the
  speaker `OWNER` is the runner's NPC, any other speaker tag the first `BP_DlgNPC` with that
  tag (`PLAYER` and captions find none and keep the shot). `BP_PlotManager.FocusSpeaker`
  takes the speaker's head (`HeadOf`: the stand-in's `head` bone, which the MetaHuman
  follows, or the mabari's `Wolf_-Head`), then turns `BP_DlgCam` toward it from halfway
  between the player and the way the speaker faces, so the face shows three-quarter
  even when the speaker turns to someone else, and the player stands out of the shot.
  `BP_DlgCam` is a spring arm (220 cm, 6 degrees from above, 16 cm to one side, probing the
  Camera channel so walls pull it in) and a 30-degree camera tilted 3 degrees down, which
  puts the face above the dialogue panel. A speaker that is hidden (inactive, ticking off:
  the night's warning servant, who talks before his plot shows him) keeps the previous shot.
  `ConversationEnded` blends back to the player's camera in 0.35 s unless another
  conversation has already started. NPC capsules ignore the Camera channel
  (`InitNPC`), so neither this arm nor the gameplay camera's stops at a body.
  Checked in Play: Bryce and Howe in the day castle's opening, the mabari at night.
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

### The mabari (2026-10-22, started)

The hero's mabari is made from the wolf in Epic's free ANIMAL VARIETY PACK
(Protofactor, Fab, Standard Licence; added through the editor's Fab panel at its
5.5 version, which loads in 5.8, into the git-ignored `Content/AnimalVarietyPack`).
The wolf brings a 33-bone skeleton and 29 animations: bite, jump and running
bites, hits from the front, left and right, death, an aggressive idle, howl, walk
and run with turns (each also with root motion), rest, sleep and getting up.

`tools/blender/mabari.py` reshapes the wolf's body into a mastiff and keeps its
skeleton and skin weights, so every animation still plays: the fur cards go (a
short coat), the seams are welded, neck, chest and legs thicken round the line
from each joint to the next (the shoulders grow out and down, so the back stays
level), the chest deepens, the bushy tail thins to a whip, the muzzle is
shortened by half and broadened, the skull widened and the ears cropped; one
subdivision smooths it. Vertex colour R marks the kaddis (a blaze on the head, a
stripe along the spine, two slashes on each shoulder). `mabari_build.body.py`
makes `/Game/Cousland/Mabari/M_Mabari` (committed: the coat texture darkened,
faint brindle from the pre-skinned position, the kaddis brushed in red) and, in
the git-ignored `/Game/ThirdParty/Mabari`, the mesh `SK_Mabari` on the wolf's
skeleton and `MI_Mabari` with the wolf's dark coat textures. `dog_shot.py` takes
booth pictures of it posed by any of the animations. Visual reference: the
Bestiarum mabari plate (Rich Longmore), looked at only.

Every mabari shares the one material, and each dog gets its own coat through its
mesh component's custom primitive data: 0-2 the coat colour (all 0 keeps the
wolf's dark coat), 3 how strong the brindle is, 4 set to 1 to leave off the
kaddis. The area export picks the coats (`area.mabari_coat`; `MABARI_COATS`,
also read by `tools/unreal/mabari_coats.py`): the hero's dog (`gen00fl_dog`) is
fawn, light brown; the war dogs of Howe's men (`dog_mabari_*`) take black,
brindle, red, grey, tan or black without paint, picked from their tag and
position so a dog always looks the same (the night castle's three: grey,
brindle, black unpainted). `mabari_lineup.py` stands every coat side by side
in the booth.

In game (2026-10-22): a mabari's crowd key is `mabari` and its `NpcVariety`
holds its coat, so `GiveNpcLook` gives it the look `BP_Mabari` like any
MetaHuman look (spawned on the stand-in, which it replaces and follows) and
`ApplyVariety` hands the coat to `ApplyCoat`, which writes it into the look's
custom primitive data. The stand-in keeps its 0.6 scale (its capsule is
dog-sized); `BP_Mabari` always stands at scale 1, about 95 cm at the head.
`DialogueLOD` skips looks without a MetaHuman `LODSyncComponent`.
`tools/unreal/beast_anim.py Mabari` builds, in the git-ignored folder (the same script builds any
animal reshaped from the pack; see "The giant rat" below):

- `BS_MabariMove`: the wolf's idle, walk and run by speed (0, 93 and
  444 cm/s, what the walk and run cover).
- `ABP_Mabari`: that blend space through the `DefaultSlot` to the pose. Every
  update measures how far the dog moved (stand-ins are moved by script, not
  physics) and watches the `BP_DlgNPC` it rides on: an attack (its
  `AttackTimer` reset upward) plays the wolf's bite, a hit (its `Health`
  dropping) the flinch. Once it is dead the pose blends to the wolf's death
  animation, played by game time and held on its last frame; a dog already
  dead when first seen lies there at once.
- `BP_Mabari`: `SK_Mabari` with that Animation Blueprint, no collision.

Checked in Simulate: all four dogs of the night castle get their look and
coat and run the update; the hero's dog fights Howe's two men in the
servant's scene with the bite. Not seen yet: a clean walk or run on camera
(Simulate has no player for the party to follow, and walks given by script
finished before a picture). A dog that dies falls and stays as a body:
`BP_DlgNPC.Die` calls `LieDead`, which for a mabari look only turns off the
stand-in's collision, tick and health bar (other creatures are still hidden,
as they have no death animation yet). Checked in Simulate: one of Howe's dogs,
hit for 1000, lies dead where it fell. Not done: a dog placed dead by its
template (`Kill` ragdolls the hidden stand-in, which would carry the dog with
it; none of the castle's dogs start dead), and the hero's dog getting up after
a fight as in the game. Next: a stud collar, short strand fur for close-ups,
and a heavier, blockier head.

### The giant rat (2026-10-24)

The larder's 18 giant rats were small mannequins. They are now reshaped from the
same pack's fox, the way the mabari comes from the wolf, so the fox's 28
animations (bites, hits, death, walk, run with turns, rest) play on them:
`tools/blender/rat.py` drops the fur cards, thins the bushy tail to a bare
tapering rat's tail, shrinks the tall ears to short round ones, hunches the back,
makes the trunk much wider and deeper (the belly hangs low, so the long fox legs
read short), thickens neck and haunches, thins the lower legs and lengthens and
narrows the muzzle; vertex colour R marks the bare skin (tail, ears, paws, nose
tip). `rat_build.body.py` imports it as `SK_GiantRat` on the fox's skeleton into
the git-ignored `/Game/ThirdParty/GiantRat`, with `MI_GiantRat`, an instance of
the mabari's material: the fox's coat tinted a dirty brown-grey, faint mottling,
and the "kaddis" colour set to flesh pink for the bare skin. `beast_anim.py
GiantRat` builds `BS_GiantRatMove` (the fox's walk and run cover 45 and 263 cm/s,
measured from their root-motion tracks; the wolf's measure 93 and 444, as used),
`ABP_GiantRat` and `BP_GiantRat` from the same graphs as the mabari
(`dsl/Beast*.dsl`, with the pack animal's animations filled in).

The export gives an animal its own look by a part of its template's name
(`area.BEAST_LOOKS`: `rat_giant` -> `giant_rat`); `BP_DlgNPC`'s `LookTags` spawn
`BP_GiantRat` for it, about 49 cm tall and 1.07 m long with the tail, and
`LieDead` leaves dead rats lying in their death pose like the mabari.

### Poses (2026-10-24)

An NPC idles in `BP_DlgNPC.IdleAnim` (default the template's `MM_Idle`; every idle in
`AnimTick` plays it), and `ApplyIdle` sets it from the area export's `NpcIdle`
(`area.IDLE_POSES`, by area and tag). The game shows Bryce wounded on the night's
larder floor through its cutscenes' body animations, which Unreal cannot play, so
he gets a held pose: `tools/blender/pose_wounded.py` poses the mannequin skeleton
(bones aimed in world space: down onto the floor and tipped back against the wall,
one leg out, the other knee drawn up, the back slumped, the head hanging, the right
hand pressed to the belly, the left arm limp) and `tools/unreal/pose_make.py`
imports it as `/Game/Cousland/Anims/A_WoundedSlump` (committed: our pose on the
template's `SK_Mannequin`). The MetaHuman look follows the mannequin as always.
Checked in Simulate: Bryce sits slumped against the larder wall.

### Outfits (2026-10-21)

Everyone wears what the game gives them: the area export lists each
creature's equipped items (`NpcOutfit`) and its chest item without
`gen_im_` (`NpcChest`, e.g. `cth_nob_c01`; `docs/COMBAT.md`, "Armour"). An
outfit is made per look and chest item, fitted to that MetaHuman's own body:

```powershell
cd tools/unreal
py outfit_make.py BryceW:cth_nob_c01 EleanorS:cth_nob_af0 CrowdM1:arm_cht_med_chn
```

`outfit_make.py` exports the look's body (`SKM_MHC_<Look>_BodyMesh`) and its
default clothes (`MHC_<Look>_Outfits`, the build's T-shirt and shorts: the
build cuts the body away under them, so together they are the whole figure),
runs `tools/blender/outfit.py` on them, imports the result as
`/Game/MetaHumans/MHC_<Look>/DAO/SKM_<Look>_<item>` on `metahuman_base_skel`
(`outfit_import.body.py`, legacy FBX importer, vertex colours kept) and sets
its material slots to the item's colours (`MATERIALS`). The outfits are
shaped from the MetaHuman bodies, so like them they stay out of git.

`outfit.py` builds each garment from the body itself, so it fits: shells (the
body's surface over some regions, by the bone that moves each vertex most,
pushed out along its normals, smoothed, cut edges relaxed into hems, kept
outside the body), lofts (skirts and coat tails: rings round both legs, each
the body's convex outline at that height plus an offset and a flare, rounder
towards the hem), and bands (belts). Weights are copied from the body and
smoothed on lofts so a skirt does not split between the legs; vertex colour R
marks 3.5 cm along every hem and cuff for the trim band. The rig is exported
in centimetres, bones and vertices alike: with the bones left in metres the
outfit's bind pose does not match the skeleton and it is drawn a hundred
times too big, nowhere near the body. `outfit_preview.py` renders front, side
and back pictures in Blender. Recipes so far:

| Item | Who | Outfit |
| --- | --- | --- |
| `arm_cht_med_chn` | castle guards (CrowdM1-5, HoweSoldier), Gilmore | mail hauberk with sleeves and a skirt to mid-thigh, Cousland-blue surcoat to the knee with silver trim, belt, hose, boots, gloves |
| `arm_cht_hvy_hch`, `arm_cht_med_scl` | Fergus; Howe's knight | the same with the mail to the knee (scale for the knight, in Howe's red and black) |
| `arm_cht_lgt_ltr`, `arm_cht_lgt_rlr` | Howe's soldiers and archers (CrowdM1-5, HoweSoldier) | Howe-red gambeson with a skirt to mid-thigh, sleeveless leather jerkin, belt, hose, boots, gloves; reinforced: mail forearms and metal shoulders |
| `cth_nob_*` (men) | Bryce, Arl Howe, Dairren | long-sleeved doublet, coat to the knee in the house's colour (Cousland blue, Howe red, green for Landra's house), belt, hose, boots |
| `cth_nob_*` (women) | Eleanor, Oriana, Landra, Iona | gown with long sleeves and a full skirt to the floor, girdle, shoes |
| `cth_com_*` | servants, the cook, the librarian | men: wool tunic to mid-thigh, belt, hose, short boots; women: long dress, apron, belt, shoes |
| `cth_mag_tra`, `cth_cha_a00`, `duncan_robe` | Aldous, Mother Mallol, Duncan | robe to the floor with long sleeves and a cord belt; Mallol's in Chantry white with a red stole, Duncan's in dark Warden blue with gloves |

The same item can dress a man or a woman (the cook and a servant share
`cth_com_c00`), so `outfit_make.py` passes the look's sex (`FEMALE`). Items with no
entry of their own take their family's recipe and colours (`cth_com_*` common clothes,
`cth_mag_*` robes, `cth_nob_*`). Every common item gives the same garment on a given
body (the elves' 11 outfits were 4 shapes), which is why `SCALING.md` moves to one
outfit per body type.

Materials (`/Game/Cousland/Outfits`, committed, procedural from the outfit's
UVs, about 0.7 UV units per metre): `M_OutfitCloth` (twill rib, two-tone
mottle, trim band from the vertex colour; `MI_Cloth_*` colour sets),
`M_OutfitLeather` and `M_OutfitMetal` (riveted rings in staggered rows, or
plain metal with `Rings` 0).

In game `BP_AreaLoader.GiveNpcLook` calls `BP_DlgNPC.ApplyOutfit` with the
NPC's `NpcChest`: it takes the look's name from its body mesh
(`SKM_MHC_<Look>_BodyMesh`), loads the matching outfit if one was made, puts
it on the look's clothing component (`SkeletalMesh`, which already follows
the body's pose) and clears that component's material overrides (the default
shirt and shorts materials, which would otherwise colour the outfit). Looks
without a matching outfit keep their default clothes.

This replaces an earlier, parked generator (a gambeson, trousers and boots for
Howe's soldier; commit 5816892 and the git-ignored `/Game/Outfits`).

Footwear (2026-10-24): boots and shoes no longer follow every toe. Below the ankle
(+6 cm for boots, +2 cm for shoes) `outfit.py` drops the shell, which copied the
foot toe by toe, and puts the convex hull of the foot and ankle in its place,
pushed out a little further than the leg's shell so it laps over it like a
boot's cuff (`shoe_last`). The old boots also showed bare toes because of a
naming trap: MetaHuman's toe bones are `indextoe`, `middletoe`, `ringtoe`, and
the region check matched "index", "middle" and "ring" as fingers first, so the
gloves carried leather toes; toes are now checked first. All 46 outfits were
rebuilt with `outfit_make.py`.

### Helmets (2026-10-24)

The castle's soldiers wear the helmets their game items name: the export writes
`NpcHelmet` (the item without `gen_im_arm_hel_`: 16 by day, 70 at night, only
soldiers). `tools/unreal/helmet_make.py` exports a MetaHuman face (CrowdM1),
`tools/blender/helmet.py` fits an ellipsoid to its skull (front and back fitted
apart) and cuts the helmets from it, in the face's own frame, and they are
imported to `/Game/Cousland/Outfits/Helmets` (committed: built from the
ellipsoid, no MetaHuman geometry) with a steel instance of the outfit metal
without rings (`MI_Metal_Steel`) and `MI_Leather_Brown`:

| Item | Helmet |
| --- | --- |
| `med_hel` (also `hvy_exc`, Howe's knight) | steel nasal helm: dome, brow band, crest, nose guard |
| `lgt_ltr` | leather cap with a rolled brow band |
| `lgt_rlr` | the leather cap with a steel brow band and crest |

In game `GiveNpcLook` calls `BP_DlgNPC.ApplyHelmet` with the NPC's `NpcHelmet`:
it loads `SM_Helmet_<kind>`, adds a static mesh component (`AttachHelmet`)
attached to the look's `Face` at the `head` bone, and hides the `Hair` groom
(`HideHair`), which would poke through. Heads differ (the Howe soldier's sits
4 cm lower on its head bone than CrowdM1's, which buried the helmet in it), so
`helmet_make.py` exports every look's face, fits each skull (`helmet.py --fit`:
centre, and widths measured above the ears) and gives each look its placement:
moved and scaled per axis from CrowdM1's skull onto its own, then carried by the
inverse of the look's own head bone in its bind pose (measured on a spawned face
mesh: the shared face skeleton's reference pose puts the head 30 cm lower).
`AttachHelmet` takes it from `HelmetFits` by `LookName` (`HelmetFitLooks`), or
`HelmetOffset` (CrowdM1's) for a look that has none. Checked in Simulate: the
leather cap (CrowdM5), the reinforced cap (HoweSoldier) and the nasal helm
(CrowdM5) sit on their heads with no hair through them.

Baseline with the mannequins, Howe's soldiers standing in the night
castle's main hall around the player (Play in the editor, not throttled):
10, 20 and 40 soldiers all run at about 116-120 fps (the editor seems to cap
near 120), with the editor at about 2 GB and 1.7-2.0 GB of RAM free. One
sample dropped to about 20 fps for a few seconds with nothing changed; with so
little RAM free, Windows may have been paging.
