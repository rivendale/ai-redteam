# Redteam review: onboarding checklist analysis

**VERDICT: REWORK.** The 12-point gap compares people who chose to finish the checklist with people who did not, so it cannot show that the checklist caused better retention. The recommendation to make it mandatory and copy it to other products rests on that causal claim.

**CONFIDENCE: medium.** The main flaw is structural and visible in the work itself. Confidence is limited because:
- There were no tools, so nothing was run or opened beyond the supplied text.
- No pre-launch baseline or per-account data was supplied.
- No fresh subagent was available. This is a same-session review, though the work was not written in this conversation, so the anchoring risk is lower. Re-run it in a fresh session before a rollout decision.

**INPUTS LEDGER:**

| Item | Status | Matters? |
|---|---|---|
| request.md | seen | – |
| context.md | seen | – |
| analysis.md | seen | – |
| evidence/cohorts.csv | seen; 2 aggregate rows | yes: no dates, no per-account data, no segments |
| Retention for accounts created before the checklist launched | not supplied, and the work does not mention it | yes: this is the comparison that could test the causal claim |
| Checklist launch date, and when "completed" is measured | not supplied | yes: needed to judge the timing bias in finding 2 |
| Any experiment or holdout | none exists; the work says every account sees the panel | yes |

**SEATS AND GATE:**
- Sensitivity gate: passed. The data is aggregate counts with no personal data.
- Seats: a single local reviewer, with no tools. No subagent and no cross-vendor seats were available.

## Pass 1: Reconstruct

The work claims the checklist raised 30-day retention by 12 points, from 40% to 52%. It recommends making the checklist mandatory for all new accounts and building it for two other products.

For that to be right, three things must hold:
1. Completers and non-completers would have retained at the same rate without the checklist (no selection effect).
2. Completion status is not itself determined by early churn.
3. Forcing completion produces the same effect as voluntary completion, and the effect transfers to other products.

All three are unstated. **Tracks:** A (analysis and decision), with D for the expansion to other products.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | A | analysis.md, "Finding" and the table; "shown to every new account … as an optional panel" | Completion is self-selected. Engaged users are more likely both to finish an optional checklist and to still be active at day 30. The comparison measures who completes, not what the checklist does. | The checklist has zero causal effect, but motivated users finish it and retain at 52% anyway. It becomes mandatory for everyone and retention does not move, or falls. | Compare 30-day retention for all accounts created after launch against all accounts created before launch (an intent-to-treat comparison, not split by completion), adjusting for seasonality. Better: a randomized holdout where some new accounts are not shown the panel. | confirmed. Strongest defense: "the checklist drives engagement." That is possible, but these data cannot tell it apart from selection, so the causal claim is unsupported. |
| 2 | High | PROBABLE (mechanism CONFIRMED from the stated design; size unknown) | A | analysis.md: "Completion takes about ten minutes over the first week" | Timing bias. Accounts that churn in days 1–7 have no chance to complete, so they land in "did not complete" automatically. This inflates the gap even if the checklist does nothing. | Many accounts leave on day 2. All of them count as non-completers and inactive, which mechanically lowers the 40%. | Restrict both groups to accounts still active at day 7 (or at the completion cutoff) and compare retention from that point. Or use the intent-to-treat comparison in finding 1. | confirmed. Defense: completion may be possible on day 1. But the stated design spreads it over the first week, and any account that leaves before completing is forced into the control group. |
| 3 | High | CONFIRMED | A | analysis.md: "so it cannot be chance" | The significance argument is correct but answers the wrong question. By my hand calculation, z ≈ 7.3 (pooled rate 42.9%, standard error ≈ 1.64 points), so chance is ruled out. Large samples do not remove bias, though, and the text presents "not chance" as if it meant "caused by the checklist." | A decision-maker reads "cannot be chance" as proof that the checklist works. | Say plainly that the gap is real but not causal. Report a confidence interval for an intent-to-treat or experimental estimate instead. | confirmed. The claim that chance is ruled out holds up; what is wrong is the implied causal reading. |
| 4 | High | PROBABLE | A / D | analysis.md, "Recommendation": "Make the checklist mandatory" | Making the checklist mandatory is a different intervention from the one observed. Forced completion adds friction at first login. Even if voluntary completion helped, forced completion may not, and it may hurt activation for the 76% who skipped it. | Users who would have skipped the panel now hit a 10-minute gate and leave in the first week. Retention falls for all new accounts, which is the outcome the context says is at stake. | Before any mandate, test it: randomize mandatory vs. optional vs. no checklist on a fraction of new accounts. Track day-1 to day-7 drop-off as a guardrail. | confirmed. No evidence in the work addresses the effect of a mandate. |
| 5 | Medium | CONFIRMED | D | analysis.md: "build the same panel for the other two products next quarter" | The work extrapolates to other products with no evidence about their users or onboarding. The original request asked about rolling out "more widely," and the panel is already shown to every account, so the work redefined "wider" as a mandate plus other products without saying so. | A quarter of engineering time is committed on the strength of an effect that is unproven even for the original product. | Make expansion conditional on a positive experiment in this product. Ask the requester what "more widely" means, since every account already sees the panel. | n/a (Medium) |
| 6 | Low | CONFIRMED | A | evidence/cohorts.csv | The CSV has no creation dates or other fields, so "accounts created 1 June to 31 July 2026" and the day-30 cutoff cannot be checked from the evidence. | Late-July accounts are measured before day 30, or the date window is mislabeled, and nobody can tell. | Supply per-account data: created date, completion date, last active date. | n/a |

