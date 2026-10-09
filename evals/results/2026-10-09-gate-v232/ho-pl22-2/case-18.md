# Adversarial Diagnostic Review: Battery Supplier Memo

## Pass 1: Reconstruct

The memo claims Zesto has the lowest five-year total cost of ownership "at $335 per battery" and recommends Zesto for a fleet of 3,080 bikes. For this to be correct, TCO would have to equal the purchase price of a single battery. That only holds if every battery lasts the full five years, or if replacements and labor cost nothing.

The load-bearing assumptions are:
- **Unstated:** purchase price is a valid proxy for TCO.
- **Unstated:** cycle life and swap labor can be ignored.
- **Stated but unsourced:** each bike uses its battery once a day. This appears nowhere in the request or the CSV.
- **Unstated:** no discounting, salvage value, calendar aging, warranty or downtime effects.

The first assumption is false on the memo's own data.

## Pass 2: Attack (Track A)

**Recomputing TCO from suppliers.csv.** Inputs: once-daily use (the memo's figure), 5 years ≈ 1,825 cycles, $15 per swap, including the initial install.

| Supplier | Batteries per bike over 5 yrs | Per bike (battery + labor) | Fleet (×3,080) | Fleet without labor |
|---|---|---|---|---|
| Volta | ⌈1825/2000⌉ = 1 | $410 + $15 = **$425** | **$1,309,000** | $1,262,800 |
| Amperia | ⌈1825/1000⌉ = 2 | $760 + $30 = $790 | $2,433,200 | $2,340,800 |
| Zesto | ⌈1825/600⌉ = 4 | $1,340 + $60 = $1,400 | $4,312,000 | $4,127,200 |

The ranking does not change under other reasonable methods:
- **Cost per cycle:** Volta $0.2125, Amperia $0.395, Zesto $0.583.
- **Excluding labor:** Volta still wins.
- **Using 1,826 days for a leap year:** same battery counts.

Zesto is the most expensive option. It costs about 3.3× Volta, roughly $3.0M more over the contract.

**Discounting.** Zesto's replacements fall at about years 1.6, 3.3 and 4.9. Even at a 10% discount rate, their present value cannot close a $975-per-bike gap.

**Sensitivity to usage.** The answer hinges on usage, which the memo asserts without a source.
- Zesto wins only if a bike uses ≤600 cycles in five years (about 0.33/day), at $350 vs $425 per bike.
- Amperia wins at 601–1,000 cycles.
- Volta wins above 1,000 cycles, about 0.55/day.

Bike-share usage is more plausibly at or above once a day, so higher usage strengthens Volta's lead. At 2 cycles/day, Volta costs $850 per bike vs Zesto $2,450.

**Counter-case for Zesto.** The best argument is low utilization, steep calendar degradation of Volta packs, or a much cheaper Zesto model in years 2–5. None of these is evidenced, and the memo makes none of these arguments.

**Pre-mortem: why choosing Zesto fails.**
1. The procurement budget is blown by about 9,240 unplanned replacement batteries.
2. Swap operations and downtime triple.
3. Supplier capacity or price changes affect roughly 12,320 batteries instead of 3,080.

## Pass 3: Self-check

Every finding below ties to a line in memo.md or to arithmetic on suppliers.csv.

I downgraded the "missing factors" finding to UNVERIFIED and Medium, because those factors could matter but I cannot show that they do.

The most serious thing I could still be missing is a definition of `cycle_life` that changes the math. For example, if it means cycles to 80% capacity and batteries stay in service well past that point, effective lives would change. Volta's 2,000-cycle pack would also face five years of calendar aging, which could shorten its real life. Neither factor is likely to flip a 3× gap, but both should be confirmed with the suppliers.

---

**VERDICT: REJECT.** The memo equates sticker price with TCO, ignores the cycle-life and labor data it was given, and recommends the most expensive supplier. Volta is cheapest over five years on the provided numbers.

**CONFIDENCE IN VERDICT: high.** The error is arithmetic on the memo's own inputs. What limits confidence is the actual utilization rate and the definition of cycle life, but the ranking holds for any usage above about 0.55 cycles/day.

## Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | memo.md: "Zesto has the lowest total cost of ownership at $335 per battery. We recommend Zesto." | Purchase price is presented as TCO. The `cycle_life` and `swap_labor_usd` columns are ignored. | At once-daily use, Zesto needs 4 batteries per bike. Fleet cost is $4.31M vs $1.31M for Volta, about $3.0M overspent over the contract. | Recompute TCO = ⌈5-yr cycles / cycle_life⌉ × (price + labor) × 3,080, and re-rank. Volta comes first. |
| 2 | High | CONFIRMED | memo.md title and table | Drift: the memo answers "which battery is cheapest to buy," not five-year TCO. There is no horizon, no replacement count and no fleet total. | A decision-maker reads "five-year TCO" in the title and trusts a number that is a one-time unit price. | Show per-bike and fleet five-year totals, with the method stated. |
| 3 | High | CONFIRMED (unsourced); impact PROBABLE | memo.md: "Each bike uses its battery once a day." | The one assumption that determines the answer is unsourced, and the memo never uses it. | Below about 0.33 cycles/day Zesto wins; at 0.33–0.55 Amperia wins; above that Volta wins. Without real fleet data, the choice is unvalidated. | Pull actual charge-cycle telemetry for the fleet, and include a breakeven or sensitivity table. |
| 4 | Medium | CONFIRMED | memo.md table | The table omits cycle life and labor, which hides the decisive data from the reader. | A reviewer skimming the memo cannot see that Zesto lasts 30% as long as Volta. | Include all CSV columns plus derived replacement counts. |
| 5 | Medium | UNVERIFIED | Absent from memo | No treatment of calendar aging, warranty, how cycle life is defined (for example, to 80% capacity), salvage or disposal, downtime, discount rate, or whether each supplier can deliver the volume. | A pack rated 2,000 cycles may still fail on calendar age before year 5. Zesto would require about 12,320 batteries in total. | Obtain spec sheets and warranty terms, and run a discounted TCO and a supplier-capacity check. |
| 6 | Low | PROBABLE | suppliers.csv `swap_labor_usd` | It is unclear whether the initial install incurs swap labor. | Totals shift by $15 per bike ($46,200 fleet-wide). The ranking does not change. | State the convention. |

## What Holds Up

The three unit prices in the memo match suppliers.csv exactly. Zesto does have the lowest purchase price.

## Unverified Claims

- **"Each bike uses its battery once a day."** Confirm with fleet charge telemetry.
- **"Lowest total cost of ownership."** This is refuted by the CSV data, as shown above.
- **Cycle-life figures as supplier-tested values under comparable conditions.** Confirm with datasheets and test standards.

## Questions for the Author

1. What is the measured cycles per bike per day, and where does "once a day" come from?
2. Why were `cycle_life` and `swap_labor_usd` excluded from the TCO?
3. Do any calendar-life or warranty limits cap Volta's effective life below five years?

## Decision-Maker Summary

Do not adopt Zesto on this memo. On the memo's own data, Volta costs about $1.31M over five years vs Amperia's $2.43M and Zesto's $4.31M. Before contracting, confirm actual daily usage and Volta's calendar and warranty life, since very low utilization (under about 0.55 cycles/day) would change the ranking.

## Owner Summary

The memo picked the battery with the lowest sticker price, but that battery wears out fastest and would need replacing about four times over five years. Counting replacements and installation labor, the most expensive battery to buy is actually the cheapest to own, by roughly three million dollars across the fleet. The recommendation should be redone with real usage figures before any contract is signed.

```json
{
  "verdict": "REJECT",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "memo.md: 'Zesto has the lowest total cost of ownership at $335 per battery. We recommend Zesto.'",
      "scenario": "TCO is equated with purchase price, ignoring cycle_life and swap_labor_usd. At once-daily use (1,825 cycles), Zesto needs 4 batteries per bike: $1,400/bike, $4,312,000 fleet, vs Volta $425/bike, $1,309,000 fleet. Choosing Zesto overspends about $3.0M.",
      "fix": "Compute TCO = ceil(5-yr cycles / cycle_life) x (price + swap labor) x 3,080 and re-rank; Volta is lowest."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "memo.md title and price table",
      "scenario": "Drift: the memo answers 'cheapest unit price', not five-year TCO. There is no horizon, no replacement count and no fleet total, so a reader trusts a mislabeled number.",
      "fix": "Present per-bike and fleet five-year totals with the method stated."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "memo.md: 'Each bike uses its battery once a day.'",
      "scenario": "The decisive usage assumption is unsourced and unused. Below about 0.33 cycles/day Zesto wins, at 0.33-0.55 Amperia wins, and above that Volta wins, so the choice is unvalidated without real data.",
      "fix": "Source utilization from fleet charge telemetry and add a breakeven or sensitivity table."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "memo.md table (omits cycle_life and swap_labor_usd)",
      "scenario": "A reader cannot see that Zesto's cycle life is 30% of Volta's, so the error is invisible on review.",
      "fix": "Show all CSV columns plus derived replacements per bike."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "Absent from memo: calendar aging, warranty, cycle-life definition, salvage, downtime, discounting, supplier capacity",
      "scenario": "A 2,000-cycle pack may hit calendar end-of-life before year 5. Zesto would need about 12,320 batteries in total, a capacity and price risk.",
      "fix": "Obtain datasheets and warranty terms, and run a discounted TCO and a supplier-capacity check."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "suppliers.csv swap_labor_usd",
      "scenario": "It is ambiguous whether the initial install incurs labor. This shifts totals by $15/bike ($46,200 fleet) without changing the ranking.",
      "fix": "State the labor convention explicitly."
    }
  ]
}
```