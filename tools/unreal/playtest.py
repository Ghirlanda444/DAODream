"""Look at the game running, with pictures, from Simulate or Play in a castle level.

For checking a change in the game itself rather than in the editor. Pictures and a contact sheet (sheet.png, needs Pillow) go to
Unreal/Cousland/Saved/claude/playtest/<command>-<time>/ (git-ignored); script errors logged during the
run are printed at the end.

    python playtest.py look night bhn200cr_warning_servant gen00fl_dog     face and full length, Simulate
    python playtest.py look night bhn200cr_howe_east_hall1 --dog           side and front of a dog
    python playtest.py dialogue night --lines 6                            Play: each line, option 1
    python playtest.py kill night bhn200cr_howe_east_hall1                 Simulate: wake, kill, watch it fall
    python playtest.py fight day --fall                                    Play: fight the larder rats, then fall
    python playtest.py talents night                                       Play: use six talents on a soldier
    python playtest.py threat night                                        Play: two soldiers' threat tables
    python playtest.py enemytalents night                                  Play: soldiers using their talents
    python playtest.py ranged night                                        Play: an archer shoots; the player's bow
    python playtest.py partytalents night                                  Play: the Teyrna and the mabari's talents

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


SOUND = False  # tests are silent unless --sound (the user asks to hear them)


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
        pie.start(simulate=simulate, sound=SOUND)
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


MGR = '''
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
m = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if a.get_class().get_name() == "BP_PlotManager_C"][0]
'''
TALLY = ("Hits", "Misses", "Crits", "PlayerHealth", "PlayerMaxHealth", "bGameOver")
# Strike down every visible live hostile (a test's win); OUT["struck"] counts them.
CLEAR = '''
n = 0
for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor):
    if a.get_class().get_name() == "BP_DlgNPC_C" and a.get_editor_property("bHostile") and not a.get_editor_property("bDead") \
            and not a.get_editor_property("hidden"):  # AActor::bHidden: waiting for a plot
        a.call_method("TakeHit", (10000.0,))
        n += 1
OUT["struck"] = n
'''


def fight(args):
    """Play: wake creatures (default: --count of the larder's giant rats), fight them as the player with the
    hit rules, and report the rules' tally (hits, misses, criticals) and both sides' health. --fall then
    wakes two more and lowers the player's health so they finish them: the game over and the level's restart."""
    run = Run("fight", args.area)
    run.start(simulate=False)
    try:
        g = run.g
        for _ in range(8):  # the opening conversation is long; fighting waits while anyone talks
            g.converse(seconds=90)
            if not g.talking().get("bTalking"):
                break
        tags = args.tags or sorted(t for t in g.a["NpcTags"] if t.startswith("bhn100cr_rat_giant"))[:args.count]
        for t in tags:
            pyrun.run(NPC % run.npc(t) + 'a.call_method("SetPlotActive", (True,))\n', 60)
        x, y, z = g.loc(run.npc(tags[0]))
        g.go(x + 150, y, z, wait=1.0)
        run.shot("start")
        tally = lambda: pyrun.run(MGR + "OUT.update({k: m.get_editor_property(k) for k in %r})" % (TALLY,), 60)
        print("before", tally())
        # Swing once a second where the rats come to bite (game.fight scans every hostile: too slow here).
        t0, k = time.time(), 0
        while time.time() - t0 < args.seconds:
            g.attack()
            time.sleep(1.0)
            k += 1
            if k % 6 == 0:
                left = [t for t in tags if not g.npc_state(g.npc(t), ("bDead",))["bDead"]]
                st = tally()
                print("  %3ds" % (time.time() - t0), "rats left", len(left), st, flush=True)
                if k == 6:
                    run.shot("fighting")
                if not left or st.get("bGameOver"):
                    break
        run.shot("after_fight")
        print("after", tally())
        for t in tags:
            print("  ", t, g.npc_state(g.npc(t), ("bDead", "Health", "Defense", "Armour", "Crit", "Flank")))
        if args.fall:
            # wake more creatures so the player is struck, at 5 health
            print("hurt", pyrun.run(MGR + 'm.call_method("HurtPlayer", (m.get_editor_property("PlayerHealth") - 5.0,))\n', 60))
            for t in sorted(t for t in g.a["NpcTags"] if t.startswith("bhn100cr_rat_giant"))[args.count:args.count + 2]:
                pyrun.run(NPC % run.npc(t) + 'a.call_method("SetPlotActive", (True,))\n', 60)
                x, y, z = g.loc(run.npc(t))
            g.go(x + 120, y, z, wait=0.5)
            for k in range(8):
                time.sleep(1.5)
                st = tally()
                print("  falling", st)
                if st.get("bGameOver") or st.get("PlayerHealth", 1) <= 0:
                    run.shot("fallen")
                    break
            time.sleep(8)  # Restart reloads the level after 5 s
            try:
                print("after restart", tally())
            except Exception as e:  # the world is being replaced
                print("after restart: (reloading)", e)
            run.shot("restarted")
    finally:
        run.finish()


def party(args):
    """Play: Gilmore and the mabari join, the larder's first six rats wake and fight the three of you (each rat's
    foe and everyone's health are printed). The player is dropped to 0 at once and lies down while the party fights
    on; then the test wins the fight (strikes down every live hostile, the later waves too) and the fallen get up
    with 1 health 4 s after the last blow and regenerate. --wipe then drops the player again and knocks the party
    out: the game over."""
    run = Run("party", args.area)
    run.start(simulate=False)
    try:
        g = run.g
        for _ in range(8):
            g.converse(seconds=90)
            if not g.talking().get("bTalking"):
                break
        rats = sorted(t for t in g.a["NpcTags"] if t.startswith("bhn100cr_rat_giant"))[:6]
        x, y, z = g.loc(run.npc(rats[0]))
        g.go(x + 250, y, z, wait=0.5)
        for k, t in enumerate(("bhn100cr_gilmore", "gen00fl_dog")):
            pyrun.run(NPC % run.npc(t) + 'a.call_method("SetInParty", (True,))\na.set_actor_location(unreal.Vector(%f, %f, %f), False, True)\n'
                      % (x + 250, y + 120 * (k * 2 - 1), z), 60)
        for t in rats:
            pyrun.run(NPC % run.npc(t) + 'a.call_method("SetPlotActive", (True,))\n', 60)
        watch = rats + ["bhn100cr_gilmore", "gen00fl_dog"]
        state = lambda: pyrun.run(MGR + '''
OUT["mgr"] = {k: m.get_editor_property(k) for k in ("PlayerHealth", "bPlayerDown", "bGameOver", "Hits", "Misses")}
for tag, name in %r:
    a = [x for x in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if x.get_name() == name][0]
    f = a.get_editor_property("Foe")
    OUT[tag[-12:]] = (round(a.get_editor_property("Health")), a.get_editor_property("bDead"), a.get_editor_property("bDown"),
                      f.get_name()[:14] if f else None)
''' % ([(t, run.npc(t)) for t in watch],), 60)
        time.sleep(4)
        print("start", state(), flush=True)
        run.shot("fight")
        print("drop the player", pyrun.run(MGR + 'm.call_method("HurtPlayer", (m.get_editor_property("PlayerHealth"),))\n', 60))
        time.sleep(1)
        run.shot("player_down")
        time.sleep(6)
        st = state()
        print("  player down", st, flush=True)
        if any(v[2] for k, v in st.items() if k != "mgr" and isinstance(v, list)):
            run.shot("member_down")
        # win the fight: strike down every live hostile, the waves their deaths bring in too
        t0 = time.time()
        while time.time() - t0 < args.seconds:
            n = pyrun.run(MGR + CLEAR, 120).get("struck", 0)
            print("  cleared", n, flush=True)
            if not n:
                break
            time.sleep(3)
        for k in range(4):
            time.sleep(3)
            st = state()
            print("  after the fight", st, flush=True)
            if not st["mgr"]["bPlayerDown"] and st["mgr"]["PlayerHealth"] > 1:
                run.shot("got_up")
                break
        if args.wipe:
            # winning set off Gilmore's conversation: finish it, then everyone falls in one go
            for _ in range(4):
                g.converse(seconds=60)
                if not g.talking().get("bTalking"):
                    break
            print("wipe", pyrun.run(MGR + '''
m.call_method("HurtPlayer", (m.get_editor_property("PlayerHealth"),))
for name in %r:
    [x for x in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if x.get_name() == name][0].call_method("TakeHit", (10000.0,))
OUT.update({k: m.get_editor_property(k) for k in ("bPlayerDown", "bGameOver", "Standing")})
''' % ([run.npc(t) for t in ("bhn100cr_gilmore", "gen00fl_dog")],), 60))
            time.sleep(1)
            run.shot("wipe")
    finally:
        run.finish()


SAMPLE = '''
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
acts = {a.get_name(): a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor)}
m = [a for a in acts.values() if a.get_class().get_name() == "BP_PlotManager_C"][0]
rats, party = %r, %r
alive = engaged = dead = waiting = 0
for name in rats:
    a = acts[name]
    if a.get_editor_property("bDead"):
        dead += 1
    elif a.get_editor_property("hidden"):
        waiting += 1
    else:
        alive += 1
        f = a.get_editor_property("Foe")
        if f and a.get_horizontal_distance_to(f) <= 150.0:
            engaged += 1
OUT["rats"] = {"alive": alive, "biting": engaged, "dead": dead, "waiting": waiting}
OUT["health"] = {"player": round(m.get_editor_property("PlayerHealth"), 1)}
for tag, name in party:
    OUT["health"][tag] = round(acts[name].get_editor_property("Health"), 1)
OUT["down"] = [tag for tag, name in party if acts[name].get_editor_property("bDown")] + (["player"] if m.get_editor_property("bPlayerDown") else [])
OUT["tally"] = [m.get_editor_property(k) for k in ("Hits", "Misses", "Crits")]
OUT["game"] = round(unreal.GameplayStatics.get_time_seconds(w), 2)
OUT["talking"] = m.get_editor_property("bTalking")
OUT["probe"] = []
for name in rats:
    a = acts[name]
    f = a.get_editor_property("Foe")
    if a.get_editor_property("bDead") or a.get_editor_property("hidden") or not f:
        continue
    OUT["probe"].append((f.get_name()[:10], round(a.get_horizontal_distance_to(f)), round(a.get_distance_to(f)),
                         round(a.get_editor_property("AttackTimer"), 2), a.get_editor_property("bChasing"),
                         round(a.get_editor_property("Interval"), 2)))
if PRESS:
    m.call_method("PlayerAttack")
'''


def larder(args):
    """Play: the whole larder fight as the game stages it, with the game's attack timing: Gilmore and the mabari
    join, the first six rats wake and each death brings the next in (the rats' death scripts). The player swings
    as often as the rules let them. Every 2 s it records how many rats are biting (alive, visible, within 1.5 m
    of their foe), everyone's health and who is down; at the end the fight's length, the most and mean rats
    biting at once and the health each party member lost, to compare with recordings of the original."""
    run = Run("larder", args.area)
    run.start(simulate=False)
    try:
        g = run.g
        for _ in range(8):
            g.converse(seconds=90)
            if not g.talking().get("bTalking"):
                break
        rats = sorted(t for t in g.a["NpcTags"] if t.startswith("bhn100cr_rat_giant"))
        party = [("gilmore", "bhn100cr_gilmore"), ("dog", "gen00fl_dog")]
        x, y, z = g.loc(run.npc(rats[0]))
        g.go(x + 300, y, z, wait=0.5)
        for k, (_, t) in enumerate(party):
            print("join", t, pyrun.run(NPC % run.npc(t) + 'a.call_method("SetInParty", (True,))\n'
                                       'a.set_actor_location(unreal.Vector(%f, %f, %f), False, True)\n'
                                       'OUT["in_party"] = a.get_editor_property("bInParty")\n'
                                       % (x + 300, y + 120 * (k * 2 - 1), z), 60))
        start = "PRESS = %s\n" + SAMPLE % ([run.npc(t) for t in rats], [(n, run.npc(t)) for n, t in party])
        full = pyrun.run(start % False, 60)["health"]
        for t in rats[:6]:
            pyrun.run(NPC % run.npc(t) + 'a.call_method("SetPlotActive", (True,))\n', 60)
        t0, samples, shots = time.time(), [], 0
        while time.time() - t0 < args.seconds:
            # the player presses attack once a sample; the rules' pace decides when a swing happens
            s = pyrun.run(start % True, 60)
            s["t"] = round(time.time() - t0, 1)
            samples.append(s)
            print("  %5.1fs game %s" % (s["t"], s.get("game")), s["rats"], s["health"], s["down"], "talking" if s.get("talking") else "",
                  s.get("probe"), s.get("error", "")[-300:], flush=True)
            time.sleep(0.3)
            if shots < 3 and s["rats"]["biting"] >= 2:
                run.shot("fight_%d" % shots)
                shots += 1
            if (s["rats"]["dead"] == len(rats) or s["rats"]["alive"] + s["rats"]["waiting"] == 0
                    or len(s["down"]) == len(party) + 1):
                break
        run.shot("end")
        last = samples[-1]
        biting = [s["rats"]["biting"] for s in samples if s["rats"]["alive"]]
        print("RESULT", json.dumps({
            "seconds": last["t"], "game_seconds": round(last["game"] - samples[0]["game"], 1), "rats_dead": last["rats"]["dead"], "rats_total": len(rats),
            "biting_max": max(biting or [0]), "biting_mean": round(sum(biting) / max(1, len(biting)), 2),
            "health_lost": {k: round(1 - last["health"][k] / full[k], 2) for k in full}, "down": last["down"],
            "tally": last["tally"]}))
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


def cut(args):
    """Simulate: a cutscene's staging (extracted/ue/cutscenes/<name>.json, daotools cutscene.staging) at given
    times: its characters moved to their poses, a picture from its camera (no player pawn in Simulate)."""
    stage = json.load(open(args.staging, encoding="utf-8"))
    run = Run("cut", args.area)
    run.start(simulate=True)
    try:
        rate, cam, tags = stage["CamRate"], stage["Cam"], stage["ActorTags"]
        frames = stage["ActorFrames"]
        n = len(frames) // 4 // max(len(tags), 1)
        acts = {}
        for tag in tags:
            if tag == "PLAYER":
                continue
            try:
                acts[tag] = run.npc(tag)
                run.show(acts[tag])
                pyrun.run(NPC % acts[tag] + "a.call_method('SetPlotActive', (True,))\nOUT['ok'] = 1", 60)
            except Exception as e:  # not in this area
                print("no", tag, str(e)[:80])
        for t in args.times:
            i = min(int(t * rate), n - 1)
            for k, tag in enumerate(tags):
                if tag not in acts:
                    continue
                x, y, z, yaw = frames[(k * n + i) * 4:(k * n + i) * 4 + 4]
                pyrun.run(NPC % acts[tag] + "a.set_actor_location_and_rotation(unreal.Vector(%r, %r, %r), "
                          "unreal.Rotator(0, 0, %r), False, True)\nOUT['ok'] = 1" % (x, y, z, yaw), 60)
            if args.camera:  # an overview instead of the cutscene's own camera
                x, y, z, yaw, pitch = (float(v) for v in args.camera.split(","))
                run.shot("cut_%05.1fs" % t, {"location": {"x": x, "y": y, "z": z},
                                              "rotation": {"pitch": pitch, "yaw": yaw, "roll": 0},
                                              "scale": {"x": 1, "y": 1, "z": 1}})
            elif cam:
                x, y, z, pitch, yaw, fov = cam[i * 6:i * 6 + 6]
                run.shot("cut_%05.1fs" % t, {"location": {"x": x, "y": y, "z": z},
                                              "rotation": {"pitch": pitch, "yaw": yaw, "roll": 0},
                                              "scale": {"x": 1, "y": 1, "z": 1}})
    finally:
        run.finish()


# talents: the game's install and the rebalance mod's tables, for the test's talent rows (daotools.abilities)
GAME_DIR = "E:/Steam/steamapps/common/Dragon Age Ultimate Edition"
MOD_TABLES = os.path.join(game.ROOT, "extracted", "mods", "da_reborn", "erf")
TEST_TALENTS = (19, 603, 617, 1, 20, 3041)  # Precise Striking, Dirty Fighting, Shield Bash, Shield Pummel...
STATE = ("PStamina", "PPool", "PFatigue", "OwnAtk", "OwnPen", "OwnCrit", "PInterval", "PlayerHealth", "TalentText")


def talents(args):
    """Play: the player gets six talents (keys 1-6: Precise Striking, Dirty Fighting, Shield Bash, Shield Pummel,
    Perfect Strike, Taunt; rows from daotools.abilities for the exported player), stands by a soldier woken at
    night (--tag) and uses them in turn through UseTalent: the stamina pool, costs, upkeep and cooldowns, the stun
    (the soldier's attacks stop until it ends), the knockdown, the buff, a refusal while cooling down. Pictures of
    the HUD and the target."""
    import sys
    sys.path.insert(0, os.path.join(game.ROOT, "tools"))
    from daotools import abilities
    run = Run("talents", args.area)
    tables = abilities.load_tables(GAME_DIR, MOD_TABLES)
    table = abilities.talents(tables)
    run.start(simulate=False)
    try:
        g = run.g
        for _ in range(8):
            g.converse(seconds=90)
            if not g.talking().get("bTalking"):
                break
        rows = [x for i in TEST_TALENTS for x in abilities.talent_row(i, table[i], g.a["Player"])]
        names = [abilities.NAMES[i] for i in TEST_TALENTS]
        state = lambda: pyrun.run(MGR + "OUT.update({k: m.get_editor_property(k) for k in %r})\n"
                                  "OUT['now'] = unreal.GameplayStatics.get_time_seconds(w)" % (STATE,), 60)
        print("set", pyrun.run(MGR + "m.call_method('SetPlayerTalents', (%r, [], %r))\n"
                                     "OUT['names'] = list(m.get_editor_property('TalentNames'))" % (rows, names), 60))
        print("start", state())
        foe = run.npc(args.tag)
        target = lambda: g.npc_state(g.npc(args.tag), ("bDead", "Health", "StunUntil", "KnockUntil", "SlowUntil",
                                                       "DurScale", "Resist"))
        pyrun.run(NPC % foe + 'a.call_method("SetPlotActive", (True,))\n', 60)
        x, y, z = g.loc(foe)
        g.go(x + 140, y, z, wait=1.0)
        steps = []
        # one editor call uses the talent and reads the result: a call takes seconds of game time
        use = MGR + """t = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if a.get_name() == %r][0]
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
pawn.set_actor_location(t.get_actor_location() + unreal.Vector(110.0, 0.0, 0.0), False, True)
pawn.set_actor_rotation(unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0), True)
if t.get_editor_property("Health") < 400.0:  # topped up, so the mabari does not finish it first
    t.call_method("TakeHit", (-600.0,))  # instance variables cannot be set from Python
before = m.get_editor_property("PStamina")
m.call_method("UseTalent", (%d,))
OUT.update({k: m.get_editor_property(k) for k in %r})
OUT["spent"] = before - OUT["PStamina"]
OUT["now"] = unreal.GameplayStatics.get_time_seconds(w)
OUT["target"] = {k: t.get_editor_property(k) for k in ("bDead", "Health", "StunUntil", "KnockUntil", "SlowUntil", "DurScale")}
OUT["target"].update({k: round(OUT["target"][k] - OUT["now"], 2) for k in ("StunUntil", "KnockUntil", "SlowUntil") if OUT["target"][k]})
"""

        def step(label, k):
            s = pyrun.run(use % (foe, k, STATE), 60)
            steps.append({"step": label, **{k2: (round(v, 2) if isinstance(v, float) else v) for k2, v in s.items()}})
            print(label, json.dumps(steps[-1], default=str)[:700], flush=True)
            return s, s.get("target", {})

        step("1 Precise Striking on", 0)
        step("5 Perfect Strike", 4)
        run.shot("buffs")
        step("2 Dirty Fighting", 1)
        run.shot("stunned")
        step("2 again (cooling down)", 1)
        step("3 Shield Bash", 2)
        run.shot("shield_bash")
        step("4 Shield Pummel", 3)
        step("6 Taunt", 5)
        step("1 Precise Striking off", 0)
        print("RESULT", json.dumps(steps, default=str)[:4000])
    finally:
        run.finish()


THREAT_TALENTS = (3041, 3023, 3016, 808)  # Taunt, Feign Death, Disengage, Threaten


def threat_check(args):
    """Play at night: two soldiers (--tags) are woken next to the player and the mabari; the player gets Taunt, Feign
    Death, Disengage and Threaten (keys 1-4). It reports each soldier's target and threat table: at first, after a
    few seconds of fighting, after Taunt, while feigning death, after it ends, after Disengage. The soldiers and
    the player are topped up so the fight lasts."""
    import sys
    sys.path.insert(0, os.path.join(game.ROOT, "tools"))
    from daotools import abilities
    run = Run("threat", args.area)
    tables = abilities.load_tables(GAME_DIR, MOD_TABLES)
    table = abilities.talents(tables)
    run.start(simulate=False)
    try:
        g = run.g
        for _ in range(8):
            g.converse(seconds=90)
            if not g.talking().get("bTalking"):
                break
        rows = [x for i in THREAT_TALENTS for x in abilities.talent_row(i, table[i], g.a["Player"])]
        names = [abilities.NAMES[i] for i in THREAT_TALENTS]
        pyrun.run(MGR + "m.call_method('SetPlayerTalents', (%r, [], %r))" % (rows, names), 60)
        foes = [run.npc(t) for t in args.tags]
        dog = run.npc("gen00fl_dog")
        for f in foes:
            pyrun.run(NPC % f + 'a.call_method("SetPlotActive", (True,))\n', 60)
        x, y, z = g.loc(foes[0])
        g.go(x + 150, y, z, wait=0.5)
        pyrun.run(NPC % dog + 'a.set_actor_location(unreal.Vector(%f, %f, %f), False, True)\n' % (x + 150, y + 150, z), 60)
        sample = MGR + """
acts = {a.get_name(): a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor)}
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
label = lambda a: "player" if a == pawn else ("dog" if a and a.get_name() == %r else (a.get_name() if a else None))
if m.get_editor_property("PlayerHealth") < 70.0:  # kept up: the run is about who the soldiers go for
    m.call_method("HurtPlayer", (m.get_editor_property("PlayerHealth") - m.get_editor_property("PlayerMaxHealth"),))
