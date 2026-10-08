```
VERDICT: needs-decision (money): the free plan covers only 3 target languages, so five languages need the $59/month
  Team plan, and every plan also sends our strings to the vendor's servers (data to a new party); my lean is skip,
  because Crowdin is already our translation tool and should be checked for consistency checks first.
WHAT IT IS: Glossary Guard pricing page (https://glossary-guard.example.test/pricing), product, read from a saved
  snapshot captured 2026-10-08, not live. Free: $0, up to 3 target languages, 1 glossary of 500 terms. Team: $59/month,
  unlimited languages, shared glossaries, API access. All plans run checks in the browser and send strings to the
  vendor's servers.
CLAIMS CHECKED:
  - "it's free" for our five languages (sender's words): REFUTED. The free tier allows up to 3 target languages.
    Five languages exceed that even if English is the source and only four are targets. Verdict rests on this.
  - Team plan ($59/month) gives unlimited languages: CONFIRMED by the pricing page as captured. Verdict rests on this.
  - On all plans, strings are sent to the vendor's servers: CONFIRMED by the vendor's own statement on the pricing page.
    Verdict rests on this.
  - It checks translation consistency (sender's words): UNVERIFIED. The page mentions a "consistency model" and
    glossaries but gives no evidence of how well it works. Verdict does not rest on this.
FIT:
  - Goal: goal 3, ship the game in five languages by end of Q1.
  - Overlap: Crowdin already handles our translations. Whether Crowdin's own glossary and QA checks cover this was not
    checked here, and should be before adding a second tool.
  - Burden: a new vendor account; the strings would have to be exported from Crowdin into a second tool.
  - Cost: $0 tier does not fit (3 languages); Team is $59/month as read on 2026-10-08. Our budget this quarter is $0
    unless approved, and a new paid subscription needs operator approval.
  - Risks: game strings leave the machine to a new third party on every plan (no player data, as far as the page
    says, but still a new party); vendor lock-in for glossaries; no license or install concerns, since it is a hosted
    service.
NEXT ACTION: The operator decides whether to approve $59/month and sending game strings to Glossary Guard. Before
  deciding, the operator or the localization owner checks whether Crowdin's existing glossary and QA checks already
  catch terminology inconsistency across the five languages. Done when there is a yes/no on Crowdin coverage and a
  recorded approve/decline on the subscription. Hand-off: none.
CONFIDENCE: high. The item is resolved (from a dated saved snapshot), the claims the verdict rests on are REFUTED or
  CONFIRMED, and a context file is present. One limit: prices and tiers are as captured on 2026-10-08, not re-read live.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "money",
  "item": {"type": "product",
           "identity": "Glossary Guard pricing (https://glossary-guard.example.test/pricing), snapshot captured 2026-10-08: Free $0 / 3 target languages; Team $59/month / unlimited languages",
           "resolved": true},
  "claims": [
    {"claim": "it's free for our five languages (sender)", "evidence": "pricing page: Free tier is up to 3 target languages", "status": "REFUTED"},
    {"claim": "Team plan at $59/month gives unlimited languages", "evidence": "pricing page as captured 2026-10-08", "status": "CONFIRMED"},
    {"claim": "on all plans, strings are sent to the vendor's servers", "evidence": "pricing page: 'your strings are sent to our servers for the consistency model'", "status": "CONFIRMED"},
    {"claim": "it checks translation consistency (sender)", "evidence": "page mentions a consistency model and glossaries, gives no evidence of quality", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "ship the game in five languages by end of Q1 (goal 3)",
          "overlap": "Crowdin already handles translations; its own glossary/QA coverage not yet checked",
          "burden": "new vendor account; strings exported from Crowdin into a second tool",
          "risks": ["game strings sent to a new third party on every plan", "glossary lock-in", "paid tier exceeds $0 quarterly budget"],
          "cost": {"price": "$59/month (Team); Free does not fit", "tier": "Team", "limits": "Free: 3 target languages, 1 glossary of 500 terms",
                   "terms": "strings sent to vendor servers on all plans", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator decides whether to approve $59/month and sending game strings to Glossary Guard, after checking whether Crowdin's existing glossary and QA checks already cover consistency across the five languages",
                  "owner": "operator", "done_when": "Crowdin coverage answered yes/no and the subscription approved or declined on record",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```