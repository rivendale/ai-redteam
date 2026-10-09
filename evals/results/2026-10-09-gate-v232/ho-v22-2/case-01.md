VERDICT: **REWORK**. `/staff/trips.csv` has no staff check, so any rider token can download every rider's name and email.

CONFIDENCE: **medium**. This session had no tools, so nothing was run. The main finding is confirmed by tracing exact lines, and it does not depend on execution. The reviewer did not author the work, but it was a single reviewer with no second seat.

INPUTS LEDGER:
- Seen: request.md (verbatim), context.md, app.py, auth.py, trips.py, test_app.py.
- Not seen: CI output for the claim that "4 tests pass" (doesn't matter much, since all 4 trace to pass); the production token source and rider identity model (matters for S1 and S2); deploy config (doesn't matter for the main finding).

COVERAGE:
- Checked: `app.py:handle`, every route branch; `auth.py:current`, `auth.py:require_staff`; all of `trips.py`; all 4 tests (traced, and mutation-reasoned on paper).
- Not checked: runtime behaviour (no tools), the production token store, the HTTP layer that builds `request`.

SEATS AND GATE: one reviewer (this session, independent of the author, no tools). No cross-vendor seats, since none were requested and none are available. Sensitivity gate: the data is synthetic (`@example.test`), so it is not sensitive. The production data will be personal data.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED (traced) | B | `app.py:20-21` | The CSV branch returns `trips.as_csv()` without calling `auth.require_staff(ident)`. The JSON branch at `app.py:14-19` does call it. | A rider sends `tok-rita` on `/staff/trips.csv`. `auth.current` succeeds, the branch at line 20 matches, and the response is 200 with every rider's name and email (including `tomas@example.test`). The request requires 403. | Wrap line 21 in the same `try: auth.require_staff(ident) / except AuthError: 403` as the JSON branch, or gate all `path.startswith("/staff/")` once before dispatch. Repro: `get("/staff/trips.csv","tok-rita")["status"]` returns 200 now; it should return 403. | a✔ b✔ c✔ d✔ |
| F2 | Medium | CONFIRMED | B | `test_app.py` (whole file) | No test touches `/staff/trips.csv`, and no test checks 401 on a `/staff` route. That gap is how F1 shipped while "4 tests pass". By trace, `test_rider_cannot_export_json` does guard the JSON check: deleting `app.py:15-18` would make it go red. Nothing guards CSV. | A future refactor drops any staff check, CI stays green, and the data leaks. | Add `test_rider_cannot_export_csv` (expects 403), `test_staff_can_export_csv` (expects 200), and `test_no_token_on_staff_is_401` for both exports. The rider/CSV test fails on the current code, which is the reproduction for F1. | a✔ b✔ c✗ d✔ |
| F3 | Low | CONFIRMED | B | `trips.py:20` | CSV fields are joined with an f-string and no quoting or escaping. | A rider name containing a comma or quote (for example `Smith, J`) shifts the columns. A name starting with `=` or `+` becomes a formula when staff open the file in a spreadsheet. | Use `csv.writer` with an `io.StringIO`, and prefix cells starting with `= + - @` with `'`. Repro: add a row with rider `"a,b"`; it produces 5 columns instead of 4. | a✔ b✔ c✗ d✗ |
| F4 | Low | CONFIRMED | B | `app.py:11`, `app.py:22` | `request["path"]` raises `KeyError` if the path is missing (the result is an uncaught exception, not a status). A rider on an unknown `/staff/...` path gets 404, but the request says a rider token on a `/staff` route gives 403. | A rider probing `/staff/anything` learns which staff routes exist (404 versus 403), and a malformed request produces a 500. | Use `request.get("path")`. Apply the staff gate to every `/staff/` prefix before the route lookup. | a✔ b✔ c✗ d✗ |

## Needs validation

- **S1** (`auth.py:4`): staff and rider tokens are string literals in source. Anyone with read access to the repo could act as staff. This is serious only if production uses this table. The unresolved fact: is `_TOKENS` a fixture, or the production token store?
- **S2** (`app.py:13`, `trips.py:10-11`): riders are matched by display name (`ident[0] == t["rider"]`), not a unique ID. Two riders with the same name would see each other's trips. The unresolved fact: is the name a unique account ID in production?

## Refuted

- **R1: a non-string or `None` token could crash `auth.current` or match a key.** `auth.py:15` maps non-strings to `b""`. `compare_digest(b"tok-…", b"")` is False for every key, so it raises AuthError and returns 401.
- **R2: a staff token on `/trips` leaks all trips.** `for_rider("sam")` filters by name and returns `[]`.
- **R3: the JSON export lets riders through.** `require_staff` checks `ident[1] != "staff"`, and a rider gets 403 (`app.py:15-18`).

