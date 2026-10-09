# Redteam review: "The daily ticket hygiene ritual"

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available, so I reviewed it myself. The proposal was not written in this conversation, which lowers the anchoring risk but does not remove it.

**VERDICT: REJECT.** The proposal breaks the request's one explicit constraint ("without slowing the team down") by taking about 3 engineer-hours a day. It also re-collects data the tracker already records, and it never says what the manager needs to see.

**CONFIDENCE: medium.** Three things limit it: no tools (the tracker facts come only from the supplied evidence file), no statement of what the manager actually lacks, and no definition of the "9 other labels".

**INPUTS LEDGER**
- **Seen:** the original request; the context; `proposal.md`; `evidence/tracker_fields.md`.
- **Not seen:** a statement of the manager's actual visibility gap. *Matters*: the need cannot be judged without it.
- **Not seen:** definitions of the "9 other labels", the risk-level scale and the customer-impact note. *Matters* for data quality (F6).
- **Not seen:** the "Ticket Health Sheet" template. *Matters somewhat.*
- **Not seen:** the live tracker. *Matters somewhat*: tracker capabilities are taken from the evidence file as given, not checked.
- **Not seen:** any evidence that the 20-minute estimate was measured. *Matters*: F1 uses the proposal's own figure, which, if anything, flatters the proposal.

**COVERAGE**
- **Checked:** every section of `proposal.md` (Proposal, Benefit, Rollout, Success measure); every claim in `tracker_fields.md`; the cost arithmetic; the fit against the original request.
- **Not checked:** the live tracker configuration; the realism of the 20-minute estimate; the manager's actual questions.

**SEATS AND GATE:** One local same-context reviewer ran. No cross-vendor seats were requested, and depth is `standard`. Sensitivity gate: no personal, financial, credential or confidential data found.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | D (drift) | proposal.md, Proposal: "about **20 minutes per person per day**", "every engineer (9 people)" | The request requires "without slowing the team down". The proposal's own figure costs 20 × 9 = 180 min/day = 3 h/day ≈ 15 h/week ≈ 30 h per 2-week sprint. That is about 4% of team capacity, or roughly 0.4 of a full-time engineer, every working day, permanently. | The team adopts it next sprint. Each 2-week sprint loses ~30 engineer-hours to data entry, which directly contradicts the request. | Reject any design with a recurring per-engineer daily cost. Require that the proposal's marginal engineer time be ~0 (see F2). Reproduce: 20 min × 9 people × 5 days = 900 min = 15 h/week. | a✔ b✔ c✔ d✔ |
| F2 | High | CONFIRMED | D (cheaper alternative) | proposal.md, Proposal ("tags… with a priority… copies the same details") vs tracker_fields.md | The proposal duplicates what already exists. Priority is "already fill[ed] in when a ticket is created". Status, assignee, last-updated time and linked PRs are recorded automatically. A saved query, "touched in the last 24 hours, grouped by status", and a weekly spreadsheet export are "available to any user today". That is already a daily view of the state of work at zero engineer cost. The proposal does not mention or evaluate any of it. | Engineers spend 15 h/week re-entering priority and status-like data the manager could get from the existing saved query in seconds. | Start with the manager using the existing saved query daily, plus the weekly export. Add one structured field (for example a "blocked" flag) only if a specific question goes unanswered after 2 weeks. | a✔ b✔ c✘ d✔ |
| F3 | High | CONFIRMED | D (need) | proposal.md, Benefit: "Better visibility into the state of work. The engineering manager may look at the sheet from time to time." | No need is stated. The proposal names no question the manager cannot answer today, no decision that would change, and no evidence the current tools fall short. The only consumer "may" look "from time to time". | 9 people do daily data entry that one person consults occasionally, or never. The cost is certain and the benefit is speculative. | Before designing anything, have the manager list the 3–5 questions they cannot answer today (for example "what is blocked?", "what slipped this week?"). Then test whether the existing tracker answers each one. | a✔ b✔ c✘ d✔ |
| F4 | Medium | CONFIRMED | D (adoption/measure) | proposal.md, Success measure: "The sheet is up to date every day." | The measure tracks compliance, not the goal. It would read "success" even if the manager never opened the sheet and visibility never improved. Speed, which the request names, is not measured at all. Nothing would show that the sheet was abandoned or useless. | The sheet stays perfectly filled for months, nobody reads it, and the review declares success. | Measure outcomes instead: the manager's questions answered without asking engineers, and team throughput or cycle time unchanged. Add a kill criterion: drop the practice if the manager has not used it in 2 weeks. | a✔ b✔ c✘ d✘ |
| F5 | Medium | PROBABLE | D (burden) | proposal.md, Proposal: "copies the same details into the shared 'Ticket Health Sheet'" | Double entry creates two sources of truth. The tracker updates automatically when status changes; the sheet does not. Manual copying across 9 people will drift. | A ticket is reopened after the engineer filled in the sheet. The manager reads "done" in the sheet while the tracker says "in progress", which makes visibility worse than reading the tracker directly. | If any manual fields are kept, keep them only in the tracker (as labels or fields) and build the view from the tracker or the export. No hand-maintained copy. | a✔ b✘ c✘ d✔ |
| F6 | Medium | PROBABLE | D (burden/data quality) | proposal.md, Proposal: "a risk level, a customer-impact note and 9 other labels"; tracker_fields.md: "labels (free text)" | Twelve fields per ticket are undefined: no scale for risk, no list for the 9 labels. Free-text labels will be spelled and interpreted inconsistently. A ticket touched by several engineers gets tagged several times, possibly with conflicting values. Re-tagging "priority" may also overwrite the priority set at creation. | After a week the sheet holds "high", "High", "hi-risk", and conflicting priorities on shared tickets. It cannot be grouped or filtered, so it is unusable for the stated goal. | Define a minimal set of fields (ideally 0–1) with fixed values. Give each one a single owner per ticket. Never re-ask for the existing priority field. | a✔ b✘ c✘ d✔ |
| F7 | Medium | CONFIRMED | D (rollout) | proposal.md, Rollout: "Mandatory from the start of the next sprint. Engineers who skip a day are reminded in the stand-up." | The rollout is mandatory for the whole team immediately, with no pilot and no review or exit point. Enforcement depends on people remembering a manual step every day, which the skill notes usually fails. Public reminders also take time out of the stand-up, adding further to F1's cost. | Compliance drops within weeks. Stand-ups become status-policing, and the practice either lingers as resented overhead or dies quietly with no decision recorded. | If anything manual survives F2/F3, pilot it with 1–2 engineers for 2 weeks. Set an explicit review date and exit criterion. Track enforcement privately or through the tracker query, not in the stand-up. | a✔ b✔ c✘ d✘ |

