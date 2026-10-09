VERDICT: **REJECT.** The memo ranks suppliers by purchase price and calls that total cost of ownership. When the CSV's cycle life and swap labor are applied over five years, the ranking reverses: Zesto is the most expensive option and Volta the cheapest.

CONFIDENCE IN VERDICT: **high.** The reversal is plain arithmetic on the supplied CSV. Volta stays cheapest under every costing method I tried at the memo's own usage rate. The limit is that the usage rate (one cycle per day) is unsourced, and the winner depends on it.

## Pass 1: Reconstruct

The memo claims Zesto has the lowest five-year TCO "at $335 per battery" and recommends Zesto for a 3,080-bike fleet. For that to be correct, three things would have to hold:
- purchase price alone would have to be the TCO, or
- every supplier would need the same number of batteries over five years, and
- swap labor would have to be equal or irrelevant.

Load-bearing assumptions:
- **Stated:** each bike uses its battery once a day.
- **Unstated:**
  - The 5-year horizon equals 1,825 cycles.
  - A battery is replaced exactly at its rated cycle life.
  - Swap labor applies to every battery installed.
  - There is no salvage value, discounting, warranty or degradation effect.
  - All three suppliers can supply 3,080 units.

## Pass 2: Attack (Track A)

**Recomputed TCO from suppliers.csv**, assuming 1 cycle/day × 365 × 5 = 1,825 cycles per bike:

| Supplier | Cycle life | Batteries per bike (ceil 1825/life) | Per bike (price + $15 swap each) | Fleet of 3,080 |
|---|---|---|---|---|
| Volta | 2,000 | 1 | 410 + 15 = **$425** | **$1,309,000** |
| Amperia | 1,000 | 2 | 760 + 30 = $790 | $2,433,200 |
| Zesto | 600 | 4 (1825/600 = 3.04) | 1,340 + 60 = $1,400 | $4,312,000 |

The ranking holds under other costing methods:
- **Excluding labor on the initial install:**
  - Volta $410
  - Amperia $775
  - Zesto $1,385
- **Pro-rated per cycle, (price + labor) / life × 1,825:**
  - Volta ≈ $388
  - Amperia ≈ $721
  - Zesto ≈ $1,065

Under the memo's own usage assumption, picking Zesto over Volta costs roughly **$3.0M more** across the fleet.

**Sensitivity to usage.** Using the CSV only, with full-battery purchases:

| 5-year cycles | Daily use | Cheapest supplier |
|---|---|---|
| ≤ 600 | ≤ ~0.33/day | Zesto ($350) |
| 601 to 1,000 | ~0.33 to 0.55/day | Amperia ($395 vs Zesto $700, Volta $425) |
| > 1,000 | > ~0.55/day | Volta |

So the usage rate decides the answer, and the memo neither sources it nor uses it.

