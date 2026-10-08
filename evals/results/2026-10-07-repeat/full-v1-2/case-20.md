# Redteam review: "The daily ticket hygiene ritual"

**Review setup:** I did not author this work, so the review is independent. I had no tools in this session, so every finding rests on the text of `proposal.md` and `evidence/tracker_fields.md`. The context asks for "Track D (ideas and proposals)", which this skill does not define. I applied Track A (decisions, analysis, recommendations) and covered the context's specific questions: is it needed, by whom, what does it ask of people, what is cheaper, and what happens if nobody uses it.

---

**VERDICT: REJECT.** By its own numbers, the proposal costs the team about 15 person-hours a week, which fails the request's one hard constraint ("without slowing the team down"). It mostly duplicates data the tracker already records, and it names no committed user of its output.

**CONFIDENCE IN VERDICT: high.** The decisive findings are arithmetic on the proposal's own figures and a direct comparison with the tracker evidence file. The main limit is that I could not see the manager's actual unmet questions, the real ticket volume, or how well the tracker data is kept today.

## Pass 1: Reconstruct

The proposal says the manager lacks visibility into the state of work. Its fix is a mandatory daily ritual. Each of 9 engineers would tag every ticket they touched with a priority, a risk level, a customer-impact note and 9 more labels, then copy the same details into a separate spreadsheet. For it to be correct, all of these must be true:

1. The manager's visibility gap is caused by missing data, not by nobody looking at existing data.
2. The new fields answer questions the manager actually has.
3. About 20 min/person/day is an acceptable cost.
4. A second copy in a spreadsheet adds value over the tracker.
5. The manager will actually use the sheet.

Assumption 3 contradicts the request outright. Assumptions 1, 4 and 5 are undermined by the evidence file and by the proposal's own wording.

## Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | proposal.md: "about **20 minutes per person per day**", "every engineer (9 people)"; request: "without slowing the team down" | The proposal fails the request's explicit constraint. 20 min × 9 = 3 person-hours/day, 15 h/week, 30 h per two-week sprint. That is roughly 0.4 FTE taken out of delivery. | It is adopted as written, and the team loses about 0.4 of an engineer's capacity every week, indefinitely. That is exactly the slowdown the request ruled out. | Make cost a hard design limit, for example under 2 min/person/day or zero added daily work. Any proposal must state its total team-hours per week next to the constraint. |
| 2 | High | CONFIRMED | proposal.md "tags … with a priority … and copies the same details into the shared 'Ticket Health Sheet'" vs tracker_fields.md "priority field the team already fills in when a ticket is created", "saved query … and a weekly export … available to any user today" | The proposal duplicates existing data and existing views. Priority is already recorded. Status, assignee, last-updated time and linked PRs are recorded automatically. A daily "touched in last 24h, grouped by status" view and a weekly spreadsheet export already exist. The proposal never mentions any of this or explains why it is not enough. | The manager could get most of the stated visibility today, at zero engineer cost, by opening the saved query. The ritual pays 15 h/week for data that is largely already available. | Do-nothing-new baseline first. The manager uses the saved query and weekly export for 2 weeks and writes down which specific questions they still cannot answer. Only those gaps justify new fields. |
| 3 | High | CONFIRMED | proposal.md Benefit: "The engineering manager may look at the sheet from time to time." | No committed consumer and no defined questions. The only beneficiary is named with "may … from time to time". Nothing says what decisions the sheet would inform. This answers the context's "what happens if nobody uses it": all of the cost remains and none of the benefit arrives. | The manager checks the sheet occasionally or never. Engineers still spend 15 h/week filling it. Nobody notices because the success measure (finding 4) still reports success. | State the 2–3 concrete questions the manager needs answered, for example "which tickets are blocked more than 3 days" or "which in-flight items carry customer risk", and who acts on the answers and when. Design only for those questions. |
| 4 | High | CONFIRMED | proposal.md Success measure: "The sheet is up to date every day." | The success measure counts compliance, not visibility or decisions. The proposal can "succeed" while delivering no value at all (Goodhart). | The sheet is filled in perfectly every day while the manager's view of risk or delays does not improve, and no review ever triggers because the metric is green. | Measure the outcome instead. For example: the manager can answer the defined questions in under 5 minutes, or surprises found at sprint review go down. Also track the cost in team-hours and set a review date. |
| 5 | Medium | PROBABLE | proposal.md "copies the same details into the shared … Sheet" | Two manually synced sources of truth. Tickets change after the copy is made, and copying by hand introduces errors. Nothing says which source wins when they disagree. | A ticket is re-prioritized or closed in the tracker after 5pm, and the sheet shows stale state the next morning. The manager acts on the sheet, which is the less accurate source. | Drop the sheet. If a spreadsheet view is needed, generate it from the tracker (the export or query already exists). |
| 6 | Medium | CONFIRMED (labels are free text) / PROBABLE (resulting inconsistency) | proposal.md "a risk level, a customer-impact note and 9 other labels"; tracker_fields.md "labels (free text)" | The 9 labels are never named or defined, and the tracker's labels are free text. Nine people tagging by hand with no fixed vocabulary will produce inconsistent values. | One engineer writes "risk-high", another writes "High risk", and the data cannot be grouped or queried, so the visibility goal fails even with full compliance. | Name every proposed field and justify each one against a manager question. Use a fixed set of values or tracker custom fields, not free-text labels. Expect most of the 9 to be cut. |
| 7 | Medium | CONFIRMED | proposal.md "tags every ticket they touched that day with a priority" vs tracker_fields.md priority "fills in when a ticket is created" | Daily re-tagging of priority by whoever touched the ticket conflicts with the existing priority field. Ownership of priority becomes unclear. | Two engineers touch the same ticket on the same day and assign different priorities. The field becomes noise, or it overwrites a priority set deliberately at creation. | Keep priority as it is today. If it goes stale, assign one owner, such as the manager or tech lead at triage, rather than 9 daily editors. |
| 8 | Medium | PROBABLE | proposal.md Rollout: "Mandatory from the start of the next sprint. Engineers who skip a day are reminded in the stand-up." | No pilot, no review date and no exit criteria. Enforcement relies on public reminders in stand-up, which costs stand-up time and morale and teaches the team that status reporting is surveillance. | Compliance slips by week 3, stand-ups turn into compliance checks, and the ritual continues on inertia because no review point exists. | Pilot any change with 2–3 volunteers for one sprint, with a set review date and kill criteria. Handle misses privately or through automation, not in stand-up. |
| 9 | Medium | PROBABLE | proposal.md "every ticket they touched that day" | The cost grows with activity, which creates a perverse incentive. The more tickets someone touches, the more admin they owe. "Touched" is also undefined: does commenting count? | Engineers postpone small ticket updates or batch them, so the tracker, which is the real source of truth, gets less current. That is the opposite of the goal. | Do not tie admin cost to ticket activity. Capture the extra fields once, at creation or at a status change into "blocked" or "at risk". |
| 10 | Medium | UNVERIFIED | proposal.md "It takes about **20 minutes**" | The time estimate has no source. With 12 fields per ticket plus manual copying, and several tickets touched per day, 20 minutes may be an underestimate. | One engineer touches 6 tickets with 12 fields each, entered twice (tracker and sheet), which is 144 entries. The real cost could be well over 20 minutes, making finding 1 worse. | Time-box a 2-day trial with 2 engineers and measure actual minutes against the number of tickets touched. |

## What holds up

- **The problem may be real.** A manager wanting visibility is a legitimate need, and the tracker does not record risk level or customer impact (tracker_fields.md lists neither). A small, targeted addition for those two dimensions could be justified.
- **The strongest counter-case partly survives.** Someone could argue the tracker data is stale or untrusted, so a deliberate daily touchpoint forces it to be current. That is plausible, but it supports a lighter fix: keep status current in the tracker, perhaps with a 2-minute end-of-day check of one's own tickets. It does not support 12 fields plus a duplicate spreadsheet. The proposal itself offers no evidence that the tracker data is stale.

## Pre-mortem: one year later, it failed because

1. Compliance faded within a few sprints, the sheet went stale, and the manager stopped trusting it while it was still officially mandatory.
2. The manager rarely looked at it, so the team paid about 700+ person-hours in a year (15 h/week × ~48 weeks) for nothing.
3. The tracker and the sheet diverged, and a decision was made from the wrong one.

## Unverified claims

- "About 20 minutes per person per day." Confirm by timing a short trial against tickets touched.
- "Better visibility into the state of work." No mechanism or questions are given. Confirm by listing the manager's questions and checking whether the existing saved query already answers them.
- Implied claim that the current tracker data is not enough. Confirm by having the manager use the saved query and weekly export for 2 weeks and record the gaps.
- Implied claim that the team will keep this up. Confirm with a pilot that measures compliance over time.

