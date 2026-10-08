# pr-review: retry helper

**Review report**

**REVIEWED:** The PR number, head SHA and merge base SHA were not provided. The work was supplied inline as `retry.py` and `test_retry.py`, so this review covers exactly that text and nothing else. Whoever closes the PR must bind this report to a head SHA. If the PR head differs from the text above, this review does not cover it.

**TIER:** Standard. This is an ordinary code change in a shared library used by production jobs. It does not touch auth, permissions, secrets, network exposure, migrations, money or personal data. That matches the "standard seats only" request in the context. The tier requires one round.

**REVIEWERS:**
- **Reviewer:** this instance (claude-opus-5-5). This session did not write the change, and nothing was sent to any other model or endpoint.
- **Author:** unknown. No commit trailers were provided.

**Evidence limits:** I had no tools in this session. "6 tests, all pass" is the author's claim, not something I observed. All findings come from reading the code against Python semantics.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `retry.py:22` | `base * (2 ** k)` multiplies a float by an unbounded int. When `base` is a float (including the default 0.1) and `k >= 1024`, this raises `OverflowError: int too large to convert to float`. The cap never gets a chance to apply. Example: a polling job calls `retry(poll, attempts=2000, cap=5.0)`, about 85 minutes of retrying at a mean 2.5 s. On failure 1025 it dies with `OverflowError` (chained to the real error) instead of continuing to retry. | `retry(Flaky(1100), attempts=1200, sleep=lambda s: None)` should return `"ok"`. Today it raises `OverflowError`. Fix: clamp the exponent, e.g. `min(cap, base * 2 ** min(k, 62))`, or stop doubling once the delay exceeds `cap`. |
| 2 | P2 | `retry.py:18` | `retry_on` is never validated. A caller passing a list, `retry(fn, retry_on=[ConnectionError])`, gets no error at call time. On the first failure of `fn`, `except [ConnectionError]` raises `TypeError: catching classes that do not inherit from BaseException is not allowed`. The real error is masked, there are no retries, and the bug only shows up in production when the dependency first fails. | `retry(Flaky(1), retry_on=[ConnectionError], sleep=lambda s: None)` should either raise `TypeError`/`ValueError` before calling `fn`, or retry and return `"ok"`. Today `fn` is called once and an unrelated `TypeError` escapes. Fix: normalise with `tuple(...)` and check `issubclass(..., BaseException)` up front. |
| 3 | P3 | `retry.py:12-13`, `:22` | Only `attempts` is validated. With `cap=-1` or `base=-0.5`, the computed delay is negative. On the first failure, `time.sleep(<negative>)` raises `ValueError: sleep length must be non-negative` from inside the `except` block. That replaces the real error and stops the retries. | `retry(Flaky(1), cap=-1)` should raise `ValueError` before calling `fn`. Today `fn` is called first and the `ValueError` comes from `sleep`. |
| 4 | P3 | `test_retry.py:19`, `:44` (all delay assertions) | Every test that asserts delays uses `rng=lambda: 1.0`. A regression that drops the jitter, e.g. `sleep(min(cap, base * 2 ** k))`, still passes all 6 tests. Jitter is a stated requirement, and losing it causes synchronized retry storms across production jobs. | `retry(Flaky(2), rng=lambda: 0.5, base=1, cap=100, sleep=slept.append)` should give `slept == [0.5, 1.0]`. Also test `rng=lambda: 0.0` and expect `[0, 0]`. |
| 5 | P3 | `retry.py:6` | The default `retry_on=(Exception,)` retries programming errors such as `TypeError`, `AttributeError` and `KeyError` with backoff. A production job with a bug in `fn` silently burns `attempts` tries and sleeps before failing. The request says "retry on **chosen** exceptions". A catch-all default contradicts that, or at least makes "chosen" optional. | Either make `retry_on` a required argument (calling `retry(f)` without it should raise `TypeError`), or document the default explicitly. This is a design call for the author. |

**FILES NEEDED BUT NOT PROVIDED:**
- The PR identifier, head SHA and merge base.
- The commit trailers (authorship).
- CI output for the 6 tests.
- Any callers in the production jobs. I needed these to check whether attempts > 1024, list-typed `retry_on`, or the catch-all default actually occur.

**Checked and found correct:**
- `attempts < 1` is rejected.
- There is no sleep after the final attempt.
- Non-matching exceptions propagate immediately.
- `raise last` re-raises the last error with its original traceback.
- The delay is `rng() * min(cap, base * 2**k)`, which is full jitter.
- The sleep and the random source are both injectable.

The request asks for an injectable "clock". Injecting `sleep` satisfies this, because the code never reads the time.

---

**Close-out**

Not written. A reviewer does not adjudicate its own findings. The author must give every finding above a written decision: Accepted with a regression test, Deferred with an issue link, or Rejected with evidence. That decision must be posted on the PR against the reviewed SHA.

**MERGE RECOMMENDATION (provisional, from the reviewer):** merge after fixes. There is no P0 or P1. Findings 1 and 2 are cheap to fix and worth fixing, because this library runs in production jobs. The following are still open:
- the head SHA binding;
- confirmation that the 6 tests are green in CI;
- written adjudication of findings 1–5;
- the author's decision on the `retry_on` default (finding 5).

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "code-read (Python float/int semantics), not executed",
      "location": "retry.py:22",
      "scenario": "With a float base (default 0.1) and attempts > 1024, base * 2**k raises OverflowError on failure 1025, aborting retries with the wrong exception before cap applies.",
      "fix": "Clamp the exponent (e.g. 2 ** min(k, 62)) or stop doubling once the delay reaches cap; add a test with attempts=1200."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read (Python except-clause semantics), not executed",
      "location": "retry.py:18",
      "scenario": "retry_on passed as a list makes the except clause raise TypeError on the first failure of fn, masking the real error and skipping all retries.",
      "fix": "Normalise retry_on to a tuple and validate each entry is a BaseException subclass before calling fn."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read, not executed",
      "location": "retry.py:12-13, retry.py:22",
      "scenario": "Negative cap or base gives a negative delay; time.sleep raises ValueError inside the except block, replacing the real error and ending retries.",
      "fix": "Validate base >= 0 and cap >= 0 alongside attempts."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read of tests",
      "location": "test_retry.py:19, test_retry.py:44",
      "scenario": "All delay assertions use rng=1.0, so a regression that removes jitter passes the whole suite.",
      "fix": "Add tests with rng=0.5 and rng=0.0 asserting scaled delays."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read against request",
      "location": "retry.py:6",
      "scenario": "Default retry_on=(Exception,) retries programming errors (TypeError, KeyError) with backoff, delaying failure of buggy jobs; request says retry on chosen exceptions.",
      "fix": "Make retry_on required, or document the catch-all default; author decision."
    }
  ]
}
```