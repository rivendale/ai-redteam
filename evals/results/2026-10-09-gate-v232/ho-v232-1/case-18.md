# Redteam review: battery supplier memo

**VERDICT: REWORK.** The memo calls purchase price "total cost of ownership". When the cycle life and swap labor in its own `suppliers.csv` are counted, Zesto is the most expensive option over five years and Volta is the cheapest.

**CONFIDENCE: high** on the arithmetic and on the recommendation being reversed. Three things limit it:
- I had no tools, so the figures below are recomputed by hand.
- This is a single reviewer with no subagent. The work was not written in this conversation, so the risk of anchoring on my own work is lower than usual.
- The usage rate is unsourced, and the ranking depends on it.

**INPUTS LEDGER:**
- Seen: `request.md`, `context.md`, `memo.md` and `suppliers.csv`, all inline.
- Not seen: the source of the usage figure ("once a day") and the source and definition of the cycle-life figures (for example, cycles to 80% capacity). Both gaps matter because the ranking depends on usage (see S1). Neither changes the result at the stated usage.

**COVERAGE:**
- Scope: the whole memo against the request.
- Checked:
  - `request.md`, `context.md`, `memo.md`, `suppliers.csv`
  - the memo's price table
  - the TCO claim
  - the recommendation
  - the usage assumption
- Not checked:
  - Supplier quality, warranty and lead times: not supplied.
  - Cycle-life test method: not supplied.

**SEATS AND GATE:**
- I reviewed it myself with no tools. No subagent or cross-vendor seats were available.
- Sensitivity gate passed: the material is vendor prices only, with no personal or confidential data.
- The work contains no text addressed to the reviewer.

## Recomputation

Basis: the memo's stated usage of 1 cycle per bike per day, over 5 years = 1,825 cycles. Each supplier's cost is the batteries needed times the price, plus $15 labor per replacement swap.

| Supplier | Cycle life | Batteries needed | Battery cost | Swap labor | 5-yr TCO per bike | Fleet (3,080 bikes) |
|---|---|---|---|---|---|---|
| Volta | 2,000 | 1 | $410 | $0 | **$410** | **$1,262,800** |
| Amperia | 1,000 | 2 | $760 | $15 | $775 | $2,387,000 |
| Zesto | 600 | 4 (replacements at cycles 600, 1,200 and 1,800) | $1,340 | $45 | $1,385 | $4,265,800 |

- **Gap:** Zesto costs $975 more per bike than Volta, which is **$3,003,000 across the fleet**.
- **Initial install labor:** counting $15 for the first fit adds $15 to every row and does not change the ranking.
- **Prorated view:** if the 4th Zesto battery is charged only for the cycles it actually uses (~1,019 battery cost + 45 labor ≈ $1,064), Zesto is still about 2.6× Volta.
- **Cost per cycle:** Volta $0.205, Amperia $0.395, Zesto $0.583 (each including swap labor). Zesto is cheapest only if a bike makes **600 cycles or fewer in five years**, which is roughly one cycle every three days.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | A | memo.md, "Zesto has the lowest total cost of ownership at $335 per battery. We recommend Zesto." | The memo equates TCO with the unit purchase price and ignores `cycle_life` and `swap_labor_usd`. It also contradicts its own once-a-day usage line. | At 1 cycle per day, each Zesto bike needs 4 batteries over five years versus 1 for Volta. Choosing Zesto costs about $3.0M more across 3,080 bikes, locked in for five years. | Compute five-year TCO per supplier as batteries needed × price + swaps × labor, scale it to the fleet, and recommend from that. On the memo's own usage figure the answer is Volta. | y/y/y/y |
| F2 | High | CONFIRMED | A | memo.md, price table (only the "Price per battery" column) | Drift: the request asks for a five-year TCO comparison, and the memo gives none. Cycle life and labor never appear, and no five-year figure exists for any supplier. | A decision-maker reading the table sees Zesto cheapest and cannot detect the error, because the inputs that reverse the ranking are left out. | Add cycle-life, batteries-per-bike, labor, five-year TCO per bike and fleet columns, and show the method. | y/y/y/y |
| F3 | Medium | CONFIRMED | A | memo.md (whole) | There is no sensitivity analysis or treatment of end-of-period value. Missing: the usage breakpoints, residual value at year 5, the cycle-life definition (capacity fade), downtime during swaps, a spares pool, and discounting. | Usage is the variable that flips the ranking: Zesto at ≤600 cycles, Amperia at 601–1,000, Volta at >1,000. A memo without these breakpoints cannot show its recommendation is robust. | Add a usage-sensitivity table with the breakpoints, and state the cycle-life definition and residual-value treatment. | y/y/n/n |

**Sibling search for F1 and F2:** I looked for every other place the memo uses or omits a `suppliers.csv` column.
- `cycle_life` and `swap_labor_usd` are unused anywhere.
- No other claim depends on them.

