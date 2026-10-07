**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools or subagent were available, so I reviewed it myself. The work was supplied as input, not authored in this conversation.

## Pass 1: Reconstruct

The plan claims the regional median salary for a senior data engineer is $84,000, citing Industry Survey 2026, p. 14. It also claims 70% of firms offer a signing bonus. It budgets two hires at $138,900 and concludes this fits the $140,000 ceiling. For that to be correct:

- the survey must say what is cited;
- the line items must sum to the stated total;
- six months of salary must be the right basis for a "first-year budget";
- the list of cost lines must be complete.

Unstated assumptions:

- The hires start mid-year.
- The ceiling is a first-year total, not an annual run-rate.
- No signing bonus, benefits or employer payroll taxes are needed.

Tracks: **C** (requested), plus **A** on requirement fit, because finance will rely on the conclusion.

## Report

**VERDICT: REWORK.** The stated total does not reproduce from its own line items. The "fits the ceiling" conclusion also rests on an unstated six-month proration and omitted cost lines.

**CONFIDENCE: medium.** The arithmetic is certain. The survey claims cannot be checked because the source was not supplied. Plausibility judgements on pay and overheads come without tools or a stated region.

**INPUTS LEDGER:**

| Item | Status | Does the gap matter? |
|---|---|---|
| request.md, context.md, plan.md | Seen | — |
| Industry Survey 2026, p. 14 | Not seen; paid source, not supplied | Yes. Both market-pay claims depend on it. |
| Which region "our region" means | Not stated | Yes. The salary benchmark depends on it. |
| Sources for recruiter, equipment and onboarding figures | None given | Moderately |
| Start dates and fiscal-year definition | Not given | Yes. The proration depends on them. |
| Meaning of the ceiling (first-year total or annual) | Not given | Yes |

