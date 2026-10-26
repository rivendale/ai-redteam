# PR #112 close-out: CSV export for the monthly report

**The author's fix cannot be accepted. Do not merge yet.** The fix closes the comma case from F1 but adds a new P1: values that contain a double quote now come out corrupted.

I have no tools in this session, so I verified everything below by reading the patches. I ran no tests and could not post to the PR.

## Review report (verification of the fix)

**Reviewed:**
- PR #112, originally at head `1c7f9a2`, merge base `40be8d1`.
- The fix commit `5d1e7a9` moves the head. I gave `5d1e7a9` only the targeted read of `fix.patch` that Step 6 and Step 7 call for, not a full review.

**Tier:** Standard. This is an ordinary code change. It does not touch auth, secrets, migrations, money or personal-data handling. Customers do download the export, which raises the cost of a wrong file but does not move the tier. The first-round report did not record a tier. Standard means one round, and that round has run.

**Reviewers:**
- Round 1: reviewer not named in `review_findings.md`.
- Fix verification: this instance (claude-opus-5-5). It did not write the change or the fix.
- Author: not recorded. No commit trailers were provided, so authorship can't be read from them. That is a gap for the record.

**Findings from the targeted read of the fix:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| N1 | P1 | `exporter.py:10` (after the fix) | The fix wraps each value in quotes but does not double the quotes inside it, which CSV requires. For example, `say "hi"` is written as `"say "hi""`. Python's `csv.reader` reads that back as `say hi""`, and spreadsheets mis-parse it in a similar way. The customer's file then has a corrupted cell, and the columns can shift. | `csv.reader(export_rows([["ann", 'say "hi"']]))` should equal `[["ann", 'say "hi"']]`. This fails at `5d1e7a9`. |
| N2 | P3 | `exporter.py:10` (after the fix) | The fix replaced `str(v)` with `'"%s"' % v`. If a value is a tuple, `%` treats it as a list of format arguments. `(1, 2)` raises `TypeError` and `(1,)` prints as `1`. The old code turned both into a string correctly. | Export `[[(1, 2)]]` and expect one cell `"(1, 2)"` with no exception. |

**Files needed but not provided:** CI or check results for `5d1e7a9`.

## Close-out

**Adjudication:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | Not accepted yet | The comma case is fixed in `5d1e7a9`. By reading: the first commit writes `ann,a,b`, which reads back as three fields, so `test_comma_value` fails there. The fix writes `"ann","a,b"`, which reads back as `["ann","a,b"]`, so it passes. That matches the author's claim. However, Step 7 says a fix that introduces a defect is a new finding, not an acceptance, and this fix introduces N1. F1 closes once N1 is fixed. |
| N1 | Open (P1, cannot be deferred) | Suggested fix: write rows with the standard library's `csv.writer` into an `io.StringIO`, which quotes and escapes correctly. The smallest alternative is `'"%s"' % str(v).replace('"', '""')`. Add the quote round-trip test above. |
| N2 | Open (P3) | This is resolved by the same fix, because `csv.writer` or `str(v)` handle tuples. Otherwise it can be deferred with a linked issue. |

**Verified after fixes:**
- `exporter.py`: I read the change from `str(v)` joins to `'"%s"' % v`. That read found N1 and N2.
- `tests/test_exporter.py`: `test_plain_row` now checks a `csv.reader` round trip instead of the exact string, which is acceptable. `test_comma_value` was added, and its fail-then-pass behaviour is confirmed by reading, not by running it.

**Outside the bounded scope (owner decision):** the export goes into customers' spreadsheets. A cell that starts with `=`, `+`, `-` or `@` will be run as a formula, which is CSV formula injection. The request did not ask for protection against this, and neither the first round nor this read covered it. The owner should decide whether this PR needs it or whether it gets a tracked issue.

**Merge recommendation: merge after fixes.** These items are still open:
1. Fix N1 and add its regression test. Then give that fix diff a targeted read for new defects.
2. Close N2 with the same fix, or defer it with a linked issue.
3. Produce a check run for the final head. No CI results were provided, and a missing check is not green.
4. Record the authorship and the first-round reviewer.
5. Get the owner's decision on formula injection.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "static read of fix.patch; csv.reader behaviour reasoned, not executed",
      "location": "exporter.py:10",
      "scenario": "The fix quotes each value but does not double the quotes inside it. The value say \"hi\" is written as \"say \"hi\"\" and reads back corrupted (csv.reader gives say hi\"\"), so the customer's spreadsheet cell is wrong.",
      "fix": "Use csv.writer with io.StringIO, or escape with str(v).replace('\"','\"\"') before quoting. Add a round-trip test for [[\"ann\", 'say \"hi\"']]."
    },
    {
      "severity": "P3",
      "evidence_level": "static read of fix.patch",
      "location": "exporter.py:10",
      "scenario": "'\"%s\"' % v treats a tuple value as format arguments: (1, 2) raises TypeError and (1,) prints as 1. The original str(v) handled both.",
      "fix": "Format with str(v) or use csv.writer. Add a test exporting [[(1, 2)]]."
    }
  ]
}
```