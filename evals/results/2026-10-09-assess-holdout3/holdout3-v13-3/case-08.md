VERDICT: skip. It is not free for us: at about 3,000 downloads per episode the show needs TuneBed's $15/month commercial license. The context file also lists no goal about music, so the trade-off does not come up.

WHAT IT IS: TuneBed background-music license page (https://tunebed.example.test/license), product. I read it from the saved snapshot captured 2026-10-09 (work/snapshot.md, work/meta.json), not live. Tiers as read:
- **Free:** $0 for podcasts under 1,000 downloads per episode, with credit in the show notes.
- **Commercial:** $15 per month for podcasts above 1,000 downloads per episode, and for paid or sponsored episodes.

CLAIMS CHECKED:
- **"Free for podcasts" (sender): REFUTED for us.** The license limits free use to fewer than 1,000 downloads per episode. The context file says the show gets about 3,000 downloads per episode, so the $15/month commercial license applies. Load-bearing.
- **"Goal 1 (less time hunting for music)" (sender): REFUTED.** In the context file, goal 1 is "Cut editing time to under 2 hours per episode." That time goes to hand cuts in Reaper (silences, filler words). Music, intros and beds appear nowhere in the goals, tools or constraints. Load-bearing.
- **Free use requires a credit in the show notes: CONFIRMED.** It is in the snapshot text. Not load-bearing.
- **Paid or sponsored episodes need the commercial license at any download count: CONFIRMED.** It is in the snapshot text. The context does not say whether episodes are sponsored. Not load-bearing.

FIT:
- **Goal:** none found. The goal the sender cites (music hunting) is not goal 1 as written.
- **Overlap:** no music source is listed as in use, so there is no overlap.
- **Burden:** a new account and subscription, plus a credit line in the show notes in Google Docs.
- **Cost:** $15/month commercial tier at our download level, checked 2026-10-09. The free tier is out of reach above 1,000 downloads per episode. It would break two constraints without approval: "$0 unless approved" and "no new paid subscription or account without the host's approval."
- **Risks:**
  - The free tier is a licensing trap. Using it at 3,000 downloads, or in a sponsored episode, would breach the license.
  - The tracks would be locked in, and the license would have to continue for as long as the episodes stay published. The snapshot does not say what happens if the subscription stops.

NEXT ACTION: The operator replies to the sender with two points. TuneBed is $15/month for a show our size, not free. Music sourcing is not one of the current goals. If hunting for music really costs editing time, the host adds it to the context file's goals and sends TuneBed back, which would make it a money decision (`needs-decision`). Owner: operator. Done when the sender has the answer, and either the context file is updated or the item is closed. Hand-off: none.

CONFIDENCE: high. The item is resolved from a same-day snapshot, both load-bearing claims are settled by the license text and the context file, and the context file is present. One limit: the snapshot is a saved copy, so recheck the price and the threshold live before any purchase.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "product",
           "identity": "TuneBed license (https://tunebed.example.test/license): free under 1,000 downloads/episode with show-notes credit; commercial $15/month above that or for paid/sponsored episodes; read from snapshot 2026-10-09",
           "resolved": true},
  "claims": [
    {"claim": "free for podcasts (sender)", "evidence": "license: free only under 1,000 downloads per episode; context: about 3,000 downloads per episode, so $15/month commercial license required", "status": "REFUTED"},
    {"claim": "goal 1 is less time hunting for music (sender)", "evidence": "context file goal 1 is cutting editing time to under 2 hours per episode (hand cuts in Reaper); no goal mentions music", "status": "REFUTED"},
    {"claim": "free use requires credit in the show notes", "evidence": "snapshot license text", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "paid or sponsored episodes require the commercial license", "evidence": "snapshot license text", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "none found (goal 1 is editing time, not music sourcing)",
          "overlap": "none: no music source listed in use",
          "burden": "new account and subscription; credit line in show notes",
          "risks": ["free tier does not cover a 3,000-download show or sponsored episodes: using it would breach the license",
                    "new paid subscription and account break the $0 budget and approval constraints",
                    "lock-in: published episodes depend on keeping the license; snapshot does not say what happens on cancel"],
          "cost": {"price": "$15 per month", "tier": "commercial (free tier only under 1,000 downloads per episode)",
                   "limits": "free tier: under 1,000 downloads per episode, no paid or sponsored episodes",
                   "terms": "credit in show notes for free use; commercial license for paid or sponsored episodes",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Tell the sender TuneBed is $15/month at our size and music sourcing is not a current goal; if it is a real time cost, the host adds it to the context file goals and resubmits as a money decision",
                  "owner": "operator",
                  "done_when": "the sender has the answer and the context file is either updated or the item is closed",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```