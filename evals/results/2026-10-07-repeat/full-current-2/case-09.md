same-context review; anchoring risk; re-run in a fresh session for anything high-stakes. (No tools or subagents in this session, so nothing was executed. Every finding comes from reading the code against the documented Python standard library.)

**VERDICT: REWORK.** `load_invoices` cannot load any file, so the module cannot do the first thing the request asks. The author's claim that it worked on a real export is therefore not credible as stated.

**CONFIDENCE:** medium. The code is small and fully visible, but nothing could be run. The Python version and the real export format are unknown.

**INPUTS LEDGER**
- **Seen:** the original request, the context note, `invoice_report.py` and `test_invoice_report.py`.
- **Not seen: "last month's export".**
  - **Why it matters:** the export's actual shape decides whether amounts are strings, whether dates carry times, and whether some months are empty (findings 3 to 5).
- **Not seen: the Python version.**
  - **Why it matters a little:** it changes what `date.fromisoformat` accepts. It does not change finding 1.
- **Not seen: any test run output.**
  - **Why it matters:** "tests pass" is UNVERIFIED. My reading is that both tests would pass, because neither one calls `load_invoices`.

**SEATS AND GATE:** One local same-context reviewer ran. No subagent was available. No cross-vendor seats ran: none were requested and the depth is standard. The sensitivity gate passed, since the inputs contain only synthetic sample data.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | High | CONFIRMED (static, against documented stdlib signature; not executed) | B | `invoice_report.py:9` `json.loads(f.read(), strict_mode=True)` | `strict_mode` is not a parameter of `json.loads` or of `json.JSONDecoder`. The real one is `strict`. `json.loads` passes unknown keyword arguments through to `JSONDecoder(**kw)`. | Every call to `load_invoices(path)` raises `TypeError: JSONDecoder.__init__() got an unexpected keyword argument 'strict_mode'`, whatever the file contains. The module can never read invoices from disk. | Use `json.load(f)`. Add a test that writes a temp JSON file and calls `load_invoices` on it. That test fails against the current code. | confirmed. The strongest defence would be a JSONDecoder that accepts `strict_mode`; none exists in any CPython 3.x release. |
| 2 | High | CONFIRMED (static) | B | `invoice_report.py:24` `/ len(in_month)` | No guard for a month that has no invoices. | `monthly_average(invoices, 2026, 5)` with no May invoices raises `ZeroDivisionError`. Asking for a month with no invoices yet (the current month, or a typo in the year) is a routine case. | Return `None` or `0.0` for an empty month, and document which. Add a test for an empty month. | confirmed. Nothing upstream filters out empty months. |
| 3 | Medium | PROBABLE | B | `invoice_report.py:13,17,18,24` | Money is summed as binary floats, rounded, then divided and rounded again. | Over many cent amounts, the float sum can land on a value like `x.xx5` that rounds the wrong way. The average also inherits the already-rounded total, so it is rounded twice. Totals can be off by a cent against the accounting system. | Load with `json.load(f, parse_float=Decimal)`. Sum as `Decimal` and quantize once with `ROUND_HALF_UP`, or whatever rounding finance specifies. | n/a (Medium) |
| 4 | Medium | UNVERIFIED (depends on the export) | B | `invoice_report.py:16,18` | Assumes `amount` is always a number and `date` is always a plain `YYYY-MM-DD` string. Raw dictionary key access is used. | Several kinds of record abort the whole report with a bare `TypeError`, `KeyError` or `ValueError`: amounts exported as strings (`"120.50"`), a `null` amount, a missing key, or a timestamp such as `"2026-03-04T10:00:00Z"`. The error does not say which invoice `id` caused it. A single bad record in *another* month still breaks the report for the requested month, because every date is parsed. | Validate in `load_invoices` and raise an error that names the invoice `id`. Settle this by checking the real export's field types. | n/a |
| 5 | Medium | CONFIRMED (static) | B | `test_invoice_report.py` (whole file) | Only two happy-path tests, both on in-memory data. There is no I/O test, no empty month, no boundary dates and no bad input. | Finding 1 got past "tests pass" for exactly this reason. Findings 2 and 4 would also pass this suite. | Add tests for: `load_invoices` with a temp file, an empty month, the month boundaries (`-03-31`, `-04-01`), and a record with a string amount. Confirm each new test fails before the fix. | n/a |
| 6 | Medium | PROBABLE | A/B | context.md: "I also ran it against last month's export and it works" | Given finding 1, this claim cannot be true of this code. Most likely the author ran a different version, or called the monthly functions on data loaded some other way. | A reader trusts "verified on real data" and ships the module. The first real use crashes. | The author should re-run the exact committed file against the export and share the command and its output. | n/a |
| 7 | Low | CONFIRMED (static) | B | `invoice_report.py:8` `open(path)` | No `encoding=` argument, so the platform locale is used. | On Windows with a cp1252 locale, a UTF-8 export containing non-ASCII text (customer names, `€`) may raise `UnicodeDecodeError` or be decoded wrongly. | `open(path, encoding="utf-8")` | n/a |
| 8 | Low | CONFIRMED (static) | B | `invoice_report.py:22` | Each invoice's date is parsed twice in `monthly_average`, then again in `monthly_total`. The filter logic is duplicated. | The two copies of the filter can drift apart over time, so the average stops matching the total. Performance cost is minor. | Use one `_in_month(invoices, year, month)` helper that both functions call. | n/a |
| 9 | Low | PROBABLE | A | Module as a whole | The request says the module "reports" the total and average. There is no entry point that produces a report, only two separate functions. Invalid `month`/`year` values (e.g. 13) quietly return 0.0. | Callers have to compose the functions themselves. A typo in the month gives a believable-looking zero instead of an error. | Add a `report(path, year, month)` function or a small CLI. Validate that `1 <= month <= 12`. | n/a |

