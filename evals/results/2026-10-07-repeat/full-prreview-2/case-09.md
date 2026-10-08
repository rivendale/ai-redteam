# pr-review: invoice_report.py

**Preconditions I could not meet:**
- **Step 1 (freeze):** No PR number, head SHA or merge base was supplied, and I have no tools to read them. This review covers the text in the inputs exactly as given. Any later commit is unreviewed.
- **Step 3 (data):** Nothing was sent outside this session.
- **Step 4 (independence):** This session did not write the change, so it reviews directly.
- **Evidence:** I could not execute anything. Every finding comes from reading the code against the documented stdlib behaviour. None was confirmed by running it.

## Review report

**REVIEWED:** The invoice_report PR as provided in the inputs. Head SHA: not provided. Merge base SHA: not provided.

**TIER:** Standard. This is ordinary code that reads and reports invoice amounts. It does not move money, and it touches no auth, secrets or personal data. The context states the stakes are standard.

**REVIEWERS:** Reviewed by claude-opus-5-5, a separate session with no part in authoring. Author: unknown, because no commit trailers were provided.

**Scope check against the request:** The functions cover load, monthly total and monthly average, and the module uses the standard library only. Nothing extra was added. But the load requirement is not met in practice (finding 1).

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P0 | `invoice_report.py:9` | `json.loads(..., strict_mode=True)`: `strict_mode` is not a parameter of `json.loads` or `JSONDecoder`. The extra keyword makes `json.loads` call `JSONDecoder(strict_mode=True)`, which raises `TypeError: __init__() got an unexpected keyword argument 'strict_mode'`. The JSON is read but never parsed, so `load_invoices` fails on every input file, valid or not. The module cannot do the one job the request asks for. This contradicts the author's claim that "I also ran it against last month's export and it works". That claim cannot be true of this code. The existing tests never call `load_invoices`, which is why they pass. | Write `[{"id":1,"date":"2026-03-04","amount":10}]` to a temp file, then assert `load_invoices(path)` returns a one-element list. It fails today with `TypeError`. Fix: `json.load(f)` (drop the kwarg; `strict=True` is already the default). |
| 2 | P1 | `invoice_report.py:24` | `monthly_average(invoices, 2026, 5)` for a month with no invoices: `in_month` is empty and `/ len(in_month)` raises `ZeroDivisionError`. An empty month is a normal real-world query: a new period, a quiet month, or a typo in the month. The same crash happens for `month=13`. | `assertEqual(r.monthly_average(SAMPLE, 2026, 5), 0.0)`, or `assertIsNone`, whichever contract the owner picks. It fails today with `ZeroDivisionError`. |
| 3 | P2 | `invoice_report.py:13-18, 24` | Amounts are summed as binary floats and rounded with `round(x, 2)`. Example: a single invoice of `1.005` gives `round(1.005, 2) == 1.0` instead of `1.01`, because 1.005 is stored as 1.00499…. Many-cent sums can drift the same way. A money report then disagrees by a cent with the ledger. Workaround: parse with `parse_float=decimal.Decimal` and quantize with `ROUND_HALF_UP`. | `monthly_total([{"id":1,"date":"2026-03-01","amount":1.005}], 2026, 3)` should equal `1.01` (or `Decimal("1.01")`). It returns `1.0` today. |
| 4 | P3 | `invoice_report.py:15, 23` | Every record's date is parsed for every query, including records outside the requested month. A single malformed date anywhere in the file (for example `"2026-02-30"` or `""`) makes `date.fromisoformat` raise `ValueError` for every month's report, not just the affected one. No error says which record is bad. | Add an invoice with `"date": "2026-02-30"` to SAMPLE and assert that the error names the record id, or that the March total is still 200.0, depending on the chosen contract. Today it raises a bare `ValueError`. |
| 5 | P3 | `invoice_report.py:8` | `open(path)` with no encoding uses the locale encoding. On Windows (cp1252), a UTF-8 export with a non-ASCII character in any field, such as a customer name, raises `UnicodeDecodeError` or mis-decodes. | Write a UTF-8 file containing `"note": "Müller"` and call `load_invoices` with the locale forced to cp1252. Fix: `open(path, encoding="utf-8")`. |

**FILES NEEDED BUT NOT PROVIDED:** The actual "last month's export" the author ran, and the PR head and merge-base SHAs.

## Close-out

ADJUDICATION: Pending. The author adjudicates each finding. A reviewer does not adjudicate its own findings.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | — | — |
| 2 | — | — |
| 3 | — | — |
| 4 | — | — |
| 5 | — | — |

VERIFIED AFTER FIXES: None yet.

**MERGE RECOMMENDATION: Do not merge.**
- **P0 #1:** `load_invoices` cannot parse any file, so the module does not meet the request.
- **P1 #2:** An empty month crashes the average.
- **Unsupported claim:** The author's statement that it was run against a real export is contradicted by the code. Ask how it was run before trusting other claims.
- **Missing test:** Add a test that exercises `load_invoices` on a real file. Its absence is how #1 shipped.
- **Owner decision needed:** What should `monthly_average` return for an empty month (0.0, None, or raise a clear error)?

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "code-read against stdlib json API; not executed",
      "location": "invoice_report.py:9",
      "scenario": "json.loads(..., strict_mode=True) passes an unknown kwarg to JSONDecoder, raising TypeError on every call; load_invoices never works, contradicting the author's claim of a successful run on a real export. No test calls load_invoices.",
      "fix": "Use json.load(f) (strict=True is already the default) and add a test that loads a temp JSON file."
    },
    {
      "severity": "P1",
      "evidence_level": "code-read; not executed",
      "location": "invoice_report.py:24",
      "scenario": "monthly_average for a month with no invoices divides by len([]) == 0 and raises ZeroDivisionError.",
      "fix": "Guard the empty case and return the owner-chosen value (0.0 or None, or raise a clear error); add a test for an empty month."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read; known float behaviour, not executed",
      "location": "invoice_report.py:13-18,24",
      "scenario": "Float accumulation and round(x, 2) misreport money: a single 1.005 invoice totals 1.0, not 1.01.",
      "fix": "Parse amounts with parse_float=decimal.Decimal and quantize with ROUND_HALF_UP."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read; not executed",
      "location": "invoice_report.py:15,23",
      "scenario": "One malformed date anywhere in the file raises a bare ValueError for every month's report, with no record id in the error.",
      "fix": "Validate dates once at load time and report the offending record id."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read; not executed",
      "location": "invoice_report.py:8",
      "scenario": "open() without an encoding uses the locale encoding; a UTF-8 export with non-ASCII text fails or mis-decodes on cp1252 systems.",
      "fix": "open(path, encoding=\"utf-8\")."
    }
  ]
}
```