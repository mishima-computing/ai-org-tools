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
└── Org Tools (this repo) ── graphicist, … ── WHAT capabilities (carrier-agnostic, shared, growing)
```

See **[ADR-0001](docs/decisions/ADR-0001-org-tools-and-the-graphicist.md)** for the full decision and
its grounding (MCP, Anthropic's workflow-vs-agent distinction, ChatDev, blender-mcp, Scenario).

## How editions use it (no MCP)

The controller is a **deterministic orchestrator** — it knows which tool to call and what to pass, so it
calls a tool's entrypoint **directly** (Anthropic "workflow" = predefined code paths). That is *not*
dynamic LLM tool-use, so **MCP is not needed internally** (it is reserved as an optional external face).

Editions stay self-contained by **vendoring** this repo, with CI checking the copy hasn't drifted from
canonical:

```bash
python sync/vendor.py sync  ../ai-org-bootstrap-codex     # canonical -> edition/vendor/ai-org-tools/
python sync/vendor.py check ../ai-org-bootstrap-codex     # exit 1 on drift (CI gate)
```

Single source of truth (here) × self-contained editions (in-repo, offline box/dogfood) × drift detection.

## Tools

Registered in [`registry/tools.yaml`](registry/tools.yaml).

### graphicist (#1)

Produce a graphic for a brief, **asset-first**, generating **only as a last resort** and capturing the
result as a new asset so generation self-shrinks. The asset is the source of truth; the image is a
disposable view.

Ladder: `1 apply → 2 process → 3 procedural (deterministic) → 4 generate (last resort)`. Rungs 1-3 are
**GATE**-verified (reproducible); rung 4 is **JUDGE**-verified (stefan aesthetic + brief fidelity +
grounding audit) and **captured-as-asset**. `tools/graphicist/graphicist.py` is a runnable skeleton with
a self-test; rungs 3/4 are injectable hooks (deterministic procedural gen; generative AI).

> Grounded, not invented: an LLM operating Blender + an asset library + generation already exists in the
> wild ([blender-mcp](https://github.com/ahujasid/blender-mcp)); our contribution is the *discipline* —
> the asset-first ladder, capture-as-asset, and GATE/JUDGE verification.
