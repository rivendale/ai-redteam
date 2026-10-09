# Redteam review: onboarding checklist analysis

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** This session has no subagent and no tools. I did not author the work. I recomputed all arithmetic by hand.

**VERDICT: REWORK.** The analysis claims the checklist *caused* a 12-point retention gain. The data only compares users who chose to complete it with users who didn't, so it cannot support making the checklist mandatory for every new account.

**CONFIDENCE: high** on the verdict. The core flaw is visible in the work's own text and needs no tools. What limits confidence: same-context review, no account-level data, and an unknown checklist launch date.

**INPUTS LEDGER**
- Seen: request.md, context.md, analysis.md, evidence/cohorts.csv (2 aggregate rows).
- Not seen, matters:
  - The checklist launch date. Without it there is no pre-launch baseline, and the request asks whether retention *improved*.
  - The definitions of "completed" and "active_day30".
  - Account-level data such as signup date, plan, channel and early activity. Without it, confounders can't be checked.
- Not seen, matters for the extension recommendation only: anything about the other two products.

**COVERAGE**
- Checked:
  - Every figure in the table, against the CSV and recomputed.
  - The headline claim and the "cannot be chance" claim.
  - Both recommendations.
  - The unstated assumption that completion is independent of user intent.
- Not checked: raw data, the active/completed definitions, launch timing, and the other products. None were supplied.

**SEATS AND GATE:** Local same-context reviewer only. The sensitivity gate passed: aggregate counts only, no personal data. Cross-vendor seats were not requested and the depth is standard, so none ran.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | A | analysis.md "Finding" line; "shown to every new account … as an optional panel" | Causal claim ("the checklist raised 30-day retention from 40% to 52%") rests on a self-selected comparison. Every account was exposed. The groups differ only in whether the user *chose* to finish. "From 40% to 52%" reads as before/after, but both numbers come from the same period. | Motivated, high-intent users both finish optional setup tasks and stay longer. Suppose the checklist has zero effect. Completers would still retain better. The company would then mandate it for all accounts based on a gap that its own users' intent created. | Answer the question the request asked. Either compare launch-period retention with a pre-launch baseline, or run a randomized holdout (show the checklist vs. don't). Restate the current result as "completers retained 12 pts better than non-completers; not causal." | a✔ b✔ c✔ d✔ |
| F2 | High | PROBABLE | A | analysis.md "Completion takes about ten minutes over the first week" | Immortal-time bias. A user must stay around long enough to complete. Anyone who churned in days 1–7 is placed in `not_completed` by construction, which inflates the gap mechanically. | 300 of the 3,800 non-completers left on day 2 before they could finish. They count against "did not complete" and lower that group's retention, with no checklist effect at all. | Define groups only among accounts still active at day 7, and measure retention from day 7 to day 30. Alternatively, use intent-to-treat (pre vs post launch). Reproduce by splitting the CSV by last-active date. | a✔ b✘ c✔ d✔ |
| F3 | High | PROBABLE | A/D | analysis.md "Recommendation": "Make the checklist mandatory" | The data concerns *voluntary* completion. Mandatory completion is a different intervention, and no data was gathered on it. Forcing a 10-minute, week-long task on low-intent users can add friction and lower activation. No alternatives were weighed: a stronger nudge, a shorter checklist, or an A/B test first. | Once mandatory, the 3,800 users who skipped it now face a gate. Some abandon onboarding. Retention for the whole cohort falls, and the rollout covers every new account, so the cost is broad and slow to detect. | Pilot "mandatory" against "optional" on a random slice before a full rollout. Pre-register the primary metric: 30-day retention of *all* new accounts, not only completers. | a✔ b✘ c✔ d✔ |
| F4 | Medium | CONFIRMED | A/D | analysis.md "add similar checklists to the other products" / "build the same panel for the other two products next quarter" | The recommendation extrapolates to two other products with no data from them. It also inherits F1: it scales an effect that has not been shown to exist. | A quarter of build effort goes to panels in products with different users and onboarding paths. The benefit is unknown even for the original product. | Gate this on a causal result from the original product, plus a per-product pilot. | a✔ b✔ c✘ d✘ |
| F5 | Low | CONFIRMED | A | analysis.md "so it cannot be chance" | The claim is asserted without a test. It is also the wrong defence: ruling out chance does not rule out bias. My recomputation agrees that chance is unlikely (two-proportion z ≈ 7.3), but the sentence implies significance settles the question. | A reader takes "not chance" to mean "real effect" and skips the bias question. | Report the test and its interval. State plainly that significance does not address selection. | a✔ b✔ c✘ d✘ |

