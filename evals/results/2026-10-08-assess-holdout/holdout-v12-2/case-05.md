```
VERDICT: needs-decision (standing_rule). Switching to crashbin would reverse two already-decided rules ("Firebase stays our crash and analytics service" and "we run no backend of our own"), so only the operator can make this call. My lean is skip: crashbin does the same job Crashlytics already does for goal 2, and it adds a server we would have to run.

WHAT IT IS: example-org/crashbin, a GitHub repo read from a saved snapshot captured 2026-10-08 (work/snapshot.md,
  work/meta.json). No commit sha was recorded. License Apache-2.0, 3,400 stars, last push 2026-09-20, last release 2026-09-20, not archived,
  default branch main. It is open-source crash reporting for mobile games: it groups crashes by stack and shows top crashes and
  trends on a web dashboard. It is self-hosted: one Docker container plus a database. It has SDKs for Unity, Unreal and native Android.

CLAIMS CHECKED:
  - "crashbin is free" (sender's words), split into two parts:
    (a) The software costs nothing to license. Evidence: Apache-2.0 per meta.json and the README. CONFIRMED. [load-bearing]
    (b) It is free to run. Evidence: none. The item says you host the server and database yourself, and hosting, storage
        and upkeep costs are not stated. UNVERIFIED.
  - "You run the server yourself (Docker image, one container plus a database)." This is the item's own description of
    how it is deployed. CONFIRMED. [load-bearing: this is what conflicts with "we run no backend of our own"]
  - "Has a Unity SDK." Evidence: README statement only, and the SDK code was not read. PROBABLE.
  - "Groups crashes by stack, shows top crashes and trends." Evidence: README statement only, with no description of the grouping
    method and no comparison with other tools. PROBABLE. The item offers nothing to show it reduces noise better than
    Crashlytics, which is what goal 2 needs.
  - The repo is actively maintained. Evidence: last push and release 2026-09-20, not archived. CONFIRMED. The 3,400 stars are a
    true count but are not evidence of quality.
  No text in the snapshot tries to direct the reader.

FIT:
  - Goal: goal 2 (cut crash-report noise so the top five crashes are the ones worth fixing). This is the goal the sender named.
  - Overlap: full. Firebase Crashlytics is already in use for crashes and already groups them and ranks the top issues.
    Switching replaces it rather than adding a capability. Nothing in the snapshot shows that crashbin's grouping is better.
  - Burden: high. We would run and maintain a new server plus database, with uptime, backups, upgrades and storage, for a team
    that has decided to run no backend. We would also have to swap the SDK in the Unity game and migrate dashboards
    and history away from Crashlytics. Analytics would stay on Firebase either way.
  - Cost: $0 license (Apache-2.0, read 2026-10-08). Hosting cost is not stated, and the quarter's budget for new tools is $0 unless the operator
    approves.
  - Risks: Apache-2.0 is allowed for code we ship, if the Unity SDK carries the same license (not checked in the
    snapshot). Player crash data would go to wherever we host the server: if that is a cloud host, it is a new third party
    and needs approval. Running a self-hosted server breaks the standing no-backend rule. The project's health looks fine (recent
    release, not archived).

NEXT ACTION: The operator decides whether to reopen the decision "Firebase stays; we run no backend". If the operator does not
  reopen it, close this as skip, and go after goal 2 inside Crashlytics instead (custom keys, issue grouping, filtering by
  build or version). Owner: operator. Done when: the decision is written down (reopened or not) in the context file's "Already decided"
  section. Hand-off: none.

CONFIDENCE: high. The item is resolved from a snapshot captured today, the context file is present, and the claims the verdict rests on
  (it is self-hosted, Apache-2.0, free to license) are CONFIRMED from the item's own text. The rule conflict is a fact in the context file. What
  is not known: hosting cost, the Unity SDK's own license, and whether crashbin's grouping is better than Crashlytics'. None of these
  changes the need for an operator decision.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "standing_rule",
  "item": {"type": "repo", "identity": "example-org/crashbin (Apache-2.0, 3,400 stars, last push 2026-09-20, not archived, default branch main; snapshot captured 2026-10-08, no sha recorded)",
           "resolved": true},
  "claims": [
    {"claim": "crashbin is free (software license)", "evidence": "meta.json and README: Apache-2.0", "status": "CONFIRMED"},
    {"claim": "crashbin is free to run", "evidence": "none; self-hosted server and database, hosting cost not stated", "status": "UNVERIFIED",
     "load_bearing": false},
    {"claim": "you run the server yourself (one Docker container plus a database)", "evidence": "the item's own README text", "status": "CONFIRMED"},
    {"claim": "has a Unity SDK", "evidence": "README statement; SDK not read", "status": "PROBABLE", "load_bearing": false},
    {"claim": "groups crashes by stack and shows top crashes and trends", "evidence": "README statement; no method or comparison given", "status": "PROBABLE",
     "load_bearing": false},
    {"claim": "actively maintained", "evidence": "meta.json: last push 2026-09-20, not archived; README: last release 2026-09-20", "status": "CONFIRMED",
     "load_bearing": false}
  ],
  "fit": {"goal": "goal 2: cut crash-report noise so the top five crashes are worth fixing",
          "overlap": "Firebase Crashlytics already in use for crash grouping and top issues; switching replaces it",
          "burden": "run and maintain a self-hosted server plus database; swap the Unity SDK; migrate away from Crashlytics history",
          "risks": ["conflicts with standing decisions: Firebase stays the crash service, and we run no backend of our own",
                    "player crash data would go to a hosting provider if not on our own hardware (new third party)",
                    "Unity SDK license not checked; Apache-2.0 is allowed for shipped code if the SDK shares it",
                    "hosting cost not stated against a $0 tools budget"],
          "cost": {"price": "free (license); hosting not stated", "tier": "open source, self-hosted", "limits": "none stated",
                   "terms": "Apache-2.0", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator decides whether to reopen 'Firebase stays; we run no backend'; if not, close as skip and pursue goal 2 inside Crashlytics",
                  "owner": "operator", "done_when": "the decision is recorded in the context file's Already decided section",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```