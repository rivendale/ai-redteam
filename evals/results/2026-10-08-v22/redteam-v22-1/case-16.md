> Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes. This session has no tools and no subagent, so I reviewed the work myself. I did not write the work, but I could not run or open anything.

**VERDICT: REWORK.** The budget total does not add up from its own lines. The claim that it "fits inside the ceiling" also rests on an unstated 6-month salary proration and leaves out employer on-costs.

**CONFIDENCE: medium.** The arithmetic findings were recomputed by hand and are certain. Confidence is limited because the Industry Survey 2026 was not supplied, the hire start date is unknown, and no second reviewer was available.

**INPUTS LEDGER**
- Seen: request.md (original request), context.md, plan.md.
- Not seen: Industry Survey 2026, p. 14 (paid; not supplied). **Matters**: both market-pay figures depend on it.
- Not seen: planned start date or fiscal-year definition. **Matters**: it decides whether a 6-month proration is legitimate.
- Not seen: basis for the recruiter, equipment and onboarding figures (quotes, policy). Matters somewhat: the figures cannot be checked.
- Not seen: the region the plan refers to. Matters: the market-pay claim cannot be scoped without it.

**COVERAGE**
- Checked: plan.md "Market pay" section (2 claims), the budget table (each line and the total), the ceiling conclusion, and the salary proration assumption.
- Not checked: the survey text, line-item sourcing, local payroll tax and benefit rates.

**SEATS AND GATE**
- Seats: only the local same-session reviewer ran. No subagent or cross-vendor seats were available, and none were requested.
- Sensitivity gate: passed. The work contains no personal data, only market aggregates and budget lines.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | C | plan.md, budget table, "**Total** \| **$138,900**" | The line items sum to $127,900, not $138,900. The $11,000 gap is unexplained: either the total is wrong or a line item was dropped. | Finance approves $138,900 against a breakdown that totals $127,900. Either $11,000 of phantom spend is approved, or a real cost line (possibly the signing bonus) is missing and the true total is unknown. | Recompute: 84,000 + 19,750 + 11,400 + 12,750 = 127,900. Either correct the total or restore the missing line, and show the sum. | a Y / b Y / c N (the error overstates, so the ceiling claim survives on its own) / d Y |
| F2 | High | CONFIRMED (contradiction) / PROBABLE (understatement) | C | plan.md, salary row: "2 x $84,000, for the first year, prorated 6 months"; and "The total fits inside the approved ceiling" | The request asks for a **first-year** budget, but the salary line covers only 6 months, and the plan never states why (for example, a mid-year start). A full first year of salary is 2 × 84,000 = $168,000, which exceeds the $140,000 ceiling on salary alone. The full-year total would be 168,000 + 43,900 = $211,900. | Finance reads "first-year budget, fits the ceiling" and approves. If the hires start near the beginning of the period, or the ceiling is meant to cover 12 months of cost, the plan overruns by about $72,000 or more. | State the start date and the period the ceiling covers. Show both the 6-month and the 12-month cost. If the ceiling is annual, the conclusion must say the plan does not fit. | a Y / b N / c Y (drift from the "first-year budget" request; misleads an approval) / d Y |
| F3 | High | CONFIRMED (omission) | C | plan.md, budget table (no on-cost line) | No employer payroll taxes, benefits, insurance or retirement contributions are budgeted. These typically add a substantial percentage to salary for employees. | After approval, payroll applies on-costs. Spend exceeds the approved figure, and the ceiling is breached even under the 6-month proration (on-costs of roughly 15–30% on $84,000 add about $12,600–$25,200, against roughly $1,100–$12,100 of headroom). | Add an on-cost line at the organization's actual rate, sourced from HR or payroll, and recompute the total against the ceiling. | a Y / b Y / c N / d Y |
| F4 | Medium | PROBABLE | C | plan.md: "70% of firms offer a signing bonus" vs. the budget table (no bonus line) | The plan cites signing bonuses as market norm, then budgets none. | Candidates expect a bonus, and the offer needs one. Either spend exceeds the approved budget or the hires are lost. | Add a bonus line or state explicitly that no bonus will be offered and what that does to hiring odds. | a Y / b N / c N / d Y |

