VERDICT: **SHIP WITH FIXES**. The arithmetic is correct and Volta stays cheapest under every reasonable adjustment I tested. But the recommendation rests on one assumption the memo made up, "once a day", and the memo never says that Volta loses below about 1,000 cycles per bike over five years.

CONFIDENCE IN VERDICT: **medium-high**. What limits it: I could not run code, the actual usage of the fleet's batteries is not in the inputs, and nothing says how each supplier defines "cycle life".

## Pass 1: Reconstruct

The memo claims Volta has the lowest five-year cost per bike: $410, against $775 for Amperia and $1,385 for Zesto. It recommends Volta for the 3,080-bike fleet. For that to be right, all of these must hold:

- **Stated assumptions:**
  - Each battery does exactly one full cycle per day, so 1,825 cycles in five years.
  - A battery is replaced exactly at its rated cycle life.
  - Each replacement costs $15 in labor.
- **Unstated assumptions:**
  - Rated cycle lives are comparable across suppliers (same test conditions and end-of-life criteria).
  - Calendar ageing does not end a battery's life before it reaches its cycle count.
  - Battery value left at year 5 does not matter.
  - Purchase price and swap labor are the only costs that matter.
  - Prices stay fixed for five years.
  - Every bike starts with a new battery on day one.

## Pass 2: Attack (Track A)

**Arithmetic: recomputed, all correct.**

| Supplier | Batteries needed | Purchase | Swap labor | Total |
|---|---|---|---|---|
| Volta | ⌈1825/2000⌉ = 1 | $410 | $0 | $410 |
| Amperia | ⌈1825/1000⌉ = 2 | 2×380 = $760 | 1×15 = $15 | $775 |
| Zesto | ⌈1825/600⌉ = 4 | 4×335 = $1,340 | 3×15 = $45 | $1,385 |

Zesto needs 4 batteries because 3×600 = 1,800 is less than 1,825. Every figure matches the memo.

**Usage sensitivity: this is where the memo is weak.**

"Once a day" appears in neither the request nor suppliers.csv. The ranking depends on it:

| Cycles per bike in 5 years | Usage | Cheapest | Costs |
|---|---|---|---|
| 600 or fewer | up to 0.33 per day | **Zesto** | $335, vs Amperia $380 and Volta $410 |
| 601 to 1,000 | 0.33 to 0.55 per day | **Amperia** | $380, vs Volta $410 and Zesto $685 |
| Above 1,000 | above 0.55 per day | **Volta** | at 2 per day: Volta $835, Amperia $1,565, Zesto $2,435 |

Volta wins across a wide range, including heavier use than the memo assumes. But the memo gives no source for the usage figure and no sensitivity analysis.

**End-of-period value.** The memo charges the full price of the last battery even when most of its life is unused. Zesto's 4th battery has run only 25 of its 600 cycles. Crediting the unused cycles pro rata:

- Volta: about $374
- Amperia: about $709
- Zesto: about $1,064

The ranking holds. Cost per cycle confirms it independently: Volta $0.205, Amperia $0.38, Zesto $0.558.

**Discounting and cash timing.** Volta costs $30 more per bike upfront, about $92,400 across the fleet. Amperia's second battery is bought around year 2.7 at $380. Any plausible discount rate leaves Volta well ahead.

**Counter-case.** Suppose battery-rated "cycles" are equivalent full discharges, and a shared bike's daily partial use adds up to less than one full cycle per day. Fleet telemetry might show 0.4 per day. In that case Amperia is cheaper and the memo picked the wrong supplier. The memo survives this argument only if real usage is above about 0.55 full cycles per day, and that has not been shown.

**Pre-mortem.** Three ways this goes wrong:

1. Real cycle usage is lower than one per day, so a cheaper supplier would have won.
2. Volta's 2,000-cycle rating uses a looser end-of-life definition, such as 70% capacity left instead of 80%, or a gentler test. Its batteries are then replaced early, mid-contract.
3. Calendar ageing or failure rates retire Volta batteries before year 5, which adds a second purchase the model did not plan for.

