#!/usr/bin/env python3
"""compose_demo — build a small isometric scene out of REAL Kenney (CC0) tiles, chosen by the
graphicist's asset-first ladder. Proves the point: a semantic scene spec ("road E-W here, a tree
there, water in the corner") is satisfied by HELD assets (rung 1, GATE) — borrowed art lands in the
town, generation never fires. Embeds each tile PNG (base64) into one SVG; rasterise with qlmanage.

  python compose_demo.py [out.svg]
"""
from __future__ import annotations

import base64
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import graphicist as g  # noqa: E402

STYLE = "kenney-iso-2d"
TW = 100                    # tile width; iso diamond is 2:1
DX, DY = TW // 2, TW // 4   # iso steps per (col,row)


def scene_brief(c: int, r: int):
    """Semantic tile + optional object for cell (c,r) — a little coastal town with a crossroads."""
    if c >= 6 and r >= 6:
        return {"water"}, None                       # pond
    if (c == 5 and r >= 5) or (r == 5 and c >= 5):
        return {"beach"}, None                       # beach ring around the pond
    if r == 3 and c == 3:
        return {"road"}, None                        # 4-way intersection
    if r == 3:
        return {"road", "ew"}, None
    if c == 3:
        return {"road", "ns"}, None
    if (c * 3 + r * 5) % 7 == 0:
        return {"grass"}, {"tree", "tall"}           # a tree on grass
    return {"grass"}, None


def _img(path: str, x: float, y: float, w: float):
    data = base64.b64encode((HERE / path).read_bytes()).decode()
    return f'<image x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" href="data:image/png;base64,{data}"/>'


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "compose_demo.svg"
    lib = g.Library.from_catalog(HERE / "assets" / "catalog.json")
    N = 8
    ox, oy = N * DX + 40, 60
    parts, rung1 = [], 0
    # painter's order: back (small c+r) first
    for c, r in sorted(((c, r) for c in range(N) for r in range(N)), key=lambda cr: (cr[0] + cr[1], cr[0])):
        ground, obj = scene_brief(c, r)
        sx = (c - r) * DX + ox
        sy = (c + r) * DY + oy
        res = g.produce(g.Brief(frozenset(ground), STYLE), lib)
        rung1 += res.rung == 1
        parts.append(_img(res.asset.data["path"], sx - TW / 2, sy - DY, TW))   # ground tile
        if obj:
            o = g.produce(g.Brief(frozenset(obj), STYLE), lib)
            from PIL import Image
            iw, ih = Image.open(HERE / o.asset.data["path"]).size
            parts.append(_img(o.asset.data["path"], sx - iw / 2, sy - ih + DY * 0.6, iw))  # object, on the tile
    W, H = N * TW + 80, N * TW + 120
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
           f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<rect width="{W}" height="{H}" fill="#cfe3ef"/>' + "".join(parts) + "</svg>")
    out.write_text(svg, encoding="utf-8")
    print(f"composed {N*N} cells from Kenney CC0 tiles, all rung-1 (held assets): {rung1}/{N*N} -> {out}")


if __name__ == "__main__":
    main()
