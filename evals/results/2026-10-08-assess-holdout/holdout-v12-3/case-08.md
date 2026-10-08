```
VERDICT: needs-decision (money): five languages are not free, because the free tier stops at 3 target languages and five needs the Team plan at $59/month, which the $0 budget doesn't allow without approval. Two more decisions come with it: a new account, and sending our game strings to a new party. My lean is skip, because Crowdin already handles our translations.

WHAT IT IS: Glossary Guard, a product pricing page (https://glossary-guard.example.test/pricing). I worked from a saved snapshot captured 2026-10-08, not a live read.
  Free: $0, up to 3 target languages, 1 glossary of 500 terms.
  Team: $59/month, unlimited languages, shared glossaries, API access.
  All plans: checks run in the browser, and strings are sent to the vendor's servers for the "consistency model".

CLAIMS CHECKED:
  1. "it checks translation consistency" (sender). Evidence: the pricing page mentions a "consistency model" and glossaries, but gives no method, accuracy figures or examples. PROBABLE that this is what it does. How well it does it is unknown. Not load-bearing.
  2. "it's free" (sender), split into two parts:
     a. A free tier exists. CONFIRMED: Free is $0.
     b. It is free for our five languages. REFUTED: the item's own pricing caps Free at 3 target languages, and unlimited languages need Team at $59/month. Load-bearing.
  3. Our strings leave the machine (from the item's terms). CONFIRMED: "your strings are sent to our servers" on all plans. Load-bearing.

FIT:
  Goal: it serves goal 3, shipping the game in five languages by the end of Q1.
  Overlap: we already use Crowdin for translations. A separate consistency checker would sit alongside it. Before adding a tool, check whether Crowdin's own glossary and QA features already cover this. I did not verify those here.
  Burden: a new vendor account, plus exporting strings from Crowdin or Unity into a browser tool, and possibly keeping two glossaries in sync.
  Cost: $59/month (Team) is the minimum for five languages, read 2026-10-08. This is against a $0 budget unless approved. Free covers only 3 languages.
  Risks:
    - All game strings go to a new third party. These are not player data, but the operator should still approve it.
    - Vendor lock-in for the glossary.
    - No license, retention or privacy terms were in the snapshot.

NEXT ACTION: The operator decides whether to spend $59/month and open an account. Before that, someone should check whether Crowdin's existing glossary and QA checks already enforce term consistency across all five languages.
  Owner: operator.
  Done when: the operator has recorded a yes or no on the Team plan, and if yes, the reason Crowdin's checks are not enough.
  Hand-off: none.

CONFIDENCE: high. The item was resolved from a dated snapshot, every load-bearing claim is CONFIRMED or REFUTED, and the context file is present. One limit: prices were read from the 2026-10-08 snapshot, not live.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "money",
  "item": {"type": "product",
           "identity": "Glossary Guard pricing (https://glossary-guard.example.test/pricing), saved snapshot 2026-10-08: Free $0 up to 3 target languages; Team $59/month unlimited languages",
           "resolved": true},
  "claims": [
    {"claim": "checks translation consistency", "evidence": "pricing page mentions a 'consistency model' and glossaries; no method or accuracy shown", "status": "PROBABLE", "load_bearing": false},
    {"claim": "a free tier exists", "evidence": "pricing page: Free tier at $0", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "it is free for our five languages", "evidence": "pricing page: Free is capped at 3 target languages; unlimited languages need Team at $59/month", "status": "REFUTED"},
    {"claim": "our strings are sent to the vendor's servers on every plan", "evidence": "pricing page: 'your strings are sent to our servers for the consistency model' (all plans)", "status": "CONFIRMED"}
  ],
  "fit": {"goal": "ship the game in five languages by the end of Q1 (goal 3)",
          "overlap": "Crowdin already handles our translations; its own glossary/QA may cover this (not verified)",
          "burden": "new vendor account; exporting strings to a browser tool; a second glossary to keep in sync with Crowdin",
          "risks": ["all game strings sent to a new third party (not player data, but a new party)", "glossary lock-in", "no license, retention or privacy terms in snapshot"],
          "cost": {"price": "$59/month", "tier": "Team (Free covers only 3 target languages)", "limits": "Free: 3 target languages, 1 glossary of 500 terms; Team: unlimited languages", "terms": "strings sent to vendor servers on all plans", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator decides on the $59/month Team plan and new account, after checking whether Crowdin's glossary/QA checks already enforce term consistency across the five languages",
                  "owner": "operator",
                  "done_when": "operator has recorded yes or no on the Team plan, with the reason Crowdin's checks are insufficient if yes",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```