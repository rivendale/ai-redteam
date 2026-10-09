VERDICT: **REWORK**. `can_unlock` fails open: any exception, including an outage or a malformed user record, unlocks any bike, reserved ones included. That is a confirmed Critical in a theft-sensitive authorization path.

CONFIDENCE: **medium**. It is limited by four things:
- There were no tools, so nothing was executed and every trace is by reading.
- The real policy service, the user and bike data model, and any tests were not supplied.
- No fresh subagent was available, so this is a single-reviewer pass. I did not author the work.

INPUTS LEDGER:
- **Seen:** `request.md` (original request), `context.md`, `perms.py`, `policy.py`.
- **Not seen: the real policy service client or API.** `policy.py` is labelled "(stub)". This matters: whether production calls a network service, its timeouts and its exception types all depend on it.
- **Not seen: the user and bike schema.** This matters for whether `name` is a unique identity, where `role` comes from, and whether "free" means more than "not reserved".
- **Not seen: tests.** None were supplied. This matters because no behavior is covered.
- **Not seen: callers of `can_unlock`.** This matters less, but they determine whether `user` can be attacker-shaped.

COVERAGE:
- **Scope:** the whole work (two files).
- **Checked:**
  - `perms.py` (file), `perms.py:can_unlock` (function)
  - `policy.py` (file), `policy.py:check` (function)
  - `request.md` and `context.md` (documents)
  - the assumptions "free means reserved_for is None", "name is identity" and "role is trustworthy"
- **Not checked:** the real policy service (not_supplied), the data schema (not_supplied), the tests (not_supplied), the callers (not_supplied).

SEATS AND GATE: one local reviewer (this instance), not cross-vendor. No fresh subagent was available. The sensitivity gate passed: no personal data, credentials or confidential records are in the work. No external seats were requested.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (traced from exact lines; not executed) | B | `perms.py:11-12` | `except Exception: return True` grants unlock on any error. | (1) The policy service is down, slow or erroring: every rider can unlock every bike, including bikes reserved for someone else. (2) With no outage, a user dict missing `"name"` reaches `user["name"]` at `policy.py:7`, which raises `KeyError`, and the result is unlock granted. (3) `user=None` or `bike=None` raises `AttributeError`, and the result is unlock granted. A rider who can induce errors, or simply waits for an outage, takes reserved bikes. | **Fix:** fail closed. Catch only the service's transport/timeout errors, log them, and `return False`. If availability matters, use an explicit, audited degraded mode that still refuses reserved bikes. Let programming errors raise. **Reproduction** (scratch copy, not run here): (1) Monkeypatch `policy.check` to raise `ConnectionError`. Call `can_unlock({"role":"rider","name":"a"}, {"reserved_for":"b"})`. Expected `False`, but the code returns `True` by trace. (2) Call `can_unlock({"role":"rider"}, {"reserved_for":"b"})`. Expected `False` or an error, but the code returns `True` by trace. | a Y / b Y / c Y / d Y |
| F2 | Medium | CONFIRMED | B | `policy.py:1`, `perms.py:2` | The request says "use the policy service", but the work ships a local stub with hardcoded rules. It has no client, no timeout and no error contract. The comment at `perms.py:12` assumes a remote service that the code does not contain. | If this stub is deployed, authorization rules are duplicated in the app and drift from the real policy service. There is also no defined exception set to catch, which is what invited the blanket `except` in F1. | **Fix:** call the real policy client, with an explicit timeout and the named exceptions it raises. Delete the stub or move it to test fixtures. **Reproduction:** read `policy.py:1`, which says `"""Policy service client (stub)."""`. It makes no network call, so no service is used. | a Y / b Y / c N / d N |
| F3 | Low | CONFIRMED | B | (missing) | No tests are supplied for any branch: staff, free, reserved-for-self, reserved-for-other, or service failure. | A regression such as F1 ships unnoticed. | **Fix:** add tests for each branch, plus a fail-closed test on service error. The F1 reproduction tests should fail on the current code. **Reproduction:** the supplied work contains only `perms.py` and `policy.py`. | a Y / b Y / c N / d N |
| F4 | Low | CONFIRMED | B | `perms.py:4` | `DEBUG = False` is never used. | It is harmless now, but it is an invitation to add a debug bypass later. | **Fix:** remove it. **Reproduction:** there is no reference to `DEBUG` in either file. | a N / b Y / c N / d N |

