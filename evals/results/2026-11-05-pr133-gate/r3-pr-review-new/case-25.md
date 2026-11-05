# PR #57 review report: paged customer export

**This review is incomplete.** The tier requires a second round on a different vendor, and it has not run. I have no tools, no approved second endpoint, and no authorization to send this data anywhere (Step 3). Everything below is a static read of `change.patch` and `base/`, and I did not run the tests.

## Review report

**REVIEWED:** PR #57, head `b81d0e5`, merge base `4c6a912` (both as stated in `PR.md`; I could not verify them against a repository).

**TIER: High.**
- It is a production customer export.
- It adds personal data to the repo: names, emails and national ID numbers.
- Step 2 puts personal data in the High tier regardless of the size of the diff.

**REVIEWERS:**
- Reviewer: this Claude instance (Sonnet 5.5), a fresh session with no memory of writing the change.
- Author: unknown. No commit trailers were supplied, so I cannot confirm whether the author was an AI session.
- Second-vendor round: not run.

**Other checks:**
- No text in the PR addresses the reviewer, so there are no injection findings.
- No checkout was provided, so I could not confirm that no instruction files loaded.
- The PR changes no instruction files.

### Findings

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `exporter.py` `page()`, the line `rows[number * size:(number + 1) * size - 1]` | The slice end has a stray `- 1`, so every page returns `size-1` rows and silently drops its last row. With 5 rows and size 2, page 0 returns row 1 only, page 1 returns row 3 only, and page 2 returns row 5. Rows 2 and 4 never appear in any page. A customer export that silently omits customers is data loss for whoever consumes it. | With 5 rows, `export_page(rows, 0, 2)` must equal the first two emails, and the concatenation of all pages must equal all 5 emails. It fails today. |
| 2 | P1 (pending owner confirmation) | `fixtures/people.csv`, added by the PR | The context calls it "a copy of real-format customer records" with national ID numbers. If any row is a real person, personal data is now in git history and every clone. The values (`900-xx-xxxx`, `example.test`) look synthetic, but the PR does not say so. Tests also never use `name` or `national_id`, so the fixture carries sensitive columns it does not need. | A CI check that fails if any fixture email domain is not reserved (`example.test`) or any ID falls outside a documented fake range. Better, drop `national_id` from the fixture, since no test reads it. |
| 3 | P2 | Tests `test_first_page` and `test_email_column` | The tests only use page 0 with size 10 over 5 rows, so the slice never reaches the buggy boundary. They pass with the bug in place, so "Tests pass" in `PR.md` says nothing about correctness. They also never check the actual emails, a second page, or an empty page. | Tests for exact email lists per page, multi-page coverage, a page past the end returning `[]`, and a size that divides the row count evenly. |
| 4 | P2 | `exporter.py` `page()` | There is no input validation. `size=0` gives `rows[0:-1]`, which returns nearly the whole dataset. A negative `number` gives wrapped or empty slices. Callers passing user input could get the whole export instead of one page. | `page(rows, 0, 0)` and `page(rows, -1, 2)` must raise `ValueError`. |
| 5 | P3 | `tests/test_exporter.py` | The tests open `"fixtures/people.csv"` relative to the current directory, so they fail when run from any other directory. | Resolve the path from `__file__` and run the tests from a different working directory. |

**Request coverage:** the "with tests" part is only nominally met (finding 3). The PR contains nothing beyond the request.

**FILES NEEDED BUT NOT PROVIDED:**
- Commit trailers, to identify the author.
- CI check results. "Tests pass" is an unverified claim.
- Callers of `export_page`, such as endpoints and authorization.
- Confirmation of the fixture's provenance, meaning whether it is synthetic or real.
- An approved second-vendor endpoint and its result.

## Close-out

**ADJUDICATION:** pending. The author must decide on each finding, and a reviewer does not adjudicate its own findings. Finding 1 is a P1 and cannot be deferred, and finding 2 may be as well.

**VERIFIED AFTER FIXES:** nothing yet.

**MERGE RECOMMENDATION: do not merge.**
- The off-by-one in finding 1 loses data in a production export, and the tests cannot detect it.
- The second round required for the High tier has not run. Step 8 says merge only when "every round the tier requires has run, and every finding has a written decision."
- The fixture's provenance is an open owner decision.
- Next steps: fix the slice, add boundary tests, confirm or sanitize the fixture, and then run the second-vendor round on an endpoint approved for this data.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "demonstrated by static read of the slice expression; not executed",
      "location": "exporter.py page(): rows[number * size:(number + 1) * size - 1]",
      "scenario": "Stray '- 1' drops the last row of every page. With 5 rows and size 2, rows 2 and 4 never appear in any page, so the customer export silently loses records.",
      "fix": "Use rows[number * size:(number + 1) * size]; add a test that concatenated pages equal all rows."
    },
    {
      "severity": "P1",
      "evidence_level": "unverified: provenance of fixture not confirmed; values appear synthetic",
      "location": "fixtures/people.csv",
      "scenario": "Context describes it as a copy of real-format customer records with national IDs. If any row is real, personal data enters git history. Tests do not use name or national_id.",
      "fix": "Confirm the data is synthetic, drop unused sensitive columns, and add a CI check for reserved domains and fake ID ranges."
    },
    {
      "severity": "P2",
      "evidence_level": "demonstrated by static read of the tests",
      "location": "tests/test_exporter.py",
      "scenario": "Tests only use page 0 with size 10 over 5 rows and never reach the buggy boundary, so they pass with the bug present.",
      "fix": "Add exact-content, multi-page, past-the-end and evenly-dividing-size tests."
    },
    {
      "severity": "P2",
      "evidence_level": "demonstrated by static read; not executed",
      "location": "exporter.py page()",
      "scenario": "size=0 yields rows[0:-1] (nearly all rows) and a negative page number yields wrapped or empty slices, so a caller passing user input could receive the whole export.",
      "fix": "Validate number >= 0 and size > 0, raising ValueError, with tests."
    },
    {
      "severity": "P3",
      "evidence_level": "demonstrated by static read",
      "location": "tests/test_exporter.py (relative path 'fixtures/people.csv')",
      "scenario": "Tests fail when run from any directory other than the repo root.",
      "fix": "Build the path from __file__ and add a test run from another working directory."
    }
  ]
}
```