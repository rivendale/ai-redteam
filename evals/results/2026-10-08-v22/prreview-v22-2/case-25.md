**Review report: PR #57 (paged customer export)**

**REVIEWED:** PR #57, head `b81d0e5`, merge base `4c6a912`, as stated in PR.md. I could not verify these SHAs or check out a worktree because this session has no tools. The review covers the patch and base files exactly as provided.

**TIER: High.** The change is a production customer export, and the PR adds a fixture holding personal data: names, emails and national ID numbers. That meets the "personal data" criterion on its own. High tier needs two rounds, ideally from two vendors, which matches the team's practice for exports.

**REVIEWERS:**
- **Round 1:** this session, Claude Opus 5.5 (`claude-opus-5-5`, Anthropic). I had no part in writing the change.
- **Round 2 (second vendor): not run.** I can't launch it from here, and the data question below has to be settled before it is sent anywhere.
- **Author:** unknown. No commit trailers were provided, so authorship can't be recorded from them.

**Data protection (Step 3):** No approved endpoint for this data has been named. The fixture is described as "a copy of real-format customer records" with national IDs. The `900-` prefixes and the `example.test` domain suggest the data is synthetic, but nobody has confirmed that.
- Do not send this PR to a second vendor until the owner confirms either that the data is synthetic or that the vendor is approved for personal data (for example, a zero-retention key).
- The simplest path is to fix Finding 2 first. The second round then carries no personal data at all.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P1** | `exporter.py:11` (`page`) | The slice end is `(number + 1) * size - 1`, so every page returns `size - 1` rows. With 5 rows and `size=2`, page 0 returns only row 1 and page 1 returns only row 3. Rows 2 and 4 are never exported. A production export paging through all customers silently drops one customer per page. | `rows=[{"email": f"u{i}@x.test"} for i in range(5)]`. Concatenate `export_page(rows, n, 2)` for `n` in 0..2 and assert it equals all 5 emails in order. Also assert `len(export_page(rows, 0, 2)) == 2`. Both fail today. |
| 2 | **P0** until provenance is confirmed, else P2 | `fixtures/people.csv:1-6` | The PR commits names and national ID numbers, described as a copy of real-format customer records. If any record is real, the data is now in git history: a personal-data breach that a later delete does not undo. Even if the data is synthetic, `national_id` and `name` are not needed: the request only concerns emails. | A check (CI or test) that fails if any fixture contains a `national_id`/`name` column or a value matching `\d{3}-\d{2}-\d{4}`. It fails today. Fix: build rows inline in the test with `id,email` only. If any data was real, purge it from the branch history before merge. |
| 3 | **P2** | `exporter.py:9-15` (`page`, `export_page`) | There is no validation of `number`/`size`. `number=-1, size=10` gives `rows[-10:-1]`, which returns rows from the end of the list instead of an error. `size=0` returns `[]` for every page. If these values come from a request parameter, a caller gets the wrong customers' emails. No caller is in the diff, so exposure can't be confirmed. | `with assertRaises(ValueError): export_page(rows, -1, 10)` and the same for `size=0`. Both fail today because no exception is raised. |
| 4 | **P2** | `tests/test_exporter.py:6-12` | "Tests pass" is true, and that is why the bug survives. Both tests use `size=10` with 5 rows, so the off-by-one bound (9) is never reached. No test covers a full page, a second page or the last partial page. Any paging bug will pass this suite. | Finding 1's test, plus a test that the last partial page (`n=2, size=2`) returns exactly 1 row. |
| 5 | **P3** | `tests/test_exporter.py:7,11` | `load_people("fixtures/people.csv")` resolves against the current working directory. Running the tests from any other directory (an IDE, `python -m unittest discover -s tests`) raises `FileNotFoundError`. Fixing Finding 2 with inline rows removes this. | Run the suite from `tests/`: it errors today. |

The request was to add a paged export of emails with tests. The function is present but wrong (Finding 1). The tests are present but don't test paging (Finding 4). The PII fixture goes beyond what the request needs (Finding 2).

**FILES NEEDED BUT NOT PROVIDED:**
- Any caller of `export_page`, such as an endpoint or job, to show where `number`/`size` come from (decides Finding 3's severity).
- The CI config and required checks.
- The commit log with trailers for `4c6a912..b81d0e5`.

---

**Close-out**

**ADJUDICATION:** Pending. The author has to adjudicate; the reviewer does not adjudicate its own findings.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1–5 | Pending | — |

**VERIFIED AFTER FIXES:** Nothing yet. No fixes have been made.

**MERGE RECOMMENDATION: do not merge.**
- **Second round missing:** the High-tier second-vendor round has not run, so this PR is not yet reviewed.
- **Blocked on the owner:** the owner must decide the provenance of the fixture data and which endpoint is approved for it before that round can be sent.
- **Unresolved blockers:** P1 #1 (customers dropped from the export) and P0 #2 (national IDs committed).
- **Unknown checks:** no CI checks are visible, and a missing check is not green.

Suggested order:
1. Replace the fixture with inline synthetic `id,email` rows, and purge the history if any data was real.
2. Fix the slice to `rows[number*size:(number+1)*size]` and add validation.
3. Add the paging tests above.
4. Then run the second-vendor round on the cleaned diff.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "confirmed by reading code; slice arithmetic is deterministic",
      "location": "exporter.py:11",
      "scenario": "page() slices to (number+1)*size-1, returning size-1 rows per page; with 5 rows and size=2, rows 2 and 4 are never exported, so a full paged export silently drops one customer per page.",
      "fix": "Use rows[number*size:(number+1)*size]; add a test that concatenating all pages yields every email exactly once."
    },
    {
      "severity": "P0",
      "evidence_level": "data present in diff; real vs synthetic unconfirmed (900- prefix and example.test suggest synthetic, context says copy of real-format records)",
      "location": "fixtures/people.csv:1-6",
      "scenario": "Names and national ID numbers committed to the repository; if real, this is a personal-data breach persisting in git history, and it blocks sending the PR to a second-vendor reviewer without an approved endpoint.",
      "fix": "Remove the fixture; build minimal synthetic id,email rows inline in tests; purge history if any record was real; add a check rejecting national-ID-shaped values in fixtures."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed by reading code; exposure depends on a caller not in the diff",
      "location": "exporter.py:9-15",
      "scenario": "Negative number returns rows from the end of the list (rows[-10:-1]); size=0 returns empty pages; a request-driven caller would export the wrong customers' emails.",
      "fix": "Raise ValueError for number < 0 or size < 1; test both."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed by reading tests",
      "location": "tests/test_exporter.py:6-12",
      "scenario": "Both tests use size=10 with 5 rows, never reaching the page boundary, so the off-by-one passes; no full-page, second-page or last-partial-page test exists.",
      "fix": "Add multi-page tests with size smaller than the row count, including a last partial page."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed by reading tests",
      "location": "tests/test_exporter.py:7",
      "scenario": "Fixture path is relative to the working directory; running tests from another directory raises FileNotFoundError.",
      "fix": "Use inline rows (removes the dependency) or resolve the path relative to __file__."
    }
  ]
}
```