## Questions for the author

1. What specific questions can the manager not answer today, and have they tried the existing "touched in last 24h by status" query and the weekly export?
2. Which of the 12 fields map to one of those questions? Name all 9 unnamed labels.
3. Who acts on the sheet, how often, and what decisions does it change?
4. Why a separate sheet instead of tracker fields or the existing export?

## Decision-maker summary

Do not adopt this. It costs about 15 engineer-hours a week, contradicts "without slowing the team down", and mostly duplicates what the tracker and its saved query already provide. Next, have the manager use the existing saved query and weekly export for two weeks, list the questions that remain unanswered, and then add only the 1–2 fields those gaps require (likely risk and customer impact), filled in once per ticket rather than daily. If the team proceeds anyway, expect fading compliance, a stale duplicate sheet and a success metric that hides the failure.

```json
{
  "verdict": "REJECT",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "proposal.md: '20 minutes per person per day', 'every engineer (9 people)'; request: 'without slowing the team down'",
      "scenario": "Adopted as written, the team loses 3 person-hours/day (15 h/week, ~0.4 FTE) of delivery capacity indefinitely, which is exactly the slowdown the request forbids.",
      "fix": "Set cost as a hard limit (e.g. under 2 min/person/day or zero added daily work) and require total team-hours/week to be stated next to the constraint."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "proposal.md 'tags ... with a priority ... and copies the same details into the shared Ticket Health Sheet' vs tracker_fields.md (priority set at creation; status, assignee, last-updated, linked PRs automatic; saved 24h query and weekly export exist)",
      "scenario": "The manager could get most of the stated visibility today at zero engineer cost from the saved query; the ritual spends 15 h/week duplicating it.",
      "fix": "Baseline first: manager uses the saved query and weekly export for 2 weeks and lists unanswered questions; only those gaps justify new fields."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "proposal.md Benefit: 'The engineering manager may look at the sheet from time to time.'",
      "scenario": "The manager rarely or never opens the sheet; the full cost is paid with no benefit, and nobody notices because the success metric stays green.",
      "fix": "Define the 2-3 concrete questions the manager needs answered and who acts on them and when; design only for those."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "proposal.md Success measure: 'The sheet is up to date every day.'",
      "scenario": "The sheet is filled in perfectly while the manager's visibility and decisions do not improve; the compliance metric hides the failure.",
      "fix": "Measure outcomes (e.g. manager answers the defined questions in under 5 minutes, fewer surprises at sprint review) plus team-hours spent, with a review date."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "proposal.md 'copies the same details into the shared ... Sheet'",
      "scenario": "A ticket changes after the daily copy; the sheet shows stale state, and the manager acts on the less accurate source.",
      "fix": "Drop the manual sheet; generate any spreadsheet view from the tracker's existing export or query."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "proposal.md '9 other labels'; tracker_fields.md 'labels (free text)'",
      "scenario": "Undefined free-text labels from 9 people diverge ('risk-high' vs 'High risk'), so the data cannot be grouped or queried even with full compliance.",
      "fix": "Name and justify each field against a manager question; use a fixed set of values or tracker custom fields, not free-text labels."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "proposal.md 'tags every ticket they touched that day with a priority' vs tracker_fields.md priority filled in at creation",
      "scenario": "Two engineers touching the same ticket set different priorities, overwriting the deliberate triage priority and turning it into noise.",
      "fix": "Keep priority as set at creation with a single owner (manager or tech lead at triage)."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "proposal.md Rollout: 'Mandatory from the start of the next sprint. Engineers who skip a day are reminded in the stand-up.'",
      "scenario": "Compliance slips within weeks, stand-ups become compliance checks, morale drops, and the ritual continues on inertia with no review point.",
      "fix": "Pilot with 2-3 volunteers for one sprint, with a set review date and kill criteria; handle misses privately or through automation."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "proposal.md 'every ticket they touched that day'",
      "scenario": "Admin cost grows with ticket activity, so engineers postpone or batch tracker updates, making the real source of truth less current.",
      "fix": "Capture extra fields once, at creation or at a transition into blocked/at-risk, not per touch per day."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "proposal.md 'It takes about 20 minutes'",
      "scenario": "12 fields entered twice across several tickets per day (e.g. 6 tickets = 144 entries) could take well over 20 minutes, making the cost in finding 1 worse.",
      "fix": "Run a 2-day timed trial with 2 engineers and measure actual minutes against tickets touched."
    }
  ]
}
```