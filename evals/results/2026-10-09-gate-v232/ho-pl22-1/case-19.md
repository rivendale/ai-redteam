**VERDICT: SHIP WITH FIXES.** The arithmetic is correct and Volta comes out cheapest under most plausible usage levels. But the memo rests on a usage rate it never sources and never tests, and it ignores the one realistic case where its single-battery advantage disappears.

**CONFIDENCE IN VERDICT: medium.** I re-did all of the arithmetic by hand from the memo and the CSV. I could not see fleet usage data, battery calendar-life specs or supplier warranty terms, and those are what could change the answer.

## Pass 1: Reconstruct

The memo says Volta has the lowest five-year cost per bike ($410, against $775 for Amperia and $1,385 for Zesto), even though it has the highest unit price, and recommends it. For that to hold:

- **Usage:** each bike uses about 1 cycle per day, so 1,825 cycles over five years. This is unstated in the inputs and appears nowhere in the request or the CSV.
- **Cycle life:** each battery reaches its rated cycle life in service, and nothing else (age, heat, defects) retires it sooner.
- **Scope of cost:** price plus swap labor is the whole cost that matters. Disposal, warranty, downtime, discounting, volume pricing and supply capacity are left out.
- **Volta's margin:** one Volta battery survives the full five years. At 1,825 of 2,000 cycles that leaves only 8.75% headroom.

## Pass 2: Attack (Track A)

**Facts.** Prices, cycle lives and the $15 labor match `suppliers.csv` (CONFIRMED). Battery counts are CONFIRMED:

| Supplier | Cycle life | Calculation | Batteries |
|---|---|---|---|
| Volta | 2,000 | 1,825 / 2,000, rounded up | 1 |
| Amperia | 1,000 | 1,825 / 1,000 = 1.825, rounded up | 2 |
| Zesto | 600 | 1,825 / 600 = 3.04, rounded up | 4 |

Purchase and labor totals are also CONFIRMED:
- Volta: 1 × $410 = $410.
- Amperia: 2 × $380 = $760, plus 1 swap at $15, gives $775.
- Zesto: 4 × $335 = $1,340, plus 3 swaps × $15 = $45, gives $1,385.

The memo counts no labor for the first installation, and it does so for all three suppliers, so the comparison stays consistent. The "once a day" rate is the only input with no source.

**Logic and sensitivity.** I tested the ranking against different usage levels (CONFIRMED by hand):