if %r >= 0:
    m.call_method("UseTalent", (%r,))
OUT["now"] = round(unreal.GameplayStatics.get_time_seconds(w), 1)
OUT["player"] = {k: round(m.get_editor_property(k), 1) if isinstance(m.get_editor_property(k), float) else m.get_editor_property(k) for k in ("PlayerHealth", "PStamina", "bFeign", "bThreatenOn")}
for n in %r:
    a = acts[n]
    if a.get_editor_property("Health") < 400.0:
        a.call_method("TakeHit", (-600.0,))
    OUT[n] = {"foe": label(a.get_editor_property("Foe")), "wait": a.get_editor_property("TWait"),
              "table": {label(w2): round(v, 1) for w2, v in zip(a.get_editor_property("ThreatWho"), a.get_editor_property("ThreatVal"))}}
"""
        steps = []

        def step(label, slot=-1, wait=0.0):
            time.sleep(wait)
            s = pyrun.run(sample % (dog, slot, slot, foes), 60)
            steps.append({"step": label, **s})
            print(label, json.dumps(s, default=str)[:900], flush=True)

        step("start", wait=2.0)
        step("fighting", wait=8.0)
        run.shot("fighting")
        step("Threaten on", 3)
        step("Taunt", 0)
        step("Feign Death on", 1)
        run.shot("feigning")
        step("feigning", wait=4.0)
        step("Feign Death off", 1)
        step("Disengage", 2, wait=2.0)
        print("RESULT", json.dumps(steps, default=str)[:6000])
    finally:
        run.finish()


def enemy_talents(args):
    """Play at night: soldiers (--tags: a weapon-and-shield one, a two-handed one, the knight) are woken next to the
    player and the mabari and fight on while the player and they are topped up; every few seconds it reports each
    soldier's stamina, its talents' cooldowns (a talent used shows a time) and modes, and the player's stun,
    disarm and talent lock. RESULT: the talents each soldier used and what reached the player."""
    run = Run("enemytalents", args.area)
    run.start(simulate=False)
    try:
        g = run.g
        for _ in range(8):
            g.converse(seconds=90)
            if not g.talking().get("bTalking"):
                break
        foes = [run.npc(t) for t in args.tags]
        x, y, z = g.loc(foes[-1])
        for k, f in enumerate(foes):  # woken and brought together, a metre and a half apart
            pyrun.run(NPC % f + 'a.call_method("SetPlotActive", (True,))\n'
                      'a.set_actor_location(unreal.Vector(%f, %f, %f), False, True)\n' % (x, y + 150 * k, z), 60)
        g.go(x + 150, y + 150, z, wait=0.5)
        sample = MGR + """
