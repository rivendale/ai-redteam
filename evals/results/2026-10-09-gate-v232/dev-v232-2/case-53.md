**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available, so nothing below was executed. Every finding comes from reading and tracing the supplied code by hand.

VERDICT: **SHIP**. The sort value is checked against a fixed list before it reaches SQL in all three listings, and customer scoping and the admin check are intact. The only confirmed defects are Low: a malformed sort value produces the wrong error type.

CONFIDENCE: **medium**. It is limited by a same-context review, no tools, no diff or prior versions, no tests, and no view of the request-parsing layer that builds `request`.

INPUTS LEDGER:
- Seen: `request.md` (verbatim), `context.md`, and the full files `admin.py`, `db.py`, `exports.py`, `reports.py`.
- Not seen:
  - **The diff or pre-change versions.** I cannot tell which lines are new, so I reviewed whole files. This matters a little: I cannot say whether the admin check is new or existing.
  - **The request-parsing and error-rendering layer.** It decides whether `role` and `user` can be supplied by the client, and how `ValueError` messages are shown. This matters because it underpins the authorization and reflection questions in NEEDS VALIDATION.
  - **Tests.** None were supplied. This matters because the allowlist behaviour is unguarded against future regression.

COVERAGE: Scope is the whole work (4 files). I checked:
- each file;
- the functions `list_orders`, `export_orders`, `totals_report` and `query`;
- the context claim "Each listing refuses an unknown sort field";
- the assumptions that `request["user"]` is verified and that `role` is server-set.

Not checked: the request layer, the error rendering and any tests (all not supplied), and runtime behaviour (no tools).

SEATS AND GATE: Same-context self-review ran. No subagent and no cross-vendor seats were available. Sensitivity gate: the code and seed data are synthetic, so nothing sensitive was found.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | CONFIRMED (traced) | B | admin.py:12-14 | A non-string `sort` gets past the intended `ValueError` path. | `sort=None` (for example JSON `null`): `None not in SORTABLE` is True, then `"cannot sort by " + None` raises `TypeError`. `sort=["id"]` raises `TypeError: unhashable type` at the membership test. The request is still refused, but as a 500, not a clean rejection. | Check `isinstance(sort, str)` first, or use `f"cannot sort by {sort!r}"`. Repro: `list_orders({"role":"admin","sort":None})`; expect `ValueError`, observe `TypeError`. | a✓ b✓ c✗ d✗ |
| F2 | Low | CONFIRMED (traced) | B | exports.py:7-9 | Same root cause as F1. | `export_orders({"user":"ann","sort":None})` raises `TypeError` instead of `ValueError`. | Same fix as F1. Repro: the call above; expect `ValueError`, observe `TypeError`. | a✓ b✓ c✗ d✗ |
| F3 | Low | CONFIRMED (traced) | B | reports.py:7-9 | Same root cause as F1. | `totals_report({"user":"ann","sort":None})` raises `TypeError`. | Same fix as F1. Repro: the call above; expect `ValueError`, observe `TypeError`. | a✓ b✓ c✗ d✗ |

None of these needed a sibling search, since none is High or Critical. I still checked every listing and found the same pattern in all three, recorded as F1 to F3.

## NEEDS VALIDATION

- **N1** (exports.py:9, reports.py:9, admin.py:10): Can a customer supply `user` or `role` through the same request dict that carries `sort`, for example with `?user=bo&role=admin`? If so, the scoping and the admin check fail. Settled by: how the server builds `request`, and whether auth fields are written after client parameters and cannot be overridden.
- **N2** (admin.py:14, exports.py:9, reports.py:9): The error message echoes raw user input. If it is rendered as unescaped HTML or written raw to logs, this is reflected XSS or log injection. Settled by: the error-handling and rendering code.
- **N3** (admin.py:15, exports.py:10): There is no tiebreaker in `ORDER BY`. The seed data already has ties: ann has three rows under `customer`, and ids 3 and 5 are both 30.0 under `total`. Order among tied rows is undefined, so repeated calls may differ, which matters if pagination or diffing of exports is added later. Settled by: whether consumers need a stable order. The fix would be `order by {sort}, id`.
- **N4**: Sort direction (asc/desc) is not supported. The request does not mention direction, so this is not drift unless the requester expected it. Settled by: asking the requester.
- **N5**: Whether tests exist that pin the allowlist. The mutation that would settle it: remove the `if sort not in …` check and confirm a test with `sort="id; drop table orders"` or `sort="secret_note"` goes red.

## REFUTED

- **SQL injection through the f-string `ORDER BY`.** All three functions check exact string membership in a fixed set before interpolating (admin.py:13, exports.py:8, reports.py:8). Look-alike or differently cased input such as `"ID"` or a Cyrillic `і` fails the check.
- **Sorting by a hidden column (`secret_note`).** No allowlist contains it, and no query selects it.
- **Cross-customer leak in export or report.** Both filter on `where customer = ?` with `request["user"]` passed as a bound parameter.
- **`order by total` in reports sorting by the raw column instead of the sum.** SQLite resolves an `ORDER BY` name to the result-column alias first, so it sorts by `sum(total)`.
- **Admin listing reachable by customers.** The role check runs before any query (admin.py:10-11). Whether `role` can be forged is N1, not a defect in this code.

