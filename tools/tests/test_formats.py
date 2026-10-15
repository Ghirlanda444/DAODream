import json
import math
import struct
import tempfile
import unittest
from pathlib import Path

from daotools import ambient, area, cnv, fields as F, fsb, kit, mfdecode, plo, plotlogic, stats, toolset, unreal
from daotools.cli import main
from daotools.erf import ERF, ERFError, is_erf
from daotools.gda import GDA, column_hash
from daotools.gff4 import (GFF4, T_FLOAT32, T_SINT16, T_UINT8, T_UINT32, T_UINT64, T_VECTOR3F, TlkString,
                           to_jsonable)
from daotools.tlk import TalkTable, TalkTables

from builders import (GFF4Writer, Tmpl, build_cnv, build_erf, build_fsb, build_gff3, build_plo,
                      build_tlk_v02, build_tlk_v05)
from daotools.gff3 import GFF3, is_gff3


class ERFTests(unittest.TestCase):
    files = {"bhn_castle.cnv": b"hello" * 50, "readme.txt": b"", "x.gda": bytes(range(256))}

    def test_v20(self):
        erf = ERF(build_erf(self.files))
        self.assertEqual(erf.version, "V2.0")
        self.assertEqual(erf.build_year, 2009)
        self.assertEqual([e.name for e in erf.entries], list(self.files))
        for name, data in self.files.items():
            self.assertEqual(erf.read(name), data)
        self.assertEqual(erf.find("BHN_CASTLE.CNV").extension, "cnv")

    def test_v22_compression(self):
        for method in (0, 1, 7):
            with self.subTest(method=method):
                erf = ERF(build_erf(self.files, "V2.2", compression=method))
                self.assertEqual(erf.compression, method)
                for name, data in self.files.items():
                    self.assertEqual(erf.read(name), data)

    def test_encrypted_lists_but_does_not_extract(self):
        erf = ERF(build_erf(self.files, "V2.2", encryption=2))
        self.assertTrue(erf.encrypted)
        self.assertEqual(len(erf.entries), 3)
        with self.assertRaises(ERFError):
            erf.read("x.gda")

    def test_open_and_magic(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "a.rim"
            p.write_bytes(build_erf(self.files))
            self.assertTrue(is_erf(p))
            with ERF.open(p) as erf:
                self.assertEqual(erf.read("x.gda"), self.files["x.gda"])
            (Path(d) / "b.erf").write_bytes(b"not an archive at all")
            self.assertFalse(is_erf(Path(d) / "b.erf"))

    def test_rejects_garbage(self):
        with self.assertRaises(ERFError):
            ERF(b"GFF V4.0" * 4)


class GFF4Tests(unittest.TestCase):
    def test_all_field_kinds(self):
        inner = Tmpl("INNR", [(1, T_UINT32), (2, "string")])
        root = Tmpl("ROOT", [
            (10, T_UINT8), (11, T_SINT16), (12, T_UINT64), (13, T_FLOAT32), (14, T_VECTOR3F),
            (15, "string"), (16, "tlk"), (17, ("struct", inner)), (18, ("list", T_UINT32)),
            (19, ("structlist", inner)), (20, ("reflist", inner)), (21, "string"), (22, ("structlist", inner)),
        ])
        data = GFF4Writer("TEST", "V0.1", [root, inner]).build({
            10: 200, 11: -5, 12: 2 ** 40, 13: 1.5, 14: [1.0, 2.0, 3.0],
            15: "Teyrn Bryce Cousland", 16: (4321, "inline override"), 17: {1: 7, 2: "inner"},
            18: [3, 1, 4, 1, 5], 19: [{1: 1, 2: "a"}, {1: 2, 2: "b"}], 20: [{1: 9, 2: "ref"}, None],
            21: None, 22: None,
        })
        g = GFF4(data)
        self.assertEqual((g.file_type, g.type_version, g.platform), ("TEST", "V0.1", "PC  "))
        r = g.root
        self.assertEqual(r.label, "ROOT")
        self.assertEqual(r.get(10), 200)
        self.assertEqual(r.get(11), -5)
        self.assertEqual(r.get(12), 2 ** 40)
        self.assertEqual(r.get(13), 1.5)
        self.assertEqual(r.get(14), [1.0, 2.0, 3.0])
        self.assertEqual(r.get(15), "Teyrn Bryce Cousland")
        self.assertEqual(r.get(16), TlkString(4321, "inline override"))
        self.assertEqual((r.get(17).get(1), r.get(17).get(2)), (7, "inner"))
        self.assertEqual(r.get(18), [3, 1, 4, 1, 5])
        self.assertEqual([s.get(2) for s in r.get(19)], ["a", "b"])
        self.assertEqual(r.get(20)[0].get(2), "ref")
        self.assertIsNone(r.get(20)[1])
        self.assertEqual(r.fields[21], "")
        self.assertEqual(r.fields[22], [])
        self.assertEqual(g.list_bytes(r, 18), struct.pack("<5I", 3, 1, 4, 1, 5))

        doc = to_jsonable(r, {15: "name"})
        self.assertEqual(doc["name"], "Teyrn Bryce Cousland")
        self.assertEqual(doc["16"], {"strref": 4321, "text": "inline override"})
        json.dumps(doc)  # must be serialisable

    def test_tlk_without_inline_text(self):
        root = Tmpl("ROOT", [(1, "tlk")])
        g = GFF4(GFF4Writer("TEST", "V0.1", [root]).build({1: 77}))
        self.assertEqual(g.root.get(1), TlkString(77, ""))


class GFF3Tests(unittest.TestCase):
    def test_creature_like_template(self):
        data = build_gff3("UTC ", {
            "Tag": (10, "bhn100cr_father"),
            "TemplateResRef": (11, "bhn100cr_father"),
            "FirstName": (12, (12345, {0: "Bryce", 4: "Brice"})),
            "Description": (18, 777),
            "Appearance": (2, 7),
            "Gender": (0, 1),
            "Level": (5, -3),
            "Speed": (8, 1.5),
            "Seed": (6, 2 ** 40),
            "Position": (17, [1.0, 2.0, 3.0]),
            "Stats": (14, {"Strength": (4, 16)}),
            "Equipment": (15, [{"Slot": (4, 1), "Item": (11, "gen_im_sword")}, {"Slot": (4, 2)}]),
        })
        self.assertTrue(is_gff3(data))
        g = GFF3(data)
        self.assertEqual((g.file_type, g.version), ("UTC ", "V3.2"))
        r = g.root
        self.assertEqual(r.get("Tag"), "bhn100cr_father")
        self.assertEqual(r.get("TemplateResRef"), "bhn100cr_father")
        self.assertEqual(r.get("FirstName"), TlkString(12345, "Bryce"))
        self.assertEqual(r.get("Description"), TlkString(777))
        self.assertEqual((r.get("Appearance"), r.get("Gender"), r.get("Level")), (7, 1, -3))
        self.assertEqual(r.get("Speed"), 1.5)
        self.assertEqual(r.get("Seed"), 2 ** 40)
        self.assertEqual(r.get("Position"), [1.0, 2.0, 3.0])
        self.assertEqual(r.get("Stats").get("Strength"), 16)
        self.assertEqual([e.get("Slot") for e in r.get("Equipment")], [1, 2])
        self.assertEqual(r.get("Equipment")[0].get("Item"), "gen_im_sword")
        doc = to_jsonable(r, resolve={777: "A teyrn."}.get)
        self.assertEqual(doc["Description"], {"strref": 777, "text": "A teyrn."})
        json.dumps(doc)


class TalkTableTests(unittest.TestCase):
    strings = {1: "Welcome to Highever.", 2: "", 70000: "Ser Gilmore — «Ça va»? 🐕", 5: "Howe"}

    def test_v02(self):
        t = TalkTable(GFF4(build_tlk_v02(self.strings)))
        self.assertEqual(t.strings, self.strings)

    def test_v05_huffman(self):
        t = TalkTable(GFF4(build_tlk_v05(self.strings)))
        self.assertEqual(t.version, "V0.5")
        self.assertEqual(t.strings, self.strings)

    def test_chain_order(self):
        a = TalkTable(GFF4(build_tlk_v02({1: "module"})))
        b = TalkTable(GFF4(build_tlk_v02({1: "core", 2: "core only"})))
        chain = TalkTables([a, b])
        self.assertEqual((chain.get(1), chain.get(2), chain.get(3, "?")), ("module", "core only", "?"))


class GDATests(unittest.TestCase):
    def test_columns_and_rows(self):
        col = Tmpl("COLM", [(F.G2DA_COLUMN_HASH, T_UINT32), (F.G2DA_COLUMN_TYPE, T_UINT8)])
        row = Tmpl("ROWS", [(F.G2DA_COLUMN_1, T_UINT32), (F.G2DA_COLUMN_1 + 1, "string"),
                            (F.G2DA_COLUMN_1 + 2, T_FLOAT32)])
        root = Tmpl("G2DA", [(F.G2DA_COLUMN_LIST, ("structlist", col)), (F.G2DA_ROW_LIST, ("structlist", row))])
        names = ["ID", "Label", "Speed"]
        data = GFF4Writer("G2DA", "V0.1", [root, col, row]).build({
            F.G2DA_COLUMN_LIST: [{F.G2DA_COLUMN_HASH: column_hash(n), F.G2DA_COLUMN_TYPE: t}
                                 for n, t in zip(names, (1, 0, 2))],
            F.G2DA_ROW_LIST: [{F.G2DA_COLUMN_1: 0, F.G2DA_COLUMN_1 + 1: "mabari", F.G2DA_COLUMN_1 + 2: 1.25}],
        })
        table = GDA(GFF4(data), ["label", "id"])
        self.assertEqual(table.column_names, ["id", "label", f"0x{column_hash('speed'):08x}"])
        self.assertEqual([c["type"] for c in table.columns], ["int", "string", "float"])
        self.assertEqual(table.records(), [{"id": 0, "label": "mabari", f"0x{column_hash('speed'):08x}": 1.25}])


class ConversationTests(unittest.TestCase):
    lines = [
        {"text": 100, "speaker": "bryce", "children": [1, 2]},
        {"text": 101, "speaker": "player", "children": [3]},
        {"text": (102, "Inline reply"), "speaker": "player", "children": [0], "action_flag": 3, "script": "bhn_plot"},
        {"text": 103, "speaker": "howe", "children": []},
        {"text": 104, "speaker": "nobody"},
    ]
    tlk = TalkTables([TalkTable(GFF4(build_tlk_v02({100: "Ah, Rendon.", 101: "Father?", 103: "Indeed."})))])

    def _check(self, conv):
        self.assertEqual(conv["vo_bank"], "vo_bank_test")
        self.assertEqual(conv["starts"], [0])
        texts = [l["text"] for l in conv["lines"]]
        self.assertEqual(texts, ["Ah, Rendon.", "Father?", "Inline reply", "Indeed.", ""])
        self.assertEqual(conv["lines"][0]["children"], [1, 2])
        self.assertEqual(conv["lines"][2]["action"], {"script": "bhn_plot", "parameter": None})
        self.assertNotIn("action", conv["lines"][0])  # empty slot: no GUID, no script
        self.assertEqual([l["kind"] for l in conv["lines"]], ["npc", "player", "player", "npc", "npc"])
        script = cnv.transcript(conv)
        self.assertIn("[0] bryce: Ah, Rendon.", script)
        self.assertIn("\n    [3] howe: Indeed.\n", script)
        self.assertIn("[2] player: Inline reply  [do]", script)
        self.assertIn("## Entry point 1 of 1", script)
        self.assertIn("-> (back to line 0)", script)
        self.assertIn("not reached from any start: [4]", script)
        json.dumps(conv)

    def test_children_as_structs(self):
        self._check(cnv.export(GFF4(build_cnv(self.lines, [0])), self.tlk, "bhn_test"))

    def test_children_as_indices(self):
        self._check(cnv.export(GFF4(build_cnv(self.lines, [0], children_as_structs=False)), self.tlk))

    def test_struct_where_text_expected(self):
        # Retail files nest structs where a plain string was expected.
        who = Tmpl("WHO ", [(1, "string"), (2, T_UINT32)])
        line = Tmpl("LINE", [(F.CONV_LINE_TEXT, "tlk"), (F.CONV_LINE_SPEAKER, ("struct", who)),
                             (F.CONV_LINE_SKIP, ("struct", who))])
        root = Tmpl("CONV", [(F.CONV_LINE_LIST, ("structlist", line)), (F.CONV_VO_BANK, ("struct", who))])
        data = GFF4Writer("DLG ", "V0.2", [root, line, who]).build({
            F.CONV_VO_BANK: {1: "bank", 2: 5},
            F.CONV_LINE_LIST: [{F.CONV_LINE_TEXT: 100, F.CONV_LINE_SPEAKER: {1: "bryce", 2: 1},
                                F.CONV_LINE_SKIP: {1: "", 2: 0}}],
        })
        conv = cnv.export(GFF4(data), self.tlk)
        json.dumps(conv)
        self.assertEqual(conv["lines"][0]["speaker"], {"_struct": "WHO ", "1": "bryce", "2": 1})
        self.assertEqual(conv["vo_bank"], {"_struct": "WHO ", "1": "bank", "2": 5})
        self.assertIn('"1":"bryce"', cnv.transcript({**conv, "starts": [0]}))

    def test_wrong_type(self):
        with self.assertRaises(cnv.CNVError):
            cnv.export(GFF4(build_tlk_v02({1: "x"})))


class UnrealConversationTests(unittest.TestCase):
    conv = {
        "conversation": "bhn_test", "vo_bank": "bhn_test", "starts": [3, 0],
        "lines": [
            {"index": 0, "kind": "npc", "text": "<desc>Laughs</desc> Ah, <emp>Rendon</emp>.",
             "speaker": "OWNER", "children": [1, 2], "stage": "bhn_stage",
             "action": {"plot": "AAAA", "flag": 4}},
            {"index": 1, "kind": "player", "text": "", "speaker": "PLAYER", "children": [],
             "condition": {"plot": "BBBB", "flag": 260}},
            {"index": 2, "kind": "player", "text": "Not now.", "speaker": "PLAYER", "children": [0],
             "condition": {"plot": "BBBB", "flag": 2, "test": 0},
             "action": {"script": "bhn_plot", "parameter": 1}},
            {"index": 3, "kind": "npc", "text": "Indeed.", "speaker": "bhn_howe", "children": [],
             "condition": {"plot": "CCCC", "flag": 1, "test": 7}, "action": {"plot": "AAAA", "flag": 4, "test": 0}},
            {"index": 4, "missing": True},
        ],
    }

    def test_runtime_shape(self):
        with tempfile.TemporaryDirectory() as d:
            for tag, name in (("bhn_test", "Teyrn Bryce"), ("bhn_howe", "Arl Howe")):
                (Path(d) / f"{tag}.utc.json").write_text(json.dumps(
                    {"root": {"Tag": tag, "LocName": {"strref": 1, "text": name}}}), encoding="utf-8")
            out = unreal.conversation(self.conv, names_dir=d, true_flags=["BBBB:260"])
        self.assertEqual(out["Format"], unreal.FORMAT)
        self.assertEqual(out["Starts"], [3, 0])
        self.assertEqual(out["SpeakerNames"],
                         {"bhn_test": "Teyrn Bryce", "OWNER": "Teyrn Bryce", "bhn_howe": "Arl Howe"})
        self.assertEqual(out["TrueFlags"], ["BBBB:260"])
        first, silent, reply, howe, missing = out["Lines"]
        self.assertEqual(first["Text"], "(Laughs) Ah, Rendon.")
        self.assertEqual((first["ActionKey"], first["CondKey"], first["Stage"]), ("AAAA:4", "", "bhn_stage"))
        self.assertEqual((silent["IsPlayer"], silent["Text"], silent["CondKey"]), (True, "", "BBBB:260"))
        self.assertEqual((reply["CondKey"], reply["CondNot"], reply["ActionScript"]), ("BBBB:2", True, "bhn_plot"))
        self.assertEqual((missing["Text"], missing["Children"], missing["Speaker"]), ("", [], ""))
        self.assertEqual((first["ActionNot"], howe["ActionKey"], howe["ActionNot"]), (False, "AAAA:4", True))
        self.assertEqual(out["Warnings"], ["line 3 condition: unknown plot test 7, read as 'flag is set'",
                                           "line 4: missing"])
        self.assertEqual(out["FlagNames"], {})
        # Unreal maps JSON onto structs: every line has every key, and no nulls.
        self.assertTrue(all(l.keys() == first.keys() for l in out["Lines"]))
        self.assertNotIn("null", json.dumps(out))

    def test_flag_names(self):
        plots = {"AAAA": {"guid": "AAAA", "name": "talked_to", "script": "", "flags": {4: "TALKED_TO_FATHER"}},
                 "BBBB": {"guid": "BBBB", "name": "class_race_gend", "script": "",
                          "flags": {2: "QUEST_DONE", 260: "GEN_GENDER_MALE"}}}
        out = unreal.conversation(self.conv, true_flags=["BBBB:260"], plots=plots)
        self.assertEqual(out["FlagNames"], {"AAAA:4": "TALKED_TO_FATHER", "BBBB:2": "QUEST_DONE",
                                            "BBBB:260": "GEN_GENDER_MALE"})
        self.assertIn("plot flag CCCC:1: not found in the plot files", out["Warnings"])


class VoiceOverTests(unittest.TestCase):
    # Two MPEG-2 layer III frames at 56 kbps, 24 kHz: 168 bytes each.
    mp3 = (b"\xff\xf3\x74\xc0" + b"\x11" * 164) * 2
    bank = build_fsb([("26080_m.wav", mp3 + b"\x00" * 13, 0x100220), ("26081_m.wav", mp3 + b"\x01", 0x100220),
                      ("ambient_sgl.wav", b"\x00" * 32, 0x500020)])

    def test_read(self):
        bank = fsb.FSB(self.bank)
        self.assertEqual([s.name for s in bank.samples], ["26080_m.wav", "26081_m.wav", "ambient_sgl.wav"])
        first, second, adpcm = bank.samples
        self.assertEqual((first.codec, first.frequency, first.channels, first.stem), ("mpeg", 24000, 1, "26080_m"))
        self.assertEqual(second.data, self.mp3 + b"\x01")  # data follows the headers, back to back
        self.assertEqual(fsb.mpeg_end(first.data), 336)
        self.assertEqual(fsb.mpeg_end(b"\x00" * 8), 0)
        self.assertEqual(adpcm.codec, "imaadpcm")
        self.assertEqual(fsb.vo_sample(26080), "26080_m.wav")
        self.assertEqual(fsb.vo_sample(None), "")
        with self.assertRaises(fsb.FSBError):
            fsb.FSB(b"RIFF" + b"\0" * 60)

    def test_runtime_vo_and_extract(self):
        conv = {"conversation": "c", "starts": [0], "lines": [
            {"index": 0, "kind": "npc", "strref": 26080, "text": "Hello.", "speaker": "OWNER", "children": [1]},
            {"index": 1, "kind": "player", "strref": 26090, "text": "Hi.", "speaker": "PLAYER", "children": [2]},
            {"index": 2, "kind": "npc", "strref": 26099, "text": "Unvoiced.", "speaker": "OWNER", "children": []}]}
        out = unreal.conversation(conv, vo_samples=fsb.FSB(self.bank).names())
        self.assertEqual([l["Vo"] for l in out["Lines"]], ["26080_m", "", ""])
        self.assertEqual(out["Warnings"], ["line 2: no voice-over sample 26099_m.wav"])
        self.assertEqual([l["Vo"] for l in unreal.conversation(conv)["Lines"]], ["", "", ""])
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "c.fsb").write_bytes(self.bank)
            self.assertEqual(main(["fsb", "extract", str(Path(d) / "c.fsb"), "--out", str(Path(d) / "mp3"),
                                   "--mp3"]), 0)
            self.assertEqual(sorted(p.name for p in (Path(d) / "mp3").iterdir()), ["26080_m.mp3", "26081_m.mp3"])
            self.assertEqual((Path(d) / "mp3" / "26080_m.mp3").read_bytes(), self.mp3)  # padding cut
        # Decoding to PCM goes through Windows' MP3 decoder, which needs real audio (checked on the
        # install, see docs/GAME_DATA.md); the PCM .wav writer is checked here.
        pcm = struct.pack("<4h", 0, 1000, -1000, 7)
        wav = mfdecode.pcm_wav(24000, 1, 16, pcm)
        self.assertEqual((wav[:4], wav[8:12], wav[12:16]), (b"RIFF", b"WAVE", b"fmt "))
        self.assertEqual(struct.unpack_from("<I", wav, 4)[0], len(wav) - 8)
        self.assertEqual(struct.unpack_from("<HHIIHH", wav, 20), (1, 1, 24000, 48000, 2, 16))
        self.assertEqual(wav[36:44], b"data" + struct.pack("<I", len(pcm)))
        self.assertEqual(wav[44:], pcm)


