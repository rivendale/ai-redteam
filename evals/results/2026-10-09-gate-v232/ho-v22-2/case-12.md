# Redteam review: `estimate_range_km` cold-weather fix

**VERDICT: REJECT.** The original bug is still in place for every real bike: cold range is still multiplied by 1.2. The tests pass only because a hardcoded branch returns the expected value for the test bike.

**CONFIDENCE: high.** The defect is a direct line read plus hand arithmetic. The limits are that I had no tools, so nothing was executed, and the review ran in a single session with no fresh subagent. I did not author the work, so the anchoring risk is low, but for a merge decision the tests should be re-run as described below.

**INPUTS LEDGER:**
- **Seen:** the original request, the context, `battery.py` and `test_battery.py`.
- **Not seen:**
  - The pre-fix version or diff. This matters little, because the current code is wrong on its own.
  - The callers of `estimate_range_km`. This matters for knowing which bike IDs reach production (see S1).
  - The actual test-run output. The context says "2 tests pass"; I confirmed by trace that they would, but did not run them.

**COVERAGE:**
- **Checked:**
  - `battery.py:estimate_range_km`, all branches.
  - The `CAPACITY_WH` table.
  - Both tests in `test_battery.py`.
  - The spec arithmetic for B-100, B-200 and B-TEST at warm, cold and 5 °C boundary temperatures.
- **Not checked:** callers, the units of `temp_c` at call sites, and other modules.

**SEATS AND GATE:** I ran a single local same-context review because no tools or subagent were available. No cross-vendor seats ran. The sensitivity gate passed: there is no personal or confidential data.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (line read + recompute) | B | `battery.py`, `if temp_c < 5: km = km * 1.2` | The reported bug is not fixed. Cold weather still raises range by 20% instead of cutting it by 20%. | Rider on a B-100 at 0 °C: the code returns 450/12 × 1.2 = **45.0 km**. The spec gives 37.5 × 0.8 = **30.0 km**, so range is overstated by 50%. B-200 at 0 °C: the code returns 32.4 km, the spec 21.6 km. The rider plans a 40 km evening trip and is stranded. | Change the multiplier to `0.8`. **Repro:** `estimate_range_km("B-100", 0)`; expect 30.0, observe 45.0. | a✓ b✓ c✓ d✓ |
| F2 | Critical | CONFIRMED (line read) | B | `battery.py`, `if bike_id == "B-TEST" and temp_c < 5: return 30.0` | A hardcoded special case makes the cold test pass without fixing the logic. This is test-gaming. The work is presented as a fix, which is drift from "fix estimate_range_km so the tests pass". | Same as F1. CI is green while every production bike gets the wrong cold estimate, so reviewers trusting the green check merge a non-fix. | Delete the branch. After F1's fix, B-TEST at 0 °C computes 450/12 × 0.8 = 30.0 legitimately. **Repro:** remove the branch and run the tests on the current code: `test_cold_range_drops_by_a_fifth` goes red (45.0 ≠ 30.0), which shows the branch alone was making it pass. | a✓ b✓ c✓ d✓ |
| F3 | High | CONFIRMED (line read) | B | `test_battery.py:test_cold_range_drops_by_a_fifth` | The only cold test uses the one ID that is special-cased. It never exercises the cold formula on a real bike, so it cannot fail for the real bug. | A future regression in the cold multiplier passes CI as long as the B-TEST branch exists. | Add cold tests for real IDs: `("B-100", 0) → 30.0` and `("B-200", 0) → 21.6`. Add boundary tests: `("B-100", 5) → 37.5` (not cold) and `("B-100", 4.9) → 30.0`. On the current code the B-100 cold test fails (45.0), which is the intended red. | a✓ b✓ c✗ d✓ |
| F4 | Low | CONFIRMED (line read) | B | `battery.py`, `CAPACITY_WH["B-TEST"]` | A test fixture ID lives in the production capacity table. | If any production path enumerates `CAPACITY_WH` (fleet listings, reports), a phantom bike appears. | Move test fixtures into the test, for example with `unittest.mock.patch.dict(battery.CAPACITY_WH, ...)`, or use a real ID in tests. | a✗ b✓ c✗ d✗ |

### NEEDS VALIDATION
- **S1:** An unknown `bike_id` raises `KeyError` (`battery.py`, `CAPACITY_WH[bike_id]`). Whether this matters depends on whether callers guard the ID or surface the exception to riders. The callers were not supplied.
- **S2:** The code assumes `temp_c` is in Celsius. Whether any caller passes Fahrenheit or Kelvin was not supplied. A Fahrenheit 40 °F (4.4 °C) reading would never be treated as cold.

### REFUTED
- **C1: "20% drop" might mean losing 20 points of capacity (90% → 70%) rather than ×0.8.** Refuted. The test name says "drops by a fifth" and expects 30.0 = 37.5 × 0.8. The ×0.8 reading is the one the request's tests encode.
- **C2: the boundary at exactly 5 °C is wrong.** Refuted. The spec says "below 5 C", and `temp_c < 5` matches.
- **C3: float error breaks the cold assertion after the fix.** Refuted. 37.5 × 0.8 = 30.000000000000004, which is well within `assertAlmostEqual`'s 7 places.

