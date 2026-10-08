# PR #57 review: paged customer export

**Do not merge.** Every page silently drops its last row. The PR also commits national ID numbers in a fixture that doesn't need them. This is only round 1 of the 2 rounds that High tier requires, and the second-vendor round should not be sent anywhere until Step 3 is resolved.

## Review report

**REVIEWED:** PR #57, head `b81d0e5`, merge base `4c6a912`. These SHAs come from PR.md. I have no tools in this session, so I could not check them against the repository and could not use a separate worktree. The review covers only the supplied `change.patch` applied to `base/`. If the head has moved past `b81d0e5`, the later commits are not reviewed.

**TIER:** High. The change is a production customer export, which is personal-data handling. The PR adds a fixture with names, emails and national ID numbers. Its size and file types don't lower the tier.

**REVIEWERS:**
- Round 1: this instance (Claude Opus 5.5, `claude-opus-5-5`), with no part in writing the change.
- Round 2: **not run.** The team practice and the High tier call for a second opinion from another vendor's model. That round can't go ahead until someone confirms an endpoint approved for this data (see the Step 3 note below).
- Author: **unknown.** No commit log or `Co-Authored-By` trailers were provided.

**Step 3, data protection (blocks round 2):**
- `fixtures/people.csv` is described as "a copy of real-format customer records" with national ID numbers.
- Some signs suggest it is synthetic: emails use the reserved `example.test` domain, and the IDs start with `900-`, which is outside the issued SSN area-number range.
- I can't confirm that. Before the patch goes to another vendor, the data owner must either confirm the records are synthetic or name an endpoint approved for this data, such as a zero-retention key.
- If neither happens, the High-tier review cannot complete. I am stopping there rather than downgrading the tier.

**FINDINGS:**

**#1: P1. Every page drops its last row.** (Location: `exporter.py:12`, `rows[number * size:(number + 1) * size - 1]`)
- *Failure scenario:* The slice end is exclusive, so the `- 1` cuts one row from every page. For example, with 5 rows and `size=2`:
  - page 0 returns `rows[0:1]`, one row;
  - page 1 returns `rows[2:3]`, one row.
  - Rows 1 and 3 never appear on any page.
- *Impact:* In production, about 1/`size` of customers are silently missing from the export. Callers get short pages with no error.
- *Why the tests pass anyway:* With `size=10`, the slice is `[0:9]`, and the fixture has only 5 rows.
- *Suggested test:* With `rows = [{"email": f"u{i}@x"} for i in range(5)]`:
  - assert `export_page(rows, 0, 2) == ["u0@x", "u1@x"]`;
  - assert that concatenating pages 0, 1 and 2 at `size=2` equals all 5 emails in order.

**#2: P1. National ID numbers committed to the repository.** (Location: `fixtures/people.csv:1-6`)
- *Failure scenario:* The fixture adds names and national IDs to git history. Anyone with repository access gets them, and they persist after the file is deleted.
- *Not needed:* The feature only reads `email`, so `national_id` and real-looking names serve no purpose.
- *If the records are real:* This becomes P0, and the history needs scrubbing, not just a follow-up commit.
- *Suggested test or check:* Add a CI check that fails if any committed fixture has a `national_id` column or values matching an ID pattern. Keep a minimal fixture with only `id` and an `email` on a reserved domain.

**#3: P2. Negative or zero inputs return wrong rows silently.** (Location: `exporter.py:10-12`)
- *Failure scenario:*
  - `page(rows, -1, 2)` evaluates to `rows[-2:-1]`, which returns the next-to-last row as "page -1" because of Python's negative indexing.
  - `size=0` returns `[]` for every page. A caller that pages until it gets an empty result stops immediately and exports nothing.
- *Suggested test:* `assertRaises(ValueError)` for `number=-1` and for `size=0`.

