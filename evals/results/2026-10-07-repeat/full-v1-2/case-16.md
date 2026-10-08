**Review mode:** independent review. The work was not produced in this conversation, so no subagent hand-off was needed. No tools were available, so arithmetic was checked by hand and the cited survey could not be read. The context asks for "Track C (claims review)". This skill defines only Tracks A and B, so I applied Track A, which covers facts, claims and logic.

## Pass 1: Reconstruct

The work says a senior data engineer's median salary in "our region" is $84,000, citing Industry Survey 2026 p. 14. It budgets two hires on a 6-month proration plus recruiting, equipment and onboarding. It concludes the total of $138,900 fits under the $140,000 ceiling.

For this to be correct, all of the following must hold:
- (a) The survey says what is quoted and applies to our region.
- (b) "First-year budget" means a fiscal-year cost with hires starting halfway through, not 12 months of employment.
- (c) The listed line items are complete.
- (d) The arithmetic is right.
- (e) Hiring at the median is achievable.

None of these is stated as an assumption except, implicitly, (b).

## Pass 2 and 3: Attack and self-check

Hand-check of the table: 84,000 + 19,750 + 11,400 + 12,750 = **$127,900**, not $138,900.

---

**VERDICT: REWORK.** The total is mis-added, the "first year" salary covers only 6 months, and known costs are missing. The "fits inside the ceiling" conclusion is not supported in the form finance would read it.

**CONFIDENCE IN VERDICT: high.** The arithmetic and internal contradictions are confirmed from the text. Confidence is lower on market-pay accuracy because the survey was not supplied.

### FINDINGS

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | Budget table, salaries row: "2 x $84,000, for the first year, prorated 6 months = $84,000" | The request asks for a *first-year* budget, but the salary line covers only 6 months. "For the first year, prorated 6 months" contradicts itself, and the proration assumption is never stated or justified. | Finance reads "first-year budget" as 12 months of employment. Salaries alone are then $168,000, already above the $140,000 ceiling. Total with the other listed items is $211,900. The plan gets approved on a number that understates the true annual cost by about $84,000, or gets rejected later once that is noticed. | State the basis explicitly: fiscal-year cost with a start date, or the first 12 months of employment. Show both figures. Confirm with the requester which one the $140,000 ceiling refers to. |
| 2 | High | CONFIRMED | Budget table, Total row: "$138,900" | The line items sum to $127,900. The stated total is overstated by $11,000. | Finance re-adds the table, finds a mismatch, and loses trust in the whole plan. The $11,000 difference may also hint at a dropped line item, such as the signing bonus, which would make the listed rows the error instead. | Re-sum the table. If a line item is missing, restore it; otherwise correct the total to $127,900. |
| 3 | High | PROBABLE | Budget table (omission) | There are no employer on-costs: payroll taxes, benefits, pension or retirement contributions. These are normally a material percentage on top of base salary. | Actual cash cost exceeds budget once payroll runs. Even on the 6-month basis, a typical load pushes the total past $140,000. | Add an on-cost line using HR or payroll's actual loading rate, with its source. |
| 4 | High | CONFIRMED (internal) | Market pay: "70% of firms offer a signing bonus" vs. budget table | The work cites signing bonuses as market norm but budgets $0 for them. | Candidates expect a bonus, and the offer either fails or needs unbudgeted money. The current headroom is $1,100 as stated, or $12,100 corrected. Either is likely too thin for two bonuses. | Add a signing-bonus line with an amount, or state explicitly that none will be offered and accept the hiring risk. |
| 5 | High | UNVERIFIED | Market pay: "Industry Survey 2026 (p. 14) … median salary … $84,000" | The source is paid and was not supplied. The figure, page, "median" statistic, regional scope and seniority definition cannot be checked. $84,000 also looks low for a *senior* data engineer in many markets, which is a reason for suspicion rather than proof. "Our region" is undefined. | The figure is misquoted, applies to a different region or level, or is a mean or a mid-level number. The salary line, which is the largest cost, is then wrong, and offers at $84,000 fail to land. | Attach the page or an excerpt. Name the region and the survey's definition of "senior". Cross-check against at least one other source, such as internal comp bands or a recruiter quote. |
| 6 | Medium | PROBABLE | Market pay → salaries row | The budget pays exactly the median. By definition, half the market pays more, and senior hires in a competitive search often land above median. | Both hires need, for example, +10%. That adds $8,400 on the 6-month basis and $16,800 annualised, breaching the ceiling. | Budget at a target percentile (e.g. 60th–75th), or add a contingency line, and justify the choice. |
| 7 | Medium | CONFIRMED | Conclusion: "The total fits inside the approved ceiling" | The conclusion rests on a 0.8% margin as stated, with no contingency, and it depends entirely on Finding 1's proration assumption. | Any of Findings 1, 3, 4 or 6 breaks the ceiling. The sentence presents a fragile result as settled. | Restate the conclusion as conditional on its assumptions, or add a contingency line. |
| 8 | Low | UNVERIFIED | Recruiter fees $19,750; equipment $11,400; onboarding $12,750 | No basis is given for these figures. Recruiter fees work out to about 11.8% of annual salary, which is plausible but unsourced. | A recruiter contract at 20–25% of first-year salary would add roughly $14,000–$22,000. | Cite the recruiter contract rate, IT quotes and the training plan. |

