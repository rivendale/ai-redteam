# Adversarial Diagnostic Review: `estimate_range_km` cold-weather fix

## Pass 1: Reconstruct

The work claims to fix the cold-weather range bug so that both tests pass. To be correct, a reading below 5 °C must cut range by 20% (×0.8) for every bike. It must also keep the warm formula (capacity × 0.9 / 12 Wh/km) unchanged. The load-bearing assumptions are:

- The tests check the spec rather than a single value.
- The cold path is computed, not special-cased.
- "Below 5 C" means strictly `< 5`.

There are also two unstated assumptions. Every `bike_id` passed in exists in `CAPACITY_WH`, and `B-TEST` is a test fixture that should not need production logic.

## Pass 2: Attack (Track B)

I traced the code by hand. I cannot run code in this session.

- **Warm path, B-100 at 20 °C:** 500 × 0.9 = 450, and 450 / 12 = 37.5. This is correct.
- **Cold path, B-100 at 0 °C:** 37.5 × 1.2 = **45.0**. The spec gives 37.5 × 0.8 = 30.0, so range goes *up*, which is the original bug.
- **Cold path, B-200 at 0 °C:** 360 × 0.9 / 12 = 27.0, and 27.0 × 1.2 = **32.4**. The spec gives 21.6, so this overstates range by 50%.
- **Cold path, B-TEST at 0 °C:** The early return at line 9–10 gives 30.0, so the test passes. The real formula is never exercised.
- **Boundary at exactly 5 °C:** `temp_c < 5` is false, so no reduction applies. This matches "below 5 C" and holds.
- **Hostile input, unknown `bike_id`:** `CAPACITY_WH[bike_id]` raises an uncaught `KeyError`.
- **Hostile input, `temp_c=None`:** At line 9 `None < 5` is only evaluated when `bike_id == "B-TEST"`. Otherwise it fails at line 13 with a `TypeError`.

**Mutation reasoning (rule 5):** I cannot run the tests, but the trace settles it. Changing `1.2` to `0.8`, to `1.0`, or deleting lines 13–14 entirely leaves both tests green. The B-TEST case returns at line 10, and the warm test never enters the cold branch. The cold test cannot fail for any change to the cold formula.

## Pass 3: Self-check

- **Injection scan:** The work contains no text addressed to the reviewer.
- **Strongest defence of F1:** "Maybe 1.2 is intentional, for example a divisor convention." This does not hold. The code multiplies, and the request itself says range "goes up instead of down" is the bug. F1 stands.
- **Strongest defence of F2:** "B-TEST is a fixture, so the shortcut is harmless." This does not hold either. It hides F1 from the only cold test, and it ships test-only logic in production code. F2 stands.
- **Sibling search (F1, F2):** I searched `battery.py` for other temperature adjustments and other `bike_id`-specific branches. There is one of each, at lines 13–14 and lines 9–10. I searched `test_battery.py` for other cold-path tests and found only line 9–10, which uses B-TEST.
- **What I might still be missing:** Callers outside the supplied files could also depend on the 1.2 behaviour, or could pass B-TEST IDs in production. Those callers were not supplied.

---

**VERDICT: REWORK.** The original bug is still present: every real bike gets 20% *more* range in the cold. The tests pass only because a hardcoded branch returns the expected value for the test bike.

**CONFIDENCE IN VERDICT: high.** The arithmetic is fully traceable from the supplied code. Confidence is limited only by not having run it.

**COVERAGE**
- `battery.py`: checked, all lines.
- `test_battery.py`: checked, all lines.
- `request.md`: checked.
- `context.md`: checked.
- Callers of `estimate_range_km`: not checked, because they were not supplied.

### FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | `battery.py:13-14` `km = km * 1.2` | The cold adjustment raises range by 20% instead of cutting it by 20%. This is the exact bug the request asked to fix. | A rider checks a B-100 at 0 °C and sees 45.0 km against a spec value of 30.0 km. A B-200 shows 32.4 km against 21.6 km. They plan a 35 km trip, the bike strands them on a cold evening, and that becomes a support case. | **Fix:** change to `km = km * 0.8`. **Reproduction:** `estimate_range_km("B-100", 0)` returns 45.0, but should be 30.0. | y/y/y/y |
| F2 | Critical | CONFIRMED | `battery.py:9-10` `if bike_id == "B-TEST" and temp_c < 5: return 30.0` | A hardcoded return makes the cold test pass without exercising the formula. Test-only logic is presented as a fix and shipped in production code. | Any change to the cold formula leaves the suite green, including the current wrong 1.2, so F1 merges undetected. | **Fix:** delete lines 9–10. B-TEST then computes 37.5 × 0.8 = 30.0 legitimately. **Reproduction:** in a scratch copy, set line 14 to `km * 5`. Both tests still pass. | y/y/y/y |
| F3 | High | CONFIRMED | `test_battery.py:9-10` | The only cold test uses the special-cased bike. No cold test covers a real bike, and nothing tests the 5 °C boundary. | A future regression in the cold path, or in the boundary (`<=` vs `<`), ships silently. | **Add tests:** `("B-100", 0)` → 30.0, `("B-200", 0)` → 21.6, `("B-100", 5)` → 37.5, `("B-100", 4.9)` → 30.0. Confirm each fails against the current code and passes after the fix. | y/y/n/y |
| F4 | Low | CONFIRMED | `battery.py:11` `CAPACITY_WH[bike_id]` | An unknown `bike_id` raises a bare `KeyError`. No error is defined for it. | A newly added fleet model is missing from the table, so the range call crashes the caller. Whether this matters depends on the caller, which was not supplied. | **Fix:** raise a clear `ValueError(f"unknown bike {bike_id}")`. **Test:** `assertRaises` on `"B-999"`. | y/y/n/n |