class OriginTests(unittest.TestCase):
    def test_export_origin(self):
        def conv(text):
            return {"conversation": "bhn_guard", "vo_bank": "bhn_guard", "starts": [0], "lines": [
                {"index": 0, "kind": "npc", "strref": 26080, "text": text, "speaker": "OWNER", "children": []}]}
        with tempfile.TemporaryDirectory() as d:
            pull = Path(d) / "pull"
            for folder, text in (("al_area", "Halt."), ("designerdialogs", "Halt."), ("patch002", "Halt!")):
                (pull / "json" / folder).mkdir(parents=True)
                (pull / "json" / folder / "bhn_guard.dlg.conv.json").write_text(json.dumps(conv(text)), encoding="utf-8")
            (pull / "json" / "designercreatures").mkdir()
            for tag in ("bhn_guard_2", "bhn_guard_amb"):
                (pull / "json" / "designercreatures" / f"{tag}.utc.json").write_text(json.dumps(
                    {"root": {"Tag": tag, "DialogResRef": "bhn_guard",
                              "LocName": {"strref": 1, "text": "Guard"}}}), encoding="utf-8")
            (pull / "raw" / "loose").mkdir(parents=True)
            (pull / "raw" / "loose" / "bhn_guard.fsb").write_bytes(build_fsb([("26080_m.wav", b"\0" * 8, 0x100220)]))
            out = Path(d) / "ue"
            self.assertEqual(main(["unreal", "origin", str(pull), "--no-vo", "--out", str(out)]), 0)
            rt = json.loads((out / "conversations" / "bhn_guard.json").read_text(encoding="utf-8"))
            index = json.loads((out / "conversations" / "index.json").read_text(encoding="utf-8"))
        self.assertEqual(rt["Lines"][0]["Text"], "Halt!")  # the patch copy wins
        self.assertEqual((rt["Owner"], rt["SpeakerNames"]["OWNER"], rt["Lines"][0]["Vo"]),
                         ("bhn_guard_2", "Guard", "26080_m"))
        entry = index["Conversations"]["bhn_guard"]
        self.assertEqual((entry["UsedBy"], entry["Source"], entry["SpokenLines"], entry["VoicedLines"]),
                         (["bhn_guard_2", "bhn_guard_amb"], "patch002", 1, 1))
        self.assertEqual(index["Warnings"], ["bhn_guard: the 3 copies differ; using patch002"])


