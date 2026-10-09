**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** This session has no tools. Every finding below comes from reading and tracing the code by hand. Nothing was executed.

VERDICT: **SHIP WITH FIXES**. The helper does what was asked for realistic inputs and has no High or Critical defect. It does have one confirmed crash at very large attempt counts, and its tests would not catch the jitter being removed.

CONFIDENCE: **medium**. Three things limit it: I had no tools, so nothing was run; this is a single same-context reviewer; and the meaning of "the clock" in the request is unclear.

INPUTS LEDGER:
- Seen: request.md, context.md, retry.py, test_retry.py.
- Not seen: the actual test run output. The claim "6 tests, all pass" is supported only by my trace (matters: low, because the trace agrees). I also could not see the raw bytes of the files, so I could not scan for hidden or bidi characters (matters: low).
- No linked sources or prior versions are referenced.

COVERAGE: The scope is the whole work, which is two files.
- Checked: `retry.py:retry` (main path, every exit path, exception chaining, numeric behaviour at large k, parameter types), all six tests in `test_retry.py` (each traced to pass/fail by hand), request.md, and context.md.
- Not checked: whether the tests actually run green (no_tools), byte-level hidden characters (no_tools), and behaviour under real `time.sleep` interruption such as KeyboardInterrupt (no_tools).

SEATS AND GATE: One same-context reviewer ran. There was no subagent tool. Cross-vendor seats were declined at the user's request. The sensitivity gate passed: the work contains no personal or confidential data. The work contains no text addressed to the reviewer.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced Python float semantics) | B | `retry.py:20` `base * (2 ** k)` | `2**k` is an int. Multiplying it by a float converts it to float. At k = 1024 that conversion raises `OverflowError: int too large to convert to float`. The cap is applied after the product is computed, so the cap does not prevent this. | A job sets `attempts=2000` ("retry for a long time") and the dependency stays down. After the 1025th failure the helper raises `OverflowError` instead of continuing. It stops early and does not re-raise the last `ConnectionError`, which survives only as `__context__`. | **Fix:** clamp before multiplying, e.g. keep `ceiling = min(cap, ceiling * 2)` across iterations, or use `min(cap, base * 2 ** min(k, 64))`. **Repro:** `retry(Flaky(10**6), attempts=1100, sleep=lambda s: None, rng=lambda: 0.0)`. Expected: `ConnectionError` after 1100 calls. Observed by trace: `OverflowError` after 1025 calls. | a✔ b✔ c✘ d✘ |
| F2 | Medium | CONFIRMED (traced every test) | B | `test_retry.py` `test_succeeds_after_failures`, `test_does_not_sleep_after_the_last_attempt`, `test_cap_applies` | Full jitter is a core requirement, yet no test exercises it. Every test that checks sleep values uses `rng=lambda: 1.0`, and every other test ignores the values. | Someone replaces `rng() * min(...)` with `min(...)` (no jitter) or with equal jitter `d*(0.5+rng()/2)`. With rng = 1.0 these give identical delays, so all 6 tests stay green and the regression ships. Fleet jobs then retry in lockstep. | **Fix:** add a test with `rng=lambda: 0.5, base=1, cap=100, Flaky(2)` that asserts `slept == [0.5, 1.0]`, and assert that rng is called once per sleep. **Repro (mutation):** change line 20 to `sleep(min(cap, base * (2 ** k)))` and run the suite. Expected: a test goes red. Observed by trace: 6/6 pass. | a✔ b✔ c✘ d✘ |
| F3 | Low | CONFIRMED (traced) | B | `retry.py:7`, `:14-15` | `base` and `cap` are never validated. A negative value or NaN reaches `time.sleep`, which raises `ValueError` from inside the except block. | A config typo `base=-0.1` raises nothing at call time. The first transient failure then turns into `ValueError: sleep length must be non-negative`, and the real error is hidden in `__context__`. | **Fix:** next to the `attempts` check, reject `base < 0`, `cap < 0`, and NaN. **Repro:** `retry(Flaky(1), base=-1)` with the real `time.sleep`. Expected: `ValueError` before `fn` is called. Observed by trace: `fn` is called once, then `ValueError` comes from `sleep`. | a✔ b✔ c✘ d✘ |
| F4 | Low | CONFIRMED (traced) | B | `retry.py:17` `except retry_on` | A caller who passes `retry_on` as a list gets an error only when `fn` fails. The `except` clause then raises `TypeError: catching classes that do not inherit from BaseException is not allowed`. | `retry(fetch, retry_on=[ConnectionError])` works in every happy-path test. It breaks only during a real outage, which is exactly when the retry is needed. | **Fix:** normalise up front with `retry_on = tuple(retry_on) if isinstance(retry_on, (list, set)) else retry_on`, or validate that every entry is a `BaseException` subclass. **Repro:** `retry(Flaky(1), retry_on=[ConnectionError], sleep=lambda s: None)`. Expected: `"ok"`. Observed by trace: `TypeError`. | a✔ b✔ c✘ d✘ |
| F5 | Low | CONFIRMED (traced) | B | `retry.py:7` `retry_on=(Exception,)` | The request says "retry on chosen exceptions", but the default retries every `Exception`, including programming errors. | A caller omits `retry_on`. A `TypeError` bug in a side-effecting `fn` (for example one that sends a message and then crashes) runs 5 times with delays before it surfaces. | **Fix:** make `retry_on` required, or default it to `()` and document that. **Repro:** `retry(Flaky(10, exc=TypeError), sleep=slept.append)`. Expected for "chosen only": 1 call. Observed by trace: 5 calls, 4 sleeps. | a✔ b✔ c✘ d✘ |

