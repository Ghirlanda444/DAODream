import json
import math
import random
import struct
import tempfile
import unittest
from pathlib import Path

from daotools import abilities, ambient, area, balance, cnv, cutscene, fields as F, fsb, kit, mfdecode, plo, plotlogic, simulate, stats, tactics, threat, toolset, unreal
from daotools.cli import main
from daotools.erf import ERF, ERFError, is_erf
from daotools.gda import GDA, column_hash
from daotools.gff4 import (GFF4, T_FLOAT32, T_SINT16, T_UINT8, T_UINT32, T_UINT64, T_VECTOR3F, TlkString,
                           to_jsonable)
from daotools.tlk import TalkTable, TalkTables

from builders import (GFF4Writer, Tmpl, build_cnv, build_cut, build_erf, build_fsb, build_gda, build_gff3,
                      build_plo, build_tlk_v02, build_tlk_v05)
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


class BalanceTests(unittest.TestCase):
    # A made-up ability table and a mod's override of it, in the game's layout (not game data).
    COLUMNS = [("ID", "int"), ("label", "string"), ("Namestrref", "int"), ("DescStrRef", "int"), ("Cost", "float"),
               ("Cooldown", "float")]

    def test_changes_against_the_game(self):
        with tempfile.TemporaryDirectory() as d:
            game, mod, src = Path(d) / "game", Path(d) / "mod", Path(d) / "src"
            for p in (game, mod, src):
                p.mkdir()
            (game / "abi_base.gda").write_bytes(build_gda(self.COLUMNS, [
                [1, "MY_STRIKE", 10, 11, 40.0, 60.0], [2, "MY_GUARD", 12, 13, 20.0, 30.0]]))
            (mod / "abi_base_ao.gda").write_bytes(build_gda(self.COLUMNS, [
                [1, "MY_STRIKE", 10, 900, 30.0, 45.0], [2, "MY_GUARD", 12, 13, 20.0, 30.0],
                [3, "MY_NEW", 901, 902, 10.0, 5.0]]))
            (src / "my_rules.nss").write_text('float f = GetM2DAFloat(TABLE_ABILITIES_TALENTS, "Cooldown", nId);')
            talk = TalkTable(GFF4(build_tlk_v02({900: "Strikes harder.", 901: "New", 902: "Something new."})))
            names = balance.script_column_names(src)
            out = balance.export(game, mod, names, talk, source="My Mod 1.0")
        self.assertIn("Cooldown", names)
        t = out["Tables"]["abi_base"]
        self.assertEqual(t["Changed"], {1: {"DescStrRef": [11, 900], "Cost": [40.0, 30.0], "Cooldown": [60.0, 45.0]}})
        self.assertEqual(list(t["New"]), [3])
        self.assertEqual(out["Text"]["abi_base"], {1: {"Desc": "Strikes harder."}, 3: {"Name": "New", "Desc": "Something new."}})
        self.assertEqual((out["Format"], out["Source"]), (balance.FORMAT, "My Mod 1.0"))


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
             "condition": {"plot": "BBBB", "flag": 260}, "extra": {"conv_line_visibility": 1}},
            {"index": 2, "kind": "player", "text": "Not now.", "speaker": "PLAYER", "children": [0],
             "condition": {"plot": "BBBB", "flag": 2, "test": 0},
             "action": {"script": "bhn_plot", "parameter": 1}},
            {"index": 3, "kind": "npc", "text": "Indeed.", "speaker": "bhn_howe", "children": [],
             "condition": {"plot": "CCCC", "flag": 1, "test": 7}, "action": {"plot": "AAAA", "flag": 4, "test": 0},
             "extra": {"conv_line_visibility": 2}},
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
        # Show once: per conversation (1), per game (2), always (0, also when absent).
        self.assertEqual([l["Show"] for l in out["Lines"]], [0, 1, 0, 2, 0])
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
                {"index": 0, "kind": "npc", "strref": 26080, "text": text, "speaker": "OWNER", "children": [1]},
                {"index": 1, "kind": "npc", "text": "(Bark)", "speaker": "a_dog", "children": []}]}
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
            dog = Path(d) / "dog"  # a speaker pulled on its own
            dog.mkdir()
            (dog / "a_dog.utc.json").write_text(json.dumps({"root": {"Tag": "a_dog", "LocName": {"text": "Dog"}}}),
                                                encoding="utf-8")
            out = Path(d) / "ue"
            self.assertEqual(main(["unreal", "origin", str(pull), "--no-vo", "--names", str(dog),
                                   "--out", str(out)]), 0)
            rt = json.loads((out / "conversations" / "bhn_guard.json").read_text(encoding="utf-8"))
            index = json.loads((out / "conversations" / "index.json").read_text(encoding="utf-8"))
        self.assertEqual(rt["Lines"][0]["Text"], "Halt!")  # the patch copy wins
        self.assertEqual((rt["Owner"], rt["SpeakerNames"]["OWNER"], rt["Lines"][0]["Vo"]),
                         ("bhn_guard_2", "Guard", "26080_m"))
        self.assertEqual(rt["SpeakerNames"]["a_dog"], "Dog")
        entry = index["Conversations"]["bhn_guard"]
        self.assertEqual((entry["UsedBy"], entry["Source"], entry["SpokenLines"], entry["VoicedLines"]),
                         (["bhn_guard_2", "bhn_guard_amb"], "patch002", 2, 1))
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
        boxes = area.floor_plan(self.nav, fill=0)
        rows = [boxes[i:i + 7] for i in range(0, len(boxes), 7)]
        floors = sorted(r for r in rows if r[6] == 0)
        # The 2 x 2 floor merges into one box; Y is flipped, so y 20..22 m becomes -2200..-2000 cm.
        self.assertEqual(floors, [[1000.0, -2200.0, -20.0, 1200.0, -2000.0, 0.0, 0],
                                  [1200.0, -2200.0, 80.0, 1300.0, -2100.0, 100.0, 0]])
        walls = [r for r in rows if r[6] == 1]
        self.assertTrue(walls)
        self.assertTrue(all(r[5] >= 300.0 for r in walls))  # 3 m above the floor beside them

    def test_floor_fills_blocked_cells(self):
        # One ring: the blocked cells beside the floor get the lowest neighbouring height,
        # so the corner cell (3, 2), two steps away, stays open.
        filled = area._filled_floor(self.nav, fill=1)
        self.assertEqual(filled, [0, 0, 0, None, 0, 0, 16, 16, 0, 0, 16, None])
        self.assertEqual(area._filled_floor(self.nav)[11], 16)  # the default reaches it

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
                                    "Race": 3, "Appearance Data": {"Gender": 1, "HeadMorph": "hm_bhn100_father.mor"}},
                     "bhn_rat": {"DialogResRef": "", "VarTable": [{"Name": "CREATURE_SPAWN_DEAD", "Value": 1}]},
                     "bhn_rat_giant": {"DialogResRef": "", "Race": 5, "Rank": 1, "GroupId": 1,
                                       "LocName": {"strref": 3, "text": "Giant Rat"}}}
        out = area.area(are, {"3020": {"3110": self.nav}}, templates, start="start")
        # Every creature, the rat without a team or conversation too (plots may move or kill it).
        self.assertEqual((out["NpcTags"], out["NpcNames"], out["NpcConversations"], out["NpcFemale"]),
                         (["bryce", "rat", "late", "larder_rat"], ["Bryce", "", "Bryce", "Giant Rat"],
                          ["bhn_father", "", "bhn_father", ""], [0, 0, 0, 0]))
        self.assertEqual(out["NpcPose"][:4], [1050.0, -2050.0, 0.0, -90.0])
        self.assertEqual(out["NpcActive"][2:], [0, 0])  # inactive ones are kept, hidden until a plot shows them
        self.assertEqual(out["NpcDead"], [0, 1, 0, 0])  # a body: its template spawns it dead
        self.assertEqual((out["NpcTeam"][2:], out["NpcScale"][2:]), ([-1, 1], [1.0, 0.35]))
        self.assertEqual((out["NpcHostile"][2:], out["NpcRank"][2:]), ([0, 1], [0, 1]))
        self.assertEqual((out["Summary"]["TalkingCreatures"], out["Summary"]["TeamOnly"]), (2, 1))
        self.assertEqual((out["WaypointTags"], out["WaypointPose"]), (["start"], [1100.0, -2100.0, 0.0, -90.0]))
        self.assertEqual(out["Summary"]["OtherCreatures"], 1)
        # Looks: the head morph names the character in any module; adult humans also get a crowd face, and the
        # giant rat its own look.
        self.assertEqual(out["NpcMorph"], ["hm_bhn100_father", "", "hm_bhn100_father", ""])
        self.assertEqual([k[:8] for k in out["NpcCrowd"]], ["crowd_m_", "crowd_m_", "crowd_m_", "giant_ra"])
        self.assertEqual(out["NpcCrowd"][0], area.look_keys({}, 3, "bryce@10,20")[1])
        # Crowd variety: per creature, stable for its key; the giant rat gets its coat instead.
        self.assertEqual(len(out["NpcVariety"]), area.VARIETY * 4)
        rgb, mottle, bare = area.BEAST_COATS["giant_rat"]
        self.assertEqual(out["NpcVariety"][area.VARIETY * 3:], [*rgb, mottle, bare] + [0.0] * (area.VARIETY - 5))
        v = area.variety("guard@1,2", "cth_com_c00")
        self.assertEqual(v, area.variety("guard@1,2", "cth_com_c00"))
        for k in range(3):  # skin between fair and light brown
            self.assertTrue(area.SKIN_TAN[k] <= v[k] <= area.SKIN_FAIR[k])
        self.assertTrue(all(x > 0 for x in v[5:]))  # servants' clothes are dyed
        self.assertEqual(area.variety("guard@1,2", "arm_cht_med_chn")[5:], [0.0] * 6)  # uniforms keep theirs
        # Mabari: the hero's dog is fawn, war dogs take an enemy coat, other creatures none.
        self.assertEqual(area.mabari_coat("gen00fl_dog", "gen00fl_dog@0,0"), "fawn")
        self.assertIn(area.mabari_coat("dog_mabari_2", "bhn200cr_howe_panicked4@5,6"), area.MABARI_ENEMY)
        self.assertEqual(area.mabari_coat("bhn_rat", "rat@0,0"), "")
        self.assertEqual(area.beast_look("bhn100cr_rat_giant"), "giant_rat")
        self.assertEqual(area.beast_look("gen00fl_dog"), "")
        self.assertEqual(area.coat_variety("fawn")[:5], [0.36, 0.215, 0.10, 0.0, 0.0])
        # Children (kn_* heads) stand smaller, and get no crowd face.
        self.assertEqual(area.stand_in_scale(3, 0, "kn_bhn100_oren"), area.CHILD_SCALE)
        self.assertEqual(area.look_keys({"HeadMorph": "kn_bhn100_oren.mor"}, 3, "oren@0,0"), ("kn_bhn100_oren", ""))
        # Elves get elf crowd faces; animals none.
        self.assertTrue(area.look_keys({"HeadMorph": "ef_x.mor", "Gender": 2}, area.RACE_ELF, "maid@0,0")[1].startswith("crowd_elf_f_"))
        self.assertEqual(area.look_keys({"HeadMorph": "", "Gender": 1}, area.RACE_ANIMAL, "rat@0,0")[1], "")
        # Only doors, with their state (1 = locked) and a small door's greybox size.
        self.assertEqual((out["DoorTags"], out["DoorPose"], out["DoorState"], out["DoorSize"], out["DoorActive"]),
                         (["bhn_door_cellar"], [1200.0, -2000.0, 0.0, -90.0], [1], [160.0, 260.0], [1]))
        self.assertEqual((out["Start"], out["Labels"], out["LabelPos"]),
                         ([1100.0, -2100.0, 0.0, -90.0], ["Main Hall"], [1100.0, -2100.0, 0.0]))
        self.assertEqual(out["Summary"]["Floors"], 3)  # blocked cells filled in: three rectangles at 0 m and 1 m
        self.assertEqual(out["Warnings"], [])


