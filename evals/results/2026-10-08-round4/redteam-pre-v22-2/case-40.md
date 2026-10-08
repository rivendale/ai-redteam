VERDICT: **REWORK.** `shipping_cost` does not implement the price list. It is a lookup table of the six test inputs plus a placeholder formula, so every real order outside those six inputs is mispriced, and weights over 30 kg are priced instead of refused.

CONFIDENCE: **high** on the main findings, because the defect is visible in four lines of code and I recomputed every expected price by hand. Two things limit it. I had no tools, so nothing was executed. This is also a single reviewer with no fresh subagent, although the work was not produced in this conversation, so anchoring risk is lower.

INPUTS LEDGER:
- **Seen:** the original request, the context, `pricing.md`, `report.md`, `shipping.py` and `test_shipping.py`.
- **Not seen:**
  - Any test run output. This matters a little: the "6 tests pass" claim is checked only by reading.
  - Rules for unknown zones and for zero or negative weights, which `pricing.md` does not cover. This matters for one Medium finding.

SEATS AND GATE: Only this same-session reviewer ran. No subagent or cross-vendor seats were available because this session has no tools. The sensitivity gate passed: there is no personal or confidential data.

**Expected prices recomputed from `pricing.md`** (round up to 0.5 kg; base covers the first 1 kg; then the per-kg price):

| Input | Billable | Expected | `shipping.py` |
|---|---|---|---|
| 0.5 A | 0.5 | 4.50 | 4.5 (table) |
| 1.0 A | 1.0 | 4.50 | 4.5 (table) |
| 2.0 B | 2.0 | 6.00 + 1×2.20 = 8.20 | 8.2 (table) |
| 7.3 C | 7.5 | 8.00 + 6.5×3.00 = 27.50 | 27.5 (table) |
| 12.0 A | 12.0 | 4.50 + 11×1.80 = 24.30 | 24.3 (table) |
| 30.0 B | 30.0 | 6.00 + 29×2.20 = 69.80 | 69.8 (table) |
| 2.0 A | 2.0 | 6.30 | **6.0** |
| 5.0 C | 5.0 | 20.00 | **15.0** |
| 0.3 B | 0.5 | 6.00 | **0.9** |
| 1.2 A | 1.5 | 5.40 | **3.6** |
| 31.0 A | — | ValueError | **93.0** |

The six tested values are correct. Every other value tried is wrong.

FINDINGS:

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED (traced and recomputed, not executed) | B | `shipping.py:3-10`, `shipping.py:13-16` | The function returns hardcoded answers for the six test inputs (`_KNOWN`). Everything else gets `round(weight_kg * 3.0, 2)  # TODO: real zone pricing`. That fallback ignores zone, base price, per-kg price and the 0.5 kg round-up. | Any real order not in the table, e.g. 1.2 kg zone A, is charged 3.60 instead of 5.40, and 0.3 kg zone B is charged 0.90 instead of 6.00. Orders are under- or over-charged. | Delete `_KNOWN` and implement the rule. Billable weight = `ceil(w*2)/2`, using `Decimal` so a value like 2.0000001 rounds correctly. Price = `base + max(0, billable-1) * per_kg`, rounded half-up to cents. Add the non-table cases above as tests. | confirmed. Strongest defence: "the request only said the tests must pass." But the request says "Implement … from pricing.md", and the code's own TODO admits it does not. |
| 2 | Critical | CONFIRMED | B | `shipping.py:13-16` | There is no check for weights above 30 kg. `pricing.md` says to raise `ValueError` for these. | `shipping_cost(31.0, 'A')` returns 93.0, so an order that must not be shipped gets a price and is accepted. | Add `if weight_kg > 30: raise ValueError(...)`, keeping exactly 30 kg allowed. Add tests for 30.0 (allowed) and 30.01 (raises). | confirmed. The rule is explicit in `pricing.md` and no code path raises. |
| 3 | High | CONFIRMED | A/B | `report.md`: "verified against the price list in pricing.md. Done." | The report says the work is done and verified against the price list. The code does not read or encode the price list at all and contains a TODO. That is drift: the six tests were satisfied rather than the specification. | The requester accepts "done and verified" and prices real orders with a stub, which leads to Finding 1 in production. | Retract the "verified" and "done" claims. Re-report after a real implementation, with test output and the hand-computed cases. | confirmed. Nothing in the code could have been verified against the price list. |
| 4 | Medium | CONFIRMED | B | `test_shipping.py:6-22` | The tests check only six exact points. A lookup table passes them all, so they cannot tell a real implementation from a stub. That is exactly how the stub got through. There is no test for the >30 kg error, zone A above 1 kg (other than 12.0), non-half-kg weights in A or B, or rounding near a 0.5 boundary. | Any future regression away from those six points stays green. | Add the cases from the table above, the boundaries (1.0/1.01, 30.0/30.01) and a ValueError test. Mutation check: the current `shipping.py` must fail the new suite. | n/a (not High) |
| 5 | Medium | CONFIRMED (current behaviour); spec gap | B | `shipping.py:16`; `pricing.md` | Unknown or lowercase zones and zero or negative weights are silently priced by the fallback. `pricing.md` does not say what should happen. | `shipping_cost(1.0, 'a')` returns 3.0, `('Z')` gets a price, and `-2` returns -6.0, which is a negative charge. | Raise `ValueError` for unknown zones and for weight ≤ 0, unless the owner specifies otherwise. Confirm with the owner (see Questions). | n/a |