acts = {a.get_name(): a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor)}
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
now = unreal.GameplayStatics.get_time_seconds(w)
if m.get_editor_property("PlayerHealth") < 70.0:
    m.call_method("HurtPlayer", (m.get_editor_property("PlayerHealth") - m.get_editor_property("PlayerMaxHealth"),))
OUT["now"] = round(now, 1)
OUT["player"] = {"health": round(m.get_editor_property("PlayerHealth"), 1),
                 "stunned": round(max(0.0, m.get_editor_property("PStunUntil") - now), 1),
                 "disarmed": round(max(0.0, m.get_editor_property("PDisarmUntil") - now), 1),
                 "locked": round(max(0.0, m.get_editor_property("PLockUntil") - now), 1)}
for n in %r:
    a = acts[n]
    if a.get_editor_property("Health") < 0.5 * a.get_editor_property("MaxHealth"):
        a.call_method("TakeHit", (-200.0,))
    t = list(a.get_editor_property("NTalents"))
    ready = list(a.get_editor_property("NReady"))
    OUT[n] = {"stamina": round(a.get_editor_property("NStamina"), 1), "pool": a.get_editor_property("NPool"),
              "talents": {int(t[k * 16]): round(ready[k] - now, 1) if ready[k] else None for k in range(len(ready)) if t[k * 16]},
              "on": [int(t[k * 16]) for k, o in enumerate(a.get_editor_property("NOn")) if o],
              "interval": round(a.get_editor_property("Interval"), 2), "foe": (a.get_editor_property("Foe").get_name() if a.get_editor_property("Foe") else None),
              "foe_m": round(a.get_distance_to(a.get_editor_property("Foe")) / 100.0, 1) if a.get_editor_property("Foe") else None}
