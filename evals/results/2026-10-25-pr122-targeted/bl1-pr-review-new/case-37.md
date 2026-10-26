# PR #112 close-out: CSV export for the monthly report

The fix fixes values with commas but breaks values that contain a double quote. **Do not merge at the fixed head.** The work from here is a small fix and one more targeted read, not another review round.

I had no tools in this session. Nothing was run, and every test result below comes from reading the code by hand.

**Review report reference**

- **Reviewed:** PR #112, head `1c7f9a2`, merge base `40be8d1`, from `work/review_findings.md`.
- **Head moved:** the fix commit `5d1e7a9` (`work/fix.patch`) changes `exporter.py` (`export_rows`) and `tests/test_exporter.py`. I checked it by a targeted read, as Step 6 requires, not by a full review. Any commits after `5d1e7a9` are not covered.
- **Tier:** the first review did not record one. It is **Standard** if the monthly report holds no personal data. Customers download the export, though, so if the rows can carry personal data the tier is **High** and a second round is needed. That is an owner decision and it is still open.
- **Reviewers:** the first round's reviewer is not recorded. This close-out is by Claude (claude-opus-5-5), in a fresh session with no part in writing the change.
- **Author:** unknown, because no commit trailers were provided.

## Checking the fix for F1

**Fix:** `'"%s"' % v` wraps every value in double quotes.

**Regression test, read by hand against `csv.reader`, which is what the test uses to read the output:**
- On `1c7f9a2`, the row comes out as `ann,a,b`, which reads back as `["ann","a","b"]`. The test **fails**.
- On `5d1e7a9`, the row comes out as `"ann","a,b"`, which reads back as `["ann","a,b"]`. The test **passes**.
- `test_plain_row` gives `"ann","ok"`, which reads back as `["ann","ok"]`, so it passes. The assertion now compares parsed values instead of the exact string. That is fine for this purpose.

The author's claim about the test holds on reading. Reading the fix itself turns up a new defect.

## New finding from reading the fix

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F2 | P1 | `exporter.py:10` (fix `5d1e7a9`) | Double quotes inside a value are not escaped. Two examples: (1) `["ann", 'a",b']` is written as `"ann","a",b"`, so the row splits into an extra column. (2) `["ann", 'say "hi"']` is written as `"ann","say "hi""`; `csv.reader` returns `say hi""` and spreadsheets corrupt it the same way. Before the fix, case (2) read back correctly, so the fix introduced this. Any customer note containing a `"` will be corrupted in their spreadsheet. | `assertEqual(list(csv.reader(export_rows([["ann", 'say "hi"'], ["bo", 'a",b']]))), [["ann", 'say "hi"'], ["bo", 'a",b']])`. It fails today. |

**Suggested fix:** escape embedded quotes as `'"%s"' % str(v).replace('"', '""')`, or better, build the lines with `csv.writer(io.StringIO(), quoting=csv.QUOTE_ALL)`.

I checked this fix against the consumer: the default `csv.reader` dialect has `doublequote=True`, which reads `""` back as `"`. Whether the result passes the test above is still **UNVERIFIED** until someone runs it.

A smaller point: `'"%s"' % v` raises `TypeError` when `v` is a tuple with more than one element. Using `str(v)`, as the original code did, avoids that.

## Outside the adjudication scope (not a gate)

This was not raised by the first round, and the fix did not introduce it.

Values that start with `=`, `+`, `-` or `@` are written unchanged. A spreadsheet will run them as formulas (CSV/formula injection), and these files go to customers.

The owner should decide whether to handle it here or in a tracked issue. I am not adding it as a merge gate.

## Close-out

**ADJUDICATION**

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | Comma case fixed in `5d1e7a9`; `test_comma_value` fails before the fix and passes after (by reading). **Not accepted as complete**: the fix introduces F2. | Step 7: "A fix that introduces a defect is a new finding, not an acceptance." |
| F2 | Open, P1. Needs a fix and a regression test. | Cannot be deferred, because it is P1. |

**VERIFIED AFTER FIXES**

`5d1e7a9` changed `exporter.py:9-10` and `tests/test_exporter.py`. Both were checked by a targeted read against `csv.reader` parsing, which found F2. No tests were run. No CI check status was provided, and a missing check is not green.

**MERGE RECOMMENDATION: do not merge at `5d1e7a9`.**

Step 8 says: "no unresolved blocker remains". F2 is an unresolved P1.

To reach merge:
1. Fix F2 and add the test above.
2. Do a targeted read of that fix diff.
3. Get CI checks present and green.
4. Have the owner confirm the tier. If the report carries personal data, run the second round that the High tier requires.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "static reading of fix.patch against csv.reader default dialect; not executed",
      "location": "exporter.py:10 (fix 5d1e7a9)",
      "scenario": "Values containing a double quote are wrapped but not escaped: 'a\",b' becomes \"a\",b\" and splits into an extra column; 'say \"hi\"' parses as 'say hi\"\"'. Regression introduced by the F1 fix; customer spreadsheets get corrupted fields.",
      "fix": "Escape embedded quotes ('\"%s\"' % str(v).replace('\"', '\"\"')) or use csv.writer with QUOTE_ALL; add test round-tripping 'say \"hi\"' and 'a\",b' through csv.reader."
    },
    {
      "severity": "P3",
      "evidence_level": "static reading; not executed",
      "location": "exporter.py:10 (fix 5d1e7a9)",
      "scenario": "'\"%s\"' % v raises TypeError when a value is a tuple with more than one element; the original str(v) did not.",
      "fix": "Format str(v) instead of v."
    }
  ]
}
```