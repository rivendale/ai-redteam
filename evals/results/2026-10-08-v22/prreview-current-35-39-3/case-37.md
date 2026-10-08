# Close-out: PR #112, CSV export for the monthly report

**Recommendation: do not merge.** The fix for F1 is incomplete: it quotes every value but does not escape double quotes inside a value. Customers' spreadsheets will still load some rows with wrong or shifted columns.

## Review report (verification of the correction diff)

**REVIEWED:** PR #112.
- Original head 1c7f9a2, merge base 40be8d1, first round in `review_findings.md`.
- This pass covers only the correction 5d1e7a9 (`work/fix.patch`), read on top of `change.patch` against `work/base/`.
- I had no tools in this session, so I could not open a worktree or run the tests. Everything below comes from reading the diffs.

**TIER:** Not recorded in the first review.
- The export has a `name` column and goes to customers. That likely carries personal data, which makes this **High** under Step 2 ("when unsure, take the higher tier").
- High needs two rounds on approved endpoints. Only one round is on record.
- If the owner confirms that `name` never holds data about people, Standard applies and one round is enough. The owner needs to decide this.

**REVIEWERS:**
- This pass: a fresh instance (Opus 5.5), which did not write the change.
- First round: reviewer not named in `review_findings.md`.
- Author: not determinable. No commit trailers were provided.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F2 | P1 | `exporter.py:10` (after 5d1e7a9) | `'"%s"' % v` wraps the value in quotes but leaves any `"` inside it as is. CSV requires an embedded quote to be written as `""`. Two examples:<br>• `["ann", 'x",y']` becomes `"ann","x",y"`. A spreadsheet or `csv.reader` reads three fields (`ann`, `x`, `y"`) instead of two, which is the same column split that F1 was meant to fix.<br>• `["ann", 'say "hi"']` becomes `"ann","say "hi""`, which reads back garbled (`say hi""`).<br>Customer notes with quotation marks are ordinary input. | `self.assertEqual(list(csv.reader(exporter.export_rows([["ann", 'x",y'], ["bob", 'say "hi"']]))), [["ann", 'x",y'], ["bob", 'say "hi"']])`. This fails at 5d1e7a9 and passes once quotes are doubled. |

**FILES NEEDED BUT NOT PROVIDED:**
- The caller that writes `export_rows` output to the download. I need it to see how lines are joined and whether a header and line terminator are added.
- The CI check list and results for 5d1e7a9.

## Close-out

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | Accepted, but the fix is **incomplete** | 5d1e7a9 fixes the exact case in the finding: `"a,b"` is now quoted, and `test_comma_value` reads back `["ann","a,b"]`. The claim that the test fails on 1c7f9a2 holds on reading: `ann,a,b` parses to 3 fields. The fix still does not deliver what F1 requires, a row that keeps its field count for any value, as F2 shows. F1 stays open until F2 is fixed. |
| F2 | Open, awaiting author | P1, so it cannot be deferred. Suggested fix: write rows with `csv.writer` to an `io.StringIO`, which handles quotes, commas and newlines. The minimum alternative is `'"%s"' % str(v).replace('"', '""')`. |

Note on the `csv.writer` fix: a value containing a newline becomes one record across two physical lines. The "list of lines" return type cannot represent that cleanly. Returning the full CSV text, or one record per element that the caller joins with `\r\n`, avoids the problem. Pick one and test it.

**VERIFIED AFTER FIXES:**
- Head moved from 1c7f9a2 to 5d1e7a9.
- `exporter.py:9–10` (docstring and quoting): verified by reading only, and found incomplete (F2).
- `tests/test_exporter.py`: `test_plain_row` was rewritten to compare via `csv.reader`, and `test_comma_value` was added. I read both but **did not run them** because no tools were available.
- Any commit after 5d1e7a9 is not reviewed.

**MERGE RECOMMENDATION: do not merge.** Open items:
1. F2 (P1) is unfixed, so F1 is not actually resolved.
2. The tier needs an owner decision. If High, the second review round has not run.
3. CI check results for the head have not been seen, and a missing check is not green.
4. An owner question, not a finding: if note values can come from users other than the customer downloading the file, a value starting with `=`, `+`, `-` or `@` opens as a formula in a spreadsheet (CSV injection). The owner should decide whether such values need neutralising.

After the F2 fix, verify it by reading the correction diff and running the F2 test. A full new review is not needed.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "read in diff, not executed",
      "location": "exporter.py:10",
      "scenario": "The fix wraps values in quotes without doubling embedded double quotes. The value 'x\",y' is written as \"x\",y\" and parses as two fields, so the row splits into the wrong number of columns. 'say \"hi\"' reads back garbled.",
      "fix": "Write rows with csv.writer to io.StringIO (or at minimum replace '\"' with '\"\"' inside each value). Add a test that round-trips values containing quotes, including a quote followed by a comma, through csv.reader."
    }
  ]
}
```