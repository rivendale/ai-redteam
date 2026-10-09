Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes. I had no tools here, so every finding comes from reading the code. None of the reproductions were run.

**VERDICT: REWORK.** Two of the three listings put the raw `sort` parameter straight into SQL. Any logged-in customer can use this to read other customers' orders.

**CONFIDENCE: medium.** I read all four files, but I had no tools, so nothing was run. The request handler, error handling and tests were not supplied.

**INPUTS LEDGER**
- Seen: request.md, context.md, admin.py, db.py, exports.py, reports.py.
- Not seen:
  - The HTTP layer that builds `request`. This matters: it decides whether `sort` can be any string and how exceptions reach the client.
  - Tests. This matters: I can't confirm any test coverage.
  - The production database engine. Not material: the injection works the same on any SQL engine.

**COVERAGE:** whole work (4 files plus the request and context).
- Checked: all three query sites, the admin role check, the allowlist, and the db helper's parameter binding.
- Not checked: the request-construction layer, exception mapping and tests (not supplied).

**SEATS AND GATE:** Local reviewer only, with no subagent available. Sensitivity gate passed: the seed data in db.py is synthetic. No cross-vendor seats were requested.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (traced) | B | exports.py:8 | `sort` from the request goes into the `ORDER BY` clause through an f-string. It is never checked against an allowlist. Only `user` is bound as a parameter. | A logged-in customer sends a crafted `sort` value. Their SQL now runs inside the query, so the `where customer = ?` filter no longer limits what they can read. They can reach other customers' rows, including the `secret_note` column. | **Fix:** check `sort` against a per-endpoint allowlist (`{"id","total"}`) before building the query, as admin.py does. Map each allowed key to a fixed column string; never interpolate the request value itself. **Repro (not run):** call `export_orders({"user":"ann","sort":"no_such_col"})`. Expected: a `ValueError` from validation. Observed by trace: sqlite `OperationalError: no such column`, which proves raw input reaches the SQL parser. Add a test asserting a non-allowlisted `sort` raises before `query()` is called. | y/y/y/y |
| F2 | Critical | CONFIRMED (traced) | B | reports.py:8 | Same root cause as F1 (sibling): `sort` is interpolated into the `ORDER BY` of the grouped query with no validation. | Same as F1: a customer escapes their own `customer = ?` scope and reads other customers' data. | **Fix:** allowlist `{"customer","total"}`. These are the only meaningful keys after `group by customer`; `total` resolves to the aggregate alias. **Repro (not run):** `totals_report({"user":"ann","sort":"no_such_col"})` raises `OperationalError` instead of a validation error. | y/y/y/y |
| F3 | Low | CONFIRMED (traced) | B | admin.py:12-13, exports.py:8, reports.py:8 | Inconsistent behavior for a bad sort key. admin.py raises `ValueError`; the other two would raise a database error once fixed differently, or leak the SQL error today. | A client gets a 500 response with a DB error string from two endpoints and a clean error from the third. | Use one shared `validate_sort(value, allowed, default)` helper across all three. **Repro:** compare the exception types for `sort="x"` across the three functions. | y/y/n/n |

Siblings searched for F1/F2: every `query(` call with an f-string across the four files. There are three sites; admin.py:14 is the only one guarded. Both are security findings with this boundary:
- **Principal:** any logged-in customer.
- **Input:** the `sort` request parameter.
- **Control that fails:** no allowlist, and the value is not bound.
- **Boundary crossed:** one customer to other customers' rows.
- **Resource:** the `orders` table, including `secret_note`.

**NEEDS VALIDATION**
- Whether the HTTP layer already restricts `sort` to known values. If it does, F1 and F2 drop in severity. Settled by reading the code that builds `request`.
- Whether DB exceptions reach the client verbatim. That would add an information-leak finding. Settled by reading the exception mapping.

**REFUTED**
- *admin.py is injectable.* Refuted: line 12 rejects any value not in `SORTABLE` before line 14 builds the query, and every allowlisted value is a fixed column name.
- *admin.py is reachable by customers.* Refuted: lines 9-10 raise unless `role == "admin"`.

**WHAT HOLDS UP:** admin.py is correct: it checks the role first, then the allowlist, then interpolates only allowlisted values. The `customer = ?` binding in exports.py and reports.py is correctly parameterized. All three listings were given sorting, so the change matches the request.

**UNVERIFIED CLAIMS:** None asserted by the work. Test coverage is unknown because no tests were supplied.

**QUESTIONS FOR THE AUTHOR:** Does anything upstream restrict `sort`? Which sort keys should customers see on each listing?

**DECISION-MAKER SUMMARY:** Do not release. F1 and F2 let any customer read other customers' orders. The fix is a small allowlist per endpoint, copied from admin.py, plus a test per endpoint that a bad sort key is rejected.

**OWNER SUMMARY:** The new sorting on the customer export and the customer summary report trusts whatever the browser sends. A customer could use this to see other customers' orders and private notes. The staff-only list is built safely, and the same approach should be applied to the other two before release.

```json
{
  "verdict": "REWORK",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "exports.py:8",
     "scenario": "A logged-in customer supplies a crafted sort value; it is interpolated unvalidated into ORDER BY, escaping the customer = ? filter and exposing other customers' rows including secret_note.",
     "fix": "Validate sort against an allowlist {id,total} and map it to a fixed column before building the query; add a test that a non-allowlisted sort raises before query() runs."},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "reports.py:8",
     "scenario": "Same root cause as exports.py:8 in the grouped totals query; a customer's sort value reaches the SQL parser and can expose other customers' data.",
     "fix": "Validate sort against {customer,total} via a shared helper; add a rejection test."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "admin.py:12-13, exports.py:8, reports.py:8",
     "scenario": "A bad sort key yields ValueError on admin but a raw database error on the other two, possibly surfaced to clients.",
     "fix": "One shared validate_sort helper so all three endpoints fail the same way."}
  ]
}
```