F1 security boundary:
- **Principal:** any rider.
- **Input:** timing during a policy-service outage, or a user/bike record that triggers an exception.
- **Control that fails:** the reservation check, which fails open.
- **Boundary crossed:** rider becomes effectively staff, with the right to unlock any bike.
- **Resource affected:** bikes reserved for other riders, and the fleet generally.

F1 sibling search: I searched both files for other exception handlers and default-allow returns. The only handler is `perms.py:11`. `policy.py:7` (`user["name"]`) and `policy.py:5,7` (`.get` on possibly-`None` objects) are triggers into that same handler, not separate fail-open paths.

## NEEDS VALIDATION

- **"Free" may mean more than unreserved** (`policy.py:7`). A bike currently ridden by someone else, or out of service, may have `reserved_for = None`, and would then be unlockable. To settle: does the bike record carry an in-use or maintenance state, and does "free" in the request include it?
- **Identity by `name`** (`policy.py:7`). If display names are not unique, a rider named "Alex" can unlock another Alex's reservation. To settle: is `name` a unique, immutable account key, or should this be `user["id"]`?
- **Trust in `role`** (`policy.py:5`). If the `user` dict is built from client-supplied data, `role="staff"` can be spoofed. To settle: where `user` is constructed, and whether `role` comes from a server-side session.
- **Timeouts.** A hung policy call may block an unlock request indefinitely. To settle: the real client's timeout behavior (not supplied).

## REFUTED

- **Candidate: staff check bypassable via case.** `role == "staff"` is an exact match, so a value like `"Staff"` is simply denied, which fails safe. The rule itself is sound; how far `role` can be trusted is the separate question listed under NEEDS VALIDATION.

## WHAT HOLDS UP

On the happy path, `policy.check` matches the request:
- staff get unconditional access (`policy.py:5-6`);
- riders get access when `reserved_for` is `None` or their own name (`policy.py:7`);
- riders get no access to a bike reserved for another rider.

The `in (None, user["name"])` test is correct for those cases.

## UNVERIFIED CLAIMS

- The comment "keep riders moving when the policy service is down" (`perms.py:12`) implies that outages are expected and that availability was chosen over safety. Confirm that a product or security owner actually approved this trade-off. It conflicts with the stated stakes in `context.md`.
- The `policy.py` docstring says it is the "policy service client". It is not one. Confirm what production actually imports.

## QUESTIONS FOR THE AUTHOR

1. What must happen when the policy service is unreachable: deny, or a limited mode that still blocks reserved bikes?
2. What is the real policy client, and what exceptions and timeouts does it have?
3. Is `name` a unique account key, and is `role` server-side?
4. Does "free" exclude bikes in use or under maintenance?

## DECISION-MAKER SUMMARY

Do not ship. Any error in the permission check, including an ordinary service outage, currently unlocks every bike, reserved ones included. Fix F1 to fail closed and wire up the real policy service (F2) before production. Proceeding risks fleet-wide unauthorized unlocks during the next outage.

## OWNER SUMMARY

