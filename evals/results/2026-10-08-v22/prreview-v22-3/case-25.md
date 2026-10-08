# pr-review: PR #57, paged customer export

## Before the report: scope and limits of this review

- **Target not independently frozen.** I have no tools in this session, so I could not check out the head, confirm the SHAs or run the tests. The SHAs below are as stated in `PR.md`, and everything here comes from reading `change.patch` against `base/exporter.py`.
- **High tier needs two rounds, and only one ran.** This is round 1. The context asks for a second opinion from another vendor's model, and that round has not run.
- **The data gate (Step 3) blocks the second round as briefed.** `fixtures/people.csv` holds records described as copies of real-format customer data, including national ID numbers. No endpoint has been named as approved for that data. I have not sent it anywhere, and it should not go to a second vendor until the owner names an approved endpoint. A practical route is to run round 2 on the diff with the fixture replaced by synthetic rows. That route makes sense anyway, given finding 2.
- **The PR is therefore not reviewed under this skill's rules** until round 2 runs.

---

## Review report

**REVIEWED:** PR #57, head `b81d0e5`, merge base `4c6a912`. Both SHAs are as stated in PR.md and were not verified against a checkout.

**TIER:** High. The PR touches personal data in two ways:
- the production customer export emits email addresses;
- the PR commits a fixture containing names, emails and national ID numbers.

**REVIEWERS:**
- **Round 1:** this session (Claude Opus 5.5, `claude-opus-5-5`). It did not author the change and has no memory of writing it.
- **Round 2:** not run. It is pending an approved endpoint from a second vendor.
- **Author:** unknown. No commit trailers were provided.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `exporter.py:12` | The slice end is `(number + 1) * size - 1`, so every page drops its last row. With 5 rows and `page(rows, 0, 2)`, it returns only row 1, and page 1 returns only row 3. Rows 2 and 4 are never exported on any page. In production, roughly 1 in `size` customers is silently missing from the export. The PR's tests use `size=10` against 5 rows, where the slice `[0:9]` still returns all 5, so the bug is invisible. | With 5 rows: `export_page(rows, 0, 2)` returns the first 2 emails, `export_page(rows, 1, 2)` returns the next 2, and `export_page(rows, 2, 2)` returns the last 1. Also assert that concatenating all pages returns every email exactly once. Fix: `rows[number * size:(number + 1) * size]`. |
| 2 | P0 until shown to be synthetic | `fixtures/people.csv:1-6` | The PR commits customer records with names, emails and national ID numbers into the repository. If they are real, merging puts national IDs in git history and in every clone, CI cache and mirror. A later delete cannot undo that. Even if they are synthetic, the export only reads `email`, so the `name` and `national_id` columns add risk for no benefit. The context's own phrase, "copy of real-format customer records", leaves their status unproven. | Data check: grep the fixture against the production customer store, or obtain written confirmation from the data owner that every row is generated. Fix: build rows in the test, or use a fixture with only `id,email` on reserved domains. |
| 3 | P2 | `exporter.py:10-12` | There is no validation of `number` or `size`. With `size=0`, the current code computes `rows[0:-1]` and returns every row except the last, instead of nothing. With a negative `number`, it returns rows from the tail (for example, `number=-2, size=2` gives `rows[-4:-3]`). If a caller passes user-supplied paging parameters, the export returns wrong or unexpected rows. No caller is in the diff, so I cannot confirm whether this is reachable. | `page(rows, 0, 0)` returns `[]` or raises `ValueError`, and `page(rows, -1, 2)` raises `ValueError`. |
| 4 | P2 | `tests/test_exporter.py:6-12` | The request says "with tests", but neither test exercises paging. Both tests use page 0 with a size larger than the data set. There is no case for a second page, a page size that divides the data exactly, a page past the end, or an empty input. The claim "Tests pass" is true and still proves nothing about paging, as finding 1 shows. | The tests from finding 1, plus `export_page(rows, 5, 2) == []` and `export_page([], 0, 10) == []`. |
| 5 | P3 | `tests/test_exporter.py:7,11` | `load_people("fixtures/people.csv")` resolves relative to the working directory. Running the tests from any directory other than the repository root, for example `python -m unittest` from `tests/` or some CI layouts, raises `FileNotFoundError`. | Run the suite from `tests/` and expect it to pass. Fix: build the path from `Path(__file__).parent`, or drop the file fixture (see finding 2). |

