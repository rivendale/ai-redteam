# pr-review: retry helper

**Review report**

**REVIEWED:** Not identifiable. The inputs give file contents but no PR number, head SHA or merge base, so Step 1 cannot be completed. This review covers only the `retry.py` and `test_retry.py` text shown above. Any commit that differs from that text is unreviewed.

**TIER:** Standard. This is ordinary code with no auth, secrets, migrations, money or personal data. It is a shared library used by production jobs, which raises the stakes but not the category. The context asked for standard seats only, which fits.

**REVIEWERS:** This instance (Opus 5.5, claude-opus-5-5). It did not write the change, so it is independent. The author is unknown because no commit trailers were provided. Data handling (Step 3): nothing was sent outside this session.

**Evidence limits:** This session had no tools, so I ran nothing. The claim "6 tests, all pass" is the author's assertion and I have not verified it. Every finding below comes from reading the code. The failure scenarios are traced through Python semantics but not executed.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `retry.py:19` (`except retry_on as e`) | A caller passes `retry_on=[ConnectionError]` (a list, not a tuple). Python checks the `except` target only when an exception is actually raised. So the happy path works, and the first real failure in production raises `TypeError: catching classes that do not inherit from BaseException is not allowed` instead of retrying. The existing tests always pass tuples or the default, so they cannot catch this. | `retry(Flaky(1), retry_on=[ConnectionError], sleep=lambda s: None)` should return `"ok"` (or `retry` should reject the list up front with `TypeError`). Today it raises `TypeError` on the first failure. Fix: `retry_on = tuple(retry_on) if not isinstance(retry_on, type) else (retry_on,)` and check that each entry subclasses `BaseException`. |
| 2 | P2 | `retry.py:23` (`base * (2 ** k)`) | `min(cap, ...)` runs after the product is computed. With the default float `base=0.1` and `attempts >= 1026`, the loop reaches k=1024, and `0.1 * 2**1024` raises `OverflowError: int too large to convert to float`. That error comes from inside the `except` block, so it replaces the real error. Someone setting `attempts=10_000, cap=5` for a long-lived job hits this, even though the cap makes the large count look safe. | `retry(Flaky(2000), attempts=1100, sleep=lambda s: None, rng=lambda: 0.0)` should raise `ConnectionError("boom 1100")`. Today it raises `OverflowError`. Fix: bound the exponent, e.g. `min(cap, base * 2 ** min(k, 64))`, or compare `k` against `log2(cap/base)` before multiplying. |
| 3 | P3 | `retry.py:15-16` (only `attempts` is validated) | `base < 0` or `cap < 0`, or an injected `rng` that returns a value outside [0, 1], produces a negative delay. Then `time.sleep(-x)` raises `ValueError: sleep length must be non-negative` from inside the `except` block. This masks the real error, and it only happens on the first retry, never at call time. | `retry(lambda: 1, base=-1)` and `retry(lambda: 1, cap=-1)` should raise `ValueError` immediately. Today both return `1`, and the bad values fail only later, on a retry. |
| 4 | P3 | `test_retry.py:18-19, 32-33, 43-44` (every sleep-checking test uses `rng=lambda: 1.0`) | Every test that inspects delays uses an rng of exactly 1.0. An implementation that ignored `rng` entirely (no jitter) would pass all six tests. Full jitter is the property that prevents synchronized retries across production jobs, and nothing tests it. | With `rng=lambda: 0.5, base=1, cap=100` and `Flaky(2)`, assert `slept == [0.5, 1.0]`. With `rng=lambda: 0.0`, assert every delay is `0`. |
| 5 | P3 | `retry.py:7` (`retry_on=(Exception,)`) | The request says "retry on *chosen* exceptions". The default retries everything, including programming errors such as `TypeError` and `AttributeError`. A bug in `fn` therefore gets retried 5 times with backoff before it surfaces, and a non-idempotent `fn` may partially run several times. | `retry(lambda: None.x, sleep=slept.append)` should call `fn` once and leave `slept == []`. Today it calls `fn` 5 times and sleeps 4 times. Fix: make `retry_on` a required argument, or document the default as a deliberate choice. |

Checked and not a finding:
- `raise last` keeps the original traceback through `__traceback__`.
- `KeyboardInterrupt` and `SystemExit` are not caught, because they are not subclasses of `Exception`.
- No sleep happens after the final attempt.
- The non-matching exception path propagates on the first call.
- "Injectable clock": the request asks only for backoff, not a deadline, so injecting `sleep` satisfies it.

**FILES NEEDED BUT NOT PROVIDED:** the PR identifier and head and merge-base SHAs, the commit trailers, the CI results for the six tests, and the library's callers (to see whether any pass a list for `retry_on` or rely on the catch-all default).

---

**Close-out**

**ADJUDICATION:** Pending. The author has not adjudicated, and a reviewer never adjudicates its own findings.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1–5 | Awaiting author | — |

**VERIFIED AFTER FIXES:** None yet. Verify fixes by reading the correction diff and running the suggested tests. No second full review is needed.

**MERGE RECOMMENDATION:** Merge after fixes, but not yet.
- No P0 or P1 found. Findings 1 and 2 are P2; they are cheap to fix and should be fixed or deferred with an issue before a shared production library ships.
- Still open:
  - no head SHA, so it is unclear what exactly was reviewed;
  - CI checks not seen (missing is not green);
  - every finding still needs a written decision.

```json
{
  "verdict": "merge_after_fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "reasoned_from_code_not_run",
      "location": "retry.py:19",
      "scenario": "retry_on passed as a list (e.g. [ConnectionError]); on the first real exception the except clause raises TypeError ('catching classes that do not inherit from BaseException is not allowed') instead of retrying; happy path hides it.",
      "fix": "Normalize retry_on to a tuple (accept a single class too) and validate that entries subclass BaseException at call time; add a test with a list."
    },
    {
      "severity": "P2",
      "evidence_level": "reasoned_from_code_not_run",
      "location": "retry.py:23",
      "scenario": "With float base (default 0.1) and attempts >= 1026, base * 2**1024 raises OverflowError before min(cap, ...) applies; raised inside the except block, it replaces the real error.",
      "fix": "Bound the exponent before multiplying, e.g. min(cap, base * 2 ** min(k, 64)); add a test with attempts=1100 expecting the original exception."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned_from_code_not_run",
      "location": "retry.py:15-16",
      "scenario": "Negative base or cap (or an rng returning a value outside [0,1]) gives a negative delay; time.sleep raises ValueError on the first retry, masking the real error, instead of failing at call time.",
      "fix": "Validate base >= 0 and cap >= 0 up front alongside attempts; clamp delay to >= 0."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned_from_code_not_run",
      "location": "test_retry.py:18-19, 32-33, 43-44",
      "scenario": "All delay assertions use rng=1.0, so an implementation that ignores rng (no jitter) passes every test; full jitter is untested.",
      "fix": "Add tests with rng=0.5 (expect [0.5, 1.0] for base=1) and rng=0.0 (expect all zeros)."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned_from_code_not_run",
      "location": "retry.py:7",
      "scenario": "Default retry_on=(Exception,) retries programming errors like TypeError/AttributeError 5 times with backoff, delaying bug surfacing and re-running non-idempotent fn; request says 'chosen exceptions'.",
      "fix": "Make retry_on required, or document the catch-all default explicitly and test it."
    }
  ]
}
```