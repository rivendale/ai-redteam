VERDICT: **SHIP WITH FIXES.** The arithmetic is correct and Volta wins under the memo's stated assumptions, but the memo does not source the usage rate the result depends on. Volta also has thin headroom on its cycle life, and the memo shows no sensitivity check for either.

CONFIDENCE IN VERDICT: **medium.** Two facts limit it, and neither is in the material: the fleet's real daily cycle rate, and whether Volta's 2,000-cycle rating holds in service.

## Pass 1: Reconstruct

The memo computes five-year cost per bike for three suppliers. It counts battery purchases plus $15 labor for each replacement, uses the prices and cycle lives in `suppliers.csv`, and recommends Volta at $410 per bike. For this to be right, four things must hold:
- **Usage rate (unstated source):** each bike uses one cycle per day, so 1,825 cycles over five years.
- **Cycle life:** the supplier figures hold in real service, and reaching cycle life is the only trigger for replacement. Calendar ageing, failures and capacity fade are not modelled.
- **Cost scope:** purchase plus swap labor captures the cost differences that matter. Energy, warranty, residual value, disposal, downtime and the time value of money are left out.
- **Supply:** one supplier can serve 3,080 bikes for five years at the listed price.

## Pass 2: Attack (Track A)

**Facts and arithmetic.** I re-derived every cell, and all are correct.

| Supplier | Cycles needed | Batteries | Purchase | Swaps | Total |
|---|---|---|---|---|---|
| Volta | 1825/2000 = 0.91 | 1 | $410 | 0 | $410 |
| Amperia | 1825/1000 = 1.83 | 2 | $760 | 1 × $15 | $775 |
| Zesto | 1825/600 = 3.04 | 4 | $1,340 | 3 × $15 | $1,385 |

- Prices, cycle lives and labor match the CSV.
- Labor for the first installation is left out for all three suppliers. That is consistent, so it does not change the ranking.

**Sensitivity of the main assumption (usage).** I tested other usage rates by arithmetic:
- **About 0.5 per day (912 cycles):** Volta costs $410 and Amperia $380. **Amperia wins.**
- **The flip point:** at or below 1,000 cycles in five years (about 0.55 per day), Amperia needs only one battery and is cheaper.
- **2 per day (3,650 cycles):** Volta $835, Amperia $1,565, Zesto $2,435. Volta still wins.

So the recommendation is robust if usage is high but flips if usage is low. The memo states "once a day" with no source.

**Sensitivity of Volta's cycle life.** Volta's headroom is 175 cycles, or 9.6%.
- **Only Volta short:** if Volta reaches 1,800 real cycles, it needs a second battery and costs $835. That loses to Amperia's $775, provided Amperia meets its own rating.
- **All suppliers short by the same 10%:** Amperia needs 3 batteries ($1,170) and Volta still wins.

So the result depends on Volta specifically meeting its rating.

**Logic.** The conclusion follows from the stated premises. The memo's note that Volta is cheapest overall despite the highest per-battery price is correct.

**Alternatives.** The memo does not consider dual sourcing, volume pricing, or reviewing the choice at mid-term.

**Counter-case.** The strongest case against Volta:
- It front-loads cost and puts a five-year fleet on one supplier.
- Its rated life barely exceeds the horizon.
- At low usage, Amperia is cheaper.

Volta survives the first point on cost: discounting does not overturn it. It does not survive the second and third points without data.

**Pre-mortem.** The three most likely reasons this decision fails:
1. Volta batteries fall short of 1,825 real cycles, which forces a near-full second purchase across 3,080 bikes.
2. Actual usage turns out well below one cycle per day.
3. Volta cannot supply the fleet or raises prices, with no second source in place.

**Missing information.** A careful expert would ask for:
- The measured cycles per bike per day.
- How cycle life is defined (for example, cycles to 80% capacity).
- Calendar-life limits.
- Warranty terms.
- Volume pricing and supply capacity.
- A fleet-level total. At 3,080 bikes: Volta $1,262,800, Amperia $2,387,000, Zesto $4,265,800.

