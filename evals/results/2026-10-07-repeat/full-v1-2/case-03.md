# Redteam Report: Onboarding Checklist Retention Analysis

**Review mode:** This is a same-context review, but the work was not produced in this conversation, so the author's reasoning isn't shared. I had no tools in this session, so I could not open `evidence/cohorts.csv` independently. I reviewed it as reproduced in the inputs and did the arithmetic by hand.

**VERDICT: REWORK.** The analysis compares people who chose to complete the checklist with people who didn't. That cannot show the checklist *caused* higher retention, and the recommendations go well past what the data supports.

**CONFIDENCE IN VERDICT: High.** The main flaw is structural and visible in the work's own description of the data. Confidence is limited only by having aggregate counts rather than account-level data, so I can't measure how large the bias is.

## Pass 1: Reconstruct

The work claims the checklist raised 30-day retention by 12 points, from 40% to 52%. It recommends making the checklist mandatory and copying it to two other products. For that to be correct, all of the following must hold:

- (a) Completers and non-completers would have retained equally without the checklist.
- (b) Assignment to a group did not depend on outcomes that happened after signup.
- (c) Forcing completion produces the same effect as completing voluntarily.
- (d) The effect transfers to other products.

None of these is stated, and none is tested.

## Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | "shown to every new account… as an optional panel"; Finding paragraph | Self-selection. The groups are defined by a choice users made. Engaged, motivated users are more likely both to finish an optional checklist and to stay. The 12 points measures a correlation, not the checklist's effect. | Completers would have retained at 52% even without the checklist. Rollout spends effort and the true lift is about zero. | Run a randomized holdout (show the panel to a random 50%) and compare by *assigned* arm. At minimum, compare all accounts before and after launch. |
| 2 | Critical | CONFIRMED (mechanism) / PROBABLE (magnitude) | "Completion takes about ten minutes over the first week" | Immortal-time / survivorship bias. Users who churn on days 1–7 never get the chance to complete, so they land in "not completed" automatically. That inflates the gap even if the checklist does nothing. | A user who leaves on day 2 counts against "not completed" by construction. The "completed" group is partly defined by having already survived the first week. | Restrict both groups to accounts still active at day 7, or classify users by completion status as of a fixed early landmark. Then recompute. |
| 3 | High | CONFIRMED | Recommendation: "Make the checklist mandatory" | The evidence comes from voluntary completers. Forcing completion changes who completes, and it adds friction. That friction could *lower* retention for users who would have skipped it. | Mandatory gating annoys low-intent users at first login. Week-1 churn rises across all new accounts, which is the stated stakes. | Test "mandatory" as its own arm in an A/B test before changing onboarding for everyone. |
| 4 | High | CONFIRMED | "add similar checklists to the other products… next quarter" | The work extrapolates to two other products with zero evidence from them. | Different user bases or activation paths mean no effect, or a negative one, plus a quarter of build cost. | Defer until a causal effect is shown here. Then pilot with a holdout in one other product. |
| 5 | Medium | CONFIRMED | "so it cannot be chance" | The conclusion is right but the reasoning is wrong. My hand calculation gives a two-proportion z ≈ 7.3 (pooled p = 2144/5000 = 0.429, SE ≈ 0.0164), so chance is indeed very unlikely. But "large groups" is not a test, and ruling out chance does nothing about bias, which is the real problem. | Readers take "not chance" to mean "causal." | Report the test and confidence interval (≈ 12 pts ± 3.2). State plainly that significance does not address confounding. |
| 6 | Medium | CONFIRMED | Data section; cohorts.csv | No pre-launch baseline. If the panel is shown to everyone, the natural question is whether overall retention moved after launch. Blended June–July retention is 2144/5000 = 42.9%, and nothing compares it with earlier cohorts. | If pre-launch retention was also around 43%, the checklist added nothing at the population level. | Compare cohorts from before launch with June–July, controlling for seasonality and acquisition mix. |
| 7 | Medium | CONFIRMED | cohorts.csv has 2 rows | The analysis uses aggregates only. There is no split by month, channel, plan, or segment, so mix effects and Simpson's paradox can't be ruled out. "Active at day 30" and "completed" (fully or partially?) are not defined. | Paid-plan or sales-led accounts complete more and retain more. Within each segment the gap disappears. | Use account-level data. Stratify or regress on acquisition channel, plan, and signup month. Write down the metric definitions. |
| 8 | Low | PROBABLE | Whole document | Alternatives were never considered: keeping it optional, improving it, nudging people to complete it, or doing nothing while a test runs. | The team skips a cheap experiment and goes straight to a forced rollout. | Add an options section that includes "run a 4-week randomized test first." |

