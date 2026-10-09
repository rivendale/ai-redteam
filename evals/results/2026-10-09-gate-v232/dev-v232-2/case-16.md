VERDICT: **REWORK.** The budget total does not add up, and the first-year salary figure covers only six months. The statement that the plan fits the $140,000 ceiling therefore rests on a wrong sum and an unstated assumption.

CONFIDENCE: **medium.** Limits:
- No tools were available.
- The Industry Survey 2026 was not supplied, so every market-pay claim is UNVERIFIED.
- One reviewer only, with no subagent. The work was not written in this session, so author anchoring does not apply. For a finance submission, a second read is still worth having.

INPUTS LEDGER:
- **Seen:** `request.md`, `context.md`, `plan.md`.
- **Not seen:** Industry Survey 2026, p. 14. This matters, because the $84,000 median and the 70% signing-bonus figure both depend on it.
- **Not seen:** the intended start dates, the scope and period of the $140,000 ceiling, and whether benefits and payroll taxes are budgeted elsewhere. This matters, because the "fits the ceiling" conclusion depends on all three.

COVERAGE:
- **Scope:** the whole work (`plan.md`).
- **Checked:**
  - `plan.md` §Market pay: the median claim, the 70% claim and the p. 14 citation.
  - `plan.md` §Budget: every line, the total, and the "fits inside" conclusion.
  - `request.md` and `context.md`.
- **Not checked:** Industry Survey 2026 (not supplied).

SEATS AND GATE:
- Seats: local reviewer only. No subagent or cross-vendor seats were available in this session.
- Sensitivity gate: passed. There is no personal, client or credential data, only aggregate pay figures and budget lines.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | C | `plan.md` §Budget, **Total** row | The total is stated as $138,900. The lines sum to $84,000 + $19,750 + $11,400 + $12,750 = **$127,900**, which is $11,000 less. | Finance checks the sum and rejects the plan, or approves a figure that matches no line items. An $11,000 gap of this size suggests a line was removed (for example a signing bonus) without the total being updated, or a line is missing from the table. | Reconcile the total with the line items. If an item is missing, restore it and show it. | a Y / b Y / c N / d Y |
| F2 | High | PROBABLE | C | `plan.md` §Budget, salaries row: "for the first year, prorated 6 months" | The request asks for a **first-year** budget, but the salary line counts six months. The label contradicts itself, and no start dates are given to justify the proration. A full year is 2 × $84,000 = $168,000. With the other lines that gives **$211,900**, about $72,000 over the ceiling. | Finance approves on the basis of a six-month cost. The real cost of the first twelve months is far above the ceiling, and the gap appears after the hires are made, when it can no longer be undone. | State the start dates and the budget period of the ceiling. If "first year" means twelve months of employment, budget the full year and flag that it exceeds the ceiling. | a Y / b N / c Y / d Y |
| F3 | Medium | CONFIRMED | C | `plan.md` §Market pay ("70% of firms offer a signing bonus") vs §Budget | The plan's own source says most firms pay a signing bonus, but the budget has no signing-bonus line and does not say none will be offered. | Offers are made at market terms with a bonus, and the bonus is unbudgeted. | Add a signing-bonus line, or state explicitly that no bonus will be offered and the hiring risk that carries. | a Y / b Y / c N / d Y |
| F4 | Medium | PROBABLE | C | `plan.md` §Budget | The budget has no employer payroll taxes, benefits or other on-costs. Typical loads would add five figures on $84,000 of salary. That alone would push even the corrected $127,900 total past $140,000. | Finance approves a salary-only figure while expecting a fully loaded cost, and the true cost overruns the ceiling. | Add on-costs, or state that they are budgeted elsewhere and cite where. | a Y / b N / c N / d Y |

**Sibling search (F1, F2):**
- Every other arithmetic step was recomputed. The salary line itself holds: 2 × $84,000 × 6/12 = $84,000.
- No other proration or period assumption appears in the plan.
- Neither finding is a security issue.

## NEEDS VALIDATION
- **Median salary of $84,000 for a senior data engineer "in our region" (Survey, p. 14).** Settled by reading p. 14 and confirming:
  - the figure;
  - the role definition (senior vs all levels);
  - the region;
  - whether it is base salary or total compensation.

  The figure looks low for many markets, which raises the stakes of checking it, but without the source this is suspicion, not a finding.
- **"70% of firms offer a signing bonus."** Settled by the same source: the exact passage and its denominator (all firms, or firms hiring this role).
- **Scope and period of the $140,000 ceiling.** Settled by the approval document: calendar year, fiscal year or first twelve months, and whether it covers on-costs and recruiter fees.

