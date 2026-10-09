# Adversarial Diagnostic Review: "Proposal: a daily bike-health sheet"

**Note on track:** The context asks for "Track D". The pasted skill defines only Tracks A, B and R, so I applied Track A (decisions and recommendations) together with the four questions the context names: is it needed, by whom, what it asks of people, and what the cheaper alternative is. Findings about the burden on technicians are tagged D in the JSON.

## Pass 1: Reconstruct

The proposal says riders report about 14 stuck bikes a week. Its fix is that 22 technicians each spend about 25 minutes every morning filling in a 40-column paper sheet for every bike. An analyst then turns the sheets into a weekly report, and "complaints will fall because the report exists." For this to work, the following must all be true:

1. A report, by itself, causes repairs to happen.
2. A manual morning inspection detects stuck-bike defects that the 5-minute telemetry does not.
3. A weekly cycle is fast enough to prevent complaints.
4. 46 technician-hours a week is a reasonable price for this.
5. No cheaper route exists.

The unstated assumption is that someone acts on the report. Nobody is named to do so.

## Pass 2: Attack (summary)

- **Facts.** The 14-a-week figure has no source and no split between locks and batteries. The cost arithmetic is correct: 22 × 25 × 5 = 2,750 minutes ≈ 45.8 hours.
- **Logic.** The step from "report exists" to "complaints fall" has no mechanism behind it.
- **Alternatives.** The proposal never considers alerting technicians from the existing dashboard "stuck" flag. It also never considers adding a low-battery threshold alert, analysing the 14 weekly complaints for root cause, or doing nothing.
- **Counter-case.** The data the sheet would collect already arrives every 5 minutes. A rule that routes the existing flag to the nearest technician costs a fraction of 46 hours and acts within hours, not days. The proposal does not survive this.
- **Pre-mortem.** If this fails, the likely reasons are:
  - The report is produced but nobody owns acting on it.
  - The sheets are filled in by rote or skipped, so the data quality is poor.
  - Defects arise after the morning check, so the sheet misses them.
- **Costs and reversibility.** The proposal is reversible, but technicians bear the whole cost. Their 25 minutes a day comes out of repair time, and they were not consulted.

## Pass 3: Self-check

