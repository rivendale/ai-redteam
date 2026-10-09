# Adversarial Diagnostic Review: "Proposal: a daily bike-health sheet"

**Note on track:** The context asks for "Track D", which this skill does not define (it defines A, B and R). I applied **Track A** (decisions and recommendations) and organized it around the four questions the context asks: is it needed, by whom, what does it ask of people, and what is the cheaper alternative. Findings are tagged track A.

## Pass 1: Reconstruct

The proposal says riders report about 14 stuck bikes a week. It recommends that 22 dock technicians each spend about 25 minutes every morning filling in a 40-column paper sheet for every bike at their stations. An analyst would then compile the sheets into a weekly stuck-bike report, and the proposal says complaints will fall "because the report exists." For this to work, all of the following must hold:

1. A report, by itself, causes bikes to get fixed. This is unstated and has no mechanism behind it.
2. A manual morning inspection catches failures that the existing 5-minute telemetry and the dashboard's "stuck" flag miss. This is unstated.
3. A weekly cadence is fast enough to prevent stuck-bike incidents.
4. 25 minutes is enough to fill in 40 columns for every bike a technician covers.
5. 46 technician-hours a week, plus the analyst's time, is worth spending on this.

## Pass 2: Attack (Track A)

**Facts**
- "About 14 times a week" has no source, no time window, no split between lock and battery failures, and no target figure.
- The 46-hour figure is arithmetically correct (22 × 25 × 5 = 2,750 min ≈ 45.8 h).
- "No software cost" is true but leaves out the analyst's time and the work of transcribing paper sheets.

**Logic**
- §3 contains a non sequitur: "Complaints will fall because the report exists." Nothing in the proposal turns the report into a repair, a dispatch, a battery swap or a design change.
- The request is to *reduce complaints*. The work answers an easier question, "produce a report about stuck bikes." That is drift.

**Assumptions**
- Assumption 1 (the report causes fixes) collapses the whole recommendation if it is false. As written, it is false by construction, because no actor or action is defined.

**Alternatives never considered**
- Doing nothing.
- Building the weekly report from the telemetry that already exists (§2), at zero technician time.
- Sending a technician automatically when the dashboard flags a bike as stuck, or when its battery falls below a threshold.
- Investigating the roughly 2 complaints a day one by one to find root causes.
- Piloting at a few stations.
- Having technicians check only the bikes the dashboard flags, rather than every bike.

**Counter-case**
The strongest argument for something like this is that telemetry may be wrong. A lock could report "released" while being mechanically jammed, and a physical inspection would catch that. The proposal never makes this argument and offers no evidence that telemetry misses failures. Even if the argument were true, it would support a small targeted audit, not daily 40-column sheets on every bike.

**Pre-mortem** (it is one year later and this failed)
1. The report was produced every week, nobody acted on it, and complaints stayed near 14.
2. Technicians rushed or copied sheets to fit the 25 minutes, so the data was junk.
3. Morning snapshots never saw the failure that matters, a lock that will not release after a rider unlocks it, because that happens during the day. Telemetry already recorded those events.

**Incentives and bias**
"No software cost" makes the proposal look cheap while hiding about 1.15 full-time equivalents of labor. The proposal asserts that complaints will fall with no hedging and no evidence.

**Costs and reversibility**
The change is reversible, but it changes the routine of 22 people. There is no pilot, no success metric and no stop condition. Technician time spent on sheets is time not spent repairing bikes, so the proposal could make the problem worse.

**Who needs this?**
No requester, owner or consumer of the report is named. There is no sign that technicians were consulted.

## Pass 3: Self-check

