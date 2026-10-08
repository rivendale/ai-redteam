# Close-out of PR #112: CSV export for the monthly report

**The fix for F1 adds a new P1, so this PR is not ready to close.** Every value is now wrapped in double quotes, but double quotes inside a value are not escaped. Any value containing `"` produces a broken row in the customers' spreadsheets.

## Review report (fix verification)

**REVIEWED:** PR #112, merge base 40be8d1. The first round covered head 1c7f9a2. I did a targeted read of fix commit 5d1e7a9 (`work/fix.patch`) on top of `work/change.patch`, with `work/base/` as the before state. I had no tools, so I could not check out the head or run anything.

**TIER: High, not Standard.** The rows include a `name` column (`header()` returns `"name,note"`), and the output is downloaded by customers. That is personal-data handling. When unsure, the skill says to take the higher tier. The first review records no tier and ran one round, so the second round High requires has not run. If the owner confirms the export carries no personal data, Standard applies and one round is enough. That is an owner decision, and it is still open.

**REVIEWERS:** This close-out was done by a separate instance (Opus 5.5) that did not write the change or the fix. The first-round reviewer is not named in `review_findings.md`. I could not establish authorship because no commit trailers were provided.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F2 | P1 | exporter.py:10 (fix 5d1e7a9) | `'"%s"' % v` quotes the value but does not double any `"` inside it. The note `say "hi"` becomes `"say "hi""`. CSV parsers read a quote inside a quoted field as the end of the field, so the cell comes out as `say hi""` or similar, or fields get merged or shifted. This is the same failure class F1 was meant to fix: the row no longer opens correctly. Spreadsheets will also mangle it. Free-text notes such as `6" pipe` or quoted speech will hit this. | `list(csv.reader(export_rows([["ann", 'say "hi"']])))` should equal `[["ann", 'say "hi"']]`. Fails today. |
| F3 | P3 | exporter.py:10 (fix 5d1e7a9) | `%` formatting treats a tuple value as format arguments. `(1, 2)` raises `TypeError: not all arguments converted`, and `(1,)` silently becomes `1`. The original `str(v)` handled both. This only matters if a value can be a tuple, which the inputs don't show. | `export_rows([["ann", (1, 2)]])` should not raise and should round-trip as `"(1, 2)"`. |

**Suggested fix for both:** use the standard library writer instead of hand-built quoting. Write each row with `csv.writer(buf, quoting=csv.QUOTE_ALL, lineterminator="")` into an `io.StringIO` and return `buf.getvalue()` per row. That doubles embedded quotes, calls `str()` on values, and handles commas and newlines.

**Also noted, not part of this PR's defect list:** values starting with `=`, `+`, `-` or `@` will run as formulas when customers open the file (CSV/formula injection). This exists both before and after the fix. Whether it is in scope depends on who controls `name` and `note`. It is a question for the owner, not a finding against the fix.

**FILES NEEDED BUT NOT PROVIDED:**
- The caller that joins these lines and writes the download: line separator and encoding (a BOM matters for Excel and non-ASCII names).
- CI check results for 5d1e7a9.
- Commit trailers.

## Close-out

### ADJUDICATION

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | **Not accepted as fixed.** | The regression test is valid. On 1c7f9a2, `"ann,a,b"` parses to three fields, so `test_comma_value` fails there and passes after the fix. But reading the fix's own diff shows a new defect (F2), and a fix that introduces a defect is a new finding, not an acceptance. F1 stays open until F2 is fixed. |
| F2 | Open (P1, cannot be deferred) | Needs a fix commit and the test above. |
| F3 | Open (P3) | Fix it along with F2 (the `csv.writer` change covers both), or defer it with a linked issue. |

**VERIFIED AFTER FIXES:** I read 5d1e7a9 line by line:
- `exporter.py:9-10`: the docstring and the quoting change. The quoting change is defective (F2, F3).
- `tests/test_exporter.py`: adds `import csv`, rewrites `test_plain_row` to parse with `csv.reader` (it still passes, because `"ann","ok"` parses to `["ann","ok"]`), and adds `test_comma_value`.

I ran no tests, so the "fails before, passes after" claim is confirmed by reading, not by execution.

**MERGE RECOMMENDATION: do not merge.** Open items:
1. F2 is an unresolved P1.
2. The tier is undecided. If it is High, the second round has not run.
3. CI check status for the current head is unknown, and a missing check is not green.
4. Formula injection needs an owner scope decision.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "code read (not executed)",
      "location": "exporter.py:10",
      "scenario": "Fix 5d1e7a9 wraps values in double quotes without doubling embedded quotes; a value like 'say \"hi\"' becomes \"say \"hi\"\" and is parsed into the wrong cell content or shifted fields when customers open the CSV.",
      "fix": "Write rows with csv.writer (quoting=csv.QUOTE_ALL, lineterminator='') into io.StringIO; add test that csv.reader round-trips [['ann', 'say \"hi\"']]."
    },
    {
      "severity": "P3",
      "evidence_level": "code read (not executed)",
      "location": "exporter.py:10",
      "scenario": "'\"%s\"' % v with a tuple value raises TypeError (len>1) or drops the tuple wrapper (len 1); the original str(v) handled it.",
      "fix": "Same csv.writer change (stringifies values); add test exporting a tuple value."
    }
  ]
}
```