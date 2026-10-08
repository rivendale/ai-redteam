**Review report**

**REVIEWED:** No PR number, head SHA or merge base SHA was supplied. Only the two files inline were reviewed. This report covers that exact text and nothing else. Whoever closes the PR must record the SHAs, and must say if they differ from this content.

**TIER:** Standard. This is ordinary library code: a rate limiter with concurrency. It touches no auth, secrets, network exposure, personal data or money. The context also states the stakes as standard. That means one model round, and this report is that round.

**DATA (Step 3):** The code is a generic algorithm with no sensitive data. It was reviewed in this session only and nothing was sent elsewhere.

**REVIEWERS:**
- Reviewer: this session, Claude Opus 5.5 (`claude-opus-5-5`). It did not write the change.
- Author: unknown. No commit trailers were provided.

**EVIDENCE NOTE:** I could not run anything in this session. The claim "7 tests, all pass" is unverified. Every finding below is reasoned from the code, not executed.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `token_bucket.py` `seconds_until` (`return ... missing / self.rate`) together with `try_acquire` (`if self._tokens >= n`) | Float round-trip error: `(missing/rate)*rate` can come out slightly below `missing`. Example: `TokenBucket(5, 49, clock)` with clock at `0.0`, then `try_acquire(5)`. `seconds_until(1)` returns `1/49`. Advance the clock exactly that much: `_tokens = (1/49)*49 = 0.9999999999999999`, so `try_acquire()` returns **False**. The documented pattern "wait `seconds_until(n)`, then `try_acquire(n)`" fails spuriously and needs an extra retry or near-zero sleep loop. | Set `clock.t = 0.0`, then `b = TokenBucket(5, 49, clock=clock)` and `b.try_acquire(5)`. Then `clock.t += b.seconds_until(1)` and `assertTrue(b.try_acquire())`. This fails today. Fix options: a small epsilon in the `>=` comparison, or have `seconds_until` round up (for example `math.nextafter`) and clamp `_tokens` to `n` when it is within epsilon. |
| 2 | P3 | `token_bucket.py` `_refill` (`if elapsed > 0:` and `_last` is updated only inside it) | A clock that steps backwards freezes refill until the clock passes the old `_last`. Example: with `clock=time.time` (the clock is injectable, so this is a supported use), an NTP step back of 1 hour gives no refills for 1 hour. The bucket starves and every `try_acquire` returns False. `seconds_until` returns e.g. 0.5 s forever, which is a lie. | Drain the bucket, then `clock.t -= 3600`, then `clock.t += 1.0`, then `assertTrue(b.try_acquire(2))`. This fails today. Fix: on `elapsed < 0`, re-baseline `self._last = now` without adding tokens. The existing backwards test still passes with this fix. |
| 3 | P3 | `token_bucket.py` `__init__` validation and the `n` checks in `try_acquire` / `seconds_until` | Non-finite input passes validation because NaN comparisons are always False. `TokenBucket(float('nan'), 1)` is accepted and every acquire returns False. `try_acquire(float('nan'))` returns False forever. `seconds_until(float('nan'))` returns `nan`, and `time.sleep(nan)` then raises. `refill_per_sec=float('inf')` makes `seconds_until` return `0.0` ("available now") while `try_acquire` returns False at the same instant. | `assertRaises(ValueError)` for `TokenBucket(nan, 1)`, `TokenBucket(1, inf)`, `b.try_acquire(nan)` and `b.seconds_until(nan)`. These fail today. Fix: require `math.isfinite` on all of them. |
| 4 | P3 | `test_token_bucket.py` `test_threads_never_over_issue` | The test does not show thread safety. It uses a constant clock and does about 400 cheap calls, so the whole check-then-decrement usually finishes inside one GIL switch interval. If `with self._lock:` is deleted, the test very likely still passes, so it guards nothing. | Run the test with the lock removed and confirm it fails. To make it bite, call `sys.setswitchinterval(1e-6)`, use a `threading.Barrier` so workers start together, and use a clock that does real work, or more iterations. |
| 5 | P3 | `test_token_bucket.py` `test_bad_arguments` and `test_seconds_until` | Tests for the request's stated contract are missing: `refill_per_sec <= 0`, `n <= 0`, and `seconds_until` returning `0.0` when tokens are available. A regression in any of these goes undetected. Line `self.assertEqual(self.b.seconds_until(0.0001 + 0) > 0, True)` is also a weak assertion: it checks for a positive value, not `0.0001/2`. | Add `assertRaises` for `TokenBucket(1, 0)`, `try_acquire(0)` and `seconds_until(-1)`. Add `assertEqual(fresh_bucket.seconds_until(1), 0.0)` and `assertAlmostEqual(b.seconds_until(0.0001), 0.00005)`. |

