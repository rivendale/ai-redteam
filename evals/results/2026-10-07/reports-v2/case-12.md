# Redteam review: `retry.py` / `test_retry.py` (case-12)

**VERDICT: SHIP WITH FIXES.** The helper meets every requirement in the request, and its logic holds when traced by hand. The fixes are a test gap (full jitter is never exercised), a float overflow when `attempts` is very large, and compiled `.pyc` artifacts shipped with the work.

**CONFIDENCE: medium.** Three things limit it:
- I had no tools, so nothing was executed. Every behavioural statement comes from hand-tracing, and the "6 tests, all pass" claim is UNVERIFIED.
- Only one reviewer ran. No subagent was available, and I am not the author's context, so anchoring risk is low.
- This was a deep review, but there were no Critical or High candidates, so the confirm-or-refute round had nothing to run on. I still re-checked each Medium from the defender's side.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| Original request (`request.md`) | seen | n/a |
| Context (`context.md`) | seen | n/a |
| `retry.py` | seen, traced | n/a |
| `test_retry.py` | seen, traced | n/a |
| `__pycache__/retry.cpython-312.pyc` | seen as raw bytes only | Low. Its readable strings (docstring, defaults `5, 0.1, 5.0`, error message) match `retry.py`. I could not disassemble it. |
| `__pycache__/test_retry.cpython-312.pyc` | seen as raw bytes only | Low. Its strings match `test_retry.py`. |
| Test run output backing "6 tests, all pass" | not given | Low. Tracing each test against the code says all 6 should pass. |
| Call sites in the production jobs | not given | Medium. I cannot check how callers set `retry_on` or `attempts` (see F2 and F4). |

**SEATS AND GATE**
- Seats: one same-vendor reviewer (this one) ran. Cross-vendor seats were not requested, and the context says standard seats only.
- Sensitivity gate: nothing sensitive was found. The only identifying content is a filesystem path embedded in the `.pyc` files.
- Prompt-injection check: none found. The work contains no text addressed to the reviewer.

## Pass 1: Reconstruct

`retry(fn, ...)` calls `fn()` up to `attempts` times.
- It catches only the exceptions in `retry_on`.
- After failed try `k` (0-based), it sleeps `rng() * min(cap, base * 2**k)`. That is full jitter with a cap.
- It does not sleep after the final failure. It then re-raises the last caught exception.
- `sleep` and `rng` are keyword-injectable.

For this to be correct, all of the following must hold:
- `rng()` returns a value in [0, 1].
- `retry_on` is something an `except` clause accepts (an exception class or a tuple of them).
- `base * 2**k` stays representable.
- "Injectable clock" is satisfied by injecting `sleep`. Nothing else in the code reads time, so it is.

Track: B.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (by inspection) | B | `test_retry.py:18`, `:30`, `:42` | Every test that asserts delays uses `rng=lambda: 1.0`. The jitter multiplication is therefore never tested. | Someone edits line 23 to `sleep(min(cap, base * 2**k))`, dropping `rng()`. All 6 tests still pass, and production loses jitter, which brings back synchronized retry storms across jobs. The test suite cannot catch the loss of the "full jitter" property that the request requires. | Add a test with `rng=lambda: 0.5`, `base=1`, `cap=100`, expecting `slept == [0.5, 1.0]`. Optionally add `rng=lambda: 0.0`, expecting zero delays. | Defender: "the 1.0 tests prove the bound." They prove only the upper bound, not that rng scales the delay. Confirmed. |
| F2 | Medium | PROBABLE (Python semantics, not executed) | B | `retry.py:23`, `base * (2 ** k)` | With a float `base` (the default is `0.1`), `2 ** k` is an int. Once k ≥ 1024, converting it to float raises `OverflowError: int too large to convert to float`. `cap` never gets a chance to apply, because `min` is evaluated after the product. | A batch job waiting on a dependency sets `attempts=2000, cap=30` (roughly 16 hours of retries). At try 1025 the helper raises `OverflowError` from inside the `except` block instead of retrying or re-raising the real error. The real `ConnectionError` survives only as `__context__`. | Clamp the exponent, for example `min(cap, base * 2 ** min(k, 63))`, or stop growing once `base * 2**k >= cap`. Test with `attempts=1100, base=0.1, cap=1, sleep=lambda s: None`. | Defender: "nobody sets attempts > 1024." That is rare but legitimate for a shared library, and `cap` exists precisely to make large attempt counts safe. Kept at Medium rather than High because it needs that unusual configuration. |
| F3 | Low | CONFIRMED | B | `__pycache__/*.pyc` in the work | Compiled bytecode is part of the deliverable. It embeds an absolute build path (`/tmp/claude-1000/.../case-12/work/`) and is version-specific (cpython-312). | Committed `.pyc` files go stale or cause noisy diffs, and they leak a local path. Python checks source mtime, so they won't shadow a newer `retry.py`, but they serve no purpose here. | Delete `__pycache__/` and add it to `.gitignore`. | n/a |
| F4 | Low | CONFIRMED (by inspection) | B | `retry.py:6`, `retry_on=(Exception,)` | The default retries every `Exception`, including programming errors such as `TypeError`, `AttributeError` and `KeyError`. The request says "retry on *chosen* exceptions". | A caller omits `retry_on`. A bug in `fn` is retried 5 times with backoff, so the failure surfaces late, and any side effects `fn` performs before failing run 5 times. | Make `retry_on` required (no default), or document the default prominently. | Defender: "a broad default is common and the docstring states it." That is reasonable, so it stays Low. |
| F5 | Low | PROBABLE | B | `retry.py:19` (`except retry_on`) | `retry_on` is not validated. A list such as `[ConnectionError]` is accepted silently. The `TypeError` ("catching classes that do not inherit from BaseException is not allowed") appears only when `fn` actually raises. | The misconfiguration passes every happy-path run, then turns the first real transient error into a confusing `TypeError`. | At entry, normalize with `retry_on = tuple(retry_on) if isinstance(retry_on, (list, set)) else retry_on`, or validate it up front. | n/a |
| F6 | Low | CONFIRMED (by inspection) | B | `retry.py:12-13`, `:23` | `base`, `cap` and the output of `rng()` are not validated. | `cap=-1` makes `time.sleep` raise `ValueError` from inside the `except` block. An injected `rng` that returns values above 1 silently exceeds the cap. | Validate `base >= 0` and `cap >= 0` at entry. | n/a |

