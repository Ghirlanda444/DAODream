"""python dsl_write.py <Blueprint path> <graph> <file.dsl>: write a graph from a staged DSL file (UTF-8)."""
import json, sys
import ue
sys.stdout.reconfigure(encoding="utf-8")
ue.init()
bp, graph, path = sys.argv[1:4]
code = open(path, encoding="utf-8").read()
print(ue.call("editor_toolset.toolsets.blueprint.BlueprintTools", "write_graph_dsl",
              {"graph": {"refPath": "%s:%s" % (bp, graph)}, "code": code})[:3000])
