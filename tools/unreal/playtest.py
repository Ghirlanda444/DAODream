"""Look at the game running, with pictures, from Simulate or Play in a castle level.

For checking a change in the game itself rather than in the editor. Pictures and a contact sheet (sheet.png, needs Pillow) go to
Unreal/Cousland/Saved/claude/playtest/<command>-<time>/ (git-ignored); script errors logged during the
run are printed at the end.

    python playtest.py look night bhn200cr_warning_servant gen00fl_dog     face and full length, Simulate
    python playtest.py look night bhn200cr_howe_east_hall1 --dog           side and front of a dog
    python playtest.py dialogue night --lines 6                            Play: each line, option 1
    python playtest.py kill night bhn200cr_howe_east_hall1                 Simulate: wake, kill, watch it fall

Characters are named by their tag (NpcTags in extracted/ue/areas/<area>.json). Hidden ones (waiting for a
plot) are shown for the pictures. The editor must be open with its MCP server running (docs/UNREAL_SETUP.md);
the level is loaded if another one is open. While the run lasts the editor is not throttled in the
background, so it keeps a usable frame rate.
"""
import argparse
import json
import math
import os
import time

import game
import pie
import pyrun
import ue

OT = "editor_toolset.toolsets.object.ObjectTools"
PERF = "/Script/UnrealEd.Default__EditorPerformanceSettings"
# Blueprint runtime errors as the editor logs them (Italian and English), not map checks ("0 Errori").
RUNTIME_ERRORS = "Errore di runtime Blueprint|Blueprint Runtime Error|Accesso nullo|Accessed None|LogScript: Error"
OUT_ROOT = os.path.join(game.ROOT, "Unreal", "Cousland", "Saved", "claude", "playtest")

# Python run inside the game world: the NPC actor for an index, and its look.
NPC = '''
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
a = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if a.get_name() == %r][0]
look = a.get_editor_property("Look")
'''


