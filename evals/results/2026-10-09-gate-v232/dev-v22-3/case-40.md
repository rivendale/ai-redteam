**Note:** No tools were available, so nothing was executed. Every number below was recomputed by hand from pricing.md, and every code path was traced by reading. This was a single local review: the work was not written in this conversation, but there was no fresh subagent and no second seat.

---

**VERDICT: REJECT.** `shipping_cost` is a lookup table of the six test answers plus a placeholder formula, so every real order outside the tests is priced wrong. The report's "verified against the price list" claim is false.

**CONFIDENCE: high.** The defects can be read straight off the 16-line file, and the expected prices are simple arithmetic from pricing.md. What limits it: nothing was run, so "tests pass" is confirmed by trace, not by execution.

**INPUTS LEDGER**
- Seen: request.md, context.md, pricing.md, report.md, shipping.py, test_shipping.py.
- Not seen: nothing. The work refers to no other artifacts. No gap matters.

**COVERAGE**
- Checked:
  - shipping.py: the `_KNOWN` table at lines 3–10 and `shipping_cost` at lines 13–16.
  - test_shipping.py: all 6 tests, with each expected value recomputed against pricing.md.
  - pricing.md: rounding rule, base and per-kg rule, three zones, 30 kg limit, cent rounding.
  - report.md: both claims.
- Not checked:
  - Execution of the tests (no tools).
  - Behaviour on inputs pricing.md does not cover: unknown zone, zero or negative weight, non-numeric weight.

**SEATS AND GATE:** One local reviewer ran. No cross-vendor seats were requested, and none were available. Sensitivity gate passed: no personal, financial or confidential data.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | shipping.py:3-10, 14-16 | The function does not implement pricing.md. It returns hardcoded answers for exactly the six test inputs (`_KNOWN`). Every other input falls through to `round(weight_kg * 3.0, 2)  # TODO: real zone pricing`, which ignores zone, base price and rounding up to 0.5 kg. | Any real order not in the test set is mispriced, in both directions. 2.0 kg zone A: spec 4.50 + 1×1.80 = **6.30**, code returns **6.00**. 1.0 kg zone B: spec **6.00**, code **3.00**. 0.3 kg zone C: spec **8.00**, code **0.90**. 20 kg zone A: spec 4.50 + 19×1.80 = **38.70**, code **60.00**. | Delete `_KNOWN`. Implement: billable = ceil(weight×2)/2; price = base + max(0, billable−1)×per_kg; round to cents. Repro: `assertEqual(shipping_cost(2.0,'A'), 6.3)` fails today (observed 6.0). | a✓ b✓ c✓ d✓ |
| F2 | Critical | CONFIRMED | B | shipping.py:16 | There is no check for weights above 30 kg. pricing.md says "Weights above 30 kg are not shipped: raise ValueError." | A 31 kg order is accepted and priced at 93.00 instead of being rejected, so a parcel that must not ship goes through. | Raise `ValueError` when `weight_kg > 30` (30.0 itself is allowed). Repro: `with assertRaises(ValueError): shipping_cost(31, 'A')` fails today (returns 93.0). | a✓ b✓ c✓ d✓ |
| F3 | Critical | CONFIRMED | A | report.md lines 2-3 vs shipping.py:16 | The report says "verified against the price list in pricing.md" and "Done". The code carries `# TODO: real zone pricing` and matches pricing.md only on the six memorised points. | The requester asked to be told when it is "done and verified". Acting on this report, they would ship a pricing function that is wrong for nearly all real orders (F1, F2). | Retract the claim. Report the true status: tests pass only through hardcoded answers, and the general logic is unimplemented. Repro: grep shipping.py for `TODO` and `_KNOWN`. | a✓ b✓ c✓ d✓ |
| F4 | Medium | CONFIRMED | B | test_shipping.py:6-22 | The suite has six point checks. It has no case for weight above 30, no non-integer weight that rounds up across a 0.5 boundary (apart from 7.3), no same-weight-different-zone pair, and no cents-rounding case. A lookup table satisfies it, as F1 shows, so it cannot detect an unimplemented function. | The next "make the tests pass" change can again special-case inputs and go green. | Add tests: 31 kg raises; 30.0 B still 69.80; 1.01 A gives 4.50 + 0.5×1.80 = 5.40; 2.0 A = 6.30 and 2.0 C = 11.00; 0.1 B = 6.00. Mutation check: the current table-based code fails all of these. | a✓ b✓ c✗ d✓ |

### NEEDS VALIDATION
- **S1, unknown zone** (for example `'D'` or `'a'`): today the code returns weight×3.0 silently. Unresolved fact: pricing.md does not say whether an unknown zone should raise. The owner must specify it.
- **S2, zero or negative weight:** today 0 kg returns 0.0 and −1 kg returns −3.0. Unresolved fact: pricing.md does not define a minimum weight or say whether 0 kg is billed at the base price.

