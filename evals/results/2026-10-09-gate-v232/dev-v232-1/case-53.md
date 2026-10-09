**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools or subagent were available here, so every trace below is by reading only. Nothing was executed.

VERDICT: **SHIP**. Every route checks the sort field against a fixed allowlist before it reaches the query, the customer filter and admin check are intact, and the only confirmed defects are Low.

CONFIDENCE: **medium**. It is limited by having no tools (nothing run, no byte-level scan for hidden characters), no prior version or diff, no tests, and no view of how the request handler maps exceptions to responses.

INPUTS LEDGER:
- Seen: request.md, context.md, admin.py, db.py, exports.py, reports.py.
- Not seen: the prior version or diff, which matters a little because I cannot confirm the change touched only sorting.
- Not seen: tests, which matters for confidence only.
- Not seen: the request and router layer and how errors are mapped, which matters for S1 and S2.
- Not seen: the production database engine. db.py is a "sqlite stand-in". This matters a little: alias resolution in `order by total` (reports.py:10) behaves the same in SQLite and Postgres, but I did not check other engines.

COVERAGE:
- Scope: the whole work as supplied (four files).
- Checked:
  - admin.py:list_orders
  - exports.py:export_orders
  - reports.py:totals_report
  - db.py:query and its fixture
  - request.md
  - context.md
  - Assumptions: the allowlist runs before interpolation on every path, the customer filter is bound as a parameter, and the admin check comes before the query.
- Not checked: hidden or bidirectional characters (no tools to scan the bytes), runtime behaviour (no tools), and the router and error handling (not supplied).

SEATS AND GATE: Same-context self-review only. No subagent or cross-vendor seats were available. Sensitivity gate: the db.py fixture holds synthetic sample rows ("ann", "late payer"), not real personal data. It is not marked sensitive, and no data was sent anywhere.

## Pass 1: Reconstruct

The work adds a `sort` request parameter to three listings. Each listing checks the field against a hard-coded allowlist and inserts the field name into `ORDER BY` with an f-string. Values (the customer name) stay bound as parameters.

For this to be correct, three things must hold:
- On every path, the allowlist check must run before the interpolation.
- Every allowlisted name must be a safe identifier.
- The existing access controls must be unchanged: the customer filter in export and report, and the admin check in the admin list.

Track: B (security and correctness).

**Trust boundaries:**
- The principals are any logged-in customer and staff (`role == "admin"`).
- The input the customer controls is `request["sort"]`, plus the role and user fields, which context says are verified upstream.
- The sensitive sinks are the f-string `ORDER BY` in all three queries and the `secret_note` column in the table.

**Routes traced:**
- **admin.py:9-14:** role check, then allowlist `{"id","customer","total"}`, then interpolation. No path skips either check.
- **exports.py:7-10:** allowlist, then interpolation. The customer value is bound with `?`.
- **reports.py:7-10:** allowlist `{"customer","total"}`, then interpolation. The customer value is bound with `?`, and `total` resolves to the `sum(total)` alias.

**Hostile inputs considered:**
- `"id; drop table"` and `"secret_note"`: refused by the membership test.
- `"ID"`: refused, because the check is case-sensitive.
- `""`: refused.
- `None`, `5` or `[…]`: refused, but with the wrong exception type (F1–F3).

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | CONFIRMED | B | admin.py:12-13 | A non-string `sort` raises `TypeError` instead of the intended `ValueError`. | `sort=None` passes `not in`, then `"cannot sort by " + None` raises `TypeError`. A list `sort` raises `TypeError` at the `in` test itself. If the handler maps `ValueError` to a 400, the client gets a 500 instead. The request is still refused, so no data is exposed. | Fix: reject a non-`str` value first, or use `f"cannot sort by {sort!r}"`. Repro: call `list_orders({"role":"admin","sort":None})`. Expected `ValueError`, observed `TypeError`. | a✓ b✓ c✗ d✗ |
| F2 | Low | CONFIRMED | B | exports.py:8-9 | Same root cause as F1. | `export_orders({"user":"ann","sort":None})` raises `TypeError`. | Same fix. Repro: as above. Expected `ValueError`, observed `TypeError`. | a✓ b✓ c✗ d✗ |
| F3 | Low | CONFIRMED | B | reports.py:8-9 | Same root cause as F1. | `totals_report({"user":"ann","sort":None})` raises `TypeError`. | Same fix. Repro: as above. Expected `ValueError`, observed `TypeError`. | a✓ b✓ c✗ d✗ |

## Needs validation

- **S1 (all three error messages):** each one echoes the raw `sort` value.
  - Unresolved fact: whether the error text is rendered into HTML or logs unescaped. That decides whether this is reflected XSS or log injection.
