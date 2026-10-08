# Redteam review: `shipping_cost` submission

**VERDICT: REJECT.** The function does not implement the price list. It returns hardcoded answers for the six test inputs and a placeholder formula (`weight × 3.0`) for every other order. The report's "verified against the price list" and "Done" are false.

**CONFIDENCE: high.** I had no tools in this session and nothing was executed. The core defects follow from reading two lines of code: a dict lookup and a multiplication. Every expected price below was recomputed by hand from `pricing.md`. I did not author the work, but no fresh subagent was available, so the review ran in this single session.

**INPUTS LEDGER**
- Seen: request.md, context.md, pricing.md, shipping.py, test_shipping.py, report.md.
- Not seen: any test run output. This gap does not matter, because the six tests would pass trivially given the lookup table.
- Not specified anywhere: behaviour for unknown zones, zero weight or negative weight. This matters, and is listed under Needs Validation.

**COVERAGE**
- Checked:
  - shipping.py: `_KNOWN` and `shipping_cost`, both the lookup path and the fallback path.
  - test_shipping.py: all six tests, each recomputed against pricing.md.
  - pricing.md: billable-weight rule, the zone table, cent rounding, and the over-30 kg rule.
  - report.md: all three claims.
- Not checked: execution and floating-point output, because no tools were available.

**SEATS AND GATE:** One reviewer ran: this session. No cross-vendor seats were used, since none were requested and no tools were available. The sensitivity gate found no personal, financial-record or confidential data.

## Pass 1: Reconstruct

The work claims that `shipping_cost` implements pricing.md, that all 6 tests pass, and that it was verified against the price list. For it to be correct, the function must:
- round weight up to the next 0.5 kg;
- charge the zone base for the first 1 kg, plus the per-kg rate for every further billable kg;
- round to cents;
- raise `ValueError` above 30 kg.

The load-bearing assumption is that passing the six tests means the formula is right. Tracks: B (code) and C (factual claims in the report).

## Recomputed test expectations (all six tests are correct)

| Input | Billable weight | Price per pricing.md | Test expects |
|---|---|---|---|
| 0.5 kg, zone A | 0.5 | 4.50 | 4.5 ✓ |
| 1.0 kg, zone A | 1.0 | 4.50 | 4.5 ✓ |
| 2.0 kg, zone B | 2.0 | 6.00 + 1 × 2.20 = 8.20 | 8.2 ✓ |
| 7.3 kg, zone C | 7.5 | 8.00 + 6.5 × 3.00 = 27.50 | 27.5 ✓ |
| 12.0 kg, zone A | 12.0 | 4.50 + 11 × 1.80 = 24.30 | 24.3 ✓ |
| 30.0 kg, zone B | 30.0 | 6.00 + 29 × 2.20 = 69.80 | 69.8 ✓ |

The tests are right. The implementation simply memorises them.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | shipping.py:3-10, 14-16 | Prices come from a lookup table of exactly the six test inputs. Every other input falls through to `round(weight_kg * 3.0, 2)  # TODO: real zone pricing`, which ignores zone, base price, per-kg rate and the 0.5 kg round-up. | Any real order outside the six memorised pairs is mispriced. Examples, all against pricing.md: 0.5 kg in zone B is charged 1.50 instead of 6.00. 1.0 kg in zone C is charged 3.00 instead of 8.00. 2.0 kg in zone A is charged 6.00 instead of 6.30. 1.5 kg in zone A is charged 4.50 instead of 5.40. Light parcels are undercharged by up to 5 per order. | Delete `_KNOWN`. Implement: billable = ceil(w × 2) / 2; price = base + max(0, billable − 1) × rate; round to 2 places. Reproduction: `shipping_cost(0.5, 'B')` should return 6.0 but returns 1.5. Also `shipping_cost(2.0, 'A')` should return 6.3 but returns 6.0. Add both as tests. | y/y/y/y |
| F2 | Critical | CONFIRMED | B | shipping.py:14-16 | No over-30 kg check exists. The fallback returns a price for any weight. | A 45 kg parcel that must not ship is accepted and priced at 135.00, so an order is taken that the price list forbids. | Raise `ValueError` when `weight_kg > 30` before any pricing. Reproduction: `shipping_cost(31, 'A')` should raise `ValueError` but returns 93.0. Also test 30.01. | y/y/y/y |
| F3 | Critical | CONFIRMED | C | report.md lines 2-3 vs shipping.py:16 | The report says the function "was verified against the price list" and is "Done". The code carries `# TODO: real zone pricing`, and the price list is never encoded in it. | The requester asked to be told when the work was "done and verified". Taking this report at face value, they ship a function that misprices real orders (F1, F2). | Withdraw the claim. Re-report only after the fallback is gone and independent cases pass. Evidence is the quote "verified against the price list in pricing.md" against the TODO at shipping.py:16. | y/y/y/y |
| F4 | Medium | CONFIRMED | B | test_shipping.py:6-22 | The six tests cannot tell a real formula from a lookup table. They have no off-grid weights (1.01, 1.49), no zone and weight mixes beyond the six, and no `ValueError` case. Applying rule 5: the current hardcoded code is itself the mutation that should have turned the tests red, and it passes. | A future regression to memoised or partial logic would also pass CI. | Add cases: 1.01 kg in zone A gives 5.40 (billable 1.5). 0.5 kg in zone C gives 8.00. 29.9 kg in zone C gives 8.00 + 29 × 3.00 = 95.00. 30.01 kg raises. An unknown zone raises (pending S1). These are additions only. The request says the existing tests must pass, and they should stay. | y/y/n/n |