class AreaTests(unittest.TestCase):
    # 4 x 3 cells of 1 m from (10, 20): a 2 x 2 floor at 0 m, one cell at 1 m, the rest blocked.
    #   row 0: F F B B
    #   row 1: F F U B     (U = upper, 16/16 m)
    #   row 2: B B B B
    nav = {"_struct": "NAVI", "3086": 4, "3087": 3, "3088": 1.0, "3090": [10.0, 20.0, 0.0],
           "3093": [0, 0, 0, 0, 0, 0, 16, 0, 0, 0, 0, 0],
           "3114": [5, 5, -1, -1, 5, 5, 15, -1, -1, -1, -1, -1]}

    def test_floor_plan(self):
        boxes = area.floor_plan(self.nav)
        rows = [boxes[i:i + 7] for i in range(0, len(boxes), 7)]
        floors = sorted(r for r in rows if r[6] == 0)
        # The 2 x 2 floor merges into one box; Y is flipped, so y 20..22 m becomes -2200..-2000 cm.
        self.assertEqual(floors, [[1000.0, -2200.0, -20.0, 1200.0, -2000.0, 0.0, 0],
                                  [1200.0, -2200.0, 80.0, 1300.0, -2100.0, 100.0, 0]])
        walls = [r for r in rows if r[6] == 1]
        self.assertTrue(walls)
        self.assertTrue(all(r[5] >= 300.0 for r in walls))  # 3 m above the floor beside them

    def test_yaw_and_area(self):
        # Game yaw 0 faces +Y; Bryce's -80 degrees faces +X, which is -10 degrees in Unreal.
        q = math.radians(-80) / 2
        self.assertAlmostEqual(area.ue_yaw(0, 0, math.sin(q), math.cos(q)), -10.0, places=1)
        are = {"Tag": "bhn_area", "Layout": "lay", "CreatureList": [
                   {"Tag": "bryce", "TemplateResRef": "bhn_father", "Active": 1, "XPosition": 10.5, "YPosition": 20.5,
                    "ZPosition": 0.0, "XOrientation": 0, "YOrientation": 0, "ZOrientation": 0, "WOrientation": 1},
                   {"Tag": "rat", "TemplateResRef": "bhn_rat", "Active": 1, "XPosition": 0, "YPosition": 0,
                    "ZPosition": 0, "XOrientation": 0, "YOrientation": 0, "ZOrientation": 0, "WOrientation": 1},
                   {"Tag": "late", "TemplateResRef": "bhn_father", "Active": 0, "XPosition": 0, "YPosition": 0,
                    "ZPosition": 0, "XOrientation": 0, "YOrientation": 0, "ZOrientation": 0, "WOrientation": 1},
                   {"Tag": "larder_rat", "TemplateResRef": "bhn_rat_giant", "Active": 0, "TeamId": 1,
                    "XPosition": 0, "YPosition": 0, "ZPosition": 0, "XOrientation": 0, "YOrientation": 0,
                    "ZOrientation": 0, "WOrientation": 1}],
               "WaypointList": [{"Tag": "start", "HasMapNote": 1, "MapNote": {"strref": 1, "text": "Main Hall"},
                                 "XPosition": 11.0, "YPosition": 21.0, "ZPosition": 0.0, "XOrientation": 0,
                                 "YOrientation": 0, "ZOrientation": 0, "WOrientation": 1}],
               "PlaceableList": [
                   {"Tag": "bhn_door_cellar", "TemplateResRef": "bhn_dr_sm_wd", "Active": 1, "InitialState": 1,
                    "XPosition": 12.0, "YPosition": 20.0, "ZPosition": 0.0, "XOrientation": 0, "YOrientation": 0,
                    "ZOrientation": 0, "WOrientation": 1},
                   {"Tag": "bhn_chest", "TemplateResRef": "bhn_chest", "Active": 1, "InitialState": 0,
                    "XPosition": 0, "YPosition": 0, "ZPosition": 0, "XOrientation": 0, "YOrientation": 0,
                    "ZOrientation": 0, "WOrientation": 1}]}
        templates = {"bhn_father": {"DialogResRef": "BHN_Father", "LocName": {"strref": 2, "text": "Bryce"},
                                    "Appearance Data": {"Gender": 1}},
                     "bhn_rat": {"DialogResRef": ""},
                     "bhn_rat_giant": {"DialogResRef": "", "Race": 5, "Rank": 1, "GroupId": 1,
                                       "LocName": {"strref": 3, "text": "Giant Rat"}}}
        out = area.area(are, {"3020": {"3110": self.nav}}, templates, start="start")
        # Every creature, the rat without a team or conversation too (plots may move or kill it).
        self.assertEqual((out["NpcTags"], out["NpcNames"], out["NpcConversations"], out["NpcFemale"]),
                         (["bryce", "rat", "late", "larder_rat"], ["Bryce", "", "Bryce", "Giant Rat"],
                          ["bhn_father", "", "bhn_father", ""], [0, 0, 0, 0]))
        self.assertEqual(out["NpcPose"][:4], [1050.0, -2050.0, 0.0, -90.0])
        self.assertEqual(out["NpcActive"][2:], [0, 0])  # inactive ones are kept, hidden until a plot shows them
        self.assertEqual((out["NpcTeam"][2:], out["NpcScale"][2:]), ([-1, 1], [1.0, 0.35]))
        self.assertEqual((out["NpcHostile"][2:], out["NpcRank"][2:]), ([0, 1], [0, 1]))
        self.assertEqual((out["Summary"]["TalkingCreatures"], out["Summary"]["TeamOnly"]), (2, 1))
        self.assertEqual((out["WaypointTags"], out["WaypointPose"]), (["start"], [1100.0, -2100.0, 0.0, -90.0]))
        self.assertEqual(out["Summary"]["OtherCreatures"], 1)
        # Only doors, with their state (1 = locked) and a small door's greybox size.
        self.assertEqual((out["DoorTags"], out["DoorPose"], out["DoorState"], out["DoorSize"], out["DoorActive"]),
                         (["bhn_door_cellar"], [1200.0, -2000.0, 0.0, -90.0], [1], [160.0, 260.0], [1]))
        self.assertEqual((out["Start"], out["Labels"], out["LabelPos"]),
                         ([1100.0, -2100.0, 0.0, -90.0], ["Main Hall"], [1100.0, -2100.0, 0.0]))
        self.assertEqual(out["Summary"]["Floors"], 2)
        self.assertEqual(out["Warnings"], [])


