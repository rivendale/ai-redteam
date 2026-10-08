# Redteam review: "The daily ticket hygiene ritual"

**Reviewer note:** I had no tools and no subagent in this session, so this was one reviewer reading the supplied text only. I did not write the work, so there is no author-anchoring risk. Nothing was fetched or run, and every figure below is recomputed from the proposal's own numbers.

**VERDICT: REJECT.** The core mechanism costs about 15 engineer-hours a week, which contradicts the request's one explicit constraint ("without slowing the team down"). It also duplicates data the tracker already records and queries, for a manager who "may look at the sheet from time to time".

**CONFIDENCE: medium.** The main findings rest on the proposal's own words and arithmetic. Confidence is limited because I could not see what the manager actually cannot see today, the label list, or the sheet's design.

**INPUTS LEDGER**
- **Seen:**
  - The original request (verbatim).
  - context.md.
  - proposal.md.
  - evidence/tracker_fields.md.
- **Not seen:**
  - **The manager's specific visibility gaps** (the questions they cannot answer today). This matters because the need cannot be established without it.
  - **The list of "9 other labels" and the definitions of risk level and customer impact.** This matters for data quality.
  - **The Ticket Health Sheet layout.** This matters only a little.
  - **How the "20 minutes" was estimated.** This matters a little, because the verdict holds even at 5 minutes per person per day.

**COVERAGE**
- **Checked:**
  - proposal.md, every section: Proposal, Benefit, Rollout, Success measure.
  - evidence/tracker_fields.md: every field, the saved query and the weekly export.
  - Assumptions: the need, the cost, and that the data is not already available.
- **Not checked:** the manager's actual needs, the label taxonomy and the sheet design (none were supplied).

**SEATS AND GATE:** One same-session reviewer ran. No cross-vendor seats ran because the user did not ask for them and depth is standard. The material is not sensitive: an internal process proposal with no personal data.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | D | proposal.md, Proposal: "about 20 minutes per person per day", 9 people | The cost breaks the request's explicit constraint. | 9 × 20 min = 180 min a day = 15 h a week. That is about 0.375 of a full-time engineer (15/40), or roughly 690 h a year over 46 working weeks. Imposed every working day from next sprint, it slows the team by design. | Reject the daily manual ritual. Any replacement must state its per-person cost, with a target of near zero added daily effort. To reproduce, recompute 9 × 20 × 5 = 900 min/week. | a✓ b✓ c✓ d✓ |
| F2 | High | CONFIRMED | D | proposal.md, Proposal, compared with tracker_fields.md | It ignores a cheaper alternative that already exists, and it duplicates fields. The tracker already records status, assignee, last-updated, linked PRs and priority, and priority is already filled in at ticket creation. A saved "touched in the last 24 hours, grouped by status" query and a weekly spreadsheet export are available today. | Engineers re-enter priority and status the tracker already holds, and copy them into a sheet the export could produce automatically. Most of the 20 minutes buys nothing new. | Start from the existing saved query and export. Add only the fields that are truly missing (risk, customer impact), and set them once per ticket, not every day. | a✓ b✓ c✗ d✓ |
| F3 | High | CONFIRMED | D | proposal.md, Benefit: "The engineering manager may look at the sheet from time to time." | The need is not established. No question the manager cannot answer today is named, and the only consumer may use the sheet only occasionally. | The team spends 15 h a week maintaining a sheet the manager opens rarely. Visibility does not improve because nobody defined what was invisible. | Ask the manager for the 3 to 5 questions they cannot answer today. Then check each against the saved query and export before building anything. | a✓ b✓ c✗ d✓ |
| F4 | Medium | CONFIRMED | D | proposal.md, Success measure: "The sheet is up to date every day." | It measures compliance, not visibility. There is no measure of whether the manager's decisions improved and no signal that the effort has been abandoned or is wasted. | The sheet is kept perfectly up to date, the project is declared a success, and the manager still lacks the answers they needed. Rated Medium because the harm follows from F3. | Measure whether the manager can answer the named questions without asking anyone, plus the time the team spends on the process. | a✓ b✓ c✗ d✓ |
| F5 | Medium | PROBABLE | D | proposal.md, Rollout: "Mandatory … Engineers who skip a day are reminded in the stand-up." | It depends on a daily act of remembering, enforced by public reminders. Plans like this usually decay, and the reminders add stand-up time and social friction. | Compliance drops within a few sprints. Stand-up time goes to chasing the sheet, so the sheet goes stale and the stand-up gets slower. | Prefer data captured as a side effect of normal work, such as tracker fields set when a ticket is created or its status changes. | a✓ b✗ c✗ d✓ |
| F6 | Medium | PROBABLE | D | proposal.md, Proposal: "copies the same details into the shared 'Ticket Health Sheet'" | It creates two sources of truth. Details are entered in the tracker and then copied by hand into the sheet. | Tickets updated after an engineer fills in the sheet, or copy errors, make the sheet disagree with the tracker. The manager then acts on the wrong one. | Keep one source of truth (the tracker) and generate any sheet from the export. | a✓ b✗ c✗ d✓ |
| F7 | Medium | PROBABLE | D | proposal.md, Proposal: "a risk level, a customer-impact note and 9 other labels"; tracker_fields.md: "labels (free text)" | The labels are undefined and free text. Nine unnamed labels, plus risk and impact with no scale, entered by 9 people every day. | Each engineer interprets "risk" and the labels differently, so the aggregated view is noise. | Define each field, its allowed values and why the manager needs it. Drop any field with no named consumer. | a✓ b✗ c✗ d✓ |