| Five-year cycles | Daily rate | Cheapest | Result |
|---|---|---|---|
| Under 600 | under ~0.33/day | Zesto | $335 |
| 600 to 1,000 | ~0.33 to 0.55/day | Amperia | $380 |
| 1,825 (memo's case) | 1.0/day | Volta | $410 |
| 3,650 | 2.0/day | Volta | $835, vs Amperia $1,565 and Zesto $2,435 |

So the recommendation holds whenever usage is above about 0.55 cycles per day. On cost per cycle, Volta is cheapest at any high usage: $0.205, against $0.38 for Amperia and $0.56 for Zesto.

Other checks:
- **Uniform shortfall in real life:** if every supplier's batteries deliver 10% fewer cycles than rated, Volta still wins ($835 vs $1,170 for Amperia).
- **Volta-only shortfall:** the ranking flips only if Volta's single battery fails to last five years while Amperia's do not. Volta then costs $410 + $410 + $15 = $835, which is more than Amperia's $775.

**Counter-case.** The strongest argument against Volta is this. One battery has to live five full years, at 91% of its rated cycles. Lithium batteries also age with time, not just with use. An Amperia battery is in service for only about 2.7 years. If Volta's battery hits a calendar limit, or a warranty or end-of-life definition (for example 80% capacity) before year five, Volta becomes the more expensive choice. The memo doesn't address this.

**Pre-mortem.** If this decision fails, the likely causes are:
1. Volta batteries degrade with age before year five, so a second full purchase is needed across 3,080 bikes.
2. Real usage turns out lower than 1 cycle per day. This is unlikely for bike-share, but it was never checked.
3. Volta cannot supply 3,080 bikes reliably, or its warranty is weak.

**Costs omitted.** These mostly favor Volta or do not change the ranking:
- **Disposal and downtime:** both scale with the number of batteries, which favors Volta.
- **Discounting:** at 8%, Amperia's second battery is worth about $311 today, so Amperia totals about $691. That is still above $410.
- **Residual value:** Amperia's last battery has 82% of its life left and Zesto's has 96%. Even crediting that, Volta wins: about $374 for Volta, $462 for Amperia and $1,065 for Zesto.
- **Volume pricing:** likely, but not in the CSV.

**Fleet scale.** The memo gives no fleet total. At 3,080 bikes:
- Volta costs about $1.26M.
- Amperia costs about $2.39M.
- Zesto costs about $4.27M.

**Bias.** The memo states the usage assumption as a fact and gives no margin or break-even. Its confidence is higher than the evidence on usage supports.

## Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | High | UNVERIFIED | memo.md line 3, "A battery is replaced when it reaches its cycle life" | The memo assumes cycle count is the only reason a battery is retired. Volta's case depends on one battery lasting the full five years, with 8.75% cycle headroom and no consideration of age. | If Volta batteries hit a calendar-age or capacity end-of-life before year five, each bike needs a second battery: $835 per bike, which is more than Amperia's $775. Across the fleet that is about $185k worse than Amperia, and about $1.26M of extra spend. | Get Volta's calendar-life spec, warranty term and end-of-life capacity definition. Add a scenario where Volta needs two batteries. |
| 2 | Medium | CONFIRMED (assumption unsourced) | memo.md line 3, "Each bike uses its battery once a day" | The usage rate is not in the request or the CSV. It is stated as fact, and no sensitivity is shown. | Below about 1,000 cycles in five years (about 0.55 per day), Amperia is cheapest. Below 600 cycles, Zesto is cheapest. | Take cycles per bike from fleet telemetry. Show the break-even points (600 and 1,000 cycles) and the spread of usage across bikes. |
| 3 | Low | CONFIRMED | memo.md table | The memo gives no fleet-level total and ignores disposal, downtime, discounting, residual value, volume pricing and Volta's capacity to supply 3,080 bikes. | The decision-maker cannot see the roughly $1.1M gap at fleet scale or the supply risk. None of the omitted costs I checked reverses the ranking. | Add a fleet total and a short line on omitted costs. Confirm Volta can supply 3,080 bikes. |

## What holds up

- All of the arithmetic.
- The rounding up of battery counts. Zesto's fourth battery covers only 25 cycles, but even three batteries ($1,035) lose to Volta.
- The ranking under faster usage, a uniform real-world shortfall, discounting and residual-value credit.
- The fact that the memo answers the request as asked: five-year total cost, a comparison of all three suppliers, and a recommendation.

## Unverified claims

- **One cycle per day.** Confirm with fleet telemetry on cycles per bike per day.
- **Batteries last to their rated cycle life with no calendar limit.** Confirm with supplier datasheets and warranty terms.
- **Price and labor are the whole total cost of ownership.** Confirm against operations figures for disposal and downtime.

## Questions for the author

1. What is the measured average usage, and how widely does it vary across bikes?
2. What are Volta's calendar life and warranty term, and how is "end of life" defined?
3. Can Volta supply 3,080 bikes and their spares?

## Decision-maker summary

Volta is the right pick on the numbers given, and that holds across most usage levels. Before signing for five years, confirm from the supplier that a Volta battery is rated and warranted to last the full five years by age as well as by cycles. If it is not, Volta needs a second battery per bike and becomes more expensive than Amperia, about $185k more across the fleet.

## Owner summary

The memo's math is right, and the recommended supplier is cheapest over five years as long as bikes are used at least about every other day. Its advantage depends on each of its batteries lasting the full five years. Before committing, ask the supplier to confirm in writing that its batteries are guaranteed to last that long, and check actual bike usage.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {
      "severity": "High",
      "evidence_level": "UNVERIFIED",
      "location": "memo.md line 3: 'A battery is replaced when it reaches its cycle life'",
      "scenario": "Volta's single battery must last 5 years at 91% of rated cycles; if calendar aging, warranty term or an 80%-capacity end-of-life definition forces replacement before year five, Volta costs $835/bike vs Amperia's $775, about $185k worse across 3,080 bikes.",
      "fix": "Obtain Volta calendar-life, warranty and end-of-life spec; add a two-battery Volta scenario to the memo."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "memo.md line 3: 'Each bike uses its battery once a day'",
      "scenario": "Usage rate is unsourced (not in request or CSV); below ~1,000 five-year cycles (~0.55/day) Amperia is cheapest, below 600 Zesto is cheapest.",
      "fix": "Source cycles/bike/day from fleet telemetry and show break-evens at 600 and 1,000 cycles plus per-bike usage spread."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "memo.md table",
      "scenario": "No fleet-level total (~$1.26M Volta vs ~$2.39M Amperia vs ~$4.27M Zesto) and omitted costs (disposal, downtime, discounting, residual value, volume pricing, Volta supply capacity for 3,080 bikes); none checked reverses the ranking but the decision-maker cannot see scale or supply risk.",
      "fix": "Add fleet totals, a note on omitted costs, and confirmation of Volta capacity for 3,080 bikes."
    }
  ]
}
```