## What holds up

- The arithmetic is correct: 624/1200 = 52%, 1520/3800 = 40%, and the gap is 12 points.
- The observed gap is very unlikely to be sampling noise.
- The 30-day window is fully observable, since the last cohort ended 31 July and today is 7 October.
- The checklist may well help. The data is simply unable to show it.

## Unverified claims

- **"Shown to every new account."** I can't confirm full exposure; any eligibility rules would bias the groups further. Check the feature-flag or exposure logs.
- **"About ten minutes over the first week."** No source is given. Check the completion-time distribution.
- **CSV contents.** I could not open the file myself. Confirm the totals and that it covers 1 June to 31 July only.
- **"The checklist raised retention."** This is a causal claim that the observational split can't establish. Only a randomized holdout or a credible quasi-experiment would confirm it.

## Questions for the author

1. What was 30-day retention for cohorts from before the checklist launched?
2. Of the "not completed" accounts, how many churned before day 7? What is the gap once both groups are restricted to accounts active at day 7?
3. Is a randomized holdout of the panel feasible for 4–6 weeks?

## Decision-maker summary

Don't make the checklist mandatory or build it for other products yet. The 12-point gap is mostly explained by who chooses to complete it and by early churners being counted as non-completers. Run a randomized holdout first. If you go ahead anyway, the risk is that you add friction to onboarding for every new account, which could reduce retention, and spend a quarter of build effort with no demonstrated benefit.

```json
{
  "verdict": "REWORK",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "analysis.md: 'optional panel' / Finding paragraph", "scenario": "Groups are self-selected; motivated users both complete the checklist and retain, so the 12-point gap reflects user type, not checklist effect; rollout yields ~0 true lift.", "fix": "Randomized holdout of panel exposure, analyzed by assigned arm; at minimum a pre/post launch comparison of all accounts."},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "analysis.md: 'Completion takes about ten minutes over the first week'", "scenario": "Users who churn in days 1-7 cannot complete and are counted as not_completed by construction (immortal-time/survivorship bias), inflating the gap even with zero effect.", "fix": "Restrict both groups to accounts active at day 7 (landmark analysis) and recompute retention."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "analysis.md Recommendation: 'Make the checklist mandatory'", "scenario": "Effect estimated from voluntary completers does not transfer to forced completion; added friction raises early churn for all new accounts.", "fix": "Test mandatory checklist as a separate A/B arm before global rollout."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "analysis.md: 'build the same panel for the other two products next quarter'", "scenario": "No data from other products; different users/activation paths give no or negative effect after a quarter of build cost.", "fix": "Defer until a causal effect is shown; pilot with holdout in one product."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "analysis.md: 'so it cannot be chance'", "scenario": "Statistical significance (z~7.3 by hand) is mistaken for causal proof; it does not address confounding.", "fix": "Report test and CI (~12 +/- 3.2 pts) and state explicitly that significance does not rule out bias."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "analysis.md Data section", "scenario": "No pre-launch baseline; if pre-launch retention was ~43% (blended June-July), the checklist added nothing population-wide.", "fix": "Compare pre-launch cohorts with June-July cohorts, adjusting for seasonality and acquisition mix."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "evidence/cohorts.csv (two aggregate rows)", "scenario": "Segment mix (channel, plan, month) could produce the gap via Simpson's paradox; 'completed' and 'active' are undefined.", "fix": "Account-level data with stratification or regression on channel, plan, signup month; document metric definitions."},
    {"severity": "Low", "evidence_level": "PROBABLE", "location": "analysis.md (whole)", "scenario": "No alternatives considered (keep optional, nudge, run test first), so a cheap experiment is skipped in favor of forced rollout.", "fix": "Add an options section including a time-boxed randomized test."}
  ]
}
```