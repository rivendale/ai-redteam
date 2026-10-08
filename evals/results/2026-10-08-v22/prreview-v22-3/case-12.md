# Review report: retry helper

**REVIEWED:** No PR number, head SHA or merge base was provided. I reviewed the two files as pasted (`retry.py`, `test_retry.py`). This report covers exactly that text. If the PR head differs from it, this is not a review of that head.

**TIER: Standard.** This is ordinary library code: no auth, secrets, network exposure, migrations, money or personal data. The production-jobs stakes raise the care taken, not the tier. That fits "standard seats only", so one round is required and this is it.

**DATA:** The code went to no endpoint outside this session, and nothing in it carries personal data.

**REVIEWERS:**
- Reviewer: this session (Claude Opus 5.5, `claude-opus-5-5`). It did not write the change and has no memory of authoring it.
- Author: unknown. No commit trailers were provided.
- Evidence level: every finding below comes from reading the code. I had no tools, so I ran nothing. The claim "6 tests, all pass" is unverified; tracing the assertions by hand, they are consistent with the code.

**Against the request:** Every requirement is met:
- retry on chosen exceptions
- exponential backoff with full jitter
- delay cap
- N attempts, then re-raise the last error
- injectable sleep and random source

Nothing extra was added. "Clock" is satisfied by injecting `sleep`, since no time reading is needed.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `retry.py:21` | `base * (2 ** k)` multiplies a float by an unbounded int. Take a long-running job configured with `attempts=2000` (or any value above 1024), the default `base=0.1` and `cap=5`, against a dependency that stays down. At `k=1024`, `0.1 * 2**1024` raises `OverflowError: int too large to convert to float` inside the `except` handler. The job dies with `OverflowError`, chained to the ConnectionError, instead of continuing at the 5 s cap and re-raising the last error. The cap never protects against this because `min` runs after the overflow. | `retry(Flaky(10**6), attempts=1100, base=0.1, cap=5, sleep=lambda s: None, rng=lambda: 1.0)` should raise `ConnectionError`, not `OverflowError`. Fix: stop growing the exponent once it passes the cap, e.g. `min(cap, base * 2 ** min(k, 64))`, or track the delay incrementally and clamp it. |
| 2 | P3 | `test_retry.py:18,30,40` | Every test that checks delays passes `rng=lambda: 1.0`, so the jitter multiplication is never exercised. A regression to `sleep(min(cap, base * 2**k))` (no jitter, so synchronized retries across jobs) passes all six tests. | With `rng=lambda: 0.5`, `base=1`, `cap=100`, `Flaky(2)`, assert `slept == [0.5, 1.0]`. Optionally use a sequence-returning rng and assert each delay is `rng_value * min(cap, base*2**k)`. |
| 3 | P3 | `retry.py:7,19` | A caller passes `retry_on=[ConnectionError, TimeoutError]`, which is a list and an easy mistake. Nothing fails until the first real exception. Then evaluating `except retry_on` raises `TypeError: catching classes that do not inherit from BaseException is not allowed`, which masks the original error, and no retry happens. Production only discovers the misconfiguration during an outage. | `retry(Flaky(1), retry_on=[ConnectionError], sleep=lambda s: None)` should return `"ok"` (normalize with `tuple(...)`), or raise `TypeError`/`ValueError` at call time before `fn` runs. |
| 4 | P3 | `retry.py:15-16` | Only `attempts` is validated. With `base=-0.1` or `cap=-1`, the first failure computes a negative delay, and `time.sleep` raises `ValueError: sleep length must be non-negative` from inside the handler, replacing the real error. If `rng` is injected and returns a value outside [0, 1], the result is a negative or over-cap sleep. | `retry(lambda: 1, base=-1)` raises `ValueError` before calling `fn`. Same for `cap < 0`. |
| 5 | P3 | `retry.py:7` | The default `retry_on=(Exception,)` retries everything a caller did not choose, including `TypeError`, `KeyError` and assertion bugs. In a production job with a non-idempotent `fn`, a programming error re-runs side effects up to 4 more times with backoff, and the real failure surfaces seconds later. The request says "retry on chosen exceptions", which arguably means there should be no catch-all default. This needs an owner decision, not a mechanical fix. | `retry(Flaky(1, exc=TypeError), sleep=lambda s: None)` should raise `TypeError` after 1 call, if the owner chooses a required `retry_on` or a narrower default. |

Two things I checked and found correct:
- No sleep happens after the final attempt.
- The last exception is re-raised outside the handler with its traceback intact.

The docstring says delays are in "[0, min(...)]" but `random.random()` returns values in [0, 1), so the top of the range is never reached. That has no failure scenario, so it is not a finding.

**FILES NEEDED BUT NOT PROVIDED:**
- PR metadata (number, head and merge-base SHAs, commit trailers)
- CI configuration and check results
- Callers of `retry` in the production jobs, needed to judge whether the default `retry_on` and large `attempts` values occur in practice

## Close-out

Not written here. The author has not adjudicated these findings, and a reviewer never adjudicates its own.

**MERGE RECOMMENDATION: not yet (expected outcome: merge after fixes).**
- There are no P0 or P1 findings.
- Before merge, each finding needs a written decision. Finding 1 should be fixed or explicitly deferred with an issue link.
- The owner must decide on finding 5, the default `retry_on`.
- The reviewed SHA must be recorded.
- CI checks must be seen present and green. They have not been seen.

```json
{
  "verdict": "merge after fixes (pending adjudication, SHAs and green checks)",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "code-read (not executed)",
      "location": "retry.py:21",
      "scenario": "attempts > 1024 with float base (default 0.1): base * 2**1024 raises OverflowError inside the except handler, killing the job with OverflowError instead of continuing at the cap and re-raising the last error.",
      "fix": "Bound the exponent before multiplying (e.g. base * 2 ** min(k, 64)) or grow the delay incrementally and clamp to cap; add test with attempts=1100."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read (not executed)",
      "location": "test_retry.py:18",
      "scenario": "All delay tests use rng=lambda: 1.0, so removing the jitter multiplication (rng() * ...) passes the whole suite.",
      "fix": "Add a test with rng=lambda: 0.5 asserting slept == [0.5, 1.0] for base=1, two failures."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read (not executed)",
      "location": "retry.py:19",
      "scenario": "retry_on passed as a list raises TypeError at the first real exception ('catching classes that do not inherit from BaseException is not allowed'), masking the error and skipping retries.",
      "fix": "Normalize retry_on with tuple() (accepting a single class too) or validate it up front."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read (not executed)",
      "location": "retry.py:15",
      "scenario": "Negative base or cap yields a negative delay; time.sleep raises ValueError inside the handler, replacing the real error.",
      "fix": "Validate base >= 0 and cap >= 0 (and optionally clamp the computed delay to [0, cap]) before calling fn."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read (not executed)",
      "location": "retry.py:7",
      "scenario": "Default retry_on=(Exception,) retries programming errors (TypeError, KeyError), re-running non-idempotent side effects up to 4 more times and delaying the real failure; the request asks for chosen exceptions.",
      "fix": "Owner decision: make retry_on required or narrow the default; add a test that a TypeError is not retried by default."
    }
  ]
}
```