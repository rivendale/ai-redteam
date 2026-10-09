# Redteam report: token bucket rate limiter

**VERDICT: SHIP WITH FIXES.** The limiter meets the request and has no High or Critical defect. Two Medium weaknesses should be fixed first: `seconds_until` can under-report the wait because of float rounding, and the thread-safety test probably cannot fail.

**CONFIDENCE: medium.** I had no tools, so nothing was run. Every trace and number below was worked out by hand. I did not write this work, but this is a single review, not a fresh subagent or extra reviewers.

**INPUTS LEDGER**
- Seen: the original request, the context, `token_bucket.py` and `test_token_bucket.py`.
- Not seen: the test run output behind "7 tests, all pass". This matters a little: I traced all 7 by hand and expect them to pass, but that is unverified.
- Not seen: the target Python version. This does not matter; nothing here depends on the version.

**COVERAGE**
- Checked: `TokenBucket.__init__`, `_refill`, `try_acquire` and `seconds_until`, and all 7 tests. Hostile inputs traced: n ≤ 0, n > capacity, NaN, inf, a clock going backwards, very large elapsed time, a constant clock, and concurrent callers.
- Not checked: actual execution, timing under real thread contention, and behaviour on other Python runtimes such as free-threaded builds.

**SEATS AND GATE:** One local reviewer, with no tools and no subagent. No other vendors' models were used: none were requested, and the stakes are standard. The sensitivity gate passed; the work contains no personal or confidential data.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | PROBABLE (hand-computed float arithmetic) | B | `token_bucket.py` `seconds_until`: `return ... missing / self.rate`; `try_acquire`: `if self._tokens >= n` | The wait it reports is the exact real-number answer. Converting it back into tokens through `now - self._last` loses precision, so after waiting exactly the reported time, fewer than n tokens may be available. | Capacity 3, rate 3, `FakeClock` at 100.0. Take 3 tokens. `seconds_until(1)` returns 0.3333333333333333. Advance the clock by that amount: 100 + 1/3 rounds down to a multiple of 2⁻⁴⁶, so elapsed is about 0.33333333333332860 and the refill is about 0.9999999999999858. `try_acquire(1)` returns False, breaking the documented meaning of `seconds_until`. With `time.monotonic` at large uptimes the rounding step is larger, so a "sleep then acquire" caller often needs an extra loop. | Repro: the setup above, then `self.clock.t += b.seconds_until(1)`, then `assertTrue(b.try_acquire(1))`. I predict it goes red. Fix: use a small tolerance in both methods, e.g. `_EPS = 1e-9`, check `self._tokens + _EPS >= n`, and compute `missing = n - self._tokens - _EPS`. Alternatively, keep tokens in integer sub-units. | a✓ b✗ c✗ d✓ |
| F2 | Medium | PROBABLE | B (tests) | `test_threads_never_over_issue` | The race it guards is between the `self._tokens >= n` check and the `-= n` update. That window is a few bytecodes, while the GIL switches threads only every 5 ms by default. With the lock removed, this test would very likely still pass, so it gives no evidence that the code is thread-safe. | Someone later removes or narrows the lock, for example by moving `_refill` outside it. CI stays green and over-issuing reaches production under real contention. | Run the mutation in a scratch copy: delete `with self._lock:` and confirm the test goes red. If it stays green, strengthen the test: call `sys.setswitchinterval(1e-6)` during it, and inject a clock that runs `time.sleep(0)` to widen the window. Also start the threads together behind a `threading.Barrier`. | a✓ b✗ c✗ d✓ |
| F3 | Low | CONFIRMED (line trace) | B | Validation in `__init__`, `try_acquire` and `seconds_until`: `n <= 0 or n > self.capacity` | NaN passes every check because all comparisons with NaN are False. | `TokenBucket(float('nan'), 1)` is accepted, and every later acquire returns False. `seconds_until(float('nan'))` returns `nan`, and a caller passing that to `time.sleep` gets a `ValueError` far from the cause. | Add `if not (math.isfinite(n) and 0 < n <= self.capacity)`. Require a finite, positive capacity and rate in `__init__`. Test: `assertRaises(ValueError, b.try_acquire, float('nan'))`. | a✓ b✓ c✗ d✗ |
| F4 | Low | CONFIRMED (read) | B (tests) | `test_clock_going_backwards_is_ignored`, `test_seconds_until`, `test_bad_arguments` | The tests do not pin down some of the behaviour they name. (1) The backwards-clock test would also pass if `_last` were reset to the earlier time on a backward step, which is the variant where an oscillating clock creates tokens. At t=100.5, refilling from 50 still gives True. (2) The `0.0` path of `seconds_until`, its argument checks, `try_acquire(0)` and a refill rate of `0` are never exercised. | A future refactor resets `_last` on backward steps or breaks the zero-wait path, and the suite stays green. | (1) Repro: step the clock back 50, call `try_acquire()`, advance 50.5, then assert `try_acquire(2)` is False. With the reset mutation it would be True. (2) Add tests: `assertEqual(b.seconds_until(1), 0.0)` on a full bucket, `assertRaises(ValueError, b.seconds_until, 6)`, `assertRaises(ValueError, TokenBucket, 5, 0)`, and `assertRaises(ValueError, b.try_acquire, 0)`. | a✓ b✓ c✗ d✗ |

**NEEDS VALIDATION**
- **S1. "7 tests, all pass."** My hand trace says yes. What would settle it: the output of `python -m unittest test_token_bucket`.
- **S2. Whether the concurrency test would catch a missing lock.** This is the open half of F2. What would settle it: the result of the lock-removal mutation run in a scratch copy.