class Run:
    def __init__(self, command, area):
        self.dir = os.path.join(OUT_ROOT, "%s-%s" % (command, time.strftime("%Y%m%d-%H%M%S")))
        os.makedirs(self.dir)
        self.area, self.shots, self.t0 = area, [], time.strftime("%Y.%m.%d-%H.%M.%S", time.gmtime())  # the log is in UTC
        ue.init()
        level = game.AREAS[area][0]
        r = pyrun.run('''
w = unreal.EditorLevelLibrary.get_editor_world()
if %r not in w.get_path_name():
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level("/Game/Cousland/Maps/" + %r)
OUT["level"] = unreal.EditorLevelLibrary.get_editor_world().get_path_name()
''' % (level, level), 600)
        print("level", r.get("level"), "->", self.dir)
        ue.call(OT, "set_properties", {"instance": {"refPath": PERF}, "values": json.dumps({"bThrottleCPUWhenNotForeground": False})})

    def start(self, simulate):
        pie.close_popups()
        pie.start(simulate=simulate)
        time.sleep(100)  # the loader builds the castle and spawns everyone
        pie.close_popups()
        self.g = game.Game(self.area)

    def shot(self, name, transform=None):
        if transform:
            ue.call(pie.EA, "SetCameraTransform", {"transform": transform})
            time.sleep(3)
        path = os.path.join(self.dir, name + ".png")
        pie.shot(path)
        self.shots.append(path)
        return path

    def npc(self, tag):
        return "BP_DlgNPC_C_%d" % self.g.npc(tag)

    def show(self, act):
        """Unhide an NPC and its look; report what it wears."""
        return pyrun.run(NPC % act + '''
a.set_actor_hidden_in_game(False)
if look:
    look.set_actor_hidden_in_game(False)
    OUT["look"] = look.get_class().get_name()
''', 60)

    def around(self, act, dist, height, pitch, turn):
        """A camera dist cm from the NPC, height cm above its origin (the feet), turn degrees round from its
        facing (0 in front), looking back at it."""
        r = json.loads(ue.call(game.AT, "get_actor_transform", {"actor": {"refPath": self.g.W + act}}))["returnValue"]
        x, y, z, yaw = r["location"]["x"], r["location"]["y"], r["location"]["z"], r["rotation"]["yaw"]
        a = math.radians(yaw + turn)
        return {"location": {"x": x + dist * math.cos(a), "y": y + dist * math.sin(a), "z": z + height},
                "rotation": {"pitch": pitch, "yaw": yaw + turn + 180, "roll": 0}, "scale": {"x": 1, "y": 1, "z": 1}}

    def finish(self):
        try:
            pie.stop()
        finally:
            ue.call(OT, "set_properties", {"instance": {"refPath": PERF}, "values": json.dumps({"bThrottleCPUWhenNotForeground": True})})
        found = json.loads(pie.log(RUNTIME_ERRORS, 60))["returnValue"]
        errors = [l for l in found if l.startswith("[") and l[1:20] >= self.t0]
        print("script errors during the run:", len(errors))
        for l in errors[-10:]:
            print("  ", l[:220])
        self.sheet()

    def sheet(self, cols=3):
        try:
            from PIL import Image
        except ImportError:
            return
        if not self.shots:
            return
        ims = [Image.open(p).convert("RGB") for p in self.shots]
        w, h = ims[0].size
        rows = (len(ims) + cols - 1) // cols
        s = Image.new("RGB", (w * min(cols, len(ims)), h * rows))
        for i, im in enumerate(ims):
            s.paste(im.resize((w, h)), ((i % cols) * w, (i // cols) * h))
        s.thumbnail((2400, 2400))
        s.save(os.path.join(self.dir, "sheet.png"))
        print("sheet", os.path.join(self.dir, "sheet.png"))


def look(args):
    """Simulate: each NPC's face and full length (a dog: side and front)."""
    run = Run("look", args.area)
    run.start(simulate=True)
    try:
        for tag in args.tags:
            act = run.npc(tag)
            print(tag, act, run.show(act))
            views = ((("side", 260, 40, -8, 90), ("front", 260, 40, -8, 0)) if args.dog else
                     (("face", 95, 158, -6, 0), ("body", 330, 110, -4, 0)))
            for name, dist, height, pitch, turn in views:
                run.shot("%s_%s" % (tag, name), run.around(act, dist, height, pitch, turn))
    finally:
        run.finish()


def dialogue(args):
    """Play: a picture of every line of the conversation that opens the level (or that is running), always
    choosing option 1, until it ends or --lines pictures are taken."""
    run = Run("dialogue", args.area)
    run.start(simulate=False)
    def wait_for_line(seconds):
        t = time.time()
        while time.time() - t < seconds:
            lines, opts = pie.dlg()
            if lines or opts:
                return lines, opts
            time.sleep(2)
        return [], []

    try:
        # the first conversation can start well after the level (a caption runs ~25 s at night)
        lines, opts = wait_for_line(60)
        for k in range(args.lines):
            print(k, lines[:2], [o[0] for o in opts][:3])
            time.sleep(1.5)
            run.shot("line_%02d" % k)
            if not lines and not opts:
                break
            pie.cmd("ke * Choose 0")
            time.sleep(2.5)
            lines, opts = wait_for_line(8)  # the next line, or the next conversation the plot starts
    finally:
        run.finish()


def kill(args):
    """Simulate: wake a creature, hit it hard, and picture it as it dies and a few seconds later."""
    run = Run("kill", args.area)
    run.start(simulate=True)
    try:
        act = run.npc(args.tag)
        run.show(act)
        pyrun.run(NPC % act + 'a.call_method("SetPlotActive", (True,))\n', 60)
        run.shot("before", run.around(act, 260, 40, -8, 90))
        pyrun.run(NPC % act + 'a.call_method("TakeHit", (1000.0,))\n', 60)
        for k in range(3):
            time.sleep(0.2)
            run.shot("dying_%d" % k)
        time.sleep(4)
        run.shot("after")
    finally:
        run.finish()


def view(args):
    """Simulate: pictures from given camera poses "x,y,z,yaw,pitch" (cm, degrees), or "near:x,y,z" for
    two views of a spot (from 4.5 m west and east of it, 2 m above, looking down at it)."""
    run = Run("view", args.area)
    run.start(simulate=True)
    try:
        k = 0
        for pose in args.poses:
            if pose.startswith("near:"):
                x, y, z = (float(v) for v in pose[5:].split(","))
                shots = [(x - 450, y, z + 200, 0, -24), (x + 450, y, z + 200, 180, -24)]
            else:
                shots = [tuple(float(v) for v in pose.split(","))]
            for x, y, z, yaw, pitch in shots:
                run.shot("view_%02d" % k, {"location": {"x": x, "y": y, "z": z},
                                           "rotation": {"pitch": pitch, "yaw": yaw, "roll": 0},
                                           "scale": {"x": 1, "y": 1, "z": 1}})
                k += 1
    finally:
        run.finish()


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("look", help=look.__doc__)
    s.add_argument("area", choices=game.AREAS)
    s.add_argument("tags", nargs="+")
    s.add_argument("--dog", action="store_true", help="side and front views at dog height")
    s.set_defaults(fn=look)
    s = sub.add_parser("dialogue", help=dialogue.__doc__)
    s.add_argument("area", choices=game.AREAS)
    s.add_argument("--lines", type=int, default=8)
    s.set_defaults(fn=dialogue)
    s = sub.add_parser("view", help=view.__doc__)
    s.add_argument("area", choices=game.AREAS)
    s.add_argument("poses", nargs="+")
    s.set_defaults(fn=view)
    s = sub.add_parser("kill", help=kill.__doc__)
    s.add_argument("area", choices=game.AREAS)
    s.add_argument("tag")
    s.set_defaults(fn=kill)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
