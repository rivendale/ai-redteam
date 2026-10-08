# pr-review: retry helper

## Review report

**REVIEWED:** No PR number, head SHA or merge base was provided, so I could not freeze the target (Step 1). This review covers only the text of `retry.py` and `test_retry.py` as pasted. Any commit that differs from that text is unreviewed.

**TIER:** Standard. The change is ordinary library code. It touches no auth, secrets, network exposure, migrations, money or personal data. It is a shared library used by production jobs, which raises the stakes but not the tier. The context also asked for standard seats only.

**DATA (Step 3):** The code is a generic helper with no data it could carry. It was reviewed in this session only and sent nowhere else.

**REVIEWERS:**
- Reviewer: this session (Claude Opus 5.5, `claude-opus-5-5`), one round. This session did not write the change.
- Author: unknown. No commit trailers were provided.

**Method and limits:** I have no tools in this session, so I ran nothing. The claim "6 tests, all pass" is unverified. I traced each test by hand against the code, and all six should pass:
- `[1, 2]`
- `calls == 3` and `"boom 3"`
- 2 sleeps
- `calls == 1`
- `[1, 2, 3, 3, 3]`
- `ValueError`

**Check against the request:** Every requested feature is present:
- retry on chosen exceptions
- exponential backoff with full jitter
- a cap on the delay
- N attempts, then re-raise the last error
- injectable sleep and random source

Nothing extra was added. "Clock" is satisfied by the injectable `sleep`, because the helper never reads the time.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `retry.py:21` | `base` is a float, which the default `0.1` is. When `k >= 1024`, `base * (2 ** k)` converts `2**1024` to float and raises `OverflowError: int too large to convert to float`. This happens inside the `except` block, before `min(cap, …)` can clamp the value. Example: a long-running job uses `attempts=5000, cap=30` to mean "keep trying for hours". After about 1024 failures it dies with `OverflowError` instead of retrying or re-raising the real error. The original error survives only as `__context__`. | `retry(Flaky(10**6), attempts=1100, sleep=lambda s: None, rng=lambda: 1.0)` should raise `ConnectionError`. Today it raises `OverflowError`. Fix: clamp the exponent, e.g. `base * 2 ** min(k, 64)`, or stop doubling once the value exceeds `cap`. |
| 2 | P2 | `retry.py:7`, `retry.py:18` | `retry_on` is never validated, and `except` only checks its operand when an exception is actually raised. Example: a caller passes `retry_on=[ConnectionError]` (a list) or `retry_on=(ConnectionError, "Timeout")`. Every call that succeeds works fine. The first real failure in production raises `TypeError: catching classes that do not inherit from BaseException is not allowed` instead of retrying. The bug only shows up during an incident. | `with assertRaises(TypeError): retry(lambda: 1, retry_on=[ConnectionError])` should raise at call time. Today it returns `1`. Fix: at entry, normalize a single class to a tuple, then check that `retry_on` is a tuple of `BaseException` subclasses. |
| 3 | P3 | `test_retry.py:18,30,41` | Every test that checks sleep durations uses `rng=lambda: 1.0`. Multiplying by 1.0 changes nothing, so the suite cannot detect a regression that removes jitter. If someone changes line 21 to `sleep(min(cap, base * (2 ** k)))`, all six tests still pass, and the shared library starts producing synchronized retry storms across production jobs. | `retry(Flaky(2), sleep=slept.append, rng=lambda: 0.5, base=1, cap=100)` should give `slept == [0.5, 1.0]`. Also add one test with `rng=lambda: 0.0`. |
| 4 | P3 | `retry.py:15-16` | Only `attempts` is validated. A negative `cap` or `base` (for example, a config typo `cap=-5`) produces a negative delay. `time.sleep(-x)` then raises `ValueError: sleep length must be non-negative` inside the `except` block, replacing the first transient error with a confusing one. A `cap` of `0` silently disables backoff. | `with assertRaises(ValueError): retry(lambda: 1, cap=-1)` should raise at entry. Today it returns `1`. |
| 5 | P3 | `retry.py:7` | The request says to retry on *chosen* exceptions, but the default `retry_on=(Exception,)` retries everything when the caller chooses nothing. Example: a production job calls `retry(fn)` and `fn` has a bug (`TypeError`, `KeyError`). The job retries a deterministic failure 5 times and waits up to about 1.5 s before surfacing it. Across many jobs, this hides real bugs as "flaky". | `retry(Flaky(5, exc=TypeError), sleep=slept.append)` should make 1 call. Today it makes 5. This is a design decision for the owner: either make `retry_on` required or keep the current default and document it. |

**FILES NEEDED BUT NOT PROVIDED:**
- PR identifier, head SHA and merge base SHA
- commit log with trailers (authorship)
- CI configuration and check results
- the library's callers, to see whether any pass large `attempts` (finding 1) or non-tuple `retry_on` (finding 2)

## Close-out

The author has not adjudicated these findings yet, and a reviewer never adjudicates its own findings, so the close-out is pending.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1–5 | Pending author | — |

**VERIFIED AFTER FIXES:** Nothing yet.

**MERGE RECOMMENDATION:** Not yet decidable. I found no blockers (no P0 or P1). Merging still requires:
- the reviewed head SHA to be recorded and matched to this text;
- every finding to have a written decision (all are P2 or P3, so each may be deferred with a tracking issue);
- CI checks to be present and green. None were shown, and a missing check is not green;
- an owner decision on finding 5.

```json
{
  "verdict": "no blockers found; merge recommendation pending SHA freeze, adjudication of 5 findings, CI checks, and owner decision on finding 5",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "traced by reading code (not run)",
      "location": "retry.py:21",
      "scenario": "With float base (default 0.1) and attempts > 1024, base * 2**k raises OverflowError at k=1024 inside the except block, before min(cap, ...) clamps it, masking the real error in long-running retry loops.",
      "fix": "Clamp the exponent (e.g. base * 2 ** min(k, 64)) or stop doubling once the delay exceeds cap; add a test with attempts=1100 expecting ConnectionError."
    },
    {
      "severity": "P2",
      "evidence_level": "traced by reading code (not run)",
      "location": "retry.py:7, retry.py:18",
      "scenario": "retry_on=[ConnectionError] or a tuple containing a non-exception is only evaluated when fn raises, so the first real failure raises TypeError instead of retrying; successful calls never reveal it.",
      "fix": "Normalize a single class to a tuple and validate at entry that retry_on is a tuple of BaseException subclasses; test that a list raises TypeError at call time."
    },
    {
      "severity": "P3",
      "evidence_level": "traced by reading tests (not run)",
      "location": "test_retry.py:18,30,41",
      "scenario": "All delay assertions use rng=1.0, so removing the jitter multiplication from retry.py:21 passes all six tests.",
      "fix": "Add tests with rng=0.5 (expect [0.5, 1.0]) and rng=0.0."
    },
    {
      "severity": "P3",
      "evidence_level": "traced by reading code (not run)",
      "location": "retry.py:15-16",
      "scenario": "Negative cap or base gives a negative delay; time.sleep raises ValueError inside the except block, replacing the transient error.",
      "fix": "Validate base >= 0 and cap >= 0 at entry, alongside the attempts check."
    },
    {
      "severity": "P3",
      "evidence_level": "traced by reading code (not run)",
      "location": "retry.py:7",
      "scenario": "Default retry_on=(Exception,) retries deterministic bugs (TypeError, KeyError) 5 times with sleeps, although the request says retry on chosen exceptions.",
      "fix": "Owner decision: make retry_on required, or keep the default and document it."
    }
  ]
}
```