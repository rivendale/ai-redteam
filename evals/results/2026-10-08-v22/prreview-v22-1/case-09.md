# pr-review: invoice_report.py

**Constraints of this session:** I have no tools, so I could not check out a worktree, read SHAs or commit trailers, or run the tests. Every finding below comes from reading the code. None was executed.

## Review report

**REVIEWED:** No PR number, head SHA or merge base was provided. I reviewed the two files exactly as pasted, so this review is tied to that text and not to a commit. Before posting, record the head SHA these files came from. Any later commit is unreviewed.

**TIER:** Standard. This is ordinary application code that reads a local file and does arithmetic. It reports on invoice amounts but moves no money and touches no auth, secrets, network or personal data. That matches the stated stakes, so one round is required, and this is that round.

**DATA PROTECTION:** Nothing was sent to a subagent or an external endpoint. The review stayed in this session.

**REVIEWERS:**
- Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), single in-session instance.
- Author: unknown, because no commit trailers were provided. This session did not write the change, so in-session review keeps independence.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `invoice_report.py:9` | `json.loads(f.read(), strict_mode=True)` raises `TypeError` on every call. `json.loads` forwards unknown keyword arguments to `JSONDecoder(**kw)`, and `JSONDecoder.__init__` accepts `strict`, not `strict_mode`. So `load_invoices` cannot load any file, even a valid one, and the "load a JSON file" half of the request never works. This contradicts the author's claim that it "works against last month's export". No test calls `load_invoices`, so the claim is unverified. Fix: drop the argument (`json.load(f)`), or use `strict=True` if that was intended. | Write SAMPLE to a temp file, call `r.load_invoices(path)`, and assert it equals SAMPLE. Today it raises `TypeError: ... unexpected keyword argument 'strict_mode'`. |
| 2 | P1 | `invoice_report.py:23-24` | `monthly_average` divides by `len(in_month)`. For a month with no invoices (a new account, a quiet month, a future month, a typo in the year) it raises `ZeroDivisionError` instead of returning a result. | `r.monthly_average(SAMPLE, 2026, 5)` should return the agreed value (`0.0` or `None`, owner's choice) and not raise. Today it raises `ZeroDivisionError`. |
| 3 | P2 | `invoice_report.py:13-18, 24` | Money is summed and averaged as binary floats, then passed through `round()`, which works on the float's binary value. Concrete case: amounts `0.01` and `0.02` average to `0.015`, which is stored as 0.01499…, so `round` returns `0.01`; half-up accounting expects `0.02`. Over many invoices, float drift in the sum can also move the rounded cent. Workaround: parse with `parse_float=Decimal`, sum as `Decimal`, and quantize with `ROUND_HALF_UP`. | Two invoices in one month with amounts `0.01` and `0.02`: assert the average equals `Decimal("0.02")`. Today it returns `0.01`. |
| 4 | P2 | `invoice_report.py:15, 23` | `date.fromisoformat` runs on every record, whichever month is requested. One record with a malformed or missing date (`"2026-3-4"`, `""`, or no `"date"` key) raises `ValueError` or `KeyError` and aborts the report for every month. The error does not name the record's id. Also, on Python 3.11+ `fromisoformat` accepts forms outside the stated `YYYY-MM-DD` contract, such as `"20260304"`, so the format is not actually enforced. | Add `{"id": 9, "date": "2026-3-4", "amount": 1}` to SAMPLE and call `monthly_total(..., 2026, 4)`. Assert either a clear error naming id 9 or a documented skip. Today it raises a bare `ValueError` with no id. |
| 5 | P3 | `invoice_report.py:8` | `open(path)` has no `encoding=`, so it uses the locale encoding. On a Windows host with cp1252, a UTF-8 export containing non-ASCII text (for example in ids or other fields) is mis-decoded or raises `UnicodeDecodeError`. JSON files are UTF-8 by spec (RFC 8259). | Write a UTF-8 file containing `"id": "Café-1"`, load it with the locale forced to cp1252, and assert the id round-trips. |

**Checked against the request:**
- Standard library only: yes.
- Total and average for a month: present as functions.
- Loading: broken (finding 1).
- Nothing extra was added.

**Tests:** The two existing tests should pass on in-memory data. They exercise none of the paths in findings 1, 2 and 4.

**FILES NEEDED BUT NOT PROVIDED:**
- The PR or commit metadata (head SHA, merge base, trailers).
- CI configuration and check results.
- A sample of "last month's export", to confirm the real `amount` type (number or string) and date format.

## Close-out

A reviewer does not adjudicate its own findings. The author needs to fill in this table.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | Pending (P1, cannot be deferred) | — |
| 2 | Pending (P1, cannot be deferred) | — |
| 3 | Pending | — |
| 4 | Pending | — |
| 5 | Pending | — |

**VERIFIED AFTER FIXES:** Nothing yet. Each fix needs a regression test that fails before the fix and passes after it, plus a targeted read of the fix diff.

**MERGE RECOMMENDATION:** Do not merge.
- Two P1s are open. Finding 1 means the module cannot load any file at all.
- The reviewed SHA is not recorded.
- CI check status is unknown, and a missing check does not count as green.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "code-read (CPython json.loads forwards **kw to JSONDecoder, which has 'strict' not 'strict_mode'); not executed",
      "location": "invoice_report.py:9",
      "scenario": "load_invoices raises TypeError on any input because strict_mode is not a valid JSONDecoder argument; no test calls it, contradicting the author's 'ran it against last month's export' claim",
      "fix": "Use json.load(f) (or strict=True if intended) and add a test that loads a temp file"
    },
    {
      "severity": "P1",
      "evidence_level": "code-read; not executed",
      "location": "invoice_report.py:23-24",
      "scenario": "monthly_average for a month with no invoices divides by zero and raises ZeroDivisionError",
      "fix": "Return 0.0 or None (owner's choice) when in_month is empty; add a test for an empty month"
    },
    {
      "severity": "P2",
      "evidence_level": "code-read; float rounding behavior of round(0.015, 2) known",
      "location": "invoice_report.py:13-18, 24",
      "scenario": "Money handled as binary float; average of 0.01 and 0.02 rounds to 0.01 instead of half-up 0.02, and float drift can shift cents",
      "fix": "Parse with parse_float=Decimal, sum as Decimal, quantize with ROUND_HALF_UP"
    },
    {
      "severity": "P2",
      "evidence_level": "code-read; not executed",
      "location": "invoice_report.py:15, 23",
      "scenario": "One malformed or missing date anywhere in the file raises ValueError/KeyError and aborts the report for every month without naming the record; fromisoformat on 3.11+ also accepts non-YYYY-MM-DD forms",
      "fix": "Validate dates once at load time against YYYY-MM-DD and raise an error that names the invoice id"
    },
    {
      "severity": "P3",
      "evidence_level": "code-read; platform-dependent",
      "location": "invoice_report.py:8",
      "scenario": "open() without encoding uses the locale encoding; UTF-8 export with non-ASCII text mis-decodes or fails on cp1252 hosts",
      "fix": "open(path, encoding='utf-8')"
    }
  ]
}
```