## Needs validation

- **S1, how accurate "20 minutes" is.** The fact that would settle it is a timed trial or the author's basis for the estimate. The verdict does not depend on this: even 5 minutes is about 3.75 h a week across the team, with no stated benefit.
- **S2, whether the manager already uses the saved query or weekly export, and what it fails to show.** The manager's answer settles this, and it decides whether any new mechanism is needed at all.
- **S3, whether risk and customer impact matter to the manager's decisions.** These are the only two proposed fields that the tracker does not already hold.

## Refuted

- **R1, "The tracker gives no daily view of activity, so a daily ritual is needed."** This is refuted by tracker_fields.md: a saved query, "touched in the last 24 hours, grouped by status", is "available to any user today".

## What holds up

- The proposal correctly treats risk level and customer impact as missing. Neither appears among the tracker's automatic fields, so there may be a small, real gap there.
- Making the rule apply to everyone, with a defined start date, is at least explicit. The problem is what it imposes, not its clarity.

## Unverified claims

- **"About 20 minutes per person per day."** Confirm with a timed trial of a few engineers over several days.
- **"Better visibility into the state of work."** Confirm by naming the manager's questions and testing whether the sheet answers them better than the saved query and export do.

## Questions for the author

1. What specific questions can the manager not answer today with the saved query and the weekly export?
2. Which of the 12+ fields does the manager actually use, and for what decision?
3. How often will the manager read the output, and how did the author arrive at "from time to time"?

## Decision-maker summary

Do not adopt this. It costs about 15 engineer-hours a week, against a request to avoid slowing the team, and mostly re-copies data the tracker already has. Ask the manager what they cannot see today, then try the existing saved query and export, plus at most two well-defined ticket fields set once per ticket. Proceeding anyway buys a stale, duplicate spreadsheet at the cost of over a third of an engineer.

## Owner summary

