# Adversarial Diagnostic Review: Pedalo ops API handlers

## Pass 1: Reconstruct

The work implements `handle(request)` for three routes. `/trips` returns the caller's own trips. `/staff/trips.json` and `/staff/trips.csv` are meant to return every rider's trips, with names and emails, to staff only. A missing or unknown token should give 401, and a rider token on a `/staff` route should give 403. The work is correct only if:

- every `/staff` route checks the staff role before returning data;
- `auth.current` rejects every token it does not know;
- `trips.for_rider` filters on the same identifier that the token resolves to;
- the four tests cover the access rules the request names.

There is also an unstated assumption: the hardcoded token table and in-memory data are placeholders and will not be what runs in production.

## Pass 2: Attack (Track B, plus Track R for personal data)

**Trace of `/staff/trips.csv` with token `tok-rita`:**

1. `auth.current` returns `("rita", "rider")`.
2. The path does not equal `/trips` or `/staff/trips.json`.
3. It matches `/staff/trips.csv` at `app.py`, which returns `trips.as_csv()` with status 200.
4. `require_staff` is never called on this branch.

So any rider gets every rider's name and email. This is CONFIRMED by reading the code.

**Hostile token inputs to `auth.current`:**
- `None`, `""`, `123`, and an unknown string all end with `supplied` as `b""` or a non-matching value, so `AuthError` is raised and the handler returns 401. This holds.
- A token sent to a `/staff` route with no valid token also gets 401, because authentication runs before routing. This holds, though no test covers it.

**Mutation reasoning on the tests (I could not run them; this session has no tools):**
- Deleting the `require_staff` call on the JSON branch would make `test_rider_cannot_export_json` fail. That test does guard something.
- Making `for_rider` return all rows would add tomas's trips and fail `test_rider_sees_only_their_own_trips`. That test also guards something.
- Deleting the guard on the CSV branch would break no test. That route has no test at all, which is how the critical defect passed "4 tests pass".

## Pass 3: Self-check

- I downgraded the timing side-channel in the token loop (early return, and `compare_digest` leaks length) to not reportable. It needs a guessable token space to matter, and the hardcoded-token finding already covers that.
- The most serious remaining risk sits outside this code: how the real `request["path"]` is produced. A router or proxy that does not normalize paths (`/staff//trips.csv`, `%2F`, trailing slash, letter case) would send those requests to 404 here. That fails closed in this code, but the result depends on whatever sits in front of it, which I cannot see.

---

**VERDICT: SHIP WITH FIXES.** The CSV export has no staff check and leaks all rider personal data to any rider. Fixing it is a one-line change plus a test, and it blocks release. The rest of the access logic holds.

**CONFIDENCE IN VERDICT: high** for the critical finding, which is a direct trace. **Medium** overall, because I could not run the tests and cannot see how tokens and paths are supplied in production.

### Findings, ordered by severity

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `app.py`, branch `if path == "/staff/trips.csv": return {"status": 200, "body": trips.as_csv()}` | No `require_staff` check on the CSV export. | A rider sends `{"path": "/staff/trips.csv", "token": "tok-rita"}` and gets 200 with every rider's name and email (e.g. tomas@example.test). The request requires 403. | Enforce the role for the whole `/staff/` prefix before dispatch (`if path.startswith("/staff/"): require_staff → 403`) so a new staff route cannot forget it. Add tests: rider on CSV gives 403, staff on CSV gives 200, no token on CSV gives 401. Confirm the new test fails against the current code. |
| 2 | High | CONFIRMED | `test_app.py` (4 tests total) | The tests cover only `/trips` and `/staff/trips.json`. Nothing covers the CSV route or 401 on a `/staff` route. "4 tests pass" is true but says nothing about the leaking route. | Finding 1 passed CI green. Any future regression on the CSV route or the 401 path would also pass. | Add a test for each route × role (none, rider, staff). Add one test that fails if any `/staff/*` route returns 200 to a rider. |
| 3 | High | CONFIRMED (in code); PROBABLE (that it reaches prod) | `auth.py`, `_TOKENS = {"tok-rita": ..., "tok-sam": ..., "tok-ola": ...}` | Tokens are hardcoded in source and guessable from names. There is no expiry, rotation or revocation. | If this ships, anyone with repo access, or anyone who guesses `tok-<staffname>`, can export all personal data as staff. | Load tokens or sessions from a secret store or identity provider, use high-entropy values, and keep nothing in the repo. If this is a stub, mark it as one and block release on replacing it. |
| 4 | Medium | CONFIRMED | `trips.py`, `as_csv` f-string join | The CSV is built by string concatenation, with no quoting or formula neutralizing. | A rider name or email containing `,` or `"` or a newline shifts or breaks columns. A value starting with `=`, `+`, `-` or `@` runs as a formula when staff open the file in a spreadsheet (CSV injection). | Use the `csv` module (quotes fields), and prefix fields that start with `=+-@` with `'`. Add a test using a hostile name. |
| 5 | Medium | UNVERIFIED | `app.py`, staff export branches | The exports of personal data leave no audit record of who exported what, or when. | After a leak (such as finding 1), there is no way to tell which accounts pulled the data. | Log the actor, route, timestamp and row count for each export, with no personal data in the log. Confirm whether the data-protection policy requires this. |
| 6 | Low | CONFIRMED | `app.py`, final `return {"status": 404, ...}` | A rider token on an unknown `/staff/...` path gets 404, but the request says a rider on a `/staff` route gets 403. | A rider can probe `/staff/*` and tell existing routes (403) apart from missing ones (404). The behavior also differs from the spec. | The prefix check from finding 1 fixes this. |
| 7 | Low | CONFIRMED | `app.py`, `path = request["path"]` | A missing `path` key raises `KeyError`, which becomes an unhandled 500. | A malformed request crashes the handler instead of returning 400 or 404. | Use `request.get("path")` and return 400 or 404 when it is absent. |
| 8 | Low | PROBABLE | `trips.for_rider(ident[0])` | Trips are matched on a display name, not a stable rider ID. | Two riders with the same name would each see the other's trips. A rename would orphan trips. | Key trips by an immutable rider ID taken from the token. |

