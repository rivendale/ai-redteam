# Close-out of PR #112: CSV export for the monthly report

**REVIEWED:** PR #112. The first round covered head `1c7f9a2` with merge base `40be8d1`. This close-out covers the correction in `work/fix.patch`, which the author names as commit `5d1e7a9`. I was not given a SHA for the patch, so I cannot confirm that `5d1e7a9` is exactly the patch content. The head has moved from `1c7f9a2` to `5d1e7a9`, and only the lines in `fix.patch` were reviewed after the first round.

**TIER:** Standard. This is an ordinary code change that formats customer-facing data. If the monthly report carries personal data, the tier becomes High and a second round is still owed. That depends on what the report contains, and the PR does not say.

**REVIEWERS:** The first round's reviewer is not named in `review_findings.md`. This close-out is by a separate Claude instance (claude-opus-5-5) that did not write the change or the fix. The author is not recorded, because no commit trailers were provided.

## Verification of the correction (targeted read of `fix.patch`)

- **The regression test is valid for F1.** On `1c7f9a2`, `export_rows([["ann","a,b"]])` gives `["ann,a,b"]`, which `csv.reader` reads as `["ann","a","b"]`, so `test_comma_value` fails. With the fix it gives `['"ann","a,b"']`, which reads back as `["ann","a,b"]`, so it passes. The F1 scenario is fixed.
- **The fix adds a new defect.** `'"%s"' % v` wraps each value in quotes but does not escape quotes already inside the value. CSV (RFC 4180) requires an embedded `"` to be written as `""`. A value containing a quote now produces a malformed field, and if it also contains a comma, the row splits again. That is exactly the F1 failure the fix was meant to close. See F2.
- **A secondary effect of `%` formatting.** If a value is a tuple, `'"%s"' % v` either raises `TypeError` or formats the wrong thing. The old `str(v)` handled tuples. This matters little for report values, but it is avoidable, and the fix for F2 removes it.

## FINDINGS (new in this close-out)

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F2 | P1 | exporter.py:10 (after fix) | Take a value with an embedded double quote, such as `say "hi", ok`. It is written as `"say "hi", ok"`. The quote before `hi` ends the field early, and the comma then splits it. Spreadsheet apps and `csv.reader` both read the wrong fields or wrong values. Customer free text such as notes will contain quotes. | `list(csv.reader(export_rows([["ann", 'say "hi", ok']])))` should equal `[["ann", 'say "hi", ok']]`. This fails today. |
| F3 | P2 | exporter.py:10 | Take a value starting with `=`, `+`, `-` or `@`, such as `=HYPERLINK("http://x","click")`. It is exported as is, and the customer's spreadsheet evaluates it as a formula (CSV/formula injection). This was already present before the fix. Its severity depends on whether report values can come from untrusted users. | `export_rows([["=1+1"]])` should neutralise the value, for example by prefixing `'`, according to a policy the owner decides. |

**Suggested fix for F2:** build each line with the standard library, for example a `csv.writer` over `io.StringIO` with `lineterminator=""`, or escape with `str(v).replace('"', '""')` before quoting. A side note on the request's "one line per row": a value containing a newline produces one quoted field that spans lines. That is valid CSV, but callers that join lines with `\n` must not split on it. Add a test for a value containing `\n`.

**FILES NEEDED BUT NOT PROVIDED:** the caller that writes the download (line terminator, encoding/BOM, header joining); CI results for `5d1e7a9`; the fix commit itself, to confirm it matches `fix.patch`.

## ADJUDICATION

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | **Not yet accepted** | The comma case is fixed and `test_comma_value` is a valid regression test (see verification above). However, the fix itself introduces F2, and under Step 7 that is a new finding, not an acceptance. F1 closes when F2 is fixed with its own test. |
| F2 | Open, P1, cannot be deferred | Author to fix and add the suggested test. |
| F3 | Open, P2 | Needs an owner decision: either fix it or defer it with a linked issue. |

**VERIFIED AFTER FIXES:** I read the `fix.patch` lines (exporter.py:9–10 and tests/test_exporter.py). I worked out the test outcomes by reading the code; I could not run them in this session. I saw no CI evidence, and a missing check is not a green check.

**MERGE RECOMMENDATION:** **Do not merge (merge after fixes).**
- F2 is an open P1.
- F3 needs an owner decision.
- The expected checks are not shown as green for the new head.
- Whether the tier is Standard or High depends on whether the report holds personal data, and that is still open.

```json
{
  "verdict": "do not merge (merge after fixes)",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "traced in code (not executed)",
      "location": "exporter.py:10",
      "scenario": "Fix wraps values in quotes without doubling embedded quotes; a value like `say \"hi\", ok` is emitted as `\"say \"hi\", ok\"`, which spreadsheets and csv.reader parse into wrong/split fields, reintroducing the F1 failure.",
      "fix": "Build lines with csv.writer over io.StringIO (lineterminator=\"\"), or escape with str(v).replace('\"','\"\"') before quoting; add test reading back [[\"ann\", 'say \"hi\", ok']] via csv.reader."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred (depends on whether report values are user-controlled)",
      "location": "exporter.py:10",
      "scenario": "Values starting with =, +, -, @ are exported verbatim and evaluated as formulas when customers open the CSV in a spreadsheet (CSV injection). Present before and after the fix.",
      "fix": "Owner decides a neutralisation policy (e.g. prefix ' to such values) and adds a test, or defers with a linked issue."
    }
  ]
}
```