class KitTests(unittest.TestCase):
    # A made-up kit piece: one 4 m x 0.4 m x 5 m box standing on the model origin.
    WALL_PHY = {"_struct": "mdlh", "6999": [{"_struct": "node", "6999": [{"_struct": "cobj", "6999": [
        {"_struct": "shap", "6058": 2, "6060": [0.0, 0.0, 0.0, 1.0], "6061": [0.0, 0.0, 2.5, 1.0],
         "6998": {"_struct": "boxs", "6071": [2.0, 0.2, 2.5]}}]}]}]}
    BLOCK_MMH = {"_struct": "mdlh", "6999": [{"_struct": "node", "6999": [
        {"_struct": "bbox", "6054": [-1.0, -0.5, 0.0, 1.0], "6055": [1.0, 0.5, 3.0, 1.0]}]}]}

    def test_solids(self):
        q90 = [0.0, 0.0, math.sqrt(0.5), math.sqrt(0.5)]  # 90 degrees about Z
        room = {"4": [10.0, 20.0, 1.0], "5": q90, "3050": [
            {"3063": "My_Wall01_0", "4": [1.0, 0.0, 0.0], "5": [0.0, 0.0, 0.0, 1.0], "3059": 1.0},
            {"3063": "blk_01_0", "4": [0.0, 0.0, 0.0], "5": [0.0, 0.0, 0.0, 1.0]},
            {"3063": "my_floor01_0", "4": [0.0, 0.0, 0.0], "5": [0.0, 0.0, 0.0, 1.0]}]}
        out = kit.solids([room], {"my_wall01_0": (self.WALL_PHY, None), "blk_01_0": (None, self.BLOCK_MMH)})
        self.assertEqual(out["Summary"]["Walls"], 1)
        self.assertEqual((out["Summary"]["Blockers"], out["Summary"]["Skipped"]), (1, 1))
        wall = out["Solids"][:13]
        # The room turns the wall's +1 m X offset into +1 m Y: (10, 21, 1 + 2.5) m, Y flipped for Unreal.
        self.assertEqual(wall[0:6], [1000.0, -2100.0, 350.0, 200.0, 20.0, 250.0])
        self.assertEqual([round(v, 3) + 0.0 for v in wall[6:12]], [0.0, -1.0, 0.0, 0.0, 0.0, 1.0])
        self.assertEqual(wall[12], kit.WALL)
        self.assertEqual(out["Solids"][13:19], [1000.0, -2000.0, 250.0, 100.0, 50.0, 150.0])

    def test_cut_doorway(self):
        wall = [0.0, 0.0, 250.0, 200.0, 20.0, 250.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0]
        out, cuts = area.cut_doorways(wall, [([50.0, 0.0, 0.0], 80.0)])
        self.assertEqual(cuts, 1)
        pieces = [out[i:i + 13] for i in range(0, len(out), 13)]
        # A 160 cm door at x = 50 (plus 10 cm either side) leaves -200..-40 and 140..200.
        self.assertEqual([(p[0], p[3]) for p in pieces], [(-120.0, 80.0), (170.0, 30.0)])
        self.assertEqual(area.cut_doorways(wall, [([900.0, 0.0, 0.0], 80.0)]), (wall, 0))