The change otherwise matches the request:
- Capacity, refill and thread safety (via the lock) are in place.
- The clock is injectable.
- `try_acquire` never blocks.
- `seconds_until` reports how long until n tokens are available.
- Tests are included.
- Nothing extra was added.

**FILES NEEDED BUT NOT PROVIDED:**
- The PR identifier, head SHA and merge base SHA.
- The commit trailers (authorship).
- CI results (needed to confirm "7 tests, all pass").
- Any callers of `TokenBucket` in the shared library.

---

**Close-out**

Not written here: a reviewer never adjudicates its own findings. The author needs to record Accepted, Deferred (with an issue link) or Rejected for each of #1–#5.

**Current status for whoever closes:** No P0 or P1 findings. Merge can be recommended once all of these hold:
- every finding has a written decision;
- the SHAs are recorded;
- the test suite is shown green in CI.

I'd suggest fixing #1 before merge, because it breaks the library's own documented usage pattern. #2–#5 could be deferred with tracking issues.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "reasoned (not executed; (1/49)*49 == 0.9999999999999999 in IEEE-754 double)",
      "location": "token_bucket.py seconds_until / try_acquire",
      "scenario": "TokenBucket(5, 49) with clock at 0.0, drain, advance clock by seconds_until(1); _tokens = 0.9999999999999999 < 1 so try_acquire() returns False despite the reported wait having elapsed",
      "fix": "Compare with a small epsilon in try_acquire (and clamp), or round the seconds_until result up so waiting it guarantees availability; add a regression test with rate=49"
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned",
      "location": "token_bucket.py _refill (elapsed > 0 guard)",
      "scenario": "Injected non-monotonic clock steps back 1 hour; _last is not rebased, so no refill occurs for an hour and the bucket starves",
      "fix": "When elapsed < 0, set self._last = now without adding tokens"
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned",
      "location": "token_bucket.py __init__, try_acquire, seconds_until argument checks",
      "scenario": "NaN capacity or n passes validation (NaN comparisons are False): acquire is always False and seconds_until returns nan; infinite rate makes seconds_until return 0.0 while try_acquire fails",
      "fix": "Validate with math.isfinite for capacity, refill_per_sec and n"
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned",
      "location": "test_token_bucket.py test_threads_never_over_issue",
      "scenario": "Test likely passes even with the lock removed (constant clock, few cheap ops within one GIL interval), so it does not demonstrate thread safety",
      "fix": "Lower sys.setswitchinterval, start workers with a Barrier, increase iterations; confirm the test fails with the lock removed"
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned",
      "location": "test_token_bucket.py test_bad_arguments / test_seconds_until",
      "scenario": "No tests for rate <= 0, n <= 0, or seconds_until == 0.0 when tokens are available; the seconds_until(0.0001) > 0 assertion is too weak to catch a wrong formula",
      "fix": "Add assertRaises cases, an exact 0.0 check on a full bucket, and assertAlmostEqual(seconds_until(0.0001), 0.00005)"
    }
  ]
}
```