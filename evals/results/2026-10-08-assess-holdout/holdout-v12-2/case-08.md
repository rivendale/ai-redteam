```
VERDICT: needs-decision (money), with a lean to skip: five languages is not free; it needs the Team plan at $59/month. Every plan also sends our game strings to their servers, a new third party. It may also duplicate Crowdin, which we already use for translations.
WHAT IT IS: Glossary Guard pricing page (https://glossary-guard.example.test/pricing), read from a saved snapshot captured 2026-10-08, not live. Product. Free tier: $0, up to 3 target languages, 1 glossary of 500 terms. Team tier: $59/month, unlimited languages, shared glossaries, API access. All plans run checks in the browser and send strings to the vendor's servers.
CLAIMS CHECKED:
  - "it's free" (sender), for our need of five languages: REFUTED. The page caps the free tier at 3 target languages. Five needs Team at $59/month. [load-bearing]
  - "checks translation consistency" (sender): PROBABLE. The page mentions a "consistency model" and glossaries but gives no evidence of quality. [not load-bearing]
  - Strings leave the machine on every plan: CONFIRMED by the page itself: "your strings are sent to our servers for the consistency model." [load-bearing]
  - Team gives unlimited languages: CONFIRMED as stated on the pricing page. [load-bearing]
FIT:
  - Goal: goal 3, ship the game in five languages by the end of Q1.
  - Overlap: Crowdin is already our translation tool. Before adding a second service, check whether our Crowdin setup already covers glossary and consistency checks. I have not verified that from the item.
  - Burden: a new vendor account, a second place to keep the glossary in sync with Crowdin, and a step in the translation workflow.
  - Cost: $59/month (Team) for five languages, read 2026-10-08. Our quarterly tool budget is $0 unless approved. The free tier (3 languages, 500 terms) does not meet the need.
  - Risks: game strings go to a new third party on every plan. These are game text, not player data, but it is still a new data recipient. Lock-in on the glossary format. Vendor health is unknown from a pricing page.
NEXT ACTION: The operator decides whether to approve $59/month plus a new account and sending strings to the vendor, or to skip and rely on Crowdin. Owner: operator. Done when the decision is recorded. Hand-off: none.
CONFIDENCE: high. The item is resolved from a same-day snapshot, the claims the verdict rests on are REFUTED or CONFIRMED by the page itself, and the context file is present. The Crowdin overlap is not verified, but it does not change the need for a decision.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "money",
  "item": {"type": "product",
           "identity": "Glossary Guard pricing (glossary-guard.example.test/pricing), snapshot 2026-10-08: Free $0 / 3 target languages / 1 glossary of 500 terms; Team $59/month unlimited languages",
           "resolved": true},
  "claims": [
    {"claim": "it's free (for our five languages)", "evidence": "pricing page: Free tier is up to 3 target languages; unlimited languages only on Team at $59/month", "status": "REFUTED"},
    {"claim": "checks translation consistency", "evidence": "pricing page mentions a consistency model and glossaries; no evidence of quality", "status": "PROBABLE", "load_bearing": false},
    {"claim": "strings are sent to the vendor's servers on all plans", "evidence": "pricing page: 'your strings are sent to our servers for the consistency model'", "status": "CONFIRMED"},
    {"claim": "Team plan covers unlimited languages", "evidence": "pricing page tier list", "status": "CONFIRMED"}
  ],
  "fit": {"goal": "ship the game in five languages by end of Q1 (goal 3)",
          "overlap": "Crowdin already handles our translations; whether it covers glossary consistency checks is unverified",
          "burden": "new vendor account, a second glossary to keep in sync with Crowdin, an extra workflow step",
          "risks": ["game strings sent to a new third party on every plan", "glossary lock-in", "vendor health unknown from pricing page"],
          "cost": {"price": "$59/month for five languages (Free is $0 but capped at 3 languages)", "tier": "Team",
                   "limits": "Free: 3 target languages, 1 glossary of 500 terms; Team: unlimited languages",
                   "terms": "all plans send strings to vendor servers", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Decide whether to approve $59/month, a new account and sending strings to Glossary Guard, or skip and rely on Crowdin",
                  "owner": "operator", "done_when": "the decision is recorded", "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```