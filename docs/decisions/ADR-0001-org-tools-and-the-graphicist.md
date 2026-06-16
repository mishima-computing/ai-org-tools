# ADR-0001: Org Tools — a carrier-agnostic capability layer, and the graphicist as its first tool

## Status

Proposed. (Umbrella-level architecture for the AI Org family. Drafted from a design conversation,
grounded in the prior art cited below — illustrative demos are NOT treated as evidence.)

## Context

The AI Org family today is two **carrier editions** — `ai-org-bootstrap-codex` (carrier = `codex exec`)
and `ai-org-bootstrap-claudecode` (carrier = `claude -p`). They share almost all of their controller
core and differ only in the carrier adapter. We felt the cost of that directly: the parallel
orchestrator, the verifier `PYTHONPATH` fix and the cp932/UTF-8 fix all had to be **ported to both
editions** by hand — carrier-agnostic work trapped inside carrier-specific repos.

Separately, users want the org to produce more than code — graphics/assets, and other capabilities to
come ("Tools will keep growing"). The question is **how to structure shared, carrier-agnostic
capabilities** so they are built once, not duplicated per edition, and so the collection can grow.

## Decision

### 1. Add "Org Tools" as a second axis under the AI Org umbrella

```
AI Org (umbrella)
├── AI Org codex    ── carrier = codex     ┐  WHO carries
├── AI Org claude   ── carrier = claude    ┘
└── Org Tools       ── graphicist, …       ── WHAT capabilities (carrier-agnostic, shared, GROWING)
```

**editions = the runtime (controller + carrier + roles + gates) for a given carrier; Org Tools = a
growing collection of carrier-agnostic capabilities** the editions operate. A tool does not care which
carrier drives it, so it must not live inside an edition. Org Tools gets a **registry/manifest** so the
collection scales to N tools.

### 2. The media-production capability is **Corps** — a `core` engine + a division per medium

Not "hold an asset library" (passive state) but "operate media producers" (active capability). Name it
**Corps** — pronounced *"core"*, after the Beatles' **Apple Corps** (their multimedia company: Apple
Records / Films / Electronics / Publishing — one umbrella, a division per medium). We use only *"Corps"*
(no "Apple"): the trademark is theirs, the idea is fair game. The homophone is apt — the shared engine
*is* the core.

- **`core`** — the medium-agnostic ENGINE: the produce ladder, the Library, GATE/JUDGE, capture-as-asset.
  It knows nothing about graphics; a division plugs in its own providers and brief vocabulary.
- **divisions** specialise it: **`graphicist`** (graphics) first, **`composer`** (music) next.

**Two layers.** The SOURCE (held assets, or a structured model built with Blender/rules) is reusable and
grounded; the VIEW (the flat image/audio) is a disposable projection. PIL, gen-AI, Blender, the asset
library are **not** distinct architecture — they are interchangeable **providers**, the chambers of a
revolver `core` rotates through.

