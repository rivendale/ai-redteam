**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** This session has no tools, so I could not delegate to a subagent. The work was not written in this conversation. Every figure below was recomputed by hand.

VERDICT: **REWORK**. The stated total does not match its own line items, and the "fits inside the ceiling" conclusion depends on an unstated six-month salary proration.

CONFIDENCE: **medium**. The arithmetic findings are certain. Confidence is limited by:
- no tools,
- no access to the Industry Survey 2026,
- no stated start dates or definition of "first year".

INPUTS LEDGER:
- **Seen:** request.md (verbatim), context.md, plan.md.
- **Not seen:** Industry Survey 2026, p. 14 (paid, not supplied). This **matters**: the $84,000 median and the 70% signing-bonus figure rest on it, and the salary line drives the whole budget.
- **Not seen:** any basis for the recruiter fee, equipment or onboarding figures (quotes, rate cards, past invoices). This **matters**: $43,900 of the budget is unsupported.
- **Not seen:** the hires' start dates or what period "first year" means (fiscal year or first 12 months of employment). This **matters**: the ceiling conclusion depends on it.

COVERAGE:
- **Checked:**
  - plan.md "Market pay" section (2 claims)
  - plan.md "Budget for the two hires" table: each line, the total, and the ceiling statement
  - the proration assumption
- **Not checked:**
  - the survey's contents (not supplied)
  - the source of each cost line (not supplied)
  - whether the $140,000 ceiling is meant to cover all costs or salaries only (request ambiguous)

SEATS AND GATE: one same-context local reviewer ran. No cross-vendor seats were run because they were not requested and the depth is standard. Sensitivity gate: no personal data, credentials or client records. The work contains internal budget figures only, so the gate passed.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | C | plan.md, budget table, "**Total** \| **$138,900**" | The total does not reproduce from its lines. 84,000 + 19,750 + 11,400 + 12,750 = **$127,900**, not $138,900, a gap of $11,000. | Finance re-adds the table and finds a $11,000 discrepancy. Either the total is a typo, or a line item (about $11,000) was dropped from the table but kept in the total. Either way, finance cannot tell what is actually being approved. | Recompute the total. If an $11,000 item exists, restore it as a labelled line. To reproduce: add the four cost cells and compare the result with the stated total. | a✓ b✓ c✗ d✓ |
| F2 | High | PROBABLE | C/A | plan.md, salary line: "2 x $84,000, for the first year, prorated 6 months" → $84,000; and "The total fits inside the approved ceiling" | The request asks for a **first-year budget**. The plan silently counts only 6 months of salary, and its own label says "for the first year". No start date or fiscal-year basis is given. | Finance reads "first year" as 12 months. Salaries are then 2 × $84,000 = $168,000, and the total becomes $211,900 using the plan's own lines (or $222,900 using its stated total). That is far above the $140,000 ceiling, so the "fits" conclusion is reversed. Even with proration, the year-two run rate of $168,000+ already exceeds the ceiling. | State the start dates and the budget period explicitly. Show both the prorated first-period cost and the full annual cost. Re-test against the ceiling on whichever basis finance uses. | a✓ b✗ c✓ d✓ |
| F3 | Medium | CONFIRMED | C | plan.md, "70% of firms offer a signing bonus" vs. the budget table (no bonus line). The table also has no employer payroll taxes or benefits line. | The plan cites signing bonuses as market practice, then budgets none. Employer on-costs, normally a material share of salary, are also absent. | Offers need a signing bonus to compete, or on-costs land in the first payroll. Actual spend then exceeds the approved figure and a second approval is needed. | Add a signing-bonus line, or an explicit statement that none will be offered. Add an employer on-costs line, or state that it is budgeted elsewhere. | a✓ b✓ c✗ d✗ |

Notes on the severity answers:
- **F1, c = false:** the corrected $127,900 still fits under the ceiling, so the error alone does not reverse the conclusion. It still makes the deliverable wrong.
- **F2, b = PROBABLE:** whether "first year" means 12 months of salary is an inference about the request, not a certainty.
- **F3, d = false:** the 70% figure is itself unverified.

### NEEDS VALIDATION
- **S1, market pay.** The $84,000 regional median for a senior data engineer is unverified. *Settled by:* the text of Industry Survey 2026, p. 14, showing the figure, the role definition, the region and the statistic (median of base pay vs. total compensation).
- **S2, signing bonus.** The "70% of firms offer a signing bonus" claim is unverified. *Settled by:* the same survey page.
- **S3, recruiter fees ($19,750).** No basis is given. This is about 11.8% of $168,000 annual salary, below many contingency rates. *Settled by:* the recruiter agreement or quoted fee percentage.
- **S4, equipment, licences, onboarding and training ($11,400 and $12,750).** No basis is given. *Settled by:* vendor quotes or past per-hire actuals.
- **S5, the ceiling.** It is unclear whether the $140,000 ceiling covers total first-year cost or salaries only. *Settled by:* the approval document that set the ceiling.

### REFUTED
- **C1:** "2 × $84,000 prorated 6 months ≠ $84,000." **Refuted.** 2 × 84,000 = 168,000, and 168,000 × 6/12 = 84,000, so the line's arithmetic is correct. The problem is the assumption behind it (F2), not the multiplication.
- **C2:** "The ceiling is breached on the plan's own prorated basis." **Refuted.** The corrected total of $127,900 and the stated total of $138,900 are both below $140,000.

### WHAT HOLDS UP
- The salary-line arithmetic is internally correct.
- The survey is cited with a page number, so it can be checked.
- On the plan's own prorated basis, even the overstated total sits under the ceiling.

