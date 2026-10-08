# Redteam review: "Proposal: the daily ticket hygiene ritual"

**VERDICT: REJECT.** By its own numbers the proposal costs the team about 3 engineer-hours every day. The request said "without slowing the team down", and most of the visibility the proposal wants already comes from the tracker's existing fields and saved query.

**CONFIDENCE: high.** The main findings come straight from the proposal's own text and the supplied tracker facts. The limits are:
- I had no tools in this session.
- One reviewer ran, with no second seat.
- The manager's actual information needs were not supplied.

**INPUTS LEDGER**
- **Seen:**
  - `request.md` (verbatim)
  - `context.md`
  - `proposal.md`
  - `evidence/tracker_fields.md`
- **Not seen:**
  - **The engineering manager's actual questions or complaints.** This matters, because without it the need cannot be established either way.
  - **The "Ticket Health Sheet" layout and the definitions of the "9 other labels".** This matters, because the burden and consistency of the labels depend on them.
  - **The source of the "20 minutes" figure.** This matters somewhat. Every finding holds even if the figure is smaller.
  - **The live tracker, saved query and export.** This matters somewhat. I took the evidence file as accurate and could not check it against the running system.

**COVERAGE**
- **Checked:**
  - `proposal.md`: the Proposal, Benefit, Rollout and Success measure sections
  - `evidence/tracker_fields.md`
  - The original request's two constraints: visibility for the manager, and not slowing the team
  - The 20-minute cost figure, which I recomputed
- **Not checked:**
  - The live tracker and the saved query's output
  - The sheet template
  - The label definitions
  - The manager's needs

**SEATS AND GATE**
- One local reviewer ran.
- No subagent or cross-vendor seats were available because this session has no tools.
- Sensitivity gate: nothing sensitive was found. The work contains no personal, client, financial or credential data.
- Independence: the work was not written in this conversation, so this is not a same-context review of my own output.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | D (drift) | proposal.md, Proposal: "about **20 minutes per person per day**", 9 people | The proposal breaks the request's explicit constraint "without slowing the team down". | 9 × 20 min = 180 min, or 3 engineer-hours, every working day. That is 15 h/week, about 4% of a 9-person team's time, or roughly 0.4 of an engineer permanently, spent on bookkeeping. | Choose a design whose recurring cost to engineers is near zero (see F2). Reproduction: 9 × 20 = 180 min/day; 180 × 5 = 900 min = 15 h/week. | a✓ b✓ c✓ d✓ |
| F2 | High | CONFIRMED | D (cheaper alternative) | proposal.md, Proposal, compared with evidence/tracker_fields.md | The proposal re-enters data the tracker already holds, and copies it a second time into a sheet. Priority "the team already fills in when a ticket is created", and status, assignee, last-updated time and linked PRs are all automatic. | Every day engineers re-tag priority that already exists and hand-copy tracker data into a spreadsheet. The manager could already see who touched what through the existing "touched in the last 24 hours, grouped by status" saved query and the weekly export. | Start the manager on the existing saved query and weekly export. Add at most one or two new fields, such as risk or customer impact, set once at ticket creation or on a status change, and only if the manager names a question the current fields cannot answer. | a✓ b✓ c✗ d✓ |
| F3 | High | CONFIRMED | D (need) | proposal.md, Benefit: "The engineering manager may look at the sheet from time to time." | No need is shown. The proposal does not name a question the manager cannot answer today, and its only consumer may look at the output just "from time to time". | The team spends 15 h/week producing a sheet the manager rarely opens, while the proposal never states what decision the visibility is meant to support. | Write down the 3 to 5 questions the manager needs answered, such as what is blocked, what is at risk this sprint, and what touches customers. Check each one against the existing fields first. | a✓ b✓ c✗ d✓ |
| F4 | High | CONFIRMED | D (adoption, measurement) | proposal.md, Success measure: "The sheet is up to date every day." | The success measure counts compliance, not visibility, so it cannot detect that the proposal has failed at its goal. | The sheet is filled in every day, the measure reports success, and the manager is still surprised by a slipped or blocked item. | Measure an outcome instead, such as "the manager can answer the agreed questions without asking anyone" or "fewer status-chasing messages". Set a review date with a stated condition for stopping the ritual. | a✓ b✓ c✗ d✓ |
| F5 | Medium | PROBABLE | D (burden) | proposal.md, Proposal: "copies the same details into the shared … Sheet before they leave"; Rollout: "reminded in the stand-up" | The proposal creates two sources of truth that depend on a daily manual step, enforced by public reminders. | End-of-day copying gets skipped or rushed, so the sheet drifts from the tracker. The manager then acts on stale or conflicting data, and stand-up time goes to compliance call-outs. | Make the tracker the only source of truth and generate any view from it automatically. Drop the stand-up reminders. | a✓ b✗ c✗ d✓ |
| F6 | Medium | PROBABLE | D (burden, consistency) | proposal.md, Proposal: "a risk level, a customer-impact note and 9 other labels"; tracker_fields.md: "labels (free text)" | Twelve fields are required, and the 9 labels are never named or defined. The labels are free text, and "every ticket they touched" means several people tag the same ticket. | Nine people apply undefined free-text labels inconsistently, and shared tickets get conflicting risk values. The resulting data cannot be aggregated. | Define a small, closed set of values. Assign one owner per ticket for each field, usually the assignee. Set fields on a state change, not daily. | a✓ b✗ c✗ d✓ |
| F7 | Medium | CONFIRMED | D (reversibility) | proposal.md, Rollout: "Mandatory from the start of the next sprint." | The ritual becomes mandatory for the whole team at once, with no pilot, no review date and no way out. | If the ritual turns out to be useless, nothing in the plan triggers stopping it, and the cost continues indefinitely. | Pilot it for two weeks with the manager using only existing tracker views. Decide afterwards, against the questions from F3, whether any new field is needed. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION

- **S1. Visibility gap.** Whether a real gap exists depends on which questions the manager cannot answer today with the saved query and weekly export. The manager's own list of unanswered questions would settle this.
- **S2. Saved query.** Whether the saved query actually returns correct, current results, which would be a positive control for the "already available" claim. Running it on a day with known activity and checking that it returns those tickets would settle this.
- **S3. The 20-minute figure.** Whether "about 20 minutes" was measured or guessed. A timed trial would settle it. F1 holds even at 5 minutes, which would still be 45 min/day.
- **S4. Custom fields.** Whether the tracker supports structured fields for risk and customer impact, or only free-text labels. The tracker's configuration would settle this.

## REFUTED

- **C1. "The tracker cannot hold the extra fields, so the sheet is necessary."** Refuted. tracker_fields.md says every ticket has free-text labels, so the data could live in the tracker without the sheet.
- **C2. "Priority is not tracked today."** Refuted. tracker_fields.md says the team already fills in priority at creation.

## WHAT HOLDS UP

- The goal of better manager visibility is legitimate and matches the request.
- Risk and customer impact are plausible things for a manager to want, and they are not among the automatic tracker fields. They may be the one real gap.
- The proposal is concrete enough to cost: it gives people, minutes and a frequency. That is what makes F1 checkable.

## UNVERIFIED CLAIMS

- **"Better visibility into the state of work."** The proposal names no mechanism or consumer behavior that delivers it. To confirm, list the manager's questions and show which ones the sheet answers that the tracker does not.
- **"About 20 minutes per person per day."** To confirm, time a sample of engineers.

## QUESTIONS FOR THE AUTHOR

1. What specific questions can the manager not answer today with the saved query and weekly export?
2. Which of the 12 fields answer those questions, and why can't they be set once on the ticket instead of every day?
3. What would make you stop the ritual?

## DECISION-MAKER SUMMARY

Do not adopt this. It costs about 15 engineer-hours a week and directly contradicts "without slowing the team down", and most of the data it collects already sits in the tracker. Next, have the manager list the questions they cannot answer, try the existing saved query and export for two weeks, and add at most one or two fields that are set once per ticket. If you proceed anyway, expect a sheet that is complete but rarely read, that drifts from the tracker, and that has no condition for stopping it.

## OWNER SUMMARY

This plan would take about three hours of the team's time every day to fill in a spreadsheet, which is the opposite of the goal of not slowing the team down. Most of what it asks people to type is already recorded automatically by the ticket system, and the manager can already see it with an existing saved view. A better first step is to find out exactly what the manager can't see today and fill only that gap, ideally without any new daily chore.

