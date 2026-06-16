#!/usr/bin/env python3
"""graphicist — the AI Org's graphics tool (Org Tools #1).

Produce a graphic for a brief, preferring HELD ASSETS and generating only as a LAST resort, and
capturing any generation back into the library so generation self-shrinks toward zero. The controller
calls produce() DIRECTLY (a deterministic workflow call — NOT via MCP; see docs/decisions/ADR-0001).

The fallback ladder (descend only when the rung above can't cover the brief):
  1 apply       — a held asset matches as-is                                 (GATE)
  2 process     — edit a held asset to fit (restyle/recolor/retopo)          (GATE)
  3 procedural  — deterministic generation from rules (Blender/Houdini/PCG)  (GATE)
  4 generate    — generative AI, last resort, conditioned + captured-as-asset (JUDGE)

The asset is the source of truth; the image is a disposable view. Rungs 1-3 are deterministic and
GATE-verified; rung 4 is JUDGE-verified (aesthetic + brief fidelity + a grounding audit of WHY no asset
covered it). A rung-4 output is captured into the library, so the same gap is covered by an asset next
time and generation is used less over time.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Asset:
    id: str
    tags: frozenset          # what it depicts / its role
    style: str
    provenance: str          # handmade | scanned | bought | procedural | generated
    data: object = None      # opaque payload (path / bytes / scene-graph)


@dataclass(frozen=True)
class Brief:
    want: frozenset          # required tags
    style: str


@dataclass(frozen=True)
class Result:
    asset: Asset
    rung: int                # 1..4 — which ladder rung produced it
    regime: str              # "GATE" (deterministic, rungs 1-3) | "JUDGE" (generative, rung 4)
    grounding: str           # why this rung; for rung 4, why no held asset covered the brief


class Library:
    """The graphicist's held assets — its own working memory, not the org's burden."""

    def __init__(self, assets=()):
        self._by_id = {a.id: a for a in assets}

    def add(self, a: Asset):
        self._by_id[a.id] = a

    def all(self):
        return [self._by_id[k] for k in sorted(self._by_id)]   # sorted -> deterministic

    def match(self, brief: Brief):
        for a in self.all():
            if brief.want <= a.tags and a.style == brief.style:
                return a
        return None


def _default_process(asset: Asset, brief: Brief):
    """Deterministically edit a held asset to fit: same subject, restyled. (rung 2)"""
    if brief.want <= asset.tags and asset.style != brief.style:
        return Asset(id=f"{asset.id}~{brief.style}", tags=asset.tags, style=brief.style,
                     provenance="procedural", data=("restyle", asset.id, brief.style))
    return None


def produce(brief: Brief, library: Library, *, process=None, procedural=None,
            generate=None, judge=None) -> Result:
    """Run the ladder. `process`/`procedural`/`generate`/`judge` are injectable hooks (the deterministic
    ones default to real implementations; `generate` is the gen-AI call — supplied only when wanted)."""
    # 1 — apply a held asset as-is
    a = library.match(brief)
    if a is not None:
        return Result(a, 1, "GATE", "held asset covers the brief as-is")

    # 2 — process a held asset to fit
    proc = process or _default_process
    for src in library.all():
        edited = proc(src, brief)
        if edited is not None:
            library.add(edited)
            return Result(edited, 2, "GATE", f"processed {src.id} to style '{brief.style}'")

    # 3 — deterministic procedural generation from rules
    if procedural is not None:
        p = procedural(brief)
        if p is not None:
            library.add(p)
            return Result(p, 3, "GATE", "deterministic procedural generation (rules)")

    # 4 — generative AI, LAST resort: record the gap, generate (conditioned), JUDGE, capture-as-asset
    gap = f"no held asset/process/procedural covers {sorted(brief.want)} in style '{brief.style}'"
    if generate is None:
        raise RuntimeError(gap + "; generative fallback not wired")
    payload = generate(brief)                                  # conditioned on the brief (img2img/control)
    asset = Asset(id=f"gen:{'-'.join(sorted(brief.want))}:{brief.style}", tags=brief.want,
                  style=brief.style, provenance="generated", data=payload)
    if judge is not None and not judge(asset, brief):          # JUDGE: aesthetic + fidelity + grounding
        raise RuntimeError("generated asset failed JUDGE (fidelity/aesthetic)")
    library.add(asset)                                         # capture-as-asset -> gap closes, gen shrinks
    return Result(asset, 4, "JUDGE", gap + " -> generated, judged, captured")


def _self_test():
    lib = Library([
        Asset("rock_mossy", frozenset({"rock", "moss"}), "warm", "scanned"),
        Asset("tree_pine", frozenset({"tree", "pine"}), "warm", "handmade"),
    ])
    # rung 1: held asset as-is
    r = produce(Brief(frozenset({"rock"}), "warm"), lib)
    assert r.rung == 1 and r.regime == "GATE", r
    # rung 2: restyle a held asset (same subject, new style)
    r = produce(Brief(frozenset({"tree", "pine"}), "dusk"), lib)
    assert r.rung == 2 and r.regime == "GATE", r
    # rung 4: nothing covers it -> generate (last resort) -> JUDGE -> capture
    calls = {"n": 0}
    def gen(b):
        calls["n"] += 1
        return ("image-bytes", sorted(b.want), b.style)
    r = produce(Brief(frozenset({"dragon"}), "warm"), lib, generate=gen)
    assert r.rung == 4 and r.regime == "JUDGE" and calls["n"] == 1, r
    # capture-as-asset: the SAME brief is now covered by an asset (rung 1); generation does NOT recur
    r2 = produce(Brief(frozenset({"dragon"}), "warm"), lib, generate=gen)
    assert r2.rung == 1 and calls["n"] == 1, ("generation must self-shrink", r2, calls)
    print("graphicist self-test ok: asset-first ladder, generation last + captured, self-shrinking")


if __name__ == "__main__":
    _self_test()
