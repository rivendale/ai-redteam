# Redteam Review: `invoice_report.py`

**Review setup:** I did not author this work, so there is no shared-context anchoring. However, I have no tools in this session and executed nothing. Findings marked CONFIRMED come from tracing the code against documented standard-library behavior, not from running it.

**VERDICT: REWORK.** The file-loading function crashes on every call, so the module cannot do what was asked. The author's claim that it worked on last month's export cannot be true for this code. The fixes are small, but the verification has to be redone.

**CONFIDENCE IN VERDICT:** High. The deciding finding comes from the `json.loads` signature, which is stable across all Python 3 versions. It is limited only by not being able to run the code here.

## Pass 1: Reconstruct

The module claims to:
- load a JSON list of invoices,
- filter them by year and month,
- return the month's total and average amount, rounded to 2 decimals.

For it to be correct, all of the following must hold:
1. `load_invoices` actually parses the file.
2. Every record has a valid `"date"` in `YYYY-MM-DD` form and a numeric `"amount"`.
3. The requested month contains at least one invoice, or the average is undefined.
4. Float arithmetic is acceptable for money.
5. The export has no duplicate invoices.
6. The file's encoding matches the platform default.

The tests check only assumptions 2 and 4, and only on clean in-memory data.

## Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED (traced against the stdlib signature; not executed) | `invoice_report.py`, `load_invoices`: `json.loads(f.read(), strict_mode=True)` | `json.loads` has no `strict_mode` parameter. Extra keyword arguments are passed on to `JSONDecoder.__init__`, which only accepts `object_hook`, `parse_float`, `parse_int`, `parse_constant`, `strict`, `object_pairs_hook`. | Any call, with any file, raises `TypeError: ... unexpected keyword argument 'strict_mode'`. The module cannot load data at all. | Use `json.load(f)`. Pass `strict=` only if control characters inside strings really need handling. Add a test that writes a temp JSON file and calls `load_invoices`. |
| 2 | High | CONFIRMED (contradiction between code and claim) | context.md: "I also ran it against last month's export and it works" | No Python 3 version can run `load_invoices` as written (finding 1). Either the claim is false, or a different version of the code was run. | Someone relies on the "verified against real data" claim and ships code that fails on first use. Any other "it works" statements from the same session are also suspect. | Re-run end-to-end on the real export using the exact committed file. Record the command and its output. |
| 3 | High | CONFIRMED (traced) | `monthly_average`: `/ len(in_month)` | No guard for a month with no invoices. | `monthly_average(SAMPLE, 2026, 5)` raises `ZeroDivisionError`. A report run for a quiet month, a future month, or a typo month (for example `month=13`) crashes. | Return `None` or `0.0` when `in_month` is empty, or raise a clear `ValueError`, and document the choice. Add a test for an empty month. |
| 4 | High | CONFIRMED (test file vs. context) | `test_invoice_report.py` | No test touches `load_invoices`, empty months, or bad records. The tests passing is what hid findings 1 and 3. | "Tests pass" is reported as evidence of correctness, while the entry point is broken. | Add tests for: a round-trip through a temp file, an empty month, a missing `date`/`amount` key, and a malformed date. |
| 5 | Medium | CONFIRMED (documented float/`round` behavior) | `monthly_total`: `total = 0.0`, `total += inv["amount"]`, `round(total, 2)`; same in `monthly_average` | Money is summed as binary floats, then rounded with `round()`. That rounds half-to-even on an inexact binary value. | `round(2.675, 2)` returns `2.67`. An average that lands on a half-cent can round the "wrong" way. Over many invoices the float sum drifts before rounding, which can cause cent-level mismatches against accounting systems. | Use `json.load(f, parse_float=Decimal)`, sum `Decimal`s, and quantize with `ROUND_HALF_UP`, if cent-exactness matters. Otherwise document that results are approximate. |
| 6 | Medium | CONFIRMED (traced) | `monthly_total` / `monthly_average`: `inv["date"]`, `inv["amount"]`, `date.fromisoformat(...)` | There is no per-record validation, so one bad record aborts the whole report. | A record with no `date` raises `KeyError`. A record like `"2026-3-4"` or `""` raises `ValueError`. A `null` amount raises `TypeError`. An amount stored as `"120.50"` (a string) raises `TypeError` when added to a float. Any one of these stops the entire report. | Decide on a policy: either skip and count bad rows, or fail with the record's `id` in the error message. Validate types in `load_invoices`. |
| 7 | Low | PROBABLE | `load_invoices`: `open(path)` with no `encoding=` | Uses the locale's default encoding. | On Windows (cp1252), a UTF-8 export with non-ASCII customer names mis-decodes or raises. A UTF-8 file that starts with a BOM makes `json.loads` raise "Unexpected UTF-8 BOM". | Use `open(path, encoding="utf-8")`, or `"utf-8-sig"` if the exporter writes a BOM. |
| 8 | Low | UNVERIFIED | Both aggregation functions | Duplicate invoice `id`s are counted twice. | An export that repeats a row, for example from a re-run or pagination overlap, inflates both the total and the count. | Ask whether the export guarantees unique ids. If not, deduplicate by `id`, or detect duplicates and warn. |
| 9 | Low | CONFIRMED | `monthly_average` | Dates are parsed twice per record in the list comprehension, and a third time inside `monthly_total`. The month filter logic is duplicated, so the two functions can drift apart. | If someone later edits the filter in one function only, the average's numerator and denominator stop matching. | Extract a single `_in_month(invoices, year, month)` helper and compute both the sum and the count from its result. |