### Severity notes

**F1 confirm-or-refute.** The four questions give Medium: c and d are both no. The failure is loud, the original error is preserved in `__context__`, and the attempt counts involved are uncommon. It is, however, a real contract violation in a shared production library, and the fix is one line. Fix it before relying on large `attempts`.

**Siblings searched.** I looked for other unbounded arithmetic in `retry.py`. `rng() * x` is safe once `x` is bounded, and there is no other exponentiation.

## Needs validation
- **"Clock injectable".** The work injects `sleep` but not a time source. This suffices if "the clock" meant sleeping. It falls short if the requester expected an injectable `now()`, for example for an overall deadline or elapsed-time logging. The fact that would settle it is the requester's intended meaning of "clock".
- **"6 tests, all pass".** My trace agrees, but nothing was run. Running `python -m unittest test_retry` would settle it.

## Refuted
- **`raise last` could raise `None`.** Refuted: `attempts >= 1` is enforced, and the only exits are `return` and `break`, which happens right after `last = e`.
- **Implicit exception chaining across attempts.** Refuted: `fn()` is called in the `try`, not inside the previous `except`, so attempts do not chain.
- **Sleeping after the final attempt.** Refuted: the `break` at `k == attempts - 1` prevents it, and the test asserts 2 sleeps for 3 attempts.
- **Cap applied wrongly.** Refuted: `min(cap, base*2**k)` matches AWS full jitter. Tracing `test_cap_applies` gives `[1, 2, 3, 3, 3]`.

## What holds up
- The backoff formula is correct full jitter.
- Non-matching exceptions propagate immediately.
- The last error is re-raised with its original traceback.
- `attempts < 1` is rejected.
- `KeyboardInterrupt` and `SystemExit` are not retried by default.
- There is no shared state, so the helper is thread-safe.
- Both `sleep` and `rng` are injectable.

## Unverified claims
- "6 tests, all pass": run the suite to confirm.

## Questions for the author
1. Did "clock" mean only `sleep`, or also a time source for a total deadline?
2. Do any production callers use `attempts` above about 1000?

## Decision-maker summary
The helper is safe to adopt once F1 (overflow at more than 1025 attempts) and F2 (no test covers jitter) are fixed. Both are small changes. If you ship as is, jobs configured for very long retry runs will crash early, and a future change that silently removes jitter will pass CI.