dog = acts[%r]
OUT["dog"] = {k: dog.get_editor_property(k) for k in ("bDead", "bDown", "Health", "bInParty")}
"""
        used, player_hits, samples = {}, {"stunned": 0, "disarmed": 0, "locked": 0}, []
        for k in range(args.samples):
            time.sleep(4.0)
            r = pyrun.run(sample % (foes, run.npc("gen00fl_dog")), 60)
            samples.append(r)
            print(json.dumps(r, default=str)[:900], flush=True)
            for f in foes:
                for tid, left in (r.get(f, {}).get("talents") or {}).items():
                    if left is not None:
                        used.setdefault(f, set()).add(int(tid))
            for key in player_hits:
                player_hits[key] += 1 if r.get("player", {}).get(key) else 0
            if k == 2:
                run.shot("fight")
        print("RESULT", json.dumps({"used": {f: sorted(v) for f, v in used.items()}, "player_samples": player_hits}))
    finally:
        run.finish()


def ranged(args):
    """Play at night: the mabari is knocked out and an archer (--tag) woken 8 m from the player; every few seconds it
    reports whether it stands
    and shoots (its distance to its foe, chasing or not, a clear shot), the arrows in flight, its talents, and the
    player's health, pin and armour. Then the player switches to the shortbow (SwitchWeapon) and shoots it
    (PlayerAttack) a few times: the rules' tally and the archer's health."""
    run = Run("ranged", args.area)
    run.start(simulate=False)
    try:
        g = run.g
        for _ in range(8):
            g.converse(seconds=90)
            if not g.talking().get("bTalking"):
                break
        archer = run.npc(args.tag)
        pyrun.run(NPC % run.npc("gen00fl_dog") + 'a.call_method("KnockOut")\n', 60)  # out of it: a duel
        x, y, z = g.loc(archer)
        g.go(x + 800, y, z, wait=0.5)
        pyrun.run(NPC % archer + 'a.call_method("SetPlotActive", (True,))\n', 60)
        sample = MGR + """
