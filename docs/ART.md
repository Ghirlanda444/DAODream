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
channel times a scale (candelas). Lights at least 0.8 bright (lamps and
fireplaces) use the loader's `LightScale` and cast shadows; dimmer ones (fills)
use `FillScale`. Lamps that the flat greybox ceilings would hide are moved just
under them (`area.tuck_lights`).

The game lights each lit candle at night like a torch (1.62, 3 m, 27 cm above
the flame), and candles stand by walls, so the wall beside one burned white at
the night's fixed exposure. The export scales those 17 lights to a quarter
(`area.dim_candle_lights`), which also stops them casting shadows.

The game also lit its rooms with baked ambient light, which a movable-light
remake lacks, so the area export can add its own fills where no game light
reaches the floor (`--fill-lights`, `area.fill_lights`): cool ones at night,
warm ones by day (`--warm-fills`).

| Level | `LightScale` | `FillScale` | Export fills | Exposure |
| --- | --- | --- | --- | --- |
| `L_CastleCousland` | 72 | 144 | 0.3, warm (162 lights) | auto, -3 to 6 EV100 |
| `L_CastleNight` | 20 | 20 | 0.25, cool | fixed, -1.5 EV |

The day castle's lighting pass (2026-10-20) fixed three things:

- Blue fog: the template's height fog (density 0.044 from 0 m) filled every room,
  and the sky light (intensity 1, lit from below too) tinted it blue. The fog is
  now 0.003 from 25 m, so only distant views get haze, and the sky light 0.3 with
  a black lower hemisphere.
- Orange glare: with no post-process volume, auto exposure ran unclamped and
  blew the saturated game lamps (about 2300 K) up to orange walls. The unbound
  `CastleExposure` volume clamps exposure to -3..6 EV100 and sets white balance
  to 4200 K, so firelight reads warm rather than orange.
- Dark rooms: lamps are 6 times and fills 12 times brighter than before, and the
  export's warm fills light the upper floor (the family's rooms), which has no
  game light within 14 m.

The day castle keeps its sun and sky; with roofs on, they light only what is
still open (the outer rims and a few uncovered patches).

## Lamps and fires

Where the game hangs a lamp or lights a fire, the loader puts one of ours
(`BP_AreaLoader.BuildFixtures`, after the solids: `PlaceFixture` per
`Fixtures` entry, `PlaceFire` per `Fires` entry). Everything in
`/Game/Cousland/Fixtures` is built by script from engine primitives and
procedural materials, no textures (`tools/unreal/fixtures_build.body.py`, run
in the editor with `pyrun`, then `tools/unreal/flame_build.py`):

| Asset | What |
| --- | --- |
| `SM_FireBowl` | hanging lamp: an iron bowl of coals on three rods meeting at a ring, its fire at the origin |
| `SM_Chain` | 1 m of chain, scaled to reach from the ring to the ceiling |
| `SM_WallLamp` | the same bowl on a bracket; the wall is at +X, which the export's yaw turns to the model's back |
| `SM_Torch` | wall plate, arm and ring holding a wooden torch that leans out to where the game burns it (lit only at night) |
| `SM_CandleHolder` | small iron holder with a candle |
| `SM_Candle` | a 37 cm church candle on a dish |
| `SM_CandleStand` | a 48 cm iron candle stand |
| `SM_HearthLogs` | a bed of coals and five logs, under medium (0.9x) and large (1.4x) fires |
| `M_FixtureIron`, `M_FixtureWood`, `M_FixtureWax` | two tints mottled by world-space noise |
| `M_FixtureEmbers` | charred wood and coals whose cracks glow and flicker (`Glow`) |
| `M_Flame` | a flame tongue for Niagara sprites: a teardrop that licks over time, orange-red edges, yellow core |
| `M_Spark` | a soft ember speck |
| `NS_FireSmall`, `NS_FireMedium`, `NS_FireLarge` | flame tongues rising on buoyancy and fading, plus embers on curl noise (from Epic's Fountain template): lamp bowls and torches, medium and large hearths or burning rubble |
| `NS_FireCandle`, `NS_FireWall` | a tiny, brighter candle flame; a wide, low spread of flames for the night's burning walls (no logs) |

The fixtures cast no shadows (the game's lamp lights sit in their bowls). The
light still comes from the game's point lights (`PlaceLight`); the flames are
only seen, they do not light.

## Next

Normal detail (bevelled joints), vaulted rather than flat ceilings,
separate looks for the kitchen, chapel and cellars, banners and rugs,
flickering lamp light and smoke.