The rule for who may unlock a bike is correct when everything works. But whenever the checking service has a problem, the code lets anyone unlock any bike, including bikes held for someone who booked them. That needs to be reversed so problems block unlocking, and the code needs to use the real checking service instead of a placeholder.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "perms.py", "status": "seen", "matters": true},
    {"item": "policy.py", "status": "seen", "matters": true},
    {"item": "real policy service client", "status": "not_seen", "matters": true},
    {"item": "user/bike data schema", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true},
    {"item": "callers of can_unlock", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "perms.py", "kind": "file"},
      {"unit": "perms.py:can_unlock", "kind": "function"},
      {"unit": "policy.py", "kind": "file"},
      {"unit": "policy.py:check", "kind": "function"},
      {"unit": "free means reserved_for is None", "kind": "assumption"},
      {"unit": "name is a unique identity", "kind": "assumption"},
      {"unit": "role is server-trusted", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "real policy service client", "reason": "not_supplied"},
      {"unit": "user/bike data schema", "reason": "not_supplied"},
      {"unit": "tests", "reason": "not_supplied"},
      {"unit": "callers of can_unlock", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "perms.py:11-12",
     "scenario": "When policy.check raises for any reason (service outage, timeout, or a user dict missing 'name' causing KeyError at policy.py:7, or None user/bike), can_unlock returns True, so any rider can unlock a bike reserved for another rider.",
     "fix": "Fail closed: catch only the policy client's transport/timeout exceptions, log, and return False; let programming errors raise. Any degraded mode must still refuse reserved bikes.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "In a scratch copy: monkeypatch policy.check to raise ConnectionError; call can_unlock({'role':'rider','name':'a'}, {'reserved_for':'b'}); expect False, code returns True by trace. Also can_unlock({'role':'rider'}, {'reserved_for':'b'}) returns True via KeyError. Traced, not executed (no tools).",
     "security": true,
     "boundary": {"principal": "any rider", "input": "a request made during a policy-service outage, or a user/bike record that makes policy.check raise",
                  "control": "reservation check fails open via except Exception: return True",
                  "crossed": "rider to staff-equivalent unlock rights", "resource": "bikes reserved for other riders and the fleet"},
     "siblings_searched": {"searched": "all exception handlers and default-allow returns in perms.py and policy.py",
                           "found": "perms.py:11 is the only handler; policy.py:5 and :7 are triggers into it, not separate fail-open paths"}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "policy.py:1",
     "scenario": "The request says to use the policy service, but the work ships a local stub with hardcoded rules and no timeout or error contract; deployed as-is, rules drift from the real service and the undefined exception set invites the blanket catch in F1.",
     "fix": "Call the real policy client with an explicit timeout and named exceptions; move the stub to test fixtures.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Read policy.py:1: docstring says 'Policy service client (stub)'; check() makes no service call."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "perms.py (no accompanying tests)",
     "scenario": "No tests cover staff, free, reserved-for-self, reserved-for-other or service-failure branches, so regressions like F1 ship unnoticed.",
     "fix": "Add a test per branch plus a fail-closed test on service error.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "The supplied work contains only perms.py and policy.py; no test file exists."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "perms.py:4",
     "scenario": "DEBUG = False is unused dead code that invites a future debug bypass in an authorization module.",
     "fix": "Remove DEBUG.",
     "answers": {"a": false, "b": true, "c": false, "d": false},
     "reproduction": "Search both files for DEBUG: only the assignment at perms.py:4."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "policy.py:7",
     "suspicion": "A bike in use by another rider or out of service may have reserved_for None and be unlockable.",
     "unresolved_fact": "Whether the bike record has an in-use/maintenance state and whether 'free' in the request includes it."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "policy.py:7",
     "suspicion": "Identity by display name lets a rider unlock a same-named rider's reservation.",
     "unresolved_fact": "Whether user['name'] is a unique immutable account key."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "policy.py:5",
     "suspicion": "role may be client-supplied and spoofable as 'staff'.",
     "unresolved_fact": "Where the user dict is built and whether role comes from a server-side session."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "perms.py:10",
     "suspicion": "A hung policy call may block unlock requests with no timeout.",
     "unresolved_fact": "The real policy client's timeout behavior."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Staff check bypassable via role case variants.",
     "evidence": "policy.py:5 uses exact equality, so variants are denied (fail safe); trust in role is tracked separately as S3."}
  ]
}
```