# Redteam report: Pedalo ops API handlers

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** I had no subagent and no tools, so I traced every finding by hand. None of the reproductions were executed.

**VERDICT: REWORK.** `/staff/trips.csv` has no staff check. Any rider token gets every rider's name and email, which is exactly what the request forbids. The test suite passes anyway because it never touches that route.

**CONFIDENCE: medium.** The trace is short and unambiguous, but I ran no code. The reproductions below are written but not executed, and the inputs are limited to the four supplied files.

**INPUTS LEDGER**
- **Seen:** `request.md`, `context.md`, `app.py`, `auth.py`, `trips.py`, `test_app.py`.
- **Not seen:**
  - The production deployment and routing layer. It matters for S2: whether anything in front of `handle()` already gates `/staff`.
  - Where tokens and rider records come from in production. It matters for S1 and S2.
- **Not verified:** the context's claim that "4 tests in test_app.py pass". I could not run them. By trace they would pass, which is part of the problem.

**COVERAGE**
- **Scope:** the whole work (4 files).
- **Checked:**
  - Documents: `request.md`, `context.md`.
  - Functions:
    - `app.handle` and all of its routes (`/trips`, `/staff/trips.json`, `/staff/trips.csv`, the 404 fallthrough)
    - `auth.current` and `auth.require_staff`
    - `trips.for_rider`, `trips.all_rows` and `trips.as_csv`
    - all 4 tests
- **Not checked:** the deployment and routing layer (`not_supplied`), and runtime behaviour (`no_tools`).

**SEATS AND GATE**
- **Seats:** one local reviewer ran. No cross-vendor seats, since none were requested and none are available.
- **Gate:** not sensitive. The sample data uses `example.test` placeholder identities. The production data would be personal data, so any future external seat must not receive real exports.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (traced) | B | `app.py:21-22` | The `/staff/trips.csv` branch returns `trips.as_csv()` without calling `auth.require_staff(ident)`. Only `/staff/trips.json` (lines 16-19) has the check. | A rider sends `{"path": "/staff/trips.csv", "token": "tok-rita"}`. `auth.current` succeeds with `("rita", "rider")` and no role check runs. The handler returns 200 with a CSV holding every rider's name and email (including `tomas@example.test`). The request requires 403 here. | **Fix:** wrap the CSV branch in the same `require_staff` / 403 block, or better, enforce staff on every `/staff/` path before route dispatch (see F3). **Reproduction:** `get("/staff/trips.csv", "tok-rita")`. Expected status 403; observed 200, with a body containing `tomas,tomas@example.test`. | a✓ b✓ c✓ d✓ |
| F2 | High | CONFIRMED | B | `test_app.py` (whole suite) | No test touches `/staff/trips.csv`, and no test checks 401 on a `/staff` route. The 4 passing tests cited as assurance in `context.md` cannot detect F1. | F1 ships with a green suite. The same blind spot hides any future regression on the CSV route or on unauthenticated staff access. | **Fix:** add three tests: `test_rider_cannot_export_csv` (expect 403), `test_staff_can_export_csv` (expect 200), and `test_no_token_on_staff_is_401` for both staff routes. **Reproduction:** the new rider-CSV test fails on the current code (200 ≠ 403), which proves it guards F1. Re-run it after the fix to confirm it goes green. | a✓ b✓ c✗ d✓ |
| F3 | Low | CONFIRMED (traced) | B | `app.py:15-23` | Authorisation is checked separately in each route instead of once for the `/staff` prefix. The request says "everything under /staff is for staff only". | 1. A rider requesting `/staff/anything-else` gets 404 instead of 403, which differs from the stated rule and lets a rider probe which staff routes exist. 2. The design defaults open: F1 is what happens when one branch forgets the check. | **Fix:** before dispatch, add `if path.startswith("/staff/"): require_staff(ident)` and return 403 on failure. **Reproduction:** `get("/staff/x", "tok-rita")`. Expected 403 per the request; observed 404. | a✓ b✓ c✗ d✗ |

**Confirm or refute (F1).** The strongest defence would be that the CSV route is meant to be public. The request rules that out: it names `/staff/trips.csv` explicitly as staff-only with 403 for riders. Another defence would be that `auth.current` enforces the role. It does not: it only maps a token to `(name, role)`. F1 stands.

**Sibling search**
- **F1:** I searched every branch of `app.handle` and every caller of `trips.all_rows` and `trips.as_csv` in the supplied files.
  - `/trips` is correctly scoped to `ident[0]` through `for_rider`.
  - `/staff/trips.json` is checked.
  - `/staff/trips.csv` is the only unchecked data route. There are no other callers.
  - F1 is a security finding:
    - Principal: an authenticated rider.
    - Input: the path `/staff/trips.csv`.
    - Failed control: `require_staff` is never called on that branch.
    - Boundary crossed: rider to staff.
    - Resource: every rider's name and email.
- **F2:** I searched for other untested routes and paths.
  - The 404 fallthrough is untested.
  - 401 on `/staff/*` is untested.
  - The CSV route is entirely untested.
  - I folded these into F2's fix because they share one root cause: the suite covers only `/trips` and the JSON route. Each needs its own test.

## Needs validation
- **S1, CSV formula and delimiter injection** (`trips.py:20`). Values are joined with commas and nothing is quoted or escaped. A name or email containing `,`, a newline, or a leading `=`, `+`, `-` or `@` would break the CSV or run as a formula when staff open it in a spreadsheet. **What would settle it:** whether riders can set their own name or email in production. The sample data is hardcoded.
- **S2, hardcoded tokens** (`auth.py:5`). Staff bearer tokens (`tok-sam`, `tok-ola`) are literals in source. Anyone who can read the repository could export all rider personal data. **What would settle it:** whether this token table ships to production or is only a fixture replaced by a real identity provider.

