VERDICT: **SHIP.** Every figure in the memo reproduces from suppliers.csv under the memo's stated rules, and Volta stays cheapest unless batteries are used far less than the memo assumes or wear out with age before their cycle life.

CONFIDENCE: **medium.** I had no tools, so all recomputation was done by hand. Two inputs the memo relies on were not supplied: the source of the "once a day" usage figure, and any calendar-life or warranty data. Either one could flip the ranking. The memo was not written in this session, so author anchoring does not apply. This was still a single-reviewer pass.

**INPUTS LEDGER**
- Seen: request.md, context.md, memo.md, suppliers.csv.
- Not seen: the source of "each bike uses its battery once a day". **Matters**, because the ranking flips below 1,000 cycles in five years.
- Not seen: battery calendar life, warranty terms, and how each supplier defines "cycle life" (for example, the capacity threshold at end of life). **Matters**, because they decide whether the CSV cycle lives can be compared.
- Not seen: residual or salvage value, downtime and disposal costs. These matter little; the margins below show they cannot close the gap.

**COVERAGE**
- Checked: every cell of the memo table; the battery count rule (ceil(1825 / cycle_life)); swap count (batteries − 1); the recommendation sentence; how sensitive the ranking is to cycles per day, calendar aging and residual value.
- Not checked: the usage source, supplier datasheets and warranties. None were supplied.

**SEATS AND GATE:** Local reviewer only, with no subagent or tools. No sensitive data was present, but no cross-vendor seats were requested or available.

**FINDINGS**

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | CONFIRMED | A | memo.md:3 and :11 | The recommendation depends on the 1-cycle/day assumption, but the memo does not say where that figure comes from or at what point the ranking changes. | If real usage is under 1,000 cycles in five years (≈0.55/day), Amperia costs $380 against Volta's $410. Under 600 cycles (≈0.33/day), Zesto costs $335. The memo gives the reader no way to see this. | Add a sensitivity line: "Volta wins at ≥1,000 cycles/5 yrs; at 2 cycles/day Volta $835 vs Amperia $1,565 vs Zesto $2,435." Also cite the usage source. Reproduction: set cycles = 900 and recompute; Amperia comes out at $380 vs Volta $410. | a:y b:y c:n d:n |
| F2 | Low | CONFIRMED | A | memo.md table | The memo gives only per-bike cost, although the context says the decision covers a 3,080-bike fleet. | A decision-maker comparing against budget has to do the multiplication themselves, so the size of the gap is less visible. | Add fleet totals: Volta $1,262,800; Amperia $2,387,000; Zesto $4,265,800 (3,080 × per-bike). | a:y b:y c:n d:n |

**NEEDS VALIDATION**
- **S1: calendar aging.** If a Volta battery cannot last five years of calendar time (if it fails from age, not cycles), each bike needs a second Volta battery. That costs 820 + 15 = $835, which loses to Amperia's $775. To settle it: the supplier's calendar life or warranty term for Volta, and field data at roughly 365 cycles per year.
- **S2: cycle-life comparability.** The comparison only holds if all three suppliers rate cycle life to the same end-of-life capacity (for example, 80%) under the same depth of discharge. To settle it: each supplier's datasheet definition.
- **S3: usage source.** The memo assumes one cycle per day. To settle it: fleet telemetry on full-equivalent cycles per bike per day. Per F1, it only matters if the figure is below about 0.55.

**REFUTED**
- **"The arithmetic is wrong."** Refuted by recomputation:
  - Volta: ceil(1825/2000) = 1 battery, $410, no swaps, total $410.
  - Amperia: ceil(1825/1000) = 2 batteries, $760, 1 swap ($15), total $775.
  - Zesto: ceil(1825/600) = 4 batteries, $1,340, 3 swaps ($45), total $1,385.
  All match the memo.
- **"Leaving out first-install labor biases the result."** Refuted: it would add the same $15 to every supplier, so the ranking is unchanged.
- **"Unused cycles left on the last battery (residual value) change the ranking."** Refuted: Zesto has the most left over, 575 of 600 cycles, worth at most about $322. That still puts Zesto at ≥$1,063, well above Volta's $410.
- **"The memo drifts from the request."** Refuted: it compares all three suppliers on five-year TCO using the CSV and recommends one, which is what the request asked for.

**WHAT HOLDS UP:** All table figures and the replacement logic hold. The memo's point that Volta's higher unit price is outweighed by its cycle life is correct. Volta's cost per cycle is $0.205, against $0.38 for Amperia and $0.56 for Zesto. Because of that, the ranking holds at any usage rate of about 1,000 cycles or more over five years.

