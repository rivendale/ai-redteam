# Adversarial Diagnostic Review: Frame-crack sensor memo

**Scope note:** The context asks for a "claims review (Track C)". The skill has no Track C. I applied what the context describes, which is to recompute every number from `inspections.csv` and check each claim against it. That fits under Track A (Facts, Logic), and I added the rest of Track A. I had no tools, so all arithmetic below is done by hand and shown so it can be checked.

## Pass 1: Reconstruct

The memo claims the sensor has 95% sensitivity and a 5% false-positive rate. From that it concludes that a flagged bike is 95% likely to be cracked, and it recommends pulling every flagged bike at once and replacing its frame. For this to be right, three things must hold:
- the probability that a flagged bike is cracked must actually be high;
- the sensor rates must be measured and representative;
- replacing frames outright must beat a cheaper confirmatory step.

There is also an unstated assumption: that P(flag | cracked) equals P(cracked | flag). The memo also cites `inspections.csv` as its support.

## Pass 2: Attack (recomputed from inspections.csv)

| Quantity | Computation | Value |
|---|---|---|
| Fleet | 30 + 2,970 | 3,000 |
| Prevalence | 30 / 3,000 | 1.0% |
| True positives (expected) | 0.95 × 30 | 28.5 |
| False positives (expected) | 0.05 × 2,970 | 148.5 |
| Total flagged | 28.5 + 148.5 | 177 |
| **P(cracked \| flagged)** | 28.5 / 177 | **16.1%** |
| P(sound \| flagged) | 148.5 / 177 | 83.9% |
| Cracked bikes missed | 0.05 × 30 | 1.5 |

Check on the arithmetic: the counts add back to the fleet (177 flagged + 2,823 unflagged = 3,000). The cracked bikes split as 28.5 flagged + 1.5 missed = 30, which matches the CSV.

**Effect of the recommendation:** about 177 bikes are pulled and get new frames. Of those, about 149 are sound, so each costs a day of income and a frame for nothing. That is roughly 5 unnecessary replacements for every necessary one. Meanwhile about 1.5 cracked bikes stay in service and the memo never mentions them.

**Counter-case:** a cracked frame can injure a rider, so pulling flagged bikes quickly may be justified. That argument supports a temporary pull followed by inspection. It does not support replacing frames on bikes that are about 84% likely to be sound. The memo's recommendation does not survive the counter-case. A narrower version of it does.

**Pre-mortem (one year on, the decision failed):**
1. The frame budget is overrun by roughly 6× the real need.
2. Sound bikes keep being pulled, which hurts fleet availability and erodes trust in the sensor.
3. Undetected cracked bikes cause a rider incident, and no one had planned for missed cracks.

## Pass 3: Self-check

Every finding below is tied to a quoted line and a scenario. The expected counts are fractional (28.5 bikes, 1.5 bikes). These are expected values, not observed counts, and the conclusion does not depend on rounding.

The most serious thing I might be missing is in the provenance of the 0.95 and 0.05 rates. If they were measured on a sample enriched with cracked frames, or on a different fleet, the real PPV could be different again. The file gives no basis for checking this.

---

**VERDICT: REWORK.** The memo's central number is wrong (16%, not 95%), and the recommendation to replace every flagged frame rests entirely on that error.

**CONFIDENCE IN VERDICT: high.** The arithmetic follows directly from the memo's own file. Confidence is limited only by the unknown origin of the sensor rates, and that uncertainty can only weaken the memo further.

### FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | memo.md: "A flagged bike is therefore 95% likely to have a cracked frame." | Base-rate fallacy. The memo treats sensitivity, P(flag\|cracked), as the predictive value, P(cracked\|flag). With 1% prevalence the PPV is 28.5/177 = 16.1%. | The decision-maker approves the replacement program believing 95% of flagged frames are cracked, when about 84% are sound. | Restate the claim as "about 16% of flagged bikes are cracked", show the 2×2 table, and redo the recommendation on that figure. |
| 2 | Critical | CONFIRMED | memo.md: "pulling every flagged bike from service at once and replacing its frame" | The recommendation follows from Finding 1, and replacing a frame cannot be undone. | About 177 frames are replaced, about 149 of them on sound bikes, each also losing a day of rental income. | Evaluate "pull, then confirm by manual or secondary inspection, and replace only confirmed cracks" against "replace all flagged". Compare the cost of the inspection step with about 149 unnecessary frames. |
| 3 | High | CONFIRMED | memo.md: no mention of misses; CSV: 0.95 sensitivity | False negatives are ignored. About 1.5 cracked bikes per fleet sweep are not flagged and stay in service. | A cracked bike that was never flagged fails under a rider, after the program has been presented as dealing with cracks. | State the expected misses and set a periodic manual-inspection policy or a re-scan interval. |
| 4 | High | CONFIRMED | memo.md: "Fleet and inspection figures are in inspections.csv." | The citation implies the file supports the memo's claim. The file actually contradicts the 95% figure. | A reader trusts the memo because it cites data, and does not recompute from that data. | Base each stated figure on the file and show the derivation. |
| 5 | Medium | PROBABLE | inspections.csv rows `sensor_detects_cracked,0.95` and `sensor_flags_sound,0.05` | Rates are stored in a column named `bikes`. There is no sample size, source or test conditions, so the rates are unsourced. The CSV also gives no basis for the "30 cracked" ground truth. | The rates came from a vendor brochure or a small or enriched sample, so even the corrected 16% PPV is unreliable. | Add a source, sample size and confidence intervals for both rates. Record how the cracked/sound labels were determined. Move rates out of the counts column. |
| 6 | Medium | CONFIRMED | memo.md as a whole | No alternatives are considered: confirmatory inspection, a re-scan to cut false positives, a temporary pull without replacement, or the status quo. | The organization commits to the most expensive option without comparing it to cheaper ones. | Add a short comparison of options with expected cost and residual safety risk. |

