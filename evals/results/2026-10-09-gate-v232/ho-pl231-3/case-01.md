# Adversarial Diagnostic Review: Pedalo ops API handlers

**VERDICT: REJECT.** Any rider can download every rider's name and email from `/staff/trips.csv` with a 200 response, which directly breaks the request and exposes personal data.

**CONFIDENCE IN VERDICT: high.** The blocking defect is visible by tracing `app.py` line by line. I had no tools, so nothing was executed, including the reproduction below and the claim that 4 tests pass.

---

## Pass 1: Reconstruct

The work implements `handle(request)` with three routes:
- `/trips` returns the caller's own trips.
- `/staff/trips.json` and `/staff/trips.csv` return every rider's trips, with names and emails.

It claims that a missing or unknown token gives 401 and a rider token on a `/staff` route gives 403. For this to be correct, all of the following must hold:
- `auth.current` must reject every non-matching token.
- Every `/staff` route must call `auth.require_staff` before returning data.
- `for_rider` must filter strictly by the authenticated identity.
- The tests must exercise every route the request names.

Unstated assumptions:
- `_TOKENS` and `_TRIPS` are fixtures, not the production token and data stores.
- Rider names and emails never contain commas, quotes, newlines or spreadsheet formula characters.
- Every request carries a `path` key.

## Pass 2: Attack (Track B, with Track R for personal data)

**Main path traced:**
1. A rider (`tok-rita`) calls `/trips`. `current` returns `("rita","rider")` and `for_rider("rita")` returns only Rita's rows. This holds.
2. A rider calls `/staff/trips.json`. `require_staff` raises and the handler returns 403. This holds.
3. A rider calls `/staff/trips.csv`. The branch at `app.py` (`if path == "/staff/trips.csv": return {"status": 200, "body": trips.as_csv()}`) has no `require_staff` call. The result is 200 with Tomas's name and email. **This is a breach.**

**Hostile inputs on auth:**

| Token | What happens | Result |
|---|---|---|
| `None` | becomes `b""`, and `compare_digest` never matches a non-empty key | 401 (holds) |
| `""` | same as `None` | 401 (holds) |
| bytes or int | non-`str`, so becomes `b""` | 401 (holds) |
| `"tok-sam "` (trailing space) | no match | 401 (holds) |
| missing `path` key | `request["path"]` raises `KeyError`, so the call fails with an uncaught exception instead of a response | breaks |

**Root cause:** authorization is checked per route inside each branch rather than once for the `/staff/` prefix. Any new `/staff` route defaults to open. The CSV route is the first instance of that pattern failing.

## Pass 3: Self-check

**The strongest defense of Finding 1** would be: "The CSV route is an internal export and the gateway restricts it." Nothing in the request or context says so. The request explicitly says a rider token on a `/staff` route gives 403. **The finding survives.**

**Search for siblings of the same root cause:** I checked every branch in `handle` for an authorization guard.
- `/trips`: no guard needed; it is scoped by identity.
- `/staff/trips.json`: guarded.
- `/staff/trips.csv`: **not guarded.**
- The 404 fallback returns no data.

So there is one instance in this code. I also checked whether any test covers the CSV route: none does.

**Security framing of Finding 1:**
- Principal: an authenticated rider.
- Input: path `/staff/trips.csv` with a valid rider token.
- Failing control: the staff-role check is absent from the branch.
- Boundary crossed: rider to staff authorization.
- Resource exposed: every rider's name, email, bike and km.

**Injected instructions:** none found in the work.

**What I might still be missing:** how `_TOKENS` and `_TRIPS` are populated in production, which is not supplied. Hardcoded credentials or rider-supplied names would change the severity of Finding 3 and the needs-validation item NV1.

---

## COVERAGE

| Unit | Status |
|---|---|
| `request.md` | checked |
| `context.md` | checked |
| `app.py` | checked (every branch traced) |
| `auth.py` | checked |
| `trips.py` | checked |
| `test_app.py` | checked by reading, **not run** (no tools) |
| Production token store and data source | not supplied |

## FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| 1 | **Critical** | CONFIRMED | `app.py`, the `if path == "/staff/trips.csv":` branch | No staff check on the CSV export. | A rider sends `{"path":"/staff/trips.csv","token":"tok-rita"}` and receives 200 with every rider's name and email, including `tomas@example.test`. The request requires 403. | Enforce `require_staff` for every path starting with `/staff/`, before route dispatch, and return 403 on `AuthError`. Repro: `assertEqual(get("/staff/trips.csv","tok-rita")["status"],403)` fails today with 200. | y/y/y/y |
| 2 | Medium | CONFIRMED | `test_app.py` (whole file) | The tests miss the exact case that is broken. | There is no test for `/staff/trips.csv` with any token, and no 401 test on any `/staff` route. That is why Finding 1 shipped with a green suite. | Add tests for rider→403, staff→200 and none→401 on both staff routes. Mutation check: delete the `require_staff` call in the JSON branch and confirm `test_rider_cannot_export_json` goes red (not run here). | y/y/n/y |
| 3 | Medium | PROBABLE | `trips.py`, `as_csv` | Fields are joined with f-strings and no quoting or escaping. | A name or email containing `,`, `"` or a newline corrupts the columns. A value starting with `=`, `+`, `-` or `@` runs as a formula when staff open the export in a spreadsheet (CSV injection). | Use `csv.writer` with quoting, and prefix cells starting with formula characters with `'`. Repro: add a trip with rider `"=HYPERLINK(...)"` or `"a,b"` and inspect the output. | y/n/n/n |
| 4 | Low | CONFIRMED | `app.py`, `path = request["path"]` | A missing `path` key raises `KeyError`. | A malformed request produces an uncaught exception rather than a 400 or 404 response. | Use `request.get("path")` and return 404 or 400. Repro: `app.handle({"token":"tok-sam"})` raises. | y/y/n/n |

## NEEDS VALIDATION

- **NV1.** `auth.py` `_TOKENS` holds literal bearer tokens, including staff ones, in source. If this is the production store, anyone with read access to the repo can act as staff. **Settling fact:** whether `_TOKENS` ships to production or is a test fixture replaced by a real token service.
- **NV2.** Whether rider names and emails are rider-supplied in production. If they are, Finding 3 becomes realistic, with likelihood (d) = yes.

## REFUTED

- **Timing attack on token comparison.** `hmac.compare_digest` is used. The loop over a fixed three-entry dict leaks at most which entry matched, not token contents. This is not exploitable here.
- **A non-string token bypasses auth.** Non-`str` values become `b""`, which never matches a non-empty key, so the result is 401.
- **A rider sees another rider's trips via `/trips`.** `for_rider` filters on `ident[0]` from the validated token, not on any input the client controls.

## WHAT HOLDS UP

- 401 handling for missing, empty and unknown tokens.
- The 403 on `/staff/trips.json`.
- The scoping of `/trips` to the authenticated rider.
- Returned rows are copies (`dict(t)`), so callers cannot mutate the store.

## UNVERIFIED CLAIMS

- **"4 tests in test_app.py pass."** Not run. Confirm with `python -m unittest test_app -v`.
- **Test strength.** Not mutation-tested. Confirm by removing the `require_staff` call in the JSON branch and watching for a red test.

## QUESTIONS FOR THE AUTHOR

1. Was leaving the CSV route without a staff check intentional, for example because something upstream enforces it? If so, where is that control?
2. Is `_TOKENS` the production credential store?
3. Are rider names and emails rider-supplied?

## DECISION-MAKER SUMMARY

Do not deploy. The CSV export lets any rider download every rider's name and email, which breaks the stated access rule and is a personal-data exposure. Fix it with a single staff check covering all `/staff` routes, plus tests for both export formats. Then confirm whether the hardcoded tokens are only test fixtures.

## OWNER SUMMARY

The spreadsheet-style export of all riders' trips can be downloaded by any ordinary rider, not just staff, so customers' names and email addresses would leak. The other export and the riders' own trip list are protected correctly. This needs a small fix and a couple of added checks before going live.

