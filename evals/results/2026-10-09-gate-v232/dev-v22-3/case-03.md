VERDICT: **REWORK.** The arithmetic is right, but the data cannot show that the checklist caused the 12-point gap, so it does not support making the checklist mandatory or building it for two other products.

CONFIDENCE: **medium.** The core flaw follows from the work's own description of the design, so it does not depend on missing data. Confidence is limited because:
- there were no tools, so I could not run anything;
- the CSV is aggregated, with no per-account rows, dates or covariates;
- there were no independent seats.

INPUTS LEDGER:
- **Seen:** the original request (request.md), the context (context.md), analysis.md, and evidence/cohorts.csv (two aggregate rows).
- **Not supplied, and it matters:**
  - per-account data with signup date, completion date, churn date, plan and acquisition channel;
  - retention for cohorts from before the checklist launched;
  - the checklist launch date;
  - the definition of "active at day 30";
  - any data for the "other two products".

  The causal question cannot be answered without at least one of: the pre-launch cohorts, an unexposed group, or a randomized holdout.
- **Not supplied, and it does not matter:** none.

COVERAGE:
- **Checked:**
  - analysis.md: Finding, Data table, Data narrative, Recommendation;
  - evidence/cohorts.csv: both rows, with counts tied to the table;
  - every percentage, recomputed;
  - the "cannot be chance" claim, recomputed;
  - the load-bearing assumptions (causality, baseline, transfer to the mandatory version, transfer to other products).
- **Not checked:** the June to July date range and the day-30 definition, because the CSV has no date or status columns.

SEATS AND GATE:
- **Seats:** a single local reviewer. No subagent or cross-vendor seat was available in this session. The work was not written in this conversation, so the anchoring risk is lower, but no second seat checked this review.
- **Sensitivity gate:** passed. The material is aggregate counts with no personal or confidential detail.

## Reconstruct

The work claims the checklist raised 30-day retention from 40% to 52%. It recommends making the checklist mandatory and building it for two other products. For that to be correct, all of these must hold:
1. The gap between completers and non-completers must be caused by the checklist, not by who chooses to complete it.
2. Non-completers must be a fair stand-in for "no checklist".
3. Forcing completion must reproduce the effect seen among people who completed it voluntarily.
4. The effect must carry over to different products.

None of these is shown. Tracks: A (main), D (the rollout proposal).

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | A | analysis.md "Finding" and Data narrative: "shown to every new account on first login, as an optional panel" | The groups are defined by **self-selected completion**, not by exposure. Every account saw the checklist, so there is no unexposed comparison group. Users who are more engaged both finish optional setup and stay. The 12-point gap measures the difference between completers and non-completers, not the checklist's effect. | The checklist is made mandatory. Retention stays near the current overall 42.9% (2,144/5,000) because the gap was selection. The cost: an onboarding change for all new accounts plus a quarter of build work on two products, with no gain. | Run a randomized holdout: new accounts randomly get no panel, the optional panel, or the mandatory panel, with 30-day retention compared by assigned arm (intent-to-treat). A weaker fallback is pre-launch versus post-launch overall retention, with seasonality caveats. To see the problem: no data supplied distinguishes "the checklist caused retention" from "people likely to stay finish checklists". | a✓ b✓ c✓ d✓ |
| F2 | High | CONFIRMED (mechanism); magnitude unknown | A | Data narrative: "Completion takes about ten minutes over the first week" | **Survivorship (immortal-time) bias.** Completing the checklist takes days of activity. Accounts that churn on days 1 to 6 often cannot complete it, so they land in the non-completed group automatically. This drags the non-completer rate down by construction, before selection (F1) is even considered. | Even if the checklist has zero effect, early churners inflate the gap. The measured 12 points overstates whatever real effect exists. | Re-cut using only accounts still active at day 7. Compare day-30 retention by completion status within that group, or use completion by day 7 as the exposure and measure retention from day 7 to day 30. This needs per-account dates (see S3). | a✓ b✓ c✗ d✓ |
| F3 | High | CONFIRMED | A, D | analysis.md Recommendation: "Make the checklist mandatory, and build the same panel for the other two products next quarter" | The recommendation goes beyond the evidence in two ways. (1) **Mandatory is a different intervention** from what was observed. Forcing a 10-minute, week-long task on unwilling users can add friction and churn, and the data says nothing about that. (2) **No data at all** is offered for the other two products. | First-week drop-off rises under a mandatory gate. Two product teams spend a quarter building panels based on a gap in a different product that is itself confounded. | Limit any recommendation to a test of the mandatory version against the optional one in this product. Extend to other products only after a measured effect exists. Track first-week abandonment at the gate. | a✓ b✓ c✗ d✓ |
| F4 | Medium | CONFIRMED | A | analysis.md Finding: "raised 30-day retention from 40% to 52%" | **Mislabelled baseline.** The 40% is non-completers in the same period, not retention before the checklist existed. Overall retention for the exposed population is 42.9%. The phrase "raised retention" invites readers to assume company-wide retention rose 12 points. | A decision-maker reads it as "retention went from 40 to 52" and expects a company-wide jump that never shows up in the overall metric. | Report overall retention for the June to July cohorts against pre-launch cohorts. Describe the 40% versus 52% split as a correlation between completion and retention. | a✓ b✓ c✗ d✓ |
| F5 | Low | CONFIRMED | A | Data narrative: "the groups are large… so it cannot be chance" | No test is shown, and "cannot" overstates. My recompute (two-proportion z ≈ 7.3, pooled p = 0.429, SE ≈ 0.0164) agrees chance is very unlikely. But ruling out chance does not rule out bias (F1, F2), and the sentence suggests it does. | A reader takes "not chance" to mean "real effect of the checklist". | Show the test and a confidence interval. Say explicitly that significance does not address selection. | a✓ b✓ c✗ d✗ |

