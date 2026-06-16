#!/usr/bin/env python3
"""procgen_pil — a DETERMINISTIC PIL/Pillow provider for the graphicist's rungs 2-3 (the GATE regime).

PIL is deterministic image code: draw an image from rules (rung 3) or recolor/restyle a held asset
(rung 2). It is preferred OVER generative AI (rung 4): same inputs -> same bytes, reproducible,
GATE-verifiable, and captured-as-asset cleanly. PIL is an OPTIONAL provider — injected as the
graphicist's `procedural` / `process` hooks — so the graphicist core stays dependency-free.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "core"))
from core import Asset, Brief  # noqa: E402

OUT = Path(__file__).resolve().parent / "assets" / "_pil"   # generated assets (gitignored, deterministic)
TW, TH = 100, 65                                            # match the Kenney iso tile footprint (2:1)


def _rgb_for(brief: Brief) -> tuple:
    """Deterministic colour from the brief (tags+style) — no randomness, so output is reproducible."""
    h = int(hashlib.sha256((",".join(sorted(brief.want)) + "|" + brief.style).encode()).hexdigest(), 16)
    return (90 + h % 120, 90 + (h >> 8) % 120, 90 + (h >> 16) % 120)


def _shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


def procedural(brief: Brief):
    """rung 3: draw a simple iso tile from rules (deterministic raster generation)."""
    from PIL import Image, ImageDraw
    OUT.mkdir(parents=True, exist_ok=True)
    name = f"pil-{'-'.join(sorted(brief.want))}-{brief.style}"
    img = Image.new("RGBA", (TW, TH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    top = _rgb_for(brief)
    d.polygon([(50, 0), (100, 25), (50, 50), (0, 25)], fill=top + (255,))            # diamond top
    d.polygon([(0, 25), (50, 50), (50, 65), (0, 40)], fill=_shade(top, 0.70) + (255,))  # left wall
    d.polygon([(100, 25), (50, 50), (50, 65), (100, 40)], fill=_shade(top, 0.85) + (255,))  # right wall
    path = OUT / (name + ".png")
    img.save(path)
    return Asset(id=f"pil:{name}", tags=brief.want, style=brief.style, provenance="procedural",
                 data={"path": str(path.relative_to(OUT.parent.parent)), "tool": "PIL", "license": "generated"})


def process(asset: Asset, brief: Brief):
    """rung 2: recolor a held raster asset to a new style (deterministic tint)."""
    src = (asset.data or {}).get("path") if isinstance(asset.data, dict) else None
    if not src or not (brief.want <= asset.tags) or asset.style == brief.style:
        return None
    from PIL import Image
    base = OUT.parent.parent / src
    if base.suffix.lower() != ".png" or not base.exists():
        return None
    from PIL import Image as _I
    img = _I.open(base).convert("RGBA")
    tint = _rgb_for(brief)
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = ((r + tint[0]) // 2, (g + tint[1]) // 2, (b + tint[2]) // 2, a)
    OUT.mkdir(parents=True, exist_ok=True)
    name = f"{asset.id.replace('/', '_')}~{brief.style}"
    path = OUT / (name + ".png")
    img.save(path)
    return Asset(id=f"pil:{name}", tags=asset.tags, style=brief.style, provenance="procedural",
                 data={"path": str(path.relative_to(OUT.parent.parent)), "tool": "PIL", "from": asset.id})


if __name__ == "__main__":
    import core as g
    lib = g.Library()                                   # empty -> nothing to apply/process -> rung 3
    b = Brief(frozenset({"plaza"}), "kenney-iso-2d")
    r = g.produce(b, lib, procedural=procedural)
    assert r.rung == 3 and r.regime == "GATE", r        # PIL filled rung 3, deterministic (GATE), no gen-AI
    p1 = (OUT.parent.parent / r.asset.data["path"]).read_bytes()
    p2_asset = procedural(b)
    p2 = (OUT.parent.parent / p2_asset.data["path"]).read_bytes()
    assert p1 == p2, "PIL output must be byte-identical (deterministic)"
    print("procgen_pil ok: rung-3 PIL generation is deterministic (GATE), reached before any gen-AI")
