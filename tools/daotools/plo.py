"""Plot files (.plo, GFF4 "PLTS"): names for plot GUIDs and their flags.

Conversations test and set plot flags by plot GUID and flag number. A plot
file holds one plot: its resource name, GUID, script and flag list. Flags 256
and up are "defined" flags whose value the plot's script computes (e.g.
GEN_GENDER_MALE); they are listed in the file like the stored ones.

Layout checked on all 898 base-game plots (single player and core): one PLOT
struct per file, and field 3 always equals the file name without "plt_".
"""

from __future__ import annotations

from pathlib import Path

from . import fields as F
from .gff4 import GFF4, GFF4Error, Struct

_NAME = 3  # plot resource name; not plot-specific, so it stays out of fields.NAMES


class PLOError(Exception):
    pass


def is_plot(gff: GFF4) -> bool:
    return gff.file_type == "PLTS"


def read(gff: GFF4) -> list[dict]:
    """Every plot in the file as {"guid", "name", "script", "flags": {id: name}}."""
    if not is_plot(gff):
        raise PLOError(f"{gff.path or 'file'} is not a plot file (type {gff.file_type!r})")
    plots = []
    for plot in gff.root.get(F.PLOT_LIST) or []:
        if not isinstance(plot, Struct):
            continue
        flags = {}
        for flag in plot.get(F.PLOT_FLAGS) or []:
            if isinstance(flag, Struct) and isinstance(flag.get(F.PLOT_FLAG_ID), int):
                flags[flag.get(F.PLOT_FLAG_ID)] = flag.get(F.PLOT_FLAG_NAME) or ""
        plots.append({
            "guid": (plot.get(F.PLOT_GUID) or "").upper(),
            "name": plot.get(_NAME) or "",
            "script": plot.get(F.PLOT_SCRIPT) or "",
            "flags": flags,
        })
    return plots


def load_dir(path: str | Path) -> dict[str, dict]:
    """Every plot under a folder of extracted .plo files, keyed by GUID.

    When the same GUID appears twice (a plot in both the core and the single
    player archive), the first file in path order wins.
    """
    plots: dict[str, dict] = {}
    for p in sorted(Path(path).rglob("*.plo")):
        try:
            found = read(GFF4.open(p))
        except (GFF4Error, PLOError):
            continue
        for plot in found:
            plots.setdefault(plot["guid"], plot)
    return plots


def flag_name(plots: dict[str, dict], key: str) -> str:
    """The flag name for a "GUID:FLAG" key, or "" when it is not known."""
    guid, _, flag = key.partition(":")
    plot = plots.get(guid.upper())
    if not plot or not flag.isdigit():
        return ""
    return plot["flags"].get(int(flag), "")


def flag_key(plots: dict[str, dict], name: str) -> str:
    """The "GUID:FLAG" key for a flag name, e.g. GEN_GENDER_MALE."""
    hits = [f"{guid}:{fid}" for guid, plot in plots.items()
            for fid, fname in plot["flags"].items() if fname == name]
    if not hits:
        raise ValueError(f"no plot flag named {name}")
    if len(hits) > 1:
        raise ValueError(f"plot flag name {name} is ambiguous: {', '.join(hits)}")
    return hits[0]
