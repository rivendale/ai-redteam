VERDICT: **REWORK**. The stated total is an addition error, and the "fits inside the ceiling" conclusion depends on an unexplained 6-month salary proration. A 12-month first year comes to about $211,900, well over the $140,000 ceiling.

CONFIDENCE: **medium**. The arithmetic and the internal wording were checked directly. The Industry Survey 2026 was not supplied, so the market-pay claims could not be checked. No tools and no subagent were available, so one reviewer did the whole review. I did not write the work.

INPUTS LEDGER:
- **Seen:** request.md, context.md, plan.md.
- **Not seen:**
  - Industry Survey 2026, p. 14. This matters: both market-pay claims depend on it.
  - The source or quotes behind recruiter fees, equipment and onboarding. This matters: the line items have no stated basis.
  - The intended start date or fiscal-year definition. This matters: it decides whether the proration is legitimate.

COVERAGE: scope is the whole work (plan.md).
- **Checked:**
  - Market-pay claims (median $84,000; 70% signing bonus).
  - Every budget line.
  - The salary arithmetic.
  - The total.
  - The ceiling statement.
- **Not checked:**
  - The survey contents (not supplied).
  - Vendor or recruiter quotes (not supplied).

SEATS AND GATE: one reviewer, in this session. No subagent or cross-vendor seats were available because this session has no tools. Sensitivity gate: no personal or confidential data found. The plan is internal and finance-bound, but it holds aggregate figures only.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | C | plan.md, budget table, **Total** row | The lines sum to **$127,900** (84,000 + 19,750 + 11,400 + 12,750), not the stated $138,900. The total is $11,000 too high. | Finance approves or adjusts against a total that does not reproduce from its own lines. The headroom shows as $1,100 when the lines give $12,100. Either a line item is missing from the table, or the total is wrong. | Recompute the total. If a line was dropped (an $11,000 gap), restore it with its basis. | a Y, b Y, c N, d Y |
| F2 | High | PROBABLE | C/A | plan.md, salaries row: "for the first year, prorated 6 months" | The label contradicts itself: a "first-year" budget shows only 6 months of salary, and no start date or fiscal-year basis is given. Over 12 months, salaries are 2 × $84,000 = $168,000, and the total is $211,900. | Finance reads this as "the two hires cost under $140,000 in their first year" and approves. The real first-year cost of employment is about $71,900 over the ceiling, which surfaces in the next budget cycle. | State the start date and the period the ceiling covers. Show the 12-month cost next to the in-year cost, and test both against the ceiling. | a Y, b N, c Y, d Y |
| F3 | Medium | CONFIRMED | C | plan.md, "Market pay" vs the budget table | The plan cites "70% of firms offer a signing bonus" but budgets no signing bonus. | A competitive offer needs a bonus, and that cost is unbudgeted. | Add a signing-bonus line, or state explicitly that none will be offered. | a Y, b Y, c N, d N |
| F4 | Medium | PROBABLE | C | plan.md, budget table | No employer on-costs appear: payroll taxes, benefits, pension or retirement contributions. These commonly add a material percentage on top of base salary. | The true cost exceeds the budget by the on-cost rate, even on the 6-month basis. | Add an on-costs line using the company's actual loaded-cost rate. | a Y, b N, c N, d Y |

**Sibling search:**
- For F1, I recomputed every other figure. The salary line holds: 2 × 84,000 × 6/12 = 84,000. The headroom statement inherits the F1 error.
- For F2, I checked whether the other lines use a period basis. Recruiter, equipment and onboarding read as one-off costs, so no other proration was found.
- Neither F1 nor F2 is a security finding.

## Needs validation
- **Median $84,000 (Survey p. 14):** confirm that the page states this figure, for this role and this region, and that it is base salary rather than total compensation. The survey was not supplied.
- **"70% of firms offer a signing bonus":** confirm the passage and its denominator (all firms surveyed, or only firms hiring senior data engineers).
- **Recruiter fees of $19,750, equipment of $11,400, onboarding of $12,750:** these need a stated basis, such as a quote, contract or fee rate. For example, a percentage-of-salary recruiter fee would normally scale with the full annual salary, not the prorated one.
- **Budgeting at the median:** confirm the median is a realistic offer level. Half the market pays more, so a median offer may not attract senior hires.

## Refuted
- **"The salary line arithmetic is wrong."** Refuted: 2 × $84,000 × 0.5 = $84,000 is correct for the 6-month basis it states.

