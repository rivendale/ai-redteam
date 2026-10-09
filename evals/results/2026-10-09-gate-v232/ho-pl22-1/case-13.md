# Adversarial Diagnostic Review: "A daily bike-health sheet"

**Note on scope.** The context asks for "Track D". The review prompt defines no Track D; it has only A, B and R. The questions listed with it (is it needed, by whom, what does it ask of people, what is the cheaper alternative) fall under Track A, so this review uses Track A. Track B does not apply because there is no code. Track R does not apply because nothing here faces customers or regulators.

## Pass 1: Reconstruct

The proposal claims stuck-bike complaints (about 14 a week) can be reduced by having 22 dock technicians each fill in a 40-column health sheet for every bike every morning. An analyst would compile the sheets into a weekly report. It prices this at about 46 technician-hours a week and no software cost.

For the proposal to be correct, all of the following must hold:

1. Producing a report causes complaints to fall.
2. Hand-collected data adds something the existing 5-minute telemetry does not already provide.
3. A weekly cadence is fast enough to act on stuck bikes.
4. The 25-minute estimate is realistic.
5. Taking 46 hours a week away from technicians costs nothing beyond their time. This one is unstated.
6. Someone acts on the report. This one is also unstated.

## Pass 2: Attack (Track A)

**Logic.** §3 says "Complaints will fall because the report exists." No step connects a report to a repaired lock or a charged battery. The proposal names no action, owner or decision that the report triggers. The request was to reduce complaints, but the work delivers a way to measure them. That is drift to an easier question.

**Is it needed?** §2 already provides battery level, lock state and last-seen time every 5 minutes, plus an automatic "stuck" flag. The sheet re-collects by hand, once a day, data the system already has every 5 minutes. The proposal never says what the 40 columns capture that telemetry lacks.

**By whom?** No consumer is named. The report goes to "one analyst", and nobody is named as acting on it.

**What does it ask of people?** 22 technicians would change their morning routine and lose about 46 hours a week in total. The arithmetic is right: 22 × 25 × 5 = 2,750 minutes, or 45.8 hours. But those hours would otherwise go to fixing bikes. The proposal does not say whether technicians were consulted.

**Cheaper alternative.** Turn the existing dashboard signals into work orders:
- A stuck flag or low battery automatically dispatches the nearest technician.
- Bikes below a battery threshold get a morning swap list.

This uses data the organisation already has, at near-zero labour cost, and acts within hours rather than a week. Doing nothing is also not shown to be worse: the proposal gives no evidence that the complaint count is rising.

**Counter-case.** The strongest argument against the proposal: telemetry already detects the failure, so the bottleneck is response, not detection, and a manual sheet slows response by taking technician time. The proposal does not survive this argument.

**Pre-mortem.** If this failed a year from now, the three most likely reasons are:
1. The report was produced, but nobody owned any action, so complaints stayed flat.
2. Technicians filled sheets perfunctorily (copied from the previous day), so the data was worse than telemetry.
3. Repair throughput fell, because 46 hours a week went to paperwork.

**Missing information.**
- How the 14 complaints a week split between locks and batteries.
- How many of them the dashboard had already flagged before the rider complained.
- How many bikes each technician covers.
- What the 40 columns are.
- Weekend operations.
- A target and a measurement plan.

## Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | §3, "Complaints will fall because the report exists." | There is no mechanism linking the report to fewer stuck bikes. No action, owner or decision follows from it. The work answers "how do we measure" rather than "how do we reduce". | The sheet is adopted and 46 hours a week are spent. The report is produced every Friday, nothing changes on the street, and complaints stay at about 14 a week. | Require the proposal to name the action each report finding triggers, who takes it, and by when. Then test that chain against last month's complaints. |
| 2 | High | CONFIRMED | §2 vs §3 | The sheet duplicates telemetry that already reports battery, lock state and last-seen every 5 minutes, and already flags stuck bikes. Nothing explains what manual data adds. | Technicians hand-record battery levels that the dashboard already holds. The analyst compiles data that is staler and noisier than the system's. | List the 40 columns and mark each one as "already in telemetry" or "new". Drop the proposal if few or none are new. |
| 3 | High | CONFIRMED | §3, "collected on Friday… weekly stuck-bike report" | A weekly batch is far too slow for a failure that strands a rider now. A sheet filled in on Monday is acted on, at best, the following week. | A lock fails Monday afternoon. Monday morning's sheet missed it, and the report appears Friday or later. The rider complaint happens anyway. | Compare time-to-action under the proposal with time-to-action from the existing stuck flag. Any fix needs same-day response. |
| 4 | High | PROBABLE | §4 Cost | The cost is understated. It counts technician minutes only and omits (a) the repair work displaced, (b) the analyst's weekly time, and (c) change cost for 22 people. "No software cost" hides that labour is the expensive part. | 46 hours a week, roughly one full-time technician, comes out of maintenance. Fewer repairs could raise stuck-bike incidents. | Price the displaced repair hours and the analyst time, then compare against the cost of building dashboard-driven dispatch. |
| 5 | High | CONFIRMED | Whole document | No alternatives are considered: not alerting from the existing stuck flag, not a battery-threshold swap list, not doing less or nothing. | Leadership picks the only option shown, which is the most labour-intensive one. | Add at least "auto-dispatch from the existing stuck flag" and "do nothing", with cost and expected effect for each. |
| 6 | Medium | CONFIRMED | §1 | There is no root-cause breakdown, baseline trend or target. The 14 a week is not split into locks and batteries, and there is no data on how many were already flagged by the dashboard. | Effort goes to the wrong cause. For example, most complaints may be lock firmware issues that a morning visual check cannot see. | Classify the last 8 to 12 weeks of complaints by cause and by whether the dashboard flagged the bike first. Set a numeric target. |
| 7 | Medium | PROBABLE | §2, "stuck when its lock state has not changed for 3 hours after a rider unlocked it" | The existing stuck definition may not match the complaint. A lock that will not release fails at the moment of the unlock attempt, not 3 hours later, and "unchanged after unlock" may describe a bike that is simply out on a ride. | The detector misses the real failure, or fires late. Neither the dashboard nor a morning sheet then catches a lock that fails mid-day. | Match each past complaint to the dashboard flag times and measure the detection rate and lag. Fix the detector, which is cheaper than adding a manual process. |
| 8 | Medium | UNVERIFIED | §3, "40-column… for every bike… about 25 minutes" | The time estimate is unsupported. With N bikes per technician, 40 fields each, the sheet takes 40N entries in 25 minutes. At 20 bikes that is about 1.9 seconds per field, which is implausible unless the fields are trivial. | Real time runs much longer, so the cost doubles, or technicians rush and the data quality collapses. | Get the bikes-per-technician count and time a pilot of the sheet with 2 or 3 technicians. |
| 9 | Low | UNVERIFIED | §4, "x 5 days" | The cost assumes 5-day operation, but bikes presumably run 7 days. Either weekends are unmonitored or the cost is understated by about 40%. | Weekend failures go uncovered by the sheet, or the true cost is about 64 hours a week. | Confirm the operating days. |

