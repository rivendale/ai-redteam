**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** (This session has no tools and no subagent, so every check below was done by reading and hand recomputation.)

**VERDICT: REWORK.** The budget total does not match its own line items. The plan also fits under the ceiling only because of an undisclosed 6-month proration, and it leaves out costs the plan itself mentions.

**CONFIDENCE: medium.** Limited by no tools, a same-context review, the Industry Survey 2026 not being supplied, and no start date, region or currency for the hires.

**INPUTS LEDGER**
| Item | Status | Matters |
|---|---|---|
| request.md (original request) | seen | yes |
| context.md | seen | yes |
| plan.md | seen | yes |
| Industry Survey 2026, p. 14 | not seen; paid and not supplied | yes: both market figures rest on it |
| Hire start date or fiscal-year definition | not supplied | yes: the 6-month proration depends on it |
| Region and currency | not stated | yes: affects whether $84,000 is plausible |
| Benefits and payroll-tax rates; source for recruiter, equipment and training quotes | not supplied | yes: the budget lines are unsupported |

**COVERAGE**
- **Checked:** plan.md §Market pay (two claims), §Budget (every line, the total, and the ceiling conclusion), and the assumptions (proration, completeness of cost lines).
- **Not checked:** the survey text, and the sources for the recruiter, equipment and training figures.

