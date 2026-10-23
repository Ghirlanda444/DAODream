---
name: unreal-editor
description: How to drive DAODream's Unreal editor (UE 5.8, Italian UI) from scripts - starting and calling its MCP server, writing Blueprint graphs with the DSL and node surgery, materials, Animation Blueprints, saving. Use before any change to Blueprints, materials, levels or assets in Unreal/Cousland, and when an editor call fails in a way the generic unreal-mcp skill does not explain.
---

# Driving the DAODream editor

Project: `Unreal/Cousland` (UE 5.8). Setup and session rules: `docs/UNREAL_SETUP.md`. Work one system
per prompt, report every actor and asset created, and stop rather than silently work around a missing
tool. MetaHuman specifics: [metahuman.md](metahuman.md). Checking a change in the running game: the
playtest skill.

## Connecting

- The editor's MCP server is `http://localhost:8000/mcp`. From a session started in the repo the unreal-mcp
  tools are not loaded; use `tools/unreal/ue.py` (JSON-RPC: `ue.init()`, then
  `ue.call(toolset, tool, args)`; `py ue.py list`, `py ue.py describe <Toolset>`).
- `tools/unreal/pyrun.py` runs Python inside the editor (`pyrun.run(code, timeout)`, results in `OUT`).
  Scripts named `*.body.py` are run this way; they refuse to run during Play/Simulate.
- In Git Bash set `MSYS_NO_PATHCONV=1`, or `/Game/...` arguments become `C:/Program Files/Git/Game/...`.
- The server often does not start by itself: with the editor window maximised and in front, type
  `ModelContextProtocol.StartServer` in the Cmd box (bottom bar). Ask the user before bringing the editor
  to the front. A "Ripristina pacchetti" (restore packages) dialog can block startup: "Salta ripristino".
- A background editor runs at ~3 fps: set `Default__EditorPerformanceSettings`
  `bThrottleCPUWhenNotForeground` to false (ObjectTools.set_properties, `values` as a JSON string) and
  back to true when done.
- Other sessions may share the editor: check before starting or stopping Play.

## Blueprint graphs: the DSL

`BlueprintTools.write_graph_dsl` / `read_graph_dsl` (`tools/unreal/dsl_write.py <BP> <graph> <file>`).
Keep graph sources in `tools/unreal/dsl/*.dsl` (UTF-8). The editor is Italian, so node ids are too, and
read-back ids are often not creatable:

- Flow: `Utilità|ControlloDiFlusso|Ramo` with `(:then ...)(:else ...)`; loops
  `Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex n (:LoopBody ...)(:Completed ...)` (index
  `_index`, one loop per function). Nothing may follow a branch (`Unreachable code after branch`): split
  the work into small functions called in turn.
- Operators: `Utility|Operatori|Aggiungi/Sottrai/Moltiplica/Dividi/Uguale(==)/Maggiore(>)/Minore(<)/Maggioreuguale(>=)`
  (the English `+ - * /` and `(for ...)` expand to ids that do not exist). A wildcard operator cannot take a
  literal first: `Aggiungi x 2.0`, not `Aggiungi 2.0 x`. Booleans `Matematica|Booleano|AND/OR/NOTBoolean`;
  strings `Utilità|Stringa|EqualExactly(String)`, `Contains`; arrays `Utilità|Array|Ottieni(unacopia)`,
  `Length`, `ContainsItem`.
- Variables `Variabili|Predefinito|OttieniX` / `ImpostaX` (bools drop the `b`: `OttieniActive` for
  `bActive`); self `Variabili|Ottieniunriferimentoasestesso`; own functions `Funzionedichiamata|F` with
  keyword pins (`:A x`), or the value goes to `self`; another class's `Classe|BPDlgNPC|F`.
- Several outputs: `(bind (_a _b _c) (Node ...))`. `.yaw` and friends expand to English ids: use
  `Matematica|Rotatore|BreakRotator` with a multi bind. `MakeRotator` takes roll, pitch, yaw.
- Pure nodes re-evaluate on every use, so do a setter last. New functions and params must be compiled
  before another graph calls them with keyword pins.
