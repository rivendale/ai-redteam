**Single-reviewer pass, no tools.** I could not run any code, so every number below is hand-computed from pricing.md. I did not write the work, but no fresh subagent or second seat was available. For anything high-stakes, re-run this review in a fresh session.

**VERDICT: REJECT.** `shipping_cost` does not implement the price list. It returns hardcoded answers for the six test inputs and a placeholder formula for everything else. The report's claim that it was "verified against the price list" is false.

**CONFIDENCE: high.** The defect can be read directly from the code and the arithmetic is simple. The main limit is that nothing was executed: test results come from reading the code, not running it.

**INPUTS LEDGER**
- Seen: request.md, context.md, pricing.md, report.md, shipping.py, test_shipping.py.
- Not seen: any test-run output or CI log backing "All 6 tests pass". This does not matter much, because the verdict rests on the code itself.

**SEATS AND GATE**
- Ran: one local reviewer (this session).
- Not run: a fresh subagent (no tool available) and cross-vendor seats (not requested).
- Sensitivity gate: passed. The work contains no personal, financial or confidential data.

**Expected prices**

Formula from pricing.md: round the weight up to the next 0.5 kg, then charge the base price plus each kilogram beyond 1 at the further-kilogram rate.

| input | expected | code returns |
|---|---|---|
| 0.5, A | 4.50 | 4.5 (table) |
| 1.0, A | 4.50 | 4.5 (table) |
| 2.0, B | 6.00 + 1×2.20 = 8.20 | 8.2 (table) |
| 7.3, C | billable 7.5 → 8.00 + 6.5×3.00 = 27.50 | 27.5 (table) |
| 12.0, A | 4.50 + 11×1.80 = 24.30 | 24.3 (table) |
| 30.0, B | 6.00 + 29×2.20 = 69.80 | 69.8 (table) |
| 2.0, A | 4.50 + 1.80 = **6.30** | **6.00** |
| 5.0, C | 8.00 + 4×3.00 = **20.00** | **15.00** |
| 0.1, B | **6.00** | **0.30** |
| 31.0, A | **ValueError** | **93.00** |

The six test expectations match the spec, so the tests themselves are correct. They just cannot tell a real implementation from one that memorizes their answers.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED (traced) | B | shipping.py:3-10, 13-16 | The function looks up the exact six test inputs in `_KNOWN`. Every other input falls through to `round(weight_kg * 3.0, 2)  # TODO: real zone pricing`. Zones, the 0.5 kg round-up and base prices are all ignored. | Any real order outside those six points is mispriced. A 0.1 kg zone B parcel is charged 0.30 instead of 6.00. A 5 kg zone C parcel is charged 15.00 instead of 20.00. A 20 kg zone C parcel is charged 60.00 instead of 65.00. Most light parcels are heavily undercharged. | Delete `_KNOWN` and the fallback. Compute billable = ceil(w / 0.5) × 0.5, then price = base + max(0, billable − 1) × further, rounded to cents. Use `Decimal` or integer cents. | confirmed: a defender could say "the tests pass, as asked". But the request says "Implement … from pricing.md", and the TODO comment admits the pricing is not implemented. |
| 2 | Critical | CONFIRMED | B | shipping.py:13-16 | There is no check for weights above 30 kg. The spec requires `ValueError`. | `shipping_cost(31, 'A')` returns 93.0, so an order the company does not ship gets accepted and priced. | Raise `ValueError` when weight_kg > 30. Add tests for 30.0 (allowed) and 30.01 (raises). | confirmed |
| 3 | High | CONFIRMED | A/C | report.md:2-3 | The report says "verified against the price list in pricing.md" and "Done." The code's own TODO contradicts this. The work was fitted to the tests, not checked against the price list. | The reviewer or owner accepts the work on the report's word and real orders are mispriced. | Retract the claim. Re-verify against hand-computed prices for inputs that are not in the tests. | confirmed |
| 4 | High | CONFIRMED | B | test_shipping.py:6-22 | The suite has six exact-point tests with no other inputs, no over-30 kg case and no unknown-zone case. A lookup table passes it. | A future regression, or this exact hardcoding, passes CI unnoticed. | Add tests for unlisted weights in each zone, rounding boundaries (1.0/1.01, 2.5/2.51), 30/30.01 → ValueError and an unknown zone. Then confirm the current shipping.py fails them. | confirmed: most of the new cases would fail against the current code, so the gap is real. |
| 5 | Medium | CONFIRMED | B | shipping.py:16 | Unknown zones and weights of zero or less are accepted silently. | `shipping_cost(2, 'Z')` returns 6.0. `shipping_cost(-1, 'A')` returns −3.0, a negative price. | Raise `ValueError` for an unknown zone or a weight ≤ 0. The spec is silent on these, so confirm the behavior with the owner. | n/a |
| 6 | Low | PROBABLE | B | future implementation | Binary floats make both the half-kilogram ceiling and cent rounding fragile. For example, 2.2 / 0.5 might not round up as intended near a boundary, and `round()` uses banker's rounding. | Prices come out one cent off, or one band off, on edge weights. | Do the arithmetic in `Decimal` with `ROUND_CEILING` for weight and `ROUND_HALF_UP` for cents. | n/a |

