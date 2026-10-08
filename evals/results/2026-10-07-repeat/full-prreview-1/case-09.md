# pr-review: invoice_report.py

**Review report**

**REVIEWED:** Not identifiable. No PR number, head SHA or merge base was supplied. Step 1 requires both SHAs. This review covers only the two files pasted in the inputs. Any commit, file or later push not shown there is unreviewed.

**TIER:** Standard. This is an ordinary code change that touches no auth, secrets, network exposure, migrations or personal data. It does report money amounts, so wrong figures matter, but it moves no money. The context also gives the stakes as standard. One round.

**DATA / ENDPOINT (Step 3):** Nothing was sent outside this session. No subagent was used and no data left the session.

**REVIEWERS:** This instance (Claude, `claude-opus-5-5`), reading the code only. This session did not write the change. The author is unknown because no commit trailers were provided.

**EXECUTION:** None. This session has no tools, so every finding below comes from reading the code against the Python standard library's documented behaviour. None was confirmed by running it.

**On the author's claims:**
- "Tests pass" is plausible for the two tests as written.
- "Ran it against last month's export and it works" contradicts the code. `load_invoices` cannot succeed on any input (finding 1), and no test calls it. Whatever was run, it was not this `load_invoices`.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `invoice_report.py:9` | `json.loads(f.read(), strict_mode=True)` fails on every call. `json.loads` passes unknown keyword arguments to `JSONDecoder(**kw)`. `JSONDecoder.__init__` accepts `strict`, not `strict_mode`, so it raises `TypeError: ... unexpected keyword argument 'strict_mode'` before any parsing. Loading any file, valid or not, crashes. The requested "load a JSON file" feature does not work. The tests miss it because none of them calls `load_invoices`. | Write `SAMPLE` to a temp file with `json.dump`, call `r.load_invoices(path)`, and assert it equals `SAMPLE`. It raises `TypeError` today. The fix is to drop the argument (`json.load(f)`); `strict=True` is already the default. |
| 2 | P2 | `invoice_report.py:24` | `monthly_average(SAMPLE, 2026, 5)` asks about a month with no invoices. `in_month` is empty, so `/ len(in_month)` raises `ZeroDivisionError`. Asking for a quiet or future month is ordinary use. `monthly_total` returns `0.0` for the same month, so the two functions are inconsistent. | `assertEqual(r.monthly_average(SAMPLE, 2026, 5), 0.0)` or `assertIsNone(...)`, depending on what the owner decides an empty month should return. It raises today. |
| 3 | P3 | `invoice_report.py:12-17, 24` | Amounts are summed as binary floats and rounded with `round()`, which rounds a half to the even digit. Example: invoices of `0.25` and `0.00` in one month give an average of `0.125`, and `round(0.125, 2)` returns `0.12`. Half-up invoice arithmetic expects `0.13`. Amounts that are not exact in binary can also land on the wrong side of a half (`round(2.675, 2) == 2.67`). The request does not name a rounding rule, so this is a question for the owner, but the report deals in money. | `assertEqual(r.monthly_average([{"id":1,"date":"2026-03-01","amount":0.25},{"id":2,"date":"2026-03-02","amount":0.0}], 2026, 3), 0.13)`. It fails today. A fix would parse with `json.load(f, parse_float=Decimal)` and use `quantize(Decimal("0.01"), ROUND_HALF_UP)`. |
| 4 | P3 | `invoice_report.py:8` | `open(path)` has no `encoding`, so it uses the locale default. On Windows that is often cp1252. A UTF-8 export with non-ASCII text, such as a customer name in an extra field, either decodes to garbled text or raises `UnicodeDecodeError`, for example on byte `0x81`. JSON files are UTF-8 by specification (RFC 8259 §8.1). | Write a UTF-8 file containing `"\u0081"` in a field and load it with the locale forced to cp1252. It fails today and passes with `open(path, encoding="utf-8")`. |

**Not raised as findings:** these lack a concrete failure scenario.
- The request says the module "reports" figures. It provides functions but no CLI or printed output. Returning the values probably satisfies the request, but the owner should confirm.
- A missing or malformed `date` raises `KeyError` or `ValueError`. The request fixes the input format, so this is acceptable unless the owner wants clean errors.

**FILES NEEDED BUT NOT PROVIDED:** the PR metadata (number, head SHA, merge base, commit trailers), the CI configuration and check results, and the "last month's export" the author says they ran it against.

**Close-out**

The reviewer does not adjudicate its own findings. The author must record a decision for each one: Accepted with a fix commit and a regression test, Deferred with an issue link (P2 and P3 only), or Rejected with evidence.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | pending (P1, cannot be deferred) | |
| 2 | pending | |
| 3 | pending (owner decision on rounding) | |
| 4 | pending | |

**VERIFIED AFTER FIXES:** Nothing has been fixed yet.

**MERGE RECOMMENDATION:** Do not merge.
- Finding 1 is an unresolved P1: the module's load path cannot work.
- The head SHA and merge base are unknown, so the reviewed target is not pinned.
- No CI check results were provided, and a missing check is not green.
- An owner decision is pending on empty-month behaviour (2) and the rounding rule (3).

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "code-read against stdlib json.loads/JSONDecoder signature; not executed",
      "location": "invoice_report.py:9",
      "scenario": "json.loads(..., strict_mode=True) forwards the unknown kwarg to JSONDecoder(**kw), which raises TypeError on every call; load_invoices never succeeds, and no test calls it, contradicting the author's claim of a successful run on last month's export.",
      "fix": "Use json.load(f) (strict=True is already the default) and add a test that round-trips SAMPLE through a temp file via load_invoices."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read; not executed",
      "location": "invoice_report.py:24",
      "scenario": "monthly_average for a month with no invoices divides by len([]) == 0 and raises ZeroDivisionError, while monthly_total returns 0.0 for the same month.",
      "fix": "Return 0.0 or None when in_month is empty (owner to choose) and add a test for an empty month."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read; Python round() half-to-even on 0.125 is exact-binary and deterministic; not executed",
      "location": "invoice_report.py:12-17, 24",
      "scenario": "Float summation plus round() gives half-to-even and binary artefacts: amounts 0.25 and 0.00 average to round(0.125, 2) == 0.12, not 0.13 under half-up.",
      "fix": "Owner to specify the rounding rule; if half-up, parse with parse_float=Decimal and quantize with ROUND_HALF_UP, with a test for the 0.125 case."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read; not executed",
      "location": "invoice_report.py:8",
      "scenario": "open(path) without encoding uses the locale codec (e.g. cp1252 on Windows); UTF-8 exports with non-ASCII text decode to garbled text or raise UnicodeDecodeError.",
      "fix": "open(path, encoding=\"utf-8\") and add a test with a non-ASCII field under a non-UTF-8 locale."
    }
  ]
}
```