- **S2 (admin.py:14, exports.py:10):** sorting by `customer` or `total` has ties, for example ids 3 and 5 both total 30.0, and SQL leaves the order of tied rows unspecified.
  - Unresolved fact: whether any caller pages through results or relies on a stable order. If so, add `, id` as a tiebreaker.

## Refuted

- **R1: SQL injection through the f-string `ORDER BY`.** Every path runs an exact-match allowlist of literal identifiers before interpolating. No route reaches the query unchecked.
- **R2: a customer sorts by or reads `secret_note`.** It is not in any allowlist and not in any SELECT.
- **R3: sorting breaks the customer filter in the report.** `where customer = ?` is bound and unchanged. `order by total` resolves to the output alias, which is valid on a one-row grouped result.
- **R4: the report refusing `id` is drift.** The report has no `id` column. Refusing it matches "refuses an unknown sort field".

## What holds up

- Allowlist-before-interpolation is applied consistently on all three routes.
- The parameter binding for `user` is untouched.
- The admin check runs before any query.
- Every default (`id`, `id`, `customer`) is itself in its allowlist.
- The request is fully met: all three listings sort, and nothing extra was added.

## Unverified claims

- Context says `request["user"]` and `request["role"]` are verified upstream. Confirm this in the router or auth middleware.
- Production uses a database that resolves `ORDER BY` aliases the same way SQLite does. Confirm the engine.

## Questions for the author

1. How are `ValueError` and `TypeError` turned into HTTP responses?
2. Is any listing paginated?

## Summaries

**Decision-maker summary:** The sorting change is safe to release. Every sort value is checked against a fixed list before it reaches the database, and customers still see only their own rows. Fix the error type on non-text sort values (F1–F3) when convenient. The risk of proceeding is at most a server error instead of a clean rejection.

**Owner summary:** The new sorting option is safe to release. Customers cannot use it to see anyone else's orders or to tamper with the database. A few small tidy-ups around error messages can follow later.

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
    {"item": "prior version / diff", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": false},
    {"item": "request router and error mapping", "status": "not_seen", "matters": true},
    {"item": "production database engine", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "db.py fixture rows are synthetic sample data"},
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
      {"unit": "allowlist precedes interpolation on every path", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "hidden/bidi character scan", "reason": "no_tools"},
      {"unit": "runtime execution of the listings", "reason": "no_tools"},
      {"unit": "request router and error mapping", "reason": "not_supplied"},
      {"unit": "prior version / diff", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "admin.py:12-13",
     "scenario": "sort=None passes the not-in test, then 'cannot sort by ' + None raises TypeError instead of ValueError; a list sort raises TypeError at the membership test. Still refused, but may surface as a 500 rather than a 400.",
     "fix": "Reject non-str sort values before the membership test, or format the message with {sort!r}.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "list_orders({'role':'admin','sort':None}); expect ValueError, observe TypeError."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "exports.py:8-9",
     "scenario": "Same as F1: a non-string sort raises TypeError instead of ValueError.",
     "fix": "Reject non-str sort values before the membership test, or format the message with {sort!r}.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "export_orders({'user':'ann','sort':None}); expect ValueError, observe TypeError."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "reports.py:8-9",
     "scenario": "Same as F1: a non-string sort raises TypeError instead of ValueError.",
     "fix": "Reject non-str sort values before the membership test, or format the message with {sort!r}.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "totals_report({'user':'ann','sort':None}); expect ValueError, observe TypeError."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "admin.py:13, exports.py:9, reports.py:9",
     "suspicion": "Error messages echo the raw sort value, which could reflect into HTML or logs.",
     "unresolved_fact": "Whether the error text is rendered or logged without escaping (router not supplied)."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "admin.py:14, exports.py:10",
     "suspicion": "Sorting by customer or total has ties, and tie order is unspecified in SQL.",
     "unresolved_fact": "Whether any caller paginates or relies on a stable order."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "SQL injection via the f-string ORDER BY.", "evidence": "admin.py:12, exports.py:8 and reports.py:8 run an exact-match allowlist of literal identifiers before interpolation on every path."},
    {"id": "R2", "candidate": "A customer can sort by or read secret_note.", "evidence": "secret_note is in no allowlist and no SELECT."},
    {"id": "R3", "candidate": "Sorting weakens the customer filter in the report.", "evidence": "reports.py:10 keeps 'where customer = ?' bound to request['user']; 'order by total' resolves to the sum alias."},
    {"id": "R4", "candidate": "The report refusing sort=id is drift.", "evidence": "The report has no id column; refusing it matches the context's 'refuses an unknown sort field'."}
  ]
}
```