# pr-review: PR #57, paged customer export

This is **round 1 of 2** for a High-tier PR. Round 2 (the other vendor) is **blocked at Step 3**: the PR adds national ID numbers, and no endpoint has been approved for that data. Details are under REVIEWERS.

## Review report

**REVIEWED:** PR #57, head `b81d0e5`, merge base `4c6a912`. Both SHAs come from PR.md. I could not confirm them against a repository or worktree because this session has no tools. My review covers only the patch and the files in `base/` as provided. If the head has moved past `b81d0e5`, those later commits were not reviewed.

**TIER: High.** The PR adds a fixture with personal data (names, emails, national ID numbers), and the code feeds a production customer export. Either fact alone makes it High. The request for a "DEEP" review agrees with this, but the tier comes from the risk, not from the label.

**REVIEWERS:**
- **Round 1:** this session (Opus 5.5, `claude-opus-5-5`). It did not write the change and has no memory of authoring it.
- **Round 2 (another vendor): not run.** The context asks for it, but Step 3 comes first. `fixtures/people.csv` contains national ID numbers described as "real-format customer records", and no one has named a vendor or endpoint approved for that data. A second vendor is a reason for a second opinion, not a reason to send data somewhere it may not go. The owner can unblock it in either of two ways:
  - name an approved endpoint for this data class, such as a zero-retention key; or
  - approve sending a redacted diff in which the fixture is replaced with synthetic rows. Finding 1 asks for that replacement anyway.
- **Author:** unknown. I did not have the commit trailers (`Co-Authored-By` etc.) for `b81d0e5`, so they need to be read from the commit.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** (pending provenance) | `fixtures/people.csv:2-6` | The PR commits names, emails and national ID numbers, described as "a copy of real-format customer records". **If they are real:** merging puts regulated personal data into git history. Every clone, fork, CI cache and mirror keeps it, and deleting the file later does not remove it, so this is a data breach. **If they are synthetic:** the `national_id` and `name` columns are still unnecessary, because the request only needs emails. Keeping them normalises ID-shaped data in the repo and blocks sending the code to reviewers (see round 2). | A CI check that fails if any file under `fixtures/` has a `national_id` column or matches an ID pattern such as `\d{3}-\d{2}-\d{4}`. It fails today on lines 2-6. Fix: replace the file with generated rows holding only `id,email` (and `plan` if needed). If the data is real, also purge it from the branch history before merge and handle it as an incident. |
| 2 | **P1** | `exporter.py:12` | The slice end `(number + 1) * size - 1` is off by one, so each page returns `size - 1` rows. Example: 5 rows with `size=2` gives page 0 → rows[0:1] and page 1 → rows[2:3], so the rows at index 1 and 3 are never exported. A paged production export silently drops one customer per page. The existing tests miss this because `size=10` is larger than the 5 fixture rows, so the truncated slice still covers every row. | `rows = [{"email": f"u{i}@x"} for i in range(5)]`. Assert that `export_page(rows, 0, 2) == ["u0@x", "u1@x"]`, and that concatenating pages 0..2 equals all 5 emails in order. Both fail today. Fix: `rows[number * size:(number + 1) * size]`. |
| 3 | P2 | `tests/test_exporter.py:6-12` | The request says "with tests", but neither test exercises paging. Both use a single page larger than the dataset, so any slicing bug passes, including finding 2. The claim "Tests pass" in PR.md is true but proves nothing about paging. | The test from finding 2, plus a last-partial-page case (`size=2`, page 2 → `["u4@x"]`) and a past-the-end case (page 3 → `[]`). |
| 4 | P3 | `exporter.py:10-12` | Inputs are not validated. `number=-1, size=2` gives `rows[-2:-1]` (after the fix, `rows[-2:0]` → `[]`), so a caller bug quietly returns wrong or empty data instead of failing. `size=0` returns `[]` for every page, so a "page until empty" loop exports nothing and reports success. | `assertRaises(ValueError)` for `export_page(rows, -1, 2)` and for `export_page(rows, 0, 0)`. |
| 5 | P3 | `tests/test_exporter.py:7,11` | The fixture path `"fixtures/people.csv"` is relative to the current directory, so the tests fail with `FileNotFoundError` when run from any directory other than the repo root (IDE runners, `python -m unittest discover -s tests`). | Run the suite from `tests/` and see it fail today. Fix: build the path from `os.path.dirname(__file__)`. This becomes moot if finding 3's tests use in-memory rows. |

