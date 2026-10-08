# Redteam review: hiring plan cost section

**VERDICT: REWORK.** The stated total does not add up from its own lines. The plan also appears to fit the $140,000 ceiling only because it counts half a year of salary and leaves out employer on-costs and signing bonuses.

**CONFIDENCE: medium.** No tools were available in this session and no fresh-instance reviewer was used, so this is a same-context review with anchoring risk; re-run it in a fresh session for anything high-stakes. The arithmetic finding is certain. The survey claims cannot be checked because the source was not supplied.

**INPUTS LEDGER**
- **Seen:** the original request (request.md), the context (context.md) and the work (plan.md).
- **Not seen: Industry Survey 2026, p. 14.** This is a paid publication and was not supplied. **This gap matters.** The $84,000 median is the base for the salary line, so the whole budget depends on it.
- **Not seen: a quote or basis for the recruiter, equipment and onboarding figures.** This matters moderately.
- **Not seen: the planned start date or the fiscal-year definition.** **This gap matters.** It decides whether 6-month proration is legitimate.
- **Not seen: any employer on-cost rate (payroll tax, benefits).** **This gap matters.**

**SEATS AND GATE**
- One reviewer ran, in this session (Claude). No subagent or cross-vendor seats were available.
- Sensitivity gate: no personal data, credentials or client records were found. The material is internal budget data and was not sent anywhere.

## Pass 1: Reconstruct

The work claims the median senior data engineer salary in the region is $84,000, citing the survey. It says first-year costs for two hires total $138,900, which fits under the $140,000 ceiling.

For this to be correct, all of the following must hold:
1. The survey says exactly this.
2. "First year" can legitimately mean 6 months of salary.
3. The line items sum to the total.
4. Base salary plus the four listed items covers all first-year costs.

Unstated assumptions:
- Both hires start at mid-year.
- Hiring at the median will be enough to attract senior candidates.
- No signing bonus will be paid.
- No employer payroll costs apply.

Tracks: C (as requested), plus A for the budget conclusion.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | High | CONFIRMED | C | plan.md budget table, Total row | The total is wrong. 84,000 + 19,750 + 11,400 + 12,750 = **$127,900**, not $138,900. The difference is $11,000. | Finance approves a figure that does not reproduce from its own lines. This undermines trust in every other number, or hides a missing $11,000 line item. | Correct the total to $127,900, or add the omitted item that explains the $11,000. | Confirmed: the sum was recomputed twice. |
| 2 | High | CONFIRMED (contradiction in the text); impact PROBABLE | A/C | Salaries row: "for the first year, prorated 6 months" | The request asks for a **first-year budget**. The row counts only 6 months of salary for two hires, with no start date given. Twelve months is 2 × $84,000 = $168,000, which alone exceeds the $140,000 ceiling. With the other items as listed, the full-year total is **$211,900**. | Finance reads "first year" as the first 12 months of employment and approves $140k. The real cost of the first year is about $212k or more, an overrun of roughly $72k or more. | State the assumed start date and the fiscal-year boundary. Show both the in-fiscal-year cost and the 12-month cost. Re-test both against the ceiling. | Defender's case: "first year" could mean the fiscal year with a mid-year start. This is not refuted, but the plan never states that assumption, so the finding is held. |
| 3 | High | PROBABLE | A | Budget table (missing rows) | There is no line for employer on-costs: payroll taxes, benefits, pension or retirement. These are usually a material percentage of salary. | Even with the corrected $127,900 total, on-costs of about 15% on the $84,000 salary line (about $12.6k) push the total over $140,000. | Add an on-cost line using HR or finance's standard loading rate. | Confirmed as an omission. The exact rate is UNVERIFIED. |
| 4 | High | UNVERIFIED | C | Market pay paragraph: "Industry Survey 2026 (p. 14) … median salary … $84,000" | The source was not supplied and cannot be read. It is unknown whether p. 14 says median rather than mean, base pay rather than total compensation, senior rather than all levels, and our region rather than national. $84,000 is also low for a senior data engineer in many markets, so it needs checking. | The real figure is higher or measures something different. Offers at $84k fail, and the budget is understated. | Attach the p. 14 table or quote it verbatim with the region, level and pay definition. Cross-check against a second source, such as recent offers or an open salary dataset. | Held as UNVERIFIED. It is not shown as confirmed wrong. |
| 5 | Medium | CONFIRMED (internal inconsistency) | A/C | "70% of firms offer a signing bonus" versus the budget table | The plan states that signing bonuses are the norm (and this claim is itself UNVERIFIED), but budgets none. | Candidates expect a bonus. An unbudgeted $10–20k per hire appears mid-process. | Either budget a signing-bonus line or state explicitly that no bonus will be offered and accept the hiring risk. | n/a |
| 6 | Medium | UNVERIFIED | C | Recruiter, equipment and onboarding rows | No basis is given for $19,750, $11,400 or $12,750. Recruiter fees are typically a percentage of annual salary. $19,750 is about 11.8% of $168k, which is below common agency rates. | Actual agency fees come in higher and the budget overruns. | Cite the recruiter contract rate and the equipment and training quotes. | n/a |

