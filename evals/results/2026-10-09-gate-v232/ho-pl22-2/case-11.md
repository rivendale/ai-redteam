# Adversarial Diagnostic Review: `can_unlock(user, bike)`

## Pass 1: Reconstruct

The work claims to implement `can_unlock` so that riders may unlock free bikes or bikes reserved for them, and staff may unlock any bike, by delegating to "the policy service". `perms.py` wraps `policy.check` and returns `True` on any exception, so it fails open. `policy.py` is a local stub that grants staff by `role`, and grants riders when `reserved_for` is absent, `None`, or equal to `user["name"]`.

For this to be correct, all of the following must be true:
- `policy.check` is the real policy service.
- Failing open is acceptable.
- A rider's `name` is a unique identity.
- "Not reserved" is the same as "free".
- The `user` dict, including `role`, comes from a trusted source.

The fail-open assumption is unstated in the request and directly contradicts the stated stakes.

## Pass 2: Attack (Track B)

- **Happy path:** the logic matches the spec for well-formed inputs.
- **Hostile inputs:**
  - `user=None`: `AttributeError`, so the function returns `True`.
  - `user={}` (no `name`, not staff): `KeyError`, so it returns `True`.
  - `bike=None`: `AttributeError`, so it returns `True`.
  - Policy service timeout: it returns `True`.
- Every error path grants access.

## Pass 3: Self-check

- Findings 1 and 2 share one line of code but have different triggers: an outage versus attacker-controlled input. I kept them separate because fixing the outage policy alone, for example with a cache, would not close the malformed-input path.
- Finding 6 is downgraded to UNVERIFIED because I cannot see where `user` originates.
- **Most serious possible miss:** the real policy service client, if one exists, may have different semantics, timeouts or exception types from this stub. All of `policy.py` may be irrelevant to production.

---

**VERDICT: REJECT.** The function grants unlock on every error, so any malformed request or policy outage lets anyone unlock any bike, including reserved ones. That is the exact harm the context names.

**CONFIDENCE IN VERDICT: high.** Findings 1 and 2 are confirmed by reading the code. Confidence is limited only by not knowing whether a real policy service client exists.

## Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `perms.py`, `except Exception: return True  # keep riders moving when the policy service is down` | Fails open. This is a security decision not in the request and against the stated stakes. | The policy service times out or is down, and for the whole outage every user can unlock every bike, including reserved bikes. A thief or the wrong rider takes a held bike. | Fail closed (`return False`), and log or alert on the exception. If availability is a business requirement, make it an explicit, owner-approved degraded mode, for example allowing unreserved bikes only from a cached reservation list. Test: mock `policy.check` to raise and assert `False`. |
| 2 | Critical | CONFIRMED | Same `except Exception` in `perms.py`, plus `user["name"]` in `policy.py` | The broad catch turns caller bugs and malformed input into a grant, not just service outages. | `can_unlock({}, bike)`, `can_unlock(None, bike)` or `can_unlock(user, None)` all raise inside `check` and return `True`. An unauthenticated or anonymous user object with no `name` unlocks any bike. | Validate inputs first and reject on missing identity. Catch only the service's transport and timeout exceptions, and let programming errors propagate. Tests for `None`, `{}`, and a bike without the expected fields, each asserting `False` or an exception. |
| 3 | High | CONFIRMED (stub) / UNVERIFIED (prod) | `policy.py` docstring `"Policy service client (stub)."` | The request says "use the policy service". This is a local stub presented as the integration, with no network call, auth, timeout or error contract. | If deployed as is, permissions depend on whatever dicts callers pass, not on the authoritative service. If a real client replaces it later, its exceptions and timeouts are untested against Finding 1. | Wire up the real policy service client with explicit timeouts and typed exceptions. If a client exists, show it. Add integration tests against it. |
| 4 | High | PROBABLE | `policy.py`, `bike.get("reserved_for") in (None, user["name"])` | "Free" is reduced to "not reserved". A bike in use by another rider, under maintenance, or reported stolen has `reserved_for=None` and is treated as free. A missing or misspelled field also reads as free. | Rider B unlocks a bike Rider A is currently riding and has parked mid-trip, or unlocks a bike flagged for repair. A data feed that omits `reserved_for` exposes reserved bikes. | Check an explicit status, for example `status == "available"`, or a reservation match. Treat a missing field as deny. Tests for in-use, maintenance and missing-field bikes. |
| 5 | High | PROBABLE | `policy.py`, comparison to `user["name"]` | Identity is matched by display name, which is not unique and may be user-editable. | Two riders are both named "Alex Kim", and either can unlock the other's reservation. A rider who renames themselves to match another's name can claim that reservation. | Compare stable user IDs (`reserved_for_id == user["id"]`). Test with two users sharing a name. |
| 6 | Medium | UNVERIFIED | `policy.py`, `user.get("role") == "staff"` | Staff privilege rests entirely on a field in the `user` dict. Its provenance is not shown. | If `user` is built from request or client data, any rider sends `role: "staff"` and unlocks any bike. | Confirm the role comes from server-side auth claims or the database, not from the request. Add a test or code reference showing where `user` is built. |
| 7 | Medium | CONFIRMED | Whole submission | There are no tests, so nothing shows the logic was exercised, and no test has ever failed. | Regressions such as the fail-open path go unnoticed. | Add unit tests for the rider-free, rider-own-reservation, rider-other's-reservation, staff, service-raises and malformed-input cases. Mutate `return True` to `return False` in the except branch and confirm a test goes red. |
| 8 | Medium | CONFIRMED | `perms.py` except branch | The exception is swallowed with no logging or metric. | An outage that silently opens every bike leaves no trace for ops or for the theft investigation afterwards. | Log the exception with user and bike IDs (no PII beyond IDs), and emit a metric or alert. |
| 9 | Low | CONFIRMED | `perms.py`, `DEBUG = False` | Dead, unused flag that invites a future debug bypass. | Someone later adds `if DEBUG: return True`, and it ships enabled. | Remove it. |