### UNVERIFIED CLAIMS
- **$84,000 median** and **70% signing-bonus prevalence**: confirm by reading Industry Survey 2026, p. 14. Someone with a subscription should quote the exact passage into the plan.
- **Recruiter fees, equipment and onboarding figures**: confirm against quotes, contracts or historical per-hire costs.

### QUESTIONS FOR THE AUTHOR
1. What are the start dates, and does "first year" mean the fiscal year or the first 12 months of employment?
2. What is the $11,000 difference between the line items and the total? Is a line missing?
3. Does the $140,000 ceiling cover all first-year costs, including on-costs and bonuses, or salaries only?
4. Will offers include a signing bonus?

### DECISION-MAKER SUMMARY
Do not send this to finance yet. The total does not add up ($127,900 by the lines vs. $138,900 stated). The ceiling claim holds only because salaries are counted for 6 months without saying so; a full year of salary puts the plan at about $212k, well over the $140k ceiling. Fix the arithmetic, state the budget period and start dates, add the bonus and on-cost lines, and have someone with survey access quote p. 14 before approval.

### OWNER SUMMARY
The cost section has an addition error: its listed costs add up to $11,000 less than the total it reports. It also counts only half a year of salary without explaining why. Counted over a full year, the two hires would cost far more than the approved limit. The salary figure comes from a paid survey nobody has checked yet, and bonuses and employer costs are not included, so the numbers need correcting and confirming before finance sees them.

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
    {"item": "Basis for recruiter, equipment and onboarding costs", "status": "not_seen", "matters": true},
    {"item": "Start dates / definition of first-year period", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Internal budget figures only; no personal data, credentials or client records."},
  "coverage": {
    "checked": [
      {"unit": "plan.md", "kind": "file"},
      {"unit": "plan.md#Market pay", "kind": "section"},
      {"unit": "plan.md#Budget for the two hires", "kind": "section"},
      {"unit": "Total $138,900", "kind": "claim"},
      {"unit": "Total fits inside $140,000 ceiling", "kind": "claim"},
      {"unit": "Salaries prorated 6 months", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "Industry Survey 2026, p. 14", "reason": "paid publication, not supplied"},
      {"unit": "Sources for recruiter, equipment and onboarding figures", "reason": "not supplied"},
      {"unit": "Scope of the $140,000 ceiling", "reason": "approval document not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "plan.md, budget table, Total row ($138,900)",
     "scenario": "Finance re-adds the lines: 84,000 + 19,750 + 11,400 + 12,750 = 127,900, not 138,900. The $11,000 gap means either a typo or a dropped line item, so finance cannot tell what it is approving.",
     "fix": "Correct the total to $127,900, or restore the missing $11,000 line item with a label.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Sum the four cost cells in plan.md; expected 138,900 as stated, observed 127,900."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "C",
     "location": "plan.md, salary line 'for the first year, prorated 6 months' and sentence 'The total fits inside the approved ceiling of $140,000.'",
     "scenario": "The request asks for a first-year budget; finance reads that as 12 months, so salaries are $168,000 and the total is $211,900 (or $222,900 on the stated total), exceeding the $140,000 ceiling. The fit conclusion depends on an unstated 6-month proration.",
     "fix": "State start dates and the budget period; show both the prorated and the full-year cost and test each against the ceiling.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Replace the salary line with 2 x 84,000 = 168,000 and re-add: 168,000 + 19,750 + 11,400 + 12,750 = 211,900 > 140,000."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "plan.md, '70% of firms offer a signing bonus' vs. budget table (no bonus or employer on-cost line)",
     "scenario": "Offers need a signing bonus, or employer payroll taxes and benefits apply; actual first-year spend exceeds the approved figure and needs re-approval.",
     "fix": "Add signing-bonus and employer on-cost lines, or state explicitly that none are offered or that they are budgeted elsewhere.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Search the budget table for a bonus or on-cost line; none is present despite the market-pay section citing signing bonuses."},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "plan.md, Market pay: '$84,000' median",
     "suspicion": "The median salary figure is unverified and drives the whole budget.",
     "unresolved_fact": "Whether Industry Survey 2026 p. 14 states $84,000 as the median salary for senior data engineers in this region."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "plan.md, Market pay: '70% of firms offer a signing bonus'",
     "suspicion": "The signing-bonus prevalence figure is unverified.",
     "unresolved_fact": "Whether Industry Survey 2026 p. 14 states this figure."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "plan.md, recruiter fees $19,750",
     "suspicion": "No basis is given; this is about 11.8% of annual salary, below common contingency rates.",
     "unresolved_fact": "The recruiter agreement's fee terms."},
    {"id": "S4", "status": "needs_validation", "track": "C", "location": "plan.md, equipment $11,400; onboarding $12,750",
     "suspicion": "No basis is given for either figure.",
     "unresolved_fact": "Vendor quotes or historical per-hire actuals."},
    {"id": "S5", "status": "needs_validation", "track": "C", "location": "request.md, 'approved ceiling is $140,000'",
     "suspicion": "The plan treats the ceiling as total first-year cost; its scope is unstated.",
     "unresolved_fact": "Whether the approval covers all first-year costs or salaries only."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The salary line arithmetic is wrong.",
     "evidence": "2 x 84,000 = 168,000; x 6/12 = 84,000, matching the table."},
    {"id": "C2", "candidate": "The plan breaches the ceiling on its own prorated basis.",
     "evidence": "The corrected total of 127,900 and the stated total of 138,900 are both below 140,000."}
  ]
}
```