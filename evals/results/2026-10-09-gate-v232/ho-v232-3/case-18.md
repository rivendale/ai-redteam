# Redteam review: battery supplier memo

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent and no tools were available. I recomputed every figure by hand from the supplied `suppliers.csv`.

**VERDICT: REWORK.** The memo treats purchase price as total cost of ownership. Applied to the supplied data, its own usage assumption reverses the recommendation: Volta is cheapest over five years and Zesto is the most expensive.

**CONFIDENCE: medium.** The arithmetic is simple and was rechecked. Confidence is limited by same-context review, no tools, and a usage rate that comes from the memo, not from the request or the data.

**INPUTS LEDGER:**
- **Seen:** request.md, context.md, memo.md, suppliers.csv.
- **Not seen:**
  - Real fleet usage data (cycles per bike per day). This matters because the ranking depends on it.
  - Warranty, calendar-ageing, failure-rate, volume-pricing and disposal terms. These may matter at the margin, but cannot close a gap of about $3M.

**COVERAGE:**
- **Scope:** the whole memo, checked against the request and the CSV.
- **Checked:** every memo sentence, the price table, every CSV row, the "once a day" assumption, and the fleet-scale cost.
- **Not checked:** usage data and contract terms, because they were not supplied.

**SEATS AND GATE:**
- **Sensitivity:** no personal or confidential data.
- **Seats:** only the local same-context reviewer ran. No subagent tool was available, and no cross-vendor seats were requested.

### Recomputation

Assumptions:
- Five years of daily use is 5 × 365 = 1,825 cycles per bike.
- Batteries needed per bike = ceil(1,825 ÷ cycle_life).
- Swap labor is $15 per battery fitted, including the first one.

| Supplier | Batteries per bike | Per bike: batteries + labor | Fleet of 3,080 bikes |
|---|---|---|---|
| Volta | ceil(1825/2000) = 1 | $410 + $15 = **$425** | **$1,309,000** |
| Amperia | ceil(1825/1000) = 2 | $760 + $30 = $790 | $2,433,200 |
| Zesto | ceil(1825/600) = 4 | $1,340 + $60 = $1,400 | $4,312,000 |

- Choosing Zesto over Volta costs about **$975 per bike, or $3,003,000 across the fleet**.
- The gap is the same if the first fit's labor is excluded ($410 against $1,385).
- The result is robust. Even if Zesto needed only 3 batteries, or were charged per fraction of a battery used (about 3.04 batteries), Zesto would cost about $1,050 per bike against Volta's $425.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | A | memo.md, "Zesto has the lowest total cost of ownership at $335 per battery. We recommend Zesto." | Upfront unit price is presented as five-year TCO. The memo ignores `cycle_life` and `swap_labor_usd`, which are both in the supplied CSV. | At the memo's own rate of one cycle per day, Zesto needs 4 batteries per bike over 5 years and Volta needs 1. Adopting Zesto costs $4.31M against $1.31M, about $3.0M more over the 5-year lock-in. | Compute five-year TCO per bike and per fleet: batteries needed × price + swaps × labor. On the supplied data, recommend Volta. | y/y/y/y |
| F2 | High | CONFIRMED | A | memo.md, price table (one column: "Price per battery") | Drift from the request. "Total cost of ownership over five years" was asked for, but the table compares only purchase price. It shows no cycle life, replacement count, labor, or five-year horizon, and no fleet total. | A reader approving from the table sees Zesto as 18% cheaper and cannot see that it is about 3.3× the cost over the period they are committing to. | Add columns for cycle life, batteries over 5 years, labor, five-year cost per bike, and fleet total for 3,080 bikes. | y/y/y/y |
| F3 | Medium | CONFIRMED | A | memo.md, "Each bike uses its battery once a day." | The usage rate is load-bearing but has no source, and the memo never applies it. The winner depends on it. At ≤600 cycles in 5 years (about 0.33 per day or less), Zesto wins. At 601–1,000 cycles, Amperia wins. Above 1,000, Volta wins. | If real usage is higher than one cycle per day, Volta's lead grows. If it is much lower, the answer changes. The memo gives no data either way. | Source the usage rate from fleet telemetry and include a short sensitivity table by cycles per day. | y/y/n/n |