## Pass 3: Self-check

- **Injected text:** none found in the work.
- **High and Critical findings:** none.
- **Most serious thing I might be missing:** what "a cycle" means in this bike-share operation. If a battery is swapped or charged at a depot several times a day, or partially, the 1,825 figure could be wrong in either direction. That hides in the first sentence of the memo.

## COVERAGE

| Item | Status |
|---|---|
| request.md | checked |
| context.md | checked |
| memo.md | checked (every number recomputed) |
| suppliers.csv | checked |

## FINDINGS

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| 1 | Medium | CONFIRMED | memo.md, line 3: "Each bike uses its battery once a day" | The usage assumption carries the recommendation, but the memo gives no source and no sensitivity check. | If real usage is 1,000 cycles or fewer over five years (about 0.55 per day or less), Amperia costs $380 per bike against Volta's $410. Across the fleet, choosing Volta would then overspend about $92k. | Source usage from fleet telemetry. Add a usage sensitivity row showing the flip point. Reproduce: at 912 cycles, Volta = 1 × 410 and Amperia = 1 × 380. | a Y / b Y / c N / d N |
| 2 | Medium | CONFIRMED (arithmetic); real-world shortfall unverified | memo.md table, Volta row; suppliers.csv `Volta,410,2000` | Volta's rated life exceeds the five-year need by only 175 cycles (9.6%). The memo treats the vendor rating as exact. | If Volta delivers about 1,800 real cycles while Amperia meets its rating, Volta costs $835 per bike against Amperia's $775. The fleet overspends about $185k and buys about 3,080 extra batteries. | State how cycle life is defined and what the warranty says. Add a derating case. Reproduce: set Volta cycle_life = 1,800, which gives 2 × 410 + 15 = 835. | a Y / b Y / c N / d N |
| 3 | Low | CONFIRMED | memo.md, whole memo | It reports per-bike cost only. It has no fleet total and does not state the cost items it leaves out (energy, residual value, disposal, downtime, discounting). | A decision-maker reads the $410 vs $775 per-bike gap without seeing that it means about $1.12M across the fleet, or knowing what is excluded. | Add fleet totals and an explicit list of exclusions. | a Y / b Y / c N / d Y |

## NEEDS VALIDATION

- **Calendar ageing.** Can a Volta battery last five years of calendar time regardless of cycles? This is settled by the supplier's calendar-life spec or warranty.
- **Supply and pricing.** Can Volta supply about 3,080 batteries plus spares, at $410, for five years? This is settled by a supplier quote and capacity commitment.
- **Definition of a cycle.** What does a "cycle" mean in this operation (full charge or partial; depot swap)? This is settled by the ops charging logs.

## REFUTED

- **"The arithmetic is wrong."** All cells recompute exactly (see the table above).
- **"Ignoring residual value biases the result."** Pro-rated by cycles used, the costs are Volta $374, Amperia $694 and Zesto $1,019. The ranking is unchanged.
- **"Discounting favours the cheaper upfront options."** At 10%, Amperia is about $380 + $395/1.3 ≈ $684, which is still more than Volta's $410.
- **"First-install labor was omitted."** It is omitted for all three suppliers equally, so the ranking is unchanged.

## WHAT HOLDS UP

- The data is transcribed correctly from the CSV.
- Ceiling-based battery counts and swap counts are correct.
- Volta's lead is robust to usage above 0.55 cycles per day, to discounting, to residual value, and to uniform derating of all suppliers.
- The memo answers the question that was asked, with no drift.

## UNVERIFIED CLAIMS

| Claim | How to confirm |
|---|---|
| "Once a day" usage | Fleet telemetry |
| Replacement happens exactly at rated cycle life | Supplier cycle-life definition and the operational replacement policy |
| The listed prices hold for five years at fleet volume | Supplier contract |

## QUESTIONS FOR THE AUTHOR

1. What is the measured average number of cycles per bike per day, and where does that figure come from?
2. How do the suppliers define cycle life, and what do Volta's warranty and calendar-life terms say?