acts = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor)]
t = [a for a in acts if a.get_name() == %r][0]
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
now = unreal.GameplayStatics.get_time_seconds(w)
if m.get_editor_property("PlayerHealth") < 60.0:
    m.call_method("HurtPlayer", (m.get_editor_property("PlayerHealth") - m.get_editor_property("PlayerMaxHealth"),))
if t.get_editor_property("Health") < 40.0:  # kept up, so it keeps shooting
    t.call_method("TakeHit", (-200.0,))
foe = t.get_editor_property("Foe")
ready = list(t.get_editor_property("NReady"))
tal = list(t.get_editor_property("NTalents"))
OUT.update({"now": round(now, 1), "arrows": sum(1 for a in acts if a.get_class().get_name() == "BP_Arrow_C"),
            "foe": foe.get_name() if foe else None, "foe_m": round(t.get_distance_to(foe) / 100.0, 1) if foe else None,
            "chasing": t.get_editor_property("bChasing"), "clear": t.get_editor_property("bShotClear"),
            "range": t.get_editor_property("NRange"), "archer_health": round(t.get_editor_property("Health"), 1),
            "talents": {int(tal[k * 18]): round(ready[k] - now, 1) for k in range(len(ready)) if tal[k * 18] and ready[k]},
            "attacks": m.get_editor_property("Hits") + m.get_editor_property("Misses"),
            "player": round(m.get_editor_property("PlayerHealth"), 1),
            "pinned": round(max(0.0, m.get_editor_property("PRootUntil") - now), 1),
            "armour_broken": round(max(0.0, m.get_editor_property("PArmourUntil") - now), 1)})
