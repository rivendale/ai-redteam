# Redteam review: token bucket rate limiter

**VERDICT: SHIP WITH FIXES.** The implementation meets every part of the request, and I found no Critical or High defect. Two Low/Medium gaps are worth closing: NaN slips past argument validation, and the tests leave the "available now" branch of `seconds_until` and its argument checks unexercised.

**CONFIDENCE: medium.** Nothing was run in this session, so all behaviour was traced by hand. The work was not written in this conversation, but no fresh-subagent seat was available. The thread-safety test's strength and one float-boundary case remain unverified.

**INPUTS LEDGER:**
- **Seen:** the original request (verbatim), `context.md`, `token_bucket.py` and `test_token_bucket.py`.
- **Not seen:** the test run output. The context says "7 tests, all pass". I counted 7 tests and hand-traced each to pass, but I did not run them. This matters only a little.

**COVERAGE:**
- **Checked:** `token_bucket.py` (`__init__`, `_refill`, `try_acquire`, `seconds_until`) and all 7 tests in `test_token_bucket.py`. Each requirement was checked: capacity N, refill R, thread safety, injectable clock, non-blocking acquire, wait-time method, and tests.
- **Not checked:** runtime behaviour (no tools), and behaviour under free-threaded (no-GIL) Python.

**SEATS AND GATE:** a single local reviewer with no tools; no cross-vendor seats. The sensitivity gate passed: there is no personal or confidential data.

## Pass 1: Reconstruct

The work is a float-based token bucket:
- It starts full and refills lazily by `elapsed * rate`, capped at capacity.
- A clock that goes backwards is ignored, because `_last` only moves forward.
- `try_acquire` and `seconds_until` both refill and read under one `threading.Lock`.
- Both reject `n` outside `(0, capacity]` with `ValueError`.

For this to be correct, four things must hold:
- The lock must serialise every read and write of `_tokens` and `_last`.
- The injected clock must be monotonic in normal use.
- Float accumulation must be accurate enough.
- Callers must accept that `n > capacity` raises rather than returning False.

Track: B.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | B | `test_token_bucket.py` (`test_seconds_until`, `test_bad_arguments`) | Several requested behaviours are untested: `seconds_until` returning `0.0` when tokens are available, `seconds_until` argument validation, `refill_per_sec <= 0`, and `n <= 0`. | A refactor that returns a negative wait when tokens are available (dropping `0.0 if missing <= 0`), or removes validation from `seconds_until`, passes all 7 tests. | Add tests:<br>• `assertEqual(self.b.seconds_until(1), 0.0)` on a full bucket.<br>• `assertRaises(ValueError)` for `seconds_until(0)`, `seconds_until(6)`, `TokenBucket(1, 0)` and `try_acquire(0)`.<br>Reproduction: change line `return 0.0 if missing <= 0 else ...` to `return missing / self.rate`; all current tests still pass. | a✓ b✓ c✗ d✗ |
| F2 | Low | CONFIRMED | B | `token_bucket.py:8`, `:24`, `:34` (the `<= 0` / `> capacity` checks) | NaN passes validation, because every comparison with NaN is False. The constructor also accepts `inf` and `nan` for capacity and rate. | If `n` is computed from bad data as `nan`:<br>• `try_acquire(nan)` silently returns False forever.<br>• `seconds_until(nan)` returns `nan` instead of raising.<br>`TokenBucket(float('inf'), 1)` never limits anything. | Write the checks positively: `if not (0 < n <= self.capacity): raise ValueError` (this rejects NaN). In `__init__`, require `math.isfinite` and `> 0` for both arguments.<br>Reproduction: `TokenBucket(5, 2, clock=lambda: 0.0).try_acquire(float('nan'))`. Expected `ValueError`; observed `False`. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION

- **S1 — thread-safety test may not catch a missing lock** (`test_threads_never_over_issue`). The race window is tiny: under the CPython GIL, 400 attempts across 8 threads may never interleave inside `if self._tokens >= n: self._tokens -= n`. The test may stay green with the lock removed. **What settles it:** in a scratch copy, delete `with self._lock:` and run the test about 50 times. If it never goes red, add a deterministic race check (for example, a clock that calls `time.sleep(0)` or yields to force interleaving), or assert the invariant with a barrier-synchronised start.
- **S2 — float boundary on wait-then-acquire** (`token_bucket.py:18`, `:38`). With a large clock base (fake clock at `t=100.0`) and a rate such as 3/s, `seconds_until(1)` returns `1/3`. Then `elapsed = (100.0 + 1/3) - 100.0` may round below `1/3`, giving tokens `0.99999999999998…` and making the next `try_acquire(1)` return False. **What settles it:** evaluate `TokenBucket(5, 3, clock=c)` with the clock at 100.0. Drain it, advance by `b.seconds_until(1)`, then call `try_acquire(1)`. If this fails, add a small epsilon (for example `self._tokens + 1e-9 >= n`) or keep the count in integer nanotokens.