## NEEDS VALIDATION
- **S1**: Is the median salary for a senior data engineer "in our region" $84,000 per Industry Survey 2026, p. 14? To settle it: read p. 14 and confirm the figure, the role definition (senior), the region, and that it is a median rather than a mean or a band. The figure also looks low for "senior" in many markets, which raises the need to check. If the true market rate is higher, F2 and F3 get worse.
- **S2**: Does the same survey report that "70% of firms offer a signing bonus", and for which role and region? To settle it: the survey passage.
- **S3**: Is budgeting at the median (rather than, say, the 60th–75th percentile) enough to hire two seniors? To settle it: recent offer and acceptance data or the recruiter's view.
- **S4**: Are the recruiter fees ($19,750), equipment ($11,400) and onboarding ($12,750) figures sourced? To settle it: the quotes, the fee agreement (often a percentage of annual salary, which here would be computed on $168,000), and the IT price list.

## REFUTED
- **R1**: "2 × $84,000 prorated 6 months ≠ $84,000." Refuted: 2 × 84,000 = 168,000, and 168,000 × 6/12 = 84,000. The row's own arithmetic is correct; the problem is the period (F2).
- **R2**: "The stated total breaches the ceiling." Refuted on the plan's own numbers: $138,900 < $140,000, and the recomputed $127,900 is also under. The breach risk comes only through F2 and F3.

## WHAT HOLDS UP
- The salary proration arithmetic is internally correct.
- The ceiling figure is copied correctly from the request ($140,000).
- The plan cites a specific source and page, so the claims can be checked once the survey is available.

## UNVERIFIED CLAIMS
- "$84,000 median salary" (survey p. 14): confirm by reading the survey.
- "70% of firms offer a signing bonus": confirm by reading the survey.
- The three non-salary line amounts: confirm against quotes, the fee agreement and the price list.
- "fits inside the approved ceiling": true for the stated numbers only. Confirm the period the ceiling covers and add on-costs.

## QUESTIONS FOR THE AUTHOR
1. Which line accounts for the $11,000 difference between the items ($127,900) and the total ($138,900)?
2. What start date justifies a 6-month salary, and does the $140,000 ceiling cover the same period?
3. Where are employer on-costs and any signing bonus in this budget?

## DECISION-MAKER SUMMARY
Do not send this to finance yet: the total does not match its lines (F1), and "fits the ceiling" depends on a 6-month salary assumption and omits on-costs (F2, F3). On a full-year basis, salaries alone ($168,000) exceed the $140,000 ceiling. If approved as is, expect an overrun or a re-approval request once payroll costs land.