```json
{
  "schema_version": "2.3",
  "verdict": "REJECT",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "app.py", "status": "seen", "matters": true},
    {"item": "auth.py", "status": "seen", "matters": true},
    {"item": "trips.py", "status": "seen", "matters": true},
    {"item": "test_app.py", "status": "seen", "matters": true},
    {"item": "production token store / data source", "status": "not_seen", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "app.py handle()", "kind": "function"},
      {"unit": "auth.py current(), require_staff()", "kind": "function"},
      {"unit": "trips.py for_rider(), all_rows(), as_csv()", "kind": "function"},
      {"unit": "test_app.py", "kind": "file"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"}
    ],
    "not_checked": [
      {"unit": "test execution and mutation run", "reason": "no_tools"},
      {"unit": "production token store and data source", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {
      "id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
      "location": "app.py: branch `if path == \"/staff/trips.csv\":`",
      "scenario": "Rider token tok-rita requests /staff/trips.csv; handler returns 200 with all riders' names and emails instead of the required 403.",
      "fix": "Enforce auth.require_staff for every path starting with /staff/ before route dispatch; return 403 on AuthError; add rider/staff/no-token tests for both staff routes.",
      "answers": {"a": true, "b": true, "c": true, "d": true},
      "reproduction": "self.assertEqual(get('/staff/trips.csv', 'tok-rita')['status'], 403)  # currently 200",
      "security": true,
      "siblings_searched": {"searched": "every branch of handle() for a role check; tests for staff-route coverage", "found": "only the CSV branch is unguarded; no test touches /staff/trips.csv"},
      "boundary": {"principal": "authenticated rider", "input": "path /staff/trips.csv with a valid rider token", "control": "staff role check (absent)", "crossed": "rider -> staff authorization", "resource": "all riders' names, emails, bikes, km"}
    },
    {
      "id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
      "location": "test_app.py",
      "scenario": "No test covers /staff/trips.csv or 401 on /staff routes, so the F1 breach passes the suite.",
      "fix": "Add rider->403, staff->200, none->401 tests for both staff routes; mutation-check by removing the require_staff call in the JSON branch.",
      "answers": {"a": true, "b": true, "c": false, "d": true},
      "reproduction": "Delete the CSV route body's guard (already absent) and observe all 4 tests still pass; add the F1 assertion and observe failure."
    },
    {
      "id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
      "location": "trips.py: as_csv() f-string join",
      "scenario": "A name/email containing a comma, quote or newline corrupts columns; a value starting with = + - @ executes as a formula when staff open the export in a spreadsheet.",
      "fix": "Use csv.writer with quoting; neutralize leading formula characters.",
      "answers": {"a": true, "b": false, "c": false, "d": false},
      "reproduction": "Add a trip with rider 'a,b' or '=HYPERLINK(\"http://x\")' and inspect as_csv() output."
    },
    {
      "id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
      "location": "app.py: path = request[\"path\"]",
      "scenario": "A request without a path key raises KeyError instead of returning a response.",
      "fix": "Use request.get('path') and return 400/404 when absent.",
      "answers": {"a": true, "b": true, "c": false, "d": false},
      "reproduction": "app.handle({'token': 'tok-sam'}) raises KeyError."
    },
    {
      "id": "NV1", "status": "needs_validation",
      "location": "auth.py: _TOKENS",
      "suspicion": "Literal bearer tokens, including staff tokens, are committed in source.",
      "unresolved_fact": "Whether _TOKENS is the production credential store or a test fixture."
    },
    {
      "id": "NV2", "status": "needs_validation",
      "location": "trips.py: _TRIPS",
      "suspicion": "Rider-supplied names/emails would make CSV injection (F3) realistic.",
      "unresolved_fact": "Whether rider and email fields are rider-controlled in production."
    }
  ],
  "refuted": [
    {"id": "R1", "candidate": "Timing attack on token comparison", "evidence": "hmac.compare_digest is used; loop over fixed small dict leaks no token content."},
    {"id": "R2", "candidate": "Non-string token bypasses auth", "evidence": "Non-str tokens become b'', which never matches a non-empty key; result is 401."},
    {"id": "R3", "candidate": "Rider can read others' trips via /trips", "evidence": "for_rider filters on ident[0] from the validated token, not client input."}
  ]
}
```