"""
        for k in range(args.samples):
            time.sleep(3.0)
            r = pyrun.run(sample % archer, 60)
            print(json.dumps(r, default=str)[:600], flush=True)
            if k == 2:
                run.shot("archer")
        tally = lambda: pyrun.run(MGR + "OUT.update({k: m.get_editor_property(k) for k in ('Hits', 'Misses', 'bBowOn', 'PInterval', 'BowRange')})", 60)
        print("switch", pyrun.run(MGR + "m.call_method('SwitchWeapon')\nOUT.update({k: m.get_editor_property(k) for k in ('bBowOn', 'PInterval', 'BowMin', 'BowMax')})", 60))
        # each shot in one editor call: the player 8 m from the archer, facing it; the shot resolves at once
        shoot = MGR + """
t = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if a.get_name() == %r][0]
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
dog = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if a.get_name() == %r][0]
if not dog.get_editor_property("bDead"):
    dog.call_method("KnockOut")  # it gets up 4 s after a lull: kept out of the duel
if t.get_editor_property("Health") < 40.0:
    t.call_method("TakeHit", (-200.0,))
OUT["archer_dead"] = t.get_editor_property("bDead")
pawn.set_actor_location(t.get_actor_location() + unreal.Vector(800.0, 0.0, 0.0), False, True)
pawn.set_actor_rotation(unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0), True)
before = (m.get_editor_property("Hits"), m.get_editor_property("Misses"), t.get_editor_property("Health"))
m.call_method("PlayerAttack")
OUT.update({"hits": m.get_editor_property("Hits") - before[0], "misses": m.get_editor_property("Misses") - before[1],
            "damage": round(m.get_editor_property("LastDamage"), 1), "archer_lost": round(before[2] - t.get_editor_property("Health"), 1),
            "metres": round(t.get_distance_to(pawn) / 100.0, 1)})
