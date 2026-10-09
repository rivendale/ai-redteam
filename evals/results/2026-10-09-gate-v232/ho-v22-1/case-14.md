# Redteam report: frame-crack sensor memo

**VERDICT: REWORK.** The memo's central claim, that a flagged bike is 95% likely to be cracked, is wrong. Recomputed from inspections.csv, the figure is about 16%. The recommendation to replace every flagged frame rests on that error.

**CONFIDENCE: high** on the arithmetic, which uses only the memo's own inputs. Two things lower confidence overall:
- I had no tools, so all arithmetic was done by hand. It is simple and is shown below.
- This was a single reviewer with no fresh subagent. The work was not written in this conversation, so the risk of anchoring on the author's reasoning is lower.

**INPUTS LEDGER:**
- Seen: request.md, context.md, memo.md, inspections.csv.
- Not seen: where the 0.95 and 0.05 sensor rates come from (vendor sheet or field trial, and the sample size).
- Not seen: whether 30 cracked out of 3,000 is the whole fleet or an inspection sample.
- Not seen: whether a manual inspection step exists.
- These gaps matter for the size of the error, not for whether it exists. The error reproduces from the memo's own numbers.

**COVERAGE:**
- Checked: both memo claims (sensitivity and specificity; the 95% figure for a flagged bike), the recommendation, and every row of inspections.csv.
- Not checked: provenance of the sensor rates and of the fleet counts (not supplied).

**SEATS AND GATE:** Local reviewer only. Sensitivity gate: no personal, client or confidential data, so the gate passed. No cross-vendor seats were requested.

## Recomputation (from inspections.csv)

| Quantity | Calculation | Result |
|---|---|---|
| Fleet | 30 + 2,970 | 3,000 bikes |
| Crack prevalence | 30 / 3,000 | 1.0% |
| True flags (cracked bikes flagged) | 30 × 0.95 | 28.5 |
| False flags (sound bikes flagged) | 2,970 × 0.05 | 148.5 |
| Total flagged | 28.5 + 148.5 | 177 |
| **P(cracked \| flagged)** | 28.5 / 177 | **16.1%** (memo says 95%) |
| Missed cracks | 30 × 0.05 | 1.5 bikes left in service |

The memo confuses P(flag | cracked), which is 95%, with P(cracked | flagged), which is about 16%. With 1% prevalence, false alarms on sound bikes outnumber true detections by about 5 to 1.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | memo.md, para 1: "A flagged bike is therefore 95% likely to have a cracked frame." | The memo uses sensitivity as if it were the chance a flagged bike is cracked, and ignores the 1% base rate. The true figure is about 16.1%. | A reader trusts "95%" and approves replacing frames. About 84% of flagged bikes are actually sound. | Replace the sentence with: "About 16% of flagged bikes (28.5 of 177) are expected to be cracked." Reproduce: 0.95·30 / (0.95·30 + 0.05·2970) = 28.5/177 = 0.161. | a✓ b✓ c✓ d✓ |
| F2 | High | CONFIRMED | A/C | memo.md, para 2: "pulling every flagged bike… and replacing its frame" | The recommendation follows from F1. Replacing every flagged frame uses about 177 frames and 177 bike-days to catch about 28.5 cracks. About 148.5 sound frames would be scrapped. | Fleet-wide rollout costs about 6× the frames needed. Each needless replacement costs a day of rental income and a frame. | Recommend pulling flagged bikes, then confirming with a manual inspection, and replacing only confirmed cracks. Reproduce: the 148.5 false flags in the table above. | a✓ b✓ c✗ d✓ |
| F3 | Medium | CONFIRMED | C | memo.md (omission) | The memo does not mention false negatives. About 1.5 of 30 cracked frames (5%) are not flagged and stay in service. | A missed cracked frame fails under a rider. The memo implies the sensor solves the problem. | Add one sentence on the miss rate and the continuing manual inspection schedule. Reproduce: 30 × 0.05 = 1.5. | a✓ b✓ c✓ d✗ |
| F4 | Low | CONFIRMED | C | inspections.csv, rows 4–5 | The `bikes` column mixes counts (30, 2970) with rates (0.95, 0.05). | A reader or script sums the column or reads 0.95 as a bike count. | Move the rates to a separate file or a separate column with units. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION
- **S1:** The sensor rates (0.95 and 0.05) have no stated source. What settles it: the trial or vendor data behind them and the sample size. A 5% false-alarm rate measured on a few dozen frames would be very uncertain.
- **S2:** It is unclear whether 30 cracked out of 3,000 reflects actual fleet prevalence. What settles it: whether these counts come from a full-fleet inspection, and their date. If true prevalence is higher, the 16% rises, but it reaches 95% only if prevalence is about 50%.
- **S3:** It is unclear whether a cheap manual confirmation is possible. What settles it: the cost and time of a manual ultrasonic or visual frame check compared with a frame replacement. This decides whether the confirm-first fix in F2 is cheaper.