**UNVERIFIED CLAIMS:** "Each bike uses its battery once a day." Confirm it with fleet telemetry. The CSV cycle lives are supplier-stated figures; confirm them against datasheets or independent test data.

**QUESTIONS FOR THE AUTHOR**
1. What is the source of 1 cycle/day?
2. Is Volta's battery rated or warrantied to last five calendar years at this duty cycle?
3. Do all three suppliers define cycle life to the same end-of-life capacity?

**DECISION-MAKER SUMMARY:** The math is correct, and Volta is the cheapest of the three at the stated usage, by about $1.1M over Amperia across the fleet. Before signing a five-year contract, confirm that Volta batteries last five calendar years and that all three suppliers measure cycle life the same way. If a Volta battery ages out early, Amperia becomes cheaper.

**OWNER SUMMARY:** The cost comparison adds up, and the recommended supplier is the cheapest over five years at the expected level of use. Before committing, check two things with the suppliers: whether that battery lasts five years on age alone, and whether the suppliers rate battery life the same way. If the answer to either is no, the recommendation could change.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "suppliers.csv", "status": "seen", "matters": true},
    {"item": "source of 1 cycle/day usage assumption", "status": "not_seen", "matters": true},
    {"item": "supplier calendar life, warranty and cycle-life definitions", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Supplier prices and cycle lives only; no personal or confidential data."},
  "coverage": {
    "checked": [
      {"unit": "memo.md", "kind": "file"},
      {"unit": "suppliers.csv", "kind": "data"},
      {"unit": "memo.md table: battery counts, purchase, swap labor, totals", "kind": "section"},
      {"unit": "memo.md:11 recommendation", "kind": "claim"},
      {"unit": "1 cycle/day usage", "kind": "assumption"},
      {"unit": "cycle life is the only replacement trigger", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "usage data source", "reason": "not supplied"},
      {"unit": "supplier datasheets and warranties", "reason": "not supplied; no tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md:3 and memo.md:11",
     "scenario": "If real usage is below 1,000 cycles in five years (about 0.55/day), Amperia ($380) beats Volta ($410); below 600 cycles Zesto ($335) wins. The memo neither sources the usage figure nor states this break-even.",
     "fix": "Cite the usage source and add a sensitivity line with the break-even and a 2 cycles/day case (Volta $835, Amperia $1,565, Zesto $2,435).",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Set cycles = 900: Volta 1 x $410 = $410; Amperia 1 x $380 = $380; ranking flips."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md table",
     "scenario": "The decision covers 3,080 bikes, but only per-bike costs are shown, so the fleet-level gap (about $1.1M Volta vs Amperia) is not visible to the decision-maker.",
     "fix": "Add fleet totals: Volta $1,262,800; Amperia $2,387,000; Zesto $4,265,800.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Multiply each per-bike total by 3,080."},
    {"id": "S1", "status": "needs_validation", "track": "A", "location": "memo.md:3",
     "suspicion": "Calendar aging may force a second Volta battery within five years, making Volta $835 per bike, above Amperia's $775.",
     "unresolved_fact": "Volta's rated calendar life or warranty term at about 365 cycles per year."},
    {"id": "S2", "status": "needs_validation", "track": "A", "location": "suppliers.csv:cycle_life",
     "suspicion": "Cycle-life figures may use different end-of-life capacity thresholds or depths of discharge, so they may not be comparable.",
     "unresolved_fact": "Each supplier's datasheet definition of cycle life."},
    {"id": "S3", "status": "needs_validation", "track": "A", "location": "memo.md:3",
     "suspicion": "The 1 cycle/day usage figure has no stated source.",
     "unresolved_fact": "Fleet telemetry on full-equivalent cycles per bike per day; it matters only if below about 0.55."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The memo's table arithmetic is wrong.",
     "evidence": "Recomputed: Volta 1 battery = $410; Amperia 2 x $380 + 1 x $15 = $775; Zesto 4 x $335 + 3 x $15 = $1,385. All match."},
    {"id": "C2", "candidate": "Excluding first-install labor biases the comparison.",
     "evidence": "The same $15 applies to every supplier, so the ranking is unchanged."},
    {"id": "C3", "candidate": "Residual value of the last battery changes the ranking.",
     "evidence": "Zesto's largest leftover is 575/600 cycles, worth at most about $322; Zesto remains at least $1,063, above Volta's $410."},
    {"id": "C4", "candidate": "The memo drifts from the request.",
     "evidence": "It compares all three suppliers on five-year TCO using the CSV and recommends one, as asked."}
  ]
}
```