class DoorFitTests(unittest.TestCase):
    @staticmethod
    def box(x, y, z, hx, hy, hz, kind=0):
        return [x, y, z, hx, hy, hz, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, kind]

    def test_door_model_size(self):
        mmh = {"_struct": "mdlh", "6999": [{"_struct": "node", "6999": [
            {"_struct": "bbox", "6054": [0.0, -0.2, 0.0, 1.0], "6055": [2.0, 0.2, 3.0, 1.0]}]}]}
        models = kit.door_models({"my_door": {"Appearance": 7}}, [{"ID": 7, "ModelName": "PLC_MyDoor_0"}],
                                 {"plc_mydoor_0": (None, mmh)})
        self.assertEqual(models, {"my_door": (0.0, 2.0, 3.0)})
        self.assertEqual(kit.door_model_names({"my_door": {"Appearance": 7}}, [{"ID": 7, "ModelName": "PLC_MyDoor_0"}]),
                         {"plc_mydoor_0"})

    def test_frames_close_the_doorway(self):
        # A 100 cm door at the origin facing +X (its width along Y); walls start at y = -200 and y = 150.
        walls = self.box(0, -220, 200, 20, 20, 200) + self.box(0, 170, 200, 20, 20, 200)
        frames, n = area.frame_doors([0.0, 0.0, 0.0, 0.0], [100.0, 200.0], walls)
        self.assertEqual(n, 2)
        self.assertEqual([(frames[i + 1], frames[i + 4]) for i in range(0, len(frames), 13)],
                         [(-125.0, 75.0), (100.0, 50.0)])
        # A wall 7 m away is a corridor beside the door, not its frame.
        far = self.box(0, -720, 200, 20, 20, 200) + self.box(0, 170, 200, 20, 20, 200)
        self.assertEqual(area.frame_doors([0.0, 0.0, 0.0, 0.0], [100.0, 200.0], far)[1], 1)

    def test_drop_hanging_props(self):
        nav = AreaTests.nav  # floor at 0 m around (10.5, 20.5) m
        table = self.box(1050, -2050, 40, 50, 50, 40, kit.PROP)
        lamp = self.box(1050, -2050, 250, 20, 20, 20, kit.PROP)
        lintel = self.box(1050, -2050, 250, 20, 20, 20, kit.WALL)
        kept, dropped = area.drop_hanging(table + lamp + lintel, nav)
        self.assertEqual((dropped, kept), (1, table + lintel))


class StatsTests(unittest.TestCase):
    # Made-up tables in the shape of the game's.
    TABLES = {
        "packages_base": {5: {"ID": 5, "StartingClass": 1, "Strategy": 1, "MinLevel": 0}},
        "autoscale": {1: {"ID": 1, "fscale": 0.5, "fHealthScale": 0.5, "nBonusPoints": 0, "nLevelScale": 1,
                          "fDamageScale": 0.5},
                      100: {"ID": 100, "fscale": 1.0, "fHealthScale": 1.0, "nBonusPoints": 0, "nLevelScale": 0,
                            "fDamageScale": 1.0}},
        "as_data": {1: {"ID": 1, "s1": 1.0, "s2": 2.0, "s3": 0.0, "s4": 0.0, "s5": 0.0, "s6": 1.0}},
        "cla_data": {1: {"ID": 1, "label": "Fighter", "BaseHealth": 80.0, "HealthPerLevel": 10.0, "BaseAttack": 50.0,
                         "BaseDefense": 40.0, "DamagePerLevel": 0.5, "StrAdjust": 2.0}},
        "race_base": {3: {"ID": 3, "StrAdjust": 1.0}},
        "itemstats": {2: {"ID": 2, "Damage": 6.0, "DamageRange": 1.5}},
        "difficulty": {1: {"ID": 1, "DmgScalingThresh": 7.0}},
    }

    def test_creature(self):
        # Rank 1 at area level 2 is level 3; STR = 10 + 2 levels x 0.5 x 3 points x (1/1)/3 = 11, +2 class.
        st = stats.stats(self.TABLES, package=5, rank=1, area_level=2)
        self.assertEqual((st["Level"], st["Attributes"]["Str"], st["Attributes"]["Dex"]), (3, 13.0, 11.0))
        self.assertEqual(st["Health"], 50.0)  # (80 + 10 x 2 levels) x 0.5
        # Unarmed 3-4.5, + strength (13 - 10) x 25-50% x 1.25, + 0.5 per level (3 levels).
        self.assertEqual(st["Damage"], (5.44, 7.88))
        self.assertEqual(stats.damage_after_scaling(7.88, st["DamageScale"], st["DamageThreshold"]), 3.94)
        self.assertEqual(stats.damage_after_scaling(5.44, st["DamageScale"], st["DamageThreshold"]), 5.44)

    def test_player_and_weapon(self):
        st = stats.stats(self.TABLES, package=0, rank=100, race=3, base_item=2, player_class=1)
        self.assertEqual((st["Level"], st["Attributes"]["Str"], st["Health"]), (1, 13.0, 80.0))
        self.assertEqual(st["Damage"], (7.25, 11.0))  # 6-9 + 3 x 25-50% + 0.5
        self.assertEqual(stats.hit_chance(50.0, 40.0), 64.0)
        self.assertEqual(stats.weapon_base_item([{"TemplateResRef": "cap"}, {"TemplateResRef": "Sword"}],
                                                {"cap": {"BaseItem": 9}, "sword": {"BaseItem": 2}},
                                                self.TABLES["itemstats"]), 2)


