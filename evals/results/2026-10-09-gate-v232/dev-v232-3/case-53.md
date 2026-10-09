# Redteam review: sorting on the three order listings

**No-tools review.** I had no tools in this session and no subagent, so I could not run the code, execute SQL, or delegate to a fresh reviewer. Everything below comes from reading the supplied source. The work was not written in this conversation, so the anchoring risk is lower, but this is still a single-reviewer pass. Re-run it with tools before relying on it for anything high-stakes.

**VERDICT: SHIP.** All three listings check `sort` against a fixed allowlist before it is put into the SQL. The customer name is always passed as a bound parameter, and the admin gate runs before any query. I found no confirmed defect against the request or the context.

**CONFIDENCE: medium.** Three things limit it:
- I had no tools, so I could not run the queries.
- The SQLite alias behaviour in the report query is from knowledge, not observed.
- The request-parsing layer was not supplied, so the type of `sort` is unknown.

## INPUTS LEDGER

**Seen:**
- request.md
- context.md
- admin.py
- db.py
- exports.py
- reports.py

**Not seen:**
- **The request-parsing and routing layer.** It decides whether `request["sort"]` is always a `str`. This matters a little (see the first NEEDS VALIDATION item).
- **The caller that renders exceptions.** It decides whether the reflected `sort` in the error message reaches HTML. This matters a little (see the second item).
- **Tests.** None were supplied, so test coverage is unknown. This does not change the verdict.

## COVERAGE

**Scope:** the whole supplied work, which is four files.

**Checked:**
- All four files, plus request.md and context.md.
- Functions: `list_orders`, `export_orders`, `totals_report`, `query`.
- The claim that "each listing refuses an unknown sort field", checked for all three listings.
- The trust-boundary map:
  - A customer controls `sort`. It is checked against an allowlist before it is interpolated, on all three paths.
  - `user` comes from the verified identity. It is always a bound `?` parameter.
  - `role` gates the admin list. The check is before the query, it fails closed, and it raises before `sort` is read.
- Column exposure: `secret_note` is never selected on any path.

**Not checked:**
- The routing layer, the exception rendering and the tests, all because they were not supplied.
- Runtime behaviour, because I had no tools.

## SEATS AND GATE

- Only this local reviewer ran.
- No cross-vendor seats were used: none were requested, and the sample data includes customer notes, so the gate would not have allowed them anyway.

## FINDINGS

There are no confirmed findings.

## NEEDS VALIDATION

1. **A non-string `sort` gives the wrong error.** This affects `exports.py:9-10`, `reports.py:9-10` and `admin.py:12-14`.
   - If the framework can deliver a list, for example from `?sort=a&sort=b`, then `sort not in {...}` raises `TypeError: unhashable type`.
   - If it delivers an int, the string concatenation raises `TypeError`.
   - Either way the caller gets a `TypeError` instead of the intended `ValueError`. That is not a security issue: nothing is interpolated.
   - **Settles it:** whether the parsing layer guarantees that `sort` is a `str`.
2. **The error message reflects the raw `sort` value.** This is `"cannot sort by " + sort` in all three files.
   - It only matters if exception text is rendered into HTML unescaped.
   - **Settles it:** how the caller renders the `ValueError`.

## REFUTED

- **SQL injection through `order by {sort}`.** Refuted. In every file the allowlist check sits directly above the f-string and raises on a miss (`admin.py:13`, `exports.py:9`, `reports.py:9`). Only literal column names can reach the SQL.
- **The admin list leaks other customers' rows to customers.** Refuted. `admin.py:10` raises `PermissionError` for any role other than `"admin"`, before the query runs. Showing every customer is what the docstring and the request intend.
- **`reports.py` `order by total` sorts by the raw column instead of the sum.** Refuted, with PROBABLE evidence. SQLite resolves a bare ORDER BY identifier to a result-column alias first, so this sorts by `sum(total)`. Either way, `where customer = ?` gives at most one row, so the order cannot be wrong.
- **Customer-scoped listings leak across customers.** Refuted. Both bind `request["user"]` as a parameter (`exports.py:11`, `reports.py:11`), and the context says it is the verified identity.

