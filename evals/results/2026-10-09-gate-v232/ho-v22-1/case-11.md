VERDICT: **REWORK**. `can_unlock` fails open: any error, including a policy outage or a malformed user, lets anyone unlock any bike, reserved ones included.

CONFIDENCE: medium. The main finding comes straight from reading the two files and tracing them by hand. I had no tools, so nothing was executed. The real policy service, the user and bike data model, and any tests were not supplied.

INPUTS LEDGER:
- **Seen:** request.md (verbatim), context.md, perms.py, policy.py.
- **Not seen:**
  - The real policy service or client (policy.py says it is a "stub"). This matters: it decides whether the logic reviewed here is what runs in production.
  - The user and bike schemas: where `role` and `name` come from, and what `reserved_for` holds. This matters for S1, S2 and S4.
  - Tests: none were supplied. This matters because no test guards the fail-open path.
  - The callers of `can_unlock`. These matter for blast radius.

COVERAGE:
- **Checked:** perms.py (whole file, `can_unlock`), policy.py (whole file, `check`), the request's three rules (rider/free, rider/reserved-for-self, staff/any), and the hostile inputs: service exception, `user=None`, user without `name`, `bike=None`, bike without `reserved_for`.
- **Not checked:**
  - The real policy service (not supplied).
  - Callers and authentication upstream (not supplied).
  - Runtime behavior (no tools).

SEATS AND GATE:
- The sensitivity gate passed: the work is code with no personal data, credentials or client material.
- Only one reviewer ran: this model, without tools. The work was not written in this conversation, so there is no shared-author anchoring. No cross-vendor seats ran because none were requested.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (traced) | B | perms.py:9-12 | `except Exception: return True` fails open on every error, not just "service down". It also swallows errors without logging. | (1) The policy service times out or raises during an outage, and every rider can unlock every bike, including bikes reserved for others. (2) `user=None`: `None.get` raises AttributeError, which returns True. (3) A rider dict with no `"name"`: building `(None, user["name"])` raises KeyError, which returns True for any bike. (4) `bike=None`: AttributeError, which returns True. An unauthenticated or malformed request is therefore an unlock. | **Fix:** fail closed. Catch only the client's specific transport/timeout error, log it, and return False. Let programming errors propagate or deny. If the business wants a degraded mode, make it an explicit, logged, owner-approved rule (for example, free bikes only, never reserved ones). **Repro:** patch `policy.check` to raise `ConnectionError`, then call `can_unlock({"role":"rider","name":"bob"}, {"reserved_for":"alice"})`. Expected False; it returns True. Also `can_unlock(None, {"reserved_for":"alice"})`: expected False; it returns True. | a✔ b✔ c✔ d✔ |
| F2 | Medium | CONFIRMED (traced) | B | policy.py:7 | A missing `reserved_for` key reads as None, so the bike counts as "free". | A bike record loaded partially, or from an older schema without the field, can be unlocked by any rider even if it is actually reserved. | **Fix:** require the key, for example `bike["reserved_for"]` or an explicit state field, and deny on a malformed record. **Repro:** `check({"role":"rider","name":"bob"}, {})`. Expected deny or error; it returns True. | a✔ b✔ c✘ d✘ |

## NEEDS VALIDATION
- **S1 (policy.py:7):** reservation ownership is matched on `user["name"]`. If names are not unique, a rider with the same name as the booker can take the reserved bike. *Unresolved fact:* is `reserved_for` a unique rider ID, or a display name?
- **S2 (policy.py:5):** staff status comes from `user.get("role")`. If the user dict is built from client-supplied claims, any rider can claim staff. *Unresolved fact:* is `role` taken from a server-verified identity?
- **S3 (policy.py:1):** the client is labelled a "(stub)" yet holds all the decision logic. The request says "Use the policy service". *Unresolved fact:* does a real service client replace this file in production, or does the stub ship? If it ships, the service is never consulted, which is requirement drift.
- **S4 (policy.py:7):** "free" is read as "not reserved". A bike that is mid-ride, in maintenance, or reported stolen with `reserved_for=None` would pass. *Unresolved fact:* does the bike model have other states that the policy must exclude?