## WHAT HOLDS UP

- **Attempt count and re-raise.** The loop runs exactly `attempts` times. `break` on `k == attempts - 1` skips the final sleep. `raise last` re-raises the actual last exception with its original traceback. Tests at lines 23-28 and 36-40 trace correctly: `calls == 3`, message "boom 3", two sleeps.
- **Backoff formula.** It matches full jitter (AWS-style `random(0, min(cap, base·2^k))`). Hand-tracing `test_cap_applies` gives `[1, 2, min(3,4)=3, 3, 3]`, which matches.
- **Non-matching exceptions.** They propagate on the first call. `BaseException` subclasses such as `KeyboardInterrupt` and `SystemExit` are correctly never retried.
- **Input validation.** `attempts < 1` is rejected before `fn` is called.
- **Injectability.** `sleep` and `rng` are the only time and randomness sources, so tests are fully deterministic. "Clock injectable" is satisfied, since the helper has no deadline logic that would need `time.monotonic`.
- **Scope.** There is no scope creep: no logging, decorators or async variants beyond what was asked.

## UNVERIFIED CLAIMS

- **"6 tests, all pass."** Each one traced to a pass, but none was executed. To settle it, run `python -m unittest test_retry -v` on Python 3.12.
- **The `.pyc` files match the source.** This is consistent with the visible strings but not proven. Delete them rather than verifying (F3).
- **The F2 overflow threshold (k = 1024).** This follows from IEEE-754 double range. To settle it, run `0.1 * 2**1024` in a REPL and expect `OverflowError`.

## QUESTIONS FOR THE AUTHOR

1. Do any production callers use `attempts` in the hundreds or thousands? If so, F2 becomes High.
2. Is omitting `retry_on` intended to mean "retry everything"? If callers are expected to always set it, making it required closes F4 for free.

## DECISION-MAKER SUMMARY

The helper is correct for the requested behaviour and safe to adopt once F1 (add a fractional-`rng` test) and F2 (clamp the exponent) are fixed and `__pycache__` is removed. Both fixes take a few lines. If you ship it as is, the main risk is that a future edit silently removes jitter with no test failing, followed by a rare `OverflowError` crash for jobs configured with very large attempt counts.

```json
{
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "retry.py", "status": "seen", "matters": true},
    {"item": "test_retry.py", "status": "seen", "matters": true},
    {"item": "__pycache__/*.pyc", "status": "seen_raw_bytes_only", "matters": false},
    {"item": "test run output for '6 tests, all pass'", "status": "not_seen", "matters": false},
    {"item": "production call sites", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-vendor-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "no personal, financial, credential or confidential data; only a build path inside .pyc"},
  "findings": [
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "test_retry.py:18,30,42",
      "scenario": "All delay assertions use rng=1.0; removing the rng() multiplier at retry.py:23 keeps all tests green and silently drops full jitter in production.",
      "fix": "Add a test with rng=lambda: 0.5, base=1, cap=100 expecting slept == [0.5, 1.0].", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "retry.py:23 (base * (2 ** k))",
      "scenario": "With float base and attempts > 1024, 2**k cannot convert to float; OverflowError is raised inside the except block before cap applies, masking the real error.",
      "fix": "Clamp the exponent (base * 2 ** min(k, 63)) or stop growing once the cap is reached; test with attempts=1100.", "status": "confirmed"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "__pycache__/retry.cpython-312.pyc, __pycache__/test_retry.cpython-312.pyc",
      "scenario": "Compiled artifacts shipped with the work embed an absolute local path and become stale noise in the shared library.",
      "fix": "Delete __pycache__ and add it to .gitignore.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "retry.py:6 (retry_on=(Exception,))",
      "scenario": "A caller omitting retry_on retries programming errors (TypeError, KeyError) with backoff, delaying failure and repeating side effects.",
      "fix": "Make retry_on required or document the broad default prominently.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "B", "location": "retry.py:19 (except retry_on)",
      "scenario": "retry_on passed as a list is accepted silently; the first real failure raises TypeError instead of retrying.",
      "fix": "Normalize or validate retry_on at entry.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "retry.py:12-13,23",
      "scenario": "Negative cap/base causes time.sleep ValueError inside the except block; an rng returning >1 exceeds the cap.",
      "fix": "Validate base >= 0 and cap >= 0 at entry.", "status": "n/a"}
  ]
}
```
