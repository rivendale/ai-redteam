# Adversarial Diagnostic Review: `can_unlock` (Pedalo bike-share)

**VERDICT: REWORK.** `can_unlock` fails open: any exception, whether from a policy service outage or a user record missing a field, grants unlock to any bike, including bikes reserved for someone else.

**CONFIDENCE IN VERDICT: high.** The fail-open path can be traced line by line in 10 lines of code. The limit is that I have no tools here, so nothing was executed. I also can't see the real policy service, the bike/user schema, or where `user` comes from.

## Pass 1: Reconstruct

The work claims `can_unlock(user, bike)` enforces three rules:
- Riders may unlock bikes that are free or reserved for them.
- Staff may unlock any bike.
- The decision is delegated to the policy service.

It returns `policy.check(...)` and returns `True` on any exception "to keep riders moving." For this to be correct, all of these must hold:
- `policy.check` must implement the rule correctly.
- "Free" must equal `reserved_for is None`.
- `user["name"]` must uniquely identify a rider and match what `reserved_for` stores.
- `user["role"]` must come from a trusted source.
- Unlocking on error must be an acceptable business risk.

The unstated assumption is that failing open is safe. The stated stakes say the opposite: reserved bikes are held for riders, and a stolen bike costs Pedalo and the next rider.

## Pass 2 and 3: Attack and self-check

**Track B (code)** applies, with Track A for the fail-open design decision. Prompt-injection check: the work contains no text addressed to the reviewer. The `# keep riders moving...` comment is design rationale, treated as data.

## FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (line trace) | `perms.py` `except Exception: return True` | Authorization fails open on any exception. | The policy service times out or errors (once it is a real network client). Every `can_unlock` call returns `True`, so any rider can unlock any bike, including bikes reserved for others. That is exactly the stated harm. | Fail closed: return `False` (or raise a typed "unavailable" error the caller turns into "try again"). Catch only the service's transport error, never bare `Exception`. Repro: monkeypatch `policy.check` to raise `TimeoutError`, call `can_unlock({"name":"a","role":"rider"}, {"reserved_for":"b"})`. Expected `False`, got `True`. | y/y/y/y |
| F2 | Critical | CONFIRMED (line trace) | `policy.py` `user["name"]` combined with the `perms.py` catch-all | Malformed or partial user input becomes an unlock. For any non-staff user, `(None, user["name"])` is built before the comparison. A user dict without `"name"` raises `KeyError`. `user=None` raises `AttributeError` on `.get`. Both are caught and turned into `True`. | A guest, a half-registered account, or a session whose user record lacks `name` calls unlock on a bike reserved for someone else and gets `True`. This is triggerable by input, not just by outage. | Same root fix as F1 (fail closed), plus validate `user` and `bike` up front and deny on missing identity. Repro: `can_unlock({"role":"rider"}, {"reserved_for":"alice"})` returns `True`. Also `can_unlock(None, {"reserved_for":"alice"})` returns `True`. | y/y/y/y |
| F3 | Medium | PROBABLE | `policy.py` `bike.get("reserved_for") in (None, ...)` | "Free" is equated with "not reserved." The check ignores whether the bike is currently in a ride, out of service, or flagged stolen. A missing `reserved_for` key is also treated as free. | Rider B requests unlock on a bike mid-ride for rider A, or on a maintenance-locked bike. `reserved_for` is `None`, so access is granted. | Define "free" against the real bike state (e.g. `status == "available"` and no reservation) and deny when the field is absent. Test: bike `{"status":"in_ride","reserved_for":None}` must be denied. | y/n/y/y |
| F4 | Medium | PROBABLE | `policy.py` comparison `reserved_for` == `user["name"]` | The reservation is matched by display name, not a unique ID. | Two riders named "Sam Lee": either can unlock the other's reserved bike. Case or whitespace differences also wrongly deny the real owner. | Compare stable user IDs (`user["id"]` vs `bike["reserved_for_id"]`). Test: two users with the same name and different IDs; only the owner is allowed. | y/n/y/n |
| F5 | Medium | CONFIRMED | `policy.py` docstring "Policy service client (stub)" | The request says "use the policy service." The authorization rule is actually written inline in a local stub, and it is unclear whether this ships. The `except` comment assumes a network service that this stub is not. | The stub ships as-is, so the business rule is unreviewed duplicate logic. Or the stub is replaced by the real client, whose return value may be a response object, `None`, or a dict. A truthy non-bool such as `{"allowed": False}` would grant access. | Call the real client, map its response explicitly to a bool (`resp.allowed is True`), and add a contract test. Repro: stub `check` returning `{"allowed": False}`; `can_unlock` returns a truthy value. | y/y/n/n |
| F6 | Medium | CONFIRMED | (absent) | No tests at all. Nothing guards the reserved-for-other case, the staff case, or the outage behaviour. | A regression or the F1 behaviour ships unnoticed. | Add tests: free bike allowed; own reservation allowed; another's reservation denied; staff allowed; policy raises → denied; missing name → denied. Mutation check: flip `return True` in `except` and confirm a test goes red. | y/y/n/y |
| F7 | Low | CONFIRMED | `perms.py` `DEBUG = False` | Unused module flag. It is dead code and invites a future debug bypass. | None today. | Remove it. Repro: grep shows no reader of `DEBUG` in the supplied files. | n/y/n/n |