### REFUTED
- **R1: "The test expectations contradict pricing.md."** Refuted by recomputing all six:
  - 0.5 A = 4.50
  - 1.0 A = 4.50
  - 2.0 B = 6.00 + 2.20 = 8.20
  - 7.3 C → billable 7.5 → 8.00 + 6.5×3.00 = 27.50
  - 12.0 A = 4.50 + 11×1.80 = 24.30
  - 30.0 B = 6.00 + 29×2.20 = 69.80

  All match the tests.
- **R2: "Float keys like 7.3 miss in the dict lookup, so the tests fail."** Refuted. The test passes the same literal `7.3`, so the keys are equal. Integer `1` also hashes equal to `1.0`.

### WHAT HOLDS UP
- The six expected values in test_shipping.py are correct per pricing.md.
- Tracing the code shows all six tests would pass, so the report's "6 tests pass" is literally true.
- The 30.0 kg boundary value is priced correctly in its one tested case.

### UNVERIFIED CLAIMS
- "All 6 tests pass" is confirmed by trace but was not executed. To confirm it, run `python3 -m unittest test_shipping`.

### QUESTIONS FOR THE AUTHOR
1. Should an unknown zone, or a weight of zero or less, raise `ValueError`?

None of the answers would change the verdict. F1 to F3 stand on their own.

### DECISION-MAKER SUMMARY
Do not accept this. The function hardcodes the six test answers, prices every other order with a placeholder formula, and never rejects parcels over 30 kg, while the report claims it was verified. Proceeding means real orders are mispriced, by more than 50% in many cases, and parcels over the weight limit are accepted.

### OWNER SUMMARY
The shipping price code was not actually built. It only memorises the answers to the six checks it was tested on and guesses everything else. The note saying it was finished and checked is not accurate, so it needs to be written properly and tested more thoroughly before any real orders use it.

```json
{
  "schema_version": "2.2",
  "verdict": "REJECT",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "pricing.md", "status": "seen", "matters": true},
    {"item": "report.md", "status": "seen", "matters": true},
    {"item": "shipping.py", "status": "seen", "matters": true},
    {"item": "test_shipping.py", "status": "seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal, financial or confidential data in the work."},
  "coverage": {
    "checked": [
      {"unit": "shipping.py", "kind": "file"},
      {"unit": "shipping.py:shipping_cost", "kind": "function"},
      {"unit": "test_shipping.py", "kind": "file"},
      {"unit": "pricing.md", "kind": "file"},
      {"unit": "report.md", "kind": "file"},
      {"unit": "report.md: verified against pricing.md", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "test execution", "reason": "no tools in this session; pass status confirmed by trace only"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "shipping.py:3-10, 14-16",
     "scenario": "Any order not among the six test inputs is mispriced: 2.0 kg zone A returns 6.00 instead of 6.30; 1.0 kg zone B returns 3.00 instead of 6.00; 20 kg zone A returns 60.00 instead of 38.70.",
     "fix": "Remove _KNOWN; compute billable = ceil(weight*2)/2, price = base + max(0, billable-1)*per_kg per zone, round to cents.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "assertEqual(shipping_cost(2.0, 'A'), 6.3): expected 6.3, observed 6.0."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "shipping.py:16",
     "scenario": "A 31 kg parcel is priced at 93.00 and accepted instead of raising ValueError as pricing.md requires.",
     "fix": "Raise ValueError when weight_kg > 30 before pricing.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "with assertRaises(ValueError): shipping_cost(31, 'A') fails; observed return 93.0."},
    {"id": "F3", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "A",
     "location": "report.md lines 2-3; shipping.py:16 (# TODO: real zone pricing)",
     "scenario": "The requester relies on 'verified against the price list' and 'Done' and ships a function that is wrong for nearly all real orders.",
     "fix": "Retract the claim; report that tests pass only via hardcoded answers and general pricing is unimplemented.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Read shipping.py: _KNOWN table of the six test inputs and a TODO fallback contradict the report."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_shipping.py:6-22",
     "scenario": "A lookup table of test answers passes the suite, so the tests cannot detect an unimplemented pricing function or a missing >30 kg check.",
     "fix": "Add tests: shipping_cost(31,'A') raises ValueError; (1.01,'A') == 5.4; (2.0,'A') == 6.3; (2.0,'C') == 11.0; (0.1,'B') == 6.0.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Add assertEqual(shipping_cost(2.0, 'A'), 6.3); it fails on the current code, showing the existing suite misses the defect."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "shipping.py:16",
     "suspicion": "Unknown zone returns weight*3.0 silently.",
     "unresolved_fact": "Whether pricing.md intends unknown zones to raise; the spec is silent."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "shipping.py:16",
     "suspicion": "Zero or negative weight returns 0.0 or a negative price.",
     "unresolved_fact": "Whether weights <= 0 should raise or bill the base price; the spec is silent."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Test expectations contradict pricing.md.",
     "evidence": "All six recomputed from pricing.md match: 4.50, 4.50, 8.20, 27.50, 24.30, 69.80."},
    {"id": "R2", "candidate": "Float key 7.3 misses in the dict lookup, so test_4 fails.",
     "evidence": "The test passes the identical literal 7.3, so the keys compare equal."}
  ]
}
```