**Review mode:** This is an independent review. The work was not produced in this conversation, so there is no shared-context anchoring. No tools were available, so findings rest on reading the text and on arithmetic.

**Scope note:** The context asks for "Track C (claims review)", but the skill defines no Track C. I applied Track A (decisions and analysis) with extra weight on claim verification, which matches the intent.

## Pass 1: Reconstruct

The plan claims that the market median salary for a senior data engineer in the region is $84,000, citing a paid survey that was not supplied. It budgets two hires at six months of prorated salary plus three overhead lines, and it concludes that the $138,900 total fits under the $140,000 ceiling.

For that to be correct, four things must hold:
- The survey figure is real, current, and regional.
- The ceiling covers only the first fiscal year, not an annual run-rate.
- Hires start at mid-year.
- No other cost categories apply, such as employer payroll burden, benefits or signing bonuses.
- The line items add up to the stated total.

**Load-bearing unstated assumptions:**
- The six-month start date.
- The ceiling means "first-year cash" rather than annual cost.
- Base salary at the median is enough to hire senior talent.

## Report

**VERDICT: REWORK.** The total is arithmetically wrong. Required cost categories are missing, and once they are added the "fits under $140,000" conclusion is unsupported and likely false. That conclusion is the one finance will act on.

**CONFIDENCE IN VERDICT: High.** The arithmetic error alone is enough. Confidence in the market-pay findings is lower because the survey was not available to check.

### Findings, ordered by severity

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | Budget table, "**Total** $138,900" | The line items sum to $127,900, not $138,900. 84,000 + 19,750 + 11,400 + 12,750 = 127,900, so the total is off by $11,000. | Finance re-adds the table, finds the error, and distrusts the whole plan. Or a line item is missing that silently makes up the $11,000, and nobody knows which number is real. | Recompute the total. If $138,900 is correct, find and add the missing $11,000 line. |
| 2 | Critical | CONFIRMED (omission) / PROBABLE (amount) | Budget table, compared with "The total fits inside the approved ceiling" | There is no employer payroll burden: payroll taxes, benefits, retirement contributions. These typically add about 20–30% of salary. On $84,000 of salary that is roughly $17,000–25,000. | Corrected total of $127,900 plus about $21,000 in burden gives about $149,000. That is over the $140,000 ceiling, and the plan has told finance it fits. | Add a fully loaded cost line using the company's actual burden rate, then re-test against the ceiling. |
| 3 | High | CONFIRMED | "70% of firms offer a signing bonus" compared with the budget table | The plan's own market claim says signing bonuses are standard, but none is budgeted. | The candidate expects a bonus, so either an unbudgeted cost appears or the offer loses to competitors. | Add a signing-bonus line, or state explicitly that none will be offered and accept the hiring risk. |
| 4 | High | CONFIRMED (assumption is unstated) | "for the first year, prorated 6 months" | The plan assumes a mid-year start without saying so. The request asked for a first-year budget, and it is unclear whether $140,000 is a fiscal-year cap or an annual run-rate cap. A full year of salary is $168,000, which exceeds the ceiling on salary alone. | 1. Hires start earlier and the budget overruns. 2. Finance reads the ceiling as annual and the year-two cost (about $168,000 plus burden) breaks it immediately. | State the assumed start date and the fiscal period. Show both the first-year cost and the annualized cost. Confirm with finance what the ceiling covers. |
| 5 | High | UNVERIFIED (PROBABLE concern) | "median salary… is **$84,000**" (Industry Survey 2026, p. 14) | The source was not supplied and cannot be checked. The figure looks low for "senior data engineer" in many markets; US figures commonly exceed $120,000. It is also unclear whether the figure is base salary or total compensation, and whether it covers this region and this seniority level. | The figure is misread (wrong role, wrong region, or a junior band) or fabricated. Offers come in below market, the hires fail, and the budget is rebuilt later. | Attach the survey excerpt (p. 14) showing role, region, seniority and pay basis. Cross-check against a second source, such as recent offers or a recruiter quote. |
| 6 | Medium | PROBABLE | "median salary" used as the offer amount | By definition, half the market pays more than the median. Senior hires in competitive markets often need offers at the 60th–75th percentile. | Candidates decline offers made at the median, and the hiring timeline slips. | Budget at a stated percentile (for example P60–P75), or give a range with a contingency. |
| 7 | Medium | UNVERIFIED | "recruiter fees $19,750" | The figure has no source or basis. Contingency fees are often 15–25% of first-year salary, which would be about $25,000–42,000 for two hires on $84,000–168,000. $19,750 is below that range. | The actual invoice exceeds the budget line. | State how the fee is calculated (percentage times which salary base) or cite the vendor quote. |
| 8 | Low | UNVERIFIED | "equipment and licences $11,400", "onboarding and training $12,750" | Neither amount has a source or breakdown. | Minor variance. Low risk individually. | Add a one-line basis for each, such as a per-head quote. |

