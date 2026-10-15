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

The material is flagged for instanced static meshes (the castle is drawn
with them); without that flag Unreal silently falls back to its default grid
material.

## Next

Normal detail (bevelled joints), ceilings (the rooms are open to the sky, so
interiors are lit like a courtyard), separate looks for the kitchen, chapel and
cellars, and banners, rugs and lighting for the rooms.
