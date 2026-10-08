# Redteam review: onboarding checklist analysis

**Review mode:** Same-context review with no tools and no subagent, so anchoring risk applies. Re-run in a fresh session for anything high-stakes. The work was not written in this conversation, which lowers the anchoring risk somewhat.

**VERDICT: REWORK.** The analysis compares people who chose to complete an optional checklist with people who did not, and reads the gap as the checklist's effect. Nothing in the data separates the checklist's effect from who chooses to finish it, so the data cannot support a rollout to every new account.

**CONFIDENCE: medium-high.** The main flaw follows from the design described in the work itself, not from any detail I couldn't check. What limits confidence:
- I had no tools, so arithmetic was recomputed by hand.
- I had no account-level data.
- This is not an independent seat.

## INPUTS LEDGER

| Item | Status | Matters? |
|---|---|---|
| request.md | Seen | — |
| context.md | Seen | — |
| analysis.md | Seen | — |
| evidence/cohorts.csv (2 aggregate rows) | Seen | — |
| Account-level data: signup date, completion date, churn date, plan, channel, early activity | Not supplied | **Yes.** Needed to test self-selection and early churn. |
| Retention for cohorts from before the checklist launched (e.g. April–May 2026) | Not supplied | **Yes.** It is the only available "without checklist" baseline. |
| Definition of "active at day 30" | Not supplied | Moderate. Activity during the checklist could count as "active". |
| Launch date of the checklist and whether any account was not shown it | Not supplied | **Yes.** The work says every account saw it, so there is no unexposed group. |

## SEATS AND GATE

- **Sensitivity gate:** passed. The data is aggregate counts with no personal data.
- **Seats:** one local same-context reviewer ran. No subagent or cross-vendor seats were available in this session; none were refused.

## Pass 1: Reconstruct

The work claims the checklist raised 30-day retention by 12 points (40% → 52%). It recommends making the checklist mandatory and copying it to two other products.

For this to be correct, three things must hold:
1. Completers and non-completers would have retained equally without the checklist (no self-selection).
2. Completion causes retention, not the reverse.
3. Forcing the checklist on users produces the same effect as users choosing to complete it.

None of these is tested.

**Tracks:** A (analysis and decision) and D (rollout proposal).