## What Holds Up

- The filtering logic on well-formed data is correct. It compares `year` and `month` on a parsed `date`, which avoids string-prefix bugs such as `"2026-1"` matching `"2026-10"`.
- `date.fromisoformat` is a real API and accepts `YYYY-MM-DD`.
- The two existing tests assert genuine values: 120.5 + 79.5 = 200.0, and 200.0 / 2 = 100.0. Both are exact in floating point, so they are not tautological.
- Only the standard library is used, as the request required.

## Unverified Claims

- **"Tests pass."** This is plausible for the two existing tests, since neither calls `load_invoices`. Confirm by running `python -m unittest` and capturing the output.
- **"Ran against last month's export and it works."** This contradicts finding 1. Confirm by running the committed file against the export and showing the output and the Python version.
- **That amounts in the real export are JSON numbers rather than strings, and that dates are always `YYYY-MM-DD`.** Confirm by inspecting a sample of the export.

## Questions for the Author

1. What exact code and command did you run against last month's export? Was it this file?
2. What should the average be for a month with no invoices: `None`, `0`, or an error?
3. Do the results need to reconcile to the cent with an accounting system? This decides whether finding 5 is required.

## Decision-Maker Summary

Do not use this as-is: `load_invoices` crashes on every call, and the claim that it was tested on real data cannot be accurate. Fix the `json.loads` call, guard the empty-month division, add tests that actually load a file, and then re-run against the real export. If you proceed after only those fixes, the remaining risks are cent-level rounding differences and a whole-report crash on any malformed record.

```json
{
  "verdict": "REWORK",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "invoice_report.py load_invoices: json.loads(f.read(), strict_mode=True)",
      "scenario": "json.loads forwards unknown kwargs to JSONDecoder, which has no 'strict_mode' parameter; every call raises TypeError, so no file can ever be loaded.",
      "fix": "Use json.load(f) (optionally strict=...); add a test that writes a temp JSON file and calls load_invoices."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "context.md author claim: 'ran it against last month's export and it works'",
      "scenario": "The committed load_invoices cannot run on any Python 3, so the claim is false or refers to different code; consumers rely on a verification that did not happen.",
      "fix": "Re-run end-to-end on the real export with the committed file and record the command, Python version, and output."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "invoice_report.py monthly_average: / len(in_month)",
      "scenario": "A month with no invoices (e.g. monthly_average(SAMPLE, 2026, 5) or month=13) raises ZeroDivisionError.",
      "fix": "Guard the empty case (return None/0.0 or raise a clear ValueError) and add an empty-month test."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "test_invoice_report.py",
      "scenario": "Tests exercise only in-memory happy paths; load_invoices, empty months, and bad records are untested, which hid the Critical and High bugs while 'tests pass' was reported.",
      "fix": "Add tests: temp-file round trip through load_invoices, empty month, missing keys, malformed date."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "invoice_report.py monthly_total/monthly_average: float accumulation and round(x, 2)",
      "scenario": "Binary float sums plus round()'s half-to-even on inexact values (round(2.675, 2) == 2.67) give cent-level mismatches against accounting figures.",
      "fix": "Parse with parse_float=Decimal, sum Decimals, quantize with ROUND_HALF_UP; or document results as approximate."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "invoice_report.py inv['date'], inv['amount'], date.fromisoformat",
      "scenario": "One record with a missing key, a malformed date, a null amount, or a string amount raises KeyError/ValueError/TypeError and aborts the entire report.",
      "fix": "Validate records in load_invoices; either skip and count bad rows or fail with the offending invoice id."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "invoice_report.py load_invoices: open(path) without encoding",
      "scenario": "On a non-UTF-8 locale (e.g. Windows cp1252) non-ASCII content mis-decodes or raises; a UTF-8 BOM makes json.loads raise.",
      "fix": "open(path, encoding='utf-8') or 'utf-8-sig'."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "monthly_total / monthly_average",
      "scenario": "Duplicate invoice ids in the export (re-run or pagination overlap) are double-counted, inflating total and count.",
      "fix": "Confirm export guarantees unique ids; otherwise dedupe by id or warn on duplicates."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "invoice_report.py monthly_average list comprehension",
      "scenario": "Month filter logic is duplicated across functions (dates parsed up to three times); a future edit to one copy desynchronizes numerator and denominator.",
      "fix": "Extract a single _in_month helper and compute sum and count from its result."
    }
  ]
}
```