**Pass 1 checks:**
- **Counter-case:** the strongest argument for Zesto is low utilization or high uncertainty in cycle-life claims. Smaller, cheaper batteries also limit exposure if a supplier underperforms. The memo makes neither argument, and at one cycle per day neither one rescues Zesto.
- **Pre-mortem:** if Zesto is chosen, the most likely ways it goes wrong are:
  1. The budget overruns by about 3× as replacements arrive every ~20 months.
  2. Swap labor and downtime pile up (about 9,240 extra swaps over the fleet's life).
  3. Volta's 2,000-cycle claim was never checked, so a corrected decision might still fail.
- **Bias:** the memo anchors on the most visible number (sticker price) and labels it with the requested term ("total cost of ownership"). That makes it read as finished.

## Pass 3: Self-check

- **F1 as its strongest defender would see it:** perhaps "TCO" was meant loosely? No. The request explicitly asks for TCO "over five years" and points to the cycle lives. The memo even states the usage rate needed for the calculation and then never uses it. The finding survives.
- **Same-root-cause search:** I searched the memo for any other use of `cycle_life` or `swap_labor_usd`. There is none: the table and the sentence use only `price_usd`. That means the five-year horizon, the fleet size, and labor are all missing, which F2 and F3 record.
- **Security:** none; this is not a security finding.
- **Embedded instructions:** none found in the work.
- **What I might still be missing:** whether the CSV's cycle lives are vendor-rated figures or measured ones, and at what depth of discharge. A Volta "2,000" measured at shallower discharge than Zesto's "600" would narrow the gap. That information would live outside the supplied material.

## Coverage

| Item | Status |
|---|---|
| request.md | checked |
| context.md | checked |
| memo.md | checked, every line |
| suppliers.csv | checked, every row; prices in the memo match the CSV |

## Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | memo.md: "Zesto has the lowest total cost of ownership at $335 per battery. We recommend Zesto." | Purchase price is presented as TCO. Cycle life and swap labor from the CSV are ignored, and the recommendation is reversed. | At the memo's own 1 cycle/day, Zesto needs 4 batteries per bike ($1,400) against Volta's 1 ($425). Choosing Zesto costs ~$4.31M vs ~$1.31M for the fleet, about $3.0M of avoidable spend. | Recompute TCO per bike as ceil(cycles over 5 years / cycle_life) × (price + swap_labor), then multiply by 3,080. Reproduction: 1825/600 → 4 × 350 = 1,400; 1825/2000 → 1 × 425 = 425. | a Y, b Y, c Y, d Y |
| F2 | Medium | CONFIRMED | memo.md: "Each bike uses its battery once a day." | The usage rate is unsourced (it is not in the CSV or the request) and is not used in any calculation. Yet the winner flips across usage bands (Zesto ≤600 cycles, Amperia 601–1,000, Volta >1,000). | If real usage is about 0.4/day, Amperia, not Volta, is the cheapest; a corrected memo built on an unchecked 1/day would also be wrong. | Source the usage from fleet telemetry. Show the breakeven bands as a sensitivity table. | a Y, b Y, c N, d Y |
| F3 | Medium | CONFIRMED | memo.md table | There is no five-year horizon, no fleet total, and no method shown. A reader cannot audit the figure, and the scale of the stakes (millions of dollars) is hidden. | A decision-maker approves on what looks like a $75-per-battery gap, when the real gap is ~$975 per bike, or ~$3.0M. | Show batteries per bike, labor, per-bike TCO and fleet TCO for each supplier, plus the formula used. | a Y, b Y, c N, d Y |
| F4 | Low | CONFIRMED | memo.md, whole | Cost drivers are omitted without any mention: warranty, capacity fade before end of life, disposal or recycling, discounting, salvage of Volta's ~175 unused cycles, and supplier capacity for 3,080 units. | A cost not in the CSV, such as Volta's warranty terms, could narrow the gap. None plausibly closes $3.0M. | List the excluded factors and say whether each could change the ranking. | a Y, b Y, c N, d N |

## Needs validation (no severity)

- **NV1, real fleet usage rate.** This is settled by average cycles per bike per day from telemetry. It decides between Volta and Amperia, and between Amperia and Zesto at low utilization.
- **NV2, basis of the cycle_life figures.** This is settled by test conditions for each supplier (depth of discharge, end-of-life capacity threshold) and whether the figures are measured or vendor-claimed.
- **NV3, whether swap labor applies to the initial fit.** This is settled by ops practice. It shifts each total by $15 but does not change the ranking.
- **NV4, Volta supply capacity and lead time for 3,080 units.** This is settled by a supplier quote.

## Refuted

- **R1, "the memo's prices are wrong."** The memo's $410, $380 and $335 match the CSV exactly.
- **R2, "Zesto could still win once Volta's leftover cycles are counted."** Even pro-rated per cycle, Volta (~$388) beats Zesto (~$1,065) at 1/day.

## What holds up

- Purchase prices are transcribed correctly.
- Zesto does have the lowest sticker price.
- Stating a usage assumption at all was the right instinct; it just was not sourced or applied.

## Unverified claims

- **"Each bike uses its battery once a day":** confirm with fleet telemetry.
- **"lowest total cost of ownership":** refuted by recomputation from the CSV (F1).

## Questions for the author

1. Where does once a day come from, and what is the measured fleet average?
2. Was cycle life deliberately excluded? If so, why?
3. Does swap labor apply to the first install?

## Decision-maker summary

Do not adopt Zesto. On the supplied data and the memo's own usage rate, it is the most expensive option (~$4.3M vs ~$1.3M for Volta over five years). Have the analysis redone with measured usage and a sensitivity table before choosing. If you proceed anyway, expect about $3M of avoidable battery and labor spend.

## Owner summary

The memo picked the battery with the lowest sticker price, but that battery wears out much faster, so it would have to be bought about four times over five years instead of once. Counting replacements and fitting labor, the cheapest-looking choice becomes roughly three times more expensive for the whole fleet. The comparison should be redone using how often the bikes are really ridden before any supplier is chosen.

```json
{
  "schema_version": "2.3",
  "verdict": "REJECT",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "suppliers.csv", "status": "seen", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "memo.md", "kind": "document"},
      {"unit": "suppliers.csv", "kind": "data"},
      {"unit": "once-a-day usage assumption", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "fleet usage telemetry", "reason": "not_supplied"},
      {"unit": "supplier cycle-life test conditions", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {
      "id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "A",
      "location": "memo.md: 'Zesto has the lowest total cost of ownership at $335 per battery. We recommend Zesto.'",
      "scenario": "At the memo's own 1 cycle/day (1,825 cycles over 5 years), Zesto needs 4 batteries per bike ($1,400 with $15 swaps) vs Volta 1 ($425); fleet of 3,080: ~$4.31M vs ~$1.31M, about $3.0M avoidable spend.",
      "fix": "Compute TCO = ceil(5-year cycles / cycle_life) x (price + swap_labor) per bike, times 3,080; recommend the lowest.",
      "answers": {"a": true, "b": true, "c": true, "d": true},
      "security": false,
      "siblings_searched": {"searched": "every memo statement for any use of cycle_life, swap_labor_usd, the 5-year horizon or fleet size", "found": "none used; recorded as F2 and F3"}
    },
    {
      "id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
      "location": "memo.md: 'Each bike uses its battery once a day.'",
      "scenario": "Usage is unsourced and unused; the winner flips by band (Zesto <=600 cycles, Amperia 601-1,000, Volta >1,000), so a wrong usage figure yields a wrong supplier.",
      "fix": "Source usage from telemetry and show breakeven sensitivity.",
      "answers": {"a": true, "b": true, "c": false, "d": true}
    },
    {
      "id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
      "location": "memo.md table",
      "scenario": "No horizon, fleet total or method; the reader sees a $75-per-battery gap instead of ~$975 per bike (~$3.0M fleet).",
      "fix": "Show batteries per bike, labor, per-bike and fleet TCO, and the formula.",
      "answers": {"a": true, "b": true, "c": false, "d": true}
    },
    {
      "id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
      "location": "memo.md, whole",
      "scenario": "Warranty, capacity fade, disposal, discounting, salvage and supply capacity are omitted without mention; none plausibly closes a $3.0M gap, but they are unaddressed.",
      "fix": "List excluded cost drivers and state whether each could change the ranking.",
      "answers": {"a": true, "b": true, "c": false, "d": false}
    },
    {"id": "NV1", "status": "needs_validation", "location": "memo.md usage sentence", "suspicion": "Actual usage may differ from 1/day and change the winner", "unresolved_fact": "Measured average cycles per bike per day"},
    {"id": "NV2", "status": "needs_validation", "location": "suppliers.csv cycle_life", "suspicion": "Cycle lives may be measured under different conditions", "unresolved_fact": "Test depth of discharge and end-of-life threshold per supplier"},
    {"id": "NV3", "status": "needs_validation", "location": "suppliers.csv swap_labor_usd", "suspicion": "Labor may not apply to the initial fit", "unresolved_fact": "Ops practice for the first install"},
    {"id": "NV4", "status": "needs_validation", "location": "memo.md recommendation", "suspicion": "The cheapest supplier may not be able to supply 3,080 units", "unresolved_fact": "Supplier capacity and lead time quote"}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Memo prices are mistranscribed", "evidence": "$410/$380/$335 match suppliers.csv exactly"},
    {"id": "R2", "candidate": "Counting Volta's leftover cycles could make Zesto cheaper", "evidence": "Pro-rated per cycle at 1/day: Volta ~$388 vs Zesto ~$1,065"}
  ]
}
```