VERDICT: needs-decision, leaning skip: the 99.9% figure leaves out the crashes that matter most, nothing in the item cuts crash-report noise, and adopting it would break the standing rule that Firebase stays our crash service. It would likely also send player crash data to a new party and add an account. The operator decides.

WHAT IT IS: example-org/steadyreport, a crash-reporter SDK for mobile games. I read a saved snapshot captured 2026-10-08, not the live repo. It is MIT-licensed, has 1,900 stars, was last pushed and last released 2026-09-04, is not archived, and its default branch is main. The snapshot gives no commit sha. It also does not say where reports are sent, whether that is a hosted service or something you run yourself.

CLAIMS CHECKED:
- **"The SDK's dashboard shows 99.9% crash-free sessions."** The evidence is a dashboard screenshot that is not in the snapshot text. **UNVERIFIED.** It is not load-bearing.
- **"99.9% of sessions in production are crash-free."** This is the inference drawn from that counter, and the item's own text contradicts it. A session only counts as crashed when the SDK catches a managed exception and sends a report. The snapshot says: "Out-of-memory kills and native signal crashes end the process before the SDK can send anything, so they are not counted." The figure measures what the SDK can see, not how many sessions survive. **REFUTED.** Load-bearing.
- **"OOM kills and native signal crashes are not counted."** The item states this itself. **CONFIRMED.** Load-bearing: on Android Unity builds, OOM and native (IL2CPP/NDK) crashes are often the top crashes, so this SDK is blind to them.
- **"Licensed MIT."** Both the snapshot and meta.json say MIT. **CONFIRMED.** It is allowed for shipped code under our license rules. Not load-bearing.
- Popularity (1.9k stars) is not evidence of reliability, and I did not weigh it.

FIT:
- **Goal:** Goal 2 is "cut crash-report noise so the top five crashes are the ones worth fixing." I found nothing in the item for grouping, deduplication, symbolication or ranking. A headline crash-free rate does not reduce noise. Because the SDK misses native and OOM crashes, it would make the top five less trustworthy, not more.
- **Overlap:** Firebase Crashlytics already does this job, and keeping it is recorded under "Already decided." Running both would mean two crash streams, which is more noise, not less.
- **Burden:** a second SDK in the Unity build, a second dashboard, and somewhere for reports to go. We run no backend of our own, so that means a hosted service (a new account) or a new backend (against the decided rule).
- **Cost:** MIT, open source, $0 for the code as of the 2026-10-08 snapshot. Any hosting cost or terms for a report endpoint are not stated.
- **Risks:** player crash and device data would go to a party other than Firebase, which needs approval. It conflicts with the decision that Firebase stays. Its blind spot for native and OOM crashes would undercount the crashes that matter most. The license is fine. Project health looks active, with a push about five weeks before capture.

NEXT ACTION: The operator decides whether to keep Firebase Crashlytics as the only crash service and close this link. My recommendation is to keep it. For goal 2, the better place to look is noise reduction inside Crashlytics itself: issue grouping, regression alerts, and custom keys for filtering. The operator owns this. It is done when the decision is recorded in the context file's "Already decided" section or noted on the goal 2 tracker. Hand-off: none.

CONFIDENCE: high. The item is resolved from a dated snapshot, a context file is present, and every load-bearing claim is CONFIRMED or REFUTED by the item's own text. The main limit is that I read a snapshot, not the live repo, and it does not say where reports are sent.

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "standing_rule",
  "item": {"type": "repo",
           "identity": "example-org/steadyreport (MIT, 1900 stars, last push 2026-09-04, not archived, default branch main; snapshot captured 2026-10-08, no sha given)",
           "resolved": true},
  "claims": [
    {"claim": "the SDK's dashboard counter shows 99.9% crash-free sessions",
     "evidence": "a dashboard screenshot referenced in the README, not present in the snapshot text",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "99.9% of production sessions are crash-free",
     "evidence": "its own text: the counter only records managed exceptions the SDK catches and reports; OOM kills and native signal crashes are not counted",
     "status": "REFUTED"},
    {"claim": "out-of-memory kills and native signal crashes are not counted",
     "evidence": "stated in the item's own README",
     "status": "CONFIRMED"},
    {"claim": "licensed MIT",
     "evidence": "snapshot and meta.json both say MIT",
     "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 2 (cut crash-report noise): none found; no grouping, dedup or ranking features, and it misses native/OOM crashes",
          "overlap": "Firebase Crashlytics already in use and decided to stay as the crash service",
          "burden": "second SDK in the Unity build, second dashboard, and a report endpoint (hosted account or own backend, which we do not run)",
          "risks": ["breaks the standing decision that Firebase stays the crash service",
                    "player crash/device data to a new party, destination not stated",
                    "blind to OOM and native crashes, undercounting the most important Android crashes",
                    "MIT license is acceptable for shipped code"],
          "cost": {"price": "free (code)", "tier": "open source", "limits": "hosting/report endpoint cost not stated",
                   "terms": "MIT", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Decide whether to keep Firebase Crashlytics as the sole crash service and close this link (recommended), and pursue goal 2 via Crashlytics grouping, regression alerts and custom keys",
                  "owner": "operator",
                  "done_when": "the decision is recorded in the context file's Already decided section or on the goal 2 tracker",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```