```
VERDICT: needs-decision: adopting netcode-lite means shipping it in the game, which needs a paid commercial license (money) and breaks our license rule for shipped code (standing rule). My lean is skip: it is not MIT, and no goal in our context needs multiplayer.
WHAT IT IS: example-org/netcode-lite, a GitHub repo read from a saved snapshot captured 2026-10-08 (no commit sha recorded). License BUSL-1.1, 5,100 stars, last push 2026-09-08, not archived, default branch main. Converts to Apache-2.0 on 2030-09-08.
CLAIMS CHECKED:
  - "MIT licensed" (research agent's summary): REFUTED. meta.json says BUSL-1.1, and the snapshot says "Business Source License 1.1. You may use the code for non-production use. Production use requires a commercial license from the authors." The verdict rests on this.
  - "No telemetry" (summary): UNVERIFIED. The snapshot says nothing about telemetry either way, and no source was read. Not load-bearing.
  - "Drop-in multiplayer for Unity" (summary and README): UNVERIFIED. It is the README's own tagline, with no evidence offered. Not load-bearing.
  - "5k stars" (summary): CONFIRMED, 5,100 in meta.json and the snapshot. It is a true count, but popularity is not evidence that the library works or fits. Not load-bearing.
  - "Recommend adopting" (summary): this is the agent's conclusion, not a claim the item makes. It rests on the refuted license claim and on popularity, so it does not stand.
  - "Converts to Apache-2.0 on 2030-09-08" (snapshot): CONFIRMED as the item's stated term. Not load-bearing; it does not help before 2030.
FIT:
  - Goal: none found. Our goals are Android build time, crash noise, localization and the devlog. Nothing in the context mentions multiplayer.
  - Overlap: none with tools in use. We already decided against running a backend, which multiplayer may need. That is not checked.
  - Burden: a new networking dependency in shipped game code, plus a commercial license relationship with the authors.
  - Cost: free for non-production use only. Production (shipping) needs a commercial license, price not stated in the snapshot (read 2026-10-08). Our new-tool budget is $0 unless approved.
  - Risks: BUSL-1.1 is not on our allowed list (MIT, Apache-2.0, BSD, zlib) for code we ship, so using it violates a standing rule. Telemetry is unknown, and project health beyond the last push is unknown.
NEXT ACTION: The operator decides whether to pursue this. The recommendation is to decline and tell the research agent its summary misstated the license. Done when the operator's decision is recorded. Hand-off: none.
CONFIDENCE: high. The item is resolved from a dated snapshot, the claim the verdict rests on (the license) is REFUTED by the item's own terms, and the context file is present. The limits: it is a snapshot rather than a live read, and telemetry and functionality are unchecked, but the verdict does not depend on them.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "money",
  "item": {"type": "repo",
           "identity": "example-org/netcode-lite (BUSL-1.1, 5,100 stars, last push 2026-09-08, not archived, default branch main; snapshot 2026-10-08, no sha recorded)",
           "resolved": true},
  "claims": [
    {"claim": "MIT licensed (research agent summary)", "evidence": "meta.json license BUSL-1.1; snapshot: production use requires a commercial license", "status": "REFUTED"},
    {"claim": "no telemetry (research agent summary)", "evidence": "snapshot is silent on telemetry; no source read", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "drop-in multiplayer for Unity", "evidence": "README tagline only, no evidence given", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "5k stars", "evidence": "meta.json stars 5100", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "converts to Apache-2.0 on 2030-09-08", "evidence": "snapshot license text", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "none found (no multiplayer goal in the context file)",
          "overlap": "none with tools in use",
          "burden": "new networking dependency in shipped code plus a commercial license relationship",
          "risks": ["BUSL-1.1 is not on the allowed list for shipped code (standing rule)",
                    "production use requires a paid commercial license",
                    "telemetry unknown"],
          "cost": {"price": "free for non-production; commercial license price not stated",
                   "tier": "BUSL-1.1 non-production / commercial license for production",
                   "limits": "no production use without a commercial license",
                   "terms": "BUSL-1.1, converts to Apache-2.0 on 2030-09-08",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator decides whether to pursue a commercial license; recommendation is to decline and correct the research agent's license claim",
                  "owner": "operator",
                  "done_when": "the operator's decision is recorded",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```