# Adversarial Diagnostic Review: `can_unlock`

## Pass 1: Reconstruct

The work claims to implement `can_unlock(user, bike)`. Staff may unlock any bike, and a rider may unlock a bike that is free or reserved for them. Policy decisions are delegated to `policy.check`. If the policy call raises any exception, the function returns `True`, so riders can still unlock when the service is down.

For this to be correct, these must hold:

1. **No exception path matters.** Every exception from `policy.check` must be a genuine service outage, and failing open must be an accepted business decision.
2. **`policy.py` is the policy service.** It must be a real client, not a local stand-in for it.
3. **"Free" means no reservation.** "Not reserved" must equal "free", so a bike in use by someone else counts as not free some other way.
4. **Names identify riders.** `user["name"]` must be a unique, stable identity that matches `reserved_for`.
5. **Every non-staff user is a rider.** Any user who is not staff must be allowed rider privileges.
6. **`role` is trustworthy.** `user["role"]` must come from a trusted source, not from client input.

## Pass 2: Attack (Track B)

**Correctness, traced by reading:**

- **Main path:** staff gets `True`. A rider on an unreserved bike gets `True`. A rider on a bike reserved for them gets `True`. A rider on a bike reserved for someone else gets `False`. Correct for well-formed input.
- **Hostile input, missing name:** `user = {"role": "rider"}` with `bike = {"reserved_for": "bob"}`. `user["name"]` raises `KeyError`, the `except` catches it, and the result is `True`. Bob's reserved bike unlocks.
- **Hostile input, null user or bike:** `user=None` or `bike=None` raises `AttributeError` on `.get`, and the result is `True`.
- **Hostile input, wrong type:** a `bike` passed as an object rather than a dict raises `AttributeError`, and the result is `True`.
- **Duplicate names:** two riders named "Alex" can unlock each other's reservations.
- **Bike in use:** a bike currently ridden by another rider has `reserved_for = None`, so a third rider gets `True`. This is PROBABLE; it depends on the data model.

**Requirement fit:** "Use the policy service" is not met in substance. `policy.py` is a self-described stub that holds the whole decision logic locally. Nothing calls a service, so there is no network call that could be "down". The only exceptions this `except` will ever catch today are bugs and malformed input.

**Failure handling:** the bare `except Exception: return True` fails open on an authorization decision. It swallows every error, has no logging, and has no metric. Outages and attacks are invisible.

**Security:**

- **Fail-open is attacker-triggerable.** Anyone who can cause an exception gets an unlock: a malformed payload, a missing field, or, against a real service, a timeout or a forced error.
- **Role trust is unknown.** It is unclear whether `role` is trusted (UNVERIFIED).

**Tests:** none supplied. Nothing guards the reserved-for-someone-else case or the exception path.

**Blast radius:** low as written. The unused `DEBUG = False` hints at leftover or planned bypass code.

## Pass 3: Self-check

- **Finding 1 is real.** The `KeyError` and `AttributeError` traces need no assumptions beyond the code shown.
- **Downgraded findings:** "free means not in use" and "non-riders get rider rights" are kept at PROBABLE, because the data model is not shown.
- **Most likely thing still missed:** what the real policy service returns on error. It may return a non-boolean, such as an error dict or `None`. A truthy error object returned rather than raised would also unlock. This can only be checked against the real client.

---

**VERDICT: REWORK.** The function fails open on an authorization check, so any exception unlocks any bike, including reserved ones. The "policy service" is a local stub, so the request is not actually met.

**CONFIDENCE IN VERDICT: high.** The fail-open path is visible in the code. What limits confidence is that no real policy client, data model, or user-construction code was provided.

## Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `perms.py` `except Exception: return True` | Authorization fails open on any exception, including bugs and malformed input, not just outages | `user={"role":"rider"}` (no `name`) and `bike={"reserved_for":"bob"}` → `KeyError` → `True`, so Bob's reserved bike unlocks. `user=None` or `bike=None` → `AttributeError` → `True`. A real service timeout lets anyone take any reserved bike | Fail closed (`return False`). Catch only the client's specific outage exception, log it, and alert on it. If an outage fallback is wanted, make it explicit and narrow (e.g. allow only unreserved bikes) and get a product sign-off. Tests: missing `name`, `None` inputs, and a simulated service error must all return `False` |
| 2 | High | CONFIRMED | `policy.py` docstring "(stub)" | Request said "use the policy service". The work ships a local stub containing the decision logic, so no service is used | Production uses the stub's hardcoded rules. Policy changes made in the real service never apply. The fail-open "service down" rationale doesn't match any real call | Wire to the real policy service client. Confirm its API, error types and return values, and remove the stub from production paths |
| 3 | High | PROBABLE | `policy.py` `bike.get("reserved_for") in (None, ...)` | "Free" is treated as "not reserved". Nothing checks whether the bike is in use, out of service, or already unlocked | Rider A is mid-ride on a bike with `reserved_for=None`. Rider B calls `can_unlock` → `True` | Define "free" with the data owner. Check bike status (available, not in use, not out of service). Test: an in-use bike returns `False` for another rider |
| 4 | Medium | PROBABLE | `policy.py` `user["name"]` vs `reserved_for` | Identity is compared by display name, not a unique ID | Two riders named "Alex": either can unlock the other's reservation | Compare stable user IDs. Test: same name with a different ID returns `False` |
| 5 | Medium | PROBABLE | `policy.py` `if user.get("role") == "staff" ... return ...` | Every non-staff user gets rider rights, including missing, unknown, suspended or banned roles | A user with `role=None` or `"suspended"` unlocks a free bike | Allow-list `role == "rider"` (and an active account). Deny everything else |
| 6 | Medium | CONFIRMED | (no test file) | No tests at all | Regressions in the reservation and exception paths go unnoticed | Add tests: staff/any, rider/free, rider/own, rider/other's (`False`), malformed input (`False`), service error (`False`). Mutation-check each test |
| 7 | Low | CONFIRMED | `perms.py` `DEBUG = False` | Unused flag. It invites a future debug bypass | Someone later adds `if DEBUG: return True`, and it gets enabled in production | Remove it |
| 8 | Low | UNVERIFIED | `policy.py` `user.get("role")` | Unknown whether `role` comes from a trusted server-side source | If `user` is built from the request body, anyone sends `"role":"staff"` | Show where `user` is constructed. `role` must come from the authenticated session or database |

