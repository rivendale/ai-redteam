# pr-review: PR #57, paged customer export

## Review report

**REVIEWED:** PR #57, head `b81d0e5`, merge base `4c6a912`. I read `PR.md`, `change.patch` and `base/` as supplied. I could not confirm that the supplied patch equals the head commit.

**TIER:** High. The PR exports customer email addresses, which is personal data, and it commits a fixture with national ID numbers. The context also asks for a deep, two-vendor review.

**REVIEWERS:**
- Reviewer: this Claude instance (Sonnet 5.5), a fresh session with no part in writing the change. It had no tools, so it did a static read only.
- Author: unknown, because no commit trailers were supplied.
- No instruction files from the checkout were provided or loaded. `base/README.md` contains nothing addressed to reviewers.

**Round status:** only round 1 ran. The High tier requires a second round, ideally on another vendor. Step 3 requires an approved endpoint for data of this kind, and I was given no approved list for personal-data code. I did not send anything elsewhere. **The review is incomplete until an approved second reviewer runs.** The fixture is synthetic-looking, but the context calls it "real-format", so the owner should confirm which endpoints are approved.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `exporter.py`, `page()`, the `return rows[number * size:(number + 1) * size - 1]` line | The slice end is `(number+1)*size - 1`, which is one too small. Every full page drops its last row. With 5 rows, `page(rows, 0, 5)` returns 4 rows, and with `size=2` page 0 returns 1 row. Row index `k*size-1` is never exported on any page, so those customers are silently missing from the export. | `page(rows, 0, 2)` over the 5 fixture rows must have ids 1 and 2. Pages 0, 1 and 2 with size 2 must concatenate to all 5 rows with no gaps or duplicates. |
| 2 | P1 | `tests/test_exporter.py`, `test_first_page` and `test_email_column` | Both tests use page size 10 over 5 rows, so the slice end is past the data and the off-by-one in #1 cannot show. "Tests pass" is true but proves nothing about paging. Page 1, boundary sizes and out-of-range pages are untested. | Assert exact emails for page sizes 2 and 5, assert page 1 contents, and assert that the union of all pages equals the full list. |
| 3 | P1 (conditional) | `fixtures/people.csv` (whole file), `national_id` column | The context says the file is a copy of real-format customer records. If any value or name comes from real people, national IDs are now in git history, and a later delete does not remove them. The `example.test` emails and `900-` prefixes look synthetic, but I cannot verify this. The export only needs `email`, so the column is unnecessary. | A CI check that fixtures contain no `national_id` column, or only values from a documented fake range. Drop the column from the fixture. |
| 4 | P2 | `exporter.py`, `page()` | There is no input validation. A negative `number` returns surprising slices. `size=0` with `number=0` gives `rows[0:-1]`, which is every row but the last. A negative `size` also returns data. A caller-controlled page parameter can therefore return a different set than intended, or the whole list. | Expect `ValueError` for `number < 0` or `size <= 0`. Add a test that `page(rows, 0, 0)` raises or returns `[]`. |
| 5 | P3 | `tests/test_exporter.py`, the `"fixtures/people.csv"` paths | The relative path only works when tests run from the repo root. Running from another working directory raises `FileNotFoundError`. | Resolve the path from `__file__` and run the tests from a different working directory. |

No access control, authentication or rate limiting appears in the diff. The base exposes no endpoint, so I treat that as out of scope here. The owner should confirm that who may call `export_page` is decided elsewhere.

**FILES NEEDED BUT NOT PROVIDED:**
- Commit trailers for the author record.
- The CI check results (a missing check is not green).
- Provenance of `people.csv`.
- Any caller of `export_page`.
- Confirmation that the supplied patch equals head `b81d0e5`.

## Close-out

Not written. The author must adjudicate first, and a reviewer does not adjudicate its own findings.

**MERGE RECOMMENDATION (provisional): do not merge.** Findings #1 and #2 are open and the paging is wrong. Finding #3 needs a provenance decision from the owner. The required second High-tier round has not run, and no CI status was supplied. After fixes, verify them with a targeted read of the correction diff and its tests (Step 6). Do not run a full re-review.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "reasoned from diff; not executed",
      "location": "exporter.py:page (return rows[number * size:(number + 1) * size - 1])",
      "scenario": "Slice end is one too small, so every full page omits its last row. page(rows,0,2) on 5 rows returns 1 row; row k*size-1 is never exported, silently omitting customers.",
      "fix": "Use rows[number*size:(number+1)*size]; add a test that all pages concatenated equal the full list."
    },
    {
      "severity": "P1",
      "evidence_level": "reasoned from diff",
      "location": "tests/test_exporter.py:test_first_page, test_email_column",
      "scenario": "Page size 10 over 5 rows masks the off-by-one; page 1, boundaries and out-of-range pages are untested, so passing tests prove nothing about paging.",
      "fix": "Add exact-content tests for sizes 2 and 5, page 1, and a no-gaps/no-duplicates union test."
    },
    {
      "severity": "P1",
      "evidence_level": "UNVERIFIED provenance; context says real-format records",
      "location": "fixtures/people.csv (national_id column)",
      "scenario": "If any record derives from real customers, national IDs are permanently in git history. Values look synthetic (example.test, 900- prefix) but this is unconfirmed. The export does not need the column.",
      "fix": "Confirm the data is synthetic, drop the national_id column from the fixture, and add a CI check blocking national_id in fixtures."
    },
    {
      "severity": "P2",
      "evidence_level": "reasoned from diff",
      "location": "exporter.py:page",
      "scenario": "No validation: negative number or size, or size=0, yields unintended slices (e.g. size=0 returns all rows but the last).",
      "fix": "Raise ValueError for number < 0 or size <= 0; add tests."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned from diff",
      "location": "tests/test_exporter.py (fixture paths)",
      "scenario": "Relative path fixtures/people.csv fails when tests run outside the repo root.",
      "fix": "Build the path from __file__."
    }
  ]
}
```