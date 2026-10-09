VERDICT: **REWORK.** The cold-weather bug is not fixed: the code still multiplies cold range by 1.2, and the cold test passes only because of a hardcoded return value for the test bike.

CONFIDENCE: **high** for the findings below. Each one comes from tracing the code and recomputing the figures by hand. Limits: there were no tools in this session, so nothing was executed. This was a single reviewer with no fresh subagent, which carries some anchoring risk. Re-run in a fresh session with tools before merging anything high-stakes.

INPUTS LEDGER:
- Seen: `request.md` (original request), `context.md`, `battery.py`, `test_battery.py`.
- Not seen: the pre-fix version of `battery.py` (doesn't matter, because the current code is wrong on its own terms). Any other callers of `estimate_range_km` or other uses of `CAPACITY_WH` (matters a little for blast radius; see the needs-validation list).
- Not verified: the context's claim that "2 tests pass". By tracing, both tests would pass, but nothing was run.

COVERAGE:
- Scope: the whole work (two files).
- Checked: `battery.py`, `battery.py:estimate_range_km`, the `CAPACITY_WH` table, `test_battery.py` (both tests), `request.md` (the spec), and `context.md`.
- Not checked: other callers (not supplied) and test execution (no tools).

SEATS AND GATE: one local reviewer ran. No cross-vendor seats were requested and none were used. Sensitivity gate: the material contains no personal, credential or confidential data, so it is not sensitive.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | `battery.py:14-15` (`km = km * 1.2`) | The cold branch increases range by 20%. The spec requires a 20% drop (×0.8). This is the exact bug the request asked to fix. | A rider checks a B-100 at 0 °C and sees 500×0.9/12 = 37.5 × 1.2 = **45.0 km**. The spec value is **30.0 km**, so the estimate overstates real range by 15 km. A B-200 shows 32.4 km against a spec of 21.6. Riders plan trips on these numbers and get stranded on cold evenings. | **Fix:** `km = km * 0.8`. **Repro:** add `assertAlmostEqual(battery.estimate_range_km("B-100", 0), 30.0)`. It fails today (observed 45.0, expected 30.0) and passes after the fix. | a✔ b✔ c✔ d✔ |
| F2 | High | CONFIRMED | B | `battery.py:9-10` (`if bike_id == "B-TEST" and temp_c < 5: return 30.0`) | A special case for the test fixture returns the expected answer, so the cold test passes without the cold logic ever running. This is a stub presented as a fix. | The test suite is green and the PR looks done, yet every real bike still gets the inflated cold range from F1. Without the special case, B-TEST at 0 °C would compute 45.0 and the test would fail, so the hardcode is exactly what hides F1. | **Fix:** delete lines 9-10 and fix F1. **Repro:** remove lines 9-10 and run `python -m unittest test_battery`. `test_cold_range_drops_by_a_fifth` fails (45.0 ≠ 30.0), which shows the test was passing only because of the hardcode. | a✔ b✔ c✘ d✔ |
| F3 | Medium | CONFIRMED | B | `test_battery.py:10-11` | The only cold test uses `B-TEST`, which follows the hardcoded branch. No test covers the real cold path for production bikes, and no test checks the 5 °C boundary. | A future change to the cold factor, or a regression back to ×1.2, passes CI unnoticed. | **Fix:** add cold tests for B-100 (30.0) and B-200 (21.6). Add boundary tests: at 5 °C a B-100 shows 37.5 (no reduction, since the spec says "below 5"), and at 4.9 °C it shows 30.0. **Repro:** with the current code, the B-100 cold assertion fails (45.0 vs 30.0). | a✔ b✔ c✘ d✘ |

**Pass 3 on F1 and F2 (confirm or refute):**
- **F1 holds.** The strongest defence would be that 1.2 is intentional. The spec ("drops by 20%"), the request ("goes up instead of down") and the repo's own test (expects 30.0 = 37.5 × 0.8) all contradict that. Security: no. Sibling search: I searched both files for every temperature adjustment and every multiplier. `battery.py:15` is the only cold-weather factor, and nothing else applies a 1.x factor.
- **F2 holds.** A defender could say B-TEST is not a real bike. That is true, but the hardcode still means the passing suite gives no evidence of a fix, and the request was to fix the function. Security: no. Sibling search: I looked for other `bike_id ==` checks or literal returns in `battery.py` and found none. In the tests, `test_warm_range` uses the real B-100 path (500×0.9/12 = 37.5 ✔) and is not gamed.

**NEEDS VALIDATION**
- S1 (`battery.py:12`): an unknown `bike_id` raises a `KeyError`. Unresolved: whether callers expect an exception, a default, or `None`. The spec is silent on this, and the callers were not supplied.
- S2: other code may read `CAPACITY_WH` or depend on the presence of `"B-TEST"` in it. Unresolved: whether any production code path sees the B-TEST entry, for example by listing fleet bikes from this dict.

**REFUTED**
- One candidate was that "drops by 20%" is ambiguous and could mean 20 percentage points of capacity (0.9 − 0.2 = 0.7, which gives 29.17 km). Refuted: the repo's test expects 30.0 = 37.5 × 0.8, which settles the reading as multiplicative.
- One candidate was that `temp_c < 5` mishandles exactly 5 °C. Refuted: the spec says "below 5 C", so the strict `<` is correct.

**WHAT HOLDS UP:** the warm path is correct. The 0.9 usable fraction and 12 Wh/km give B-100 = 37.5 km, which matches the test. The `< 5` threshold matches the spec.

**UNVERIFIED CLAIMS:** "Tests: 2 tests pass." By trace they would pass, but nothing was run here. To confirm, run `python -m unittest test_battery`. Their passing proves nothing about the cold fix (see F2).

**QUESTIONS FOR THE AUTHOR:**
1. Why was a B-TEST special case added instead of changing 1.2 to 0.8?
2. Does any production code enumerate `CAPACITY_WH`?

**DECISION-MAKER SUMMARY:** Do not merge. The cold-weather bug is still present for every real bike, and the passing tests come from a hardcoded answer for the test bike. If this ships, riders get cold-weather estimates about 50% too high (45 km shown where 30 km is real), which leads to stranded bikes and support cases.

**OWNER SUMMARY:** The fix doesn't actually fix the problem. In cold weather the app still promises riders more range than the bike has, and the tests only pass because a special answer was written in for the test bike. A one-number change and a couple of honest tests would resolve it.

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
    {"item": "other callers of estimate_range_km / CAPACITY_WH", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local-no-tools", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "battery.py", "kind": "file"},
      {"unit": "battery.py:estimate_range_km", "kind": "function"},
      {"unit": "battery.py:CAPACITY_WH", "kind": "data"},
      {"unit": "test_battery.py", "kind": "file"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"}
    ],
    "not_checked": [
      {"unit": "other callers of estimate_range_km", "reason": "not_supplied"},
      {"unit": "test execution", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "battery.py:14-15",
     "scenario": "B-100 at 0 C returns 45.0 km instead of the spec's 30.0 km (B-200: 32.4 vs 21.6); riders plan trips on an overstated range and are stranded in the cold.",
     "fix": "Change km * 1.2 to km * 0.8.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Add assertAlmostEqual(battery.estimate_range_km('B-100', 0), 30.0); observe 45.0, expected 30.0.",
     "security": false,
     "siblings_searched": {"searched": "all temperature adjustments and multipliers in battery.py and test_battery.py", "found": "battery.py:15 is the only cold factor"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "battery.py:9-10",
     "scenario": "A hardcoded return of 30.0 for B-TEST in the cold makes the cold test pass while every real bike still gets the inflated range, so CI reports the bug fixed when it is not.",
     "fix": "Delete the B-TEST special case and fix F1.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Remove lines 9-10 and run python -m unittest test_battery; test_cold_range_drops_by_a_fifth fails with 45.0 != 30.0.",
     "security": false,
     "siblings_searched": {"searched": "other bike_id comparisons or literal returns in battery.py; gamed assertions in test_battery.py", "found": "none; test_warm_range exercises the real path"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_battery.py:10-11",
     "scenario": "The only cold test uses the hardcoded B-TEST path; no test covers cold range for real bikes or the 5 C boundary, so a regression to *1.2 passes CI.",
     "fix": "Add cold tests for B-100 (30.0) and B-200 (21.6), plus boundary tests at 5.0 (37.5) and 4.9 (30.0) for B-100.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Add assertAlmostEqual(battery.estimate_range_km('B-100', 0), 30.0); fails on current code with 45.0."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "battery.py:12",
     "suspicion": "An unknown bike_id raises KeyError.",
     "unresolved_fact": "Whether callers expect an exception or a default; the spec is silent and callers were not supplied."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "battery.py:3",
     "suspicion": "The B-TEST fixture lives in the production capacity table.",
     "unresolved_fact": "Whether any production code enumerates CAPACITY_WH."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "'Drops by 20%' could mean 0.9 - 0.2 = 0.7 of capacity.", "evidence": "The test expects 30.0 = 37.5 * 0.8, so the reduction is multiplicative."},
    {"id": "C2", "candidate": "temp_c < 5 mishandles exactly 5 C.", "evidence": "The spec says 'below 5 C', so strict < is correct."}
  ]
}
```

This JSON was not run through `tools/validate_findings.py` because no tools were available in this session.