- Events cannot be written: start a looping `SetTimerbyFunctionName` from a setup function, or hook a
  function call onto an existing event by node surgery. The construction script is
  `(fn ConstructionScript ...)` on graph `UserConstructionScript`.
- Spawning a Blueprint class: `Gioco|Generaattoredallaclasse :Class "/Game/...X.X_C" :SpawnTransform ...`.
- `find_node_types` (with `type_id_filter` and `context_pins: []`) lists creatable ids; it searches the
  palette text, so try Italian and English words. `get_node_type_pins` leaves stray nodes in the graph.

## Node surgery

For big or read-back graphs (BP_PlotManager.DoActionNow, BP_DlgNPC's event graph), splice instead of
rewriting: `find_nodes` + `get_node_infos` (pins by index, connections), `create_node` (pass
`declaring_class` when one id exists on two classes, e.g. the MID's `SetVectorParameterValue`),
`break_pins`, `connect_pins`, `set_pin_value`, `delete_node`, then `compile_blueprint`. Graphs can hold
orphaned duplicate chains: the live one starts at the entry's `then`. A node the DSL cannot pick can live
in a tiny helper function built this way and called from DSL.

## Blueprints and components

- `BP_DlgNPC` is a plain Actor (its own `Mesh`, `Look` the spawned MetaHuman or mabari), not a Character;
  the player is `BP_ThirdPersonCharacter`.
- Components added with SubobjectDataSubsystem do not become graph variables: find them at runtime by
  class and `GetObjectName`. Component templates are `SubobjectDataBlueprintFunctionLibrary.get_object`.
- Components added to a placed Blueprint reach existing instances empty; set mesh and material at runtime.
- Arrays on a CDO: clear to `[]` first, then fill (shrinking and changing in one set is refused).
- Save with `EditorAssetLibrary.save_asset(path, only_if_is_dirty=False)`. Read-only asset tools say
  "Asset does not exist" during Play. Never `save_current_level()` blindly; switching maps with
  OpenEditorForAsset drops unsaved level edits.

## Materials

- `MaterialEditingLibrary` from Python. Custom HLSL nodes need `(expr, "RGB")` pins for float3 inputs from
  textures and vector parameters; `PreSkinnedPosition` needs a `VertexInterpolator`.
- Per-instance values without new instances: Scalar/VectorParameter with `use_custom_primitive_data` and
  `primitive_data_index` (defaults apply when unset); set with `SetCustomPrimitiveDataFloat`.
- Materials on instanced static meshes need `bUsedWithInstancedStaticMeshes`, or the grid shows instead.
- MetaHuman skin: `Basecolor Global Multiply Post-Bake` on Face and Body; hair: `hairMelanin`,
  `hairRedness`, `WhiteAmount` on grooms (`SetScalarParameterValueOnMaterials` makes the MIDs).

## Animation Blueprints

- Create with `AnimBlueprintFactory` (target skeleton); blend spaces with `BlendSpaceFactory1D`, samples
  and axis via `sample_data` / `blend_parameters`.
- AnimGraph nodes by `create_node`: `Animazione|Spazidifusione|GiocatoreBlendspace'<BS>'`,
  `Animation|Montage|Slot'DefaultSlot'`, `Animation|Blends|Fusioneposeperbool`,
  `Animazione|Sequenze|Valuta'<anim>'` (evaluator at an explicit time); output node
  `AnimGraphNode_Root_0`. Ids go by asset name, so never keep two assets of the same name.
- Read an anim instance's variables at runtime with `get_anim_instance().get_editor_property(...)`.
- Example of all of this: `tools/unreal/beast_anim.py`.

## Imports

- FBX from Blender: export in centimetres (armature scaled 100 and applied, unit scale 0.01), one colour
  attribute, active. Legacy FBX import: `Interchange.FeatureFlags.Import.FBX False`.
- Grooms: Alembic through `HairStrandsFactory`, conversion rotation (90,0,0), scale (100,-100,100);
  set `hair_width_override` (~0.011 cm) or curves render as 1 cm ribbons.
- Fab content comes in through the editor's Fab panel (Finestra → Fab) or the Launcher, into git-ignored
  Content folders (CLAUDE.md); free assets only, and the user accepts licences.
