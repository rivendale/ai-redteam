**Review note:** I reviewed this in a session with no tools, so I couldn't open files, run code or launch a subagent. I didn't write the work, so there's no shared-author anchoring, but no independent second reviewer ran. I recomputed every figure by hand.

---

**VERDICT: REWORK.** The causal claim comes from comparing people who chose to finish an optional checklist against people who didn't, so the data can't show the checklist caused anything. The recommendation goes even further than that claim.

**CONFIDENCE: medium.** The design flaws are visible in the work's own text, so those findings are firm. Confidence is limited by:
- no tools;
- no data from before the checklist launched;
- no launch date;
- no definition of "completed" or "active".

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| request.md | seen | – |
| context.md | seen | – |
| analysis.md | seen | – |
| evidence/cohorts.csv | seen, 2 summary rows only | yes: no per-account data, so no adjusted analysis is possible |
| Checklist launch date | not supplied | yes: if it launched after 1 June, some "not completed" accounts never saw it |
| Retention from before the checklist existed | not supplied | yes: this is the comparison the question actually needs |
| Definitions of "active at day 30" and "completed" | not supplied | yes |
| Per-account traits (signup source, plan, early activity) | not supplied | yes: needed to adjust for who chooses to complete |

**COVERAGE**
- Checked:
  - analysis.md: the Finding, Data and Recommendation sections.
  - evidence/cohorts.csv.
  - Claims: "raised 40% to 52%", "+12 points", "cannot be chance", "make mandatory", "other products".
  - Assumptions: comparable groups; everyone was exposed to the checklist; optional and mandatory checklists have the same effect.
- Not checked: per-account data, launch timing and metric definitions, because none were supplied.

**SEATS AND GATE:** Only this local reviewer ran. No subagent or cross-vendor reviewers ran because none were available in this session. Sensitivity gate: passed. The data is aggregate counts with no personal data.

**Arithmetic (recomputed)**
- 624 / 1,200 = 52.0%, and 1,520 / 3,800 = 40.0%. The difference is 12.0 points. Correct.
- Overall: 2,144 / 5,000 = 42.9%.
- Two-proportion test: pooled rate 0.4288, standard error ≈ 0.0164, z ≈ 7.3. The gap is not sampling noise.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | A | analysis.md, "Finding", and the Data note "shown … as an optional panel" | The groups chose themselves. Completing an optional panel is a sign of an already engaged user. The 12-point gap mixes the checklist's effect with who chooses to do it, and the work reports all of it as "the checklist raised retention". | Suppose motivated users are more likely to finish the checklist and also more likely to stay. Then the gap appears even if the checklist does nothing. Making it mandatory would cost every new account about ten minutes and might bring no gain, or even a loss. | Estimate the effect properly: run a randomized holdout (checklist shown vs not shown), or compare all accounts before and after launch. Reproduction: the work's own table cannot tell "the checklist works" apart from "engaged users complete it", because both predict 52% vs 40%. | T/T/T/T |
| F2 | Critical | CONFIRMED | A | Data note: "Completion takes about ten minutes over the first week" | Survival bias built into the groups. A user who leaves in days 1–7 cannot complete the checklist, so they land in "not completed". Early churners are pushed into the comparison group, which lowers its retention automatically. | An account that churns on day 3 counts against "not completed" even if it would have finished the checklist. The 40% is pulled down for reasons that have nothing to do with the checklist. | Measure only accounts still active on day 7, and compare their retention to day 30 by completion status. Or switch to the randomized or all-accounts comparison from F1. Check: count the "not completed" accounts that were inactive before day 7. | T/T/T/T |
| F3 | High | CONFIRMED | A | analysis.md, "raised 30-day retention from 40% to 52%" | The phrasing describes a before-and-after change, but 40% is the non-completers' retention, not retention before the checklist existed. Every account in the data was offered the checklist, so the data cannot answer "did retention improve". | A reader takes 40% as the old baseline. If retention before launch was already about 43% (all accounts now average 42.9%), the real change could be close to zero. | Report overall retention for June–July (42.9%) next to the same measure for cohorts before launch. Rewrite the claim as a gap between groups, not a gain. | T/T/F/T |
| F4 | High | CONFIRMED | A | analysis.md, "Recommendation" | The recommendation goes beyond the evidence. (1) A mandatory checklist is a different intervention from an optional one: it adds friction at first login for users who skip it today. (2) Copying the checklist to two other products assumes the effect carries over, and nothing supports that. | Making it mandatory could raise early drop-off among the 76% who don't complete it now. The cost then repeats across three products, with no measurement planned. | Test a mandatory version against the optional one on a share of new accounts before rolling out. Decide on the other products separately, each with its own test. | T/T/F/T |
| F5 | Low | CONFIRMED | A | "it cannot be chance" | The statement is correct (z ≈ 7.3), but the work gives no test, and statistical significance says nothing about the bias in F1 and F2. It reads as if it settles the causal question. | A reader takes "not chance" to mean "caused by the checklist". | Show the test, and state that it rules out noise only, not bias. | T/T/F/F |

### NEEDS VALIDATION
- **S1, launch date.** Was the checklist live on 1 June 2026? If it launched later, accounts created before launch fall into "not completed" without ever seeing it. Settled by: the checklist's release date.
- **S2, metric definitions.** What counts as "active at day 30", and does a partly finished checklist count as "completed"? Settled by: the metric definitions.
- **S3, complete follow-up.** Did every account get a full 30 days of follow-up? July 31 signups reach day 30 on 30 Aug, so this is probably fine. Settled by: the date the data was extracted.