class KitTests(unittest.TestCase):
    # A made-up kit piece: one 4 m x 0.4 m x 5 m box standing on the model origin.
    WALL_PHY = {"_struct": "mdlh", "6999": [{"_struct": "node", "6999": [{"_struct": "cobj", "6999": [
        {"_struct": "shap", "6058": 2, "6060": [0.0, 0.0, 0.0, 1.0], "6061": [0.0, 0.0, 2.5, 1.0],
         "6998": {"_struct": "boxs", "6071": [2.0, 0.2, 2.5]}}]}]}]}
    BLOCK_MMH = {"_struct": "mdlh", "6999": [{"_struct": "node", "6999": [
        {"_struct": "bbox", "6054": [-1.0, -0.5, 0.0, 1.0], "6055": [1.0, 0.5, 3.0, 1.0]}]}]}

    def test_soften_fills(self):
        # A cool fill keeps 30% of its tint, turned toward warm white at the same brightness; a lamp is untouched.
        lights = [0, 0, 0, 600, 0.2, 0.26, 0.29, 0, 0, 0, 600, 1.2, 0.7, 0.3]
        out, n = area.soften_fills(lights, 0.3)
        self.assertEqual(n, 1)
        self.assertEqual(out[7:], lights[7:])
        r, g, b = out[4:7]
        self.assertAlmostEqual(max(r, g, b), 0.29, places=3)
        self.assertGreater(r, b)  # now warmer than it is blue

    def test_kit_meshes(self):
        # A barrel (bbox 2 x 1 x 3 m, see BLOCK_MMH) turned 90 degrees, mapped to a mesh 100 x 100 x 150 cm
        # whose pivot is its base: fitted to the piece's height, its base on the piece's bottom.
        q90 = [0.0, 0.0, math.sqrt(0.5), math.sqrt(0.5)]
        room = {"4": [0.0, 0.0, 0.0], "5": [0.0, 0.0, 0.0, 1.0], "3050": [
            {"3063": "prp_barrel01_0", "4": [1.0, 2.0, 0.0], "5": q90, "3059": 1.0},
            {"3063": "prp_chair_0", "4": [0.0, 0.0, 0.0], "5": [0.0, 0.0, 0.0, 1.0]}]}
        pieces = {"prp_barrel01_0": (None, self.BLOCK_MMH), "prp_chair_0": (None, self.BLOCK_MMH)}
        kit_map = {"meshes": {"Barrel": {"path": "/Game/X/SM_Barrel", "bounds": [0, 0, 75, 50, 50, 75]},
                              "Chair": {"path": "/Game/X/SM_Chair", "bounds": [0, 0, 75, 50, 50, 75]}},
                   "pieces": [{"match": "prp_barrel*", "mesh": "Barrel"},
                              {"match": "prp_chair*", "mesh": "Chair", "fit": "stretch"}]}
        out = kit.kit_meshes([room], pieces, kit_map, has_mesh=lambda p: p.endswith("Barrel"))
        self.assertEqual(out["KitMeshes"], ["/Game/X/SM_Barrel.SM_Barrel"])
        self.assertEqual(out["Mapped"], {"prp_barrel01_0"})  # the chair's mesh is missing: it stays a box
        p = out["KitPlaced"]
        self.assertEqual(p[:3], [100.0, -200.0, 0.0])  # base on the floor, Y mirrored for Unreal
        self.assertEqual(p[3:6], [2.0, 2.0, 2.0])  # 3 m tall piece / 1.5 m mesh
        self.assertEqual([round(v, 3) for v in p[6:9]], [0.0, -1.0, 0.0])  # +90 in the game is -90 in Unreal
        self.assertEqual(p[12], 0)
        stretched = kit.kit_meshes([room], pieces, kit_map)["KitPlaced"][13:]
        self.assertEqual(stretched[3:6], [2.0, 1.0, 2.0])  # 2 x 1 x 3 m from a 1 x 1 x 1.5 m mesh
        self.assertEqual(kit.solids([room], pieces | {"blk": (None, None)}, skip={"prp_barrel01_0"})["Summary"]["Props"], 1)

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

    def test_ceilings(self):
        # A vault piece (bounding box 4 x 4 x 4 m, 5.4 m up) and a vault's end arch, a flat sheet.
        vault = {"_struct": "mdlh", "6999": [{"_struct": "node", "6999": [
            {"_struct": "bbox", "6054": [-2.0, -2.0, 5.4, 1.0], "6055": [2.0, 2.0, 9.4, 1.0]}]}]}
        arch = {"_struct": "mdlh", "6999": [{"_struct": "node", "6999": [
            {"_struct": "bbox", "6054": [1.5, -2.0, 5.6, 1.0], "6055": [1.5, 2.0, 9.4, 1.0]}]}]}
        room = {"4": [0.0, 0.0, 0.0], "5": [0.0, 0.0, 0.0, 1.0], "3050": [
            {"3063": "FCA_Ceiling01_0", "4": [10.0, 20.0, 0.0], "5": [0.0, 0.0, 0.0, 1.0]},
            {"3063": "FCA_Ceiling05_0", "4": [10.0, 20.0, 0.0], "5": [0.0, 0.0, 0.0, 1.0]},
            {"3063": "FCA_CorrTop01_0", "4": [0.0, 0.0, 0.0], "5": [0.0, 0.0, 0.0, 1.0]}]}
        out = kit.solids([room], {"fca_ceiling01_0": (None, vault), "fca_ceiling05_0": (None, arch)})
        self.assertEqual((out["Summary"]["Ceilings"], out["Summary"]["NoCollision"]), (2, 1))
        boxes = [out["Solids"][i:i + 13] for i in range(0, len(out["Solids"]), 13)]
        self.assertEqual(boxes[0][:6], [1000.0, -2000.0, 740.0, 200.0, 200.0, 200.0])
        self.assertEqual(boxes[1][:6], [1150.0, -2000.0, 750.0, 10.0, 200.0, 190.0])  # sheet: 20 cm thick
        self.assertEqual({b[12] for b in boxes}, {kit.CEILING})
        # Ceilings are neither cut by doors nor dropped as hanging props.
        self.assertEqual(area.drop_hanging(out["Solids"], AreaTests.nav), (out["Solids"], 0))
        self.assertEqual(area.cut_doorways(out["Solids"], [([1000.0, -2000.0, 600.0], 80.0)])[1], 0)

    def test_lights(self):
        # A room light model with a lamp 1 m to its +X, 2 m up, and a level-wide sun stand-in.
        mmh = {"format": "V4.0 PC MMH V0.1", "root": {"_struct": "mdlh", "6999": [{"_struct": "node", "6999": [
            {"_struct": "nplt", "6000": "lamp_001_RT", "6007": [1.8, 0.96, 0.3, 1.0], "6008": 6.0,
             "6999": [{"_struct": "trsl", "6047": [1.0, 0.0, 2.0, 1.0]}, {"_struct": "rota", "6048": [0, 0, 0, 1]}]},
            {"_struct": "nplt", "6000": "sun_fake", "6007": [1.0, 1.0, 1.0, 1.0], "6008": 2250.0,
             "6999": [{"_struct": "trsl", "6047": [0.0, 0.0, 500.0, 1.0]}]}]}]}}
        q90 = [0.0, 0.0, math.sqrt(0.5), math.sqrt(0.5)]  # 90 degrees about Z
        room = {"4": [10.0, 20.0, 0.0], "5": q90, "3050": [
            {"3063": "lay_10_ll", "4": [0.0, 0.0, 1.0], "5": [0.0, 0.0, 0.0, 1.0]},
            {"3063": "FCA_Wall01_0", "4": [0.0, 0.0, 0.0], "5": [0.0, 0.0, 0.0, 1.0]}]}
        # The room turns the lamp's +1 m X into +1 m Y: (10, 21, 3) m, Y flipped for Unreal.
        self.assertEqual(kit.lights([room], {"lay_10_ll": mmh}), [1000.0, -2100.0, 300.0, 600.0, 1.8, 0.96, 0.3])

    def test_fixtures(self):
        # A hanging lamp with its fire, a torch turned 90 degrees (its back, local +Y, now facing -X) and a hearth.
        q90 = [0.0, 0.0, math.sqrt(0.5), math.sqrt(0.5)]
        room = {"4": [10.0, 20.0, 0.0], "5": [0.0, 0.0, 0.0, 1.0], "3050": [
            {"3063": "prp_ferlamp_01_0", "4": [1.0, 0.0, 3.0], "5": [0.0, 0.0, 0.0, 1.0]},
            {"3063": "fxe_fire_small_p", "4": [1.0, 0.0, 3.03], "5": [0.0, 0.0, 0.0, 1.0]},
            {"3063": "prp_ferelden_torch_0", "4": [0.0, 2.0, 2.0], "5": q90},
            {"3063": "fxe_fire_l_ns_p", "4": [5.0, 0.0, 0.5], "5": [0.0, 0.0, 0.0, 1.0]},
            {"3063": "FCA_Wall01_0", "4": [0.0, 0.0, 0.0], "5": [0.0, 0.0, 0.0, 1.0]}]}
        out = kit.fixtures([room])
        self.assertEqual(out["Fixtures"], [1100.0, -2000.0, 300.0, 270.0, kit.HANGING_LAMP,
                                           1000.0, -2200.0, 200.0, 180.0, kit.TORCH])
        self.assertEqual(out["Fires"], [1100.0, -2000.0, 303.0, kit.SMALL_FIRE, 1500.0, -2000.0, 50.0, kit.LARGE_FIRE])

    def test_hang_fixtures(self):
        ceiling = [0.0, 0.0, 600.0, 600.0, 600.0, 50.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, kit.CEILING]   # bottom at 550
        lamps = [0.0, 0.0, 400.0, 0.0, kit.HANGING_LAMP,      # chain up to the ceiling
                 100.0, 0.0, 560.0, 0.0, kit.HANGING_LAMP,    # inside the slab: moved under it with its fire
                 0.0, 0.0, 300.0, 0.0, kit.WALL_LAMP,
                 2000.0, 0.0, 300.0, 0.0, kit.HANGING_LAMP]   # no ceiling: the full chain
        fires = [100.0, 0.0, 563.0, kit.SMALL_FIRE, 500.0, 0.0, 100.0, kit.LARGE_FIRE]
        out, fires = area.hang_fixtures(lamps, fires, ceiling)
        self.assertEqual([out[i + 5] for i in range(0, len(out), 6)], [150.0, 30.0, 0.0, area.CHAIN])
        self.assertEqual((out[8], fires[2], fires[6]), (520.0, 523.0, 100.0))

    def test_dim_candle_lights(self):
        candle_light = [0.0, 0.0, 140.0, 300.0, 1.62, 0.94, 0.18]   # 27 cm above the candle's flame
        torch = [500.0, 0.0, 200.0, 300.0, 1.62, 0.94, 0.18]
        fires = [0.0, 0.0, 113.0, kit.CANDLE_FIRE, 500.0, 0.0, 190.0, kit.SMALL_FIRE]
        out, dimmed = area.dim_candle_lights(candle_light + torch, fires)
        self.assertEqual((dimmed, out[4:7], out[11:14]), (1, [0.405, 0.235, 0.045], [1.62, 0.94, 0.18]))

    def test_lids(self):
        # A 10 x 10 m room of 5 m walls (and a pillar, looked past) around an 8 x 8 m floor.
        def wall(x, y, hx, hy, h=500.0):
            return [x, y, h / 2, hx, hy, h / 2, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, kit.WALL]
        room = wall(500, 0, 20, 500) + wall(-500, 0, 20, 500) + wall(0, 500, 500, 20) + wall(0, -500, 500, 20)
        pillar = wall(100, 100, 30, 30, 900.0)
        floor = [-400.0, -400.0, -20.0, 400.0, 400.0, 0.0, 0]
        out, n = area.lids(floor, room + pillar)
        boxes = [out[i:i + 13] for i in range(0, len(out), 13)]
        # Four 2 m columns, each one slab along Y at the walls' top, 50 cm wider all round.
        self.assertEqual(n, 4)
        self.assertEqual([b[:6] for b in boxes][0], [-300.0, 0.0, 515.0, 150.0, 450.0, 15.0])
        self.assertEqual({b[12] for b in boxes}, {kit.CEILING})
        # Under a kit ceiling that meets the walls, or with walls on two sides only
        # (outdoors), no lid; under one 3 m above the walls, a lid closes the gap.
        ceiling = [0.0, 0.0, 550.0, 600.0, 600.0, 50.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, kit.CEILING]
        self.assertEqual(area.lids(floor, room + ceiling)[1], 0)
        high = ceiling[:2] + [850.0] + ceiling[3:]
        self.assertEqual(area.lids(floor, room + high)[0][2], 515.0)
        self.assertEqual(area.lids(floor, wall(500, 0, 20, 500) + wall(-500, 0, 20, 500))[1], 0)

    def test_tuck_lights(self):
        ceiling = [0.0, 0.0, 600.0, 600.0, 600.0, 50.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, kit.CEILING]
        lamp = [0.0, 0.0, 580.0, 500.0, 1.8, 0.96, 0.3]  # inside the ceiling slab
        low = [100.0, 0.0, 300.0, 500.0, 1.8, 0.96, 0.3]
        upstairs = [0.0, 0.0, 1500.0, 500.0, 1.8, 0.96, 0.3]
        out, moved = area.tuck_lights(lamp + low + upstairs, ceiling)
        self.assertEqual((moved, out[2], out[9], out[16]), (1, 520.0, 300.0, 1500.0))

    def test_armed_ally(self):
        def utc(*refs, group=3):
            return {"GroupId": group, "Equip_ItemList": [{"TemplateResRef": r} for r in refs]}
        self.assertTrue(area.armed_ally(utc("gen_im_arm_cht_med_chn", "gen_im_wep_mel_lsw_lsw")))   # a guard
        self.assertFalse(area.armed_ally(utc("gen_im_cth_com_c00", "gen_im_wep_mel_dag_dag")))     # armed servant
        self.assertFalse(area.armed_ally(utc("gen_im_cth_nob_af0")))                               # a noble
        self.assertFalse(area.armed_ally(utc("gen_im_arm_cht_med_chn", "gen_im_wep_mel_lsw_lsw", group=1)))
        self.assertFalse(area.armed_ally({}))
        self.assertFalse(area.armed_ally(utc("gen_im_arm_cht_lgt_rlr", "gen_im_wep_mel_lsw_lsw"), "bhn200cr_howe_mother1"))

    def test_fill_lights(self):
        torch = [250.0, 250.0, 250.0, 600.0, 1.6, 0.9, 0.2]
        lit = [0.0, 0.0, 0.0, 500.0, 500.0, 0.0, 0]             # 5 x 5 m under the torch
        corridor = [3000.0, 0.0, 0.0, 4000.0, 300.0, 0.0, 0]    # 10 m of unlit corridor
        wall = [3000.0, 300.0, 0.0, 4000.0, 320.0, 300.0, 1]    # not floor: ignored
        fills = area.fill_lights(torch, lit + corridor + wall, 0.25)
        self.assertEqual(len(fills) // 7, 1)                    # the first sample gets a fill, which reaches the second...
        self.assertEqual(fills[:4], [3250.0, 150.0, 220.0, 900.0])
        self.assertEqual(fills[4:], [0.15, 0.175, 0.25])        # ...cool, at the asked brightness
        self.assertGreater(area.light_reach(fills, 3900.0, 150.0, 100.0), 0.0)
        self.assertEqual(area.fill_lights(torch, lit, 0.25), [])
        warm = area.fill_lights(torch, lit + corridor, 0.25, tint=area.WARM_FILL_COLOUR)
        self.assertEqual(warm[4:], [0.25, 0.2, 0.15])           # by day: warm instead

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
                         "BaseDefense": 40.0, "DamagePerLevel": 0.5, "BaseManaStamina": 50.0,
                         "DepletableProgression": 5.0, "StrAdjust": 2.0},
                     3: {"ID": 3, "label": "Sneak", "BaseHealth": 60.0, "BaseAttack": 50.0, "BaseDefense": 45.0,
                         "DexAdjust": 4.0, "IntAdjust": 7.0}},
        "race_base": {3: {"ID": 3, "StrAdjust": 1.0}},
        "itemstats": {2: {"ID": 2, "Damage": 6.0, "DamageRange": 1.5, "ArmorPenetration": 2.0,
                          "CritChanceModifier": 2.0, "AttributeMod": 1.0, "Attribute0": 1},
                      3: {"ID": 3, "Damage": 4.0, "DamageRange": 1.5, "AttributeMod": 0.85, "Attribute0": 1,
                          "Attribute1": 2}},
        "difficulty": {1: {"ID": 1, "DmgScalingThresh": 7.0}},
        "alwarrior_default": {1: {"ID": 1, "AttInit": 3}, 2: {"ID": 2, "AttInit": 1}},
    }

    def test_equipment(self):
        tables = {"itemstats": {10: {"ID": 10, "label": "Armor - Medium", "Armor": 4.25},
                                45: {"ID": 45, "label": "Helmet - Medium", "Armor": 1.0},
                                9: {"ID": 9, "label": "Armor - Light", "Armor": 3.0},
                                6: {"ID": 6, "label": "Shield - Kite", "Armor": 0.0, "Defense": 4.0, "MissileDeflection": 3.0},
                                2: {"ID": 2, "label": "Weapon - Longsword", "Damage": 6.0}},
                  "materialtypes": {1: {"ID": 1, "Armor": 1.0}, 8: {"ID": 8, "Armor": 1.25}, 60: {"ID": 60, "Armor": 0.0}}}
        items = {"chain": {"BaseItem": 10, "Material": 8}, "helm": {"BaseItem": 45, "Material": 1},
                 "hide": {"BaseItem": 9, "Material": 60}, "kite": {"BaseItem": 6, "Material": 79},
                 "sword": {"BaseItem": 2}}
        out = stats.equipment([{"TemplateResRef": r} for r in ("sword", "chain", "helm", "kite")], items, tables)
        self.assertEqual(out["Outfit"], {"chest": "chain", "helmet": "helm", "shield": "kite"})   # weapons are not worn
        self.assertEqual((out["Armour"], out["ShieldDefense"], out["MissileDeflection"]), (6.312, 4.0, 3.0))  # 4.25 x 1.25 + 1, rounded
        self.assertEqual(stats.equipment([{"TemplateResRef": "hide"}], items, tables)["Armour"], 3.0)  # no multiplier: x1

    def test_creature(self):
        # Rank 1 at area level 2 is level 3. Each level above 1 brings 0.5 x 3 + 5 = 6.5 points, the start 5;
        # STR weighs 1/3: 10 + (2 x 6.5 + 5) / 3 = 16, + 2 class = 18; DEX 1/6: 10 + 18 / 6 = 13; CON 1/3: 16.
        st = stats.stats(self.TABLES, package=5, rank=1, area_level=2)
        self.assertEqual((st["Level"], st["Attributes"]["Str"], st["Attributes"]["Dex"], st["Attributes"]["Con"]),
                         (3, 18.0, 13.0, 16.0))
        self.assertEqual(st["Health"], 80.0)  # (80 + 10 x 2 levels) x 0.5, + 5 x CON 6 above 10
        self.assertEqual(st["Stamina"], 30.0)  # (50 + 5 x 2 levels) x 0.5
        self.assertEqual((st["Attack"], st["Defense"]), (55.5, 43.0))  # + 0.5 x (STR 8 + DEX 3); + DEX 3
        # Unarmed 3-4.5, + strength (18 - 10) x 25-50% x 1.25; 0.5 per level (3 levels) after armour.
        self.assertEqual((st["Damage"], st["DamageBonus"]), ((5.5, 9.5), 1.5))
        self.assertEqual((st["Crit"], st["Penetration"], st["Flanking"]), (1.5, 0.0, 7.5))  # 3 x 0.5; half of 15
        self.assertEqual(stats.damage_after_scaling(7.88, st["DamageScale"], st["DamageThreshold"]), 3.94)
        self.assertEqual(stats.damage_after_scaling(5.44, st["DamageScale"], st["DamageThreshold"]), 5.44)

    def test_player_and_weapon(self):
        # The hero: 10 + race 1 + class 2 + the class's default 3 of the free points = STR 16; DEX 10 + 1.
        st = stats.stats(self.TABLES, package=0, rank=100, race=3, base_item=2, player_class=1, hero=True)
        self.assertEqual((st["Level"], st["Attributes"]["Str"], st["Attributes"]["Dex"], st["Health"], st["Attack"]),
                         (1, 16.0, 11.0, 80.0, 53.5))
        self.assertEqual((st["Damage"], st["DamageBonus"]), ((7.5, 12.0), 0.5))  # 6-9 + 6 x 25-50%
        self.assertEqual((st["Crit"], st["Penetration"]), (5.0, 2.0))  # 3 + the longsword's 2; its 2
        self.assertEqual(stats.hit_chance(50.0, 40.0), 64.0)
        self.assertEqual(stats.hit_chance(50.0, 40.0, flanking=7.5), 71.5)
        self.assertEqual(stats.weapon_base_item([{"TemplateResRef": "cap"}, {"TemplateResRef": "Sword"}],
                                                {"cap": {"BaseItem": 9}, "sword": {"BaseItem": 2}},
                                                self.TABLES["itemstats"]), 2)


    def test_one_shot(self):
        # A one-shot creature (a giant rat) is not scaled: 1 health, no attack or defense, its weapon's raw damage.
        st = stats.stats(self.TABLES, package=5, rank=1, area_level=2, base_item=2, one_shot=True)
        self.assertEqual((st["Level"], st["Health"], st["Attack"], st["Defense"], st["DamageBonus"]), (1, 1.0, 0.0, 0.0, 0.0))
        self.assertEqual((st["Damage"], st["Crit"], st["Penetration"]), ((6.0, 9.0), 2.0, 2.0))
        self.assertTrue(stats.is_one_shot(37, {"apr_base": {37: {"OneShotKills": 1}}}))
        self.assertFalse(stats.is_one_shot(35, {"apr_base": {35: {"OneShotKills": 0}}}))

    def test_weapon_material(self):
        # A grey iron weapon (materialtypes 41 -> tier 2): x1.1 damage, x1.15 armour penetration.
        tables = {k: dict(v) for k, v in self.TABLES.items()}
        tables["materialtypes"] = {41: {"ID": 41, "Material": 2}}
        tables["materialrules"] = {2: {"ID": 2, "Damage": 1.1, "ArmorPenetration": 1.15, "CritChanceModifier": 1.1}}
        st = stats.stats(tables, package=0, rank=100, race=3, base_item=2, player_class=1, hero=True, weapon_material=41)
        plain = stats.stats(tables, package=0, rank=100, race=3, base_item=2, player_class=1, hero=True)
        self.assertAlmostEqual(st["Damage"][0] - plain["Damage"][0], 0.6, places=2)  # 6 x 0.1
        self.assertAlmostEqual(st["Penetration"], 2.3, places=2)  # 2 x 1.15

    def test_follower(self):
        # Gilmore as the game rebuilds him on joining (checked against a save): level 2, 10 + race + class =
        # 15/14/10/11/11/13, then 5 + 3 points up to 14 + level x weight: STR +1 (target 16.4), DEX +2, WIL +5.
        weights = {1: {"AttWeight": 1.2}, 2: {"AttWeight": 1.0}, 3: {"AttWeight": 0.75}, 5: {"AttWeight": 0.25},
                   6: {"AttWeight": 1.0}}
        start = {"Str": 15.0, "Dex": 14.0, "Will": 10.0, "Mag": 11.0, "Int": 11.0, "Con": 13.0}
        self.assertEqual(stats.follower_attributes(start, 2, weights),
                         {"Str": 16.0, "Dex": 16.0, "Will": 15.0, "Mag": 11.0, "Int": 11.0, "Con": 13.0})

    def test_rogue_dagger(self):
        # A rogue: all of the flanking bonus; a dagger's bonus is the mean of STR and DEX above 10 x 0.85;
        # cunning 17 gives 1 armour penetration.
        st = stats.stats(self.TABLES, package=0, rank=100, base_item=3, player_class=3, hero=True)
        self.assertEqual((st["Flanking"], st["Penetration"], st["Defense"]), (15.0, 1.0, 49.0))
        self.assertEqual(st["Damage"], (4.42, 6.85))  # 4-6 + (0 + 4) / 2 x 25-50% x 0.85

    def test_hit_damage(self):
        # 10 rolled against armour 7 (4.9 fixed + 30% of 7 x the roll), penetration 2, bonus 1.
        self.assertAlmostEqual(stats.hit_damage(10.0, armour=7.0, armour_roll=1.0, penetration=2.0, bonus=1.0), 6.0)
        self.assertAlmostEqual(stats.hit_damage(10.0, armour=7.0, armour_roll=0.0, penetration=2.0, bonus=1.0), 8.1)
        self.assertAlmostEqual(stats.hit_damage(10.0, crit=True, armour=7.0, penetration=2.0), 10.0)  # 15 - 5
        self.assertEqual(stats.hit_damage(3.0, armour=7.0), 1.0)  # always at least 1
        self.assertEqual(stats.hit_damage(10.0, scale=0.5, threshold=7.0), 5.0)  # rank-scaled above the threshold

    def test_flanking(self):
        self.assertEqual(stats.flanking_bonus(180.0, 15.0), 15.0)  # right behind
        self.assertEqual(stats.flanking_bonus(150.0, 15.0), 7.5)   # halfway to the edge of 60 degrees
        self.assertEqual(stats.flanking_bonus(-150.0, 7.5), 3.75)
        self.assertEqual(stats.flanking_bonus(90.0, 15.0), 0.0)    # at the side
        self.assertEqual(stats.crit_chance(3.0, 7.5), 7.5)         # x (1 + 7.5 / 5)
        self.assertEqual(stats.crit_chance(3.0), 3.0)

    def test_natural_equipment_and_timing(self):
        # A rat (appearance 37) wears nothing: its appearance's bite and hide are added; a dressed man keeps his.
        tables = {"itemstats": {56: {"ID": 56, "label": "Creature - Claw, Quick", "Damage": 3.0},
                                9: {"ID": 9, "label": "Armor - Light", "Armor": 3.0},
                                2: {"ID": 2, "label": "Weapon - Longsword", "Damage": 7.0, "dspeed": -0.1},
                                5: {"ID": 5, "label": "Weapon - Greatsword", "Damage": 11.0},
                                3: {"ID": 3, "label": "Weapon - Dagger", "Damage": 4.0, "dspeed": -0.5},
                                7: {"ID": 7, "label": "Shield - Small Round", "Defense": 1.5}},
                  "materialtypes": {},
                  "apr_base": {37: {"ID": 37, "DefaultWeapon": "rat_bite.uti", "DefaultArmor": "hide.uti"}}}
        items = {"rat_bite": {"BaseItem": 56}, "hide": {"BaseItem": 9}, "sword": {"BaseItem": 2},
                 "great": {"BaseItem": 5}, "dagger": {"BaseItem": 3}, "round": {"BaseItem": 7}}
        self.assertEqual(stats.natural_equipment(37, [], items, tables),
                         [{"TemplateResRef": "rat_bite"}, {"TemplateResRef": "hide"}])
        self.assertEqual(stats.natural_equipment(37, [{"TemplateResRef": "sword"}], items, tables),
                         [{"TemplateResRef": "hide"}])
        eq = lambda *refs: [{"TemplateResRef": r} for r in refs]
        self.assertEqual(stats.attack_interval(eq("sword", "round"), items, tables), 1.9)  # 2.0 - 0.1
        self.assertEqual(stats.attack_interval(eq("dagger", "dagger"), items, tables), 1.0)  # dual 1.5 - 0.5
        self.assertEqual(stats.attack_interval(eq("great"), items, tables), 2.5)
        self.assertEqual(stats.attack_interval(eq("rat_bite"), items, tables, anim=0.633), stats.ANIMAL_ROUND)
        self.assertEqual(stats.attack_interval(eq("rat_bite"), items, tables, anim=9.0), 9.0)  # or the animation
        self.assertEqual(stats.attack_interval([], items, tables), stats.ANIMAL_ROUND)

    def test_overrides(self):
        # A mod's <table>_<suffix>.gda rows replace the game's rows by ID.
        with tempfile.TemporaryDirectory() as d:
            Path(d, "autoscale_ao.gda").write_bytes(build_gda(
                [("ID", "int"), ("fscale", "float"), ("fHealthScale", "float"), ("nBonusPoints", "int"),
                 ("nLevelScale", "int"), ("fDamageScale", "float")], [[1, 0.5, 0.75, 0, 1, 0.5]]))
            Path(d, "autoscale_gxa_ao.gda").write_bytes(b"not ours")  # another table's override: left alone
            tables = stats.apply_overrides({k: dict(v) for k, v in self.TABLES.items()}, d)
        self.assertEqual((tables["autoscale"][1]["fHealthScale"], tables["autoscale"][100]["fHealthScale"]), (0.75, 1.0))
        self.assertEqual(stats.stats(tables, package=5, rank=1, area_level=2)["Health"], 105.0)  # 100 x 0.75 + 30


