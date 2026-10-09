VERDICT: REWORK. The budget total is arithmetically wrong, the "first-year" salary line covers only six months without saying why, and the "fits inside the ceiling" conclusion rests on both.

CONFIDENCE: medium. The arithmetic and internal consistency were fully checkable by hand. The market-pay figures could not be checked because the Industry Survey 2026 was not supplied. There were no tools and a single reviewer, and the work was not authored in this session, so there is no author-anchoring risk.

INPUTS LEDGER:
- **Seen:** the original request (request.md), the context (context.md) and the work (plan.md).
- **Not seen:** the Industry Survey 2026, p. 14. This matters: both market-pay claims depend on it.
- **Not seen:** the basis for the recruiter, equipment and onboarding figures. This matters, because three of the four line items are unsourced.
- **Not seen:** the definition of the $140,000 ceiling, and the planned start date. This matters, because the proration and the fit conclusion depend on them.

COVERAGE:
- **Checked:**
  - plan.md "Market pay": both claims.
  - plan.md "Budget for the two hires": every row and the total.
  - The fit-to-ceiling conclusion.
- **Not checked:** the survey text, and the sources for the cost lines (not supplied).

SEATS AND GATE: one local reviewer ran. No subagent or cross-vendor seats were available. The sensitivity gate passed: there is no personal data, only aggregate pay figures.

FINDINGS:

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | plan.md, budget table, **Total** row | The line items sum to $127,900, not $138,900. The $11,000 gap means either the sum is wrong or a line item was dropped from the table. | Finance approves or rejects against a figure that does not reproduce from its own rows. They cannot tell whether the real request is $127,900 or whether a missing $11,000 item (for example a signing bonus) exists. | Recompute: 84,000 + 19,750 + 11,400 + 12,750 = 127,900. Either correct the total or restore the missing row and name it. | y/y/y/y |
| F2 | High | CONFIRMED | C | plan.md, salaries row: "2 x $84,000, for the first year, prorated 6 months" | The row calls itself a first-year cost but budgets only 6 months (half of 2 × $84,000 = $168,000). No start date or fiscal-year basis is given. A full first year of salary alone is $168,000, which exceeds the $140,000 ceiling. | Finance reads "first-year budget" as the first 12 months of employment. The real salary cost is then $84,000 higher than shown, and the plan breaches the ceiling. | State the start date and the period the ceiling covers (fiscal year or 12 months of employment). Show the full-year figure next to the prorated one. | y/y/n/y |
| F3 | High | CONFIRMED | C | plan.md, budget table (absent rows) | There is no line for employer on-costs (payroll taxes, benefits, pension), and no statement that they are excluded or budgeted elsewhere. | Finance treats $138,900 as fully loaded. Actual first-year cost then exceeds the ceiling once on-costs are added. Even on the corrected $127,900 total, the headroom is only $12,100. | Add an on-costs line at the company's loaded rate, or state explicitly where on-costs are budgeted. | y/y/n/y |
| F4 | Medium | CONFIRMED | C | plan.md, "Market pay" vs. budget table | The plan cites signing bonuses as market practice (70% of firms) but budgets none and does not say the firm will not offer one. | If offers need a signing bonus to compete, the cost appears after approval and outside the budget. | Add a signing-bonus line, or a sentence that none will be offered and why. | y/y/n/n |

NEEDS VALIDATION (no severity):
- **S1, the $84,000 median.** It is unconfirmed that Industry Survey 2026 p. 14 reports a median of $84,000 for senior data engineers in "our region". It is also unconfirmed whether the figure is base salary or total compensation, and how the survey defines the region. The page itself would settle this. Every salary figure depends on it.
- **S2, the 70% signing-bonus figure.** It is unconfirmed whether the 70% statistic is on the same page, refers to the same role and region, and says "offer" rather than "paid". The page would settle this.
- **S3, recruiter fees ($19,750), equipment ($11,400) and onboarding ($12,750).** No basis is given for these figures. A quote, a contract fee percentage or a past invoice would settle each one.
- **S4, the ceiling.** It is unclear whether the $140,000 ceiling covers both hires and which period it covers. The approval document would settle this.

REFUTED:
- **R1: "the stated items exceed the ceiling."** Refuted as stated. The rows actually sum to $127,900, which is under $140,000. This holds only under the unstated six-month proration (F2) and with on-costs excluded (F3).

WHAT HOLDS UP:
- The proration arithmetic itself is correct: 2 × $84,000 × 6/12 = $84,000.
- Each individual line amount is internally consistent.
- The survey is named with a page number, so the claims are checkable once the publication is obtained.

