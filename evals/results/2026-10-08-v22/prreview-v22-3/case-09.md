# Review report

**REVIEWED:** No PR number, head SHA or merge base was provided; the code was supplied inline (`invoice_report.py`, `test_invoice_report.py`). **This review covers only the text shown above.** It is not tied to a commit. Any commit posted later must be checked against this text. I had no tools, so I executed nothing. Every finding comes from reading the code against the stdlib behaviour I know.

**TIER:** Standard. This is ordinary application code: a read-only report over invoice data. It does not move money, touch auth, secrets or network exposure, or carry personal-data fields beyond id, date and amount.

**REVIEWERS:**
- Reviewer: this session, Claude Opus 5.5 (`claude-opus-5-5`). It did not write the change.
- Author: unknown. No commit trailers were provided.
- Data: no code was sent outside this session.

**Author's claims:** "Tests pass" is plausible, but the tests never call `load_invoices`. "Ran it against last month's export" cannot be true of this code, because `load_invoices` raises on every call (finding 1). Either a different version was run, or the run never went through `load_invoices`. The author should confirm which code was actually exercised.

FINDINGS:

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `invoice_report.py:9` | `json.loads(..., strict_mode=True)` passes `strict_mode` through to `JSONDecoder(**kw)`. `JSONDecoder` has no such parameter; the real one is `strict`. So every call to `load_invoices`, with any file, raises `TypeError: ... unexpected keyword argument 'strict_mode'`. The module cannot load invoices at all, which is half the original request. No test calls this function, so the suite stays green. | Write a temp file containing `[{"id":1,"date":"2026-03-04","amount":120.5}]`, then assert `load_invoices(path)` returns that list. This fails today with `TypeError`. Fix: drop the argument, or use `json.load(f)`. Also add an end-to-end test: `monthly_total(load_invoices(path), 2026, 3)`. |
| 2 | P2 | `invoice_report.py:24` | Any month with no invoices makes `len(in_month)` zero, and `monthly_average` raises `ZeroDivisionError`. This happens for a quiet month, an empty export, a future month, or a typo such as `month=13`. A caller asking "what was the average for March?" gets a crash instead of an answer. Workaround: callers check the total or count first. | `assertIsNone(r.monthly_average(SAMPLE, 2026, 5))` (or whatever empty-month contract is chosen, e.g. `0.0` or a documented `ValueError`). This fails today with `ZeroDivisionError`. |
| 3 | P3 | `invoice_report.py:13-18`, `:24` | Amounts are summed as binary floats and rounded with `round()`, which rounds half-to-even on the binary value. `round(1.005, 2)` is `1.0`, not `1.01`. The average is also rounded twice: the total is rounded to cents, then divided, then rounded again. Any cent-level discrepancy against an accounting system that rounds half-up, or that computes the average from unrounded data, shows up as a reconciliation difference. | Use `SAMPLE = [{"id":1,"date":"2026-03-01","amount":1.005}]` and assert the total is `Decimal("1.01")`, after switching to `json.load(f, parse_float=Decimal)` and `Decimal.quantize(Decimal("0.01"), ROUND_HALF_UP)`. This fails today because the result is `1.0`. |
| 4 | P3 | `invoice_report.py:8` | `open(path)` has no `encoding`, so it uses the locale default. On a Windows host using cp1252, a UTF-8 export with non-ASCII characters in any field can raise `UnicodeDecodeError` or decode to garbage. JSON is UTF-8 by spec. | Write a temp file as UTF-8 containing `"note": "café"`, then call `load_invoices` with the locale forced to a non-UTF-8 encoding. Fix: `open(path, encoding="utf-8")`. |

**FILES NEEDED BUT NOT PROVIDED:**
- The commit or PR with head and merge-base SHAs.
- The CI configuration and check results.
- A sample of "last month's export". I need it to check the real `amount` type (number or string) and the date format. If amounts are strings, line 17 raises `TypeError`, but I have not raised that as a finding without evidence.

# Close-out

Not written yet. The author adjudicates the findings above, and a reviewer does not adjudicate its own findings.

**ADJUDICATION:** pending, for all four findings.

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION (reviewer's view, pending close-out): do not merge.**
- Finding 1 is P1: the loader cannot run, so the module does not meet the request.
- Finding 2 still needs a fix or a deferral.
- No commit SHA or CI checks were provided. A missing check is not green.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "static read against stdlib json API; not executed",
      "location": "invoice_report.py:9",
      "scenario": "json.loads(..., strict_mode=True) forwards strict_mode to JSONDecoder, which has no such parameter (it is 'strict'); every load_invoices call raises TypeError, so no file can be loaded. Untested, so the suite stays green; contradicts the author's claim of a successful run on last month's export.",
      "fix": "Use json.load(f) (or strict=True if intended) and add a test that loads a temp file and feeds it to monthly_total."
    },
    {
      "severity": "P2",
      "evidence_level": "static read; division by len(in_month) with no guard",
      "location": "invoice_report.py:24",
      "scenario": "A month with no invoices (empty export, future month, month=13) makes len(in_month) == 0 and monthly_average raises ZeroDivisionError.",
      "fix": "Guard the empty case with a documented contract (return None/0.0 or raise ValueError) and test it."
    },
    {
      "severity": "P3",
      "evidence_level": "static read; known float/round() behaviour (round(1.005, 2) == 1.0)",
      "location": "invoice_report.py:13-18, invoice_report.py:24",
      "scenario": "Money summed as binary floats and rounded half-to-even; the average is double-rounded (total rounded, then divided, then rounded again). Cent-level mismatches against half-up accounting figures.",
      "fix": "Parse amounts with parse_float=Decimal, sum as Decimal, quantize once to 0.01 with ROUND_HALF_UP; compute the average from the unrounded sum."
    },
    {
      "severity": "P3",
      "evidence_level": "static read; open() uses locale encoding when none is given",
      "location": "invoice_report.py:8",
      "scenario": "On a non-UTF-8 locale (e.g. Windows cp1252), a UTF-8 JSON export with non-ASCII text raises UnicodeDecodeError or mis-decodes.",
      "fix": "open(path, encoding=\"utf-8\")."
    }
  ]
}
```