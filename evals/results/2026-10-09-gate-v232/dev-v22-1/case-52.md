# Redteam review: sorting for the three order listings

**No tools were available in this session.** Nothing was run. Every finding below comes from reading the supplied code and tying it to exact lines, so nothing is claimed as executed.

**VERDICT: REWORK.** The export and summary report put the customer-supplied `sort` value straight into SQL. Any logged-in customer can then use the orders table, including other customers' rows and `secret_note`, from inside their own query.

**CONFIDENCE: medium.** The code-trace findings are high confidence. Confidence is limited because nothing could be run, no tests or callers were supplied, and this was a single reviewer with no fresh subagent or cross-vendor seat.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, admin.py, db.py, exports.py, reports.py.
- **Not seen:** tests (matters: there is no evidence any were written), the request-handling layer that builds `request` (matters: whether `sort` is filtered upstream), and a spec of which fields should be sortable or whether a sort direction is wanted (matters a little).

**COVERAGE**
- **Checked:** `admin.py:list_orders`, `exports.py:export_orders`, `reports.py:totals_report`, `db.py:query` and the schema.
- **Not checked:** the request framework, tests, and the real production database. db.py is a sqlite stand-in, so behaviour on another engine was not verified.

**SEATS AND GATE:** One reviewer only (this session). No subagent or cross-vendor seat was available. The gate is not triggered: the seed data is fictional, and the request supplied no real customer data.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | exports.py:7-8 | `sort` from the request is put into `order by {sort}` with no allowlist. The `where customer = ?` parameter does not protect the ORDER BY clause. | A logged-in customer sends a `sort` value that is an SQL expression, such as a subquery. It runs with full read access to `orders`. By watching how their own rows get reordered, they can learn other customers' rows and `secret_note` values. | Validate against an allowlist, as admin.py does: `{"id", "total"}`, else reject. **Repro (benign):** call with `sort="(select 1)"`. The query is accepted, which shows arbitrary expressions reach the SQL. The expected behaviour is rejection. A test should assert that any value outside the allowlist raises an error before `query` is called. | y/y/y/y |
| F2 | Critical | CONFIRMED | B | reports.py:7-8 | Same unvalidated interpolation of `sort` into ORDER BY. | Same as F1: a customer-supplied expression reads beyond the customer's own rows. | Use an allowlist of `{"customer", "total"}` (`total` is the alias). **Repro:** `sort="(select 1)"` is accepted, but it should be rejected. | y/y/y/y |
| F3 | Medium | CONFIRMED | B | exports.py:8, reports.py:8 | An invalid `sort` such as `nosuchcol` surfaces as a raw `sqlite3.OperationalError`, not as the clean `ValueError` that admin.py raises. | If the framework shows exception text, the error names the column and query. The three endpoints also behave inconsistently. | This is fixed along with F1/F2. Add a test that a bad `sort` raises `ValueError`. | y/y/n/y |
| F4 | Low | CONFIRMED | B | admin.py:15, exports.py:8 | There is no tie-breaker. Sorting by `customer` or `total` with ties (ann ×3; total 30.0 ×2) gives an order the engine can change between calls. | Paginated or exported results can come back in a different order on each request. | Append `, id` to the ORDER BY clause. **Repro:** `sort="total"` in admin: rows 3 and 5 have no guaranteed relative order. | y/y/n/n |

## Needs validation
- **S1:** Is a sort direction (asc/desc) expected? The request says only "sorting". The fact that settles it is the product spec. If direction is wanted, it needs its own allowlist of `{"asc", "desc"}`.
- **S2:** Does the request layer already reject or filter `sort`? The fact that settles it is the framework code, which was not supplied. Even if it does, F1/F2 still stand as defence-in-depth gaps on endpoints every customer can reach.
- **S3:** Are there tests? None were supplied. Each allowlist test should be confirmed to go red when the allowlist is removed.

