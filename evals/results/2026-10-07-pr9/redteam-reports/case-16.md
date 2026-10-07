**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available, so this review is by one reviewer working only from the text supplied.

**VERDICT: REWORK.** The stated total does not match its own line items. The only market-pay figure comes from a source nobody can check. The budget fits the ceiling only because of an unstated six-month start assumption and because it leaves out employer costs.

**CONFIDENCE: medium.** The arithmetic findings are certain. Confidence is limited because the Industry Survey 2026 was not supplied, no tools were available, and this is a same-context review.

**INPUTS LEDGER**
| Item | Status | Matters? |
|---|---|---|
| request.md (original request) | seen | yes |
| context.md | seen | yes |
| plan.md | seen | yes |
| Industry Survey 2026, p. 14 | not seen and not obtainable (paid) | **yes**: the salary, the signing-bonus claim and the whole budget rest on it |
| Hire start dates or hiring timeline | not supplied | **yes**: the 6-month proration depends on it |
| Basis for recruiter, equipment and onboarding figures | not supplied | moderately |
| Definition of the $140,000 ceiling (total first-year cost or per-salary cap) | not supplied | **yes** |

**SEATS AND GATE:** One same-context reviewer ran. No cross-vendor seats were used because none were requested or available. Sensitivity gate: there is no personal data or credentials. Internal pay planning is mildly confidential, which would argue against external seats anyway.

### Pass 1: Reconstruct
The plan says the regional median salary for a senior data engineer is $84,000, citing the survey at p. 14. It also says 70% of firms offer signing bonuses. It budgets two hires at a total of $138,900 and concludes this fits the $140,000 ceiling.

For the plan to be correct, four things must be true:
- the survey says what is claimed;
- "first-year budget" means about six months of salary;
- the ceiling covers total cost but excludes employer on-costs and bonuses;
- the line items add up.

Track: C (with A for the budget logic).

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | High | CONFIRMED | C | plan.md, budget table, **Total** row | The line items sum to $127,900 (84,000 + 19,750 + 11,400 + 12,750). The table states $138,900, which is $11,000 too high. | Finance re-adds the table, finds the mismatch and loses trust in every figure. Alternatively, the wrong headroom ($1,100 instead of $12,100) drives decisions. | Correct the total to $127,900, or identify the missing $11,000 line item. Re-add before resubmitting. | confirmed: the sum is unambiguous |
| 2 | High | CONFIRMED (assumption present); PROBABLE (impact) | A/C | budget table, salaries row: "prorated 6 months" | The request asks for a "first-year budget". The plan silently assumes both hires start six months into the year, and no start date or timeline is given. A full year is 2 × $84,000 = $168,000 in salary alone, which already exceeds the $140,000 ceiling. | Finance reads "first-year" as the first 12 months of employment. They approve $140k against a true cost of at least $211,900 (168,000 + 43,900 in other items). | State the assumed start date and fiscal year. Show the full-year cost alongside the prorated cost, and the year-2 run rate. | confirmed: the label discloses the proration, but its basis is missing and the "fits the ceiling" conclusion depends on it |
| 3 | High | UNVERIFIED | C | plan.md, Market pay: "Industry Survey 2026 (p. 14) … median salary … $84,000" | The figure that holds up the budget cannot be checked. Sourced or not, $84k is low for a *senior* data engineer in many markets (PROBABLE). The text also does not say whether the figure is base pay or total compensation, or which region and sample it covers. | The real median is higher, or the figure is total compensation rather than base. Offers at $84k fail, and the salary line is understated by tens of thousands. | Quote the p. 14 passage verbatim, with the table name, region and figure definition. Have someone with access confirm it. Cross-check against a second free source. | confirmed as a finding: the claim stays unsupported whatever its true value |
| 4 | High | PROBABLE | A | budget table (absent items) | There are no employer on-costs: payroll taxes, benefits, retirement contributions. These typically add about 20–30% to salary, roughly $17k–25k on $84k. | Actual first-year cost is about $145k–153k (using the corrected $127,900), which exceeds the ceiling. The plan is approved and then overruns. | Add an on-cost line using the company's loaded-cost rate from HR or finance. | confirmed. Defender's case: the ceiling may be salary-only. But the table already includes non-salary items, so on-costs belong in it. |
| 5 | Medium | CONFIRMED | A/C | Market pay: "70% of firms offer a signing bonus" vs the budget table | The plan cites signing bonuses as market practice but budgets nothing for them. | A candidate expects a bonus, and the cost is either unbudgeted or the hire is lost. | Add a signing-bonus line, or state explicitly that none will be offered and accept the hiring risk. | n/a |
| 6 | Medium | CONFIRMED (absent) | C | recruiter fees $19,750; equipment $11,400; onboarding $12,750 | No basis is given for these figures, such as a fee percentage, quote or vendor. Recruiter fees are often 15–25% of first-year salary; $19,750 across two hires is about 11.8% of $168k, which is low if the fee uses the full annual salary. | The agency invoices on the annualized salary and the fees come in higher than budgeted. | State the fee basis and percentage, and cite quotes for equipment and training. | n/a |
| 7 | Medium | PROBABLE | A | Market pay: "median" | Budgeting at the median means about half the market pays more. With no range (P25–P75), finance cannot see the risk. | Offers at the median lose candidates and the role stays open. | Give a range and a target percentile. | n/a |