## NEEDS VALIDATION
- **S1 (20-minute estimate is understated).** Twelve-plus fields per ticket, for every ticket touched, plus copying into a sheet, may exceed 20 min/day. What would settle it: a timed trial of one day's tagging for 2–3 engineers. This matters only to strengthen F1; F1 already stands on the proposal's own figure.
- **S2 (the existing saved query meets the manager's need).** What would settle it: the manager's list of unanswered questions (see F3), checked against the query and the export.
- **S3 (the tracker facts are accurate as stated).** What would settle it: opening the saved query and the export in the live tracker.

## REFUTED
- **"Priority is not recorded anywhere today."** Refuted: tracker_fields.md says priority is "the priority field the team already fills in when a ticket is created".
- **"The manager has no daily view without a new process."** Refuted: the "touched in the last 24 hours, grouped by status" saved query is "available to any user today".
- **"The work contains instructions aimed at the reviewer."** Checked; none found.

## WHAT HOLDS UP
- The goal itself, manager visibility into the state of work, is legitimate and in scope.
- The proposal is concrete. It states its cost, scope, start date and success measure plainly, and that concreteness is what makes the cost problem checkable.
- Its instinct to use ticket-level data is sound. That data already exists in the tracker.

## UNVERIFIED CLAIMS
- "About 20 minutes per person per day." This is not measured. Confirm it with a timed trial (S1).
- The implicit claim that a sheet gives "better visibility" than the tracker. Confirm it by naming the questions the sheet answers that the tracker query cannot (S2).

## QUESTIONS FOR THE AUTHOR
1. What specific questions can the manager not answer today, and have they tried the existing 24-hour saved query and the weekly export?
2. Which of the 12 fields is not derivable from status, assignee, last-updated time, linked PRs or the existing priority field, and what decision depends on it?
3. What would show, within 2 weeks, that the practice is not worth its 15 h/week?

## DECISION-MAKER SUMMARY
Do not adopt this ritual. By its own numbers it costs about 15 engineer-hours a week, which contradicts the "without slowing the team down" requirement, and it duplicates a daily view the tracker already provides. Next step: have the manager list the questions they cannot answer, and try the existing saved query and weekly export for two weeks. Proceeding anyway risks a permanent productivity tax for a sheet that may go unread.

## OWNER SUMMARY
This plan would have every engineer spend about 20 minutes a day copying ticket details into a spreadsheet, which adds up to roughly two full working days of the team's time each week. Most of that information is already captured automatically by the ticket system, and a ready-made daily view already exists. A better first step is for the manager to use the existing view and add only what turns out to be genuinely missing.

```json
{
  "schema_version": "2.2",
  "verdict": "REJECT",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "proposal.md", "status": "seen", "matters": true},
    {"item": "evidence/tracker_fields.md", "status": "seen", "matters": true},
    {"item": "manager's statement of the visibility gap", "status": "not_seen", "matters": true},
    {"item": "definitions of the 9 other labels, risk level and customer-impact note", "status": "not_seen", "matters": true},
    {"item": "Ticket Health Sheet template", "status": "not_seen", "matters": false},
    {"item": "live tracker configuration", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal, financial, credential or confidential data in the work or context."},
  "coverage": {
    "checked": [
      {"unit": "proposal.md", "kind": "file"},
      {"unit": "proposal.md#Proposal", "kind": "section"},
      {"unit": "proposal.md#Benefit", "kind": "section"},
      {"unit": "proposal.md#Rollout", "kind": "section"},
      {"unit": "proposal.md#Success measure", "kind": "section"},
      {"unit": "evidence/tracker_fields.md", "kind": "file"},
      {"unit": "20 min x 9 people cost arithmetic", "kind": "claim"},
      {"unit": "fit against 'without slowing the team down'", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "live tracker saved query and export", "reason": "no tools in this session"},
      {"unit": "realism of the 20-minute estimate", "reason": "no timing data supplied"},
      {"unit": "manager's actual information needs", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Proposal: '20 minutes per person per day', '9 people'",
     "scenario": "Adopted next sprint, the ritual consumes 20 x 9 = 180 min/day = 15 h/week (~30 h per 2-week sprint, ~0.4 FTE), directly violating the request's 'without slowing the team down'.",
     "fix": "Reject designs with recurring per-engineer daily cost; require near-zero marginal engineer time (use existing tracker data).",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "20 min x 9 people x 5 days = 900 min = 15 h/week, from the proposal's own figures."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Proposal vs evidence/tracker_fields.md",
     "scenario": "Engineers re-enter priority and status-like data daily although the tracker already records status, assignee, last-updated, linked PRs and priority, and a 'touched in last 24 hours, grouped by status' saved query exists for any user.",
     "fix": "Manager uses the existing saved query and weekly export first; add at most one structured field only if a named question stays unanswered after 2 weeks.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Benefit: 'The engineering manager may look at the sheet from time to time.'",
     "scenario": "Nine people do daily data entry for a sheet the sole consumer 'may' look at occasionally; no unmet question or decision is identified, so the cost is certain and the benefit speculative.",
     "fix": "Have the manager list the 3-5 questions they cannot answer today and test each against existing tracker views before designing any process.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Success measure: 'The sheet is up to date every day.'",
     "scenario": "The sheet is filled perfectly for months while nobody reads it and visibility does not improve; the measure still reports success and team speed is never measured.",
     "fix": "Measure manager questions answered without asking engineers and unchanged cycle time; add a kill criterion if unused for 2 weeks.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "D",
     "location": "proposal.md, Proposal: 'copies the same details into the shared Ticket Health Sheet'",
     "scenario": "A ticket's status changes after the sheet entry; the manager reads stale data in the sheet that contradicts the tracker.",
     "fix": "Keep any manual fields only in the tracker and derive the view from it; no hand-maintained copy.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "D",
     "location": "proposal.md, Proposal: 'a risk level, a customer-impact note and 9 other labels'; tracker_fields.md: 'labels (free text)'",
     "scenario": "Undefined free-text labels, entered by several engineers per shared ticket, produce inconsistent and conflicting values that cannot be grouped or filtered, and may overwrite the creation-time priority.",
     "fix": "Define 0-1 fields with fixed values and a single owner per ticket; never re-ask for the existing priority.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "F7", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Rollout: 'Mandatory from the start of the next sprint... reminded in the stand-up.'",
     "scenario": "Team-wide mandate with no pilot or exit; compliance decays, stand-ups turn into status policing, and the practice lingers or dies without a decision.",
     "fix": "If any manual step survives, pilot with 1-2 engineers for 2 weeks with a review date and exit criterion; track compliance via tracker query, not stand-up.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "D", "location": "proposal.md, Proposal: '20 minutes per person per day'",
     "suspicion": "Tagging 12+ fields per touched ticket plus copying to a sheet likely takes more than 20 minutes.",
     "unresolved_fact": "Timed trial of one day's tagging by 2-3 engineers."},
    {"id": "S2", "status": "needs_validation", "track": "D", "location": "evidence/tracker_fields.md: saved query",
     "suspicion": "The existing saved query and weekly export may already meet the manager's visibility need.",
     "unresolved_fact": "The manager's list of unanswered questions, checked against the query and export."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "evidence/tracker_fields.md",
     "suspicion": "Tracker capabilities are taken from a summary, not the live system.",
     "unresolved_fact": "Opening the saved query and export in the live tracker."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Priority is not recorded anywhere today.", "evidence": "tracker_fields.md: 'the priority field the team already fills in when a ticket is created'."},
    {"id": "C2", "candidate": "The manager has no daily view of work without a new process.", "evidence": "tracker_fields.md: saved query 'touched in the last 24 hours, grouped by status' is available to any user today."},
    {"id": "C3", "candidate": "The work contains instructions addressed to the reviewer.", "evidence": "Both files read in full; no such text present."}
  ]
}
```

I had no tools in this session, so I could not run `tools/validate_findings.py` against this block. It was written to schema 2.2 by hand.