**Severity re-examination as the author's strongest defender would argue:**

- **F1.** "Availability matters; stranded riders are also harm." This is a fair business tradeoff, but it was made silently in code, against the stated stakes, and it covers far more than outages (see F2). It survives as Critical. Any fail-open policy would need an explicit owner decision and a narrower scope, for example allowing only bikes known to be unreserved from a local cache.
- **F2.** "Callers always pass full user records." Nothing in the work enforces this, and the catch converts the bug into a grant. It survives.

**Sibling search for the F1/F2 root cause (exception → grant):** I searched both supplied files for other `except`, `.get` defaults, and implicit truthiness.

| Location | What it does | Effect |
|---|---|---|
| `user.get("role")` | Missing role → `None` → treated as non-staff | Safe |
| `bike.get("reserved_for")` | Missing field → `None` → treated as free | Fail-open sibling, logged as F3 |
| `return policy.check(...)` | Returns raw value, no bool coercion | Truthiness sibling, logged as F5 |

No other handlers were found.

**Security boundary (F1/F2):**

| Element | Value |
|---|---|
| Principal | A non-staff rider, or a caller with an incomplete identity |
| Input | A user record lacking `name` (or `None`), or a request made during policy service failure |
| Failing control | The `except Exception: return True` handler in `can_unlock` |
| Boundary crossed | The authorization decision for physical bike release |
| Resource | Reserved bikes belonging to other riders, and any bike |

## NEEDS VALIDATION

- **Trust in `role`.** Where does the `user` dict come from? If any part is client-supplied (request body, unsigned token claim), `{"role":"staff"}` unlocks everything. This is settled by tracing the caller to an authenticated server-side user record.
- **Bike state model.** Does the bike record have a status (in ride, maintenance, stolen)? This decides whether F3 is real or moot.
- **Reservation key.** Does `reserved_for` store a name or a user ID? This settles F4.
- **Real client contract.** What does the production policy client return, what does it raise, and does it have a timeout? This settles the F5 truthiness risk and the realism of F1.
- **Product decision.** Is there any approved requirement to fail open during outages? If so, it must be scoped and recorded.

## REFUTED

- **"Staff check bypasses reservation for riders."** Refuted: only `role == "staff"` short-circuits. Non-staff users always reach the reservation comparison.
- **"Reserved-for-self is denied."** Refuted: `user["name"]` is in the allowed tuple, so the owner is allowed (subject to F4 matching).

