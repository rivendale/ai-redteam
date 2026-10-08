# Redteam review: "Proposal: the daily ticket hygiene ritual"

**VERDICT: REJECT.** The proposal takes about 3 person-hours every day to re-enter data the tracker already records, for a reader who "may look at the sheet from time to time". That directly contradicts the request's constraint, "without slowing the team down".

**CONFIDENCE: high.** The core findings rest on direct quotes and arithmetic from the supplied files. Three things limit it:
- I had no tools in this session.
- The manager's actual unmet questions were not supplied.
- There was a single reviewer and no subagent. The work was not produced in this conversation, so there is no authorship anchoring.

**INPUTS LEDGER**
- **Seen:**
  - The original request (verbatim)
  - context.md
  - proposal.md
  - evidence/tracker_fields.md
- **Not seen:**
  - **The manager's specific visibility gaps.** This matters: it is the need the proposal should serve.
  - **The definition of the "9 other labels".** This matters: the labels are undefined in the work itself.
  - **The "Ticket Health Sheet" template.** Minor.
  - **The basis for the "20 minutes" estimate.** This matters only for whether the true cost is higher. The verdict holds even at face value.
  - **Sprint length.** It does not matter; the costs below are stated per day and per week.

**COVERAGE**
- **Checked:**
  - proposal.md: the Proposal, Benefit, Rollout and Success measure sections
  - evidence/tracker_fields.md: every listed field and the existing saved query and export
  - The request's two constraints: visibility for the manager, and not slowing the team
- **Not checked:**
  - The manager's needs (not supplied)
  - Label definitions (not supplied)
  - The sheet template (not supplied)

**SEATS AND GATE**
- One local reviewer. No subagent or cross-vendor seats were available.
- Sensitivity gate passed: there is no personal or confidential data in the work. A customer-impact note could later carry customer names; see S3.

## Pass 1: Reconstruct

**What the work proposes:**
- All 9 engineers tag every ticket they touched each day with:
  - a priority
  - a risk level
  - a customer-impact note
  - 9 further labels
- They then copy the same details into a shared sheet.
- This is mandatory from next sprint, and anyone who skips a day is reminded in stand-up.

**What must be true for it to be correct:**
1. The manager lacks visibility that the tracker cannot already provide.
2. The manager will actually use the sheet.
3. 20 minutes a day per person does not count as "slowing the team down".
4. A daily manual step will be done reliably and consistently.
5. "Sheet up to date" is a valid proxy for "manager has visibility".