## WHAT HOLDS UP

- Allowlisting the identifier, rather than trying to bind it, is the right way to handle ORDER BY. It is applied consistently on all three paths.
- The defaults (`id`, `customer`) are in their own allowlists.
- `reports.py` correctly leaves out `id`, which is not a column in an aggregate query.
- No path selects `secret_note`.

Two observations that are not defects:
- Ties are broken in no defined order. For example, orders 3 and 5 both have `total` 30.0. Add `, id` as a tiebreaker if pagination is ever added.
- Sorting the summary report is a no-op, because it returns one row.

## UNVERIFIED CLAIMS

- **"request["user"] is the verified customer name."** This was taken from the context. Confirm it in the auth middleware.

## QUESTIONS FOR THE AUTHOR

1. Can `request["sort"]` ever be a non-string?
2. Is exception text ever rendered to a browser?

## DECISION-MAKER SUMMARY

The sorting change is safe to release. Every listing only accepts known column names, customers can only see their own orders, and the admin list stays staff-only. The remaining risk is two small edge cases in error handling that depend on code that was not supplied.

## OWNER SUMMARY

The new sorting option looks safe: customers can only sort by a few fixed fields, and they still only see their own orders. The staff-only list is still locked to staff. Two minor questions about how unusual input is reported back should be checked, but they do not block release.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "admin.py", "status": "seen", "matters": true},
    {"item": "db.py", "status": "seen", "matters": true},
    {"item": "exports.py", "status": "seen", "matters": true},
    {"item": "reports.py", "status": "seen", "matters": true},
    {"item": "request parsing / routing layer", "status": "not_seen", "matters": false},
    {"item": "exception rendering in callers", "status": "not_seen", "matters": false},
    {"item": "tests", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": true, "reason": "Sample data contains customer notes; no external seats used."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "admin.py", "kind": "file"},
      {"unit": "db.py", "kind": "file"},
      {"unit": "exports.py", "kind": "file"},
      {"unit": "reports.py", "kind": "file"},
      {"unit": "admin.py:list_orders", "kind": "function"},
      {"unit": "exports.py:export_orders", "kind": "function"},
      {"unit": "reports.py:totals_report", "kind": "function"},
      {"unit": "db.py:query", "kind": "function"},
      {"unit": "each listing refuses an unknown sort field", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "request parsing / routing layer", "reason": "not_supplied"},
      {"unit": "exception rendering in callers", "reason": "not_supplied"},
      {"unit": "tests", "reason": "not_supplied"},
      {"unit": "runtime execution of queries", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "exports.py:9-10, reports.py:9-10, admin.py:12-14",
     "suspicion": "A non-string sort (list or int) raises TypeError instead of the intended ValueError.",
     "unresolved_fact": "Whether the request parser guarantees request['sort'] is a str."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "exports.py:10, reports.py:10, admin.py:14",
     "suspicion": "Raw sort value is reflected in the ValueError message; reflected XSS if rendered unescaped.",
     "unresolved_fact": "How callers render exception text to the client."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "SQL injection via f-string order by {sort}.",
     "evidence": "Allowlist membership check raises before interpolation in admin.py:13, exports.py:9, reports.py:9."},
    {"id": "C2", "candidate": "Admin list exposes all customers' orders to non-staff.",
     "evidence": "admin.py:10 raises PermissionError unless role == 'admin', before the query."},
    {"id": "C3", "candidate": "reports.py order by total sorts by raw column, not sum.",
     "evidence": "SQLite resolves ORDER BY identifiers to result aliases first; query also returns at most one row."},
    {"id": "C4", "candidate": "Customer-scoped listings leak other customers' rows.",
     "evidence": "request['user'] bound as ? parameter at exports.py:11 and reports.py:11."}
  ]
}
```