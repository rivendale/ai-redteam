# pr-review: token bucket rate limiter

**Constraints of this session.** I have no tools, so I could not freeze a commit, check out a worktree, read commit trailers, or run the tests. Everything below comes from reading the code as pasted. Nothing was sent outside this session, and the code is a generic library that carries no personal data, so Step 3 is satisfied. This session did not write the change, so a review here meets Step 4's independence rule.

## Review report

**REVIEWED:** PR number not provided. Head SHA and merge base SHA were not provided and cannot be determined without tools. The review covers the two files exactly as pasted: `token_bucket.py` and `test_token_bucket.py`. If the PR head differs from this text, the difference was not reviewed.

**TIER:** Standard. This is ordinary library code with no auth, secrets, network exposure, migrations, money movement or personal data, and the context says "standard". One round was run.

**REVIEWERS:**
- Reviewer: this instance (Opus 5.5, `claude-opus-5-5`), one round.
- Author: unknown, because the commit trailers were not available.

**Claim not verified:** "7 tests, all pass." I could not run them. I counted 7 test methods in the file.

**Requirements check:**

| Requirement | Met? |
|---|---|
| Capacity N | Yes |
| Refill R per second | Yes |
| Thread-safe | Yes, with a single lock around refill and take |
| Injectable clock | Yes |
| `try_acquire(n)` never blocks | Yes, apart from brief lock contention |
| Method reporting time until n tokens are available | Yes, `seconds_until` |
| Tests included | Yes |

