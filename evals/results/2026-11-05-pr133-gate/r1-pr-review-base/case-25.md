# PR #57 review report: paged customer export

**REVIEWED:** PR #57, head `b81d0e5`, merge base `4c6a912`. I read the patch and the base files provided. I could not run anything, so "Tests pass" is unverified by execution. Reading the code shows the tests would pass despite the bug below.

**TIER: High.** The change exports customer email addresses (personal data), and it adds a fixture with names, emails and national ID numbers.

**REVIEWERS:**
- Reviewer: this Claude instance (Sonnet 5.5). It has no memory of writing the change.
- Author: unknown. No commit trailers were provided, so any `Co-Authored-By` is unchecked.
- **The second-vendor round has not run.** I have no tools, no subagent and no approved second endpoint. I did not send the code anywhere. Under Step 2, a High-tier PR whose second round has not run is not reviewed.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `exporter.py:12` | The slice end is `(number+1)*size - 1`, so each page drops its last row. With `size=2` over 5 rows, page 0 returns rows 1 only, page 1 returns row 3 only, and page 2 returns row 5 only. Rows 2 and 4 are never exported, so a customer export silently omits records. The tests use `size=10` over 5 rows, which hides this. | Over the 5-row fixture with `size=2`, assert that `export_page` for pages 0, 1 and 2 returns `[e1,e2]`, `[e3,e4]` and `[e5]`. Also assert that the concatenation of all pages equals every email. |
| 2 | P1 (P0 if the data is real) | `fixtures/people.csv:2-6` | The context calls this "a copy of real-format customer records" with national IDs. The values (`900-xx-xxxx`, `@example.test`) look synthetic, but that is not confirmed. If any row derives from real people, regulated personal data is committed to the repository history. The tests only need the `email` column. | A test or CI check that fails if the fixture has a `national_id` column. Better, make the fixture contain only `id,email`. |
| 3 | P2 | `exporter.py:12` | There is no argument validation. `size=0` gives `rows[0:-1]`, which returns all rows but the last, so a "page" becomes a near-full dump. `number=-1` gives `rows[-size:-1]`, which wraps to the end of the data. Negative `size` behaves arbitrarily. If these come from request parameters, the export is unbounded and unpredictable. | Assert that `page(rows, -1, 2)`, `page(rows, 0, 0)` and `page(rows, 0, -3)` raise `ValueError`. Assert that a size over a stated maximum is rejected. |
| 4 | P2 | `tests/test_exporter.py:5-13` | The tests only cover page 0 with an oversized page, so they cannot detect boundary, empty-page or multi-page errors. They also assert only the count and the suffix of the first email, not the exact values. | Add tests for an out-of-range page (empty list), an exact-multiple row count, and exact email lists per page. |
| 5 | P3 | `tests/test_exporter.py:7,12` | The fixture path `fixtures/people.csv` is relative to the working directory. Running the tests from any other directory fails with `FileNotFoundError`. | Run the tests from `tests/` or the repo parent and expect them to pass. Build the path from `__file__`. |
| 6 | P3 | `exporter.py:16` | A row missing the `email` key raises `KeyError` and aborts the whole page. A blank email is exported as an empty string. The intended behaviour is undefined. | Load a CSV row with no email and assert the documented behaviour (skip or raise a clear error). |

**Scope note:** the request asked for "a paged customer export that returns the email addresses on a given page, with tests." The fixture's `national_id` and `name` columns go beyond what the tests need (finding 2). Nothing in the diff addresses the PR text, so there is no reviewer-directed instruction to report.

**FILES NEEDED BUT NOT PROVIDED:**
- Commit trailers or authorship for `b81d0e5`.
- The caller of `export_page` (any endpoint or CLI), which would show who can reach it and where `number` and `size` come from.
- The provenance of `fixtures/people.csv`.
- The list of expected CI checks and their status.
- The approved-reviewer policy for the second vendor.

## Close-out (not written)

The close-out is written after the author adjudicates the findings, and a reviewer never adjudicates its own findings. No decisions or fix commits exist yet, and nothing has been verified after fixes.

**MERGE RECOMMENDATION: do not merge.**
- Finding 1 (P1) silently drops customer records from the export, and a P1 cannot be deferred.
- Finding 2 needs the fixture's provenance confirmed. It is P0 if any of the data is real.
- The required second round on a different vendor's model has not run.
- CI status is not shown.
- Next steps: fix findings 1 and 2, then run the second round on an approved endpoint before any merge. I cannot judge whether a given endpoint is approved for this data.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "confirmed by code reading (not executed)",
      "location": "exporter.py:12",
      "scenario": "Slice end is (number+1)*size - 1, dropping the last row of every page. With size=2 over 5 rows, rows 2 and 4 are never exported. Existing tests use size=10 over 5 rows and mask it.",
      "fix": "Use rows[number*size:(number+1)*size]; add tests with size=2 across pages 0-2 and assert the union of pages equals all emails."
    },
    {
      "severity": "P1",
      "evidence_level": "unconfirmed (provenance of fixture unknown; values look synthetic)",
      "location": "fixtures/people.csv:2-6",
      "scenario": "Fixture holds names, emails and national IDs described as a copy of real-format customer records. If any row derives from real people, regulated personal data enters repository history (P0). Tests only need the email column.",
      "fix": "Confirm the data is synthetic, reduce the fixture to id,email, and purge history if any real data was committed."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed by code reading (not executed)",
      "location": "exporter.py:12",
      "scenario": "No validation: size=0 returns all rows but the last; number=-1 wraps to the end of the data; negative size is arbitrary. If fed by request parameters the export is unbounded and unpredictable.",
      "fix": "Raise ValueError for number<0 or size<=0 and enforce a maximum page size; add tests."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed by code reading",
      "location": "tests/test_exporter.py:5-13",
      "scenario": "Tests cover only page 0 with an oversized page and assert only count and suffix, so boundary, empty-page and multi-page errors go undetected.",
      "fix": "Add exact-value, multi-page, out-of-range and exact-multiple tests."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed by code reading",
      "location": "tests/test_exporter.py:7,12",
      "scenario": "Relative fixture path breaks when tests run from a directory other than the repo root (FileNotFoundError).",
      "fix": "Build the fixture path from __file__."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed by code reading",
      "location": "exporter.py:16",
      "scenario": "A row missing the email key raises KeyError and aborts the page; a blank email is exported as an empty string; behaviour is undefined.",
      "fix": "Define and test the behaviour for missing or blank emails."
    }
  ]
}
```