VERDICT: **REWORK.** The cold-weather bug is not fixed. The code still multiplies range by 1.2 in the cold, and a hardcoded branch for the test bike makes the cold test pass anyway.

CONFIDENCE: **high** on the core finding, which is plain arithmetic traced line by line. Medium overall: there were no tools in this session, so nothing was executed. All results are hand-traced, and the prior version of `battery.py` was not supplied.

INPUTS LEDGER:
- Seen: the original request (request.md), the context (context.md), `battery.py` and `test_battery.py`.
- Not seen: the pre-fix version of `battery.py`, or a diff. This matters a little: I cannot tell whether the author changed the `1.2` at all. It does not change the verdict, because the current code is wrong either way.
- Not seen: any other callers of `estimate_range_km` or fleet data. This matters for whether `B-TEST` is reachable in production.
- The claim that "2 tests pass" was not run. I traced it by hand, and both should pass.

COVERAGE:
- Checked: `battery.py`, `battery.py:estimate_range_km`, `CAPACITY_WH`, `test_battery.py`, `test_warm_range`, `test_cold_range_drops_by_a_fifth`, and the spec arithmetic.
- Not checked: callers, the fleet ID registry and the prior version.

SEATS AND GATE: one reviewer, this session, with no tools and no subagent. The work was not written in this conversation, so there is no authorship anchoring, but nothing was executed. The sensitivity gate passed: there is no personal or confidential data. No cross-vendor seats were run, since none were requested and none were available.

## Pass 1: Reconstruct

**What the work claims.** It claims to fix the cold-weather range so that the tests pass.

**What the spec requires.**
- Range = capacity × 0.9 / 12 Wh/km.
- Below 5 °C, range × 0.8.
- So B-100 should give 37.5 km when warm and 30.0 km when cold.

**Load-bearing assumptions.**
- The cold multiplier is 0.8.
- The tests exercise the real cold path.
- `B-TEST` is not a real bike.

**What the code actually does.**
- The cold multiplier is still `1.2`.
- The only cold test hits a special case that returns a hardcoded `30.0`.

Tracks used: B (code), plus drift under rule 8.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (hand trace / recompute) | B | `battery.py:13-14` (`km = km * 1.2`) | Cold weather still *raises* range by 20% instead of cutting it. This is the exact bug the request asked to fix. | B-100 at 0 °C: 500×0.9/12 = 37.5, then ×1.2 = **45.0 km**. The spec gives 37.5×0.8 = **30.0 km**, so the estimate is 50% too high. B-200 at 0 °C returns 32.4 km against a spec of 21.6. A rider plans a 40 km cold-evening trip and is stranded. | Change the line to `km = km * 0.8`. Repro: `python3 -c "import battery; print(battery.estimate_range_km('B-100', 0))"`. Expected 30.0; the trace gives 45.0. Add `assertAlmostEqual(estimate_range_km("B-100", 0), 30.0)`; it fails on the current code. | a✓ b✓ c✓ d✓ |
| F2 | High | CONFIRMED | B (drift) | `battery.py:9-10` (`if bike_id == "B-TEST" and temp_c < 5: return 30.0`); `battery.py:3` (`"B-TEST": 500`) | A test-only branch returns the value the cold test expects. The test passes without the real cold path running, so the fix is a stub presented as complete. A test fixture also lives in the production capacity table. | Anyone trusting the green tests merges F1. Any future change to the cold logic is invisible to the suite. If `B-TEST` is ever a real or demo ID, it gets a constant 30 km at any cold temperature. | Delete the `B-TEST` branch. Remove `B-TEST` from `CAPACITY_WH`, or inject the fixture from the test. Repro: delete line 14 entirely, or change `1.2` to `99`. Both tests still pass by trace, which shows the cold test guards nothing. | a✓ b✓ c✓ d✓ |
| F3 | Medium | CONFIRMED | B | `test_battery.py:9-10` | The cold test never reaches the formula, and there is no boundary test. Under rule 5, this test has never been able to fail for the real logic. | A regression in the multiplier, or a change from `< 5` to `<= 5`, ships silently. | Add cold tests for B-100 (30.0) and B-200 (21.6). Add `estimate_range_km("B-100", 5) == 37.5` and `estimate_range_km("B-100", 4.9) == 30.0`. Confirm each goes red when the multiplier is mutated. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION
- **S1:** whether `B-TEST` is reachable in production, for example as a demo bike or through the fleet registry. Settled by a search of the fleet data and callers for `"B-TEST"`, with a positive control on a known ID like `"B-100"`.
- **S2:** whether an unknown `bike_id` raises `KeyError` (`battery.py:11`) uncaught at the call site, causing a rider-facing error. Settled by reading the callers, which were not supplied.
- **S3:** whether the author changed anything in the real path at all. Settled by the pre-fix version or a diff.