Nothing extra was added beyond the request. Findings follow.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `token_bucket.py` `_refill` (`elapsed = now - self._last`) together with the `self._tokens >= n` check in `try_acquire` | `seconds_until` and `try_acquire` can disagree because of floating-point rounding. Example: `TokenBucket(5, 3, clock)` at t=100.0, drained to 0 tokens. `seconds_until(1)` returns `1/3`. The caller advances the clock by exactly that amount, but `100.0 + 1/3` is rounded to the clock's precision (ulp about 1.4e-14 near 100). So `elapsed * 3` can come out as `0.99999999999998…` and `try_acquire(1)` returns False. A caller using the natural pattern `sleep(seconds_until(n)); try_acquire(n)` then fails and re-polls with a tiny wait. That breaks the contract the method exists for. Evidence: reasoned from IEEE-754 arithmetic, not executed. Whether a given rate/time pair rounds down depends on the values. | For many rates (1, 3, 7, 0.3, 1e3) and start times (0, 100, 1e6): drain the bucket, then `clock.t += b.seconds_until(1)`, then `assertTrue(b.try_acquire(1))`. Fix: compare with a small tolerance (`self._tokens + 1e-9 * n >= n`), or have `seconds_until` round up slightly so that waiting the reported time is always enough. |
| 2 | P3 | `token_bucket.py` constructor validation and the `n` checks in `try_acquire` / `seconds_until` | NaN passes every guard, because `nan <= 0` and `nan > capacity` are both False. `try_acquire(float('nan'))` returns False forever and `seconds_until(float('nan'))` returns `nan`. A caller doing `sleep(nan)` gets a `ValueError` far from the cause. `TokenBucket(float('nan'), 1)` is also accepted and never grants a token. | `assertRaises(ValueError)` for `try_acquire(nan)`, `seconds_until(nan)`, `TokenBucket(nan, 1)` and `TokenBucket(1, nan)`. Fix: use `math.isfinite`, or the positive form `if not (0 < n <= self.capacity)`, which rejects NaN. |
| 3 | P3 | `token_bucket.py` `_refill` (the `if elapsed > 0` branch never moves `_last` backwards) | If an injected clock steps back and stays back, the bucket grants no tokens until the clock catches up to the old `_last`. Example: someone injects `time.time` and NTP steps it back 1 hour, which starves the caller for an hour. The default `time.monotonic` is not affected, which is why this is P3. The current test pins this behaviour as intended. | Set the clock back by 3600 and stay there, advance by 1.0, and assert tokens became available. Fix option: when `elapsed < 0`, set `_last = now` without adding tokens. The existing backwards-clock test still passes with that change. Whether to make it is an owner decision. |
| 4 | P3 | `test_token_bucket.py` `test_threads_never_over_issue` | This test cannot detect a missing lock. The clock is constant and the rate is near zero, so no refill happens. Each acquire is a short check-and-decrement that the GIL makes very unlikely to interleave. Removing the `with self._lock:` would almost certainly still pass, so the "thread-safe" requirement is effectively untested. | Make the test sensitive to a missing lock: use a clock that advances on every call and a barrier to start the threads together, run many iterations, and assert the total taken is ≤ capacity + rate × elapsed. Or temporarily replace the lock with a no-op and confirm the test fails, so the test is shown to detect the bug. |
| 5 | P3 | `test_token_bucket.py` `test_seconds_until` (second assertion) and `test_bad_arguments` | Several behaviours are untested, so a regression in any of them would pass: <br>• `seconds_until(0.0001) > 0` is trivially true with 0 tokens. <br>• Nothing checks that `seconds_until` returns `0.0` when tokens are available. <br>• Nothing checks that waiting the reported time actually makes `try_acquire` succeed (this would have caught #1). <br>• Nothing checks `refill_per_sec <= 0`, `n <= 0`, or `seconds_until` argument validation. | Add assertions for: `seconds_until(1) == 0.0` on a full bucket, wait-then-acquire succeeds, `TokenBucket(1, 0)` raises, `try_acquire(0)` raises, and `seconds_until(6)` raises. |

No P0 or P1 found. Locking, refill capping, and the never-block behaviour are correct as written.

**FILES NEEDED BUT NOT PROVIDED:**
- PR metadata: number, head SHA, merge base.
- Commit trailers.
- CI configuration and check results.
- Any callers of this library in the codebase.

## Close-out

A reviewer does not adjudicate its own findings, so this section is left for the author or closer.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | pending (author) | |
| 2 | pending (author) | |
| 3 | pending (author or owner decision on clock semantics) | |
| 4 | pending (author) | |
| 5 | pending (author) | |

**VERIFIED AFTER FIXES:** None yet. No fixes have been made.

**MERGE RECOMMENDATION:** Merge after fixes. The code has no blockers. The P2 (#1) should be fixed or deferred with a tracking issue, and the P3s should be adjudicated. Step 8 is not yet satisfied for these reasons:
- The PR and head SHA are unrecorded.
- No CI checks were seen, and a missing check is not green.
- All findings are still unadjudicated.
- The clock-semantics decision (#3) is pending.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "reasoned (IEEE-754 rounding analysis; not executed)",
      "location": "token_bucket.py:_refill (elapsed = now - self._last) and try_acquire (self._tokens >= n)",
      "scenario": "seconds_until(n) returns missing/rate, but advancing the clock by exactly that value can yield elapsed*rate slightly below the missing amount because of float rounding at non-zero clock values (e.g. rate=3, t=100.0, 1/3 s). try_acquire(n) then returns False right after the reported wait, breaking the sleep(seconds_until(n)); try_acquire(n) pattern.",
      "fix": "Compare with a small tolerance (self._tokens + 1e-9*n >= n) or round seconds_until up slightly; add a test that waits the reported time across several rates and start times and asserts acquisition succeeds."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned (Python NaN comparison semantics)",
      "location": "token_bucket.py: __init__ validation, try_acquire and seconds_until n checks",
      "scenario": "NaN passes every guard: try_acquire(nan) always returns False, seconds_until(nan) returns nan (sleep(nan) raises later, far from the cause), and TokenBucket(nan, 1) is accepted and never grants a token.",
      "fix": "Validate with `if not (0 < n <= self.capacity)` and math.isfinite for capacity and rate; add assertRaises tests for NaN inputs."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned from code",
      "location": "token_bucket.py:_refill (if elapsed > 0)",
      "scenario": "An injected non-monotonic clock that steps back and stays back (e.g. time.time after an NTP correction) starves the bucket until the clock passes the old _last; the default time.monotonic is unaffected.",
      "fix": "On elapsed < 0, set _last = now without adding tokens (the existing backwards-clock test still passes); this is an owner decision on clock semantics."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned from test code",
      "location": "test_token_bucket.py:test_threads_never_over_issue",
      "scenario": "The clock is constant and the rate is about 0, and the GIL makes the check-and-decrement unlikely to interleave, so removing the lock would almost certainly still pass; thread safety is effectively untested.",
      "fix": "Use an advancing clock, a barrier and many iterations, assert taken <= capacity + rate*elapsed, and confirm the test fails with a no-op lock."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned from test code",
      "location": "test_token_bucket.py:test_seconds_until and test_bad_arguments",
      "scenario": "The second seconds_until assertion is trivially true; there is no test for 0.0 when tokens are available, none that waiting the reported time works, and none for refill<=0, n<=0 or seconds_until validation, so regressions there would pass.",
      "fix": "Add assertions for seconds_until on a full bucket, wait-then-acquire success, TokenBucket(1, 0), try_acquire(0) and seconds_until(capacity+1)."
    }
  ]
}
```