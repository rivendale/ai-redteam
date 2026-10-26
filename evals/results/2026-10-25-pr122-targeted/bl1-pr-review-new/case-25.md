# PR #57 Review: Paged Customer Export

**Review report (round 1 of 2)**

**REVIEWED:** PR #57. Head `b81d0e5`, merge base `4c6a912`, both as stated in PR.md. I reviewed `change.patch` against `base/` exactly as supplied. I had no tools, so I could not check that the patch matches `b81d0e5`, and any commit after `b81d0e5` is not reviewed.

**TIER:** High. The change adds a production customer export of email addresses (personal data). It also commits a fixture with names, emails and national ID numbers. The team's practice for exports is a second vendor's opinion, which agrees with the High tier's two rounds.

**REVIEWERS:**
- Round 1: this instance (Claude Opus 5.5). It is independent and did not write the change.
- Round 2 (second vendor): **not run.** I cannot dispatch it from here. No endpoint has been identified as approved for this data. `fixtures/people.csv` holds national ID numbers, so under Step 3 it must not go to a second vendor until someone names an approved endpoint for that data, for example a zero-retention key. If none exists, the review stops at round 1 and does not drop to a lower tier.
- Author: unknown. No commit trailers were provided.

**Scope checks**
- Supply-chain lens, OSV lookup and runtime/TLS lens: not applicable. The patch changes no dependencies, runtime or trust configuration.
- "Tests pass" is unverified. I could not run the tests. Reading them, I would expect them to pass, because they never exercise the defect in finding 1.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `exporter.py:11` (patch line `return rows[number * size:(number + 1) * size - 1]`) | **Off-by-one: the `- 1` drops the last row of every page.**<br>• With 5 rows and `size=2`, page 0 returns 1 row, page 1 returns 1 row and page 2 returns 1 row. Rows 2 and 4 are never exported.<br>• A full paged export silently omits one customer in every `size`.<br>• `size=1` returns nothing at all.<br>• The current tests miss it because they use `size=10` with 5 rows, so the slice `[0:9]` covers everything.<br>• P1 cannot be deferred. | Build 5 rows in the test with `email` values `e0`–`e4`. Assert `len(export_page(rows, 0, 2)) == 2`. Assert that the concatenation of pages 0–2 at `size=2` equals `["e0","e1","e2","e3","e4"]`. Fails today; passes once `- 1` is removed. |
| 2 | P1 | `fixtures/people.csv:1-6` | **Personal data committed to the repository.**<br>• The fixture is described as "a copy of real-format customer records" and contains names and `national_id` values.<br>• If any row comes from real records, merging puts national IDs into git history, every clone, CI artifacts and any review endpoint. This is hard to reverse.<br>• The values look synthetic (`example.test` domains, `900-` prefix), but provenance is not established.<br>• The request asked only for emails. The `national_id` and `name` columns are extra and nothing tests them.<br>• Becomes P0 if the data is real. | A repository check that fails if any file under `fixtures/` has a `national_id` column, or values matching a national-ID pattern. Replace the fixture with in-test synthetic rows that contain only `email`, or `id,email`. |
| 3 | P2 | `tests/test_exporter.py:6-12` | **Tests do not cover paging.**<br>• Both tests call page 0 with a page size larger than the dataset, so `page()` boundaries, later pages and the empty last page are untested.<br>• This is why "Tests pass" coexists with finding 1. | Tests for page 1 at `size=2`, the last partial page, a page past the end (expects `[]`), and complete coverage across all pages, as in finding 1. |
| 4 | P2 | `exporter.py:9-11` | **No validation of `number` or `size`.**<br>• With current code, `size=0` gives `rows[0:-1]`: every row except the last, not an empty page.<br>• Negative `number` or `size` give tail or near-full slices.<br>• If these come from a request parameter, one call can export almost the whole customer list, defeating paging.<br>• After fixing finding 1, `size<0` still slices from the end.<br>• I could not see the callers, so whether these values are request-controlled is unverified. | `assertRaises(ValueError, export_page, rows, 0, 0)`, the same for `size=-1` and `number=-1`. All fail today; they pass once inputs are validated as `number >= 0` and `size >= 1`, with an optional maximum `size`. |
| 5 | P3 | `tests/test_exporter.py:7,11` | **Fixture path depends on the working directory.**<br>• `"fixtures/people.csv"` is relative to the current directory, so the tests fail with `FileNotFoundError` when run from `tests/` or by a runner with a different working directory. | Run the suite from `tests/`. It fails today; it passes once the path is resolved from `__file__`, or the fixture is replaced by in-test rows. |

**FILES NEEDED BUT NOT PROVIDED:**
- Commit metadata and trailers for `b81d0e5`, to identify the author.
- CI check results for `b81d0e5`.
- Callers of `export_page` and `page`, to see where `number` and `size` come from.
- Provenance of `fixtures/people.csv`: synthetic, or derived from real customers.
- The list of endpoints approved for national-ID data, which round 2 needs.

---

**Close-out:** not written. The author adjudicates these findings, and a reviewer does not adjudicate its own.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1–5 | Pending (author) | — |

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION: do not merge.**
- Round 2 is missing. Step 2 states: "The tier's rounds are the review; a High-tier PR whose second round has not run is not reviewed." Round 2 has not run, and it needs an approved endpoint first (Step 3).
- The Step 8 gates are not met. Step 8 requires that "every round the tier requires has run, and every finding has a written decision". It also requires "no unresolved blocker remains", but two P1 findings (1 and 2) are open. Finally, "every expected check is present and green" cannot be confirmed because no CI results were provided.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "confirmed by reading code (slice arithmetic); not executed",
      "location": "exporter.py:11",
      "scenario": "page() slices rows[number*size:(number+1)*size-1], dropping the last row of every page; with 5 rows and size=2 rows 2 and 4 are never exported, size=1 returns nothing. Existing tests use size=10 over 5 rows and miss it.",
      "fix": "Use rows[number*size:(number+1)*size]; add a test that concatenated pages at size=2 equal all rows."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed present in diff; real-vs-synthetic provenance unverified (escalate to P0 if real)",
      "location": "fixtures/people.csv:1-6",
      "scenario": "Fixture described as a copy of real-format customer records commits names and national ID numbers to git history, clones, CI and review endpoints; the columns are not needed by the request or tests.",
      "fix": "Remove the fixture (purge from branch history); use in-test synthetic rows with only an email field; confirm provenance."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed by reading tests",
      "location": "tests/test_exporter.py:6-12",
      "scenario": "Tests only call page 0 with size larger than the dataset, so paging boundaries are untested and the off-by-one ships with 'tests pass'.",
      "fix": "Add tests for later pages, last partial page, page past end, and full coverage across pages."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed by reading code; caller exposure unverified",
      "location": "exporter.py:9-11",
      "scenario": "size=0 returns rows[0:-1] (nearly all rows); negative number/size return tail or near-full slices, letting one call bypass paging if parameters are request-controlled.",
      "fix": "Validate number >= 0 and size >= 1 (optionally a max size); raise ValueError otherwise."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed by reading tests",
      "location": "tests/test_exporter.py:7,11",
      "scenario": "Relative path 'fixtures/people.csv' makes tests fail with FileNotFoundError when run from another working directory.",
      "fix": "Resolve the path from __file__ or replace the fixture with in-test rows."
    }
  ]
}
```