# Adversarial Diagnostic Review: `can_unlock(user, bike)`

## Pass 1: Reconstruct

The work claims to implement `can_unlock` as requested: riders may unlock free bikes or bikes reserved for them, staff may unlock any bike, and the decision is delegated to "the policy service." `perms.py` calls `policy.check` and returns `True` if that call raises anything. `policy.py`, which describes itself as a "(stub)", implements the rule locally.

For this to be correct, all of the following must hold:
- `policy.check` is the real policy service, or is replaced by it in production.
- Exceptions only happen when the service is down. Failing open must also be an acceptable business choice.
- `user["name"]` is a unique, authenticated identifier that matches `bike["reserved_for"]`.
- `user["role"]` comes from a trusted server-side source.
- "Free" means "not reserved". The work assumes nothing else, such as "in use" or "out of service", can make a bike unavailable.

## Pass 2: Attack (Track B, with security focus)

**Fail-open handler (`perms.py`, `except Exception: return True`).** Every exception becomes an unlock grant, not just outages. Tracing hostile inputs through `policy.check`:

| Input | What happens | Result |
|---|---|---|
| `user=None` | `None.get` raises `AttributeError` | **True** (anyone, unauthenticated, unlocks any bike) |
| `user={"role":"rider"}` with no `"name"` | Building the tuple `(None, user["name"])` raises `KeyError` | **True**, including bikes reserved for someone else |
| `bike=None` (unknown bike ID) | `AttributeError` | **True** |
| Policy service timeout or `ConnectionError` | Caught | **True** for every rider on every reserved bike |
| Bug inside `check` (`TypeError` etc.) | Caught, no log | **True**, and the bug stays silent |

The context says reserved bikes are held for the riders who booked them, and a stolen bike costs Pedalo and the next rider. Failing open is the opposite of what those stakes require. Nothing is logged, so nobody would see an outage-driven run of unlocks.

**"Use the policy service."** `policy.py` is a local function labelled "stub". It makes no network call and has no client, timeout, or auth. The "service is down" comment in `perms.py` guards against an outage of a service the code never calls. If this ships as is, any rules that live only in the real service are never consulted. That would include suspended accounts, unpaid balances, and bikes in maintenance.

**Meaning of "free."** `check` treats every bike with `reserved_for` set to `None` or missing as free. A bike that is currently rented by another rider, or out of service, is probably not reserved, so it passes. Whether this is a real hole depends on the bike data model, which I was not given.

**Identity by name.** Reservations are matched on `user["name"]`. If that is a display name, not a unique ID, two riders called "Alex" can unlock each other's reservations.

## Pass 3: Self-check

**Defending finding 1.** "Keeping riders moving" is a real product goal. That defence covers at most an outage. It does not cover `KeyError` or `AttributeError` from malformed or missing identities, and those are reachable without any outage. Even for outages, the context weighs theft and lost reservations as the cost, and the work records no business sign-off for availability over integrity. The finding survives at Critical.

**Siblings searched.** I looked for other `except` blocks, default-allow returns, and bypass flags in both files. `perms.py` has one handler, the one in finding 1. `policy.py` has none. `DEBUG` is defined but never read, so it is not a bypass today. The `KeyError` and `AttributeError` paths are the same root cause and are folded into finding 1.

**Boundary for finding 1.**
- Principal: any rider, or an unauthenticated caller.
- Input: an unlock request made during a policy failure, or with a missing or malformed user or bike.
- Failing control: the exception handler in `can_unlock`.
- Boundary crossed: rider-to-other-rider's-reservation and anonymous-to-any-bike authorization.
- Resource: the physical bike lock.

**What I might still be missing.** The most serious remaining risk would be in the callers, which I was not given. If `user` is built from client-supplied JSON, a rider can send `"role": "staff"` and unlock anything without any exception.

---

**VERDICT: REWORK.** The unlock check fails open on any exception, so a policy outage, a missing user, or a malformed request lets anyone unlock any bike, including reserved ones.

**CONFIDENCE IN VERDICT: high.** The fail-open path is visible directly in the code. The limits: I had no tools, so I traced but did not run anything, and I was not given the real policy client, the data model, the callers, or any tests.

**COVERAGE**
- request.md: checked
- context.md: checked
- perms.py: checked
- policy.py: checked
- Real policy service client: not supplied
- User and bike data model: not supplied
- Callers and auth layer: not supplied
- Tests: not supplied

