# Close-out: PR #112, CSV export for the monthly report

**Review report (close-out verification)**

**REVIEWED:** PR #112. The original head is 1c7f9a2 and the merge base is 40be8d1. The fix commit is 5d1e7a9 (`work/fix.patch` applied on top of `work/change.patch`). I verified the fix by reading the correction diff, as Step 6 requires. This session has no tools, so I ran no tests. Every test result below comes from reading the code against `csv.reader`'s documented behaviour, not from running it.

**TIER:** Standard. This is an ordinary code change to output formatting. It does not touch authentication, permissions, secrets, network exposure, migrations or money. The exported rows include a `name` column, which may be personal data. That affects where the code may be sent for review (Step 3), but it does not change who can access what. If the owner treats this export as personal data handling, the tier becomes High and a second round is owed.

**REVIEWERS:** This instance (Opus 5.5), which did not write the change. The author is not recorded: no commit trailers were provided for 1c7f9a2 or 5d1e7a9.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F2 | P1 | exporter.py:10 (after fix 5d1e7a9) | The fix wraps each value in quotes but does not double the quotes inside it (`'"%s"' % v`). A value of `a",b` becomes `"a",b"`. `csv.reader` and spreadsheets read that as two fields, `a` and `b"`, so the row has the wrong number of columns. This is the same failure as F1, now triggered by a double quote instead of a bare comma. A value of `say "hi"` becomes `"say "hi""`, which is read back as `say hi""` (corrupted, not split). | `list(csv.reader(exporter.export_rows([["ann", 'a",b']])))` should equal `[["ann", 'a",b']]`. Do the same for `'say "hi"'`. Both fail today. |
| F3 | P2 | exporter.py:10 | This was present before the fix and missed in round 1. A value that starts with `=`, `+`, `-` or `@`, such as a note of `=HYPERLINK("http://x","click")`, is written as-is. The export is downloaded by customers and opened in their spreadsheets, so the spreadsheet runs it as a formula (CSV/formula injection). It matters if any exported field can be set by someone other than the downloading customer. | Export `[["ann", "=1+1"]]` and assert the field is neutralised, for example read back as `'=1+1` or rejected. This depends on the policy the owner chooses. |

**Verification of F1 as adjudicated:**
- The claim "`test_comma_value` fails on the first commit and passes now" holds by reading. On 1c7f9a2 the output is `ann,a,b`, which reads back as 3 fields, so the test fails. On 5d1e7a9 the output is `"ann","a,b"`, which reads back correctly, so it passes.
- The fix is incomplete, though: it does not escape quotes (F2). F1 was "a value containing a CSV special character splits the row". The fix moved that failure from `,` to `"`, so F1 is not closed.
- The regression test covers only a comma. It has no case with a quote or a newline.

**FILES NEEDED BUT NOT PROVIDED:**
- The commit trailers for 1c7f9a2 and 5d1e7a9 (to identify the author).
- The CI check results on 5d1e7a9.
- The caller that writes `export_rows` output to the download, including how lines are joined. This matters because a quoted value containing a newline is valid CSV only if the caller joins the lines without re-splitting them.

**Suggested fix for F2:** use the standard library writer instead of hand-quoting, for example:

```python
import csv, io

def export_rows(rows):
    """Lines of a CSV file for `rows` (lists of values), header excluded."""
    out = []
    for row in rows:
        buf = io.StringIO()
        csv.writer(buf, lineterminator="").writerow(row)
        out.append(buf.getvalue())
    return out
```

The minimal alternative is `'"%s"' % str(v).replace('"', '""')`.

**Close-out**

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | Accepted, but **not closed** | The fix in 5d1e7a9 handles commas but not embedded quotes (see F2). It reopens until F2 is fixed. |
| F2 | Pending author decision | New in close-out. It is a P1, so it cannot be deferred. |
| F3 | Pending author decision | A P2 can be deferred with a linked issue, or rejected with evidence that no exported field is attacker-controlled. |

**VERIFIED AFTER FIXES:** I read `exporter.py:9-10` and `tests/test_exporter.py` in 5d1e7a9. The comma case is correct by reading. Embedded quotes are not handled. I ran no tests because this session has no tools.

**MERGE RECOMMENDATION: do not merge.** These items are open:
- F2 is an unresolved P1. Customers' spreadsheets will misparse any value that contains a `"`.
- F3 has no decision yet.
- CI status on the new head is not shown, and a missing check is not green.
- The author is not recorded.

Merge after F2 is fixed with a quote regression test, F3 is adjudicated, and checks on the final head are green.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "read (csv.reader parsing traced by hand; not executed)",
      "location": "exporter.py:10",
      "scenario": "Fix 5d1e7a9 quotes values without doubling embedded quotes: value 'a\",b' is written as \"a\",b\" and parsed as two fields ('a', 'b\"'); 'say \"hi\"' is read back as 'say hi\"\"'. F1's column-split defect persists for values containing a double quote.",
      "fix": "Use csv.writer (e.g. via io.StringIO with lineterminator='') or escape with str(v).replace('\"', '\"\"'); add regression tests for 'a\",b' and 'say \"hi\"' read back with csv.reader."
    },
    {
      "severity": "P2",
      "evidence_level": "read (depends on whether exported fields are attacker-controlled; caller not provided)",
      "location": "exporter.py:10",
      "scenario": "Values beginning with =, +, - or @ (e.g. '=HYPERLINK(...)') are exported verbatim and run as formulas when customers open the download in a spreadsheet (CSV/formula injection).",
      "fix": "Decide a policy: prefix such values with a single quote or reject them; add a test asserting '=1+1' is neutralised. Alternatively defer with a tracking issue or reject with evidence that fields are not externally controlled."
    }
  ]
}
```