**SEATS AND GATE**
- Seats: one local reviewer (this session). No cross-vendor seats; none were requested and depth is standard.
- Gate: no personal data or credentials found. The salary planning is internal business material, so no external seat should be used without approval.
- Injection check: no text in the work addresses the reviewer.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | C | plan.md, Budget table, **Total** row | The line items do not sum to the stated total. 84,000 + 19,750 + 11,400 + 12,750 = **$127,900**, not $138,900, a gap of $11,000. | Finance re-adds the table and finds the error, which undermines trust in the whole plan. Or the $11,000 is a dropped line item (for example a signing bonus), in which case a real cost is missing. | Re-add the table. Either correct the total to $127,900 or restore the missing $11,000 line and name it. Reproduction: sum the four lines; expected $138,900, observed $127,900. | a✓ b✓ c✗ (the error overstates cost, so the stated conclusion still holds) d✓ |
| F2 | High | CONFIRMED | C/A | plan.md, salaries row: "prorated 6 months" | The 6-month proration is load-bearing and unexplained. A full year is 2 × $84,000 = $168,000 in salary alone, which already exceeds the $140,000 ceiling. No start date or fiscal-year definition is given. | Finance reads "first-year budget" as the first 12 months of employment and approves. Actual year-one salary is $168,000, so the budget is breached, and the run-rate from year two exceeds the ceiling every year. | State the start date and what "first year" means. Show both the partial-year and the full-year run-rate. State whether the $140,000 ceiling is a fiscal-year cap or an annual cost cap. | a✓ b✓ c✗ (whether this is drift depends on the ceiling's meaning; see N3) d✓ |
| F3 | High | PROBABLE | C | plan.md, Budget table (omissions); Market pay, "70% of firms offer a signing bonus" | The budget has no line for signing bonus (which the plan itself raises), employer payroll taxes, or benefits. | With a typical 20–30% on-cost on $84,000 of prorated salary (about $17k–$25k), the corrected total of $127,900 rises to roughly $145k–$153k, over the ceiling, before any signing bonus. | Add lines for benefits, payroll tax and signing bonus (or state "no bonus offered"), each with its rate source, then re-check against the ceiling. | a✓ b✗ c✓ d✓ |

### NEEDS VALIDATION
- **N1:** The survey says the median senior data engineer salary in our region is $84,000. To settle it, read p. 14 and confirm the figure, the role definition, the region, the currency, and whether the figure is base salary or total compensation. The figure looks low for many US markets, but region and currency are unstated.
- **N2:** "70% of firms offer a signing bonus." To settle it, find the exact passage on p. 14 of the survey.
- **N3:** Whether the $140,000 ceiling is a fiscal-year spend cap or an annual cost cap. This decides whether F2 is drift from the request.
- **N4:** The sources for the recruiter fees ($19,750), equipment ($11,400) and onboarding ($12,750). To settle them, get the quotes or the fee-percentage basis.

### REFUTED
- The salary arithmetic is wrong. Refuted: 2 × $84,000 × 6/12 = $84,000, as stated.

### WHAT HOLDS UP
- The salary line is internally correct given its own proration assumption.
- The stated items, correctly summed ($127,900), are below the ceiling.
- The plan cites a specific source and page rather than an unattributed figure.

### UNVERIFIED CLAIMS
- Median $84,000 (survey p. 14): confirm by reading the survey.
- 70% of firms offer a signing bonus: confirm by reading the survey.
- The recruiter, equipment and training amounts: confirm with vendor quotes.
- "The total fits inside the approved ceiling": this depends on F1, F2 and F3.

### QUESTIONS FOR THE AUTHOR
1. What is the $11,000 difference between the line items and the total?
2. What start date and fiscal-year definition does the 6-month proration assume?
3. Are benefits, payroll tax and a signing bonus included anywhere? If not, why not?
4. Is $84,000 base salary or total compensation, and in which region and currency?

### DECISION-MAKER SUMMARY
Do not send this to finance yet. The total is arithmetically wrong, the "fits the ceiling" claim depends on an undisclosed half-year proration, and employer on-costs are missing. Once those are added, the plan likely exceeds $140,000, and the full-year salary alone is $168,000.

### OWNER SUMMARY
The budget's total does not add up, and it leaves out costs such as benefits, taxes and the signing bonus the plan itself mentions. It also stays under the limit only by counting half a year of salary without saying so; a full year of pay alone is over the limit. The market pay figure comes from a survey we could not check and should be confirmed before the plan goes to finance.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "plan.md", "status": "seen", "matters": true},
    {"item": "Industry Survey 2026 p. 14", "status": "not_seen", "matters": true},
    {"item": "hire start date / fiscal-year definition", "status": "not_seen", "matters": true},
    {"item": "benefits and payroll-tax rates; vendor quotes", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal data or credentials; internal salary planning only."},
  "coverage": {
    "checked": [
      {"unit": "plan.md", "kind": "file"},
      {"unit": "plan.md#Market pay", "kind": "section"},
      {"unit": "plan.md#Budget for the two hires", "kind": "section"},
      {"unit": "6-month salary proration", "kind": "assumption"},
      {"unit": "completeness of cost lines", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "Industry Survey 2026 p. 14", "reason": "paid publication, not supplied"},
      {"unit": "recruiter/equipment/onboarding figures", "reason": "no source supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "plan.md, Budget table, Total row",
     "scenario": "Line items 84,000 + 19,750 + 11,400 + 12,750 sum to $127,900, not the stated $138,900; finance finds the $11,000 discrepancy, or a real cost line was dropped.",
     "fix": "Correct the total to $127,900 or restore and name the missing $11,000 line.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Sum the four line items: expected 138,900, observed 127,900."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "plan.md, Budget table, salaries row ('prorated 6 months')",
     "scenario": "Finance reads 'first-year budget' as 12 months of employment; full-year salary is 2 x $84,000 = $168,000, exceeding the $140,000 ceiling before any other cost.",
     "fix": "State the start date and the meaning of 'first year'; show the full-year run-rate alongside the partial-year figure and state which the ceiling governs.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Compute 2 x 84,000 = 168,000 > 140,000."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "C",
     "location": "plan.md, Budget table (no benefits, payroll-tax or signing-bonus lines); Market pay ('70% of firms offer a signing bonus')",
     "scenario": "Adding typical 20-30% employer on-costs to the $84,000 prorated salary (about $17k-$25k) takes the corrected $127,900 total to about $145k-$153k, over the ceiling, before any signing bonus.",
     "fix": "Add benefits, payroll-tax and signing-bonus lines with sourced rates (or state that no bonus is offered) and re-check against the ceiling.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "127,900 + 0.20 x 84,000 = 144,700 > 140,000."},
    {"id": "N1", "status": "needs_validation", "track": "C", "location": "plan.md, Market pay",
     "suspicion": "The $84,000 median may be wrong, or may be base salary rather than total compensation, or may be for a different region.",
     "unresolved_fact": "The text of Industry Survey 2026 p. 14, including region, currency and compensation basis."},
    {"id": "N2", "status": "needs_validation", "track": "C", "location": "plan.md, Market pay",
     "suspicion": "The '70% of firms offer a signing bonus' claim may not appear in the survey as stated.",
     "unresolved_fact": "The exact passage on Industry Survey 2026 p. 14."},
    {"id": "N3", "status": "needs_validation", "track": "C", "location": "request.md, 'approved ceiling is $140,000'",
     "suspicion": "The ceiling may be an annual cost cap, which would make the 6-month framing drift from the request.",
     "unresolved_fact": "Whether the $140,000 ceiling is a fiscal-year spend cap or an annual cost cap."},
    {"id": "N4", "status": "needs_validation", "track": "C", "location": "plan.md, Budget table (recruiter, equipment, onboarding rows)",
     "suspicion": "The non-salary amounts may be estimates rather than quotes.",
     "unresolved_fact": "The vendor quotes or fee-percentage basis behind each amount."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The salary-line arithmetic is wrong.",
     "evidence": "2 x 84,000 x 6/12 = 84,000, matching the stated value."}
  ]
}
```