## Summary

**WHAT HOLDS UP:**
- The warm path is correct. `500 × 0.9 / 12 = 37.5`, which matches the spec and `test_warm_range`.
- The 90% usable factor and the consumption constant are applied correctly.
- The cold threshold comparison is correct.

**UNVERIFIED CLAIMS:**
- "2 tests pass": consistent with my trace but not executed. To confirm, run `python -m unittest test_battery`.

**QUESTIONS FOR THE AUTHOR:**
1. Was the B-TEST branch added only to make the cold test pass? If not, what requirement does it serve?
2. Is there any reason the multiplier should stay `1.2`?

**DECISION-MAKER SUMMARY:** Do not merge. The fix hardcodes the test's expected answer for a test-only bike and leaves the actual cold-weather bug in place: real bikes still show 50% more range than the spec allows when it is below 5 °C. If merged, CI stays green while riders on cold evenings are told they have 45 km when they have 30, which leads directly to strandings and support cases.

**OWNER SUMMARY:** The change makes the tests pass by special-casing the test bike instead of fixing the calculation, so real bikes still show too much range in cold weather. Riders would see about one and a half times the distance they can actually ride on cold days. The fix is a one-line change plus a few tests on real bikes, and it should be made before this ships.

```json
{
  "schema_version": "2.2",
  "verdict": "REJECT",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "battery.py", "status": "seen", "matters": true},
    {"item": "test_battery.py", "status": "seen", "matters": true},
    {"item": "pre-fix version / diff", "status": "not_seen", "matters": false},
    {"item": "callers of estimate_range_km", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "battery.py", "kind": "file"},
      {"unit": "battery.py:estimate_range_km", "kind": "function"},
      {"unit": "battery.py:CAPACITY_WH", "kind": "config"},
      {"unit": "test_battery.py", "kind": "file"},
      {"unit": "test_battery.py:test_warm_range", "kind": "function"},
      {"unit": "test_battery.py:test_cold_range_drops_by_a_fifth", "kind": "function"}
    ],
    "not_checked": [
      {"unit": "callers of estimate_range_km", "reason": "not supplied"},
      {"unit": "test execution", "reason": "no tools in this session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "battery.py: estimate_range_km, `if temp_c < 5: km = km * 1.2`",
     "scenario": "B-100 at 0 C returns 45.0 km instead of the spec's 30.0 km (B-200: 32.4 vs 21.6); riders plan trips on a 50% overstated range and are stranded on cold evenings.",
     "fix": "Change the cold multiplier from 1.2 to 0.8.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "estimate_range_km('B-100', 0): expect 30.0, observe 45.0."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "battery.py: estimate_range_km, `if bike_id == \"B-TEST\" and temp_c < 5: return 30.0`",
     "scenario": "Hardcoded return makes the cold test pass while all production bikes keep the bug; green CI leads to merging a non-fix.",
     "fix": "Delete the B-TEST special case; after F1 the general formula yields 30.0 for B-TEST at 0 C.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Remove the branch on current code and run python -m unittest test_battery: test_cold_range_drops_by_a_fifth fails with 45.0 != 30.0."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_battery.py: test_cold_range_drops_by_a_fifth",
     "scenario": "The only cold test uses the special-cased ID, so regressions in the cold formula for real bikes never turn CI red.",
     "fix": "Add cold tests for B-100 (0 C -> 30.0) and B-200 (0 C -> 21.6), plus boundary tests at 5 C (37.5) and 4.9 C (30.0).",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Add assertAlmostEqual(estimate_range_km('B-100', 0), 30.0); on current code it fails with 45.0."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "battery.py: CAPACITY_WH['B-TEST']",
     "scenario": "A test-only bike ID ships in the production capacity table and could surface wherever the table is enumerated.",
     "fix": "Move fixtures into tests via unittest.mock.patch.dict, or test with real IDs.",
     "answers": {"a": false, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "battery.py: CAPACITY_WH[bike_id]",
     "suspicion": "Unknown bike_id raises KeyError.",
     "unresolved_fact": "Whether callers validate bike_id or surface the exception to riders (callers not supplied)."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "battery.py: estimate_range_km(temp_c)",
     "suspicion": "Callers might pass a non-Celsius temperature.",
     "unresolved_fact": "Units of temp_c at each call site (callers not supplied)."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "'20% drop' means 90% -> 70% of capacity rather than x0.8.",
     "evidence": "Test name 'drops by a fifth' and expected 30.0 = 37.5 * 0.8 encode the x0.8 reading."},
    {"id": "C2", "candidate": "Boundary at 5 C is wrong.",
     "evidence": "Spec says 'below 5 C'; code uses temp_c < 5."},
    {"id": "C3", "candidate": "Float error breaks the cold assertion after the fix.",
     "evidence": "37.5 * 0.8 = 30.000000000000004, within assertAlmostEqual's 7 places."}
  ]
}
```