## WHAT HOLDS UP

- **Arithmetic.** 624/1,200 = 52.0% and 1,520/3,800 = 40.0%; the totals are 5,000 accounts and 2,144 retained (42.9%).
- **Statistical significance.** The difference is far from chance (z ≈ 7.3).
- **The question.** The request was the right question to ask, and the data honestly show that completers retain better. That is a useful descriptive fact, and a reasonable starting hypothesis.

## UNVERIFIED CLAIMS

- **The checklist launch date, and that it applied to all June–July accounts.** Settle it with the launch log and the cohort dates.
- **"Completion takes about ten minutes over the first week."** Settle it with the distribution of completion timestamps.
- **The date window and the day-30 measurement.** Settle it with per-account data.

## QUESTIONS FOR THE AUTHOR

1. What was 30-day retention for accounts created in the two months before the checklist launched, and for the same months last year?
2. When can an account complete the checklist, and how many non-completers churned before day 7?
3. Is a randomized holdout feasible for the next month of signups?

## DECISION-MAKER SUMMARY

The 12-point gap reflects who chose to finish the checklist, not proven impact. Making it mandatory and building it for two more products would change onboarding for every new account on unproven evidence. Run a before/after comparison of all accounts now and a small randomized test of the mandatory version before any rollout. If you proceed anyway, you risk adding friction that lowers retention while believing it went up.

## OWNER SUMMARY

People who finished the onboarding checklist stayed longer, but they may simply have been the more committed users to begin with, so we don't yet know whether the checklist itself helped. Forcing everyone through it could even push some new users away. A short controlled test should come before making it mandatory or copying it to other products.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "evidence/cohorts.csv", "status": "seen", "matters": true},
    {"item": "pre-launch retention baseline", "status": "not_seen", "matters": true},
    {"item": "checklist launch date and completion timing", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "aggregate counts only"},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "A", "location": "analysis.md: Finding and table; 'optional panel'", "scenario": "Completion is self-selected; engaged users both complete and retain, so the 12-point gap may be zero causal effect and a mandate would not move retention.", "fix": "Compare all post-launch vs pre-launch accounts (intent-to-treat, seasonality-adjusted) or run a randomized holdout.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "PROBABLE", "track": "A", "location": "analysis.md: 'Completion takes about ten minutes over the first week'", "scenario": "Accounts that churn before they can complete are counted as non-completers, mechanically lowering the 40% (timing bias).", "fix": "Condition both groups on being active at the completion cutoff (e.g. day 7), or use the intent-to-treat comparison.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "A", "location": "analysis.md: 'so it cannot be chance'", "scenario": "Significance (z about 7.3) is presented as proof of effect; large samples do not remove selection bias, misleading the decision-maker.", "fix": "State that the difference is real but not causal; report a causal estimate with a confidence interval.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "PROBABLE", "track": "A", "location": "analysis.md: Recommendation 'Make the checklist mandatory'", "scenario": "A mandatory 10-minute gate is a different intervention; it adds friction for the 76% who skipped it and may lower retention for all new accounts.", "fix": "Randomized test of mandatory vs optional vs none, with day 1-7 drop-off as a guardrail.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "D", "location": "analysis.md: 'build the same panel for the other two products next quarter'", "scenario": "A quarter of work is committed to other products based on an unproven effect in this one; 'more widely' was reinterpreted without saying so.", "fix": "Make expansion conditional on a positive experiment; clarify what 'more widely' means with the requester.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "A", "location": "evidence/cohorts.csv", "scenario": "No dates or per-account fields, so the June-July window and day-30 measurement cannot be checked.", "fix": "Supply per-account created, completed and last-active dates.", "status": "n/a"}
  ]
}
```