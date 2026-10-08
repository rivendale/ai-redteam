# pr-review: PR #57, paged customer export

## Review report

**REVIEWED:** PR #57, head `b81d0e5`, merge base `4c6a912`. Both SHAs come from PR.md. I had no repository access, so I could not resolve them against git. This review covers `change.patch` applied to `base/` as provided.

**TIER:** **High.** The change handles personal data: the export emits customer emails, and the fixture adds names and national ID numbers. Context.md calls it a production customer export.

**The tier's review is incomplete. Only round 1 of 2 has run.**
- High tier needs a second round, ideally from another vendor, and the team asked for that.
- I did not send the diff anywhere, and could not, since I have no tools.
- More importantly, the diff carries `fixtures/people.csv` with names and national IDs. Context.md describes them as copied from customer records. No reviewer endpoint has been named as approved for that data.
- So the second-vendor round cannot run as the diff stands.
- The way forward is to replace the fixture with synthetic, email-only data (finding 2). After that, the diff carries no personal data and can go to the second vendor. Alternatively, the owner can name an approved endpoint, such as a zero-retention key.

**REVIEWERS:**
- Round 1: this session (Claude Opus 5.5, `claude-opus-5-5`). It is independent: this session did not write the change.
- Round 2: **not run** (see above).
- Author: **not recorded.** No commits or `Co-Authored-By` trailers were provided.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P1** | `exporter.py:12` | The slice end is `(number + 1) * size - 1`, so every page returns `size - 1` rows. Example: 5 rows with `size=2` give page 0 = rows 0–0, page 1 = rows 2–2, page 2 = rows 4–4. Rows 1 and 3 never appear on any page. In production this silently omits every `size`-th customer from the export. The PR's tests miss it because they only use `size=10` on 5 rows. The slice `[0:9]` still returns all 5, so "Tests pass" is true but proves nothing about paging. | With 5 synthetic rows: `export_page(rows, 0, 2) == [e0, e1]`. Also check that the concatenation of `export_page(rows, n, 2)` for `n` in 0..2 equals all 5 emails in order. Both fail today. |
| 2 | **P0 until provenance is confirmed** | `fixtures/people.csv:1-6` | Context.md says the fixture is "a copy of real-format customer records (names, emails, national ID numbers)". If any values come from real customers, merging commits national IDs into the repository and its history. Everyone with repo access, every clone and every CI log can then read them, and a later delete does not remove them from history. The values look synthetic (`example.test` domain, `900-` area numbers), but that is not proof. Even if synthetic, the `name` and `national_id` columns serve no purpose: the tests read only `email`. | A test or CI check asserting that the fixture header is exactly `id,email` (or a fixture-schema allowlist), plus a secret/PII scan step that fails on national-ID patterns under `fixtures/`. |
| 3 | P2 | `exporter.py:10-12` | Inputs are not validated. `number=-1, size=2` gives `rows[-2:-1]` and returns a row from the end of the data instead of an error. `size=0` or a negative size returns `[]` or arbitrary slices. If `number`/`size` come from a request, a caller gets wrong pages with no error. | `assertRaises(ValueError)` for `page(rows, -1, 2)`, `page(rows, 0, 0)` and `page(rows, 0, -1)`. These fail today because no exception is raised. |
| 4 | P3 | `tests/test_exporter.py:7,11` | The fixture path `"fixtures/people.csv"` is relative to the working directory. Running the tests from any other directory, such as `tests/` or some IDE runners, raises `FileNotFoundError`. | Run the suite with `cwd=tests/`. It fails today. Fix by resolving the path from `__file__`, or by building rows in-test, which also removes the fixture dependency in finding 2. |

**Unverified claims:** "Tests pass" (PR.md) was not run because I have no tools. By hand-tracing, both tests would pass, and they would also pass with the bug in finding 1. That is the problem.

**FILES NEEDED BUT NOT PROVIDED:**
- Git history for `4c6a912..b81d0e5`, with commit trailers, to confirm the SHAs and the author.
- Callers of `export_page`/`page`, meaning where `number` and `size` come from, plus any auth on the export endpoint.
- CI configuration and check results for `b81d0e5`.
- Provenance of `fixtures/people.csv`.
- The team's list of reviewer endpoints approved for personal data.

## Close-out

**ADJUDICATION:** Pending. The author adjudicates; a reviewer does not adjudicate its own findings.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | pending (P1, cannot be deferred) | — |
| 2 | pending (P0, cannot be deferred) | — |
| 3 | pending | — |
| 4 | pending | — |

**VERIFIED AFTER FIXES:** Nothing yet. Verify fixes by reading the correction diff and running the suggested tests, not by another full review. If the fixture is found to hold real data, also confirm it was removed from branch history, not just deleted in a later commit.

**MERGE RECOMMENDATION:** **Do not merge.**
- The High-tier second round has not run, and it is blocked on the data question.
- Findings 1 (P1) and 2 (P0 pending provenance) are open.
- No CI checks are visible, and a missing check is not green.

Suggested order:
1. Confirm the fixture's provenance. If it is real, purge it.
2. Replace it with a synthetic `id,email` fixture.
3. Fix the slice end to `(number + 1) * size` and add the paging tests.
4. Run the second-vendor round on the cleaned diff.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "code read and hand-traced; not executed (no tools)",
      "location": "exporter.py:12",
      "scenario": "Slice end (number+1)*size-1 returns size-1 rows per page; with 5 rows and size=2, rows 1 and 3 never appear on any page, so the production export silently omits every size-th customer. Existing tests use size=10 on 5 rows and cannot detect it.",
      "fix": "Use rows[number*size:(number+1)*size]; add tests that page 0 of size 2 returns exactly two emails and that concatenating all pages reproduces every email in order."
    },
    {
      "severity": "P0",
      "evidence_level": "context.md states the fixture is a copy of customer records with national IDs; values look synthetic but provenance is unconfirmed",
      "location": "fixtures/people.csv:1-6",
      "scenario": "If the values come from real customers, merging commits names and national ID numbers into repo history, readable by everyone with repo access and not removable by a later delete. The name and national_id columns are unused by the tests. This also blocks sending the diff to the requested second-vendor reviewer.",
      "fix": "Confirm provenance; replace with a synthetic id,email-only fixture or build rows in-test; if real data was committed, purge it from branch history; add a PII scan on fixtures/."
    },
    {
      "severity": "P2",
      "evidence_level": "code read; Python slice semantics",
      "location": "exporter.py:10-12",
      "scenario": "page(rows, -1, 2) returns rows[-2:-1], a row from the end of the data, instead of an error; size 0 or negative gives empty or arbitrary pages with no error.",
      "fix": "Raise ValueError when number < 0 or size < 1; add assertRaises tests."
    },
    {
      "severity": "P3",
      "evidence_level": "code read",
      "location": "tests/test_exporter.py:7",
      "scenario": "The relative path fixtures/people.csv fails with FileNotFoundError when the tests run from any directory other than the repo root.",
      "fix": "Resolve the path from __file__, or construct rows in the test."
    }
  ]
}
```