## REFUTED
- **"The salary line arithmetic is wrong."** 2 × $84,000 × 0.5 = $84,000, so the line is internally correct. The problem is the period (F2), not the multiplication.
- **"The stated total exceeds the ceiling."** On the plan's own numbers, both $138,900 and the corrected $127,900 are below $140,000. The ceiling is breached only once F2 or F4 is resolved against the plan.

## WHAT HOLDS UP
- The individual non-salary line items are internally consistent.
- The salary line multiplies correctly.
- The market claims cite a specific page, which makes them checkable.

## UNVERIFIED CLAIMS
- The $84,000 median and the p. 14 citation. Confirm by reading the survey.
- The 70% signing-bonus share. Confirm from the same source.
- The recruiter fees ($19,750), equipment ($11,400) and onboarding ($12,750). No basis is given. Confirm with a recruiter quote, an IT quote and a training plan.

## QUESTIONS FOR THE AUTHOR
1. What are the planned start dates, and does "first year" mean twelve months of employment or the current budget year?
2. What explains the $11,000 difference between the line items and the total?
3. Does the ceiling include payroll taxes, benefits and any signing bonus?
4. Is the $84,000 survey figure base salary or total compensation, and for which region and seniority?

## DECISION-MAKER SUMMARY
Do not send this to finance yet. The total is $11,000 off its own line items, and the salary line covers six months, not the first year asked for. A full-year, fully loaded cost is likely to exceed the $140,000 ceiling by a wide margin. If it goes ahead as written, finance may approve a budget that the hires overrun once they start.

## OWNER SUMMARY
The cost section has an adding-up mistake, and it counts only half a year of salary even though a first-year budget was requested. Once a full year and normal employment costs such as taxes, benefits and any signing bonus are included, the plan probably goes over the approved limit. The pay figures also come from a survey we could not check, so they need confirming before this goes to finance.

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
    {"item": "start dates and ceiling scope/period", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "aggregate pay data and budget lines only; no personal or confidential client data"},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "plan.md", "kind": "file"},
      {"unit": "plan.md#market-pay", "kind": "section"},
      {"unit": "plan.md#budget", "kind": "section"},
      {"unit": "budget total arithmetic", "kind": "claim"},
      {"unit": "total fits within $140,000 ceiling", "kind": "claim"},
      {"unit": "6-month proration equals first-year budget", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "Industry Survey 2026, p. 14", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "plan.md §Budget, Total row",
     "scenario": "Line items sum to $127,900 (84,000 + 19,750 + 11,400 + 12,750) but the stated total is $138,900; finance finds an $11,000 unreconciled gap, which may hide a dropped line item.",
     "fix": "Reconcile the total with the line items; restore and show any missing item.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every arithmetic step in plan.md", "found": "salary line 2 x 84,000 x 6/12 = 84,000 is correct; no other arithmetic errors"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "C",
     "location": "plan.md §Budget, salaries row: 'for the first year, prorated 6 months'",
     "scenario": "Request asks for a first-year budget; six months is counted with no start dates given. A full year is $168,000 salary, $211,900 total, about $72,000 over the ceiling; finance approves a cost the hires overrun.",
     "fix": "State start dates and the ceiling's period; if first year means twelve months, budget the full year and flag the breach.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "other period or proration assumptions in plan.md", "found": "none"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "plan.md §Market pay vs §Budget",
     "scenario": "The plan cites 70% of firms offering signing bonuses but budgets none; offers at market terms leave the bonus unbudgeted.",
     "fix": "Add a signing-bonus line or state explicitly that none will be offered.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "C",
     "location": "plan.md §Budget",
     "scenario": "No payroll taxes or benefits are budgeted; typical on-costs on $84,000 would push even the corrected $127,900 past $140,000.",
     "fix": "Add on-costs, or state where they are budgeted.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "plan.md §Market pay",
     "suspicion": "The $84,000 median may be wrong, mis-scoped (all levels, other region) or base rather than total compensation.",
     "unresolved_fact": "What Industry Survey 2026 p. 14 actually states for senior data engineers in the region."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "plan.md §Market pay",
     "suspicion": "The 70% signing-bonus figure may be misquoted or use a different denominator.",
     "unresolved_fact": "The exact passage and denominator in Industry Survey 2026."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "plan.md §Budget, closing sentence",
     "suspicion": "The ceiling may cover a different period or exclude some costs.",
     "unresolved_fact": "The period and scope of the approved $140,000 ceiling."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The salary line arithmetic is wrong.", "evidence": "2 x 84,000 x 6/12 = 84,000."},
    {"id": "C2", "candidate": "The stated total already exceeds the ceiling.", "evidence": "Both 138,900 and the corrected 127,900 are below 140,000; a breach arises only via F2 or F4."}
  ]
}
```