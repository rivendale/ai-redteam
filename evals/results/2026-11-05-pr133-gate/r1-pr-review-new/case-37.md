# PR #112 close-out review

## Review report

**REVIEWED:** PR #112, head 1c7f9a2, merge base 40be8d1. The fix is reviewed as `work/fix.patch` on top of `work/change.patch`. Commit 5d1e7a9, which the author cites, was not provided, so I cannot confirm it matches the patch. The PR head named in PR.md (1c7f9a2) predates the fix. Everything below is from reading the patches, since I could not run code.

**TIER:** Standard. This is ordinary code with no auth, secrets, money or migration. If the monthly report rows carry personal data, the tier becomes High and a second round on another vendor is required. The inputs don't say. No data leaves this session beyond the supplied patches.

**REVIEWERS:** This session is a fresh instance with no part in writing the change. Authorship is unknown because no commit trailers were supplied. The first round is `review_findings.md`, and its reviewer is not identified.

**Targeted read of the fix diff (Step 7):** The fix makes the comma case work, so F1's original scenario is resolved by inspection. `'"%s"' % v` wraps every value in quotes without escaping a `"` inside the value. That is a new defect.

### Findings

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F2 (new, introduced by the fix) | P1 | `exporter.py:10` | The row `["ann", 'say "hi"']` becomes `"ann","say "hi""`. The quote inside the value ends the field early, so the file is malformed CSV. A spreadsheet or `csv.reader` mis-parses the field and the text is corrupted. Any note containing a double quote triggers it. | Export `[["ann", 'say "hi"']]`, read it back with `csv.reader`, and expect `[["ann", 'say "hi"']]`. It fails today. |
| F3 | P2 | `exporter.py:10` | A value starting with `=`, `+`, `-` or `@` (for example `=HYPERLINK("http://x","click")`) is quoted but still evaluated as a formula when a customer opens the file in a spreadsheet. Quoting does not prevent this. | Export a value `=1+1` and expect the output cell to carry a neutralizing prefix (for example `'`) and read back as text. |
| F4 | P3 | `exporter.py:10` | A value containing a newline produces one row spanning two physical lines. This is valid CSV when quoted, but it contradicts the request's "one line per row". | Export `[["a", "x\ny"]]` and assert the chosen behavior: either newlines are replaced, or the requirement is documented as quoted multi-line fields. |

F3 and F4 depend on a product decision (neutralize formulas, and what to do with newlines). They are not proven failures of the stated request, so they are lower confidence than F2.

**Suggested fix for F2 (UNVERIFIED, not run):** build the line with `csv.writer` on an `io.StringIO` using `QUOTE_MINIMAL`, or at minimum escape `"` as `""` before quoting. Check it against the F2 round-trip test above, which is the consumer of this output. The test file should use `csv.reader` round trips, as the author's new tests already do.

**Claims I could not verify:** the author says `test_comma_value` fails on the first commit and passes now. By inspection that is plausible: the old output `ann,a,b` reads back as three fields, so the test fails. I did not run it. The author's `test_plain_row` rewrite is fine.

**FILES NEEDED BUT NOT PROVIDED:** commit 5d1e7a9 itself, to confirm it equals `fix.patch`. CI or check status, which was not supplied and so counts as not green.

## Close-out

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | Not accepted yet. The author's "Accepted" cannot stand. | The comma case is fixed in `fix.patch`, with a test. Step 7 requires the fix's own diff to be free of new defects, and it introduces F2. |
| F2 | Open, awaiting the author's decision. A P1 cannot be deferred. | Needs a fix and a regression test. |
| F3 | Open, awaiting the author's decision. It may be deferred with a tracking issue, or fixed. | No issue link yet. |
| F4 | Open, awaiting the author's decision. It may be deferred with a tracking issue, or fixed. | No issue link yet. |

**VERIFIED AFTER FIXES:** The lines changed since the review are `exporter.py:9-10` and `tests/test_exporter.py`. I verified them by targeted reading only, not by running them. That read found F2.

**MERGE RECOMMENDATION:** Merge after fixes. F2 is an unresolved P1, F1 is not properly accepted, and no check status was provided. No written rule was supplied, so I cite none. Once F2 is fixed with a failing-then-passing regression test, a targeted read of that diff should be enough to close F1 and F2. F3 and F4 need an owner decision. The export goes straight into customers' spreadsheets, so I would not defer F3 without a tracking issue.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "read from the diff, not run",
      "location": "exporter.py:10",
      "scenario": "Fix wraps each value in quotes without escaping embedded double quotes. Row [\"ann\", 'say \"hi\"'] becomes \"ann\",\"say \"hi\"\"; the field is malformed and the text is corrupted when a spreadsheet or csv.reader parses it.",
      "fix": "Use csv.writer on io.StringIO (QUOTE_MINIMAL), or escape \" as \"\"; add a csv.reader round-trip test for a value containing a double quote."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred from known spreadsheet behavior, needs product decision",
      "location": "exporter.py:10",
      "scenario": "A value beginning with =, +, - or @ is evaluated as a formula when a customer opens the export in a spreadsheet; quoting does not prevent it.",
      "fix": "Prefix such values with ' (or equivalent) and test that they read back as text, or record an explicit decision not to."
    },
    {
      "severity": "P3",
      "evidence_level": "read from the diff, not run",
      "location": "exporter.py:10",
      "scenario": "A value containing a newline yields a row that spans two physical lines, contradicting 'one line per row' in the request.",
      "fix": "Decide between replacing newlines or documenting quoted multi-line fields, and add a test for the chosen behavior."
    }
  ]
}
```