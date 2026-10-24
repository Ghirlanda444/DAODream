"""Held poses for the UE5 mannequin skeleton (Blender 5.2, headless).
blender -b --factory-startup -P poses.py -- <SKM_Manny_Simple.fbx> <out.fbx> <pose> [preview_prefix]

  A_WoundedSlump  a wounded man slumped against a wall, for Teyrn Bryce in the night castle (the game shows him
                  so through its cutscenes' body animations, which we cannot play): the pelvis drops to the floor
                  and tips back against the wall, the right leg lies out along the floor, the left knee is drawn
                  up, the back slumps, the head hangs forward and to the side, the right hand is pressed to the
                  belly (the wound) and the left arm lies limp on the floor.
  A_Fallen        knocked out in a fight, on the back: legs a little apart, one knee bent, the head turned to
                  the side, the arms flung out on the floor. A fallen player or party member lies so until the
                  fight is won (docs/COMBAT.md).

<SKM_Manny_Simple.fbx> is /Game/Characters/Mannequins/Meshes/SKM_Manny_Simple exported from Unreal. Bones are
aimed in world space (each bone's head toward its child's head, along a target direction), parents first, so
children follow. Exported as a two-frame animation for Unreal's SK_Mannequin (tools/unreal/pose_make.py imports
each as /Game/Cousland/Anims/<pose>)."""
import math
import sys

import bpy
from mathutils import Matrix, Vector

ARGS = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT, POSE = ARGS[:3]
PREVIEW = ARGS[3] if len(ARGS) > 3 else ""

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=SRC)
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
mesh = next(o for o in bpy.data.objects if o.type == "MESH")
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="POSE")
mw = arm.matrix_world
mwi = mw.inverted()
pb = arm.pose.bones


def head(name):
    bpy.context.view_layer.update()
    return mw @ pb[name].head


def rotate(name, rot: Matrix, pivot: Vector):
    """Turn a bone (and so its children) by a world rotation about a world point."""
    m = mwi @ Matrix.Translation(pivot) @ rot.to_4x4() @ Matrix.Translation(-pivot) @ mw
    pb[name].matrix = m @ pb[name].matrix
    bpy.context.view_layer.update()


def aim(name, child, direction):
    """Turn a bone about its head so that its child's head lies along `direction` (world)."""
    h, c = head(name), head(child)
    rot = (c - h).normalized().rotation_difference(Vector(direction).normalized()).to_matrix()
    rotate(name, rot, h)


FWD = Vector((0.0, -1.0, 0.0))  # the mannequin faces -y in Blender (Unreal +y, mirrored)
UP = Vector((0.0, 0.0, 1.0))

def wounded():
    # the whole body: down onto the floor and tipped back 22 degrees against the wall behind it
    pelvis0 = head("pelvis")
    pb["pelvis"].matrix = Matrix.Translation(mwi.to_3x3() @ Vector((0.0, 0.10, -0.80))) @ pb["pelvis"].matrix
    bpy.context.view_layer.update()
    rotate("pelvis", Matrix.Rotation(math.radians(-22), 3, "X"), head("pelvis"))
    # legs: the right one out along the floor, the left knee drawn up
    aim("thigh_r", "calf_r", (-0.10, -1.0, -0.12))
    aim("calf_r", "foot_r", (-0.05, -1.0, -0.08))
    aim("thigh_l", "calf_l", (0.15, -0.75, 0.62))
    aim("calf_l", "foot_l", (0.05, -0.45, -0.90))
    aim("foot_l", "ball_l", (0.05, -1.0, -0.15))
    aim("foot_r", "ball_r", (-0.05, -0.35, 0.95))
    # the back slumps forward from the wall a little, the head hangs down and to its right
    rotate("spine_03", Matrix.Rotation(math.radians(12), 3, "X"), head("spine_03"))
    rotate("neck_01", Matrix.Rotation(math.radians(18), 3, "X"), head("neck_01"))
    rotate("head", Matrix.Rotation(math.radians(14), 3, "X") @ Matrix.Rotation(math.radians(-16), 3, "Y"), head("head"))
    # right hand pressed to the belly; left arm limp on the floor
    aim("upperarm_r", "lowerarm_r", (-0.25, -0.35, -0.90))
    belly = head("spine_01") + FWD * 0.14 + UP * 0.05
    aim("lowerarm_r", "hand_r", belly - head("lowerarm_r"))
    aim("upperarm_l", "lowerarm_l", (0.45, 0.05, -0.89))
    aim("lowerarm_l", "hand_l", (0.30, -0.65, -0.70))



def fallen():
    # the whole body tipped onto its back and laid on the floor, the pelvis 12 cm up
    rotate("pelvis", Matrix.Rotation(math.radians(-90), 3, "X"), head("pelvis"))
    p = head("pelvis")
    pb["pelvis"].matrix = Matrix.Translation(mwi.to_3x3() @ Vector((0.0, 0.0, 0.12 - p.z))) @ pb["pelvis"].matrix
    bpy.context.view_layer.update()
    # legs along the floor a little apart, the left knee bent up; feet fall outward
    aim("thigh_r", "calf_r", (-0.16, -1.0, 0.0))
    aim("calf_r", "foot_r", (-0.10, -1.0, -0.02))
    aim("thigh_l", "calf_l", (0.22, -0.80, 0.40))
    aim("calf_l", "foot_l", (0.10, -0.60, -0.75))
    aim("foot_r", "ball_r", (-0.55, -0.25, 0.80))
    aim("foot_l", "ball_l", (0.20, -0.85, 0.10))
    # the head rolls to its left; the arms flung out on the floor, the right one bent back toward the hip
    rotate("head", Matrix.Rotation(math.radians(35), 3, "Y"), head("head"))
    aim("upperarm_l", "lowerarm_l", (0.85, 0.45, -0.06))
    aim("lowerarm_l", "hand_l", (0.55, 0.80, -0.04))
    aim("upperarm_r", "lowerarm_r", (-0.90, 0.25, -0.06))
    aim("lowerarm_r", "hand_r", (-0.45, -0.85, -0.04))


POSES = {"A_WoundedSlump": wounded, "A_Fallen": fallen}
POSES[POSE]()

bpy.ops.object.mode_set(mode="OBJECT")
lowest = min((mw @ b.head).z for b in pb)
print("POSE lowest bone head z", round(lowest, 3), "pelvis", [round(v, 3) for v in head("pelvis")])

if PREVIEW:
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.render.resolution_x, sc.render.resolution_y = 600, 600
    sc.render.film_transparent = False
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 2.0
    for name, yaw in (("front", 0), ("side", 90), ("q", 35)):
        a = math.radians(yaw)
        cam.location = Vector((4 * math.sin(a), -4 * math.cos(a), 0.6))
        cam.rotation_euler = (math.radians(90), 0, a)
        sc.render.filepath = "%s_%s.png" % (PREVIEW, name)
        bpy.ops.render.render(write_still=True)

# a two-frame action of the pose, every bone keyed, exported for Unreal's SK_Mannequin
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="POSE")
for frame in (0, 1):
    for b in pb:
        b.keyframe_insert("location", frame=frame)
        b.keyframe_insert("rotation_quaternion", frame=frame)
        b.keyframe_insert("scale", frame=frame)
bpy.ops.object.mode_set(mode="OBJECT")
sc = bpy.context.scene
sc.frame_start, sc.frame_end = 0, 1
bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True)
bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, object_types={"ARMATURE"}, add_leaf_bones=False,
                         bake_anim=True, bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False,
                         bake_anim_force_startend_keying=True)
print("POSE ->", OUT, "armature", arm.name)
