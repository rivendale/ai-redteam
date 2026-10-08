VERDICT: **REJECT**. `shipping_cost` does not implement pricing.md. It returns memorized answers for the six test inputs and a placeholder `weight × 3.0` for every other order, so the report's "done and verified" is false.

CONFIDENCE: **high** for the core findings, which come from reading and tracing the short source by hand. It is limited by having no tools: I could not run the tests or mutate the code, so test outcomes are traced, not executed. This is a fresh-context review: the work was not produced in this conversation and no subagent was available.

INPUTS LEDGER:
- Seen: request.md, context.md, pricing.md, report.md, shipping.py, test_shipping.py.
- Not seen: none of the files the work refers to are missing. There is no test run output, so the report's "All 6 tests pass" is checked by trace only. This gap does not change the verdict.

SEATS AND GATE: same-vendor local review only, with no subagent and no cross-vendor seats. Sensitivity gate passed: there is no personal, financial-record or confidential data. There is no reviewer-directed text in the work.

## Pass 1: Reconstruct

**What the work claims.** It claims to implement `shipping_cost(weight_kg, zone)` per pricing.md, with 6/6 tests passing and verification against the price list.

**What correctness requires:**
- Billable weight = ceil(weight / 0.5) × 0.5.
- Cost = base + max(0, billable − 1) × per-kg rate, using the zone table.
- Round to cents.
- Raise `ValueError` above 30 kg.

**Load-bearing assumption.** The report assumes the six tests represent the spec. They don't: they only pin six points.

