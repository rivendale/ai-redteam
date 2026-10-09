VERDICT: **SHIP WITH FIXES.** The limiter meets the request and the core logic is correct, but `seconds_until` can report a wait that is too short, and the thread-safety test probably cannot fail.

CONFIDENCE: **medium.** I had no tools: nothing was run, and the "7 tests, all pass" claim comes from the context, not from me. The finding about `seconds_until` was recomputed by hand in IEEE-754 doubles. I did not author the work, but this is one reviewer and no second seat ran.

INPUTS LEDGER:
- **Seen:** `request.md` (verbatim), `context.md`, `token_bucket.py`, `test_token_bucket.py`.
- **Not seen:** test run output and the Python version, which decides whether a GIL is present. This matters for F2 only.

COVERAGE:
- **Checked:**
  - `token_bucket.py`: `__init__`, `_refill`, `try_acquire`, `seconds_until`.
  - All 7 tests. The count of 7 matches the context.
  - Requirement fit for each clause of the request.
- **Not checked:** runtime behaviour, free-threaded (no-GIL) builds, and performance under contention.

SEATS AND GATE: one reviewer (this session), no tools. No external seats ran. Sensitivity gate passed: no personal or confidential data.

## Pass 1: Reconstruct
The work is a token bucket that starts full and refills continuously at `rate` tokens per second, capped at `capacity`. It uses an injectable clock and ignores clock values that go backwards. `try_acquire(n)` returns a bool without waiting for tokens. `seconds_until(n)` returns `max(0, n - tokens) / rate`. A single `threading.Lock` guards the state.

For this to be correct:
- The state must only change under the lock.
- The float arithmetic must keep `seconds_until` consistent with `try_acquire`.
- The tests must actually exercise the guarded behaviour.

Track: B.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (hand-recomputed in IEEE-754) | B | `token_bucket.py` `seconds_until`, last line; `_refill` `elapsed * self.rate` | The returned wait can be 1 ulp short. Advancing the clock by exactly that amount refills slightly less than `n`, so the promised tokens are not available. | `TokenBucket(5, 3, clock)` with the clock at 100.0. Take 5 tokens, so tokens = 0.0 exactly. `seconds_until(1)` returns `0.3333333333333333`. `clock.t += that` rounds to 100 + (2⁴⁶−1)/3·2⁻⁴⁶, so elapsed is slightly below 1/3 and tokens = 1 − 2⁻⁴⁶ < 1. `try_acquire(1)` then returns **False**. A "wait the reported time, then acquire" loop fails once, and a fake-clock test of that pattern fails. | Fix: compare with a tolerance (`self._tokens + 1e-9 >= n`, clamping tokens at ≥ 0 after the subtraction), or document the result as a lower bound. Reproduction test: `b=TokenBucket(5,3,clock=c); b.try_acquire(5); c.t += b.seconds_until(1); assert b.try_acquire(1)`, which fails on the current code. | a Y / b Y / c N / d N |
| F2 | Medium | PROBABLE | B | `test_token_bucket.py` `test_threads_never_over_issue` | The test probably stays green with the lock removed. 8 threads × 50 tiny iterations under the GIL (5 ms switch interval) likely run almost one after another, so the read-modify-write on `_tokens` never interleaves. The thread-safety requirement is then effectively untested. | Someone refactors and drops `with self._lock`. CI stays green, and over-issue appears in production under real contention. | Mutation check (in a scratch copy): delete the lock and run the test about 1000 times. If it never goes red, add a contention trigger, for example a clock callable that calls `time.sleep(0)` or yields between read and write, or a `threading.Barrier` plus many more iterations, and lower `sys.setswitchinterval`. | a Y / b N / c N / d Y |
| F3 | Low | CONFIRMED (IEEE NaN comparison semantics) | B | `token_bucket.py` `__init__` validation; `try_acquire` / `seconds_until` `if n <= 0 or n > self.capacity` | NaN passes every check, because every comparison with NaN is False. | `try_acquire(float('nan'))` returns False forever with no error, and `seconds_until(nan)` returns `nan`. `TokenBucket(float('nan'), 1)` builds a bucket that never grants anything. | Use `if not (0 < n <= self.capacity)` and `if not (capacity > 0 and refill_per_sec > 0)`, which reject NaN. Test: `assertRaises(ValueError, b.try_acquire, float('nan'))`. | a Y / b Y / c N / d N |
| F4 | Low | CONFIRMED (read) | B | `test_seconds_until`, `test_bad_arguments` | Several cases are missing or weak: the `0.0` return path of `seconds_until`, a partial-refill value, "wait then acquire succeeds" (which would have caught F1), `n <= 0`, `refill_per_sec <= 0`, and the validation in `seconds_until`. The assertion `seconds_until(0.0001 + 0) > 0` only checks the sign. | A regression in the "available now" branch, or in rejecting `n <= 0` or a zero rate, passes CI. | Add `assertEqual(b.seconds_until(1), 0.0)` on a full bucket, a partial-refill value check, the F1 round-trip, and `assertRaises` for `try_acquire(0)`, `TokenBucket(1, 0)` and `seconds_until(6)`. | a Y / b Y / c N / d N |

## NEEDS VALIDATION
- **F2 under free-threaded CPython (3.13t+).** The lock is correct there, but the test's ability to catch a missing lock depends on the build. To settle it, I need the target interpreter and a run of the mutation from F2.

