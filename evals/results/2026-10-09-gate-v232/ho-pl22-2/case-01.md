VERDICT: **REWORK.** `/staff/trips.csv` has no staff check, so any rider token can download every rider's name and email, which is exactly the leak the request was meant to prevent.

CONFIDENCE IN VERDICT: **high** for the main finding, which I traced line by line. I had no tools in this session, so test results and mutation checks are reasoned, not run.

## Pass 1: Reconstruct

The work claims to add handlers where `/trips` returns only the caller's trips and both `/staff/*` exports are staff-only, with 401 for no token and 403 for a rider token. It does this with one `handle()` function: it authenticates first, then matches exact paths, and each `/staff` route is supposed to call `auth.require_staff` itself. For this to be correct, every `/staff` branch must call `require_staff`. It also relies on two unstated assumptions:

- A rider's display name uniquely identifies them, because trips are filtered on `rider == name`.
- The hardcoded token table is acceptable for production.

## Pass 2: Attack (Track B, plus Track R for personal data)

**Traced paths:**

| Request | Code path | Result | Spec |
|---|---|---|---|
| No token → `/staff/trips.csv` | `current(None)` → `supplied=b""` → no match → `AuthError` | 401 | ✅ |
| `tok-rita` → `/staff/trips.json` | `require_staff(("rita","rider"))` raises | 403 | ✅ |
| `tok-rita` → `/staff/trips.csv` | `app.py:21-22`, no `require_staff` | **200 + all names/emails** | ❌ |
| `tok-rita` → `/staff/anything-else` | falls through | 404 | spec says 403 for a rider on a /staff route |
| `{"token": "tok-sam"}` with no `"path"` key | `request["path"]` raises `KeyError` | unhandled exception | — |

**Test mutation (reasoned):**
- If I deleted the `require_staff` block from the JSON route, `test_rider_cannot_export_json` would return 200 and go red. That test guards something real.
- No test touches `/staff/trips.csv` at all. The existing CSV bug is the "mutation", and the suite stays green.

## FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | **Critical** | CONFIRMED | `app.py:21-22` (`if path == "/staff/trips.csv": return {"status": 200, "body": trips.as_csv()}`) | The CSV export never calls `auth.require_staff`. | Rider `tok-rita` requests `/staff/trips.csv` and gets 200 with every rider's name and email, including other riders' data. This is a personal-data breach and breaks the spec's "rider token on a /staff route gives 403". | Gate the route on `require_staff`. Add `test_rider_cannot_export_csv` (expect 403) and `test_staff_can_export_csv` (expect 200). Confirm the new rider test fails against the current code before applying the fix. |
| 2 | High | CONFIRMED | `app.py:13-22` (per-route authorization) | Staff authorization is opt-in for each branch, not enforced for "everything under /staff". Finding 1 is a direct result of this design, and the next `/staff` route added will have the same risk. A rider on an unknown `/staff/...` path gets 404, not the 403 the spec asks for. | A developer adds `/staff/riders.json` and forgets the check, and riders can read it. Separately, `tok-rita` on `/staff/x` gets 404, which also confirms which staff routes exist. | Before dispatching, check `path.startswith("/staff/")` (or `== "/staff"`), call `require_staff`, and return 403 on failure. Add a test that loops over all `/staff` routes with a rider token and expects 403 for each. |
| 3 | High | CONFIRMED | `test_app.py` (4 tests total) | The context says "4 tests pass" as if that shows readiness. There are no tests for the CSV route, for 401 on any `/staff` route, or for an invalid (not missing) token. The JSON staff test checks only the status code, not the body. | The suite is green even though a Critical data exposure exists (finding 1). | Add tests: 401 for no token and for a bad token on both `/staff` routes; 403 for a rider on both; 200 with the expected rows for staff on both. |
| 4 | Medium | PROBABLE | `auth.py:4` (`_TOKENS = {"tok-rita": ..., "tok-sam": ..., "tok-ola": ...}`) | Static bearer tokens, including two staff tokens, are hardcoded in source. This is a fixture presented as production auth. The request was reviewed "before production". | Anyone with repo or artifact access holds working staff tokens, and the tokens cannot be rotated without a code deploy. | Load tokens or identities from a secret store or identity provider. If this is meant to be a stub, label it as one and block deploy until it is replaced. |
| 5 | Medium | PROBABLE | `trips.py:13-14` (`for_rider` filters on `t["rider"] == name`) and `app.py:14` (`ident[0]`) | Trip ownership is keyed on a display name, not a unique rider ID. | Two riders both named "rita" each see the other's trips and email. | Key trips and identities on a stable unique rider ID. Add a test with two riders who share a name. |
| 6 | Medium | PROBABLE | `trips.py:22` (f-string CSV) | Values are not quoted or escaped, and there is no guard against spreadsheet formula injection. | A rider name containing a comma shifts the columns. A name such as `=HYPERLINK(...)` runs as a formula when staff open the export in a spreadsheet. | Write the CSV with the `csv` module (`QUOTE_ALL`), and prefix any value starting with `= + - @` with a `'`. Add a test with a comma and a leading `=`. |
| 7 | Low | CONFIRMED | `app.py:11` (`request["path"]`) | A missing `path` key raises `KeyError` after authentication succeeds. | A malformed request produces an unhandled exception or 500, not a 400 or 404. | Use `request.get("path")` and return 400 or 404 when it is missing. |