class AbilityTests(unittest.TestCase):
    # abi_base and passive_abilities rows as the tables hold them (abilities.talents reads them).
    TABLES = {
        "abi_base": {
            19: {"ID": 19, "label": "PRECISE_STRIKING", "usetype": 2, "cooldown": 15.0, "costupkeep": 40.0,
                 "fatigue": 5.0, "prereqability": 4022, "prereqattribute": 2, "0x7cfe85d1": 10, "passive_id": 0},
            14: {"ID": 14, "label": "POWERFUL", "usetype": 3, "prereqability": 4022, "prereqattribute": 1,
                 "0x7cfe85d1": 10, "passive_id": 100},
            21: {"ID": 21, "label": "COMBAT_MOVEMENT", "usetype": 3, "prereqability": 603, "prereqlevel": 4,
                 "prereqattribute": 2, "0x7cfe85d1": 14, "passive_id": 29},
            603: {"ID": 603, "label": "DIRTY_FIGHTING", "usetype": 4, "cost": 25.0, "cooldown": 25.0},
            617: {"ID": 617, "label": "SHIELD_BASH", "usetype": 4, "cost": 25.0, "cooldown": 20.0},
            40003: {"ID": 40003, "label": "TRICKS_OF_THE_TRADE", "usetype": 4, "cost": 20.0, "cooldown": 60.0},
        },
        "passive_abilities": {100: {"ID": 100, "Prop1": 7, "modifier1": 25.0, "Prop2": 41, "modifier2": -10.0},
                              29: {"ID": 29, "Prop1": 20, "modifier1": 30.0, "Prop2": 21, "modifier2": 2.0}},
        "autoscale": {1: {"fEffectDurNormal": 1.5}, 3: {"fEffectDurNormal": 0.75, "fResistanceModifier": 10.0,
                                                         "fResistanceMaximum": 75.0}},
        "alwarrior_default": {0: {"InitialTalentID": 11}, 1: {"InitialTalentID": 617}, 2: {"InitialTalentID": 19},
                              3: {"InitialTalentID": 3074}},
    }

    def test_talents(self):
        t = abilities.talents(self.TABLES)
        self.assertEqual(set(t), {19, 14, 21, 603, 617, 40003})
        ps = t[19]
        self.assertEqual((ps["Name"], ps["Use"], ps["Upkeep"], ps["Fatigue"], ps["Cooldown"], ps["Attribute"],
                          ps["Value"]), ("Precise Striking", abilities.SUSTAINED, 40.0, 5.0, 15.0, 2, 10.0))
        self.assertEqual(t[14]["Passive"], {"Health": 25.0, "Fatigue": -10.0})
        self.assertEqual(abilities.starting_talents(self.TABLES, 1), [617, 19])
        self.assertTrue(abilities.can_learn(t[21], {603}, 4, {"Dex": 14.0}))
        self.assertFalse(abilities.can_learn(t[21], {603}, 3, {"Dex": 14.0}))
        self.assertFalse(abilities.can_learn(t[21], set(), 4, {"Dex": 14.0}))

    def test_levelups(self):
        # 3 points a level towards 14 + level x weight (the warrior's: strength 1.2, dexterity 1.0, willpower 0.75)
        weights = {1: {"AttWeight": 1.2}, 2: {"AttWeight": 1.0}, 3: {"AttWeight": 0.75}}
        start = {"Str": 18.0, "Dex": 15.0, "Will": 11.0, "Mag": 11.0, "Int": 11.0, "Con": 13.0}
        self.assertEqual(stats.hero_levelups(start, 2, weights), dict(start, Dex=16.0, Will=13.0))
        self.assertEqual(stats.hero_levelups(start, 1, weights), start)
        # one talent a level: the first of the TalentID list the hero can learn
        tables = dict(self.TABLES, cla_data={1: {"StartingAbility1": 4022}},
                      alwarrior_default={0: {}, 1: {"TalentID": 3009}, 2: {"TalentID": 21},
                                                      3: {"TalentID": 1}, 4: {"TalentID": 14}})
        tables["abi_base"] = {**self.TABLES["abi_base"],
                              3009: {"ID": 3009, "label": "FINAL_BLOW", "usetype": 3, "prereqlevel": 12},
                              1: {"ID": 1, "label": "SHIELD_PUMMEL", "usetype": 4, "prereqability": 617,
                                  "prereqattribute": 1, "0x7cfe85d1": 15}}
        self.assertEqual(abilities.levelup_talents(tables, 1, 2, [617, 19], {"Str": 18.0}), [1])
        self.assertEqual(abilities.levelup_talents(tables, 1, 3, [617, 19], {"Str": 18.0}), [1, 14])
        self.assertEqual(abilities.levelup_talents(tables, 1, 2, [19], {"Str": 18.0}), [14])  # no Shield Bash yet
        self.assertEqual(abilities.levelup_talents(dict(tables, cla_data={}), 1, 2, [19], {"Str": 18.0}), [])

    def test_follower_talents(self):
        # on hire: the InitialTalentID list (row 0: its length) in order, whatever the prerequisites, with 2 points,
        # 1 a level above 1 and 1 more unless a dog or rogue; later levels: the TalentID list, learnable ones only
        tables = dict(self.TABLES, cla_data={17: {"StartingAbility1": 4034}},
                      alarcher_default={0: {"InitialTalentID": 6}, 1: {"InitialTalentID": 3071},
                                        2: {"InitialTalentID": 803}, 3: {"InitialTalentID": 19},
                                        4: {"InitialTalentID": 3072}, 5: {"InitialTalentID": 805}},
                      aldog={0: {"InitialTalentID": 4}, 1: {"InitialTalentID": 90017, "TalentID": 90015},
                             2: {"InitialTalentID": 90050, "TalentID": 90016}, 3: {"InitialTalentID": 90016}})
        tables["abi_base"] = {**self.TABLES["abi_base"],
                              90015: {"ID": 90015, "label": "DOG_OVERWHELM", "usetype": 4, "prereqability": 90049},
                              90016: {"ID": 90016, "label": "DOG_CHARGE", "usetype": 4, "prereqability": 90050}}
        self.assertEqual(abilities.follower_talents(tables, "alarcher_default", 2, {}), [3071, 803, 19, 3072])
        self.assertEqual(abilities.follower_talents(tables, "alarcher_default", 1, {}), [3071, 803, 19])
        # the dog joins at level 1 (2 points), then levels to 2: Overwhelm needs Combat Training, Charge is next
        self.assertEqual(abilities.follower_talents(tables, "aldog", 2, {}, 17, hired_at=1), [90017, 90050, 90016])
        self.assertEqual(abilities.follower_talents(tables, "aldog", 1, {}, 17, hired_at=1), [90017, 90050])

    def test_costs_and_timing(self):
        self.assertEqual(abilities.ability_cost(25.0, 3.5), 26.0)  # rounded after fatigue
        self.assertEqual(abilities.ability_cost(25.0, -6.5), 23.0)
        self.assertEqual(abilities.max_stamina(105.0, [40.0]), 65.0)
        self.assertAlmostEqual(abilities.attack_interval(1.9, 1.1), 2.09)  # Precise Striking
        self.assertAlmostEqual(abilities.attack_interval(1.9, 21.0), 2.85)  # capped at 1.5
        # a critter: (4 s + 1 for the missing party member) x 1.5; party members and short effects not extended
        self.assertEqual(abilities.effect_duration(4.0, 1, self.TABLES, party_size=3), 7.5)
        self.assertEqual(abilities.effect_duration(4.0, 1, self.TABLES, party_size=3, party_member=True), 6.0)
        self.assertEqual(abilities.effect_duration(0.5, 2, self.TABLES, party_size=1), 0.5)
        # a lieutenant resists 10 - (18 - 10) = 2%; 5 more a level the attacker is below it
        self.assertEqual(abilities.resist_chance(3, self.TABLES, attribute=18.0, level_difference=0), 2.0)
        self.assertEqual(abilities.resist_chance(3, self.TABLES, attribute=18.0, level_difference=-3), 17.0)
        self.assertEqual(abilities.resist_chance(1, self.TABLES, attribute=18.0, level_difference=0), 0.0)

    def test_passives_and_rows(self):
        t = abilities.talents(self.TABLES)
        st = {"Health": 115.0, "Flanking": 7.5, "Crit": 5.0, "Fatigue": 3.5, "Level": 1, "Attack": 60.0,
              "Attributes": {"Str": 11.0, "Dex": 18.0, "Int": 14.0}}
        w = abilities.with_passives(st, [14, 19], t, 1)
        self.assertEqual((w["Health"], w["Fatigue"], w["Flanking"]), (140.0, -6.5, 7.5))
        r = abilities.with_passives(st, [21], t, stats.CLASS_ROGUE)
        self.assertEqual((r["Flanking"], r["FlankingAngle"], r["Crit"]), (20.0, 90.0, 7.0))
        row = dict(zip(abilities.TALENT_FIELDS, abilities.talent_row(19, t[19], st)))
        self.assertEqual((row["Upkeep"], row["Attack"], row["Speed"], row["Crit"]), (40.0, 5.0, 0.1, 3.0))
        stun = dict(zip(abilities.TALENT_FIELDS, abilities.talent_row(603, t[603], st)))
        self.assertEqual((stun["Cost"], stun["Seconds"], stun["AttackBonus"]), (25.0, 4.0, 0.0))
        bash = dict(zip(abilities.TALENT_FIELDS, abilities.talent_row(617, t[617], st)))
        self.assertEqual((bash["AttackBonus"], bash["Seconds"]), (10.0, abilities.KNOCKDOWN_SECONDS))
        # Tricks of the Trade by the highest attribute: dexterity's is too small to export
        self.assertEqual(abilities.tricks({"Str": 11.0, "Dex": 12.0, "Int": 14.0}, 60.0), {"Attack": 12.0})
        self.assertEqual(abilities.tricks({"Str": 18.0, "Dex": 15.0, "Int": 11.0}, 60.0), {"AttackSpeed": 20.0})
        self.assertEqual(abilities.talent_row(40003, t[40003], st)[8:], [0.0] * 7 + [1.0, 0.0, 0.0])


