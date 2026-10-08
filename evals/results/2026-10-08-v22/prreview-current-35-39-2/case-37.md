# Close-out of PR #112: CSV export for the monthly report

**I can't close this PR out.** The fix in 5d1e7a9 doesn't resolve F1. It wraps each value in quotes but doesn't escape quotes inside the value. A value that contains `",` still splits into extra columns, and a value that contains a quote is read back wrong. F1 is a P1, so it can't be deferred.

I had no tools in this session. Everything below comes from reading the diffs and tracing Python's `csv` module by hand. Nothing was run.

## Scope of this close-out

- **Reviewed (first round):** PR #112, head `1c7f9a2`, merge base `40be8d1`, per `work/review_findings.md`.
- **Correction verified here:** `work/fix.patch`, presented as commit `5d1e7a9` on top of `1c7f9a2`. Per Step 6, I verified it by reading the correction diff, not by another full review. The head moved from `1c7f9a2` to `5d1e7a9`, and the only commit not covered by the first round is `5d1e7a9`, which this close-out reads.
- **Tier:** The first review recorded none. I'd call this **Standard**: it's ordinary code, but the output goes to customers. It becomes **High** if the monthly report carries personal data. The PR doesn't say what the rows contain, and the owner should confirm. If it's High, the second round hasn't run.
- **Authorship:** No commit trailers were provided, so who wrote the change is unrecorded. The first-round reviewer isn't named either. This session didn't write the change.

## Verifying the fix against F1

F1 says a value containing a comma splits into two columns. The fix changes `exporter.py:10` to:

```python
return [",".join('"%s"' % v for v in row) for row in rows]
```

**What the new test covers.** `test_comma_value` passes after the fix and fails before it:

- After the fix, the output is `"ann","a,b"`, which reads back as `["ann", "a,b"]`.
- Before the fix, the output is `ann,a,b`, which reads back as `["ann", "a", "b"]`.

So the regression test does what the adjudication claims, for the one input it tests.

**What it misses.** CSV (RFC 4180, and Python's default `csv` dialect with `doublequote=True`) requires a quote inside a quoted field to be doubled. The fix doesn't double it:

- `['ann', 'a",b']` becomes `"ann","a",b"`. `csv.reader` returns `['ann', 'a', 'b"']`: three fields instead of two. This is exactly F1's failure, still present.
- `['ann', 'say "hi"']` becomes `"ann","say "hi""`. This reads back as a corrupted value (roughly `say hi""` in non-strict mode). Spreadsheets mis-split it in similar ways.

Customer data such as names, notes and free text routinely contains quotes, so this is likely in real use. The fix narrows F1 but doesn't close it.

## Findings from verifying the fix

These are new findings. The author adjudicates them; I don't.

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F2 | P1 | `exporter.py:10` (after 5d1e7a9) | A value containing a double quote is wrapped in quotes without the inner quote being doubled. `'a",b'` exports as `"a",b"`, which reads back as two fields (`a`, `b"`). `say "hi"` reads back corrupted. The customer's spreadsheet gets shifted or wrong columns. This is F1's failure through a different input. | `list(csv.reader(export_rows([["ann", 'a",b'], ["bob", 'say "hi"']])))` should equal `[["ann", 'a",b'], ["bob", 'say "hi"']]`. Fails today. |
| F3 | P3 | `exporter.py:10` (after 5d1e7a9) | The fix replaced `str(v)` with `'"%s"' % v`. If a value is a tuple, `%` treats it as the argument list: `(1, 2)` raises `TypeError: not all arguments converted`, and `(1,)` exports `1` instead of `(1,)`. `str(v)` handled both. This only matters if rows can hold tuples. | `export_rows([["ann", (1, 2)]])` should not raise, and should read back as `["ann", "(1, 2)"]`. |

**Suggested fix for both:** build the lines with the `csv` module rather than by hand. Write each row with `csv.writer(buf, lineterminator="")` into an `io.StringIO` and return `buf.getvalue()`, or use `quoting=csv.QUOTE_ALL` to keep every value quoted. This doubles inner quotes, handles embedded newlines, and calls `str()` on each value.

**Two open questions for the owner.** These aren't findings, because the request doesn't settle them:

- **Embedded newlines.** The request says "one line per row". A value containing a newline is correct CSV once quoted, but it spans two physical lines. The owner should decide whether that's acceptable or whether newlines should be replaced. This affects how the returned "lines" are joined for download.
- **Formula injection.** Customers open this file in spreadsheets. A value beginning with `=`, `+`, `-` or `@` (for example `=HYPERLINK(...)`) is executed as a formula by Excel and LibreOffice. Whether to neutralise these, for example with a leading `'`, is a security or product decision that should be made before this ships to customers. It was present before the fix and isn't introduced by it.

## Close-out

**ADJUDICATION**

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | Accepted, but **the fix is incomplete** | 5d1e7a9 fixes the tested input (`"a,b"`), and `test_comma_value` fails before the fix and passes after it. The same failure still occurs for `'a",b'` (see F2). F1 can only be closed together with F2. |
| F2 | Pending (author) | New finding, P1, so it can't be deferred. |
| F3 | Pending (author) | New finding, P3. Fixed by the same change as F2 if the `csv` module is used. |

**VERIFIED AFTER FIXES:** 5d1e7a9 changes `exporter.py:9-10` (docstring and the join expression) and `tests/test_exporter.py`:

- It adds `import csv`.
- It rewrites `test_plain_row` to read the output back with `csv.reader`. This is equivalent to the old test, and the new output `"ann","ok"` reads back correctly.
- It adds `test_comma_value`.

I traced both tests by hand and didn't run them. No CI results were provided, so I have no evidence that any check is present or green.

**MERGE RECOMMENDATION:** **Do not merge at `5d1e7a9`. Merge after fixes.** Before merging:

1. Fix F2 (P1), ideally with the `csv` module, which also fixes F3. Add the F2 test as a regression test.
2. Confirm the tier: is personal data in the report? If so, it's High and a second round is required.
3. Make the owner decisions on embedded newlines and formula injection.
4. Get the expected CI checks present and green on the new head.
5. Record the authorship trailers.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "traced by hand against Python csv default dialect (doublequote=True); not executed",
      "location": "exporter.py:10 (after 5d1e7a9)",
      "scenario": "Fix wraps values in quotes without doubling inner quotes. Value 'a\",b' exports as \"a\",b\" and csv.reader returns ['a', 'b\"'] (extra column, F1's failure remains); value 'say \"hi\"' reads back corrupted. Customer spreadsheets get shifted or wrong columns.",
      "fix": "Build each line with csv.writer (io.StringIO, lineterminator='', optionally quoting=csv.QUOTE_ALL); add a test round-tripping [['ann','a\",b'],['bob','say \"hi\"']] through csv.reader."
    },
    {
      "severity": "P3",
      "evidence_level": "code reading of Python %-formatting semantics; not executed",
      "location": "exporter.py:10 (after 5d1e7a9)",
      "scenario": "'\"%s\"' % v treats a tuple value as the argument tuple: (1, 2) raises TypeError, and (1,) exports '1'. The previous str(v) handled both. Only matters if rows can contain tuples.",
      "fix": "Use csv.writer (which calls str on values) or '\"%s\"' % (v,); add a test with a tuple value."
    }
  ]
}
```