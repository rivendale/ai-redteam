**Review mode: no tools and no fresh subagent.** The work was supplied, not written in this session, so there is no authorship anchoring. Everything below comes from reading the three supplied texts and doing the arithmetic by hand. I did not run any code.

VERDICT: **REWORK.** The memo calls unit purchase price "total cost of ownership" and ignores cycle life and swap labour. Using the supplied CSV, Zesto is the most expensive option over five years and Volta is the cheapest.

CONFIDENCE: **high** on the main finding, because it is plain arithmetic on the supplied data. **Medium** overall. Three things limit it: no tools (the arithmetic is by hand), no independent seat, and no context on actual fleet usage, warranty terms or calendar ageing.

INPUTS LEDGER:
- **Seen:** request.md, context.md, memo.md, suppliers.csv.
- **Not seen:** any source for "each bike uses its battery once a day." This matters, but only at very low usage (see S1).
- **Not seen:** warranty, calendar-life, residual-value or disposal data. This could matter at the margin, but the CSV contains no such fields.
- **Not seen:** whether swap labour applies to the first install. This does not matter, because the ranking is the same either way.

COVERAGE: Whole work. Checked:
- request.md
- context.md
- memo.md: the table, the TCO claim, the recommendation, and the usage assumption
- suppliers.csv: all 3 rows and all 4 columns

Not checked: none of the supplied units. Any facts outside the CSV were not supplied.

SEATS AND GATE: One same-context reviewer (this session) ran. No subagent or cross-vendor seats were available. The sensitivity gate passed: the material is supplier pricing with no personal data.

### Recomputation

The horizon is 5 years × 365 days = **1,825 cycles per bike**, using the memo's own once-a-day figure. A leap day gives 1,826, which changes nothing.

| Supplier | Cycle life | Batteries per bike (ceil 1825/life) | Battery cost | Swap labour ($15 each) | 5-yr TCO per bike | Fleet × 3,080 |
|---|---|---|---|---|---|---|
| Volta | 2,000 | 1 | $410 | $15 | **$425** | **$1,309,000** |
| Amperia | 1,000 | 2 | $760 | $30 | $790 | $2,433,200 |
| Zesto | 600 | 4 (1,825/600 = 3.04) | $1,340 | $60 | $1,400 | $4,312,000 |