## WHAT HOLDS UP

- The context claim "each listing refuses an unknown sort field" is true for all three listings.
- Each allowlist matches its columns. The report correctly omits `id`, because grouped rows have no id.
- Defaults (`id`, `id`, `customer`) are all in their own allowlists.
- Parameter binding is kept for the customer value.
- The work fits the request: sorting on exactly the three listings, with no extras.

## UNVERIFIED CLAIMS

- "`request["user"]` is the verified customer name" and "`role` is admin for staff" come from the context only. Confirm them in the auth middleware (N1).
- Nothing in the work claims to have been tested. Whether tests exist is unknown (N5).

## QUESTIONS FOR THE AUTHOR

1. Can client-supplied parameters overwrite `user` or `role` in `request`?
2. How are `ValueError` messages surfaced to the client and to the logs?

## DECISION-MAKER SUMMARY

The sorting change is safe to release: injection is blocked by the allowlists, and customer scoping is unchanged. Before or soon after release, fix F1 to F3 (a malformed sort value returns a 500) and confirm N1. N1 sits outside the sorting change, but if it fails, any customer could read all orders.

## OWNER SUMMARY

The new sorting option is safe: customers can only sort by a few approved columns and still only see their own orders. One small issue is that an oddly formed sort value causes a server error instead of a polite refusal, which is easy to fix. We also recommend confirming that customers cannot pretend to be staff through the same request, a question that predates this change.

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
    {"item": "diff / prior versions", "status": "not_seen", "matters": false},
    {"item": "request parsing and error rendering layer", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "synthetic code and seed data only"},
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
      {"unit": "Each listing refuses an unknown sort field", "kind": "claim"},
      {"unit": "request user/role are server-set", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "request parsing and error rendering layer", "reason": "not_supplied"},
      {"unit": "tests", "reason": "not_supplied"},
      {"unit": "runtime behaviour", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "admin.py:12-14",
     "scenario": "sort=None or a list: membership test or string concatenation raises TypeError, so the request fails with a 500 instead of the intended ValueError rejection.",
     "fix": "Reject non-string sort first (isinstance check) or format the message with {sort!r}.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "list_orders({'role':'admin','sort':None}); expect ValueError, observe TypeError (traced, not run)."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "exports.py:7-9",
     "scenario": "sort=None or a list raises TypeError instead of ValueError.",
     "fix": "Same as F1.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "export_orders({'user':'ann','sort':None}); expect ValueError, observe TypeError (traced, not run)."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "reports.py:7-9",
     "scenario": "sort=None or a list raises TypeError instead of ValueError.",
     "fix": "Same as F1.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "totals_report({'user':'ann','sort':None}); expect ValueError, observe TypeError (traced, not run)."},
    {"id": "N1", "status": "needs_validation", "track": "B", "location": "exports.py:9, reports.py:9, admin.py:10",
     "suspicion": "Client parameters may be able to override user or role in the request dict.",
     "unresolved_fact": "How the server builds request and whether auth fields are written after client parameters."},
    {"id": "N2", "status": "needs_validation", "track": "B", "location": "admin.py:14, exports.py:9, reports.py:9",
     "suspicion": "Raw sort value echoed in the error message may be rendered unescaped or logged raw.",
     "unresolved_fact": "The error handling and rendering code."},
    {"id": "N3", "status": "needs_validation", "track": "B", "location": "admin.py:15, exports.py:10",
     "suspicion": "No ORDER BY tiebreaker; tied rows have undefined order.",
     "unresolved_fact": "Whether any consumer needs a stable order (pagination, diffing)."},
    {"id": "N4", "status": "needs_validation", "track": "B", "location": "request.md",
     "suspicion": "Sort direction is not supported.",
     "unresolved_fact": "Whether the requester expected asc/desc."},
    {"id": "N5", "status": "needs_validation", "track": "B", "location": "tests (not supplied)",
     "suspicion": "Allowlist behaviour may be untested.",
     "unresolved_fact": "Whether a test goes red when the allowlist check is removed."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "SQL injection via f-string ORDER BY.", "evidence": "Exact membership check against a fixed set precedes interpolation in all three functions."},
    {"id": "C2", "candidate": "Sorting by or exposing secret_note.", "evidence": "Not in any allowlist and not selected by any query."},
    {"id": "C3", "candidate": "Cross-customer rows in export or report.", "evidence": "where customer = ? with request['user'] bound as a parameter."},
    {"id": "C4", "candidate": "Report 'order by total' sorts by the raw column.", "evidence": "SQLite resolves ORDER BY names to result-column aliases first, so it sorts by sum(total)."},
    {"id": "C5", "candidate": "Admin listing reachable by customers.", "evidence": "Role check at admin.py:10-11 runs before the query; forgeability of role is tracked as N1."}
  ]
}
```