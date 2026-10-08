**Review setup:** The work was not produced in this conversation, so this is an independent review with no anchoring risk. No tools were available. The CSV is included inline, so I checked all arithmetic and statistics by hand.

## Pass 1: Reconstruct

The analysis claims the onboarding checklist caused a 12-point gain in 30-day retention (40% to 52%). It recommends making the checklist mandatory for all new accounts and copying it to two other products. For this to hold, three things must be true:

1. Accounts that completed the checklist are comparable to those that did not, apart from the checklist itself.
2. The 40% figure is a valid "without checklist" baseline.
3. Forcing completion would reproduce the retention seen among people who chose to complete it.
4. The effect would transfer to other products.

The data supports none of these.

## Pass 2 and 3: Attack and self-check

VERDICT: **REWORK.** The data compares people who chose to complete an optional checklist against people who didn't. That cannot show the checklist caused anything, so the "mandatory everywhere" recommendation has no support.

CONFIDENCE IN VERDICT: **High.** The design flaw is visible in the analysis's own text ("shown to every new account… as an optional panel"). What limits confidence: no account-level data, no pre-checklist cohort, and no definition of "active at day 30".

### Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | "The checklist is shown to every new account… as an optional panel" vs "raised 30-day retention from 40% to 52%" | Completion is self-selected. Motivated, high-intent users are more likely both to complete an optional checklist and to stay. The 12-point gap mixes any checklist effect with who chooses to do it. | Suppose the checklist has zero causal effect. Engaged users finish it and retain at 52%; less engaged users skip it and retain at 40%. The analysis reports a 12-point "gain" anyway. Mandating it then yields no lift. | Run a randomized test: hold out a random share of new accounts from seeing the panel and compare all exposed vs all held-out accounts (intent-to-treat). At minimum, compare against a pre-launch cohort and adjust for signup source, plan, and early activity. |
| 2 | Critical | CONFIRMED | "Completion takes about ten minutes over the first week" | Immortal-time / reverse-causation bias. To be counted as "completed", an account must stay active long enough to finish over the first week. Accounts that churn in days 1–7 land in "not completed" almost automatically. | A user who leaves on day 2 can never complete, so early churners are pushed into the 3,800 group. This depresses its retention mechanically, even if the checklist does nothing. | Define groups only from behaviour before a fixed landmark (e.g. completed by day 7), then measure retention only among accounts still active at day 7. Or use the randomized design from #1. |
| 3 | High | CONFIRMED | "from 40% to 52%" | Misframed baseline. 40% is not retention before the checklist. It is the non-completers in the same period, all of whom were shown the checklist. The actual June–July retention for everyone is 2,144 / 5,000 = **42.9%**. The analysis never compares that to a pre-checklist period. | A reader assumes overall retention rose 12 points. It may not have moved at all compared with May or earlier. | Report overall retention for June–July against pre-launch cohorts, with seasonality caveats. |
| 4 | High | PROBABLE | Recommendation: "Make the checklist mandatory" | Voluntary completion is a different intervention from forced completion. Even a real effect among people who opt in says nothing about people who would be forced. A mandatory gate adds friction at the most churn-sensitive moment. | The 3,800 accounts (76%) who currently skip it are made to complete it. Some abandon onboarding entirely, and overall retention falls. The change applies to all new accounts, so the downside is broad. | Test the mandatory variant directly in a randomized experiment before rollout, with a guardrail on activation and day-7 retention. |
| 5 | High | CONFIRMED | "build the same panel for the other two products next quarter" | Extrapolation with zero data from those products. | Different products have different onboarding needs. The effort is spent and could hurt retention there, based on an effect not established even in the original product. | Make any cross-product rollout depend on a positive randomized result here, then pilot one product at a time. |
| 6 | Medium | CONFIRMED | Request: "roll it out more widely"; Recommendation: "Make… mandatory" | Drift. The checklist is already shown to every account, so "wider" can only mean mandatory or other products. The analysis jumps to the most aggressive option. It never considers alternatives: keep as is, nudge completion, or shorten it. | Decision-makers get one high-risk option presented as the natural next step. | Lay out the options (status quo, reminders, shortened checklist, mandatory, other products) with the evidence each would need. |
| 7 | Medium | CONFIRMED | "the groups are large… so it cannot be chance" | Statistical significance is real but irrelevant to the main problem. Being confident the gap isn't random says nothing about whether it's causal. Large samples make a biased estimate more precise, not more correct. | Readers take "not chance" to mean "caused by the checklist". | Keep the significance statement, but add explicitly that it does not address selection bias (#1, #2). |
| 8 | Low | UNVERIFIED | "still active at day 30" | "Active" is undefined (login? key action? paid?). The CSV has only aggregates, with no month split or segments. | A loose definition such as "any login" may inflate retention for users who are merely curious. | State the metric definition. Provide account-level data with signup date, completion date, segment, and activity. |

**Most serious problem that could still be missed:** Mix differences between June and July, or across acquisition channels. If completers come mostly from a high-retention channel, the whole gap could be composition. This can't be checked without segment data.

### WHAT HOLDS UP

- **Arithmetic.** 624/1,200 = 52.0% and 1,520/3,800 = 40.0%, both correct. The groups sum to 5,000.
- **"Not chance".** A two-proportion z-test gives pooled p ≈ 0.429, SE ≈ 0.0164, z ≈ 7.3. The gap is far outside random noise.
- **Timing.** The date window is consistent: accounts created by 31 July 2026 have had their full 30 days.
- **Direction.** Completion is plausibly a useful engagement signal, even though it isn't proven to be a cause.

### UNVERIFIED CLAIMS

| Claim | How to confirm |
|---|---|
| "raised" retention (causal) | Randomized holdout test (see #1). |
| ~10 minutes over first week | Distribution of completion times from event logs. |
| Shown to every new account | Exposure logs. Did anyone miss it due to bugs or platform? |
| Benefit transfers to other products | Pilot in one product. |

### QUESTIONS FOR THE AUTHOR

1. What was 30-day retention for accounts created before the checklist launched?
2. Was any group of accounts randomly not shown the checklist?
3. Among accounts still active at day 7, what is retention for completers vs non-completers?
4. How is "active at day 30" defined?

### DECISION-MAKER SUMMARY

The data shows that people who choose to finish the checklist stay longer. It does not show the checklist makes them stay. Part of the gap is built in, because early churners can't finish it. Don't make it mandatory or copy it to other products yet. Run a randomized holdout first; proceeding now risks adding friction for every new account with no proven benefit.

```json
{
  "verdict": "REWORK",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "analysis.md: 'shown to every new account... as an optional panel' / 'raised 30-day retention from 40% to 52%'", "scenario": "Completion is self-selected; high-intent users both complete and retain, producing a 12-point gap even if the checklist has zero causal effect, so mandating it yields no lift.", "fix": "Randomized holdout (intent-to-treat), or at minimum compare to pre-launch cohorts adjusted for signup source, plan and early activity."},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "analysis.md: 'Completion takes about ten minutes over the first week'", "scenario": "Immortal-time bias: accounts churning in days 1-7 cannot complete and fall into the not-completed group, mechanically lowering its retention.", "fix": "Landmark analysis: define completion by day 7 and compare retention only among accounts active at day 7; or randomize."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "analysis.md: 'from 40% to 52%'", "scenario": "40% is non-completers in the same period, not a pre-checklist baseline; overall June-July retention is 2144/5000 = 42.9% and may be unchanged from before launch.", "fix": "Report overall retention vs pre-launch cohorts with seasonality caveats."},
    {"severity": "High", "evidence_level": "PROBABLE", "location": "analysis.md Recommendation: 'Make the checklist mandatory'", "scenario": "Forcing the 76% who skip it adds friction at the most churn-sensitive moment; some abandon onboarding and overall retention falls across all new accounts.", "fix": "Randomized test of the mandatory variant with guardrails on activation and day-7 retention before rollout."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "analysis.md: 'build the same panel for the other two products next quarter'", "scenario": "No data from other products; effort spent and possible retention harm based on an unestablished effect.", "fix": "Make cross-product rollout depend on a positive randomized result; pilot one product at a time."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "request.md 'roll it out more widely' vs analysis.md 'Make... mandatory'", "scenario": "Checklist already shown to all, so analysis jumps to the most aggressive option without considering status quo, nudges, or a shorter checklist.", "fix": "Present an options table with the evidence each option requires."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "analysis.md: 'so it cannot be chance'", "scenario": "True (z about 7.3) but readers equate 'not chance' with 'caused by the checklist'; large samples make a biased estimate more precise, not correct.", "fix": "Keep significance statement but state explicitly it does not address selection or immortal-time bias."},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "location": "analysis.md table: 'still active at day 30'; evidence/cohorts.csv aggregates only", "scenario": "Undefined activity metric (e.g. any login) may inflate retention; no segment or month split prevents checking composition effects.", "fix": "Define the metric; provide account-level data with signup date, completion date, segment and activity."}
  ]
}
```