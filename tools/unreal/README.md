# Unreal editor scripts

Python that drives the running Unreal editor (`Unreal/Cousland`) from outside, over the
editor's MCP server (`localhost:8000/mcp`, the ModelContextProtocol plugin):

- `ue.py`: tiny JSON-RPC client (`python ue.py call <Toolset> <tool> '<json>'`).
- `pie.py`: Play/Simulate, console commands, properties, editor screenshots.
- `pyrun.py`: runs a Python body inside the editor (typed into the console as `py "<file>"`,
  staged in `Saved/claude/`) and returns what it puts in `OUT`.
- `wshot.py`: full-resolution screenshot of one editor window (e.g. a MetaHuman Creator).
- `metahuman_make.py` + `metahuman_recipes.json`: makes MetaHumans in batches, one fresh editor
  each (`python metahuman_make.py metahuman_recipes.json Fergus Eleanor ...`); see
  `docs/CHARACTERS.md`. `mh_look.body.py` is its colours-and-body step;
  `metahuman_strands.body.py` its last step (real hair strands instead of the build's
  cards-only grooms; also runs alone with `NAMES = [...]` and optional `THICKEN`).
  `elf_ears.body.py` points the ears of a built face mesh (recipes with `"elf_ears"`).
  `custom_groom.body.py` puts a Blender-made groom (`tools/blender/*_hair.py`) on the Hair slot
  (recipes with `"custom_hair"`).
- `booth_shot.py`: front, three-quarter and side pictures of a built MetaHuman in the portrait booth
  level (`Content/Cousland/Dev/L_PortraitBooth`: grey backdrop, key/fill/rim lights, fixed exposure),
  to compare faces with reference pictures under the same light.
- `fixtures_build.body.py` (run with `pyrun`, Play/Simulate stopped) and then `flame_build.py`: the
  castle's lamp meshes, materials and fire effects in `Content/Cousland/Fixtures` (`docs/ART.md`).
- `dsl_write.py <Blueprint> <graph> <file>`: writes a Blueprint graph from a staged DSL file; `dsl/` holds
  the loader's fixture graphs (`BP_AreaLoader.BuildFixtures` and the functions it calls, the lamp flicker
  `StartFlicker`/`Flicker` among them).
- `duncan_groom_apply.py`: run inside the editor after building Duncan, puts his custom groom back.

The MetaHumans they make stay out of git (`Content/MetaHumans/`).
