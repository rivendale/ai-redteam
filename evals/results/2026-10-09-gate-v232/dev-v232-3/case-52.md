**Review note:** I reviewed this myself in the same context, with no tools. Anchoring risk applies, and nothing here was executed. Re-run it in a fresh session with tools before release.

**VERDICT: REWORK.** Two of the three listings put the customer-supplied `sort` value straight into the SQL text with no check. Any logged-in customer can reach that, and the `orders` table holds other customers' rows and notes.

**CONFIDENCE: medium.** The defect is plain from reading the code. I could not run the reproductions, and no tests were supplied.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, admin.py, db.py, exports.py, reports.py.
- **Not seen:**
  - Tests. This matters: nothing shows the change was exercised.
  - The router or caller that builds `request`. This matters a little: it decides whether `sort` arrives raw from the query string. context.md says it does.
  - Production DB engine and schema. This does not change the verdict, because db.py is a stand-in.

**COVERAGE**
- **Scope:** all four supplied files, read in full.
- **Checked:**
  - `admin.list_orders`
  - `exports.export_orders`
  - `reports.totals_report`
  - `db.query`
  - The request and context documents
- **Not checked:**
  - The test suite (not supplied)
  - The request-parsing layer (not supplied)
  - Runtime behaviour (no tools)

**SEATS AND GATE**
- Only the local same-context reviewer ran. No subagent or cross-vendor seat was available.
- Sensitivity: the work contains no real personal data. The fixture rows are synthetic.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (traced) | B | `exports.py:8` | `sort` comes from the request and goes into `order by {sort}` unchecked. The `?` parameter protects only `customer`. | A logged-in customer sends a crafted `sort`. `ORDER BY` accepts arbitrary expressions, so the customer can influence the query beyond ordering. That includes inferring data from rows that are not theirs, such as other customers' `secret_note`. This crosses the customer-isolation boundary the endpoint promises ("own orders"). | **Fix:** validate against an allowlist before building SQL, as admin.py does (`{"id","customer","total"}`). Better still, map each allowed key to a fixed column string. **Reproduction (not run):** `export_orders({"user":"ann","sort":"no_such_column"})`. Expected: `ValueError` raised before any query. Observed by trace: the raw value reaches SQLite, which raises `OperationalError: no such column`. That proves request text becomes SQL text. **Test:** patch `query`, then assert it is never called for any key outside the allowlist. | y/y/y/y |
| F2 | Critical | CONFIRMED (traced) | B | `reports.py:8` | This is a sibling of F1 with the same root cause: `order by {sort}` is unvalidated. | The same scenario applies through the summary report. | **Fix:** use an allowlist that fits this query, `{"customer","total"}`, because `id` is not in the grouped output. **Reproduction (not run):** `totals_report({"user":"ann","sort":"no_such_column"})`. Expected: `ValueError`. Observed by trace: `OperationalError` from the DB. | y/y/y/y |
| F3 | Low | CONFIRMED | B | `admin.py:14`, `exports.py:8` | Sorting on `total` or `customer` has no tie-breaker. | Rows 3 and 5 both have total 30.0, so their relative order can change between calls and pages. | **Fix:** append `, id` to the order clause. **Reproduction:** `list_orders({"role":"admin","sort":"total"})`. The order of ids 3 and 5 is not guaranteed by SQL. | y/y/n/n |

**Siblings searched (F1, F2):** every f-string or format call that builds SQL in the four files. There are three in total. admin.py:14 is the only one guarded, by `SORTABLE` at admin.py:12-13, and that guard holds. db.py has no string building.

**Security boundary (F1, F2):**
- **Principal:** any logged-in customer
- **Input:** the `sort` request parameter
- **Failed control:** no allowlist on these two paths
- **Boundary crossed:** one customer's data to another's
- **Resource exposed:** other customers' rows in the `orders` table, including `secret_note`

## Needs validation
- **Whether the router coerces or limits `sort`.** context.md implies it arrives raw. The router code would settle it.
- **Whether production uses parameter-unsafe dynamic SQL elsewhere.** Only these files were supplied.