Assumptions 1, 3 and 5 are contradicted by the supplied evidence or by the request itself. Track: D.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | D | proposal.md, Proposal: "about **20 minutes per person per day**"; request: "without slowing the team down" | The proposal breaks the request's explicit constraint. 20 min × 9 = 180 min = **3 person-hours/day**, or **15 person-hours/week**. That is about 4% of a 9×40 h week, every week, with no end date. | From the next sprint, the team loses about 15 h/week of engineering time to data entry. The request's one hard constraint is violated on day one. | Drop the daily per-engineer step. Any proposal must state its added cost per engineer, and that cost should be near zero. Reproduction: 20 × 9 / 60 = 3.0 h/day; 3.0 × 5 = 15 h/week. | a Y, b Y, c Y, d Y |
| F2 | High | CONFIRMED | D | proposal.md, Proposal vs evidence/tracker_fields.md | **Most of what is collected already exists, and a cheaper alternative was ignored.** The tracker already records status, assignee, last-updated time, linked PRs and priority ("filled in when a ticket is created"). A saved query ("touched in the last 24 hours, grouped by status") and a weekly spreadsheet export are "available to any user today". The proposal re-tags priority daily and copies everything into a second sheet. | Engineers spend time duplicating fields the manager could read directly. The manager running the existing saved query each morning would get "state of work" in minutes, with zero engineer time. | First alternative: the manager uses the existing saved query daily and the weekly export. If one specific gap remains (for example "blocked" or "customer-impacting"), add **one** label, applied only when the condition changes, not daily. Compare: the existing query costs about 0 engineer-minutes/day; this proposal costs 180. | a Y, b Y, c Y, d Y |
| F3 | High | CONFIRMED | D | proposal.md, Benefit: "Better visibility into the state of work. The engineering manager may look at the sheet from time to time." | **The need is unestablished.** No specific question the manager cannot answer today is named. The only consumer is described as an occasional, optional reader. | 15 h/week is spent producing a sheet the manager rarely opens. No decision changes because of it. | Before any build, write down the 2–3 questions the manager cannot answer today (for example "what is blocked for more than 2 days?") and show the tracker cannot answer them. | a Y, b Y, c N, d Y |
| F4 | High | CONFIRMED | D | proposal.md, Success measure: "The sheet is up to date every day."; Rollout: "Mandatory from the start of the next sprint" | **The success measure tracks compliance, not visibility, and there is no pilot, review date or exit criterion.** The ritual can "succeed" while delivering nothing, so nothing would ever trigger stopping it. | Engineers fill the sheet daily, so the measure reports success. The manager never uses it. The ritual runs indefinitely because the only measure is always met. | Measure outcomes instead, for example "the manager can answer questions X/Y without asking in stand-up" or "time-to-notice a blocked ticket". Pilot for 2 weeks with a stop rule. Track sheet views, or simply ask the manager whether they used it. | a Y, b Y, c N, d Y |
| F5 | Medium | PROBABLE | D | proposal.md, Proposal: "copies the same details into the shared 'Ticket Health Sheet'" | **Two sources of truth.** Manual copying from tracker to sheet will diverge: there will be typos, missed tickets, and status changes after the copy. | The manager reads the sheet, sees a ticket as "in progress" that the tracker shows as done (or vice versa), and acts on stale data. Visibility gets worse, not better. | Keep the tracker as the single source. Any sheet should be generated from the tracker's existing export, never hand-copied. | a Y, b N, c N, d Y |
| F6 | Medium | PROBABLE | D | proposal.md, Proposal: "a risk level, a customer-impact note and 9 other labels" | **Undefined fields.** The 9 labels are not named. "Risk level" and "customer-impact" have no scale. Labels are free text per tracker_fields.md. | Nine people apply 12 fields inconsistently ("High"/"high"/"hi", personal interpretations of risk). The sheet cannot be filtered or compared, so the data is noise. | Define any retained field with a fixed set of values and an example of each. Cut to the minimum the manager's stated questions need (see F3). | a Y, b N, c N, d Y |
| F7 | Low | PROBABLE | D | proposal.md, Rollout: "Engineers who skip a day are reminded in the stand-up." | Enforcement by public reminder uses stand-up time and adds social pressure. It also depends on someone remembering to do something every working day at the end of the day, which is the pattern most likely to be abandoned. | Stand-ups grow a compliance segment, people resent it, and compliance decays after a few weeks, typically as people rush the step before leaving. | Remove the daily manual step (F1/F2). If any human input remains, attach it to an existing event, such as a status change, rather than to a daily deadline. | a Y, b N, c N, d N |

## Confirm or refute (Critical and High)

- **F1, defended as "20 min is small":**
  - **Defence:** 20 minutes is small per person.
  - **Response:** The request's constraint is not "slightly slow". The proposal adds an uncapped, permanent daily cost with no offsetting time saving claimed anywhere.
  - **Outcome:** Holds as confirmed.
- **F2, defended as "the extra fields are new information":**
  - **Defence:** Risk, customer impact and the extra labels are new.
  - **Response:** That is partly true. Status, assignee, recency and priority are clearly duplicated, though, and the work never shows the new fields are needed (F3).
  - **Outcome:** Holds.