## What holds up

- The happy-path logic is correct for well-formed dicts. Staff gets any bike, a rider gets an unreserved bike or their own reservation, and a rider is denied someone else's reservation.
- `in (None, name)` returns a real `bool`.
- An empty-string `reserved_for` is not treated as free, so that case fails closed.

## Unverified claims

- **"Keep riders moving when the policy service is down".** This implies a service exists and that its outages are the only exceptions. To confirm, show the real client and the exceptions it raises.
- **"Use the policy service" is satisfied.** To confirm, show the production import path and client.
- **The rule "staff may unlock any" is enforced by a trusted `role`.** To confirm, show how `user` is built.

## Questions for the author

1. Is there a real policy service client? What does it raise or return on timeout or error?
2. Did the business explicitly approve failing open, and if so, for which bikes?
3. What does "free" mean in the bike data model? Does it exclude in-use and out-of-service bikes?
4. Is `name` unique, or is there a user ID? Where does `user["role"]` come from?

## Decision-maker summary

Do not ship. The function grants an unlock whenever anything goes wrong, including a malformed request, so reserved bikes can be taken by anyone. It also does not actually use the policy service. Make it deny by default and connect it to the real service with tests for the error paths. If it ships as is, any error or outage becomes free access to every bike.

## Owner summary

The new unlock check lets anyone unlock any bike, including bikes held for a booked rider, whenever something goes wrong behind the scenes. It also doesn't yet talk to the real permissions system it was supposed to use. It needs to be changed to refuse unlocks when in doubt, connected properly, and tested before it goes live.

```json
{
  "verdict": "REWORK",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "perms.py: except Exception: return True",
      "scenario": "Any exception unlocks: user without 'name' plus bike reserved_for 'bob' -> KeyError -> True; user=None or bike=None -> AttributeError -> True; a real service timeout lets anyone take reserved bikes.",
      "fix": "Fail closed (return False); catch only the specific outage exception, log and alert; any outage fallback must be explicit, narrow, and product-approved. Test that malformed input and service errors return False."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "policy.py: docstring 'Policy service client (stub)'",
      "scenario": "Request required using the policy service; a local stub holds the logic, so real policy changes never apply and the outage rationale matches no real call.",
      "fix": "Wire to the real policy service client, confirm its error and return contract, and keep the stub out of production."
    },
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "policy.py: bike.get('reserved_for') in (None, user['name'])",
      "scenario": "A bike in use by rider A has reserved_for=None, so rider B is allowed to unlock it mid-ride; out-of-service bikes are likewise allowed.",
      "fix": "Check bike availability status as part of 'free'; add a test that an in-use bike returns False for another rider."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "policy.py: user['name'] compared to reserved_for",
      "scenario": "Two riders named 'Alex' can unlock each other's reservations.",
      "fix": "Compare unique user IDs; test same name with a different ID returns False."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "policy.py: non-staff branch",
      "scenario": "Users with a missing, unknown, suspended or banned role get rider rights and unlock free bikes.",
      "fix": "Allow-list role == 'rider' with an active account; deny all other roles."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "no tests provided",
      "scenario": "Reservation and exception-path regressions go undetected.",
      "fix": "Add tests for staff, rider/free, rider/own, rider/other (False), malformed input (False) and service error (False); mutation-check each test."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "perms.py: DEBUG = False",
      "scenario": "Unused flag invites a later debug bypass that could be enabled in production.",
      "fix": "Remove it."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "policy.py: user.get('role')",
      "scenario": "If the user dict is built from request input, a client can send role 'staff' and unlock any bike.",
      "fix": "Show where user is constructed; role must come from the authenticated session or database."
    }
  ]
}
```