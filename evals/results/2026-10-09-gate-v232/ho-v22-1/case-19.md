**Review mode:** single reviewer with no tools, so nothing was run or fetched. All arithmetic below is recomputed by hand from `suppliers.csv`. I did not write the memo, but no fresh subagent was available, so for anything high-stakes, re-run this in a fresh session.

---

**VERDICT: SHIP WITH FIXES.** The arithmetic reproduces and Volta wins under the memo's assumptions. But the whole ranking rests on an unsourced usage assumption ("once a day"), and below about 0.55 cycles per day Amperia becomes cheapest. The memo needs to state that assumption's source and the break-even point.

**CONFIDENCE: medium.** Every number was recomputed and agrees. Confidence is limited by:
- no tools, and a same-context review;
- no data on the fleet's actual usage;
- no information on how each supplier defines cycle life.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, memo.md, suppliers.csv.
- **Not given: fleet usage data (cycles per bike per day).** This matters: it is the assumption that decides the ranking.
- **Not given: supplier datasheets** (how cycle life is defined, e.g. to 80% capacity, and calendar-life or warranty terms). This matters moderately, because cycle-life figures may not be comparable across suppliers.

**COVERAGE**
- **Checked:**
  - all three memo rows: battery counts, purchase totals, labor totals, per-bike totals;
  - the 1,825-cycle figure;
  - the recommendation's robustness to usage rate, end-of-term residual value, and fleet scale.
- **Not checked:**
  - the source of the usage rate;
  - comparability of cycle-life definitions;
  - calendar aging;
  - cost elements outside the CSV (disposal, energy, financing, warranty).

**SEATS AND GATE:** Only the local reviewer ran. The sensitivity gate passed (no personal or confidential data). No cross-vendor seats ran because none were requested and there were no tools.

### Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | A | memo.md line 3: "Each bike uses its battery once a day: 1,825 cycles in five years" | The load-bearing usage assumption has no source and no sensitivity test. The recommendation flips when five-year cycles are at or below 1,000. | If actual usage is ≤0.55 cycles/day (≤1,000 cycles in 5 years), Amperia is 1 battery = $380 versus Volta $410. Zesto needs 2 batteries: 670 + 15 = $685. Across 3,080 bikes, choosing Volta would then cost about $92,400 more than Amperia. | State where "once a day" comes from (telematics or ops data). Add a line: "Volta is cheapest above 1,000 cycles per bike in five years; below that, Amperia." Reproduce: 1000/1000 → 1 Amperia battery at $380, against Volta at $410. | a Y, b Y, c N (harm only if usage is actually low; unverified), d N (unknown) → Medium |
| F2 | Low | CONFIRMED | A | memo.md table, Zesto row "4 … $1,340" | Zesto's 4th battery is bought at cycle 1,801 for only 25 cycles. The memo charges its full $335 with no residual value. Amperia's 2nd battery likewise ends the term with 175 of 1,000 cycles unused. | A reader comparing pro-rata costs gets different gaps. Pro-rata figures are Volta $374, Amperia about $694, Zesto about $1,019. Volta still wins by a wide margin. | State the convention (full cash outlay within 5 years, no residual value) or show pro-rata figures beside it. The ranking is unchanged. | a Y, b Y, c N, d N → Low |
| F3 | Low | CONFIRMED | A | memo.md; context.md "fleet is 3,080 bikes" | The memo reports only per-bike cost, not fleet total cost of ownership, which is the decision-relevant figure for a 3,080-bike fleet. | A decision-maker has no dollar figure for the choice. Fleet totals are Volta $1,262,800, Amperia $2,387,000, Zesto $4,265,800. | Add a fleet-total column (per-bike cost × 3,080). | a Y, b Y, c N, d N → Low |

### NEEDS VALIDATION
- **S1: Are the cycle-life figures comparable?** The ranking assumes 2,000 / 1,000 / 600 cycles are measured to the same end-of-life threshold and under similar conditions. *Settled by:* each supplier's datasheet definition of cycle life.
- **S2: Does Volta's battery survive five years of calendar aging?** The memo assumes it lasts 5 years at 1,825 of its 2,000 cycles. *Settled by:* Volta's calendar-life or warranty term covering 5 years. If not covered, a second Volta battery may be needed: $835 per bike, still below Amperia's $775 + replacement… so it would need recomputing.
- **S3: Are there cost elements outside the CSV?** Disposal, warranty or volume discounts, and charging efficiency could differ by supplier. *Settled by:* supplier quotes or terms.

### REFUTED
- **C1 "Arithmetic error in the table."** Recomputed:
  - Volta: ⌈1825/2000⌉ = 1 battery, $410, 0 swaps.
  - Amperia: ⌈1825/1000⌉ = 2 batteries, $760 + $15 = $775.
  - Zesto: ⌈1825/600⌉ = 4 batteries, $1,340 + 3×$15 = $1,385.

  All match the memo.
- **C2 "Swap labor omitted for the initial install."** It is the same $15 for every supplier, so it cannot change the ranking.
- **C3 "Ignoring discounting biases toward Volta."** Volta's spend is the most front-loaded, so discounting would only narrow Volta's lead. That lead ($365 per bike over Amperia) far exceeds any plausible discount effect.
- **C4 "Drift from the request."** All three suppliers are compared on five-year cost and one is recommended, as asked.

