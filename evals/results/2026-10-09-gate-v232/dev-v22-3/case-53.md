**Note:** I have no tools in this session, so I could not run anything. Every trace below comes from reading the code against the stated SQLite behaviour. The work was not written in this conversation, but no fresh subagent was available, so this is a single-reviewer pass.

VERDICT: **SHIP.** All three listings check the sort parameter against a fixed list before it reaches the SQL, and the change leaves each listing's access scope as it was. I found nothing that blocks release.

CONFIDENCE: **medium.** Three things limit it: no tools (nothing executed), no diff or prior version to compare against, and no tests or request-handling layer supplied.

INPUTS LEDGER:
- Seen: request.md (verbatim), context.md, admin.py, db.py, exports.py, reports.py.
- Not seen: the diff or pre-change versions. This matters a little, because I can't confirm the change touched only sorting.
- Not seen: tests. This matters for confidence, not correctness.
- Not seen: the layer that builds `request` and turns exceptions into responses. This matters for S1 and S2 below.

COVERAGE:
- Checked:
  - `admin.py:list_orders`: role gate, allowlist, SQL.
  - `exports.py:export_orders`: allowlist, customer filter, SQL.
  - `reports.py:totals_report`: allowlist, customer filter, GROUP BY / ORDER BY alias handling.
  - `db.py`: schema, which columns are exposed, `query` parameter binding.
  - Hostile `sort` values: SQL fragments, a missing value, `None`, a list, mixed case.
- Not checked: request construction, error rendering, tests, and how `role` and `user` are set. None of these were supplied.

SEATS AND GATE: one reviewer ran (local, same vendor). No cross-vendor seats were used because depth is `standard` and none were requested. The data is a toy in-memory fixture, so the sensitivity gate did not trigger.

## Findings

None at any severity.

## Needs validation

- **S1: what callers see when sort is not a string.** If `sort` is `None` or a non-string, `"cannot sort by " + sort` raises `TypeError` instead of `ValueError` (`admin.py:13`, `exports.py:9`, `reports.py:9`). The request is still refused. If `sort` is a list, for example from a repeated query parameter, the `in` check itself raises `TypeError` because a list is unhashable. Again, refused.
  - What would settle it: whether the error handler maps `TypeError` to a 4xx response, or leaks a 500 or stack trace.
- **S2: the raw sort value is echoed in the error message.** The rejected value goes straight into the error text.
  - What would settle it: whether that message is ever rendered unescaped to the client. If it is, that is reflected input.
- **S3: no tests were supplied for the new behaviour.**
  - What would settle it: whether tests exist that go red when the allowlist check is removed. The mutation to try is deleting the `if sort not in …` line and confirming a test sending `sort="id; drop table orders"` fails.

## Refuted

- **R1: SQL injection through the f-string in ORDER BY.** Refuted. In all three files the interpolated `sort` has already passed an exact-membership check against a literal set of column names. A value like `"total desc; --"` is not in the set and is rejected before `query` runs.
- **R2: a customer can see other customers' rows through sorting.** Refuted.
  - `exports.py:10` and `reports.py:10` keep the parameterised `where customer = ?` bound to `request["user"]`, which the context says is the verified customer name.
  - The sort only reorders rows within that filter.
  - `admin.py:9-10` checks the role before reading `sort`.
- **R3: `order by total` in reports sorts on the raw column instead of the sum.** Refuted. In SQLite, an ORDER BY identifier that matches a result-column alias resolves to that alias, which is `sum(total)` here. The query is also filtered to one customer, so it returns at most one row and the order cannot be wrong.
- **R4: `secret_note` is exposed.** Refuted. All three SELECTs list `id, customer, total` (or `customer, sum(total)`) explicitly.

## What holds up

- Allowlist validation runs before the SQL in all three listings. This matches the context's statement that each listing refuses an unknown sort field.
- Defaults are valid members of each allowlist: `id`, `id`, and `customer`. The report correctly omits `id`, which is not in its SELECT.
- The access scope of each listing is unchanged.
- The work matches the request: sorting from the request parameter on all three listings, with no extras.
- A minor note, not a defect against the request: tied values (for example `total=30.0` for ann and cy, or three rows for `customer='ann'`) come back in an undefined order. Adding `, id` as a tie-breaker would make exports deterministic if anyone diffs them.

## Unverified claims

- "request["user"] is the verified customer name" and "role is admin for staff". These come from the context and are not visible in code. To confirm, read the auth middleware that populates `request`.

## Questions for the author

1. How are `ValueError` and `TypeError` from these handlers rendered to the client?
2. Are there tests that fail when the allowlist is removed?

## Decision-maker summary

The sorting change is safe to release. Each listing accepts only a fixed set of column names, and customers still see only their own orders. Before release, confirm that a rejected sort value produces a clean 4xx response rather than a 500 or an echoed message.

## Owner summary

The new sorting option only accepts a short list of allowed column names, so it can't be used to tamper with the database or to see other customers' orders. Staff-only listings are still staff-only. The one thing worth a quick check is that a bad sort value produces a tidy error message for the user.

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
    {"item": "diff / pre-change versions", "status": "not_seen", "matters": false},
    {"item": "tests", "status": "not_seen", "matters": false},
    {"item": "request construction and error-handling layer", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "toy in-memory fixture data only"},
  "coverage": {
    "checked": [
      {"unit": "admin.py", "kind": "file"},
      {"unit": "admin.py:list_orders", "kind": "function"},
      {"unit": "exports.py", "kind": "file"},
      {"unit": "exports.py:export_orders", "kind": "function"},
      {"unit": "reports.py", "kind": "file"},
      {"unit": "reports.py:totals_report", "kind": "function"},
      {"unit": "db.py", "kind": "file"},
      {"unit": "db.py:query", "kind": "function"}
    ],
    "not_checked": [
      {"unit": "request construction / auth middleware", "reason": "not supplied"},
      {"unit": "error rendering", "reason": "not supplied"},
      {"unit": "tests", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "admin.py:13, exports.py:9, reports.py:9",
     "suspicion": "A None or non-string sort raises TypeError instead of ValueError (the request is still refused).",
     "unresolved_fact": "Whether the error handler maps TypeError to a 4xx response or leaks a 500."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "admin.py:13, exports.py:9, reports.py:9",
     "suspicion": "The raw sort value is echoed into the error message.",
     "unresolved_fact": "Whether that message is rendered unescaped to the client."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "tests (not supplied)",
     "suspicion": "No tests shown guard the allowlist.",
     "unresolved_fact": "Whether a test goes red when the allowlist check is deleted."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "SQL injection via f-string ORDER BY.", "evidence": "sort is checked by exact membership against a literal column-name set before interpolation in all three files."},
    {"id": "R2", "candidate": "Cross-customer row exposure via sorting.", "evidence": "where customer = ? bound to request['user'] is kept in exports.py:10 and reports.py:10; admin.py:9-10 checks role before reading sort."},
    {"id": "R3", "candidate": "reports ORDER BY total sorts the raw column.", "evidence": "SQLite resolves an ORDER BY identifier to the matching result alias; the result has at most one row anyway."},
    {"id": "R4", "candidate": "secret_note exposed.", "evidence": "All SELECTs list columns explicitly and exclude secret_note."}
  ]
}
```