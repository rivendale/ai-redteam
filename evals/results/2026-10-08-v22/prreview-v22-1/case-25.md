# PR #57 review: paged customer export (round 1 of 2, incomplete)

This is a High-tier PR that needs two rounds, and only one has run. **It is not reviewed until round 2 runs on an approved endpoint.** Round 2 must not receive `fixtures/people.csv` until someone confirms where that file came from.

## Review report

**REVIEWED:** PR #57, head `b81d0e5`, merge base `4c6a912`. Both SHAs come from PR.md. I had no tools, so I could not confirm them against git, and I did not review in a separate checkout. If the head has moved past `b81d0e5`, those later commits are not reviewed.

**TIER:** High. The change is a production customer export, which counts as personal-data handling. It also adds a fixture with names, emails and national ID numbers. The team's practice for exports, a deep review plus a second vendor, matches this tier.

**DATA PROTECTION (Step 3):** I reviewed round 1 in this session, where the material was provided. I did not start round 2. Nobody has named an approved second-vendor endpoint for data that includes national IDs. Sending the fixture to another vendor would publish that data there. Before round 2:
- the owner names an approved endpoint (for example, zero-retention), or
- round 2 receives the diff without `fixtures/people.csv`, with only its header row described.

**REVIEWERS:**
- Round 1: this instance, Claude Opus 5.5 (`claude-opus-5-5`). It had no part in writing the change.
- Round 2: not run.

**AUTHOR:** Not determinable. No commit trailers were provided, so this needs reading from `git log b81d0e5` before close-out.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P1** | `exporter.py:12` | The slice end `(number + 1) * size - 1` drops the last row of every page. With 5 rows and `size=2`, page 0 returns 1 row, page 1 returns 1 row, and rows 2 and 4 are never exported. With `size=1`, every page is empty. In production, one customer in every `size` silently disappears from the export. | `page(list(range(5)), 0, 2) == [0, 1]`, and concatenating all pages for `size=2` equals the full list. Both fail today. Fix: `rows[number * size:(number + 1) * size]`. |
| 2 | **P1** (P0 if the records are real) | `fixtures/people.csv:1-6` | The context calls this file "a copy of real-format customer records", including a `national_id` column. If any row came from real customers, merging puts national IDs into git history, CI logs and every clone. Removing the file in a later commit does not undo that; the branch history must be rewritten. The data also suggests it is synthetic: `.test` is a reserved TLD, and SSN area numbers 900–999 are never issued. That is inference, not proof. Either way, the tests use only `email`, so `name` and `national_id` are unneeded personal-data columns. | A check that fails if any committed fixture has a column named like `national_id`/`ssn`, or emails outside reserved domains. Fix: confirm provenance in writing, then replace the file with clearly synthetic rows holding only `id,email`. |
| 3 | **P2** | `tests/test_exporter.py:8`, `:12` | "Tests pass" is true but proves nothing about paging. Both tests use `size=10` against 5 rows, so the bad slice `[0:9]` still returns all 5 rows and finding 1 goes undetected. There is no test with more than one page, a partial last page, or a page past the end. | The tests listed for finding 1, plus `page(rows, 3, 2) == []` for 5 rows. |
| 4 | **P2** | `exporter.py:10-12` | Nothing checks the inputs. `size=0` gives `rows[0:-1]`, which returns every row but the last: an unbounded export from a "page" request. `number=-1, size=2` gives `rows[-2:-1]`, a tail row instead of an error. If `number` or `size` ever comes from a request parameter, a caller gets data they did not ask for. (After fix 1, `size=0` returns `[]`, but negative values still slice from the end.) | `assertRaises(ValueError)` for `page(rows, 0, 0)`, `page(rows, -1, 2)` and `page(rows, 0, -1)`. |
| 5 | **P3** | `tests/test_exporter.py:7`, `:11` | The fixture path `"fixtures/people.csv"` is relative to the current directory. Running the tests from any other directory (an IDE, or `python -m unittest discover -s tests`) fails with `FileNotFoundError`. | Run the suite from `tests/`; it fails today. Fix: build the path from `os.path.dirname(__file__)`, or build rows inline. |

**Scope against the request:** The PR adds a page function and an email export with tests, which is what was asked. The only extra is the unneeded personal-data columns in the fixture (finding 2).

**FILES NEEDED BUT NOT PROVIDED:**
- Callers of `export_page`. I need these to see whether `number` and `size` come from users, and what access control guards the export (this affects the severity of finding 4).
- The CI configuration and the list of required checks.
- The actual test run output.
- Where `fixtures/people.csv` came from.
- The commit log for `b81d0e5` (trailers).

## Close-out

The reviewer does not adjudicate its own findings. The author adjudicates after round 2.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1–5 | Pending | — |

**VERIFIED AFTER FIXES:** None yet.

**MERGE RECOMMENDATION: do not merge.**
- The second round, required for High tier, has not run. It needs an approved endpoint first.
- Findings 1 and 2 are P1 and cannot be deferred.
- Nobody has confirmed where the fixture came from. If it is real, the branch history must be rewritten before merge, not just the file deleted.
- No CI check results were provided, and a missing check is not green.

```json
{
  "verdict": "do not merge",
  "findings": [
    {"severity": "P1", "evidence_level": "confirmed by reading code", "location": "exporter.py:12", "scenario": "Slice end (number+1)*size-1 drops the last row of every page; size=2 over 5 rows never exports rows 2 and 4; size=1 returns empty pages. Customers silently missing from production export.", "fix": "Use rows[number*size:(number+1)*size]; add a test that concatenated pages equal all rows."},
    {"severity": "P1", "evidence_level": "inferred (provenance unknown; P0 if records are real)", "location": "fixtures/people.csv:1-6", "scenario": "Fixture described as a copy of real-format customer records with national_id and name columns; if real, merging commits national IDs to git history and every clone. Tests use only email.", "fix": "Confirm provenance in writing; replace with clearly synthetic id,email rows; if any row is real, rewrite branch history before merge. Exclude the file from any unapproved second-vendor review."},
    {"severity": "P2", "evidence_level": "confirmed by reading code", "location": "tests/test_exporter.py:8", "scenario": "Tests use size=10 over 5 rows, so the off-by-one slice still returns all rows; no multi-page, partial-page or past-end test, so finding 1 passes CI.", "fix": "Add multi-page tests: page(range(5),0,2)==[0,1], page(range(5),2,2)==[4], page(range(5),3,2)==[]."},
    {"severity": "P2", "evidence_level": "confirmed by reading code; exposure depends on callers not provided", "location": "exporter.py:10-12", "scenario": "size=0 yields rows[0:-1] (nearly the whole table); negative number or size slices from the end and returns unrequested rows.", "fix": "Raise ValueError when number<0 or size<1; test with assertRaises."},
    {"severity": "P3", "evidence_level": "confirmed by reading code", "location": "tests/test_exporter.py:7", "scenario": "Relative fixture path fails with FileNotFoundError when tests run from any directory other than the repo root.", "fix": "Resolve the path from os.path.dirname(__file__) or build rows inline."}
  ]
}
```