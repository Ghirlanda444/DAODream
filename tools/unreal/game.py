"""Play the origin like a player would: walk (teleport), E (Interact / TryUse), pick dialogue options
(ke * Choose), F (PlayerAttack). No flags are set by hand. Needs Play running (pie.start()); the area's
export (extracted/ue/areas) tells where everyone stands.

    import game; g = game.Game("night")   # or "day"
    g.talk_to("bhn100cr_father"); g.converse(); print(g.has("BHN_MOTHER_IN_PARTY"))

Flag names come from the game's plots (extracted/plots/raw, see docs/SCRIPTS.md), cached in
extracted/ue/flagkeys.json: game data, so never committed.
"""
import json, math, os, sys, time
import ue, pie

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
AT = "editor_toolset.toolsets.actor.ActorTools"
AREAS = {"day": ("L_CastleCousland", "bhn100ar_castle_cousland"),
         "night": ("L_CastleNight", "bhn200ar_castle_after_siege")}


def flag_keys():
    """Flag name -> "GUID:FLAG" key (the keys BP_PlotManager stores)."""
    cache = os.path.join(ROOT, "extracted", "ue", "flagkeys.json")
    if not os.path.exists(cache):
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        from daotools import plo
        plots = plo.load_dir(os.path.join(ROOT, "extracted", "plots", "raw"))
        keys = {name: "%s:%d" % (guid, fid) for guid, p in plots.items() for fid, name in p["flags"].items()}
        json.dump(keys, open(cache, "w"))
    return json.load(open(cache))


class Game:
    def __init__(self, area):
        ue.init()
        self.level, name = AREAS[area]
        self.W = "/Game/Cousland/Maps/UEDPIE_0_%s.%s:PersistentLevel." % (self.level, self.level)
        pie.W = self.W
        self.a = json.load(open(os.path.join(ROOT, "extracted", "ue", "areas", name + ".json"), encoding="utf-8"))
        self.said = []
        self._rk = None

    # --- world ---------------------------------------------------------------------------
    def loc(self, actor):
        l = json.loads(ue.call(AT, "get_actor_transform", {"actor": {"refPath": self.W + actor}}))["returnValue"]["location"]
        return l["x"], l["y"], l["z"]

    def place(self, actor, x, y, z, yaw=0):
        return ue.call(AT, "set_actor_transform", {"actor": {"refPath": self.W + actor}, "worldspace": True, "xform": {
            "location": {"x": x, "y": y, "z": z}, "rotation": {"pitch": 0, "yaw": yaw, "roll": 0},
            "scale": {"x": 1, "y": 1, "z": 1}}})

    def go(self, x, y, floor_z, wait=0.8):
        """Walk the player to a spot (feet at floor_z)."""
        self.place("BP_ThirdPersonCharacter_C_0", x, y, floor_z + 95)
        time.sleep(wait)

    def npc(self, tag):
        return self.a["NpcTags"].index(tag)

    def npc_state(self, i, names=("bHidden", "bDead", "bHostile", "bInParty", "Health")):
        return json.loads(json.loads(pie.props(self.W + "BP_DlgNPC_C_%d" % i, list(names)))["returnValue"])

    # --- player input --------------------------------------------------------------------
    def talk_to(self, tag, dist=140):
        """Walk up to a character and press E."""
        i = self.npc(tag)
        x, y, z = self.loc("BP_DlgNPC_C_%d" % i)
        self.go(x + dist, y, z, wait=0.8)
        pie.cmd("ke * Interact")
        time.sleep(0.8)

    def use_door(self, tag, side=1):
        """Walk up to a door and press E (side: which side of the door to stand on)."""
        i = self.a["DoorTags"].index(tag)
        x, y, z, yaw = self.a["DoorPose"][i * 4:i * 4 + 4]
        w = self.a["DoorSize"][i * 2] if self.a["DoorSize"] else 300
        r = math.radians(yaw)
        # the panel runs along the door's X from the hinge; stand in front of its middle
        mx, my = x + math.cos(r) * w / 2, y + math.sin(r) * w / 2
        nx, ny = -math.sin(r) * side, math.cos(r) * side
        self.go(mx + nx * 120, my + ny * 120, z, wait=0.8)
        pie.cmd("ke * TryUse")
        time.sleep(0.8)

    def attack(self):
        pie.cmd("ke BP_PlotManager_C_0 PlayerAttack")

    def converse(self, seconds=60, quiet=4, pick=1, picks=None):
        """Click through whatever conversation is open. picks: {text substring: option number}."""
        t0 = last = time.time()
        seen = None
        while time.time() - t0 < seconds:
            lines, opts = pie.dlg()
            if lines:
                key = (tuple(lines), tuple(o[0] for o in opts))
                if key != seen:
                    print("   ", lines, [o[0] for o in opts], flush=True)
                    self.said.append(key)
                    seen = key
                n = pick
                for sub, num in (picks or {}).items():
                    if any(sub in o[0] for o in opts):
                        n = num
                n = n if len(opts) >= n else 1
                pie.cmd("ke * Choose %d" % (n - 1))
                last = time.time()
                time.sleep(0.6)
            else:
                if time.time() - last > quiet:
                    return
                time.sleep(0.5)
        print("    (still talking after %ds)" % seconds)

    def fight(self, seconds=60, radius=2000):
        """Attack every hostile within radius of the player until none is left."""
        t0 = time.time()
        px, py, pz = self.loc("BP_ThirdPersonCharacter_C_0")
        while time.time() - t0 < seconds:
            live = []
            for i, h in enumerate(self.a["NpcHostile"]):
                if not h:
                    continue
                s = self.npc_state(i, ("bHidden", "bDead", "bHostile"))
                if s["bHidden"] or s["bDead"] or not s["bHostile"]:
                    continue
                x, y, z = self.loc("BP_DlgNPC_C_%d" % i)
                if math.dist((x, y), (px, py)) < radius:
                    live.append((i, x, y, z))
            if not live:
                return True
            i, x, y, z = live[0]
            print("    attack", self.a["NpcTags"][i], flush=True)
            self.go(x + 120, y, z, wait=0.3)
            self.attack()
            time.sleep(1.1)
        print("    (hostiles left after %ds)" % seconds)
        return False

    # --- state ---------------------------------------------------------------------------
    def flags(self):
        if self._rk is None:
            self._rk = {v: k for k, v in flag_keys().items()}
        return {self._rk.get(f, f) for f in json.loads(json.loads(pie.props("BP_PlotManager_C_0", ["Flags"]))["returnValue"])["Flags"]}

    def has(self, *names):
        f = self.flags()
        return {n: n in f for n in names}

    def talking(self):
        return json.loads(json.loads(pie.props("BP_PlotManager_C_0", ["bTalking", "PendingTalk"]))["returnValue"])

    def where(self):
        return [round(v) for v in self.loc("BP_ThirdPersonCharacter_C_0")]

    def errors(self, since=""):
        r = json.loads(pie.log("Error|Accessed None|not built yet|could not load|no start line", 30))["returnValue"]
        return [l for l in r if l > since]
