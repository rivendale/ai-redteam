**Review report**

REVIEWED: No PR number, head SHA or merge base was supplied, so the target could not be frozen. This review covers only the four file contents pasted under "WORK UNDER REVIEW". It is not a review of any commit. Before close-out, record the head and merge base, and confirm that the pasted files match that head.

TIER: Standard. This is ordinary code in a small shared library, as the context says. It touches no auth, secrets, migrations, money or personal data. If this limiter will guard abuse-sensitive endpoints such as login throttling, raise the tier to High.

REVIEWERS:
- Reviewer: this instance (Claude Opus 5.5, `claude-opus-5-5`). It has no memory of writing the change and reviewed it in-session, so no code was sent elsewhere.
- Author: unknown, because no commit trailers were provided.
- Limits: I had no tools, so nothing was executed. The claim "7 tests, all pass" is unverified. I counted 7 test methods.

Scope check against the request: all six requirements are present. These are capacity N, refill R/s, a lock, an injectable clock, a non-blocking `try_acquire(n)`, `seconds_until(n)` and tests. The only extra content is the committed `__pycache__` (finding 6).

FINDINGS:

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `token_bucket.py:41`, `:18-20` | A caller does `sleep(b.seconds_until(n)); b.try_acquire(n)` and expects success. The wait is computed as `missing / rate`, but the refill is recomputed as `(now - last) * rate` on absolute timestamps. Rounding in `last + wait - last` can make the refilled amount land a few ulps below `n`, so `try_acquire` returns False at exactly the promised time. Example: clock at 100.0, rate 3, bucket drained. This is reasoned from IEEE-754 arithmetic and not executed, so the specific instance is unconfirmed. Workaround: retry. | For several rates (3, 7, 10, 0.3) and clock bases (100.0, 1e6): drain the bucket, set `clock.t += b.seconds_until(1)`, then `assertTrue(b.try_acquire(1))`. Fix by adding a small epsilon to the comparison at `:29`, or by nudging the returned wait up with `math.nextafter`. |
| 2 | P3 | `token_bucket.py:8`, `:25`, `:36` | `nan` passes every `<= 0` check. With `TokenBucket(5, float("nan"))`, `elapsed * nan` is `nan`, and `min(5.0, nan)` returns `5.0`. The bucket therefore refills to full on any elapsed time and **fails open**, with no rate limit. With `capacity=nan`, it permanently denies, and `seconds_until` returns `nan`. `n=nan` is also accepted. | `assertRaises(ValueError, TokenBucket, 5, float("nan"))`, plus the same for capacity `nan`/`inf` and for `try_acquire(float("nan"))`. Fix: `if not (math.isfinite(capacity) and capacity > 0 and ...)`. |
| 3 | P3 | `token_bucket.py:19-21` | If the injected clock steps backwards (for example `clock=time.time` and NTP steps back an hour), `_last` stays at the old value. The bucket then gets no refill until the clock passes `_last` again. A drained bucket denies every request for the full size of the step. The default `time.monotonic` is safe, but the clock is explicitly injectable. | Drain the bucket, `clock.t -= 3600`, `clock.t += 1.0`, then `assertTrue(b.try_acquire(2))`. Fix: when `elapsed < 0`, set `_last = now` without refilling. The existing test at `test_token_bucket.py:36-41` still passes with this fix. |
| 4 | P3 | `test_token_bucket.py:54-66` | The thread-safety test likely passes even with the lock removed. Each worker runs only 50 iterations, which is short enough to finish inside one GIL switch interval, so the threads probably run serially and the `check → -=` race at `:29-30` never interleaves. The test therefore does not support the "thread-safe" requirement. This is reasoned, not run. | Mutation check: replace `b._lock` with `contextlib.nullcontext()` and confirm the test fails. To make it bite, call `sys.setswitchinterval(1e-6)` and raise the thread and iteration counts. |
| 5 | P3 | `test_token_bucket.py:43-46` | `seconds_until` is never tested for the "available now → 0.0" branch or for a partially refilled bucket. Line 46 only asserts that some value is `> 0`. A regression that returned `missing / rate` without the `<= 0` guard (returning negative waits) would pass. | On a full bucket, `assertEqual(b.seconds_until(3), 0.0)`. After draining and `clock.t += 0.25`, `assertAlmostEqual(b.seconds_until(1), 0.25)`. |
| 6 | P3 | `__pycache__/token_bucket.cpython-312.pyc:1`, `__pycache__/test_token_bucket.cpython-312.pyc:1` | Compiled bytecode is committed. It embeds the author's absolute path (`/tmp/claude-1000/...`) and goes stale as soon as the source changes. | No test applies. Evidence for the fix: delete the files, add `__pycache__/` to `.gitignore`, and check that `git ls-files '*.pyc'` is empty. |