class AmbientTests(unittest.TestCase):
    # Made-up rows in the shape of ambient_anim_patterns and anim_base.
    ANIMS = {650: {"AnimName": "my_pray_enter"}, 808: {"AnimName": "my_pointforward"},
             838: {"AnimName": "my_wandereast"}, 640: {"AnimName": "my_twitch_v1"}, 700: {"AnimName": "my_stand"}}

    def test_actions(self):
        row = {"ActionTotal": 6, "Action0": 1.04, "Action1": 650.99, "Action2": 808.0, "Action3": 838.02,
               "Action4": 700.0, "Action5": -3.0}
        self.assertEqual(ambient.actions(row, self.ANIMS),
                         [(ambient.IDLE, 4.0), (ambient.KNEEL, ambient.HOLD), (ambient.GESTURE, 2.5),
                          (ambient.LOOK_RIGHT, 5.0), (ambient.IDLE, 2.5)])
        index, flat = ambient.pattern_table({"patterns": {7: row, 8: {"ActionTotal": 0}}, "anims": self.ANIMS})
        self.assertEqual(index, [7.0, 0.0, 5.0])
        self.assertEqual(flat[:4], [float(ambient.IDLE), 4.0, float(ambient.KNEEL), -1.0])

    def test_settings_and_destinations(self):
        template = {"VarTable": [{"Name": "AMBIENT_SYSTEM_STATE", "Value": 0},
                                 {"Name": "AMBIENT_MOVE_PREFIX", "Value": "ap_<tag>"},
                                 {"Name": "AMBIENT_ANIM_FREQ", "Value": -1.0}]}
        instance = {"VarTable": [{"Name": "AMBIENT_SYSTEM_STATE", "Value": 1},
                                 {"Name": "AMBIENT_MOVE_PATTERN", "Value": 2},
                                 {"Name": "AMBIENT_ANIM_PATTERN", "Value": 15}]}
        st = ambient.settings(ambient.variables(template, instance), "maid")
        self.assertEqual(st, {"State": 1, "Move": 2, "Prefix": "ap_maid", "Pattern": 15, "Freq": -1.0})
        wps = ["start", "ap_maid_02", "ap_maid_01", "post", "post"]
        self.assertEqual(ambient.destinations("ap_maid", wps), [2, 1])
        self.assertEqual(ambient.destinations("post", wps), [3, 4])
        self.assertEqual(ambient.destinations("", wps), [])

    def test_plot_calls(self):
        script = """
            void main()
            {
                object oMaid = UT_GetNearestCreatureByTag(oPC, MY_CR_MAID);
                if (nType == EVENT_TYPE_SET_PLOT)
                {
                    switch(nFlag)
                    {
                        case MAID_BUSY: Ambient_Start(oMaid, AMBIENT_SYSTEM_ENABLED, AMBIENT_MOVE_INVALID,
                                                      AMBIENT_MOVE_PREFIX_NONE, 15); break;
                        case MAID_RESTS: Ambient_Stop(oMaid); Ambient_StartTeam(MY_TEAM); break;
                    }
                }
            }
        """
        plot = {"guid": "DDDD", "name": "my_maid", "script": "my_maid", "flags": {0: "MAID_BUSY", 1: "MAID_RESTS"}}
        t = plotlogic.translate(script, plot, {}, {"MY_CR_MAID": "my_cr_maid", "MY_TEAM": 4})
        self.assertEqual({k: [(a["kind"], a["target"], a["value"]) for a in v] for k, v in t["cases"].items()},
                         {"MAID_BUSY": [(9, "my_cr_maid", 15)],
                          "MAID_RESTS": [(9, "my_cr_maid", 0), (9, "team:4", -1)]})


class NightLogicTests(unittest.TestCase):
    # Made-up scripts in the shape of the game's, not game text.
    PLOTS = {"my_main": {"guid": "AAAA", "name": "my_main", "flags": {0: "BATTLE", 1: "PRELUDE"}}}

    def test_events_helpers_and_new_kinds(self):
        script = """
            void Wake()
            {
                object oMum = UT_GetNearestCreatureByTag(oPC, MY_CR_MUM);
                WR_SetObjectActive(oMum, TRUE);
            }
            void main()
            {
                switch (nEventType)
                {
                    case EVENT_TYPE_AREALOAD_POSTLOADEXIT:
                    {
                        if (nAreaOnce == FALSE)
                        {
                            object oBody = GetObjectByTag("cook");
                            KillCreature(oBody);
                            oBody = GetObjectByTag("scribe");
                            KillCreature(oBody);
                            if (nDebug == FALSE) { UT_DoAreaTransition(MY_AR_NIGHT, MY_WP_BED); }
                            else { KillCreature(oBody); }
                        }
                        break;
                    }
                    case EVENT_TYPE_ENTER:
                    {
                        Wake();
                        UT_TeamGoesHostile(MY_TEAM);
                        UT_ExitDestroy(oBody, TRUE, "exit_wp");
                        break;
                    }
                }
            }
        """
        consts = {"MY_CR_MUM": "mum", "MY_AR_NIGHT": "night_area", "MY_WP_BED": "bed_wp", "MY_TEAM": 7}
        t = plotlogic.translate_events(script, self.PLOTS, consts, "my_area")
        acts = {k: [(a["kind"], a["target"], a["arg"], a["value"]) for a in v] for k, v in t["cases"].items()}
        self.assertEqual(acts["load:my_area"], [(12, "cook", "", 1), (12, "scribe", "", 1),
                                                (13, "bed_wp", "night_area", 1)])
        self.assertEqual(acts["enter:my_area"], [(3, "mum", "", 1), (10, "team:7", "", 1),
                                                 (11, "scribe", "exit_wp", 1)])

    def test_defined_flags(self):
        script = """
            void main()
            {
                if (nType == EVENT_TYPE_SET_PLOT) { switch (nFlag) { } }
                else
                {
                    switch (nFlag)
                    {
                        case NIGHT_NOT_PRELUDE:
                        {
                            int nA = WR_GetPlotFlag(PLT_MY_MAIN, BATTLE);
                            int nB = WR_GetPlotFlag(PLT_MY_MAIN, PRELUDE);
                            if ((nA == TRUE) && (nB == FALSE)) { nResult = TRUE; }
                            break;
                        }
                        case EITHER:
                        {
                            if (WR_GetPlotFlag(PLT_MY_MAIN, BATTLE) || WR_GetPlotFlag(PLT_MY_MAIN, PRELUDE))
                            { nResult = TRUE; }
                            break;
                        }
                        case HURT:
                        {
                            if (GetInjuries(oPC) > 0) { nResult = TRUE; }
                            break;
                        }
                    }
                }
            }
        """
        plot = {"guid": "BBBB", "name": "my_defined", "flags": {256: "NIGHT_NOT_PRELUDE", 257: "EITHER", 258: "HURT"}}
        d = plotlogic.translate_defined(script, plot, self.PLOTS)
        self.assertEqual(d["NIGHT_NOT_PRELUDE"], [[("AAAA:0", False), ("AAAA:1", True)]])
        self.assertEqual(sorted(map(sorted, d["EITHER"])), [[("AAAA:0", False)], [("AAAA:1", False)]])
        self.assertNotIn("HURT", d)

    def test_triggers(self):
        are = {"TriggerList": [
            {"Tag": "t_talk", "TemplateResRef": "t_talk", "XPosition": 1.0, "YPosition": 2.0, "ZPosition": 0.0,
             "XOrientation": 0, "YOrientation": 0, "ZOrientation": 0, "WOrientation": 1,
             "Geometry": [{"XPoint": -1.0, "YPoint": -1.0, "ZPoint": 0.0}, {"XPoint": 2.0, "YPoint": 1.0, "ZPoint": 0.0}]},
            {"Tag": "t_script", "TemplateResRef": "t_script", "XPosition": 0.0, "YPosition": 0.0, "ZPosition": 0.0,
             "XOrientation": 0, "YOrientation": 0, "ZOrientation": 0, "WOrientation": 1,
             "Geometry": [{"XPoint": 0.0, "YPoint": 0.0, "ZPoint": 0.0}, {"XPoint": 1.0, "YPoint": 1.0, "ZPoint": 0.0}]},
            {"Tag": "", "Type": 3, "XPosition": 0.0}]}
        templates = {"t_talk": {"EventScript": "gen00tr_talk", "VarTable": [
                         {"Name": "TRIG_TALK_SPEAKER", "Value": "mum"},
                         {"Name": "TRIG_TALK_ACTIVE_FOR_PLOT", "Value": "AAAA"},
                         {"Name": "TRIG_TALK_ACTIVE_FOR_FLAG", "Value": 0},
                         {"Name": "TRIG_TALK_SET_PLOT", "Value": "NONE"},
                         {"Name": "TRIG_TALK_SET_FLAG", "Value": -1}]},
                     "t_script": {"EventScript": "my_trigger"}}
        t = area.triggers(are, templates)
        self.assertEqual(t["TriggerTags"], ["t_talk", "t_script"])
        self.assertEqual(t["TriggerBox"][:6], [0.0, -300.0, -50.0, 300.0, -100.0, 300.0])
        self.assertEqual(t["TriggerKey"], ["", "enter:my_trigger"])
        self.assertEqual(t["TriggerTalk"][:6], ["mum", "AAAA:0", "", "", "", ""])