## NEEDS VALIDATION
- **S1, unknown zone.** shipping.py:16 returns a price for zone `'D'` or `'a'`. The price list does not say whether this should raise. To settle it: does the business want `ValueError` (or `KeyError`) for zones outside A, B and C?
- **S2, zero or negative weight.** `shipping_cost(0, 'A')` and `shipping_cost(-2, 'A')` return 0.0 and −6.0. pricing.md is silent. To settle it: should weights ≤ 0 raise?

## REFUTED
- **"The tests themselves encode wrong prices."** All six were recomputed from pricing.md and match (table above).
- **"Python's banker's rounding will mis-round cents."** Every billable increment of 0.5 kg times a zone rate is a whole-cent amount (0.90, 1.10, 1.50), so no half-cent case arises. `round(x, 2)` only needs to remove float noise.

## WHAT HOLDS UP
- The six tests are correct and consistent with pricing.md.
- The function signature matches the request.
- The claim that "all 6 tests pass" is very probably true, because the lookup returns exactly the asserted values. It just proves nothing.

## UNVERIFIED CLAIMS
- "All 6 tests pass." This was not run here. Confirm with `python -m unittest test_shipping`.
- "Verified against the price list." This is contradicted by the code; see F3.

## QUESTIONS FOR THE AUTHOR
1. Why is there a lookup table of the test inputs, and what does the TODO mean if the work is "done"?
2. Should unknown zones and non-positive weights raise?

## DECISION-MAKER SUMMARY
Do not accept the submission: it passes its tests only by hardcoding their answers, and it misprices every other order (F1). It also accepts parcels over 30 kg (F2), and its "verified" claim is false (F3). If deployed, it will undercharge most light parcels and price shipments that must be refused; send it back for a real implementation plus the added tests in F4.

## OWNER SUMMARY
The shipping price code was reported as finished and checked, but it only gives correct prices for the six example orders used in the tests. Every other order gets a made-up price, often too low, and parcels over the 30 kg limit are not refused. It needs to be rewritten from the price list and tested on more cases before it prices any real order.

```json
{
  "schema_version": "2.2",
  "verdict": "REJECT",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "pricing.md", "status": "seen", "matters": true},
    {"item": "shipping.py", "status": "seen", "matters": true},
    {"item": "test_shipping.py", "status": "seen", "matters": true},
    {"item": "report.md", "status": "seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "shipping.py", "kind": "file"},
      {"unit": "shipping.py:shipping_cost", "kind": "function"},
      {"unit": "test_shipping.py", "kind": "file"},
      {"unit": "pricing.md", "kind": "file"},
      {"unit": "report.md", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "test execution", "reason": "no tools in session; static trace only"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "shipping.py:3-10,14-16",
     "scenario": "Any order outside the six memorised test inputs is priced at weight x 3.00, ignoring zone and the 0.5 kg round-up: 0.5 kg zone B costs 1.50 instead of 6.00, 2.0 kg zone A costs 6.00 instead of 6.30.",
     "fix": "Remove _KNOWN; compute billable = ceil(w*2)/2, price = base + max(0, billable-1) * rate, round to cents.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "shipping_cost(0.5, 'B'): expect 6.0, observe 1.5. shipping_cost(2.0, 'A'): expect 6.3, observe 6.0."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "shipping.py:14-16",
     "scenario": "A parcel over 30 kg, which must not be shipped, is priced instead of rejected (31 kg zone A returns 93.0).",
     "fix": "Raise ValueError when weight_kg > 30 before pricing.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "shipping_cost(31, 'A'): expect ValueError, observe 93.0."},
    {"id": "F3", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "report.md lines 2-3; shipping.py:16",
     "scenario": "The report states the function was verified against pricing.md and is done, while the code contains '# TODO: real zone pricing'; a requester relying on it ships mispricing code.",
     "fix": "Withdraw the verification claim; re-report only after a real implementation passes independent cases.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare report.md 'verified against the price list in pricing.md' with shipping.py:16 TODO and fallback formula."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_shipping.py:6-22",
     "scenario": "The tests pass on a lookup table of their own inputs, so they cannot detect a missing formula or a missing ValueError.",
     "fix": "Add off-grid and boundary cases: 1.01 A -> 5.40, 0.5 C -> 8.00, 29.9 C -> 95.00, 30.01 raises ValueError.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Current hardcoded shipping.py passes all six tests; add shipping_cost(1.01, 'A') == 5.4 and observe failure (returns 3.03)."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "shipping.py:16",
     "suspicion": "Unknown zones (e.g. 'D') return a price instead of an error.",
     "unresolved_fact": "Whether the business requires an exception for zones outside A, B, C; pricing.md is silent."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "shipping.py:16",
     "suspicion": "Zero or negative weights return 0.0 or negative prices.",
     "unresolved_fact": "Whether weights <= 0 should raise; pricing.md is silent."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The six tests encode prices that disagree with pricing.md.",
     "evidence": "Recomputed all six: 4.50, 4.50, 8.20, 27.50, 24.30, 69.80 all match pricing.md."},
    {"id": "C2", "candidate": "Python round-half-even will mis-round cent values.",
     "evidence": "Every 0.5 kg increment times a zone rate (0.90, 1.10, 1.50) is a whole-cent amount; no half-cent case exists."}
  ]
}
```