## What holds up
- The ceiling of $140,000 matches the request.
- The salary multiplication is correct on its own basis.
- The survey is cited with a page number, which makes it checkable.

## Unverified claims
- Both survey figures. To confirm, read p. 14 of the Industry Survey 2026.
- All three non-salary line items. To confirm, attach the quotes or rates they came from.

## Questions for the author
1. Where does $138,900 come from? Is a line missing from the table?
2. What start date and budget period justify the 6-month proration, and does the $140,000 ceiling cover a fiscal year or the first 12 months of employment?
3. Is $84,000 base salary, and are on-costs and a signing bonus intended?

## Decision-maker summary
Do not send this to finance as written. The total does not add up, and the "fits the ceiling" claim holds only if the hires start halfway through the budget year. Over a full 12 months the cost is about $212,000 before on-costs. If it goes as is, finance may approve a commitment that exceeds the ceiling from the next period onward.

## Owner summary
The budget total in this plan is added up wrong. It also counts only half a year of salary while calling itself a first-year budget, and over a full year the two hires would cost well above the approved limit. The plan also leaves out a signing bonus it says most firms offer, as well as employer payroll costs, and its market salary figure comes from a survey that was not available to check.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "plan.md", "status": "seen", "matters": true},
    {"item": "Industry Survey 2026, p. 14", "status": "not_seen", "matters": true},
    {"item": "basis for recruiter, equipment and onboarding figures", "status": "not_seen", "matters": true},
    {"item": "start date / budget period definition", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Aggregate cost figures only; no personal or credential data."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "plan.md", "kind": "file"},
      {"unit": "plan.md: median salary $84,000 claim", "kind": "claim"},
      {"unit": "plan.md: 70% signing bonus claim", "kind": "claim"},
      {"unit": "plan.md: budget table arithmetic", "kind": "data"},
      {"unit": "plan.md: fits-ceiling conclusion", "kind": "claim"},
      {"unit": "6-month proration", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "Industry Survey 2026", "reason": "not_supplied"},
      {"unit": "line-item quotes and rates", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "plan.md, budget table, Total row",
     "scenario": "The lines sum to $127,900 (84,000 + 19,750 + 11,400 + 12,750), not the stated $138,900. Finance approves against a total that does not reproduce from its lines, with headroom misstated as $1,100 instead of $12,100, or with a missing $11,000 line left unexplained.",
     "fix": "Recompute the total to $127,900, or restore the missing $11,000 line with its basis.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every computed figure in plan.md (salary line, total, headroom statement)", "found": "salary line correct; headroom statement inherits the error"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "C",
     "location": "plan.md, salaries row: 'for the first year, prorated 6 months'",
     "scenario": "A first-year budget counts only 6 months of salary with no stated start date or budget period. Over 12 months salaries are $168,000 and the total is $211,900, $71,900 over the $140,000 ceiling; finance approves believing the hires fit.",
     "fix": "State the start date and the period the ceiling covers; show the 12-month cost alongside the in-year cost and test both against the ceiling.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "other budget lines for a period or proration basis", "found": "recruiter, equipment and onboarding read as one-off costs; no other proration"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "plan.md, Market pay section vs budget table",
     "scenario": "The plan cites that 70% of firms offer a signing bonus but budgets none; a competitive offer requiring one creates an unbudgeted cost.",
     "fix": "Add a signing-bonus line or state explicitly that none will be offered.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "C",
     "location": "plan.md, budget table",
     "scenario": "No employer on-costs (payroll taxes, benefits, retirement contributions) are budgeted, so the true cost exceeds the budget by the loaded-cost rate.",
     "fix": "Add an on-costs line using the company's actual loaded-cost rate.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "plan.md, Market pay: median $84,000",
     "suspicion": "The median figure may not be on p. 14, may cover a different role or region, or may be total compensation rather than base salary.",
     "unresolved_fact": "The text of Industry Survey 2026 p. 14 (not supplied)."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "plan.md, Market pay: 70% signing bonus",
     "suspicion": "The figure and its denominator are unverified.",
     "unresolved_fact": "The survey passage and the population it describes."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "plan.md, recruiter/equipment/onboarding rows",
     "suspicion": "The figures have no stated basis; a percentage-of-salary recruiter fee would normally scale with full annual salary.",
     "unresolved_fact": "The quotes, contracts or rates behind $19,750, $11,400 and $12,750."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The salary line arithmetic is wrong.", "evidence": "2 x 84,000 x 0.5 = 84,000, which matches the table on its stated 6-month basis."}
  ]
}
```