**FINDINGS**

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `perms.py` `can_unlock`, `except Exception: return True` | Fails open on every exception, without logging. | (i) Policy service outage: rider `eve` unlocks a bike with `reserved_for="alice"`, result True. (ii) `can_unlock({"role":"rider"}, {"reserved_for":"alice"})` raises `KeyError` on `user["name"]`, result True. (iii) `can_unlock(None, any_bike)` raises `AttributeError`, result True. | Fail closed: catch only the client's transport and timeout errors, log them, and return False. Let programming errors propagate, or deny them too. Validate `user` and `bike` before calling. If availability during outages is a business requirement, get explicit sign-off and limit it to unreserved bikes. Repro: `policy.check = lambda u,b: (_ for _ in ()).throw(ConnectionError()); assert perms.can_unlock({"role":"rider","name":"eve"},{"reserved_for":"alice"}) is False` fails today. So do `assert perms.can_unlock(None, {}) is False` and `assert perms.can_unlock({"role":"rider"}, {"reserved_for":"alice"}) is False`. | Y/Y/Y/Y |
| 2 | High | PROBABLE | `policy.py` docstring "Policy service client (stub)", whole file | The request says to use the policy service. The work calls a local stub with no service call, no timeout, and no auth, and presents it as complete. | If deployed as is, rules that live only in the real service are skipped: suspended riders, out-of-service bikes, payment holds. The outage handling in finding 1 is untested against real failure modes. | Replace with the real client, or document that a real implementation is injected at deploy and add an integration test against it. Repro: grep the deploy artifact for which `policy` module is imported. Check that `check` makes a network call with a timeout. | Y/N/Y/Y |
| 3 | Medium | PROBABLE | `policy.py` `return bike.get("reserved_for") in (None, user["name"])` | "Free" is read as "not reserved". Availability (in use, maintenance) is never checked. | A bike rented by rider A with no reservation is unlocked by rider B mid-ride or at a stop. | Check availability status explicitly, in the service or the bike record. Test: bike `{"status":"in_use","reserved_for":None}`, other rider, expect False. | Y/N/Y/N |
| 4 | Medium | PROBABLE | same line, `user["name"]` | Identity is matched on a name field. If names are not unique IDs, reservations can be taken by namesakes. | Two riders named "Alex": one unlocks the other's reserved bike. | Match on a stable unique user ID. Test: two users with the same name and different IDs, expect False for the non-holder. | Y/N/Y/N |

For findings 1 and 2: security is true for #1 and false for #2. Siblings searched: all `except` blocks, default-allow returns, and bypass flags in both files. The only one found is #1, with its `KeyError` and `AttributeError` variants.

**NEEDS VALIDATION**
- Is `user["role"]` taken from a trusted server-side record or token? If it is client-supplied, any rider can claim staff.
- Is `user["name"]` a unique, immutable ID? This settles #4.
- Do bike records carry an availability status? This settles #3.
- Does a real policy client exist, and what exceptions does it raise?
- Do any tests exist for `can_unlock`? None were supplied. I could not run them or mutation-test them, so test coverage is UNVERIFIED. The mutation that settles it: change the handler to `return False` and see whether any test turns red.

**REFUTED**
- *`DEBUG` is a bypass:* it is never referenced, so it has no effect. At most it is dead code.
- *Role spoofing through case, e.g. `"Staff"`:* the exact match `== "staff"` denies variants, so this fails closed.
- *Missing `role` key grants staff:* `.get` returns None, so the user falls through to the rider path.

**WHAT HOLDS UP**
- On the happy path, `check` matches the request text: staff get True, riders get True only for unreserved bikes or their own reservation.
- The staff comparison is exact and safe against missing keys.

**UNVERIFIED CLAIMS**
- The comment says it "keeps riders moving when the policy service is down", but no service is called. To confirm, read the real client.
- The docstring implies the requested behaviour is complete. To confirm, run the tests suggested above.

**QUESTIONS FOR THE AUTHOR**
1. Has the business explicitly chosen fail-open during outages? If so, for reserved bikes too?
2. Is the stub replaced in production, and by what?
3. What uniquely identifies a rider, and where does `role` come from?

**DECISION-MAKER SUMMARY**
Do not ship. Make `can_unlock` fail closed, wire it to the real policy service, and add tests that deny outage, missing-user, and other-rider-reservation cases. If shipped as is, any outage or malformed request lets anyone unlock any bike, including reserved ones, with no log of it happening.