## Owner summary
The retry helper works correctly for normal settings and does what was asked. It crashes if someone asks for more than about a thousand retries. Its tests also would not notice if the randomized waiting were accidentally removed. Both are quick fixes and should be made before teams rely on it widely.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "retry.py", "status": "seen", "matters": true},
    {"item": "test_retry.py", "status": "seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "retry.py", "kind": "file"},
      {"unit": "retry.py:retry", "kind": "function"},
      {"unit": "test_retry.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "actual test execution", "reason": "no_tools"},
      {"unit": "byte-level hidden/bidi character scan", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "retry.py:20",
     "scenario": "With attempts >= 1026, base * 2**k raises OverflowError at k=1024 (int too large to convert to float) before the cap applies; retries stop after 1025 calls and OverflowError replaces the last retried error.",
     "fix": "Clamp the exponent or track the ceiling iteratively: ceiling = min(cap, ceiling * 2).",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "retry(Flaky(10**6), attempts=1100, sleep=lambda s: None, rng=lambda: 0.0); expected ConnectionError after 1100 calls, observed (by trace) OverflowError after 1025 calls."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_retry.py: test_succeeds_after_failures, test_does_not_sleep_after_the_last_attempt, test_cap_applies",
     "scenario": "All value-checking tests use rng=lambda: 1.0, so removing jitter or switching to equal jitter leaves all 6 tests green.",
     "fix": "Add a test with rng=lambda: 0.5, base=1, cap=100, Flaky(2) asserting slept == [0.5, 1.0], and assert rng is called once per sleep.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Mutate retry.py:20 to sleep(min(cap, base * (2 ** k))) and run the suite; expected a red test, observed (by trace) 6/6 pass."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "retry.py:7, retry.py:14-15",
     "scenario": "Negative or NaN base/cap is accepted; on the first retried failure time.sleep raises ValueError, masking the real error.",
     "fix": "Validate base >= 0, cap >= 0 and not NaN alongside the attempts check.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "retry(Flaky(1), base=-1) with real time.sleep; expected ValueError before fn is called, observed (by trace) fn called once then ValueError from sleep."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "retry.py:17",
     "scenario": "retry_on passed as a list raises TypeError only when fn fails, i.e. during a real outage.",
     "fix": "Normalise retry_on to a tuple and validate entries are BaseException subclasses at call time.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "retry(Flaky(1), retry_on=[ConnectionError], sleep=lambda s: None); expected 'ok', observed (by trace) TypeError."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "retry.py:7",
     "scenario": "Default retry_on=(Exception,) retries programming errors; a side-effecting fn with a TypeError bug runs 5 times.",
     "fix": "Make retry_on required, or default to () and document it.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "retry(Flaky(10, exc=TypeError), sleep=slept.append); observed (by trace) 5 calls and 4 sleeps instead of 1 call."},
    {"id": "S1", "status": "needs_validation", "track": "A", "location": "retry.py:7 (sleep parameter)",
     "suspicion": "The request asks for an injectable clock; only sleep is injectable, not a time source.",
     "unresolved_fact": "Whether the requester meant sleep only, or also a now() source, e.g. for an overall deadline."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "context.md: '6 tests, all pass'",
     "suspicion": "Test pass claim not executed in this review.",
     "unresolved_fact": "Output of python -m unittest test_retry."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "raise last could raise None.", "evidence": "attempts >= 1 is enforced; the loop exits only via return or via break immediately after last = e."},
    {"id": "C2", "candidate": "Exceptions chain across attempts.", "evidence": "fn() is called in the try block of a new iteration, not inside the previous except."},
    {"id": "C3", "candidate": "Sleeps after the final attempt.", "evidence": "break at k == attempts - 1; test asserts 2 sleeps for 3 attempts."},
    {"id": "C4", "candidate": "Cap misapplied.", "evidence": "min(cap, base*2**k) matches full jitter; test_cap_applies traces to [1, 2, 3, 3, 3]."}
  ]
}
```