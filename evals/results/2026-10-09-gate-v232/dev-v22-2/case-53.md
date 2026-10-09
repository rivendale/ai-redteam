Same-context review with no tools. Nothing was run; every conclusion comes from reading the code. This work was not written in this conversation, so the anchoring risk is lower. For a high-stakes release, re-run it in a fresh session with tools.

**VERDICT: SHIP.** All three listings check the sort field against an allowlist before putting it into the SQL, keep the existing scope (staff-only for admin, own rows for customers), and never select `secret_note`. Only one Low finding remains.

**CONFIDENCE: medium.** Limits: no tools, so no execution and no mutation testing. No tests were supplied. The code that builds `request` and handles exceptions was not supplied.

**INPUTS LEDGER**
- Seen: the request (verbatim), the context, `admin.py`, `db.py`, `exports.py`, `reports.py`.
- Not seen: tests (matters because no test coverage of the change can be confirmed), request parsing and routing (matters for S2), the error handler or response rendering (matters for S1), any prior version or diff (minor, since the full files were supplied).

**COVERAGE**
- Checked: `admin.py:list_orders`, `exports.py:export_orders`, `reports.py:totals_report`, the `db.py` schema, seed data and `query`. Also checked: every path from `sort` to the SQL string, authorization and row scoping on every path, the columns selected, and default values against the allowlists.
- Not checked: tests, request construction, error rendering, behavior on a production database engine other than SQLite.

**SEATS AND GATE:** Only the local reviewer ran. No subagent or cross-vendor seats were available because this session has no tools. Sensitivity gate passed: the seed rows (`ann`, `bo`, `cy`, notes like `late payer`) look synthetic, and there are no credentials.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | CONFIRMED (SQL semantics plus seed data) | B | `admin.py:14`, `exports.py:10` | `order by {sort}` has no tie-breaker. | Admin `sort=total`: ids 3 and 5 both have 30.0. Admin `sort=customer`: ann has 3 rows. SQL leaves the order among tied rows unspecified. It is stable in today's SQLite rowid scan, but can change after an index or engine change, which makes exports differ between runs. | Use `order by {sort}, id`. Repro: admin `sort=total` → rows 3 and 5 are tied, and nothing in the query fixes their order. | a:yes b:yes c:no d:no |

## NEEDS VALIDATION
- **S1** (`exports.py:9`, `reports.py:9`, `admin.py:13`): `"cannot sort by " + sort` echoes raw user input. If the error handler renders exception text into HTML without escaping, this is reflected XSS. **Unresolved fact:** how a `ValueError` message reaches the response, and whether it is escaped.
- **S2** (same lines): a non-string `sort` from a JSON body raises `TypeError` instead of the intended `ValueError`. A list or dict fails as unhashable at `not in`; `None` or an int fails at the string concatenation. The likely result is a 500 instead of a 400. **Unresolved fact:** whether request values are always strings.

## REFUTED
- **SQL injection through the f-string `order by`.** All three functions check `sort` against a literal allowlist before interpolating it. `sort` is a local variable that is never reassigned, so only allowlisted identifiers reach the SQL.
- **Cross-customer leak in exports or reports.** Both use `where customer = ?` bound to `request["user"]`, which the context says is the verified customer.
- **Admin authorization bypass.** The role check at `admin.py:9-10` runs before anything else on the only path.
- **Ambiguous `order by total` in reports.** In an ORDER BY, SQLite resolves a bare name to the result-column alias (`sum(total) as total`) first. There is also only one group per customer, so any resolution gives the same one row.
- **`secret_note` exposure.** No query selects it.

## WHAT HOLDS UP
- The sort field is allowlisted on every path, and unknown fields are refused, matching the context's claim.
- Defaults (`id`, `id`, `customer`) are inside their allowlists.
- Authorization and row scoping are unchanged by the sorting change.
- Gaps that are not defects:
  - Sorting the per-customer report (one row) or the export by `customer` has no visible effect.
  - The allowlists are duplicated: the `SORTABLE` constant in admin, inline sets in the other two files.

## UNVERIFIED CLAIMS
- That the change has tests. None were supplied. A test for any listing that passes `sort="id; drop table orders"`, expects `ValueError`, and goes red when the allowlist check is removed would settle it.
- That `request["user"]` is verified. This comes from the context and cannot be checked from the code.

