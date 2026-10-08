# pr-review: TokenBucket

## Review report

**REVIEWED:** Not identifiable. No PR number, head SHA or merge base SHA was supplied; the inputs are file contents only. This review covers exactly the two files quoted above (`token_bucket.py`, `test_token_bucket.py`). It does not apply to any commit whose contents differ from them.

**TIER:** Standard. This is ordinary library code: no auth, secrets, network exposure, personal data, money or migrations. That matches the stated stakes. One round is required, and this is that round.

**DATA (Step 3):** The code carries no personal or regulated data. It was reviewed in this session and nothing was sent elsewhere.

**REVIEWERS:**
- Reviewer: this instance (Claude Opus 5.5, `claude-opus-5-5`), which did not write the change.
- Author: unknown. No commits or `Co-Authored-By` trailers were provided.

**EVIDENCE LIMITS:** I had no tools, so nothing was run.
- "7 tests, all pass" remains a claim. Tracing each test by hand, all 7 should pass against this implementation.
- Findings are marked **traced** (worked step by step through the code) or **reasoned** (likely, but depends on float rounding I could not execute).

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `token_bucket.py` `seconds_until`, last line, interacting with `_refill` (`elapsed * self.rate`) | **Reasoned.** `seconds_until` returns `missing / rate`, computed exactly. But the refill later recomputes `(now - last) * rate` in floating point. Example: `rate=3`, bucket empty, `_last=100.0`, `w = 1/3`. The clock reads `100.0 + w`, which rounds to the nearest ulp at 100 (~1.4e-14). Then `elapsed*3` can come out as `0.99999999999998…`, so `try_acquire(1)` returns **False**. A caller doing `sleep(b.seconds_until(n)); b.try_acquire(n)` fails, and then spins on tiny waits. Larger `time.monotonic()` values (long uptime) widen the error. This breaks the request's "report how long until n tokens are available" contract. | Use FakeClock at `t=100.0` and `TokenBucket(3, 3)`. Drain it, then for k in 1..1000: `clock.t += b.seconds_until(1)` and assert `b.try_acquire(1)`. Fix: add a small epsilon to `seconds_until`, or compare `self._tokens >= n - 1e-9` (and clamp). |
| 2 | P3 | `token_bucket.py` `_refill`: `if elapsed > 0:` | **Traced.** If an injected clock steps backward by D (for example `time.time` under an NTP correction), `_last` stays ahead. No tokens refill for D seconds, so a one-hour step back throttles the caller to zero refill for an hour. `seconds_until` also under-reports during that window, because it returns `missing/rate` and ignores the `_last - now` gap. The default `time.monotonic` is not affected, which is why this is P3. | Drain the bucket, then `clock.t -= 50`. Assert either that `seconds_until(1) == 50.5` (if the stall is the intended behaviour), or that `try_acquire()` succeeds after `clock.t += 0.5` (if `_last` should resync to `now` on a backward step). Pick one and document it. |
| 3 | P3 | `test_token_bucket.py` `test_clock_going_backwards_is_ignored` | **Traced.** The test cannot detect removal of the `elapsed > 0` guard. Without the guard: tokens = `0 + (-50*2) = -100` and `_last = 50`; the next acquire is False; at `t=100.5`, elapsed is 50.5, so tokens = `-100 + 101 = 1` and the acquire is True. The test passes either way, so the behaviour it is named for is untested. | After the backward step, also assert `b.seconds_until(1) > 0` and that `b._tokens >= 0`. Or step back, then forward by only 0.5 *relative to the original time*, and assert exactly 1 token (not 0, not -100). |
| 4 | P3 | `test_token_bucket.py` `test_threads_never_over_issue` | **Reasoned.** With the lock deleted, this test almost certainly still passes. The loop is 400 trivial iterations, so each thread probably finishes within one GIL switch interval (5 ms) and the check-then-decrement race never interleaves. The "thread-safe" requirement is therefore asserted rather than tested. | Inject a clock that calls `time.sleep(0)` (forcing a thread switch inside the critical section), or set `sys.setswitchinterval(1e-6)`. Confirm the test **fails** with the `with self._lock:` lines removed, then passes with them. |
| 5 | P3 | `token_bucket.py` `__init__` validation and `try_acquire`/`seconds_until` validation (`n <= 0 or n > self.capacity`) | **Traced.** NaN slips past every comparison. `TokenBucket(float('nan'), 1)` is accepted, `min(nan, x)` keeps `_tokens` as NaN, and every acquire returns False. `try_acquire(float('nan'))` returns False forever, and `seconds_until(nan)` returns `nan` (because `nan <= 0` is False). | `assertRaises(ValueError)` for NaN capacity, NaN rate, `try_acquire(nan)` and `seconds_until(nan)`. Fix: use `not (0 < n <= self.capacity)` and `math.isfinite` checks. |
| 6 | P3 | `test_token_bucket.py` `test_seconds_until`, `test_bad_arguments` | **Traced.** Several gaps: no test that `seconds_until` returns `0.0` when tokens are available; no test of its `ValueError` path; `n=0` and negative `n` are not tested; negative rate is not tested. `seconds_until(0.0001 + 0) > 0` is a weak check, since it only asserts positivity (expected value 0.00005). | Add `assertEqual(fresh_bucket.seconds_until(5), 0.0)`, `assertRaises(ValueError, b.seconds_until, 6)`, `assertRaises(ValueError, b.try_acquire, 0)`, `TokenBucket(1, -1)`, and `assertAlmostEqual(b.seconds_until(0.0001), 0.00005)`. |