class ToolsetTests(unittest.TestCase):
    def test_parse_dump(self):
        m = toolset.MARK
        dump = (f"{m}bhn_plot|\\Plots\\|12\nvoid main()\n{{\n    // old\n}}\n"
                f"{m}bhn_plot|\\Plots\\|40\nvoid main()\n{{\n}}\n"
                f"{m}core_h||3\nconst int X = 1;\n")
        scripts = toolset.parse(dump)
        self.assertEqual(sorted(scripts), ["bhn_plot", "core_h"])
        self.assertEqual((scripts["bhn_plot"]["version"], scripts["bhn_plot"]["folder"]), (40, "\\Plots\\"))
        self.assertEqual(scripts["bhn_plot"]["text"], "void main()\n{\n}\n")
        self.assertEqual(scripts["core_h"]["text"], "const int X = 1;\n")
        self.assertIn("LIKE 'bhn%'", toolset.query("bhn*"))
        self.assertIn("LIKE 'o''brien'", toolset.query("o'brien"))  # quotes are escaped


class PlotTests(unittest.TestCase):
    def test_read_and_lookup(self):
        gff = GFF4(build_plo("bhn000pt_talked_to", "4b60deda", {4: "BHN_TALKED_TO_FATHER", 256: "DEFINED"},
                             script="bhn000pt_talked_to"))
        self.assertTrue(plo.is_plot(gff))
        [p] = plo.read(gff)
        self.assertEqual(p, {"guid": "4B60DEDA", "name": "bhn000pt_talked_to", "script": "bhn000pt_talked_to",
                             "flags": {4: "BHN_TALKED_TO_FATHER", 256: "DEFINED"}})
        plots = {p["guid"]: p}
        self.assertEqual(plo.flag_name(plots, "4b60deda:4"), "BHN_TALKED_TO_FATHER")
        self.assertEqual(plo.flag_name(plots, "4B60DEDA:5"), "")
        self.assertEqual(plo.flag_key(plots, "DEFINED"), "4B60DEDA:256")
        with self.assertRaises(ValueError):
            plo.flag_key(plots, "NOPE")

    def test_not_a_plot(self):
        with self.assertRaises(plo.PLOError):
            plo.read(GFF4(build_tlk_v02({1: "x"})))

    def test_cli_names_true_flags(self):
        conv = {"conversation": "c", "starts": [0], "lines": [
            {"index": 0, "kind": "npc", "text": "Hi", "speaker": "OWNER", "children": [],
             "condition": {"plot": "BBBB", "flag": 260}}]}
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "plt_gen.plo").write_bytes(build_plo("gen", "BBBB", {260: "GEN_GENDER_MALE"}))
            (Path(d) / "c.dlg.conv.json").write_text(json.dumps(conv), encoding="utf-8")
            out = Path(d) / "out.json"
            self.assertEqual(main(["unreal", "conv", str(Path(d) / "c.dlg.conv.json"), "--plots", d,
                                   "--true-flag", "GEN_GENDER_MALE", "--out", str(out)]), 0)
            got = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(got["TrueFlags"], ["BBBB:260"])
            self.assertEqual(got["FlagNames"], {"BBBB:260": "GEN_GENDER_MALE"})
            self.assertEqual(main(["unreal", "conv", str(Path(d) / "c.dlg.conv.json"),
                                   "--true-flag", "GEN_GENDER_MALE", "--out", str(out)]), 1)
            self.assertEqual(main(["plo", "list", d, "--out", str(Path(d) / "plots.json")]), 0)
            listed = json.loads((Path(d) / "plots.json").read_text(encoding="utf-8"))
            self.assertEqual(listed["BBBB"]["flags"], {"260": "GEN_GENDER_MALE"})


class PlotLogicTests(unittest.TestCase):
    # Made-up script in the shape of a plot script, not game text.
    SCRIPT = """
        #include "my_constants_h"
        int StartingConditional()
        {
            object oGuard = UT_GetNearestCreatureByTag(oPC, MY_CR_GUARD);  // a creature
            if (nType == EVENT_TYPE_SET_PLOT)
            {
                switch(nFlag)
                {
                    case GUARD_MOVES:
                    {
                        UT_LocalJump(oGuard, MY_WP_GATE);
                        WR_SetPlotFlag(PLT_OTHER, OTHER_DONE, TRUE);
                        object oGate = GetObjectByTag("my_door_gate");
                        SetPlaceableActionResult(oGate, PLACEABLE_ACTION_UNLOCK, TRUE);
                        SetPlaceableState(oGate, PLC_STATE_DOOR_OPEN_2);
                        break;
                    }
                    case GUARD_WALKS:
                    {
                        object oPost = UT_GetNearestObjectByTag(oPC, MY_WP_GATE);
                        location lPost = GetLocation(oPost);
                        command cMove = CommandMoveToLocation(lPost, bHurry);
                        AddCommand(oGuard, cMove, TRUE);
                        WR_AddCommand(oGuard, CommandMoveToObject(oPost, TRUE));
                        UT_QuickMoveObject(oGuard, "my_wp_far", TRUE);
                        UT_TeamAppears(MY_TEAM_RATS);
                        UT_TeamMove(MY_TEAM_RATS, MY_WP_GATE, TRUE);
                        UT_TeamAppears(MY_TEAM_RATS, FALSE, OBJECT_TYPE_PLACEABLE);
                        break;
                    }
                    case GUARD_TALKS:
                        UT_Talk(oGuard, oPC);
                    case GUARD_LEAVES:
                        WR_SetObjectActive(oGuard, FALSE);
                        SetCreatureGoreLevel(oGuard, 0.5);
                        DoAutoSave();
                        break;
                }
            }
            return nResult;
        }
    """

    def test_translate_and_export(self):
        plots = {"AAAA": {"guid": "AAAA", "name": "my_plot", "script": "my_plot",
                          "flags": {0: "GUARD_MOVES", 1: "GUARD_TALKS", 2: "GUARD_LEAVES", 3: "GUARD_WALKS"}},
                 "BBBB": {"guid": "BBBB", "name": "other", "script": "", "flags": {7: "OTHER_DONE"}}}
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "my_plot.nss").write_text(self.SCRIPT, encoding="utf-8")
            (Path(d) / "my_constants_h.nss").write_text(
                'const string MY_CR_GUARD = "my_cr_guard";\nconst string MY_WP_GATE = "my_wp_gate";\n'
                'const int MY_TEAM_RATS = 7;\n',
                encoding="utf-8")
            out = plotlogic.export(d, plots)
        report = out["Plots"]["my_plot"]
        self.assertEqual(report["Cases"], {
            "GUARD_MOVES": ["jump my_cr_guard my_wp_gate 1", "setflag  BBBB:7 1",
                            "door my_door_gate unlock 1", "door my_door_gate open2 1"],
            "GUARD_TALKS": ["talk my_cr_guard  1", "active my_cr_guard  0", "autosave   1"],  # falls through
            "GUARD_WALKS": ["walk my_cr_guard my_wp_gate 0",  # the run flag is only known at runtime
                            "walk my_cr_guard my_wp_gate 1", "walk my_cr_guard my_wp_far 1",
                            "active team:7  1", "walk team:7 my_wp_gate 1"],
            "GUARD_LEAVES": ["active my_cr_guard  0", "autosave   1"]})
        self.assertEqual(report["Skipped"], ["GUARD_WALKS: UT_TeamAppears: OBJECT_TYPE_PLACEABLE teams",
                                             "GUARD_LEAVES: SetCreatureGoreLevel"])
        self.assertEqual(out["Keys"], ["AAAA:0", "AAAA:3", "AAAA:1", "AAAA:2"])
        self.assertEqual((out["Start"], out["Count"]), ([0, 4, 9, 12], [4, 5, 3, 2]))
        self.assertEqual(out["Kind"], [1, 4, 7, 7, 6, 6, 6, 3, 6, 2, 3, 5, 3, 5])
        self.assertEqual(out["Arg"][:2], ["my_wp_gate", "BBBB:7"])
        self.assertEqual((out["Value"][4], out["Value"][10]), (0, 0))
        self.assertEqual((out["Target"][7:9], out["Arg"][8]), (["team:7", "team:7"], "my_wp_gate"))
        self.assertEqual(out["Arg"][4:7], ["my_wp_gate", "my_wp_gate", "my_wp_far"])


