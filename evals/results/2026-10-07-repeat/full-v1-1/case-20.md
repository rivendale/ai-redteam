# Redteam Review: "The daily ticket hygiene ritual"

**Review setup:** The proposal was not written in this conversation, so I reviewed it directly rather than delegating to a subagent. I had no tools, so all evidence comes from the two supplied files. The context names "Track D (ideas and proposals)", which this skill does not define. I applied Track A (decisions, analysis, recommendations) and covered the context's own questions: is it needed, by whom, what does it ask of people, what is cheaper, and what happens if nobody uses it.

---

**VERDICT: REJECT.** The proposal costs about 15 engineer-hours a week, which directly contradicts the request's "without slowing the team down." It mostly duplicates data the tracker already records, and it has no committed consumer.

**CONFIDENCE IN VERDICT: high.** What limits it:
- I don't know which specific visibility gaps the manager has.
- I accepted the tracker facts in `tracker_fields.md` as stated.
- Neither limit could rescue a 12-field daily double-entry ritual. At most they would justify a much smaller change.

---

## Pass 1: Reconstruct

The proposal says the manager lacks visibility into the state of work. Its fix is that all 9 engineers tag every ticket they touched each day with 12 labels (priority, risk, customer-impact note and 9 unnamed others) and copy the same details into a separate spreadsheet. It estimates the cost at about 20 minutes per person per day. Rollout would be mandatory next sprint, enforced by reminders at stand-up, and success means the sheet is up to date.

For this to be correct, all of the following must be true:
1. The manager's visibility gap cannot be closed with existing tracker data.
2. All 12 fields are needed, and needed daily.
3. The manager will actually use the output.
4. 20 minutes per person per day is accurate and acceptable.
5. A second copy in a spreadsheet adds value over the tracker.

Assumptions 1, 3, 4 and 5 are contradicted by the proposal's own text or by the evidence file.

## Pass 2: Attack

- **Is it needed?** No specific question the manager can't answer today is stated. Per `tracker_fields.md`, status, assignee, last-updated time, linked PRs and priority already exist on every ticket. A saved query ("touched in the last 24 hours, grouped by status") and a weekly spreadsheet export are also available to any user today. The proposal never mentions either.
- **Who needs it?** The only beneficiary is the manager, who "may look at the sheet from time to time." That describes an optional, occasional consumer for a mandatory daily producer workload.
- **What does it ask of people?**
  - 9 × 20 min = 3 h/day, which is 15 h/week, about 30 h per two-week sprint and roughly 690 h/year at about 230 working days.
  - That is about 4% of team capacity, or roughly 0.4 of an engineer.
  - It also adds a public reminder step to stand-up.
- **What is cheaper?**
  - The manager uses the existing saved query.
  - The manager uses the weekly export.
  - Add one or two genuinely missing fields (risk, customer impact) and set them once per ticket, at creation or on change, not daily.
  - A 15-minute weekly sync.
  - First, ask the manager what they cannot see today.
- **What if nobody uses it?** The team pays about 15 h/week indefinitely for nothing. The success measure ("sheet is up to date") would still report success, so nobody would notice.
- **Counter-case:** Existing tracker fields may be poorly maintained, and risk and customer impact are captured nowhere. This is plausible. But it argues for fixing hygiene on existing fields and adding one or two event-driven fields. It does not argue for 12 fields re-entered daily in two places. The proposal does not survive the counter-case.
- **Pre-mortem (one year on, it failed):**
  1. Compliance decayed within weeks and the sheet went stale.
  2. The sheet and the tracker disagreed, and the manager stopped trusting both.
  3. Engineers resented the public stand-up reminders, and labels became copy-paste noise.

---

## FINDINGS

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | proposal.md: "about 20 minutes per person per day", 9 people | The cost contradicts the original request ("without slowing the team down"). | 9 × 20 min = 3 h/day, 15 h/week, roughly 690 h/year: about 0.4 of an engineer spent on reporting. | Reject the daily ritual. Any replacement should cost under ~1 min/person/day or fall on the manager rather than the team. |
| 2 | Critical | CONFIRMED | proposal.md "Benefit" vs tracker_fields.md | The proposal ignores the existing capability. Status, assignee, last-updated, linked PRs, priority, the saved 24h query and the weekly export already exist. | The manager could get daily state-of-work visibility today at zero team cost, yet the team spends 15 h/week recreating it. | The manager trials the saved query and weekly export for 2 weeks and writes down which questions they still can't answer. |
| 3 | High | CONFIRMED | proposal.md: "may look at the sheet from time to time" | There is no committed consumer, and the benefit is vague ("better visibility"). | The sheet is filled daily and read rarely or never. The cost is incurred and the benefit is zero. | Name the decisions the manager will make from the data, and how often. Drop any field that doesn't feed one. |
| 4 | High | CONFIRMED | proposal.md "Success measure" | It measures compliance, not visibility or outcomes. | The sheet is 100% up to date and nobody's understanding improved. The measure still reports success, so the failure is invisible. | Measure manager-side outcomes, e.g. "manager can answer X, Y, Z without asking engineers," or fewer surprise slips. |
| 5 | High | CONFIRMED (duplication) / PROBABLE (drift) | proposal.md: "copies the same details into the shared 'Ticket Health Sheet'" | Double entry creates two sources of truth. Priority is already set at creation and would now be re-entered daily. | Tracker priority and sheet priority diverge after a re-triage, and the manager acts on the wrong one. | Keep a single source in the tracker. If a spreadsheet is wanted, generate it from the existing export. |
| 6 | Medium | PROBABLE | proposal.md: "20 minutes" for 12 labels on every ticket touched | The time estimate is likely low. | An engineer who touches 5 tickets enters about 60 fields twice, with free-text labels. That realistically takes more than 20 minutes, or gets rushed with low-quality entries. | Time-box a 3-day pilot with 2 volunteers and measure actual minutes and data quality. |
| 7 | Medium | CONFIRMED | proposal.md: "9 other labels"; tracker_fields.md: labels are "free text" | The fields are undefined: the 9 are unnamed, and risk and customer impact have no scale. | 9 people use 9 vocabularies ("high", "HIGH", "hi-risk"), so the aggregated view is meaningless. | Define each field, its allowed values, and the question it answers. Use controlled values, not free text. |
| 8 | Medium | CONFIRMED | proposal.md "Rollout" | Mandatory from day one with no pilot, no review date, no exit, and enforcement by public stand-up reminders. | It takes stand-up time, carries morale cost, and has no mechanism to stop the ritual once it proves useless. | Pilot first, set a review date (e.g. after 1 sprint), and define an explicit kill criterion. Handle enforcement privately, if at all. |

