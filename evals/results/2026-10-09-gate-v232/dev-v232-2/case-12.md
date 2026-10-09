# Redteam report: `retry.py` / `test_retry.py`

**Review conditions:** I am a single reviewer with no tools. I did not write this work, but I had no way to start a fresh subagent and could not run the code. Every finding comes from reading and tracing the code, not from running it. Re-run the reproductions below before relying on them.

**VERDICT: SHIP WITH FIXES.** The retry logic matches the request on the main path, but no test checks the jitter, and two inputs raise the wrong error instead of retrying or re-raising the last error.

**CONFIDENCE: medium.** Limits: no tools, so the tests and reproductions were traced, not run; the "6 tests, all pass" claim was not seen; a single reviewer.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, retry.py, test_retry.py.
- **Not seen:**
  - Output of the test run. Matters a little: it would settle the "all pass" claim, which my trace agrees with.
  - Target Python version. Low impact.
  - Production callers and how they set `attempts` and `retry_on`. Matters for how likely F2 and F3 are.

**COVERAGE**
- **Scope:** the whole work, both files.
- **Checked:**
  - `retry.py:retry`: validation, loop, exception filter, delay formula, final raise.
  - All 6 tests, traced against the code.
  - request.md, read clause by clause.
  - context.md.
- **Not checked:**
  - Running tests or mutations (no tools).
  - Production callers (not supplied).

**SEATS AND GATE:** the local reviewer ran. Cross-vendor seats were declined because the context asked for standard seats only. The sensitivity gate passed: no personal or confidential data.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | PROBABLE (traced; not run) | B | test_retry.py:19, 32, 44 (`rng=lambda: 1.0` in every test that checks delays) | Full jitter, a core requirement, has no test. Each test that asserts a delay uses an rng that returns 1.0, which makes `rng() * x` equal `x`. | Someone later "simplifies" line 22 to `sleep(min(cap, base * 2**k))`. All 6 tests stay green. Production jobs then retry in lockstep (thundering herd) against a recovering dependency. | **Fix:** add a test with `rng=lambda: 0.5`, `base=1`, `cap=100`, expecting `slept == [0.5, 1.0]`. **Repro:** in a scratch copy, delete `rng() *` from retry.py:22 and run `python -m unittest test_retry`. Expected: a failure. Traced result: 6 pass. | a✔ b✘ c✘ d✘ |
| F2 | Medium | PROBABLE (Python int→float semantics; not run) | B | retry.py:22 `base * (2 ** k)` | `2 ** k` is an exact int. Multiplying it by a float raises `OverflowError` once k ≥ 1024. This happens before `min(cap, …)` can clamp it. | A job sets `attempts=2000` and `cap=5` to retry for about 80 minutes. On the 1025th failure the helper raises `OverflowError` instead of retrying, and never re-raises the last error as the request requires. | **Fix:** clamp the exponent, e.g. `base * 2 ** min(k, 60)`, or carry the delay forward with `min(cap, prev*2)`. **Repro:** `retry(Flaky(10**4), attempts=1100, sleep=lambda s: None)`. Expected: `ConnectionError("boom 1100")`. Traced result: `OverflowError: int too large to convert to float`. | a✔ b✘ c✔ d✘ |
| F3 | Medium | PROBABLE (Python `except` semantics; not run) | B | retry.py:6, 18 (`retry_on` not validated) | `except retry_on` only accepts a class or a tuple of classes. A list, or a non-exception class, fails only when an exception actually occurs. | A caller writes `retry_on=[ConnectionError]`. Success paths and happy-path tests work. On the first real `ConnectionError` in production, Python raises `TypeError: catching classes that do not inherit from BaseException is not allowed`, and the job gets no retry at all. | **Fix:** at entry, convert a non-class `retry_on` to a tuple and check that each item is a subclass of `BaseException`, raising `TypeError` early. **Repro:** `retry(Flaky(1), retry_on=[ConnectionError], sleep=lambda s: None)`. Expected: `"ok"`. Traced result: `TypeError`. | a✔ b✘ c✔ d✘ |
| F4 | Low | CONFIRMED (read) | B | retry.py:6 `retry_on=(Exception,)` | The request says to retry on *chosen* exceptions, but the default retries everything, including programming errors such as `TypeError` and `KeyError`. | A bug in `fn` is retried 5 times with backoff, which delays and hides the real failure in production jobs. | **Fix:** make `retry_on` a required argument, or document the broad default. **Repro:** `retry(Flaky(10, exc=TypeError), sleep=slept.append)` sleeps 4 times before raising. | a✔ b✔ c✘ d✘ |
| F5 | Low | PROBABLE (not run) | B | retry.py:6, 12–13 | `base` and `cap` are not validated. A negative value gives a negative delay, and `time.sleep` then raises `ValueError` inside the except block. | Config sets `cap=-1` by mistake. The first retry raises `ValueError: sleep length must be non-negative` instead of retrying. | **Fix:** check `base >= 0` and `cap >= 0` next to the `attempts` check. **Repro:** `retry(Flaky(1), cap=-1)` raises `ValueError` from sleep, not `"ok"`. | a✔ b✘ c✘ d✘ |

