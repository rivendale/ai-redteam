VERDICT: watch. The post cannot tell you which tool to use for goal 1: it says there is "no single winner" and that it "did not benchmark them against each other". The choice depends on where our Android build time goes, and we have not measured that yet.

WHAT IT IS: A post, "Seven Unity build accelerators compared", posted 2026-09-18 at https://posts.example.test/build-accelerators-2026. I read it from a saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json). No author is named in the snapshot. It is a short roundup with one line per tool: BuildLane (cloud cache, paid), Cachefox (self-hosted cache, free), Shardwright (splits scenes across machines), Packrat (asset bundle cache), HotSwapper (editor only), Tidewater (CI plugin for Jenkins) and Quickbake (shader precompile). It gives no prices, licenses, versions or links to the tools.

CLAIMS CHECKED:
- **Load-bearing. Sender's question: one of the seven can be picked from this roundup.** REFUTED. The post says "No single winner: each fits a different bottleneck" and "Which helps depends on whether your time goes to shader compilation, asset import or packaging."
- **Load-bearing. The tools were not benchmarked against each other.** CONFIRMED. The post says so itself ("We did not benchmark them against each other"). Nothing in it measures speed-ups.
- **Each tool fits a different bottleneck.** UNVERIFIED. This is the author's framing, and the post offers no data for it.
- **The per-tool descriptions** (BuildLane is paid, Cachefox is free and self-hosted, Tidewater is a Jenkins plugin, HotSwapper is editor only, and so on). UNVERIFIED. These are one-line summaries, not the tools' own pages. Not load-bearing.

FIT:
- **Goal:** goal 1, "Get the Android release build under 10 minutes."
- **Overlap:** none of the seven is in use. Tidewater would add to our existing Jenkins rather than replace it.
- **What the post suggests about each tool:**
  - HotSwapper is editor only, so it would not shorten release builds.
  - Shardwright splits scenes across machines, and we have one Mac mini.
  - BuildLane is a paid cloud cache. It would mean money, a new account and build data going to a new party, so it needs the operator's approval under our constraints.
- **Burden:** unknown until one tool is chosen. A self-hosted cache (Cachefox) or a Jenkins plugin (Tidewater) adds upkeep on the Mac mini.
- **Cost:** the post gives no prices. Only BuildLane is described as paid. Our budget is $0 unless approved.
- **Risks:** license, telemetry and project health are not stated for any tool. These are build tools we run and never ship, so GPL or AGPL would be acceptable. Each tool still needs its own check before a trial.

NEXT ACTION: Profile one Android release build on the Jenkins Mac mini. Split its time into shader compilation, asset import and packaging (plus anything else that is large).
- **Owner:** operator, or whoever maintains the Jenkins job.
- **Done when:** a timing breakdown of one release build exists and the largest phase is named.
- **After that:** assess the one matching tool from its own page: Quickbake for shaders, Cachefox or Packrat for import or bundles, Tidewater for CI. BuildLane only goes ahead with operator approval.
- **Hand-off:** none, since this is choosing a tool, not borrowing ideas.

CONFIDENCE: medium. The post was read in full, the context file is present, and the load-bearing claims are settled by the post's own words. What limits confidence is that the post is a thin summary and none of the seven tools was read directly, so the shortlist after profiling is unconfirmed.

```json
{
  "schema_version": "assess-1",
  "verdict": "watch",
  "item": {"type": "post", "identity": "\"Seven Unity build accelerators compared\", posted 2026-09-18, https://posts.example.test/build-accelerators-2026 (saved snapshot captured 2026-10-08; author not named)",
           "resolved": true},
  "claims": [
    {"claim": "one of the seven tools can be picked for our build from this roundup (sender's question)",
     "evidence": "the post says 'No single winner: each fits a different bottleneck' and that it depends on whether time goes to shader compilation, asset import or packaging",
     "status": "REFUTED"},
    {"claim": "the tools were not benchmarked against each other",
     "evidence": "the post states 'We did not benchmark them against each other'",
     "status": "CONFIRMED"},
    {"claim": "each tool fits a different bottleneck",
     "evidence": "the author's framing; no data offered",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "per-tool descriptions (BuildLane paid cloud cache, Cachefox free self-hosted, Tidewater Jenkins plugin, HotSwapper editor only, etc.)",
     "evidence": "one-line summaries in the post; the tools' own pages were not read",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 1: Android release build under 10 minutes",
          "overlap": "none of the seven is in use; Tidewater would extend our existing Jenkins",
          "burden": "unknown until one tool is chosen; a self-hosted cache or Jenkins plugin adds upkeep on the Mac mini",
          "risks": ["licenses, telemetry and project health not stated for any tool",
                    "BuildLane is paid and cloud-hosted: money, a new account and build data to a new party need operator approval",
                    "HotSwapper is editor only and Shardwright needs several machines; neither fits our single Mac mini release build"],
          "cost": {"price": "not stated in the post (BuildLane described as paid, Cachefox as free)", "tier": "not stated",
                   "limits": "not stated", "terms": "not stated", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Profile one Android release build on the Jenkins Mac mini and split its time into shader compilation, asset import and packaging; then assess only the matching tool from its own page",
                  "owner": "operator (or whoever maintains the Jenkins job)",
                  "done_when": "a timing breakdown of one release build exists and the largest phase is named",
                  "stop_condition": "stop if the build is already under 10 minutes or the largest phase is not one any of these tools targets",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```