## OWNER SUMMARY
The budget total does not add up from its own lines, and the plan counts only half a year of salary without saying why. It also leaves out employer costs such as payroll taxes and benefits, and any signing bonus. Once these are fixed, the plan may no longer fit the approved limit, so it should be corrected before finance sees it.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "plan.md", "status": "seen", "matters": true},
    {"item": "Industry Survey 2026, p. 14", "status": "not_seen", "matters": true},
    {"item": "planned start date / period covered by the ceiling", "status": "not_seen", "matters": true},
    {"item": "sources for recruiter, equipment and onboarding figures", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Market aggregates and budget lines only; no personal or confidential records."},
  "coverage": {
    "checked": [
      {"unit": "plan.md", "kind": "file"},
      {"unit": "plan.md#Market pay: median salary $84,000", "kind": "claim"},
      {"unit": "plan.md#Market pay: 70% signing bonus", "kind": "claim"},
      {"unit": "plan.md#Budget table line items and total", "kind": "section"},
      {"unit": "plan.md: total fits inside $140,000 ceiling", "kind": "claim"},
      {"unit": "6-month salary proration", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "Industry Survey 2026", "reason": "paid publication, not supplied"},
      {"unit": "line-item sourcing (recruiter, equipment, onboarding)", "reason": "no quotes or agreements supplied"},
      {"unit": "employer on-cost rates", "reason": "no payroll data supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "plan.md, budget table, Total row ($138,900)",
     "scenario": "Line items sum to $127,900 (84,000 + 19,750 + 11,400 + 12,750) but the stated total is $138,900; finance approves an $11,000 figure with no supporting line, or a dropped cost line goes unbudgeted.",
     "fix": "Correct the total or restore the missing line item, and show the sum.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Add the four line items: 84,000 + 19,750 + 11,400 + 12,750 = 127,900; expected to equal the stated total of 138,900; observed difference of 11,000."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "C",
     "location": "plan.md, salary row 'for the first year, prorated 6 months' and the ceiling sentence",
     "scenario": "The request asks for a first-year budget, but salaries cover only 6 months with no stated start date; a full year is $168,000 in salary alone (total $211,900), exceeding the $140,000 ceiling, so finance approves a plan that overruns if the ceiling is annual.",
     "fix": "State the start date and the period the ceiling covers; show both 6-month and 12-month costs; revise the ceiling conclusion accordingly.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "2 x 84,000 = 168,000 > 140,000; 168,000 + 19,750 + 11,400 + 12,750 = 211,900."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "plan.md, budget table (no employer on-cost line)",
     "scenario": "Payroll taxes and benefits are applied after approval; even at 15% on the $84,000 of salary they add $12,600, exceeding the remaining headroom and breaching the ceiling.",
     "fix": "Add an employer on-cost line at the organization's actual rate and recompute against the ceiling.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Budget table lists salaries, recruiter, equipment and onboarding only; 84,000 x 0.15 = 12,600 > 140,000 - 127,900 = 12,100."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "C",
     "location": "plan.md, Market pay ('70% of firms offer a signing bonus') vs. budget table",
     "scenario": "The plan cites signing bonuses as market norm but budgets none; if offers require one, spend exceeds the approved budget or candidates are lost.",
     "fix": "Add a signing-bonus line or state explicitly that none will be offered and the hiring risk.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "Market pay section cites 70% signing-bonus prevalence; budget table has no bonus line."},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "plan.md, Market pay, median salary $84,000",
     "suspicion": "The $84,000 median may not match the survey, role level or region, and looks low for a senior data engineer.",
     "unresolved_fact": "The text of Industry Survey 2026 p. 14 (figure, statistic, role definition, region); not supplied."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "plan.md, Market pay, 70% signing bonus",
     "suspicion": "The 70% signing-bonus figure may be misquoted or scoped to a different role or region.",
     "unresolved_fact": "The survey passage supporting the 70% figure; not supplied."},
    {"id": "S3", "status": "needs_validation", "track": "A", "location": "plan.md, Market pay (budgeting at median)",
     "suspicion": "Budgeting at the median may be too low to hire two senior engineers.",
     "unresolved_fact": "Recent offer and acceptance data or the recruiter's assessment for this role and region."},
    {"id": "S4", "status": "needs_validation", "track": "C", "location": "plan.md, budget table, recruiter/equipment/onboarding rows",
     "suspicion": "Line amounts are unsourced; recruiter fees are often a percentage of annual salary, which would be higher.",
     "unresolved_fact": "The recruiter fee agreement, equipment quotes and onboarding cost basis."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The salary row's arithmetic is wrong.", "evidence": "2 x 84,000 = 168,000; 168,000 x 6/12 = 84,000, matching the row."},
    {"id": "R2", "candidate": "The stated total breaches the ceiling.", "evidence": "$138,900 and the recomputed $127,900 are both below $140,000; breach risk arises only via F2 and F3."}
  ]
}
```