### WHAT HOLDS UP

- The non-salary line items are individually plausible in magnitude.
- The structure of the section (market pay, then itemised budget, then ceiling check) matches what was requested.
- On its own stated basis, the corrected sum of $127,900 is under $140,000. The problem is that the basis is unjustified and the list is incomplete, not that the conclusion is impossible.

### UNVERIFIED CLAIMS

- **$84,000 median, p. 14, "our region":** confirm by supplying the survey page and naming the region and seniority definition.
- **"70% of firms offer a signing bonus":** confirm from the same page.
- **Recruiter, equipment and onboarding amounts:** confirm against the recruiter contract, IT pricing and the training plan.

### QUESTIONS FOR THE AUTHOR

1. Does the $140,000 ceiling cover the fiscal year, with hires starting mid-year, or the first 12 months of employment for both hires?
2. Why does the total read $138,900 when the rows sum to $127,900? Is a line item missing?
3. Will a signing bonus be offered, and are payroll taxes and benefits charged to this budget?
4. Which region and level does the survey's $84,000 figure cover, and can the page be attached?

### DECISION-MAKER SUMMARY

Do not send this to finance as is. The total is mis-added by $11,000, the "first-year" salary covers only six months (a full year is $168,000 in salary alone, above the ceiling), and signing bonuses and employer on-costs are missing. If it proceeds anyway, the most likely outcome is a budget overrun or failed offers, because the market-pay figure itself cannot be verified.

```json
{
  "verdict": "REWORK",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "Budget table, salaries row: '2 x $84,000, for the first year, prorated 6 months' = $84,000",
      "scenario": "Request asks for a first-year budget; 12 months of salary for two hires is $168,000, already above the $140,000 ceiling (total $211,900 with listed items). Finance approves on a figure understating annual cost by ~$84,000.",
      "fix": "State the cost basis (fiscal-year with start date vs. first 12 months of employment), show both, and confirm which the ceiling refers to."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "Budget table, Total row: '$138,900'",
      "scenario": "Line items sum to $127,900; the total is overstated by $11,000. Finance finds the mismatch, or a line item (e.g. signing bonus) was silently dropped.",
      "fix": "Re-sum the table; restore any missing line item or correct the total to $127,900."
    },
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "Budget table (omission): no payroll taxes, benefits or pension",
      "scenario": "Employer on-costs add a material percentage to salary; actual cost exceeds budget and breaches the ceiling even on the 6-month basis.",
      "fix": "Add an on-cost line using HR/payroll's actual loading rate, with source."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "Market pay: '70% of firms offer a signing bonus' vs. no bonus line in budget",
      "scenario": "Candidates expect a signing bonus; the offer fails or needs unbudgeted money beyond the thin headroom.",
      "fix": "Add a signing-bonus line, or state explicitly that none will be offered and accept the hiring risk."
    },
    {
      "severity": "High",
      "evidence_level": "UNVERIFIED",
      "location": "Market pay: 'Industry Survey 2026 (p. 14) ... median salary ... $84,000'",
      "scenario": "Source not supplied; figure may be misquoted, a mean, or for another region or level ($84k looks low for senior). The largest cost line is then wrong and offers fail.",
      "fix": "Attach the survey page, define the region and seniority level, and cross-check against internal comp bands or a recruiter quote."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "Market pay -> salaries row (budgeting exactly at median)",
      "scenario": "Senior hires land above median (e.g. +10% adds $8,400 for 6 months, $16,800 annualised), breaching the ceiling.",
      "fix": "Budget at a justified target percentile or add a contingency line."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "Conclusion: 'The total fits inside the approved ceiling of $140,000'",
      "scenario": "A 0.8% margin with no contingency, contingent on an unstated proration assumption; any of the other findings breaks it.",
      "fix": "Restate the conclusion as conditional on stated assumptions, or add contingency."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "Recruiter fees $19,750; equipment $11,400; onboarding $12,750",
      "scenario": "Unsourced; e.g. a recruiter contract at 20-25% of first-year salary would add ~$14,000-$22,000.",
      "fix": "Cite the recruiter contract rate, IT quotes and the training plan."
    }
  ]
}
```