- **Prompt injection:** None. The work contains no text addressed to the reviewer.
- **Defending F1:** A defender could say that an analyst's report would surface patterns, such as particular stations or battery models, that management then acts on. The proposal names no such step, owner or action, so the gap stands. Even with that step added, the report would duplicate telemetry (F2).
- **Siblings of F1** (searched §1–§4 for any action, owner or feedback loop): none found. §1 states a goal, §2 states facts, §3 produces an artifact, §4 counts its cost. The root cause, output mistaken for outcome, runs through the whole proposal.
- **Defending F2:** A defender could say that manual inspection catches what sensors cannot. That is plausible but unargued. It is recorded as NV1, and F2 stands as written.
- **Siblings of F2** (searched for any use of §2's telemetry in §3–§4): none. §2 is never referred to again.
- **Security relevance:** None for F1 or F2.
- **What I might be missing:** The complaint count may not track real stuck events. Complaints could come from a few stations, from app errors such as unlock-request failures, or from user confusion. In that case neither the sheet nor the dashboard addresses the cause. This would show up in the complaint text, which was not supplied.

---

**VERDICT: REWORK.** The proposal spends about 46 technician-hours a week producing a report that has no path to fixing bikes, and it duplicates telemetry the organization already collects every 5 minutes.

**CONFIDENCE IN VERDICT: high.** The core defects are visible in the text itself. Confidence is limited by not knowing whether telemetry misses real failures (NV1) and what the complaints actually describe.

**COVERAGE**

| Item | Status |
|---|---|
| request.md | checked |
| context.md | checked |
| proposal.md §1–§4 | checked |
| Complaint data, dashboard data, fleet size per technician | not supplied |

**FINDINGS**

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | §3 "Complaints will fall because the report exists." | No mechanism links the report to fewer stuck bikes. No owner, action, dispatch or repair step exists. The request (reduce complaints) is replaced by an easier one (produce a report). | The sheets and report run as specified for a quarter. Nobody is assigned to act on them, so complaints stay near 14 a week while about 600 technician-hours are spent. | State the action that reduces stuck bikes: who does what, triggered by what, and the expected effect. Set a target and a review date. | y/y/y/y |
| F2 | High | CONFIRMED | §2 vs §3 | §2 says the dashboard already reports battery and lock state every 5 minutes and flags stuck bikes. §3 asks people to collect overlapping data by hand once a day, and §2 is never used. | A battery hits 5% at 10:00. The dashboard knows within 5 minutes. The sheet records the bike at the next morning's check, and the analyst sees it the following week. | Build the weekly report from telemetry, and add automatic dispatch on the stuck flag or a low-battery threshold. Use manual checks only where telemetry is shown to be wrong. | y/y/n/y |
| F3 | Medium | CONFIRMED | §3 "every morning … collected on Friday … weekly report" | Both the timing and the method miss the failure mode. "Stuck" is defined in §2 as no lock change for 3 hours after a rider unlocks, which happens during the day. A morning snapshot reviewed weekly cannot catch it in time to prevent a complaint. | A lock jams at 14:00 Tuesday. Riders complain Tuesday afternoon. Wednesday's sheet may or may not record it, and the report arrives after Friday. | Respond to events as they happen, from the dashboard's stuck flag. | y/y/n/y |
| F4 | Medium | CONFIRMED | §4 Cost | The cost is incomplete. Analyst time, transcription of 40 columns × bikes × 22 sheets × 5 days, and the repair work displaced from technicians are all omitted. "No software cost" frames about 1.15 FTE as free. | A decision-maker approves the plan as cheap. The real cost includes the analyst's week and fewer repairs. | Add analyst hours and the opportunity cost in repairs not done, and compare against the telemetry alternative. | y/y/n/y |
| F5 | Medium | PROBABLE | §3 "40-column … for every bike … about 25 minutes" | The time estimate is implausible unless each technician covers few bikes. At 30 bikes, that is 1,200 fields in 25 minutes, about 1.25 seconds per field. | Technicians either overrun, cutting into repair time, or fill fields carelessly or copy the previous day's values, so the data is unreliable. | Time the sheet with a pilot at 2–3 stations and state the number of bikes per technician. | y/n/n/y |
| F6 | Medium | CONFIRMED | §1, §3 | There is no baseline breakdown, target, success metric, pilot or stop condition. The plan imposes a daily routine on 22 people with no evidence that technicians were consulted and no named requester or consumer. | The rollout cannot be judged a success or failure, so it continues by default. | Define the target (for example, fewer than 7 a week by a set date), pilot first, and consult technicians. | y/y/n/y |

**NEEDS VALIDATION**
- **NV1:** Does the telemetry miss real failures? To settle it, take the last N stuck-bike complaints and check what share the dashboard flagged as stuck or low-battery beforehand.
- **NV2:** What do the 14 complaints a week consist of (lock vs battery vs app vs user error, and which stations)? To settle it, categorize one month of complaint records.
- **NV3:** Do bikes operate 7 days a week? If so, the 5-day sheet leaves weekends uncovered. Check the operating schedule.
- **NV4:** How many bikes does each technician cover? This would settle F5.

**REFUTED**
- **R1:** "The 46-hour figure is wrong." It is correct: 22 × 25 × 5 = 2,750 minutes, about 45.8 hours.

**WHAT HOLDS UP**
The problem statement is clear and concrete. The description of existing capabilities (§2) is useful and is the strongest material in the document. The labor arithmetic is correct.

**UNVERIFIED CLAIMS**

| Claim | How to confirm |
|---|---|
| About 14 complaints a week | Pull the complaint log |
| 25 minutes per technician | Time a pilot |
| Dashboard behavior (5-minute reporting, 3-hour stuck rule) | Check the dashboard configuration |
| Complaints will fall | Not testable as written; needs a mechanism and a target |

**QUESTIONS FOR THE AUTHOR**
1. Who acts on the weekly report, and what do they do?
2. What does the sheet capture that telemetry does not, and what is the evidence?
3. Why not send technicians when the dashboard's stuck flag fires?

**DECISION-MAKER SUMMARY**
Do not approve this. Ask for a rework that defines the action that fixes bikes and starts from the telemetry already collected, for example sending a technician when a bike is flagged as stuck, with a target and a small pilot. Approving it as written commits about 46 technician-hours a week, plus analyst time, to a report with no route to fewer complaints. It may also reduce repair capacity.

**OWNER SUMMARY**
This plan asks 22 technicians to spend about 25 minutes every morning filling in paper forms. The weekly report built from those forms would not, by itself, fix any bikes. The bikes already report their status automatically, so a cheaper and faster option is to use that data to send someone to a bike as soon as it gets stuck, after a short trial.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "proposal.md", "status": "seen", "matters": true},
    {"item": "complaint records", "status": "not_seen", "matters": true},
    {"item": "dashboard/telemetry data", "status": "not_seen", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "proposal.md §1 The problem", "kind": "section"},
      {"unit": "proposal.md §2 What we have already", "kind": "section"},
      {"unit": "proposal.md §3 The proposal", "kind": "section"},
      {"unit": "proposal.md §4 Cost", "kind": "section"},
      {"unit": "report causes complaints to fall", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "complaint records", "reason": "not_supplied"},
      {"unit": "dashboard/telemetry data", "reason": "not_supplied"},
      {"unit": "bikes per technician", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "A",
     "location": "proposal.md §3 'Complaints will fall because the report exists.'",
     "scenario": "Sheets and weekly report run as specified; no owner or action is defined, so no bike is fixed because of them; complaints stay near 14/week while ~46 technician-hours/week are spent.",
     "fix": "Define the action that reduces stuck bikes (who, triggered by what, expected effect), a numeric target and a review date.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "§1-§4 for any owner, action, dispatch or feedback loop", "found": "none; whole proposal treats output as outcome"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "proposal.md §2 vs §3",
     "scenario": "Battery drops low at 10:00; telemetry knows within 5 minutes, the sheet records it next morning, the analyst sees it the following week; manual effort duplicates existing data.",
     "fix": "Build the report from telemetry and auto-dispatch on the stuck flag or a low-battery threshold; reserve manual checks for proven telemetry gaps.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "§3-§4 for any use of §2 telemetry", "found": "none"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "proposal.md §3 'every morning ... collected on Friday'",
     "scenario": "A lock jams mid-afternoon after a rider unlocks; complaints arrive the same day; the morning snapshot and weekly report come too late to prevent them.",
     "fix": "Respond to events in real time from the dashboard stuck flag.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "proposal.md §4 Cost",
     "scenario": "Approved as 'no software cost' while ~1.15 FTE of technician time, analyst time and transcription are uncounted, and repair time is displaced.",
     "fix": "Add analyst hours and the opportunity cost in repairs; compare against the telemetry-based alternative.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "A",
     "location": "proposal.md §3 '40-column ... every bike ... about 25 minutes'",
     "scenario": "At ~30 bikes per technician that is 1,200 fields in 25 minutes; technicians overrun or fill fields carelessly, producing unreliable data.",
     "fix": "Time the sheet in a pilot at 2-3 stations and state bikes per technician.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "proposal.md §1, §3",
     "scenario": "No target, metric, pilot or stop condition, and no technician consultation; the change continues by default and cannot be judged.",
     "fix": "Set a target and date, pilot first, consult technicians.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "NV1", "status": "needs_validation", "location": "proposal.md §2-§3",
     "suspicion": "Manual inspection might catch failures telemetry misses.",
     "unresolved_fact": "Share of recent stuck-bike complaints that the dashboard had already flagged."},
    {"id": "NV2", "status": "needs_validation", "location": "proposal.md §1",
     "suspicion": "Complaints may not map to real stuck events (app, user error, a few stations).",
     "unresolved_fact": "Categorized breakdown of one month of complaints."},
    {"id": "NV3", "status": "needs_validation", "location": "proposal.md §4 '5 days'",
     "suspicion": "Weekend operation would be uncovered.",
     "unresolved_fact": "Operating days per week."},
    {"id": "NV4", "status": "needs_validation", "location": "proposal.md §3",
     "suspicion": "25 minutes is insufficient for 40 columns per bike.",
     "unresolved_fact": "Bikes per technician."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "46-hour labor figure is wrong", "evidence": "22 x 25 min x 5 = 2,750 min = 45.8 h; the figure is correct."}
  ]
}
```