**Confirm-or-refute (F1, F2):**
- **Strongest defence:** "TCO" might have meant unit price.
- **Rebuttal:** the request says "over five years" and points to cycle lives in the CSV. Both findings hold.

**Siblings:**
- I searched every memo sentence for other places that use price alone.
- F1 (the conclusion) and F2 (the table) share one root cause and are recorded separately.
- No other locations exist.
- Neither is a security finding.

### NEEDS VALIDATION

- **Calendar ageing:** does Volta reach 2,000 cycles within 5 years without capacity fade or calendar-life failure? Settled by the warranty and capacity-retention spec.
- **Contract terms:** volume discounts, warranty replacements or disposal fees that could change per-battery cost. Settled by the supplier quotes.
- **Discounting:** whether future replacement spend should be discounted. A discount rate cannot plausibly close a $975-per-bike gap.

### REFUTED

- **Candidate:** "Zesto's 4th battery covers only 25 days, so counting 4 overstates its cost."
- **Evidence against:** counting 3 batteries, or a fractional 3.04, still gives about $1,050 per bike against $425. The ranking is unchanged.

### WHAT HOLDS UP

- All three prices in the memo match `suppliers.csv` exactly.
- Zesto does have the lowest purchase price.

### UNVERIFIED CLAIMS

- "Each bike uses its battery once a day." Confirm it from fleet charge or swap logs.

### QUESTIONS FOR THE AUTHOR

1. Where does "once a day" come from?
2. Does any supplier cover replacements under warranty within five years?

### DECISION-MAKER SUMMARY

Do not approve Zesto. The memo compares sticker prices, and the CSV's cycle lives show Zesto costing about $3.0M more than Volta over five years for 3,080 bikes. Have the memo redone as a true five-year TCO with a sourced usage rate. On current data that favours Volta.

### OWNER SUMMARY

The memo picks the cheapest battery to buy, but that battery wears out more than three times faster. Over five years it would cost about three million dollars more than the longest-lasting option. The analysis should be redone on full five-year cost before a supplier is chosen.

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
    {"item": "fleet usage data (cycles per bike per day)", "status": "not_seen", "matters": true},
    {"item": "supplier warranty and calendar-life terms", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
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
      {"unit": "fleet usage data", "reason": "not_supplied"},
      {"unit": "supplier warranty and calendar-life terms", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md: 'Zesto has the lowest total cost of ownership at $335 per battery. We recommend Zesto.'",
     "scenario": "At one cycle per day for 5 years (1,825 cycles), Zesto needs 4 batteries per bike ($1,400 with labor) vs Volta 1 ($425); choosing Zesto costs $4,312,000 vs $1,309,000 for 3,080 bikes, about $3.0M more.",
     "fix": "Compute five-year TCO as batteries needed x price + swaps x labor, per bike and per fleet; on supplied data recommend Volta.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every memo sentence and table for price-only reasoning", "found": "the price table (recorded as F2)"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md: price table (single column 'Price per battery')",
     "scenario": "An approver reading the table sees Zesto 18% cheaper and cannot see it costs about 3.3x Volta over the five-year commitment; the requested five-year TCO comparison is never performed.",
     "fix": "Add cycle life, batteries over 5 years, labor, five-year cost per bike and fleet total for 3,080 bikes.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every memo sentence and table for price-only reasoning", "found": "the conclusion sentence (recorded as F1)"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md: 'Each bike uses its battery once a day.'",
     "scenario": "The winner depends on usage (<=600 cycles in 5 years favours Zesto, 601-1,000 Amperia, >1,000 Volta); the rate is unsourced and never applied, so the recommendation rests on an unverified number.",
     "fix": "Source the usage rate from fleet telemetry and add a cycles-per-day sensitivity table.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "A", "location": "suppliers.csv: Volta cycle_life 2000",
     "suspicion": "Volta may suffer calendar ageing before 5 years despite unused cycle life.",
     "unresolved_fact": "Volta's warranty and capacity-retention spec at 5 years."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Counting a 4th Zesto battery for the final 25 days overstates its cost enough to change the ranking.",
     "evidence": "With 3 or a fractional 3.04 batteries Zesto is still about $1,050 per bike vs Volta $425."}
  ]
}
```