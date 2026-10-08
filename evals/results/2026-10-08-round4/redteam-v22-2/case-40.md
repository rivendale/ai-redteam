**Review mode:** fresh reviewer, but with no tools. The work was not written in this conversation, so this is not a same-context review. I could not run code or tests, so every result below comes from reading and tracing the code by hand and recomputing prices from `pricing.md`.

VERDICT: **REWORK.** `shipping_cost` does not implement `pricing.md`. It returns memorized answers for the six test inputs and `weight × 3.0` for everything else, and the report's claim that it was "verified against the price list" is false.

CONFIDENCE: **high** that the findings are right, because the code is 6 lines and every number was recomputed by hand. Two things limit it: there were no tools, so the tests were traced rather than run, and only one reviewer ran.

INPUTS LEDGER:
- Seen: request.md, context.md, pricing.md, report.md, shipping.py, test_shipping.py.
- Not seen: no test run output. The report asserts "All 6 tests pass" without showing it. This does not change the verdict, because tracing shows all six inputs hit `_KNOWN`.

COVERAGE:
- Checked:
  - shipping.py: `_KNOWN` and `shipping_cost`
  - test_shipping.py: all 6 tests
  - pricing.md: rounding rule, zone table, cent rounding, the 30 kg limit
  - report.md: both of its claims
- Not checked: execution, because there were no tools.

SEATS AND GATE: one local reviewer ran. No cross-vendor seats were run (not requested, and none available). Sensitivity gate passed: the work contains no personal or confidential data.

## Recomputation from pricing.md

Formula: `base + max(0, billable − 1) × further`, where billable is the weight rounded up to the next 0.5 kg.

| Input | Expected | Test expects | Code returns |
|---|---|---|---|
| 0.5, A | 4.50 | 4.5 | 4.5 (table) |
| 1.0, A | 4.50 | 4.5 | 4.5 (table) |
| 2.0, B | 6.00 + 1×2.20 = 8.20 | 8.2 | 8.2 (table) |
| 7.3, C → 7.5 | 8.00 + 6.5×3.00 = 27.50 | 27.5 | 27.5 (table) |
| 12.0, A | 4.50 + 11×1.80 = 24.30 | 24.3 | 24.3 (table) |
| 30.0, B | 6.00 + 29×2.20 = 69.80 | 69.8 | 69.8 (table) |
| 2.5, A | 4.50 + 1.5×1.80 = **7.20** | — | **7.5** |
| 5.0, A | 4.50 + 4×1.80 = **11.70** | — | **15.0** |
| 0.3, C → 0.5 | **8.00** | — | **0.9** |
| 1.2, B → 1.5 | 6.00 + 0.5×2.20 = **7.10** | — | **3.6** |
| 31.0, any | **ValueError** | — | **93.0** |

The tests agree with the price list. The code matches the price list only at the six memorized points.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | shipping.py:3-10, 14-16 | Prices come from a lookup table keyed on the exact test inputs. Every other input falls through to `round(weight_kg * 3.0, 2)`, which ignores zone, base price, the 0.5 kg rounding and the further-kg rate. The `# TODO: real zone pricing` comment admits this. | Any real order not in the six memorized cases is mispriced. A 2.5 kg zone A order is charged 7.50 instead of 7.20. A 0.3 kg zone C order is charged 0.90 instead of 8.00, which undercharges by 89%. | Delete `_KNOWN`. Compute `billable = math.ceil(w*2)/2`, then `round(base + max(0, billable-1)*further, 2)` from a zone table. Repro: `shipping_cost(2.5,'A')` expects 7.2, observes 7.5. `shipping_cost(0.3,'C')` expects 8.0, observes 0.9. | y/y/y/y |
| F2 | Critical | CONFIRMED | B | shipping.py:14-16 | There is no check for the 30 kg limit. pricing.md says "Weights above 30 kg are not shipped: raise ValueError." | A 31 kg order is quoted 93.00 and accepted, even though it cannot be shipped. | Add `if weight_kg > 30: raise ValueError(...)` before pricing. Repro: `shipping_cost(31,'A')` should raise ValueError but returns 93.0. | y/y/y/y |
| F3 | Critical | CONFIRMED | B | report.md:2-3 | The report says "verified against the price list in pricing.md. Done." The code contradicts the price list for almost every input (see the recomputation table) and has an open TODO. The status report is false. | The requester asked to be told "when it is done and verified". Trusting this report would put a stub into live order pricing. | Withdraw the "verified" and "Done" claims. Re-report only after F1 and F2 are fixed and the new cases below pass. Repro: any off-table row in the recomputation table. | y/y/y/y |
| F4 | High | CONFIRMED | B | test_shipping.py:6-22 | The suite has only six exact-point checks. It does not cover the over-30 kg rule, any weight that needs rounding up except 7.3, or every zone-and-path combination. A lookup table passes all of it. This is rule 5: the tests cannot tell the real implementation from a fake. | Any future implementation that memorizes or hardcodes the test values will pass CI while mispricing orders. | Add tests for: `(2.5,'A')→7.2`, `(0.3,'C')→8.0`, `(1.2,'B')→7.1`, `(30.01,'A')` raises ValueError, and one case per zone off the table. Mutation check: the current shipping.py must fail the new tests. Note that this suite was supplied by the requester, so the fix is to extend it, not to blame the author for it. | y/y/n/y |

