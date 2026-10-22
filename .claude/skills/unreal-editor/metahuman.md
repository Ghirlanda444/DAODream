# MetaHumans in DAODream

Background: `docs/CHARACTERS.md`. All MetaHuman content stays in git-ignored `Content/MetaHumans/`.

## Making characters

- Batches: `tools/unreal/metahuman_make.py` + `metahuman_recipes.json`, one fresh editor per character
  (~8 min each; two builds in one session ran the 12 GB GPU out of memory, and opening 20+ presets hangs
  the editor). "Preview Collection build failed" with no reason means: restart the editor.
- Rig and textures need the user's Epic sign-in: `request_auto_rigging` opens a device-code page in the
  user's browser (the code expires in 10 minutes; the refresh token lasts ~6 months). Never type credentials.
- Logged errors during `build_meta_human` surface as Python RuntimeErrors even when the build works: wrap it,
  then look for "Assemblaggio personaggio MetaHuman completato" in the log and the BP on disk. The build
  output is left unsaved: save the dirty `/Game/MetaHumans` packages.
- Faces by script: blend presets with `get/set_face_model_coefficients` + `commit_face_state`; age from
  `skin_settings.skin.face_texture_index`. Strong landmark sculpting distorts the face: small moves only.
- A freshly duplicated character returns no landmarks, and its grooms do not assemble, until the editor
  restarts. A custom groom binding must be set again after `compile_blueprint`.
- Never let a backup script copy over an existing backup.
- Never run a GPU AI job while the editor renders: together they crashed the GPU (device removed).

## In game

- Looks are keyed by head morph (`NpcMorph`) and crowd key (`NpcCrowd`) in `BP_DlgNPC.LookTags/LookClasses`;
  `ApplyLook` spawns the look, attaches it to the stand-in and leader-poses its Body.
- Outfits: `tools/unreal/outfit_make.py`; the outfit component is `SkeletalMesh`.
- Crowd variety (`ApplyVariety`) only touches `MHC_Crowd*` / `MHC_HoweSoldier` looks.
- Dialogue: `BP_PlotManager.ConversationStarted/Ended` → `BP_DlgNPC.DialogueLOD` (strands, dialogue lights).
- Hair under shadowless lights reads white: fill lights have specular 0 (`docs/ART.md`).

## Pictures

- Portrait booth: `tools/unreal/booth_shot.py <Name> <tag>` in `/Game/Cousland/Dev/L_PortraitBooth`. A camera
  on the sitter's +X side sees nothing, so the side shot is taken from -X and mirrored. The editor reopens
  the last level: load the castle again before Play.
- `CaptureViewport` renders any camera in Simulate; in Play use `CaptureEditorImage`. Capture twice after a
  camera jump (motion blur).