The ranking holds under every alternative method I tried:
- **Labour on replacements only:** Volta $410, Amperia $775, Zesto $1,385 per bike.
- **Prorated cost per cycle** (crediting Zesto for the 4th battery's unused life): Volta $0.2125, Amperia $0.395, Zesto $0.583.

On the fleet figures, choosing Zesto over Volta costs about **$3.0M more** over five years ($4,312,000 − $1,309,000 = $3,003,000).

### Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | A | memo.md, "Zesto has the lowest total cost of ownership at $335 per battery. We recommend Zesto." | The memo presents unit purchase price as five-year TCO. The `cycle_life` column is never used. This is drift from the request, which asked for five-year TCO and a recommendation based on it. | The fleet is 3,080 bikes at the memo's own 1 cycle per day. Zesto batteries wear out about every 600 days, so each bike needs 4 over the term. Choosing Zesto costs $4.31M against $1.31M for Volta, about $3.0M more for a five-year commitment. | Recompute TCO per bike over 1,825 cycles as ceil(cycles ÷ cycle_life) × (price + swap labour), scale by 3,080, and recommend the minimum. **Repro:** 1825/600 → 4 × $350 = $1,400 (Zesto) vs 1825/2000 → 1 × $425 = $425 (Volta). | a✔ b✔ c✔ d✔ |
| F2 | High | CONFIRMED | A | memo.md table; suppliers.csv `swap_labor_usd` | Swap labour is in the input but missing from the "TCO". It is a TCO cost component. This is a sibling of F1's root cause: CSV columns ignored. | If the memo is used for budgeting, Zesto's labour alone is understated by 4 × $15 × 3,080 = $184,800. Volta's is understated by $46,200. On its own, this omission does not flip the ranking. | Include labour for each battery fitted and state whether the first install counts. **Repro:** the memo's $335 vs $335 + 4×$15 labour component = $395 in labour-inclusive battery spend before replacement counts. | a✔ b✔ c✘ d✔ |
| F3 | Medium | CONFIRMED | A | memo.md, whole document | The memo shows no method, horizon, cycle count or fleet total. A reader cannot tell that the "TCO" is a single purchase price. This lack of transparency is why F1 is easy to miss in sign-off. | An approver skims the table, sees the "lowest TCO", and signs off on a five-year contract. | Add the per-bike and fleet five-year table above, state the assumptions (cycles per day, labour on first install, no residual value), and add a sensitivity line. **Repro:** search the memo for "1825", "five years ×", or a fleet total; none appear. | a✔ b✔ c✘ d✘ |

**Siblings search (F1/F2):** I checked each CSV column against the memo.
- `supplier`: used.
- `price_usd`: used.
- `cycle_life`: unused (F1).
- `swap_labor_usd`: unused (F2).

I also checked the memo's stated usage assumption ("once a day"). It is stated but never applied in any calculation, which is part of F1. There are no other inputs. None of these are security findings.

### NEEDS VALIDATION
- **S1: Usage rate.** The claim "Each bike uses its battery once a day" is unsourced. Volta beats Zesto unless five-year usage is ≤ 600 cycles (about 0.33 per day), and only below that does Zesto win. Above about 1.1 per day, Volta and Amperia each need one more battery, and Volta still wins. Settle this with the fleet's measured cycles per bike per day.
- **S2: Calendar ageing.** Volta's battery must last the full 5 years and reach 91% of its rated cycles. If it loses capacity with age before reaching 2,000 cycles, it may need replacing early. Settle this with Volta's warranty and calendar-life specification. Even one extra Volta battery ($850 per bike) still beats Zesto ($1,400).
- **S3: Off-CSV costs** such as disposal, residual value, downtime per swap and volume discounts are not modelled. Settle this with the supplier quotes. Downtime cost would widen Volta's lead, because Zesto needs the most swaps.

### REFUTED
- **"Ceiling rounding unfairly penalises Zesto's 4th battery (25 cycles used)."** Refuted. Prorated per-cycle cost still ranks Volta ($0.21) < Amperia ($0.40) < Zesto ($0.58).
- **"The ranking depends on whether first-install labour counts."** Refuted. With labour on replacements only, the costs are $410 / $775 / $1,385, the same order.

**WHAT HOLDS UP:** The memo's three unit prices match the CSV exactly. A clear recommendation is the right format for the request. The once-a-day assumption, while unsourced, gives a robust answer across a wide range of usage.

**UNVERIFIED CLAIMS:** "Each bike uses its battery once a day." Confirm from fleet telemetry or trip logs.

**QUESTIONS FOR THE AUTHOR:**
1. What is the measured cycles per bike per day?
2. Do any suppliers' warranties or calendar-life limits cut a battery's service life short of five years?

**DECISION-MAKER SUMMARY:** Do not approve Zesto. The memo's "TCO" is just the sticker price, and on the supplied data Zesto costs about $3.0M more over five years than Volta ($4.31M vs $1.31M for 3,080 bikes). Have the memo redone with cycle life and swap labour, then confirm actual usage and Volta's calendar-life warranty before signing.

**OWNER SUMMARY:** The memo recommends the cheapest battery to buy, not the cheapest to own. The cheap battery wears out more than three times faster, so over five years it would cost the fleet roughly three million dollars more than the longest-lasting option. The analysis should be redone before any contract is signed.

I could not run `tools/validate_findings.py`, so the block below is written to schema 2.3 by hand and has not been validated.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "suppliers.csv", "status": "seen", "matters": true},
    {"item": "source for 'once a day' usage", "status": "not_seen", "matters": true},
    {"item": "warranty / calendar-life data", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Supplier pricing only; no personal or confidential client data."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "memo.md", "kind": "document"},
      {"unit": "suppliers.csv", "kind": "data"},
      {"unit": "memo.md: TCO claim and recommendation", "kind": "claim"},
      {"unit": "memo.md: once-a-day usage", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "fleet usage telemetry", "reason": "not_supplied"},
      {"unit": "supplier warranty and calendar-life terms", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md: 'Zesto has the lowest total cost of ownership at $335 per battery. We recommend Zesto.'",
     "scenario": "At the memo's own 1 cycle/day over 5 years (1,825 cycles), Zesto (600-cycle life) needs 4 batteries per bike: $1,400 per bike, $4,312,000 for 3,080 bikes, versus Volta at 1 battery, $425 per bike, $1,309,000. Choosing Zesto costs about $3.0M more; the memo ranks on unit price and ignores cycle_life, drifting from the five-year TCO request.",
     "fix": "Compute ceil(1825/cycle_life) x (price + swap labour) per bike, scale by 3,080, recommend the minimum (Volta on supplied data).",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every suppliers.csv column and every memo assumption against the memo's calculation",
                           "found": "swap_labor_usd also unused (F2); 'once a day' stated but never applied"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md table; suppliers.csv swap_labor_usd",
     "scenario": "Swap labour ($15 per battery fitted) is omitted from 'TCO'; a budget built from the memo understates Zesto labour by 4 x $15 x 3,080 = $184,800 and Volta by $46,200.",
     "fix": "Include swap labour per battery fitted and state whether first install is counted.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all CSV cost columns against the memo",
                           "found": "cycle_life also unused (F1); no other cost columns"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md, whole document",
     "scenario": "No method, horizon, cycle count or fleet total is shown, so an approver skimming the table cannot see that 'TCO' is a single purchase price and signs a five-year contract on it.",
     "fix": "Show the per-bike and fleet five-year table, state assumptions, add a usage sensitivity line.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "A", "location": "memo.md: 'Each bike uses its battery once a day.'",
     "suspicion": "Unsourced usage rate; Zesto only wins if five-year usage is at most 600 cycles (about 0.33/day).",
     "unresolved_fact": "Measured cycles per bike per day from fleet data."},
    {"id": "S2", "status": "needs_validation", "track": "A", "location": "suppliers.csv Volta row",
     "suspicion": "Volta must last 5 calendar years at 91% of rated cycles; calendar ageing may force an early replacement.",
     "unresolved_fact": "Volta warranty and calendar-life specification (even one extra Volta battery, $850/bike, still beats Zesto)."},
    {"id": "S3", "status": "needs_validation", "track": "A", "location": "suppliers.csv (absent fields)",
     "suspicion": "Disposal, residual value, swap downtime and volume discounts are not modelled.",
     "unresolved_fact": "Supplier quotes and per-swap downtime cost."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Ceiling rounding unfairly penalises Zesto's 4th battery.",
     "evidence": "Prorated per-cycle cost still ranks Volta $0.2125 < Amperia $0.395 < Zesto $0.583."},
    {"id": "R2", "candidate": "Ranking depends on whether first-install labour counts.",
     "evidence": "Replacement-only labour gives $410 / $775 / $1,385; same order."}
  ]
}
```