> Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes. No tools were available in this session, so nothing was run or opened beyond the text supplied.

**VERDICT: REWORK.** The analysis compares people who chose to finish the checklist with people who did not, so it cannot show that the checklist caused the retention gap, and the recommendation goes beyond what the data covers.

**CONFIDENCE: high** on the verdict. The main defects come straight from the work's own text and arithmetic. Three things limit confidence on the details: there were no tools, only one reviewer ran, and the CSV has no account-level, date or segment fields.

**INPUTS LEDGER**
- Seen: `request.md`, `context.md`, `analysis.md`, `evidence/cohorts.csv` (two aggregate rows).
- Not seen, and it matters:
  - Account-level data (signup date, completion date, churn date). Needed to test the timing bias in F2.
  - Any cohort from before the checklist launched. Needed for a real comparison.
  - Definitions of "completed" and "active at day 30".
  - Segment fields such as plan, channel and region.
- Not seen, and it does not matter for the verdict: the checklist's launch date, and data on the other two products.

**COVERAGE**
- Scope: the whole work.
- Checked:
  - `analysis.md`: headline finding, data table, method paragraph, recommendation.
  - `evidence/cohorts.csv`.
  - `request.md`, `context.md`.
  - Arithmetic: 624/1200 = 52.0%; 1520/3800 = 40.0%; total 5,000 accounts, 2,144 active (42.9%).
  - Significance: two-proportion z ≈ 7.3, computed by hand.
  - The causal claim, the "cannot be chance" claim, and the claims about making it mandatory and adding it to other products.
- Not checked: the cohort window and the metric definitions, because the CSV has no dates and no definitions were supplied.

**SEATS AND GATE**
- One local reviewer only.
- No subagent or cross-vendor seats were available.
- Sensitivity gate passed: the data is aggregate counts with no personal information.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | A | analysis.md, "Finding" and the "optional panel" sentence | Users chose whether to complete the checklist, so the two groups differ in more than the checklist. Motivated or better-fit users are more likely both to finish an optional ten-minute task and to stay. The work states a causal result ("the checklist raised 30-day retention") from a correlation. It answers "do completers retain better?" rather than the question asked: "did the checklist improve retention?" | The checklist is made mandatory for all new accounts. Retention stays near the current 42.9% overall, or falls. The 12-point gap was a difference in who completes, not an effect of the checklist. | Estimate the causal effect. Best option: a randomized holdout where some new accounts do not see the panel, compared on everyone assigned, not only completers. Fallback: overall day-30 retention for cohorts before vs after launch, with seasonality and acquisition mix controlled. Check: the gap should shrink when you compare like-for-like users (same plan and channel). | y/y/y/y |
| F2 | High | CONFIRMED | A | analysis.md: "Completion takes about ten minutes over the first week" | Timing bias. A user who leaves in the first days never gets the chance to complete, so they land in "did not complete" automatically. This inflates the gap even if the checklist does nothing. Same root cause as F1 (the groups are defined by behavior after signup), but a separate mechanism. | Users who churn in week one are all counted as non-completers. That alone can produce a large gap. A mandatory checklist cannot fix churn that happens before the user would finish it. | Restrict both groups to accounts still active at day 7 and compare from there. Or define the comparison at signup (exposed vs not exposed). Check: if the gap shrinks sharply among users active at day 7, the bias is real. | y/y/n/y |
| F3 | High | CONFIRMED | A/D | analysis.md, "Recommendation" | The recommendation is for something no data covers. The data is about an *optional* panel on *one* product. The work recommends making it *mandatory* and building it for *two other products*. Forcing a ten-minute task on users can raise early drop-off, and the work has no data on the other products. | A mandatory checklist blocks or annoys users in week one and lowers activation. Two products then spend a quarter building panels with no evidence they help. | If the causal test in F1 holds, test a mandatory version in an experiment before rollout. Treat the other products as separate experiments. Set an exit rule (for example, revert if day-7 activation falls by X). | y/y/y/y |
| F4 | Medium | CONFIRMED | A/C | analysis.md: "from 40% to 52%" | The phrasing reads as a before-and-after change, but 40% is the non-completer rate, not a baseline. Current overall retention is 2,144/5,000 = 42.9%. Even if the gap were fully causal and everyone completed, the overall gain would be about 9.1 points (52.0 − 42.9), not 12. | A decision-maker budgets for a 12-point lift that the work's own figures cannot deliver. | Report overall retention and the expected lift at a realistic completion rate. State clearly that 40% is the non-completer group, not a prior baseline. | y/y/n/y |
| F5 | Medium | CONFIRMED | A | analysis.md, data table; evidence/cohorts.csv | There is no comparison cohort and no breakdown by segment. Every account in the window saw the panel ("shown to every new account"), so nothing in the data shows what happens without the checklist. The two-row table also cannot rule out a mix effect, where plan, channel or region differ between the groups and drive the gap. | Paid or sales-assisted accounts complete more and also retain more. The gap reflects plan type, not the checklist, and the analysis cannot detect this. | Break the comparison down by plan and acquisition channel. Add the overall retention of pre-launch cohorts. | y/y/n/n |

Sibling search for F1–F3: I looked through the whole of `analysis.md` for other causal claims resting on behavior-defined groups. The only other one is the plan to add similar checklists to the other products, which is covered in F3. No security findings.

## NEEDS VALIDATION
- **S1.** Is the cohort window really 1 June – 31 July 2026, and was every account given a full 30 days? This is settled by signup dates in the raw data; the CSV has none.
- **S2.** How are "completed" and "active at day 30" defined? For example, does completing count only all steps, and does "active" mean a login or a paid status? This is settled by the metric definitions.
- **S3.** Did the checklist launch at the same time as other changes, such as pricing or marketing? This is settled by the release log for May–July.