```json
{
  "schema_version": "2.2",
  "verdict": "REJECT",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "proposal.md", "status": "seen", "matters": true},
    {"item": "evidence/tracker_fields.md", "status": "seen", "matters": true},
    {"item": "Engineering manager's actual information needs", "status": "not_seen", "matters": true},
    {"item": "Ticket Health Sheet template and definitions of the 9 other labels", "status": "not_seen", "matters": true},
    {"item": "Basis for the 20-minute estimate", "status": "not_seen", "matters": false},
    {"item": "Live tracker, saved query and weekly export", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal, client, financial, health, credential or confidential data in the work."},
  "coverage": {
    "checked": [
      {"unit": "proposal.md", "kind": "file"},
      {"unit": "proposal.md#Proposal", "kind": "section"},
      {"unit": "proposal.md#Benefit", "kind": "section"},
      {"unit": "proposal.md#Rollout", "kind": "section"},
      {"unit": "proposal.md#Success measure", "kind": "section"},
      {"unit": "evidence/tracker_fields.md", "kind": "file"},
      {"unit": "20 minutes x 9 people per day cost", "kind": "claim"},
      {"unit": "Request constraint: without slowing the team down", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "Live tracker saved query and weekly export", "reason": "no tools; not openable"},
      {"unit": "Ticket Health Sheet template", "reason": "not supplied"},
      {"unit": "Definitions of the 9 other labels", "reason": "not supplied"},
      {"unit": "Engineering manager's information needs", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Proposal: 'about 20 minutes per person per day' (9 people)",
     "scenario": "9 x 20 min = 180 min (3 engineer-hours) every working day, 15 h/week, about 4% of team capacity, contradicting the request's 'without slowing the team down'.",
     "fix": "Choose a design with near-zero recurring engineer cost built on existing tracker data.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compute 9 x 20 = 180 min/day; 180 x 5 = 900 min = 15 h/week; compare with request.md 'without slowing the team down'."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Proposal vs evidence/tracker_fields.md",
     "scenario": "Engineers re-tag priority already set at creation and hand-copy status, assignee and activity into a sheet, although the saved query 'touched in the last 24 hours, grouped by status' and the weekly export already provide them.",
     "fix": "Have the manager use the existing saved query and export; add at most one or two fields set once per ticket, only for questions current fields cannot answer.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Benefit: 'The engineering manager may look at the sheet from time to time.'",
     "scenario": "The team spends 15 h/week producing a sheet the manager opens only occasionally, and no question or decision the visibility serves is named.",
     "fix": "List the manager's 3-5 unanswered questions and check each against existing tracker fields before adding anything.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Success measure: 'The sheet is up to date every day.'",
     "scenario": "The sheet is filled in daily, so the measure reports success, while the manager is still surprised by blocked or slipping work.",
     "fix": "Measure an outcome (the manager answers the agreed questions without asking anyone) and set a review date with a stop condition.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "D",
     "location": "proposal.md, Proposal: 'copies the same details into the shared Ticket Health Sheet before they leave'; Rollout: 'reminded in the stand-up'",
     "scenario": "End-of-day copying is skipped or rushed, so the sheet drifts from the tracker; the manager acts on stale or conflicting data, and stand-up time goes to compliance reminders.",
     "fix": "Keep the tracker as the single source of truth and generate any view automatically; drop the stand-up reminders.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "D",
     "location": "proposal.md, Proposal: 'a risk level, a customer-impact note and 9 other labels'; tracker_fields.md: 'labels (free text)'",
     "scenario": "Nine people apply undefined free-text labels inconsistently, and tickets touched by several people get conflicting values, so the data cannot be aggregated.",
     "fix": "Define a small closed set of values, assign one owner per ticket field (the assignee), and set fields on a state change, not daily.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "F7", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Rollout: 'Mandatory from the start of the next sprint.'",
     "scenario": "If the ritual proves useless, nothing in the plan triggers stopping it, so the 15 h/week cost continues indefinitely.",
     "fix": "Run a two-week pilot using existing tracker views, then decide against the manager's stated questions whether any new field is needed.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "D", "location": "proposal.md, Benefit",
     "suspicion": "There may be no real visibility gap beyond what the tracker already shows.",
     "unresolved_fact": "Which questions the manager cannot answer today with the saved query and weekly export."},
    {"id": "S2", "status": "needs_validation", "track": "D", "location": "evidence/tracker_fields.md",
     "suspicion": "The saved query may not return correct, current results.",
     "unresolved_fact": "Whether the query returns the tickets known to have been touched on a given day (positive control)."},
    {"id": "S3", "status": "needs_validation", "track": "D", "location": "proposal.md, Proposal: 'about 20 minutes'",
     "suspicion": "The 20-minute figure may be a guess rather than a measurement.",
     "unresolved_fact": "A timed trial of the ritual by a sample of engineers."},
    {"id": "S4", "status": "needs_validation", "track": "D", "location": "evidence/tracker_fields.md",
     "suspicion": "The tracker may support structured custom fields for risk and customer impact.",
     "unresolved_fact": "The tracker's field configuration options."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The tracker cannot hold the extra fields, so the sheet is necessary.",
     "evidence": "tracker_fields.md: every ticket has free-text labels."},
    {"id": "C2", "candidate": "Priority is not tracked today.",
     "evidence": "tracker_fields.md: 'the priority field the team already fills in when a ticket is created'."}
  ]
}
```