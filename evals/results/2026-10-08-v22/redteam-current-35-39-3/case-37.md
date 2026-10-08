# Close-out review of PR #112: CSV export (fix 5d1e7a9)

**VERDICT: REWORK** (of the fix, not the whole PR). The fix wraps values in quotes but does not escape quote characters inside them. A value containing `"` still corrupts the row, and a value containing both `"` and `,` still splits into extra columns, which is the same failure F1 reported. F1 is therefore not closed.

**CONFIDENCE: medium.** Three things limit it:
- No tools were available, so code behaviour was traced by hand against Python's `csv` reader rules, not run.
- No fresh subagent or other reviewer was available. The work was not written in this conversation, so anchoring risk is lower than usual. Re-run in a fresh session with tools before relying on this for anything high-stakes.
- The code that calls `export_rows` and writes the download was not supplied.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| request.md, context.md, PR.md, review_findings.md, adjudication.md | Seen | — |
| base/exporter.py, base/README.md, change.patch, fix.patch | Seen | — |
| Commit 5d1e7a9 itself (only fix.patch was supplied as standing in for it) | Not seen | Low. Assumed identical; worth a `git diff` check. |
| The download handler: how lines are joined, line terminator, encoding/BOM, where the header is added | Not seen | Yes, for findings 3 and 4 and for "opens correctly in a spreadsheet". |
| Where row values come from (customer- or user-entered free text?) | Not seen | Yes, it sets the severity of findings 1 and 2. |
| CI or test output showing `test_comma_value` red then green | Not seen | Medium. The claim was checked by hand-trace only. |

