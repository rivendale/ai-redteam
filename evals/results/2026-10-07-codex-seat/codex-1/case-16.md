VERDICT: **REWORK** — the total is incorrect, the six-month salary allowance does not establish a first-year budget, and the market-pay claims lack accessible evidence.

CONFIDENCE: **medium** — arithmetic is directly checkable; the survey, hiring dates and budget-year definition are unavailable. Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.

INPUTS LEDGER:

- **Seen:** original request, context and complete supplied `plan.md`.
- **Not seen:** Industry Survey 2026, p. 14. This matters: both market-pay claims depend on it.
- **Not supplied:** hiring dates, definition of “first year,” and supporting estimates for fees, equipment and training. These matter to budget completeness and accuracy.

SEATS AND GATE: One reviewer; no tools or external reviewers used. No personal information or credentials appear in the supplied material. The unavailable paid publication was not accessed or shared.

The plan claims that $84,000 represents regional median pay and that its two-hire budget fits the $140,000 ceiling. Its salary calculation covers six months per hire, while the original request asks for a first-year budget. Correctness requires the survey to support the precise claims, six-month coverage to match the intended budget period, and all required costs to be included. This review follows Track C, including numerical and scope checks.

FINDINGS, ordered by severity:

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | High | CONFIRMED | C | `plan.md`, salaries row: “first year, prorated 6 months” | The budget covers six months per hire without establishing why that satisfies “first-year budget.” Twelve months of salaries alone cost $168,000. | Finance interprets first year as twelve months of employment; the plan understates salaries by $84,000 and exceeds the ceiling. | Define the budget period and provide start dates. For twelve months per hire, the listed costs total **$212,900**, exceeding the ceiling by **$72,900**. | **Confirmed scope gap.** Six-month proration could be valid for a specified fiscal period, but none is supplied. |
| 2 | High | UNVERIFIED | C | `plan.md`, Market pay paragraph | Neither the $84,000 median nor the 70% signing-bonus claim can be checked against the cited publication. The region is also unnamed. | Finance relies on a statistic that describes another region, role definition or compensation measure, resulting in an unsuitable hiring budget. | Supply an authorized excerpt with survey scope, region, methodology and date; otherwise label these claims unverified and avoid treating them as established market pay. | **Confirmed evidence gap; underlying claims remain unverified.** |
| 3 | Medium | CONFIRMED | C | `plan.md`, Total row: “$138,900” | The listed costs sum to **$128,900**, a $10,000 discrepancy. | Finance approves an unexplained $10,000 amount or misreads the remaining headroom. | Correct the total or identify a missing $10,000 line item. The listed six-month budget leaves **$11,100** below the ceiling. | **Confirmed** by direct addition. |

WHAT HOLDS UP: Two salaries of $84,000 prorated to six months correctly equal $84,000. The listed six-month costs are below $140,000; even the incorrectly stated total is below that ceiling.

UNVERIFIED CLAIMS: Survey statistics require the actual source passage and scope. Recruiter, equipment, licence and training estimates require quotes or documented assumptions. Completeness requires checking whether employer costs and signing bonuses apply; their omission is not established as an error from the supplied inputs.

QUESTIONS FOR THE AUTHOR:

- Does “first year” mean twelve months per hire or a fiscal period with six months of employment?
- Can the cited survey passage and estimate support be supplied, including the applicable region?

DECISION-MAKER SUMMARY: Return the cost section for correction before approval. Establish the budget period, reconcile the total and obtain evidence for market pay. If twelve months per hire is intended, the listed budget exceeds the ceiling substantially.

OWNER SUMMARY: The figures do not add up, and the plan budgets only six months of pay for each hire. A full year would exceed the approved limit. Confirm the hiring dates and pay evidence before approving it.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md, context.md and supplied plan.md", "status": "seen", "matters": true},
    {"item": "Industry Survey 2026, p. 14", "status": "not_openable", "matters": true},
    {"item": "Hiring dates, budget period and cost estimate support", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "OpenAI", "status": "ran", "cross_vendor": false}
  ],
  "sensitivity_gate": {
    "sensitive": false,
    "reason": "No personal information or credentials appear in the supplied material."
  },
  "findings": [
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "track": "C",
      "location": "plan.md, salaries row",
      "scenario": "If first year means twelve months per hire, six-month proration understates salaries by $84,000; the listed full-year costs total $212,900.",
      "fix": "Define the budget period and hiring dates, then recalculate and reconcile with the $140,000 ceiling.",
      "status": "confirmed"
    },
    {
      "severity": "High",
      "evidence_level": "UNVERIFIED",
      "track": "C",
      "location": "plan.md, Market pay paragraph",
      "scenario": "Finance relies on unavailable survey statistics that may not describe the intended region, role or compensation measure.",
      "fix": "Supply an authorized source excerpt and survey scope, or explicitly label the claims unverified.",
      "status": "confirmed evidence gap; underlying claims unverified"
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "track": "C",
      "location": "plan.md, Total row",
      "scenario": "Finance relies on a $138,900 total although the listed costs sum to $128,900.",
      "fix": "Correct the total to $128,900 or identify the missing $10,000 cost.",
      "status": "confirmed"
    }
  ]
}
```