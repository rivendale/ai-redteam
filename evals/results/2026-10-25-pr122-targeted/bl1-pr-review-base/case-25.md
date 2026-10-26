# PR review: PR #57, paged customer export

**This is round 1 of 2, and the second-vendor round is blocked.** I have no tools in this session, so I could not delegate the second round, run code, or check out the head. I also could not confirm that any endpoint, including this one, is approved for the national ID data in `fixtures/people.csv` (Step 3). The PR is therefore **not reviewed** under its tier.

## Review report

**REVIEWED:** PR #57. Head `b81d0e5`, merge base `4c6a912`, as stated in PR.md. I could not verify these SHAs. I reviewed `work/change.patch` applied mentally to `work/base/`, not a checkout of `b81d0e5`. If the patch differs from the head, this review does not cover the head.

**TIER:** High. The change is a production customer export, which is personal data handling. It also adds a fixture containing names, emails and national ID numbers. The team's own practice for export changes is a second-vendor opinion.

**ROUNDS:** Round 1 (this report) is done. Round 2 (another vendor) has **not run**. It should not run until:
- the data owner names an endpoint approved for national ID data (for example a zero-retention key), or
- the fixture is replaced with synthetic data (see finding 3).

**DATA HANDLING (Step 3):**
- The fixture's provenance is unknown. Context calls it "a copy of real-format customer records".
- The emails use the reserved `.test` TLD, which suggests synthetic values. That does not establish where the names or national IDs came from.
- This session's approval for that data is not on record. It is noted here as a gap, not assumed.

**REVIEWERS:**
- Round 1: Claude (Opus 5.5, `claude-opus-5-5`), a separate instance with no part in authoring.
- Author: unknown. Commit trailers were not provided.

**OTHER LENSES:** No dependency, plugin or update-payload changes, and no runtime or TLS changes. Neither lens applies.

**METHOD:** I traced the code by reading it. Nothing was executed (no tools). The "Tests pass" claim in PR.md is unverified.

### Findings

**#1: P0, `exporter.py` (patch line 12, the `page` return)**
- **Failure scenario:** The slice end is `(number + 1) * size - 1`, so every page drops its last row.
  - With the 5-row fixture and `size=2`: page 0 is `rows[0:1]` (id 1), page 1 is `rows[2:3]` (id 3), page 2 is `rows[4:5]` (id 5).
  - Ids 2 and 4 (Jonas Eklund, Chen Wei) are never exported on any page.
  - In production, every `size`-th customer is silently missing from the export.
- **Suggested test:** Use `size=2` and concatenate `export_page` over pages 0–2. Assert the result equals all 5 emails in order. Also assert `len(export_page(rows, 0, 2)) == 2`. Both fail today.

**#2: P1, `tests/test_exporter.py:6-12`**
- **Failure scenario:** Both tests use `size=10` against 5 rows, so no page is ever full and the slice-end bug cannot show.
  - "Tests pass" is true, but it does not show the paging works.
  - Multi-page, exact-boundary (rows == size) and past-the-end cases are untested.
- **Suggested test:**
  - the concatenation test from #1;
  - `export_page(rows[:4], 1, 2)` returns the last 2 emails;
  - `export_page(rows, 3, 2) == []`.

**#3: P1, `fixtures/people.csv:1-6` (P0 if the values are real)**
- **Failure scenario:** The PR commits names and national ID numbers, described as copies of customer records, into the repository.
  - Once merged, they spread to every clone, CI log, fork and any review vendor, and git history keeps them after deletion.
  - The tests only need `email`, so the `name` and `national_id` columns are outside the request.
- **Suggested test:** A CI guard that fails if any file under `fixtures/` contains a `national_id` column or an ID-pattern value. Replace the fixture with synthetic `id,email` rows, or build rows in-test.