- **F3, defended as "the manager asked for visibility, so need is shown":**
  - **Defence:** The request itself shows the manager wants visibility.
  - **Response:** It shows a want for visibility. It does not show that *this sheet* answers anything the tracker cannot, and the proposal itself says the manager "may" look "from time to time".
  - **Outcome:** Holds.
- **F4, defended as "an up-to-date sheet is a reasonable proxy":**
  - **Defence:** An up-to-date sheet stands in for visibility.
  - **Response:** It does only if someone reads it. The measure cannot distinguish use from non-use.
  - **Outcome:** Holds.

## NEEDS VALIDATION

- **S1:** Whether the 20-minute estimate is realistic for 12 fields across all tickets touched, plus copying them to a sheet.
  - **Settled by:** Timing 2–3 engineers for one day.
  - **Note:** A higher figure would worsen F1. The verdict already holds at 20 minutes.
- **S2:** Whether the manager currently uses the existing saved query or export.
  - **Settled by:** Asking the manager.
  - **Note:** If they do and still lack something, that names the real gap.
- **S3:** Whether customer-impact notes would contain customer names or account details in a broadly shared sheet.
  - **Settled by:** The sheet's sharing settings and the field's intended content.

## REFUTED

- **R1: "The ticket tracker is the wrong data source for state of work."**
  - **Refuted by:** tracker_fields.md shows it records status, assignee, last-updated and linked PRs, which together describe the state of work.
  - **Consequence:** The proposal's choice of source is sound. What fails is its manual duplication of that source.

## WHAT HOLDS UP

- The goal is legitimate: the request asks for manager visibility.
- Anchoring on tickets is right, since the tracker is the natural source.
- Including a customer-impact signal could be valuable if the manager actually needs it. That need should be established first (F3) and captured once per ticket rather than daily.

## UNVERIFIED CLAIMS

- **"It takes about 20 minutes per person per day":** no basis is given. Confirm by timing a trial day.
- **"Better visibility into the state of work":** no mechanism or consumer is shown. Confirm by naming the manager's questions and checking the sheet answers them where the tracker cannot.

## QUESTIONS FOR THE AUTHOR

1. What specific questions can the manager not answer today with the saved query and the weekly export?
2. What are the 9 other labels, and which manager decision uses each one?
3. What result after two weeks would make you stop the ritual?

## DECISION-MAKER SUMMARY

Do not adopt this. It costs about 15 engineer-hours a week, mostly re-entering data the tracker already has, and it breaks the request's "without slowing the team down" constraint. Instead, the manager should first try the existing 24-hour saved query and weekly export. Add at most one or two defined labels for any gap that remains, and judge the result by questions answered, not by sheet completeness.

## OWNER SUMMARY