**SEATS AND GATE:** Only the local same-context reviewer ran. The gate flags the material as sensitive: internal compensation and budget data is confidential business material. Cross-vendor seats were therefore refused. None were requested anyway.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | High | CONFIRMED | C | plan.md, budget table, **Total** row | The line items sum to **$127,900** (84,000 + 19,750 + 11,400 + 12,750), not $138,900. The stated total is overstated by $11,000. | Finance approves or challenges a figure that does not reproduce. Either $11,000 is over-allocated, or there is a missing $11,000 line item (for example a signing bonus) that was dropped from the table but kept in the total. Either way the document loses credibility at review. | Recompute the total. If an $11,000 item was intended, add it as an explicit line. | Confirmed. Re-summed twice: 103,750, then 115,150, then 127,900. |
| 2 | High | CONFIRMED (the text says it); PROBABLE (impact) | A/C | plan.md, salaries row: "2 x $84,000, for the first year, prorated 6 months" | The request asks for a "first-year budget", but salaries are prorated to 6 months with no start date or reason. "For the first year, prorated 6 months" contradicts itself. Full-year salary for two is $168,000, which alone exceeds the $140,000 ceiling. | Finance reads "fits the ceiling" as covering the first year of employment. From year 2, or if the ceiling is annual, salaries alone break it by $28,000+. | State the start dates and fiscal-year basis. Show both the first-fiscal-year cost and the annualized run-rate. Confirm with finance what the ceiling covers. | Confirmed. The strongest defence is a mid-fiscal-year start, which would make the proration legitimate, but that is stated nowhere. As written, the "fits" claim depends on it. |
| 3 | High | PROBABLE | A/C | plan.md, budget table (absent lines) | No employer payroll taxes or benefits, typically about 20–30% of salary. No signing bonus, even though the plan says 70% of firms offer one. | Adding a conservative 20% load on $84,000 (about $16,800) pushes the corrected $127,900 to about $144,700, over the ceiling, before any signing bonus. The plan then gets approved and breaks the budget once hiring happens. | Add benefits/payroll load and a signing-bonus line (or state "no signing bonus" and the hiring risk that carries). Source the load rate from HR or finance. | Confirmed as an omission. The rate is an assumption, so the evidence level stays PROBABLE. |
| 4 | Medium | UNVERIFIED | C | plan.md, Market pay: "median salary … $84,000" (Survey p. 14) | The source was not supplied and cannot be checked. The region is unnamed. $84,000 also looks low for a *senior* data engineer in many markets, so it may be misread: a different role, level or region, or base vs. total pay. | Offers at $84,000 fail to land candidates. Budget and timeline then slip after approval. | Attach the p. 14 excerpt (table, role, level, region, base or total). Cross-check against one free source (public salary data, recent offers, a recruiter quote). | n/a |
| 5 | Medium | UNVERIFIED | C | plan.md, Market pay: "70% of firms offer a signing bonus" | Unverifiable for the same reason. The plan cites the figure but never uses it in the budget (see #3). | The statistic is wrong or mis-scoped, or it is right and silently ignored. | Quote the passage. Either budget for it or explain why not. | n/a |
| 6 | Medium | UNVERIFIED | C | plan.md, recruiter fees $19,750; equipment $11,400; onboarding $12,750 | No source or basis for any figure. Recruiter fees work out to about 11.8% of $168,000 annual salary, below common agency rates of about 15–25%. | Actual fees come in higher. For example, 20% of $168,000 is $33,600, which adds about $14,000. | Cite the quotes or contracts, or show the formula behind each figure. | n/a |
| 7 | Low | PROBABLE | C | plan.md, Market pay | "Median" is used as the budget figure. Senior hires in a competitive market often land above median. | Offers at median lose candidates. | Budget a range (for example median to 75th percentile) and show the ceiling at each point. | n/a |

## Assessment

**WHAT HOLDS UP:**
- The salary-row arithmetic is internally correct: 2 × $84,000 × 0.5 = $84,000.
- Even with the corrected total of $127,900, the line items as listed fit the ceiling.
- The plan cites a specific source and page, which makes it checkable once someone supplies the excerpt.

**UNVERIFIED CLAIMS:**
- The $84,000 regional median. Settle it with the p. 14 excerpt plus a second source.
- The 70% signing-bonus share. Settle it with the p. 14 excerpt.
- The recruiter, equipment and onboarding figures. Settle them with vendor quotes or internal rates.

**QUESTIONS FOR THE AUTHOR:**
1. Where does $138,900 come from? Is an $11,000 line missing?
2. Why 6 months? What are the expected start dates, and does the $140,000 ceiling cover the first fiscal year or annual cost?
3. Are benefits, payroll taxes and signing bonuses excluded on purpose, and does finance budget them elsewhere?
4. What region and role level does the survey figure on p. 14 refer to, and is it base or total pay?

**DECISION-MAKER SUMMARY:** Do not send this to finance as is. The total is arithmetically wrong by $11,000. The "fits the ceiling" claim rests on an unexplained six-month proration and leaves out benefits and bonuses, which likely push the real first-year cost over $140,000. Two full-year salaries alone would come to $168,000. If it goes forward anyway, expect either a rejected plan or an approved budget that is exceeded once the hires start.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "Industry Survey 2026 p. 14", "status": "not_seen", "matters": true},
    {"item": "region definition", "status": "not_seen", "matters": true},
    {"item": "start dates / fiscal-year basis / ceiling scope", "status": "not_seen", "matters": true},
    {"item": "sources for recruiter, equipment, onboarding costs", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": true, "reason": "internal compensation and budget data; no external seats used"},
  "findings": [
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "C", "location": "plan.md budget table, Total row",
     "scenario": "Line items sum to $127,900, not $138,900; finance receives a total that does not reproduce ($11,000 discrepancy, possibly a dropped line item).",
     "fix": "Recompute the total; add any intended $11,000 item as an explicit line.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "A", "location": "plan.md salaries row ('for the first year, prorated 6 months')",
     "scenario": "A 'first-year budget' uses 6 months of salary without a stated start date; full-year salaries are $168,000, exceeding the $140,000 ceiling, so 'fits the ceiling' misleads finance.",
     "fix": "State start dates and fiscal basis; show first-fiscal-year and annualized cost; confirm the ceiling's scope.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "PROBABLE", "track": "A", "location": "plan.md budget table (missing lines)",
     "scenario": "Benefits/payroll taxes (~20%+) and signing bonuses are omitted; adding ~$16,800 load alone takes the corrected $127,900 to ~$144,700, over the ceiling.",
     "fix": "Add benefits/payroll load and a signing-bonus line (or an explicit exclusion) using HR/finance rates.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "C", "location": "plan.md Market pay, '$84,000 median' (Survey p. 14)",
     "scenario": "Source not supplied; the figure may be mis-scoped (role, level, region, base vs total) and look low for senior roles, causing failed offers.",
     "fix": "Attach the p. 14 excerpt and cross-check with a second source.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "C", "location": "plan.md Market pay, '70% of firms offer a signing bonus'",
     "scenario": "Unverifiable statistic, and it is never reflected in the budget.",
     "fix": "Quote the source passage; budget for it or justify its exclusion.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "C", "location": "plan.md recruiter fees $19,750; equipment $11,400; onboarding $12,750",
     "scenario": "Unsourced figures; recruiter fees at ~11.8% of annual salary are below common 15-25% rates, so actual fees could add ~$14,000.",
     "fix": "Cite quotes/contracts or show the derivation of each figure.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "C", "location": "plan.md Market pay",
     "scenario": "Budgeting at median for senior hires risks offers below market and lost candidates.",
     "fix": "Budget a range (median to 75th percentile) and show the ceiling impact at each point.", "status": "n/a"}
  ]
}
```