class ThreatTests(unittest.TestCase):
    def test_values(self):
        self.assertEqual(threat.seen_threat("Armor - Light"), 20.0)
        self.assertEqual(threat.seen_threat("Armor - Heavy"), 25.0)
        self.assertEqual(threat.seen_threat(""), 15.0)
        self.assertEqual(threat.seen_threat("Armor - Heavy", nightmare=True), 10.0)
        self.assertEqual(threat.damage_threat(12.0, 120.0), 10.0)  # a tenth of its health
        self.assertAlmostEqual(threat.damage_threat(12.0, 120.0, rogue=True), 8.0)
        self.assertEqual(threat.damage_threat(12.0, 120.0, threaten=True), 20.0)
        self.assertEqual(threat.talent_threat(3041), 310.0)
        self.assertEqual(threat.talent_threat(3016), -99.0)

    def test_switching(self):
        rng = random.Random(1)
        t = threat.Threat()
        t.change("warrior", 25.0, 0.0, rng)
        t.change("dog", 15.0, 0.0, rng)
        self.assertEqual(t.target, "warrior")  # the first target: the most hated
        t.change("dog", 20.0, 1.0, rng)  # the dog now leads; the switch timer starts at 0
        self.assertEqual((t.target, t.wait), ("dog", 5))
        t.change("warrior", 30.0, 2.0, rng)  # 1 s after a switch, with 5 s to wait: kept
        self.assertEqual(t.target, "dog")
        t.change(None, 0.0, 6.0, rng)  # 5 s on: may switch
        self.assertEqual((t.target, t.wait), ("warrior", 10))
        t.change("dog", 500.0, 7.0, rng)
        t.taunted()  # Taunt clears the timer
        t.change(None, 0.0, 7.5, rng)
        self.assertEqual(t.target, "dog")
        # a change is at least 1, never brings threat to 0 or below, and stops at 1000
        t.change("dog", 0.2, 8.0, rng)
        self.assertEqual(t.table["dog"], 536.0)
        t.change("dog", -900.0, 8.0, rng)
        self.assertEqual(t.table["dog"], 1.0)
        t.change("warrior", 5000.0, 8.0, rng)
        self.assertEqual(t.table["warrior"], 1000.0)
        t.forget("warrior")
        self.assertEqual(t.target, "dog")
        t.attacked("mother", 9.0, rng)
        self.assertEqual(t.table["mother"], 1.0)

    def test_keep_wounded(self):
        rng = random.Random(3)
        self.assertFalse(threat.keep_wounded(0.5, rng))
        kept = sum(threat.keep_wounded(0.05, rng) for _ in range(4000)) / 4000
        self.assertAlmostEqual(kept, 0.9, delta=0.02)
        kept = sum(threat.keep_wounded(0.15, rng) for _ in range(4000)) / 4000
        self.assertAlmostEqual(kept, 0.5, delta=0.03)


