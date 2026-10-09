**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools were available, so nothing was executed. Every trace below was done by hand.

VERDICT: **SHIP WITH FIXES.** The limiter itself is correct and meets every part of the request, but several tests would still pass if the code they guard were broken, so the suite proves less than "7 tests, all pass" suggests.

CONFIDENCE: **medium.** Three things limit it: this is a single same-context reviewer, no code or tests were run, and the concurrency behaviour depends on the interpreter.

INPUTS LEDGER:
- Seen: `request.md` (verbatim), `context.md`, `token_bucket.py`, `test_token_bucket.py`.
- Not seen: the actual test run output. "7 tests, all pass" is asserted only. This matters a little; by hand-trace all 7 should pass.
- Not seen: the Python version and whether it is a free-threaded build. This matters for the threading test (S1).

COVERAGE: The scope is the whole work (two files).
- Checked:
  - `token_bucket.py`: `__init__`, `_refill`, `try_acquire`, `seconds_until`.
  - All 7 tests in `test_token_bucket.py`.
  - `request.md` and `context.md`.
  - The claims in the request: capacity, rate, thread safety, injectable clock, non-blocking acquire, wait-time method, tests.
- Not checked: runtime behaviour (no tools) and `docs/*` references (not supplied).

SEATS AND GATE:
- One local reviewer ran. No subagent or cross-vendor seats were available in this session.
- Sensitivity: none. The work is generic library code.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced) | B | `test_token_bucket.py` `test_seconds_until` | The second assertion is trivially true. Nothing tests the "0 if available now" branch, and nothing checks that advancing the clock by the returned value lets `try_acquire` succeed. | Someone changes `return 0.0 if missing <= 0 else missing / self.rate` to `return missing / self.rate`. Callers then get negative waits when tokens are available, and the suite stays green. | **Repro:** apply that mutation and run the tests. Expected red, but by trace all pass (`seconds_until(1)`=0.5, `seconds_until(0.0001)`=5e-5 > 0). **Fix:** assert `seconds_until(1) == 0.0` on a full bucket. Assert that after `clock.t += b.seconds_until(2)`, `try_acquire(2)` is True. Test a partial refill. | a✓ b✓ c✗ d✗ |
| F2 | Low | CONFIRMED (traced) | B | `test_token_bucket.py` `test_clock_going_backwards_is_ignored` | The test cannot detect removal of the `if elapsed > 0` guard. | The guard is deleted, so the body always runs. At t=50, tokens = min(5, -100) = -100 and `try_acquire` returns False. At t=100.5, tokens = -100 + 101 = 1 and it returns True. Both assertions pass while negative "debt" is now possible. | **Repro:** dedent the body of `_refill` out of the `if` and run the test; it passes. **Fix:** add a check that does not rely on the clock coming back symmetrically. For example, after the backward step, call `seconds_until(1)` and assert it is finite and ≤ 0.5. Or assert directly that `_tokens` never goes below 0. | a✓ b✓ c✗ d✗ |
| F3 | Low | CONFIRMED (traced) | B | `token_bucket.py` `_refill` | "Ignored" in practice means refill freezes until the clock passes the old `_last`. A persistent backward step therefore stalls the bucket for the full size of the step. | Someone injects `time.time` and NTP steps the clock back 60 s. The bucket then issues no new tokens for 60 s. The default `time.monotonic` is not affected. | **Repro:** `TokenBucket(5,2,clock=c)`, `try_acquire(5)`, then `c.t -= 60`, `c.t += 1`. `try_acquire()` returns False; expected True (1 s elapsed). **Fix:** on `elapsed < 0`, set `self._last = now` without adding tokens. Alternatively, document that the clock must be monotonic. | a✓ b✓ c✗ d✗ |
| F4 | Low | CONFIRMED (traced) | B | `token_bucket.py` `__init__`, `if capacity <= 0 or refill_per_sec <= 0` | NaN passes the check, because `nan <= 0` is False. | `TokenBucket(float('nan'), 1)` is constructed silently. `_tokens` becomes NaN, every `try_acquire` returns False, and every `n` passes the range check. The result is a dead limiter with no error. | **Repro:** `TokenBucket(float('nan'), 1)`. Expected `ValueError`; it constructs. **Fix:** `if not (capacity > 0) or not (refill_per_sec > 0): raise ValueError(...)` | a✓ b✓ c✗ d✗ |
| F5 | Low | CONFIRMED (traced) | B | `token_bucket.py` `try_acquire`, `if n <= 0 or n > self.capacity` | `n=nan` passes validation. | `try_acquire(float('nan'))` returns False forever instead of raising. | **Repro:** `b.try_acquire(float('nan'))`. Expected `ValueError`; it returns False. **Fix:** `if not (0 < n <= self.capacity): raise ValueError(...)` | a✓ b✓ c✗ d✗ |
| F6 | Low | CONFIRMED (traced) | B | `token_bucket.py` `seconds_until`, same check | `n=nan` passes validation and the method returns `nan`. | A caller runs `time.sleep(b.seconds_until(x))` with a computed NaN and gets an unrelated `ValueError` from `sleep`, far from the cause. | **Repro:** `b.seconds_until(float('nan'))`. Expected `ValueError`; it returns `nan`. **Fix:** the same as F5. | a✓ b✓ c✗ d✗ |
| F7 | Low | CONFIRMED (traced) | B | `test_token_bucket.py` `test_bad_arguments` | Only `capacity=0` and `n > capacity` (on `try_acquire`) are covered. The `refill_per_sec <= 0` check, `n <= 0`, and all of the validation in `seconds_until` are untested. | Someone deletes `or refill_per_sec <= 0`. `TokenBucket(5, 0)` then builds a bucket that never refills, and the suite stays green. | **Repro:** apply that deletion and run the tests; all pass. **Fix:** add `assertRaises` for `TokenBucket(1, 0)`, `TokenBucket(1, -1)`, `try_acquire(0)`, `try_acquire(-1)`, `seconds_until(0)`, `seconds_until(6)`. | a✓ b✓ c✗ d✗ |