## REFUTED
- **"`try_acquire` blocks because it takes a lock."** In rate-limiter terms, "never block" means never waiting for tokens. The critical section is O(1) and has no waits. One remaining edge: the injected clock is called inside the lock, so a slow clock would hold the lock. That is contrived with `time.monotonic`.
- **"Refill is lost because `_last` advances on every call while tiny `elapsed*rate` rounds away."** This needs `elapsed*rate` below about 1e-16 × tokens on every call, which is unrealistic for any practical rate and polling interval.
- **"A backwards clock corrupts state."** `elapsed > 0` leaves both tokens and `_last` unchanged, so refill resumes from the old high-water mark. The test covers this correctly.

## WHAT HOLDS UP
- Every request clause is met: capacity, rate, lock-guarded state, injectable clock, non-waiting `try_acquire`, `seconds_until`, and tests. There is nothing extra.
- The refill is capped at capacity and an overflow to inf is clamped.
- `seconds_until` refills under the lock before computing.
- Validation runs outside the lock but uses immutable-in-practice fields.
- The FakeClock tests are deterministic and assert real values: 0.5 s, and 2 tokens after 1 s.

## UNVERIFIED CLAIMS
- **"7 tests, all pass."** The count matches; the pass result was not run. Run `python -m unittest -v`.

## QUESTIONS FOR THE AUTHOR
1. Is `seconds_until` meant as an exact guarantee or a lower bound? This decides whether F1 needs a code fix or a docstring.
2. Which Python builds must be supported? This decides whether F2's test rewrite is needed.

## DECISION-MAKER SUMMARY
The limiter is correct in normal use and can ship once two cheap fixes land: a tolerance so the reported wait is never too short (F1), and a thread test proven to fail without the lock (F2). If shipped as-is, callers that wait exactly the reported time will occasionally be refused. A future change that removes locking would also pass CI unnoticed.

## OWNER SUMMARY
The rate limiter works and does what was asked. Two small issues should be fixed first. The "how long to wait" answer can be a hair too short because of rounding, and the test meant to prove it is safe with many threads probably could not catch a mistake. Both are quick changes with no risk to existing behaviour.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "token_bucket.py", "status": "seen", "matters": true},
    {"item": "test_token_bucket.py", "status": "seen", "matters": true},
    {"item": "test run output / Python version", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "token_bucket.py", "kind": "file"},
      {"unit": "token_bucket.py:__init__", "kind": "function"},
      {"unit": "token_bucket.py:_refill", "kind": "function"},
      {"unit": "token_bucket.py:try_acquire", "kind": "function"},
      {"unit": "token_bucket.py:seconds_until", "kind": "function"},
      {"unit": "test_token_bucket.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "runtime test execution", "reason": "no tools in session"},
      {"unit": "free-threaded CPython behaviour", "reason": "no tools; target interpreter not stated"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "token_bucket.py:seconds_until (return missing / self.rate) and _refill (elapsed * self.rate)",
     "scenario": "TokenBucket(5, 3) with fake clock at 100.0, drain 5; seconds_until(1)=0.3333333333333333; advancing the clock by that amount yields elapsed*3 = 1 - 2**-46 < 1, so try_acquire(1) returns False after the reported wait.",
     "fix": "Compare with a tolerance (self._tokens + 1e-9 >= n, clamp tokens >= 0) or document the value as a lower bound.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "b=TokenBucket(5,3,clock=c); b.try_acquire(5); c.t += b.seconds_until(1); assert b.try_acquire(1)  # fails on current code"},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "test_token_bucket.py:test_threads_never_over_issue",
     "scenario": "Under the GIL, 8 threads x 50 short iterations rarely interleave, so removing the lock likely leaves the test green and a thread-safety regression ships.",
     "fix": "Force contention (Barrier, more iterations, sys.setswitchinterval(1e-6), or a clock callable that yields) and confirm the test goes red with the lock removed.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "In a scratch copy delete 'with self._lock:' in try_acquire and run the test 1000 times; expected red, predicted green."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "token_bucket.py:__init__ and try_acquire/seconds_until validation 'if n <= 0 or n > self.capacity'",
     "scenario": "try_acquire(float('nan')) passes validation and returns False forever; seconds_until(nan) returns nan; TokenBucket(nan, 1) is accepted.",
     "fix": "Use 'if not (0 < n <= self.capacity)' and 'if not (capacity > 0 and refill_per_sec > 0)'.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "self.assertRaises(ValueError, b.try_acquire, float('nan'))  # fails on current code"},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_token_bucket.py:test_seconds_until, test_bad_arguments",
     "scenario": "Regressions in the seconds_until 0.0 path, partial-refill value, n<=0 rejection, zero-rate rejection or seconds_until validation pass CI.",
     "fix": "Add assertions for seconds_until==0.0 when full, a partial-refill value, the wait-then-acquire round trip, try_acquire(0), TokenBucket(1,0), seconds_until(6).",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Change seconds_until to always return missing/self.rate (drop the 0.0 branch); all 7 current tests still pass."},
    {"id": "S1", "status": "needs_validation", "track": "B",
     "location": "test_token_bucket.py:test_threads_never_over_issue",
     "suspicion": "On free-threaded CPython the test's sensitivity to a missing lock differs from GIL builds.",
     "unresolved_fact": "Target interpreter build and the result of the lock-removal mutation run on it."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "try_acquire blocks because it acquires a lock.",
     "evidence": "'Never block' means no waiting for tokens; the critical section is O(1) with no waits."},
    {"id": "C2", "candidate": "Frequent calls lose refill to float rounding as _last advances.",
     "evidence": "Requires elapsed*rate below ~1e-16 x tokens per call; unrealistic for practical rates and intervals."},
    {"id": "C3", "candidate": "A backwards clock corrupts bucket state.",
     "evidence": "_refill only acts when elapsed > 0, leaving tokens and _last untouched; covered by test_clock_going_backwards_is_ignored."}
  ]
}
```