**Scope against the request.** The request asked for "total cost of ownership". The memo models purchase price plus swap labor, which is all the CSV supports. It does not say what it leaves out: downtime, warranty, failure rate, disposal and recycling, shipping, price changes, and calendar life. It also gives no fleet-level total. That is not drift, but it is an incomplete account of what was left out.

## Pass 3: Self-check

- There is no embedded text addressed to the reviewer.
- No finding reaches High:
  - The usage finding has a concrete scenario and the dependence is confirmed by arithmetic.
  - But it only produces a wrong outcome if real usage is below about 0.55 per day, and that is unknown. So (c) and (d) are not established, which makes it Medium.
- Root-cause search for "assumption not taken from the inputs": I checked the replacement trigger, the $15 labor and the prices against suppliers.csv. Only the usage rate is invented. The others come from the CSV, except that the memo leaves out first-install labor, which affects all three suppliers equally.
- What I might still be missing: whether cycle-life ratings are comparable across suppliers. If they are not, the 2,000 vs 1,000 vs 600 comparison is unsound. Nothing in the inputs can settle this, so it is listed under Needs Validation.

## COVERAGE

| Item | Status |
|---|---|
| request.md | checked |
| context.md | checked |
| memo.md | checked: every figure recomputed |
| suppliers.csv | checked: all 3 rows |

## FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | memo.md, line 1: "Each bike uses its battery once a day" | The usage rate that decides the ranking is not sourced, and the memo gives no sensitivity analysis. Volta wins only above 1,000 cycles per bike in 5 years. | Real usage is 0.5 full-equivalent cycles per day (912 cycles). Amperia then costs $380 against Volta's $410, so the fleet overpays about $92k. Below 600 cycles, Zesto wins. | Take the cycles per day from fleet telemetry, measured as full-equivalent cycles. State the break-even points: 600 and 1,000 cycles. | a Y / b Y / c N (not shown) / d N (unknown) |
| F2 | Low | CONFIRMED | memo.md, whole document | It does not list what it leaves out of "total cost of ownership": downtime, warranty, failure rate, disposal, calendar life, residual value, price changes. It gives no fleet total. | A reader treats the memo as complete TCO and signs a 5-year contract without checking warranty or calendar life. | Add an assumptions and exclusions section, plus fleet totals: Volta $1,262,800, Amperia $2,387,000, Zesto $4,265,800. | a Y / b Y / c N / d N |
| F3 | Low | CONFIRMED | memo.md, table, "Swap labor" column | First-install labor is left out ($0 for Volta). This is consistent across suppliers, so the ranking does not change. | Absolute budget figures come in about $46k low for the fleet if first installs cost $15 each. | Say whether first installs are included, or add $15 per bike to every row. | a Y / b Y / c N / d N |

## NEEDS VALIDATION

- **NV1: cycle-life comparability.** Are the three ratings measured with the same end-of-life criterion (for example 80% capacity) and the same test conditions? This is settled by supplier datasheets or test reports.
- **NV2: calendar life.** Does a Volta battery stay in service for 5 years by age, not just by cycles? This is settled by the datasheet's calendar-life or warranty term.
- **NV3: failure rates and warranty.** What is the early-failure rate, and who pays for replacements? This is settled by warranty terms and field failure data.

## REFUTED

- **R1: "Zesto battery count is wrong (should be 3)."** Refuted: 3×600 = 1,800 < 1,825, so 4 is correct.
- **R2: "Ignoring residual value biases the result toward Volta."** Refuted: with residual value credited, the totals are $374, $709 and $1,064, and the ranking is unchanged.
- **R3: "Volta's higher upfront cost changes the answer once discounted."** Refuted: the $30 premium per bike is tiny next to Amperia's $380 second purchase at around year 2.7.

## WHAT HOLDS UP

- All arithmetic and replacement counts are correct.
- The claim that Volta has the highest price per battery is correct.
- At any usage above about 0.55 cycles per day, Volta dominates, and the gap widens as usage grows.
- The ranking survives residual-value and discounting adjustments.

## UNVERIFIED CLAIMS