## REFUTED
- **"Pulling flagged bikes is wrong."** I considered this and withdrew it. A cracked frame is a safety risk, and taking a flagged bike out of service pending a check is defensible even at 16%. The defect is replacing every flagged frame on the strength of a false 95%, not pulling flagged bikes at all.

## WHAT HOLDS UP
- "Detects 95% of cracked frames" matches inspections.csv (0.95).
- "False alarm on 5% of sound frames" matches inspections.csv (0.05).
- Both are stated correctly as conditional rates. The error comes only in the inference drawn from them.

## UNVERIFIED CLAIMS
- The sensor's 95% and 5% performance: confirm from the trial data (S1).
- The fleet counts: confirm from the inspection record (S2).

## QUESTIONS FOR THE AUTHOR
1. Where do 0.95 and 0.05 come from, and on how many frames were they measured?
2. Can a flagged bike be confirmed by hand before its frame is replaced, and at what cost?

## DECISION-MAKER SUMMARY
The memo's "95% likely cracked" is a base-rate error. From its own data, only about 16% of flagged bikes are cracked, so replacing every flagged frame would scrap about 148 sound frames to catch about 28 cracked ones. Send the memo back with a pull-then-confirm recommendation. Proceeding as written costs roughly six times the frames and rental days needed and still leaves about 1.5 cracked bikes undetected.

## OWNER SUMMARY
The memo overstates how reliable the new sensor is. Because cracked frames are rare, most bikes the sensor flags are actually fine, so replacing every flagged frame would waste many good frames and days of rentals. A better plan is to take flagged bikes out of service, check them by hand, and replace only the frames that are really cracked.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "inspections.csv", "status": "seen", "matters": true},
    {"item": "source and sample size of sensor rates 0.95/0.05", "status": "not_seen", "matters": true},
    {"item": "provenance of fleet counts 30/2970", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal, client, financial, health or confidential data."},
  "coverage": {
    "checked": [
      {"unit": "memo.md", "kind": "file"},
      {"unit": "inspections.csv", "kind": "data"},
      {"unit": "memo.md: sensor detects 95% / false alarm 5%", "kind": "claim"},
      {"unit": "memo.md: flagged bike 95% likely cracked", "kind": "claim"},
      {"unit": "memo.md: pull and replace every flagged frame", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "sensor trial data", "reason": "not supplied"},
      {"unit": "fleet inspection record", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "memo.md para 1: \"A flagged bike is therefore 95% likely to have a cracked frame.\"",
     "scenario": "Readers rely on 95%; actual P(cracked|flagged) = 28.5/177 = 16.1%, so about 84% of flagged bikes are sound.",
     "fix": "State about 16% (28.5 of 177 flagged bikes expected cracked).",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "0.95*30 / (0.95*30 + 0.05*2970) = 28.5/177 = 0.161; memo states 0.95."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md para 2: \"pulling every flagged bike ... and replacing its frame\"",
     "scenario": "Fleet-wide, about 177 frames and bike-days are spent to catch about 28.5 cracks; about 148.5 sound frames are scrapped.",
     "fix": "Pull flagged bikes, confirm by manual inspection, and replace only confirmed cracked frames.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "2970*0.05 = 148.5 false flags vs 30*0.95 = 28.5 true flags."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "memo.md (omission)",
     "scenario": "About 1.5 of 30 cracked frames are not flagged and stay in service; the memo implies the sensor resolves the risk.",
     "fix": "State the 5% miss rate and keep the manual inspection schedule.",
     "answers": {"a": true, "b": true, "c": true, "d": false},
     "reproduction": "30*0.05 = 1.5 missed cracked bikes."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "inspections.csv rows 4-5",
     "scenario": "The bikes column mixes counts and rates; a reader or script misreads 0.95 as a bike count.",
     "fix": "Move the rates to a separate file or a column with units.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Sum of the bikes column = 3001.0, which is not a meaningful total."},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "inspections.csv rows 4-5",
     "suspicion": "Sensor rates may come from a small or vendor-only sample.",
     "unresolved_fact": "Source and sample size of the 0.95 and 0.05 figures."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "inspections.csv rows 2-3",
     "suspicion": "30/3000 may not reflect current fleet crack prevalence.",
     "unresolved_fact": "Whether the counts come from a recent full-fleet inspection."},
    {"id": "S3", "status": "needs_validation", "track": "A", "location": "memo.md para 2",
     "suspicion": "A confirm-before-replace step may or may not be cheaper than replacement.",
     "unresolved_fact": "Cost and time of a manual frame check vs a frame replacement."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Pulling flagged bikes from service is itself wrong.",
     "evidence": "Cracked frames are a safety risk; pulling pending confirmation is defensible at 16%. The defect is replacing frames on a false 95%."}
  ]
}
```