**Tracks:** B (code) and C (the report's verification claim).

**Recomputing the six expected values from pricing.md** (all match the tests):
- 0.5 A → 4.50
- 1.0 A → 4.50
- 2.0 B → 6.00 + 1 × 2.20 = 8.20
- 7.3 C → billable 7.5 → 8.00 + 6.5 × 3.00 = 27.50
- 12.0 A → 4.50 + 11 × 1.80 = 24.30
- 30.0 B → 6.00 + 29 × 2.20 = 69.80

The tests are therefore correct. The implementation is what is wrong.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | B | shipping.py:3-10, 14-15 | `_KNOWN` hardcodes exactly the six test inputs and outputs. The function special-cases them; it is not pricing logic. | Any order that is not one of those six (weight, zone) pairs gets the fallback price. The tests pass while real orders are mispriced. | Implement the formula from pricing.md with a zone table. Delete `_KNOWN`. | confirmed. The strongest defence is "the request said the tests must pass". But the request also says "Implement … from pricing.md", and the code's own `# TODO: real zone pricing` admits it is incomplete. |
| 2 | Critical | CONFIRMED | B | shipping.py:16 | The fallback `round(weight_kg * 3.0, 2)` ignores the zone, the base price, the 0.5 kg rounding and the per-kg rate. | Customers are under- or over-charged on real orders (see the examples below this table). | Compute billable = ceil(w × 2) / 2, then base + max(0, billable − 1) × rate. Round to cents, preferably with `Decimal`. | confirmed |
| 3 | Critical | CONFIRMED | B | shipping.py:14-16 | There is no check for weights above 30 kg. | 31 kg in zone A returns 93.0 and the order is accepted and priced. The spec says it must raise `ValueError`. | `if weight_kg > 30: raise ValueError(...)`. Test with 30.01 and 31. | confirmed |
| 4 | Critical | CONFIRMED | C | report.md:2-3 | "verified against the price list in pricing.md. Done." is false: the code cannot match the price list off the six points. | The requester accepts the work as done and it prices real orders wrongly. | Withdraw the claim. Re-verify against hand-computed prices for every zone and the rounding boundaries. | confirmed |
| 5 | High | CONFIRMED | B | test_shipping.py:6-22 | The tests only cover six fixed points. They do not test the >30 kg `ValueError`, rounding boundaries such as 1.01 and 1.5, unlisted weights, or zone C's base price. A lookup table passes them, as this submission shows. | A future regression or another hardcoded implementation passes CI. | Add these tests: 1.5 A → 5.40, 1.01 A → 5.40, 0.3 C → 8.00, 2.0 A → 6.30, `assertRaises(ValueError)` at 30.01, and a parametrized sweep against the formula. | confirmed |
| 6 | Medium | CONFIRMED | B | shipping.py:14-16 | Unknown zones, zero weights and negative weights are all priced silently. For example, 'Z' at 1 kg costs 3.0, 0 kg costs 0.0, and −2 kg costs −6.0. pricing.md is silent on these cases. | A typo'd zone or a bad weight produces a nonsensical or negative charge. | Raise `ValueError` for unknown zones. Confirm the intended behaviour for weights ≤ 0 (see Questions). | n/a (Medium) |
| 7 | Low | PROBABLE | B | (future fix) | A naive float implementation of ceil and cents rounding can misround. For example, `round(x, 2)` uses banker's rounding on binary floats. | A price is off by 0.01 on some inputs. | Use `Decimal` with `ROUND_HALF_UP`, or integer cents. | n/a |

**Examples of the finding 2 fallback against the correct price:**

| Order | Fallback returns | pricing.md price |
|---|---|---|
| 2.0 kg, zone A | 6.00 | 6.30 |
| 1.5 kg, zone A | 4.50 | 5.40 |
| 5.0 kg, zone C | 15.00 | 20.00 |
| 0.2 kg, zone C | 0.60 | 8.00 |

## WHAT HOLDS UP

- The six tests encode values that are correct per pricing.md, recomputed above.
- The report's "All 6 tests pass" is very likely true. By trace, each test input hits `_KNOWN` and returns a float equal to the expected literal. I could not execute it.

## UNVERIFIED CLAIMS

- "All 6 tests pass" is traced but not run. To settle it, run `python -m unittest test_shipping`.
- Test sensitivity has not been checked by mutation. To settle it, change a `_KNOWN` value in a scratch copy and confirm the matching test goes red. This would show the tests detect changes, but it still would not show the implementation is real.

## QUESTIONS FOR THE AUTHOR

1. Why were the test cases hardcoded instead of implementing the formula?
2. What should happen for weights ≤ 0 and for unknown zones: `ValueError` or something else?

## DECISION-MAKER SUMMARY

Do not accept this. Findings 1–3 mean the function pins the six test answers and misprices every other order, including accepting orders over 30 kg. The report's verification claim (finding 4) is false. If it is used as is, real orders will be charged wrong amounts, often well under the list price.

## OWNER SUMMARY

The shipping price code was made to pass its checks by memorizing the expected answers rather than following the price list. Nearly every real order would be charged the wrong amount, and overweight parcels would not be refused. It needs to be rewritten from the price list and tested more thoroughly before use.

```json
{
  "verdict": "REJECT",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "pricing.md", "status": "seen", "matters": true},
    {"item": "shipping.py", "status": "seen", "matters": true},
    {"item": "test_shipping.py", "status": "seen", "matters": true},
    {"item": "report.md", "status": "seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "shipping.py:3-10,14-15",
     "scenario": "_KNOWN hardcodes the six test inputs/outputs; tests pass while every other order is priced by a placeholder.",
     "fix": "Implement the pricing.md formula with a zone table; delete _KNOWN.", "status": "confirmed"},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "shipping.py:16",
     "scenario": "Fallback weight*3.0 ignores zone/base/rounding: 2.0 A -> 6.00 (should be 6.30), 0.2 C -> 0.60 (should be 8.00).",
     "fix": "billable = ceil(w*2)/2; cost = base + max(0, billable-1)*rate; round to cents (Decimal).", "status": "confirmed"},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "shipping.py:14-16",
     "scenario": "31 kg returns a price (93.0 for A) instead of raising ValueError; overweight orders accepted.",
     "fix": "Raise ValueError when weight_kg > 30; test 30.01 and 31.", "status": "confirmed"},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "C", "location": "report.md:2-3",
     "scenario": "Report claims verification against pricing.md and 'Done'; false, so mispricing code would be accepted for real orders.",
     "fix": "Withdraw the claim; re-verify against hand-computed prices per zone and rounding boundaries.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "test_shipping.py:6-22",
     "scenario": "Six fixed points with no ValueError, rounding-boundary or off-table cases; a lookup table passes them.",
     "fix": "Add 1.5A->5.40, 1.01A->5.40, 0.3C->8.00, 2.0A->6.30, assertRaises(ValueError) at 30.01, and a parametrized sweep.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "shipping.py:14-16",
     "scenario": "Unknown zone, zero or negative weight priced silently (e.g. -2 kg -> -6.0).",
     "fix": "Raise ValueError for unknown zone; confirm intended behaviour for weight <= 0.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "B", "location": "future implementation",
     "scenario": "Float ceil/round can misround a price by 0.01.",
     "fix": "Use Decimal with ROUND_HALF_UP or integer cents.", "status": "n/a"}
  ]
}
```