**Considered and not raised:** `try_acquire` takes a lock, so it can wait briefly on another thread. I read "never block" in the request as "never waits for tokens", which the code satisfies. The critical section is O(1) plus one call to the injected clock. Request coverage is otherwise complete: capacity, rate, thread safety, injectable clock, non-blocking acquire, time-until method and tests are all present, with nothing extra.

**FILES NEEDED BUT NOT PROVIDED:** PR metadata (number, head SHA, merge base SHA), commit log with trailers, and CI/check results.

## Close-out

Not written. Under the skill, a reviewer never adjudicates its own findings. The author decides findings 1–6 (accept with regression test / defer with issue link for P2–P3 / reject with evidence), and whoever closes the PR writes the close-out against a recorded head SHA.

**Provisional merge position:** **merge after fixes**, and not before these hold:
- (a) the head SHA is recorded;
- (b) finding 1 (P2) is accepted or deferred with an issue link;
- (c) the "7 tests pass" claim is confirmed by a CI check on that SHA. The check is currently missing, and a missing check is not green.

There are no P0 or P1 findings and no pending architecture decision.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "reasoned (float rounding not executed)",
      "location": "token_bucket.py:seconds_until (return missing / self.rate) with _refill (elapsed * self.rate)",
      "scenario": "rate=3, empty bucket, _last=100.0: advancing the clock by seconds_until(1)=1/3 can yield elapsed*3 = 0.99999999999998, so try_acquire(1) returns False right after the reported wait; sleep-then-acquire callers fail and spin.",
      "fix": "Add a small epsilon to the returned wait or compare tokens >= n - 1e-9; test by looping clock += seconds_until(1) then asserting try_acquire(1)."
    },
    {
      "severity": "P3",
      "evidence_level": "traced",
      "location": "token_bucket.py:_refill (if elapsed > 0)",
      "scenario": "Injected wall clock steps back D seconds: _last stays ahead, no refill for D seconds, and seconds_until under-reports by D.",
      "fix": "Decide the policy (resync _last = now on backward step, or include the _last - now gap in seconds_until), document it, and test it."
    },
    {
      "severity": "P3",
      "evidence_level": "traced",
      "location": "test_token_bucket.py:test_clock_going_backwards_is_ignored",
      "scenario": "Removing the elapsed > 0 guard leaves the test passing (tokens -100 then +101 = 1), so the guarded behaviour is untested.",
      "fix": "Assert the exact token count / seconds_until after the backward step so the unguarded version fails."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned",
      "location": "test_token_bucket.py:test_threads_never_over_issue",
      "scenario": "With the lock removed the test very likely still passes, because 400 short iterations rarely cross a GIL switch; thread safety is unverified.",
      "fix": "Force switches inside the critical section (clock that calls time.sleep(0), or sys.setswitchinterval(1e-6)) and confirm the test fails without the lock."
    },
    {
      "severity": "P3",
      "evidence_level": "traced",
      "location": "token_bucket.py:__init__ and try_acquire/seconds_until argument checks",
      "scenario": "NaN capacity, rate or n passes all comparisons; the bucket becomes permanently empty or seconds_until returns nan.",
      "fix": "Use not (0 < n <= capacity) and math.isfinite checks; add ValueError tests for NaN."
    },
    {
      "severity": "P3",
      "evidence_level": "traced",
      "location": "test_token_bucket.py:test_seconds_until, test_bad_arguments",
      "scenario": "No coverage of seconds_until == 0.0 when available, the seconds_until ValueError path, n=0, negative n or negative rate; the 0.0001 assertion only checks > 0.",
      "fix": "Add the missing assertions, including assertAlmostEqual(seconds_until(0.0001), 0.00005)."
    }
  ]
}
```