```
VERDICT: needs-decision (standing_rule). Switching means replacing Firebase Crashlytics and running our own crash server, and both are ruled out under "Already decided". My lean is skip: nothing in the item shows it cuts noise better than Crashlytics, which already groups crashes and ranks the top ones. Self-hosting may also cost money (money), which this item does not settle.

WHAT IT IS: example-org/crashbin, a GitHub repo. Apache-2.0, 3,400 stars, last push 2026-09-20, not archived, default branch main. This comes from a saved snapshot and meta.json captured 2026-10-08, not a live read. No commit sha was captured.

CLAIMS CHECKED:
- "It is free" (sender). Split:
  - The license costs nothing (Apache-2.0): CONFIRMED by meta.json and the README.
  - Running it costs nothing: UNVERIFIED. The README says "You run the server yourself (Docker image, one container plus a database)". Hosting, storage and upkeep are not priced anywhere in the item.
- "We have to run our own server": CONFIRMED by the item's own text. [verdict rests on this]
- "Has a Unity SDK": PROBABLE. The README says so, but the SDK code was not read.
- "Groups crashes by stack and shows the top crashes and trends": PROBABLE. The README says so, with no detail on how grouping or deduplication works.
- "Switching would help goal 2 (cut noise so the top five are worth fixing)" (sender's implied claim): UNVERIFIED. The item claims no better grouping, filtering or noise reduction than standard crash reporters.
- Popularity and health: 3,400 stars and a push on 2026-09-20 are CONFIRMED facts. They show the project is active, not that its grouping is good.

FIT:
- Goal: goal 2 by topic only. No evidence it reduces noise.
- Overlap: Firebase Crashlytics, already in use, does the same job: collects crashes, groups them by stack and ranks the top issues. This would be a replacement, not a new capability.
- Burden: a new server we would have to run (container plus database), plus its upgrades and backups and a new SDK in the game. It also breaks "we run no backend of our own".
- Cost: free under Apache-2.0. Hosting cost is unknown. The $0 tool budget needs approval for any spend.
- Risks: Apache-2.0 is allowed for code we ship, so the SDK license is fine. Player crash data would go to a server we run, not a third party, but we would own its security and retention. A two-way migration away from Crashlytics would also split our crash history from our analytics.

NEXT ACTION: The operator decides whether to reopen "Firebase stays our crash service; we run no backend of our own". If not, close this as skip. Goal 2 is better pursued inside Crashlytics. Owner: operator. Done when: the decision is recorded in the context file. Hand-off: none.

CONFIDENCE: medium. Limited by working from a short saved snapshot rather than the live repo, the SDK and grouping code not being read, and no hosting cost being stated. The conflict with the standing rule is itself clear.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "standing_rule",
  "item": {"type": "repo", "identity": "example-org/crashbin (Apache-2.0, 3400 stars, last push 2026-09-20, not archived, default branch main; snapshot captured 2026-10-08, no sha)",
           "resolved": true},
  "claims": [
    {"claim": "the software license is free (Apache-2.0)", "evidence": "meta.json license field and README: License: Apache-2.0", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "running it is free", "evidence": "README: you run the server yourself (Docker container plus a database); no hosting cost stated", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "it requires running our own server", "evidence": "README: You run the server yourself (Docker image, one container plus a database)", "status": "CONFIRMED"},
    {"claim": "has a Unity SDK", "evidence": "README lists SDKs for Unity, Unreal and native Android; SDK code not read", "status": "PROBABLE", "load_bearing": false},
    {"claim": "groups crashes by stack and shows top crashes and trends", "evidence": "README description only, no detail on grouping", "status": "PROBABLE", "load_bearing": false},
    {"claim": "switching would cut crash-report noise (goal 2)", "evidence": "sender's implied claim; item claims no better grouping or filtering than other reporters", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "3,400 stars and a push on 2026-09-20", "evidence": "meta.json captured 2026-10-08", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 2 (crash-report noise) by topic only; no evidence it reduces noise",
          "overlap": "Firebase Crashlytics already collects, groups and ranks crashes; this would replace it",
          "burden": "self-hosted server (container plus database) to run, upgrade and back up; new SDK in the game; migration off Crashlytics",
          "risks": ["breaks the decision that Firebase stays and we run no backend of our own",
                    "we would own security and retention of player crash data",
                    "crash history split from Firebase analytics",
                    "Apache-2.0 is allowed for shipped code"],
          "cost": {"price": "free software; hosting cost unknown", "tier": "open source, self-hosted", "limits": "none stated",
                   "terms": "Apache-2.0", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Decide whether to reopen the standing decision that Firebase stays our crash service and we run no backend; if not, close as skip and pursue goal 2 within Crashlytics",
                  "owner": "operator", "done_when": "the decision is recorded in the context file", "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```