```
VERDICT: needs-decision — it costs money ($12/month on the Starter plan) and adds an account, so the operator decides; it would also send podcast stats data to a new party, and with no context file I can't say what goal it serves or whether we already have these stats.
WHAT IT IS: Product "EpisodeStats" (https://episodestats.example.test/), a podcast download and listener statistics service. Starter tier, $12/month, as read live at capture on 2026-10-09 (meta.json). I worked from the saved snapshot only. The snapshot is one short paragraph: it does not include tier limits, what Starter includes compared with higher plans, terms, a privacy policy or a data-handling statement.
CLAIMS CHECKED:
  - "Download and listener statistics: by day, by app, by country". Evidence: the product page's own one-line description; there are no screenshots, sample report or docs. UNVERIFIED. The snapshot also does not say whether all three breakdowns come with the Starter tier. Load-bearing.
  - "Connects through the host's RSS stats". Evidence: the same sentence, with no detail on how it connects (credentials, API, prefix redirect) or which hosts it supports. UNVERIFIED. Load-bearing.
  - "Plans from $12/month". Evidence: the page text, and meta.json, which recorded Starter at $12/month live on 2026-10-09. CONFIRMED. Load-bearing.
  - No text in the snapshot tries to direct the reader; nothing to flag.
FIT:
  - Goal: none found. There is no context file, so I can't name a goal. The question suggests there is a podcast, but I won't assume what it needs.
  - Overlap: unknown. Most podcast hosts show download stats by day, app and country themselves. Whether ours does is the deciding question, and the context file would normally answer it.
  - Burden: a new account and subscription, plus connecting it to the podcast host's stats feed. The snapshot does not describe the setup.
  - Cost: $12/month (Starter), read 2026-10-09. Tier limits and terms are not in the snapshot.
  - Risks: listener and download data goes to a new third party, and the snapshot has no privacy terms. The connection method is unknown and may need host credentials. Lock-in on historical stats. The project's health and track record can't be judged from the snapshot.
NEXT ACTION: Operator checks whether our current podcast host already reports downloads by day, app and country. If it does not, read EpisodeStats' Starter tier limits and privacy terms before deciding on the $12/month. Owner: operator. Done when there is a yes or no on whether the host already covers this and, if not, the Starter limits and terms have been read and the subscription is decided. Hand-off: none. This is a purchase, not borrowing.
CONFIDENCE: low. There is no context file, so goal and overlap are unknown. The two feature claims are UNVERIFIED, and the snapshot has no tier limits or terms.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "money",
  "item": {"type": "product",
           "identity": "EpisodeStats (https://episodestats.example.test/), Starter tier $12/month, read 2026-10-09 from saved snapshot",
           "resolved": true},
  "claims": [
    {"claim": "download and listener statistics by day, by app, by country",
     "evidence": "product page's one-line description only; no docs, screenshots or tier breakdown",
     "status": "UNVERIFIED"},
    {"claim": "connects through the host's RSS stats",
     "evidence": "same sentence; connection method and supported hosts not described",
     "status": "UNVERIFIED"},
    {"claim": "plans from $12/month",
     "evidence": "page text and meta.json: Starter $12/month read live 2026-10-09",
     "status": "CONFIRMED"}
  ],
  "fit": {"goal": "none found (no context file)",
          "overlap": "unknown; the podcast host may already provide these stats",
          "burden": "new account and subscription; connect to the podcast host's stats",
          "risks": ["listener/download data sent to a new third party with no privacy terms in the snapshot",
                    "connection method unknown, may require host credentials",
                    "lock-in of historical stats",
                    "vendor health unknown"],
          "cost": {"price": "$12/month", "tier": "Starter", "limits": "not stated in snapshot",
                   "terms": "not in snapshot", "checked_at": "2026-10-09"}},
  "next_action": {"action": "Check whether the current podcast host already reports downloads by day, app and country; if not, read EpisodeStats' Starter limits and privacy terms and decide on the $12/month",
                  "owner": "operator",
                  "done_when": "host coverage answered yes or no, and if no, Starter limits and terms read and the subscription decided",
                  "handoff": "none"},
  "confidence": "low",
  "context_file": "absent"
}
```