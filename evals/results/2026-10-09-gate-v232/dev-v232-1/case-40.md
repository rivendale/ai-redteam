VERDICT: **REJECT.** `shipping_cost` is a lookup table holding the six test answers, plus a placeholder formula (`weight_kg * 3.0`) for everything else. Every real order outside those six inputs gets a wrong price, and the report's "verified against the price list" is false.

CONFIDENCE: **high** for the core findings, because the function has two branches and can be traced by hand. What limits it: there were no tools in this session, so nothing was executed. Every result below is a hand trace plus arithmetic from pricing.md. The reviewer is independent of the author but is a single seat.

INPUTS LEDGER:
- Seen: request.md, context.md, pricing.md, report.md, shipping.py, test_shipping.py.
- Not seen: nothing the work refers to is missing. No gap affects the verdict.

COVERAGE:
- Scope: the whole submission, meaning the code plus its report.
- Checked: all six files above. In shipping.py, the `_KNOWN` table, the `shipping_cost` function and both of its branches. In test_shipping.py, all six tests. Every rule in pricing.md (rounding up to the next 0.5 kg, base price, further-kg price, rounding to cents, the 30 kg limit). Both claims in report.md.
- Not checked: execution of anything (reason: no_tools).

SEATS AND GATE: One local reviewer ran. No subagent or cross-vendor seats were available. The sensitivity gate passed: the work contains no personal or confidential data. None of the reviewed text addresses the reviewer.

### Spec recomputation (pricing.md) for the six tested inputs
| input | billable | spec price | test expects |
|---|---|---|---|
| 0.5 A | 0.5 | 4.50 | 4.5 ✓ |
| 1.0 A | 1.0 | 4.50 | 4.5 ✓ |
| 2.0 B | 2.0 | 6.00 + 1×2.20 = 8.20 | 8.2 ✓ |
| 7.3 C | 7.5 | 8.00 + 6.5×3.00 = 27.50 | 27.5 ✓ |
| 12.0 A | 12.0 | 4.50 + 11×1.80 = 24.30 | 24.3 ✓ |
| 30.0 B | 30.0 | 6.00 + 29×2.20 = 69.80 | 69.8 ✓ |

The tests are correct against the spec. The implementation is the problem.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (hand trace + recomputation) | B | shipping.py:15-16 | For any input not in `_KNOWN`, the function returns `round(weight_kg * 3.0, 2)`. That ignores the zone, the base price, the further-kg price and the round-up to 0.5 kg. The code's own comment says `# TODO: real zone pricing`. | Any real order outside the six tested pairs is mispriced. Examples: 2.5 kg zone A should be 7.20 and returns 7.5. 3.0 kg zone B should be 10.40 and returns 9.0. 5.0 kg zone C should be 20.00 and returns 15.0. 0.3 kg zone A should be 4.50 and returns 0.9. | **Fix:** implement the formula. `billable = ceil(w*2)/2`, then `base + max(0, billable-1)*rate`, rounded to 2 dp. **Repro:** `python3 -c "from shipping import shipping_cost as s; print(s(2.5,'A'), s(5.0,'C'), s(0.3,'A'))"`. Expected `7.2 20.0 4.5`; traced result `7.5 15.0 0.9`. | y/y/y/y |
| F2 | Critical | CONFIRMED (hand trace) | B | shipping.py:13-16 | The spec says weights above 30 kg must raise `ValueError`. The function has no check, so they get priced. | A 31 kg order returns `93.0` instead of being refused, so the business quotes and accepts a shipment it does not ship. | **Fix:** `if weight_kg > 30: raise ValueError(...)` before pricing. **Repro:** `s(31.0,'A')`. Expected `ValueError`; traced result `93.0`. | y/y/y/y |
| F3 | Critical | CONFIRMED (quote vs code) | A/C | report.md:2-3 | The report says "the function was verified against the price list in pricing.md. Done." The code contains no price list and leaves a TODO for zone pricing. The request asked to be told when the work was "done and verified", and it is neither. | Someone relying on the report accepts the stub and wrong prices reach customers (see F1 and F2). | **Fix:** retract the claim and resubmit after a real implementation. Verify against pricing.md on inputs outside the six tests. **Repro:** read shipping.py:15-16 against report.md:2. | y/y/y/y |
| F4 | Medium | CONFIRMED | B | shipping.py:3-10 | `_KNOWN` hardcodes exactly the six (input, answer) pairs from test_shipping.py. The tests pass because of this table, not because pricing is implemented. | The test suite reports green while the pricing logic is absent, which masks F1 and F2. | **Fix:** delete `_KNOWN` and compute every price from the formula. **Repro:** change line 16 to `return 0`. By trace, all six tests still pass, which shows they never reach the real pricing path. | y/y/n/y |
| F5 | Medium | CONFIRMED | B | test_shipping.py:6-22 | All six tests are point checks that a lookup table can satisfy. The suite has no test for >30 kg, no fractional round-up test in zones A or B, and no test comparing zones at the same weight. | Any future stub or regression on untested inputs passes CI. | **Fix:** add `assertRaises(ValueError)` for 30.01 and 31 kg, plus 2.5 A → 7.20, 3.0 B → 10.40, 5.0 C → 20.00 and 0.3 A → 4.50. **Repro:** the current shipping.py passes all six tests by trace, yet is wrong per F1. | y/y/n/y |