## REFUTED

- **R1 — "`try_acquire` can block on the lock, violating 'never blocks'."** The lock is held only for a constant-time refill plus compare, so contention is bounded and brief. That is standard for a "non-blocking" limiter, and the request means no waiting for tokens. One caveat stays with the caller: a slow injected clock is called inside the lock.
- **R2 — "Clock going backwards could mint or lose tokens."** `_refill` only updates when `elapsed > 0`, so `_last` stays at the high-water mark. No tokens are credited for the backwards period, and none are lost. `test_clock_going_backwards_is_ignored` traces correctly: 0 tokens at t=50, then 1 token at t=100.5.
- **R3 — "Raising on `n > capacity` breaks the contract."** A request larger than capacity can never succeed. Raising is a defensible, explicit choice and is tested. Returning `float('inf')` from `seconds_until` would also be reasonable, but this is not a defect.

## WHAT HOLDS UP

- **Requirement fit is complete:** capacity and rate, injectable clock (all tests use a fake clock and none sleep), a non-blocking boolean acquire, `seconds_until`, and tests.
- **The refill math is correct:** lazy refill, capped with `min`, no overflow concern because of the cap.
- **Every mutation of `_tokens` and `_last` happens under one lock,** and validation outside the lock reads only immutable fields.
- **Hand traces of all 7 tests pass:**
  - starts full
  - 2 tokens after 1 s
  - capped at 5 after 1000 s
  - backwards clock
  - wait 0.5 s for 1 token
  - `ValueError` cases
  - exactly 100 issued with a frozen clock

## UNVERIFIED CLAIMS

- **"7 tests, all pass":** hand-traced only. Confirm by running `python -m unittest test_token_bucket`.
- **Thread safety:** confirmed by reading; whether the test proves it is open (see S1).

## QUESTIONS FOR THE AUTHOR

1. Should `seconds_until(n > capacity)` return `inf` rather than raise?
2. Is wait-then-acquire with exactly the reported delay expected to succeed? If so, S2 needs an epsilon.

## Summaries

**DECISION-MAKER SUMMARY:** The limiter is correct and does what was asked, so it can ship. Before release, add the missing tests (F1) and tighten argument validation (F2), and check whether the threading test can actually detect a missing lock. Shipping as is risks little now, but a future regression in the wait-time method or the locking would not be caught.

**OWNER SUMMARY:** The rate limiter works as requested and is safe to use. A few small gaps should be closed first: some behaviours have no tests, and a malformed input value is quietly accepted instead of rejected. One test may not be strong enough to catch a future concurrency mistake.

## Machine-readable report

Schema 2.2. The validator could not be run in this session.

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
    {"item": "test run output", "status": "not_seen", "matters": false}
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
      {"unit": "runtime execution of tests", "reason": "no tools in this session"},
      {"unit": "free-threaded (no-GIL) Python behaviour", "reason": "no tools; out of scope"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_token_bucket.py:test_seconds_until, test_bad_arguments",
     "scenario": "A regression making seconds_until return a negative value when tokens are available, or dropping its argument validation, passes all 7 tests.",
     "fix": "Add tests: seconds_until(1) == 0.0 on a full bucket; ValueError for seconds_until(0), seconds_until(6), TokenBucket(1, 0), try_acquire(0).",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Replace 'return 0.0 if missing <= 0 else missing / self.rate' with 'return missing / self.rate'; run the suite; all 7 tests still pass."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "token_bucket.py:8, 24, 34",
     "scenario": "try_acquire(float('nan')) passes validation and returns False forever; seconds_until(nan) returns nan; TokenBucket(inf, 1) never limits.",
     "fix": "Use 'if not (0 < n <= self.capacity): raise ValueError' and require math.isfinite and > 0 for capacity and rate in __init__.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "TokenBucket(5, 2, clock=lambda: 0.0).try_acquire(float('nan')): expected ValueError, observed False."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "test_token_bucket.py:test_threads_never_over_issue",
     "suspicion": "Under the GIL the test may pass with the lock removed, so it may not guard thread safety.",
     "unresolved_fact": "Whether the test goes red in a scratch copy with 'with self._lock:' removed, over ~50 runs."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "token_bucket.py:18, 38",
     "suspicion": "Sleeping exactly seconds_until(n) then try_acquire(n) may fail due to float rounding at a large clock base.",
     "unresolved_fact": "Whether, at clock 100.0 and rate 3, advancing by seconds_until(1) yields tokens >= 1.0."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Lock acquisition makes try_acquire blocking.", "evidence": "Critical section is constant-time; the request's 'never block' means not waiting for tokens."},
    {"id": "R2", "candidate": "Backwards clock mints or loses tokens.", "evidence": "_refill updates only when elapsed > 0; _last stays at the high-water mark; the test traces correctly."},
    {"id": "R3", "candidate": "Raising on n > capacity breaks the contract.", "evidence": "Such a request can never succeed; an explicit ValueError is defensible and tested."}
  ]
}
```