class TacticsTests(unittest.TestCase):
    TABLES = {"packages": {42: {"LevelsPerAbility": 2.0, "Ability1": 3074, "Ability2": 19, "Ability3": 1,
                                "Ability4": 14, "Ability5": 0},
                           53: {"LevelsPerAbility": 1.8, "Ability1": 100075, "Ability2": 6, "Ability3": 3026}}}
    # aip_two_handed's rows: stamina under 25% jumps past Indomitable; Pommel Strike a quarter of the time
    KNIGHT = [{"Target": 1, "Base": 14, "Param": -25.0, "Command": 10, "Sub": 3, "Chance": 100.0},
              {"Target": 1, "Base": 16, "Param": 0.0, "Command": 5, "Sub": 28, "Chance": 25.0},
              {"Target": 7, "Base": 18, "Param": 2.0, "Command": 4, "Sub": 4, "Chance": 20.0},
              {"Target": 7, "Base": 16, "Param": 0.0, "Command": 4, "Sub": 3024, "Chance": 25.0}]

    def test_package_talents(self):
        # level / LevelsPerAbility + 1, +2 at 1 or more: three at level 1, four at level 2
        self.assertEqual(tactics.package_talents(self.TABLES, 42, 1), [3074, 19, 1])
        self.assertEqual(tactics.package_talents(self.TABLES, 42, 2), [3074, 19, 1, 14])
        self.assertEqual(tactics.package_talents(self.TABLES, 42, 9), [3074, 19, 1, 14])  # stops at an empty slot
        self.assertEqual(tactics.package_talents(self.TABLES, 53, 1), [100075, 6, 3026])

    def test_conditions(self):
        self.assertTrue(tactics.level_holds(20.0, -25.0))
        self.assertFalse(tactics.level_holds(30.0, -25.0))
        self.assertTrue(tactics.level_holds(75.0, 75.0))
        row = {"Base": 22, "Param": 1.0}
        self.assertTrue(tactics.condition_holds(row, {"AttackedInMelee": True}, {}))
        self.assertFalse(tactics.condition_holds({"Base": 22, "Param": 2.0}, {"AttackedInMelee": True}, {}))
        self.assertFalse(tactics.condition_holds({"Base": 18, "Param": 2.0}, {}, {}))  # armour type: not handled

    def test_choose(self):
        rng = random.Random(5)
        full, low = {"Health": 100.0, "Stamina": 100.0}, {"Health": 100.0, "Stamina": 10.0}
        foe = {"Health": 100.0, "Stamina": 100.0}
        everything = lambda ability, mode: True
        picks = [tactics.choose(self.KNIGHT, full, foe, everything, rng) for _ in range(4000)]
        indomitable = sum(p == (5, 28) for p in picks) / 4000
        pommel = sum(p == (4, 3024) for p in picks) / 4000
        self.assertAlmostEqual(indomitable, 0.25, delta=0.03)
        self.assertAlmostEqual(pommel, 0.75 * 0.25, delta=0.03)
        # low on stamina: the jump skips Indomitable
        picks = [tactics.choose(self.KNIGHT, low, foe, everything, rng) for _ in range(2000)]
        self.assertFalse(any(p == (5, 28) for p in picks))
        # nothing usable: attack
        self.assertEqual(tactics.choose(self.KNIGHT, full, foe, lambda a, m: False, rng), (tactics.ATTACK, 0))
        flat = tactics.flat_rows(self.KNIGHT)
        self.assertEqual(len(flat), tactics.MAX_TACTICS * len(tactics.FIELDS))
        self.assertEqual(flat[:6], [1.0, 14.0, -25.0, 10.0, 3.0, 100.0])


