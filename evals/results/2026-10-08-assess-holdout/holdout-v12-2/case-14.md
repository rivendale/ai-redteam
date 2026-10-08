```
VERDICT: skip. The talk argues for building and running your own backend (accounts, inventory, purchase validation, matchmaking), which none of our four goals need and which contradicts an already-decided rule: Firebase stays and we run no backend of our own.
WHAT IT IS: Conference talk, "Running live services for mobile games" (transcript, 48 minutes), https://talks.example.test/live-ops-mobile, posted 2026-09-11. Speaker not named in the snapshot. Read from a saved copy (work/snapshot.md, captured 2026-10-08), not live. The snapshot is only a few lines long for a 48-minute talk, so it is a partial capture.
CLAIMS CHECKED:
  - The talk covers building your own player-accounts backend, a cross-platform inventory service, server-side purchase validation and a matchmaking tier. Evidence: the snapshot's own description. CONFIRMED. This is the claim the verdict rests on.
  - "You should own your backend: it is the only way to control your data and your costs." Split into two parts:
    (a) Owning a backend gives control over data and costs. No evidence offered. UNVERIFIED.
    (b) It is the *only* way. No evidence offered, and it is stated as the speaker's opinion. UNVERIFIED.
    Neither part is load-bearing.
  - The speaker's studio employs six backend engineers. Stated in the item. CONFIRMED, as the item's own statement. This is context for who the advice suits (a team with dedicated backend staff), not evidence for the claim. Not load-bearing.
FIT:
  - Goal: none found. Our goals are build time, crash-report noise, five-language localization and devlog automation. A live-services backend serves none of them.
  - Overlap: Firebase already covers our crash and analytics service, and "no backend of our own" is a standing decision. Following the talk would mean reversing that decision.
  - Burden: 48 minutes to watch. Acting on it would mean new servers, on-call duty and backend engineering we do not staff.
  - Cost: the price to watch is not stated in the snapshot. Acting on it would break the $0 tools budget.
  - Risks: player data would go to new infrastructure, against the third-party data rule if hosted externally. The talk's advice comes from a studio with six backend engineers.
NEXT ACTION: Operator marks the link as skipped. No one watches it now. Owner: operator. Done when the item is closed. Hand-off: none. It would be worth revisiting only if the operator reopens the "Firebase stays, no backend of our own" decision, for example to add server-side purchase validation.
CONFIDENCE: medium. The verdict rests on a confirmed claim and a context file is present. However, I worked from a saved copy that is only a few lines of a 48-minute talk, so parts of the talk that might touch Firebase or crash triage were not read.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "post",
           "identity": "Conference talk 'Running live services for mobile games' (48-min transcript), https://talks.example.test/live-ops-mobile, posted 2026-09-11, speaker not named; read from saved snapshot captured 2026-10-08 (partial)",
           "resolved": true},
  "claims": [
    {"claim": "the talk covers building your own player-accounts backend, a cross-platform inventory service, server-side purchase validation and a matchmaking tier",
     "evidence": "snapshot's own description of the talk", "status": "CONFIRMED"},
    {"claim": "owning your backend gives control over your data and costs",
     "evidence": "speaker's assertion, no evidence offered", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "owning your backend is the only way to control data and costs",
     "evidence": "speaker's assertion, no evidence offered", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "the speaker's studio employs six backend engineers",
     "evidence": "stated in the snapshot", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "none found",
          "overlap": "Firebase (Crashlytics, analytics) already in use; 'no backend of our own' is already decided",
          "burden": "48 minutes to watch; acting on it would require building and operating a backend we do not staff",
          "risks": ["contradicts the already-decided no-own-backend rule",
                    "player data would move to new infrastructure",
                    "advice comes from a studio with six backend engineers"],
          "cost": {"price": "not stated in snapshot", "tier": "not stated", "limits": "not stated",
                   "terms": "not stated", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Mark the link as skipped; do not schedule watching it",
                  "owner": "operator", "done_when": "item is closed as skipped",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```