**OWNER SUMMARY**
The check that decides who may unlock a bike says "yes" whenever anything goes wrong, including when the permission system is unreachable or the rider's identity is missing. That means bikes held for one rider, or any bike at all, could be taken by someone else. The fix is small: say "no" when in doubt, connect to the real permission system, and add tests before release.

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
    {"item": "real policy service client", "status": "not_seen", "matters": true},
    {"item": "user/bike data model", "status": "not_seen", "matters": true},
    {"item": "callers / auth layer", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "perms.py:can_unlock", "kind": "function"},
      {"unit": "policy.py:check", "kind": "function"}
    ],
    "not_checked": [
      {"unit": "real policy service client", "reason": "not_supplied"},
      {"unit": "user/bike data model", "reason": "not_supplied"},
      {"unit": "callers / auth layer", "reason": "not_supplied"},
      {"unit": "tests (cannot run; none supplied)", "reason": "no_tools"}
    ]
  },
  "findings": [
    {
      "id": "F1",
      "status": "confirmed",
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "track": "B",
      "location": "perms.py can_unlock: except Exception: return True",
      "scenario": "Any exception grants unlock: policy outage lets rider eve unlock bike reserved_for alice; user without 'name' raises KeyError -> True; user=None or bike=None raises AttributeError -> True. No logging.",
      "fix": "Fail closed: catch only client transport/timeout errors, log, return False; validate inputs; any outage allowance needs explicit sign-off and must exclude reserved bikes.",
      "reproduction": "policy.check = lambda u,b: (_ for _ in ()).throw(ConnectionError()); assert perms.can_unlock({'role':'rider','name':'eve'},{'reserved_for':'alice'}) is False  # fails today; also assert perms.can_unlock(None, {}) is False and perms.can_unlock({'role':'rider'},{'reserved_for':'alice'}) is False",
      "answers": {"a": true, "b": true, "c": true, "d": true},
      "security": true,
      "siblings_searched": {"searched": "all except blocks, default-allow returns and bypass flags in perms.py and policy.py", "found": "only this handler; KeyError/AttributeError variants are the same root cause; DEBUG unused"},
      "boundary": {"principal": "any rider or unauthenticated caller", "input": "unlock request during policy failure or with missing/malformed user or bike", "control": "exception handler in can_unlock", "crossed": "rider-to-other-rider reservation and anonymous-to-any-bike authorization", "resource": "physical bike lock"}
    },
    {
      "id": "F2",
      "status": "confirmed",
      "severity": "High",
      "evidence_level": "PROBABLE",
      "track": "B",
      "location": "policy.py (docstring 'Policy service client (stub)')",
      "scenario": "Request says use the policy service; work calls a local stub with no service call. If shipped, service-only rules (suspensions, maintenance, payment holds) are never consulted and outage handling is untested.",
      "fix": "Use the real policy client with timeout and auth, or document injection at deploy and add an integration test.",
      "reproduction": "Inspect deploy artifact for which policy module is imported; confirm check() makes a network call with a timeout.",
      "answers": {"a": true, "b": false, "c": true, "d": true},
      "security": false,
      "siblings_searched": {"searched": "other service/network calls in both files", "found": "none"}
    },
    {
      "id": "F3",
      "status": "confirmed",
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "track": "B",
      "location": "policy.py: return bike.get('reserved_for') in (None, user['name'])",
      "scenario": "Bike in use by rider A with no reservation is treated as free; rider B unlocks it.",
      "fix": "Check availability status explicitly.",
      "reproduction": "check({'role':'rider','name':'b'}, {'status':'in_use','reserved_for':None}) expected False, returns True.",
      "answers": {"a": true, "b": false, "c": true, "d": false}
    },
    {
      "id": "F4",
      "status": "confirmed",
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "track": "B",
      "location": "policy.py: user['name'] comparison",
      "scenario": "Two riders sharing a display name can unlock each other's reservations.",
      "fix": "Match reservations on a stable unique user ID.",
      "reproduction": "check({'role':'rider','name':'Alex','id':2}, {'reserved_for':'Alex'}) for a reservation held by id 1 returns True.",
      "answers": {"a": true, "b": false, "c": true, "d": false}
    },
    {"id": "NV1", "status": "needs_validation", "location": "policy.py user.get('role')", "suspicion": "role may be client-supplied, allowing self-elevation to staff", "unresolved_fact": "source of the user dict and role field"},
    {"id": "NV2", "status": "needs_validation", "location": "tests", "suspicion": "no tests guard fail-closed behaviour", "unresolved_fact": "whether tests exist; whether any goes red when the handler returns False"},
    {"id": "NV3", "status": "needs_validation", "location": "real policy client", "suspicion": "exception types and timeouts unknown", "unresolved_fact": "client implementation and its failure modes"}
  ],
  "refuted": [
    {"id": "R1", "candidate": "DEBUG flag is an auth bypass", "evidence": "DEBUG is defined but never referenced"},
    {"id": "R2", "candidate": "Role case variants (e.g. 'Staff') grant staff", "evidence": "exact match == 'staff' denies variants"},
    {"id": "R3", "candidate": "Missing role key grants staff", "evidence": "user.get('role') returns None, falls to rider path"}
  ]
}
```