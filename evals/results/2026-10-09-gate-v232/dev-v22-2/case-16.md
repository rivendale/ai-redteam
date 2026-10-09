**Single reviewer, no tools.** The plan was supplied as input and was not written in this conversation, so anchoring risk is low. Nothing could be run or opened; all checks are by hand.

**VERDICT: REWORK.** The budget total does not add up from its own line items ($127,900, not $138,900). The claim that it fits under the ceiling rests on an unstated six-month proration and leaves out employer on-costs.

**CONFIDENCE: medium.** The arithmetic is certain. The salary figure depends on a paid survey that was not supplied. The start date and recruiter terms are unknown.

**INPUTS LEDGER**
- Seen: request.md, context.md, plan.md.
- Not seen: Industry Survey 2026 (p. 14). This matters because every salary figure and the bonus claim depend on it.
- Not seen: planned start date or fiscal-year definition. This matters because the proration depends on it.
- Not seen: recruiter contract terms. This matters for the fee line.

**COVERAGE**
- Checked: plan.md "Market pay" (two claims); every line and the total of the budget table; the ceiling comparison; the proration assumption; what the budget leaves out.
- Not checked: the survey's content, because it was not supplied.

**SEATS AND GATE:** Local reviewer only. The work holds no personal or confidential data, so the gate passed. No cross-vendor seats were requested.

### Reconstruct
The plan says the market median for a senior data engineer is $84,000. It budgets two hires at six months' prorated salary plus recruiter, equipment and onboarding costs, and concludes the total ($138,900) fits under $140,000.

For that to be correct, four things must hold:
- the survey says what is quoted;
- "first year" means a period in which the hires work only six months;
- the line items are complete;
- the sum is right.

Track: C, as requested. Arithmetic and completeness are treated as factual claims.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | plan.md budget table, **Total** row | The total does not reproduce from the lines: 84,000 + 19,750 + 11,400 + 12,750 = **127,900**, not 138,900. That is an $11,000 gap. | Finance approves or audits against a total that matches none of the listed items. Either a cost row (about $11,000) was dropped, or the sum is wrong. Either way the figure sent for approval is wrong. | Re-add the lines. If an $11,000 item is missing, restore its row. Reproduction: sum the four rows, expect 138,900, observe 127,900. | Y/Y/Y/Y |
| F2 | High | CONFIRMED | C | plan.md row "2 x $84,000, for the first year, prorated 6 months" | The request asks for a **first-year budget**. The plan silently prorates to six months, and no start date or fiscal-year basis is given. Full-year salaries are $168,000, which alone exceeds the $140,000 ceiling. | Finance reads "first-year budget, fits the ceiling" as covering a year of employment. Over the hires' first 12 months, salaries alone cost $168,000, and $211,900 with the other lines. | State the start date and budget period explicitly. Also show the 12-month cost. If the ceiling is meant to cover a year of employment, the plan does not fit. | Y/Y/Y/Y |
| F3 | High | PROBABLE | C | plan.md budget table (no row for on-costs) | The budget lists base salary only. It has no employer payroll taxes, benefits or pension contributions. These are typically about 20–30% of salary; the exact rate depends on the jurisdiction and is not given. | Even on the prorated basis, a 20% load adds about $16,800. Corrected total ≈ $144,700, which is over the ceiling. | Add an on-cost row using the company's actual load rate, then re-test the total against the ceiling. | Y/N/Y/Y |
| F4 | Medium | CONFIRMED | C | plan.md "70% of firms offer a signing bonus" vs budget table | The plan cites signing bonuses as market practice, but the budget has no signing-bonus line. | A competitive offer needs a bonus, and the cost lands outside the approved budget. | Add a bonus line, or state that offers will not include one and accept the hiring risk. | Y/Y/N/Y |

### NEEDS VALIDATION
- **S1** (Market pay): "median salary … $84,000" (Survey p. 14). To settle it: does p. 14 give $84,000 as the **median** for **senior** data engineers in **this region**, rather than a mean, an all-levels figure or a national figure? The survey was not supplied.
- **S2** (Market pay): "70% of firms offer a signing bonus". To settle it: does the survey state this, and for which population?
- **S3** (Recruiter fees, $19,750): this equals about 23.5% of the *prorated* $84,000, or about 11.8% of the $168,000 annual base. Agency fees are usually charged on annual base salary. To settle it: the recruiter contract's fee basis. If the fee is charged on annual base, the line is understated by roughly $20,000.
- **S4** (Strategy): budgeting senior hires at the *median* may not win candidates. To settle it: the target percentile the hiring team intends to offer.