## Refuted
- **"A missing or non-string token crashes or bypasses auth."** `auth.current` maps any non-`str` value to `b""`, and `b""` matches no known token, so the request gets `AuthError` and then 401. `None` is covered by `test_no_token_is_401`.
- **"Riders can see other riders' trips via `/trips`."** `for_rider(ident[0])` filters on the name taken from the token. The request has no rider-name parameter that could be tampered with.

## What holds up
- Token lookup uses `hmac.compare_digest`, rejects unknown tokens with 401, and runs before any route.
- `/trips` correctly scopes data to the caller.
- `/staff/trips.json` correctly returns 403 for riders and 200 for staff.
- `trips` returns copies (`dict(t)`), so callers cannot mutate the store.

## Unverified claims
- **"4 tests in test_app.py pass."** To confirm, run `python -m unittest test_app` in a scratch copy. By trace they would pass, and that is the point of F2.

## Questions for the author
1. Is anything in front of `handle()` (a gateway or middleware) already enforcing `/staff/*` for staff only? If so, F1 drops in practice, but the handler still contradicts the request.
2. Does the `_TOKENS` table ship to production? (S2)

## Decision-maker summary
Do not deploy. The CSV staff export is open to any logged-in rider and leaks every rider's name and email, and the passing tests never check it. The fix is a one-line authorisation check plus three tests. Deploying anyway means a personal-data exposure available to every rider account.

## Owner summary
One of the two staff-only download links has no lock on it, so any rider who is logged in can download every rider's name and email address. The automated checks did not catch this because none of them try that link. It is a small fix, but it must be made and tested before going live.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "app.py", "status": "seen", "matters": true},
    {"item": "auth.py", "status": "seen", "matters": true},
    {"item": "trips.py", "status": "seen", "matters": true},
    {"item": "test_app.py", "status": "seen", "matters": true},
    {"item": "production routing/gateway layer", "status": "not_seen", "matters": true},
    {"item": "production token and rider-record sources", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Sample data uses example.test placeholder identities; no real personal data supplied."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "app.py", "kind": "file"},
      {"unit": "app.py:handle", "kind": "function"},
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:current", "kind": "function"},
      {"unit": "auth.py:require_staff", "kind": "function"},
      {"unit": "trips.py", "kind": "file"},
      {"unit": "trips.py:for_rider", "kind": "function"},
      {"unit": "trips.py:all_rows", "kind": "function"},
      {"unit": "trips.py:as_csv", "kind": "function"},
      {"unit": "test_app.py", "kind": "file"},
      {"unit": "claim: 4 tests in test_app.py pass", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "production routing/gateway layer", "reason": "not_supplied"},
      {"unit": "runtime execution of tests and reproductions", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:21-22",
     "scenario": "A rider token (tok-rita) on GET /staff/trips.csv passes authentication, no role check runs, and the response is 200 with every rider's name and email; the request requires 403.",
     "fix": "Call auth.require_staff(ident) and return 403 on AuthError for /staff/trips.csv, preferably as a single check on every /staff/ path before dispatch.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "get('/staff/trips.csv', 'tok-rita'): expected status 403, observed 200 with body containing 'tomas,tomas@example.test'.",
     "security": true,
     "boundary": {"principal": "an authenticated rider", "input": "the /staff/trips.csv path",
                  "control": "require_staff is never called on the CSV branch", "crossed": "rider to staff",
                  "resource": "every rider's name and email"},
     "siblings_searched": {"searched": "every branch of app.handle and every caller of trips.all_rows and trips.as_csv in the supplied files",
                           "found": "/staff/trips.csv is the only unchecked data route; /trips is correctly scoped and /staff/trips.json is checked"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_app.py (whole suite)",
     "scenario": "No test exercises /staff/trips.csv or 401 on /staff routes, so the suite is green while F1 leaks all rider PII.",
     "fix": "Add test_rider_cannot_export_csv (403), test_staff_can_export_csv (200) and test_no_token_on_staff_is_401 for both staff routes.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Add assertEqual(get('/staff/trips.csv', 'tok-rita')['status'], 403); it fails on the current code (observed 200), confirming it guards F1.",
     "security": false,
     "siblings_searched": {"searched": "all routes in app.handle against the four tests",
                           "found": "CSV route, 401 on /staff routes and the 404 fallthrough are all untested"}},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:15-23",
     "scenario": "Authorisation is checked separately in each /staff route, so a missed route fails open (as F1 shows), and a rider on an unknown /staff path gets 404 instead of the 403 the request specifies for everything under /staff.",
     "fix": "Before dispatch: if path.startswith('/staff/'), call require_staff and return 403 on failure.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "get('/staff/x', 'tok-rita'): expected 403 per the request, observed 404."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "trips.py:20",
     "suspicion": "Unquoted CSV output allows delimiter breakage and spreadsheet formula injection via rider name or email.",
     "unresolved_fact": "Whether riders can set their own name or email in production."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "auth.py:5",
     "suspicion": "Staff bearer tokens are hardcoded in source; anyone who can read the repository could export all rider PII.",
     "unresolved_fact": "Whether this _TOKENS table ships to production or is a fixture replaced by a real identity provider."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "A missing or non-string token crashes or bypasses auth.",
     "evidence": "auth.current maps non-str tokens to b'', which matches no known token, so AuthError leads to 401; test_no_token_is_401 covers None."},
    {"id": "C2", "candidate": "Riders can read other riders' trips via /trips.",
     "evidence": "app.py calls trips.for_rider(ident[0]), filtering on the name taken from the token; there is no client-controlled rider parameter."}
  ]
}
```