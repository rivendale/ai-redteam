# Adversarial Diagnostic Review: Battery supplier TCO memo

## Pass 1: Reconstruct

The memo claims Zesto has the lowest five-year total cost of ownership and recommends it for a 3,080-bike fleet. Its only evidence is a table of purchase prices, and it treats "lowest price per battery" as "lowest TCO". For that to hold, battery replacements over five years would have to cost the same for every supplier, or not happen at all.

Load-bearing assumptions:
- Each bike uses one battery cycle per day. This is stated in the memo but has no source.
- Purchase price is the whole cost. This is unstated, and it ignores both `cycle_life` and `swap_labor_usd` in the CSV.
- Cycle life is defined the same way for all three suppliers. This is unstated and unverifiable from the material.
- The batteries do not age out by time (calendar life) within five years. This is unstated.

## Pass 2: Attack (Track A)

**Recomputing TCO from suppliers.csv** (hand arithmetic, no tools available):

- Five years at one cycle per day is 1,825 cycles, or 1,826 with the 2028 leap day. The result is the same either way.
- Batteries needed per bike over five years:
  - Volta: 1 (2,000 cycles covers 1,825)
  - Amperia: 2 (1,825 / 1,000, rounded up)
  - Zesto: 4 (1,825 / 600 = 3.04, rounded up)
- Five-year cost per bike, counting price plus $15 swap labor for each battery including the first:

| Supplier | Per bike | Fleet (×3,080) |
|---|---|---|
| Volta | 1 × $425 = **$425** | **$1,309,000** |
| Amperia | 2 × $395 = $790 | $2,433,200 |
| Zesto | 4 × $350 = $1,400 | $4,312,000 |

Two other ways of counting give the same ranking:
- **Excluding labor on the first install:** Volta $410, Amperia $775, Zesto $1,385 per bike.
- **Pro-rating cost per cycle** (no rounding up to whole batteries): Volta about $388, Zesto about $639, Amperia about $721 per bike. Volta still wins.
- **Discounting future replacements:** even at a 10% discount rate, Zesto stays near $1,100 or more per bike against Volta's $425.

Volta is cheapest under every reasonable method. On the memo's own usage assumption, Zesto costs about **$3.0M more** across the fleet than Volta.

**Logic:** The statement "lowest total cost of ownership at $335 per battery" is a category error. $335 is a unit purchase price, not a five-year TCO. The conclusion does not follow from the memo's premises. It contradicts them once you combine its own one-cycle-per-day statement with the CSV.

**Drift:** The request asked for a comparison of five-year TCO. The memo answered an easier question, "which battery is cheapest to buy?"