There are no High or Critical candidates. I ran the confirm-or-refute check on F2 and F3 as possible High findings. Both stay Medium: they are real, but they need unusual input (more than 1024 attempts, or a list passed as `retry_on`), so the d question is no.

## Needs validation
- **Clock injection.** The request asks for an injectable "clock". The work injects only `sleep`. That is enough if "clock" meant the sleep source. It falls short if the requester expected a `now()` clock, for example for an overall deadline. To settle it: ask the requester what "clock" meant.

## Refuted
- **`raise last` could raise `None`.** Refuted: `attempts >= 1` is enforced at line 12. Every run of the loop either returns, propagates a non-matching exception, or sets `last` before line 21 breaks out.
- **Sleeps after the final attempt.** Refuted: line 20 breaks before the sleep when `k == attempts-1`, and test_retry.py:33 checks this.
- **Swallows KeyboardInterrupt or SystemExit.** Refuted: the default is `Exception`, not `BaseException`.
- **Off-by-one in the backoff.** Refuted: the first delay bound is `base * 2**0 = base`. This matches the standard full-jitter formula `rand(0, min(cap, base*2^attempt))`.
- **Traceback lost on re-raise.** Refuted: `raise last` re-raises the same exception object, and its `__traceback__` is kept.

## What holds up
- The attempt count, the stop-after-N behaviour, and re-raising the *last* error (test_retry.py:27 checks "boom 3").
- Non-matching exceptions propagate immediately (test at line 35).
- The cap is applied (test at line 41; traced as `[1,2,3,3,3]`).
- Both `sleep` and `rng` are injectable.
- No sleep after the last try.
- Input validation for `attempts`.
- Minor wording point: the docstring describes a closed interval `[0, …]`, but the default `random.random()` returns values in `[0, 1)`. This is harmless.

## Unverified claims
- **"6 tests, all pass."** I traced each test and expect all 6 to pass, but I did not run them. To confirm: run `python -m unittest test_retry` and attach the output.

## Questions for the author
1. Did "clock" mean only the sleep function, or should there also be a time source for a total deadline?
2. Do any production jobs use `attempts` above roughly 1000, or pass `retry_on` as a list? If so, F2 or F3 become High.

## Decision-maker summary
Fix F1–F3 before this shared library goes into production jobs. Each fix is a few lines plus a test. If it ships as is, a later change could remove the jitter without any test failing, and two input mistakes produce confusing errors instead of retries.

