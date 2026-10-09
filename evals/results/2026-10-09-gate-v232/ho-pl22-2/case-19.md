VERDICT: SHIP WITH FIXES. The arithmetic is correct and Volta stays cheapest under most realistic variations, but the result depends on two unexamined assumptions (one cycle per day, and no calendar ageing over five years), and either one can flip the answer to Amperia.

CONFIDENCE IN VERDICT: medium. I checked every number against suppliers.csv. I could not check the real fleet usage rate or the suppliers' calendar-life and warranty terms, and those decide whether the recommendation is safe.

## Pass 1: Reconstruct

The memo assumes 1,825 cycles per bike over five years (one per day). It assumes each battery is replaced exactly at its rated cycle life, with $15 labour per replacement. On that basis it computes a per-bike five-year cost and recommends Volta, the highest unit price but the longest life.

The recommendation depends on these assumptions:

- **(a)** Usage is about one full cycle per day. This is stated but has no source, and it is not in the CSV.
- **(b)** Rated cycle life is the only thing that ends a battery's life. Calendar ageing, failures and warranty are not considered.
- **(c)** Purchase plus swap labour is all of TCO.
- **(d)** Per-bike cost scales linearly to the 3,080-bike fleet.

## Pass 2: Attack (Track A)

**Arithmetic check (CONFIRMED correct):**

| Supplier | Batteries needed | Purchase | Swaps | Total per bike |
|---|---|---|---|---|
| Volta | ⌈1825/2000⌉ = 1 | 1 × 410 = 410 | 0 | **$410** |
| Amperia | ⌈1825/1000⌉ = 2 | 2 × 380 = 760 | 1 × 15 = 15 | **$775** |
| Zesto | ⌈1825/600⌉ = 4 (3 × 600 = 1,800 < 1,825) | 4 × 335 = 1,340 | 3 × 15 = 45 | **$1,385** |

All of these match the memo.

**Counter-case tests I ran by hand:**

- **Pro-rata residual value.** Charge only the cycles actually used, so a part-used last battery is not counted in full. Volta comes to $374, Amperia $709 and Zesto $1,064 (including labour). The ranking holds.
- **Higher usage, 2 cycles per day (3,650 cycles).** Volta $835, Amperia $1,565, Zesto $2,435. The ranking holds.
- **Lower usage, at or below 1,000 cycles in five years (about 0.55 per day or less).** Volta $410 and Amperia $380. **Amperia wins.**
- **Volta needs a second battery because of calendar ageing.** Volta becomes 820 + 15 = $835, against Amperia's $775. **Amperia wins** by $60 per bike, which is about $185k across the fleet.
- **Discounting.** Volta's cost is all up front, so discounting future purchases makes the others look somewhat better. The gaps are too large for that to change the ranking. It holds.

## FINDINGS

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | High | PROBABLE (the flip is CONFIRMED by arithmetic; whether it happens is UNVERIFIED) | "A battery is replaced when it reaches its cycle life" | Cycle life is treated as the only end-of-life trigger. Under the Volta plan each battery must last the full five years, and calendar ageing is never considered. Amperia batteries are replaced at about 2.7 years. | If Volta packs degrade below a usable level, or out of warranty, before year five, every bike needs a second Volta pack. Volta then costs $835 per bike against Amperia's $775, and the recommendation reverses: about $185k extra across 3,080 bikes. | Get each supplier's rated calendar life, the end-of-life definition behind its cycle rating (for example 80% capacity) and warranty terms. Rerun the comparison with replacement at whichever of cycle life or calendar life comes first. |
| 2 | Medium | CONFIRMED (no source in the memo or CSV) | "Each bike uses its battery once a day: 1,825 cycles" | The usage rate is the main input and has no source. Bike-share battery cycles depend on energy use per day, not on trips. | If real usage is 0.55 full cycles per day or less (1,000 or fewer cycles), Amperia is cheaper ($380 against $410, about $92k across the fleet). Above that, Volta wins at every usage level I tested. | Use measured fleet data on daily state-of-charge consumption. Add one line to the memo giving the break-even point ("Volta wins above about 1,000 cycles in five years"). |
| 3 | Medium | CONFIRMED | Whole memo | No assumptions or limitations section. TCO is narrowed to purchase plus labour without saying so. Missing items: disposal and recycling, failure and warranty returns, bike downtime during swaps, spare stock, volume pricing. | A reader takes "total cost of ownership" at face value. Costs the memo left out, which hit long-life single-pack plans hardest (failure exposure), come up later. | State the scope explicitly. At minimum, ask suppliers for failure rate and warranty terms. |
| 4 | Low | CONFIRMED | Table | Costs are shown per bike only. The fleet is 3,080 bikes, and the decision is made at fleet level. | The decision-maker cannot see the size of the gap: Volta about $1.26M, Amperia $2.39M, Zesto $4.27M. | Add a fleet-total column. |
| 5 | Low | PROBABLE | "Swap labor $0" for Volta | Labour for the first installation is left out for all three suppliers. The CSV column `swap_labor_usd` does not say whether it covers the first fit. | This adds $15 to every supplier, so the ranking does not change. The fleet total is understated by about $46k if the first fit is billed. | State the convention you used. |

