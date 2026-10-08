# Redteam Review: `invoice_report.py`

**Review conditions:** I had no tools in this session, so I ran nothing. Every finding comes from reading the code against the documented stdlib behaviour. The work was not produced in this conversation, so anchoring risk is low. The lack of execution is the main limit on confidence.

**VERDICT: REWORK.** `load_invoices` raises on every call, so the module cannot do what was asked end to end. That also contradicts the author's claim that it "works" on last month's export. Money handling and the empty-month case need a small redesign as well.

**CONFIDENCE IN VERDICT: high.** The critical finding follows from `json.loads` forwarding unknown keyword arguments to `JSONDecoder.__init__`, which is well documented. A one-line run would settle it fully.

## Pass 1: Reconstruct

The module claims to load a JSON list of invoices and compute a month's total and average invoice amount, using only the standard library. For that to be correct, four things must hold:
- the loader must parse real files;
- dates must be strict `YYYY-MM-DD`;
- amounts must be JSON numbers;
- the month must contain at least one invoice.

There are also unstated assumptions: binary floats are acceptable for currency, the platform's default encoding can read the file, and "reports" means returning numbers rather than printing a report. The author's assurance rests on two tests that never touch `load_invoices`, plus an unevidenced manual run.

## Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED (by stdlib signature; not executed) | `load_invoices`: `json.loads(f.read(), strict_mode=True)` | `strict_mode` is not a parameter of `json.loads` or `JSONDecoder`. `json.loads` passes extra kwargs to `JSONDecoder(**kw)`, which rejects unknown names. The real flag is `strict`, and it already defaults to `True`. | Any call, on any file, raises `TypeError: JSONDecoder.__init__() got an unexpected keyword argument 'strict_mode'`. Nothing can be loaded, which means the "ran it against last month's export" claim cannot be accurate as written. | Use `json.load(f)` and drop the kwarg. Add a test that writes a temp JSON file and calls `load_invoices`. |
| 2 | High | CONFIRMED | `monthly_average`: `... / len(in_month)` | There is no guard for a month with no invoices. | Asking for a month with no invoices (a future month, a typo'd year, an empty export) raises `ZeroDivisionError` and crashes the report. | Return `None` or 0 (or raise a clear domain error) when `in_month` is empty, and choose and document one. Add a test for an empty month. |
| 3 | Medium | CONFIRMED | `monthly_total`: `total = 0.0`, `total += inv["amount"]`; `round(...)` | Currency is accumulated in binary floats, and `round` uses banker's rounding on inexact values. | Summing many cent values drifts, e.g. `0.1 + 0.2 = 0.30000000000000004`. Half-cent results round unpredictably (`round(2.675, 2) == 2.67`), so totals can be off by a cent against accounting systems. | Load with `json.load(f, parse_float=Decimal)`, sum `Decimal`s, and quantize with `ROUND_HALF_UP` (or whatever the business rule is). Add a test with amounts such as `0.1, 0.2` and a `.xx5` case. |
| 4 | Medium | CONFIRMED | `monthly_total` / `monthly_average`: `inv["date"]`, `inv["amount"]`, `date.fromisoformat` | There is no validation, and one bad record aborts the whole report. | All of these raise and kill the report: a record missing `amount` (`KeyError`), an amount stored as a string like `"120.50"` (`TypeError` on `+=`), or a date like `"2026-3-4"` or `""` (`ValueError`). On Python 3.11+, `fromisoformat` also accepts non-`YYYY-MM-DD` forms like `"20260304"`, so the format is not actually enforced. | Validate at load time with an explicit `strptime(s, "%Y-%m-%d")` and a type check on `amount`. Either reject the file with a message naming the invoice id, or skip and report bad rows. Add tests for each malformed case. |
| 5 | Medium | CONFIRMED | `test_invoice_report.py` | The tests cover only the happy path, and the sample amounts are chosen so they are exactly representable in float. | The loader bug (#1), division by zero (#2), float drift (#3) and malformed input (#4) all pass CI undetected. "Tests pass" says nothing about the requested load-and-report flow. | Add tests for: loading from a file, an empty month, a month with a single invoice, float-hostile amounts, malformed records, and the December/January boundaries. |
| 6 | Low | CONFIRMED | `monthly_average`: `round(monthly_total(...) / len(...), 2)` | The average is computed from an already-rounded total, so it is rounded twice. The month filter is also duplicated and dates are parsed up to three times per invoice. | The double rounding can shift the average by 0.01 in edge cases. The duplicated filter logic can drift if one copy is edited and the other is not. | Factor out an `_in_month(invoices, year, month)` helper. Compute the average from the unrounded sum and count, and round once. |
| 7 | Low | PROBABLE | `load_invoices`: `open(path)` | No encoding is specified, so the locale default is used. JSON is UTF-8. | On Windows (cp1252), or in a container with a C/POSIX locale, an export containing non-ASCII text (customer names, `€`) raises `UnicodeDecodeError` or misreads the content. | Use `open(path, encoding="utf-8")`. |
| 8 | Low | PROBABLE | Module as a whole | The request says "reports the total and the average", but there is no entry point or function that produces the report. | A user expecting `python invoice_report.py invoices.json 2026 3` gets nothing. Whether that matters depends on what "report" meant in the request. | Either add a `report(path, year, month)` function and a `__main__` block, or confirm with the requester that library functions are enough. |

## What Holds Up

- Standard library only, as required.
- The month filter correctly matches on both year and month, so the same month in a different year is not counted.
- `fromisoformat` is a reasonable parser for well-formed `YYYY-MM-DD` dates.
- The two existing tests are arithmetically correct for their data: 120.5 + 79.5 = 200.0, average 100.0.
- At the expected scale, performance is not a concern.

## Unverified Claims

- **"Tests pass."** This is plausible for the two in-memory tests. Confirm by running `python -m unittest`. It does not cover loading.
- **"Ran it against last month's export and it works."** This is contradicted by finding #1. Confirm by running `python -c "import invoice_report as r; print(r.load_invoices('export.json')[:1])"` on the current file. If it succeeded, the code that was run is not the code under review.

## Questions for the Author

1. What exact command did you run against last month's export, and on which revision of the file?
2. What should the average be for a month with no invoices: `None`, 0, or an error?
3. Are amounts always JSON numbers in the export, and is cent-exact rounding required?

## Decision-Maker Summary

Do not use this as is: the loader fails on every call, and the claim that it was verified against real data does not match the code. Fixing #1 and #2 is a few lines, but #3 (float money) and missing tests for the load path should be done before anyone relies on the figures. If it ships with only #1 fixed, expect crashes on empty months and occasional one-cent discrepancies.

```json
{
  "verdict": "REWORK",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "invoice_report.py load_invoices: json.loads(f.read(), strict_mode=True)",
      "scenario": "json.loads forwards unknown kwargs to JSONDecoder, which has no 'strict_mode' parameter; every call raises TypeError, so no file can be loaded and the claim of running it on last month's export cannot hold for this code.",
      "fix": "Use json.load(f) (the 'strict' flag already defaults to True); add a test that loads a temp JSON file via load_invoices."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "invoice_report.py monthly_average: / len(in_month)",
      "scenario": "A month with no invoices raises ZeroDivisionError.",
      "fix": "Handle the empty month explicitly (return None/0 or raise a clear error) and add an empty-month test."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "invoice_report.py monthly_total: total = 0.0; total += inv['amount']; round(total, 2)",
      "scenario": "Float accumulation and banker's rounding on inexact values make totals drift by cents (e.g. 0.1+0.2, round(2.675,2)==2.67).",
      "fix": "Parse with parse_float=Decimal, sum Decimals, and quantize with an explicit rounding mode; test with float-hostile amounts."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "invoice_report.py monthly_total/monthly_average: inv['date'], inv['amount'], date.fromisoformat",
      "scenario": "A missing key, a string amount, or a malformed date raises KeyError/TypeError/ValueError and aborts the whole report; on Python 3.11+ fromisoformat also accepts non-YYYY-MM-DD forms.",
      "fix": "Validate records at load time with strptime('%Y-%m-%d') and an amount type check; report or reject bad rows; add a test for each malformed case."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "test_invoice_report.py",
      "scenario": "Only happy-path in-memory tests with float-exact values; the loader bug, empty month, rounding and malformed input all pass undetected.",
      "fix": "Add tests for loading from a file, an empty month, a single invoice, float-hostile amounts, malformed records, and year boundaries."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "invoice_report.py monthly_average: round(monthly_total(...)/len(...), 2)",
      "scenario": "The average is computed from an already-rounded total (double rounding, possible 0.01 shift); the month filter is duplicated and can drift.",
      "fix": "Factor out a shared month filter; compute the average from the unrounded sum and count and round once."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "invoice_report.py load_invoices: open(path)",
      "scenario": "Without an encoding the locale default is used; on cp1252 or C locale, a UTF-8 export with non-ASCII text raises UnicodeDecodeError.",
      "fix": "open(path, encoding='utf-8')."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "invoice_report.py (module as a whole)",
      "scenario": "The request asks for something that 'reports' the total and average, but there is no report function or CLI entry point.",
      "fix": "Add report(path, year, month) and a __main__ block, or confirm with the requester that library functions are enough."
    }
  ]
}
```