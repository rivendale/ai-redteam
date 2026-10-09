# Redteam report: "The daily ticket hygiene ritual"

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available. This proposal was not written in this conversation.

**VERDICT: REJECT.** The ritual costs the team about 15 engineer-hours a week, which contradicts the "without slowing the team down" constraint. Most of what it collects is already in the tracker. Its only beneficiary "may look at the sheet from time to time".

**CONFIDENCE: medium.** All findings come from the supplied text and arithmetic, so they are traceable. Confidence is limited by:
- no fresh-instance reviewer;
- no tools;
- no statement from the engineering manager about what they actually cannot see today.

**INPUTS LEDGER**
- **Seen:**
  - `request.md`, the original request, verbatim.
  - `context.md`.
  - `proposal.md`.
  - `evidence/tracker_fields.md`.
- **Not seen:**
  - **The engineering manager's own statement of the visibility gap.** This matters: the need cannot be judged without it (finding F3).
  - **The definitions of the "9 other labels".** This matters for F5.
  - **The layout and access permissions of the Ticket Health Sheet.** This matters for the data-handling suspicion S3.
  - **The team's working-day and sprint calendar.** This matters little; it only changes the weekly cost figure slightly.

**COVERAGE**
- **Scope:** the whole proposal.
- **Checked:**
  - `request.md` (document).
  - `context.md` (document).
  - `proposal.md` (document): its Proposal, Benefit, Rollout and Success measure sections.
  - `evidence/tracker_fields.md` (document).
  - The 20-minute cost claim (recomputed).
  - The assumption that the tracker lacks this data.
- **Not checked:**
  - The definitions of the 9 labels (not supplied).
  - The sheet's permissions (not supplied).
  - The engineering manager's requirements (not supplied).

