# Redteam report: Hiring plan cost section

**Review setup.** The work was not produced in this conversation, so there is no shared-context anchoring. No tools were available, so I checked the arithmetic by hand and could not check any external source. The context asks for "Track C (claims review)". This skill defines only Tracks A and B, so I applied Track A (decisions and analysis) with extra weight on factual claims.

## Pass 1: Reconstruct

The plan says the median salary for a senior data engineer in the region is $84,000, citing Industry Survey 2026, p. 14. It also says 70% of firms offer a signing bonus. It budgets two hires at $138,900 and concludes this fits under the $140,000 ceiling.

For this to be correct, all of the following must hold:
- The survey figures are real and quoted accurately.
- "First-year budget" can be met with 6 months of salary.
- The line items are complete.
- The total is the correct sum.
- The ceiling applies to this total.

---

**VERDICT: REWORK.** The stated total does not equal the sum of its own line items. The "fits the ceiling" conclusion depends on an unexplained 6-month proration. Budgeting a full first year exceeds the ceiling by about $72k.

**CONFIDENCE IN VERDICT: high.** The arithmetic and proration findings come straight from the text. The market-pay claims cannot be checked because the survey was not supplied.

## Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | Budget table, **Total** row | The line items add to $127,900 (84,000 + 19,750 + 11,400 + 12,750), not $138,900. The total is overstated by $11,000. | Finance checks the column, finds the error, and stops trusting the rest of the plan. Alternatively, a hidden item exists and the table omits it. | Recompute the total. If an $11,000 item is missing, add it as its own row. |
| 2 | Critical | CONFIRMED (6-month basis); PROBABLE (drift from request) | "2 x $84,000, for the first year, prorated 6 months" | The request asked for a first-year budget, but salary covers only 6 months, with no start date or reason given. A full year of salary is $168,000. With the other items as listed, the total becomes $211,900, which is $71,900 over the ceiling. | Finance approves $140k as the cost of the hires. Months 7 to 12 then appear as an unfunded overrun. | State the start date and fiscal-year boundary explicitly. Show both the current-fiscal-year cost and the 12-month run-rate. Compare the run-rate to the ceiling, or confirm the ceiling is fiscal-year scoped. |
| 3 | High | CONFIRMED (omission); UNVERIFIED (amount) | Budget table compared with the "Market pay" section | The plan says 70% of firms offer signing bonuses but budgets none. It also has no line for employer costs: payroll taxes, benefits, retirement contributions. | Competitive offers need a signing bonus, and employer costs add a significant percentage on top of salary. Actual spend exceeds the approved figure. | Add rows for signing bonus and employer load. Get the load rate from HR or payroll. |
| 4 | High | UNVERIFIED | "Industry Survey 2026 (p. 14) … $84,000 … 70%" | The whole market-pay section rests on a paid source that was not supplied. The page number, median, region definition and 70% figure cannot be confirmed and may be misquoted or fabricated. | The figure is wrong or covers a different region or role level. Every salary-driven number in the plan inherits the error. | Attach the page excerpt. Confirm the region and seniority definitions. Cross-check against a second independent source, such as internal comp bands or another survey. |
| 5 | Medium | PROBABLE | "median salary … $84,000" used as the offer amount | Budgeting at the median means about half the market pays more. Senior hires competing for talent often need offers above median. | Offers at $84k are declined. The search runs longer and recruiter costs rise. | Budget at a target percentile (for example P60 to P75) or a range, and state the choice. |
| 6 | Medium | UNVERIFIED | Recruiter fees $19,750; equipment $11,400; onboarding $12,750 | None of these items has a source or basis, such as a fee percentage or a quote. Agency fees are often quoted as a percentage of first-year salary, so this figure may be computed on the prorated base. | The fee is a percentage of annual salary, so the actual invoice is higher than budgeted. | Show the basis for each item: fee percentage times base, vendor quote, or internal standard cost. |
| 7 | Low | CONFIRMED | "The total fits inside the approved ceiling" | Even on the plan's own figures, headroom is $1,100 (0.8%), with no contingency line. | Any small variance breaches the ceiling. | Add a contingency line or state the remaining headroom explicitly. |

## What holds up

- 2 × $84,000 × 6/12 = $84,000 is arithmetically correct.
- The table structure is clear.
- The plan names its source and page, so the claim can be checked once the survey is available.

## Unverified claims

1. **$84,000 regional median.** Confirm with the survey p. 14 excerpt plus a second source.
2. **70% of firms offer a signing bonus.** Confirm with the same excerpt.
3. **"p. 14" citation.** Confirm the page exists and contains these figures.
4. **Recruiter, equipment and onboarding amounts.** Confirm with vendor terms or internal cost standards.
5. **The ceiling applies to this total.** Confirm with the approval memo.

## Questions for the author

1. Is $138,900 a typo, or is there an $11,000 item missing from the table?
2. Why 6 months? Is the $140k ceiling for the current fiscal year or for the hires' first 12 months?
3. Are signing bonuses and employer costs (taxes and benefits) intentionally excluded? If so, where are they funded?

## Decision-maker summary

Do not send this to finance as is. The total is wrong by $11,000, and a full first year of salary puts the cost at about $212k against a $140k ceiling, before signing bonuses and benefits. Ask for a corrected table with a 12-month run-rate and a sourced market-pay figure. If it goes anyway, the main risk is an unfunded overrun of at least $70k later in the year.

```json
{
  "verdict": "REWORK",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "Budget table, Total row ($138,900)", "scenario": "Line items sum to $127,900; the stated total is off by $11,000, so finance finds the error or an item is missing from the table.", "fix": "Recompute the total; if an $11,000 item exists, add it as an explicit row."},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "salaries row: '2 x $84,000, for the first year, prorated 6 months'", "scenario": "A first-year budget covers only 6 months of salary; the full year is $168,000 salaries and $211,900 total, $71,900 over the $140,000 ceiling, so months 7-12 become an unfunded overrun.", "fix": "State the start date and fiscal-year scope; show both the current-FY cost and the 12-month run-rate against the ceiling."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "Budget table vs Market pay section (70% signing bonus)", "scenario": "Signing bonus and employer costs (payroll taxes, benefits) are omitted, so actual spend exceeds the approved figure.", "fix": "Add signing-bonus and employer-load rows using HR/payroll rates."},
    {"severity": "High", "evidence_level": "UNVERIFIED", "location": "Market pay: 'Industry Survey 2026 (p. 14) ... $84,000 ... 70%'", "scenario": "The paid source was not supplied; if the figures are misquoted or fabricated, or cover a different region or level, all salary-based numbers are wrong.", "fix": "Attach the p. 14 excerpt and cross-check against a second independent comp source."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "Market pay: median $84,000 used as the offer amount", "scenario": "Offers at the median for senior hires are declined, extending the search and raising recruiting cost.", "fix": "Budget at a stated target percentile or a range."},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "location": "Rows: recruiter fees $19,750, equipment $11,400, onboarding $12,750", "scenario": "Amounts are unsourced; if the recruiter fee is a percentage of annual salary, the invoice exceeds the budget line.", "fix": "Show the basis for each amount (fee % x base, vendor quote, internal standard)."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "'The total fits inside the approved ceiling of $140,000.'", "scenario": "Only $1,100 headroom with no contingency; any variance breaches the ceiling.", "fix": "Add a contingency line and state the headroom explicitly."}
  ]
}
```