## WHAT HOLDS UP

- Every figure in the table matches suppliers.csv under the memo's own rules, including the ceiling for Zesto (four packs, not three).
- The ranking survives pro-rata residual value, discounting, and any usage level above about 1,000 cycles in five years.
- The memo answers the question that was asked: a five-year comparison of all three suppliers with a single recommendation. It does not drift to an easier question.

## UNVERIFIED CLAIMS

- **One cycle per day.** Confirm it from fleet telemetry (energy per bike per day).
- **Cycle life is the effective replacement point.** Confirm it from supplier datasheets: how end-of-life is defined, and the rated calendar life.
- **$15 is the full cost of a swap.** Confirm it with operations: does it include bike downtime and the first installation?

## QUESTIONS FOR THE AUTHOR

1. What is Volta's rated calendar life or warranty period? Is it at least five years?
2. What is the measured average depth of discharge per bike per day?

## DECISION-MAKER SUMMARY

Volta is the right pick if its packs really last five years and bikes use at least about half a full charge per day. Before signing, get Volta's calendar-life and warranty terms in writing and check fleet usage data. If Volta packs need replacing even once in five years, Amperia becomes about $185k cheaper across the fleet.

## OWNER SUMMARY

The memo's maths is right, and the longest-lasting battery looks like the best value over five years. That conclusion assumes each battery lasts the full five years and that bikes are used heavily every day, and neither has been checked. Confirm both with the supplier and with real usage records before committing to a five-year contract.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "memo.md: 'A battery is replaced when it reaches its cycle life'",
      "scenario": "Volta packs hit calendar/warranty end-of-life before year 5; each bike needs a second Volta pack: $835/bike vs Amperia $775, recommendation reverses (~$185k extra across 3,080 bikes).",
      "fix": "Obtain calendar life, end-of-life definition and warranty from each supplier; recompute with replacement at the earlier of cycle or calendar life."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "memo.md: 'Each bike uses its battery once a day: 1,825 cycles'",
      "scenario": "Usage assumption is unsourced; at <=1,000 cycles in five years (~0.55/day or less) Amperia costs $380 vs Volta $410 (~$92k fleet-wide).",
      "fix": "Source usage from fleet telemetry; state the ~1,000-cycle break-even in the memo."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "memo.md: whole memo (no assumptions/limitations section)",
      "scenario": "TCO silently limited to purchase plus labor; disposal, failures, warranty, downtime and spares omitted, surfacing as unplanned cost later.",
      "fix": "State scope explicitly; request failure-rate and warranty data from suppliers."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "memo.md: cost table",
      "scenario": "Only per-bike costs shown for a 3,080-bike decision; fleet totals (~$1.26M / $2.39M / $4.27M) not visible.",
      "fix": "Add a fleet-total column."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "memo.md: 'Swap labor $0' for Volta",
      "scenario": "Initial-fit labor excluded for all suppliers; ranking unchanged but fleet total understated by ~$46k if the first fit is billed.",
      "fix": "State whether swap_labor_usd applies to the initial installation."
    }
  ]
}
```