This plan asks every engineer to spend about 20 minutes a day copying ticket details into a spreadsheet. Together that adds up to roughly two working days a week, which directly conflicts with the goal of not slowing the team down. Most of that information is already available in the ticket tool, so the better first step is to ask the manager what they actually cannot see and use what already exists.

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
    {"item": "Manager's specific visibility gaps", "status": "not_seen", "matters": true},
    {"item": "Definitions of the 9 other labels, risk level, customer-impact note", "status": "not_seen", "matters": true},
    {"item": "Ticket Health Sheet layout", "status": "not_seen", "matters": false},
    {"item": "Basis for the 20-minute estimate", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Internal process proposal; no personal, financial, health, credential or confidential client data."},
  "coverage": {
    "checked": [
      {"unit": "proposal.md", "kind": "file"},
      {"unit": "proposal.md#Proposal", "kind": "section"},
      {"unit": "proposal.md#Benefit", "kind": "section"},
      {"unit": "proposal.md#Rollout", "kind": "section"},
      {"unit": "proposal.md#Success measure", "kind": "section"},
      {"unit": "evidence/tracker_fields.md", "kind": "file"},
      {"unit": "Cost: 9 people x 20 min/day", "kind": "claim"},
      {"unit": "Need: manager lacks visibility not available from tracker", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "Manager's actual information needs", "reason": "not supplied"},
      {"unit": "Label taxonomy and field definitions", "reason": "not supplied"},
      {"unit": "Ticket Health Sheet", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Proposal: 'about 20 minutes per person per day' (9 people)",
     "scenario": "Mandatory daily ritual costs 9 x 20 = 180 min/day = 15 h/week (~0.375 FTE, ~690 h/year), directly contradicting the request's constraint 'without slowing the team down'.",
     "fix": "Reject the daily manual ritual; any replacement must state per-person cost and target near-zero added daily effort.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Recompute 9 people x 20 min x 5 days = 900 min = 15 h/week from the proposal's own figures."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Proposal vs evidence/tracker_fields.md",
     "scenario": "Engineers re-enter priority and status already held by the tracker and hand-copy them into a sheet, although a 'touched in last 24 hours, grouped by status' saved query and a weekly export already exist.",
     "fix": "Use the existing saved query and export; add only genuinely missing fields (risk, customer impact), set once per ticket rather than daily.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Compare the proposal's fields with tracker_fields.md: status, priority, assignee, last-updated, linked PRs and the 24-hour query are already present."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Benefit: 'The engineering manager may look at the sheet from time to time.'",
     "scenario": "No unmet question is named and the sole consumer may read the sheet only occasionally; the team spends 15 h/week on an artifact that does not change any decision.",
     "fix": "Elicit the manager's 3 to 5 unanswerable questions and test each against the existing query and export before building anything.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Read the Benefit section: it names no question, decision or frequency of use."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Success measure: 'The sheet is up to date every day.'",
     "scenario": "A fully up-to-date sheet is declared a success while the manager still lacks the answers they needed; no abandonment or waste signal exists.",
     "fix": "Measure whether the manager can answer the named questions unaided, and track time spent on the process.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "The success measure references only sheet freshness, not any manager outcome."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "D",
     "location": "proposal.md, Rollout: 'Engineers who skip a day are reminded in the stand-up.'",
     "scenario": "A daily remember-to-do-it step decays within a few sprints; stand-up time shifts to chasing the sheet, which slows the team further and leaves the sheet stale.",
     "fix": "Capture data as a side effect of normal work (tracker fields set on ticket creation or status change) instead of a daily manual step.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "Rollout relies solely on a daily manual action plus public reminders; no automation is described."},
    {"id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "D",
     "location": "proposal.md, Proposal: 'copies the same details into the shared Ticket Health Sheet'",
     "scenario": "Tickets updated after the sheet is filled in, or copy errors, make the sheet disagree with the tracker; the manager acts on the wrong one.",
     "fix": "Keep the tracker as the single source of truth; generate any sheet from the existing export.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "The proposal requires manual dual entry; nothing reconciles the sheet with the tracker."},
    {"id": "F7", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "D",
     "location": "proposal.md, Proposal: 'a risk level, a customer-impact note and 9 other labels'; tracker_fields.md: 'labels (free text)'",
     "scenario": "Nine engineers interpret undefined, free-text fields differently every day, so the aggregated view is noise.",
     "fix": "Define each field, its allowed values and its consumer; drop any field with no named use.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "The proposal names none of the 9 labels and gives no scale for risk or impact; tracker labels are free text."},
    {"id": "S1", "status": "needs_validation", "track": "D", "location": "proposal.md, Proposal: '20 minutes per person per day'",
     "suspicion": "The 20-minute estimate may be inaccurate.",
     "unresolved_fact": "A timed trial or the author's basis for the estimate (the verdict holds even at 5 minutes)."},
    {"id": "S2", "status": "needs_validation", "track": "D", "location": "evidence/tracker_fields.md, saved query and weekly export",
     "suspicion": "The existing query and export may already meet the manager's needs.",
     "unresolved_fact": "Whether the manager uses them and what specific information they fail to show."},
    {"id": "S3", "status": "needs_validation", "track": "D", "location": "proposal.md, Proposal: risk level and customer-impact note",
     "suspicion": "Risk and customer impact may be the only genuine gap.",
     "unresolved_fact": "Whether these fields inform any decision the manager makes."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The tracker gives no daily view of activity, so a daily ritual is needed.",
     "evidence": "tracker_fields.md: a saved query 'touched in the last 24 hours, grouped by status' is available to any user today."}
  ]
}
```