**SEATS AND GATE:** I was the only reviewer (local, same-context). No cross-vendor seats ran; none were requested and there are no tools. The sensitivity gate passed: the supplied material contains no personal or confidential data.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (arithmetic) | D | proposal.md, Proposal: "about 20 minutes per person per day" | The proposal directly breaks the request's constraint "without slowing the team down". | 9 people × 20 min = 180 min a day. Over 5 working days that is **15 h/week**, about 0.375 of an FTE, or roughly 4% of team capacity, before counting the stand-up reminders. That time is spent every working day indefinitely. | Replace the ritual with a near-zero-entry approach that reads data the tracker already has (see F2). Recompute: 9 × 20 × 5 / 60 = 15 h. | a✓ b✓ c✓ d✓ |
| F2 | High | CONFIRMED (quote) | D | proposal.md, Proposal ("tags… with a priority… copies the same details into the shared Ticket Health Sheet") vs tracker_fields.md | **It duplicates existing data.** Priority is already filled in at ticket creation. Status, assignee, last-updated and linked PRs are recorded automatically. A saved query ("touched in the last 24 hours, grouped by status") and a weekly spreadsheet export are "available to any user today". The proposal ignores this cheaper alternative. | Engineers re-enter priority on top of the existing field and hand-copy it into a second store. The tracker and the sheet then drift apart (one gets updated, the other doesn't), so the manager sees two conflicting "truths". | Before collecting anything new, the manager uses the saved query daily and the weekly export. Repro: open the saved query and confirm it already lists the touched tickets by status. | a✓ b✓ c✗ d✓ |
| F3 | High | CONFIRMED (quote) | D | proposal.md, Benefit: "The engineering manager may look at the sheet from time to time." | **The need is unestablished.** No question the manager needs answered is named. The beneficiary's own use is optional, while the cost to the 9 engineers is mandatory. | The team spends 15 h/week. The manager looks occasionally and makes no decision differently. Nobody notices the waste, because nothing measures it. | Ask the manager to name the 2–3 questions they cannot answer today, for example "what is blocked?" or "what is at risk this sprint?". Map each question to an existing field or query. Add a field only where none exists. Pilot for 2 weeks with a stop criterion. | a✓ b✓ c✗ d✓ |
| F4 | High | CONFIRMED (quote) | D | proposal.md, Success measure: "The sheet is up to date every day." | **The success measure counts the burden, not the benefit.** It tracks compliance, not whether the manager gained visibility or used it. | The sheet is updated perfectly every day while the manager never opens it. By this measure the proposal "succeeds", so it is never reconsidered. | Measure the outcome instead: the manager answers the named questions without asking anyone, plus a check on how often the view is actually used. Include an explicit exit criterion. | a✓ b✓ c✗ d✓ |
| F5 | Medium | PROBABLE | D | proposal.md, Proposal: "a risk level, a customer-impact note and 9 other labels"; tracker_fields.md: "labels (free text)" | The 9 labels are unnamed, and the tracker's labels are free text. Nothing defines the vocabulary or what "risk level" means. | Nine people label inconsistently (for example "risk-high", "High risk", "hi-risk"). Grouping the sheet or the tracker by label then gives misleading counts. | Do not add labels unless one maps to a named question from F3. If one does, use a fixed-value field rather than free text. | a✓ b✗ c✗ d✓ |
| F6 | Medium | PROBABLE | D | proposal.md, Proposal ("before they leave") and Rollout ("reminded in the stand-up") | The plan depends on 9 people remembering a manual step every day. It is enforced by public reminders, which also take time out of the stand-up. | Compliance decays within weeks. Stand-up time goes to chasing the sheet. Entries are rushed at end of day, so data quality drops just as the sheet starts to look "complete". | Remove the daily manual step entirely (see F2). If any manual input survives, make it part of an action engineers already take, such as setting a field when changing a ticket's status. | a✓ b✗ c✗ d✓ |
| F7 | Low | CONFIRMED (quote) | D | proposal.md, Proposal: "every ticket they touched that day" | "Touched" is undefined: it could mean viewed, commented, committed or status-changed. | Engineers interpret it differently, so both the workload and the sheet's coverage vary from person to person. | If anything survives, reuse the tracker's own definition: the saved query's "touched in the last 24 hours". | a✓ b✓ c✗ d✗ |

**Siblings searched (F1–F4):**
- F1: I searched all four sections for any other stated cost. There are none besides the stand-up reminders (F6). Not a security finding.
- F2: I compared every field the proposal asks for against `tracker_fields.md`. Priority duplicates the existing field outright. Status and activity are covered by the saved query. Risk and customer impact have no existing field. Not a security finding.
- F3 and F4: I checked the Benefit and Success sections. No other section mentions the manager's use. Neither is a security finding.

**Confirm-or-refute round:**
- **F1 survives.** Its strongest defence would be "20 minutes is small". But 15 h/week is not small, and the request forbids slowing the team down at all.
- **F2 survives.** The defence "risk and customer impact are new" holds for those two fields only. It does not hold for priority, status or the sheet copy.
- **F3 survives.** The defence "visibility is obviously needed" does not answer the problem: the request asks for better visibility, but the proposal never says which visibility is missing.
- **F4 survives.** No defence was found.

## NEEDS VALIDATION
- **S1:** whether the 20-minute estimate is realistic, or optimistic. Tagging 12 or more labels on every touched ticket and then copying them could take longer. This is settled by timing one engineer for a week.
- **S2:** whether the manager's actual gap is something the existing saved query cannot answer, such as risk or customer impact. This is settled by the manager's written list of questions.
- **S3:** whether the customer-impact notes copied into a "shared" sheet would carry customer names or details beyond the sheet's access controls. This is settled by the sheet's sharing settings and an example note.

## REFUTED
- **"The tracker has no priority data, so the ritual adds it."** Refuted: `tracker_fields.md` says priority is "the priority field the team already fills in when a ticket is created".
- **"The existing query and export are restricted, so the manager cannot use them."** Refuted: both are "available to any user today".

## WHAT HOLDS UP
- The underlying goal, giving the manager visibility into work, is legitimate and matches the request.
- A shared, single view for the manager is a reasonable idea. It just should be generated from the tracker, not typed by hand.

## UNVERIFIED CLAIMS
- **"About 20 minutes per person per day":** confirm by timing (S1).
- **"Better visibility" as the benefit:** confirm by naming the questions it would answer (S2).

## QUESTIONS FOR THE AUTHOR
1. Which specific questions can the engineering manager not answer today using the saved query and the weekly export?
2. Which of the 12+ fields would change a decision the manager makes, and what decision?
3. What result after 2 weeks would make you stop the ritual?

## DECISION-MAKER SUMMARY
Do not adopt the ritual. It costs about 15 engineer-hours a week, against an explicit "don't slow the team down" constraint, and mostly duplicates data the tracker already holds. Have the manager use the existing saved query and weekly export for two weeks. Add a structured field only for a question those cannot answer. Adopting it anyway risks permanent lost capacity for a sheet with no committed reader.

## OWNER SUMMARY
The proposed daily form would take the team about three hours of combined time every day. Most of what it asks for is already recorded automatically. A better first step is for the manager to use the reports the ticket system already offers, and to add new information only when there is a specific question it would answer.

```json
{
  "schema_version": "2.3",
  "verdict": "REJECT",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "proposal.md", "status": "seen", "matters": true},
    {"item": "evidence/tracker_fields.md", "status": "seen", "matters": true},
    {"item": "engineering manager's stated visibility questions", "status": "not_seen", "matters": true},
    {"item": "definitions of the 9 other labels", "status": "not_seen", "matters": true},
    {"item": "Ticket Health Sheet layout and sharing settings", "status": "not_seen", "matters": true},
    {"item": "team working-day calendar", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "proposal.md", "kind": "document"},
      {"unit": "evidence/tracker_fields.md", "kind": "document"},
      {"unit": "proposal.md#Proposal", "kind": "section"},
      {"unit": "proposal.md#Benefit", "kind": "section"},
      {"unit": "proposal.md#Rollout", "kind": "section"},
      {"unit": "proposal.md#Success measure", "kind": "section"},
      {"unit": "20 minutes per person per day", "kind": "claim"},
      {"unit": "tracker lacks the needed data", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "definitions of the 9 other labels", "reason": "not_supplied"},
      {"unit": "Ticket Health Sheet sharing settings", "reason": "not_supplied"},
      {"unit": "engineering manager's requirements", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Proposal: 'about 20 minutes per person per day'",
     "scenario": "9 engineers x 20 min = 180 min/day = 15 h/week (~0.375 FTE) spent indefinitely, contradicting the request's 'without slowing the team down'.",
     "fix": "Replace the ritual with a view generated from existing tracker data; add no daily manual step.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all four proposal sections for other stated costs", "found": "stand-up reminder time only (F6)"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Proposal vs evidence/tracker_fields.md",
     "scenario": "Priority, status and activity already exist in the tracker and a saved query; re-entering them by hand into a second sheet creates conflicting records for the manager.",
     "fix": "Have the manager use the existing saved query and weekly export first; collect only fields with no existing source.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every requested field against tracker_fields.md", "found": "priority and status/activity duplicated; risk and customer impact have no existing field"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Benefit: 'The engineering manager may look at the sheet from time to time.'",
     "scenario": "The team spends 15 h/week while the only beneficiary's use is optional and no question to be answered is named; no decision changes.",
     "fix": "Have the manager name the 2-3 unanswered questions; map each to existing data; pilot any addition for 2 weeks with a stop criterion.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all sections for any statement of manager use or need", "found": "none besides the Benefit sentence"}},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Success measure: 'The sheet is up to date every day.'",
     "scenario": "The sheet is perfectly maintained while the manager never opens it; the measure reports success and the ritual is never reconsidered.",
     "fix": "Measure outcome (manager answers named questions unaided, view usage) and define an exit criterion.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "Rollout and Success sections for any outcome or exit criterion", "found": "none"}},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "D",
     "location": "proposal.md, Proposal: '9 other labels'; tracker_fields.md: 'labels (free text)'",
     "scenario": "Nine people use inconsistent free-text values, so grouping by label yields misleading counts.",
     "fix": "Add no labels without a named question; use fixed-value fields if any survive.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "D",
     "location": "proposal.md, Proposal ('before they leave') and Rollout ('reminded in the stand-up')",
     "scenario": "A daily memory-dependent step decays within weeks; stand-up time is spent chasing compliance; rushed entries degrade data quality.",
     "fix": "Remove the manual step; if any input remains, attach it to an existing action such as a status change.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "F7", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Proposal: 'every ticket they touched that day'",
     "scenario": "'Touched' is undefined, so workload and coverage differ per engineer.",
     "fix": "Reuse the saved query's 'touched in the last 24 hours' definition.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "D", "location": "proposal.md, Proposal: '20 minutes'",
     "suspicion": "The 20-minute estimate may be optimistic for 12+ fields per touched ticket plus copying.",
     "unresolved_fact": "Measured time for one engineer over one week."},
    {"id": "S2", "status": "needs_validation", "track": "D", "location": "proposal.md, Benefit",
     "suspicion": "The manager's real gap may be limited to risk or customer impact, which the tracker lacks.",
     "unresolved_fact": "The manager's written list of unanswered questions."},
    {"id": "S3", "status": "needs_validation", "track": "D", "location": "proposal.md, Proposal: 'customer-impact note' copied to the shared sheet",
     "suspicion": "Customer details may be copied into a broadly shared sheet.",
     "unresolved_fact": "The sheet's sharing settings and an example customer-impact note."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The tracker has no priority data, so the ritual adds it.",
     "evidence": "tracker_fields.md: 'the priority field the team already fills in when a ticket is created'."},
    {"id": "C2", "candidate": "The existing query and export are not available to the manager.",
     "evidence": "tracker_fields.md: both are 'available to any user today'."}
  ]
}
```