### WHAT HOLDS UP

- The memo quotes the sensor rates (95% / 5%) accurately from the CSV.
- Fleet counts are internally consistent (3,000 bikes).
- The underlying concern, that cracked frames are a safety risk and flagged bikes deserve attention, is reasonable.

### UNVERIFIED CLAIMS

- **0.95 and 0.05 sensor rates:** need the validation study, its sample size and its conditions.
- **30 cracked / 2,970 sound:** need to know how ground truth was established (for example, a full manual inspection).
- **Implied claim that replacement is the right remedy:** need the cost of a manual inspection compared with a frame plus a day of income.

### QUESTIONS FOR THE AUTHOR

1. Where do the 95% and 5% figures come from, and on how many bikes were they measured?
2. Does a confirmatory inspection exist, and what does it cost per bike compared with a frame replacement?
3. What is the plan for the cracked bikes the sensor misses?

### DECISION-MAKER SUMMARY

Do not approve frame replacement for every flagged bike. Only about 16% of flagged bikes are actually cracked, so roughly 149 of 177 replacements would be wasted. A temporary pull with confirmation before replacement is the defensible version, and the cracked bikes the sensor misses still need a plan either way.

### OWNER SUMMARY

The memo overstates how reliable the new sensor's alarms are. Most bikes it flags are actually fine, so replacing every flagged frame would waste money on many good bikes. A better plan is to take flagged bikes out briefly, check them by hand, and replace only the ones that are really cracked.

```json
{
  "verdict": "REWORK",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "memo.md: \"A flagged bike is therefore 95% likely to have a cracked frame.\"",
      "scenario": "Base-rate fallacy: with 1% prevalence (30/3000), expected flags are 28.5 true + 148.5 false = 177, so P(cracked|flagged) = 28.5/177 = 16.1%, not 95%; decision-maker approves replacements believing nearly all flagged frames are cracked.",
      "fix": "Restate as ~16% PPV with the 2x2 table derived from inspections.csv and redo the recommendation on that figure."
    },
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "memo.md: \"pulling every flagged bike from service at once and replacing its frame\"",
      "scenario": "About 177 frames replaced, ~149 of them on sound bikes, each also losing a day of rental income; frame replacement is irreversible.",
      "fix": "Compare 'pull, confirm by inspection, replace only confirmed cracks' against 'replace all flagged' on expected cost and residual risk."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "memo.md (omission); inspections.csv sensor_detects_cracked,0.95",
      "scenario": "~1.5 cracked bikes per sweep are not flagged and remain in service; a rider incident occurs on a bike the program implied was safe.",
      "fix": "State expected misses and add periodic manual inspection or re-scan policy."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "memo.md: \"Fleet and inspection figures are in inspections.csv.\"",
      "scenario": "Citation implies the file supports the 95% claim; recomputing from the file contradicts it, and readers who trust the citation are misled.",
      "fix": "Base every stated figure on the file and show the derivation."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "inspections.csv rows sensor_detects_cracked,0.95 and sensor_flags_sound,0.05",
      "scenario": "Rates are stored in a 'bikes' counts column with no source, sample size, or ground-truth method; if they come from a vendor or an enriched sample, even the corrected PPV is unreliable.",
      "fix": "Document source, sample size, and confidence intervals for both rates and how cracked/sound labels were determined; separate rates from counts."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "memo.md (whole document)",
      "scenario": "No alternatives (confirmatory inspection, re-scan, temporary pull, status quo) considered; the most expensive irreversible option is chosen by default.",
      "fix": "Add an options comparison with expected cost and residual safety risk for each."
    }
  ]
}
```