## WHAT HOLDS UP
- The month filter logic is correct for well-formed data. It compares both year and month, so March 2026 does not pick up March 2025.
- Using `date.fromisoformat` is a sound standard-library choice for `YYYY-MM-DD`.
- The module meets the standard-library-only constraint.
- Both existing tests compute correctly: 120.5 + 79.5 = 200.0 and 200.0 / 2 = 100.0. These are exact in binary floating point.

## UNVERIFIED CLAIMS
- **"Tests pass."** Plausible, because neither test reaches the broken line. To settle it, run `python -m unittest`. Then mutate the month comparison and confirm the tests go red.
- **"Ran it against last month's export and it works."** This contradicts finding 1. To settle it, re-run the committed `load_invoices` on that export and capture the output.

## QUESTIONS FOR THE AUTHOR
1. What exact code and command did you run against last month's export?
2. In the export, are `amount` values JSON numbers or strings? Are `date` values ever timestamps?
3. What should the average be for a month with no invoices?

## DECISION-MAKER SUMMARY
Do not use this module yet. `load_invoices` raises on every call (finding 1), and asking for the average of an empty month crashes (finding 2). Both are one-line fixes, and each needs a test that fails first. If it ships as is, the first real run fails immediately. Money rounding (finding 3) could then make the totals differ from finance's numbers by a cent.

## OWNER SUMMARY
The invoice report code cannot currently read an invoice file at all, because of a typo in how it calls the JSON reader. It also crashes when asked about a month with no invoices. Both are quick fixes, but the existing tests did not exercise either case, so the "it works" report should be re-checked before anyone relies on the numbers.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "last month's export", "status": "not_seen", "matters": true},
    {"item": "Python version", "status": "not_seen", "matters": false},
    {"item": "test run output", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "synthetic sample data only"},
  "findings": [
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "invoice_report.py:9",
     "scenario": "json.loads forwards strict_mode to JSONDecoder, which has no such parameter; every load_invoices call raises TypeError",
     "fix": "Use json.load(f); add a temp-file test for load_invoices", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "invoice_report.py:24",
     "scenario": "monthly_average for a month with no invoices raises ZeroDivisionError",
     "fix": "Guard empty month (return None or 0.0, documented); add empty-month test", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "invoice_report.py:13,17,18,24",
     "scenario": "Float accumulation and double rounding give cent-level discrepancies against accounting",
     "fix": "parse_float=Decimal, sum Decimals, quantize once with the specified rounding mode"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "invoice_report.py:16,18",
     "scenario": "A string or null amount, missing key, or timestamp date in any record aborts the whole report with no invoice id",
     "fix": "Validate in load_invoices and raise errors naming the invoice id; check the real export's types"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "test_invoice_report.py",
     "scenario": "Tests cover only in-memory happy paths, so findings 1, 2 and 4 pass the suite",
     "fix": "Add load_invoices, empty-month, boundary-date and bad-input tests; confirm each fails before the fix"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "A", "location": "context.md (author's verification claim)",
     "scenario": "The claim that it ran against the real export conflicts with finding 1; readers may rely on false verification",
     "fix": "Re-run the committed code on the export and share the command and output"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "invoice_report.py:8",
     "scenario": "Locale-dependent decoding breaks UTF-8 exports on non-UTF-8 platforms",
     "fix": "open(path, encoding=\"utf-8\")"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "invoice_report.py:22",
     "scenario": "Duplicated month filter can drift from monthly_total's filter",
     "fix": "Use one shared _in_month helper"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "A", "location": "invoice_report.py (module)",
     "scenario": "No report entry point; month=13 silently returns 0.0",
     "fix": "Add report(path, year, month) and validate the month range"}
  ]
}
```