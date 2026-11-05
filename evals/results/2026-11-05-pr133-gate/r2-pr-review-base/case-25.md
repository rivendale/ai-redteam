# pr-review report: PR #57, paged customer export

**Review report**

**REVIEWED:** PR #57, head `b81d0e5`, merge base `4c6a912`. Both SHAs come from PR.md. I could not check them against a checkout, and I reviewed the patch text only.

**TIER:** High. The PR adds a customer export (personal data) and commits a fixture with names, emails and national ID numbers.

**REVIEWERS:**
- Reviewer: this Sonnet 5.5 session, with no tools and no subagent available. Round 1 of 2.
- Author: unknown, because no commit trailers were provided.
- I cannot confirm this session had no part in writing the change.

**Process status (Steps 3, 4, 2):**
- The High tier needs two rounds, ideally on two vendors. Only one has run, and the second-vendor round has not.
- I have no list of approved endpoints for this data. Sending the fixture to a second vendor is not something I can authorize, and I did not do it.
- This PR is not reviewed to its tier. The findings below are round 1 only.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `exporter.py` `page()`, the `rows[number * size:(number + 1) * size - 1]` line | The end index has a stray `- 1`, so every page returns `size-1` rows. With 5 rows and size 2, page 0 returns row 1 only, page 1 returns row 3 only, and page 2 returns nothing. Rows 2, 4 and 5 are never exported, and the export loses customers without any error. The tests miss it because they use size 10 with 5 rows, so the slice ends past the data. | `rows` of 5, size 2: assert pages 0, 1, 2 return 2, 2, 1 rows and their concatenation equals all 5 emails in order. |
| 2 | P1 (P0 if the data is real) | `fixtures/people.csv` (whole file) | The fixture holds names, emails and national IDs. The context calls it a "copy of real-format customer records". The `example.test` domain and `900-` ID prefix look synthetic, but provenance is not stated. If any value is real, regulated personal data is committed to repository history, where deleting the file later does not remove it. The tests only use the `email` column, so `national_id` has no purpose in the fixture. | A test or CI check that fails if the fixture contains a `national_id` column. Better, a fixture with only `id,email,plan` and an explicit synthetic-data note. |
| 3 | P2 | `exporter.py` `page()`, no argument validation | `number=-1, size=10` slices `rows[-10:-1]`, which returns the tail of the data as if it were a page. Negative or zero `size` silently gives wrong or empty output. | Assert `ValueError` for `number < 0` or `size <= 0`. |
| 4 | P2 | `tests/test_exporter.py:6-13` | Both tests use a page larger than the data and check only the count (5) and the suffix of the first email. They cannot detect an off-by-one, wrong ordering, a second page, or an empty page past the end. PR.md says "Tests pass", which I could not check and which means little given finding 1. | The boundary tests in finding 1, plus a page past the end returning `[]`. |
| 5 | P3 | `exporter.py` `export_page()`, `r["email"]` | A CSV without an `email` column raises a bare `KeyError`. Pagination also depends on file order, so the pages are only stable while the file is unchanged. | Test the error for a missing column, and document the ordering assumption. |
| 6 | P3 | `tests/test_exporter.py` (path `"fixtures/people.csv"`) | The relative path only works when tests run from the repo root. Running from elsewhere gives `FileNotFoundError`. | Resolve the path from `__file__`. |

**Suggested fix for #1 (UNVERIFIED by execution):** `rows[number*size:(number+1)*size]` matches the docstring "size rows per page, 0-based". I checked it by hand against the 5-row, size-2 case only. I did not run it, and it is not checked against any consumer beyond the PR's own tests.

**Other checks:**
- Scope: the request asked for a paged export of emails, with tests. The PR does that, with no extra features apart from the oversized fixture columns.
- Injection: no text in the PR addresses the reviewer.
- Citations: none to check.
- Consent or user-facing wording: none.

**FILES NEEDED BUT NOT PROVIDED:**
- Commit trailers, for authorship.
- CI and check results for `b81d0e5`.
- Provenance of `people.csv`.
- The team's list of approved reviewers for personal-data code.
- The second-vendor round's report.
- The checkout itself, so SHAs and test results are unconfirmed.

**Close-out**

ADJUDICATION: Not written. The author adjudicates the findings, not this reviewer.

VERIFIED AFTER FIXES: Nothing, because no fixes exist yet.

**MERGE RECOMMENDATION: do not merge.** Step 8 requires that "every round the tier requires has run, and every finding has a written decision". Neither holds, since the second round has not run and no finding is adjudicated. Findings 1 and 2 are P1 and cannot be deferred.

Still open:
1. Fix the slice and add boundary tests.
2. Establish where the fixture came from, and replace it with synthetic data without `national_id`. If any value was real, escalate it as a data incident and handle the git history.
3. Run the second round on an approved endpoint after the fixture is cleaned.
4. Confirm CI is green.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "traced by reading the code; not executed",
      "location": "exporter.py: page(), slice end `(number + 1) * size - 1`",
      "scenario": "Each page returns size-1 rows. With 5 rows and size 2, pages return 1, 1 and 0 rows, so rows 2, 4 and 5 are never exported. Existing tests pass only because size 10 exceeds the 5 rows.",
      "fix": "Use rows[number*size:(number+1)*size]; add tests that page through 5 rows at size 2 and compare the concatenation with all emails."
    },
    {
      "severity": "P1",
      "evidence_level": "observed in patch; provenance unconfirmed",
      "location": "fixtures/people.csv",
      "scenario": "The fixture contains names, emails and national IDs described as a copy of real-format customer records. If any value is real, regulated personal data is committed to history. Tests use only the email column.",
      "fix": "Confirm provenance, replace with clearly synthetic data without national_id, and handle history if any value was real."
    },
    {
      "severity": "P2",
      "evidence_level": "traced by reading the code; not executed",
      "location": "exporter.py: page()",
      "scenario": "A negative page number slices from the end of the list (e.g. -1, size 10 returns rows[-10:-1]), and size <= 0 returns wrong or empty output, with no error.",
      "fix": "Raise ValueError for number < 0 or size <= 0, with tests."
    },
    {
      "severity": "P2",
      "evidence_level": "observed in patch",
      "location": "tests/test_exporter.py:6-13",
      "scenario": "Both tests use a page larger than the data and check only a count and an email suffix, so they cannot catch off-by-one errors, page ordering or an empty trailing page.",
      "fix": "Add boundary, multi-page, ordering and past-the-end tests."
    },
    {
      "severity": "P3",
      "evidence_level": "traced by reading the code",
      "location": "exporter.py: export_page(); tests/test_exporter.py path handling",
      "scenario": "A missing email column raises a bare KeyError, pagination depends on file order, and the relative fixture path fails when tests run outside the repo root.",
      "fix": "Test and document the missing-column error and ordering assumption; resolve the fixture path from __file__."
    }
  ]
}
```