# Adversarial Diagnostic Review: Pedalo ops API handlers

*No tools in this session. Every finding comes from reading the code. Nothing was executed.*

## Pass 1: Reconstruct

The work says it implements the Pedalo ops API. Riders list their own trips at `/trips`. Two staff-only exports, `/staff/trips.json` and `/staff/trips.csv`, dump every rider's trips with names and emails. A missing or unknown token gets 401, and a rider token on any `/staff` route gets 403.

For this to be correct, three things must hold:
- Every `/staff` route must enforce the staff role.
- Token lookup must fail closed.
- The 4 passing tests must cover the access-control promises in the request.

Two assumptions are not stated:
- Each route remembers to call `require_staff`, because there is no central `/staff` guard.
- A static token table compiled into source is acceptable for production.

## Pass 2: Attack (Track B, with Track R for personal data)

**Route by route, using the rider token `tok-rita`:**
- `/trips` returns 200 with only rita's rows. Correct.
- `/staff/trips.json` reaches `require_staff`, which raises, so it returns 403. Correct.
- `/staff/trips.csv` returns 200 with **every rider's name and email**. The branch at `app.py`, `if path == "/staff/trips.csv": return {"status": 200, "body": trips.as_csv()}`, never calls `auth.require_staff(ident)`. This breaks the explicit requirement that a rider token on a /staff route gets 403, and it exposes personal data.

**Hostile token inputs to `auth.current`:**
- `None`, an integer, or bytes become `b""`. That matches no known token, so the result is 401. Correct.
- `""` gives the same result: 401. Correct.
- A missing `"token"` key means `.get` returns `None`, so 401. Correct.
- `auth.current` fails closed. It holds.

**Hostile request shape:** a missing `"path"` key raises `KeyError` at `request["path"]` and the handler crashes instead of returning a status. This is low severity.

**Tests:**
- Nothing touches `/staff/trips.csv`.
- No test checks 401 on a `/staff` route.
- Mutation analysis by trace, not run: deleting `require_staff` from the JSON branch would turn `test_rider_cannot_export_json` red, because it would get 200 instead of 403. That test does guard its route. No test guards the CSV route, and that is exactly where the bug is.

**Secrets:** `_TOKENS` in `auth.py` holds the live bearer tokens in source. The tokens never expire, cannot be revoked without a deploy, and anyone with repository access can impersonate staff.

**CSV construction:** the f-string join does no quoting. A comma, quote or newline in a name or email corrupts rows. A value starting with `=`, `+`, `-` or `@` becomes a formula when staff open the file in a spreadsheet. Today's data is in-memory constants, so this is a latent problem rather than a live one.

**Records:** bulk exports of personal data leave no audit trail of who exported what or when.

**Drift:** the work answers the asked question. The request specifies CSV with 403 behaviour, and the CSV route silently dropped it.

## Pass 3: Self-check

I re-read the CSV finding against the code. The ident is computed and then never checked on that branch, so the finding stands as CONFIRMED.

I dropped the timing side-channel in the `compare_digest` loop. `compare_digest` only leaks length differences, and the tokens are hardcoded anyway, so the finding was not worth its place.

The most serious remaining blind spot is the real production auth and data layer. This code is an in-memory stand-in. If production swaps in a different `trips` or `auth` module, the review would need to be repeated against that code.

---

**VERDICT: REJECT.** Any rider can download every rider's name and email from `/staff/trips.csv`. That is a direct breach of the request and of personal data, and no test covers it.

**CONFIDENCE IN VERDICT: high.** The defect is visible in a two-line branch. The limit is that nothing was executed, including the claim that the 4 tests pass.

