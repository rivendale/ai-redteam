# Adversarial Diagnostic Review: "Proposal: a daily bike-health sheet"

**Note on scope:** The context asks for "Track D", which this skill does not define (it has Tracks A, B and R). I applied **Track A (decisions and recommendations)**, which covers the questions the context lists: is it needed, who needs it, what it asks of people, and what the cheaper alternative is. Track B does not apply because there is no code. Track R does not apply because nothing here is customer-facing.

## Pass 1: Reconstruct

The proposal says riders report about 14 stuck bikes a week, from locks that won't release and dead batteries. It recommends that 22 dock technicians each spend about 25 minutes every morning filling in a 40-column paper sheet for every bike at their stations. An analyst would then compile the sheets into a weekly stuck-bike report each Friday. It claims complaints will fall "because the report exists", at a cost of about 46 technician-hours a week and no software cost.

For this to be correct, all of the following must be true:
1. Producing a report, by itself, causes bikes to be fixed sooner or fail less.
2. Hand inspection captures something the existing 5-minute telemetry does not.
3. A once-a-day morning snapshot, read weekly, catches failures in time to matter.
4. 46 technician-hours a week are worth more on paperwork than on repairs.

Two assumptions are unstated: that the weekly report has a reader who acts on it, and that 14 complaints a week is a real, current and meaningful baseline.

## Pass 2: Attack (Track A)

**Facts.** "About 14 times a week" has no source, date range or breakdown between lock and battery failures. The telemetry description in §2 is the proposal's own statement and is internally consistent. The arithmetic checks out: 22 × 25 min × 5 = 2,750 min ≈ 45.8 h. The 25-minute figure is unsupported. With 40 columns per bike, even 20 bikes per technician means 800 hand-written fields in 25 minutes, under 2 seconds per field.

**Logic.** §3 says "Complaints will fall because the report exists." That is the entire causal mechanism, and it does not hold. A report describes bikes; it does not repair them. Nothing names who reads the report, what decision it drives, or what action follows. The request was to *reduce* complaints. The work answers an easier question, how to *measure* bike health, which is drift.

**Assumptions that collapse it.** The proposal assumes hand inspection adds information. But §2 says battery level, lock state and last-seen time already arrive every 5 minutes, and the dashboard already flags stuck bikes. A technician eyeballing a battery gauge in the morning is a slower, less accurate copy of data the system already holds. That assumption is very likely false.

**Alternatives never considered.**
- (a) Act on the existing dashboard flag: send flagged bikes to the nearest technician the same day.
- (b) Generate the weekly report automatically from telemetry. This costs zero technician time.
- (c) Set a low-battery threshold that triggers a swap before the bike dies.
- (d) Tighten the 3-hour "stuck" threshold. A rider whose lock won't release complains within minutes, not hours.
- (e) Find the root cause of the lock failures, such as a specific model, firmware version or station.
- (f) Do nothing until someone establishes why already-flagged bikes are not being fixed.

Each of these is cheaper, and most are faster.

**Counter-case.** "Hand inspection catches physical faults that telemetry misses, such as a bent lock or a corroded contact." That is possible. But the case would support a *targeted* check of the few signals telemetry can't see, on bikes with complaint history. It does not support 40 columns × every bike × every day. The proposal does not make even this argument.

**Pre-mortem (one year on, it failed):**
1. The sheets were filled in, but nobody acted on the Friday report, so complaints didn't move.
2. Technicians, losing about 2 hours a week each, rushed or copied forward the sheets. The data became garbage and morale dropped.
3. Failures happen during the day and on weekends, but the sheet is a weekday-morning snapshot read once a week. The data was always 1 to 7 days stale.

**Incentives and bias.** "No software cost" frames the plan as free. In fact it moves about 46 hours a week, plus the analyst's time, onto people. That cost is invisible in a software budget but real in labour. There is no evidence that the technicians were consulted.

**Costs and reversibility.** The plan is reversible, since the sheets can be stopped. The ongoing cost is about 46 technician-hours a week plus unstated analyst hours, data entry or transcription, printing, and storage. The technicians bear the downside. They also lose repair time, which could *raise* stuck-bike counts.

