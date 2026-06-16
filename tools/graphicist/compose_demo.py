#!/usr/bin/env python3
"""compose_demo — build a small isometric TOWN out of REAL Kenney (CC0) tiles via the asset-first
ladder. Ground/roads/water/trees are chosen by the ladder (rung 1, GATE, no generation); buildings are
placed from the held building library (a scene-designer pick for variety). Borrowed art lands in the
town; generation never fires. One SVG with each tile PNG embedded (base64); rasterise with qlmanage.

  python compose_demo.py [out.svg]
"""
from __future__ import annotations

import base64
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "core"))
import core as g  # noqa: E402

STYLE = "kenney-iso-2d"
TW = 100
DX, DY = TW // 2, TW // 4


def scene_cell(c, r):
    """ground tags + overlay ('tree'|'building'|None) for cell (c,r): a crossroads, a downtown, a pond."""
    if c >= 7 and r >= 7:
        return {"water"}, None
    if (c == 6 and r >= 6) or (r == 6 and c >= 6):
        return {"beach"}, None
    if r == 4 and c == 4:
        return {"road"}, None
    if r == 4:
        return {"road", "ew"}, None
    if c == 4:
        return {"road", "ns"}, None
    if (c, r) in {(1, 1), (3, 2), (5, 1), (2, 0), (0, 3), (5, 3), (7, 1), (1, 5), (3, 5)}:  # scattered lots
        return {"grass"}, "building"
    if (c * 3 + r * 5) % 6 == 0:
        return {"grass"}, "tree"
    return {"grass"}, None


def _img(path, x, y, w):
    data = base64.b64encode((HERE / path).read_bytes()).decode()
    return f'<image x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" href="data:image/png;base64,{data}"/>'


def main():
    from PIL import Image
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "compose_demo.svg"
    lib = g.Library.from_catalog(HERE / "assets" / "catalog.json")
    # held building tiles that are complete buildings-on-a-base (~127 tall) -> a rotation for variety
    bld = []
    for a in lib.all():
        if a.id.startswith("kenney-isometric-buildings") and isinstance(a.data, dict):
            p = HERE / a.data["path"]
            if Image.open(p).size[1] >= 120:
                bld.append(a.data["path"])
    bld.sort()

    N = 9
    ox, oy = N * DX + 60, 90
    parts, rung1, bi = [], 0, 0
    for c, r in sorted(((c, r) for c in range(N) for r in range(N)), key=lambda cr: (cr[0] + cr[1], cr[0])):
        ground, overlay = scene_cell(c, r)
        sx, sy = (c - r) * DX + ox, (c + r) * DY + oy
        res = g.produce(g.Brief(frozenset(ground), STYLE), lib)
        rung1 += res.rung == 1
        parts.append(_img(res.asset.data["path"], sx - TW / 2, sy - DY, TW))
        if overlay == "tree":
            o = g.produce(g.Brief(frozenset({"tree", "tall"}), STYLE), lib)
            iw, ih = Image.open(HERE / o.asset.data["path"]).size
            parts.append(_img(o.asset.data["path"], sx - iw / 2, sy - ih + DY * 0.6, iw))
        elif overlay == "building" and bld:
            bp = bld[bi % len(bld)]; bi += 1
            iw, ih = Image.open(HERE / bp).size
            bw = TW * 0.96; bh = ih * bw / iw                              # scale ~ a tile wide
            parts.append(_img(bp, sx - bw / 2, sy - bh + DY * 1.3, bw))    # base sits on the tile
    W, H = N * TW + 140, N * TW + 200
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<rect width="{W}" height="{H}" fill="#cfe3ef"/>' + "".join(parts) + "</svg>")
    out.write_text(svg, encoding="utf-8")
    print(f"composed {N*N} cells + {bi} buildings from Kenney CC0 tiles; ground rung-1 (held): "
          f"{rung1}/{N*N}, generation never fired -> {out}")


if __name__ == "__main__":
    main()