### NEEDS VALIDATION

- **S1** (`test_threads_never_over_issue`): Under the GIL, 8 threads × 50 iterations probably finish inside a few 5 ms switch intervals. If so, the test would likely still pass with the lock removed, and it would prove nothing about thread safety. **What would settle it:** remove `with self._lock:` in a scratch copy and run the test 200 times, on both standard CPython and a free-threaded 3.13t build, and count the failures. If it never goes red, add a barrier so all threads start together. Also consider an injected clock that calls `time.sleep(0)` to force interleaving.
- **S2** (the `seconds_until` and `try_acquire` round trip): Floating-point rounding in `(t + s) - t` and in `missing / rate * rate` may leave the bucket 1 ulp short. In that case `try_acquire(n)` would fail right after advancing the clock by exactly `seconds_until(n)`. **What would settle it:** with `FakeClock` at t=100 and rate=3, drain the bucket, run `clock.t += b.seconds_until(1)`, and check `b.try_acquire()`. If it fails, add a small epsilon in the comparison or round the returned wait up.
- **S3** (`context.md`): The claim "7 tests, all pass" was not run here. **What would settle it:** `python -m unittest -v test_token_bucket`.

### REFUTED

- **"`try_acquire` blocks because it takes a lock."** The lock is held only for O(1) arithmetic plus one clock read. The request's "never block" means not waiting for tokens, and the method returns False immediately when tokens are short.
- **"There is an over-issue race between refill, check and decrement."** All three happen inside one `with self._lock:` block in both methods. The clock is read inside the lock, so updates to `_last` are serialized.
- **"`seconds_until` mutating state loses tokens."** `_refill` only moves `_last` forward after crediting the elapsed time, so calling it extra times is harmless.
- **"Raising on `n > capacity` violates 'never block'."** Raising is not blocking. The request does not specify behaviour for an impossible `n`, and raising is a defensible choice.

### WHAT HOLDS UP

- The refill arithmetic is correct: elapsed × rate, capped at capacity, with `_last` advanced only on forward time.
- Failed acquires do not consume tokens.
- The default `time.monotonic` is the right clock.
- Injecting the clock through the constructor works cleanly for tests.
- Every requested feature is present and nothing extra was added.
- `test_never_exceeds_capacity` and `test_refills_at_rate` would catch real regressions in the cap and the rate.

### UNVERIFIED CLAIMS

- "All 7 tests pass": run the suite.
- "Thread-safe": the code is correct by inspection, but the test does not demonstrate it (S1).

### QUESTIONS FOR THE AUTHOR

1. Is a non-monotonic injected clock a supported use? If so, F3 should be fixed rather than documented.
2. Which Python builds must this support? This matters for S1, especially free-threaded builds.

### DECISION-MAKER SUMMARY

The implementation is correct and can ship once the test gaps are closed. The most important gaps are F1 (the wait-time method is barely tested) and S1 (the threading test is probably unable to fail). If it ships as is, future regressions in exactly those areas will pass CI unnoticed.

### OWNER SUMMARY

