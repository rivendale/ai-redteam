# Adversarial Diagnostic Review: Battery supplier TCO memo

## Pass 1: Reconstruct

The memo claims Volta has the lowest five-year cost per bike ($410, against $775 for Amperia and $1,385 for Zesto), even though it has the highest price per battery, and it recommends Volta. The result rests on four things:

1. Each bike uses exactly one cycle per day, so 1,825 cycles over five years. This is stated without a source, and nothing in the request or the CSV supports it.
2. Batteries last exactly their listed cycle life, read as vendor spec equals real field replacement point.
3. Total cost of ownership means purchase price plus swap labor and nothing else. This is unstated.
4. A leftover battery has no value at the end of five years, and money spent later counts the same as money spent now. Both are unstated.

The CSV values are transcribed correctly. I re-derived the arithmetic and it is correct:

| Supplier | Cycles per battery | Batteries needed (1,825 ÷ life, rounded up) | Battery cost | Swaps | Labor | Total |
|---|---|---|---|---|---|---|
| Volta | 2,000 | 1 | $410 | 0 | $0 | $410 |
| Amperia | 1,000 | 2 | $760 | 1 | $15 | $775 |
| Zesto | 600 | 4 (1,825 ÷ 600 = 3.04) | $1,340 | 3 | $45 | $1,385 |

## Pass 2: Attack (Track A)

**Facts.** All prices, cycle lives and labor costs match suppliers.csv, and "highest price per battery" is true ($410 > $380 > $335). The only fact the memo introduces is the one-cycle-per-day usage rate, which has no source.

**Logic and sensitivity.** I tested whether the recommendation survives different assumptions.

- **Cost per cycle.** Volta costs $0.205 per cycle ($410 ÷ 2,000), Amperia $0.38 and Zesto about $0.56. Volta is cheapest by this measure regardless of rounding.
- **Usage rate.** I recomputed the winner at different total usage over five years:
  - At 600 cycles or fewer (about 0.33 per day), every supplier needs only one battery, so Zesto wins at $335.
  - Between 601 and 1,000 cycles (up to about 0.55 per day), Amperia wins at $380, against Volta at $410 and Zesto at $685.
  - Above 1,000 cycles, Volta wins at every level I checked: at 2 cycles per day it costs $835, against $1,565 for Amperia and $2,435 for Zesto.
  
  So the choice of Volta holds for any usage above about 0.55 cycles per day. The memo states none of this.
- **Leftover battery value.** If unused battery life is credited on a pro-rata basis, the totals become about $374 for Volta, $709 for Amperia and $1,062 for Zesto. Volta still wins.
- **Discounting.** Discounting future costs helps the suppliers whose purchases come later, which is Amperia and Zesto. Their gaps to Volta ($365 and $975 per bike) are far larger than any realistic discounting effect over five years. Volta still wins.

**The fragile point.** The one-battery result for Volta has only 175 cycles of headroom (2,000 against 1,825, about 9.6%). If a bike actually uses more than about 1.096 cycles per day, or if Volta batteries in the field last fewer than 1,825 cycles, that bike needs a second Volta battery. Its cost then becomes $835, which is more than Amperia's $775, unless Amperia batteries fall short of their spec by a similar amount. The memo presents $410 as exact and includes no sensitivity analysis.

**Counter-case.** The strongest argument against Volta is that its advantage depends on a vendor cycle-life figure that nobody has checked. It also depends on usage being uniform across the fleet, when bike-share usage is typically uneven. With a five-year commitment to a single supplier, a shortfall in Volta's real cycle life could erase the margin on the most heavily used bikes. A split or pilot purchase would hedge that risk. Even so, the per-cycle advantage is large enough that Volta survives unless its shortfall is specific to Volta.

**Pre-mortem.** If this choice looks bad in a year, the three most likely reasons are:

1. Volta's real cycle life comes in below about 1,825, for example because the 2,000 figure is measured to 80% capacity under lab conditions. Heavy-use bikes then need a second battery and the budget is blown.
2. Battery aging over time, not just cycle count, forces replacements before year five.
3. Single-supplier risk: Volta has failure rates, warranty disputes or supply problems, and there is no fallback.

**Scope drift.** The request asks for total cost of ownership. The memo covers purchase and swap labor only. It leaves out failure and warranty rates, end-of-life disposal or recycling, downtime, leftover value, and charging energy (which probably differs little between suppliers). It also never says it is leaving these out. And with stakes of 3,080 bikes, it gives no fleet-level total: by my calculation that is about $1.26M for Volta, $2.39M for Amperia and $4.27M for Zesto.

## Pass 3: Self-check

I dropped a possible finding about first-install labor. It is excluded for all three suppliers equally, so it does not affect the comparison.

I downgraded the usage-rate finding from Critical to High. Volta remains the right choice across a wide range of usage, but the budget figure is fragile.

The most serious problem that could still be hiding is how "cycle_life" is defined in the CSV: whether it means cycles to 80% capacity or to end of life, and whether all three suppliers define it the same way. If the definitions differ, the comparison is not apples to apples. I cannot settle this from the material provided.

---

**VERDICT: SHIP WITH FIXES.** The arithmetic is correct and Volta wins under any reasonable assumption above about 0.55 cycles per day, but the memo hides an unsourced usage rate, a 9.6% headroom margin that drives its budget figure, and a narrowed definition of total cost of ownership.

**CONFIDENCE IN VERDICT: medium.** It is limited by not knowing the real usage distribution, how each supplier defines cycle life, or their warranty and failure terms.

## Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | High | CONFIRMED (the assumption is unsourced); the impact is calculated | "Each bike uses its battery once a day: 1,825 cycles" | The usage rate that drives every number has no source and is applied uniformly to all bikes. | Bike-share usage varies by bike. Any bike above about 1.096 cycles per day needs a second Volta battery, costing $835 instead of $410, so the fleet budget is understated. Below 0.55 per day, the winner changes to Amperia or Zesto. | Cite fleet telemetry for the average and the spread of cycles per bike per day. State the break-even thresholds (Zesto at 600 cycles or fewer, Amperia at 601 to 1,000, Volta above 1,000). Report fleet cost using the real usage spread. |
| 2 | High | PROBABLE | Volta row, "Batteries over 5 years: 1" | The one-battery result depends on Volta meeting its 2,000-cycle spec with only 175 cycles to spare. The memo shows no sensitivity check. | Field cycle life of 1,800 or less means a second battery: $835 per bike, about $2.57M fleet-wide, more than Amperia's $775 if only Volta underperforms. | Get Volta's cycle-life test conditions and warranty terms, and show the result if all specs are 10–20% lower. Consider a pilot or a cycle-life guarantee in the contract. |
| 3 | Medium | CONFIRMED | The memo's title and table, compared with the request's "total cost of ownership" | Total cost of ownership is narrowed to purchase plus labor without saying so. Failures and warranty, disposal, downtime, leftover value, energy, and aging over time are all left out. | A higher Volta failure rate or worse warranty terms, a disposal cost, or calendar aging could narrow the gap. The reader assumes full TCO was assessed. | State the cost categories the memo excludes, or add them. At minimum, add warranty and failure-rate terms and calendar-life specs for each supplier. |
| 4 | Medium | UNVERIFIED | suppliers.csv `cycle_life` column | It is not established that all three suppliers measure cycle life to the same standard (for example, depth of discharge or end-of-life capacity). | If Volta's 2,000 cycles is measured to 70% capacity and Amperia's 1,000 to 80%, the ranking compares unlike figures. | Obtain the test standard from each supplier's datasheet. |
| 5 | Low | CONFIRMED | Recommendation section | There is no fleet-level total and no mention of the risk of committing to one supplier for five years, despite the 3,080-bike stakes. | A decision-maker cannot see the roughly $1.1M savings against Amperia or the concentration risk. | Add fleet totals and one line on supplier risk and exit terms. |

## What holds up

- The CSV values are transcribed correctly.
- The battery counts, swap counts and per-bike totals are all correct.
- Volta has the lowest cost per cycle by a wide margin, so the ranking survives three changes I tested: crediting leftover battery value, discounting future costs, and any usage above about 0.55 cycles per day.

## Unverified claims

- **One cycle per day per bike.** Confirm with fleet telemetry, including the spread across bikes.
- **Cycle lives as real replacement points.** Confirm with supplier test standards, warranty terms and field data from reference customers.
- **Zero cost for disposal, failures and downtime.** Confirm with supplier quotes and contract terms.

## Questions for the author

1. Where does the one-cycle-per-day figure come from, and what does the spread of cycles per bike look like?
2. Are the three cycle-life figures measured to the same standard, and does any supplier guarantee its figure?
3. Did you deliberately exclude warranty, failure, disposal and calendar-aging costs from total cost of ownership?

## Decision-maker summary

Volta is very likely the right choice: it is cheapest per cycle by nearly half and wins across a wide range of assumptions. The memo's $410-per-bike figure, however, is fragile. Before signing a five-year contract, confirm real usage per bike and Volta's tested cycle life, and secure a cycle-life warranty. Otherwise heavy-use bikes may need a second battery and the fleet budget could roughly double.

## Owner summary

The recommended battery supplier looks like the best value, and the math in the memo checks out. However, the savings depend on each bike's battery lasting the full five years. That only holds if bikes are used about once a day and the batteries perform as the supplier claims, and neither has been confirmed. Check real usage and get a lifespan guarantee in writing before committing.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "memo.md: 'Each bike uses its battery once a day: 1,825 cycles in five years'",
      "scenario": "Usage rate is unsourced and applied uniformly; bikes above ~1.096 cycles/day need a second Volta battery ($835 vs $410), understating fleet cost; below 0.55/day the winner flips to Amperia or Zesto.",
      "fix": "Source usage from fleet telemetry including the spread across bikes; state break-even thresholds (Zesto <=600 cycles, Amperia 601-1,000, Volta >1,000); compute fleet cost from the actual distribution."
    },
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "memo.md table, Volta row 'Batteries over 5 years: 1'",
      "scenario": "Only 175 cycles (9.6%) of headroom; if Volta's field cycle life falls below 1,825, cost becomes $835/bike (~$2.57M fleet), exceeding Amperia's $775 if only Volta underperforms.",
      "fix": "Run a sensitivity case with specs derated 10-20%; obtain Volta's test conditions; negotiate a cycle-life warranty or run a pilot."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "memo.md title and table vs request 'total cost of ownership'",
      "scenario": "TCO silently reduced to purchase plus swap labor; failure/warranty, disposal, downtime, residual value, energy and calendar aging omitted, so the reader assumes a full TCO was done.",
      "fix": "List excluded cost categories or add them; at minimum include warranty/failure terms and calendar-life specs per supplier."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "suppliers.csv cycle_life column",
      "scenario": "Suppliers may rate cycle life to different end-of-life capacities or depths of discharge, making the comparison apples-to-oranges.",
      "fix": "Obtain each supplier's cycle-life test standard from their datasheet."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "memo.md recommendation paragraph",
      "scenario": "No fleet-level totals (~$1.26M vs $2.39M vs $4.27M for 3,080 bikes) and no mention of single-supplier concentration risk over five years.",
      "fix": "Add fleet totals and a line on supplier risk and exit terms."
    }
  ]
}
```