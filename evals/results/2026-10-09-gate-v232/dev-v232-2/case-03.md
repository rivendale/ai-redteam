VERDICT: **REWORK.** The arithmetic is correct, but the design cannot show that the checklist caused the 12-point gap, and the recommendation goes well past what the data shows.

CONFIDENCE: **medium.** I had no tools, so I recomputed everything by hand and validated nothing by running it. I was the only reviewer, but not the author, so there is no same-context anchoring. The main limit is missing inputs: the launch date, a pre-launch baseline and account-level data.

INPUTS LEDGER:
- **Seen:** request.md, context.md, analysis.md, evidence/cohorts.csv (two aggregate rows).
- **Not seen, and it matters:**
  - The checklist launch date, and whether any June–July accounts predate it.
  - Retention for cohorts created before the checklist existed.
  - Account-level data with signup date, channel, plan and first-week activity.
  - The definition of "still active at day 30."
- **Not seen, and it does not matter here:** `docs/why-reviews-fail.md` and `docs/attack-catalog.md`. I also could not run `tools/validate_findings.py`.

COVERAGE:
- **Scope:** the whole work.
- **Checked:**
  - Every figure in the table.
  - The CSV against the table.
  - The causal claim, the "cannot be chance" claim, and both parts of the recommendation (mandatory, other products).
  - The fit between the work and the original request.
- **Not checked:** the external docs and the validator script (no tools); the cohort mix inside the CSV (not supplied).

SEATS AND GATE: one reviewer, no subagent and no tools. The sensitivity gate found nothing sensitive (aggregate counts only). No cross-vendor seats were requested.

**Recomputed by hand:**
- 624/1,200 = 52.0% and 1,520/3,800 = 40.0%. Both match the table and the CSV.
- Overall: 2,144/5,000 = 42.9%.
- Two-proportion z ≈ 0.12 / 0.0164 ≈ 7.3.

FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | A | analysis.md "Finding" line; Data paragraph "shown to every new account … as an optional panel" | The comparison is completers vs non-completers. Both groups were shown the checklist, and completion was self-selected. There is no unexposed group, so "raised 30-day retention from 40% to 52%" misdescribes the data: 40% is not retention without the checklist. | Highly engaged users are both more likely to finish an optional 10-minute task and more likely to stay. The 12 points can then be entirely selection, and the checklist's true effect could be zero or negative. | Compare all June–July accounts (42.9%) with a matched pre-launch cohort as an interrupted time series. Better, run a randomized holdout (show vs. don't show). Report the result as an association until then. | a✓ b✓ c✗ d✓ |
| F2 | High | CONFIRMED | A | Data paragraph: "Completion takes about ten minutes over the first week" | Immortal-time bias. An account that churns on day 1–6 cannot complete a checklist that spans the first week, so early churners fall into "not_completed" by construction. | Two users have identical intent; one leaves on day 3. That user is counted as a non-completer who churned, which inflates the gap even if the checklist has no effect. | Restrict both groups to accounts still active at day 7, and define the groups by completion within days 0–7. Compare day-30 retention among those survivors. | a✓ b✓ c✗ d✓ |
| F3 | High | CONFIRMED | A | Recommendation: "Make the checklist mandatory" | Drift and extrapolation. The data concerns optional, voluntary completion. Making it mandatory is a different intervention, and forced completion by uninterested users need not carry the volunteers' retention. Doing nothing, a randomized test, or making the checklist more prominent were not considered. | The checklist becomes mandatory for all new accounts. The added friction raises early abandonment, and overall retention falls below 42.9%. | Recommend a randomized test of "mandatory vs. optional," with a day-30 retention readout, before any rollout. | a✓ b✓ c✗ d✓ |
| F4 | Medium | CONFIRMED | A | Recommendation: "build the same panel for the other two products next quarter" | There is no evidence from those products. Even a true effect here would not transfer automatically. | A quarter of build effort goes into panels whose effect was never measured. | Make this conditional on a positive randomized result here, plus a small pilot per product. | a✓ b✓ c✗ d✗ |
| F5 | Low | CONFIRMED | A | Data paragraph: "so it cannot be chance" | The claim is asserted without a test and is used as though significance settled causation. It does not: F1 and F2 are bias, not noise. | A reader treats "not chance" as "caused by the checklist." | Report z ≈ 7.3 or a CI on the difference (about 8.8–15.2 points, hand-computed). State that this rules out noise only, not selection. | a✓ b✓ c✗ d✗ |

Severity notes:
- **F1–F3 are not Critical.** Each flaw is confirmed. What is not confirmed is the harm of acting on it: whether the checklist actually lowers or fails to raise retention is unknown (c = no). The rollout is also reversible.
- **Siblings searched for F1–F3:** I checked every causal or extrapolating sentence in analysis.md. F4 and F5 are the only others. None of these are security findings.

