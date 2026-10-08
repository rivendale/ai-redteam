# pr-review: invoice_report.py

**Review report**

**REVIEWED:** No PR number, head SHA or merge base was provided, and I have no tools to check out a commit. This review covers the two files exactly as pasted (`invoice_report.py`, `test_invoice_report.py`) and nothing else. Whoever closes this out must record the head SHA these files correspond to. A different head is not reviewed.

**TIER:** Standard. This is ordinary application code. It reports on invoice amounts but does not move money, and it touches no auth, secrets, network exposure or personal-data handling. That matches the stated stakes.

**REVIEWERS:**
- Reviewer: a separate Claude instance (claude-opus-5-5) with no part in writing the change. Nothing was sent to any other endpoint or subagent.
- Author: unknown. No commit trailers were provided.

**Claims checked against the code:**
- **"Tests pass."** Plausible. Both tests exercise `monthly_total` and `monthly_average` on in-memory data, and both expected values work out by hand. I could not run them.
- **"Ran it against last month's export and it works."** The code shown contradicts this. Finding 1 shows `load_invoices` raises on every call, and no test calls it. Either a different version was run or the claim is wrong.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `invoice_report.py:9` | `json.loads(f.read(), strict_mode=True)`: `json.loads` forwards unknown keyword arguments to `JSONDecoder(**kw)`. `JSONDecoder.__init__` has no `strict_mode` parameter (the real one is `strict`, already `True` by default). So every call to `load_invoices`, on any file, raises `TypeError: ... unexpected keyword argument 'strict_mode'`. The module cannot load invoices at all. | Write a temp file with `json.dump(SAMPLE, f)`, then `assertEqual(r.load_invoices(path), SAMPLE)`. This raises `TypeError` today and passes once the argument is removed. |
| 2 | P1 | `invoice_report.py:24` | `monthly_average` for a month with no invoices (e.g. 2026-05 with `SAMPLE`, or a month that has not happened yet) gives `len(in_month) == 0`, so the function raises `ZeroDivisionError`. An empty month is an ordinary input for a monthly report, and the behaviour is undefined in the code and docstring. | `r.monthly_average(SAMPLE, 2026, 5)` should return a defined value (`0.0` or `None`, whichever the owner decides) instead of raising. |
| 3 | P2 | `invoice_report.py:13-18, 24` | Money is handled as binary floats, rounded with Python's `round` (round-half-even on inexact values), and the average is computed from an already-rounded total (double rounding). Example: amounts `1.00` and `1.01` in March give a total of `2.01` and an average of `1.005`. `round(1.005, 2)` returns `1.0`, because `1.005` is stored as `1.00499…`. A half-up accounting convention gives `1.01`. Reported cents can be wrong. | Two March invoices of `1.00` and `1.01` should give `monthly_average == 1.01` (or `Decimal("1.01")`). This returns `1.0` today. Fix: `json.loads(..., parse_float=Decimal)`, sum as `Decimal`, and `quantize(Decimal("0.01"), ROUND_HALF_UP)` once, on the final value. |
| 4 | P3 | `invoice_report.py:8` | `open(path)` has no `encoding`. On a platform whose locale encoding is not UTF-8 (e.g. Windows cp1252), an export containing non-ASCII text, such as a customer name in an extra field, either fails with `UnicodeDecodeError` or is silently mis-decoded. JSON files are UTF-8 by specification (RFC 8259). | Write a UTF-8 file containing `"customer": "Müller"`. With the locale forced to a non-UTF-8 encoding, `load_invoices` should return the correct string. Fix: `open(path, encoding="utf-8")`. |
| 5 | P3 | `invoice_report.py:15, 23` | Every invoice's date is parsed regardless of the month requested. One malformed or missing `date` in any month (e.g. `"2026-02-30"` in February) makes the March report fail with `ValueError` or `KeyError`. Whether to fail loudly or skip bad records is an owner decision. Right now it is implicit and untested. | A list containing one invalid-date record in February: assert the documented behaviour for `monthly_total(..., 2026, 3)`, either a clear error naming the bad record or `200.0`. |

**FILES NEEDED BUT NOT PROVIDED:**
- A sample of "last month's export". I need it to confirm the real `amount` type (number or string) and `date` format.
- The PR, head SHA and CI configuration.

---

**Close-out**

Not written. A reviewer does not adjudicate its own findings. The author must answer each of findings 1–5 as Accepted (fix commit plus regression test, with the fix diff read), Deferred (P2/P3 only, with an issue link) or Rejected (with evidence).

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1–5 | pending | none |

**VERIFIED AFTER FIXES:** None yet.

**MERGE RECOMMENDATION (current state): do not merge.**
- Two P1 findings are open, and P1s cannot be deferred. Finding 1 means the module's entry point cannot work.
- No head SHA is recorded, and CI status is unknown. A missing check is not green.
- One owner decision is pending: the behaviour for empty months and malformed records.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "code-read; stdlib json.loads forwards unknown kwargs to JSONDecoder, which has no strict_mode parameter (not executed, no tools)",
      "location": "invoice_report.py:9",
      "scenario": "Any call to load_invoices raises TypeError: unexpected keyword argument 'strict_mode'; the module cannot load any file. Contradicts the author's claim of a successful run; no test calls load_invoices.",
      "fix": "Use json.load(f) (strict=True is already the default); add a test that round-trips SAMPLE through a temp file."
    },
    {
      "severity": "P1",
      "evidence_level": "code-read",
      "location": "invoice_report.py:24",
      "scenario": "monthly_average for a month with no invoices divides by len(in_month) == 0 and raises ZeroDivisionError.",
      "fix": "Return a defined value (0.0 or None, owner's choice) when no invoices fall in the month; add a test for an empty month."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read; known float behaviour (round(1.005, 2) == 1.0)",
      "location": "invoice_report.py:13-18,24",
      "scenario": "Float money with round-half-even and double rounding: invoices 1.00 and 1.01 give an average of 1.0 instead of 1.01; reported cents can be wrong.",
      "fix": "Parse with parse_float=Decimal, sum Decimals, quantize once to 0.01 with ROUND_HALF_UP; add the 1.00/1.01 test."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "invoice_report.py:8",
      "scenario": "open() without encoding uses the locale encoding; on a non-UTF-8 locale, non-ASCII content in the export fails to decode or is mis-decoded.",
      "fix": "open(path, encoding=\"utf-8\")."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "invoice_report.py:15,23",
      "scenario": "One malformed or missing date in any month (e.g. 2026-02-30) makes the report for every other month fail with ValueError or KeyError.",
      "fix": "Decide and document the behaviour (a clear error naming the record, or skip); add a test with one bad record outside the requested month."
    }
  ]
}
```