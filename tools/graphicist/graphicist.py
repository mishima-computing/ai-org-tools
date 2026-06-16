#!/usr/bin/env python3
"""graphicist — the GRAPHICS division of Corps, built on the medium-agnostic `core` engine.

core supplies the produce ladder / Library / GATE-JUDGE / capture; graphicist supplies the graphics
PROVIDERS (the revolver chambers): the held asset catalog (Kenney CC0 to start), the PIL view-renderer
(rungs 2-3, explicit/GATE). Blender (3D source build) and a gen-image chamber (rung 4, synthesized/JUDGE)
slot in here later. The controller calls produce() DIRECTLY (a workflow call, not via MCP).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "core"))
sys.path.insert(0, str(HERE))
import core            # noqa: E402
import procgen_pil     # noqa: E402

# re-export the engine's vocabulary so callers need only import this division
Asset, Brief, Result, Library = core.Asset, core.Brief, core.Result, core.Library


def library() -> "core.Library":
    """The graphics division's held assets (catalog-backed, provenance/license tracked)."""
    return core.Library.from_catalog(HERE / "assets" / "catalog.json")


def produce(brief, lib=None, **kw):
    """Run the ladder with the graphics chambers wired in (PIL = explicit rungs 2-3)."""
    lib = library() if lib is None else lib
    kw.setdefault("process", procgen_pil.process)
    kw.setdefault("procedural", procgen_pil.procedural)
    return core.produce(brief, lib, **kw)


if __name__ == "__main__":
    lib = library()
    r = produce(Brief(frozenset({"road", "ew"}), "kenney-iso-2d"), lib)
    assert r.rung == 1 and r.regime == "GATE", r          # held Kenney asset, no generation
    r2 = produce(Brief(frozenset({"plaza"}), "kenney-iso-2d"), lib)
    assert r2.rung == 3 and r2.regime == "GATE", r2        # PIL explicit generation, still GATE, before gen-AI
    print(f"graphicist ok: {len(lib.all())} held assets; road->{r.asset.id} (rung1), "
          f"plaza->PIL (rung3); generation stays the last resort")