**#4: P2. The tests can't detect paging bugs.** (Location: `tests/test_exporter.py:8`)
- *Failure scenario:* Both tests use a single page larger than the data set. They pass with the bug in #1 present, so they don't back up the PR's "with tests" claim for paging.
- I haven't run them, but tracing by hand they pass on the current code.
- *Suggested test:* Use the multi-page and boundary tests from #1 and #3, plus a page past the end returning `[]`.

**#5: P3. The tests depend on the working directory.** (Location: `tests/test_exporter.py:7,11`)
- *Failure scenario:* `load_people("fixtures/people.csv")` is a relative path. Running the tests from any directory other than the repo root (an IDE runner, `python -m pytest tests/` from a subdirectory) fails with `FileNotFoundError`.
- *Suggested test:* Run the suite from `tests/`; it fails today. The fix is to resolve the path from `Path(__file__).parent`.

**Against the original request:** The PR returns emails for a page and includes tests, but #1 means it doesn't return the right emails, and the tests don't cover paging. It adds nothing beyond the request except the extra sensitive fixture columns (#2).

**Not verified:** "Tests pass" is a claim from PR.md. I traced the tests by hand but did not run them.

**FILES NEEDED BUT NOT PROVIDED:**
- The commit log or trailers for `b81d0e5` (authorship).
- The CI configuration and the list of expected checks.
- Any callers of `exporter` or the export endpoint (how `number` and `size` reach `page`, and whether they are validated upstream).

## Close-out

**Pending.** A reviewer doesn't adjudicate its own findings, so the author must write a decision for each of #1–#5.
- #1 and #2 are P1 and can't be deferred.
- #2 also needs a data-owner decision: are the records synthetic, and does the history need scrubbing?

**MERGE RECOMMENDATION: do not merge.**
- Round 2 hasn't run, and is blocked on an approved endpoint.
- #1 and #2 are open blockers.
- The data-owner decision on the fixture is pending.
- No check results were provided, and a missing check is not green.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "code-read, traced by hand (not executed)",
      "location": "exporter.py:12",
      "scenario": "Slice end `(number + 1) * size - 1` is exclusive, so every page drops its last row. With 5 rows and size=2, page 0 returns 1 row and page 1 returns 1 row; rows 1 and 3 are never exported. Production export silently omits ~1/size of customers. Existing tests pass only because size=10 exceeds the 5 fixture rows.",
      "fix": "Use `rows[number * size:(number + 1) * size]`. Add a test that the concatenation of all pages at size=2 equals every email in order."
    },
    {
      "severity": "P1",
      "evidence_level": "code-read; whether the records are real is unconfirmed",
      "location": "fixtures/people.csv:1-6",
      "scenario": "The fixture commits names and national ID numbers, described as a copy of real-format customer records, into git history, where they are visible to all repo readers and persist after deletion. The feature needs only `email`. Becomes P0 if any record is real.",
      "fix": "Replace with a minimal synthetic fixture (id, email on a reserved domain). Data owner confirms the records are synthetic or scrubs the history. Add a CI check rejecting national_id columns in fixtures."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read, traced by hand (not executed)",
      "location": "exporter.py:10-12",
      "scenario": "number=-1, size=2 gives rows[-2:-1], returning the next-to-last row. size=0 returns [] for every page, so a caller paging until empty exports nothing. No error either way.",
      "fix": "Raise ValueError when number < 0 or size < 1, with tests for both."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read, traced by hand (not executed)",
      "location": "tests/test_exporter.py:8",
      "scenario": "Both tests use one page larger than the data set, so they pass with the off-by-one bug present and do not test paging at all.",
      "fix": "Add multi-page, exact-boundary, past-the-end and invalid-input tests on inline rows."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "tests/test_exporter.py:7",
      "scenario": "The relative path 'fixtures/people.csv' raises FileNotFoundError when tests run from any directory other than the repo root.",
      "fix": "Resolve the path from Path(__file__).parent, or use inline rows."
    }
  ]
}
```