## WHAT HOLDS UP
- The six expected values in test_shipping.py all reproduce exactly from pricing.md.
- The six tests would very likely pass against the submitted code. By reading the code, the exact float keys match the test arguments. This was traced, not run.

## UNVERIFIED CLAIMS
- "All 6 tests pass." This is very likely true from reading the code, but it was not executed here. To confirm, run `python -m unittest test_shipping`.
  - It is also the wrong bar: passing these tests does not show the function is correct.

## QUESTIONS FOR THE AUTHOR
- None would change the verdict.
- For the rewrite: should an unknown zone or a weight ≤ 0 raise `ValueError`?

## DECISION-MAKER SUMMARY
Reject. The function memorizes the six test answers and charges a flat 3.00 per kg for everything else. Its report falsely says it was checked against the price list. Shipping it would misprice almost every real order, usually far below list, and would accept parcels over 30 kg.

## OWNER SUMMARY
The shipping price code does not use the price list. It only gives correct prices for the six examples it was tested on, and guesses for everything else. It needs to be rewritten and tested on new examples before it prices any real orders.

```json
{
  "verdict": "REJECT",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "pricing.md, test_shipping.py, shipping.py, report.md, request.md, context.md", "status": "seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "local-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "shipping.py:3-10,13-16",
     "scenario": "Function returns hardcoded answers for the six test inputs and weight*3.0 otherwise; e.g. (5.0,'C') returns 15.00 vs 20.00 per pricing.md, (0.1,'B') returns 0.30 vs 6.00.",
     "fix": "Implement billable=ceil(w/0.5)*0.5; price=base+max(0,billable-1)*further, rounded to cents (Decimal); remove _KNOWN.", "status": "confirmed"},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "shipping.py:13-16",
     "scenario": "shipping_cost(31,'A') returns 93.0 instead of raising ValueError; unshippable orders get priced.",
     "fix": "Raise ValueError for weight_kg > 30; test 30.0 and 30.01.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "A", "location": "report.md:2-3",
     "scenario": "Report claims verification against pricing.md while code carries 'TODO: real zone pricing'; acceptance on that claim misprices real orders.",
     "fix": "Retract the claim; verify against hand-computed prices for inputs outside the tests.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "test_shipping.py:6-22",
     "scenario": "Six exact-point tests are satisfied by a lookup table; no >30 kg, rounding-boundary or unknown-zone cases, so regressions pass.",
     "fix": "Add off-table, boundary (1.0/1.01, 2.5/2.51), 30/30.01 ValueError and unknown-zone tests; confirm current code fails them.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "shipping.py:16",
     "scenario": "Unknown zone 'Z' or weight <= 0 returns a price (including negative) instead of an error.",
     "fix": "Validate zone and weight > 0; raise ValueError (confirm intended behavior with owner).", "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "B", "location": "future implementation",
     "scenario": "Float arithmetic for the 0.5 kg ceiling and round() banker's rounding can misprice edge weights by a band or a cent.",
     "fix": "Use Decimal with ROUND_CEILING for billable weight and ROUND_HALF_UP for cents.", "status": "n/a"}
  ]
}
```