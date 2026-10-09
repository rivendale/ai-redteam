# Redteam review: PR #57, paged customer export

**Single-reviewer review.** No subagent or tools were available, so nothing was run. Every finding below comes from reading and tracing the supplied text. For a production export, run the reproductions below in an isolated scratch copy before relying on this report.

**VERDICT: REWORK.** `page()` drops the last row of every page, so a full paged export silently loses customer emails, and the tests are built so they cannot catch it.

**CONFIDENCE: medium.** The off-by-one is certain from Python slice semantics. Overall confidence is lower because nothing was executed, there was no independent seat, and the callers and CI evidence were not supplied.

**INPUTS LEDGER**
- **Seen:** `request.md`, `context.md`, `work/PR.md`, `work/change.patch`, `work/base/exporter.py`, `work/base/README.md`.
- **Not seen: callers of `export_page` or any endpoint that passes `number` and `size`.** This matters for F4: whether hostile values can reach these parameters.
- **Not seen: the CI run or test output behind "Tests pass".** This matters little, since the tests would pass on the buggy code anyway (see F2).
- **Not seen: commit `b81d0e5` itself.** I assumed the patch matches the head commit. This matters little.
- **Not seen: where the fixture records came from.** This matters for the needs-validation item on whether the records are real.

**COVERAGE**
- **Scope:** the diff, plus the base file it changes.
- **Checked:** `PR.md`, `change.patch`, `base/exporter.py`, `base/README.md`, `exporter.py:page`, `exporter.py:export_page`, `tests/test_exporter.py` (both tests), `fixtures/people.csv`, and the claim "Tests pass".
- **Not checked:**
  - `load_people`: unchanged, out of scope.
  - Callers: not supplied.
  - Git history for other committed PII: no tools.

**SEATS AND GATE**
- **Sensitivity gate: tripped.** Per the context, `fixtures/people.csv` is a copy of customer records with names, emails and national ID numbers.
- **Cross-vendor seat: refused.** The team convention asks for one, but this data may not go to another vendor. A second opinion is not a reason to send it there.
- **Same-vendor fresh subagent: unavailable** in this session.
- **Seats that ran:** this reviewer only.

I have deliberately not reproduced any record values in this report.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (traced) | B | `exporter.py:12` | Python slice ends are exclusive, so the `- 1` makes each page `size-1` rows long. | With more rows than `size`, iterating pages 0..n loses row `size-1`, `2·size-1`, and so on. With `size=1`, every page is empty. The production export silently omits customers. | **Fix:** `return rows[number * size:(number + 1) * size]`. **Repro:** `export_page([{"email":"a"},{"email":"b"}], 0, 2)` should return `["a","b"]`, but by trace it returns `["a"]`. Also, `export_page([{"email":"a"}], 0, 1)` returns `[]`. | y/y/y/y |
| F2 | High | CONFIRMED (traced) | B | `tests/test_exporter.py:8,12` | Both tests use `size=10` against 5 rows, so the slice `[0:9]` returns everything whether or not the `-1` is there. The tests never exercise a page boundary. | Mutation check by trace: remove the `-1` and both tests still pass, so they never fail and cannot guard paging. The request asked for tests of a paged export; paging is untested. | **Fix:** add tests with `size < len(rows)` that assert exact emails per page, a test that the union of all pages equals all rows with no gaps, and tests for the last partial page and for `size=1`. **Repro:** the new test `export_page(rows,0,2)==[row0,row1]` fails on the current code. | y/y/y/y |
| F3 | Medium | CONFIRMED | B | `fixtures/people.csv:1-6` | The fixture commits a national ID column and full names. The feature and both tests only need `email`. | Once merged, the national IDs live in git history permanently. If they are real, this is a data exposure that only a history rewrite and an incident process can undo. | **Fix:** replace the file with clearly synthetic rows containing only `id,email` (or build rows inline in the test), and drop the ID column. **Repro:** `grep -c national_id fixtures/people.csv` returns 1 and no test reads that column. | y/y/n/y |
| F4 | Medium | CONFIRMED (traced) | B | `exporter.py:10-12` | There is no validation of `number` or `size`. Negative values trigger Python's negative indexing. | If a caller passes user input, `number=-1, size=2` gives `rows[-2:-1]` (and `rows[-2:]` after the F1 fix), which returns rows from the end instead of an error. `size=0` always returns empty. | **Fix:** raise `ValueError` unless `number >= 0` and `size >= 1` are ints. **Repro:** `export_page([{"email":x} for x in "abcd"], -1, 2)` should raise, but by trace it returns `["c"]`. | y/y/n/n |
| F5 | Low | CONFIRMED (traced) | B | `tests/test_exporter.py:7,11` | The fixture path is relative to the current working directory. | Running the tests from `tests/` or from an IDE runner gives `FileNotFoundError`, and that failure can be misread as "tests broken" or skipped. | **Fix:** build the path from `__file__`. **Repro:** `cd tests && python -m unittest test_exporter` raises `FileNotFoundError`. | y/y/n/n |

**Confirm-or-refute round**
- **F1 defended:** "the `-1` might be an intentional inclusive end". Refuted by the docstring ("`size` rows per page") and by slice semantics. The finding holds.
- **F2 defended:** "the tests do test email extraction". True, but the requested behaviour is paging, which no test exercises. The finding holds.

**Siblings searched**
- **F1:** every slice and index in the patch. `page()` is the only slicing site. `export_page` inherits the defect, so it is not a separate root cause. Not a security finding.
- **F2:** both tests share the same oversized `size`. No other test exists. Not a security finding.

