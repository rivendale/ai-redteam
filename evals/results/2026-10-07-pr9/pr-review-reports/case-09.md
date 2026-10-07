# Review report

**REVIEWED:** No PR number, head SHA or merge base was supplied. I reviewed the three files as given: `invoice_report.py`, `test_invoice_report.py` and `__pycache__/invoice_report.cpython-312.pyc`. Whoever closes this must record the SHAs, because this review covers only the content shown here.

**TIER:** Standard. This is ordinary application code that reads invoice data and reports on it. It touches no auth, secrets, network, migrations, personal data or money movement. The context also sets the stakes as standard.

**REVIEWERS:** One independent instance (Opus 5.5). This session did not write the change. The author is unknown because no commit trailers were provided.

**Data handling (Step 3):** Only the code was reviewed. No invoice data was seen or sent anywhere.

**Execution:** I had no tools in this session. Nothing was run, and every finding comes from reading the code against the stdlib behaviour.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P1** | `invoice_report.py:9` | **`load_invoices` fails on every call, for any file.** `json.loads` has no `strict_mode` parameter. When unknown keywords are passed, `json.loads` hands them to the decoder as `JSONDecoder(**kw)`, which raises `TypeError: __init__() got an unexpected keyword argument 'strict_mode'`. This happens before any input is parsed. The module therefore cannot load an invoice file, which is half of the original request. This contradicts the author's claim: "I ran it against last month's export and it works." The committed `.pyc` also references `strict_mode`, so it does not show an earlier working version. The tests miss this because no test calls `load_invoices`. | Write `[{"id":1,"date":"2026-03-04","amount":120.5}]` to a temp file. Assert that `load_invoices(path)` returns a one-element list. Then assert `monthly_total(load_invoices(path), 2026, 3) == 120.5`. This test fails today with `TypeError`. |
| 2 | P2 | `invoice_report.py:24` | **The average crashes on a month with no invoices.** If `year, month` match no invoice (for example, a query for a month before any invoices exist), `in_month` is empty and `/ len(in_month)` raises `ZeroDivisionError`. A report over a quiet month crashes instead of returning a defined value, such as `0.0` or `None`, which should be documented. | `assertEqual(r.monthly_average(SAMPLE, 2026, 5), 0.0)`, or whatever value is agreed for an empty month. This test fails today with `ZeroDivisionError`. |
| 3 | P3 | `invoice_report.py:13-18`, `:24` | **Money is held as binary floats and rounded twice.** Amounts are summed as `float` and rounded with `round()`. Halfway values round inconsistently because of binary representation. For example, a single invoice of `2.675` gives a total of `2.67`, not `2.68`. The average divides the already rounded total, so it is rounded twice. With invoices of `0.10` and `0.15`, the true average is 0.125 and the result is `0.12`. Cent-level discrepancies against an accounting system are likely. | Use `[{"date":"2026-03-01","amount":2.675}]` and assert `monthly_total(...) == 2.68`. The fix is to parse with `parse_float=Decimal` and quantize with `ROUND_HALF_UP`. This test fails today. |
| 4 | P3 | `invoice_report.py:8` | **The file encoding depends on the platform.** `open(path)` has no `encoding`. On Windows the default is cp1252. A UTF-8 export with a non-ASCII byte in any field raises `UnicodeDecodeError` or produces mojibake. The bytes `0x81` and `0x8D` are undefined in cp1252. | Write a UTF-8 file containing `"id": "Ł-1"`, then call `load_invoices` with the locale forced to cp1252, for example `PYTHONUTF8=0` on Windows or a patch of `locale.getpreferredencoding`. This test fails today. The fix is `open(path, encoding="utf-8")` or `json.load(open(path, "rb"))`. |
| 5 | P3 | `__pycache__/invoice_report.cpython-312.pyc` | **A build artifact is committed.** The `.pyc` is generated output, and it embeds the author's absolute path, `/tmp/claude-1000/.../invoice_report.py`. It adds noise to the repo and leaks a local path. It can also confuse readers into treating it as evidence of a tested build. | There is no test for this. Delete the file and add `__pycache__/` to `.gitignore`. |

**Check against the request:** The request asks for loading the file, a monthly total and a monthly average using the standard library only. Loading is broken (#1). Total and average are implemented. Nothing extra was added beyond the `.pyc` (#5).

**Check against claims:** "Tests pass" is plausible for the two in-memory tests, but I did not run them. "Works against last month's export" cannot be true for the code as shown (#1).

**FILES NEEDED BUT NOT PROVIDED:** PR metadata (number, head and merge-base SHAs, commit trailers), CI configuration and check results, and a sample of the real export format. The sample would confirm that `amount` is a JSON number and not a string, and that `date` is a plain `YYYY-MM-DD`.

# Close-out

Pending. The author adjudicates the findings and the person closing the PR writes the close-out. A reviewer does not adjudicate its own findings.

**ADJUDICATION:** Not yet written for #1–#5. #1 is a P1, so it cannot be deferred.

**VERIFIED AFTER FIXES:** Nothing yet. The fix for #1 should be verified by reading the correction diff and running the new file-based test.

**MERGE RECOMMENDATION (reviewer's input):** **Do not merge.** `load_invoices` raises on every call (#1), so the module does not meet the request. CI status is unknown, and a missing check is not a green check. It becomes "merge after fixes" once #1 is fixed with a file-loading test, #2 is fixed or the empty-month behaviour is specified and tested, and #3–#5 are each accepted, deferred with an issue link, or rejected with evidence.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "code-read against stdlib json.loads behaviour (unknown kwargs forwarded to JSONDecoder); not executed",
      "location": "invoice_report.py:9",
      "scenario": "json.loads(..., strict_mode=True) raises TypeError (unexpected keyword 'strict_mode') on every call before parsing, so load_invoices can never load a file; untested because no test calls load_invoices; contradicts author's claim it worked on last month's export",
      "fix": "Remove strict_mode (e.g. `json.load(f)`), and add a test that writes a temp JSON file and loads it"
    },
    {
      "severity": "P2",
      "evidence_level": "code-read; not executed",
      "location": "invoice_report.py:24",
      "scenario": "Month with no invoices -> in_month empty -> ZeroDivisionError in monthly_average",
      "fix": "Return a defined value (0.0 or None) when in_month is empty, document it, and test it"
    },
    {
      "severity": "P3",
      "evidence_level": "code-read; float rounding behaviour known; not executed",
      "location": "invoice_report.py:13-18,24",
      "scenario": "Float money and double rounding: single 2.675 invoice totals 2.67; invoices 0.10 and 0.15 average to 0.12 instead of 0.13",
      "fix": "Parse with parse_float=Decimal, sum Decimals, compute average from the unrounded total, quantize once with ROUND_HALF_UP"
    },
    {
      "severity": "P3",
      "evidence_level": "code-read; not executed",
      "location": "invoice_report.py:8",
      "scenario": "open() without encoding uses locale default (cp1252 on Windows); UTF-8 export with non-ASCII content raises UnicodeDecodeError or yields mojibake",
      "fix": "open(path, encoding='utf-8') or open in binary mode for json.load"
    },
    {
      "severity": "P3",
      "evidence_level": "file present in submission",
      "location": "__pycache__/invoice_report.cpython-312.pyc",
      "scenario": "Generated bytecode committed; embeds the author's absolute local path and adds repo noise",
      "fix": "Delete it and add __pycache__/ to .gitignore"
    }
  ]
}
```