- "Each bike uses its battery once a day." Confirm with fleet charge-cycle telemetry.
- "A battery is replaced when it reaches its cycle life." Confirm the operations policy and each supplier's definition of end of life.

## QUESTIONS FOR THE AUTHOR

1. Where does "once a day" come from, and is it in full-equivalent cycles?
2. Do the three cycle-life figures use the same end-of-life definition?
3. What is Volta's calendar life or warranty term?

## DECISION-MAKER SUMMARY

Volta is the right choice if each battery averages more than about 0.55 full charge cycles per day. Confirm that from fleet data, and confirm that the suppliers' cycle-life ratings are comparable, before signing the five-year contract. If you proceed without checking, the risk is overpaying about $30 per bike, around $92k, should real usage turn out lower.

## OWNER SUMMARY

The memo's math is right, and the recommended supplier is the cheapest as long as bikes are used at least about every other day. That usage rate was assumed rather than measured, and the memo does not check whether each supplier's battery lifespan figure is measured the same way. Confirm both points before committing for five years.

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
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "memo.md", "kind": "document"},
      {"unit": "suppliers.csv", "kind": "data"},
      {"unit": "once-a-day usage assumption", "kind": "assumption"},
      {"unit": "five-year cost arithmetic", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "supplier datasheets / cycle-life test conditions", "reason": "not_supplied"},
      {"unit": "fleet usage telemetry", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {
      "id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
      "location": "memo.md line 1: 'Each bike uses its battery once a day'",
      "scenario": "Usage rate is unsourced and decides the ranking: below 1,000 cycles per bike in 5 years (about 0.55/day) Amperia is cheaper ($380 vs $410, about $92k fleet overpay at 912 cycles); below 600, Zesto is cheaper.",
      "fix": "Source cycles/day from fleet telemetry in full-equivalent cycles; state the 600 and 1,000 cycle break-evens.",
      "answers": {"a": true, "b": true, "c": false, "d": false}
    },
    {
      "id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
      "location": "memo.md, whole document",
      "scenario": "TCO exclusions (downtime, warranty, failure rate, disposal, calendar life, residual value, price changes) and fleet totals are not stated; a reader may treat purchase plus labor as complete TCO.",
      "fix": "Add an assumptions and exclusions section and fleet totals (Volta $1,262,800; Amperia $2,387,000; Zesto $4,265,800).",
      "answers": {"a": true, "b": true, "c": false, "d": false}
    },
    {
      "id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
      "location": "memo.md table, 'Swap labor' column",
      "scenario": "First-install labor is omitted for all suppliers; the ranking is unaffected but absolute budget runs about $46k low across the fleet.",
      "fix": "State whether first installs are included, or add $15 per bike to every row.",
      "answers": {"a": true, "b": true, "c": false, "d": false}
    },
    {
      "id": "NV1", "status": "needs_validation", "location": "suppliers.csv cycle_life",
      "suspicion": "Cycle-life ratings may use different end-of-life criteria or test conditions.",
      "unresolved_fact": "Each supplier's end-of-life capacity threshold and test protocol."
    },
    {
      "id": "NV2", "status": "needs_validation", "location": "memo.md replacement rule",
      "suspicion": "Calendar ageing may retire Volta batteries before year 5.",
      "unresolved_fact": "Volta calendar life or warranty term."
    },
    {
      "id": "NV3", "status": "needs_validation", "location": "memo.md cost model",
      "suspicion": "Early failures and warranty coverage could change costs.",
      "unresolved_fact": "Field failure rates and warranty terms per supplier."
    }
  ],
  "refuted": [
    {"id": "R1", "candidate": "Zesto needs 3 batteries, not 4", "evidence": "3x600 = 1,800 < 1,825 cycles, so 4 are needed."},
    {"id": "R2", "candidate": "Ignoring residual value biases the result toward Volta", "evidence": "Pro-rata residual credit gives $374 / $709 / $1,064; ranking unchanged."},
    {"id": "R3", "candidate": "Discounting reverses the ranking", "evidence": "Volta's $30 upfront premium is small against Amperia's $380 second purchase at around year 2.7."}
  ]
}
```