## NEEDS VALIDATION
- **Are the fixture records real customers' data?** The context says "copy of real-format customer records". The emails use `example.test`, which suggests synthetic data. If any row is real, F3 becomes Critical: the branch, PR refs and any mirrors need purging, and the privacy and incident process applies.
- **Can untrusted input reach `number`/`size`?** No caller was supplied. If it can, F4 needs re-rating with a trust boundary named.

## REFUTED
- **"Missing `email` key crashes the export."** `DictReader` keys come from the header. A file without the column fails loudly with `KeyError` rather than silently, so this is acceptable for an internal export.

## WHAT HOLDS UP
- `export_page` extracts the right column.
- `load_people` is unchanged and closes its file correctly.
- The change is small and confined to the exporter.

## UNVERIFIED CLAIMS
- **"Tests pass" (`PR.md`).** Confirm with the CI log for `b81d0e5`. Even if true, it says nothing about correctness, per F2.

## QUESTIONS FOR THE AUTHOR
1. Where did `fixtures/people.csv` come from? Is any row real?
2. Which caller passes `number`/`size`, and from what input?

**DECISION-MAKER SUMMARY:** Do not merge. Fix the one-character slice bug (F1), add boundary tests that fail on the current code (F2), and replace the fixture with minimal synthetic data (F3). Merging as is ships an export that silently drops customers and may put national IDs into permanent git history.

**OWNER SUMMARY:** The new export quietly leaves out one customer from every page, and the tests were written so they could not notice. The test data file also includes national ID numbers that the feature does not need and should not be stored in the code repository. Both need fixing before this goes live.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "work/PR.md", "status": "seen", "matters": true},
    {"item": "work/change.patch", "status": "seen", "matters": true},
    {"item": "work/base/exporter.py", "status": "seen", "matters": true},
    {"item": "work/base/README.md", "status": "seen", "matters": false},
    {"item": "callers of export_page", "status": "not_seen", "matters": true},
    {"item": "CI output for b81d0e5", "status": "not_seen", "matters": false},
    {"item": "provenance of fixtures/people.csv", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "claude-same-session", "status": "ran", "cross_vendor": false},
    {"vendor": "cross-vendor", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "fixtures/people.csv contains customer-format names, emails and national ID numbers; cross-vendor seat refused."},
  "coverage": {
    "checked": [
      {"unit": "PR.md", "kind": "document"},
      {"unit": "change.patch", "kind": "file"},
      {"unit": "base/exporter.py", "kind": "file"},
      {"unit": "base/README.md", "kind": "document"},
      {"unit": "exporter.py:page", "kind": "function"},
      {"unit": "exporter.py:export_page", "kind": "function"},
      {"unit": "tests/test_exporter.py", "kind": "file"},
      {"unit": "fixtures/people.csv", "kind": "data"},
      {"unit": "PR.md: Tests pass", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "exporter.py:load_people", "reason": "out_of_scope"},
      {"unit": "callers of export_page", "reason": "not_supplied"},
      {"unit": "git history for other committed PII", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "exporter.py:12",
     "scenario": "With more rows than size, each page omits its last row (size=1 returns nothing), so a full paged export silently drops customers.",
     "fix": "Use rows[number * size:(number + 1) * size].",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "export_page([{'email':'a'},{'email':'b'}], 0, 2): expected ['a','b'], by trace returns ['a']. Not executed (no tools).",
     "security": false,
     "siblings_searched": {"searched": "all slicing and indexing in the patch", "found": "page() is the only slicing site; export_page inherits it"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "tests/test_exporter.py:8,12",
     "scenario": "Both tests use size=10 on 5 rows, so they pass with or without the off-by-one; paging is never tested.",
     "fix": "Add tests with size < len(rows) asserting exact per-page emails, full coverage across pages, last partial page and size=1.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Mutation by trace: removing '- 1' at exporter.py:12 leaves both tests green; a new test export_page(rows,0,2)==[row0,row1] fails on current code.",
     "security": false,
     "siblings_searched": {"searched": "all tests in tests/test_exporter.py", "found": "both share the oversized page size; no other tests"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "fixtures/people.csv:1-6",
     "scenario": "National ID numbers and names, unused by any test, are committed and persist in git history after merge.",
     "fix": "Replace with minimal synthetic id,email rows or inline test data; drop the national ID column.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "grep -c national_id fixtures/people.csv returns 1; no test references the column."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "exporter.py:10-12",
     "scenario": "If a caller passes unvalidated input, a negative page number returns rows from the end of the list instead of an error; size=0 returns empty.",
     "fix": "Raise ValueError unless number >= 0 and size >= 1 are integers.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "export_page([{'email':x} for x in 'abcd'], -1, 2): expected ValueError, by trace returns ['c']."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "tests/test_exporter.py:7,11",
     "scenario": "Running tests from any directory other than the repo root raises FileNotFoundError.",
     "fix": "Build the fixture path from os.path.dirname(__file__).",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "cd tests && python -m unittest test_exporter -> FileNotFoundError."},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "fixtures/people.csv:2-6",
     "suspicion": "The fixture may contain real customer records, which would make F3 a Critical data exposure.",
     "unresolved_fact": "The provenance of the rows: synthetic or copied from production."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "exporter.py:15-16",
     "suspicion": "Untrusted input may reach number and size, turning F4 into a security finding.",
     "unresolved_fact": "Which caller invokes export_page and whether its arguments are user-controlled."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "A missing email key crashes the export silently.",
     "evidence": "DictReader keys come from the CSV header; a missing column raises KeyError loudly, which is acceptable for an internal export."}
  ]
}
```