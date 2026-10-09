**Note on scope:** the context asks for "Track C". The skill defines Tracks A, B and R only. I treated the request as a claims check, recomputing every number from `inspections.csv` under Track A (Facts and Logic), and applied Track R where the memo's wording reaches operations.

## Pass 1: Reconstruct

The memo says the ultrasonic sensor has 95% sensitivity and a 5% false-positive rate. From that it concludes a flagged bike is 95% likely to be cracked, and recommends pulling and re-framing every flagged bike at once. For this to be right, the chance that a flagged bike is cracked would have to be high enough to justify a day's income plus a frame on every flag.

Load-bearing assumptions:
- Sensitivity equals the chance a flagged bike is cracked. This ignores the 1% base rate.
- The 0.95 and 0.05 rates hold for this fleet.
- Pulling a bike means replacing its frame, with no cheaper check in between.
- Unflagged bikes are safe.

## Pass 2: Attack (recomputed from inspections.csv)

| Quantity | Computation | Value |
|---|---|---|
| Fleet | 30 + 2970 | 3000 |
| Crack prevalence | 30 / 3000 | 1.0% |
| True positives | 0.95 × 30 | 28.5 |
| False positives | 0.05 × 2970 | 148.5 |
| Total flagged | 28.5 + 148.5 | 177 |
| **P(cracked \| flagged)** | 28.5 / 177 | **16.1%** |
| Sound frames replaced under the memo's plan | 148.5 / 177 | 83.9% of pulls |
| Cracked bikes missed (left in service) | 0.05 × 30 | 1.5 |
| P(cracked \| not flagged) | 1.5 / 2823 | 0.053% |

- **Facts:** the 95% and 5% figures match the CSV. The 95% posterior does not follow from them. It is off by a factor of about 6.
- **Logic:** the memo confuses P(flag | cracked) with P(cracked | flag). This is the base-rate fallacy, and the recommendation is built on it.
- **Alternatives not considered:** pull flagged bikes for a manual or confirmatory inspection, and replace only confirmed cracks. That avoids about 148 unnecessary frame replacements. The memo also offers no option of delaying, re-testing, or doing a staged rollout.
- **Counter-case:** about 5 of every 6 pulls would replace a sound frame. At a day's income plus a frame each, the cost is roughly 177 frames to catch about 28.5 cracks. A confirm-then-replace process catches the same cracks for about 28.5 frames plus 177 inspections.
- **Pre-mortem:**
  1. Frame budget is exhausted on sound bikes.
  2. Staff lose trust in the sensor after repeated "no crack found" results, and start ignoring flags.
  3. A missed crack (about 1.5 per sweep) causes an injury, because the memo implies unflagged bikes are fine and sets no re-inspection policy.
- **Data provenance:** 0.95 × 30 = 28.5 is not a whole number of bikes. The rates therefore cannot be observed counts from this fleet. They are probably vendor or spec figures stored in a column named `bikes`. With only 30 cracked frames, any sensitivity measured on this fleet would carry a wide confidence interval, roughly 0.83 to 0.99.

## Pass 3: Self-check

Every finding is tied to a memo sentence or CSV row and reproduces from the arithmetic above. The finding most likely to be underweighted is the safety one. The memo is silent on false negatives, and a missed crack harms a rider, which is a worse outcome than a wasted frame.

---

**VERDICT: REWORK.** The memo's central number is wrong (16%, not 95%), and its recommendation to replace the frame on every flag rests entirely on that error.

**CONFIDENCE IN VERDICT: high.** The arithmetic is fully determined by the CSV. The only limit is uncertainty about where the 0.95 and 0.05 rates came from, and that uncertainty does not rescue the memo.

### FINDINGS

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | memo.md: "A flagged bike is therefore 95% likely to have a cracked frame." | Sensitivity is presented as the chance a flagged bike is cracked (base-rate fallacy). From the CSV: 28.5 / 177 = 16.1%. | Decision-makers approve a policy believing 95% of pulls are justified, when about 84% are sound frames. | Replace the claim with 16% computed from the CSV, and show the 2×2 table (28.5 TP, 148.5 FP, 1.5 FN, 2821.5 TN). |
| 2 | Critical | CONFIRMED | memo.md: "pulling every flagged bike from service at once and replacing its frame" | The recommendation depends on Finding 1. Replacing every flagged frame means about 177 frames and 177 bike-days to fix about 28.5 cracks. | About 148 sound frames are destroyed per sweep of 3,000 bikes, along with the lost rental income. | Re-derive the recommendation: pull on flag, confirm by manual or secondary inspection, and replace only confirmed cracks. Compare the costs of both options. |
| 3 | High | CONFIRMED | memo.md (omission) | False negatives are not addressed. About 1.5 cracked bikes per sweep go unflagged and stay in service. | A rider is injured on a cracked frame the sensor missed, and the memo's framing implied it was safe. | Add a false-negative rate and a re-inspection cadence for unflagged bikes. State the residual risk explicitly. |
| 4 | Medium | PROBABLE | inspections.csv rows `sensor_detects_cracked,0.95` and `sensor_flags_sound,0.05` | Rates are stored as `bikes` counts. 28.5 is not an integer, so these are not observed results from this fleet. Their source and sample size are unstated. | If the real rates on this fleet differ (for example, a false-positive rate of 8%), the posterior falls further and the cost estimates shift. | Cite the source of the rates, put rates in their own column or table, and report observed TP/FP counts with confidence intervals once a trial has run. |
| 5 | Medium | CONFIRMED | memo.md (omission) | No alternatives were compared: confirmatory inspection, re-testing flagged bikes, a staged pilot, or keeping the status quo. | A one-option memo locks in the most expensive policy without a comparison. | Add an options table with the cost per crack caught for each option. |
| 6 | Low | CONFIRMED | memo.md: "Fleet and inspection figures are in inspections.csv." | The memo states no fleet size or prevalence, so readers cannot spot the error without redoing the math. | A reviewer skims the memo and accepts the 95% figure. | State fleet size (3,000) and prevalence (1%) in the body of the memo. |