class PartyLogicTests(unittest.TestCase):
    # Made-up party plot in the shape of the game's, not game text.
    SCRIPT = """
        void main()
        {
            object oWolf = Party_GetFollowerByTag(MY_FL_WOLF);
            object oKnight = UT_GetNearestObjectByTag(GetHero(), MY_CR_KNIGHT);
            if (nType == EVENT_TYPE_SET_PLOT)
            {
                switch(nBitFlag)
                {
                    case WOLF_JOINS: SetFollowerRecruited(oWolf, nValue, strPlot, 1, 2, FALSE); break;
                    case WOLF_WAITS: Party_SetFollowerInCamp(oWolf, 2); break;
                    case KNIGHT_JOINS: UT_HireFollower(oKnight); break;
                    case KNIGHT_LEAVES: UT_FireFollower(oKnight, TRUE, FALSE); break;
                }
            }
        }
    """

    def test_join_and_leave(self):
        plot = {"guid": "CCCC", "name": "my_party", "script": "my_party",
                "flags": {0: "WOLF_JOINS", 1: "WOLF_WAITS", 2: "KNIGHT_JOINS", 3: "KNIGHT_LEAVES"}}
        consts = {"MY_FL_WOLF": "my_fl_wolf", "MY_CR_KNIGHT": "my_cr_knight"}
        t = plotlogic.translate(self.SCRIPT, plot, {}, consts)
        self.assertEqual({k: [(a["kind"], a["target"], a["value"]) for a in v] for k, v in t["cases"].items()},
                         {"WOLF_JOINS": [(8, "my_fl_wolf", 1)], "WOLF_WAITS": [(8, "my_fl_wolf", 0)],
                          "KNIGHT_JOINS": [(8, "my_cr_knight", 1)], "KNIGHT_LEAVES": [(8, "my_cr_knight", 0)]})
        self.assertTrue(plotlogic._matches("gen00pt_party", "bhn*, gen00pt_party"))


class EventLogicTests(unittest.TestCase):
    # Made-up creature and area scripts in the shape of the game's, not game text.
    CREATURE = """
        void main()
        {
            switch (nEventType)
            {
                case EVENT_TYPE_DEATH:
                {
                    object oNext = UT_GetNearestCreatureByTag(oPC, MY_CR_WOLF_2);
                    string sTag = GetTag(OBJECT_SELF);
                    if (sTag == MY_CR_WOLF_1)
                    {
                        WR_SetObjectActive(oNext, TRUE);
                    }
                    else if (sTag == MY_CR_WOLF_2)
                    {
                        WR_SetObjectActive(arPack[i], TRUE);
                    }
                    break;
                }
            }
        }
    """
    AREA = """
        void main()
        {
            object oGate = GetObjectByTag("my_door_gate");
            switch (nEventType)
            {
                case EVENT_TYPE_TEAM_DESTROYED:
                {
                    int nTeamID = GetEventInteger(ev, 0);
                    switch (nTeamID)
                    {
                        case MY_TEAM_WOLVES:
                        {
                            SetPlaceableActionResult(oGate, PLACEABLE_ACTION_UNLOCK, TRUE);
                            PlaySomeMusic();
                            break;
                        }
                    }
                }
            }
        }
    """

    def test_death_and_team_destroyed(self):
        consts = {"MY_CR_WOLF_1": "my_cr_wolf_1", "MY_CR_WOLF_2": "my_cr_wolf_2", "MY_TEAM_WOLVES": 4}
        death = plotlogic.translate_events(self.CREATURE, {}, consts)
        self.assertEqual(death["cases"], {
            "death:my_cr_wolf_1": [{"kind": 3, "target": "my_cr_wolf_2", "arg": "", "value": 1}],
            "death:my_cr_wolf_2": []})
        self.assertEqual(death["skipped"], ["death:my_cr_wolf_2: WR_SetObjectActive(arPack[i]): "
                                            "object only known at runtime"])
        team = plotlogic.translate_events(self.AREA, {}, consts)
        self.assertEqual(team["cases"], {"teamdead:4": [{"kind": 7, "target": "my_door_gate", "arg": "unlock",
                                                         "value": 1}]})
        self.assertEqual(team["skipped"], ["teamdead:4: PlaySomeMusic"])


class CLITests(unittest.TestCase):
    def test_scan_find_pull(self):
        with tempfile.TemporaryDirectory() as d:
            game = Path(d) / "game"
            (game / "packages" / "core" / "data").mkdir(parents=True)
            (game / "packages" / "core" / "data" / "conversations.erf").write_bytes(build_erf({
                "bhn100cr_father.dlg": build_cnv(ConversationTests.lines, [0]),
                "orz_other.dlg": build_cnv(ConversationTests.lines, [0]),
                "bhn100cr_father.utc": build_gff3("UTC ", {"Tag": (10, "bhn100cr_father")}),
            }))
            (game / "packages" / "core" / "data" / "core_en-us.tlk").write_bytes(
                build_tlk_v02({100: "Ah, Rendon.", 101: "Father?"}))
            out = Path(d) / "out"

            self.assertEqual(main(["scan", str(game), "--out", str(out / "scan.json")]), 0)
            report = json.loads((out / "scan.json").read_text(encoding="utf-8"))
            self.assertEqual(report["archives"][0]["by_extension"], {"dlg": 2, "utc": 1})
            self.assertEqual(len(report["talk_tables"]), 1)

            self.assertEqual(main(["pull", str(game), "bhn*", "--out", str(out / "hn")]), 0)
            self.assertTrue((out / "hn" / "raw" / "conversations" / "bhn100cr_father.dlg").exists())
            self.assertFalse((out / "hn" / "raw" / "conversations" / "orz_other.dlg").exists())
            conv_dir = out / "hn" / "json" / "conversations"
            script = (conv_dir / "bhn100cr_father.dlg.txt").read_text(encoding="utf-8")
            self.assertIn("bryce: Ah, Rendon.", script)
            dump = json.loads((conv_dir / "bhn100cr_father.dlg.json").read_text(encoding="utf-8"))
            self.assertEqual(dump["format"], "V4.0 PC DLG V0.2")
            first_text = dump["root"]["conv_line_list"][0]["conv_line_text"]
            self.assertEqual(first_text, {"strref": 100, "text": "Ah, Rendon."})
            summary = json.loads((out / "hn" / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["formats"], {"dlg: GFF V4.0 DLG V0.2": 1, "utc: GFF3 UTC V3.2": 1})
            utc = json.loads((conv_dir / "bhn100cr_father.utc.json").read_text(encoding="utf-8"))
            self.assertEqual(utc["root"]["Tag"], "bhn100cr_father")

            runtime = out / "ue" / "bhn100cr_father.json"
            self.assertEqual(main(["unreal", "conv", str(conv_dir / "bhn100cr_father.dlg.conv.json"),
                                   "--names", str(out / "hn" / "json"), "--true-flag", "X:1",
                                   "--out", str(runtime)]), 0)
            runtime = json.loads(runtime.read_text(encoding="utf-8"))
            self.assertEqual(runtime["Lines"][0]["Text"], "Ah, Rendon.")
            self.assertEqual(runtime["TrueFlags"], ["X:1"])


if __name__ == "__main__":
    unittest.main()
