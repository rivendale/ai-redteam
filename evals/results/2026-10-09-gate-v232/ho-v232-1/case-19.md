> Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes. No tools were available, so every figure below was recomputed by hand from the supplied inputs.

**VERDICT: SHIP.** Every figure in the memo recomputes from `suppliers.csv`, and the recommendation (Volta) holds under any usage above about 0.55 cycles per bike per day.

**CONFIDENCE: medium.** It is limited by three things: this was a same-context review, I had no tools, and the usage rate of one cycle per day is the memo's assumption, not sourced data.

**INPUTS LEDGER:**
- **Seen:**
  - `request.md`
  - `context.md`
  - `memo.md`
  - `suppliers.csv`
- **Not seen:** actual fleet usage data (cycles per bike per day).
  - It matters only if real usage is below about 1,000 cycles in five years. See the Needs Validation section.
- **Not supplied:** warranty, calendar-aging, disposal and pricing-stability terms.
  - These lie outside the data the request named. They are listed as questions, not as defects.

**COVERAGE:**
- **Scope:** the whole memo, checked against the request and the CSV.
- **Checked:**
  - `request.md`, `context.md`, `memo.md` and `suppliers.csv`
  - the cycle count (5 × 365 = 1,825)
  - battery counts, purchase totals, labor totals and per-bike totals for all three suppliers
  - the ranking
  - the usage assumption, including a sensitivity sweep
  - residual value
  - discounting
- **Not checked:** data outside the inputs (warranty, calendar life, disposal), because it was not supplied.

**SEATS AND GATE:**
- **Sensitivity:** no sensitive data was found.
- **Seats:** no subagent or cross-vendor seats were available, so this was a local same-context review only.

**FINDINGS:**

None. Nothing reached Low.

The arithmetic checks out for each supplier:

| Supplier | Cycle life | Batteries for 1,825 cycles | Purchase | Swap labor | Per-bike total | Memo |
|---|---|---|---|---|---|---|
| Volta | 2,000 | 1 | 1 × 410 = $410 | 0 swaps = $0 | $410 | ✓ |
| Amperia | 1,000 | ⌈1.825⌉ = 2 | 2 × 380 = $760 | 1 swap = $15 | $775 | ✓ |
| Zesto | 600 | ⌈3.04⌉ = 4 | 4 × 335 = $1,340 | 3 swaps = $45 | $1,385 | ✓ |

For Zesto, batteries 1 to 3 cover cycles 1 to 1,800, and battery 4 covers cycles 1,801 to 1,825. That gives 4 batteries and 3 replacements.

**NEEDS VALIDATION:**
- **N1, the usage rate (`memo.md`, line 1).** "Once a day" is asserted, not sourced.
  - The decision flips only if five-year usage is at most 1,000 cycles, which is about 0.55 per day. At that usage Amperia needs one battery ($380) and Volta still costs $410, so Amperia saves $30 per bike, or $92,400 across the fleet.
  - The fact that settles it is the fleet's measured average cycles per battery per day.
  - Above that threshold Volta wins at every rate. Its cost per cycle is $0.205, against $0.38 for Amperia and about $0.56 for Zesto.
- **N2, calendar aging.** The memo assumes Volta's battery lasts five years if it stays under 2,000 cycles.
  - The fact that settles it is Volta's rated calendar life or warranty term, which was not supplied.

**REFUTED:**
- **R1, "Ignoring residual value biases the result."**
  - Crediting leftover cycles pro rata gives Volta about $374, Amperia about $709 and Zesto about $1,064.
  - The ranking is unchanged.
- **R2, "Ignoring discounting biases the result."**
  - Discounting lowers only the later replacement costs. At any plausible rate it cannot close Volta's $365 lead over Amperia.
- **R3, "Initial install labor is omitted."**
  - The omission applies equally to all three suppliers, so it does not change the comparison.

**WHAT HOLDS UP:**
- All figures are correct.
- The labor model is applied consistently.
- The recommendation follows from the table.
- The memo correctly flags the counterintuitive result: the most expensive battery is the cheapest to own.

**UNVERIFIED CLAIMS:**
- The once-a-day usage rate. Confirm it from fleet telemetry.

**QUESTIONS FOR THE AUTHOR:**
- What is the fleet's measured cycles per bike per day?
- Does Volta's warranty or calendar life cover five years?

**DECISION-MAKER SUMMARY:**
- Proceed with Volta. The math is correct and the choice is robust to usage anywhere above about 0.55 cycles per day.
- At one cycle per day, the fleet-wide five-year cost is $1.26M for Volta, against $2.39M for Amperia and $4.27M for Zesto.
- Confirm actual usage and Volta's calendar life before signing.

**OWNER SUMMARY:**
The cost comparison is correct, and Volta is clearly the cheapest battery to own over five years despite its higher sticker price. The only thing that could change the answer is if bikes are used much less than once a day on average. Check real usage data and the battery's age-based warranty before committing.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "fleet usage data (cycles per bike per day)", "status": "not_seen", "matters": true},
    {"item": "supplier warranty / calendar-life terms", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "memo.md", "kind": "document"},
      {"unit": "suppliers.csv", "kind": "data"},
      {"unit": "memo.md:table (battery counts, purchase, labor, totals)", "kind": "claim"},
      {"unit": "memo.md:once-a-day usage", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "warranty, calendar life, disposal costs", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "N1", "status": "needs_validation", "track": "A", "location": "memo.md:line 1 (\"once a day\")",
     "suspicion": "If real usage is at most 1,000 cycles in five years (about 0.55/day), Amperia is $30/bike cheaper and the recommendation flips.",
     "unresolved_fact": "Measured average cycles per bike per day from fleet telemetry."},
    {"id": "N2", "status": "needs_validation", "track": "A", "location": "memo.md:table, Volta row",
     "suspicion": "A single Volta battery may not last five years on calendar aging even under 2,000 cycles.",
     "unresolved_fact": "Volta's rated calendar life or warranty term."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Ignoring residual value biases the ranking.", "evidence": "Pro-rata residual credit gives about $374 / $709 / $1,064; ranking unchanged."},
    {"id": "R2", "candidate": "Ignoring discounting biases the ranking.", "evidence": "Discounting only reduces later replacement costs and cannot close a $365 per-bike gap."},
    {"id": "R3", "candidate": "Initial install labor is omitted.", "evidence": "The omission is identical across all suppliers, so the comparison is unaffected."}
  ]
}
```