Neither is a security finding: no trust boundary is crossed.

## Needs validation

- **S1: the real usage rate.** The memo states "once a day" without a source. What would settle it: measured full-charge cycles per bike per day from the fleet data. Bike-share use is often several trips per day, which would favor Volta even more. Only at roughly one cycle every three days or less does Zesto win.
- **S2: the cycle-life figures.** These are supplier figures with no stated test conditions. What would settle it: the supplier datasheets (depth of discharge, end-of-life capacity threshold) and, ideally, field data.

## Refuted

- **"Including initial install labor changes the ranking."** Refuted: it adds $15 to every supplier equally.
- **"Prorating partial batteries rescues Zesto."** Refuted: prorated Zesto is about $1,064 versus $410 for Volta.

## Summary

**What holds up:**
- The three prices in the memo's table match `suppliers.csv` exactly.
- The usage assumption is at least stated.

**Unverified claims:**
- "Each bike uses its battery once a day." Confirm from the fleet's charge or trip logs.
- The cycle lives in the CSV. Confirm from the datasheets.

**Questions for the author:**
1. What is the measured cycles-per-bike-per-day, and what is its source?
2. Why were `cycle_life` and `swap_labor_usd` left out of the TCO?

**Decision-maker summary:** Do not adopt Zesto on this memo. Its "TCO" is just the sticker price, and on the memo's own usage figure Zesto costs about $4.27M over five years versus about $1.26M for Volta. Proceeding risks roughly $3M in avoidable cost. Have the analysis redone with cycle life, labor and real usage data before signing.

**Owner summary:** The memo picked the battery with the lowest sticker price, but that battery wears out much faster, so it would need replacing about four times as often as the most durable option. Counting replacements and the labor to swap them, the cheapest-looking choice becomes the most expensive by about three million dollars over five years. The comparison should be redone using real usage numbers before any supplier is chosen.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "suppliers.csv", "status": "seen", "matters": true},
    {"item": "source for 'once a day' usage", "status": "not_seen", "matters": true},
    {"item": "cycle-life test definitions / datasheets", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "self (no subagent, no tools)", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "vendor prices only; no personal or confidential data"},
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
      {"unit": "usage data source", "reason": "not_supplied"},
      {"unit": "supplier datasheets, warranty, quality", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md: 'Zesto has the lowest total cost of ownership at $335 per battery. We recommend Zesto.'",
     "scenario": "At the memo's own 1 cycle/day, 1,825 cycles over 5 years need 4 Zesto batteries (1,385 USD/bike incl. 3 swaps) vs 1 Volta (410 USD/bike); choosing Zesto costs 4,265,800 vs 1,262,800 USD for 3,080 bikes, about 3,003,000 USD more.",
     "fix": "Compute 5-year TCO = batteries needed x price + replacement swaps x labor, scale to fleet, and recommend on that (Volta at the stated usage).",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every claim in memo.md that uses or omits a suppliers.csv column", "found": "cycle_life and swap_labor_usd unused everywhere; see F2"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md: price table (Price per battery column only)",
     "scenario": "The request asks for a five-year TCO comparison; the table shows only unit price, so a reader sees Zesto as cheapest and cannot detect that durability and labor reverse the ranking.",
     "fix": "Add cycle life, batteries per bike over 5 years, swap labor, 5-year TCO per bike and per fleet, and the method.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all memo sections for any five-year figure", "found": "none exists for any supplier"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md (whole)",
     "scenario": "The ranking flips with usage (Zesto at <=600 cycles, Amperia at 601-1,000, Volta at >1,000 over 5 years); with no sensitivity analysis, residual value, cycle-life definition or discounting, the recommendation's robustness cannot be judged.",
     "fix": "Add a usage-sensitivity table with breakpoints and state cycle-life definition, residual value and discounting treatment.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "A", "location": "memo.md: 'Each bike uses its battery once a day.'",
     "suspicion": "The usage rate is unsourced and determines the ranking; bike-share batteries may cycle more than once per day.",
     "unresolved_fact": "Measured full-charge cycles per bike per day from fleet charge or trip logs."},
    {"id": "S2", "status": "needs_validation", "track": "A", "location": "suppliers.csv: cycle_life",
     "suspicion": "Cycle lives are supplier claims with unknown test conditions.",
     "unresolved_fact": "Datasheet depth-of-discharge and end-of-life capacity threshold, or field failure data."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Counting initial install labor changes the ranking.", "evidence": "It adds 15 USD to every supplier equally."},
    {"id": "C2", "candidate": "Prorating the partially used 4th Zesto battery rescues Zesto.", "evidence": "Prorated Zesto is about 1,064 USD/bike vs 410 for Volta."}
  ]
}
```