## WHAT HOLDS UP

- **Authentication runs before routing.** Every route, including unknown ones, returns 401 without a valid token. `None`, empty, and non-string tokens all become `b""`, which matches nothing.
- **Token comparison** uses `hmac.compare_digest`, a constant-time comparison.
- **The JSON export** correctly returns 403 for riders, and its test guards it.
- **Rider scoping on `/trips`** returns copies of only matching rows. Its test checks that the result is non-empty and contains only the caller's trips.
- **Error bodies** do not leak data, and nothing logs personal data.

## UNVERIFIED CLAIMS

- **"4 tests in test_app.py pass."** I could not run them. Confirm with `python -m unittest test_app -v`. Even if they pass, they do not cover finding 1.
- **That the hardcoded token table is not what ships to production.** Confirm from the deploy configuration.

## QUESTIONS FOR THE AUTHOR

1. Was the missing staff check on the CSV route intentional? If not, will you move to a single `/staff` prefix gate?
2. Is `auth._TOKENS` a placeholder, and what replaces it in production?
3. Are rider names guaranteed unique, or is there a rider ID that should be used instead?

## DECISION-MAKER SUMMARY

Do not deploy. Any rider can currently download every rider's name and email through the CSV export, and the test suite does not catch it. Fix the staff gate (ideally one check covering all of `/staff`), add CSV and authorization tests, and replace the hardcoded tokens before release. If this ships as is, the risk is a reportable personal-data breach.

## OWNER SUMMARY

The new system has a gap: any ordinary rider can download a file containing every rider's name and email address. The automated checks did not catch this because no one wrote a check for that download. It is a small fix, but it must be made and verified before the system goes live.

```json
{
  "verdict": "REWORK",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "app.py:21-22, /staff/trips.csv branch",
      "scenario": "Rider token tok-rita requests /staff/trips.csv and receives 200 with every rider's name and email; spec requires 403.",
      "fix": "Call auth.require_staff and return 403 on AuthError; add rider-403 and staff-200 tests for the CSV route, confirming the rider test fails before the fix."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "app.py:13-22, per-route authorization",
      "scenario": "Staff authorization is opt-in per branch; a new /staff route added without the check is exposed, and a rider on an unknown /staff path gets 404 instead of 403.",
      "fix": "Enforce require_staff once for any path under /staff before dispatch; add a test that iterates all /staff routes with a rider token expecting 403."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "test_app.py",
      "scenario": "The suite passes while the CSV route leaks all personal data; there are no tests for the CSV route, for 401 on /staff routes, for invalid tokens, or for the staff response body.",
      "fix": "Add 401 (missing and bad token), 403 (rider), and 200-with-expected-body (staff) tests for both /staff routes."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "auth.py:4, _TOKENS",
      "scenario": "Staff bearer tokens are hardcoded in source; anyone with repo access can authenticate as staff, and tokens cannot be rotated without a deploy.",
      "fix": "Load tokens from a secret store or identity provider, or explicitly mark this as a stub and block production deploy."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "trips.py:13-14 for_rider; app.py:14 ident[0]",
      "scenario": "Two riders with the same display name see each other's trips and email.",
      "fix": "Key identities and trips on a unique rider ID; add a test with a duplicate name."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "trips.py:22, f-string CSV construction",
      "scenario": "A name containing a comma corrupts the columns; a name starting with '=' runs as a formula when staff open the export in a spreadsheet.",
      "fix": "Use the csv module with quoting and neutralize values that start with = + - @; add a test covering both cases."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "app.py:11, request[\"path\"]",
      "scenario": "An authenticated request without a path key raises an unhandled KeyError.",
      "fix": "Use request.get(\"path\") and return 400 or 404 when it is missing."
    }
  ]
}
```