### WHAT HOLDS UP
- The salary row's own arithmetic is correct: 2 × $84,000 × 6/12 = $84,000.
- The proration is labelled rather than hidden.
- The plan cites a page number, which makes verification possible for someone who has the survey.

### UNVERIFIED CLAIMS
- **Median $84,000 at p. 14:** someone with a survey copy should quote it, including the region, the definition and whether it is base pay.
- **70% of firms offer a signing bonus:** same check.
- **Ceiling scope:** confirm with finance what the $140,000 covers.

### QUESTIONS FOR THE AUTHOR
1. Where does the extra $11,000 in the total come from?
2. What start date justifies the six-month proration, and does the ceiling apply to the fiscal year or to the first 12 months of employment?
3. Does the $140,000 ceiling include employer on-costs and bonuses?
4. What exactly does p. 14 say?

### DECISION-MAKER SUMMARY
Do not approve as submitted. The total is mis-added; the correct figure is $127,900, not $138,900. The plan stays under the ceiling only by assuming a mid-year start and leaving out payroll on-costs and signing bonuses, and its salary figure cannot be checked against the cited survey. If it is approved anyway, a full-year or fully loaded cost would likely exceed $140,000 by a wide margin.

### OWNER SUMMARY
The hiring budget has an addition mistake, and its main salary figure comes from a report nobody has been able to check. It also counts only half a year of pay and leaves out costs such as payroll taxes and benefits. Once those are added, it probably goes over the approved limit, so it needs to be corrected before it goes to finance.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "Industry Survey 2026 p. 14", "status": "not_seen", "matters": true},
    {"item": "hire start dates / timeline", "status": "not_seen", "matters": true},
    {"item": "definition of $140,000 ceiling", "status": "not_seen", "matters": true},
    {"item": "basis for recruiter/equipment/onboarding figures", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "no personal data or credentials; internal pay planning only"},
  "findings": [
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "C", "location": "plan.md budget table, Total row", "scenario": "Line items sum to $127,900 but total states $138,900 (+$11,000); finance finds the mismatch or acts on wrong headroom.", "fix": "Correct total to $127,900 or identify the missing $11,000 item; re-add before resubmitting.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "A", "location": "plan.md budget table, salaries row 'prorated 6 months'", "scenario": "Request asks for first-year budget; unexplained 6-month proration. Full year is $168,000 in salary alone, over the $140,000 ceiling.", "fix": "State assumed start date and fiscal year; show full-year cost and year-2 run rate.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "UNVERIFIED", "track": "C", "location": "plan.md Market pay, 'Industry Survey 2026 (p. 14) ... $84,000'", "scenario": "The survey was not supplied; if the real median is higher or the figure is not base pay, offers fail and the salary line is understated.", "fix": "Quote p. 14 verbatim with region and definition; have someone with access confirm; cross-check a second source.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "PROBABLE", "track": "A", "location": "plan.md budget table (no on-cost line)", "scenario": "Payroll taxes and benefits (about 20-30% of salary) are omitted; loaded cost is about $145k-153k, over the ceiling.", "fix": "Add an employer on-cost line using the company loaded-cost rate.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "A", "location": "plan.md Market pay '70% of firms offer a signing bonus' vs budget table", "scenario": "Signing bonus cited as market norm but not budgeted; cost is unbudgeted or the candidate is lost.", "fix": "Add a signing-bonus line or state explicitly that none is offered."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "C", "location": "plan.md budget table: recruiter $19,750, equipment $11,400, onboarding $12,750", "scenario": "No basis given; recruiter fees billed on annualized salary exceed the budget.", "fix": "State the fee percentage and basis; cite quotes."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "A", "location": "plan.md Market pay 'median salary'", "scenario": "Budgeting at the median with no range; about half the market pays more and offers are declined.", "fix": "Provide P25-P75 and a target percentile."}
  ]
}
```