The rate limiter works as asked. Several of its tests would keep passing even if the code broke, so they offer less protection than they appear to. Strengthening those tests and tightening input checks is a small job and should happen before others depend on the library.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "token_bucket.py", "status": "seen", "matters": true},
    {"item": "test_token_bucket.py", "status": "seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false},
    {"item": "target Python version / free-threaded build", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "token_bucket.py", "kind": "file"},
      {"unit": "test_token_bucket.py", "kind": "file"},
      {"unit": "token_bucket.py:TokenBucket.__init__", "kind": "function"},
      {"unit": "token_bucket.py:TokenBucket._refill", "kind": "function"},
      {"unit": "token_bucket.py:TokenBucket.try_acquire", "kind": "function"},
      {"unit": "token_bucket.py:TokenBucket.seconds_until", "kind": "function"},
      {"unit": "context.md: 7 tests, all pass", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "runtime execution of tests and mutations", "reason": "no_tools"},
      {"unit": "docs/why-reviews-fail.md, docs/attack-catalog.md", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_token_bucket.py:test_seconds_until",
     "scenario": "Mutating seconds_until to always return missing / rate (negative when tokens are available) leaves all tests green; callers would get negative waits.",
     "fix": "Assert seconds_until(1) == 0.0 on a full bucket, a partial-refill value, and that advancing the clock by seconds_until(n) makes try_acquire(n) succeed.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Replace 'return 0.0 if missing <= 0 else missing / self.rate' with 'return missing / self.rate'; run unittest; expected failure, traced result: all pass."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_token_bucket.py:test_clock_going_backwards_is_ignored",
     "scenario": "Removing the 'if elapsed > 0' guard lets tokens go to -100 at t=50, yet the symmetric clock return yields 1 token at t=100.5, so the test still passes.",
     "fix": "Assert behaviour that the symmetric return cannot mask, e.g. seconds_until(1) <= 0.5 right after the backward step, or tokens never negative.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Dedent _refill's body out of the if; run test_clock_going_backwards_is_ignored; expected failure, traced result: pass."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "token_bucket.py:TokenBucket._refill",
     "scenario": "With an injected non-monotonic clock stepped back 60 s, no tokens refill for 60 s because _last stays at the old value.",
     "fix": "On elapsed < 0 set self._last = now without crediting tokens, or document that the clock must be monotonic.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "FakeClock; TokenBucket(5,2,clock=c); try_acquire(5); c.t -= 60; c.t += 1; try_acquire() -> False, expected True."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "token_bucket.py:TokenBucket.__init__ (capacity/refill check)",
     "scenario": "TokenBucket(float('nan'), 1) constructs; tokens are NaN and every try_acquire returns False silently.",
     "fix": "if not (capacity > 0) or not (refill_per_sec > 0): raise ValueError",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "TokenBucket(float('nan'), 1): expected ValueError, traced: constructs."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "token_bucket.py:TokenBucket.try_acquire (n range check)",
     "scenario": "try_acquire(float('nan')) passes validation and returns False forever instead of raising.",
     "fix": "if not (0 < n <= self.capacity): raise ValueError",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "b.try_acquire(float('nan')): expected ValueError, traced: returns False."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "token_bucket.py:TokenBucket.seconds_until (n range check)",
     "scenario": "seconds_until(float('nan')) returns nan; time.sleep(nan) then raises far from the cause.",
     "fix": "if not (0 < n <= self.capacity): raise ValueError",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "b.seconds_until(float('nan')): expected ValueError, traced: returns nan."},
    {"id": "F7", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_token_bucket.py:test_bad_arguments",
     "scenario": "Deleting 'or refill_per_sec <= 0' allows TokenBucket(5, 0), a bucket that never refills, and no test fails.",
     "fix": "Add assertRaises for TokenBucket(1,0), TokenBucket(1,-1), try_acquire(0), try_acquire(-1), seconds_until(0), seconds_until(6).",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Delete 'or refill_per_sec <= 0' in __init__; run unittest; traced result: all pass."},
    {"id": "S1", "status": "needs_validation", "track": "B",
     "location": "test_token_bucket.py:test_threads_never_over_issue",
     "suspicion": "Under the GIL the threads likely run near-serially, so the test passes even without the lock.",
     "unresolved_fact": "Whether the test ever goes red with the lock removed over ~200 runs on standard and free-threaded CPython."},
    {"id": "S2", "status": "needs_validation", "track": "B",
     "location": "token_bucket.py:TokenBucket.seconds_until",
     "suspicion": "Float rounding may leave try_acquire(n) 1 ulp short right after advancing the clock by seconds_until(n).",
     "unresolved_fact": "Result of: clock t=100, rate=3, drain, clock.t += seconds_until(1), try_acquire()."},
    {"id": "S3", "status": "needs_validation", "track": "B",
     "location": "context.md",
     "suspicion": "'7 tests, all pass' is asserted, not shown.",
     "unresolved_fact": "Output of python -m unittest -v test_token_bucket."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "try_acquire blocks because it takes a lock.",
     "evidence": "The lock guards O(1) arithmetic and one clock read; the method returns False immediately when tokens are short, which is the sense of 'never block' in the request."},
    {"id": "C2", "candidate": "Race between refill, check and decrement can over-issue.",
     "evidence": "All three occur inside a single 'with self._lock:' block in both methods; the clock is read inside the lock."},
    {"id": "C3", "candidate": "seconds_until calling _refill loses tokens.",
     "evidence": "_refill credits elapsed time before advancing _last, so extra calls are idempotent with respect to total tokens."},
    {"id": "C4", "candidate": "Raising ValueError for n > capacity violates the non-blocking requirement.",
     "evidence": "Raising is not blocking; the request leaves impossible n unspecified."}
  ]
}
```

`tools/validate_findings.py` was not run because no tools were available in this session.