### What holds up

- The salary arithmetic is internally consistent: 2 × $84,000 × 6/12 = $84,000.
- The structure (market pay followed by a cost table compared against the ceiling) is the right shape for finance.
- The plan answers the question that was asked; it has not drifted to an easier one.

### Unverified claims

| Claim | How to confirm |
|---|---|
| $84,000 median, Industry Survey 2026, p. 14 | Obtain the page. Check that role, region, seniority and pay basis match. |
| "70% of firms offer a signing bonus" | Same source. Check whether it applies to this role and region. |
| Recruiter fee, equipment and onboarding amounts | Vendor quotes or internal historical costs. |
| Six-month proration | Confirm the planned start dates. |

### Questions for the author

1. Does the $140,000 ceiling cover first-fiscal-year cash or annual cost, and what start date is assumed?
2. Where did the $11,000 difference between the line items and the total come from?
3. Is $84,000 base salary or total compensation, and does the survey's role definition match "senior data engineer" in our region?
4. Why are employer burden and signing bonuses excluded?

### Decision-maker summary

Do not send this to finance as written. The total is mis-added by $11,000, and payroll burden and signing bonuses are missing; once those are included, the plan very likely exceeds the $140,000 ceiling. Fix the arithmetic, add fully loaded costs, state the proration assumption, and attach the survey excerpt. If it goes anyway, the main risks are a budget overrun and below-market offers.

```json
{
  "verdict": "REWORK",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "Budget table, Total $138,900", "scenario": "Line items sum to $127,900; stated total is $11,000 off, undermining the plan's credibility with finance or hiding a missing line item.", "fix": "Recompute the total; if $138,900 is intended, identify and add the missing $11,000 line."},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "Budget table vs. 'The total fits inside the approved ceiling'", "scenario": "No employer payroll burden or benefits; adding roughly 20-30% on $84,000 salary pushes the corrected total to about $149,000, over the $140,000 ceiling.", "fix": "Add a fully loaded cost line at the company's actual burden rate and re-test against the ceiling."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "'70% of firms offer a signing bonus' vs. budget table", "scenario": "Plan cites bonuses as standard but budgets none; candidates expect one, creating an unbudgeted cost or lost offers.", "fix": "Add a signing-bonus line or explicitly decide to offer none and accept the hiring risk."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "'for the first year, prorated 6 months'", "scenario": "Unstated mid-year start; an earlier start or an annual reading of the ceiling ($168,000 full-year salary) breaks the budget.", "fix": "State the start date and fiscal period, show first-year and annualized cost, and confirm the ceiling's meaning with finance."},
    {"severity": "High", "evidence_level": "UNVERIFIED", "location": "'median salary ... $84,000' (Industry Survey 2026, p. 14)", "scenario": "Source not supplied; the figure looks low for senior data engineers and may be the wrong role, region, or pay basis, leading to below-market offers.", "fix": "Attach the p. 14 excerpt showing role, region, seniority and pay basis, and cross-check against a second source."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "Median used as offer amount", "scenario": "Half the market pays above the median; senior candidates decline and hiring slips.", "fix": "Budget at a stated percentile (P60-P75) or include a contingency range."},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "location": "Recruiter fees $19,750", "scenario": "Unsourced and below typical 15-25% contingency rates; the actual invoice exceeds the line.", "fix": "State the fee calculation basis or cite the vendor quote."},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "location": "Equipment $11,400; onboarding $12,750", "scenario": "Unsourced amounts may vary from actual cost.", "fix": "Add a per-head basis or quote for each line."}
  ]
}
```
