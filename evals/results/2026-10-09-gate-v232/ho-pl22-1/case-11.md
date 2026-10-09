# Adversarial Diagnostic Review: `can_unlock(user, bike)`

## Pass 1: Reconstruct

The work claims to implement the unlock rule: staff may unlock any bike, and riders may unlock a bike that is free or reserved for them, with the decision delegated to the policy service. `perms.can_unlock` calls `policy.check`. If that call raises any exception, it returns `True` so riders keep moving. `policy.py` is a local stub that reads `role`, `reserved_for` and `name` from plain dicts.

For this to be correct, all of the following must hold:
1. Granting unlock when the policy check fails is acceptable.
2. `policy.check` is, or will be replaced by, the real policy service.
3. A rider's `name` uniquely identifies them and matches what `reserved_for` stores.
4. `reserved_for is None` means the bike is free.
5. The `role` field on `user` is trustworthy.
6. Inputs are always well-formed dicts.

The context makes assumptions 1, 3 and 4 the most important, because a wrong "yes" means a bike can be stolen or a reservation taken.

## Pass 2: Attack (Track B, plus some Track A on the fail-open decision)

**Fail-open on any exception.** In `perms.py`, the `except Exception: return True` does not only catch "service down". It catches every error from the check, including bugs and bad input. I traced these cases by hand; nothing was executed:
- `user = {"role": "rider"}` with no `name`, and the bike reserved for someone else: `bike.get("reserved_for")` returns that rider's name, then `user["name"]` raises `KeyError`, and the function returns **True**. A rider with an incomplete record unlocks someone else's reserved bike.
- `user = None`: `None.get` raises `AttributeError`, and the function returns **True**. An unauthenticated caller passing no user can unlock any bike.
- `bike = None` or a malformed bike record: the function returns **True**.
- Policy service outage or timeout, once a real client exists: every bike unlocks for anyone, including reserved ones. An attacker who can degrade the service, for example by flooding it or cutting the network, turns off access control.

The comment documents this as a deliberate trade-off, but the stakes stated in the context make it the wrong default. The trade-off is also not stated anywhere else, and nothing is logged or alerted when it happens.

**The policy service is not used.** `policy.py` says `"""Policy service client (stub)."""`. It reimplements the rule locally and never calls a service. The request said "Use the policy service". The work is presented as complete but ships a stub. If this file goes to production as is, the rule lives in two places, or only here, and nothing about a real service, such as timeouts, auth or error types, has been exercised.

**Identity by display name.** `bike.get("reserved_for") in (None, user["name"])` compares against `name`. If names are not unique, a second rider with the same name can unlock the first rider's reserved bike. If `reserved_for` stores a user ID while `user["name"]` is a display name, the rider who booked the bike is locked out of it. In either case the comparison should use a stable unique ID.

**"Free" is reduced to "not reserved".** A bike that is currently rented by another rider, out of service, under maintenance or reported stolen has `reserved_for is None` and is treated as free. The request's word "free" almost certainly means available, not merely unreserved.

**Reservation lifecycle.** No expiry is checked. A stale `reserved_for` blocks other riders indefinitely, and nothing shows that expiry is handled upstream.

**Trust in `role`.** Staff status comes from `user.get("role")`. If the `user` dict is built from anything the client controls, such as a request body or an unsigned token claim, a rider can send `role: "staff"`. I cannot see where `user` comes from.

**Minor edges.**
- `name == ""` matches `reserved_for == ""`, a degenerate match.
- `role` matching is case-sensitive, so `"Staff"` is treated as a rider. This fails closed, which is fine.
- `check` returns whatever the comparison yields, which is a bool here but not guaranteed once a real service is behind it.

**Tests.** None are provided. Nothing covers the exception path, so the fail-open behaviour is invisible to CI.

**Dead code.** `DEBUG = False` is unused.

**What holds:** the staff branch, the "reserved for me" branch and the "reserved for someone else → deny" branch are logically correct for well-formed input.

## Pass 3: Self-check

- The name-uniqueness and "free means unreserved" findings depend on a data model I cannot see, so they are marked PROBABLE.
- The `role` trust finding is UNVERIFIED.
- The fail-open finding is CONFIRMED by tracing, even though I ran nothing.
- The most serious issue I might still be missing would sit in the caller: whether `can_unlock` is the only gate before the physical unlock command, and whether its result is checked server-side or by a client app that could skip it.

---

**VERDICT: REWORK.** Any error, including a missing field, a null user or a service outage, grants unlock. With the rule only stubbed and identity keyed on names, this is not safe to put in production.

**CONFIDENCE IN VERDICT: high.** The fail-open path alone justifies it and is traceable from the code. Confidence in the data-model findings is limited because the user and bike schemas, the real policy service API and the call site are not visible.

### Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `perms.py` `except Exception: return True` | Fails open on every exception, not only outages | User missing `name`, `user=None`, `bike=None`, or the policy service is down: unlock is granted, including on bikes reserved for others | Fail closed (`return False`). Catch only specific service errors. Log and alert on every failure. Let callers show "try again". Add tests for each exception path asserting `False` |
| 2 | High | CONFIRMED | `policy.py` docstring "(stub)" | The request said to use the policy service; this is a local reimplementation | Production runs on an untested stub, or the rule drifts from the real service; timeout and auth behaviour are never exercised | Call the real service client with an explicit timeout. Contract-test against it. Keep no duplicate rule logic |
| 3 | High | PROBABLE | `policy.py` `user["name"]` vs `reserved_for` | Identity is matched on a display name | Two riders share a name and the wrong one unlocks the reserved bike, or `reserved_for` holds an ID and the booking rider is denied | Compare stable unique user IDs. Test same-name riders |
| 4 | High | PROBABLE | `policy.py` `in (None, ...)` | "Free" is treated as "unreserved"; in-use, out-of-service and stolen states are ignored | A rider unlocks a bike that is mid-rental for someone else or flagged stolen | Check the bike's status (available) as well as reservation. Test each non-available status returns `False` |
| 5 | Medium | UNVERIFIED | `policy.py` `user.get("role")` | Staff role is trusted from the `user` object | If `user` is built from client input, a rider sets `role:"staff"` and unlocks any bike | Confirm that role comes from a server-side, authenticated source. Add a test that a forged role is rejected at the boundary |
| 6 | Medium | PROBABLE | `policy.py` | No reservation expiry | A stale reservation blocks a bike indefinitely, or an expired booking is still honoured | Check reservation validity time against the server clock. Test an expired reservation |
| 7 | Medium | CONFIRMED | whole change | No tests; the exception path has no coverage | A regression to fail-open or a logic flip passes CI | Add unit tests for staff, own reservation, other's reservation, free bike, malformed input and service error. Mutation-check that flipping the `except` return turns a test red |
| 8 | Medium | CONFIRMED | `perms.py` `except` block | Failures are silent: no log, metric or audit of unlock decisions | Mass fail-open during an outage goes unnoticed; there is no trail when investigating a theft | Log every decision and every policy error with user ID and bike ID. Alert on the error rate |
| 9 | Low | CONFIRMED | `policy.py` | Empty-string `name` matches empty-string `reserved_for` | A corrupted record with `""` on both sides allows unlock | Treat empty identifiers as invalid and deny |
| 10 | Low | CONFIRMED | `perms.py` `DEBUG = False` | Unused flag | A future reader wires it into a bypass | Remove it |

### What holds up
- The staff check, the "reserved for me" check and the "reserved for someone else → deny" check are correct for well-formed input.
- A missing or unknown role defaults to rider treatment, which fails closed.

### Unverified claims
- **"Keep riders moving when the policy service is down"** assumes outages are the only exception source. Settle it by listing the real service's error types and checking whether the business accepts fail-open. The stated stakes suggest it does not.
- **The stub matches the policy service.** Settle it with the real service's API and a contract test.
- **`name` is unique and is what `reserved_for` stores.** Settle it with the user and bike schemas.
- **`role` is set server-side.** Settle it by tracing where `user` is constructed.
- **`can_unlock` is the only gate before the physical unlock.** Settle it by inspecting the unlock endpoint and the bike command path.

### Questions for the author
1. Was failing open on errors an explicit product decision, and does it still stand once the bike-theft stakes are considered?
2. Is `policy.py` meant to ship, or will it be replaced by a real client? If it will be replaced, where is that client?
3. What does `reserved_for` store (ID or name), and is `name` unique?
4. Does the bike record carry an availability status (in use, maintenance, stolen) that "free" should check?

### Decision-maker summary
Do not ship. As written, any error, including a policy outage, lets anyone unlock any bike, and the real policy service is never called. Fix the error path to deny, wire in the real service, and key reservations on user IDs. Until then, theft and reservation hijacking are realistic outcomes.

### Owner summary
The new bike-unlock check lets anyone unlock any bike whenever something goes wrong, such as the permissions system being down or a rider's account details being incomplete. It also does not yet use the real permissions system and may confuse two riders who share a name. It should be fixed to refuse unlocking when in doubt before it goes live.

```json
{
  "verdict": "REWORK",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "perms.py: except Exception: return True", "scenario": "User missing 'name', user=None, bike=None, or policy service outage causes an exception; can_unlock returns True and any bike, including ones reserved for others, unlocks", "fix": "Fail closed (return False), catch only specific service errors, log and alert; add tests asserting False on each exception path"},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "policy.py: docstring 'Policy service client (stub)'", "scenario": "Request required using the policy service; production would run an untested local stub whose rule can drift from the real service", "fix": "Call the real policy service client with an explicit timeout; add contract tests; remove duplicated rule logic"},
    {"severity": "High", "evidence_level": "PROBABLE", "location": "policy.py: bike.get('reserved_for') in (None, user['name'])", "scenario": "Two riders share a name and one unlocks the other's reserved bike, or reserved_for stores an ID and the booking rider is denied", "fix": "Compare stable unique user IDs; test same-name riders"},
    {"severity": "High", "evidence_level": "PROBABLE", "location": "policy.py: reserved_for in (None, ...)", "scenario": "Bike that is in use by another rider, out of service, or flagged stolen has reserved_for None and is treated as free", "fix": "Require bike status == available in addition to the reservation check; test each non-available status"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "location": "policy.py: user.get('role') == 'staff'", "scenario": "If the user object is built from client input, a rider sets role 'staff' and unlocks any bike", "fix": "Confirm role comes from a server-side authenticated source; test that a forged role is rejected"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "policy.py: reservation check", "scenario": "No expiry check: a stale reservation blocks the bike indefinitely or an expired booking is honoured", "fix": "Validate reservation time window server-side; test an expired reservation"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "whole change: no tests", "scenario": "A regression to fail-open or an inverted condition passes CI unnoticed", "fix": "Unit tests for staff, own reservation, other's reservation, free bike, malformed input, service error; mutation-check the except branch"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "perms.py: except block", "scenario": "Silent failures: mass fail-open during an outage goes unnoticed and no audit trail exists for theft investigation", "fix": "Log every decision and every policy error with user and bike IDs; alert on the error rate"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "policy.py: user['name'] comparison", "scenario": "Empty-string name matches empty-string reserved_for on corrupted records", "fix": "Treat empty identifiers as invalid and deny"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "perms.py: DEBUG = False", "scenario": "Unused flag invites a future debug bypass", "fix": "Remove it"}
  ]
}
```