**The asset-first ladder** (descend only when the rung above can't cover the brief):

1. **reuse-apply** — a held asset matches as-is (GATE);
2. **reuse-process** — edit a held asset to fit (GATE);
3. **build+render** — source built from rules + view rendered **explicitly** (PIL / Blender) (GATE);
4. **synthesize** — view **synthesized** by gen-AI, conditioned on the brief; last resort (JUDGE).

Rungs 3 and 4 are *both* generation — they differ only in **explicit vs synthesized** (you write the
rules → reproducible/auditable, vs a model supplies unspecified content from priors). That is a
*verification* difference, not a structural one: PIL and gen-AI are the same structural role (produce the
view). The real structural contrast is **source-builders (Blender / scene / assets) vs view-producers
(PIL / gen-AI)** — which is exactly "asset = source of truth, image = disposable view".

Two rules keep it grounded and shrinking:

- **capture-as-asset** — any generated output is captured into the library, so the same gap is covered by
  an asset next time and **synthesis self-shrinks toward zero** (settledness for media; cf. ADR-0005);
- **two-regime verification** — the explicit path (rungs 1–3) is a **GATE** (reproducible, traceable);
  the synthesized path (rung 4) is judged by **stefan** (aesthetic + brief fidelity) **plus a grounding
  audit** (why no asset covered it; is the view a projection of a grounded source, not a free
  hallucination).

The generative/perceptual "flavour" is thereby **quarantined inside the synthesize rung + stefan**; the
deterministic controller core and the explicit pipeline are untouched.

### 3. The controller calls Org Tools **directly** — not via MCP

Our controller is a **deterministic orchestrator** (ADR-0004 Python-ification): it knows which tool to
call and what to pass (the implementer's output → the graphicist). In Anthropic's own taxonomy this is a
**workflow** ("LLM and tools orchestrated through predefined code paths"), not an **agent** ("LLM
dynamically directs its own tool usage"). MCP's value — model-agnostic *dynamic* tool discovery for an
LLM-in-the-loop — is therefore **absent here**, while its costs (JSON-RPC, tool discovery, session
management, large tool-definition token overhead) are pure waste for a hardcoded controller→tool call.

**Internally: direct function/service call.** Reserve MCP for the only cases that need it — an external
ecosystem client, or a carrier that must call a tool dynamically *mid-reasoning* — as a thin optional
adapter on a protocol-independent core.

### 4. Home: new repo as source of truth, vendored into editions with a CI drift-check (the synthesis)

Pure vendoring re-creates the very duplication Org Tools exists to kill; a pure cross-repo dependency
fights our offline `box`/dogfood runtime. Take the middle:

| home | single source | self-contained (box) | atomic change | extra machinery |
|------|:---:|:---:|:---:|---|
| A. new repo, editions depend | ◎ | △ (must fetch) | ✗ | medium (separate CI/dep) |
| B. plain vendoring | ✗ (re-duplicates) | ◎ | ◎ | small |
| **C. new repo + synced vendor (chosen)** | **◎** | **◎** | ○ | small–medium (sync + CI check) |

- canonical code lives in **`ai-org-tools`** (its own tests, ADRs, references, tool registry);
- a **sync script** copies it into each edition's `vendor/ai-org-tools/`, and **CI fails if a vendored
  copy drifts** from canonical;
- → single source of truth (duplication truly gone) × self-contained editions (box/dogfood stay
  in-repo, offline) × drift detection.

## Consequences

- Cross-edition duplication ends for shared capabilities; new tools are added once.
- Org Tools is positioned to grow (registry + per-tool structure); it is also the natural home to later
  absorb the shared **controller core**, leaving editions as thin carrier adapters.
- The org does not become a different org: its deterministic, GATE-verified engineering core is
  unchanged; the generative/perceptual capability is contained in the graphicist tool + the stefan
  JUDGE, behind a direct controller call.

## Grounding (prior art — real sources, not self-made demos)

- **MCP is the model-agnostic tool standard, and the right *external* face** — but a workflow that
  hardcodes its tool calls does not need it: [MCP](https://github.com/modelcontextprotocol);
  [When to use MCP vs API vs Tool-call](https://jamwithai.substack.com/p/when-to-use-mcp-vs-api-vs-functiontool);
  [You Probably Don't Need MCP](https://nocodeapi.com/tutorials/you-probably-dont-need-mcp-when-direct-apis-beat-protocol-complexity/).
- **Workflow vs agent (the decisive distinction):**
  [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
  (workflows = predefined code paths; agents = dynamic tool use; prefer the simplest solution).
- **Role-based agent orgs (the "AI Org" pattern), incl. a designer role:** MetaGPT; ChatDev
  ([IBM — What is ChatDev?](https://www.ibm.com/think/topics/chatdev)).
- **The graphicist already exists in the wild** — an LLM operating Blender, fetching from an asset
  library and generating: [blender-mcp](https://github.com/ahujasid/blender-mcp) (Claude + `bpy` +
  Poly Haven assets + Hyper3D generation).
- **Library-grounded vs from-scratch generation:**
  [AI 3D asset tools (Meshy)](https://www.meshy.ai/blog/best-ai-tools-for-3d-game-assets);
  Scenario (trains on *your* asset library for style consistency) vs Meshy/Hyper3D (generate from
  scratch) — our ladder + capture-as-asset sits on the library-grounded end.
