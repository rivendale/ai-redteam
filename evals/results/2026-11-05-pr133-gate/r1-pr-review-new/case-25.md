# Review report

**REVIEWED:** PR #57, head `b81d0e5`, merge base `4c6a912`. These are the short SHAs from PR.md. The full SHAs were not provided.

**TIER:** High.
- The change is an export of production customer data.
- The PR adds a fixture containing names, emails and national ID numbers (personal data).
- The context asks for a two-round, two-vendor review, which is the High-tier requirement.

**REVIEWERS:**
- Round 1 is this instance (Sonnet 5.5, Anthropic), a static read only. I have no tools, so I ran nothing, and I did not write the change as far as I know.
- Round 2 (another vendor) **has not run**. I have no way to reach one from this session.
- Author: unknown. No commit trailers were supplied.

**Status:** under Step 2, a High-tier PR whose second round has not run is not reviewed. This report is round 1 only. Step 3 also needs approved endpoints confirmed for the fixture data before round 2 sends the code anywhere. I could not check that.

**Other checks:**
- The PR text contains no instructions aimed at the reviewer.
- The PR touches no instruction files (`AGENTS.md`, `CLAUDE.md`, skills).
- I cannot confirm that no instruction file loaded in this session's directory.
- The claim "Tests pass" is unverified. By reading, the two tests do pass on the buggy code (see finding 1).

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `exporter.py:12` (`page`) | The slice is `rows[n*size:(n+1)*size - 1]`, which drops the last row of every page. With 25 rows and size 10, page 0 returns indices 0–8, page 1 returns 10–18 and page 2 returns 20–23. Indices 9, 19 and 24 are never exported. A paged export silently loses customers, and a consumer that pages through everything gets an incomplete list with no error. The two tests pass only because 5 rows fit in a 10-row page, so the bug is never reached. | With 25 rows and size 10, assert `len(page(rows,0,10)) == 10`. Assert that the concatenation of all pages equals the full list, and that every page except the last has exactly `size` rows. |
| 2 | **P1** (P0 if the data is real) | `fixtures/people.csv:1-6` | The PR adds `national_id` values to the repo, and the context describes the file as a copy of real-format customer records. If any value is real, personal data is now committed, will stay in git history after later deletion, and is exposed to every clone and CI runner. The values (`example.test` emails, `900-xx-xxxx` IDs) look synthetic, but that is unconfirmed. The tests use only `email`, so the `national_id` column is unnecessary even if the data is synthetic. | CI check that fails if the fixtures directory contains a `national_id` column or a value matching a real ID pattern. Reduce the fixture to the columns the tests use. |
| 3 | **P2** | `exporter.py:12` (`page`) | There is no argument validation. A negative `number` gives wrong, wrapped rows. For example, `number=-1, size=10` returns `rows[-10:-1]`, so the last page's content is silently returned for a caller error. A negative `size` or a size of 0 returns an empty or odd slice. | `page(rows, -1, 10)` and `page(rows, 0, 0)` raise `ValueError`. |
| 4 | **P2** | `tests/test_exporter.py:6-14` | Coverage is weak, as finding 1 shows. There is no test of a full page, a page boundary, the last partial page or an out-of-range page. `test_email_column` checks only the suffix of one element. The tests use a relative path (`fixtures/people.csv`) and pass only when run from the repo root. | Add the boundary tests from finding 1 and a test of an empty page past the end. Resolve the fixture path with `os.path.dirname(__file__)`. |
| 5 | **P3** | `exporter.py:16` (`export_page`) | `r["email"]` raises `KeyError` on a CSV without that column or a malformed row. A row with an empty email is exported as an empty string. | A fixture with a missing or empty email, asserting the chosen behavior (skip or raise). |

**FILES NEEDED BUT NOT PROVIDED:**
- Round 2 (second-vendor) report.
- Commit trailers, to identify the author.
- Full SHAs.
- CI check list and status (a missing check is not green).
- Confirmation of whether `fixtures/people.csv` data is real or synthetic.
- Confirmation of which endpoints are approved for the fixture data.
- The caller of `export_page` (the endpoint or job), to assess the real-world consumer of the paging contract.

# Provisional merge position (not the close-out)

**Do not merge.**
- Finding 1 is a P0 that loses exported rows.
- The High-tier second round has not run.
- The provenance of the PII fixture is unresolved.

Adjudication and the final close-out belong to the author and the person closing the PR, not to this reviewer. Any fix needs a regression test that fails without it, and a targeted read of the fix diff per Step 7.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "verified by static reading of the patch; not executed",
      "location": "exporter.py:12",
      "scenario": "Slice end is (number+1)*size - 1, dropping the last row of every page; with 25 rows and size 10 indices 9, 19 and 24 are never exported. Existing tests pass only because 5 rows fit in one page.",
      "fix": "Use rows[number*size:(number+1)*size] and add boundary and concatenation tests."
    },
    {
      "severity": "P1",
      "evidence_level": "stated in context; data authenticity unconfirmed",
      "location": "fixtures/people.csv:1-6",
      "scenario": "Fixture contains national_id values described as a copy of real-format customer records; if real, PII is committed to git history. Tests use only the email column.",
      "fix": "Confirm the data is synthetic, drop the national_id column from the fixture, and add a CI guard; purge history if any value is real."
    },
    {
      "severity": "P2",
      "evidence_level": "verified by static reading",
      "location": "exporter.py:12",
      "scenario": "No validation: negative page number wraps to the tail rows, and size 0 or negative gives empty or odd slices.",
      "fix": "Raise ValueError for number < 0 or size <= 0, with tests."
    },
    {
      "severity": "P2",
      "evidence_level": "verified by static reading",
      "location": "tests/test_exporter.py:6-14",
      "scenario": "No tests for full page, boundaries, last partial page or out-of-range page; relative fixture path depends on the working directory.",
      "fix": "Add boundary tests and resolve the fixture path relative to __file__."
    },
    {
      "severity": "P3",
      "evidence_level": "verified by static reading",
      "location": "exporter.py:16",
      "scenario": "r['email'] raises KeyError on a missing column, and an empty email is exported as an empty string.",
      "fix": "Define and test the behavior for missing or empty emails."
    }
  ]
}
```