## Owner summary
The retry helper does what was asked in normal use. However, the tests never check its randomized waiting, so that could break later without anyone noticing. Two unusual settings also make it fail with a confusing error instead of retrying, and each needs a small fix and test before wide use.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "retry.py", "status": "seen", "matters": true},
    {"item": "test_retry.py", "status": "seen", "matters": true},
    {"item": "test run output for '6 tests, all pass'", "status": "not_seen", "matters": false},
    {"item": "production callers and their retry settings", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "local-reviewer (no tools, no subagent)", "status": "ran", "cross_vendor": false},
    {"vendor": "cross-vendor", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "retry.py", "kind": "file"},
      {"unit": "retry.py:retry", "kind": "function"},
      {"unit": "test_retry.py", "kind": "file"},
      {"unit": "claim: 6 tests, all pass", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "test and mutation execution", "reason": "no_tools"},
      {"unit": "production callers", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "test_retry.py:19,32,44",
     "scenario": "Every delay-asserting test uses rng=lambda: 1.0, so removing rng() from retry.py:22 keeps all 6 tests green; jitter regresses unnoticed and production jobs retry in lockstep.",
     "fix": "Add a test with rng=lambda: 0.5, base=1, cap=100 expecting slept == [0.5, 1.0].",
     "reproduction": "In a scratch copy, change retry.py:22 to sleep(min(cap, base * (2 ** k))); run python -m unittest test_retry; expected a failure, traced result 6 pass.",
     "answers": {"a": true, "b": false, "c": false, "d": false}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "retry.py:22",
     "scenario": "With attempts > 1024 and persistent failure, base * 2**k raises OverflowError at k=1024 before min(cap, ...) clamps it, so the last error is never re-raised.",
     "fix": "Clamp the exponent (base * 2 ** min(k, 60)) or carry the delay forward with min(cap, prev * 2).",
     "reproduction": "retry(Flaky(10**4), attempts=1100, sleep=lambda s: None): expected ConnectionError('boom 1100'), traced OverflowError.",
     "answers": {"a": true, "b": false, "c": true, "d": false}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "retry.py:6,18",
     "scenario": "retry_on=[ConnectionError] (a list) works on success, but the first real failure raises TypeError from the except clause and no retry happens.",
     "fix": "At entry, convert a non-class retry_on to a tuple and check every item is a BaseException subclass, raising TypeError early.",
     "reproduction": "retry(Flaky(1), retry_on=[ConnectionError], sleep=lambda s: None): expected 'ok', traced TypeError.",
     "answers": {"a": true, "b": false, "c": true, "d": false}},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "retry.py:6",
     "scenario": "The default retry_on=(Exception,) retries programming errors such as TypeError, delaying and hiding bugs in production jobs; the request asks for chosen exceptions.",
     "fix": "Make retry_on a required argument, or document the broad default.",
     "reproduction": "retry(Flaky(10, exc=TypeError), sleep=slept.append): 4 sleeps occur before TypeError is raised.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "B",
     "location": "retry.py:6,12-13",
     "scenario": "A negative cap or base gives a negative delay; time.sleep raises ValueError inside the except block instead of retrying.",
     "fix": "Check base >= 0 and cap >= 0 next to the attempts check.",
     "reproduction": "retry(Flaky(1), cap=-1): expected 'ok', traced ValueError from time.sleep.",
     "answers": {"a": true, "b": false, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "A",
     "location": "retry.py:6 (sleep parameter)",
     "suspicion": "The request asks for an injectable clock; only sleep is injectable, with no now() source.",
     "unresolved_fact": "Whether the requester meant only the sleep function or also a time source (for example for a deadline)."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "raise last could raise None.", "evidence": "attempts >= 1 is enforced at retry.py:12; every path sets last or exits before line 23."},
    {"id": "C2", "candidate": "Sleeps after the final attempt.", "evidence": "retry.py:20-21 breaks before the sleep; test_retry.py:33 checks this."},
    {"id": "C3", "candidate": "KeyboardInterrupt or SystemExit swallowed.", "evidence": "The default retry_on is Exception, not BaseException."},
    {"id": "C4", "candidate": "Off-by-one in the backoff exponent.", "evidence": "The first bound is base * 2**0 = base, matching the standard full-jitter formula."},
    {"id": "C5", "candidate": "Traceback lost on re-raise.", "evidence": "raise last re-raises the same object, and its __traceback__ is kept."}
  ]
}
```