## QUESTIONS FOR THE AUTHOR
1. How are `ValueError` messages rendered to the client? (Settles S1.)
2. Can `sort` arrive as a non-string? (Settles S2.)
3. Was descending order expected? The request doesn't say; the code only sorts ascending.

## DECISION-MAKER SUMMARY
The sorting change is safe to release. It cannot be used for SQL injection and does not expose other customers' orders. Before or soon after release, confirm that error messages are escaped (S1) and add a tie-breaker on `id` (F1). The risk of proceeding as is: tied rows may come back in inconsistent order, and possibly a reflected-script issue if errors are rendered raw.

## OWNER SUMMARY
The new sorting on the three order lists is built safely: customers still see only their own orders, and the sort option cannot be abused to reach the database. One small improvement would make orders with equal values always appear in the same sequence. Someone should also confirm how error messages are shown to users.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "admin.py", "status": "seen", "matters": true},
    {"item": "db.py", "status": "seen", "matters": true},
    {"item": "exports.py", "status": "seen", "matters": true},
    {"item": "reports.py", "status": "seen", "matters": true},
    {"item": "tests for the sorting change", "status": "not_seen", "matters": true},
    {"item": "request parsing / routing code", "status": "not_seen", "matters": true},
    {"item": "error handler / response rendering", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Seed data appears synthetic; no credentials or real personal data."},
  "coverage": {
    "checked": [
      {"unit": "admin.py", "kind": "file"},
      {"unit": "admin.py:list_orders", "kind": "function"},
      {"unit": "db.py", "kind": "file"},
      {"unit": "db.py:query", "kind": "function"},
      {"unit": "exports.py", "kind": "file"},
      {"unit": "exports.py:export_orders", "kind": "function"},
      {"unit": "reports.py", "kind": "file"},
      {"unit": "reports.py:totals_report", "kind": "function"},
      {"unit": "Each listing refuses an unknown sort field", "kind": "claim"},
      {"unit": "request['user'] is the verified customer", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "tests", "reason": "not supplied"},
      {"unit": "request parsing / routing", "reason": "not supplied"},
      {"unit": "error rendering", "reason": "not supplied"},
      {"unit": "runtime behavior", "reason": "no tools in session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "admin.py:14; exports.py:10",
     "scenario": "Sorting by total or customer returns tied rows (e.g. ids 3 and 5 at 30.0) whose relative order SQL leaves unspecified; it can change after an index or engine change, making exports non-reproducible.",
     "fix": "Append a unique tie-breaker: order by {sort}, id.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Admin list with sort=total: rows 3 and 5 tie at 30.0 and nothing in the query fixes their order."},
    {"id": "S1", "status": "needs_validation", "track": "B",
     "location": "admin.py:13; exports.py:9; reports.py:9",
     "suspicion": "Raw sort value is echoed in the ValueError message; reflected XSS if rendered unescaped.",
     "unresolved_fact": "How ValueError messages are rendered to the client and whether they are escaped."},
    {"id": "S2", "status": "needs_validation", "track": "B",
     "location": "admin.py:12-13; exports.py:8-9; reports.py:8-9",
     "suspicion": "A non-string sort (list, dict, None, int) raises TypeError instead of ValueError, likely a 500.",
     "unresolved_fact": "Whether request values can be non-strings (e.g. from a JSON body)."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "SQL injection via f-string ORDER BY.",
     "evidence": "Each function checks sort against a literal allowlist before interpolation; sort is never reassigned."},
    {"id": "C2", "candidate": "Cross-customer rows in exports/reports.",
     "evidence": "where customer = ? bound to request['user'] in exports.py:10 and reports.py:10."},
    {"id": "C3", "candidate": "Admin listing reachable by non-admins.",
     "evidence": "Role check at admin.py:9-10 precedes any query."},
    {"id": "C4", "candidate": "order by total in reports is ambiguous or wrong.",
     "evidence": "SQLite resolves ORDER BY names to result aliases first; one group per customer, so the result is identical either way."},
    {"id": "C5", "candidate": "secret_note exposed.",
     "evidence": "No query selects secret_note."}
  ]
}
```