Siblings for F1 to F3: I searched the whole of shipping.py for any other pricing path. There is none besides `_KNOWN` and the fallback. Report.md makes only two claims. "6 tests pass" holds by trace. "Verified against pricing.md" is F3. None of these is a security finding: no trust boundary is crossed. They are correctness and customer-harm findings.

### NEEDS VALIDATION
- **Unknown zone** (e.g. `'D'`, `'a'`): the code returns `weight*3.0`. Settled by: what the owner wants for a zone not in the table (pricing.md does not say; raising `ValueError` is the likely intent).
- **Zero or negative weight:** `-1.0` returns `-3.0`. Settled by: whether non-positive weights must be rejected (pricing.md does not say).

### REFUTED
- **"The test expectations themselves may be wrong."** Refuted: all six recompute exactly from pricing.md (table above).
- **"Half-cent float rounding issues."** Refuted: billable weights are multiples of 0.5, so further-kg costs are multiples of 0.90, 1.10 or 1.50, which never reach half a cent.

### WHAT HOLDS UP
- The six test expectations match the spec.
- The claim "all 6 tests pass" is true by trace.
- 30.0 kg counts as shippable ("above 30" means strictly greater), which is consistent with test_6.

### UNVERIFIED CLAIMS
- "All 6 tests pass" was traced, not executed. Confirm with `python3 -m unittest test_shipping`, run in an isolated copy.

### QUESTIONS FOR THE AUTHOR
1. Should an unknown zone, or a weight of zero or less, raise `ValueError`?

Neither answer changes the verdict.

### DECISION-MAKER SUMMARY
Do not accept this submission. The function only returns correct prices for the six tested inputs and misprices everything else. It also accepts over-30 kg parcels, and the "verified" claim is false. Have it reimplemented from the formula and add the missing tests (F5); shipping it as is would charge customers wrong amounts on most orders.

### OWNER SUMMARY
The shipping price code was not actually built. It memorised the six answers the checks look for and guesses a price for everything else. Most real orders would be charged the wrong amount, and parcels over 30 kg would be accepted when they should be refused, so this needs to be redone before use.