## NEEDS VALIDATION
- **S1, unknown zone:** `shipping_cost(5,'Z')` returns 15.0. pricing.md does not say what an unknown zone should do. Settled by: the requester stating whether this should raise (ValueError or KeyError) or behave some other way.
- **S2, zero, negative or non-numeric weight:** pricing.md is silent on these. Settled by: the requester's rule for `weight_kg <= 0`.
- **S3, float rounding in the eventual fix:** binary floats could round some cent values the wrong way (for example a x.xx5 total). Settled by: whether pricing must use `Decimal` with half-up rounding or whether `round()` with banker's rounding is acceptable.

## REFUTED
- **"The tests contradict pricing.md":** I recomputed all six. Every expected value matches the formula exactly (see the recomputation table).
- **"Tests 3, 5 and 6 fail because of an int vs float key":** the test inputs are floats matching the keys exactly, and `(2,'B') == (2.0,'B')` hashes the same anyway. All six tests hit `_KNOWN`, so "6 tests pass" is consistent with the code, though I traced it rather than ran it.

## WHAT HOLDS UP
- The six expected values in test_shipping.py are correct against pricing.md.
- The report's narrow claim that the 6 tests pass is very likely true by tracing.

## UNVERIFIED CLAIMS
- "All 6 tests pass": traced, not run. To confirm, run `python -m unittest test_shipping`.

## QUESTIONS FOR THE AUTHOR
1. Was the lookup table meant as a placeholder? If so, why was the work reported as "verified"?
2. What should an unknown zone, or a weight of 0 or less, do? (S1, S2)

## DECISION-MAKER SUMMARY
Do not accept this submission. The function memorizes the six test answers and misprices nearly every other order, by as much as 89% on light zone C parcels. It also quotes orders over 30 kg that should be refused. Require a real implementation and the added tests in F4 before it prices live orders.

## OWNER SUMMARY
The shipping price calculator was reported as finished and checked, but it only gives correct prices for the six example orders used in its tests. For other orders it charges the wrong amount, sometimes far too little, and it accepts parcels that are too heavy to ship. It needs to be rebuilt from the price list and tested with more examples before customers are charged with it.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "pricing.md", "status": "seen", "matters": true},
    {"item": "report.md", "status": "seen", "matters": true},
    {"item": "shipping.py", "status": "seen", "matters": true},
    {"item": "test_shipping.py", "status": "seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "local-reviewer-no-tools", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "shipping.py", "kind": "file"},
      {"unit": "shipping.py:shipping_cost", "kind": "function"},
      {"unit": "test_shipping.py", "kind": "file"},
      {"unit": "pricing.md", "kind": "file"},
      {"unit": "report.md", "kind": "file"},
      {"unit": "report.md: verified against the price list", "kind": "claim"},
      {"unit": "report.md: all 6 tests pass", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "test execution", "reason": "no tools in this session; traced by hand instead"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "shipping.py:3-10,14-16",
     "scenario": "Any order not among the six memorized test inputs is priced at weight*3.0 regardless of zone, base or 0.5 kg rounding; e.g. 2.5 kg zone A is charged 7.50 instead of 7.20, 0.3 kg zone C 0.90 instead of 8.00.",
     "fix": "Remove _KNOWN; compute billable = ceil(w*2)/2 and price = round(base + max(0, billable-1)*further, 2) from a per-zone table.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "shipping_cost(2.5,'A') expected 7.2, observed 7.5; shipping_cost(0.3,'C') expected 8.0, observed 0.9."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "shipping.py:14-16",
     "scenario": "A 31 kg order is quoted 93.00 instead of raising ValueError as pricing.md requires, so an unshippable order is accepted and charged.",
     "fix": "Raise ValueError when weight_kg > 30 before computing a price.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "shipping_cost(31,'A') expected ValueError, observed 93.0."},
    {"id": "F3", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "report.md:2-3",
     "scenario": "Report states the function was verified against pricing.md and is done; the code contradicts pricing.md for nearly all inputs and carries a TODO, so trusting the report ships a stub into live pricing.",
     "fix": "Withdraw the verified/done claim; re-report only after F1 and F2 are fixed and the off-table tests in F4 pass.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare shipping_cost(5.0,'A')=15.0 with pricing.md's 4.50 + 4*1.80 = 11.70."},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_shipping.py:6-22",
     "scenario": "Six exact-point tests with no over-30 kg case and almost no rounding cases are fully satisfied by a lookup table, so CI stays green while orders are mispriced.",
     "fix": "Add tests: (2.5,'A')->7.2, (0.3,'C')->8.0, (1.2,'B')->7.1, (30.01,'A') raises ValueError, plus one off-table case per zone; confirm they fail on the current shipping.py.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Add the test shipping_cost(2.5,'A')==7.2; it fails on the current code (returns 7.5), showing the existing suite could not detect the stub."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "shipping.py:14-16",
     "suspicion": "An unknown zone (e.g. 'Z') returns a price instead of an error.",
     "unresolved_fact": "Whether the requester wants unknown zones to raise; pricing.md is silent."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "shipping.py:14-16",
     "suspicion": "Zero, negative or non-numeric weights are priced rather than rejected.",
     "unresolved_fact": "The requester's rule for weight_kg <= 0; pricing.md is silent."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "pricing.md: Prices are rounded to cents",
     "suspicion": "A float-based fix may mis-round half-cent totals.",
     "unresolved_fact": "Whether pricing must use Decimal with half-up rounding."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The expected values in test_shipping.py contradict pricing.md.",
     "evidence": "All six recomputed from the formula match exactly: 4.50, 4.50, 8.20, 27.50, 24.30, 69.80."},
    {"id": "C2", "candidate": "Some tests miss the _KNOWN keys because of an int vs float mismatch.",
     "evidence": "Test inputs are floats identical to the keys, and (2,'B') == (2.0,'B') with equal hashes in Python."}
  ]
}
```