## REFUTED
- **R1, `< 5` should be `<= 5`.** Refuted: the spec says "below 5 C", so the strict `<` is correct.
- **R2, the usable fraction is wrong.** Refuted: `* 0.9` matches "90% of capacity is usable", and 500×0.9/12 = 37.5 matches `test_warm_range`.

## WHAT HOLDS UP
- The warm path is correct: usable fraction 0.9, consumption 12 Wh/km, and B-100 gives 37.5 km.
- The 5 °C threshold comparison is correct.
- The docstring states the spec accurately. The code just does not implement it.

## UNVERIFIED CLAIMS
- "2 tests in test_battery.py pass" is plausible by trace but was not run here. Confirm with `python3 -m unittest test_battery`.

## QUESTIONS FOR THE AUTHOR
1. Is `B-TEST` a real or demo fleet ID anywhere?
2. Was the `B-TEST` branch added in this change, or did it exist before?

## DECISION-MAKER SUMMARY
Do not merge. The cold-weather multiplier is still ×1.2 (F1), and the passing cold test is satisfied by a hardcoded special case for a test bike (F2). If this ships, every real bike overstates its cold-weather range by 50%, which is the stranded-rider scenario this fix was meant to prevent.

## OWNER SUMMARY
The fix does not fix the problem: in cold weather the app still tells riders they can go farther than they can. The tests look green only because the code returns the expected answer for the test bike specifically. Change the cold-weather calculation to reduce range, remove the test-bike shortcut, and add tests that use real bikes.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "battery.py", "status": "seen", "matters": true},
    {"item": "test_battery.py", "status": "seen", "matters": true},
    {"item": "pre-fix battery.py / diff", "status": "not_seen", "matters": false},
    {"item": "callers of estimate_range_km and fleet ID registry", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session-no-tools", "status": "ran", "cross_vendor": false}],
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
      {"unit": "pre-fix battery.py", "reason": "not supplied"},
      {"unit": "test execution", "reason": "no tools in session; traced by hand"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "battery.py:13-14",
     "scenario": "B-100 at 0 C returns 45.0 km (37.5 x 1.2) instead of the spec's 30.0 km (37.5 x 0.8); B-200 returns 32.4 vs 21.6. Riders plan cold trips on an overstated range and get stranded.",
     "fix": "Replace km = km * 1.2 with km = km * 0.8.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "python3 -c \"import battery; print(battery.estimate_range_km('B-100', 0))\" -> expected 30.0, hand trace gives 45.0; add assertAlmostEqual(estimate_range_km('B-100', 0), 30.0), which fails on current code."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "battery.py:9-10; battery.py:3",
     "scenario": "A hardcoded branch returns 30.0 for B-TEST when cold, so the cold test passes without exercising the real formula; the green suite masks F1 and any future regression, and B-TEST lives in the production capacity table.",
     "fix": "Delete the B-TEST special case and remove B-TEST from CAPACITY_WH (inject fixtures from the test instead).",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Change 1.2 to 99 (or delete line 14) in a scratch copy; both tests still pass by trace, showing the cold test guards nothing."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_battery.py:9-10",
     "scenario": "No cold test on a real bike and no boundary test at 5 C, so a wrong multiplier or a < vs <= change ships silently.",
     "fix": "Add cold tests for B-100 (30.0) and B-200 (21.6), plus boundary tests at 5 (37.5) and 4.9 (30.0); confirm each goes red under mutation.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Mutate the cold multiplier in a scratch copy; current suite stays green."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "battery.py:3,9",
     "suspicion": "B-TEST may be reachable in production and would get a constant 30 km in any cold temperature.",
     "unresolved_fact": "Whether any fleet data or caller uses the ID B-TEST (search with a positive control on B-100)."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "battery.py:11",
     "suspicion": "An unknown bike_id raises KeyError, possibly uncaught at the call site.",
     "unresolved_fact": "How callers handle exceptions from estimate_range_km (callers not supplied)."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The threshold should be <= 5.", "evidence": "Spec says 'below 5 C'; strict < is correct."},
    {"id": "R2", "candidate": "The usable fraction is wrong.", "evidence": "0.9 matches the spec; 500 x 0.9 / 12 = 37.5 matches test_warm_range."}
  ]
}
```