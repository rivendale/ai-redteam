# PR #112 close-out review

## Review report

**REVIEWED:** PR #112, original head 1c7f9a2, merge base 40be8d1. The fix commit 5d1e7a9 (`work/fix.patch`) is read as a targeted diff only. I have no tools, so nothing was run; every conclusion below is from reading the code.

**TIER:** Standard. This is ordinary code with no auth, secrets or migrations. The stakes (customer downloads loaded into spreadsheets) argue against going lower. Whether the rows carry personal data is not stated. If they do, the tier is High and a second round is required.

**REVIEWERS:** I reviewed this as a fresh instance (Sonnet 5.5) and did not write the change. The commit trailers were not provided, so the author is unknown. Round 1 is in `review_findings.md`. The author adjudicated it themselves.

**Targeted read of the fix** (`exporter.py:9`):
```python
return [",".join('"%s"' % v for v in row) for row in rows]
```
This wraps every value in quotes but does not escape a double quote inside a value. In CSV (RFC 4180, which spreadsheets follow) an embedded `"` must be written as `""`.

**FINDINGS** (new findings from the fix read; F1 itself is addressed in the close-out):

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F2 | P1 | `exporter.py:9` (fix.patch) | A value containing a double quote, e.g. `5" pipe` or `say "hi"`, is emitted as `"5" pipe"`. The field closes early and the spreadsheet misparses the row. Fields shift or merge, which is the same class of failure F1 reported, now for quotes. | Export `[["ann", 'say "hi"']]` and read it back with `csv.reader`. Expect `[["ann", 'say "hi"']]`. Reasoned, not run; it should fail on 5d1e7a9. |
| F3 | P2 | `exporter.py:9` | A value beginning with `=`, `+`, `-` or `@` (e.g. `=HYPERLINK(...)`) is evaluated as a formula when the customer opens the file. Quoting does not prevent this. It is only relevant if any exported field can contain customer-controlled text. | Export `[["=1+1"]]` and assert the cell is neutralised (e.g. prefixed with `'`), if the owner decides to mitigate. |
| F4 | P3 | `exporter.py:9` | `'"%s"' % v` raises `TypeError` or misformats if `v` is a tuple. `None` becomes the text `None`. | Export `[[None]]` and `[[(1, 2)]]`; assert the expected cell text. |
| F5 | P3 | `tests/test_exporter.py` | The only regression test covers commas. No test covers quotes, newlines, or the header. | Add the F2 test plus a value containing `\n`. |

**Suggested fix for F2:** replace the hand-rolled quoting with `csv.writer` over `io.StringIO`, or use `'"%s"' % str(v).replace('"', '""')`. This is UNVERIFIED against the consumer (csv.reader and a real spreadsheet), since I cannot run either.

**FILES NEEDED BUT NOT PROVIDED:** commit trailers, CI check results, and whether the report fields can contain customer-controlled text. For the fix commit 5d1e7a9, only the patch was seen, not the commit itself.

## Close-out

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | **Not accepted.** The comma case is fixed, and `test_comma_value` plausibly fails before the fix and passes after. However, Step 7 requires the fix's own diff to be read for new defects, and that read found F2. A fix that introduces a defect is a new finding, not an acceptance. | 5d1e7a9; `exporter.py:9` |
| F2 | Open. A P1 cannot be deferred. | Needs a fix and a regression test |
| F3 | Open. May be deferred (P2) only with a tracking issue link, or fixed. | No issue linked |
| F4, F5 | Open. May be deferred (P3) with an issue link. | None |

**VERIFIED AFTER FIXES:** The head moved from 1c7f9a2 to 5d1e7a9, changing `exporter.py:9` and the test file. I verified this by reading the patch only. Nothing was run, and the test claim "fails on the first commit, passes now" is plausible by reading but not observed.

**MERGE RECOMMENDATION: merge after fixes.** F2 is an unresolved P1 introduced by the fix. Escape embedded quotes (or switch to `csv.writer`), add the quote test, then do a targeted read of that correction diff, not a full round. Also open: no CI results were provided (a missing check is not green), F3 needs an owner decision or issue, and the tier needs confirming if personal data is in the report. The author's "Ready to close out" does not hold.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "reasoned from code, not executed",
      "location": "exporter.py:9 (fix.patch, commit 5d1e7a9)",
      "scenario": "Values containing a double quote are wrapped in quotes without doubling the embedded quote, e.g. 5\" pipe becomes \"5\" pipe\". The spreadsheet misparses the row, shifting or merging fields.",
      "fix": "Escape quotes as \"\" (str(v).replace('\"','\"\"')) or use csv.writer over io.StringIO. Add a test exporting 'say \"hi\"' and reading it back with csv.reader."
    },
    {
      "severity": "P2",
      "evidence_level": "reasoned; depends on whether fields can hold customer-controlled text",
      "location": "exporter.py:9",
      "scenario": "A value starting with =, +, - or @ is evaluated as a formula when a customer opens the export.",
      "fix": "Owner decision: neutralise leading formula characters (e.g. prefix with an apostrophe), or defer with a tracking issue."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned from code, not executed",
      "location": "exporter.py:9",
      "scenario": "'\"%s\"' % v raises TypeError or misformats for tuple values; None is exported as the text None.",
      "fix": "Convert with str(v) first and decide explicit handling for None; add tests."
    },
    {
      "severity": "P3",
      "evidence_level": "read of tests/test_exporter.py",
      "location": "tests/test_exporter.py",
      "scenario": "Tests cover only plain rows and commas; quotes, newlines and the header are untested.",
      "fix": "Add quote and newline regression tests."
    }
  ]
}
```