### WHAT HOLDS UP
- The 95% detection and 5% false-alarm figures are quoted accurately from the CSV.
- The fleet counts (30 cracked, 2,970 sound) are internally consistent.
- Pulling flagged bikes for inspection is defensible. Unconditional frame replacement is what fails.

### UNVERIFIED CLAIMS
- **Sensor accuracy (0.95 / 0.05):** the source is unknown. Confirm with the vendor test report or a blinded field trial against manual inspection.
- **The 30 cracked bikes:** how were they identified, and is that method itself a reliable reference? Confirm against the inspection records.
- **"Costs a day of rental income and a frame" per pull:** this assumes no cheaper inspect-only path exists. Confirm with the maintenance team.

### QUESTIONS FOR THE AUTHOR
1. Can a flagged bike be inspected manually without replacing the frame, and what does that cost?
2. Where do the 0.95 and 0.05 rates come from, and on how many frames were they measured?
3. What is the policy for unflagged bikes, given the sensor misses about 5% of cracks?

### DECISION-MAKER SUMMARY
Do not adopt the memo's recommendation. A flagged bike is about 16% likely to be cracked, not 95%, so replacing every flagged frame wastes about five frames for every crack it finds. Send the memo back for a confirm-before-replace option and a plan for the roughly 1.5 cracked bikes per sweep the sensor misses. If you proceed anyway, expect about 148 unnecessary frame replacements per 3,000-bike sweep.

### OWNER SUMMARY
The memo overstates how reliable the crack sensor is. Most bikes it flags actually have sound frames, so replacing every flagged frame would waste a lot of money. A better plan is to check flagged bikes by hand first and keep checking unflagged bikes too, because the sensor misses a few real cracks.

```json
{
  "verdict": "REWORK",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "memo.md: 'A flagged bike is therefore 95% likely to have a cracked frame.'",
      "scenario": "Base-rate fallacy: with 30 cracked of 3000, flags = 28.5 TP + 148.5 FP = 177, so P(cracked|flag) = 16.1%, not 95%; decision-makers approve a policy believing nearly all pulls are justified when about 84% are sound frames.",
      "fix": "Replace with 16.1% computed from the CSV and show the full 2x2 table (TP 28.5, FP 148.5, FN 1.5, TN 2821.5)."
    },
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "memo.md: 'pulling every flagged bike from service at once and replacing its frame'",
      "scenario": "The recommendation rests on the wrong 95% figure; about 177 frames and bike-days are spent to fix about 28.5 cracks, destroying about 148 sound frames per sweep.",
      "fix": "Re-derive the recommendation: pull on flag, confirm by manual or secondary inspection, replace only confirmed cracks; include a cost comparison."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "memo.md (omission of false negatives)",
      "scenario": "About 1.5 cracked bikes per sweep go unflagged and stay in service; a rider is injured on a missed crack.",
      "fix": "State the false-negative rate and residual risk; add a periodic manual re-inspection policy for unflagged bikes."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "inspections.csv rows sensor_detects_cracked,0.95 and sensor_flags_sound,0.05",
      "scenario": "Rates are stored in a 'bikes' column and imply 28.5 bikes, so they are not observed fleet counts; if real field rates differ, the posterior and costs shift further.",
      "fix": "Cite the source of the rates, separate rates from counts, and report observed TP/FP counts with confidence intervals from a field trial."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "memo.md (single option presented)",
      "scenario": "No comparison with confirmatory inspection, re-test, a staged pilot, or the status quo locks in the most expensive policy.",
      "fix": "Add an options table with cost per crack caught for each option."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "memo.md: 'Fleet and inspection figures are in inspections.csv.'",
      "scenario": "Fleet size and the 1% prevalence are not stated in the memo, so readers cannot spot the base-rate error without recomputing.",
      "fix": "State fleet size (3000) and prevalence (1%) in the memo body."
    }
  ]
}
```