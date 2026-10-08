```
VERDICT: skip. It serves none of our four goals, and the repo has had no commits since 2023-02-14, so 28k stars do not make it solid.
WHAT IT IS: example-org/assetflow, default branch main (no sha in the snapshot). MIT license. 28,000 stars. Last push 2023-02-14, about 3 years 8 months before capture. Not archived. 410 open issues. The newest issue asks "does this work with Unity 6?" and has no reply. Source: the saved snapshot and meta.json captured 2026-10-08, not a live read.
CLAIMS CHECKED:
  - "28k stars" (sender and snapshot): meta.json says stars 28000. CONFIRMED. This is a true count and nothing more.
  - "so it has to be solid" (sender): this is an inference from popularity, and popularity is not evidence. The item gives no tests, no release notes and no maintenance record. What it does show points the other way: no push in 3.7 years and 410 open issues. UNVERIFIED.
  - "Used by thousands of games" (snapshot): no list, source or method is given. UNVERIFIED.
  - Asynchronous asset loading for Unity (snapshot): this is the item's own one-line description, and no code was read. PROBABLE.
  - Works with Unity 6, which we use: the item does not say. The only evidence is an unanswered issue asking that question. UNVERIFIED.
  - Last push 2023-02-14 and not archived (meta.json): CONFIRMED. The verdict rests on this.
  - License is MIT (meta.json and snapshot): CONFIRMED. MIT is allowed for code we ship.
FIT:
  - Goal: none found. Our goals are Android build time, crash noise, five languages and the devlog. Runtime asset loading speeds none of them up, and it does not shorten the release build (goal 1).
  - Overlap: Unity 6 is already in use and ships its own asset-loading path (Addressables). The context file does not list it as in use, so this is a probable overlap, not a confirmed one.
  - Burden: a dependency we would ship in the game. It looks unmaintained, so any Unity 6 breakage would fall on us.
  - Cost: free and MIT, read 2026-10-08 from the snapshot.
  - Risks: project health (stale for 3.7 years, 410 issues, Unity 6 support unknown); shipping an unmaintained library inside the game. No telemetry or data flow is described in the snapshot, but the code was not read.
NEXT ACTION: The operator replies to the sender: skip assetflow. It matches none of our goals and has been unmaintained since 2023, and star count is not a reason to adopt. Revisit only if a runtime asset-loading problem shows up on the goal list. Done when the reply is sent. Hand-off: none.
CONFIDENCE: medium. The context file is present and the facts the verdict rests on are confirmed. Two things limit it: the snapshot is a thin saved copy with no code and no sha, and I could not check live whether the repo has changed since capture or whether Addressables is already in our project.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "repo",
           "identity": "example-org/assetflow (main, no sha in snapshot; MIT, last push 2023-02-14, not archived, 410 open issues; snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "the repo has 28k stars", "evidence": "meta.json: stars 28000", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "28k stars, so it has to be solid", "evidence": "popularity only; no tests, releases or maintenance record offered; last push 2023-02-14 and 410 open issues", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "used by thousands of games", "evidence": "snapshot assertion with no list, source or method", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "asynchronous asset loading for Unity", "evidence": "the repo's own one-line description; no code read", "status": "PROBABLE", "load_bearing": false},
    {"claim": "works with Unity 6", "evidence": "nothing in the item settles it; newest issue asks and has no reply", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "last push 2023-02-14 and not archived", "evidence": "meta.json last_push and archived fields; snapshot last commit date", "status": "CONFIRMED"},
    {"claim": "license is MIT", "evidence": "meta.json license field and snapshot", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "none found (goals are Android build time, crash noise, five languages, devlog; runtime asset loading serves none)",
          "overlap": "Unity 6 is in use and has its own asset-loading path (Addressables); not listed in the context file, so probable overlap",
          "burden": "a shipped in-game dependency that appears unmaintained; any Unity 6 fixes would fall on us",
          "risks": ["no push since 2023-02-14 with 410 open issues", "Unity 6 compatibility unknown, question unanswered", "MIT is allowed for shipped code", "code not read, so telemetry and data flow are unchecked"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Reply to the sender: skip assetflow; it serves none of our goals and has been unmaintained since 2023, and stars are not a reason to adopt",
                  "owner": "operator", "done_when": "the reply is sent",
                  "stop_condition": "n/a (not a trial)", "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```