**Missing information.**
- A complaint breakdown: lock vs battery, which stations, which bike models, time of day.
- How many dashboard "stuck" flags there are per week compared with complaints.
- Time from a dashboard flag to a repair today.
- How many bikes each technician covers.
- What the 40 columns are.
- Who owns the report, and what they will do with it.
- A target and a review date.

## Pass 3: Self-check

Every finding below points to a specific section. I downgraded the 25-minute estimate to PROBABLE, because the number of bikes per technician is unknown. I also kept the weekend-coverage point at PROBABLE, because I don't know the operating days. The most serious thing I might be missing is whether the dashboard flags are already being acted on. If they are, and 14 complaints a week is the residual, then the real problem is elsewhere, perhaps detection latency or hardware. The proposal gives no data on this either way.

---

**VERDICT: REJECT.** The plan costs about 46 technician-hours a week to duplicate data the telemetry already collects. It has no mechanism by which a weekly report reduces complaints.

**CONFIDENCE IN VERDICT: High.** The duplication and the missing causal link are visible in the text itself. Confidence is limited only by the absence of complaint and repair data, which could reveal a physical fault class that telemetry misses. Even that would justify a much smaller, targeted check, not this one.

### Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | §3 "Complaints will fall because the report exists." | No causal mechanism, and no owner or action tied to the report. | Sheets get filled and the report is built every Friday, but no bike is repaired sooner, so complaints stay at about 14 a week while 46 h a week is spent. | Name the action, its owner and the response time. Pilot it, and measure complaints against a baseline. |
| 2 | Critical | CONFIRMED | §2 vs §3 | The hand sheet duplicates telemetry (battery, lock state, last-seen every 5 min) and the existing "stuck" flag. | A technician records a battery level in the morning that the dashboard already logged 288 times that day. The new data adds nothing, and transcription errors add noise. | Build the stuck-bike report from telemetry automatically. Justify each manual column with a signal telemetry cannot see. |
| 3 | High | CONFIRMED | §3 "collected on Friday… weekly" | Feedback is 1 to 7 days late. A morning snapshot misses failures that happen during the day. | A lock fails Monday at noon. It is not on Monday's sheet. Tuesday's sheet records it, but no one reads it until Friday. Riders complain all week. | Use same-day dispatch from the dashboard flag instead of a weekly batch. |
| 4 | High | CONFIRMED | Whole proposal | Drift: it answers "how do we document bike health" instead of "how do we reduce complaints". No alternatives are considered. | The decision-maker approves the only option shown, while cheaper ones go unexamined: acting on flags, battery-swap thresholds, a tighter stuck threshold, root-cause analysis. | Add an options comparison that includes doing nothing and automated reporting, with cost and expected effect for each. |
| 5 | High | CONFIRMED | §4 "No software cost" | The cost is understated. It omits analyst time, sheet transcription and printing, and the opportunity cost of repair work lost. | 46 h a week of technician time is taken from repairs, so the backlog of stuck bikes grows. | Cost the full workflow in hours and money, including lost repair capacity. |
| 6 | Medium | PROBABLE | §3 "about 25 minutes… 40-column… every bike" | The time estimate is implausible for 40 fields per bike across a station's fleet. | At 20 bikes per technician that is 800 fields in 25 min (<2 s per field). The real time is higher, or the data is rushed and copied forward. | Time a pilot with 2–3 technicians, and record the number of bikes per technician. |
| 7 | Medium | CONFIRMED | §1 | No baseline source, failure breakdown, target or success measure. | There is no way to tell later whether the plan worked or whether complaints fell for other reasons. | Give the source and period for "14 a week", split by failure type and station, and set a target and a review date. |
| 8 | Medium | PROBABLE | §4 "x 5 days" | Weekend coverage is unclear if bikes run 7 days. | Weekend failures are never sheeted, leaving gaps in the report. | State the operating days and coverage. |
| 9 | Medium | CONFIRMED | §3 / stakes | It asks a lot of 22 technicians, with no consultation and no stated benefit to them. | Low compliance and poor data quality. Technicians resent paperwork that displaces repairs. | Consult technicians on which checks only a human can do. Size the burden to that. |
| 10 | Low | CONFIRMED | §2 "3 hours after a rider unlocked it" | The proposal doesn't ask whether the existing detection threshold is too slow. The rider complains long before the flag fires. | Bikes stay unflagged for up to 3 hours after a failed release. | Evaluate a shorter threshold, or a "release command sent, lock state unchanged within N minutes" rule. |