## DECISION-MAKER SUMMARY

The cost math is correct, and Volta is cheapest if bikes really cycle about once a day and Volta batteries reach their rated 2,000 cycles. Before signing, confirm actual usage from fleet data and get Volta's cycle-life definition and warranty in writing. If you proceed without that, the risk is low usage (Amperia becomes cheaper) or Volta falling slightly short of its rating (a second battery for every bike, about $185k more than Amperia).

## OWNER SUMMARY

The memo's numbers add up, and its pick is the cheapest option if the bikes are used about once a day and the batteries last as long as the supplier claims. Both of those points are assumptions rather than measured facts, and either one being off could make a different supplier cheaper. Checking real usage and getting the battery lifetime guaranteed in writing would settle it before the five-year commitment.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
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
      {"unit": "usage assumption: once a day", "kind": "assumption"},
      {"unit": "cycle life equals replacement point", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "fleet usage telemetry", "reason": "not_supplied"},
      {"unit": "supplier warranty and calendar-life terms", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {
      "id": "F1",
      "status": "confirmed",
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "track": "A",
      "location": "memo.md line 3: 'Each bike uses its battery once a day'",
      "scenario": "The usage rate is unsourced. At 1,000 or fewer cycles over 5 years (about 0.55/day or less), Amperia costs $380 per bike against Volta's $410, so the recommendation flips.",
      "fix": "Source usage from fleet telemetry and add a usage sensitivity row showing the flip point.",
      "answers": {"a": true, "b": true, "c": false, "d": false}
    },
    {
      "id": "F2",
      "status": "confirmed",
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "track": "A",
      "location": "memo.md table, Volta row; suppliers.csv Volta cycle_life 2000",
      "scenario": "Volta has only 9.6% headroom over the 1,825-cycle need. At about 1,800 real cycles, Volta costs $835 per bike against Amperia's $775, about $185k more across 3,080 bikes.",
      "fix": "State the cycle-life definition and warranty terms, and add a derating case.",
      "answers": {"a": true, "b": true, "c": false, "d": false}
    },
    {
      "id": "F3",
      "status": "confirmed",
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "track": "A",
      "location": "memo.md, whole memo",
      "scenario": "The memo reports per-bike cost only, with no fleet total (Volta $1.26M, Amperia $2.39M, Zesto $4.27M) and no list of excluded cost items.",
      "fix": "Add fleet totals and an explicit list of exclusions.",
      "answers": {"a": true, "b": true, "c": false, "d": true}
    },
    {
      "id": "NV1",
      "status": "needs_validation",
      "location": "memo.md replacement rule",
      "suspicion": "Calendar ageing may require replacing Volta batteries before five years.",
      "unresolved_fact": "Volta calendar-life spec and warranty terms"
    },
    {
      "id": "NV2",
      "status": "needs_validation",
      "location": "memo.md recommendation",
      "suspicion": "Single-supplier capacity and price stability for a fleet of 3,080 bikes over five years.",
      "unresolved_fact": "Supplier quote and capacity commitment"
    },
    {
      "id": "NV3",
      "status": "needs_validation",
      "location": "memo.md line 3",
      "suspicion": "The definition of 'cycle' in this operation may not match the supplier's cycle-life definition.",
      "unresolved_fact": "Ops charging logs and the supplier's cycle definition"
    }
  ],
  "refuted": [
    {"id": "R1", "candidate": "Arithmetic errors", "evidence": "All cells recomputed: 410; 2x380+15=775; 4x335+45=1385"},
    {"id": "R2", "candidate": "Residual value changes the ranking", "evidence": "Pro-rated: Volta 374, Amperia 694, Zesto 1019; ranking unchanged"},
    {"id": "R3", "candidate": "Discounting changes the ranking", "evidence": "At 10%, Amperia is about 684, still more than Volta's 410"},
    {"id": "R4", "candidate": "First-install labor omitted", "evidence": "Omitted equally for all suppliers; ranking unchanged"}
  ]
}
```