class SimulateTests(unittest.TestCase):
    # An area export's combat fields: a knight and five rats; the player from PlayerStats.
    AREA = {
        "Area": "test", "NpcTags": ["knight", "rat_1", "rat_2", "rat_3", "rat_4", "rat_5"],
        "NpcHealth": [120.0] + [55.0] * 5, "NpcAttack": [63.5] * 6, "NpcDefense": [48.0] * 6,
        "NpcDamage": [8.0, 12.5] + [4.2, 7.0] * 5, "NpcDamageScale": [1.0] + [0.5] * 5,
        "NpcRules": [6.0, 2.0, 5.0, 7.5, 0.8] + [0.0, 0.0, 1.2, 7.5, 0.4] * 5,
        "PlayerStats": [115.0, 64.5, 50.5, 8.25, 13.0, 7.0, 4.25, 2.14, 5.0, 7.5, 0.4, 100.0],
    }

    def test_fighters(self):
        ours, foes = simulate.fighters(self.AREA, ["knight"], ["rat_*"])
        self.assertEqual([f.tag for f in ours], ["player", "knight"])
        self.assertEqual([f.tag for f in foes], ["rat_1", "rat_2", "rat_3", "rat_4", "rat_5"])
        p, k, r = ours[0], ours[1], foes[0]
        self.assertEqual((p.armour, p.crit, p.interval, p.threshold), (4.25, 5.0, 1.0, 7.0))
        self.assertEqual((k.damage, k.armour, k.interval), ((8.0, 12.5), 6.0, 1.5))
        self.assertEqual((r.scale, r.bonus, r.interval, r.threshold), (0.5, 0.4, 2.0, 7.0))

    def test_strike_rates(self):
        # The same rates as the rules: 64.5 + 54 - 48 = 70.5% to hit; criticals 5% of attacks, of hits too.
        rng = random.Random(3)
        ours, foes = simulate.fighters(self.AREA, [], ["rat_1"])
        results = [simulate.strike(rng, ours[0], foes[0]) for _ in range(20000)]
        hits = [d for d, c in results if d is not None]
        self.assertAlmostEqual(len(hits) / len(results), 0.705, delta=0.01)
        self.assertAlmostEqual(sum(c for d, c in results) / len(hits), 0.05, delta=0.01)
        self.assertTrue(all(8.65 <= d <= 13.4 * 1.5 for d in hits))  # 8.25-13 + 0.4, x1.5 on a critical

    def test_fight(self):
        a = simulate.simulate(self.AREA, ["knight"], ["rat_1", "rat_2"], runs=200, seed=5)
        b = simulate.simulate(self.AREA, ["knight"], ["rat_1", "rat_2"], runs=200, seed=5)
        self.assertEqual(a, b)  # the seed decides everything
        self.assertEqual((a["Won"], a["Lost"]), (1.0, 0.0))
        self.assertEqual(set(a["Party"]), {"player", "knight"})
        self.assertAlmostEqual(sum(p["DamageShare"] for p in a["Party"].values()), 1.0, delta=0.002)
        self.assertIn("won 100%", simulate.report(a))
        # a player alone against five rats at once, weakened: lost every time
        weak = dict(self.AREA, PlayerStats=[10.0] + self.AREA["PlayerStats"][1:])
        self.assertEqual(simulate.simulate(weak, [], ["rat_*"], runs=50)["Lost"], 1.0)

    def test_slots(self):
        # One foe per target: with only the player standing, never more than one rat attacks; the rest wait.
        rng = random.Random(2)
        ours, foes = simulate.fighters(self.AREA, [], ["rat_*"])
        out = simulate.fight(ours, foes, rng, slots=1, use_threat=False)
        self.assertLessEqual(sum(1 for f in foes if f.target is not None and not f.down), 1)
        self.assertIn(out["Won"] or out["Lost"], (True,))

    def test_waves(self):
        # Waves of two: each death brings the next rat in, so all five are fought.
        rng = random.Random(1)
        ours, foes = simulate.fighters(self.AREA, ["knight"], ["rat_*"])
        out = simulate.fight(ours, foes, rng, wave=2)
        self.assertTrue(out["Won"])
        self.assertTrue(all(f.down for f in foes))


    def test_talents(self):
        # The player with Precise Striking, Dirty Fighting and Shield Bash (TALENT_FIELDS rows) and 105 stamina.
        rows = [[19, 2, 0, 15, 40, 5, 0, 0, 5, 0, 0.1, 3, 0, 0, 0, 1, 0, 0],
                [603, 4, 25, 25, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                [617, 4, 25, 20, 0, 0, 10, 3.43, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0]]
        area = dict(self.AREA, PlayerStats=self.AREA["PlayerStats"][:11] + [105.0, 1.9, 3.5, 1.0, 0.0, 0.0, 2.0, 4.0],
                    PlayerTalents=[x for r in rows for x in r], NpcStatus=[2.0, 1.0, 0.0] + [1.0, 1.5, 0.0] * 5)
        ours, foes = simulate.fighters(area, [], ["rat_1"])
        p, rat = ours[0], foes[0]
        self.assertEqual((p.stamina, p.fatigue, p.offhand, len(p.talents), rat.duration_scale), (105.0, 3.5, (2.0, 4.0), 3, 1.5))
        rng = random.Random(1)
        # first Precise Striking: 40 upkeep off the pool, 5 more fatigue, +5 attack while on
        self.assertEqual(simulate.use_talent(rng, p, rat, 0.0, 1, 0.0), (True, None, False))
        self.assertEqual((p.pool, p.stamina, p.fatigue, p.own("Attack", 0.0)), (65.0, 65.0, 8.5, 5.0))
        # then Dirty Fighting: 25 x 1.085 -> 27 stamina, the rat stunned (4 + 3 missing members) x 1.5
        self.assertEqual(simulate.use_talent(rng, p, rat, 1.0, 1, 0.0), (True, None, False))
        self.assertEqual((p.stamina, rat.disabled), (38.0, 11.5))
        # no Shield Bash on a stunned rat; once it is up, Shield Bash (stamina back 1 a second)
        self.assertEqual(simulate.use_talent(rng, p, rat, 2.0, 1, 0.0)[0], False)
        self.assertTrue(simulate.use_talent(rng, p, rat, 12.0, 1, 0.0)[0])
        self.assertEqual((p.stamina, p.used), (38.0 + 11.0 - 27.0, {19: 1, 603: 1, 617: 1}))
        # nothing left until the cooldowns end
        self.assertEqual(simulate.use_talent(rng, p, rat, 13.0, 1, 0.0)[0], False)
        # in fights the player uses its talents and wins faster against a lone knight
        knight = simulate.simulate(area, [], ["knight"], runs=300, seed=2)
        plain = simulate.simulate(area, [], ["knight"], runs=300, seed=2, talents=False)
        self.assertEqual(set(knight["Talents"]), {"Precise Striking", "Dirty Fighting", "Shield Bash"})
        self.assertEqual(plain["Talents"], {})
        self.assertIn("Dirty Fighting", simulate.report(knight))

    def test_rogue_backstab_and_evasion(self):
        rng = random.Random(4)
        ours, foes = simulate.fighters(self.AREA, [], ["rat_1"])
        p, rat = ours[0], foes[0]
        p.rogue = True
        hits = [simulate.strike(rng, p, rat, 7.5) for _ in range(2000)]
        self.assertTrue(all(c for d, c in hits if d is not None))  # every flanking hit a backstab
        p.displacement = 20.0
        misses = sum(simulate.strike(rng, rat, p)[0] is None for _ in range(5000)) / 5000
        # the rat hits 63.5 + 54 - 50.5 = 67% of the time, 20% of it lost to Evasion
        self.assertAlmostEqual(misses, 1 - 0.67 * 0.8, delta=0.02)


    def test_threat(self):
        # every foe sees the knight (25: heavy armour) above the player (20) and goes for it first
        area = dict(self.AREA, PlayerStats=self.AREA["PlayerStats"][:11] + [100.0, 1.9, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 20.0],
                    NpcStatus=[1.0, 1.0, 0.0, 25.0, 0.0] + [1.0, 1.5, 0.0, 15.0, 0.0] * 5)
        ours, foes = simulate.fighters(area, ["knight"], ["rat_1", "rat_2"])
        self.assertEqual((ours[0].seen, ours[1].seen, foes[0].seen), (20.0, 25.0, 15.0))
        rng = random.Random(2)
        first = []
        for _ in range(50):
            ours, foes = simulate.fighters(area, ["knight"], ["rat_1", "rat_2"])
            simulate.fight(ours, foes, rng)
            first.append(all(f.threat is not None for f in foes))
        self.assertTrue(all(first))
        ours, foes = simulate.fighters(area, ["knight"], ["rat_1"])
        f = foes[0]
        f.threat = threat.Threat()
        for m in ours:
            f.threat.change(m, m.seen, 0.0, rng)
        self.assertIs(f.threat.target, ours[1])
        # Taunt: the player's row, used because a foe is on someone else
        taunt = dict(zip(abilities.TALENT_FIELDS, [3041, 4, 40, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0]))
        ours[0].talents = [taunt]
        used = simulate.use_talent(rng, ours[0], f, 0.0, 2, 0.0, foes=[f])
        self.assertEqual((used[0], f.threat.target, f.threat.table[ours[0]]), (True, ours[0], 330.0))
        self.assertEqual(ours[0].stamina, 60.0)
        # no threat: the prototype's rule
        r = simulate.simulate(area, ["knight"], ["rat_*"], runs=50, use_threat=False)
        self.assertEqual(r["Won"], 1.0)


    def test_hero_tactics(self):
        # the Tank preset as the game has it, abridged: modes and talents the level-2 warrior lacks are skipped,
        # Shield Bash and Shield Pummel fill his two slots; an attack row needs no ability
        rows = [{"Target": 1, "Base": 16, "Param": 0, "Command": 5, "Sub": 808, "Chance": 100.0},
                {"Target": 3, "Base": 2, "Param": 75, "Command": 4, "Sub": 617, "Chance": 100.0},
                {"Target": 3, "Base": 6, "Param": 1, "Command": 4, "Sub": 1, "Chance": 100.0},
                {"Target": 3, "Base": 6, "Param": 1, "Command": 4, "Sub": 3, "Chance": 100.0}]
        use_types = {2: 0, 4: 4, 5: 2}
        known = [617, 19, 1]
        self.assertEqual([r["Sub"] for r in tactics.preset_rows(rows, known, 2, use_types)], [617, 1])
        self.assertEqual([r["Sub"] for r in tactics.preset_rows(rows, known + [808], 2, use_types)], [808, 617])
        attack = {"Target": 3, "Base": 16, "Param": 0, "Command": 2, "Sub": 0, "Chance": 100.0}
        self.assertEqual(tactics.preset_rows([attack] + rows, [], 2, use_types), [attack])
        tables = {"presets": {1: rows}, "slots": {2: 2, 3: 3}, "use_types": use_types}
        self.assertEqual([r["Sub"] for r in tactics.hero_tactics(tables, 1, 3, known)], [617, 1])
        self.assertTrue(tactics.condition_holds(rows[2], {}, {}))  # the nearest visible: the foe in hand

    def test_follower_tactics(self):
        # a follower's slots: the level's, more with Combat Tactics; its package's table loaded into them, none
        # without one (Ser Gilmore's -1)
        dog = [{"Target": 3, "Base": 6, "Param": 1, "Command": 4, "Sub": s, "Chance": 100.0} for s in (90017, 90016, 90015)]
        tables = {"slots": {2: 2, 3: 3}, "use_types": {2: 0, 4: 4, 5: 2}, "gui": {10107: dog},
                  "packages": {78: {"FollowerTacticsTable": 10107}, 96: {"FollowerTacticsTable": -1}}}
        self.assertEqual(tactics.slots(tables, 2), 2)
        self.assertEqual(tactics.slots(tables, 2, [100110]), 3)
        self.assertEqual(tactics.slots(tables, 3, [100111, 100113]), 9)
        self.assertEqual([r["Sub"] for r in tactics.follower_tactics(tables, 78, 2, [90015, 90016, 90017])], [90017, 90016])
        self.assertEqual([r["Sub"] for r in tactics.follower_tactics(tables, 78, 2, [90015])], [90015])
        self.assertEqual(tactics.follower_tactics(tables, 96, 2, [1, 3]), [])
        # the conditions the menu adds: its own health whatever the target, the followers' range bands
        me, foe = {"Health": 30.0, "Stamina": 90.0, "Distance": 8.0}, {"Health": 100.0, "Stamina": 100.0}
        row = {"Target": 3, "Base": tactics.SELF_HP, "Param": -50, "Command": 4, "Sub": 1, "Chance": 100.0}
        self.assertTrue(tactics.condition_holds(row, me, foe))
        self.assertFalse(tactics.condition_holds(dict(row, Base=tactics.HP), me, foe))
        self.assertTrue(tactics.condition_holds(dict(row, Base=tactics.FOLLOWER_RANGE, Param=2), me, foe))
        # an attack row attacks: the rows below it are not tried
        attack = dict(row, Base=tactics.ANY, Command=tactics.ATTACK, Sub=0)
        shot = dict(row, Base=tactics.ANY)
        self.assertEqual(tactics.choose([attack, shot], me, foe, lambda a, m: True, random.Random(1)), (tactics.ATTACK, 0))
        self.assertEqual(tactics.choose([shot, attack], me, foe, lambda a, m: True, random.Random(1)), (tactics.USE_ABILITY, 1))

    def test_tactics_menu(self):
        # the screen's lists: the player's menu entries the Unreal side runs, named from the talk table
        tables = {"menu": {
            "targets": [{"ID": 1, "label": "Self", "StrRef": 11, "Type": 1}, {"ID": 2, "label": "Ally", "Type": 2},
                        {"ID": 3, "label": "Enemy", "StrRef": 13, "Type": 4}],
            "bases": [{"ID": 2, "label": "HP Level", "StrRef": 20, "ValidForTarget": 7, tactics.IN_MENU: 1},
                      {"ID": 33, "label": "Self, HP", "ValidForTarget": 70, tactics.IN_MENU: 0},
                      {"ID": 22, "label": "Attacked", "ValidForTarget": 1, tactics.IN_MENU: 1},
                      {"ID": 31, "label": "Surrounded", "ValidForTarget": 1, tactics.IN_MENU: 1},
                      {"ID": 4, "label": "Clustered", "ValidForTarget": 4, tactics.IN_MENU: 1}],
            "conditions": [{"ID": 4, "label": "HP < 50%", "StrRef": 30, "ConditionBase": 2, "ConditionParameter": -50, tactics.IN_MENU: 1},
                           {"ID": 50, "label": "Highest", "ConditionBase": 2, "ConditionParameter": 1, tactics.IN_MENU: 0},
                           {"ID": 101, "label": "Melee", "ConditionBase": 22, "ConditionParameter": 1, tactics.IN_MENU: 1},
                           {"ID": 103, "label": "Magic", "ConditionBase": 22, "ConditionParameter": 4, tactics.IN_MENU: 1},
                           {"ID": 153, "label": "No enemies", "ConditionBase": 31, "ConditionParameter": 0, tactics.IN_MENU: 1},
                           {"ID": 300, "label": "Self < 50%", "ConditionBase": 33, "ConditionParameter": -50, tactics.IN_MENU: 1},
                           {"ID": 24, "label": "Clustered 2", "ConditionBase": 4, "ConditionParameter": 2, tactics.IN_MENU: 1}],
            "commands": [{"ID": 2, "label": "Attack", "StrRef": 40}, {"ID": 3, "label": "Wait"},
                         {"ID": 4, "label": "Use Ability"}]}}
        names = {11: "Self", 13: "Enemy", 20: "Health", 30: "Health < 50%", 40: "Attack"}
        m = tactics.menu(tables, names.get)
        self.assertEqual(m["TacticTargets"], [1.0, 1.0, 3.0, 4.0])
        self.assertEqual(m["TacticTargetNames"], ["Self", "Enemy"])
        self.assertEqual(m["TacticBaseNames"], ["Health", "Self, HP", "Attacked"])
        self.assertEqual(m["TacticBases"], [2.0, 1.0, 1.0, 33.0, 0.0, 1.0, 22.0, 1.0, 0.0])
        self.assertEqual(m["TacticConds"], [4.0, 2.0, -50.0, 101.0, 22.0, 1.0, 300.0, 33.0, -50.0])
        self.assertEqual(m["TacticCondNames"], ["Health < 50%", "Melee", "Self < 50%"])
        self.assertEqual(m["TacticCommandNames"], ["Attack", "Use Ability"])

    def test_allies(self):
        # an ally fights on the party's side; an immortal one never falls; the fight is lost with the party down
        area = dict(self.AREA, NpcImmortal=[1, 0, 0, 0, 0, 0])
        ours, foes = simulate.fighters(area, [], ["rat_*"], allies=["knight"])
        self.assertEqual([f.tag for f in ours], [simulate.PLAYER, "knight"])
        knight = ours[1]
        self.assertTrue(knight.ally and knight.immortal and knight.side == "party")
        knight.health = 1.0
        result = simulate.fight(ours, foes, random.Random(2))
        self.assertFalse(knight.down)
        self.assertEqual(result["Lost"], ours[0].down)

    def test_spells(self):
        # spellpower: magic above 10; a staff's damage + 25-75% of spellpower / 4
        self.assertEqual(stats.spellpower({"Mag": 18.0}), 8.0)
        self.assertEqual(stats.spellpower({"Mag": 9.0}), 0.0)
        self.assertTrue(stats.is_staff({"label": "Weapon - Staff"}))
        # Lightning's row carries its factor; (100 + 8) x 0.3 = 32.4, no roll, no armour
        table = {i: {"Name": str(i), "Use": 4, "Cost": 20.0, "Cooldown": 10.0, "Upkeep": 0.0, "Fatigue": 0.0,
                     "Effect": abilities.EFFECTS[i]} for i in abilities.SPELLS}
        rows = {i: dict(zip(abilities.TALENT_FIELDS, abilities.talent_row(i, table[i], {"Level": 1.0})))
                for i in abilities.SPELLS}
        self.assertEqual((rows[abilities.LIGHTNING]["DamageMul"], rows[abilities.SHOCK]["DamageMul"]), (0.3, 0.4))
        ours, foes = simulate.fighters(self.AREA, [], ["rat_*"])
        p, mage, other = ours[0], foes[0], foes[1]
        mage.spellpower, mage.stamina, mage.pool = 8.0, 100.0, 100.0
        rng = random.Random(5)
        damage, crit = simulate.perform(rng, mage, p, rows[abilities.LIGHTNING], 0.0, 1)
        self.assertAlmostEqual(damage, 32.4)
        # Mind Blast: the target and those on the caster in melee stunned 3 s x their rank's scale
        other.target = mage
        p.target = mage
        simulate.perform(rng, mage, p, rows[abilities.MIND_BLAST], 0.0, 1, enemies=[p, other])
        self.assertEqual(p.disabled, 3.0 * p.duration_scale)
        self.assertGreater(other.disabled, 0.0)
        # a staff bolt always hits
        mage.staff, mage.damage = True, (4.0, 6.0)
        p.defense, p.displacement = 1000.0, 0.0
        damage, crit = simulate.strike(rng, mage, p)
        self.assertTrue(4.0 <= damage <= 6.0 and not crit)

    def test_party_talents(self):
        # the dog: Growl (-15 defense 30 s, no roll), Charge (a knockdown), Overwhelm (pinned 2 s, two bites that
        # land), Mabari Howl (every foe not a boss stunned 5 s); Rapid Shot's row by dexterity
        table = {i: {"Name": str(i), "Use": 2 if i == 3071 else 4, "Cost": 10.0, "Cooldown": 30.0, "Upkeep": 0.0,
                     "Fatigue": 0.0, "Effect": abilities.EFFECTS.get(i, {})} for i in abilities.PARTY}
        dog = {"Level": 2.0, "Attributes": {"Str": 14.0, "Dex": 16.0}}
        rows = {i: dict(zip(abilities.TALENT_FIELDS, abilities.talent_row(i, table[i], dog)))
                for i in (90017, 90016, 90015, 90048, 3071)}
        self.assertEqual((rows[90017]["Defense"], rows[90017]["Seconds"]), (-15.0, 30.0))
        self.assertAlmostEqual(rows[3071]["AimDelay"], -0.3)
        self.assertEqual(rows[3071]["Crit"], -100.0)
        ours, foes = simulate.fighters(self.AREA, [], ["rat_*"])
        p, rat, other = ours[0], foes[0], foes[1]
        p.stamina = p.pool = 100.0
        rng = random.Random(3)
        simulate.perform(rng, p, rat, rows[90017], 0.0, 1)
        self.assertEqual(rat.own("Defense", 10.0), -15.0)
        self.assertEqual(rat.own("Defense", 31.0), 0.0)
        damage, crit = simulate.perform(rng, p, rat, rows[90015], 0.0, 1)
        self.assertEqual((rat.disabled, crit), (2.0, False))
        self.assertGreater(damage, 0)
        simulate.perform(rng, p, rat, rows[90048], 0.0, 1, enemies=[rat, other])
        self.assertEqual((rat.disabled, other.disabled), (5.0, 5.0))

    def test_foe_talents(self):
        # a rat that only Shield Pummels (always, 4 s stun): the player is stunned and struck three times
        rows = [1, 4, 30, 20, 0, 0, 10, 4.0, 0, 0, 0, 0, 0, 0, 0, 1.1, 0, 0]
        tac = [7, 16, 0, 4, 1, 100] + [0.0] * (tactics.MAX_TACTICS * 6 - 6)
        area = dict(self.AREA, NpcStatus=[1.0, 1.0, 0.0, 25.0, 0.0, 0.0, 0.0, 0.0, 0.0] +
                    [1.0, 1.5, 0.0, 15.0, 0.0, 50.0, 0.0, 3.0, 4.0] * 5,
                    NpcTalents=[0.0] * 108 + (rows + [0.0] * 90) * 5, NpcTactics=[0.0] * tactics.MAX_TACTICS * 6 + tac * 5)
        ours, foes = simulate.fighters(area, [], ["rat_1"])
        p, rat = ours[0], foes[0]
        self.assertEqual((rat.stamina, rat.offhand, len(rat.talents), len(rat.tactics)), (50.0, (3.0, 4.0), 1, 1))
        rng = random.Random(7)
        used, damage, crit = simulate.foe_turn(rng, rat, p, 1.0, ours, len(ours), 0.0)
        self.assertTrue(used)
        self.assertEqual((rat.stamina, p.disabled), (20.0, 5.0))  # 30 stamina; a party member's stun is not lengthened
        self.assertGreater(damage, 0)  # the two shield blows always land
        # the next round it cannot pay: it attacks
        self.assertEqual(simulate.foe_turn(rng, rat, p, 2.0, ours, len(ours), 0.0)[0], False)
        # Sunder Weapon disarms, Critical Strike kills at 25% health
        sunder = dict(zip(abilities.TALENT_FIELDS, [3025, 4, 25, 20, 0, 0, 0, 6.0] + [0.0] * 7 + [0.6]))
        rat.stamina = 50.0
        for _ in range(20):
            simulate.perform(rng, rat, p, sunder, 3.0, 1)
            if p.disarm[0]:
                break
        self.assertEqual(p.disarm, (9.0, p.attack))
        execute = dict(zip(abilities.TALENT_FIELDS, [3, 4, 0, 45, 0, 0, 0, 0] + [0.0] * 7 + [1.0]))
        p.health = p.max_health * 0.2
        for _ in range(20):
            damage, _ = simulate.perform(rng, rat, p, execute, 4.0, 1)
            if damage:
                break
        self.assertAlmostEqual(damage, p.max_health * 0.2 + 1.0)


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

    def test_load_special_flag_chain(self):
        # AREALOAD_SPECIAL runs before the other load cases; an else-if chain on plot flags is kept as
        # kinds 14/15, while a test on anything else leaves the whole case out.
        script = """
            void main()
            {
                object oFriend = UT_GetNearestCreatureByTag(oPC, MY_CR_FRIEND);
                object oGuest = UT_GetNearestCreatureByTag(oPC, MY_CR_GUEST);
                object oServant = UT_GetNearestCreatureByTag(oPC, MY_CR_SERVANT);
                switch (nEventType)
                {
                    case EVENT_TYPE_AREALOAD_PRELOADEXIT:
                    {
                        object oBody = GetObjectByTag("cook");
                        KillCreature(oBody);
                        break;
                    }
                    case EVENT_TYPE_AREALOAD_SPECIAL:
                    {
                        if (nAreaOnce == FALSE)
                        {
                            int nFriend = WR_GetPlotFlag(PLT_MY_MAIN, BATTLE);
                            int nGuest = WR_GetPlotFlag(PLT_MY_MAIN, PRELUDE);
                            if (nFriend == TRUE) { WR_SetObjectActive(oFriend, TRUE); }
                            else if (nGuest == TRUE) { WR_SetObjectActive(oGuest, TRUE); }
                            else { WR_SetObjectActive(oServant, TRUE); }
                        }
                        break;
                    }
                }
            }
        """
        consts = {"MY_CR_FRIEND": "friend", "MY_CR_GUEST": "guest", "MY_CR_SERVANT": "servant"}
        t = plotlogic.translate_events(script, self.PLOTS, consts, "my_area")
        acts = [(a["kind"], a["target"], a["arg"], a["value"]) for a in t["cases"]["load:my_area"]]
        self.assertEqual(acts, [(14, "1", "AAAA:0", 2), (3, "friend", "", 1), (15, "", "", 4),
                                (14, "1", "AAAA:1", 2), (3, "guest", "", 1), (15, "", "", 1),
                                (3, "servant", "", 1), (12, "cook", "", 1)])
        state = script.replace("if (nFriend == TRUE)", "if (GetLevel(oPC) > 3)")
        t = plotlogic.translate_events(state, self.PLOTS, consts, "my_area")
        self.assertEqual([(a["kind"], a["target"]) for a in t["cases"]["load:my_area"]], [(12, "cook")])
        self.assertTrue(any("AREALOAD_SPECIAL branches on game state" in s for s in t["skipped"]))

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

    def test_defined_flag_order(self):
        # Unreal recomputes defined flags in order: what a flag tests must come before it.
        entries = [("P:256", [("P:2", False), ("G:260", False)]),   # battle begun and male
                   ("Q:257", [("P:256", False)]),                   # tests the one above
                   ("R:258", [("P:1", True)]),
                   ("G:260", [])]                                    # a true flag
        order = [k for k, _ in plotlogic._dependency_order(entries)]
        self.assertEqual(order, ["R:258", "G:260", "P:256", "Q:257"])
        cycle = [("A:256", [("B:256", False)]), ("B:256", [("A:256", False)])]
        self.assertEqual(len(plotlogic._dependency_order(cycle)), 2)

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


class ConditionTests(unittest.TestCase):
    # Made-up trigger script in the shape of the game's, not game text.
    PLOTS = {"my_father": {"guid": "FFFF", "name": "my_father", "flags": {6: "READY", 7: "ENTERED"}}}

    def test_flag_tests_become_conditions(self):
        script = """
            void main()
            {
                switch (nEventType)
                {
                    case EVENT_TYPE_ENTER:
                    {
                        if (WR_GetPlotFlag(PLT_MY_FATHER, READY) == TRUE)
                        {
                            if (IsFollower(oCreature) == TRUE)
                            {
                                WR_SetPlotFlag(PLT_MY_FATHER, ENTERED, TRUE, TRUE);
                                UT_Talk(oDad, oPC);
                            }
                        }
                        else
                            UT_Talk(oGuard, oPC);
                        int nDone = WR_GetPlotFlag(PLT_MY_FATHER, ENTERED);
                        if (!nDone) UT_Talk(oDad, oPC);
                        break;
                    }
                }
            }
        """
        consts = {}
        text = script.replace("oDad", '"dad"').replace("oGuard", '"guard"')
        t = plotlogic.translate_events(text, self.PLOTS, consts, "my_trigger")
        acts = [(a["kind"], a["target"], a["arg"], a["value"]) for a in t["cases"]["enter:my_trigger"]]
        self.assertEqual(acts, [
            (14, "1", "FFFF:6", 3),        # unless READY: skip the two actions and the skip
            (4, "force", "FFFF:7", 1),     # 4th argument TRUE: run its script again
            (2, "dad", "", 1),
            (15, "", "", 1),                # READY: skip the else
            (2, "guard", "", 1),
            (14, "0", "FFFF:7", 1),         # only while ENTERED is not set
            (2, "dad", "", 1)])
        # No other trigger destroyed: nothing marks the event done.
        self.assertNotIn("done:", json.dumps(t["cases"]))

    def test_trigger_removes_its_siblings(self):
        # Made-up trigger script in the shape of the game's doorway triggers, not game text.
        script = """
            void main()
            {
                switch (nEventType)
                {
                    case EVENT_TYPE_ENTER:
                    {
                        object oCreature = GetEventCreator(ev);
                        UT_Talk(oKnight, oCreature);
                        object[] arOthers = GetNearestObjectByTag(oCreature, GetTag(OBJECT_SELF), OBJECT_TYPE_ALL, 10);
                        int i;
                        for (i = 0; i < GetArraySize(arOthers); i++)
                            WR_DestroyObject(arOthers[i]);
                        WR_DestroyObject(OBJECT_SELF);
                        break;
                    }
                }
            }
        """
        t = plotlogic.translate_events(script.replace("oKnight", '"knight"'), self.PLOTS, {}, "my_door_trigger")
        acts = [(a["kind"], a["target"], a["arg"], a["value"]) for a in t["cases"]["enter:my_door_trigger"]]
        self.assertEqual(acts, [(2, "knight", "", 1), (4, "", "done:enter:my_door_trigger", 1)])


class DoorEventTests(unittest.TestCase):
    # Made-up door script in the shape of the game's, not game text.
    PLOTS = {"my_mother": {"guid": "EEEE", "name": "my_mother", "flags": {3: "TOLD", 5: "BANTER"}}}

    def test_opening_and_unlocking(self):
        script = """
            void DoorOpened(string sTag)
            {
                if (sTag == "hall_door")
                {
                    UT_TeamAppears(TEAM_HALL);
                }
                if (sTag == SERVANT_DOOR)
                {
                    object oCook = UT_GetNearestCreatureByTag(oPC, "cook");
                    UT_QuickMove("maid", "wp_maid", TRUE);
                    UT_Talk(oCook, oPC);
                }
            }
            void main()
            {
                switch (GetEventType(ev))
                {
                    case EVENT_TYPE_USE:
                    {
                        switch (GetPlaceableAction(OBJECT_SELF))
                        {
                            case PLACEABLE_ACTION_UNLOCK:
                            {
                                if (sTag == "stairs") { }
                                else if (sTag == "vault")
                                {
                                    if (!WR_GetPlotFlag(PLT_MY_MOTHER, TOLD))
                                        WR_SetPlotFlag(PLT_MY_MOTHER, BANTER, TRUE);
                                }
                                break;
                            }
                            case PLACEABLE_ACTION_OPEN:
                            {
                                DoorOpened(sTag);
                                break;
                            }
                        }
                        break;
                    }
                }
            }
        """
        t = plotlogic.translate_events(script, self.PLOTS, {"SERVANT_DOOR": "servant_door", "TEAM_HALL": 9}, "my_door")
        acts = {k: [(a["kind"], a["target"], a["arg"], a["value"]) for a in v] for k, v in t["cases"].items()}
        self.assertEqual(acts["open:hall_door"], [(3, "team:9", "", 1)])
        self.assertEqual(acts["open:servant_door"], [(6, "maid", "wp_maid", 1), (2, "cook", "", 1)])
        self.assertEqual(acts["unlock:vault"], [(14, "0", "EEEE:3", 1), (4, "", "EEEE:5", 1)])
        self.assertEqual(acts["unlock:stairs"], [])

    def test_use_by_area(self):
        script = """
            void main()
            {
                switch (GetEventType(ev))
                {
                    case EVENT_TYPE_USE:
                    {
                        Placeable_HandleUsed(ev);
                        if (GetTag(GetArea(OBJECT_SELF)) == MY_AR_NIGHT && !GetLocalInt(OBJECT_SELF, PLC_DO_ONCE_A))
                        {
                            SetLocalInt(OBJECT_SELF, PLC_DO_ONCE_A, TRUE);
                            CS_LoadCutscene(MY_CUT, PLT_MY_MOTHER, TOLD, MY_CR_DAD);
                        }
                        else if ((GetTag(GetArea(OBJECT_SELF)) == MY_AR_DAY) && (WR_GetPlotFlag(PLT_MY_MOTHER, BANTER) == FALSE))
                        {
                            UT_Talk(GetObjectByTag("my_dog"), GetHero());
                        }
                        else if (GetTag(GetArea(OBJECT_SELF)) == MY_AR_OTHER && GetHour() > 3)
                        {
                            UT_Talk(GetObjectByTag("my_dog"), GetHero());
                        }
                        break;
                    }
                }
            }
        """
        consts = {"MY_AR_NIGHT": "night_area", "MY_AR_DAY": "day_area", "MY_AR_OTHER": "other_area",
                  "MY_CUT": "bhn200cs_night_falls.cut", "MY_CR_DAD": "dad"}
        t = plotlogic.translate_events(script, self.PLOTS, consts, "my_pantry")
        acts = {k: [(a["kind"], a["target"], a["arg"], a["value"]) for a in v] for k, v in t["cases"].items()}
        self.assertEqual(acts, {
            "open:my_pantry@night_area": [(16, "bhn200cs_night_falls", "EEEE:3", 1), (2, "dad", "", 1)],
            "open:my_pantry@day_area": [(14, "0", "EEEE:5", 1), (2, "my_dog", "", 1)]})
        self.assertIn("open:my_pantry@other_area: tests GetHour() > 3, left out", t["skipped"])


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

    def test_cli_owner_from_second_names_folder(self):
        # The owner is the creature whose DialogResRef is the conversation, found
        # in any --names folder (the mabari's template is pulled apart from bhn*).
        conv = {"conversation": "pet_main", "starts": [0], "lines": [
            {"index": 0, "kind": "npc", "text": "Woof", "speaker": "OWNER", "children": []},
            {"index": 1, "kind": "npc", "text": "Hi", "speaker": "bhn_cook", "children": []}]}
        with tempfile.TemporaryDirectory() as d:
            for sub, tag, name, dialog in (("hn", "bhn_cook", "Cook", "bhn_cook"),
                                           ("pet", "gen_pet", "Dog", "pet_main")):
                (Path(d) / sub).mkdir()
                (Path(d) / sub / f"{tag}.utc.json").write_text(json.dumps({"root": {
                    "Tag": tag, "DialogResRef": dialog, "LocName": {"strref": 1, "text": name}}}),
                    encoding="utf-8")
            (Path(d) / "c.dlg.conv.json").write_text(json.dumps(conv), encoding="utf-8")
            out = Path(d) / "out.json"
            self.assertEqual(main(["unreal", "conv", str(Path(d) / "c.dlg.conv.json"),
                                   "--names", str(Path(d) / "hn"), "--names", str(Path(d) / "pet"),
                                   "--out", str(out)]), 0)
            got = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(got["Owner"], "gen_pet")
            self.assertEqual(got["SpeakerNames"], {"bhn_cook": "Cook", "gen_pet": "Dog", "OWNER": "Dog"})


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


class CutsceneTests(unittest.TestCase):
    # A made-up cutscene and scripts in the shape of the game's, not game text.
    PLOTS = {"my_main": {"guid": "AAAA", "name": "my_main", "flags": {0: "FAREWELL", 1: "PRELUDE"}}}

    def _cut(self, d):
        path = Path(d) / "raw" / "designercutscenes" / "my_farewell.cut"
        path.parent.mkdir(parents=True)
        path.write_bytes(build_cut([
            {"tag": "MASTER", "tracks": [("anim", 0.0, "cs_fade")]},
            {"tag": "my_cr_father", "tracks": [("anim", 0.0, "cs_up"),
                                               ("line", 0.7, 4.4, "my_farewell_dlg", 10, "Go.")]},
            {"tag": "my_cr_mother", "tracks": [("line", 4.9, 10.1, "my_farewell_dlg", 11, "We love you.")]},
        ], length=33.5, area="my_night"))
        return path

    def test_lines_and_conversation(self):
        with tempfile.TemporaryDirectory() as d:
            s = cutscene.summary(GFF4.open(self._cut(d)))
            scanned = cutscene.scan(d)
        self.assertEqual((s["Length"], s["Area"], s["Conversation"]), (33.5, "my_night", "my_farewell_dlg"))
        self.assertEqual([(l["Start"], l["Actor"], l["Strref"], l["Text"]) for l in s["Lines"]],
                         [(0.7, "my_cr_father", 10, "Go."), (4.9, "my_cr_mother", 11, "We love you.")])
        self.assertEqual(list(scanned), ["my_farewell"])
        self.assertEqual(cutscene.conversation_for("MY_FAREWELL", scanned), "my_farewell_dlg")
        self.assertEqual(cutscene.conversation_for("bhn200cs_night_falls", scanned), "bhn200cs_night_falls")
        self.assertIsNone(cutscene.conversation_for("unknown", scanned))

    def test_staging(self):
        # A made-up scene: the origin at (60, 40) m; the mother starts beside it, ignores a key before the start
        # (where she stood before the scene) and one in another frame (small values), walks between two area
        # keys half a second apart, and is put back in the last half second (ignored). A camera looks at her.
        path_keys = [(-0.1, (30.0, 40.0, 0.0)), (2.0, (0.5, 0.5, 0.0)), (5.0, (63.0, 42.0, 0.0)),
                     (5.5, (63.5, 42.0, 0.0)), (9.9, (30.0, 40.0, 0.0))]
        pos = ("curve", 17, [(base, [(t, v[i]) for t, v in path_keys]) for i, base in enumerate((61.0, 41.0, 0.0))])
        rot = ("curve", 18, [(90.0, [(t, 90.0) for t, _ in path_keys]), (0.0, []), (0.0, [])])
        cam = [("curve", 17, [(56.0, []), (41.0, []), (1.5, [])]), ("curve", 18, [(0.0, []), (0.0, []), (0.0, [])]),
               ("curve", 13, [(45.0, [])])]
        data = build_cut([{"tag": "MASTER", "tracks": [("cut", 0.0, 7)]},
                          {"tag": "", "id": 7, "tracks": cam},
                          {"tag": "my_cr_mother", "tracks": [pos, rot]}], length=10.0, origin=(60.0, 40.0, 0.0))
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "my.cut"
            p.write_bytes(data)
            st = cutscene.staging(GFF4.open(p))
        self.assertEqual(st["ActorTags"], ["my_cr_mother"])
        f = st["ActorFrames"]
        frame = lambda t: f[int(t * st["CamRate"]) * 4:int(t * st["CamRate"]) * 4 + 4]
        yaw = cutscene._ue_yaw_deg(90.0)
        self.assertEqual(frame(0.0), [6100.0, -4100.0, 0.0, yaw])
        self.assertEqual(frame(3.0), [6100.0, -4100.0, 0.0, yaw])  # the key in another frame is held over
        self.assertAlmostEqual(frame(5.2)[0], 6320.0, delta=1.0)  # walking from 63 to 63.5 m
        self.assertEqual(frame(9.95)[:2], [6350.0, -4200.0])  # not put back at the end
        self.assertEqual(st["Framed"], 1.0)
        self.assertEqual(st["Cam"][:6], [5600.0, -4100.0, 150.0, 0.0, 0.0, 72.7])

    def test_caption_conversation(self):
        rt = cutscene.caption_conversation("bhn200cs_night_falls")
        n = len(cutscene.CAPTIONS["bhn200cs_night_falls"][1])
        lines = rt["Lines"]
        self.assertEqual((rt["Starts"], rt["VoBank"], rt["SpeakerNames"]), ([0], "", {"caption": "Night falls"}))
        self.assertEqual([l["Children"] for l in lines[:n]], [[n + i] for i in range(n)])  # text, then a click
        self.assertEqual([l["Children"] for l in lines[n:]], [[i + 1] for i in range(n - 1)] + [[]])
        self.assertTrue(all(l["Text"] and not l["IsPlayer"] for l in lines[:n]))
        self.assertTrue(all(l["IsPlayer"] and not l["Text"] and not l["Vo"] for l in lines[n:]))
        made = unreal.conversation({"conversation": "x", "starts": [0], "lines": [
            {"index": 0, "kind": "npc", "text": "Hi.", "speaker": "OWNER", "children": []}]})
        self.assertEqual(set(rt) - {"Warnings"}, set(made) - {"Warnings"})
        self.assertEqual(set(lines[0]), set(made["Lines"][0]))

    def test_load_cutscene(self):
        plot_script = """
            void main()
            {
                if (nType == EVENT_TYPE_SET_PLOT)
                {
                    switch (nFlag)
                    {
                        case FAREWELL:
                        {
                            WR_UnlockAchievement(ACH_X);
                            CS_LoadCutscene(MY_CUT_FAREWELL, PLT_MY_MAIN, PRELUDE);
                            break;
                        }
                        case PRELUDE:
                        {
                            CS_LoadCutscene(MY_CUT_OTHER);
                            break;
                        }
                    }
                }
            }
        """
        area_script = """
            void main()
            {
                switch (nEventType)
                {
                    case EVENT_TYPE_AREALOAD_PRELOADEXIT:
                    {
                        if (nAreaOnce == FALSE)
                        {
                            if (nDebug == FALSE) { CS_LoadCutscene(MY_CUT_NIGHT, "", -1, MY_CR_DOG); }
                        }
                        break;
                    }
                }
            }
        """
        with tempfile.TemporaryDirectory() as d:
            self._cut(d)
            (Path(d) / "my_cutscenes_h.nss").write_text(
                'const resource MY_CUT_FAREWELL = R"my_farewell.cut";\n'
                'const resource MY_CUT_NIGHT = R"bhn200cs_night_falls.cut";\n'
                'const resource MY_CUT_OTHER = R"my_other.cut";\nconst string MY_CR_DOG = "my_dog";\n',
                encoding="utf-8")
            consts = plotlogic.load_constants(d)
            cuts = cutscene.scan(d)
        self.assertEqual(consts["MY_CUT_FAREWELL"], "my_farewell.cut")
        plot = self.PLOTS["my_main"]
        t = plotlogic.translate(plot_script, plot, self.PLOTS, consts, cuts)
        acts = {k: [(a["kind"], a["target"], a["arg"], a["value"]) for a in v] for k, v in t["cases"].items()}
        self.assertEqual(acts["FAREWELL"], [(16, "my_farewell_dlg", "AAAA:1", 1)])  # PRELUDE set when it ends
        self.assertEqual(acts["PRELUDE"], [])
        self.assertIn("PRELUDE: CS_LoadCutscene(MY_CUT_OTHER): no conversation or caption", t["skipped"])
        e = plotlogic.translate_events(area_script, self.PLOTS, consts, "my_night", cuts)
        self.assertEqual([(a["kind"], a["target"], a["arg"]) for a in e["cases"]["load:my_night"]],
                         [(16, "bhn200cs_night_falls", ""), (2, "my_dog", "")])  # its caption, then the dog talks


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
