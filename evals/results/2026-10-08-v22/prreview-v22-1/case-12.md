# pr-review: retry helper

**Review report**

**REVIEWED:** I could not freeze the target. The inputs are pasted file contents with no PR number, head SHA or merge base, and I have no tools to check them out. This review covers the text of `retry.py` and `test_retry.py` exactly as provided. It does not cover any particular commit. Whoever closes the PR must confirm the head SHA matches these contents. Any commit beyond that point is unreviewed.

**TIER:** Standard. This is ordinary code in a shared library used by production jobs. It does not touch auth, secrets, network exposure, migrations, money or personal data. The stakes justify a careful read but not the High tier. The requester asked for standard seats only, which fits this tier. Budget: one round, and this report is that round.

**DATA:** Nothing was sent outside this session. The code carries no personal data.

**REVIEWERS:** This session (Opus 5.5, `claude-opus-5-5`), which did not write the change and has no memory of doing so. The author is unknown because commit trailers were not provided.

**Verification:** I read the code and could not run it. I traced all 6 tests by hand and they should pass as written. "All pass" is still the author's claim until CI shows it. Line numbers count from line 1 of each pasted file.

**Against the request:** The request asks for exponential backoff, full jitter, a capped delay, N attempts, re-raising the last error, and an injectable random source; all are present. "Clock" injection is met by `sleep`. That holds because the helper has no deadline and never reads the time. Nothing extra was added.

FINDINGS:

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `retry.py:22` | With a float `base` (the default is 0.1) and `attempts >= 1026`, the failure at k=1024 computes `0.1 * 2**1024`. Python must convert `2**1024` to a float, so this raises `OverflowError: int too large to convert to float` before `min(cap, …)` can clamp it. The error is raised inside the `except` block. The job therefore dies with an `OverflowError` chained to the real error, instead of retrying. A caller who sets a large `attempts` with `cap=5` to mean "keep trying" hits this after about 85 minutes of retries. | `retry(Flaky(2000), attempts=1100, base=0.1, cap=5, sleep=lambda s: None, rng=lambda: 1.0)` currently raises `OverflowError` and should raise `ConnectionError`. Also assert that every recorded sleep is `<= 5`. Fix: clamp the exponent first, e.g. `delay = cap if k >= 64 else min(cap, base * 2 ** k)`. |
| 2 | P2 | `retry.py:6`, `retry.py:18` | Validation of `retry_on` only happens on the failure path. Example: `retry(fn, retry_on=[ConnectionError])` passes a list. On the happy path everything works. On the first real `ConnectionError`, the `except` clause raises `TypeError: catching classes that do not inherit from BaseException is not allowed`, and no retry happens. A bare class (`retry_on=ConnectionError`) works, but a list does not. The bug stays invisible until production hits the exact error the caller wanted to survive. | `retry(Flaky(1), retry_on=[ConnectionError], sleep=lambda s: None)` currently raises `TypeError`. It should return `"ok"`, or the call should be rejected up front with `ValueError` or `TypeError`. Fix: normalise to a tuple at entry and check each item is a `BaseException` subclass. |
| 3 | P2 | `retry.py:6` (`retry_on=(Exception,)`) | The request says "retry on chosen exceptions", but the default chooses everything. A production job with a programming error (`TypeError`, `KeyError`, `AttributeError`) still retries 5 times and sleeps about 1.5 s in the worst case before failing. A non-idempotent `fn` (a write, a charge, an enqueue) is re-executed on any error, including ones that occur after a side effect. In a shared library, callers who omit `retry_on` get this by default. | `retry(Flaky(5, exc=TypeError), sleep=lambda s: None)` currently calls `fn` 5 times. The test should assert it is called once with no explicit `retry_on`, or should assert that `retry_on` is required. Fix: make `retry_on` a required keyword with no default. This is an API decision for the owner. |
| 4 | P3 | `retry.py:12-13`, `retry.py:22` | Only `attempts` is validated. A negative `base` or `cap` gives a negative delay, so `time.sleep` raises `ValueError: sleep length must be non-negative`. That happens inside the `except` block on the first failure and masks the real error. A non-integer `attempts` such as `2.5` passes the `< 1` check and then fails in `range()` with `TypeError`. | `retry(lambda: 1, cap=-1)` and `retry(lambda: 1, base=-1)` should raise `ValueError` at entry. Currently they succeed silently, then misbehave on the first failure. |
| 5 | P3 | `test_retry.py:18,31,41` | Every test that checks delays uses `rng=lambda: 1.0`. A regression that drops the jitter, e.g. `sleep(min(cap, base * 2**k))`, still passes all 6 tests. The "full jitter" requirement is therefore untested, and so is the claim that the random source is actually used. | Run `Flaky(2)` with `rng=lambda: 0.5`, `base=1`, `cap=100` and assert `slept == [0.5, 1.0]`. |
| 6 | P3 | `retry.py:9-10` | The docstring says the delay is in `[0, d]`, a closed interval. The default `random.random` returns values in `[0, 1)`, so the real range is `[0, d)`. The only effect is that a reader who relies on the docstring to bound `rng` is misled. | Not testable. Fix the docstring to `[0, d)`, or say "rng() * d where rng returns a value in [0, 1)". |

