# Review report

**REVIEWED:** PR #57, head `b81d0e5`, merge base `4c6a912`. Both SHAs are taken from `PR.md`. I had no checkout and no tools, so I could not confirm them against a repository. I reviewed only the patch and the base files supplied.

**TIER:** High. The change is a production customer export, and it adds a fixture of customer-format records with national ID numbers, which is personal data.

**REVIEWERS:** This is a fresh Sonnet 5.5 instance with no memory of writing the change. The author is unknown because no commit trailers were supplied. I did not run the code, so "Tests pass" is unverified.

## Review status

- **Second round not run.** High tier requires two rounds, ideally on two vendors. I can do only one, and I have no subagent tool and no way to reach another vendor. Under Step 2, a High-tier PR whose second round has not run is not reviewed. This report is round 1 only.
- **No approved endpoint confirmed (Step 3).** `fixtures/people.csv` carries national IDs, and I don't know which models or endpoints are approved for this data. Do not send the diff to a second vendor until that is settled. Confirm first whether the fixture is real data (finding 3).

## Findings

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `exporter.py:12` | The slice `rows[number*size:(number+1)*size - 1]` has an off-by-one. Python slices already exclude the end index, so the `- 1` drops the last row of every page. With 25 rows and size 10, page 0 returns 9 rows (indices 0–8), and row 9 appears on no page. Every page silently omits one customer, so the export is incomplete and nothing signals it. | `rows = [{"email": f"{i}@x"} for i in range(25)]`. Assert `len(page(rows,0,10)) == 10` and that the concatenation of all pages equals all 25 emails. This fails today. |
| 2 | P1 | `tests/test_exporter.py:8`, `:12` | The tests cannot catch finding 1. Both use `size=10` on a 5-row fixture, so only a short page 0 is exercised. `rows[0:9]` still returns all 5 rows. No test covers a second page, a full page, the final partial page, or an out-of-range page. The test names suggest paging is covered when it is not. | Use `page(rows, 0, 2)` on the 5-row fixture and expect 2 rows. Also expect page 1 to give rows 3–4, page 2 to give row 5, and page 3 to give `[]`. |
| 3 | P1 (P2 if confirmed synthetic) | `fixtures/people.csv:1-6` | The context calls the fixture a "copy of real-format customer records" with names, emails and national IDs. If any row derives from real customers, committing it puts regulated personal data into repository history, and removing it later does not purge it. The `900-xx` ID prefix and `example.test` domain suggest synthetic data, but the PR doesn't say so. The tests only need the `email` column, so the sensitive columns serve no purpose. | CI check that fails if any fixture matches a national-ID pattern outside a documented synthetic range. Have the owner state the fixture's provenance in the PR. |
| 4 | P2 | `exporter.py:12` | `page` does not validate its arguments. With `size=0`, the slice becomes `rows[0:-1]` and returns every row but the last, which is an unbounded export from a paging function. With `number=-1`, it returns `rows[-size:-1]`, an arbitrary tail window. Negative or zero inputs from a caller produce wrong data rather than an error. | `assertRaises(ValueError)` for `page(rows, 0, 0)`, `page(rows, -1, 10)` and `page(rows, 0, -5)`. |
| 5 | P3 | `tests/test_exporter.py:8`, `:12` | The fixture path `"fixtures/people.csv"` is relative to the current directory. Running the tests from any other directory fails with `FileNotFoundError`. | Run the suite from the repo root and from `tests/`. Both should pass once the path is resolved from `__file__`. |
| 6 | P3 | `exporter.py:16` | `export_page` raises a bare `KeyError` if a row has no `email` column, for example a CSV with a different header. The export fails opaquely. The `email` column is also not checked for blank values. | Load a CSV without an `email` header and expect a clear, specific error. |

**Scope check:** The request asked for a paged export of emails on a given page, with tests. The functions exist, but they return wrong pages (finding 1) and the tests do not cover paging (finding 2). The PR adds nothing beyond the request except the sensitive fixture columns.

**Embedded instructions:** I found no text in the PR description, diff or files that addresses the reviewer.

**FILES NEEDED BUT NOT PROVIDED:** The commit trailers and history, to identify the author. CI check results, since "Tests pass" is a claim I could not confirm. The repository's list of approved endpoints for personal data. Provenance of `fixtures/people.csv`.

## Verdict

**Do not merge.** Finding 1 is a P1 that silently drops customer rows from a production export, and the existing tests pass with it present. Separately, the required second High-tier round has not run, and the fixture's data status is unresolved.

## Close-out (to be completed by the author and PR closer, not by this reviewer)

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1–6 | Pending | Pending |

**VERIFIED AFTER FIXES:** Nothing yet. Any fix commits need a targeted read of the fix diff, plus a regression test for finding 1 that fails without the fix.

**MERGE RECOMMENDATION:** Do not merge. Open items:
- Fix finding 1.
- Resolve the fixture's provenance (finding 3).
- Run the second High-tier round on an approved endpoint.
- Confirm that required checks are present and green.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "confirmed by static reading of the patch; not executed",
      "location": "exporter.py:12",
      "scenario": "Slice end index is (number+1)*size - 1; Python's exclusive end already gives size rows, so each page silently omits its last row. With 25 rows and size 10, page 0 returns 9 rows and row index 9 appears on no page.",
      "fix": "Return rows[number*size:(number+1)*size]; add a test that concatenated pages equal all rows."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed by static reading of the tests",
      "location": "tests/test_exporter.py:8",
      "scenario": "Both tests use size=10 on a 5-row fixture, so only a short first page is exercised. The off-by-one in page() passes undetected, and no multi-page, boundary or out-of-range case is covered.",
      "fix": "Add tests with page size 2 over the 5-row fixture covering pages 0, 1, 2 and 3, and an equality check that all pages together equal all emails."
    },
    {
      "severity": "P1",
      "evidence_level": "inferred from context.md; data provenance unverified",
      "location": "fixtures/people.csv:1-6",
      "scenario": "Fixture is described as a copy of real-format customer records and includes names and national ID numbers. If derived from real customers, committing it puts regulated personal data in repository history. The tests only need the email column.",
      "fix": "Confirm the data is synthetic and say so in the PR, or replace it with a fixture containing only the email column and invented values; add a CI check for national-ID patterns."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed by static reading of slice semantics",
      "location": "exporter.py:12",
      "scenario": "No argument validation: size=0 gives rows[0:-1] (nearly the whole dataset), and number=-1 gives an arbitrary tail window, so invalid input yields wrong or unbounded data instead of an error.",
      "fix": "Raise ValueError when number < 0 or size <= 0; add tests for each."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed by static reading",
      "location": "tests/test_exporter.py:8",
      "scenario": "Relative fixture path depends on the working directory; running the suite from another directory raises FileNotFoundError.",
      "fix": "Build the path from os.path.dirname(__file__)."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed by static reading",
      "location": "exporter.py:16",
      "scenario": "A row or CSV without an 'email' column raises a bare KeyError, and blank emails are not handled, so the export fails opaquely.",
      "fix": "Check the header and raise a clear error; decide and test the behavior for blank values."
    }
  ]
}
```