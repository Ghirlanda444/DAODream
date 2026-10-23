# Godot great hall (ink and cel)

PROTOTYPE - NOT FOR PRODUCTION. Throwaway code: if Godot is chosen, the real
project is written fresh, not grown from this folder.

## Hypothesis

Godot 4.7 can draw DAODream in the Ink & Cel style (flat light bands plus ink
contours) at a quality we like, light enough to keep running while the same PC
does other work, using only free tools. A second question rides along: can
Claude build Godot scenes as text, without the editor open?

## How to run (Windows)

1. Download Godot 4.7 (standard build, not .NET) from https://godotengine.org/download.
   It is a zip of about 80 MB holding one exe, with no installer.
2. Open it, choose **Import**, and pick `prototypes/godot-hall/project.godot` in your clone.
3. Press **F5** (Run Project). The first start imports the project for a few seconds.

To try the lightweight renderer meant for weaker PCs, run `run-lowspec.bat`
(set `GODOT` to the path of the Godot exe first, or put the exe in this folder).
It starts the same scene on the Compatibility renderer (OpenGL 3.3).

### Controls

| Key | Action |
|---|---|
| Drag / wheel | Look around / zoom (the camera sways on its own after 3 s idle) |
| 1 / 2 / 3 | Plain lighting / Ink & cel / Cel without ink |
| B | 2, 3 or 4 light bands |
| L | Low-spec: 60% render scale, no shadows, no MSAA |
| V | Toggle vsync (turn it off to see uncapped fps) |
| H | Hide the on-screen text, for clean video capture |
| F12 | Save a screenshot to Godot's user folder (path printed in the output) |

The top-left shows fps, draw calls, triangles, the renderer, RAM and video memory.

## What is in it

- `hall.gd` builds everything at runtime: the hall (walls with window openings,
  pillars, dais, throne, banners, table, braziers), Bryce, Howe, two guards and
  the mabari from primitives, the lights, the camera and the stats display.
  Textures (ashlar, flagstones, planks, banners, rug) are generated in code.
- `spatial_cel_toon.gdshader`: banded lighting, world-projected textures (no
  UVs needed), contact darkening near the floor.
- `post_ink_outline.gdshader`: full-screen ink contours from the depth buffer.

Nothing comes from the original game.

## Status

In progress: waiting for a run on the real PC.

## Findings so far

Rendered in a cloud container with software rendering only (no GPU), on Godot
4.7.2, so the fps there (3 to 7) says nothing about real performance:

- Both renderers work unchanged: Forward+ (Vulkan) and Compatibility (OpenGL).
  Script and shaders loaded with no errors on either.
- The engine's own memory use was about 38 MB (Compatibility) and 52 MB
  (Forward+), with about 90 to 210 MB of video memory, for this scene.
- The whole prototype is text: scenes, scripts and shaders were written and
  tested without opening the editor.

To fill in after the run on the PC: fps with vsync off in each mode, fps with
the usual programs open, how the look compares with the web style test and the
Unreal build.
