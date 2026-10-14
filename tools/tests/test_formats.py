import json
import struct
import tempfile
import unittest
from pathlib import Path

from daotools import cnv, fields as F
from daotools.cli import main
from daotools.erf import ERF, ERFError, is_erf
from daotools.gda import GDA, column_hash
from daotools.gff4 import (GFF4, T_FLOAT32, T_SINT16, T_UINT8, T_UINT32, T_UINT64, T_VECTOR3F, TlkString,
                           to_jsonable)
from daotools.tlk import TalkTable, TalkTables

from builders import GFF4Writer, Tmpl, build_cnv, build_erf, build_tlk_v02, build_tlk_v05


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
        self.assertEqual(conv["lines"][2]["action"]["conv_plot_flag"], 3)
        self.assertEqual(conv["lines"][2]["action"]["conv_script"], "bhn_plot")
        script = cnv.transcript(conv)
        self.assertIn("   0 bryce: Ah, Rendon.", script)
        self.assertIn("     3 howe: Indeed.", script)
        self.assertIn("-> (back to line 0)", script)
        self.assertIn("not reached from any start: [4]", script)
        json.dumps(conv)

    def test_children_as_structs(self):
        self._check(cnv.export(GFF4(build_cnv(self.lines, [0])), self.tlk, "bhn_test"))

    def test_children_as_indices(self):
        self._check(cnv.export(GFF4(build_cnv(self.lines, [0], children_as_structs=False)), self.tlk))

    def test_wrong_type(self):
        with self.assertRaises(cnv.CNVError):
            cnv.export(GFF4(build_tlk_v02({1: "x"})))


class CLITests(unittest.TestCase):
    def test_scan_find_pull(self):
        with tempfile.TemporaryDirectory() as d:
            game = Path(d) / "game"
            (game / "packages" / "core" / "data").mkdir(parents=True)
            (game / "packages" / "core" / "data" / "conversations.erf").write_bytes(build_erf({
                "bhn100cr_father.dlg": build_cnv(ConversationTests.lines, [0]),
                "orz_other.dlg": build_cnv(ConversationTests.lines, [0]),
            }))
            (game / "packages" / "core" / "data" / "core_en-us.tlk").write_bytes(
                build_tlk_v02({100: "Ah, Rendon.", 101: "Father?"}))
            out = Path(d) / "out"

            self.assertEqual(main(["scan", str(game), "--out", str(out / "scan.json")]), 0)
            report = json.loads((out / "scan.json").read_text(encoding="utf-8"))
            self.assertEqual(report["archives"][0]["by_extension"], {"dlg": 2})
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
            self.assertEqual(summary["formats"], {"dlg: GFF V4.0 DLG V0.2": 1})


if __name__ == "__main__":
    unittest.main()
