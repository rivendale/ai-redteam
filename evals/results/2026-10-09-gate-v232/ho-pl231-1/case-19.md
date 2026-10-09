# Adversarial Diagnostic Review: Battery Supplier TCO Memo

## Pass 1: Reconstruct

The memo claims Volta has the lowest five-year cost per bike ($410), against Amperia ($775) and Zesto ($1,385), and recommends Volta. For that to be correct, five things must hold:

1. Each bike runs about 1,825 cycles in five years (one per day). This is stated, not sourced.
2. A battery lasts its rated cycle life within five years of calendar time. This is unstated.
3. Purchase price and swap labor are the only cost drivers that differ between suppliers. This is unstated.
4. Leftover battery life at year five has no value. This is unstated.
5. The first battery is fitted without swap labor. This is implied by Volta's $0 labor.

## Pass 2: Attack (Track A)

**Facts and arithmetic.** I recomputed every row from suppliers.csv.

| Supplier | Batteries needed | Purchase | Swaps × $15 | Total |
|---|---|---|---|---|
| Volta | 1,825 ÷ 2,000 → 1 | 1 × 410 = $410 | 0 → $0 | $410 |
| Amperia | 1,825 ÷ 1,000 → 2 | 2 × 380 = $760 | 1 → $15 | $775 |
| Zesto | 1,825 ÷ 600 → 4 | 4 × 335 = $1,340 | 3 → $45 | $1,385 |

- Zesto needs a fourth battery because 3 × 600 = 1,800, which is short of 1,825.
- Every number in the memo matches the CSV.
- The memo's statement that Volta has the highest per-battery price is also correct.

**Sensitivity to the usage assumption.** Cost per rated cycle is Volta $0.205, Amperia $0.38 and Zesto $0.558, so Volta dominates on a continuous basis.

- Against Amperia's step function, Volta wins at every usage level above 1,000 cycles. Above 2,000 cycles Volta costs $835 while Amperia costs at least $1,170.
- Volta loses only if five-year usage is at or below 1,000 cycles, which is under about 0.55 cycles per day. At that level Amperia ($380) and Zesto at or below 600 cycles ($335) are cheaper.
- So the conclusion survives any realistic share-fleet utilization. The memo, however, never shows this; the reader has to take "once a day" on faith.

**Counter-case.** The strongest argument against Volta is that a single cell chemistry has to survive five years of calendar aging and outdoor heat. Rated cycle life is a lab figure, and a battery that fails by calendar age in year three or four turns Volta into two purchases ($835). Even then Volta still beats Amperia ($775 only if Amperia also needs no third battery) by a narrow margin. If calendar aging hits Volta and not the others, Volta at $835 is still roughly tied with Amperia and well below Zesto. The recommendation survives, but the margin shrinks from $365 to about $60.

**Pre-mortem: the three most likely failure reasons.**
1. Volta batteries fade or fail by calendar age before 2,000 cycles.
2. Real utilization differs sharply from one cycle per day, or degradation in the field cuts usable cycles.
3. Volta has supply or warranty problems. One supplier for 3,080 bikes over five years is a concentration risk the memo never mentions.

**Omitted cost items.** The memo does not address warranty terms, end-of-life disposal and recycling, downtime during swaps, volume pricing, or discounting (time value of money). Discounting slightly favors suppliers whose spend is deferred, but a few percent cannot close a gap of $365 or more.

**Leftover life.** At year five, value is left unused in each final battery:

| Supplier | Unused cycles in final battery | Value left |
|---|---|---|
| Volta | 175 | about $36 |
| Amperia | 175 | about $67 |
| Zesto | 575 (fourth battery bought for 25 cycles) | about $321 |

Pro-rated costs are about Volta $374, Amperia $709 and Zesto $1,064. The ranking is unchanged.

**Fit to the request.** The memo answers the request: it compares all three suppliers on five-year TCO and recommends one. It does not drift. It does omit the fleet-level figure that matters at these stakes.