## REFUTED
- **"Staff path missing":** refuted. policy.py:5-6 returns True for `role == "staff"`.
- **"On the normal path a rider can unlock a bike reserved for someone else":** refuted. With `reserved_for="alice"` and `name="bob"`, the membership test at policy.py:7 is False.

## WHAT HOLDS UP
On the happy path, with the service up and well-formed user and bike dicts, `policy.check` implements the three rules in the request correctly. `can_unlock` delegates to the policy client as asked. `DEBUG` is unused dead code; it causes no failure.

## UNVERIFIED CLAIMS
- The comment "keep riders moving when the policy service is down" implies the only expected exception is an outage. The code catches everything, so the claim does not match the behavior.
- The stub is implied to stand in for a real service. To confirm, inspect the production client and its error types.

## QUESTIONS FOR THE AUTHOR
1. Is fail-open during an outage an approved business decision, and if so, should it ever cover reserved bikes?
2. Is `reserved_for` a unique rider ID?
3. Does policy.py ship as is, or is it replaced by a real client?

## DECISION-MAKER SUMMARY
Do not deploy. Any outage or malformed request turns `can_unlock` into "yes, unlock", which defeats reservations and enables theft (F1). Make it fail closed, add tests for the error paths, and answer S1–S3 before the next review.

## OWNER SUMMARY
The unlock check says "yes" whenever anything goes wrong, so during an outage or with a bad request anyone could take any bike, including one booked by someone else. On the normal path it follows the rules correctly. It needs to say "no" when it cannot decide, and a few questions about how riders and bookings are identified still need answers.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "perms.py", "status": "seen", "matters": true},
    {"item": "policy.py", "status": "seen", "matters": true},
    {"item": "real policy service client", "status": "not_seen", "matters": true},
    {"item": "user and bike schemas", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true},
    {"item": "callers of can_unlock", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local-no-tools", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "perms.py", "kind": "file"},
      {"unit": "perms.py:can_unlock", "kind": "function"},
      {"unit": "policy.py", "kind": "file"},
      {"unit": "policy.py:check", "kind": "function"},
      {"unit": "request: rider free / reserved-for-self / staff any", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "real policy service", "reason": "not supplied"},
      {"unit": "callers and upstream authentication", "reason": "not supplied"},
      {"unit": "runtime behavior", "reason": "no tools in session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "perms.py:9-12",
     "scenario": "When the policy service raises (outage, timeout) or the input is malformed (user=None, user without name, bike=None), the bare except returns True, so any rider or unauthenticated caller unlocks any bike, including reserved ones.",
     "fix": "Fail closed: catch only the client's transport/timeout error, log it, return False; deny on malformed input. Any degraded mode must be explicit, logged, owner-approved and exclude reserved bikes.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Patch policy.check to raise ConnectionError; can_unlock({'role':'rider','name':'bob'}, {'reserved_for':'alice'}) expected False, observed True. can_unlock(None, {'reserved_for':'alice'}) expected False, observed True."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "policy.py:7",
     "scenario": "A bike record missing the reserved_for key is treated as free, so any rider can unlock a bike whose reservation field was not loaded.",
     "fix": "Require an explicit reservation/state field and deny on malformed records.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "check({'role':'rider','name':'bob'}, {}) expected deny or error, observed True."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "policy.py:7",
     "suspicion": "Reservation ownership matched on display name; same-name riders could take each other's bikes.",
     "unresolved_fact": "Whether reserved_for and user['name'] are unique rider IDs."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "policy.py:5",
     "suspicion": "Staff role read from the user dict could be client-controlled, allowing escalation.",
     "unresolved_fact": "Whether role comes from a server-verified identity."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "policy.py:1",
     "suspicion": "Stub client may ship in place of the policy service the request requires.",
     "unresolved_fact": "Whether a real policy service client replaces policy.py in production."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "policy.py:7",
     "suspicion": "'Free' is read as 'not reserved'; in-use, maintenance or stolen bikes may pass.",
     "unresolved_fact": "Whether the bike model has states beyond reserved_for that the policy must exclude."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Staff path is missing.",
     "evidence": "policy.py:5-6 returns True when role == 'staff'."},
    {"id": "R2", "candidate": "On the normal path a rider can unlock a bike reserved for another rider.",
     "evidence": "policy.py:7: 'alice' in (None, 'bob') is False."}
  ]
}
```