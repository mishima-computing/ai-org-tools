# Org Tools

A **carrier-agnostic, growing capability layer** for the AI Org family. The AI Org has two **carrier
editions** — [`ai-org-bootstrap-codex`](https://github.com/mishima-computing/ai-org-bootstrap-codex)
(carrier = `codex`) and [`ai-org-bootstrap-claudecode`](https://github.com/mishima-computing/ai-org-bootstrap-claudecode)
(carrier = `claude`). They differ only in *who carries*. **Org Tools is the orthogonal axis: *what
capabilities* the editions operate** — built once here, not duplicated per edition.

```
AI Org (umbrella)
├── AI Org codex    ── carrier = codex     ┐  WHO carries
├── AI Org claude   ── carrier = claude    ┘
└── Org Tools (this repo) ── Corps, …      ── WHAT capabilities (carrier-agnostic, shared, growing)
```

## AI Org Codex — architecture

The Codex edition is now a **complete autonomous builder**: a GOAL goes in, PRs come out. Three layers
(carrier → dialectic → autonomous builder), the two-axis Splitter, the shared observability stream, and
the Shagiri host boundary are written up in full, with diagrams, here:

**→ [`docs/ai-org-codex-architecture.md`](docs/ai-org-codex-architecture.md)**

```
GOAL → Splitter (task DAG) → Frontier (ready leaves) → Dialectic (10-agent, per leaf) → merge → PR
                    ▲ split-on-convergence-failure (recursion) ┘
```

## Corps — media production (pronounced "core")

**Corps** is the AI Org's media-production capability. The name is pronounced *"core"* — after the
Beatles' **Apple Corps** (their multimedia company: Apple Records / Films / Electronics / Publishing),
which is exactly this shape: one umbrella, a division per medium. We use only *"Corps"* (no "Apple") —
the trademark is theirs; the idea is fair game.

```
Corps
├── core         ── the medium-agnostic ENGINE: the produce ladder, Library, GATE/JUDGE, capture-as-asset
├── graphicist   ── division: graphics  (Kenney CC0 assets, PIL, Blender, gen-image)
└── composer     ── division: music      (samples/MIDI, synth, gen-audio)  — future
```

Two layers: the **SOURCE** (held assets, or a structured model built with Blender/rules) is reusable and
grounded; the **VIEW** (the flat image/audio) is a disposable projection of it. PIL / gen-AI / Blender /
the asset library are not distinct architecture — they are interchangeable **providers**, the chambers
of a revolver `core` rotates through.

**The asset-first ladder** (descend only when the rung above can't cover the brief):

| rung | what | regime |
|------|------|--------|
| 1 reuse-apply | a held asset matches as-is | GATE |
| 2 reuse-process | edit a held asset to fit | GATE |
| 3 build+render | source built from rules + view rendered **explicitly** (PIL / Blender) | GATE |
| 4 synthesize | view **synthesized** by gen-AI, conditioned on the brief; last resort | JUDGE |

Rungs 1-3 are **explicit** (you specify it → reproducible, auditable); rung 4 is **synthesized** (a model
supplies unspecified content from priors → judged for fidelity/aesthetic + a grounding audit of *why* no
asset covered it). Any output is **captured as an asset**, so the gap closes and synthesis shrinks toward
zero. The same shape produces a `composer` (music) division — see
[ADR-0001](docs/decisions/ADR-0001-org-tools-and-the-graphicist.md).

## How editions use it (no MCP)

The controller is a **deterministic orchestrator** — it knows which division to call and what to pass,
so it calls a division's `produce()` **directly** (Anthropic "workflow" = predefined code paths). That
is *not* dynamic LLM tool-use, so **MCP is not needed internally** (it is an optional external face).

Editions stay self-contained by **vendoring** this repo, with CI checking the copy hasn't drifted:

```bash
python sync/vendor.py sync  ../ai-org-bootstrap-codex     # canonical -> edition/vendor/ai-org-tools/
python sync/vendor.py check ../ai-org-bootstrap-codex     # exit 1 on drift (CI gate)
```

Registered divisions live in [`registry/tools.yaml`](registry/tools.yaml). `tools/graphicist/` already
runs the ladder on real Kenney CC0 tiles (`compose_demo.py`); generation never fires when the library
covers the brief.