**Arithmetic check:**
- 624/1200 = 52.0% and 1520/3800 = 40.0%. Both correct, as the context states.
- Overall retention across both groups is 2144/5000 = 42.9%.
- A two-proportion test gives z ≈ 7.3 (pooled p = 0.429, SE ≈ 0.0164). The gap is not chance, but that only rules out chance, not confounding.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | High | CONFIRMED (by the work's own design description) | A | analysis.md, "Finding" and the sentence "shown to every new account … as an optional panel" | Completion is self-selected, yet the gap between groups is reported as the checklist's causal effect ("raised retention"). Motivated, high-intent users are the ones who spend ten minutes on an optional panel, and they would retain better anyway. This answers "do completers retain better?" rather than the question asked, "did the checklist improve retention?", which is drift from the request. | The checklist is made mandatory. Retention for all new accounts stays near about 43%, or drops. Engineering time is spent on two more products. The 12 points was the motivation gap, not the checklist. | Randomized holdout: hide the checklist (or keep it optional vs. make it mandatory) for a random share of new accounts and compare 30-day retention by assigned group. Until that exists, adjust for pre-completion signals such as day-1 activity, plan and acquisition channel. | Confirmed. Strongest defence: "the gap is big and significant." But significance does not address selection, so the defence fails. |
| 2 | High | PROBABLE | A | analysis.md, "Completion takes about ten minutes over the first week"; cohorts.csv `not_completed` row | Survivorship / immortal-time bias. Anyone who churns in the first days cannot complete a checklist that runs over the first week, so early churners are counted automatically as non-completers. The comparison builds in a retention gap even if the checklist does nothing. | The 40% group is inflated with users who left before they could finish. Part or all of the 12 points is created by how the groups were defined. | Use account-level dates and restrict both groups to accounts still active at day 7. Or define the groups as "completed by day N" and measure retention from day N onward. | Confirmed as a mechanism. Its size is unknown without the dates. |
| 3 | High | CONFIRMED | A | analysis.md, "from 40% to 52%" | The 40% is not a "before" figure. It is the non-completer group in the same period. No pre-launch baseline is shown, and because every account saw the checklist, there is no unexposed group at all. | Readers believe retention rose 12 points. True overall retention for June–July is 42.9%. Whether that number moved at all after launch is unknown. | Compare overall 30-day retention for cohorts before launch with June–July cohorts, and check for seasonality, pricing or channel changes in that window. | Confirmed. The only defence would be that "40%" meant non-completers, and the text says "raised … from 40%", which contradicts it. |
| 4 | Medium | PROBABLE | D | analysis.md, "Recommendation: make the checklist mandatory" | Even if completing the checklist voluntarily helps, forcing it is a different intervention. Mandatory steps add friction at first login, when drop-off is highest. | Forced users rush through or abandon onboarding, and activation falls for the very users the change is meant to help. | Test mandatory vs. optional as separate arms in the randomized holdout from Finding 1 before any rollout. | — |
| 5 | Medium | PROBABLE | D | analysis.md, "build the same panel for the other two products next quarter" | The result is extended to products with different users and onboarding, without evidence from those products and before the effect is established in this one. | A quarter of build effort goes on an unproven pattern in two products. | Make the expansion depend on a positive randomized result here, then run a small pilot in one other product. | — |
| 6 | Low | CONFIRMED | A | analysis.md, "so it cannot be chance" | The claim is true (z ≈ 7.3), but no test is shown. Presenting it as the reason to trust the result implies that significance establishes causation. | A reader takes "not chance" to mean "caused by the checklist." | Show the test and its interval, and state that it rules out chance only, not confounding. | — |
| 7 | Low | UNVERIFIED | A | analysis.md, data table header "still active at day 30" | "Active" is not defined. If completing checklist steps counts as activity, completers are partly measured as active by the checklist itself. | Some of the gap reflects how activity is measured, not real retention. | State the definition, and exclude checklist interactions from the activity signal. | — |

## WHAT HOLDS UP

- The percentages and totals reproduce from the CSV.
- The gap between the two groups is real and not chance.
- The date window (1 June to 31 July 2026) allows a full 30-day follow-up for every account before today.
- The work states the design honestly ("optional panel", "over the first week"), which is what makes Findings 1 and 2 visible.

## UNVERIFIED CLAIMS

- **"The checklist raised retention."** Settle with a randomized holdout, or failing that, a pre/post comparison plus day-7-conditioned groups.
- **That mandatory roll-out reproduces the effect.** Settle with a mandatory arm in the experiment.
- **That other products would benefit.** Settle with a pilot in one product.
- **How "active" is defined.** Settle by quoting the metric definition.

## QUESTIONS FOR THE AUTHOR

1. What was overall 30-day retention for cohorts before the checklist launched?
2. Restricted to accounts still active at day 7, what are completer and non-completer retention?
3. Can a random holdout be run for 4–6 weeks before deciding?

## DECISION-MAKER SUMMARY

The 12-point gap compares users who chose to finish an optional checklist with those who did not. That mostly measures who those users are and who churned early, not what the checklist does. Do not make the checklist mandatory or build it elsewhere yet. Run a short randomized holdout, including a mandatory arm, first. Proceeding anyway risks adding friction to every new account and a quarter of build work for an effect that may be near zero.

## OWNER SUMMARY

The users who finished the onboarding checklist stayed longer, but they may simply be the more committed users, and people who left in the first week never had the chance to finish it. So we don't yet know whether the checklist itself helps. A short fair test, where some new users get the checklist and others don't, would answer this before we make it compulsory for everyone.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "account-level cohort data (signup, completion, churn dates)", "status": "not_seen", "matters": true},
    {"item": "pre-launch cohort retention baseline", "status": "not_seen", "matters": true},
    {"item": "definition of active at day 30", "status": "not_seen", "matters": true},
    {"item": "evidence/cohorts.csv", "status": "seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "aggregate counts only"},
  "findings": [
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "A", "location": "analysis.md: Finding; 'shown to every new account ... as an optional panel'",
      "scenario": "Completion is self-selected; motivated users both complete and retain, so the 12-point gap is reported as causal when it may be selection; mandatory rollout yields no gain.",
      "fix": "Randomized holdout comparing retention by assigned group; meanwhile adjust for pre-completion covariates.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "PROBABLE", "track": "A", "location": "analysis.md: 'Completion takes about ten minutes over the first week'; cohorts.csv not_completed row",
      "scenario": "Users who churn in the first week cannot complete and are automatically non-completers, mechanically lowering that group's retention (immortal-time bias).",
      "fix": "Condition both groups on being active at day 7, or measure retention from the completion cutoff onward.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "A", "location": "analysis.md: 'raised 30-day retention from 40% to 52%'",
      "scenario": "40% is the concurrent non-completer group, not a pre-checklist baseline; overall retention is 42.9% and no before/after comparison exists, so readers believe retention rose 12 points.",
      "fix": "Report pre-launch vs post-launch overall 30-day retention, controlling for seasonality and channel mix.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "D", "location": "analysis.md: Recommendation 'Make the checklist mandatory'",
      "scenario": "Forcing a ten-minute checklist at first login adds friction; voluntary-completion effect does not transfer and activation drops.",
      "fix": "Include a mandatory-vs-optional arm in the experiment before rollout."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "D", "location": "analysis.md: 'build the same panel for the other two products next quarter'",
      "scenario": "Unproven effect extrapolated to products with different users; a quarter of build effort wasted.",
      "fix": "Gate expansion on a positive randomized result here, then pilot one product."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "A", "location": "analysis.md: 'so it cannot be chance'",
      "scenario": "Claim is true (z about 7.3) but untested in the text and implies significance proves causation.",
      "fix": "Show the test and interval; state it rules out chance only, not confounding."},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "track": "A", "location": "analysis.md table header 'still active at day 30'",
      "scenario": "If checklist interactions count as activity, completers are partly measured as active by the treatment itself.",
      "fix": "State the activity definition and exclude checklist interactions."}
  ]
}
```