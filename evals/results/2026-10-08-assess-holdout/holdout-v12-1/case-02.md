VERDICT: needs-decision, leaning skip. Using this SDK would break a standing rule ("Firebase stays our crash and analytics service"), and its 99.9% figure does not measure what it seems to. The SDK does not count out-of-memory or native crashes, so it does nothing for goal 2. It may also send player data to a new party; the snapshot does not say where reports go.

WHAT IT IS: example-org/steadyreport, read from a saved snapshot captured 2026-10-08 (not read live). The commit sha was not captured. License MIT, 1,900 stars, last push and last release 2026-09-04, not archived, default branch `main`. It is a lightweight crash-reporter SDK for mobile games.

CLAIMS CHECKED:
- **"The SDK's dashboard showed 99.9% crash-free sessions in production."** The evidence is a dashboard screenshot that is referenced but not in the snapshot. It is not stated whose production or what sample. **UNVERIFIED.** Not load-bearing.
- **The inference that 99.9% of sessions were crash-free.** **REFUTED** by the item's own text. A session counts as crashed only when the SDK catches a managed exception and sends a report. "Out-of-memory kills and native signal crashes end the process before the SDK can send anything, so they are not counted." The figure is the share of sessions without a reported managed exception, not a crash-free rate. Load-bearing.
- **It only sees managed exceptions, not OOM kills or native signal crashes.** **CONFIRMED** by the item's own text. Load-bearing: in a Unity game, those uncounted crash types are exactly what a crash triage needs to see.
- **License MIT, last release 2026-09-04.** **CONFIRMED** from the snapshot and meta.json. Not load-bearing.

FIT:
- **Goal:** Goal 2 is "cut crash-report noise so the top five crashes are the ones worth fixing." The item claims nothing about grouping, deduplication or noise reduction. It also sees fewer crashes than a full reporter, which would bias the top five rather than clean it. No goal is served.
- **Overlap:** Firebase Crashlytics already does this job. "Already decided" says Firebase stays our crash service.
- **Burden:** A second SDK in the Unity build. It would also need a place to receive reports, and we run no backend of our own.
- **Cost:** The code is free (MIT). Any hosted service behind it was not read (checked 2026-10-08).
- **Risks:**
  - MIT is allowed for shipped code.
  - It conflicts with a standing decision.
  - Crash reports are player data, and their destination is unknown. A new party would need approval.
  - Its crash metric undercounts by design.
  - Health looks fine, with a push 2026-09-04.

NEXT ACTION: The operator confirms the lean to skip and tells the sender that it does not help goal 2. Goal 2 stays with Crashlytics.
- Owner: operator.
- Done when: the decision is recorded and the sender has a reply.
- Hand-off: none.

CONFIDENCE: high. The item is resolved from the 2026-10-08 snapshot, the load-bearing claims are settled by its own text, and the context file is present. Two things are limited but not load-bearing: the snapshot is a saved copy rather than a live read, and the report destination is unread.

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "standing_rule",
  "item": {"type": "repo",
           "identity": "example-org/steadyreport@main (sha not captured; MIT, 1900 stars, last push 2026-09-04, not archived; snapshot 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "the SDK's dashboard showed 99.9% crash-free sessions in production",
     "evidence": "a dashboard screenshot is referenced but absent from the snapshot; whose production and what sample are not stated",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "therefore 99.9% of sessions were crash-free",
     "evidence": "its own text: a crash counts only when the SDK catches a managed exception and sends a report; OOM kills and native signal crashes are not counted",
     "status": "REFUTED"},
    {"claim": "the SDK records only managed exceptions, not OOM kills or native signal crashes",
     "evidence": "stated in the item's own text",
     "status": "CONFIRMED"},
    {"claim": "MIT license, last release 2026-09-04",
     "evidence": "snapshot text and meta.json",
     "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "none found: goal 2 (cut crash-report noise) is not addressed; the SDK claims no grouping or dedup and misses OOM and native crashes",
          "overlap": "Firebase Crashlytics is already in use and is decided as the crash service",
          "burden": "a second crash SDK in the Unity build plus somewhere to receive reports (we run no backend)",
          "risks": ["conflicts with the standing decision that Firebase stays the crash service",
                    "report destination unknown; crash reports are player data and may go to a new third party",
                    "crash-free metric undercounts by design",
                    "MIT is allowed for shipped code"],
          "cost": {"price": "free (code)", "tier": "open source", "limits": "any hosted service not read",
                   "terms": "MIT", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator confirms the lean to skip and tells the sender it does not help goal 2; keep Crashlytics",
                  "owner": "operator", "done_when": "the decision is recorded and the sender has a reply",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```