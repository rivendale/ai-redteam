Same-context review, anchoring risk; re-run in a fresh session for anything high-stakes. No tools in this session, so nothing was executed — findings come from reading the source, and reproductions are tests still to run.

## Report

**VERDICT: REWORK** — the `sort` parameter reaches SQL unparameterized in two of the three listings, defeating the per-customer row filter and letting a logged-in customer reach other customers' data including `secret_note`.

**CONFIDENCE: medium** — the injection sinks are clear from the source; no tools means no reproduction was run, so the exact payload behavior in sqlite is UNVERIFIED.

**INPUTS LEDGER**
- Seen: `admin.py`, `db.py`, `exports.py`, `reports.py`, request.md, context.md.
- Not seen: the request-construction / auth layer that sets `request["user"]` and `request["role"]`; any test suite; the real DB backend (sqlite is a stand-in). Matters: how `user`/`role` are trusted upstream.

**COVERAGE**
- Checked: `export_orders`, `totals_report`, `list_orders`, `query`, schema in `db.py`.
- Not checked: upstream auth, real DB engine behavior, concurrency.

**SEATS AND GATE:** sensitivity gate — work contains no real personal data (toy fixtures), not sensitive. Seats: same-context self-review only; no subagent/cross-vendor available.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix & reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | `exports.py:8` | `sort` is interpolated into SQL with an f-string; only `user` is parameterized | A customer sends a crafted `sort` value; the trailing clause is extended so the `where customer = ?` filter no longer confines the result set, exposing other customers' rows and `secret_note` | Reject `sort` against an allow-list (as `admin.py` does) before building SQL; map the validated key to a literal column. Repro: call `export_orders` with a `sort` string containing a subquery/`union`-style clause and confirm rows for other customers appear | a:T b:T c:T d:T |
| F2 | Critical | CONFIRMED | B | `reports.py:8` | Same unparameterized `sort` interpolation | As F1, on the summary report; the per-customer `group by`/filter can be subverted | Same allow-list validation as F1 | a:T b:T c:T d:T |
| F3 | High | CONFIRMED | B | `exports.py`, `reports.py` (missing) | `admin.py` has `SORTABLE` allow-list; the two customer endpoints have none — inconsistent and the gap is exactly where the sink is reachable by every customer | Any invalid/hostile `sort` is accepted on the two broadest-exposure endpoints | Factor one shared validator (allow-list + explicit `asc`/`desc` handling) used by all three | a:T b:F c:T d:T |
| F4 | Medium | CONFIRMED | B | `exports.py:6`, `reports.py:6`, `admin.py:9` | `sort` accepts only a column name; the request param is a single token with no direction — "add sorting from the sort parameter" is met only for ascending single-column. Possible drift if the intended feature was direction/multi-key | Users cannot sort descending; requirement may be under-delivered | Confirm intended `sort` grammar with author; if direction needed, parse and validate it separately | a:T b:T c:F d:T |
| F5 | Low | CONFIRMED | C | `admin.py:11` | Error message echoes the attacker-supplied `sort` back (`"cannot sort by " + sort`) | Reflects input into an error string; minor info-leak/log-injection surface | Return a static message; log the value separately with escaping | a:T b:T c:F d:F |

### NEEDS VALIDATION
- Whether `request["user"]` / `request["role"]` are trusted from a verified session upstream or attacker-settable. Unresolved fact: the auth layer that populates `request` (not supplied). If `role` is client-controllable, `admin.py`'s guard is also bypassable — that would raise it to Critical.
- Whether sqlite's parser actually permits the clause extension through `order by` in this exact query shape. Unresolved fact: a run against the real engine. (The vulnerability class is certain; the precise reachable payload is engine-dependent.)

### WHAT HOLDS UP
- `admin.py` correctly gates on `role == "admin"` and validates `sort` against `SORTABLE` before interpolation — that endpoint's sort handling is sound (subject to the auth-trust question above).
- The `customer = ?` and `group by` filters themselves are parameterized for the `user` value; the defect is solely the `sort` concatenation.

### UNVERIFIED CLAIMS
- "The signed-in customer's own orders" (exports.py docstring) / "own totals" (reports.py) — false in the presence of F1/F2; confirm by running the injection repro.

### QUESTIONS FOR THE AUTHOR
1. Is `request["role"]`/`request["user"]` set server-side from a verified session, or can the client set it?
2. Was descending / multi-column sort in scope for "add sorting"?

### DECISION-MAKER SUMMARY
Do not release. The two customer-facing listings build their sort clause by string-concatenating untrusted input, which can defeat the per-customer filter and expose other customers' order data. Fix by applying the same allow-list the admin endpoint already uses, then re-test with an injection payload before shipping.

### OWNER SUMMARY
The new sorting option on the customer order pages isn't safe to release yet: the way it handles the "sort by" choice could let a signed-in customer pull up other customers' orders. One of the three screens already does this safely and the other two need the same guard added, then a quick test, before this goes live.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "upstream auth setting request['user']/['role']", "status": "not_seen", "matters": true},
    {"item": "test suite", "status": "not_seen", "matters": true},
    {"item": "real DB backend (sqlite is stand-in)", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "toy fixture data only, no real personal data"},
  "coverage": {
    "checked": [
      {"unit": "exports.py", "kind": "file"},
      {"unit": "exports.py:export_orders", "kind": "function"},
      {"unit": "reports.py", "kind": "file"},
      {"unit": "reports.py:totals_report", "kind": "function"},
      {"unit": "admin.py", "kind": "file"},
      {"unit": "admin.py:list_orders", "kind": "function"},
      {"unit": "db.py", "kind": "file"},
      {"unit": "db.py:query", "kind": "function"}
    ],
    "not_checked": [
      {"unit": "upstream auth layer", "reason": "not supplied"},
      {"unit": "real DB engine behavior", "reason": "no tools; sqlite stand-in only"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "exports.py:8",
     "scenario": "A logged-in customer supplies a crafted sort value that extends the trailing clause so the parameterized customer filter no longer confines results, returning other customers' rows including secret_note.",
     "fix": "Validate sort against an allow-list (as admin.py does) and map to a fixed column before building SQL.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Call export_orders with a hostile sort string and confirm rows for a different customer are returned; expect rejection."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "reports.py:8",
     "scenario": "Same unparameterized sort interpolation on the summary report lets a customer subvert the per-customer grouping/filter.",
     "fix": "Apply the same allow-list validation as F1 before building SQL.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Call totals_report with a hostile sort string and confirm it affects rows beyond the signed-in customer; expect rejection."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "exports.py, reports.py",
     "scenario": "The two customer-facing endpoints lack the SORTABLE allow-list that admin.py has, exactly where the injection sink is reachable by every customer.",
     "fix": "Extract one shared sort validator and use it in all three listings.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Pass an invalid sort to export_orders/totals_report; observe it is accepted rather than raising ValueError as admin.py does."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "exports.py:6, reports.py:6, admin.py:9",
     "scenario": "sort accepts only a bare column name with no direction; if descending/multi-key sort was intended the feature is under-delivered (possible request drift).",
     "fix": "Confirm intended sort grammar with author; if direction needed, parse and validate asc/desc separately.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Request a descending sort and observe no supported syntax."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "admin.py:11",
     "scenario": "Error message concatenates attacker-supplied sort into the string, a minor reflection/log-injection surface.",
     "fix": "Return a static error message; log the raw value separately with escaping.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Pass sort='<marker>' to list_orders and observe it echoed in the exception text."}
  ],
  "refuted": []
}
```