## Refuted
- **"admin.py is injectable."** Refuted: `sort not in SORTABLE` raises before the query at admin.py:12-13. The default `"id"` is in the set.
- **"Customers can reach the admin list."** Refuted: the role check at admin.py:9-10 runs first.

## What holds up
- admin.py's allowlist pattern and role check.
- The `customer = ?` parameterisation in both customer endpoints.

## Unverified claims
- No tests exist in what was supplied, so nothing shows any sort path was exercised. Add the allowlist rejection tests above.
- Before trusting those tests, confirm each one fails when the allowlist check is removed.

## Questions for the author
1. Was the admin.py allowlist meant to be shared by all three listings?
2. Are there tests that were not included?

## Decision-maker summary
Do not release. Two customer-facing endpoints let a customer inject text into the database query, which risks exposing other customers' orders and notes. The fix is small: reuse the existing allowlist on all three listings, and add tests that reject unknown sort keys.

## Owner summary
The new sorting feature checks its input on the staff page but not on the two customer pages. As a result, a customer could misuse the sort option to see information belonging to other customers. Applying the same simple check everywhere, and adding a test for it, fixes the problem before release.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "tests", "status": "not_seen", "matters": true},
    {"item": "request router", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "admin.py", "kind": "file"}, {"unit": "db.py", "kind": "file"},
      {"unit": "exports.py", "kind": "file"}, {"unit": "reports.py", "kind": "file"},
      {"unit": "request.md", "kind": "document"}, {"unit": "context.md", "kind": "document"}
    ],
    "not_checked": [
      {"unit": "tests", "reason": "not_supplied"},
      {"unit": "runtime behaviour", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "exports.py:8",
     "scenario": "A logged-in customer supplies a crafted sort value that is interpolated into ORDER BY unvalidated, letting them influence the query and infer other customers' rows.",
     "fix": "Validate sort against an allowlist mapped to fixed column names before building SQL; add a test that query is never called for keys outside it.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "export_orders({'user':'ann','sort':'no_such_column'}): expect ValueError; by trace SQLite raises OperationalError, showing raw input reaches SQL. Not executed (no tools).",
     "security": true,
     "boundary": {"principal": "any logged-in customer", "input": "sort request parameter", "control": "no allowlist on this path", "crossed": "customer to other customers' data", "resource": "orders rows incl. secret_note"},
     "siblings_searched": {"searched": "all SQL built with f-strings in the four files", "found": "reports.py:8 (F2); admin.py:14 is guarded"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "reports.py:8",
     "scenario": "Same as F1 via the summary report endpoint.",
     "fix": "Allowlist {'customer','total'} before building SQL; add rejection test.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "totals_report({'user':'ann','sort':'no_such_column'}): expect ValueError; by trace SQLite raises OperationalError. Not executed (no tools).",
     "security": true,
     "boundary": {"principal": "any logged-in customer", "input": "sort request parameter", "control": "no allowlist on this path", "crossed": "customer to other customers' data", "resource": "orders rows incl. secret_note"},
     "siblings_searched": {"searched": "all SQL built with f-strings in the four files", "found": "exports.py:8 (F1); admin.py:14 is guarded"}},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "admin.py:14",
     "scenario": "Sorting by total with ties (ids 3 and 5 at 30.0) gives an unstable order across calls.",
     "fix": "Append ', id' as a tie-breaker in every ORDER BY.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "list_orders({'role':'admin','sort':'total'}): relative order of ids 3 and 5 is not guaranteed."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "request router (not supplied)",
     "suspicion": "sort may arrive raw from the query string.",
     "unresolved_fact": "Whether the router restricts or coerces the sort parameter."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "admin.py ORDER BY is injectable.", "evidence": "admin.py:12-13 rejects any sort not in SORTABLE before the query."},
    {"id": "C2", "candidate": "Customers can reach the admin list.", "evidence": "admin.py:9-10 raises PermissionError unless role is admin."}
  ]
}
```