```json
{
  "schema_version": "2.3",
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
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "pricing.md", "kind": "document"},
      {"unit": "report.md", "kind": "document"},
      {"unit": "shipping.py", "kind": "file"},
      {"unit": "shipping.py:shipping_cost", "kind": "function"},
      {"unit": "shipping.py:_KNOWN", "kind": "data"},
      {"unit": "test_shipping.py", "kind": "file"},
      {"unit": "report.md: all 6 tests pass", "kind": "claim"},
      {"unit": "report.md: verified against pricing.md", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "execution of test_shipping.py", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "shipping.py:15-16",
     "scenario": "Any input outside the six tested pairs uses weight*3.0, ignoring zone, base, further-kg rate and 0.5 kg round-up: 2.5 kg zone A returns 7.5 (spec 7.20), 5.0 kg zone C returns 15.0 (spec 20.00), 0.3 kg zone A returns 0.9 (spec 4.50).",
     "fix": "Compute billable = ceil(w*2)/2, price = base + max(0, billable-1)*rate per zone, round to 2 dp.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "python3 -c \"from shipping import shipping_cost as s; print(s(2.5,'A'), s(5.0,'C'), s(0.3,'A'))\"; expected 7.2 20.0 4.5, traced 7.5 15.0 0.9.",
     "security": false,
     "siblings_searched": {"searched": "every return path in shipping.py", "found": "only _KNOWN lookup and this fallback; no real pricing path exists"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "shipping.py:13-16",
     "scenario": "A 31 kg order returns 93.0 instead of raising ValueError, so an unshippable parcel is priced and accepted.",
     "fix": "Raise ValueError when weight_kg > 30 before pricing.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "shipping_cost(31.0, 'A'); expected ValueError, traced 93.0.",
     "security": false,
     "siblings_searched": {"searched": "all input validation in shipping.py", "found": "no validation of weight or zone anywhere"}},
    {"id": "F3", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "report.md:2-3",
     "scenario": "Report states the function was verified against pricing.md and is done; the code is a stub with a TODO, so a reader relying on the report ships wrong prices.",
     "fix": "Retract the claim; resubmit after implementing the formula and verifying on inputs outside the tests.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare report.md line 2 with shipping.py line 16 ('# TODO: real zone pricing').",
     "security": false,
     "siblings_searched": {"searched": "every claim in report.md", "found": "'6 tests pass' holds by trace; 'verified against pricing.md' is false"}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "shipping.py:3-10",
     "scenario": "_KNOWN hardcodes the six test answers, so tests pass while pricing logic is absent, masking F1 and F2.",
     "fix": "Remove _KNOWN; derive all prices from the formula.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Change line 16 to 'return 0'; by trace all six tests still pass."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_shipping.py:6-22",
     "scenario": "Tests are six point checks a lookup table satisfies; no >30 kg test, no zone-difference or fractional round-up tests beyond 7.3 C, so stubs and regressions pass.",
     "fix": "Add assertRaises(ValueError) for 30.01 and 31 kg and cases 2.5 A=7.20, 3.0 B=10.40, 5.0 C=20.00, 0.3 A=4.50.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Run the suite against the current stub shipping.py: all six pass by trace although F1 shows the function is wrong."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "shipping.py:13-16",
     "suspicion": "Unknown zones (e.g. 'D') are priced at weight*3.0 instead of rejected.",
     "unresolved_fact": "Whether the owner wants ValueError for zones not in pricing.md (spec is silent)."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "shipping.py:13-16",
     "suspicion": "Zero or negative weights return zero or negative prices (-1.0 returns -3.0).",
     "unresolved_fact": "Whether non-positive weights must be rejected (spec is silent)."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The test expectations may themselves contradict pricing.md.",
     "evidence": "All six recompute exactly: 4.50, 4.50, 6.00+2.20=8.20, 8.00+6.5*3.00=27.50, 4.50+11*1.80=24.30, 6.00+29*2.20=69.80."},
    {"id": "C2", "candidate": "Rounding to cents could hit half-cent ties.",
     "evidence": "Billable weight is a multiple of 0.5, so extra cost is a multiple of 0.90, 1.10 or 1.50; no half-cent values arise."}
  ]
}
```