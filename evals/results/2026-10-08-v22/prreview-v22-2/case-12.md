# pr-review: retry helper (`retry.py`, `test_retry.py`)

**Review report**

**REVIEWED:** Not frozen. No PR number, head SHA or merge base was provided, and this session has no tools, so I could not check out a head. This review covers only the two files pasted above. Any commit containing different content was not reviewed.

**TIER:** Standard. This is ordinary library code with no auth, secrets, network exposure, data handling or money movement. The stakes (a shared library used by production jobs) justify a careful single round, but they do not change what the code touches. One round has been run, so the tier's budget is spent.

**REVIEWERS:**
- Reviewer: this session (claude-opus-5-5), standard seat, one round, as the context requests. It did not write the change.
- Author: unknown. No commit trailers were provided.
- Data: the code was pasted inline and was sent nowhere else.

**Method:**
- I read the code and hand-traced all 6 tests against it. All 6 trace to a pass, but I could not run them, so "all pass" is still the author's claim, consistent with my reading.
- The change matches the request on every point: chosen exceptions, exponential backoff, full jitter, delay cap, N attempts, re-raise of the last error, injectable sleep and rng.
- It adds nothing extra beyond the `Exception` default in F4.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `retry.py:22` | `base * (2 ** k)` multiplies a float by an unbounded int. With the default float `base=0.1`, once `k` reaches 1024, `2**1024` cannot be converted to float and Python raises `OverflowError: int too large to convert to float`. A job configured as "retry for a long time" (for example `attempts=5000, cap=30`) crashes on its 1025th failure with `OverflowError` instead of retrying or re-raising the real error. The cap never gets a chance to apply. | `retry(Flaky(2000), attempts=1100, base=0.1, cap=1, sleep=lambda s: None)` should raise `ConnectionError`. Today it raises `OverflowError`. Fix: compute `min(cap, base * 2 ** min(k, 64))`, or stop doubling once the cap is reached. |
| 2 | P2 | `retry.py:19` | `retry_on` is used directly in `except retry_on`. If a caller passes a list, e.g. `retry_on=[ConnectionError]`, every successful call works, so the mistake goes unnoticed. On the first real failure, Python raises `TypeError: catching classes that do not inherit from BaseException is not allowed`. That hides the original error and skips every retry, exactly when retrying matters. | `retry(Flaky(1), retry_on=[ConnectionError], sleep=lambda s: None)` should return `"ok"`, or reject the argument up front with `ValueError`/`TypeError` before calling `fn`. Today it raises `TypeError` from inside the handler. Fix: normalise with `tuple(retry_on)` and validate it at entry. |
| 3 | P3 | `retry.py:14-15, 22` | Only `attempts` is validated. A negative `base` or `cap` (for example a config typo `cap=-1`) makes the computed delay negative. `time.sleep(-0.3)` raises `ValueError: sleep length must be non-negative` on the first retry, which again hides the real error. | `retry(lambda: 1, cap=-1)` should raise `ValueError` before calling `fn`. Today it returns `1`, and the same call with a failing `fn` raises `ValueError` from `sleep` instead of the original error. |
| 4 | P3 | `retry.py:7` | The default `retry_on=(Exception,)` retries programming errors as well as transient ones. A `TypeError` or `AttributeError` bug in `fn` is retried 5 times with backoff before it surfaces, which delays failure and multiplies side effects of a partly-run `fn` in production jobs. The request says "retry on *chosen* exceptions", which suggests the caller should choose. | `retry(lambda: None.x)` with `sleep` recorded: today `sleep` is called 4 times. After the fix, either the call fails with no sleep because `retry_on` is now required, or the default is documented as deliberate and the finding is rejected. |

The tests cover the happy path, give-up, no sleep after the last attempt, non-matching exceptions, the cap, and zero attempts. They never use a fractional `rng` value or a non-tuple `retry_on`, which is why findings 1–3 pass unnoticed.

**FILES NEEDED BUT NOT PROVIDED:**
- The PR, head SHA and merge base.
- The commit trailers.
- The CI configuration and check results.
- Any callers of `retry` in the production jobs, to check whether any pass `attempts` > 1024, list-typed `retry_on`, or config-sourced `base`/`cap`.

**Close-out**

The close-out is not written here: a reviewer does not adjudicate its own findings. The author must give each of findings 1–4 a decision. P2s and P3s may be deferred, but only with a linked tracking issue.

**MERGE RECOMMENDATION (reviewer's view, pending adjudication):** merge after fixes.
- There is no P0 or P1. The core logic is correct by trace.
- Findings 1 and 2 are cheap to fix and each comes with a ready-made test. I recommend fixing them in this PR rather than deferring them.
- Still open before merge:
  - the reviewed head SHA (not frozen);
  - CI checks (not seen, and a missing check is not green);
  - the author's written adjudication of all four findings.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "traced by reading; Python float(int) overflow behaviour for 2**1024 is well-established, not executed here",
      "location": "retry.py:22",
      "scenario": "Float base (default 0.1) with attempts > 1024: base * 2**k raises OverflowError at k=1024, crashing the retry loop and masking the real error before the cap applies.",
      "fix": "Clamp the exponent (e.g. 2 ** min(k, 64)) or stop growing once base*2**k >= cap; add a test with attempts=1100."
    },
    {
      "severity": "P2",
      "evidence_level": "traced by reading; Python raises TypeError when an except clause names a non-exception/non-tuple object, not executed here",
      "location": "retry.py:19",
      "scenario": "retry_on=[ConnectionError] (a list) works while fn succeeds, then on first failure raises TypeError from the except clause, masking the original error and skipping all retries.",
      "fix": "Normalise retry_on with tuple() and validate each entry is a BaseException subclass at entry; add a list-input test."
    },
    {
      "severity": "P3",
      "evidence_level": "traced by reading; not executed",
      "location": "retry.py:14-15,22",
      "scenario": "Negative base or cap yields a negative delay; time.sleep raises ValueError on the first retry, masking the original error.",
      "fix": "Validate base >= 0 and cap >= 0 up front alongside attempts; add a test."
    },
    {
      "severity": "P3",
      "evidence_level": "read against the request text",
      "location": "retry.py:7",
      "scenario": "Default retry_on=(Exception,) retries programming errors (TypeError, AttributeError) 5 times with backoff, delaying failure and repeating side effects; the request asks for chosen exceptions.",
      "fix": "Make retry_on required, or document the broad default as deliberate and reject this finding with that reference."
    }
  ]
}
```