**FILES NEEDED BUT NOT PROVIDED:**
- The PR itself: number, head SHA, merge base, description and commit trailers.
- The CI run showing the 6 tests pass.
- Any existing callers in the shared library. These would show whether any caller relies on the `Exception` default (finding 3) or passes a list (finding 2).

**Close-out**

This section is not written. Per the skill, the reviewer does not adjudicate its own findings. The author must give each of findings 1–6 one of these decisions:
- **Accepted:** name the fix commit and a regression test.
- **Deferred:** P2 and P3 only, with a link to the tracking issue.
- **Rejected:** with evidence.

Then whoever closes the PR writes ADJUDICATION, VERIFIED AFTER FIXES and MERGE RECOMMENDATION.

**What still has to happen before merge:**
- Every finding needs a written decision.
- The reviewed head SHA must be recorded and confirmed against these contents.
- CI checks must be present and green.
- The owner must decide whether `retry_on` stays defaulted to `Exception` (finding 3).

There are no P0 or P1 findings, so nothing here blocks merge outright. Findings 1 and 2 are cheap to fix, and I recommend fixing them rather than deferring.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "reasoned from code (not run): float(2**1024) overflows in Python",
      "location": "retry.py:22",
      "scenario": "Float base (default 0.1) and attempts >= 1026: at k=1024, base * 2**1024 raises OverflowError inside the except block before min(cap, ...) clamps it. The job dies with OverflowError instead of retrying.",
      "fix": "Clamp the exponent before multiplying, e.g. delay = cap if k >= 64 else min(cap, base * 2 ** k). Add a test with attempts=1100 asserting ConnectionError is raised and every sleep is <= cap."
    },
    {
      "severity": "P2",
      "evidence_level": "reasoned from code (not run): Python checks except-clause types only when matching",
      "location": "retry.py:6, retry.py:18",
      "scenario": "retry_on=[ConnectionError] (a list) works until the first real failure, then raises TypeError ('catching classes that do not inherit from BaseException is not allowed') instead of retrying.",
      "fix": "Normalise retry_on to a tuple at entry and validate that each item is a BaseException subclass. Test with a list."
    },
    {
      "severity": "P2",
      "evidence_level": "reasoned from code and request text",
      "location": "retry.py:6",
      "scenario": "The default retry_on=(Exception,) retries programming errors (TypeError, KeyError) 5 times with delays, and re-executes non-idempotent fn on any error. The request says 'chosen exceptions'.",
      "fix": "Make retry_on a required keyword argument (owner API decision). Test that a TypeError is not retried by default."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned from code (not run)",
      "location": "retry.py:12-13, retry.py:22",
      "scenario": "Negative base or cap gives a negative sleep; time.sleep raises ValueError inside the except block, masking the real error. Non-integer attempts fails later in range().",
      "fix": "Validate base >= 0, cap >= 0, and attempts as an int at entry. Test that retry(lambda: 1, cap=-1) raises ValueError."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned from test code",
      "location": "test_retry.py:18,31,41",
      "scenario": "All delay tests use rng=1.0, so removing the jitter multiplication still passes all 6 tests. Full jitter is untested.",
      "fix": "Add a test with rng=lambda: 0.5, base=1, cap=100 asserting slept == [0.5, 1.0]."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned from docstring and random.random contract",
      "location": "retry.py:9-10",
      "scenario": "The docstring says the delay is in [0, d] but random.random() returns [0, 1), so the actual range is [0, d).",
      "fix": "Correct the docstring to [0, d), or state the rng contract."
    }
  ]
}
```