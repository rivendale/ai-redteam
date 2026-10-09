VERDICT: watch. There is no context file, so I can't name a goal this serves or check it against stats the podcast host may already provide; that is what would change the answer.

WHAT IT IS: EpisodeStats (https://episodestats.example.test/), a paid podcast statistics product. Starter tier at $12/month, as read live at capture on 2026-10-09 (meta.json). I worked from a saved snapshot dated 2026-10-09 and did not open the live page. The snapshot shows no tier limits, no list of features per plan, no terms of service and no privacy policy.

CLAIMS CHECKED:
- *"Download and listener statistics: downloads by day, by app, by country."* The only evidence is the product's one-line description. It shows no sample report, no method and no statement of how "listeners" are counted as distinct from downloads. **UNVERIFIED**. The verdict does not rest on it.
- *"Connects through the host's RSS stats."* The snapshot names no supported hosts and does not say what access it needs (a login, an API key, a redirect prefix). **UNVERIFIED**. The verdict does not rest on it.
- *"Plans from $12/month."* meta.json records Starter at $12/month, read live on 2026-10-09. **CONFIRMED**. The verdict does not rest on it.
- Sender's question, *"should we use this?"*: this implies a podcast and an interest in its stats. With no context file I can't confirm either, and I have not assumed a goal.

FIT:
- **Goal:** none found, because there is no context file.
- **Overlap:** unknown. The tool reads the host's own stats, so the podcast host may already show the same downloads by day, app and country. That needs checking before paying for this.
- **Burden:** a new account and subscription. Probably also linking it to the host account or feed.
- **Cost:** $12/month for Starter, read 2026-10-09. Limits and terms were not in the snapshot, so it is unknown which breakdowns are Starter-only or on higher tiers.
- **Risks:** podcast audience data goes to a new party; terms and privacy policy unread; the access method to the host is unstated; project health is unknown.

NEXT ACTION: The operator writes a context file covering three things: whether there is a podcast and what decision its stats should inform, which host it is on, and what that host's dashboard already shows (by day, app, country). Then re-run assess on this item. Done when the context file exists and lists the host's built-in stats. Hand-off: none. If it then fills a real gap, the verdict becomes needs-decision (money; also account and data to a new party), and the operator decides.

CONFIDENCE: low. There is no context file, the item is a thin saved snapshot, and its feature claims are unverified, with no limits or terms shown.

```json
{
  "schema_version": "assess-1",
  "verdict": "watch",
  "item": {"type": "product",
           "identity": "EpisodeStats (https://episodestats.example.test/), Starter tier $12/month as read 2026-10-09 (saved snapshot)",
           "resolved": true},
  "claims": [
    {"claim": "statistics for downloads by day, by app, by country", "evidence": "product's own one-line description; no sample report or method", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "connects through the host's RSS stats", "evidence": "product's own description; no supported hosts or access method named", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "plans from $12/month", "evidence": "meta.json: Starter $12/month read live at capture 2026-10-09", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "none found (no context file)",
          "overlap": "unknown; the podcast host's own stats may already give the same breakdowns",
          "burden": "new account and subscription, linking to the host account or feed",
          "risks": ["podcast audience data sent to a new party", "terms and privacy policy not in snapshot", "access method to host unstated", "project health unknown"],
          "cost": {"price": "$12/month", "tier": "Starter", "limits": "not shown in snapshot", "terms": "not shown in snapshot",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Write a context file stating the podcast goal, the host, and what the host's built-in stats already show, then re-run assess on this item",
                  "owner": "operator",
                  "done_when": "a context file exists that lists the host's built-in stats and the goal stats should serve",
                  "handoff": "none"},
  "confidence": "low",
  "context_file": "absent"
}
```