## Pass 3: Self-check

- The work contains no embedded instructions.
- There are no High or Critical candidates, so no siblings search is required.
- **Most serious thing I might be missing:** whether "cycle_life" in the CSV means the same thing for each supplier. For example, cycles to 80% capacity versus 70%, or different depth-of-discharge test conditions. That would hide in the supplier datasheets, not in the CSV.

---

**VERDICT: SHIP WITH FIXES.** The arithmetic is correct and Volta wins under any plausible utilization. However, the memo states its load-bearing usage assumption as fact, with no source and no sensitivity check, and it omits the fleet total.

**CONFIDENCE IN VERDICT: Medium-high.** It is limited by having no utilization data, no calendar-life data, and no definition of how each supplier measures cycle life.

**COVERAGE**
- memo.md: checked. Every figure was recomputed.
- suppliers.csv: checked. All four columns were cross-referenced.
- request.md and context.md: checked.

**FINDINGS**

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| 1 | Medium | CONFIRMED | memo.md line 3: "Each bike uses its battery once a day" | A load-bearing usage figure is stated as fact. It is not in the request or the CSV, and the memo gives no sensitivity analysis. | If real usage is 1,000 cycles or fewer over five years (under about 0.55 per day), Amperia ($380) or Zesto ($335) is cheaper than Volta ($410). | Source the figure from fleet telemetry. Add a short break-even note: Volta is cheapest for any usage above 1,000 cycles. | a Y, b Y, c N, d N |
| 2 | Medium | PROBABLE | memo.md line 3: replacement is triggered only by cycle life | The model assumes calendar life is at least five years. A Volta battery is expected to last the full five years on one unit. | Calendar aging forces a Volta replacement before 2,000 cycles. Volta's cost rises to $835 and its lead over Amperia narrows from $365 to about $60. | Get each supplier's calendar-life or warranty-years figure and the definition behind its cycle-life rating. Re-run the table with a calendar-life cap. | a Y, b N, c N, d N |
| 3 | Low | CONFIRMED | memo.md table: per-bike only | No fleet total is given, although the context names 3,080 bikes. | The decision-maker cannot see that the choice is roughly $1.26M (Volta) vs $2.39M (Amperia) vs $4.27M (Zesto). | Add a fleet column: per-bike cost × 3,080. | a Y, b Y, c N, d Y |
| 4 | Low | CONFIRMED | memo.md table: Zesto row | The memo charges full price for leftover battery life. Zesto's fourth battery is bought for only 25 cycles, and the memo does not disclose this. | A reader may treat $1,385 as exact. Pro-rated, Zesto costs about $1,064. The ranking does not change. | State the method (whole batteries, no residual value) or show pro-rated figures alongside. | a Y, b Y, c N, d N |
| 5 | Low | CONFIRMED | memo.md: cost scope | Warranty, disposal, downtime, discounting and supplier concentration risk are not mentioned. | Warranty coverage or disposal fees that differ by supplier shift the comparison, and that goes unseen. | Add a "not included" line, or gather these terms from each supplier. | a Y, b Y, c N, d N |

**NEEDS VALIDATION**
- Whether "cycle_life" uses the same end-of-life criterion and test conditions for all three suppliers. The supplier datasheets would settle this.
- Whether actual fleet utilization is about one cycle per day. Fleet telemetry on cycles per bike per day would settle this.

**REFUTED**
- **Arithmetic error:** all three rows recompute exactly from the CSV.
- **Swap labor misapplied:** labor is charged per replacement and the first battery is excluded. This is consistent across suppliers, and adding $15 to every row would not change the ranking.
- **Zesto battery count wrong:** 3 × 600 = 1,800, which is less than 1,825, so 4 batteries is correct.