### Findings, ordered by severity

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `app.py`, the `/staff/trips.csv` branch | No `require_staff` check | `handle({"path": "/staff/trips.csv", "token": "tok-rita"})` returns 200 with tomas's name and email. This is a personal-data breach and violates "rider token on a /staff route gives 403". | Enforce staff centrally: `if path.startswith("/staff/"): require_staff`, before dispatch. Add a test asserting 403 for a rider and 200 for staff on the CSV route. |
| 2 | High | CONFIRMED | `test_app.py` | No test covers the CSV route or 401 on `/staff/*`. The suite passes with finding 1 present. | A future regression on any staff route ships green. | Parametrize over every `/staff` path × {no token → 401, rider → 403, staff → 200}. Confirm that removing the guard turns these tests red. |
| 3 | High | CONFIRMED | `auth.py`, `_TOKENS` | Live bearer tokens are hardcoded in source, with no expiry or revocation | A repository leak or any developer with access can use `tok-sam` to pull all personal data. A compromised token stays valid until a code deploy. | Load hashed tokens from a secret store or identity provider, with expiry and revocation. Rotate the current values. |
| 4 | Medium | CONFIRMED | `app.py` per-route guards | Authorization is opt-in per route | The next `/staff/...` route added will repeat finding 1. | Use a prefix guard or deny-by-default routing, which is the same fix as finding 1. |
| 5 | Medium | PROBABLE | `app.py` staff branches | Bulk personal-data exports are not audit-logged | After a leak, there is no record of who exported what or when. | Log the actor, route and timestamp on each export, without logging the personal data itself. |
| 6 | Low | CONFIRMED | `trips.py`, `as_csv` | No CSV quoting and no formula neutralisation | A name like `O'Neil, Jr` breaks the columns. A value like `=HYPERLINK(...)` executes in a spreadsheet. | Use `csv.writer` with quoting, and prefix cells starting with `=+-@` with a `'`. |
| 7 | Low | CONFIRMED | `app.py`, `request["path"]` | A missing path raises `KeyError` | A malformed request crashes the handler, which becomes a 500 or an unhandled exception. | Use `request.get("path")` and return 400 or 404. |

### What holds up
- `auth.current` fails closed for `None`, non-string and empty tokens, and uses a constant-time compare.
- The JSON export correctly returns 403 for riders, and its test would catch removal of the guard.
- `/trips` filters by the authenticated identity rather than by a client-supplied name, so it has no direct-object-reference hole.
- Rows are copied, so callers cannot mutate `_TRIPS`.

### Unverified claims
- "4 tests in test_app.py pass." Confirm by running `python -m unittest test_app`.
- That this in-memory `auth` and `trips` code is what will actually run in production. Confirm against the deployed artifact.

### Questions for the author
1. Is the hardcoded token table a placeholder, or the intended production mechanism? If it is the intended mechanism, finding 3 becomes Critical.
2. Was the CSV route meant to be guarded somewhere outside `handle`, such as a gateway? If so, show where. Otherwise finding 1 stands.

### Decision-maker summary
Do not ship. Any rider can download every customer's name and email through the CSV export, and the tests do not catch it. Add a single staff check for all `/staff` routes with tests for each route, and replace the hardcoded tokens before production. Shipping as-is is a reportable personal-data exposure.

### Owner summary
One of the two staff-only download links has no lock on it, so any rider who is logged in can download every rider's name and email address. The automated tests never check that link, which is why they all pass. The fix is small, but this should not go live until it is fixed and tested, and the login keys written into the code should be replaced.

```json
{
  "verdict": "REJECT",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "app.py: `if path == \"/staff/trips.csv\": return {\"status\": 200, \"body\": trips.as_csv()}`", "scenario": "Rider token tok-rita requests /staff/trips.csv and receives 200 with every rider's name and email; request requires 403.", "fix": "Enforce require_staff for all paths starting with /staff/ before dispatch; add tests for rider->403 and staff->200 on the CSV route."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "test_app.py (no test references /staff/trips.csv or 401 on /staff routes)", "scenario": "The suite passes with the CSV authorization hole present; future staff-route regressions ship green.", "fix": "Parametrized tests over every /staff path x {no token:401, rider:403, staff:200}; confirm they fail when the guard is removed."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "auth.py: _TOKENS = {\"tok-rita\": ..., \"tok-sam\": ..., \"tok-ola\": ...}", "scenario": "Anyone with repo access or a leaked copy uses tok-sam to export all personal data; tokens cannot expire or be revoked without a deploy.", "fix": "Load hashed tokens from a secret store or identity provider with expiry and revocation; rotate current values."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "app.py: per-route require_staff calls in handle()", "scenario": "A newly added /staff route omits the check, as the CSV route already did, and leaks data.", "fix": "Deny-by-default prefix guard on /staff/."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "app.py: /staff/trips.json and /staff/trips.csv branches", "scenario": "A bulk personal-data export happens with no record of actor or time, so a breach cannot be investigated.", "fix": "Audit-log actor, route and timestamp per export, without logging the personal data."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "trips.py: as_csv f-string join", "scenario": "Comma, quote or newline in a field corrupts rows; a leading = + - @ triggers formula execution in a spreadsheet.", "fix": "Use csv.writer with quoting and neutralise leading formula characters."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "app.py: path = request[\"path\"]", "scenario": "A request without a path raises KeyError instead of returning a status.", "fix": "Use request.get(\"path\") and return 400/404."}
  ]
}
```