## What holds up

- The 401 path for missing or unknown tokens applies to every route, because auth runs before dispatch.
- Token comparison is constant-time.
- Rider scoping on `/trips` is correct.
- The JSON staff gate is correct.
- `dict(t)` copies keep callers from mutating the stored rows.

## Unverified claims

- "4 tests in test_app.py pass." I could not run them. By trace, all 4 should pass. To confirm, run `python -m unittest test_app -v`.

## Questions for the author

1. Was the missing CSV check deliberate (for example, gated upstream by a proxy)? If so, where is that enforced?
2. Is `_TOKENS` the production token source?
3. Is the rider name a unique ID?

## Decision-maker summary

Do not deploy. The CSV export skips the staff check, so any logged-in rider can download every rider's name and email, which is a personal-data breach. The fix is about three lines plus two tests (F1, F2). After that, the remaining items are low-risk.

## Owner summary

The new system has a gap: an ordinary rider can download a file with every customer's name and email, which should be staff-only. The tests did not check that file, so they passed anyway. The fix is small and should be made and tested before launch.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "app.py", "status": "seen", "matters": true},
    {"item": "auth.py", "status": "seen", "matters": true},
    {"item": "trips.py", "status": "seen", "matters": true},
    {"item": "test_app.py", "status": "seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false},
    {"item": "production token store / identity model", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session-no-tools", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Synthetic @example.test data; production data will be personal data."},
  "coverage": {
    "checked": [
      {"unit": "app.py", "kind": "file"},
      {"unit": "app.py:handle", "kind": "function"},
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:current", "kind": "function"},
      {"unit": "auth.py:require_staff", "kind": "function"},
      {"unit": "trips.py", "kind": "file"},
      {"unit": "trips.py:as_csv", "kind": "function"},
      {"unit": "test_app.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "runtime test execution", "reason": "no tools in session"},
      {"unit": "HTTP layer constructing request", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:20-21",
     "scenario": "A rider token on GET /staff/trips.csv passes auth.current, hits the CSV branch with no require_staff call, and receives 200 with every rider's name and email instead of 403.",
     "fix": "Call auth.require_staff(ident) and return 403 on AuthError before trips.as_csv(), or gate every /staff/ path once before dispatch.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "get('/staff/trips.csv', 'tok-rita')['status']: expect 403, observe 200 with tomas@example.test in the body."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_app.py",
     "scenario": "No test covers /staff/trips.csv or 401 on /staff routes, so the missing CSV gate (F1) passes CI and any future regression would too.",
     "fix": "Add tests: rider on CSV gets 403, staff on CSV gets 200, no token on both staff routes gets 401.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Add test_rider_cannot_export_csv asserting 403; it fails on the current code."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "trips.py:20",
     "scenario": "A rider name containing a comma or starting with '=' corrupts the columns or injects a spreadsheet formula when staff open the export.",
     "fix": "Use csv.writer with StringIO and neutralise leading = + - @ characters.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Add a row with rider 'a,b'; the CSV line has 5 fields instead of 4."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:11,22",
     "scenario": "A request without a path raises KeyError (uncaught). A rider on an unknown /staff/x path gets 404, not the 403 the request specifies for /staff routes.",
     "fix": "Use request.get('path') and apply the staff gate to every /staff/ prefix before route lookup.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "get('/staff/x', 'tok-rita'): expect 403, observe 404. app.handle({'token': 'tok-rita'}) raises KeyError."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:4",
     "suspicion": "Staff tokens are hardcoded in source; anyone with repo access could act as staff.",
     "unresolved_fact": "Whether production loads tokens from _TOKENS or from a real secret store."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "app.py:13; trips.py:10-11",
     "suspicion": "Riders are matched by display name; riders with the same name would see each other's trips.",
     "unresolved_fact": "Whether the rider name is a unique account identifier in production."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "A non-string or None token crashes or bypasses auth.current.",
     "evidence": "auth.py:15 maps non-strings to b''; compare_digest is False for all keys, so it raises AuthError and returns 401."},
    {"id": "R2", "candidate": "A staff token on /trips returns all trips.",
     "evidence": "for_rider('sam') filters by name and returns []."},
    {"id": "R3", "candidate": "The JSON export admits riders.",
     "evidence": "app.py:15-18 calls require_staff, which raises for role 'rider', so the response is 403."}
  ]
}
```