## WHAT HOLDS UP

- On well-formed input with the service up, the stub logic matches the literal wording of the request:
  - Staff → allow.
  - Unreserved → allow.
  - Reserved for self → allow.
  - Reserved for another → deny.
- The delegation structure (`perms` → `policy`) is the right shape for "use the policy service."

## UNVERIFIED CLAIMS

- **"keep riders moving when the policy service is down."** This assumes a networked service exists and goes down. The supplied `policy.py` is a local stub. Confirm by locating the production client.
- **Docstring "staff may unlock any."** This is true in the stub only. Confirm the real service enforces the same rule.
- Nothing claims tests were run. None exist.

## QUESTIONS FOR THE AUTHOR

1. Is fail-open on error an approved product decision, and who signed off given the theft and reservation stakes?
2. Is `policy.py` the code that ships, or a placeholder for a real client? If a placeholder, what does the real one return and raise?
3. Is `user` (especially `role`) loaded server-side from an authenticated session?
4. Does a bike have an availability state beyond `reserved_for`?

## DECISION-MAKER SUMMARY

Do not ship. `can_unlock` grants access whenever anything goes wrong, including an outage or a user record missing its name, so reserved bikes can be taken by anyone. Change it to deny on error, match reservations by user ID, add tests for the deny paths, and confirm the real policy service contract. If shipped as-is, the risk is unauthorized unlocks and bike theft during any service hiccup or bad input.

## OWNER SUMMARY