- The work contains no text addressed to the reviewer.
- I re-examined the Critical finding (#1) from the strongest defender's position. The defence would be: "Obviously the report informs repair priorities." The proposal never says this, names no owner, and states the causal claim outright. The finding survives.
- **Same-root-cause search:** I looked across sections 1–4 for any action step, owner or target. I found none.
- **What I might still be missing:** whether the dashboard's "stuck" flag is itself broken or ignored. If it is, the real fix lies there, and the proposal never examines it.

---

**VERDICT: REJECT.** The sheet duplicates telemetry the organization already has, delivers it a week late, and has no step that turns information into a repaired bike. The problem statement is valid. The proposed solution is not.

**CONFIDENCE IN VERDICT: high.** It is limited only by not having seen the dashboard or the complaint data. Neither could rescue the missing action step.

**COVERAGE:**

| File | Status |
|---|---|
| request.md | checked |
| context.md | checked |
| proposal.md, §1–4 | checked |

### FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | §3: "Complaints will fall because the report exists." | There is no mechanism from report to repair. No owner, action, SLA or target is named. | The report is produced every Friday, nobody is assigned to act on it, and complaints stay at about 14 a week while 46 hours a week are spent. | Name who acts on which signal, within what time, and a measurable complaint target. Otherwise drop the proposal. | y/y/y/y |
| 2 | High | CONFIRMED | §2 vs §3 | The sheet re-collects by hand what telemetry already reports every 5 minutes: battery level, lock state, and a "stuck" flag. The cheaper alternative, alerting from the existing flag, is never considered. | A bike shows "stuck" on the dashboard at 10:00. The sheet records it the next morning and the analyst sees it on Friday. The automated signal was available days earlier at no labour cost. | Compare against routing the dashboard "stuck" flag and a low-battery threshold to the nearest technician, and against doing nothing. Justify any remaining manual columns individually. | y/y/n/y |
| 3 | High | CONFIRMED | §3: "collected on Friday… weekly stuck-bike report" | The weekly batch is too slow for a defect that strands a rider now. | A battery dies on Monday afternoon. Monday's sheet did not catch it and the next sheets are not analysed until Friday. Every rider who picks that bike until then can complain. | Any detection must feed same-day dispatch. A weekly report can at most be a trend view. | y/y/n/y |
| 4 | Medium | CONFIRMED | §4 | The cost is understated. It omits analyst time, sheet collection and transcription, and the repair work displaced by 25 minutes a day. "No software cost" hides labour standing in for software. 46 hours a week for about 14 complaints is over 3 technician-hours per complaint, before any reduction. | Leadership approves on a cost figure missing perhaps 30–50% of the true labour, and repair throughput drops. | Cost it fully: technicians, analyst, collection, and displaced repairs. Compare against the alert option. | y/y/n/y |
| 5 | Medium | CONFIRMED (by absence) | §1 | There is no baseline source, no breakdown by cause (lock vs battery), and no target. The problem is never diagnosed before a solution is chosen. | If most complaints are from one lock model or one station, a fleet-wide daily sheet misallocates 46 hours a week. | Analyse 4–8 weeks of complaints by cause, bike and station first. Set a numeric target and a review date. | y/y/n/y |
| 6 | Medium | CONFIRMED (by absence) | §3 | The proposal changes the morning routine of 22 technicians without their input or a pilot. It asks a lot of people for an unproven gain. | Technicians fill in 40 columns by rote to finish on time. Data quality collapses and the report misleads. | Consult technicians and pilot on a few stations with a control group before any rollout. | y/y/n/y |

### NEEDS VALIDATION

- **Can a morning inspection of a parked bike detect a lock that fails to release for a rider?** This is settled by whether the lock fault reproduces at rest, or only under an unlock command.
- **Is 25 minutes realistic for 40 columns per bike?** This is settled by bikes per technician. Even 15 bikes would mean 600 entries in 25 minutes, or 2.5 seconds per entry.
- **Does the dashboard "stuck" flag cover dead batteries, and does it fire correctly?** The definition in §2 ("lock state has not changed for 3 hours after a rider unlocked it") is ambiguous. This is settled by the flag's logic and its hit rate against actual complaints.
- **Is the existing flag already being acted on?** If it is, the gap is elsewhere. If it is not, the fix is routing it. This is settled by current ops practice.

### REFUTED

- **Arithmetic error in §4.** 22 × 25 × 5 = 2,750 minutes = 45.8 hours, so "about 46 hours" is correct.

### WHAT HOLDS UP

- The problem framing in §1 is legitimate.
- The description of existing telemetry in §2 is the strongest part of the document, and it undercuts the proposal.
- The cost arithmetic is correct as far as it goes.

### UNVERIFIED CLAIMS

| Claim | How to confirm |
|---|---|
| "About 14 times a week" | Complaint log export |
| 5-minute telemetry cadence | Dashboard configuration |
| 3-hour stuck rule | Dashboard flag logic |
| 25 minutes per technician | Timed pilot |
| "Complaints will fall" | A/B pilot with a control group |

### QUESTIONS FOR THE AUTHOR

1. Who acts on the report, and what do they do?
2. Which of the 40 columns does telemetry not already capture, and do any of them predict stuck bikes?
3. Why not alert technicians from the existing "stuck" flag?
4. What share of the 14 weekly complaints are locks and what share are batteries?

### DECISION-MAKER SUMMARY

Do not approve the daily sheet. Its stated mechanism ("the report exists") does not repair bikes, and its data already arrives automatically every 5 minutes. Ask instead for a complaint root-cause breakdown and a costed option that routes the existing dashboard "stuck" and low-battery signals to technicians the same day. Proceeding anyway costs about 46 or more technician-hours a week with no named action that would reduce complaints.

### OWNER SUMMARY

The plan would have technicians spend nearly an hour a week each, about 46 hours across the team, writing down bike conditions that the bikes already report automatically. The results would only be reviewed weekly, and nobody is assigned to fix what they show. A cheaper and faster approach is to send the existing automatic "stuck bike" alerts straight to technicians, after first checking what is actually causing the complaints.

```json
{
  "schema_version": "2.3",
  "verdict": "REJECT",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "proposal.md", "status": "seen", "matters": true},
    {"item": "ops dashboard / stuck-flag logic", "status": "not_seen", "matters": true},
    {"item": "complaint log", "status": "not_seen", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "proposal.md §1 problem", "kind": "section"},
      {"unit": "proposal.md §2 existing telemetry", "kind": "section"},
      {"unit": "proposal.md §3 proposal", "kind": "section"},
      {"unit": "proposal.md §4 cost", "kind": "section"},
      {"unit": "report causes complaint reduction", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "dashboard stuck-flag behaviour", "reason": "not_supplied"},
      {"unit": "complaint data by cause", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "A",
     "location": "proposal.md §3: 'Complaints will fall because the report exists.'",
     "scenario": "Weekly report produced with no named owner or action; complaints stay ~14/week while ~46 h/week are spent.",
     "fix": "Name who acts on which signal, within what time, and a numeric complaint target; otherwise withdraw.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "§1-§4 for any owner, action step, SLA or target", "found": "none"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "proposal.md §2 vs §3",
     "scenario": "Dashboard flags a stuck bike at 10:00; the sheet records it next morning and the analyst sees it Friday. The automated signal was available days earlier at zero labour cost.",
     "fix": "Evaluate routing the existing stuck flag and a low-battery threshold to technicians, and doing nothing; justify any remaining manual columns individually.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "§3 sheet columns vs §2 telemetry fields", "found": "battery and lock state duplicated; the other columns are unspecified"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "proposal.md §3: 'collected on Friday... weekly stuck-bike report'",
     "scenario": "Battery dies Monday afternoon; it is not seen until the next sheets are analysed Friday, so riders hit it all week.",
     "fix": "Detection must drive same-day dispatch; keep any weekly report as a trend view only.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "any same-day path in §3", "found": "none"}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "proposal.md §4",
     "scenario": "Approval is based on technician minutes only, omitting analyst, collection and transcription time and displaced repair work; >3 technician-hours per complaint.",
     "fix": "Full labour costing compared against the alert-routing option.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "proposal.md §1",
     "scenario": "If complaints cluster on one lock model or one station, a fleet-wide daily sheet misallocates effort.",
     "fix": "Root-cause the complaint log by cause, bike and station; set a numeric target and a review date.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md §3: 'Every morning each dock technician fills in a 40-column... sheet'",
     "scenario": "22 technicians fill 40 columns by rote under time pressure; data quality collapses and the report misleads.",
     "fix": "Consult technicians; pilot on a few stations with a control group before rollout.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "NV1", "status": "needs_validation", "location": "proposal.md §3",
     "suspicion": "A morning at-rest inspection may not detect locks that fail only on an unlock command.",
     "unresolved_fact": "Whether lock faults reproduce at rest."},
    {"id": "NV2", "status": "needs_validation", "location": "proposal.md §3",
     "suspicion": "25 minutes for 40 columns per bike may be unrealistic.",
     "unresolved_fact": "Bikes per technician."},
    {"id": "NV3", "status": "needs_validation", "location": "proposal.md §2",
     "suspicion": "Stuck-flag definition is ambiguous and may not cover dead batteries or may not fire correctly.",
     "unresolved_fact": "Flag logic and its hit rate against actual complaints."},
    {"id": "NV4", "status": "needs_validation", "location": "proposal.md §2",
     "suspicion": "The existing stuck flag may simply be unrouted or ignored.",
     "unresolved_fact": "Current ops handling of dashboard stuck flags."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Arithmetic error in §4 cost", "evidence": "22 x 25 x 5 = 2750 min = 45.8 h, so 'about 46 hours' is correct."}
  ]
}
```