**REFUTED**
- **"A backward clock step loses refill time."** The default clock is `time.monotonic`, which never goes backwards. Ignoring backward steps is deliberate (it is named in a test) and is the safe choice, because it never creates tokens. The only cost is that an injected wall clock such as `time.time` stalls refill until it catches up. That is worth one docstring line, not a finding.
- **"`try_acquire(n > capacity)` raising violates 'never blocks'."** Raising an exception is not blocking, and n > capacity can never succeed. Raising is a defensible contract and `seconds_until` matches it.
- **"Thread-unsafe."** Every read and write of `_tokens` and `_last` after construction happens under `self._lock`. `capacity` and `rate` are read outside the lock, but they are never written after `__init__`.

## What holds up
- The refill logic is correct, including the cap at capacity and huge elapsed times (an infinite refill is clamped by `min`).
- `try_acquire` never blocks: the lock is held only for O(1) work.
- The clock is injectable and the tests use it without sleeping.
- `seconds_until` returns 0 when n tokens are available now and `missing / rate` otherwise.
- I traced all 7 tests by hand and they match the implementation.
- The scope matches the request, with nothing extra.

## Unverified claims
- **"Tests all pass."** Confirm by running the suite (S1).
- **"Thread-safe" as shown by a test.** The code is safe by inspection (see the third refuted item), but the test proof needs the mutation run (S2).

## Questions for the author
1. Is the backwards-clock behaviour intended to be "stall until the clock catches up"? If so, document it, especially for injected wall clocks.
2. Should `seconds_until` guarantee that `try_acquire` succeeds right after the wait, ignoring other threads? If yes, F1 must be fixed rather than just documented.

## Decision-maker summary
The limiter is correct and fit to use. Before relying on it, fix the rounding issue (F1) and make the concurrency test actually able to fail (F2). If you skip these, callers that sleep for the reported wait will sometimes find the tokens not yet available, and a future change that breaks locking would pass CI unnoticed.

## Owner summary
The rate limiter works and does what was asked. Two small fixes are recommended first: the "how long to wait" answer can be off by a tiny fraction, and the multi-threading test is too weak to catch the bug it is meant to catch. Neither causes harm today, but both are cheap to fix now.

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
    {"item": "test run output", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "token_bucket.py", "kind": "file"},
      {"unit": "token_bucket.py:TokenBucket.__init__", "kind": "function"},
      {"unit": "token_bucket.py:TokenBucket._refill", "kind": "function"},
      {"unit": "token_bucket.py:TokenBucket.try_acquire", "kind": "function"},
      {"unit": "token_bucket.py:TokenBucket.seconds_until", "kind": "function"},
      {"unit": "test_token_bucket.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "test execution", "reason": "no tools in this session"},
      {"unit": "behaviour under free-threaded or non-CPython runtimes", "reason": "no tools; out of scope"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "token_bucket.py:seconds_until (missing / self.rate) and try_acquire (self._tokens >= n)",
     "scenario": "Capacity 3, rate 3, clock at 100.0; after taking all tokens, advancing the clock by seconds_until(1) yields a refill of about 0.9999999999999858, so try_acquire(1) returns False.",
     "fix": "Use a small tolerance (e.g. 1e-9) in both comparisons, or track tokens in integer sub-units.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "FakeClock t=100.0, TokenBucket(3, 3); try_acquire(3); clock.t += seconds_until(1); assertTrue(try_acquire(1)); expect pass, predicted fail."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "test_token_bucket.py:test_threads_never_over_issue",
     "scenario": "The lock is removed in a refactor; the check-then-decrement race window is far shorter than the GIL switch interval, so the test stays green and over-issuing ships.",
     "fix": "Set sys.setswitchinterval(1e-6), inject a clock that calls time.sleep(0), and start threads behind a Barrier; prove the test goes red with the lock removed.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "In a scratch copy, delete 'with self._lock:' and run the test; a valid test must fail."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "token_bucket.py: validation in __init__, try_acquire and seconds_until",
     "scenario": "NaN passes the checks because NaN comparisons are False; seconds_until(nan) returns nan and a later time.sleep(nan) raises far from the cause.",
     "fix": "Require math.isfinite and 0 < n <= capacity; validate capacity and rate the same way.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "b.seconds_until(float('nan')) returns nan; expected ValueError."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_token_bucket.py: test_clock_going_backwards_is_ignored, test_seconds_until, test_bad_arguments",
     "scenario": "A refactor that resets _last on a backward clock step (minting tokens), or breaks the 0.0 path of seconds_until or its validation, keeps the suite green.",
     "fix": "After the backward step and forward 50.5, assert try_acquire(2) is False; add tests for seconds_until == 0.0 on a full bucket, seconds_until(6) raising, try_acquire(0) raising and TokenBucket(5, 0) raising.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Mutate _refill to set self._last = now on a negative elapsed time; the current suite stays green."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "context.md",
     "suspicion": "The claim '7 tests, all pass' was not observed.",
     "unresolved_fact": "Output of python -m unittest test_token_bucket."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "test_token_bucket.py:test_threads_never_over_issue",
     "suspicion": "The concurrency test cannot detect a missing lock.",
     "unresolved_fact": "Result of the lock-removal mutation run in a scratch copy."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "A backward clock step loses refill time.",
     "evidence": "The default clock is time.monotonic; ignoring backward steps is deliberate, tested and safe because it never creates tokens."},
    {"id": "C2", "candidate": "Raising ValueError for n > capacity violates 'never blocks'.",
     "evidence": "Raising is not blocking, n > capacity can never succeed, and seconds_until has the same contract."},
    {"id": "C3", "candidate": "State is accessed without the lock.",
     "evidence": "All reads and writes of _tokens and _last after construction are inside self._lock; capacity and rate are never written after __init__."}
  ]
}
```