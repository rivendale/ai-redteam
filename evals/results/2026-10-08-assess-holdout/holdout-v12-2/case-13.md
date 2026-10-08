```
VERDICT: watch. The post cannot answer "which one for goal 1": it says it did not benchmark the tools and that the right one depends on where build time goes, which we have not measured. Revisit it once the Android build is profiled.
WHAT IT IS: Post "Seven Unity build accelerators compared" (posts.example.test, posted 2026-09-18). Read from a saved snapshot captured 2026-10-08; author not shown in the snapshot. It gives a one-line description of each of seven tools (BuildLane, Cachefox, Shardwright, Packrat, HotSwapper, Tidewater, Quickbake), with no prices, licenses, links or measurements.
CLAIMS CHECKED:
  1. Sender's premise that the roundup "compares" the tools well enough to pick one. REFUTED by the post itself: "We did not benchmark them against each other" and "No single winner." (verdict rests on this)
  2. "We did not benchmark them against each other." CONFIRMED: the post states it, and it contains no numbers. (verdict rests on this)
  3. "Which helps depends on whether your time goes to shader compilation, asset import or packaging." PROBABLE: no evidence is given, but the claim matches how the tools are described (Quickbake for shaders, Cachefox/BuildLane/Packrat for caches and bundles). (verdict rests on this)
  4. The one-line descriptions (BuildLane is a paid cloud cache, Cachefox is a free self-hosted cache, Tidewater is a Jenkins CI plugin, HotSwapper is editor only, and so on). UNVERIFIED: no source, price or license is given. (not load-bearing)
FIT:
  Goal: goal 1 (Android release build under 10 minutes). The post points at candidates and does not choose among them.
  Overlap: Jenkins on one Mac mini is already the CI. Tidewater would plug into it and not replace it. HotSwapper is editor only, so it does nothing for release builds.
  Burden: depends on the tool. Shardwright needs several build machines and we have one. A self-hosted cache (Cachefox) is a new service to maintain.
  Cost: reading the post is free (2026-10-08). The post lists no tool prices. BuildLane is described as paid, which would need operator approval because the quarter's budget is $0.
  Risks: no licenses are given for any tool. Build tools are not shipped, so GPL/AGPL would be allowed. BuildLane's cloud cache would send project assets to a new party (not player data, but still a new account). macOS and Windows support is not stated for any tool.
NEXT ACTION: Profile one Android release build on the Jenkins Mac mini and split its time into shader compilation, asset import and packaging, using Unity's build report and Editor.log timings. Owner: operator or build owner. Done when: one build's minutes are attributed to those three buckets. Then re-run assess on the one or two tools that match the largest bucket, read from their own pages. Hand-off: none.
CONFIDENCE: high. The verdict rests only on what the post says about itself, which is clear. Limits: this was read from the 2026-10-08 snapshot, and nothing here judges any individual tool.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "watch",
  "item": {"type": "post",
           "identity": "\"Seven Unity build accelerators compared\", posts.example.test, posted 2026-09-18 (snapshot captured 2026-10-08, author not shown)",
           "resolved": true},
  "claims": [
    {"claim": "the roundup compares the seven tools well enough to pick one for us (sender's premise)",
     "evidence": "post: \"We did not benchmark them against each other\" and \"No single winner\"",
     "status": "REFUTED"},
    {"claim": "the tools were not benchmarked against each other",
     "evidence": "stated in the post; no measurements appear in it",
     "status": "CONFIRMED"},
    {"claim": "which tool helps depends on whether time goes to shader compilation, asset import or packaging",
     "evidence": "the post's own reasoning, no data; consistent with the tool descriptions",
     "status": "PROBABLE"},
    {"claim": "per-tool descriptions (BuildLane paid cloud cache, Cachefox free self-hosted cache, Tidewater Jenkins plugin, etc.)",
     "evidence": "one line each, no links, prices or licenses",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 1: Android release build under 10 minutes (points at candidates, does not pick one)",
          "overlap": "Jenkins on the Mac mini is the existing CI; Tidewater would extend it, not replace it; HotSwapper is editor only and does not affect release builds",
          "burden": "varies: Shardwright needs several build machines (we have one); a self-hosted cache is a new service to maintain",
          "risks": ["no licenses stated for any tool (build-only use allows GPL/AGPL)",
                    "BuildLane cloud cache would send project assets to a new party and add a paid account",
                    "macOS and Windows support not stated"],
          "cost": {"price": "free to read; tool prices not given (BuildLane described as paid)",
                   "tier": "n/a", "limits": "n/a", "terms": "not stated",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Profile one Android release build on the Jenkins Mac mini and split its time into shader compilation, asset import and packaging, then re-assess the tools matching the largest bucket",
                  "owner": "operator or build owner",
                  "done_when": "one build's minutes are attributed to those three buckets",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```