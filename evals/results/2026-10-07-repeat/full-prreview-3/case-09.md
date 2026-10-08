# pr-review: invoice_report.py

**Review report**

**REVIEWED:** No PR number, head SHA or merge base SHA was provided. I could not freeze the target (Step 1). This review covers only the two files as pasted in this session. If the PR's head differs from this text, this review does not apply to it.

**TIER:** Standard. This is ordinary code: read-only reporting over invoice amounts. It has no auth, secrets, network exposure, migrations or money movement, and the context sets the stakes as standard. One round is required, and this is that round.

**REVIEWERS:**
- Reviewer: this instance (claude-opus-5-5), which had no part in writing the change. Nothing was sent to any other model or endpoint.
- Author: unknown. No commits or trailers were provided.
- I had no tools, so nothing was executed. Evidence levels are stated per finding.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `invoice_report.py:9` | `json.loads(..., strict_mode=True)`: `strict_mode` is not a parameter of `json.loads`. Unknown keyword arguments are forwarded to `JSONDecoder(**kw)`, which raises `TypeError: __init__() got an unexpected keyword argument 'strict_mode'`. So `load_invoices` fails on every call, whatever the file contains. The module cannot do its main job of loading a JSON file. The real parameter is `strict`, and it defaults to `True`, so the fix is to drop the argument and use `json.load(f)`. *Evidence: reading against the stdlib `json.loads` signature; not executed.* | Write `[{"id":1,"date":"2026-03-04","amount":120.5}]` to a temp file. Assert that `load_invoices(path)` returns a one-element list. This raises `TypeError` today. |
| 2 | P2 | `invoice_report.py:24` | If no invoice falls in the requested month, `len(in_month) == 0` and the function raises `ZeroDivisionError`. Example: `monthly_average(SAMPLE, 2026, 5)`. Asking about a month with no invoices is a normal input. The workaround is for the caller to check `monthly_total` or the count first. *Evidence: code reading; certain.* | `monthly_average(SAMPLE, 2026, 5)` returns `0.0` or `None` (whichever is chosen and documented) instead of raising. |
| 3 | P3 | `invoice_report.py:13-18`, `:24` | Amounts are summed as binary floats and rounded with `round()`. That rounding is round-half-even and works on the float representation, not on decimal cents. Example: amounts `0.01` and `0.02` give an average of `0.015`. `round(0.015, 2)` returns `0.01` (because 0.015 is stored as 0.01499…), not the `0.02` a finance reader would expect. Totals are fine at realistic sizes. Averages on half-cent boundaries can be off by a cent. *Evidence: code reading plus known float behaviour.* | `monthly_average([{"id":1,"date":"2026-03-01","amount":0.01},{"id":2,"date":"2026-03-02","amount":0.02}], 2026, 3) == 0.02`. Fix: load with `parse_float=Decimal` and use `quantize(Decimal("0.01"), ROUND_HALF_UP)`. |
| 4 | P3 | `invoice_report.py:8` | `open(path)` has no `encoding`, so it uses the locale's default encoding. JSON exports are UTF-8. On a Windows default code page (cp1252), a file with any non-ASCII text, such as an accented customer name in another field, either fails with `UnicodeDecodeError` or loads garbled text. | Write a UTF-8 file containing `"note": "Société"`. Under a non-UTF-8 locale (or with `locale.getpreferredencoding` patched), assert that it loads and that the text survives. Fix: `open(path, encoding="utf-8")`. |

**Notes on the author's claims (Step 5.3):**
- "Tests pass" is plausible. Both tests run against in-memory data, and their expected values (200.0 and 100.0) match the code. But the tests never call `load_invoices`, which is exactly where finding 1 sits.
- "Ran it against last month's export and it works" cannot be true of this code: line 9 raises before reading any data. Either a different version of the file was run, or the claim is mistaken. The owner should check which version was actually tested.
- Against the original request: the request says the module "reports" the total and average. The module provides functions but no entry point or report output. I am noting this, not raising it as a finding, because the request is ambiguous on this point.

**FILES NEEDED BUT NOT PROVIDED:** the PR metadata (number, head SHA, merge base) and the commit log with trailers.

**Close-out**

Under the skill's rules, a reviewer does not adjudicate its own findings. The author's decisions are still pending.

**ADJUDICATION:** pending author.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | — (P1, cannot be deferred) | — |
| 2 | — | — |
| 3 | — | — |
| 4 | — | — |

**VERIFIED AFTER FIXES:** none yet. Each fix should be checked by reading its diff and running the suggested test. No second full review is needed.

**MERGE RECOMMENDATION:** do not merge as it stands.
- Finding 1 (P1) is an open blocker: the file-loading path fails on every call.
- The target SHA is unrecorded, and no CI or check status was provided.
- Recommend "merge after fixes" once finding 1 is fixed with a test that calls `load_invoices` on a real file, and finding 2 is fixed or deferred to a linked issue.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "code reading against stdlib json.loads signature; not executed",
      "location": "invoice_report.py:9",
      "scenario": "json.loads(..., strict_mode=True) forwards the unknown kwarg to JSONDecoder, raising TypeError on every call; load_invoices never works. No test calls it, so the passing tests do not catch it.",
      "fix": "Replace with json.load(f) (strict=True is already the default); add a test that loads a temp file."
    },
    {
      "severity": "P2",
      "evidence_level": "code reading; certain",
      "location": "invoice_report.py:24",
      "scenario": "A month with no invoices makes len(in_month) == 0, so the function raises ZeroDivisionError, e.g. monthly_average(SAMPLE, 2026, 5).",
      "fix": "Return 0.0 or None (documented) when no invoices match; add a test for an empty month."
    },
    {
      "severity": "P3",
      "evidence_level": "code reading plus known float/round behaviour",
      "location": "invoice_report.py:13-18,24",
      "scenario": "Float summation with round-half-even: amounts 0.01 and 0.02 average 0.015, and round() gives 0.01 instead of the expected 0.02.",
      "fix": "Parse with parse_float=Decimal and quantize to 0.01 with ROUND_HALF_UP."
    },
    {
      "severity": "P3",
      "evidence_level": "code reading",
      "location": "invoice_report.py:8",
      "scenario": "open(path) uses the locale encoding; a UTF-8 export with non-ASCII text fails with UnicodeDecodeError or is garbled under cp1252.",
      "fix": "open(path, encoding=\"utf-8\")."
    }
  ]
}
```