**Counter-case (the strongest case for Zesto):** Zesto wins only if each bike uses no more than 600 cycles in five years, which is about 0.33 cycles per day ($350 vs Volta's $425). Amperia wins between roughly 0.33 and 0.55 cycles per day. So the true answer depends on utilization. The memo asserts a figure, one cycle per day, under which Zesto is the worst option.

**Pre-mortem (why this decision failed a year from now):**
1. Zesto batteries began hitting end of life around month 20, triggering an unbudgeted fleet-wide replacement wave.
2. Replacement spend and swap labor ran about 3× the budget.
3. Bike downtime during swaps reduced availability. This cost is not modelled anywhere.

**Missing information a careful expert would demand:**
- Measured fleet utilization (cycles per bike per day).
- The cycle-life definition for each supplier, such as cycles to 80% capacity, and the test conditions.
- Calendar-life limits.
- Warranty terms.
- Volume pricing.
- Disposal and recycling cost.
- Spare-pool size and downtime cost.
- Residual value of the remaining Volta cycles at year five, which would favor Volta further.

## Pass 3: Self-check

Every finding below ties to a quoted line and to arithmetic on the CSV. The cross-supplier comparison is downgraded to UNVERIFIED where it depends on cycle-life definitions or calendar aging.

The most serious thing I could still be missing is calendar aging. If Volta's pack degrades by time to below usable capacity before five years, it would need a replacement too. Even then, Volta at 2 × $425 = $850 per bike still beats Zesto at $1,400. A hidden cost that applies to only one supplier, such as warranty or a special charger, could shift the Volta/Amperia gap but not rescue Zesto.

---

**VERDICT: REJECT.** The recommendation is the opposite of what the supplied data shows: on the memo's own usage assumption Zesto is the most expensive option over five years, by about $3.0M across the fleet.

**CONFIDENCE IN VERDICT: High.** The arithmetic uses only the CSV and the memo's stated usage. Confidence is limited by the unsourced utilization figure and by cycle-life definitions I cannot check.

## Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | "Zesto has the lowest total cost of ownership at $335 per battery. We recommend Zesto." | Purchase price is presented as TCO; the recommendation is wrong on the memo's own data | At 1 cycle/day, Zesto needs 4 batteries per bike over 5 years ($1,400/bike, $4.31M fleet) vs Volta's 1 ($425/bike, $1.31M); choosing Zesto costs about $3.0M extra | Compute five-year TCO as batteries needed × (price + swap labor) per bike × 3,080; re-decide |
| 2 | High | CONFIRMED (omission); truth UNVERIFIED | Table in memo.md; whole memo | `cycle_life` and `swap_labor_usd` from suppliers.csv are ignored; there is no five-year horizon, no fleet total and no method | A reader cannot see that replacements dominate cost; the decision is made on 1 of 3 cost inputs | Add the cycle_life, replacements, labor, per-bike TCO and fleet TCO columns; state the method |
| 3 | High | CONFIRMED unsourced; value UNVERIFIED | "Each bike uses its battery once a day." | The usage rate is the pivotal assumption and has no source. The winner flips with it: Zesto wins at ≤0.33 cycles/day, Amperia at about 0.33–0.55, Volta above that | If real utilization differs from 1/day, even a correctly computed TCO picks the wrong supplier | Pull measured cycles per bike per day from fleet telemetry; include a sensitivity table across utilization rates |
| 4 | Medium | UNVERIFIED | suppliers.csv `cycle_life` | Cycle-life ratings may use different end-of-life thresholds or test conditions across suppliers, and calendar aging is not considered | Volta's 2,000 cycles may be measured to a looser threshold, or may age out by time before 5 years, eroding its advantage | Obtain datasheets with the end-of-life definition, test conditions and calendar-life rating; check warranties |
| 5 | Medium | CONFIRMED (omission) | Whole memo | No alternatives or other cost lines: volume discounts, warranty, downtime, spares, disposal, residual value, discounting | TCO understated for high-replacement options; Volta's leftover cycles at year five go unvalued | Add these lines or explicitly scope them out with a rationale |

## What holds up

- The three prices in the memo's table match suppliers.csv exactly.
- Zesto is genuinely the cheapest to purchase.

## Unverified claims

- **"Each bike uses its battery once a day."** Confirm with telemetry or operations data.
- **Comparability of cycle-life figures across suppliers.** Confirm with supplier datasheets and warranty terms.
- **That swap labor is $15 for each supplier in all cases**, and whether it applies to the first install. Confirm with operations or the supplier quotes.

## Questions for the author

1. What is the source for one cycle per day, and what is the measured fleet average?
2. Why were `cycle_life` and `swap_labor_usd` left out of the TCO?
3. Are the cycle-life ratings defined to the same end-of-life threshold?

## Decision-maker summary

Do not adopt this recommendation. On the supplied data and the memo's own usage assumption, Volta is cheapest over five years (about $1.3M for the fleet), and Zesto is the most expensive (about $4.3M). Before deciding, confirm actual daily usage, because Zesto or Amperia would win only at much lower usage.

## Owner summary

The memo picked the battery that is cheapest to buy, but that battery wears out fastest and would need replacing about three times in five years. Counting replacements, it is the most expensive choice by roughly three million dollars across the fleet. The longer-lasting option looks cheapest overall, but how often the bikes are actually used should be confirmed before signing.

```json
{
  "verdict": "REJECT",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "memo.md: \"Zesto has the lowest total cost of ownership at $335 per battery. We recommend Zesto.\"",
      "scenario": "At the memo's stated 1 cycle/day (1,825 cycles over 5 years), Zesto (600-cycle life) needs 4 batteries per bike = 4 x ($335 + $15) = $1,400/bike, $4,312,000 for 3,080 bikes; Volta (2,000 cycles) needs 1 = $425/bike, $1,309,000. Choosing Zesto costs about $3.0M more.",
      "fix": "Compute five-year TCO as batteries needed x (price + swap labor) per bike x 3,080 for each supplier and re-decide; on current data Volta is lowest."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "memo.md price table; whole memo",
      "scenario": "cycle_life and swap_labor_usd from suppliers.csv are omitted, and there is no five-year horizon or fleet total, so the decision rests on purchase price alone and replacement costs are invisible.",
      "fix": "Add the cycle_life, replacements, labor, per-bike TCO and fleet TCO columns, and state the method."
    },
    {
      "severity": "High",
      "evidence_level": "UNVERIFIED",
      "location": "memo.md: \"Each bike uses its battery once a day.\"",
      "scenario": "The usage rate is unsourced and pivotal: Zesto wins at <=0.33 cycles/day, Amperia at about 0.33-0.55, Volta above that. A wrong rate picks the wrong supplier.",
      "fix": "Use measured cycles per bike per day from fleet telemetry; include a sensitivity table across utilization rates."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "suppliers.csv cycle_life column",
      "scenario": "Cycle-life ratings may use different end-of-life thresholds or test conditions, and calendar aging is ignored; Volta's advantage could shrink if its pack ages out by time before 5 years.",
      "fix": "Obtain datasheets (end-of-life definition, test conditions, calendar life) and warranty terms for all three suppliers."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "memo.md (whole)",
      "scenario": "No volume pricing, warranty, downtime, spares, disposal, residual value or discounting is considered, which understates TCO for high-replacement options.",
      "fix": "Add these cost lines, or explicitly scope them out with a rationale."
    }
  ]
}
```