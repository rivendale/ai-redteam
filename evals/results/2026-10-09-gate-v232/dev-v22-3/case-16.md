# Redteam report: Hiring plan cost section

**Review mode:** I had no tools in this session, so I could not open the survey or run anything. The work was not written in this conversation, so there is no authorship anchoring. Every number below I recomputed by hand from the work's own figures.

**VERDICT: REWORK.** The budget total does not add up from its own line items, it is off by $11,000. The salary line also assumes a 6-month first year that conflicts with both its own label and the request.

**CONFIDENCE: medium.** It is limited by three things:
- I had no tools.
- The Industry Survey 2026 was not supplied, so every market-pay figure is unverified.
- I don't know the planned start dates or how the organization defines "first year".

**INPUTS LEDGER:**

| Item | Status | Does the gap matter? |
|---|---|---|
| ORIGINAL REQUEST (request.md) | Seen | – |
| CONTEXT (context.md) | Seen | – |
| plan.md | Seen | – |
| Industry Survey 2026, p. 14 | Not seen (paid, not supplied) | Yes. The $84,000 median and the "70%" signing-bonus claim depend on it. |
| Planned start dates, fiscal-year definition | Not seen | Yes. These decide whether 6-month proration is correct. |
| Org policy on fully loaded cost (payroll tax, benefits) | Not seen | Yes. It decides whether the budget is complete. |
| Basis for recruiter, equipment and onboarding figures | Not seen | Partly. These lines are plausible but unsourced. |

**COVERAGE:**
- **Checked:**
  - plan.md "Market pay" section: the $84,000 claim and the 70% claim.
  - plan.md budget table: all 4 lines and the total.
  - The closing ceiling sentence.
  - The proration assumption.
- **Not checked:**
  - The survey text.
  - The sources for the non-salary lines.
  - Regional plausibility of $84,000 against any second source.