### Severity notes
- **F1** is Critical because the confirmed logic flaw breaks the original request. The question was whether the checklist *improved* retention, and the recommendation changes onboarding for every new account.
- **F2** is PROBABLE because the exact completion definition was not supplied. If completion could not occur after churn, the bias holds.
- **F3** is High through (a), (c) and (d): plausible customer harm and a realistic scenario. Its evidence is PROBABLE, not CONFIRMED.

### Confirm-or-refute round
- **F1, defended:** "Large groups make it robust." Refuted as a defence. Sample size reduces noise, not selection bias. F1 holds.
- **F2, defended:** "Maybe completion counts even after inactivity." That only weakens F2 if users can complete after leaving, and that is implausible for an in-app panel. F2 holds as PROBABLE.
- **F3, defended:** "Mandatory just means more people get the benefit." This presumes F1's causal effect exists. F3 holds.

## NEEDS VALIDATION
- **S1:** There may be no untreated cohort at all. Unresolved fact: the checklist launch date relative to 1 June 2026. If it launched before June, every account in the data was exposed, and the data cannot answer "did it improve retention" without an earlier baseline.
- **S2:** Groups may differ on plan, acquisition channel or signup month. Unresolved fact: account-level attributes, which were not supplied.
- **S3:** "Active at day 30" may be defined loosely, for example as any login. Unresolved fact: the metric definition.

## REFUTED
- **"The 12-point gap is just noise."** Refuted. Pooled rate 2,144/5,000 = 42.88%. SE ≈ √(0.4288·0.5712·(1/1200+1/3800)) ≈ 0.0164, so z ≈ 0.12/0.0164 ≈ 7.3.
- **"The percentages are wrong."** Refuted. 624/1200 = 52.0% and 1520/3800 = 40.0%. Both match the CSV, as context.md also states.

## WHAT HOLDS UP
- The table matches cohorts.csv exactly, and the arithmetic is correct.
- The difference between the groups is statistically real.
- The observation window is complete. Accounts created on 31 July reached day 30 on 30 August 2026, before the review date.
- "Completers retained better than non-completers" is a true descriptive statement.

## UNVERIFIED CLAIMS
- **"Completion takes about ten minutes."** Confirm from panel telemetry: median completion time.
- **"Shown to every new account on first login."** Confirm from feature-flag or exposure logs.
- **"The checklist raised retention"** (causal). Confirm with a randomized holdout or a pre/post comparison adjusted for seasonality.

## QUESTIONS FOR THE AUTHOR
1. When did the checklist launch, and what was 30-day retention for comparable cohorts before it?
2. How are "completed" and "active at day 30" defined, and can a user who churned in week 1 ever count as completed?
3. Is a randomized holdout possible before making it mandatory?

## DECISION-MAKER SUMMARY
The 12-point gap compares users who chose to finish the checklist with those who didn't. It does not show that the checklist caused better retention. Run a randomized holdout, or at least a pre/post-launch comparison, before making it mandatory or building it for other products. Proceeding now risks adding friction to every new account's onboarding, plus a quarter of build work, for an effect that may be zero.

