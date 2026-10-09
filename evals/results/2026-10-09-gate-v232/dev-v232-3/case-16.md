VERDICT: **REWORK.** The budget total does not match its own line items. The "first year" salary line covers only six months with no stated reason. Employer costs are missing, so the claim that the total "fits inside the ceiling" cannot be relied on.

CONFIDENCE: **medium.** The arithmetic findings are certain, since I recomputed them from the work. Three things limit the rest:
- The Industry Survey 2026 was not supplied, so every market-pay figure is UNVERIFIED.
- No tools were available, so nothing was fetched or run.
- The start date and what the ceiling covers are unknown.

I was not the author, so this is not a same-context review, but no second reviewer ran.

INPUTS LEDGER:
- Seen: `request.md` (original request), `context.md`, `plan.md` (work under review).
- Not seen: *Industry Survey 2026*, p. 14. It is paid and was not supplied. **This matters:** the $84,000 median and the 70% signing-bonus figure rest entirely on it.
- Not seen: the planned start date for the hires, and the definition of the $140,000 ceiling (salary only or fully loaded; calendar or fiscal year). **This matters** for F2 and F3.
- Not seen: the recruiter agreement (fee basis). It matters only for S3.

COVERAGE:
- Scope: the whole of `plan.md`.
- Checked:
  - `request.md`, `context.md`, `plan.md`.
  - The "Market pay" section: the median salary claim and the signing-bonus claim.
  - Every row of the budget table and its total.
  - The ceiling conclusion.
  - The proration assumption.
  - Completeness of cost categories against "first-year budget".
- Not checked: the survey itself (not supplied); the recruiter contract (not supplied).

The context asked for a Track C (claims) review. F1 is Track C. F2 to F4 are Track A gaps found in the same document, and I report them because they decide whether the ceiling claim holds.

SEATS AND GATE: one local reviewer (this session), with no tools and no subagent. A hiring budget with salary figures is confidential business material, so cross-vendor seats were refused. None were requested anyway.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | C | plan.md, budget table, **Total** row | The line items sum to **$127,900**, not $138,900. The stated total is off by $11,000. | Finance checks the arithmetic and rejects the plan, or approves a figure that matches no itemisation. If an $11,000 line was dropped instead, a real cost is missing from the plan. | Recompute: 84,000 + 19,750 + 11,400 + 12,750 = 127,900. Either correct the total, or restore the missing $11,000 line and name it. | a Y / b Y / c N / d Y |
| F2 | High | PROBABLE | A | plan.md, salaries row: "for the first year, prorated 6 months" | The request asks for a **first-year** budget. The row says "first year" but costs only six months of salary. No start date or fiscal-year reason is given. | "First year" probably means the first 12 months of employment. If so, salaries are 2 × 84,000 = $168,000, and the corrected total is at least $211,900 (from the true sum of $127,900). That is about $72,000 over the $140,000 ceiling. Finance would approve a budget that cannot hold. | State the start date and the period the ceiling covers. If the ceiling is for 12 months of employment, budget $168,000 for salaries and re-test the ceiling. | a Y / b N / c Y / d Y |
| F3 | High | PROBABLE | A | plan.md, budget table (no rows for employer costs) | There are no employer payroll taxes, benefits or other on-costs. A first-year hiring budget normally includes them. | The ceiling claim depends on what is left over: $1,100 against the stated total, or $12,100 against the true sum. US employer FICA alone is about 7.65%, roughly $6,400 on $84,000 of salary. Typical benefits load is 20–30%, about $17,000–25,000. The real cost likely exceeds $140,000 even with six months' proration. | Add a fully loaded cost line using the company's actual on-cost rate, or state explicitly that the ceiling is salary-and-fees only. | a Y / b N / c Y / d Y |
| F4 | Medium | CONFIRMED | A | plan.md, "Market pay" ("70% of firms offer a signing bonus") vs the budget table | The plan cites signing bonuses as market norm, then budgets nothing for them. | The firm has to match a market signing bonus to land a senior candidate, and the unbudgeted cost breaks the ceiling or stalls the hire. | Add a signing-bonus line, or state the policy that none will be offered and accept the hiring risk. | a Y / b Y / c N / d N |

**Confirm or refute (Highs):**
- **F1, defended as "the total includes something not shown":** the table presents itself as complete and the total row is bolded as the sum. The total is still wrong. Held.
- **F2, defended as "this is a fiscal-year budget with a mid-year start":** this is plausible, but the plan says neither. The row's own words, "for the first year", contradict six months. Held as PROBABLE.
- **F3, defended as "the ceiling may cover salary and fees only":** possible, but unstated. Held as PROBABLE. The question for the author would settle it.

**Siblings searched:** I re-derived every number in the plan:
- 2 × 84,000 × 6/12 = 84,000 is correct.
- The implied headroom of 140,000 − 138,900 = 1,100 is consistent with the wrong total.

No other arithmetic error was found. Other prorated-basis risk: see S3. Other omitted categories: the signing bonus (F4). No other categories were identified beyond on-costs.

None of these are security findings.

## NEEDS VALIDATION
- **S1:** "the median salary for a senior data engineer in our region is $84,000" (Survey p. 14). To settle it, read p. 14 and confirm four things: the role, the seniority level, the region, and that the figure is the median annual base salary, not a percentile, a total-comp component or another currency. $84,000 is also low against commonly reported US senior data engineer pay, which raises the risk of a misread.
- **S2:** "70% of firms offer a signing bonus." To settle it, find the exact passage on p. 14 and its denominator (all firms, or firms hiring at this level).
- **S3:** recruiter fees of $19,750. That is 11.8% of $168,000 annual salary, or 23.5% of the prorated $84,000. Recruiter fees are usually charged on annual base, so this may be under-budgeted. To settle it, check the recruiter agreement's percentage and base.