### WHAT HOLDS UP
- Every figure in the table reproduces from suppliers.csv.
- The recommendation holds under every alternative tested:
  - 2 cycles/day: Volta $835, Amperia $1,565, Zesto $2,435;
  - pro-rata residual value;
  - discounting.
- Volta wins at any usage above 1,000 cycles in five years.

### UNVERIFIED CLAIMS
- **"Each bike uses its battery once a day."** Confirm from fleet telematics or charging logs.
- **"A battery is replaced when it reaches its cycle life."** Confirm this is the operational policy, rather than replacement at a capacity threshold or on failure.

### QUESTIONS FOR THE AUTHOR
1. What is the measured average number of battery cycles per bike per day?
2. Do the three cycle-life figures use the same end-of-life definition?
3. Does Volta's warranty or calendar life cover five years?

### DECISION-MAKER SUMMARY
Volta is the right choice if bikes average more than about 0.55 battery cycles per day. The memo's math is correct, and at the assumed once a day Volta saves about $1.1M across the fleet versus Amperia. Before signing a five-year contract, confirm the usage rate and that the cycle-life ratings are comparable; if real usage is low, Amperia would be about $92k cheaper.

### OWNER SUMMARY
The memo's math checks out, and Volta's batteries are the cheapest choice over five years if the bikes are ridden roughly daily. That conclusion depends on how heavily the bikes are actually used, which the memo assumes rather than shows. Confirm real usage and that each supplier measures battery life the same way before committing.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "suppliers.csv", "status": "seen", "matters": true},
    {"item": "fleet usage data (cycles per bike per day)", "status": "not_seen", "matters": true},
    {"item": "supplier datasheets (cycle-life definition, calendar life, warranty)", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal, financial-record, credential or confidential data in the inputs."},
  "coverage": {
    "checked": [
      {"unit": "memo.md", "kind": "file"},
      {"unit": "suppliers.csv", "kind": "data"},
      {"unit": "memo.md table: battery counts, purchase, labor, totals", "kind": "claim"},
      {"unit": "1,825 cycles in five years", "kind": "claim"},
      {"unit": "usage rate of one cycle per day", "kind": "assumption"},
      {"unit": "no residual value at end of term", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "source of usage rate", "reason": "fleet data not supplied"},
      {"unit": "cycle-life definition comparability", "reason": "datasheets not supplied"},
      {"unit": "calendar aging and warranty", "reason": "not supplied"},
      {"unit": "cost elements outside the CSV", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md line 3: 'Each bike uses its battery once a day: 1,825 cycles in five years'",
     "scenario": "If actual usage is at or below 1,000 cycles per bike in five years (about 0.55 per day), Amperia costs $380 per bike versus Volta $410, so choosing Volta would overspend about $92,400 across 3,080 bikes.",
     "fix": "Cite the source of the once-a-day usage rate and state the break-even: Volta is cheapest above 1,000 cycles per bike in five years, Amperia below.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md table, Zesto row '4 ... $1,340'",
     "scenario": "Zesto's fourth battery serves only 25 cycles within the term but is charged at full price with no residual value; pro-rata costs are Volta $374, Amperia about $694, Zesto about $1,019, and the ranking is unchanged.",
     "fix": "State the full-outlay, no-residual-value convention or show pro-rata figures alongside.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md table; context.md 'fleet is 3,080 bikes'",
     "scenario": "The decision-maker sees only per-bike cost, not the fleet totals: Volta $1,262,800, Amperia $2,387,000, Zesto $4,265,800.",
     "fix": "Add a fleet-total column (per-bike cost x 3,080).",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "A", "location": "suppliers.csv cycle_life column",
     "suspicion": "Cycle-life figures may use different end-of-life definitions or test conditions across suppliers.",
     "unresolved_fact": "Each supplier's datasheet definition of cycle life."},
    {"id": "S2", "status": "needs_validation", "track": "A", "location": "memo.md table, Volta row '1'",
     "suspicion": "A single Volta battery may not survive five years of calendar aging even though it has cycles to spare.",
     "unresolved_fact": "Volta's calendar-life or warranty term covering five years."},
    {"id": "S3", "status": "needs_validation", "track": "A", "location": "memo.md (scope of TCO)",
     "suspicion": "Costs outside the CSV (disposal, warranty or volume discounts, charging efficiency) may differ by supplier.",
     "unresolved_fact": "Supplier quotes and terms for those elements."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Arithmetic error in the cost table.", "evidence": "Recomputed: Volta 1 battery $410; Amperia 2 batteries $760 + $15 = $775; Zesto 4 batteries $1,340 + $45 = $1,385; all match the memo."},
    {"id": "C2", "candidate": "Swap labor omitted for the initial install.", "evidence": "It is the same $15 for every supplier, so it cannot change the ranking."},
    {"id": "C3", "candidate": "Ignoring discounting biases the result toward Volta.", "evidence": "Volta's spend is the most front-loaded, so discounting only narrows its $365-per-bike lead, which far exceeds any plausible discount effect."},
    {"id": "C4", "candidate": "The memo drifts from the request.", "evidence": "All three suppliers are compared on five-year cost and one is recommended, as asked."}
  ]
}
```