NEEDS VALIDATION:
- **S1: confounding by cohort mix.** June and July may differ in acquisition channel, plan or promotions, and completion rates may differ across those segments (a Simpson's-paradox risk). This is settled by account-level data broken down by month and channel.
- **S2: launch timing.** If the checklist launched partway through June, some "not_completed" accounts never saw it. This is settled by the launch timestamp versus account creation dates.
- **S3: the outcome definition.** It is unclear whether "active at day 30" means a login on day 30 or any activity in days 23–30. The choice could favour users who had to log in to finish the checklist. This is settled by the metric definition.

REFUTED:
- **"The percentages or counts are wrong."** I recomputed 52.0% and 40.0% exactly, and they match the CSV.
- **"The gap could be chance."** By hand, z ≈ 7.3, so noise is not a plausible explanation. The weakness is bias, not sample size.

WHAT HOLDS UP:
- The arithmetic is correct.
- The table matches the CSV.
- The day-30 window is fully observed for July 31 signups as of today.
- The difference is statistically real as an association.

UNVERIFIED CLAIMS:
- **"The checklist raised 30-day retention."** Confirm with a randomized holdout, or with a pre/post comparison of overall retention.
- **The checklist is "shown to every new account on first login."** Confirm from product logs or exposure events.
- **Completion "takes about ten minutes over the first week."** Confirm from completion-time telemetry.

QUESTIONS FOR THE AUTHOR:
1. What was 30-day retention for accounts created before the checklist launched?
2. When exactly did the checklist launch?
3. Does the gap survive when both groups are restricted to accounts active at day 7?
4. Is a randomized holdout feasible?

DECISION-MAKER SUMMARY: The data shows that users who chose to finish the checklist stayed longer. It does not show that the checklist made them stay, and making it mandatory is an untested change. Run a randomized test, or at minimum a pre/post and day-7-survivor comparison, before changing onboarding for everyone. Proceeding now risks adding friction to every new account with no proven benefit, and spending a quarter extending it to two more products.

OWNER SUMMARY: The numbers are added up correctly, but they compare people who chose to do the checklist with people who didn't, and keen users do both things. So we don't yet know whether the checklist itself helps. A short controlled test should come before forcing it on everyone or building it for other products.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "analysis.md", "status": "seen", "matters": true},
    {"item": "evidence/cohorts.csv", "status": "seen", "matters": true},
    {"item": "checklist launch date", "status": "not_seen", "matters": true},
    {"item": "pre-launch cohort retention", "status": "not_seen", "matters": true},
    {"item": "account-level data (signup date, channel, plan, day-7 activity)", "status": "not_seen", "matters": true},
    {"item": "definition of active at day 30", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "aggregate counts only"},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "analysis.md", "kind": "document"},
      {"unit": "evidence/cohorts.csv", "kind": "data"},
      {"unit": "analysis.md: causal claim 40% to 52%", "kind": "claim"},
      {"unit": "analysis.md: cannot be chance", "kind": "claim"},
      {"unit": "analysis.md: Recommendation", "kind": "section"}
    ],
    "not_checked": [
      {"unit": "docs/why-reviews-fail.md", "reason": "no_tools"},
      {"unit": "docs/attack-catalog.md", "reason": "no_tools"},
      {"unit": "pre-launch cohorts and launch date", "reason": "not_supplied"},
      {"unit": "account-level data", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "analysis.md: Finding line and Data paragraph ('optional panel')",
     "scenario": "Completion is self-selected and both groups saw the checklist; engaged users both complete it and retain, so the 12-point gap can be pure selection and is not retention 'without' the checklist.",
     "fix": "Compare all June-July accounts (42.9%) to a matched pre-launch cohort, or run a randomized show/no-show holdout; report as association until then.",
     "answers": {"a": true, "b": true, "c": false, "d": true}, "security": false,
     "siblings_searched": {"searched": "every causal or extrapolating sentence in analysis.md", "found": "F3, F4, F5"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "analysis.md: Data paragraph ('takes about ten minutes over the first week')",
     "scenario": "Accounts that churn before finishing the week-long checklist are forced into not_completed, inflating the gap by construction (immortal-time bias).",
     "fix": "Restrict both groups to accounts active at day 7, with groups defined by completion within days 0-7, then compare day-30 retention.",
     "answers": {"a": true, "b": true, "c": false, "d": true}, "security": false,
     "siblings_searched": {"searched": "group definitions in analysis.md and cohorts.csv", "found": "no other timing-defined group"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "analysis.md: Recommendation ('Make the checklist mandatory')",
     "scenario": "Mandatory completion is a different intervention than voluntary; forcing it on all new accounts adds friction and may lower overall retention below 42.9%.",
     "fix": "Recommend a randomized test of mandatory vs optional with a day-30 readout before any rollout.",
     "answers": {"a": true, "b": true, "c": false, "d": true}, "security": false,
     "siblings_searched": {"searched": "all recommendation sentences", "found": "F4 (other products)"}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "analysis.md: Recommendation ('other two products next quarter')",
     "scenario": "A quarter of build effort goes into panels for products with no evidence of effect.",
     "fix": "Make it conditional on a positive randomized result here and a pilot per product.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
     "location": "analysis.md: Data paragraph ('cannot be chance')",
     "scenario": "Significance is asserted without a test and read as proof of causation, though it rules out only noise, not bias.",
     "fix": "Report z of about 7.3 or a CI on the difference and state it does not address selection.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "A", "location": "evidence/cohorts.csv",
     "suspicion": "Cohort mix (month, channel, plan) confounds completion and retention.",
     "unresolved_fact": "Account-level breakdown by signup month and channel."},
    {"id": "S2", "status": "needs_validation", "track": "A", "location": "analysis.md: Data heading (1 June to 31 July)",
     "suspicion": "Some not_completed accounts predate the checklist launch.",
     "unresolved_fact": "Launch timestamp versus account creation dates."},
    {"id": "S3", "status": "needs_validation", "track": "A", "location": "analysis.md: table column 'still active at day 30'",
     "suspicion": "The activity definition may favour users who logged in to complete the checklist.",
     "unresolved_fact": "Exact definition of active at day 30."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Percentages or counts are wrong.", "evidence": "624/1200 = 52.0%, 1520/3800 = 40.0%; table matches the CSV."},
    {"id": "C2", "candidate": "The gap could be chance.", "evidence": "Hand-computed two-proportion z of about 7.3."}
  ]
}
```

I could not run `tools/validate_findings.py` in this session, so this block has not been validated against the schema.