### What holds up

- **401 handling.** No token, empty token, non-string token and unknown token all reach `AuthError`, which returns 401. Authentication runs before routing, so this covers `/staff` routes too.
- **JSON export.** It is correctly guarded and returns 403 for riders. Its test would catch removal of the guard.
- **`/trips` filtering.** Riders see only their own rows, and copies (`dict(t)`) are returned, so callers cannot change the stored data.
- **Unknown paths.** They fail closed with 404.
- **Token comparison.** It uses a constant-time compare.

### Unverified claims

- **"4 tests in test_app.py pass."** By trace, they should. Confirm with `python -m unittest test_app`.
- **That hardcoded tokens and in-memory data are not the production design.** The author needs to confirm this.
- **Path normalization by whatever sits in front of `handle`.** Confirm with the deployment's router config.

### Questions for the author

1. Is `_TOKENS` a stub? What replaces it in production? (This decides whether finding 3 blocks release.)
2. Is an audit trail of personal-data exports required? (This decides the severity of finding 5.)
3. What component produces `request["path"]`, and does it normalize paths?

### Decision-maker summary

Do not deploy until the CSV export checks for staff and has tests proving riders get 403. Today any rider can download every rider's name and email. Also confirm that the hardcoded tokens will be replaced before production. Otherwise, staff access rests on guessable strings in the source code.

### Owner summary

One of the two staff download links has no lock, so any rider who knows the address can download every rider's name and email. The fix is small, but it must be made and tested before this goes live. The login keys are also written directly into the code and are easy to guess, so they need replacing before real use.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "app.py: if path == \"/staff/trips.csv\": return {\"status\": 200, \"body\": trips.as_csv()}", "scenario": "Rider token tok-rita on /staff/trips.csv returns 200 with all riders' names and emails; spec requires 403.", "fix": "Enforce require_staff for every path starting with /staff/ before dispatch; add rider->403, staff->200, none->401 tests for the CSV route and confirm they fail on current code."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "test_app.py (4 tests)", "scenario": "No test touches /staff/trips.csv or 401 on staff routes, so the critical leak passed CI.", "fix": "Add a route x role matrix test, including a check that no /staff/* route returns 200 to a rider."},
    {"severity": "High", "evidence_level": "PROBABLE", "location": "auth.py: _TOKENS hardcoded dict", "scenario": "Guessable tokens in source (tok-sam) let anyone with repo access, or a guesser, export all personal data as staff.", "fix": "Load high-entropy tokens/sessions from a secret store or identity provider; block release on replacing the stub."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "trips.py: as_csv f-string join", "scenario": "Names or emails containing commas, quotes, newlines or a leading = + - @ break columns or execute as spreadsheet formulas on a staff machine.", "fix": "Use the csv module and neutralize leading formula characters; add a hostile-value test."},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "location": "app.py: staff export branches", "scenario": "No audit record of personal-data exports, so a leak cannot be traced to the accounts that exported.", "fix": "Log actor, route, time and row count (no personal data); confirm the policy requirement."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "app.py: final 404 return", "scenario": "Rider on an unknown /staff/... path gets 404 instead of 403, which lets them enumerate routes and deviates from the spec.", "fix": "The /staff/ prefix check returns 403 before route matching."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "app.py: path = request[\"path\"]", "scenario": "A request without a path key raises KeyError, giving an unhandled 500.", "fix": "Use request.get(\"path\") and return 400 or 404 when it is missing."},
    {"severity": "Low", "evidence_level": "PROBABLE", "location": "app.py: trips.for_rider(ident[0])", "scenario": "Trips are keyed by display name; two riders with the same name see each other's trips.", "fix": "Key trips by an immutable rider ID carried in the token identity."}
  ]
}
```