This plan would have every engineer spend about 20 minutes a day copying information that the ticket system already holds. That adds up to roughly two full working days of the team's time each week. The manager can likely get the same view today from a saved search that already exists, at no cost to the team. Try that first and add only the one or two missing details the manager actually needs.

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
    {"item": "manager's specific visibility gaps", "status": "not_seen", "matters": true},
    {"item": "definition of the 9 other labels", "status": "not_seen", "matters": true},
    {"item": "Ticket Health Sheet template", "status": "not_seen", "matters": false},
    {"item": "basis for the 20-minute estimate", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal, client, financial or confidential data in the proposal or evidence."},
  "coverage": {
    "checked": [
      {"unit": "proposal.md", "kind": "file"},
      {"unit": "proposal.md#Proposal", "kind": "section"},
      {"unit": "proposal.md#Benefit", "kind": "section"},
      {"unit": "proposal.md#Rollout", "kind": "section"},
      {"unit": "proposal.md#Success measure", "kind": "section"},
      {"unit": "evidence/tracker_fields.md", "kind": "file"},
      {"unit": "20 min x 9 people = 3 h/day, 15 h/week", "kind": "claim"},
      {"unit": "manager lacks visibility the tracker cannot provide", "kind": "assumption"},
      {"unit": "sheet up to date implies visibility", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "manager's unmet questions", "reason": "not supplied"},
      {"unit": "definitions of the 9 other labels", "reason": "not supplied"},
      {"unit": "Ticket Health Sheet template and sharing settings", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Proposal: 'about 20 minutes per person per day'",
     "scenario": "From next sprint, 9 engineers x 20 min = 3 person-hours/day (15 h/week) of data entry with no end date, violating the request's 'without slowing the team down'.",
     "fix": "Drop the daily per-engineer step; any proposal must state its added engineer cost, which should be near zero.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "20 x 9 / 60 = 3.0 h/day; 3.0 x 5 = 15 h/week."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Proposal vs evidence/tracker_fields.md",
     "scenario": "Engineers re-enter status, assignee, recency and priority that the tracker already records, while the existing 24-hour saved query and weekly export would give the manager the same view at zero engineer cost.",
     "fix": "Manager uses the existing saved query and weekly export first; add at most one or two defined labels for a named gap, applied on change rather than daily.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare proposal fields with tracker_fields.md: status, assignee, last-updated, linked PRs and priority already exist; saved query and export are available to any user today."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Benefit: 'The engineering manager may look at the sheet from time to time.'",
     "scenario": "15 h/week is spent producing a sheet the manager rarely opens; no decision changes.",
     "fix": "Name the 2-3 questions the manager cannot answer today and show the tracker cannot answer them before building anything.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Success measure: 'The sheet is up to date every day.'; Rollout: 'Mandatory from the start of the next sprint'",
     "scenario": "Engineers comply daily, the measure reports success, the manager never uses the sheet, and with no pilot or stop rule the ritual runs indefinitely.",
     "fix": "Measure outcomes (manager questions answered, time to notice a blocked ticket); run a 2-week pilot with an explicit stop rule.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "D",
     "location": "proposal.md, Proposal: 'copies the same details into the shared Ticket Health Sheet'",
     "scenario": "Hand-copied sheet diverges from the tracker after later status changes; the manager acts on stale data.",
     "fix": "Keep the tracker as the single source; generate any sheet from the existing export, never by hand.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "D",
     "location": "proposal.md, Proposal: 'a risk level, a customer-impact note and 9 other labels'",
     "scenario": "Nine people apply 12 undefined free-text fields inconsistently, so the data cannot be filtered or compared.",
     "fix": "Define a fixed value set for each retained field and cut to the minimum the manager's named questions require.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "F7", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "D",
     "location": "proposal.md, Rollout: 'Engineers who skip a day are reminded in the stand-up.'",
     "scenario": "Stand-up gains a compliance segment, the end-of-day manual step depends on daily memory, and compliance decays within weeks.",
     "fix": "Remove the daily manual step; if any input remains, tie it to a ticket status change, not a daily deadline.",
     "answers": {"a": true, "b": false, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "D", "location": "proposal.md, Proposal: '20 minutes per person per day'",
     "suspicion": "The true daily cost of 12 fields plus copying may exceed 20 minutes.",
     "unresolved_fact": "Measured time for 2-3 engineers over one day."},
    {"id": "S2", "status": "needs_validation", "track": "D", "location": "evidence/tracker_fields.md, saved query and weekly export",
     "suspicion": "The manager may not be using the existing saved query or export.",
     "unresolved_fact": "Whether the manager currently uses them, and what they still cannot see."},
    {"id": "S3", "status": "needs_validation", "track": "D", "location": "proposal.md, Proposal: 'a customer-impact note'",
     "suspicion": "Customer-impact notes may put customer names or account details in a widely shared sheet.",
     "unresolved_fact": "The sheet's sharing settings and the intended content of the customer-impact field."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The ticket tracker is the wrong data source for state of work.",
     "evidence": "tracker_fields.md shows it records status, assignee, last-updated and linked PRs, which describe the state of work; the failure is manual duplication, not the source."}
  ]
}
```