"""
        shots = []
        for k in range(6):
            r = pyrun.run(shoot % (archer, run.npc("gen00fl_dog")), 60)
            shots.append(r)
            print("  shot", r, flush=True)
            time.sleep(2.5)
            if k == 1:
                run.shot("player_shoots")
        print("RESULT", json.dumps({"shots": len(shots), "landed": sum(1 for r in shots if r.get("archer_lost", 0) > 0),
                                    "resolved": sum(r.get("hits", 0) + r.get("misses", 0) for r in shots)}))
    finally:
        run.finish()


def party_talents(args):
    """Play at night: the Teyrna is woken (she starts the night hidden) and joins (SetInParty) beside the player and
    the mabari, and hostiles (--tags) are
    woken 8 m away; every few seconds, per fighter: health, foe and its distance, stamina, the talents cooling down
    and the modes on, its defense debuff (Growl) and knockdown left; the arrows in flight. The player is kept up."""
    run = Run("partytalents", args.area)
    run.start(simulate=False)
    try:
        g = run.g
        for _ in range(8):
            g.converse(seconds=90)
            if not g.talking().get("bTalking"):
                break
        foes = [run.npc(t) for t in args.tags]
        x, y, z = g.loc(foes[0])
        g.go(x + 800, y, z, wait=0.5)
        for k, t in enumerate(("bhn100cr_mother", "gen00fl_dog")):
            pyrun.run(NPC % run.npc(t) + 'a.call_method("SetPlotActive", (True,))\na.call_method("SetInParty", (True,))\n'
                      'a.set_actor_location(unreal.Vector(%f, %f, %f), False, True)\n' % (x + 900, y + 150 * (k * 2 - 1), z), 60)
        for f in foes:
            pyrun.run(NPC % f + 'a.call_method("SetPlotActive", (True,))\n', 60)
        watch = [(t[-12:], run.npc(t)) for t in ("bhn100cr_mother", "gen00fl_dog")] + list(zip(args.tags, foes))
        sample = MGR + """
acts = {a.get_name(): a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor)}
now = unreal.GameplayStatics.get_time_seconds(w)
if m.get_editor_property("PlayerHealth") < 60.0:
    m.call_method("HurtPlayer", (m.get_editor_property("PlayerHealth") - m.get_editor_property("PlayerMaxHealth"),))