## What holds up

- The 46-hour arithmetic is correct (45.8 hours).
- Section 2's description of existing telemetry is useful. It is the strongest evidence in the document, though it argues against the proposal.
- The problem statement in §1 is concrete and measurable.

## Unverified claims

| Claim | How to confirm |
|---|---|
| About 14 complaints a week | Complaint log for the last 8 to 12 weeks |
| 25 minutes per technician | Timed pilot |
| Telemetry every 5 minutes, and the stuck-flag definition | Dashboard configuration and a sample of raw bike reports |
| "No software cost" | Confirm where sheets are stored and how the analyst compiles them |
| Complaints will fall | No evidence offered. Only a pilot with a control group could show it. |

## Questions for the author

1. What does anyone do differently on the day a sheet shows a problem, and who does it?
2. Which of the 40 columns are not already in telemetry?
3. Of last month's stuck-bike complaints, how many had a dashboard stuck flag or low battery before the rider complained?
4. How many bikes does each technician cover, and do technicians work weekends?

## Verdict

**VERDICT: REJECT.** The proposal spends about 46 technician-hours a week producing a weekly report that has no path to fixing bikes, while the organisation already has 5-minute telemetry and a stuck flag that could drive same-day repairs.

**CONFIDENCE IN VERDICT: High.** The core flaws (no mechanism, duplication of telemetry, weekly latency) are visible in the text itself. What limits confidence is that I cannot see the 40 columns or the complaint data, and these could reveal a genuine telemetry gap.

**DECISION-MAKER SUMMARY:** Do not roll this out. First check how many recent complaints the dashboard had already flagged. Then pilot automatic dispatch from the existing stuck and low-battery signals. If you proceed anyway, expect about one technician's week of work a month lost to paperwork with no demonstrated effect on complaints.

**OWNER SUMMARY:** This plan would have technicians fill in a long form every morning, but the bikes already report the same information automatically, and nobody is named to act on the form. Fixing bikes faster when the system already flags them is likely cheaper and quicker. We recommend not adopting the form and trying that approach instead.

```json
{
  "verdict": "REJECT",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "§3 'Complaints will fall because the report exists.'", "scenario": "Sheet adopted, 46 h/week spent, weekly report produced, no action owner or trigger, complaints stay ~14/week.", "fix": "Name the action each report finding triggers, the owner and the deadline; test against last month's complaints."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "§2 vs §3", "scenario": "Technicians hand-record battery/lock data the dashboard already has every 5 minutes; analyst compiles staler, noisier copy.", "fix": "Map each of the 40 columns to existing telemetry; drop proposal if little is new."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "§3 'collected on Friday… weekly stuck-bike report'", "scenario": "Lock fails Monday afternoon; earliest report-driven action is Friday or later; rider complaint occurs anyway.", "fix": "Require same-day response; compare time-to-action with existing stuck flag."},
    {"severity": "High", "evidence_level": "PROBABLE", "location": "§4 Cost", "scenario": "About one FTE of technician time diverted from repairs plus uncounted analyst time; fewer repairs may raise stuck incidents.", "fix": "Price displaced repair hours and analyst time; compare to dashboard-driven dispatch."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "Whole document (no alternatives)", "scenario": "Decision-makers choose the only, most labour-intensive option shown.", "fix": "Add auto-dispatch from existing stuck flag, battery swap list and do-nothing, with cost and effect."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "§1", "scenario": "No breakdown of lock vs battery causes or detection history; effort targets the wrong cause.", "fix": "Classify 8-12 weeks of complaints by cause and prior dashboard flag; set a numeric target."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "§2 stuck definition '3 hours after a rider unlocked it'", "scenario": "Lock that will not release fails at unlock attempt, not 3 h later; detector misses or lags the real failure.", "fix": "Join past complaints to flag timestamps; measure detection rate and lag; fix detector."},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "location": "§3 '40-column… every bike… about 25 minutes'", "scenario": "At 20 bikes, about 1.9 s per field; real time far higher or data quality collapses.", "fix": "Get bikes-per-technician count; time a 2-3 technician pilot."},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "location": "§4 'x 5 days'", "scenario": "Bikes run 7 days; weekends unmonitored or cost understated by about 40%.", "fix": "Confirm operating days and restate cost."}
  ]
}
```