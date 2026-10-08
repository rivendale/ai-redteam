# Close-out: PR #112, CSV export for the monthly report

**Review report (verification of the fix)**

REVIEWED: PR #112. The first round was at head `1c7f9a2`, merge base `40be8d1`. The fix commit `5d1e7a9` (work/fix.patch) moved the head after that round. This close-out covers only the fix diff, read in a targeted way as Step 6 requires. It is not a new full round.

TIER: The first round did not record one. I take **Standard**: this is ordinary code, but customers download the output and open it in spreadsheets. If the exported values include personal data or customer-entered text, the owner should decide whether it moves to High (see F3).

REVIEWERS: This session (Opus 5.5) did the close-out read. I did not write the change or the fix. The author can't be read from commit trailers because none were provided. Record the author before posting.

FINDINGS (new, from the fix read):

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F2 | P1 | exporter.py:10 | The fix wraps each value as `'"%s"' % v` but does not double embedded quotes. The value `say "hi"` is written as `"say "hi""`. `csv.reader` and spreadsheets then read it as `say hi""` or split/shift it, so the cell is corrupted. A value like `a",b` breaks the field count, which is exactly the failure F1 was about. RFC 4180 requires `"` inside a quoted field to be written as `""`. | `list(csv.reader(export_rows([["ann", 'say "hi"']]))) == [["ann", 'say "hi"']]`, and the same check with `'a",b'`. |
| F3 | P2 (owner decision) | exporter.py:10 | This was present before the fix and the first round missed it. A value starting with `=`, `+`, `-` or `@`, such as `=HYPERLINK("http://evil","x")`, is evaluated as a formula when the customer opens the file (CSV/formula injection). Quoting does not prevent this. Severity depends on whether report values can be entered by users or third parties, which I can't see. | Export `[["=1+1"]]` and assert the cell is neutralised, e.g. `'=1+1` or whatever policy the owner chooses. |
| F4 | P3 | exporter.py:10 | `'%s' % v` treats a tuple value as format arguments. A value `(1, 2)` raises `TypeError: not all arguments converted`. Before the fix, `str(v)` handled this. | `export_rows([[(1, 2)]])` does not raise. |

FILES NEEDED BUT NOT PROVIDED: the download handler that joins these lines, adds `header()`, and sets line endings and encoding. Also the CI check list and status for `5d1e7a9`, and where the report values come from (needed to settle F3).

**Close-out**

ADJUDICATION:

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | **Not accepted** | The regression test is valid. On `1c7f9a2`, `"ann,a,b"` reads as 3 fields, so it fails. On `5d1e7a9`, `"ann","a,b"` reads as 2 fields, so it passes. I checked this by reading the code, not by running it, because I have no tools here. But the fix's own diff introduces F2, and Step 7 says that makes it a new finding, not an acceptance. F1 stays open until F2 is fixed. |
| F2 | Open, P1, cannot be deferred | Recommended fix: write through the standard library rather than hand-quoting, e.g. `csv.writer(buf, lineterminator="")` per row with `io.StringIO`. Alternatively, `'"%s"' % str(v).replace('"', '""')`. Add the quote tests above. |
| F3 | Open, needs an owner decision | Either neutralise leading `= + - @` (and tab/CR), or document why the values are trusted. |
| F4 | Open, P3 | Using the `csv` module, or `str(v)` before formatting, fixes it. It can be deferred with an issue link. |

VERIFIED AFTER FIXES: Only `5d1e7a9` changed after the review: exporter.py:9–10 and tests/test_exporter.py. I verified it by reading the diff against csv quoting rules. The change to `test_plain_row` (comparing through `csv.reader`) is correct. `test_comma_value` is a real regression test for F1. The quoting itself is incomplete (F2). I could not run the tests in this session.

MERGE RECOMMENDATION: **Do not merge.** F1 is not resolved because its fix introduces F2 (P1), and a P1 cannot be deferred. The F3 decision is pending with the owner. No CI check status was provided for the new head, and a missing check is not green. Once the export moves to the `csv` module and has the quote tests, plus an F3 decision, a targeted read of that diff is enough to close this out. No new paid round is needed.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "verified by reading the fix diff against RFC 4180 / csv.reader quoting rules (not executed)",
      "location": "exporter.py:10",
      "scenario": "Fix quotes values with '\"%s\"' % v but does not double embedded quotes; value 'say \"hi\"' becomes '\"say \"hi\"\"' and value 'a\",b' splits fields, so customers' spreadsheets read corrupted or shifted cells. F1's fix introduces this defect, so F1 is not accepted.",
      "fix": "Write rows with csv.writer into io.StringIO (lineterminator=''), or escape with str(v).replace('\"', '\"\"'); add round-trip tests for values containing '\"' and '\",'."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred; depends on whether report values are user-controlled (source not provided)",
      "location": "exporter.py:10",
      "scenario": "A value starting with =, +, - or @ (e.g. =HYPERLINK(...)) is executed as a formula when the customer opens the CSV; quoting does not prevent it.",
      "fix": "Owner decides: prefix such values with a single quote (or otherwise neutralise), or document that values are trusted; add a test for '=1+1'."
    },
    {
      "severity": "P3",
      "evidence_level": "verified by reading Python %-formatting semantics (not executed)",
      "location": "exporter.py:10",
      "scenario": "A tuple value such as (1, 2) makes '\"%s\"' % v raise TypeError; the pre-fix str(v) handled it.",
      "fix": "Use the csv module or format str(v); test export_rows([[(1, 2)]]) does not raise."
    }
  ]
}
```