# pr-review close-out: PR #112

## Review report (close-out verification of the F1 fix)

**REVIEWED:** PR #112, head 1c7f9a2, merge base 40be8d1. The fix is `work/fix.patch`, which the author calls 5d1e7a9. I could not confirm that SHA from the materials, and I could not confirm that the head hasn't moved. This session has no tools, so nothing was run.

**TIER:** Standard. It is ordinary code with no auth, secrets or migration, but the output goes to customer spreadsheets. If the report rows carry personal data, that would raise it to High, and the materials don't say.

**REVIEWERS:** This is a targeted read of the correction diff and its tests, as Step 6 and Step 7 require, not a new full round. No commit trailers were provided, so the author and any co-author are unknown. This reviewer did not write the change. Step 3 isn't triggered because no code left this session.

**Targeted read of the fix.** `'"%s"' % v` wraps each value in quotes but does not escape a `"` inside the value. CSV requires an embedded quote to be doubled. For example, `say "hi"` becomes `"say "hi""`, which a spreadsheet or `csv.reader` misparses. F1 fixed the comma case and introduced a new defect in the same function, so under Step 7 it cannot be marked Accepted.

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F1 | P1 (original) | exporter.py:10 | A comma in a value splits the field. The fix handles this case. The `test_comma_value` claim is consistent with the diff: the old code gives `ann,a,b` and reads back as 3 fields. I did not run it. | Already added (`test_comma_value`). |
| F2 (new, from the fix) | P1 | exporter.py:10 (after fix) | A value containing `"`, such as `5" pipe` or `say "hi"`, is emitted as `"5" pipe"`. Quote handling then ends the field early, so the row is corrupted or the columns shift. A value with a quote and a comma fails the same way. | Export `[["ann", 'say "hi"']]` and read it back with `csv.reader`. Expect `[["ann", 'say "hi"']]`. It fails with the current fix. |
| F3 (new) | P2 | exporter.py:10 | Quoting does not stop spreadsheet formula evaluation. A value such as `=HYPERLINK(...)` or `+cmd...` that came from user data runs when the customer opens the file. The original request says the file must open correctly in a spreadsheet. | Export `[["=1+1", "x"]]`. Expect the cell to be neutralised, for example prefixed with `'`. |
| F4 (new) | P2 | PR.md / change.patch | The PR says `export_rows` is for the report download, but the diff only adds the function. No caller, endpoint or header-plus-rows assembly is in it. The request ("add a CSV export for the monthly report") may not be met. | An integration test that downloads the monthly report and parses it with `csv.reader`. |
| F5 (new) | P3 | tests/test_exporter.py hunk header in fix.patch | The hunk is declared `-1,10 +1,14`, but the lines shown count as 11 old and 15 new. The patch may be malformed and fail to apply. I haven't applied it, so this is unverified. | Run `git apply --check work/fix.patch` on top of `change.patch`. |

**Suggested fix for F2:** use the standard library rather than hand-quoting. For example, write with `csv.writer` into `io.StringIO`, or at minimum use `'"%s"' % str(v).replace('"', '""')`. This is UNVERIFIED against the consumer. The check is the round-trip test above, which uses the same `csv.reader` the author's tests use.

**FILES NEEDED BUT NOT PROVIDED:** the caller of `export_rows` and the download endpoint (F4), CI results, the full 5d1e7a9 commit, and the commit trailers.

## Close-out

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | Not Accepted | The fix and a regression test exist, but the fix diff introduces F2, so by Step 7 it is a new finding rather than an acceptance. |
| F2 | Open | The author must fix it and add the quote round-trip test. |
| F3 | Open | The author must fix it or defer it with an issue link, since a P2 can be deferred. |
| F4 | Open | The author must wire `export_rows` into the download or confirm that is a separate PR. |
| F5 | Open | Unverified until `git apply --check` is run. |

The author's "Ready to close out" is not supported.

**VERIFIED AFTER FIXES:** only the fix diff was read, not run. The head has not been re-verified.

**MERGE RECOMMENDATION:** merge after fixes. F2 is a P1 introduced by the fix, and it corrupts customer-facing output. The fix commit has to be read again after F2 is corrected. Before merging, the expected checks must also be present and green. None were provided, and a missing check is not green. No written rule settles this, so none is cited.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "reasoned from the diff; not executed",
      "location": "exporter.py:10 (after fix.patch)",
      "scenario": "The fix quotes every value with '\"%s\"' % v but does not double embedded double quotes. A value like 'say \"hi\"' is emitted as \"say \"hi\"\"; spreadsheets and csv.reader misparse it, corrupting the row or shifting columns.",
      "fix": "Use csv.writer with io.StringIO, or escape with str(v).replace('\"', '\"\"'). Add a test that exports [['ann', 'say \"hi\"']] and round-trips through csv.reader."
    },
    {
      "severity": "P2",
      "evidence_level": "reasoned from the diff; not executed",
      "location": "exporter.py:10",
      "scenario": "Quoting does not stop formula injection: a value starting with =, +, - or @ is evaluated when the customer opens the file in a spreadsheet.",
      "fix": "Prefix such values with a single quote, or defer with a tracked issue. Test that export_rows([['=1+1','x']]) neutralises the cell."
    },
    {
      "severity": "P2",
      "evidence_level": "reasoned from the diff; caller not provided",
      "location": "PR.md / change.patch",
      "scenario": "export_rows has no caller or download endpoint in the diff, so the requested monthly-report CSV export may not be delivered.",
      "fix": "Wire the function into the report download with the header, or confirm a follow-up PR. Add an integration test parsing the downloaded file."
    },
    {
      "severity": "P3",
      "evidence_level": "UNVERIFIED; hunk counts only",
      "location": "fix.patch tests/test_exporter.py hunk header",
      "scenario": "The hunk header says -1,10 +1,14 but the lines shown count as 11 old and 15 new, so the patch may fail to apply.",
      "fix": "Run git apply --check on fix.patch over change.patch and regenerate the patch if it fails."
    }
  ]
}
```