## OWNER SUMMARY
People who finished the new onboarding checklist stayed longer, but they were probably the most engaged people to begin with, so we can't yet tell whether the checklist helped. Forcing everyone through it could even push some new customers away. A short controlled test should come before changing onboarding for everyone or copying it to other products.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "analysis.md", "status": "seen", "matters": true},
    {"item": "evidence/cohorts.csv", "status": "seen", "matters": true},
    {"item": "checklist launch date / pre-launch retention baseline", "status": "not_seen", "matters": true},
    {"item": "definitions of completed and active_day30", "status": "not_seen", "matters": true},
    {"item": "account-level data (signup date, plan, channel)", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Aggregate counts only; no personal or confidential data."},
  "coverage": {
    "checked": [
      {"unit": "analysis.md", "kind": "file"},
      {"unit": "evidence/cohorts.csv", "kind": "data"},
      {"unit": "analysis.md:Finding", "kind": "claim"},
      {"unit": "analysis.md:cannot be chance", "kind": "claim"},
      {"unit": "analysis.md:Recommendation", "kind": "section"},
      {"unit": "completion is independent of user intent", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "account-level data", "reason": "not supplied"},
      {"unit": "checklist launch date", "reason": "not supplied"},
      {"unit": "other two products", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "A",
     "location": "analysis.md: Finding line; 'shown to every new account ... as an optional panel'",
     "scenario": "Every account was exposed and completion was optional, so high-intent users self-select into completing and also retain better; with zero true effect the 12-point gap still appears, and onboarding is changed for all accounts on that basis.",
     "fix": "Measure causally: randomized holdout or pre/post-launch comparison; restate the current result as a non-causal association.",
     "answers": {"a": true, "b": true, "c": true, "d": true}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "A",
     "location": "analysis.md: 'Completion takes about ten minutes over the first week'",
     "scenario": "Accounts that churn before finishing in week 1 are counted as not_completed by construction, mechanically lowering that group's retention (immortal-time bias).",
     "fix": "Restrict both groups to accounts active at day 7 and measure day-7-to-30 retention, or use intent-to-treat pre/post comparison.",
     "answers": {"a": true, "b": false, "c": true, "d": true}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "A",
     "location": "analysis.md: Recommendation 'Make the checklist mandatory'",
     "scenario": "Mandatory completion is a different intervention from voluntary; gating low-intent users behind a week-long task can reduce activation and lower overall retention across all new accounts.",
     "fix": "Pilot mandatory vs optional on a random slice; primary metric is 30-day retention of all new accounts.",
     "answers": {"a": true, "b": false, "c": true, "d": true}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "D",
     "location": "analysis.md: 'build the same panel for the other two products next quarter'",
     "scenario": "A quarter of build effort goes to two products with no supporting data, scaling an effect not shown to exist.",
     "fix": "Gate on a causal result in the original product and a per-product pilot.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
     "location": "analysis.md: 'so it cannot be chance'",
     "scenario": "Readers take 'not chance' as proof of a real effect; significance (z about 7.3) does not address selection bias.",
     "fix": "Report the test and interval and state that significance does not rule out bias.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "A", "location": "evidence/cohorts.csv",
     "suspicion": "No untreated cohort exists in the data.",
     "unresolved_fact": "Checklist launch date relative to 1 June 2026."},
    {"id": "S2", "status": "needs_validation", "track": "A", "location": "evidence/cohorts.csv",
     "suspicion": "Groups differ on plan, channel or signup month.",
     "unresolved_fact": "Account-level attributes for both groups."},
    {"id": "S3", "status": "needs_validation", "track": "A", "location": "evidence/cohorts.csv:active_day30",
     "suspicion": "The retention metric may be loosely defined.",
     "unresolved_fact": "Definition of active at day 30."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The 12-point gap is noise.",
     "evidence": "Two-proportion z about 7.3 (pooled 2144/5000 = 42.88%, SE about 0.0164)."},
    {"id": "C2", "candidate": "The retention percentages are miscomputed.",
     "evidence": "624/1200 = 52.0%, 1520/3800 = 40.0%, matching the CSV."}
  ]
}
```