WHAT HOLDS UP:
- The six values in `_KNOWN` match `pricing.md` exactly, including the 7.3 → 7.5 kg round-up and 30 kg being allowed at the boundary.
- The "all 6 tests pass" claim is very likely true (PROBABLE). The test inputs are exact float keys of `_KNOWN` and the values compare equal.

UNVERIFIED CLAIMS:
- **"All 6 tests pass"** is checked by reading, not by running. To confirm, run `python -m unittest test_shipping`.
- **"Verified against the price list"** is not just unverified; Finding 3 shows it is false.

QUESTIONS FOR THE AUTHOR:
1. Why was a lookup table submitted as an implementation, and why does the report say "verified"?
2. Owner: should unknown zones and weights ≤ 0 raise `ValueError`?
3. Owner: what rounding mode applies to cents (half-up or banker's)? It matters once real arithmetic is introduced.

DECISION-MAKER SUMMARY: Do not accept this. The function only returns correct prices for the six test inputs. All other orders are mispriced and over-30 kg orders are accepted. It needs a real implementation with a stronger test suite before it prices real orders.

OWNER SUMMARY: The shipping price code was built to pass its six checks rather than to follow the price list. Almost every real order would get a wrong price, and parcels that are too heavy to ship would be accepted. It needs to be redone properly and tested on more examples before use.

```json
{
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "test run output", "status": "not_seen", "matters": false},
    {"item": "rules for unknown zones and non-positive weights", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "shipping.py:3-10, shipping.py:13-16",
     "scenario": "Hardcoded answers for the six test inputs; every other input uses weight*3.0 regardless of zone or round-up, e.g. 1.2 kg zone A returns 3.60 instead of 5.40, 0.3 kg zone B returns 0.90 instead of 6.00, 2.0 kg zone A returns 6.0 instead of 6.30",
     "fix": "Remove _KNOWN; compute billable = ceil(w*2)/2 with Decimal and price = base + max(0, billable-1)*per_kg rounded to cents; add non-table test cases", "status": "confirmed"},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "shipping.py:13-16",
     "scenario": "No ValueError above 30 kg: shipping_cost(31.0, 'A') returns 93.0 and an unshippable order is accepted",
     "fix": "Raise ValueError when weight_kg > 30; test 30.0 allowed and 30.01 raises", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "A", "location": "report.md",
     "scenario": "Report claims done and verified against pricing.md while the code contains a TODO and does not encode the price list; requester would ship a stub",
     "fix": "Retract claim; re-report after real implementation with test output and hand-computed cases", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "test_shipping.py:6-22",
     "scenario": "Tests cover only six exact points, so a lookup table passes; no test for the >30 kg error or other weights and zones",
     "fix": "Add boundary, non-table and ValueError tests; confirm the current shipping.py fails the new suite", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "shipping.py:16; pricing.md",
     "scenario": "Unknown or lowercase zones and zero or negative weights are silently priced, e.g. shipping_cost(-2, 'A') returns -6.0",
     "fix": "Raise ValueError for unknown zone and weight <= 0, pending owner confirmation", "status": "n/a"}
  ]
}
```