**SEATS AND GATE:**
- Single reviewer, local, no tools.
- Cross-vendor seats were not run. They were not requested, and the content is internal compensation and budget material, so the gate would restrict external seats anyway.
- No personal data is present.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | C | plan.md budget table, "**Total** \| **$138,900**" | The lines sum to $127,900, not $138,900. 84,000 + 19,750 + 11,400 + 12,750 = 127,900. The difference is $11,000. | Finance re-adds the table and it doesn't reconcile. Either the plan is rejected for credibility, or an $11,000 item that was dropped from the table goes unbudgeted. | Re-add the lines. If an item is missing (for example the signing bonus, see F3), restore it and recompute. Reproduction: sum the four rows; expect 138,900, observe 127,900. | a Y, b Y, c N (the ceiling conclusion survives either total), d Y |
| F2 | High | CONFIRMED (text conflict) / PROBABLE (impact) | C, A | plan.md salaries row: "2 x $84,000, for the first year, prorated 6 months" | The request asks for a "first-year budget". The row says "first year" but costs only 6 months, and no start date or fiscal-year basis is stated. Two full first-year salaries are $168,000, which alone exceeds the $140,000 ceiling. | Finance reads "first-year budget" as 12 months of employment, or the hires start before mid-year. The real cost would be about $168,000 + $43,900 = $211,900 (or more, see F3/F4). That is far over the ceiling, and the ceiling sentence would be false. | State the start dates and the period the budget covers. Show a full 12-month figure next to the prorated one. Re-test the ceiling claim against the full-year figure. | a Y, b Y (contradiction quoted), c N (the meaning of "first year" isn't settled), d Y |
| F3 | Medium | CONFIRMED | C | plan.md "70% of firms offer a signing bonus" vs the budget table | The plan presents signing bonuses as market practice but budgets $0 for them. | The offers need bonuses to compete, the bonuses get paid outside the approved budget, and the ceiling is breached. | Either budget a bonus line or state explicitly that no bonus will be offered. | a Y, b Y, c N, d N (not certain bonuses will be offered) |
| F4 | Medium | PROBABLE | C | plan.md budget table (absent lines) | There are no employer on-costs (payroll taxes, benefits, retirement contributions). These commonly add a substantial share on top of base salary. | Finance approves $127,900–$138,900, and the true loaded cost is materially higher. | Add an on-cost line using the organization's standard loading rate, or state that the budget covers base salary only. | a Y, b N, c N, d Y |
| F5 | Low | CONFIRMED | C | plan.md "Market pay" heading: "**median salary**" | The plan doesn't say whether the median is base salary or total compensation, or which region definition and sample it uses. | Base is read as total compensation, or the reverse, and the offers fall below market. | Quote the survey's exact metric definition alongside the figure. | a Y, b Y, c N, d N |

## NEEDS VALIDATION
- **S1 (survey median).** Does the Industry Survey 2026, p. 14, state a median salary of $84,000 for a senior data engineer in "our region"? What settles it: the page itself, quoted verbatim, with the region and role definition.
- **S2 (signing-bonus prevalence).** Does the same survey support "70% of firms offer a signing bonus", and for which population? What settles it: the quoted passage.
- **S3 (plausibility of $84,000).** For a *senior* data engineer, $84,000 looks low in many markets. A figure this low is also what lets the plan fit under the ceiling. What settles it: the region, plus one independent comparator (another survey, or internal pay bands).
- **S4 (recruiter fees).** What is the basis for the $19,750 (fee percentage, flat fee, and which salary it is applied to)? What settles it: the recruiter agreement or quote.

## REFUTED
- **"The total exceeds the ceiling."** Refuted as an arithmetic matter. Both the stated $138,900 and the correct $127,900 are under $140,000. The ceiling risk comes from F2–F4, not from the addition.

## WHAT HOLDS UP
- The prorated salary arithmetic is internally correct: 2 × $84,000 × 6/12 = $84,000.
- Equipment at $11,400 ($5,700 per hire) and onboarding at $12,750 are of plausible magnitude, though unsourced.
- The plan cites a specific source and page, which makes it checkable.

## UNVERIFIED CLAIMS
- "$84,000 median" and "70% of firms offer a signing bonus". Confirm both by quoting Industry Survey 2026, p. 14.
- "The total fits inside the approved ceiling". This holds only for a 6-month, base-only budget. Confirm it against a 12-month, fully loaded figure.

## QUESTIONS FOR THE AUTHOR
1. What are the planned start dates, and does "first year" mean the fiscal year or the first 12 months of employment?
2. Where did $138,900 come from? Is a line item missing from the table?
3. Is the budget meant to be base-only, or fully loaded with taxes, benefits and bonus?

## DECISION-MAKER SUMMARY
Don't send this to finance yet. The total is wrong by $11,000, and the salary line covers only six months while the plan calls itself a first-year budget. On a full-year, fully loaded basis, two hires at this survey figure would be well above the $140,000 ceiling. That ceiling claim is the risk if the plan goes ahead as written.

## OWNER SUMMARY
The cost table doesn't add up: the listed items come to about eleven thousand dollars less than the stated total. The salaries only cover half a year and leave out taxes, benefits and the signing bonuses the plan itself says are common. Over a full year the true cost would likely be well above the approved limit. The salary figure also comes from a survey nobody has checked, so it should be confirmed before the plan is approved.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "plan.md", "status": "seen", "matters": true},
    {"item": "Industry Survey 2026 p. 14", "status": "not_seen", "matters": true},
    {"item": "planned start dates / fiscal-year definition", "status": "not_seen", "matters": true},
    {"item": "org on-cost policy (payroll tax, benefits)", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": true, "reason": "Internal compensation and budget material; no personal data. No cross-vendor seats requested or used."},
  "coverage": {
    "checked": [
      {"unit": "plan.md", "kind": "file"},
      {"unit": "plan.md#Market pay", "kind": "section"},
      {"unit": "plan.md#Budget for the two hires", "kind": "section"},
      {"unit": "Total $138,900", "kind": "claim"},
      {"unit": "Fits inside $140,000 ceiling", "kind": "claim"},
      {"unit": "6-month proration counts as first-year budget", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "Industry Survey 2026 p. 14", "reason": "paid publication, not supplied"},
      {"unit": "basis for recruiter, equipment, onboarding figures", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "plan.md budget table, Total row ($138,900)",
     "scenario": "Line items sum to $127,900 (84,000+19,750+11,400+12,750), not $138,900; finance re-adds, the table fails to reconcile, and any dropped $11,000 item goes unbudgeted.",
     "fix": "Recompute the total; if a line was dropped (e.g. signing bonus), restore it.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Sum the four rows: expected 138,900 as stated, observed 127,900."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "plan.md salaries row: '2 x $84,000, for the first year, prorated 6 months'",
     "scenario": "Request asks for a first-year budget; the row costs only 6 months with no stated start date. Full 12-month salaries are $168,000 alone, so if hires start before mid-year or finance reads first year as 12 months, cost is about $211,900 and the ceiling claim is false.",
     "fix": "State start dates and budget period; show the full 12-month figure; re-test the ceiling claim against it.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "plan.md Market pay '70% of firms offer a signing bonus' vs budget table",
     "scenario": "The plan cites signing bonuses as market practice but budgets none; if offers need them, they are paid outside the approved budget.",
     "fix": "Add a signing-bonus line or state explicitly that none will be offered.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "C",
     "location": "plan.md budget table (no on-cost line)",
     "scenario": "Payroll taxes and benefits are omitted, so finance approves a figure materially below the true loaded cost.",
     "fix": "Add an on-cost line at the org's standard loading rate, or label the budget base-only.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "plan.md Market pay: 'median salary'",
     "scenario": "The metric (base vs total comp), region and sample are undefined, so offers may be benchmarked against the wrong figure.",
     "fix": "Quote the survey's metric definition alongside the figure.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "plan.md Market pay: '$84,000'",
     "suspicion": "Median figure attributed to Industry Survey 2026 p. 14 is unverified and looks low for a senior role.",
     "unresolved_fact": "Verbatim text of Industry Survey 2026 p. 14, including region and role definition."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "plan.md Market pay: '70% of firms offer a signing bonus'",
     "suspicion": "Prevalence figure is unverified.",
     "unresolved_fact": "The survey passage supporting 70%, and its population."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "plan.md budget table: recruiter fees $19,750",
     "suspicion": "Recruiter fee has no stated basis.",
     "unresolved_fact": "Recruiter agreement or quote (fee percentage and salary base)."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The stated total exceeds the $140,000 ceiling.",
     "evidence": "Both the stated $138,900 and the correct $127,900 are below $140,000; the ceiling risk comes from proration and omitted costs (F2-F4), not the addition."}
  ]
}
```