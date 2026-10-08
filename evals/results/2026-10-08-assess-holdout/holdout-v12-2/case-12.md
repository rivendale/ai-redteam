```
VERDICT: needs-decision (data_to_new_party). Pointing builds at CrashView would send each player's advertising ID and device model to a new third party. It would also overturn a standing decision ("Firebase stays our crash and analytics service"), and a hosted dashboard probably needs a new account. My lean is skip: it repeats Crashlytics, which is already in use, and nothing in the item addresses our crash-noise goal. The operator decides.

WHAT IT IS: CrashView, a hosted crash-log dashboard, read from its docs/privacy page (https://crashview.example.test/docs/privacy). The free plan costs $0 and allows up to 10,000 crashes a month. I read a saved snapshot captured on 2026-10-08, not the live page. Only the short privacy/plan text was captured. It does not include the full terms, the paid tiers, what happens above the cap, or whether sign-up needs an account.

CLAIMS CHECKED:
- "crashview is free" (sender). The snapshot says "Free for up to 10,000 crashes a month" and meta.json says tier free, price $0. CONFIRMED, with a cap. What happens above 10,000 crashes is not stated.
- "nicer dashboard than crashlytics" (sender). The item offers no evidence or comparison. UNVERIFIED, and the verdict does not rest on it.
- The uploader sends symbolicated crash logs, device model and advertising ID to CrashView's cloud (item). This is the item's own text. CONFIRMED, and the verdict rests on it.
- Data is kept for 12 months (item). Item's own text. CONFIRMED, and the verdict does not rest on it.
- "let's point our builds at it" (sender's implied claim that this is a drop-in switch). The context file says Firebase stays our crash service. This is a policy conflict, not a fact about the item, so it is handled under FIT.

FIT:
- Goal: none found. Goal 2 is cutting crash-report noise so the top five crashes are worth fixing. The snapshot claims no grouping, deduplication or ranking, only a hosted dashboard. A nicer view of the same crashes does not cut noise.
- Overlap: full overlap with Firebase Crashlytics, which is already in use and decided ("Firebase stays our crash and analytics service").
- Burden:
  - adds an uploader to the Unity build on Jenkins (macOS) and probably Windows
  - adds a second crash pipeline to keep in sync, or a migration off Crashlytics
  - probably adds a new account (not shown in the snapshot)
- Cost: $0 on the free plan as read on 2026-10-08, capped at 10,000 crashes a month. Overage handling and full terms were not captured.
- Risks:
  - Player data, including the advertising ID, would go to a new third party, which needs approval under our constraints.
  - Our store privacy labels and data-safety disclosures would need updating, and consent rules may apply to advertising IDs.
  - The 12-month retention sits on their servers.
  - Lock-in to a hosted service.
  - The uploader's license and install path are unknown. If it ships in the game, it must be MIT, Apache-2.0, BSD or zlib.
  - Vendor health is unknown.

NEXT ACTION: The operator decides whether to reopen the "Firebase stays" decision and approve sending advertising IDs to CrashView. Until then, builds stay on Crashlytics. Owner: operator. Done when the operator records approve or decline. If the real need is crash noise (goal 2), raise that separately as Crashlytics grouping or triage work. Hand-off: none.

CONFIDENCE: high. The item is resolved from a dated snapshot, the claims the verdict rests on are CONFIRMED from the item's own text, and the context file is present. The limits are that this is a saved copy of one short page: the full terms, overage behavior, account requirement and uploader license were not read. None of those would remove the data-sharing or standing-rule issue.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "data_to_new_party",
  "item": {"type": "product",
           "identity": "CrashView free plan ($0, up to 10,000 crashes/month), docs/privacy page, read from snapshot captured 2026-10-08",
           "resolved": true},
  "claims": [
    {"claim": "crashview is free", "evidence": "snapshot: 'Free for up to 10,000 crashes a month'; meta.json price $0, tier free",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "crashview has a nicer dashboard than crashlytics", "evidence": "none offered in the item",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "the uploader sends symbolicated crash logs, device model and advertising ID to CrashView's cloud",
     "evidence": "snapshot, item's own text", "status": "CONFIRMED"},
    {"claim": "data is kept for 12 months", "evidence": "snapshot, item's own text", "status": "CONFIRMED",
     "load_bearing": false}
  ],
  "fit": {"goal": "none found (goal 2 is crash noise; the item claims no grouping or ranking, only a dashboard)",
          "overlap": "Firebase Crashlytics already in use and decided as our crash service",
          "burden": "uploader added to Unity/Jenkins builds on macOS and Windows, a second or migrated crash pipeline, probably a new account",
          "risks": ["advertising ID and device model sent to a new third party (needs approval)",
                    "conflicts with standing decision that Firebase stays our crash service",
                    "store privacy labels and consent for advertising IDs would need review",
                    "12-month retention on vendor servers",
                    "uploader license and install path unknown; shipped code must be MIT/Apache-2.0/BSD/zlib",
                    "lock-in to a hosted service"],
          "cost": {"price": "$0", "tier": "free", "limits": "up to 10,000 crashes a month; overage behavior not captured",
                   "terms": "full terms not captured in snapshot", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator decides whether to reopen the Firebase decision and approve sending advertising IDs to CrashView; builds stay on Crashlytics meanwhile",
                  "owner": "operator", "done_when": "operator records approve or decline",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```