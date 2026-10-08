VERDICT: watch. The roundup cannot answer "which one for goal 1": it says it did not benchmark the seven tools and that the right one depends on where build time goes, which we have not measured. Once a profile of our Android release build shows the main cost, this post becomes a useful shortlist.

WHAT IT IS: Post "Seven Unity build accelerators compared", posted 2026-09-18, read from the saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json). The snapshot names no author. It is a one-paragraph roundup with one-line descriptions, and gives no links, licenses, prices or versions.

CLAIMS CHECKED:
- The sender says the roundup "compares seven Unity build accelerators." This splits into two claims:
  - It lists seven tools with a one-line role each: **CONFIRMED** (BuildLane, Cachefox, Shardwright, Packrat, HotSwapper, Tidewater, Quickbake). *Load-bearing.*
  - It compares them in a way that could pick one: **REFUTED** by its own text: "We did not benchmark them against each other" and "No single winner." *Load-bearing.*
- Its one-line descriptions of each tool are **UNVERIFIED**. They are the post's own summaries, and the snapshot has no source for them. Examples: BuildLane is a "cloud cache, paid", Cachefox is a "self-hosted cache, free", Tidewater is a "CI plugin for Jenkins" and HotSwapper is "editor only". Not load-bearing.
- "Which helps depends on whether your time goes to shader compilation, asset import or packaging" is **UNVERIFIED**. It is plausible, but the post gives no evidence. Not load-bearing.

FIT:
- **Goal:** goal 1, getting the Android release build under 10 minutes.
- **Overlap:** we have no build cache or accelerator today. Jenkins on the Mac mini is our CI, so Tidewater, a Jenkins plugin according to the post, would sit on top of a tool we already use.
- **Ruled out for goal 1 by the post's own descriptions:**
  - HotSwapper is editor only, so it does nothing for release builds.
  - Shardwright splits scenes across machines, and we have one build machine.
- **Burden:** unknown until a tool is chosen. Cachefox would mean running a cache server ourselves.
- **Cost:** BuildLane is paid, which needs operator approval against a $0 budget and the no-new-subscription rule. Cachefox is free according to the post. The others are not stated. Nothing was read from the vendors, as of 2026-10-08.
- **Risks:**
  - No licenses are given. Build tools are run, not shipped, so GPL or AGPL would be acceptable, but each license still needs checking.
  - BuildLane's cloud cache would send our build artifacts to a new party.
  - macOS and Windows support is not stated for any tool.

NEXT ACTION:
- **Action:** Profile one Android release build on the Jenkins Mac mini, using Unity's build report and Editor.log timings, and split the wall time into shader compilation, asset import and packaging.
- **Owner:** operator, or whoever maintains Jenkins.
- **Done when:** one build's time is broken down by phase, with the largest phase named. That phase then maps to a candidate from the post: Quickbake for shaders, Cachefox, Packrat or BuildLane for import or caching, Tidewater for CI. That candidate gets its own `assess` against its real repo or page.
- **Hand-off:** none.

CONFIDENCE: high. The item is resolved from a dated snapshot, the claims the verdict rests on are settled by the post's own text, and the context file is present. The per-tool facts come from the post alone and are not verified, but the verdict does not depend on them.

```json
{
  "schema_version": "assess-1",
  "verdict": "watch",
  "item": {"type": "post",
           "identity": "\"Seven Unity build accelerators compared\", posted 2026-09-18, author not given; saved snapshot captured 2026-10-08",
           "resolved": true},
  "claims": [
    {"claim": "the roundup lists seven Unity build accelerators (sender: 'compares seven')",
     "evidence": "snapshot names BuildLane, Cachefox, Shardwright, Packrat, HotSwapper, Tidewater, Quickbake with one-line roles",
     "status": "CONFIRMED"},
    {"claim": "the roundup compares them well enough to pick one (sender's framing)",
     "evidence": "its own text: 'We did not benchmark them against each other' and 'No single winner'",
     "status": "REFUTED"},
    {"claim": "per-tool descriptions (BuildLane paid cloud cache, Cachefox free self-hosted, Tidewater Jenkins plugin, HotSwapper editor only, etc.)",
     "evidence": "the post's one-liners only; no links, licenses or sources",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "which tool helps depends on whether time goes to shader compilation, asset import or packaging",
     "evidence": "stated without evidence",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 1: Android release build under 10 minutes",
          "overlap": "no build cache or accelerator in use; Jenkins already in use (Tidewater would plug into it); HotSwapper is editor only and Shardwright needs several machines, we have one",
          "burden": "unknown until a tool is chosen; Cachefox means running a cache server",
          "risks": ["no licenses stated (tools are run, not shipped, so GPL/AGPL acceptable but unchecked)",
                    "BuildLane cloud cache sends build artifacts to a new party",
                    "macOS and Windows support not stated for any tool"],
          "cost": {"price": "BuildLane paid (amount not given); Cachefox free; others not stated",
                   "tier": "not stated", "limits": "not stated", "terms": "not stated",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Profile one Android release build on the Jenkins Mac mini (Unity build report and Editor.log timings) and split wall time into shader compilation, asset import and packaging",
                  "owner": "operator",
                  "done_when": "one build's time is broken down by phase and the largest phase is named, so it can be mapped to one candidate for its own assess",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```