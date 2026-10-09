# Adversarial Diagnostic Review: "Proposal: a daily bike-health sheet"

**Note on scope:** The context asks for "Track D", which is not defined in this review prompt. Its four questions (is it needed, by whom, what does it ask of people, what is the cheaper alternative) map onto **Track A** (decisions and recommendations), so I applied Track A and answered each of those four questions explicitly. Tracks B and R do not apply: there is no code, and nothing customer-facing.

## Pass 1: Reconstruct

The proposal claims that riders report about 14 stuck bikes a week, from locks that won't release or dead batteries. It recommends that 22 technicians each spend about 25 minutes every weekday morning filling in a 40-column paper sheet for every bike at their stations. One analyst would then compile the sheets into a weekly stuck-bike report, and the proposal asserts complaints will fall "because the report exists."

For this to be correct, several things must hold:
- (a) The manual sheet captures information that predicts or prevents stuck bikes and that the existing 5-minute telemetry does not.
- (b) Someone acts on the weekly report fast enough to fix bikes before riders hit them.
- (c) 25 minutes is enough to fill 40 columns for every bike.
- (d) About 46 technician-hours a week is better spent on this than on repairs.

Unstated assumptions:
- Technicians currently have 25 idle morning minutes.
- The complaints come from conditions visible on a morning inspection.
- Complaints cluster on weekdays, since the sheet runs only 5 days.

## Pass 2: Attack (Track A)

**Is it needed?** Not as designed. §2 says the dashboard already reports battery level, lock state and last-seen time every 5 minutes, and already flags stuck bikes. These are the same two failure modes named in §1. The proposal never says what the hand sheet would show that the telemetry doesn't.

**By whom?** No consumer of the report is named. An analyst builds it, but nobody is assigned to read it, decide anything, or dispatch a repair.

**What does it ask of people?** About 46 hours a week of technician time, roughly 1.15 full-time technicians, every week, indefinitely. It also changes 22 people's morning routine with no stated consultation. The analyst's time is not costed at all.

**Cheaper alternative:** Use the data that already exists. Each morning, give technicians a list of bikes the dashboard flags as stuck or low-battery, with the fix-first bikes at the top.

**Counter-case (strongest argument for the proposal):** Telemetry can't see some physical faults, such as a jammed mechanism that still reports "locked" correctly, and a human eye catches them. This argument survives only if the 14 weekly complaints have been shown to be invisible to telemetry. The proposal never checks, and the two named causes (lock state, battery) are exactly what telemetry measures.

**Pre-mortem (one year on, it failed):**
1. The reports piled up and nobody acted on them, so complaints didn't move.
2. Technicians rushed or copied sheets to meet a 25-minute budget for 40 columns per bike, so the data was junk.
3. Repairs were delayed by the lost 46 hours a week, so complaints rose.

## Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | §3: "Complaints will fall because the report exists." | No causal mechanism. A report does not fix a lock or charge a battery. No step turns a report into a repair. | Report is produced weekly, nobody owns acting on it, complaints stay at about 14/week while 46 h/week are spent. | Define the action loop (who reads what, when, and what they dispatch). Measure complaints before and after a pilot. |
| 2 | Critical | CONFIRMED | §2 vs §3 | Duplicates existing telemetry. Battery level and lock state are already reported every 5 minutes, and "stuck" is already flagged. The sheet re-collects by hand what machines already report. | Technicians transcribe a battery % the dashboard already shows, adding cost and transcription error for no new signal. | Show which of the 40 columns are *not* in telemetry and which complaint causes they explain. Drop the rest. |
| 3 | High | CONFIRMED | §3: "collected on Friday… weekly report" | Latency is wrong for the problem. A stuck bike hurts a rider within hours, but this data reaches a decision up to 7 days later. | A Monday sheet shows a failing lock, the report appears Friday, and riders have hit that bike all week. | Make detection-to-dispatch same-day, driven by dashboard flags. |
| 4 | High | CONFIRMED | §4: "No software cost" | Cost is framed to look free. 22 × 25 min × 5 = 2,750 min ≈ 45.8 h/week, so the arithmetic is right. That is about 1.15 FTE of technician time taken from repairs, plus uncosted analyst time. The opportunity cost isn't stated. | Repair throughput falls by about 46 h/week, so more bikes stay broken and complaints rise. | Cost technician and analyst hours in money and in lost repairs. Compare with using that time to fix the bikes the dashboard flags. |
| 5 | High | CONFIRMED | §1 | No baseline breakdown and no target. The 14/week isn't split by cause (lock vs battery), by station, or by whether the dashboard had already flagged the bike. "Lower" is undefined. | Success can't be judged. The project continues or stops on anecdote. | Split the last 8–12 weeks of complaints by cause and by dashboard-flag status. Set a numeric target and a review date. |
| 6 | Medium | PROBABLE | §3: "40-column… every bike… about 25 minutes" | Time estimate is likely implausible. Bikes per technician isn't stated. At 20 bikes, that is about 75 seconds per bike, or about 2 seconds per field. | Fields are guessed or copied forward. The data looks complete but is wrong. | State bikes per technician. Time a real sheet fill at one station. |
| 7 | Medium | PROBABLE | §2: stuck = "lock state has not changed for 3 hours after a rider unlocked it" | The real detection gap goes unexamined. The rule needs an unlock to register, so a lock that never releases may not trigger it. A dead battery may show up as stale last-seen time rather than "stuck". The proposal doesn't ask whether the 14 complaints were already flagged or missed. | Complaints come from bikes the dashboard's rule misses. A paper sheet doesn't close that gap; fixing the rule would. | Cross-match complaint records against dashboard flags. If most were missed, adjust the rule (failed-release events, a low-battery threshold, stale last-seen). |
| 8 | Medium | CONFIRMED | §3, §4: "5 days" | Weekend coverage isn't addressed. Complaints are a weekly count, but sheets run only on weekdays. | Weekend failures, often peak riding, go unrecorded. | State the complaint distribution by day of week. |
| 9 | Medium | CONFIRMED | §3 | Asks 22 people to change their routine with no stated consultation, owner, pilot, or exit. It is open-ended and all-at-once. | Resentment and low compliance. There is no way to learn cheaply whether it works. | Pilot at 2–3 stations for 4 weeks with a stop rule. Get technician input on what they see that the dashboard doesn't. |
| 10 | Low | PROBABLE | §3: "one analyst… by hand" | Single point of failure, and hand transcription of about 22 sheets × 40 columns × N bikes. | Analyst is absent and no report is produced. Transcription errors go uncaught. | Only relevant if a sheet survives rework. Then use a digital form. |

