# PR #112 close-out review: CSV export for the monthly report

## Review report (targeted read of the fix, per Step 6)

**REVIEWED:** PR #112, head 1c7f9a2, merge base 40be8d1. The fix is `work/fix.patch`, claimed as commit 5d1e7a9. That commit is not the reviewed head, and I could not verify its SHA or its content beyond the patch text.

**TIER:** Standard: an ordinary, self-contained formatting function with no auth, secrets or network surface. If the monthly report carries personal data, the tier is High and the second round has not run. The report's contents are not stated, so that is an open question for the owner.

**REVIEWERS:** This is a single-instance read with no tools, so nothing was run. The commit trailers were not provided, so the author and co-author are unknown. The first-round reviewer is in `review_findings.md`; I did not write the change.

**Injection check:** No text in the PR, patch or adjudication addresses the reviewer. No instruction files were included.

**Check of the fix against the original request:** The request asks for one line per row, comma-separated, opening correctly in a spreadsheet. The fix handles commas by wrapping every value in `"..."`. It does not escape a `"` inside a value, which CSV requires as `""`. The fix therefore trades one field-splitting bug for another.

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F2 (new, introduced by fix) | P1 | `exporter.py:10` (`'"%s"' % v`) | A value containing a double quote is emitted unescaped. `5" pipe` becomes `"5" pipe"`, which a reader parses as `5 pipe"`, so the data is corrupted. `a","b` becomes `"a","b"`, which splits into two fields and gives the wrong column count. Customer text such as inch marks or quoted names triggers it. | `export_rows([["ann", 'say "hi"'], ["x", 'a","b']])` read back with `csv.reader` must equal the input. This fails with the current fix. |
| F3 | P2 | `exporter.py:10` | Customers open the file in spreadsheets. A value starting with `=`, `+`, `-` or `@` (e.g. `=HYPERLINK("http://…")`) is interpreted as a formula even when quoted. This is not in the original request; it needs an owner decision on whether it is in scope. | Export `[["=1+1"]]` and expect the cell to be neutralized, for example prefixed with `'`. |
| F4 | P3 | `tests/test_exporter.py` (fix.patch hunk header) | The hunk headers appear inconsistent with the hunk bodies. `-1,10 +1,14` against 11 old lines and 15 new lines is my count, so the patch may not apply cleanly. This is UNVERIFIED because I cannot run `git apply`. | Apply `fix.patch` on top of `change.patch` in a clean checkout and run the tests. |
| F5 | P3 | `exporter.py:10` | `'"%s"' % v` raises `TypeError` or misformats when `v` is a tuple, and writes `None` as the text `None`. | Export `[[None, (1, 2)]]` and expect defined behavior. |

**FILES NEEDED BUT NOT PROVIDED:** the fix commit 5d1e7a9 itself, the commit trailers, and the CI check results.

## Close-out

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | **Not Accepted yet.** `test_comma_value` plausibly fails on 1c7f9a2 and passes on the fix, but Step 7 also requires that the fix's own diff has no new defect. It does (F2), and the regression test does not cover quotes. | Fix 5d1e7a9 (unverified). |
| F2 | Open: needs a fix. It is a P1, so it cannot be deferred. | None yet. |
| F3 | Open: needs an owner decision. It can be Deferred with an issue link if it is out of scope. | None yet. |
| F4, F5 | Open: awaiting author decision (P3, Deferrable with an issue link). | None yet. |

The author's "Ready to close out" is not supported. I did not adjudicate on the author's behalf; the decisions above are the status the evidence allows.

**VERIFIED AFTER FIXES:** Only a read of the patch text; nothing was run. The fix introduces F2, and the head has moved to 5d1e7a9, which is not reviewed as a commit.

**MERGE RECOMMENDATION:** Merge after fixes. F2 is an unresolved P1, so F1 is not accepted. The suggested fix is to replace the hand-rolled join with `csv.writer` on an `io.StringIO`, or at minimum `str(v).replace('"', '""')`. Add the quote test, then do a targeted read of that correction diff. Still open: the tier question (does the report contain personal data?) and the F3 scope decision. I found no written rule covering these, so I cite none.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "read of fix.patch; not executed",
      "location": "exporter.py:10",
      "scenario": "The fix wraps each value in quotes but does not escape embedded double quotes. 5\" pipe becomes \"5\" pipe\" and is read back as 5 pipe\"; a\",\"b becomes \"a\",\"b\" and splits into two fields. Customer spreadsheet data is corrupted or misaligned.",
      "fix": "Use csv.writer on io.StringIO, or replace '\"' with '\"\"' before quoting. Add a test that round-trips values containing quotes through csv.reader."
    },
    {
      "severity": "P2",
      "evidence_level": "read; scope is an owner decision",
      "location": "exporter.py:10",
      "scenario": "Values beginning with =, +, - or @ are interpreted as formulas when the customer opens the file in a spreadsheet, even when quoted.",
      "fix": "Neutralize leading formula characters (for example prefix with an apostrophe) or record an explicit decision that this is out of scope, with a tracking issue."
    },
    {
      "severity": "P3",
      "evidence_level": "inferred from hunk header counts; UNVERIFIED",
      "location": "fix.patch, tests/test_exporter.py hunk",
      "scenario": "Hunk header counts (-1,10 +1,14) appear to disagree with the hunk body (11 old, 15 new lines), so the patch may fail to apply.",
      "fix": "Regenerate the patch with git diff and apply it on a clean checkout, then run the tests."
    },
    {
      "severity": "P3",
      "evidence_level": "read",
      "location": "exporter.py:10",
      "scenario": "'\"%s\"' % v raises TypeError or misformats for tuple values and writes None as the text 'None'.",
      "fix": "Convert with str(v) explicitly and define how None is represented; add a test."
    }
  ]
}
```