The gap is real and not due to chance; what the work cannot show is that the checklist caused it.

## NEEDS VALIDATION

- **S1. Exposure versus "roll out more widely".** The request asks whether to roll out more widely, but the analysis says the checklist is already shown to every new account. Is there any segment, platform or period without the panel? If so, that is the comparison group the analysis needs.
- **S2. Definition of "active at day 30".** Is it a login, a billable action, or not cancelled? How the term is defined could change both rates.
- **S3. Cohort dates and completeness.** The CSV has no date column, so the June 1 to July 31 range, and whether completion was measured by a fixed day, cannot be verified.
- **S4. Composition of the groups.** Do completers differ by plan, acquisition channel or account size? Per-account data with these fields would show how much of the gap is mix.

## REFUTED

- **"The percentages are wrong."** Recomputed: 624/1200 = 52.0% and 1520/3800 = 40.0%. The context also states this.
- **"The table does not match the CSV."** Accounts and day-30 counts match row for row.
- **"The gap could be chance."** z ≈ 7.3. Chance is not a credible explanation; selection is (F1).

## WHAT HOLDS UP

- The arithmetic and the agreement between the table and the CSV.
- The gap is real and very unlikely to be chance.
- The description of the design (an optional panel shown to all accounts) is candid. It is what makes the flaw visible.
- The sample is large enough to support a proper experiment quickly.

## UNVERIFIED CLAIMS

- **The June 1 to July 31, 2026 cohort range.** Confirm by supplying per-account signup dates.
- **"About ten minutes over the first week".** Confirm from product telemetry on time to complete.
- **"Shown to every new account".** Confirm from the feature flag or exposure logs.

## QUESTIONS FOR THE AUTHOR

1. Was there ever a group of new accounts that did not see the panel, such as a pre-launch period, a holdout or a platform without it? What was its 30-day retention?
2. What was overall 30-day retention for cohorts created before launch?
3. Can you supply per-account data with completion date and churn date, so day-1 to day-6 churners can be separated out?
4. Given that every account already sees the panel, what does "roll out more widely" mean here?

## DECISION-MAKER SUMMARY

The 12-point gap compares people who chose to finish the checklist with people who did not. It shows that engaged users finish checklists, not that the checklist keeps users. Do not make it mandatory or build it for other products yet. Run a randomized test of mandatory against optional against none first. Proceeding now risks a quarter of build work and added onboarding friction with no retention gain.

## OWNER SUMMARY

