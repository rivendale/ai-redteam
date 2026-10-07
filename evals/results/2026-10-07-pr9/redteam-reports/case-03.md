# Redteam review: onboarding checklist analysis

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent and no tools were available, so I reviewed the work myself. Nothing was executed. I recomputed the figures by hand.

**VERDICT: REWORK.** The 12-point gap compares people who chose to finish an optional checklist with people who did not. It does not show that the checklist caused retention, so it cannot justify making the checklist mandatory for every new account.

**CONFIDENCE: high** on the main flaw, because it follows directly from the design the work describes. It is limited by three things: no tools, aggregate-only data, and no pre-launch or holdout data.

**INPUTS LEDGER:**
- **Seen:**
  - request.md
  - context.md
  - analysis.md
  - evidence/cohorts.csv (2 aggregate rows)
- **Not seen, and it matters:**
  - **Pre-launch cohorts or a holdout group.** The causal question cannot be answered without one of these.
  - **Account-level data.** Needed for completion timing, signup channel, plan and company size, which are the obvious confounders.
  - **Definitions** of "completed" and "active at day 30".
  - **The extraction date.**
- **Not seen, and it matters less:**
  - **The date range.** The CSV has no dates, so "1 June to 31 July 2026" cannot be checked.
  - **The other two products.** Their onboarding and user base were not supplied.

**SEATS AND GATE:**
- **Sensitivity:** the data is aggregate counts only, with no personal or confidential data, so the gate passed.
- **Seats that ran:** the local reviewer only.
- **Seats not run:** no cross-vendor seats were requested, and the depth is standard.

## Pass 1: Reconstruct

**What the work claims:** the checklist raised 30-day retention by 12 points (from 40% to 52%).

**What it recommends:**
- Make the checklist mandatory for all new accounts.
- Build the same panel for two other products.

**What must be true for it to be correct:**
1. People who did not complete the checklist are a valid stand-in for "no checklist".
2. Completing the checklist causes retention; it is not just a marker of users who were already going to stay.
3. Forcing the checklist would produce the same effect as choosing to do it.
4. The effect carries over to other products.

