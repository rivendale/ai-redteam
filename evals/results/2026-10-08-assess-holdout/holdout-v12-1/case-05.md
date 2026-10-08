```
VERDICT: needs-decision (standing_rule): switching to crashbin means running our own crash server and dropping Firebase, which reverses two "already decided" rules ("Firebase stays our crash and analytics service; we run no backend of our own"); my lean is skip, because nothing in the item shows it cuts crash noise better than the Crashlytics grouping we already have.
WHAT IT IS: example-org/crashbin, default branch main (no commit sha captured), Apache-2.0, 3,400 stars, last push and last release 2026-09-20, not archived. Read from a saved snapshot and meta.json captured 2026-10-08, not live. A self-hosted crash reporter for mobile games: a Docker server (one container plus a database), a web dashboard, and SDKs for Unity, Unreal and native Android.
CLAIMS CHECKED:
  - "crashbin is free" (sender), split into two parts:
    (a) The software costs nothing to license: CONFIRMED (Apache-2.0 per meta.json and README).
    (b) Switching costs nothing: UNVERIFIED. The item says you run the server and database yourself. Hosting, uptime, backups and upgrades are new costs and work, and nothing in the item puts a number on them.
  - "You run the server yourself (one container plus a database)": CONFIRMED by the item's own text. Load-bearing: this is the conflict with "we run no backend of our own".
  - "Groups crashes by stack, shows top crashes and trends": PROBABLE (README description; no code or screenshots in the snapshot). This is the same job Crashlytics already does.
  - "Has a Unity SDK": PROBABLE (README statement; SDK not inspected). It would fit our Unity 6 stack if true.
  - Implied by the sender: "it would serve goal 2 (cut crash-report noise)": UNVERIFIED. The item says nothing about deduplication rules, noise filtering or prioritization beyond the stack grouping Crashlytics also does.
  - Project health is active: CONFIRMED (push 2026-09-20, not archived). The 3,400 stars show popularity, not quality.
FIT:
  - Goal: goal 2 (crash noise) in principle, but no noise-reduction advantage is shown.
  - Overlap: full overlap with Firebase Crashlytics, which is already in use and decided to stay.
  - Burden: a new backend to host and run (container, database, upgrades, backups, uptime), an SDK swap in the Unity build, and a migration of the crash history and dashboards. Crashlytics is part of Firebase, which also does our analytics, so a switch would split our tools.
  - Cost: software free (Apache-2.0, read 2026-10-08). Hosting is not free unless it runs on hardware we already have, and the quarter's budget is $0 unless approved.
  - Risks:
    - License: Apache-2.0 is allowed for code we ship, so the in-game SDK would pass.
    - Data: player crash data goes to wherever the server is hosted. Self-hosting keeps it out of a new third party, but a cloud host would count as a new party and need approval.
    - Standing rules: it reverses two decided rules.
    - Health: project health looks fine.
NEXT ACTION: The operator decides whether to keep the standing rule (Firebase stays, no backend of our own). If it stands, close this as skip. Separately, address goal 2 inside Crashlytics: review its issue grouping, mark known noise crashes as closed or muted, and check symbol upload for the Unity build. Owner: operator. Done when the operator has recorded keep-rule/skip or asked for a scoped trial. Hand-off: none.
CONFIDENCE: medium. The item is resolved only from a 2026-10-08 snapshot with no code read and no commit sha. The goal-2 benefit is UNVERIFIED. The verdict itself rests on the self-hosting fact and the context file's rules, and both are clear.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "standing_rule",
  "item": {"type": "repo",
           "identity": "example-org/crashbin@main (sha not captured; Apache-2.0, 3,400 stars, last push 2026-09-20, not archived; snapshot 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "crashbin is free: the software license costs nothing", "evidence": "meta.json and README: Apache-2.0",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "switching to crashbin costs nothing", "evidence": "README: you run the server and a database yourself; hosting cost not stated",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "you run the server yourself (one container plus a database)", "evidence": "item's own README text",
     "status": "CONFIRMED"},
    {"claim": "groups crashes by stack and shows top crashes and trends", "evidence": "README description, no code or screenshots",
     "status": "PROBABLE", "load_bearing": false},
    {"claim": "has a Unity SDK", "evidence": "README statement, SDK not inspected",
     "status": "PROBABLE", "load_bearing": false},
    {"claim": "it would cut crash-report noise (goal 2) better than what we have", "evidence": "nothing in the item addresses noise reduction beyond stack grouping",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "the project is actively maintained", "evidence": "meta.json: last push 2026-09-20, not archived",
     "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 2 (cut crash-report noise), but no advantage over current tooling shown",
          "overlap": "Firebase Crashlytics already does crash grouping and top-crash reporting, and is decided to stay",
          "burden": "a new self-hosted backend (container plus database, upgrades, backups, uptime), a Unity SDK swap, migration off Crashlytics",
          "risks": ["reverses standing rules: Firebase stays, no backend of our own",
                    "player crash data would go to a new host if not on our own hardware",
                    "Apache-2.0 is allowed for shipped code"],
          "cost": {"price": "free software; hosting cost not stated", "tier": "open source, self-hosted",
                   "limits": "none stated", "terms": "Apache-2.0", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator decides whether the 'Firebase stays, no backend of our own' rule stands; if it does, close as skip and pursue goal 2 inside Crashlytics (grouping review, muting known noise, Unity symbol upload)",
                  "owner": "operator", "done_when": "operator has recorded keep-rule/skip or requested a scoped trial",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```