## What holds up

- 2 × $84,000 × 6/12 = $84,000 is arithmetically correct as written.
- The request's structure (market pay plus a first-year budget against a ceiling) is followed.
- The ceiling figure of $140,000 matches the request.

## Unverified claims

- **The $84,000 median, survey p. 14.** Settle it by producing the page and checking the region, level and pay definition.
- **"70% of firms offer a signing bonus."** Settle it the same way, from the same source.
- **The recruiter, equipment and onboarding amounts.** Settle them with contracts or quotes.

## Questions for the author

1. What start date and fiscal-year definition does "first year, prorated 6 months" assume?
2. What is the missing $11,000 in the total? Is it a dropped line, or an error?
3. Does the survey figure describe base or total compensation, for senior level in our region? Can you attach p. 14?
4. Why are employer on-costs and signing bonuses excluded?

## Decision-maker summary

Do not send this to finance as is. The total is overstated by $11,000 (it should be $127,900). Once full-year salary or employer on-costs are counted, the plan very likely exceeds the $140,000 ceiling, and the salary basis is unverified.

If it is approved as is, the realistic risk is a first-year overrun of tens of thousands of dollars, and offers that fail if the market figure is wrong.

## Owner summary

The cost section's total does not match its own line items. It also looks like it fits the budget only because it counts half a year of pay and leaves out payroll costs and signing bonuses. Please fix the total, state the assumed start date, add the missing costs and attach the salary source before this goes to finance.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "Industry Survey 2026 p. 14", "status": "not_seen", "matters": true},
    {"item": "start date / fiscal-year definition", "status": "not_seen", "matters": true},
    {"item": "employer on-cost rate", "status": "not_seen", "matters": true},
    {"item": "recruiter/equipment/onboarding quotes", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "internal budget figures only; nothing sent externally"},
  "findings": [
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "C", "location": "plan.md budget table, Total row",
     "scenario": "Line items sum to $127,900, not the stated $138,900; finance approves a figure that does not reproduce and may hide a dropped $11,000 item.",
     "fix": "Correct the total to $127,900 or add the missing line item.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "A", "location": "plan.md Salaries row: 'for the first year, prorated 6 months'",
     "scenario": "Request asks for a first-year budget; 12 months of salary is $168,000 (full total $211,900), exceeding the $140,000 ceiling; finance approves believing the first year is covered.",
     "fix": "State start date and fiscal-year basis; show both in-fiscal-year and 12-month cost against the ceiling.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "PROBABLE", "track": "A", "location": "plan.md budget table (no on-cost row)",
     "scenario": "Employer payroll taxes and benefits omitted; even on the corrected $127,900, ~15% on-costs (~$12.6k) push the total over $140,000.",
     "fix": "Add an on-cost line at finance's standard loading rate.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "UNVERIFIED", "track": "C", "location": "plan.md Market pay: 'Industry Survey 2026 (p. 14) ... median salary ... $84,000'",
     "scenario": "Source not supplied; if the figure is mean, base-only, all-levels, national, or simply higher, offers fail and the budget is understated.",
     "fix": "Attach or quote p. 14 with region, level and pay definition; cross-check with a second source.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "A", "location": "plan.md '70% of firms offer a signing bonus' vs budget table",
     "scenario": "Plan says signing bonuses are standard but budgets none; an unbudgeted bonus per hire appears mid-process.",
     "fix": "Budget a signing-bonus line or explicitly decide not to offer one.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "C", "location": "plan.md recruiter fees, equipment, onboarding rows",
     "scenario": "No basis given; recruiter fee is ~11.8% of annual salary, below common agency rates; actual invoices exceed budget.",
     "fix": "Cite contract rates and quotes for each line.", "status": "n/a"}
  ]
}
```