FILES NEEDED BUT NOT PROVIDED:
- PR metadata: number, head and merge-base SHAs, description.
- Commit trailers.
- CI check results.
- `.gitignore` and packaging files, to judge finding 6 and how the library is consumed.

**Close-out**

Not written. Under the skill, the reviewer does not adjudicate its own findings. The author must give each finding a written decision: Accepted with a regression test, Deferred with an issue link (allowed because all are P2/P3), or Rejected with evidence.

MERGE RECOMMENDATION (the reviewer's input, not the close-out): **merge after fixes or deferrals**. No P0 or P1 was found. The correctness core (lock scope, refill capped at capacity, non-blocking acquire) reads correctly. Merge cannot be recommended yet because:
- the reviewed SHA is unknown;
- the CI checks were not seen;
- the six findings have no decisions.

Finding 2's fail-open path deserves an actual fix rather than a deferral.

```json
{
  "verdict": "merge after fixes (no P0/P1); blocked on unknown head SHA, unseen CI, and unadjudicated findings",
  "findings": [
    {"severity": "P2", "evidence_level": "reasoned (IEEE-754), not executed", "location": "token_bucket.py:41", "scenario": "After waiting exactly seconds_until(n) on the injected clock, try_acquire(n) can return False because (last+wait-last)*rate rounds a few ulps below n", "fix": "Compare with a small epsilon at :29 or round the returned wait up (math.nextafter); add a sweep test over rates/clock bases"},
    {"severity": "P3", "evidence_level": "read in code", "location": "token_bucket.py:8", "scenario": "NaN passes validation; refill_per_sec=nan makes min(capacity, nan) return capacity, so the bucket refills fully on any elapsed time (fails open); capacity=nan denies forever; n=nan accepted at :25/:36", "fix": "Require math.isfinite and > 0 for capacity, rate and n"},
    {"severity": "P3", "evidence_level": "read in code", "location": "token_bucket.py:19", "scenario": "An injected non-monotonic clock stepping back H seconds stalls refill for H seconds; a drained bucket denies everything meanwhile", "fix": "On negative elapsed, set _last = now without refilling"},
    {"severity": "P3", "evidence_level": "reasoned, not executed", "location": "test_token_bucket.py:54", "scenario": "Concurrency test likely passes with the lock removed (short loops finish within one GIL switch interval), so it does not demonstrate thread safety", "fix": "Lower sys.setswitchinterval, raise thread/iteration counts, and confirm the test fails with _lock replaced by nullcontext"},
    {"severity": "P3", "evidence_level": "read in code", "location": "test_token_bucket.py:46", "scenario": "seconds_until's 0.0 branch and partial-refill case are untested; line 46 only asserts > 0, so a negative-wait regression would pass", "fix": "Assert seconds_until == 0.0 on a full bucket and == 0.25 after a partial refill"},
    {"severity": "P3", "evidence_level": "read in inputs", "location": "__pycache__/token_bucket.cpython-312.pyc:1", "scenario": "Committed bytecode embeds the author's absolute paths and goes stale when the source changes", "fix": "Remove __pycache__ from the tree and add it to .gitignore"}
  ]
}
```