**WHAT HOLDS UP**
- The arithmetic, the use of the CSV inputs, and the ranking all check out.
- The ranking survives pro-rating, discounting at normal rates, and any usage above 1,000 cycles.
- The memo addresses the request directly, without drift.

**UNVERIFIED CLAIMS**
- "once a day": confirm with utilization data.
- Replacement happens only at rated cycle life: confirm with calendar-life and warranty terms.

**QUESTIONS FOR THE AUTHOR**
1. Where does "once a day" come from?
2. What calendar life and warranty does each supplier state, and how does each define cycle life?

**DECISION-MAKER SUMMARY**
Volta is the right choice on the numbers given, at roughly $1.26M for the fleet versus $2.39M or more for the alternatives. Before signing, confirm actual daily usage and each supplier's calendar-life and warranty terms. The remaining risk is Volta batteries aging out before five years, which would shrink but probably not erase their advantage.

**OWNER SUMMARY**
The recommendation to pick Volta is sound and the math checks out. Before committing to a five-year contract, confirm how often bikes are actually used and how many years each supplier's batteries are expected to last. The memo should also show the total cost for the whole fleet, not just per bike.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium-high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "suppliers.csv", "status": "seen", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "memo.md", "kind": "document"},
      {"unit": "suppliers.csv", "kind": "data"},
      {"unit": "once-a-day usage assumption", "kind": "assumption"},
      {"unit": "cost table arithmetic", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "supplier datasheets / cycle-life definitions", "reason": "not_supplied"},
      {"unit": "fleet utilization data", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md line 3: 'Each bike uses its battery once a day'",
     "scenario": "Usage at or below 1,000 cycles over five years makes Amperia ($380) or Zesto ($335) cheaper than Volta ($410); the assumption is unsourced and untested.",
     "fix": "Source utilization from telemetry; add break-even note (Volta cheapest above 1,000 cycles).",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "A",
     "location": "memo.md line 3: replacement only at cycle life",
     "scenario": "Calendar aging forces a Volta replacement before 2,000 cycles; Volta cost rises to $835 and the lead over Amperia narrows from $365 to about $60.",
     "fix": "Obtain calendar-life and warranty terms and cycle-life definitions; re-run with a calendar cap.",
     "answers": {"a": true, "b": false, "c": false, "d": false}},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md table (per-bike only)",
     "scenario": "Fleet of 3,080 bikes: decision-maker does not see $1.26M vs $2.39M vs $4.27M.",
     "fix": "Add a fleet-total column.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md table, Zesto row",
     "scenario": "Fourth Zesto battery bought for 25 cycles is charged in full; pro-rated cost is about $1,064 vs $1,385; method undisclosed; ranking unchanged.",
     "fix": "State the whole-battery, no-residual method or show pro-rated figures.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md cost scope",
     "scenario": "Warranty, disposal, downtime, discounting and supplier concentration excluded without disclosure; supplier-specific differences go unseen.",
     "fix": "Add a 'not included' line or collect those terms.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "NV1", "status": "needs_validation", "location": "suppliers.csv cycle_life column",
     "suspicion": "Cycle life may be measured to different end-of-life criteria by different suppliers.",
     "unresolved_fact": "Each supplier's cycle-life test definition (capacity threshold, depth of discharge)."},
    {"id": "NV2", "status": "needs_validation", "location": "memo.md line 3",
     "suspicion": "Actual utilization may differ from one cycle per day.",
     "unresolved_fact": "Measured cycles per bike per day from the fleet."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Arithmetic error in cost table", "evidence": "All rows recompute exactly from suppliers.csv: 410; 760+15=775; 1340+45=1385."},
    {"id": "R2", "candidate": "Swap labor misapplied", "evidence": "Labor is charged per replacement, consistently across suppliers; including first-fit labor adds $15 to every row and does not change the ranking."},
    {"id": "R3", "candidate": "Zesto battery count wrong", "evidence": "3 x 600 = 1,800 < 1,825, so 4 batteries is correct."}
  ]
}
```