## What Holds Up

- With well-formed inputs and a working service, the logic matches the request text:
  - Staff get access to any bike.
  - A rider gets their own reservation.
  - A rider is denied someone else's reservation.
- The role check is case-sensitive, which fails closed. That is acceptable.

## Unverified Claims

- **"Use the policy service" is satisfied.** Confirm by showing the production client and its endpoint, timeout and exception types.
- **The comment says failing open "keeps riders moving".** Confirm whether any business owner approved fail-open and accepted the theft risk.
- **The `user` and `bike` dict shapes and provenance.** Confirm with the auth middleware code and the bike data schema, including the status and reservation fields.

## Questions for the Author

1. Is there a real policy service client, and what does it raise on timeout or unavailability?
2. Who decided to fail open, and was it approved against the theft and reserved-bike stakes?
3. Where is the `user` dict built, and is `role` server-derived?
4. Does a bike have a status (in use, maintenance) separate from `reserved_for`, and is there a stable user ID to use instead of `name`?

## Decision-Maker Summary

Do not ship. The code grants unlock on any error, so a policy-service outage or a malformed request lets anyone take any bike, including reserved ones. Before reconsidering, it needs to fail closed, connect to the real policy service, match riders by ID rather than name, check bike status, and add tests that prove each of these.

## Owner Summary

This code is meant to decide who can unlock a bike, but whenever something goes wrong, such as the permission system being down or bad data arriving, it lets everyone unlock everything. That means reserved bikes could be taken by the wrong person and bikes could be stolen during an outage. It should be fixed to refuse access when in doubt, and tested, before it goes live.

```json
{
  "verdict": "REJECT",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "perms.py: except Exception: return True",
      "scenario": "Policy service down or timing out; every user can unlock every bike, including reserved ones, for the duration of the outage.",
      "fix": "Fail closed (return False) and log/alert; any degraded-availability mode must be explicit and owner-approved. Test: mock policy.check to raise, assert False."
    },
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "perms.py: except Exception (with policy.py user[\"name\"])",
      "scenario": "can_unlock({}, bike), can_unlock(None, bike) or can_unlock(user, None) raise inside check and return True; anonymous or malformed users unlock any bike.",
      "fix": "Validate inputs and deny on missing identity; catch only service transport/timeout exceptions. Tests for None, {}, malformed bike asserting False."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "policy.py docstring: \"Policy service client (stub).\"",
      "scenario": "Request requires the policy service; a local stub ships instead, so permissions depend on caller-supplied dicts and the real client's error behavior is untested.",
      "fix": "Integrate the real policy service client with explicit timeouts and typed exceptions; add integration tests."
    },
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "policy.py: bike.get(\"reserved_for\") in (None, user[\"name\"])",
      "scenario": "Bike in use by another rider, in maintenance, or missing the reserved_for field is treated as free and unlocked.",
      "fix": "Check explicit availability status; treat a missing field as deny. Tests for in-use, maintenance, missing-field bikes."
    },
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "policy.py: comparison against user[\"name\"]",
      "scenario": "Two riders with the same name, or a rider who renames themselves, can unlock another's reservation.",
      "fix": "Compare stable user IDs; test two users sharing a name."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "policy.py: user.get(\"role\") == \"staff\"",
      "scenario": "If the user dict is built from request data, a rider sets role=staff and unlocks any bike.",
      "fix": "Confirm role comes from server-side auth; show where user is constructed; add a test."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "Whole submission (no tests)",
      "scenario": "Fail-open and authorization regressions go undetected; no test has ever failed.",
      "fix": "Add unit tests for every rule and error path; mutate the except branch and confirm a test goes red."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "perms.py except branch",
      "scenario": "Exceptions swallowed silently; an outage that opens all bikes leaves no trace for ops or theft investigation.",
      "fix": "Log with user/bike IDs and emit a metric/alert."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "perms.py: DEBUG = False",
      "scenario": "Unused flag invites a future debug bypass that could ship enabled.",
      "fix": "Remove it."
    }
  ]
}
```