### REFUTED
- **"The 12-point gap could just be noise."** Refuted: z ≈ 7.3 with these counts.
- **"The percentages are miscalculated."** Refuted: recomputed above, and context.md confirms the arithmetic.

### WHAT HOLDS UP
- The counts, percentages and the 12-point difference are arithmetically correct.
- The gap is statistically real.
- The question is appropriate, and the data covers the full requested period, June and July.

### UNVERIFIED CLAIMS
- "Shown to every new account on first login." Confirm from the release or feature-flag records.
- "Takes about ten minutes." Confirm from product analytics.

### QUESTIONS FOR THE AUTHOR
1. What was 30-day retention for accounts created before the checklist launched?
2. When exactly did the checklist go live?
3. Is per-account data available, so accounts can be filtered to those still active on day 7, or engagement in the first days can be controlled for?
4. Can a holdout group be run?

### DECISION-MAKER SUMMARY
The 52% vs 40% gap is real but compares self-selected groups, and early churners are pushed into the lower group. It doesn't show the checklist caused higher retention (F1, F2, F3). Don't make the checklist mandatory or build it for the other products yet. First compare against retention before launch, or run a short randomized holdout. Proceeding now risks adding friction for every new account across three products with no proven benefit.

### OWNER SUMMARY
The people who finished the checklist stayed longer, but they may simply be the more committed users, and people who left in the first week never had a chance to finish it. So we can't yet tell whether the checklist itself helps. Before making it required or copying it to other products, we should run a fair test that shows it to some new accounts and not others.

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
    {"item": "pre-launch retention baseline", "status": "not_seen", "matters": true},
    {"item": "checklist launch date", "status": "not_seen", "matters": true},
    {"item": "metric definitions (active at day 30, completed)", "status": "not_seen", "matters": true},
    {"item": "account-level covariates", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-reviewer-no-tools", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Aggregate counts only; no personal data."},
  "coverage": {
    "checked": [
      {"unit": "analysis.md", "kind": "file"},
      {"unit": "evidence/cohorts.csv", "kind": "data"},
      {"unit": "analysis.md#Finding", "kind": "section"},
      {"unit": "analysis.md#Data", "kind": "section"},
      {"unit": "analysis.md#Recommendation", "kind": "section"},
      {"unit": "retention raised from 40% to 52%", "kind": "claim"},
      {"unit": "it cannot be chance", "kind": "claim"},
      {"unit": "groups are comparable", "kind": "assumption"},
      {"unit": "mandatory has the same effect as optional", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "pre-launch retention baseline", "reason": "not supplied"},
      {"unit": "account-level data", "reason": "not supplied"},
      {"unit": "metric definitions", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "A",
     "location": "analysis.md: Finding; Data note 'shown ... as an optional panel'",
     "scenario": "Completion of an optional checklist marks already-engaged users; a 12-point gap appears even if the checklist has no effect, and making it mandatory adds friction for every new account with no gain.",
     "fix": "Estimate the causal effect with a randomized holdout or an all-accounts before/after comparison instead of completers vs non-completers.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Both 'checklist works' and 'engaged users self-select' predict 52% vs 40% on the supplied table; the design cannot distinguish them."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "A",
     "location": "analysis.md: Data note 'Completion takes about ten minutes over the first week'",
     "scenario": "Accounts that churn in days 1-7 cannot complete and are counted as not_completed, mechanically lowering that group's day-30 retention.",
     "fix": "Day-7 landmark analysis (only accounts active at day 7, split by completion), or the intent-to-treat comparison.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Count not_completed accounts inactive before day 7; that share explains part of the gap."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "analysis.md: 'raised 30-day retention from 40% to 52%'",
     "scenario": "Readers take 40% as the pre-checklist baseline; overall retention is 2144/5000 = 42.9%, which may match pre-launch, so the true change could be near zero.",
     "fix": "Report overall June-July retention against pre-launch cohorts and reword the claim as a between-group gap.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "analysis.md: Recommendation",
     "scenario": "Making the checklist mandatory changes the intervention and adds first-login friction for the 76% who skip it; extending to two other products repeats an unmeasured cost.",
     "fix": "A/B test mandatory vs optional on a share of new accounts; decide on other products separately with their own tests.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
     "location": "analysis.md: 'it cannot be chance'",
     "scenario": "Readers treat statistical significance (z about 7.3, true) as proof of causation, though it does not address selection bias.",
     "fix": "Show the test and state that it rules out noise, not bias.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "A", "location": "analysis.md: Data (1 June to 31 July)",
     "suspicion": "If the checklist launched after 1 June, accounts that never saw it are counted as not_completed.",
     "unresolved_fact": "The checklist's go-live date."},
    {"id": "S2", "status": "needs_validation", "track": "A", "location": "evidence/cohorts.csv: columns",
     "suspicion": "Definitions of 'active_day30' and 'completed' (partial completion) may shift the groups.",
     "unresolved_fact": "The metric definitions used to build the CSV."},
    {"id": "S3", "status": "needs_validation", "track": "A", "location": "analysis.md: Data (accounts to 31 July)",
     "suspicion": "Late-July accounts may lack a full 30-day follow-up.",
     "unresolved_fact": "The data extraction date (must be on or after 30 Aug 2026)."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The 12-point gap is sampling noise.",
     "evidence": "Two-proportion z of about 7.3 (pooled 0.4288, SE about 0.0164)."},
    {"id": "C2", "candidate": "The percentages are miscalculated.",
     "evidence": "624/1200 = 52.0% and 1520/3800 = 40.0%, recomputed; context.md confirms."}
  ]
}
```