UNVERIFIED CLAIMS:
- **The $84,000 median salary.** Confirm it against Survey p. 14.
- **"70% of firms offer a signing bonus."** Confirm it against the same page.
- **The three non-salary cost lines.** Each needs its source.
- **"The total fits inside the approved ceiling."** This claim is unsupported until F1–F3 and S4 are resolved.

QUESTIONS FOR THE AUTHOR:
1. Was a row dropped from the table, given the $11,000 gap? If so, what is it?
2. What is the start date, and does the ceiling cover a fiscal year or the first 12 months of employment?
3. Are on-costs and any signing bonus budgeted elsewhere?
4. Can you supply the text of Survey p. 14?

DECISION-MAKER SUMMARY: Do not send this to finance yet. The total does not add up (F1), and the "first-year" salary covers only six months (F2). On a full-year or fully loaded basis, the plan likely exceeds the $140,000 ceiling (F2, F3). If it goes ahead as is, finance approves a number that is either wrong or incomplete, and the real cost surfaces after the hires are made.

OWNER SUMMARY: The cost section has an addition error, and it counts only half a year of salary while calling it a first-year budget. It also leaves out taxes, benefits and any signing bonus. Once those are fixed, the hires may not fit within the approved amount, so the section needs correcting and its pay figures checked against the survey before finance sees it.

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
    {"item": "Sources for recruiter, equipment and onboarding costs", "status": "not_seen", "matters": true},
    {"item": "Ceiling definition and planned start date", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Aggregate market pay figures only; no personal or confidential records."},
  "coverage": {
    "checked": [
      {"unit": "plan.md", "kind": "file"},
      {"unit": "plan.md#Market pay", "kind": "section"},
      {"unit": "plan.md#Budget for the two hires", "kind": "section"},
      {"unit": "Budget total = $138,900", "kind": "claim"},
      {"unit": "Total fits inside $140,000 ceiling", "kind": "claim"},
      {"unit": "Six-month salary proration", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "Industry Survey 2026, p. 14", "reason": "paid publication not supplied"},
      {"unit": "Basis of recruiter, equipment, onboarding figures", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "plan.md, budget table, Total row",
     "scenario": "Line items sum to $127,900 but the total says $138,900; finance decides on a figure that does not reproduce, and an $11,000 item may be missing from the table.",
     "fix": "Recompute the total or restore and name the missing $11,000 row.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "84,000 + 19,750 + 11,400 + 12,750 = 127,900; expected 138,900 as stated, observed 127,900."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "plan.md, salaries row",
     "scenario": "A row labelled first-year budgets 6 months; if finance reads first-year as 12 months of employment, salary is $168,000 and alone exceeds the $140,000 ceiling.",
     "fix": "State the start date and the period the ceiling covers; show full-year salary alongside the prorated figure.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "2 x 84,000 = 168,000 for 12 months; 168,000 > 140,000."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "plan.md, budget table (no on-costs row)",
     "scenario": "Finance treats the total as fully loaded; payroll taxes and benefits push first-year cost past the ceiling, with only $12,100 headroom on the corrected total.",
     "fix": "Add an employer on-costs line at the company loaded rate, or state where on-costs are budgeted.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "plan.md, Market pay vs budget table",
     "scenario": "The plan cites signing bonuses as common but budgets none; if offers need one, the cost lands outside the approved budget.",
     "fix": "Add a signing-bonus line or state that none will be offered.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "plan.md, Market pay",
     "suspicion": "The $84,000 median may not match the survey, or may be total compensation or a different region.",
     "unresolved_fact": "The text of Industry Survey 2026 p. 14 for senior data engineers in the stated region."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "plan.md, Market pay",
     "suspicion": "The 70% signing-bonus statistic may not apply to this role and region.",
     "unresolved_fact": "Whether p. 14 states 70% for the same role and region."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "plan.md, recruiter, equipment, onboarding rows",
     "suspicion": "Three of four cost lines have no stated basis.",
     "unresolved_fact": "A quote, fee percentage or past invoice for each figure."},
    {"id": "S4", "status": "needs_validation", "track": "C", "location": "plan.md, final sentence",
     "suspicion": "The ceiling's scope and period are undefined.",
     "unresolved_fact": "Whether the approved $140,000 covers both hires and over what period."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The stated line items exceed the $140,000 ceiling.",
     "evidence": "The rows sum to $127,900, below the ceiling, but only under the six-month proration and with on-costs excluded."}
  ]
}
```