## WHAT HOLDS UP

- The underlying goal is legitimate: a manager wanting visibility is reasonable.
- Risk and customer impact are genuinely not among the tracker's recorded fields, so some gap may be real.
- Keeping the data near the ticket tracker is the right instinct. The problem is the daily, manual, duplicated execution.

## UNVERIFIED CLAIMS

- **"About 20 minutes per person per day."** No measurement is given. Confirm by timing a pilot.
- **"Better visibility into the state of work."** No baseline or gap is stated. Confirm by having the manager list the questions they can't answer from the tracker today.
- **Implied: the existing tracker data is insufficient.** Never argued. Confirm with a 2-week trial of the saved query and weekly export.

## QUESTIONS FOR THE AUTHOR

1. What specific question can the manager not answer today using the saved 24h query and the weekly export?
2. What are the "9 other labels," and which manager decision does each one feed?
3. Has the manager committed to a review cadence for this data, and what would they do differently based on it?

## DECISION-MAKER SUMMARY

Do not adopt this proposal. It costs about 15 engineer-hours a week and mostly re-enters data the tracker already holds. Instead, have the manager use the existing saved query and weekly export for two weeks, list what is still missing, and add only those one or two fields to the tracker, set once when they change. If the team adopts the proposal anyway, expect a steady capacity loss, a sheet that drifts from the tracker, and a success metric that hides the fact that nobody is using it.

```json
{
  "verdict": "REJECT",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "proposal.md: 'about 20 minutes per person per day' x 9 engineers",
      "scenario": "9 x 20 min = 3 h/day, 15 h/week, ~690 h/year (~0.4 engineer), contradicting the request's 'without slowing the team down'",
      "fix": "Reject the daily ritual; any replacement must cost the team under ~1 min/person/day or fall on the manager"
    },
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "proposal.md 'Benefit' vs evidence/tracker_fields.md",
      "scenario": "Status, assignee, last-updated, linked PRs, priority, a saved 24h-by-status query and a weekly export already exist; the team spends 15 h/week recreating visibility available today at zero cost",
      "fix": "Manager trials the saved query and weekly export for 2 weeks and lists the questions still unanswered"
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "proposal.md: 'The engineering manager may look at the sheet from time to time'",
      "scenario": "No committed consumer; the sheet is filled daily and rarely read, so cost is incurred with no benefit",
      "fix": "Name the decisions the data feeds and the review cadence; drop fields that feed no decision"
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "proposal.md 'Success measure': 'The sheet is up to date every day'",
      "scenario": "Measures compliance, not visibility; reports success even if nobody uses the sheet, so failure is invisible",
      "fix": "Measure manager-side outcomes, e.g. questions answerable without asking engineers, fewer surprise slips"
    },
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "proposal.md: 'copies the same details into the shared Ticket Health Sheet'; priority already set at ticket creation",
      "scenario": "Tracker and sheet diverge after re-triage; the manager acts on the stale copy",
      "fix": "Single source of truth in the tracker; generate any spreadsheet from the existing export"
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "proposal.md: 12 labels on every ticket touched in '20 minutes'",
      "scenario": "An engineer touching 5 tickets enters ~60 fields twice, exceeding 20 min or producing rushed, low-quality data",
      "fix": "Time a 3-day pilot with 2 volunteers; measure minutes and data quality"
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "proposal.md: '9 other labels' (unnamed); tracker_fields.md: labels are free text",
      "scenario": "9 engineers use inconsistent free-text values, so aggregation is meaningless",
      "fix": "Define each field, its allowed values and the question it answers; use controlled values"
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "proposal.md 'Rollout': mandatory next sprint, reminders in stand-up",
      "scenario": "No pilot, review date or exit; public enforcement costs stand-up time and morale, and a useless ritual persists indefinitely",
      "fix": "Pilot first, set a review date after one sprint with an explicit kill criterion; handle enforcement privately if at all"
    }
  ]
}
```
