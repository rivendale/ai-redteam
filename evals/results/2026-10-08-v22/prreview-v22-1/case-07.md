# pr-review: TokenBucket (token_bucket.py, test_token_bucket.py)

**Review report**

**REVIEWED:** The work was supplied inline, not as a PR. There is no PR number, head SHA or merge base SHA, so the exact commit cannot be recorded. This review covers only the two files as quoted. I had no tools, so nothing was run, including the claimed "7 tests, all pass". The file has 7 tests, but whether they pass is unverified.

**TIER:** Standard. This is an ordinary code change in a small shared library. It touches no auth, secrets, network exposure, personal data or money.

**REVIEWERS:** This session (Claude Opus 5.5, `claude-opus-5-5`) did not write the change, so the review is independent. The author is unknown because no commit trailers were provided.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `token_bucket.py` `_refill` (`elapsed * self.rate`) and `seconds_until` (`missing / self.rate`) | **The documented wait is not always enough.** The common pattern is "sleep `seconds_until(n)`, then `try_acquire(n)`", and it can fail.<br>• Example: `TokenBucket(5, 3)` with clock at `100.0`. Drain it. `seconds_until(1)` returns `1/3`.<br>• Advance the clock by exactly that: `100.0 + 1/3` rounds to `100.33333333333333`.<br>• In `_refill`, `elapsed = 0.33333333333332859…`, so tokens = `0.9999999999999858 < 1`, and `try_acquire()` returns False.<br>• A real `time.monotonic()` (often 1e5 to 1e6 s) loses even more precision.<br>• Result: callers get a spurious False and spin or re-sleep. This breaks the promise of the "how long until n tokens" method. | Use `FakeClock` at `t=100.0` and `TokenBucket(5, 3)`. Call `try_acquire(5)`, then `w = seconds_until(1)`, then `clock.t += w`, then `assertTrue(try_acquire())`. I expect this to fail today; reasoned, not run. Fix: compare with a small epsilon (e.g. `self._tokens + 1e-9 >= n`), or add a tiny margin to the returned wait, and keep `seconds_until`/`try_acquire` consistent. |
| 2 | P3 | `token_bucket.py` `_refill` (`if elapsed > 0:` leaves `_last` unchanged) | **A backward clock jump stalls refill.** If the injected clock (e.g. `time.time` under an NTP correction) jumps back by an hour, `_last` stays at the old value. The bucket then refills nothing for an hour, so the limiter starves all callers. The existing `test_clock_going_backwards_is_ignored` would also pass if `_last` were reset to `now` on a backward jump, so it does not pin this behaviour. | Drain the bucket, then `clock.t -= 3600`, then `clock.t += 1`, then `assertTrue(try_acquire())`. This fails today. Fix: on `elapsed < 0`, set `self._last = now` without adding tokens. |
| 3 | P3 | `token_bucket.py` `__init__`, `try_acquire`, `seconds_until` (validation `<= 0` / `> capacity`) | **NaN passes validation.**<br>• `float('nan')` passes every check.<br>• `try_acquire(nan)` then returns False forever.<br>• `seconds_until(nan)` returns `nan`, and `time.sleep(nan)` raises ValueError.<br>• `TokenBucket(nan, 1)` builds a bucket that can never issue tokens.<br>• `TokenBucket(5, inf)` is also accepted. | `assertRaises(ValueError)` for `try_acquire(float('nan'))`, `seconds_until(float('nan'))`, `TokenBucket(float('nan'), 1)` and `TokenBucket(5, float('inf'))`. Fix: use `math.isfinite` checks. |
| 4 | P3 | `test_token_bucket.py` `test_threads_never_over_issue` | **The thread-safety test is weak.** The check-then-decrement window is a few bytecodes, and threads mostly run serially under the GIL. With `self._lock` removed, this test will very likely still pass, so it does not prove thread safety. | Make the window observable. For example, use a clock that calls `time.sleep(0)` or yields on a barrier inside the critical section, or run `sys.setswitchinterval(1e-6)` with many more threads and iterations. Then confirm the test fails with the lock removed. |
| 5 | P3 | `test_token_bucket.py` `test_bad_arguments`, `test_seconds_until` | **Untested branches.** None of these are tested:<br>• `refill_per_sec <= 0`<br>• `n <= 0`<br>• `seconds_until(n > capacity)`<br>• `seconds_until` returning `0.0` when tokens are available<br>• a fractional `n` path<br>The second assertion in `test_seconds_until` (`> 0` for `0.0001`) is near-vacuous. | Add `assertRaises` for `TokenBucket(1, 0)`, `try_acquire(0)` and `seconds_until(6)`. On a full bucket, add `assertEqual(seconds_until(1), 0.0)`. |