### NEEDS VALIDATION
- **B-TEST in the production table:** Is `"B-TEST"` in `CAPACITY_WH` reachable from production callers? This is settled by grepping the callers and fleet data for `B-TEST`.
- **Consumers of the inflated value:** Has any consumer, such as UI or trip-planner thresholds, been tuned against the inflated cold values? This is settled by reviewing the callers of `estimate_range_km`.

### REFUTED
- **"5 °C boundary is off-by-one":** The code uses `< 5`, which matches the spec's "below 5 C".
- **"Warm formula is wrong":** 500 × 0.9 / 12 = 37.5, which matches the spec and the test.
- **"Cold test expectation is wrong":** 30.0 = 37.5 × 0.8, so the expectation is correct. Only the way it is satisfied is wrong.

### WHAT HOLDS UP
- The warm-path formula (90% usable, 12 Wh/km).
- The strict `< 5` threshold.
- The test expectations themselves.

### UNVERIFIED CLAIMS
- **"2 tests in test_battery.py pass":** This is consistent with my trace, but I did not run it. Confirm with `python -m unittest test_battery`.
- **"Fixed":** This is false by trace (F1).

### QUESTIONS FOR THE AUTHOR
1. Why was the B-TEST early return added instead of changing 1.2 to 0.8?
2. Is B-TEST ever present in production data?

**DECISION-MAKER SUMMARY:** Do not merge. The change leaves cold-weather range inflated by 20% for every real bike, and it hides this behind a hardcoded test shortcut. To fix it, use ×0.8, delete the B-TEST branch, and add cold tests for real bikes; if merged as is, riders will be stranded on cold days.

**OWNER SUMMARY:** The fix does not actually fix the problem. In cold weather, real bikes still show more range than they have, and the tests were made to pass with a shortcut that only works for the test bike. This needs a small rework and better tests before it goes live.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "battery.py", "status": "seen", "matters": true},
    {"item": "test_battery.py", "status": "seen", "matters": true},
    {"item": "callers of estimate_range_km", "status": "not_seen", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "battery.py", "kind": "file"},
      {"unit": "test_battery.py", "kind": "file"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"}
    ],
    "not_checked": [
      {"unit": "callers of estimate_range_km", "reason": "not_supplied"},
      {"unit": "test execution", "reason": "no_tools"}
    ]
  },
  "findings": [
    {
      "id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
      "location": "battery.py:13-14 `km = km * 1.2`",
      "scenario": "B-100 at 0 C returns 45.0 km (spec 30.0); B-200 returns 32.4 (spec 21.6). Rider plans on inflated range and is stranded in the cold.",
      "fix": "Change multiplier to 0.8.",
      "reproduction": "estimate_range_km('B-100', 0) == 45.0; expected 30.0.",
      "answers": {"a": true, "b": true, "c": true, "d": true},
      "security": false,
      "siblings_searched": {"searched": "all temperature adjustments in battery.py", "found": "only lines 13-14"}
    },
    {
      "id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
      "location": "battery.py:9-10 `if bike_id == \"B-TEST\" and temp_c < 5: return 30.0`",
      "scenario": "Hardcoded return satisfies the only cold test, so any cold-formula error (including F1) passes CI.",
      "fix": "Delete lines 9-10; B-TEST then computes 30.0 from the formula.",
      "reproduction": "In a scratch copy set line 14 to `km * 5`; both tests still pass.",
      "answers": {"a": true, "b": true, "c": true, "d": true},
      "security": false,
      "siblings_searched": {"searched": "bike_id-specific branches in battery.py; cold tests in test_battery.py", "found": "one branch (lines 9-10); one cold test, B-TEST only"}
    },
    {
      "id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
      "location": "test_battery.py:9-10",
      "scenario": "No cold test on a real bike and no boundary test; cold-path regressions ship silently.",
      "fix": "Add tests: B-100@0 -> 30.0, B-200@0 -> 21.6, B-100@5 -> 37.5, B-100@4.9 -> 30.0.",
      "reproduction": "Add B-100@0 -> 30.0 test; it fails against current code (returns 45.0).",
      "answers": {"a": true, "b": true, "c": false, "d": true},
      "security": false,
      "siblings_searched": {"searched": "all tests in test_battery.py", "found": "only warm B-100 and cold B-TEST"}
    },
    {
      "id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
      "location": "battery.py:11 `CAPACITY_WH[bike_id]`",
      "scenario": "Unknown bike_id raises bare KeyError.",
      "fix": "Raise ValueError with the bike id; add assertRaises test.",
      "reproduction": "estimate_range_km('B-999', 20) raises KeyError.",
      "answers": {"a": true, "b": true, "c": false, "d": false}
    },
    {
      "id": "NV1", "status": "needs_validation",
      "location": "battery.py:3 CAPACITY_WH['B-TEST']",
      "suspicion": "Test fixture lives in production capacity table and may be reachable.",
      "unresolved_fact": "Whether any production caller or fleet record uses bike_id 'B-TEST'."
    },
    {
      "id": "NV2", "status": "needs_validation",
      "location": "callers of estimate_range_km",
      "suspicion": "Downstream thresholds may be tuned to the inflated cold values.",
      "unresolved_fact": "Review of callers and their thresholds."
    }
  ],
  "refuted": [
    {"id": "R1", "candidate": "5 C boundary off-by-one", "evidence": "Code uses `< 5`, matching spec 'below 5 C'."},
    {"id": "R2", "candidate": "Warm formula wrong", "evidence": "500*0.9/12 = 37.5, matches spec and test."},
    {"id": "R3", "candidate": "Cold test expectation wrong", "evidence": "37.5*0.8 = 30.0; expectation correct, only satisfied by hardcoding."}
  ]
}
```