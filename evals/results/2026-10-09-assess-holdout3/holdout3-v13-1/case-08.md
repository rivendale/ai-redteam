```
VERDICT: needs-decision (money): the sender says it is free for podcasts, but the license we read makes it free only under 1,000 downloads per episode. We get about 3,000, so using it means a $15/month commercial license, which needs the host's approval (probably a new account too, though the page does not say).
WHAT IT IS: TuneBed background-music license page (https://tunebed.example.test/license), product. Read from a saved snapshot captured 2026-10-09, not live. Free tier: $0, only for podcasts under 1,000 downloads per episode, with credit in the show notes. Commercial license: $15/month for podcasts above 1,000 downloads per episode, and also required for paid or sponsored episodes.
CLAIMS CHECKED:
  - "free for podcasts" (sender): REFUTED for us. The license limits the free tier to fewer than 1,000 downloads per episode, and the context file says we get about 3,000. [verdict rests on this]
  - "above 1,000 downloads per episode a commercial license is required: $15 per month" (item): CONFIRMED by snapshot.md and meta.json (captured 2026-10-09). [verdict rests on this]
  - "less time hunting for music, goal 1" (sender): UNVERIFIED. The snapshot is only the license page and says nothing about the catalog, search or quality. Also, our goal 1 is "cut editing time to under 2 hours per episode". Finding music is not named there, and the context file does not mention using music at all, so the link to goal 1 is the sender's inference.
  - Paid or sponsored episodes need the commercial license (item): CONFIRMED by the snapshot. It is moot at our download count, which needs the commercial license anyway.
FIT:
  - Goal: goal 1 (editing time), only if finding music is part of our per-episode editing time. The sender says it is, but the context file does not show it.
  - Overlap: nothing in use supplies music, so there is no overlap.
  - Burden: a credit line in the show notes on the free tier (not ours), a $15/month subscription and probably an account.
  - Cost: $15/month (about $180/year) at our size, read 2026-10-09 from the snapshot. The quarter's budget for new tools is $0 unless approved.
  - Risks: if we used the free tier at 3,000 downloads per episode, we would break the license. The license's other terms (term length, what happens to episodes already published if we cancel) are not on the captured page. This is a paid subscription, so the host must approve it.
NEXT ACTION: The host decides whether to approve the $15/month TuneBed commercial license, or to keep finding music the current way. Owner: the host. Done when the host's yes or no is recorded. Hand-off: none.
CONFIDENCE: medium. The license terms are clear and the context file is present. Limits: we worked from a saved snapshot, not a live read; the time-saving benefit is unverified; and the context file does not say that music is part of editing time.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "money",
  "item": {"type": "product",
           "identity": "TuneBed license (https://tunebed.example.test/license): free under 1,000 downloads/episode with show-notes credit; commercial license $15/month above that or for paid/sponsored episodes; read from snapshot captured 2026-10-09",
           "resolved": true},
  "claims": [
    {"claim": "free for podcasts (sender)", "evidence": "license: free only for podcasts with fewer than 1,000 downloads per episode; context file: about 3,000 downloads per episode", "status": "REFUTED"},
    {"claim": "podcasts above 1,000 downloads per episode need a $15/month commercial license", "evidence": "snapshot.md and meta.json, captured 2026-10-09", "status": "CONFIRMED"},
    {"claim": "saves time hunting for music, serving goal 1 (sender)", "evidence": "license page says nothing about the catalog; context goal 1 is editing time under 2 hours and does not mention music", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "paid or sponsored episodes need the commercial license", "evidence": "snapshot.md", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 1 (cut editing time to under 2 hours per episode), only if finding music counts as editing time; the sender asserts it and the context file does not show it",
          "overlap": "none: nothing in use supplies music",
          "burden": "a $15/month subscription, probably a new account, credit or license bookkeeping",
          "risks": ["using the free tier at ~3,000 downloads/episode would break the license",
                    "$0 tool budget this quarter unless the host approves",
                    "terms on cancellation and on episodes already published are not on the captured page"],
          "cost": {"price": "$15/month for us (free tier does not apply)", "tier": "commercial (free tier only under 1,000 downloads/episode)",
                   "limits": "free tier: under 1,000 downloads per episode, credit in show notes, not for paid or sponsored episodes",
                   "terms": "commercial license required above 1,000 downloads/episode or for paid/sponsored episodes",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Host decides whether to approve the $15/month TuneBed commercial license or keep finding music the current way",
                  "owner": "host", "done_when": "the host's yes or no is recorded", "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```