The numbers are calculated correctly, but they only show that people who finish the checklist tend to stay. They do not show that the checklist is the reason they stay. Before requiring it for everyone or copying it to other products, run a short, fair test where some new accounts get it and some do not.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "analysis.md", "status": "seen", "matters": true},
    {"item": "evidence/cohorts.csv", "status": "seen", "matters": true},
    {"item": "per-account data (signup, completion, churn dates, plan, channel)", "status": "not_seen", "matters": true},
    {"item": "pre-launch cohort retention", "status": "not_seen", "matters": true},
    {"item": "definition of active at day 30", "status": "not_seen", "matters": true},
    {"item": "data for the other two products", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Aggregate counts only; no personal or confidential detail."},
  "coverage": {
    "checked": [
      {"unit": "analysis.md", "kind": "file"},
      {"unit": "analysis.md#Finding", "kind": "section"},
      {"unit": "analysis.md#Data", "kind": "section"},
      {"unit": "analysis.md#Recommendation", "kind": "section"},
      {"unit": "evidence/cohorts.csv", "kind": "data"},
      {"unit": "checklist caused the retention gap", "kind": "assumption"},
      {"unit": "cannot be chance", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "cohort date range June-July 2026", "reason": "CSV has no date column"},
      {"unit": "day-30 activity definition", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "A",
     "location": "analysis.md Finding; Data narrative 'shown to every new account on first login, as an optional panel'",
     "scenario": "Groups are self-selected by completion with no unexposed control; the checklist is made mandatory and overall retention stays near 42.9% because the gap was selection, not effect.",
     "fix": "Randomized holdout (none vs optional vs mandatory) analysed by assigned arm; fallback pre/post comparison of overall retention.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "No supplied data separates 'checklist causes retention' from 'retainers complete checklists'; every account was exposed."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "analysis.md Data narrative 'Completion takes about ten minutes over the first week'",
     "scenario": "Accounts churning in days 1-6 cannot complete and fall into non-completed by construction, inflating the gap even with zero true effect.",
     "fix": "Restrict to accounts active at day 7, or use completion-by-day-7 exposure and measure day 7 to day 30 retention.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "With per-account dates, count non-completers churned before day 7; recompute the gap excluding them."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "D",
     "location": "analysis.md Recommendation",
     "scenario": "A mandatory gate (an untested intervention) adds first-week friction and churn, and two products build panels with no supporting data.",
     "fix": "Test mandatory vs optional in this product first; extend only after a measured effect; track gate abandonment.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "No data for a mandatory version or for the other two products appears in the inputs."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "analysis.md Finding 'raised 30-day retention from 40% to 52%'",
     "scenario": "Readers expect a company-wide 12-point rise; the 40% is concurrent non-completers and the overall exposed rate is 42.9% (2,144/5,000).",
     "fix": "Report overall retention against pre-launch cohorts; describe 40 vs 52 as an association.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "(624+1520)/(1200+3800) = 2144/5000 = 42.9%."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
     "location": "analysis.md Data narrative 'so it cannot be chance'",
     "scenario": "Readers take 'not chance' to mean 'real checklist effect'; significance does not address selection bias.",
     "fix": "Show the test and a confidence interval; state that significance does not rule out bias.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Two-proportion z = 0.12 / 0.0164 = 7.3; chance is excluded but bias is not."},
    {"id": "S1", "status": "needs_validation", "track": "A", "location": "request.md 'roll it out more widely' vs analysis.md 'shown to every new account'",
     "suspicion": "Scope of the current rollout is unclear; there may be an unexposed segment usable as a control.",
     "unresolved_fact": "Whether any segment, platform or period had no checklist panel."},
    {"id": "S2", "status": "needs_validation", "track": "A", "location": "evidence/cohorts.csv active_day30",
     "suspicion": "The activity definition may affect both rates.",
     "unresolved_fact": "The exact definition of active at day 30."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "analysis.md Data heading (1 June to 31 July 2026)",
     "suspicion": "Cohort range and completion window cannot be verified.",
     "unresolved_fact": "Per-account signup and completion dates."},
    {"id": "S4", "status": "needs_validation", "track": "A", "location": "evidence/cohorts.csv",
     "suspicion": "Completers may differ in plan, channel or size, explaining part of the gap.",
     "unresolved_fact": "Group composition by plan, channel and account size."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The percentages are wrong.", "evidence": "624/1200 = 52.0% and 1520/3800 = 40.0%."},
    {"id": "R2", "candidate": "The table does not match the CSV.", "evidence": "Accounts and day-30 counts match row for row."},
    {"id": "R3", "candidate": "The gap could be chance.", "evidence": "Two-proportion z is about 7.3."}
  ]
}
```