### What holds up
- The problem is real and worth reducing.
- The 46-hour arithmetic is correct for the inputs given.
- §2 accurately sets out that the organisation already has the data needed for a cheaper solution, which is the proposal's most useful paragraph.

### Unverified claims
- **"About 14 times a week":** confirm with complaint-log counts by week, failure type and station.
- **"About 25 minutes per technician":** confirm with a timed pilot.
- **Telemetry every 5 minutes and the 3-hour stuck flag:** confirm against the dashboard configuration and a sample of flags.
- **"No software cost":** confirm the full cost, including analyst and transcription time.

### Questions for the author
1. When the dashboard flags a bike as stuck today, what happens, and how long until it is fixed?
2. Which of the 40 columns captures something telemetry cannot?
3. Who reads the weekly report, and what will they do differently because of it?
4. What share of complaints are lock failures vs dead batteries, and are they concentrated by station or bike model?

### Decision-maker summary
Do not approve. The plan spends about 46 technician-hours a week re-recording data the system already collects, and it gives no way for a weekly report to reduce complaints. Ask instead for a short proposal that acts on the existing stuck-bike alerts the same day and adds an automated battery-swap trigger, measured against a sourced complaint baseline.

### Owner summary
This plan asks every technician to fill in a long paper form each morning, but the bikes already report the same information automatically, and a report on its own won't fix any bikes. It would cost nearly fifty staff hours a week that could go into repairs instead. A cheaper and faster approach is to send technicians to bikes the system already flags as stuck or low on battery, and track whether complaints drop.

```json
{
  "verdict": "REJECT",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "§3 'Complaints will fall because the report exists.'", "scenario": "Sheets filled and report built weekly, but no owner or action is defined, so no bike is fixed sooner and complaints stay ~14/week while 46 h/week is spent.", "fix": "Name the action, owner and response time the report drives; pilot and measure complaints against a baseline."},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "§2 vs §3", "scenario": "Technicians hand-record battery and lock state already reported every 5 minutes and already flagged as stuck on the dashboard; no new information, added transcription error.", "fix": "Generate the stuck-bike report from telemetry; justify each manual column by a signal telemetry cannot capture."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "§3 'collected on Friday… weekly stuck-bike report'", "scenario": "A lock failing midday Monday is missed by that morning's sheet and not reviewed until Friday; riders keep hitting it all week.", "fix": "Replace the weekly batch with same-day dispatch from the dashboard stuck flag."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "Whole proposal", "scenario": "The proposal measures bike health instead of reducing complaints and presents one option; cheaper alternatives (act on flags, battery-swap threshold, tighter stuck threshold, root-cause analysis, do nothing) are never weighed.", "fix": "Add an options comparison including do-nothing and automated reporting, with cost and expected effect."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "§4 'No software cost'", "scenario": "Analyst, transcription and printing time are omitted, and 46 technician-hours/week leave repair work, which can increase stuck bikes.", "fix": "Cost the full workflow, including lost repair capacity."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "§3 'about 25 minutes… 40-column… every bike'", "scenario": "At ~20 bikes per technician, 800 fields in 25 minutes is under 2 s per field; either time overruns or data is rushed and copied forward.", "fix": "Time a pilot with 2-3 technicians and state bikes per technician."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "§1", "scenario": "No source, period, lock/battery split, target or success measure for '14 times a week', so the outcome cannot be judged.", "fix": "Source the baseline, break it down by failure type and station, set a target and review date."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "§4 'x 5 days'", "scenario": "If bikes run 7 days, weekend failures are never sheeted.", "fix": "State operating days and coverage."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "§3, stakes in context", "scenario": "22 technicians take on ~2 h/week of paperwork without consultation or benefit to them, leading to low compliance and poor data.", "fix": "Consult technicians on which checks only a human can do and size the burden to those."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "§2 'not changed for 3 hours after a rider unlocked it'", "scenario": "A rider complains within minutes of a failed release, but the bike is not flagged for up to 3 hours.", "fix": "Evaluate a shorter threshold or a rule keyed to release command vs lock-state change within minutes."}
  ]
}
```