**FILES NEEDED BUT NOT PROVIDED:**
- **The caller of `export_page`** (endpoint, job or CLI). I need it to judge who can trigger the export, the authorization around it, and whether `number` and `size` come from user input (finding 3).
- **CI configuration and the list of required checks**, to confirm the checks that are expected.
- **The team's list of models and endpoints approved for personal data**, which Step 3 requires before round 2.
- **Any existing tests or fixtures policy** in the repository.

---

## Close-out

Not written. The author adjudicates these findings, and a reviewer never adjudicates its own findings. The table below is the template for the author.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | pending (P1: cannot be deferred) | |
| 2 | pending (P0: cannot be deferred) | |
| 3 | pending | |
| 4 | pending | |
| 5 | pending | |

**VERIFIED AFTER FIXES:** Nothing yet. Each fix needs a regression test that fails before the fix and passes after it, plus a targeted read of the fix's own diff.

**MERGE RECOMMENDATION: do not merge.**
- The High tier's second round has not run, and it is blocked on an approved endpoint for personal data.
- Finding 1 (P1) silently drops customers from a production export.
- Finding 2 (P0 pending confirmation) commits national ID numbers to the repository.
- The expected checks have not been seen.
- **Owner decisions still open:**
  - which endpoint is approved for round 2;
  - whether the fixture data is real.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "read in code; behavior derived from slice arithmetic, not run",
      "location": "exporter.py:12",
      "scenario": "Slice end (number+1)*size-1 drops the last row of every page; with 5 rows and size 2, rows 2 and 4 are never exported. Existing tests use size 10 over 5 rows, so they still pass.",
      "fix": "Use rows[number*size:(number+1)*size]; add multi-page tests asserting every row appears exactly once across pages."
    },
    {
      "severity": "P0",
      "evidence_level": "read in diff; real vs synthetic status unconfirmed (context calls them copies of real-format customer records)",
      "location": "fixtures/people.csv:1-6",
      "scenario": "Commits names, emails and national ID numbers into git history; if real, this is an irreversible personal-data exposure to every clone, CI cache and mirror. The export only needs the email column.",
      "fix": "Remove the fixture before merge; generate synthetic rows with only id and email in the test, or confirm with the data owner in writing that all rows are generated."
    },
    {
      "severity": "P2",
      "evidence_level": "read in code; reachability unknown because no caller is in the diff",
      "location": "exporter.py:10-12",
      "scenario": "size=0 returns rows[0:-1] (all but the last row); a negative page number returns tail rows; user-supplied paging parameters yield wrong exports.",
      "fix": "Validate number >= 0 and size > 0 (raise ValueError); add tests for these cases."
    },
    {
      "severity": "P2",
      "evidence_level": "read in tests",
      "location": "tests/test_exporter.py:6-12",
      "scenario": "Tests only read page 0 with a size larger than the data set, so paging is never exercised and the off-by-one passes.",
      "fix": "Add tests for second page, exact-multiple size, page past end, and empty input."
    },
    {
      "severity": "P3",
      "evidence_level": "read in tests, not run",
      "location": "tests/test_exporter.py:7",
      "scenario": "The relative path fixtures/people.csv fails with FileNotFoundError when the tests run from any directory other than the repository root.",
      "fix": "Resolve the path from Path(__file__).parent, or build the rows in the test."
    }
  ]
}
```