## Refuted
- **R1: Stacked statements, such as `; drop table`.** Refuted. sqlite3's `execute` runs a single statement and raises an error on a second one. The real risk is a read through an expression, which is F1/F2.
- **R2: The admin listing is injectable or missing authorization.** Refuted. `admin.py:9-10` checks the role before anything else, and `admin.py:12-13` enforces the allowlist before the interpolation.

## What holds up
- admin.py is correct: the role check comes first, there is an allowlist of real columns, and a bad value is rejected cleanly.
- Customer scoping in exports.py and reports.py correctly uses a bound `?` parameter for `request["user"]`.
- None of the queries select `secret_note` directly.

## Unverified claims
- The docstring claims "the signed-in customer's own orders" (exports.py, reports.py). F1/F2 show this holds only for the rows returned, not for what the query can read.
- Behaviour on the production database engine was not checked. The sqlite stand-in may differ.

## Questions for the author
1. Is a sort direction in scope?
2. Which columns should customers be allowed to sort by on each endpoint?
3. Where are the tests?

## Decision-maker summary
Do not release yet. Two of the three listings let any logged-in customer run their own SQL expressions against the orders table, which exposes other customers' data. The fix is a few lines per file, the same allowlist pattern admin.py already uses, plus tests.

## Owner summary
The new sorting works for staff, but the two customer-facing lists trust whatever the customer types in for the sort order. A customer who knows what they are doing could use that to learn other customers' order details. Limiting the sort to a fixed list of allowed fields closes the gap, and it is a small change.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true},
    {"item": "request-handling layer", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "fictional seed data only"},
  "coverage": {
    "checked": [
      {"unit": "admin.py", "kind": "file"},
      {"unit": "admin.py:list_orders", "kind": "function"},
      {"unit": "exports.py", "kind": "file"},
      {"unit": "exports.py:export_orders", "kind": "function"},
      {"unit": "reports.py", "kind": "file"},
      {"unit": "reports.py:totals_report", "kind": "function"},
      {"unit": "db.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "tests", "reason": "not supplied"},
      {"unit": "request framework", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "exports.py:7-8",
     "scenario": "A logged-in customer supplies an SQL expression as sort; it runs inside ORDER BY with read access to all orders rows, letting them infer other customers' data from the ordering of their own rows.",
     "fix": "Reject sort values not in an allowlist {id, total} before building the query.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Call export_orders with sort='(select 1)'; expect rejection, observe the query accepted."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "reports.py:7-8",
     "scenario": "Same unvalidated ORDER BY interpolation as F1 on the customer summary report.",
     "fix": "Allowlist {customer, total} before building the query.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Call totals_report with sort='(select 1)'; expect rejection, observe the query accepted."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "exports.py:8, reports.py:8",
     "scenario": "An unknown column raises a raw sqlite3.OperationalError that may expose the query text, unlike admin.py's ValueError.",
     "fix": "Raise ValueError on a bad sort value, as admin.py does.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "sort='nosuchcol' raises OperationalError; expect ValueError."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "admin.py:15, exports.py:8",
     "scenario": "Ties on customer or total give a nondeterministic row order across calls.",
     "fix": "Append ', id' as a tie-breaker to the ORDER BY clause.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Admin sort='total': rows 3 and 5 (both 30.0) have no guaranteed order."},
    {"id": "S1", "status": "needs_validation", "track": "D", "location": "request.md",
     "suspicion": "A sort direction may be expected but is not implemented.",
     "unresolved_fact": "Whether the product spec requires asc/desc."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "request layer",
     "suspicion": "Upstream code may already filter sort.",
     "unresolved_fact": "The request framework code, which was not supplied."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Stacked statements such as '; drop table' via sort.",
     "evidence": "sqlite3 execute runs a single statement and raises an error on multiple statements."},
    {"id": "R2", "candidate": "The admin listing is injectable or missing authorization.",
     "evidence": "admin.py:9-13 checks the role, then the allowlist, before interpolating sort."}
  ]
}
```