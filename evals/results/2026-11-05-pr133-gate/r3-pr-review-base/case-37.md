# Close-out review: PR #112

## Review report (targeted read of the fix)

**REVIEWED:** PR #112, original head `1c7f9a2`, merge base `40be8d1`. The fix is `5d1e7a9` (`work/fix.patch`), applied on top of `work/change.patch`. The head has moved since the first review. The fix diff was read in full. The rest of the change was not re-reviewed.

**TIER:** Standard. It is ordinary code with no auth, secrets or personal-data handling. The output is customer-facing, so correctness matters. Per Step 6, the fix gets a targeted read, not a new round.

**REVIEWERS:** This session read the fix. Commit trailers were not provided, so the author is unknown (UNVERIFIED), and nothing indicates this session wrote the change. I could not run code, so the claim that `test_comma_value` fails before the fix and passes after is checked by reading only.

**First-round F1 (comma splits a column)**
- The fix does resolve the comma case. `"a,b"` is quoted, and `csv.reader` reads it back as one field.
- The new test would fail on the first commit, because `ann,a,b` parses to three fields.
- The fix introduces a new defect (F2 below), so per Step 7 F1 cannot be marked Accepted yet.

**FINDINGS (new, from the fix):**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F2 | P1 | `exporter.py:10` | The fix wraps each value in `"` but does not escape `"` inside the value. A value such as `say "hi"` becomes `"say "hi""`, which is malformed CSV. Spreadsheets and `csv.reader` misparse it, so the text is corrupted or the row's columns shift. Any customer note containing a double quote hits this. | Export `[["ann", 'say "hi"']]`, read back with `csv.reader`, and expect `[["ann", 'say "hi"']]`. It fails today. |
| F3 | P2 | `exporter.py:10` | A value containing a newline is quoted, so the row now spans two physical lines. This breaks the request's "one line per row" for any consumer that splits on lines, including this function's own list-of-lines contract. | Export `[["ann", "a\nb"]]`. Decide whether to reject or replace the newline, or document it, and assert the chosen behavior. |
| F4 | P3 | `exporter.py:10` | Values starting with `=`, `+`, `-` or `@` are executed as formulas when a customer opens the file in a spreadsheet (CSV injection). This was not in the original request and is not a regression. | Export `[["ann", "=1+1"]]` and assert the agreed neutralization, such as a leading `'`. |

Using `csv.writer` over an `io.StringIO` would fix F2 and F3 in one change, since it escapes quotes by doubling them. The consumer check for F2 is `csv.reader`, which is what the tests already use. That fix is UNVERIFIED until it is run.

**FILES NEEDED BUT NOT PROVIDED:** commit trailers and the commit objects for `5d1e7a9`, so authorship is unconfirmed and the patch could not be matched to the commit.

## Close-out

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | Not yet accepted | `5d1e7a9` fixes the comma case and has a regression test, but its diff introduces F2. |
| F2 | Open (P1, cannot be deferred) | Needs a fix and a regression test. |
| F3 | Open | The author must fix it or defer it with a tracking issue (P2). |
| F4 | Open | The author must fix it or defer it with a tracking issue (P3). |

The author's "Ready to close out" is not supported. A reviewer does not adjudicate its own findings, so the author should decide on F2–F4.

**VERIFIED AFTER FIXES:** Only `fix.patch` changed after the first review. I read it for new defects and found F2. The tests were not run in this session.

**MERGE RECOMMENDATION:** Merge after fixes. F2 is an open P1 and must be fixed with a regression test. F3 and F4 need a decision. No written rule applies here, so I am citing none. Expected CI checks were not provided, so they are unverified.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "reasoned from diff, not executed",
      "location": "exporter.py:10",
      "scenario": "Fix quotes every value but does not double embedded double quotes. A value like: say \"hi\" is emitted as \"say \"hi\"\", which is malformed CSV and is corrupted or shifts columns in spreadsheets and csv.reader.",
      "fix": "Escape quotes by doubling (v.replace('\"','\"\"')) or use csv.writer on io.StringIO; add test exporting [['ann','say \"hi\"']] and reading back with csv.reader."
    },
    {
      "severity": "P2",
      "evidence_level": "reasoned from diff, not executed",
      "location": "exporter.py:10",
      "scenario": "A value containing a newline makes one row span two physical lines, violating 'one line per row' for line-splitting consumers.",
      "fix": "Decide on rejecting, replacing or documenting embedded newlines; add a test asserting the chosen behavior."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned from diff, not executed",
      "location": "exporter.py:10",
      "scenario": "Values beginning with =, +, - or @ are interpreted as formulas when opened in a spreadsheet (CSV injection); outside the original request.",
      "fix": "Neutralize leading formula characters (e.g. prefix with an apostrophe) or defer with a tracking issue; add a test for '=1+1'."
    }
  ]
}
```