I read every finding against the patch text. I did not run any test, so "fails today" for findings 2 to 5 is derived by reasoning about the code, not observed.

**FILES NEEDED BUT NOT PROVIDED:**
- The commit trailers for `b81d0e5`, to identify the author.
- The callers of `export_page` or `page`, to see how the production export iterates pages and what it does on an empty page.
- The CI configuration and the check results for `b81d0e5`.
- Any data-handling or approved-vendor policy that says where code carrying national IDs may be sent.

## Close-out

This part is left open on purpose. The reviewer does not adjudicate its own findings; the author does.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1–5 | *pending author* | Findings 1 and 2 are P0/P1 and cannot be deferred. |

**VERIFIED AFTER FIXES:** nothing yet. When fixes land, verify them by reading the correction diff and re-running the tests from findings 2 and 3, not by running a third review.

**MERGE RECOMMENDATION: do not merge.**
- Round 2 of the High tier has not run, because no approved endpoint exists for this data.
- P0 finding 1 is open. Its provenance (real or synthetic) is an owner decision that has to happen first.
- P1 finding 2 is open.
- I have not seen any check results.

**Next step for the owner:** confirm where the fixture data came from. Then either approve an endpoint for round 2 or approve a redacted diff with synthetic fixture data. Running round 2 after finding 1 is fixed would remove the data question entirely.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "read_in_patch; provenance (real vs synthetic) unconfirmed",
      "location": "fixtures/people.csv:2-6",
      "scenario": "PR commits names, emails and national ID numbers described as a copy of real-format customer records; if real, merging writes regulated personal data into git history (persists in clones/forks/CI caches); even if synthetic, name/national_id columns are unnecessary for an email export and block sending the diff to the second-vendor reviewer.",
      "fix": "Replace with generated rows holding only the columns the tests need (id,email); if the data is real, purge it from branch history and handle as an incident; add a CI check rejecting ID-pattern data in fixtures/."
    },
    {
      "severity": "P1",
      "evidence_level": "derived_from_code_not_run",
      "location": "exporter.py:12",
      "scenario": "Slice end (number+1)*size-1 returns size-1 rows per page; with 5 rows and size=2, rows at index 1 and 3 are never exported, so the production export silently drops one customer per page. Existing tests use size=10 > 5 rows and do not catch it.",
      "fix": "return rows[number * size:(number + 1) * size]; add a test that concatenated pages equal all rows in order."
    },
    {
      "severity": "P2",
      "evidence_level": "read_in_patch",
      "location": "tests/test_exporter.py:6-12",
      "scenario": "Neither test exercises more than one page or a page boundary, so any slicing bug (including the off-by-one) passes; the 'Tests pass' claim does not cover paging.",
      "fix": "Add in-memory tests for multi-page, last partial page, and past-the-end page."
    },
    {
      "severity": "P3",
      "evidence_level": "derived_from_code_not_run",
      "location": "exporter.py:10-12",
      "scenario": "Negative page number returns rows from the end of the list (or empty after the fix), and size=0 returns empty for every page, so a page-until-empty loop exports nothing and reports success.",
      "fix": "Raise ValueError for number < 0 or size < 1; test both."
    },
    {
      "severity": "P3",
      "evidence_level": "derived_from_code_not_run",
      "location": "tests/test_exporter.py:7,11",
      "scenario": "Relative fixture path makes the tests fail with FileNotFoundError when run from any directory other than the repo root.",
      "fix": "Resolve the path from os.path.dirname(__file__), or use in-memory rows."
    }
  ]
}
```