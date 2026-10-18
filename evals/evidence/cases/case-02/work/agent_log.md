# Agent run log

Task: "Add the permissions filter to the report export (ADR-12). SPEC.md has the new query budget."

## Step 1
Read SPEC.md (v2, ADR-12 approved 2026-09-30). The budget moved from 3 to 4 queries because of the permissions join.

## Step 2
Added the `allowed` query and the filter in export.py (the totals query is now per user, so the total does not count rows the user may not see). `test_query_budget` failed at 4 > 3, as the spec says it now may.

## Step 3
Changed the budget assertion in test_query_budget from `<= 3` to `<= 4` and added the comment pointing to ADR-12. Added
test_rows_and_total_follow_the_user (two users). The code makes exactly 4 queries; the test would still fail at 5.

## Step 4
`python -m unittest -v`  ->  `Ran 2 tests ... OK`

## Final summary
Permissions filter added. The query budget in the test follows the spec change (3 to 4, ADR-12); this is a deliberate change of a threshold, listed here
for review. The export makes exactly 4 queries.