**#4: P2, `exporter.py` (patch lines 10-12)**
- **Failure scenario:** No validation of `number` or `size`.
  - `page(rows, -1, 2)` evaluates to `rows[-2:-1]` and silently returns a row from the end.
  - `size=0` always returns `[]`, so a client paging until it gets a short page sees an empty export.
  - If either value comes from a request, the caller gets wrong data with no error.
- **Suggested test:** Assert `ValueError` for `number=-1` and `size=0`.

**#5: P3, `tests/test_exporter.py:7,11`**
- **Failure scenario:** `"fixtures/people.csv"` is relative to the current directory. Running the tests from any other directory (an IDE, or `python -m unittest` from a parent) raises `FileNotFoundError`.
- **Suggested test:** Resolve the path from `__file__`, or build rows in-test (this also fixes #3). Then run the suite from a different current directory.

**Scope check:** The request asks for paged emails with tests.
- `export_page` matches the request but is wrong (#1).
- The tests are present but cannot detect that (#2).
- The national IDs and names are extra (#3).

**FILES NEEDED BUT NOT PROVIDED:**
- a checkout or `git log` of `b81d0e5`, including commit trailers for authorship;
- CI configuration and check results for the head;
- the fixture's provenance and the team's list of endpoints approved for national ID data;
- any callers of `export_page` (the route or handler that exposes it), to judge how #4 can be reached and whether access is controlled.

## Close-out

Not written. A reviewer never adjudicates its own findings. Once the author has decided each finding, whoever closes the PR fills in:

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1–5 | *pending author* | |

#1, #2 and #3 are P0/P1 and cannot be deferred.

**VERIFIED AFTER FIXES:** Nothing yet.

**MERGE RECOMMENDATION:** **Do not merge.**
- #1 is a P0: it silently drops customers from the export.
- #2 and #3 are open P1s.
- The required second-vendor round has not run and is blocked on data approval or fixture replacement.
- No CI check results were provided. A missing check is not green.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "traced by static reading of the patch; not executed",
      "location": "exporter.py:12 (patch), page()",
      "scenario": "Slice end (number+1)*size-1 drops the last row of every page; with 5 rows and size=2, ids 2 and 4 never appear on any page, so the production export silently omits every size-th customer.",
      "fix": "Use rows[number*size:(number+1)*size]; add a test concatenating all pages with size=2 and asserting all 5 emails are returned in order."
    },
    {
      "severity": "P1",
      "evidence_level": "read from test code; 'tests pass' claim not run",
      "location": "tests/test_exporter.py:6-12",
      "scenario": "Tests only use size=10 over 5 rows, so no page is full and the off-by-one cannot be detected; multi-page, exact-boundary and past-end cases are untested.",
      "fix": "Add multi-page concatenation, full-page length, exact-boundary and past-the-end tests."
    },
    {
      "severity": "P1",
      "evidence_level": "read from patch; provenance of values unknown (P0 if real)",
      "location": "fixtures/people.csv:1-6",
      "scenario": "Names and national ID numbers described as copies of customer records are committed to the repo and would propagate to clones, CI, forks, git history and review vendors; the tests only need email.",
      "fix": "Replace with synthetic id,email rows or in-test data, purge from the branch history before merge, and add a CI guard against national_id data in fixtures."
    },
    {
      "severity": "P2",
      "evidence_level": "traced by static reading; reachability depends on callers not provided",
      "location": "exporter.py:10-12 (patch)",
      "scenario": "number=-1, size=2 returns rows[-2:-1] (a row from the end); size=0 always returns [], so a caller gets wrong or empty data with no error.",
      "fix": "Raise ValueError for number<0 or size<=0; test both."
    },
    {
      "severity": "P3",
      "evidence_level": "read from test code",
      "location": "tests/test_exporter.py:7,11",
      "scenario": "Relative fixture path fails with FileNotFoundError when tests run from a directory other than the repo root.",
      "fix": "Resolve the path from __file__ or build rows in-test."
    }
  ]
}
```