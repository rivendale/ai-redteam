VERDICT: needs-decision (standing_rule). Using it would put a second crash service beside Firebase, which the context file says "stays our crash and analytics service". I lean to **skip**. Its 99.9% figure comes from a counter that, by its own text, misses out-of-memory kills and native crashes. So it does not cut noise for goal 2; it hides whole classes of crashes. The snapshot also does not say where reports are sent, so player data may go to a new party.

WHAT IT IS: example-org/steadyreport, a crash-reporter SDK for mobile games. Read from a saved snapshot captured 2026-10-08, not live. MIT license, 1,900 stars, last push and last release 2026-09-04, not archived, default branch `main`. No commit SHA was captured. The snapshot does not say whether it supports Unity, where reports are sent, or what any hosting costs.

CLAIMS CHECKED:
- **"99.9% crash-free sessions in production": the counter shows 99.9%.** The evidence is a dashboard screenshot, and the snapshot has only the caption, not the image or any data. UNVERIFIED. Not load-bearing.
- **"99.9% crash-free sessions in production": 99.9% of sessions were actually crash-free.** REFUTED by the item's own definition. A session counts as crashed only when the SDK catches a managed exception and sends a report. Out-of-memory kills and native signal crashes "end the process before the SDK can send anything, so they are not counted." The figure measures what the SDK can see, not how many sessions crashed. Load-bearing.
- **The SDK does not capture out-of-memory or native signal crashes.** CONFIRMED by its own text. Load-bearing: this blind spot is why it would hide crashes rather than reduce noise.
- **It is "lightweight".** No evidence given. UNVERIFIED. Not load-bearing.
- **License is MIT, last release 2026-09-04.** CONFIRMED by meta.json and the snapshot. Not load-bearing.
- **Sender's question: "does that help goal 2?"** No. Goal 2 is noise reduction, so the top five crashes are the ones worth fixing. A crash-free percentage does not rank or group crashes. A reporter that cannot see two crash classes would make the top five less trustworthy.

FIT:
- **Goal:** goal 2 is the named target, but the item does not serve it (see above).
- **Overlap:** Firebase Crashlytics already does this job and is an already-decided choice. This would be a second, partial crash pipeline.
- **Burden:** a new SDK in the shipped game, a second dashboard, and two sets of crash numbers to reconcile.
- **Cost:** the code is MIT and free, read 2026-10-08. Any hosted service, its price, tiers or terms are not in the snapshot. Budget is $0 unless approved.
- **Risks:**
  - MIT is allowed for shipped code.
  - Report destination is unknown. It may be player data to a new third party, which needs approval, or it may need a backend, which the context says "we run no backend".
  - Project health looks fine: pushed a month ago, not archived.

NEXT ACTION: The operator decides whether to consider any second crash reporter beside Firebase. My lean is to decline and keep goal 2 work inside Crashlytics. Owner: operator. Done when the decision is recorded in the context file. Hand-off: none.

CONFIDENCE: high. The item is resolved from a saved snapshot dated 2026-10-08. The load-bearing claims are REFUTED or CONFIRMED from its own text, and the context file is present. One open point does not change the verdict: the snapshot does not say where reports go.

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "standing_rule",
  "item": {"type": "repo",
           "identity": "example-org/steadyreport@main (no SHA captured; MIT, 1900 stars, last push 2026-09-04, not archived; saved snapshot 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "the SDK's counter shows 99.9% crash-free sessions in production",
     "evidence": "a dashboard screenshot referenced in the snapshot; only the caption was captured, no data",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "99.9% of production sessions are crash-free",
     "evidence": "its own text: a session counts as crashed only when the SDK catches a managed exception; OOM kills and native signal crashes are not counted",
     "status": "REFUTED"},
    {"claim": "the SDK does not capture out-of-memory kills or native signal crashes",
     "evidence": "stated in the snapshot: they end the process before the SDK can send anything",
     "status": "CONFIRMED"},
    {"claim": "it is a lightweight crash reporter",
     "evidence": "none given", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "license MIT, last release 2026-09-04",
     "evidence": "meta.json license and last_push; snapshot text", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 2 (cut crash-report noise) is the target, but the item does not serve it: a crash-free percentage does not rank crashes, and missing OOM and native crashes hides them",
          "overlap": "Firebase Crashlytics already does crash reporting and is an already-decided choice",
          "burden": "a new SDK in the shipped game, a second dashboard, and reconciling two sets of crash numbers",
          "risks": ["MIT is allowed for shipped code",
                    "report destination not stated: may send player data to a new third party or need a backend we do not run",
                    "blind to OOM and native signal crashes by its own text",
                    "Unity support not stated in the snapshot"],
          "cost": {"price": "free (MIT code); any hosted service price not stated", "tier": "open source",
                   "limits": "not stated", "terms": "MIT", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator decides whether to consider a second crash reporter beside Firebase; lean is to decline and keep goal 2 work in Crashlytics",
                  "owner": "operator", "done_when": "the decision is recorded in the context file",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```