The new unlock check lets anyone unlock any bike, including bikes held for other riders, whenever the permission system has a problem or receives incomplete account details. It also identifies riders by name, which isn't unique, and doesn't check whether a bike is already in use. It needs to refuse unlocks when in doubt, and get proper tests, before it goes live.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "perms.py", "status": "seen", "matters": true},
    {"item": "policy.py", "status": "seen", "matters": true},
    {"item": "production policy service client", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "perms.py:can_unlock", "kind": "function"},
      {"unit": "policy.py:check", "kind": "function"},
      {"unit": "fail-open on outage is acceptable", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "real policy service client", "reason": "not_supplied"},
      {"unit": "caller / source of user dict", "reason": "not_supplied"},
      {"unit": "bike schema", "reason": "not_supplied"},
      {"unit": "test execution and mutation check", "reason": "no_tools"}
    ]
  },
  "findings": [
    {
      "id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
      "location": "perms.py can_unlock: except Exception: return True",
      "scenario": "Policy service raises (timeout/outage); can_unlock returns True for every user and bike, including bikes reserved for others.",
      "fix": "Fail closed (return False or raise a typed unavailable error); catch only the client's transport error.",
      "answers": {"a": true, "b": true, "c": true, "d": true},
      "reproduction": "Monkeypatch policy.check to raise TimeoutError; can_unlock({'name':'a','role':'rider'}, {'reserved_for':'b'}) returns True; expected False.",
      "security": true,
      "siblings_searched": {"searched": "all except handlers, .get defaults and truthiness in perms.py and policy.py", "found": "bike.get('reserved_for') missing-field-as-free (F3); untyped return truthiness (F5)"},
      "boundary": {"principal": "non-staff rider", "input": "unlock request during policy failure", "control": "except Exception: return True", "crossed": "authorization for physical bike release", "resource": "any bike, including reserved bikes"}
    },
    {
      "id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
      "location": "policy.py user[\"name\"] plus perms.py catch-all",
      "scenario": "User dict without 'name' (or user=None) raises KeyError/AttributeError in policy.check; caught and turned into True, unlocking a bike reserved for someone else.",
      "fix": "Fail closed as F1; validate user/bike up front and deny on missing identity.",
      "answers": {"a": true, "b": true, "c": true, "d": true},
      "reproduction": "can_unlock({'role':'rider'}, {'reserved_for':'alice'}) returns True; can_unlock(None, {'reserved_for':'alice'}) returns True; expected False for both.",
      "security": true,
      "siblings_searched": {"searched": "every dict access in policy.check", "found": "user.get('role') safe (defaults to non-staff); bike.get('reserved_for') fail-open (F3)"},
      "boundary": {"principal": "caller with incomplete or absent identity", "input": "user record lacking name, or None", "control": "except Exception: return True", "crossed": "authorization for physical bike release", "resource": "bikes reserved for other riders"}
    },
    {
      "id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
      "location": "policy.py bike.get(\"reserved_for\") in (None, ...)",
      "scenario": "Bike in an active ride or maintenance with reserved_for None, or missing the field, is treated as free and unlocked.",
      "fix": "Check real availability status and deny when the field is absent.",
      "answers": {"a": true, "b": false, "c": true, "d": true},
      "reproduction": "can_unlock({'name':'b','role':'rider'}, {'status':'in_ride','reserved_for':None}) returns True; expected False."
    },
    {
      "id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
      "location": "policy.py reserved_for compared to user[\"name\"]",
      "scenario": "Two riders share a name; either can unlock the other's reserved bike. Case/whitespace mismatch denies the real owner.",
      "fix": "Match on stable user ID.",
      "answers": {"a": true, "b": false, "c": true, "d": false},
      "reproduction": "Users {'name':'Sam','id':1} and {'name':'Sam','id':2}; bike reserved_for 'Sam'; both return True; expected only id 1 allowed."
    },
    {
      "id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
      "location": "policy.py docstring '(stub)'; perms.py return policy.check(...)",
      "scenario": "Rule lives in a local stub instead of the policy service; a real client returning a truthy non-bool (e.g. {'allowed': False}) would grant access.",
      "fix": "Call the real client, map its response explicitly to bool, add a contract test.",
      "answers": {"a": true, "b": true, "c": false, "d": false},
      "reproduction": "Stub policy.check to return {'allowed': False}; can_unlock returns a truthy value."
    },
    {
      "id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
      "location": "no test files supplied",
      "scenario": "Deny paths and outage behaviour are unguarded; F1 or a regression ships unnoticed.",
      "fix": "Add tests for free, own reservation, other's reservation, staff, policy raises, missing name; mutation-check the except branch.",
      "answers": {"a": true, "b": true, "c": false, "d": true},
      "reproduction": "No tests exist to run; flip `return True` in the except branch and confirm a new test fails."
    },
    {
      "id": "F7", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
      "location": "perms.py DEBUG = False",
      "scenario": "Dead flag; invites a future debug bypass.",
      "fix": "Remove it.",
      "answers": {"a": false, "b": true, "c": false, "d": false},
      "reproduction": "Search supplied files for DEBUG; no reader found."
    },
    {"id": "NV1", "status": "needs_validation", "location": "callers of can_unlock", "suspicion": "role may be client-supplied, allowing self-promotion to staff", "unresolved_fact": "whether user is loaded server-side from an authenticated session"},
    {"id": "NV2", "status": "needs_validation", "location": "bike schema", "suspicion": "bikes have availability states beyond reservation", "unresolved_fact": "bike record fields"},
    {"id": "NV3", "status": "needs_validation", "location": "production policy client", "suspicion": "return type, exceptions and timeout differ from stub", "unresolved_fact": "real client contract"},
    {"id": "NV4", "status": "needs_validation", "location": "perms.py except branch", "suspicion": "fail-open may be an unapproved product decision", "unresolved_fact": "whether an owner approved fail-open behaviour"}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Staff short-circuit also bypasses reservation for riders", "evidence": "Only role == 'staff' returns early; riders always reach the reservation comparison."},
    {"id": "R2", "candidate": "Owner of a reservation is denied", "evidence": "user['name'] is in the allowed tuple, so the owner is allowed (subject to F4)."}
  ]
}
```