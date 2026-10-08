```
VERDICT: needs-decision (money). It is $39 per seat per month billed yearly against a $0 budget. It also needs a new account and sends tester screen recordings and device logs to a new third party. My lean is skip: it records individual crashes but does nothing to cut crash-report noise (goal 2), and Crashlytics already captures our crashes. I have not set it up, because only the operator can approve this.

WHAT IT IS: PlaytestCloud, Pro tier, $39 per seat per month, billed yearly. Read from a saved snapshot of
  https://playtestcloud.example.test/pricing captured 2026-10-08 (work/snapshot.md, work/meta.json), not live.
  The snapshot holds only the pricing text. It has no terms, data-handling policy, SDK or platform details.

CLAIMS CHECKED:
  1. "captures crash videos from testers" (sender). Evidence: the snapshot says it "Records the tester's screen and
     the device log when a crash happens." CONFIRMED.
  2. "$39 a seat" (sender). Evidence: the snapshot says "$39 per seat per month, billed yearly." CONFIRMED as the
     seat price. The sender left out the period and billing: each seat is about $468 a year, paid up front. Load-bearing.
  3. "Create an account to start. 7-day trial, then billed" (item). CONFIRMED from the snapshot. Even a trial needs a
     new account and becomes a paid plan when it ends. Load-bearing.
  4. "feels right for goal 2" (sender's inference). Goal 2 is cutting crash-report noise so the top five crashes are
     the ones worth fixing. The snapshot describes recording single crashes for playback. It says nothing about
     grouping, deduplicating or ranking crashes, so nothing in the item settles this. UNVERIFIED. Not load-bearing.

FIT:
  - Goal: the nearest is goal 2, but only indirectly. Videos may help debug a crash once it is chosen. They do not
    reduce noise or rank crashes. No stronger fit found.
  - Overlap: Firebase Crashlytics is already our crash service, and "Firebase stays our crash and analytics service"
    is already decided. This would add a second crash-capture path next to it.
  - Burden: a new vendor account, seat management, an SDK in the Unity build (integration not shown in the snapshot),
    and enrolling testers.
  - Cost: $39 per seat per month, billed yearly; Pro tier; limits and terms not in the snapshot; read 2026-10-08.
    The tool budget this quarter is $0 unless approved.
  - Risks: tester screen recordings and device logs go to a new third party (needs approval). Yearly billing means
    lock-in. The trial turns into a paid plan automatically. Telemetry, data retention, Unity 6 support and Android/iOS
    coverage are unknown from the snapshot.

NEXT ACTION: The operator decides whether to approve the spend, the new account and the data sharing. Before that,
  it is worth checking whether Crashlytics' own grouping and breadcrumb logs already cover goal 2. Owner: operator.
  Done when the operator records approve or decline. Hand-off: none.

CONFIDENCE: medium. The item is resolved only from a saved pricing snapshot, and the context file is present. The
  snapshot has no terms, data-handling, SDK or platform details, which limits the fit and risk assessment.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "money",
  "item": {"type": "product",
           "identity": "PlaytestCloud Pro, $39 per seat per month billed yearly (saved pricing snapshot, captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "captures crash videos from testers", "evidence": "snapshot: records the tester's screen and the device log when a crash happens",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "$39 a seat", "evidence": "snapshot: $39 per seat per month, billed yearly (about $468 per seat per year up front)",
     "status": "CONFIRMED"},
    {"claim": "starting requires an account; the 7-day trial is then billed", "evidence": "snapshot: 'Create an account to start. 7-day trial, then billed.'",
     "status": "CONFIRMED"},
    {"claim": "it fits goal 2 (cut crash-report noise)", "evidence": "snapshot describes per-crash recording only; nothing on grouping, deduplication or ranking",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 2 only indirectly: helps debug a chosen crash, does not reduce noise",
          "overlap": "Firebase Crashlytics already captures crashes and is the decided crash service",
          "burden": "new vendor account, seat management, Unity SDK integration, tester enrollment",
          "risks": ["tester screen recordings and device logs sent to a new third party",
                    "yearly billing lock-in; trial auto-converts to paid",
                    "terms, retention, telemetry and Unity 6/platform support not in snapshot"],
          "cost": {"price": "$39 per seat per month", "tier": "Pro", "limits": "not stated in snapshot",
                   "terms": "billed yearly; 7-day trial then billed; full terms not in snapshot",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator decides whether to approve the spend, new account and data sharing, after checking whether Crashlytics grouping and breadcrumbs already cover goal 2",
                  "owner": "operator", "done_when": "operator records approve or decline",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```