OUT["arrows"] = sum(1 for a in acts.values() if a.get_class().get_name() == "BP_Arrow_C")
OUT["player"] = round(m.get_editor_property("PlayerHealth"), 1)
for tag, name in %r:
    a = acts[name]
    foe = a.get_editor_property("Foe")
    tal = list(a.get_editor_property("NTalents"))
    ready = list(a.get_editor_property("NReady"))
    on = list(a.get_editor_property("NOn"))
    OUT[tag[-14:]] = {"hp": round(a.get_editor_property("Health"), 1), "dead": a.get_editor_property("bDead"),
        "foe": foe.get_name()[-14:] if foe else None, "m": round(a.get_distance_to(foe) / 100.0, 1) if foe else None,
        "sta": round(a.get_editor_property("NStamina"), 1),
        "cool": {int(tal[k * 18]): round(ready[k] - now, 1) for k in range(len(ready)) if tal[k * 18] and ready[k] > now},
        "on": [int(tal[k * 18]) for k in range(len(on)) if on[k] > 0],
        "growled": round(max(0.0, a.get_editor_property("NDefUntil") - now), 1),
        "down": round(max(0.0, a.get_editor_property("KnockUntil") - now), 1),
        "every": round(a.get_editor_property("Interval"), 2)}
"""
        seen = {}
        for k in range(args.samples):
            time.sleep(3.0)
            r = pyrun.run(sample % (watch,), 60)
            print(json.dumps(r, default=str)[:1400], flush=True)
            for tag, v in r.items():
                if isinstance(v, dict):
                    for i in list(v.get("cool", {})) + v.get("on", []):
                        seen.setdefault(tag, set()).add(i)
            if k in (1, 4):
                run.shot("party_%d" % k)
        print("RESULT", json.dumps({t: sorted(str(i) for i in s) for t, s in seen.items()}))
    finally:
        run.finish()


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sound", action="store_true", help="play the game's sound (tests are silent otherwise)")
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
    s = sub.add_parser("cut", help=cut.__doc__)
    s.add_argument("area", choices=game.AREAS)
    s.add_argument("staging")
    s.add_argument("times", nargs="+", type=float)
    s.add_argument("--camera", help="an overview pose x,y,z,yaw,pitch instead of the cutscene's camera")
    s.set_defaults(fn=cut)
    s = sub.add_parser("kill", help=kill.__doc__)
    s.add_argument("area", choices=game.AREAS)
    s.add_argument("tag")
    s.set_defaults(fn=kill)
    s = sub.add_parser("fight", help=fight.__doc__)
    s.add_argument("area", choices=game.AREAS)
    s.add_argument("tags", nargs="*")
    s.add_argument("--seconds", type=int, default=60)
    s.add_argument("--count", type=int, default=2, help="how many of the larder's rats to wake (the game: 6)")
    s.add_argument("--fall", action="store_true", help="then let the player fall: game over and restart")
    s.set_defaults(fn=fight)
    s = sub.add_parser("larder", help=larder.__doc__)
    s.add_argument("area", choices=game.AREAS)
    s.add_argument("--seconds", type=int, default=180)
    s.set_defaults(fn=larder)
    s = sub.add_parser("talents", help=talents.__doc__)
    s.add_argument("area", choices=game.AREAS, nargs="?", default="night")
    s.add_argument("--tag", default="bhn200cr_howe_east_hall1", help="the soldier to wake and fight")
    s.set_defaults(fn=talents)
    s = sub.add_parser("threat", help=threat_check.__doc__)
    s.add_argument("area", choices=game.AREAS, nargs="?", default="night")
    s.add_argument("--tags", nargs=2, default=["bhn200cr_howe_east_hall1", "bhn200cr_howe_east_hall2"])
    s.set_defaults(fn=threat_check)
    s = sub.add_parser("enemytalents", help=enemy_talents.__doc__)
    s.add_argument("area", choices=game.AREAS, nargs="?", default="night")
    s.add_argument("--tags", nargs="+", default=["bhn200cr_howe_mother2", "bhn200cr_howe_mother1", "bhn200cr_howe_knight"])
    s.add_argument("--samples", type=int, default=15)
    s.set_defaults(fn=enemy_talents)
    s = sub.add_parser("ranged", help=ranged.__doc__)
    s.add_argument("area", choices=game.AREAS, nargs="?", default="night")
    s.add_argument("--tag", default="bhn200cr_howe_main_hall1", help="a hostile archer")
    s.add_argument("--samples", type=int, default=8)
    s.set_defaults(fn=ranged)
    s = sub.add_parser("partytalents", help=party_talents.__doc__)
    s.add_argument("area", choices=game.AREAS, nargs="?", default="night")
    s.add_argument("--tags", nargs="+", default=["bhn200cr_howe_panicked1", "bhn200cr_howe_panicked2",
                                                 "bhn200cr_howe_panicked3", "bhn200cr_howe_panicked4"])
    s.add_argument("--samples", type=int, default=10)
    s.set_defaults(fn=party_talents)
    s = sub.add_parser("party", help=party.__doc__)
    s.add_argument("area", choices=game.AREAS)
    s.add_argument("--seconds", type=int, default=120)
    s.add_argument("--wipe", action="store_true", help="then knock everyone out: the game over")
    s.set_defaults(fn=party)
    args = p.parse_args()
    global SOUND
    SOUND = args.sound
    args.fn(args)


if __name__ == "__main__":
    main()