The work states none of these assumptions. I attacked the analysis under Track A, with Track D for the expansion to other products.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | A | analysis.md "Finding" and Data paragraph: "optional panel"; "raised 30-day retention" | **Self-selection treated as cause.** Completion is optional, so the two groups are people who chose to engage and people who did not. Motivated, high-intent accounts both finish onboarding tasks and stay. | The checklist has zero causal effect, but engaged users finish it. The gap appears anyway, and the company makes onboarding mandatory for everyone based on an artifact. | Run a randomized holdout: show the panel to a random 50% and compare *all* accounts by assignment (intent-to-treat), not by completion. | confirmed. The strongest defense is "the checklist may genuinely help". That is possible, but this data cannot tell the two explanations apart, so the causal claim stays unsupported. |
| 2 | High | PROBABLE | A | Data paragraph: "Completion takes about ten minutes over the first week" | **Survivorship (immortal-time) bias.** To complete over the first week, an account has to still be active during that week. Accounts that churn on days 1 to 6 land in "not completed" almost automatically. | Early churners drag down the comparison group's day-30 rate. Part of the 12 points is guaranteed by how the groups are defined. | Use a landmark analysis: limit both groups to accounts still active on day 7 (or on the day completion is measured), then compare day-30 retention. Better still, use the randomized design from #1. | confirmed. It is PROBABLE rather than CONFIRMED only because completion timing per account is not supplied. |
| 3 | High | CONFIRMED | A | "raised 30-day retention from 40% to 52%" versus "shown to every new account on first login" | **There is no baseline.** The 40% is the non-completers in the same period, not retention before the checklist. Everyone saw the panel, so nothing in the data represents "without the checklist", and "raised from" is not established. | Overall retention for June and July is 2,144 / 5,000 = 42.9%. That figure could be the same as, or lower than, the pre-launch rate. The real effect could then be zero or negative. | Compare all-account 30-day retention for comparable cohorts before and after launch. Account for seasonality and a mix of acquisition channels, or use the holdout from #1. | confirmed |
| 4 | High | PROBABLE | A, D | Recommendation: "Make the checklist mandatory" | **Optional is not mandatory.** The evidence concerns people who chose a ten-minute task. Forcing that task on unwilling users is a different intervention. It adds friction at first login and could raise early churn among the 76% who did not opt in. | Mandatory rollout lowers activation for low-intent users. Retention falls, and because the change applies to all new accounts, there is no comparison group left to detect the drop. | Test "mandatory" as its own experimental arm against "optional" before any full rollout. Watch first-week drop-off as a guardrail metric. | confirmed. The mechanism is plausible, but the direction of the effect is unknown. |
| 5 | Medium | CONFIRMED | A | "so it cannot be chance" | **The significance claim is unsupported and beside the point.** No test is shown. My recomputation (z ≈ 7.3, below) says chance is indeed very unlikely. But that only rules out sampling noise; it says nothing about the bias in #1 and #2. | Readers take "not chance" to mean "real effect", and the bias goes unchallenged. | State the test and the confidence interval, and say explicitly that significance does not address selection. | n/a |
| 6 | Medium | CONFIRMED | D | Recommendation: "build the same panel for the other two products next quarter" | **The expansion has no evidence behind it.** Nothing is shown about the other products' users, their onboarding, or their retention problems. | A quarter of build effort goes into a feature whose effect is unproven even in the original product. | Hold the expansion until the holdout result from #1 is in, then check whether the other products have the same activation gap. | n/a |
| 7 | Medium | CONFIRMED | A | evidence/cohorts.csv | **The evidence is two aggregate rows.** There are no dates, no definitions and no account-level fields, so confounders cannot be adjusted for and the stated date range cannot be checked. | Even a careful re-analysis is impossible from what was supplied. The conclusion rests on a two-by-two table. | Supply account-level data: signup date, completion timestamp, channel, plan, and the activity definition. | n/a |
| 8 | Low | UNVERIFIED | A | Data heading: "accounts created 1 June to 31 July" | **Some July signups may not have reached day 30**, depending on the extraction date (the 31 July cohort reaches day 30 on 30 August). | If the data was pulled before late August, late-July accounts are misclassified as not active. | State the extraction date and confirm every account had a full 30 days. | n/a |

## Pass 3 checks

- **Arithmetic.** It checks out, as the context said it would:
  - 624 / 1,200 = 52.0%
  - 1,520 / 3,800 = 40.0%
- **Significance recomputation:**
  - Pooled rate: 2,144 / 5,000 = 0.4288
  - Standard error: √(0.4288 × 0.5712 × (1/1,200 + 1/3,800)) ≈ 0.0164
  - z ≈ 0.12 / 0.0164 ≈ 7.3
- **Verdict consistency.** With an open Critical, the verdict cannot be SHIP or SHIP WITH FIXES.
- **Most serious miss still possible:** a confounder in how accounts were acquired. For example, a June–July campaign may have brought in a different mix of customers who differ both in completion and in retention. This would sit in the account-level data, which was not supplied.

## WHAT HOLDS UP

- **The arithmetic** in the table is correct.
- **Sampling noise is not the explanation.** The gap is too large for chance at these group sizes (z ≈ 7.3).
- **The question is worth testing.** A strong link between completion and retention justifies running an experiment.
- **The data fits the stated scope.** The two groups sum to 5,000, consistent with a single two-month cohort.

## UNVERIFIED CLAIMS

- **"Accounts created 1 June to 31 July 2026".** The CSV has no dates. To settle it, provide signup dates.
- **"Completion takes about ten minutes over the first week".** No timing data was supplied. To settle it, provide completion timestamps.
- **The definition of "still active at day 30".** It is not stated. To settle it, provide the metric definition.
- **That the checklist "raised" retention.** This needs a pre-launch baseline or a randomized holdout.

## QUESTIONS FOR THE AUTHOR