## REFUTED
- **"It cannot be chance" is wrong.** Refuted. The pooled rate is 0.4288, the standard error is about 0.0164, and z is about 7.3, so the gap is not chance. But ruling out chance does nothing about the selection bias in F1 and F2. The work treats "not chance" as if it meant "caused by the checklist", and that error is F1.
- **The percentages are wrong.** Refuted. 624/1200 = 52% and 1520/3800 = 40%, consistent with `context.md`.

## WHAT HOLDS UP
- The arithmetic.
- The sample sizes.
- The conclusion that the completer gap is unlikely to be noise.
- The day-30 measurement window. The last cohort hit day 30 on about 30 August 2026, before this review date of 8 October 2026.

## UNVERIFIED CLAIMS
- The cohort dates (S1).
- The "ten minutes over the first week" completion time. Check this against product telemetry.
- That the panel is "shown to every new account". Check this against the feature-flag configuration.

## QUESTIONS FOR THE AUTHOR
1. Is there a cohort from before launch, or a holdout group that did not see the panel?
2. What is the gap among accounts still active at day 7?
3. Does the gap persist within each plan and acquisition channel?

## DECISION-MAKER SUMMARY
The 12-point gap compares users who chose to finish the checklist against those who did not, so it does not show that the checklist works. Before rolling out, run a holdout experiment or a pre-versus-post comparison, and test a mandatory version separately. If you proceed now, you risk forcing a ten-minute task on every new account for no gain, possibly with more early drop-off, and copying it to two products with no evidence.

## OWNER SUMMARY
Customers who finished the new checklist did stay longer. But they were likely the more committed customers to begin with, so we cannot yet tell whether the checklist itself helped. We recommend a short controlled test before making it required for everyone or copying it to other products.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "analysis.md", "status": "seen", "matters": true},
    {"item": "evidence/cohorts.csv", "status": "seen", "matters": true},
    {"item": "account-level data with signup, completion and churn dates", "status": "not_seen", "matters": true},
    {"item": "pre-launch or holdout cohort", "status": "not_seen", "matters": true},
    {"item": "metric definitions for completed and active_day30", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Aggregate counts only; no personal data."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "analysis.md", "kind": "file"},
      {"unit": "evidence/cohorts.csv", "kind": "data"},
      {"unit": "analysis.md:Finding (causal claim)", "kind": "claim"},
      {"unit": "analysis.md:cannot be chance", "kind": "claim"},
      {"unit": "analysis.md:Recommendation", "kind": "section"},
      {"unit": "retention percentages and z-test recomputation", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "cohort window 1 June-31 July 2026", "reason": "not_supplied"},
      {"unit": "metric definitions", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "A",
     "location": "analysis.md: Finding; 'shown to every new account on first login, as an optional panel'",
     "scenario": "Completion is self-selected; motivated users both complete and retain. Checklist made mandatory, overall retention stays near 42.9% or falls because the 12-point gap was selection, not effect.",
     "fix": "Estimate the causal effect: randomized holdout analysed by exposure (intention-to-treat), or pre/post overall retention with seasonality and mix controls.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every causal or extrapolated claim in analysis.md resting on behavior-defined groups",
                           "found": "the other-products recommendation, recorded as F3"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "analysis.md: 'Completion takes about ten minutes over the first week'",
     "scenario": "Users who churn in week one cannot complete, so they are counted as non-completers by construction, inflating the gap even with zero effect.",
     "fix": "Restrict to accounts active at day 7 or compare by exposure at signup; check whether the gap shrinks.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "other group definitions in analysis.md and cohorts.csv that depend on post-signup behavior",
                           "found": "none besides the completed/not_completed split"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "analysis.md: Recommendation",
     "scenario": "Evidence covers an optional panel on one product; a mandatory ten-minute task may raise early drop-off, and two products build panels with no evidence.",
     "fix": "Test a mandatory variant experimentally with a pre-set exit criterion; treat other products as separate experiments.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all recommendations and generalizations in analysis.md",
                           "found": "mandatory rollout and other-products rollout, both in this finding's section"}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "analysis.md: 'from 40% to 52%'",
     "scenario": "The phrasing implies a before/after lift; current overall retention is 42.9%, so even a fully causal effect at 100% completion gives about 9.1 points, not 12.",
     "fix": "Report overall retention and the expected lift at a realistic completion rate; label 40% as the non-completer rate.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "analysis.md data table; evidence/cohorts.csv",
     "scenario": "All accounts saw the panel, so there is no unexposed comparison; plan or channel mix could drive the gap undetected.",
     "fix": "Break down by plan and acquisition channel; add pre-launch cohort retention.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "analysis.md: Data heading",
     "suspicion": "Cohort window and full 30-day observation not verifiable.",
     "unresolved_fact": "Signup dates per account; cohorts.csv has none."},
    {"id": "S2", "status": "needs_validation", "track": "A", "location": "evidence/cohorts.csv header",
     "suspicion": "Definitions of completed and active_day30 may bias the comparison.",
     "unresolved_fact": "Written metric definitions."},
    {"id": "S3", "status": "needs_validation", "track": "A", "location": "analysis.md: Data",
     "suspicion": "Concurrent launches may confound any pre/post comparison.",
     "unresolved_fact": "Release log for May-July 2026."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "'It cannot be chance' is wrong.",
     "evidence": "Two-proportion z is about 7.3 (pooled p 0.4288, SE about 0.0164); chance is ruled out. The real flaw is causal, recorded as F1."},
    {"id": "C2", "candidate": "Retention percentages are miscomputed.",
     "evidence": "624/1200 = 52.0% and 1520/3800 = 40.0%."}
  ]
}
```