**SEATS AND GATE**
- Seats: one same-session reviewer ran. No subagent or cross-vendor seats were available because this session has no tools.
- Gate: the material is an invented sample repository with no personal or confidential data, so the gate passed. Unused, because no external seats existed.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | High | PROBABLE (hand-traced against the `csv` reader's state machine; not run) | B | fix.patch → exporter.py:10, `'"%s"' % v` | Values are wrapped in quotes, but a quote inside a value is not doubled (CSV escapes `"` as `""`). The F1 failure class (wrong number of fields) survives the fix. | A note `say "hi", ok` is written as `"say "hi", ok"`. The reader closes the quoted field at the second `"`, then the `,` splits the value, so the row gains a column and later values shift. Customers open a spreadsheet with misaligned columns. | Use the standard library's `csv.writer`, writing each row into an in-memory buffer with `lineterminator=""`, or at least double every `"` inside a value. Add a round-trip test with `[["ann", 'say "hi", ok']]` that expects the identical row back. | Confirmed. Strongest defence: "no value ever contains a quote". Nothing in the request, PR or context says so, and a free-text `note` column makes quotes realistic. F1's adjudication as "fixed" therefore does not hold. |
| 2 | Medium | PROBABLE | B | Same line | Even without a comma, a quote inside a value is silently altered. | `say "hi"` is written as `"say "hi""` and reads back as `say hi""`: the value is changed without any error. | Same fix as finding 1. Add a test case with a value that contains quotes but no comma. | — |
| 3 | Medium | UNVERIFIED (depends on where values come from) | B / R | exporter.py:10, both versions | No defence against formula injection. A cell starting with `=`, `+`, `-` or `@` runs as a formula when a customer opens the file in a spreadsheet. | A user-entered name such as `=HYPERLINK("http://evil","click")` becomes a live link or formula in a customer's spreadsheet. This was already present before the fix and was missed by the first review. | Decide the policy explicitly. If values can contain user input, prefix risky leading characters with `'` and test that. | — |
| 4 | Low | UNVERIFIED | B | Caller (not supplied) | Quoting allows a newline inside a value, so one data row spans several physical lines. That is valid CSV, but the request says "one line per row", and any consumer that splits the output on newlines will break. | A note containing a line break produces two physical lines for one row. A downstream line-based import or row count is then wrong. | Decide: either keep valid embedded newlines and confirm the caller writes the whole buffer as one file, or replace newlines in values. Add a test for it. | — |
| 5 | Low | PROBABLE | B | exporter.py:10, `'"%s"' % v` | `%` formatting treats a tuple specially. | If `v` is a tuple, it raises `TypeError` or formats wrongly, where the original `str(v)` would not. | `csv.writer` (finding 1's fix) removes this. | — |

## What holds up
- **F1's literal case is fixed.** By trace, `[["ann", "a,b"]]` becomes `"ann","a,b"`, which `csv.reader` reads back as `["ann", "a,b"]`.
- **The adjudication's regression-test claim is consistent.** On the first commit the output was `ann,a,b`, which reads back as three fields, so the test fails there and passes after the fix.
- **The rewritten `test_plain_row` was not weakened.** Comparing the read-back result instead of the exact string is the right check for CSV.
- **The header `name,note` needs no quoting.**

## Unverified claims
- **"Fails on the first commit and passes now"**: settle it by running `python -m unittest` at 1c7f9a2 plus the new test, then at 5d1e7a9.
- **That 5d1e7a9 equals fix.patch**: settle it with `git diff 1c7f9a2 5d1e7a9`.
- **"Opens correctly in a spreadsheet"**: depends on the unseen download handler (encoding, BOM, line terminator). Settle it by reading the handler.

## Questions for the author
1. Can `name` or `note` contain user- or customer-entered text, and so quotes or text starting with `=`?
2. Which code joins these lines into the download, and with what line terminator and encoding?

## Decision-maker summary
Do not close out PR #112 yet. The fix covers the exact example the first review gave but not the general problem: any value containing a quote character still corrupts or shifts columns in customers' spreadsheets. Switching to Python's built-in CSV writer and adding one test with a quote in a value closes it. Shipping as is risks wrong exported data for any customer whose notes contain quotes.

## Owner summary
The fix for the report download handles commas inside values but not quotation marks. Text containing a quote mark can still end up altered or in the wrong spreadsheet column for customers. It is a small, well-understood change to finish, and it should be done before the work is signed off.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "download handler / caller of export_rows", "status": "not_seen", "matters": true},
    {"item": "source of row values (user-entered?)", "status": "not_seen", "matters": true},
    {"item": "commit 5d1e7a9 (fix.patch assumed identical)", "status": "not_seen", "matters": false},
    {"item": "test run output", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "invented sample repository; no personal or confidential data"},
  "findings": [
    {"severity": "High", "evidence_level": "PROBABLE", "track": "B", "location": "exporter.py:10 (fix.patch)",
     "scenario": "A value containing a double quote and a comma, e.g. 'say \"hi\", ok', is written as \"say \"hi\", ok\" without escaping the inner quotes; the reader ends the field early and splits on the comma, so the row has extra fields and columns shift in the customer's spreadsheet. F1 is not actually fixed.",
     "fix": "Use csv.writer (e.g. on an in-memory buffer) or double embedded quotes; add a round-trip test with a value containing both a quote and a comma.",
     "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "exporter.py:10 (fix.patch)",
     "scenario": "A value 'say \"hi\"' is written as \"say \"hi\"\" and read back as 'say hi\"\"', silently altering customer data.",
     "fix": "Same as the High finding; add a test with a value containing quotes but no comma."},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "R", "location": "exporter.py:10",
     "scenario": "A user-entered value starting with = + - @ becomes a live formula when a customer opens the export (CSV formula injection).",
     "fix": "Decide a policy; if values can come from users, prefix risky leading characters with an apostrophe and test it."},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "track": "B", "location": "caller of export_rows (not supplied)",
     "scenario": "A value containing a newline makes one row span several physical lines, contrary to 'one line per row'; any line-based consumer miscounts rows.",
     "fix": "Decide whether to allow quoted embedded newlines or replace them; add a test."},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "B", "location": "exporter.py:10 (fix.patch)",
     "scenario": "'\"%s\"' % v raises TypeError or misformats if a value is a tuple, unlike the original str(v).",
     "fix": "Removed by switching to csv.writer."}
  ]
}
```