1. What was 30-day retention, across all accounts, for cohorts that signed up before the checklist launched?
2. On which day did completers typically finish? What is the day-30 gap among accounts that were still active on day 7?
3. Is a randomized holdout feasible, given that the panel is already shown to everyone?

## DECISION-MAKER SUMMARY

The 12-point gap compares self-selected completers with everyone else. It does not measure what the checklist does, and the data has no baseline. Before changing onboarding for all new accounts, run a randomized test with three arms: no panel, optional panel and mandatory panel, and measure retention by assignment. If the company rolls out the mandatory version now, it risks adding first-login friction that lowers retention, with no comparison group left to notice the drop.

## OWNER SUMMARY

The people who finished the checklist stayed longer, but they were probably the more committed users to begin with, so we don't yet know whether the checklist itself helped. Making it required for everyone could even push some new users away. A simple controlled test should come first, and only then should we roll it out or copy it to other products.

```json
{
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "analysis.md", "status": "seen", "matters": true},
    {"item": "evidence/cohorts.csv", "status": "seen", "matters": true},
    {"item": "pre-launch cohort retention or randomized holdout", "status": "not_seen", "matters": true},
    {"item": "account-level data (signup date, completion timestamp, channel, plan)", "status": "not_seen", "matters": true},
    {"item": "definitions of 'completed' and 'active at day 30'", "status": "not_seen", "matters": true},
    {"item": "data extraction date", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "aggregate counts only; no personal or confidential data"},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "A", "location": "analysis.md Finding; Data paragraph ('optional panel')", "scenario": "Completion is self-selected; engaged users both complete and retain, so the 12pp gap can exist with zero causal effect, and onboarding is made mandatory for everyone on an artifact.", "fix": "Randomized holdout of the panel; compare retention by assignment (intent-to-treat), not by completion.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "PROBABLE", "track": "A", "location": "analysis.md Data paragraph ('ten minutes over the first week')", "scenario": "Accounts that churn before finishing the week-long checklist are mechanically counted as non-completers, inflating the gap (immortal-time bias).", "fix": "Landmark analysis restricted to accounts active at the completion point (e.g. day 7), or the randomized design.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "A", "location": "analysis.md 'raised 30-day retention from 40% to 52%' vs 'shown to every new account'", "scenario": "40% is same-period non-completers, not a pre-checklist baseline; overall retention is 42.9% and may equal or trail pre-launch, so the true effect could be zero or negative.", "fix": "Compare all-account 30-day retention for pre- vs post-launch cohorts, controlling for seasonality and channel mix, or use a holdout.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "PROBABLE", "track": "A", "location": "analysis.md Recommendation ('Make the checklist mandatory')", "scenario": "Forcing a 10-minute task on the 76% who did not opt in adds first-login friction, may raise early churn, and removes any comparison group to detect it.", "fix": "Test a mandatory arm against optional before rollout, with first-week drop-off as a guardrail metric.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "A", "location": "analysis.md 'so it cannot be chance'", "scenario": "No test shown; recomputed z is about 7.3, so chance is ruled out, but readers equate 'not chance' with 'causal', masking selection bias.", "fix": "Report the test and confidence interval and state that significance does not address selection.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "D", "location": "analysis.md Recommendation ('other two products next quarter')", "scenario": "A quarter of build effort is spent copying an unproven effect to products with no shown need.", "fix": "Defer until the holdout result exists; check whether the other products have the same activation gap.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "A", "location": "evidence/cohorts.csv", "scenario": "Two aggregate rows with no dates, definitions or account fields make confounder adjustment and date verification impossible.", "fix": "Provide account-level data with signup date, completion timestamp, channel, plan and the activity definition.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "track": "A", "location": "analysis.md Data heading ('1 June to 31 July')", "scenario": "If data was extracted before about 30 August, late-July signups had not reached day 30 and are miscounted as inactive.", "fix": "State the extraction date and confirm every account had a full 30-day window.", "status": "n/a"}
  ]
}
```
