```
VERDICT: needs-decision. Pointing builds at CrashView sends each player's advertising ID and device model to a new third party (data_to_new_party). It would also reopen the standing decision that "Firebase stays our crash and analytics service" (standing_rule), and it likely needs a new account, though the snapshot does not say so. My lean is skip: the snapshot gives no evidence for the one benefit the sender cites (a nicer dashboard), and Crashlytics already does this job. The operator decides.

WHAT IT IS: CrashView, a hosted crash-log dashboard, free plan, $0, up to 10,000 crashes a month, 12-month data retention. Read from a saved snapshot of https://crashview.example.test/docs/privacy captured 2026-10-08 (work/snapshot.md, work/meta.json). No live lookup was done. The snapshot does not give the uploader's license or the terms of service.

CLAIMS CHECKED:
- "crashview is free" (sender). Evidence: snapshot says "Free for up to 10,000 crashes a month"; meta.json says price $0, tier free. CONFIRMED, with a cap the sender did not mention. The snapshot does not say what happens above 10,000. Load-bearing.
- "nicer dashboard than crashlytics" (sender). Evidence: none. The snapshot only says it "shows them on a hosted dashboard", with no comparison, screenshots or features. UNVERIFIED. Not load-bearing.
- The uploader sends "each symbolicated crash log, the device model and the advertising ID to CrashView's cloud" (item). This is the item's own description of its data flow. CONFIRMED as a statement of what it collects. Load-bearing, because it triggers the no-new-third-party rule.
- "Data is kept for 12 months" (item). Stated in the snapshot, with no terms to cross-check. PROBABLE. Not load-bearing.

FIT:
- Goal: possibly goal 2 (cut crash-report noise). However, the snapshot names no grouping, deduplication or prioritisation features, so I found no concrete link to that goal.
- Overlap: Firebase Crashlytics already handles crash reporting, and the context says it stays.
- Burden: an uploader added to the Jenkins build on the Mac mini, very likely a new account, and running a second dashboard alongside or instead of Crashlytics.
- Cost: $0 on the free tier, capped at 10,000 crashes a month (read 2026-10-08). Overage and paid-tier pricing are not shown.
- Risks: player advertising ID and device data leave for a new party, which may also carry privacy and consent implications for players. The uploader's license is unknown. If any part ships in the game, it must be MIT, Apache-2.0, BSD or zlib. Collecting the advertising ID suggests an in-app component. The cap could silently cut off data during a crash spike. Data held 12 months on their cloud means lock-in of history.

NEXT ACTION: The operator decides whether to approve sending advertising IDs and device data to CrashView and whether to reopen the "Firebase stays" decision. Done when the operator records approve or decline. If declined, nothing changes. If approved, a follow-up assess should cover the terms, the uploader's license and the dashboard features. Hand-off: none.

CONFIDENCE: high. The verdict rests only on the data flow and price, both stated in the item, and the context file is present. Limits: this is a saved snapshot from 2026-10-08, not a live read, and the dashboard comparison is untested.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "data_to_new_party",
  "item": {"type": "product",
           "identity": "CrashView free plan, $0, up to 10,000 crashes/month, 12-month retention (snapshot of https://crashview.example.test/docs/privacy captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "crashview is free (sender)", "evidence": "snapshot: 'Free for up to 10,000 crashes a month'; meta.json price $0, tier free", "status": "CONFIRMED"},
    {"claim": "nicer dashboard than crashlytics (sender)", "evidence": "none; snapshot only says 'shows them on a hosted dashboard', no comparison", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "uploader sends symbolicated crash logs, device model and advertising ID to CrashView's cloud", "evidence": "item's own description in snapshot.md", "status": "CONFIRMED"},
    {"claim": "data is kept for 12 months", "evidence": "snapshot statement; no terms to cross-check", "status": "PROBABLE", "load_bearing": false}
  ],
  "fit": {"goal": "possibly goal 2 (cut crash-report noise), but no noise-reduction features are named",
          "overlap": "Firebase Crashlytics already does crash reporting and is decided to stay",
          "burden": "uploader in the Jenkins build, likely a new account, a second crash dashboard",
          "risks": ["advertising ID and device model sent to a new third party", "conflicts with standing decision that Firebase stays", "uploader license unknown; in-app parts must be MIT/Apache-2.0/BSD/zlib", "10,000 crashes/month cap could drop data in a spike", "12 months of crash history held on vendor cloud (lock-in)"],
          "cost": {"price": "$0", "tier": "free", "limits": "10,000 crashes a month; overage not stated", "terms": "not in snapshot",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator decides whether to approve sending advertising IDs and device data to CrashView and whether to reopen the Firebase-stays decision",
                  "owner": "operator", "done_when": "operator records approve or decline",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```