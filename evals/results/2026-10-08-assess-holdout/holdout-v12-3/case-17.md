```
VERDICT: skip. It serves none of our four goals, has had no commits for over three and a half years, and nobody has answered whether it works with Unity 6. The 28,000 stars do not change either fact.
WHAT IT IS: example-org/assetflow, read from a saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json),
  not live. No commit sha was recorded. It is an asynchronous asset loader for Unity. License MIT, default branch main,
  not archived, last push 2023-02-14 (about 3 years 8 months before capture), 410 open issues, 28,000 stars. The
  newest issue asks "does this work with Unity 6?" and has no reply.
CLAIMS CHECKED:
  - "28,000 stars" (meta.json and snapshot): CONFIRMED as a count. Not load-bearing.
  - Sender's inference "28k stars, so it has to be solid": UNVERIFIED. Stars measure popularity, not reliability. The
    item gives no tests, benchmarks or changelog that would show it is solid, and its 410 open issues and lack of
    commits since 2023 point the other way. Not load-bearing.
  - "Used by thousands of games": UNVERIFIED. It is a quote with no list, source or method behind it. Not load-bearing.
  - Works with Unity 6, our engine (implied by the request): UNVERIFIED. The last commit predates Unity 6, and the only
    question about it is unanswered. Not load-bearing, because the verdict already holds without it.
  - Last commit 2023-02-14, no maintainer activity since: CONFIRMED (meta.json last_push matches the snapshot).
    Load-bearing.
FIT:
  Goal: none found. Async runtime asset loading does not shorten the Android build (goal 1), reduce crash noise
    (goal 2), help localization (goal 3) or speed up the devlog (goal 4).
  Overlap: nothing in our context file does async asset loading, so there is no recorded overlap. The context file does
    not say how the game loads assets today, so whether we need a loader at all is an open question, not a gap the item
    fills.
  Burden: a runtime dependency compiled into the shipped game. We would have to maintain it ourselves, since upstream
    is inactive, and port it to Unity 6 if it breaks.
  Cost: free, open source, MIT (read 2026-10-08 from the snapshot).
  Risks: MIT is allowed for shipped code, so the license is fine. The project is stale (no push since 2023-02-14,
    410 open issues, Unity 6 compatibility unanswered), and it is code we would ship to players. The snapshot showed no
    telemetry or network behavior either way. Nothing was installed or run.
NEXT ACTION: Operator replies to the sender: skip, because no goal is served and the project is unmaintained. Done when
  the reply is sent. If a goal about asset load times or memory is added later, open a new assessment of current
  options rather than reviving this one. Hand-off: none.
CONFIDENCE: high. The item is resolved (from a dated snapshot, not a live read), the context file is present, and the
  one load-bearing claim (no commits since 2023-02-14) is CONFIRMED. The main limit is that this is a 2026-10-08
  snapshot; any later activity would not show here.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "repo",
           "identity": "example-org/assetflow (sha not recorded; MIT, last push 2023-02-14, not archived, 410 open issues; read from snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "28,000 stars", "evidence": "meta.json stars: 28000; snapshot states the same", "status": "CONFIRMED",
     "load_bearing": false},
    {"claim": "28k stars, so it has to be solid (sender)", "evidence": "popularity only; no tests, benchmarks or changelog offered; 410 open issues and no commits since 2023-02-14", "status": "UNVERIFIED",
     "load_bearing": false},
    {"claim": "used by thousands of games", "evidence": "quoted in the README with no source or list", "status": "UNVERIFIED",
     "load_bearing": false},
    {"claim": "works with Unity 6", "evidence": "last commit predates Unity 6; newest issue asking this has no reply", "status": "UNVERIFIED",
     "load_bearing": false},
    {"claim": "last commit 2023-02-14, no activity since", "evidence": "meta.json last_push and snapshot agree", "status": "CONFIRMED"}
  ],
  "fit": {"goal": "none found (goals 1-4 are build time, crash noise, localization, devlog)",
          "overlap": "none recorded in the context file; how the game loads assets today is not stated",
          "burden": "runtime dependency shipped in the game; would need self-maintenance and a possible Unity 6 port",
          "risks": ["MIT, allowed for shipped code", "stale: no push since 2023-02-14, 410 open issues", "Unity 6 compatibility unanswered"],
          "cost": {"price": "free", "tier": "open source", "limits": "none", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Reply to the sender: skip, because no goal is served and the project is unmaintained since 2023-02-14",
                  "owner": "operator", "done_when": "the reply is sent",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```