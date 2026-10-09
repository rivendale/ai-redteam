**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools in this session: nothing was executed. Findings below are tied to exact lines. Reproductions are limited to benign inputs that show the defect; they do not include exploit payloads.

**VERDICT: REWORK.** Two of the three listings put a customer-controlled `sort` value directly into SQL. Any logged-in customer can therefore reach a table that holds other customers' rows and private notes.

**CONFIDENCE: medium.** This is a same-context review with no execution. The tests, the request layer and the error handling were not supplied.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, admin.py, db.py, exports.py, reports.py.
- **Not seen:** tests, which matters because there is no evidence the change was exercised. The HTTP/request layer and error-to-response mapping were also not supplied. That matters for S1, because it decides whether SQL errors reach the customer.
- **Not seen:** callers of the three functions. This does not change the verdict.

**COVERAGE**
- **Checked:** `admin.py:list_orders`, `exports.py:export_orders`, `reports.py:totals_report`, `db.py:query`, and the schema in `db.py`.
- **Not checked:** tests, the request layer and error handling, because they were not supplied.

**SEATS AND GATE:** Single same-context reviewer. No subagent or cross-vendor seats were available. Sensitivity gate: no real personal data. db.py holds synthetic sample rows only.

## Pass 1: Reconstruct

The change adds a `sort` request parameter to three listings. It interpolates that value into `ORDER BY` with f-strings, because SQL placeholders cannot bind identifiers. For this to be correct, every value reaching `ORDER BY` must be limited to known column names. Only admin.py enforces that, with `SORTABLE` at admin.py:4 and the check at admin.py:12-13. exports.py and reports.py, which are the two endpoints every customer can reach, have no allowlist.

Tracks: B (code) and A (requirement fit).

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (exact line) | B | exports.py:9 | `sort` from the request is interpolated into `order by {sort}` with no allowlist. | Any logged-in customer sends a crafted `sort`. `ORDER BY` accepts expressions and subqueries, so the customer can affect the query beyond sorting. The `where customer = ?` filter does not stop a subquery from reading other customers' rows, including `secret_note`, for example by inferring values through the order of results. | Add a per-endpoint allowlist, e.g. `{"id","total"}`, and reject anything else before building SQL, as admin.py:12-13 does. **Repro (benign):** `export_orders({"user":"ann","sort":"no_such_col"})`. Expected: a validation error before any query runs. On this code: sqlite raises `OperationalError: no such column`, which shows raw input reaches the SQL text. Add this as a failing test, plus a test that each allowed value works. | a✓ b✓ c✓ d✓ |
| F2 | Critical | CONFIRMED (exact line) | B | reports.py:9 | Same defect in `order by {sort}`, default `"customer"`. | Same as F1, on the totals report. | Use an allowlist of `{"customer","total"}`, which are the report's output columns. **Repro:** `totals_report({"user":"ann","sort":"no_such_col"})`. Expected: a validation error. Observed: sqlite `OperationalError`. | a✓ b✓ c✓ d✓ |
| F3 | Low | CONFIRMED | A/B | admin.py:4 vs exports.py, reports.py | The allowlist is local to admin.py, so the same rule is applied on 1 of 3 paths. Each endpoint also needs a different set: the report's columns are `customer` and `total`, not `id`. | A future listing copies the exports pattern and ships unvalidated input again. | Move one helper, e.g. `order_clause(sort, allowed)`, into db.py and call it from all three. | a✓ b✓ c✗ d✗ |

The F1 and F2 severity confirm-or-refute round, argued as the strongest defender would:
- **"Only the customer's own rows are selected."** That is false for `ORDER BY`, which can contain any SQL expression, including subqueries over the full `orders` table.
- **"sqlite3 blocks stacked statements."** True, since `execute` runs one statement. But that is not needed for a read-only data leak.
- **Result:** both findings hold.

