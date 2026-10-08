**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools were available, so nothing external could be opened. All arithmetic below was recomputed by hand.

**VERDICT: REWORK.** The budget total does not match its own line items. The "fits the ceiling" conclusion rests on an unstated 6-month proration. The only market-pay source cannot be checked.

**CONFIDENCE: medium.** The arithmetic findings are certain. The survey claims cannot be checked because the source was not supplied. This is a same-context review with no tools.

**INPUTS LEDGER:**
- Seen: the request (request.md), the context (context.md) and the work (plan.md).
- Not seen: Industry Survey 2026, p. 14. This matters because every salary figure comes from it.
- Not seen: the region definition, start dates and fiscal-year boundaries, and the basis for the recruiter, equipment and onboarding figures. These matter because the proration and the ceiling comparison depend on them.
- Not seen: what the $140,000 ceiling covers (annual run-rate or first-year cash). This matters.

**SEATS AND GATE:** Only a local same-context review ran. There was no subagent and no tools. No cross-vendor seats were used; none were requested and none were available. The sensitivity gate passed: the work contains no personal data, only aggregate pay figures and an internal budget.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | High | CONFIRMED | C | plan.md, budget table, **Total** row | The line items sum to **$127,900** (84,000 + 19,750 + 11,400 + 12,750), not the stated $138,900. The gap is $11,000. | Finance approves a figure that matches no itemization. Either the total is mistyped, or an $11,000 line was dropped, such as a signing bonus or benefits. If a line was dropped, the true cost is unknown. | Reconcile the table. Restore any missing line, or correct the total, and show the sum. | confirmed. The arithmetic does not depend on any source. |
| 2 | High | CONFIRMED (the wording); PROBABLE (the impact) | C/A | plan.md, salaries row, "for the first year, prorated 6 months" | A "first-year" budget counts only 6 months of salary. Full-year salary for two hires is **$168,000**, which alone exceeds the $140,000 ceiling. Full-year total: 168,000 + 43,900 = **$211,900**. The 6-month start assumption is never stated or justified. | If "first year" means 12 months of employment, or the ceiling is an annual run-rate, the plan is about $72,000 over the ceiling. Finance would approve a cost that recurs at roughly 1.5 times the ceiling from year two. | State the start date and the fiscal-year basis. Show the full-year run-rate next to the prorated figure. Confirm with finance what the ceiling covers. | confirmed. The line says "first year" and "prorated 6 months" at once, and the ceiling check holds only under proration. |
| 3 | Medium | UNVERIFIED | C | plan.md, Market pay: "Industry Survey 2026 (p. 14) … median salary … $84,000" | The only market-pay figure cites a source that was not supplied. It is also unclear whether "median salary" means base pay or total compensation, and which region it covers. | If p. 14 gives a different figure, region, percentile or compensation basis, every salary line is wrong. $84,000 is also low for senior data engineers in many markets. That is a plausibility concern, not proof. | Attach or quote p. 14 verbatim, with region, percentile and base-or-total basis. Cross-check one second public source. | n/a |
| 4 | Medium | CONFIRMED (the omission) | C/A | plan.md, budget table vs. "70% of firms offer a signing bonus" | The plan cites signing-bonus prevalence but budgets nothing for it. It also has no employer payroll taxes or benefits. These typically add materially to the cost of an employee, and none appear. | If competing offers include bonuses and benefits load applies, the real first-year cost is understated and may breach the ceiling. | Add lines for signing bonus (or state the policy of offering none), payroll taxes and benefits, or state explicitly that the ceiling excludes them. | n/a |
| 5 | Low | UNVERIFIED | C | plan.md, recruiter fees, equipment and licences, onboarding and training | These three figures have no stated basis. For example, $19,750 is about 11.8% of full-year salary for two hires, below commonly quoted agency rates. | If they are estimates rather than quotes, the actual spend may differ. | Cite the quote, contract or rate behind each figure. | n/a |

## WHAT HOLDS UP
- 2 × $84,000 × 6/12 = $84,000 is correct arithmetic.
- The stated total of $138,900 is below $140,000. Even the recomputed $127,900 is below it, under the 6-month assumption.
- The work answers both parts of the request (market pay and a budget) with no scope drift beyond Finding 2.

## UNVERIFIED CLAIMS
- **Median $84,000 for a senior data engineer in "our region".** Settle this with a verbatim quote of Survey p. 14, including region and basis.
- **"70% of firms offer a signing bonus".** Same source and same check. Note that the work does not cite a page for it.
- **Recruiter, equipment and onboarding figures.** Settle these with vendor quotes or internal rate cards.

## QUESTIONS FOR THE AUTHOR
1. Which figure is wrong, the total or the line items? Was an $11,000 line removed?
2. When do the hires start? Does the $140,000 ceiling cover first-fiscal-year cash or the annual run-rate?
3. What exactly does p. 14 say (figure, region, percentile, base or total)? Are benefits and taxes inside or outside the ceiling?

## DECISION-MAKER SUMMARY
Do not send this to finance yet. The total does not match its own lines (off by $11,000), and the ceiling is met only by counting six months of salary. Full-year salaries alone ($168,000) exceed $140,000. If approved as is, finance commits to a cost that recurs well above the ceiling, on market data no one has checked.

## OWNER SUMMARY
The budget's total does not add up from its own lines, so it needs correcting before anyone approves it. It only fits under the limit because it counts half a year of pay. A full year of pay for the two people would already be over the limit. The salary figure comes from a report we could not check, so someone should confirm it against the actual page.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "Industry Survey 2026 p. 14", "status": "not_seen", "matters": true},
    {"item": "start dates / fiscal-year basis and ceiling definition", "status": "not_seen", "matters": true},
    {"item": "basis for recruiter, equipment, onboarding figures", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "aggregate pay data and internal budget only; no personal data"},
  "findings": [
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "C", "location": "plan.md budget table, Total row",
      "scenario": "Line items sum to $127,900, not the stated $138,900 ($11,000 gap); finance approves a total that matches no itemization, possibly with a dropped cost line",
      "fix": "Reconcile: restore the missing line or correct the total, and show the sum", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "C", "location": "plan.md salaries row, 'for the first year, prorated 6 months'",
      "scenario": "Full-year salaries are $168,000 (total $211,900), above the $140,000 ceiling; the fit depends on an unstated mid-year start, and the cost recurs above the ceiling from year two",
      "fix": "State start date and fiscal basis, show full-year run-rate, confirm with finance what the ceiling covers", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "C", "location": "plan.md Market pay, Industry Survey 2026 p. 14, $84,000 median",
      "scenario": "Source not supplied; if p. 14 gives a different figure, region, percentile or base vs total basis, all salary lines are wrong",
      "fix": "Quote p. 14 verbatim with region and basis; cross-check a second source", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "C", "location": "plan.md budget table vs '70% of firms offer a signing bonus'",
      "scenario": "No signing bonus, payroll taxes or benefits are budgeted, so first-year cost is understated and may breach the ceiling",
      "fix": "Add those lines or state explicitly that the ceiling excludes them", "status": "n/a"},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "track": "C", "location": "plan.md recruiter fees, equipment and licences, onboarding rows",
      "scenario": "Figures have no stated basis; actual spend may differ",
      "fix": "Cite the quotes or rate cards behind each figure", "status": "n/a"}
  ]
}
```