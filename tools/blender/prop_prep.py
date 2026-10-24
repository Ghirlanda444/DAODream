"""A prop that comes as a .blend, exported as an FBX for tools/unreal/kit_props.py (Blender 5.2, headless):
blender -b --factory-startup -P prop_prep.py -- <in.blend> <object> <out.fbx>

Keeps one object (a file may hold variants, e.g. the hanging banner's emblazoned and blank ones), with its
modifiers applied and its transform baked in, and exports it alone."""
import sys

import bpy

SRC, KEEP, OUT = sys.argv[sys.argv.index("--") + 1:][:3]
bpy.ops.wm.open_mainfile(filepath=SRC)
ob = bpy.data.objects[KEEP]
bpy.ops.object.select_all(action="DESELECT")
bpy.context.view_layer.objects.active = ob
ob.select_set(True)
for m in list(ob.modifiers):
    bpy.ops.object.modifier_apply(modifier=m.name)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, object_types={"MESH"}, mesh_smooth_type="FACE")
print("PREP", KEEP, len(ob.data.vertices), "verts ->", OUT)
