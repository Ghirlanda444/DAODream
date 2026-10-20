# Art: materials

Everything you see is new: no texture, model or material comes from the game.
The game's data decides where things are and what they are (a wall, a prop,
a door); how they look is made here.

## Castle surfaces (procedural)

`/Game/Cousland/Materials/M_CastleSurface` draws its surface from the world
position alone, in an HLSL Custom node (source:
`Unreal/Cousland/MaterialSource/M_CastleSurface.hlsl`), so it needs no texture
files and no UVs: the castle is made of scaled cubes whose UVs would stretch.
It projects a pattern on the three world planes and blends them by the
surface normal, so walls, floors and box tops each get the right one. Three
patterns:

- `Mode` 0, ashlar: blocks in a running bond (every other row offset by half
  a block).
- `Mode` 1, flagstones: rows of slabs, each row shifted by a random amount.
- `Mode` 2, planks: long boards with a grain from stretched noise and faint
  rings.

Each block, slab or plank gets its own tint from a hash of its cell, broken
up by value noise; joints wander a little so the edges look chipped, and a
few stones are darker. Parameters: `Size` (block width and height, cm),
`Mortar` (joint width, cm), `ColorA` and `ColorB` (the range of tints),
`MortarColor`. The joint also darkens ambient occlusion and is rougher.

The greybox instances now derive from it:

| Instance | Used on | Look |
| --- | --- | --- |
| `MI_Greybox_Wall` | kit walls and pillars (`BP_AreaLoader` Walls) | sandstone ashlar, 52 x 28 cm |
| `MI_Greybox_Floor` | the floor plan (Floors) | dark flagstones, 70 x 55 cm |
| `MI_Greybox_Prop` | furniture and other props (Props) | oak planks, 16 cm |
| `MI_Greybox_Door` | `BP_Door` | dark planked doors |
| `MI_Greybox_Ceiling` | ceilings and lids (Ceilings) | pale lime plaster: ashlar mode, 110 x 70 cm panels, faint 0.8 cm joints |

The material is flagged for instanced static meshes (the castle is drawn
with them); without that flag Unreal silently falls back to its default grid
material.

## Castle surfaces (Megascans, optional)

When the free Megascans surfaces are in the project, they replace the
procedural ones at load time; a clone without them keeps the procedural look.
They come from Fab (Quixel Megascans, Fab Standard License, free) and, like the
MetaHumans, stay out of git: 2K texture sets unpacked in `extracted/fab/`,
imported to `Content/ThirdParty/Megascans/Castle/<Kind>/T_<Kind>_<Map>`
(BaseColor, Normal, Roughness, AO).

| Kind | Fab listing | Used on |
| --- | --- | --- |
| Wall | Stone Wall (tinifauaw) | Walls, Blockers |
| Floor | Stone Floor (xbmgeba) | Floors |
| Ceiling | Wooden Planks (wckqdbvs) | Ceilings |
| Door | Wooden Planks (vjisagn) | `BP_Door` Panel |
| Prop | Wooden Planks (vlzhdbwdy) | Props |
| Plaster | Damaged Wall Plaster (uc2lddzcw) | not used yet |

`/Game/Cousland/Materials/M_CastleScan` (committed, engine functions only)
projects a texture set on the three world planes (`WorldAlignedTexture`,
`WorldAlignedNormal`), so the scaled-cube castle needs no UVs; parameters
`TexBaseColor/Normal/Roughness/AO`, `TileSize` (cm per repeat), `Tint`,
`RoughnessScale`. The instances `MI_Castle_<Kind>` live with the textures.
`BP_AreaLoader.BuildSolids` ends with `ApplyScanArt`, which calls
`SetScan(component, path)` per component: it loads the instance by its path
and sets it only if it exists. `BP_Door.Setup` calls `ScanArt` the same way.
No committed asset references the Megascans directly.

## Ceilings

The rooms have roofs now (`docs/GAME_DATA.md`, "Walls from the level kit"):
the kit's ceiling pieces (solid kind 3, their bounding boxes) and, where those
are missing or sit above the walls, lids at the top of the surrounding walls.
`BP_AreaLoader` draws both with its `Ceilings` instanced mesh component and
`MI_Greybox_Ceiling`; `BuildSolids` sets that component's mesh and material
itself, so a level whose loader was placed before the component existed still
gets them. Ceilings block like walls (`BlockAllDynamic`), so the third-person
camera's spring arm, which probes the camera channel, pulls in under them
instead of rising through them: from the start in the Main Hall, a boom
pitched 75 degrees down meets the lid at 3.9 of its 4 m.

## Lights

Interiors are lit by the game's own lights: each room's light model lists its
lamps, fireplaces and fill lights, and `BP_AreaLoader.SpawnLights` adds a
movable point light per light (`PlaceLight`) at its position, with its radius
as attenuation radius. The game's colour carries the brightness too: the light
gets that colour divided by its largest channel and an intensity of that
channel times the loader's `LightScale` (candelas), and lights at least 0.8
bright (lamps and fireplaces rather than fills) cast shadows. `LightScale` is
12 in `L_CastleCousland`, where auto exposure adapts to the dark rooms, and 20
in `L_CastleNight`, whose exposure is fixed at -1.5 EV. Lamps that the flat
greybox ceilings would hide are moved just under them (`area.tuck_lights`).

The day castle keeps its sun and sky; with roofs on, they light only what is
still open (the outer rims and a few uncovered patches).

## Next

Normal detail (bevelled joints), vaulted rather than flat ceilings,
separate looks for the kitchen, chapel and cellars, banners and rugs, and
flame effects at the lamps.