## What holds up

- The problem is real and quantified at the top level (about 14/week).
- §2 accurately states that useful telemetry exists. That is the strongest asset here, though the proposal doesn't use it.
- The arithmetic in §4 is correct (≈45.8 h/week).

## Unverified claims

- **"About 14 times a week."** Confirm from the complaint log, with source and date range.
- **"About 25 minutes per technician."** Confirm by a timed trial with the actual 40-column sheet.
- **Dashboard telemetry every 5 minutes and the 3-hour stuck rule work as described.** Confirm by checking a known-stuck bike's history on the dashboard; this is the positive control.
- **The 40 columns add information beyond telemetry.** The column list isn't provided. Confirm by mapping each column to a telemetry field or to "not available."

## Questions for the author

1. Of the last N stuck-bike complaints, how many had the dashboard already flagged before the rider complained? If most were flagged, the fix is acting on flags. If most were missed, the fix is the detection rule.
2. Who acts on the weekly report, and what do they do?
3. What do the 40 columns contain that the dashboard doesn't?
4. How many bikes does each technician cover?

## Decision-maker summary

Don't approve this. It spends about 46 technician-hours a week re-collecting data the dashboard already has, and it delivers that data a week late to no named decision-maker. Instead, first check whether complaint bikes were already flagged on the dashboard, then pilot a same-day "fix the flagged bikes" morning list at a few stations. If you proceed anyway, expect lost repair time and no measurable drop in complaints.

## Owner summary

The plan asks technicians to spend nearly an hour and a half of combined time every working day filling in paper forms. Most of that information is already sent automatically by the bikes. A weekly report won't fix bikes by itself, so complaints are unlikely to fall. A cheaper first step is to check whether the existing system already spotted the problem bikes, and have technicians fix those bikes each morning.

```json
{
  "verdict": "REJECT",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "§3 'Complaints will fall because the report exists.'", "scenario": "Weekly report is produced but no one owns acting on it; stuck bikes are not repaired and complaints stay ~14/week while 46 h/week are spent.", "fix": "Define an action loop (owner, cadence, dispatch); pilot and measure complaints before/after."},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "§2 vs §3", "scenario": "Technicians hand-copy battery and lock state the dashboard already reports every 5 minutes, adding cost and transcription error with no new signal.", "fix": "Map each of the 40 columns to telemetry; keep only fields that are unavailable and tied to complaint causes."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "§3 'collected on Friday... weekly report'", "scenario": "A failing bike noted Monday surfaces in Friday's report; riders hit it all week.", "fix": "Same-day detection-to-dispatch using dashboard flags."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "§4 'No software cost'", "scenario": "~46 h/week (~1.15 FTE) of technician time plus uncosted analyst time is diverted from repairs; more bikes stay broken.", "fix": "Cost labor and lost repair capacity; compare against spending that time fixing flagged bikes."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "§1", "scenario": "No cause breakdown, baseline split, or numeric target, so success cannot be judged.", "fix": "Break down 8-12 weeks of complaints by cause, station and dashboard-flag status; set a target and review date."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "§3 '40-column... every bike... about 25 minutes'", "scenario": "At ~20 bikes per technician that is ~2 seconds per field; fields get guessed or copied forward.", "fix": "State bikes per technician; time a real sheet fill."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "§2 stuck rule '3 hours after a rider unlocked it'", "scenario": "Locks that never release or dead batteries may not trigger the rule; the real gap is detection logic, which a paper sheet does not fix.", "fix": "Cross-match complaints against dashboard flags; extend the rule (failed-release events, low-battery threshold, stale last-seen)."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "§3/§4 '5 days'", "scenario": "Weekend failures go unrecorded although complaints are counted weekly.", "fix": "Report complaint distribution by day of week."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "§3", "scenario": "22 technicians' routines change with no consultation, pilot, owner or stop rule; low compliance and no cheap way to learn.", "fix": "Pilot at 2-3 stations for 4 weeks with a stop rule and technician input."},
    {"severity": "Low", "evidence_level": "PROBABLE", "location": "§3 'one analyst... by hand'", "scenario": "Analyst absence means no report; manual transcription errors go uncaught.", "fix": "If any sheet survives rework, use a digital form with validation."}
  ]
}
```