## REFUTED
- **Candidate: "2 × $84,000 prorated is mis-computed."** Refuted: 168,000 × 0.5 = 84,000 is correct. The problem is the proration assumption (F2), not the arithmetic.

## WHAT HOLDS UP
- The salary row's arithmetic is internally consistent.
- The equipment and onboarding figures are plausible and not contradicted by anything supplied.
- The structure answers both parts of the request (market pay, then budget).

## UNVERIFIED CLAIMS
- The $84,000 median and the 70% signing-bonus figure, both attributed to *Industry Survey 2026* p. 14. To confirm, obtain the survey and quote p. 14 verbatim in the plan.
- "The total fits inside the approved ceiling." This is contradicted by F1 as written, and depends on F2 and F3.

## QUESTIONS FOR THE AUTHOR
1. What is the planned start date, and does "first year" mean 12 months of employment or the current fiscal year?
2. Does the $140,000 ceiling cover salary only, or the fully loaded cost including taxes, benefits, fees and equipment?
3. Was an $11,000 line item dropped from the table, or is the total simply wrong?
4. What exactly does Survey p. 14 say? Please quote it.

## DECISION-MAKER SUMMARY
Do not send this to finance yet. The total is arithmetically wrong, salaries cover only six months of a "first-year" budget, and employer on-costs and signing bonuses are absent. If "first year" means 12 months of employment, the real cost is probably well over $140,000. If approved as is, the hires are likely to overrun the approved ceiling.

## OWNER SUMMARY
The cost figures in this hiring plan don't add up, and the stated total is $11,000 higher than its own items. The plan also counts only half a year of pay and leaves out payroll taxes, benefits and signing bonuses, so the true first-year cost is probably above the approved limit. The salary figure comes from a paid survey nobody here could check, so it should be confirmed before finance sees the plan.

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
    {"item": "planned start date and definition of the $140,000 ceiling", "status": "not_seen", "matters": true},
    {"item": "recruiter agreement (fee basis)", "status": "not_seen", "matters": false}
  ],
  "seats": [
    {"vendor": "claude-local", "status": "ran", "cross_vendor": false},
    {"vendor": "cross-vendor", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "Internal hiring budget with salary figures is confidential business material; no external or cross-vendor reviewer."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "plan.md", "kind": "file"},
      {"unit": "plan.md#Market pay: median salary claim", "kind": "claim"},
      {"unit": "plan.md#Market pay: signing bonus claim", "kind": "claim"},
      {"unit": "plan.md#Budget table rows and total", "kind": "data"},
      {"unit": "plan.md#ceiling conclusion", "kind": "claim"},
      {"unit": "6-month proration of first-year salary", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "Industry Survey 2026, p. 14", "reason": "not_supplied"},
      {"unit": "recruiter agreement", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "plan.md, budget table, Total row",
     "scenario": "Line items sum to $127,900 (84,000 + 19,750 + 11,400 + 12,750) but the stated total is $138,900; finance receives a total that matches no itemisation, or an $11,000 line was silently dropped.",
     "fix": "Correct the total to $127,900 or restore and name the missing $11,000 line item.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every figure in plan.md recomputed: salary proration, implied headroom", "found": "no other arithmetic error"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "A",
     "location": "plan.md, budget table, salaries row ('for the first year, prorated 6 months')",
     "scenario": "If 'first year' means 12 months of employment, salaries are $168,000 and the total is at least $211,900, about $72,000 over the $140,000 ceiling, yet finance approves it as fitting.",
     "fix": "State the start date and the period the ceiling covers; if 12 months, budget $168,000 for salaries and re-test the ceiling.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "other rows that may depend on the prorated basis", "found": "recruiter fee may be computed on the prorated base (S3, needs_validation)"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "A",
     "location": "plan.md, budget table (no employer on-cost rows)",
     "scenario": "Employer payroll taxes and benefits (about 7.65% FICA alone, typically 20-30% total) on $84,000 exceed the $1,100 stated headroom and likely the $12,100 true headroom, so the real cost breaks the ceiling.",
     "fix": "Add a fully loaded on-cost line at the company's actual rate, or state that the ceiling excludes on-costs.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all standard first-year hiring cost categories against the table", "found": "signing bonus also omitted (F4)"}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "plan.md, Market pay ('70% of firms offer a signing bonus') vs budget table",
     "scenario": "The plan cites signing bonuses as the market norm but budgets none; matching the market to land a senior hire breaks the ceiling or stalls hiring.",
     "fix": "Add a signing-bonus line or state a no-bonus policy and its hiring risk.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "plan.md, Market pay, '$84,000' median",
     "suspicion": "The median may be misread (wrong level, region, percentile, component or currency); it is low for senior data engineers in commonly reported US markets.",
     "unresolved_fact": "The verbatim figure, role, level, region and statistic on Industry Survey 2026 p. 14."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "plan.md, Market pay, '70% of firms offer a signing bonus'",
     "suspicion": "The figure is unverified and its denominator is unknown.",
     "unresolved_fact": "The exact passage on Survey p. 14 and the population it covers."},
    {"id": "S3", "status": "needs_validation", "track": "A", "location": "plan.md, budget table, recruiter fees row",
     "suspicion": "$19,750 is 23.5% of the prorated $84,000 but only 11.8% of the $168,000 annual base; it may be computed on the wrong base.",
     "unresolved_fact": "The recruiter agreement's fee percentage and the salary base it applies to."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "2 x $84,000 prorated 6 months is mis-computed.",
     "evidence": "168,000 x 0.5 = 84,000; the arithmetic is correct and the issue is the proration assumption (F2)."}
  ]
}
```