Scope against the request: capacity, refill rate, lock, injectable clock, non-blocking `try_acquire` and a wait-time method are all present, and nothing extra is added. Finding 1 is the one place where the code does not meet the request.

**FILES NEEDED BUT NOT PROVIDED:** None needed to review the code. I lack the PR, commit SHAs and CI check results needed for Steps 1 and 8.

**Close-out**

The reviewer does not adjudicate its own findings. The author must give a decision on each of findings 1–5. Finding 1 is P2: it can be deferred with an issue link, but I recommend fixing it now, because it is a two-line change and is the core contract of `seconds_until`.

**MERGE RECOMMENDATION (provisional):** Merge after fixes. These are still open:
- Adjudication of findings 1–5.
- The head SHA and merge base, which were not supplied.
- CI checks present and green. The test pass claim is unverified.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "reasoned (float arithmetic traced by hand, not executed)",
      "location": "token_bucket.py:_refill / seconds_until",
      "scenario": "TokenBucket(5,3) at clock 100.0, drained; seconds_until(1)=1/3; advancing the clock by exactly that gives elapsed 0.33333333333332860, tokens 0.9999999999999858 < 1, so try_acquire() returns False right after the advertised wait.",
      "fix": "Compare with a small epsilon (tokens + 1e-9 >= n) or pad the returned wait; add a sleep-then-acquire regression test with a non-integer rate."
    },
    {
      "severity": "P3",
      "evidence_level": "code read",
      "location": "token_bucket.py:_refill (if elapsed > 0)",
      "scenario": "A large backward jump of an injected non-monotonic clock leaves _last in the future, so no refill happens until the clock catches up and the limiter starves callers; the existing test does not pin this.",
      "fix": "On elapsed < 0 set _last = now without adding tokens; test a 3600 s backward jump followed by +1 s."
    },
    {
      "severity": "P3",
      "evidence_level": "code read",
      "location": "token_bucket.py:__init__/try_acquire/seconds_until validation",
      "scenario": "NaN passes all checks: try_acquire(nan) is always False, seconds_until(nan) returns nan (time.sleep(nan) raises), TokenBucket(nan,1) never issues tokens, and an infinite rate is accepted.",
      "fix": "Require math.isfinite for capacity, rate and n; add assertRaises tests."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned",
      "location": "test_token_bucket.py:test_threads_never_over_issue",
      "scenario": "The race window is tiny under the GIL; the test very likely still passes with the lock removed, so it does not demonstrate thread safety.",
      "fix": "Widen the window (yielding clock, low switchinterval, more threads) and confirm the test fails without the lock."
    },
    {
      "severity": "P3",
      "evidence_level": "code read",
      "location": "test_token_bucket.py:test_bad_arguments / test_seconds_until",
      "scenario": "No tests for rate <= 0, n <= 0, seconds_until(n > capacity), or seconds_until returning 0.0 when available; the 0.0001 assertion is near-vacuous.",
      "fix": "Add assertRaises and assertEqual(seconds_until(1), 0.0) on a full bucket."
    }
  ]
}
```