### REFUTED
- **R1**: "2 × $84,000 prorated 6 months = $84,000 is a miscalculation." Withdrawn: 168,000 × 6/12 = 84,000. The arithmetic is correct; the problem is the unstated basis, covered by F2.

### WHAT HOLDS UP
- The salary proration arithmetic is internally correct.
- The equipment and onboarding lines are plausibly sized. They could not be verified, but nothing contradicts them.
- The plan cites a specific source and page rather than an unattributed figure.

### UNVERIFIED CLAIMS
- Median of $84,000 (S1) and the 70% bonus figure (S2). To confirm: obtain the Survey p. 14 and quote the passage.
- "Fits inside the ceiling." This is false as stated (F1) and doubtful once on-costs are included (F3).

### QUESTIONS FOR THE AUTHOR
1. Is there a missing $11,000 line, or is the total simply mis-summed?
2. What start date and budget period justify six months of salary?
3. What is the employer on-cost rate, and what is the recruiter fee basis?

### DECISION-MAKER SUMMARY
Do not send this to finance yet. The total is wrong by $11,000, and the ceiling fit depends on an unstated six-month proration and omitted employer on-costs. A corrected budget likely exceeds $140,000 on a six-month basis and far exceeds it on a full year.

### OWNER SUMMARY
The budget's total does not match its own line items, so it needs to be re-added before it goes for approval. It also counts only half a year of pay and leaves out employer costs like taxes and benefits. Once those are included, the plan probably goes over the approved limit. The salary figure comes from a paid survey nobody here could check, so someone with a copy should confirm it.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "Industry Survey 2026 p. 14", "status": "not_seen", "matters": true},
    {"item": "planned start date / budget period", "status": "not_seen", "matters": true},
    {"item": "recruiter contract terms", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal, client or credential data; market pay figures only."},
  "coverage": {
    "checked": [
      {"unit": "plan.md", "kind": "file"},
      {"unit": "plan.md#Market pay", "kind": "section"},
      {"unit": "plan.md#Budget for the two hires", "kind": "section"},
      {"unit": "Total = $138,900", "kind": "claim"},
      {"unit": "6-month proration", "kind": "assumption"}
    ],
    "not_checked": [{"unit": "Industry Survey 2026", "reason": "paid publication, not supplied"}]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "plan.md budget table, Total row",
     "scenario": "Line items sum to $127,900 but the total states $138,900; finance approves a figure that matches no itemization.",
     "fix": "Re-add the lines and restore any dropped $11,000 row.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "84,000 + 19,750 + 11,400 + 12,750 = 127,900; expected 138,900."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "plan.md row 'salaries (2 x $84,000, for the first year, prorated 6 months)'",
     "scenario": "Request asks for a first-year budget; a full year of salaries is $168,000, over the $140,000 ceiling, but the plan silently prorates to 6 months.",
     "fix": "State start date and budget period; show the 12-month cost alongside.",
     "answers": {"a": true, "b": true, "c": true, "d": true}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "C",
     "location": "plan.md budget table (no on-cost row)",
     "scenario": "Employer taxes and benefits omitted; at a 20% load the prorated total is about $144,700, over the ceiling.",
     "fix": "Add an on-cost row at the company's actual load rate and re-test against the ceiling.",
     "answers": {"a": true, "b": false, "c": true, "d": true}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "plan.md 'Market pay' vs budget table",
     "scenario": "Plan cites signing bonuses as market practice but budgets none; a needed bonus lands outside the approved budget.",
     "fix": "Add a signing-bonus line or state that none will be offered.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "plan.md 'Market pay'",
     "suspicion": "The $84,000 median may not be the regional senior-level median.",
     "unresolved_fact": "What Survey p. 14 actually states (not supplied)."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "plan.md 'Market pay'",
     "suspicion": "The 70% signing-bonus figure is unsourced beyond the survey.",
     "unresolved_fact": "Whether the survey states it, and for which population."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "plan.md row 'recruiter fees'",
     "suspicion": "Fee appears computed on prorated rather than annual salary; may be understated by about $20,000.",
     "unresolved_fact": "Recruiter contract fee basis."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Prorated salary arithmetic is wrong.",
     "evidence": "2 x 84,000 x 6/12 = 84,000; arithmetic correct, basis issue covered by F2."}
  ]
}
```