## NEEDS VALIDATION
- **S1:** Whether sqlite error text such as column names reaches the client. To settle it, check how the request layer maps uncaught exceptions to responses.
- **S2:** Whether "sorting" was meant to include direction (asc/desc). The request does not say. Ask the requester. If yes, add direction as a separate allowlisted parameter, never as free text.

## REFUTED
- **"admin.py is injectable too."** Refuted. admin.py:12-13 rejects any value not in `SORTABLE` before the f-string at line 14.
- **"admin.py lacks authorization."** Refuted. admin.py:9-10 checks the role first, on the only path.

## WHAT HOLDS UP
- admin.py is correct: it checks the role first, then the allowlist, then interpolates only a fixed identifier.
- The customer filter in exports.py and reports.py is properly parameterised (`?` with `request["user"]`).
- `db.query` passes params correctly.

## UNVERIFIED CLAIMS
- **That the change was tested.** No tests were supplied. To confirm: provide tests and check that the F1/F2 repros fail on the current code.

## QUESTIONS FOR THE AUTHOR
1. Should sorting support descending order (S2)?
2. Are raw database errors returned to clients (S1)?

## DECISION-MAKER SUMMARY
Do not release. The export and summary-report endpoints let any customer inject SQL through `sort`, which exposes other customers' orders and notes. The fix is small: apply the admin listing's allowlist pattern to both endpoints and add tests that fail today.

## OWNER SUMMARY
The new sorting option on two of the three order pages accepts any text a customer types and passes it straight to the database. A customer could use it to see other customers' orders and private notes. It needs a short fix, limiting sorting to a few known choices, before it goes live.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "tests", "status": "not_seen", "matters": true},
    {"item": "request layer / error handling", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "synthetic sample data only"},
  "coverage": {
    "checked": [
      {"unit": "admin.py", "kind": "file"}, {"unit": "admin.py:list_orders", "kind": "function"},
      {"unit": "exports.py", "kind": "file"}, {"unit": "exports.py:export_orders", "kind": "function"},
      {"unit": "reports.py", "kind": "file"}, {"unit": "reports.py:totals_report", "kind": "function"},
      {"unit": "db.py", "kind": "file"}, {"unit": "db.py:query", "kind": "function"}
    ],
    "not_checked": [
      {"unit": "tests", "reason": "not supplied"},
      {"unit": "request layer", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "exports.py:9",
     "scenario": "Any logged-in customer supplies a crafted sort value; it is interpolated into ORDER BY unvalidated, letting a subquery read other customers' rows including secret_note.",
     "fix": "Reject sort values outside a per-endpoint allowlist before building SQL, as admin.py:12-13 does.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "export_orders({'user':'ann','sort':'no_such_col'}): expect a validation error; observe sqlite OperationalError, showing raw input reaches the SQL."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "reports.py:9",
     "scenario": "Same unvalidated ORDER BY interpolation on the totals report, reachable by any customer.",
     "fix": "Allowlist {'customer','total'} and reject anything else.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "totals_report({'user':'ann','sort':'no_such_col'}): expect a validation error; observe sqlite OperationalError."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "admin.py:4",
     "scenario": "The allowlist exists on one of three paths; a future listing copying exports.py repeats the injection.",
     "fix": "Shared order_clause(sort, allowed) helper in db.py used by all listings.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "exports.py:9, reports.py:9",
     "suspicion": "sqlite error text may be returned to clients, exposing schema.",
     "unresolved_fact": "How the request layer maps uncaught exceptions to responses."},
    {"id": "S2", "status": "needs_validation", "track": "A", "location": "request.md",
     "suspicion": "Sort direction may be expected but is unsupported.",
     "unresolved_fact": "Whether the requester wants asc/desc."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "admin.py is injectable via sort.", "evidence": "admin.py:12-13 rejects values not in SORTABLE before interpolation at line 14."},
    {"id": "C2", "candidate": "admin.py lacks authorization.", "evidence": "admin.py:9-10 checks role == 'admin' before any query."}
  ]
}
```