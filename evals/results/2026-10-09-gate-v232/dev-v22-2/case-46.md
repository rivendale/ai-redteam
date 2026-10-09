# Redteam review: project API handlers

**Review conditions:** no tools in this session, so nothing was run. Every finding below comes from reading the supplied code and tracing it by hand. The work was not written in this conversation, but no fresh subagent was available, so this is a single-reviewer review. Re-run it in a fresh session with tools before release.

**VERDICT: REWORK.** Two access checks trust values the client sends. Any logged-in member can read anyone's private project list and can set billed quotas.

**CONFIDENCE: medium.** The two Critical findings come from reading single lines, so I am sure of them. Confidence is limited because nothing was executed, the middleware was not supplied, and the concurrency model and storage plan are unknown.

**INPUTS LEDGER**
- **Seen:**
  - request.md (verbatim request)
  - context.md
  - handlers.py
  - test_handlers.py
- **Not seen:**
  - **Login middleware.** It matters only a little. The request states it already verifies the session, and both Critical findings bypass the session rather than depend on it.
  - **Router and server, including the concurrency model.** This matters for finding F3.
  - **Persistence layer, if any.** This matters for S1.
  - **The test run output behind "3 tests pass".** It does not matter much. By reading, all three tests would pass on this code, and that is part of the problem.

**COVERAGE**
- **Checked:**
  - `handlers.py`: the module docstring, `create_project`, `list_projects`, `set_quota`
  - `test_handlers.py`: all 3 tests
  - The assumption "session is the trusted identity"
- **Not checked:**
  - Middleware, router and server (not supplied)
  - Actual test execution (no tools)

**SEATS AND GATE**
- **Sensitivity gate:** passed. The code holds no personal data, credentials or client material.
- **Seats:** one same-vendor reviewer, this session.
- **Cross-vendor seats:** none ran. They were not requested, and none was available.

## Pass 1: Reconstruct

The work claims to implement three handlers: create a project, list the caller's own projects, and an admin-only quota setter. The request says the verified identity is `request["session"]`.

For the work to be correct, three things must hold:
- Identity and role must come only from the session, never from `query` or `body`. The module's own docstring says those are "whatever the client sent".
- Project IDs must be unique.
- Quotas, which are billed, must be valid values for projects that exist.

Tracks: **B** (code) and **A** (fit to the original request).

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | `handlers.py` `set_quota`: `role = body.get("role", request["session"]["role"])` | The admin check reads the role from the client's request body first and uses the session role only as a fallback. | A member sends `{"project_id": 1, "quota": 999999, "role": "admin"}`. The check sees `"admin"`, so the handler returns 200 and writes a billed quota. | **Fix:** use `role = request["session"]["role"]` and ignore any role in the body. **Reproduction test:** a member session with body `{"project_id":1,"quota":5,"role":"admin"}` should get 403. On the current code it gets 200. | a✓ b✓ c✓ d✓ |
| F2 | Critical | CONFIRMED | B | `handlers.py` `list_projects`: `request["query"].get("user_id", request["session"]["user_id"])` | The list is filtered by a `user_id` taken from the client's query string. That breaks "list **my** projects" and exposes private lists. | Member u2 calls `?user_id=u1` and receives all of u1's projects, including their names. | **Fix:** filter by `request["session"]["user_id"]` only. If admins need to view other users' lists, add a separate endpoint that checks the session role. **Reproduction test:** u1 creates "alpha", then u2 calls with `query={"user_id":"u1"}`. The result should be `[]`. On the current code it is `["alpha"]`. | a✓ b✓ c✓ d✓ |
| F3 | Medium | PROBABLE | B | `handlers.py` `create_project`: `"id": len(PROJECTS) + 1` | The new ID is computed from the current count of projects, so it is not guaranteed to be unique. | Two concurrent creates on a threaded server can both read the same length, get the same ID, and the second silently overwrites the first, losing a project. Any delete added later causes the same collision even without concurrency. | **Fix:** use a monotonic counter under a lock, or a UUID or database sequence. **Reproduction:** run two threads that call `create_project` with a barrier placed between the `len` call and the assignment. Expect 2 projects; observe 1. | a✓ b✗ c✓ d✗ |
| F4 | Medium | CONFIRMED | B | `handlers.py` `set_quota`: `QUOTAS[body["project_id"]] = body["quota"]` | Nothing checks that the project exists or that the quota is a sensible number. | Even a real admin can store a quota of `-5`, `"lots"`, or a quota for project 4242, which does not exist. Billing then reads garbage. | **Fix:** return 404 if `project_id` is not in `PROJECTS`, and require a non-negative integer within limits (otherwise 400). **Reproduction test:** an admin sets `{"project_id":4242,"quota":-5}`. Expect 4xx; observe 200. | a✓ b✓ c✓ d✗ |
| F5 | Medium | CONFIRMED | B | `test_handlers.py`, all three tests | The tests never send hostile input, so they pass on code that has both Critical bugs. | The "3 tests pass" claim gave false assurance before a production release. | **Fix:** add the reproduction tests from F1, F2 and F4, and confirm each fails on the current code before applying the fix. | a✓ b✓ c✗ d✓ |
| F6 | Low | CONFIRMED | B | `create_project` (`body["name"]`) and `set_quota` (`body["project_id"]`, `body["quota"]`) | Missing fields raise `KeyError`. The name is never validated: it can be empty, huge, or not a string. | A body of `{}` produces an unhandled exception (likely a 500) instead of a 400. A very large name gets stored as is. | **Fix:** validate the body and return 400 on bad input. **Reproduction test:** `create_project` with body `{}` should return 400. It currently raises `KeyError`. | a✓ b✓ c✗ d✗ |

### Severity answers (Pass 3 questions a–d)

- **F1:** a, b, c and d all hold. It is a security breach that changes billed values, so it is Critical.
- **F2:** a, b, c and d all hold. It is a privacy breach of project lists that are explicitly private, so it is Critical.
- **F3:** b fails (the evidence is probable, not confirmed) and d fails (it depends on the concurrency model). So it is Medium.
- **F4:** a, b and c hold. It rated Medium only because d fails: it needs an admin to make a mistake, so it is not likely under normal use. That also means it can never trigger the Critical rule's "a, b and c" combination in practice.
- **F5:** c fails. The tests cause no harm directly; they are the reason F1 and F2 shipped. So it is Medium.
- **F6:** c and d fail, so it is Low.

## Confirm or refute (Critical findings only)

**F1, defended:** "The router may strip `role` from the body." Nothing supplied shows any such stripping. The module's own docstring says the body is "whatever the client sent", and the handler deliberately reads `role` from the body. **The finding holds.**

**F2, defended:** "Maybe a `user_id` query parameter was intended so admins can see other users' lists." The handler never checks the session role, so any member can use it. The request also says "list **my** projects". **The finding holds, and it is also drift from the request.**

## NEEDS VALIDATION

- **S1. In-memory storage:** `PROJECTS` and `QUOTAS` are module-level dicts. In production they would be lost on every restart and diverge across worker processes. This includes billed quota data.
  - **Settles it:** whether these dicts are placeholders for a real data store, or the intended production storage.
- **S2. Middleware fallback:** whether the middleware always sets `session` before these handlers run.
  - **Settles it:** whether any route reaches these handlers without passing through the middleware.

## REFUTED

- **C1. "`create_project` lets a client set the project owner."** Refuted: the owner comes from `session["user_id"]`, and nothing from the body is used except `name`.
- **C2. "Member test proves the admin check works."** Refuted as a defense of the code. The test's body contains no `role`, so the check falls back to the session role and passes. The test never exercises the bypass in F1.

## WHAT HOLDS UP

- `create_project` takes the owner from the verified session.
- The admin check *does* fall back to the session role when the body has no `role`, so the normal paths behave correctly.
- The three existing tests correctly cover the normal, honest-client paths.

## UNVERIFIED CLAIMS

- **"3 tests pass."** I did not run them. By reading the code, they would pass. Confirm by running `python -m unittest test_handlers` in a scratch copy.
- **"Middleware puts the verified user in session."** Confirm by reading the middleware and the route table.

## QUESTIONS FOR THE AUTHOR

1. Is the `?user_id=` parameter meant to exist at all? If so, for whom?
2. Are these dicts the production storage?
3. Is the server threaded or async, and how many worker processes run?

## DECISION-MAKER SUMMARY

Do not release this code. Any logged-in member can read other users' private project lists (F2) and set billed quotas (F1), and the passing tests do not cover either path. Fix both by reading identity and role only from the session, add the failing tests from the findings table, then re-review.

## OWNER SUMMARY

The new project features let any ordinary user see other people's private projects and change billing limits just by adding a value to their request. The existing tests did not catch this because they only try honest requests. The fixes are small, but they are needed before release.

## Findings JSON

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "handlers.py", "status": "seen", "matters": true},
    {"item": "test_handlers.py", "status": "seen", "matters": true},
    {"item": "login middleware", "status": "not_seen", "matters": false},
    {"item": "router/server concurrency model", "status": "not_seen", "matters": true},
    {"item": "persistence layer", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "handlers.py", "kind": "file"},
      {"unit": "handlers.py:create_project", "kind": "function"},
      {"unit": "handlers.py:list_projects", "kind": "function"},
      {"unit": "handlers.py:set_quota", "kind": "function"},
      {"unit": "test_handlers.py", "kind": "file"},
      {"unit": "session is the only trusted identity", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "login middleware", "reason": "not supplied"},
      {"unit": "router/server", "reason": "not supplied"},
      {"unit": "test execution", "reason": "no tools in session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handlers.py:set_quota role = body.get(\"role\", request[\"session\"][\"role\"])",
     "scenario": "A member sends body {\"project_id\":1,\"quota\":999999,\"role\":\"admin\"}; the check passes and a billed quota is written (200).",
     "fix": "Read role only from request[\"session\"][\"role\"]; ignore any role in the body.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "set_quota(req({\"user_id\":\"u1\",\"role\":\"member\"},{\"project_id\":1,\"quota\":5,\"role\":\"admin\"})): expect 403, observe 200."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handlers.py:list_projects user_id = request[\"query\"].get(\"user_id\", ...)",
     "scenario": "Member u2 calls list_projects with ?user_id=u1 and receives u1's private projects.",
     "fix": "Filter by request[\"session\"][\"user_id\"] only; put any admin cross-user listing behind a session role check.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "u1 creates 'alpha'; list_projects(req({\"user_id\":\"u2\",\"role\":\"member\"}, query={\"user_id\":\"u1\"})): expect [], observe ['alpha']."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "handlers.py:create_project \"id\": len(PROJECTS) + 1",
     "scenario": "Two concurrent creates on a threaded server read the same length and get the same id; the second overwrites the first.",
     "fix": "Use a locked monotonic counter, a UUID or a database sequence.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "Two threads with a barrier between len() and the assignment: expect 2 projects, observe 1."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handlers.py:set_quota QUOTAS[body[\"project_id\"]] = body[\"quota\"]",
     "scenario": "An admin sets quota -5, a string, or a quota on nonexistent project 4242; billing reads an invalid value.",
     "fix": "Return 404 for an unknown project; require a non-negative integer within limits, else 400.",
     "answers": {"a": true, "b": true, "c": true, "d": false},
     "reproduction": "Admin set_quota {\"project_id\":4242,\"quota\":-5}: expect 4xx, observe 200."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_handlers.py (all three tests)",
     "scenario": "The tests contain no hostile inputs, so they pass with both Critical bypasses present and gave false release assurance.",
     "fix": "Add the F1, F2 and F4 reproduction tests and confirm each fails on the current code first.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Add the F1 test; it fails on the current handlers.py."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handlers.py:create_project body[\"name\"]; set_quota body[\"project_id\"], body[\"quota\"]",
     "scenario": "A body of {} raises KeyError (an unhandled 500); empty or huge names are stored unvalidated.",
     "fix": "Validate the body and return 400 on missing or invalid fields.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "create_project(req(session, {})): expect 400, observe KeyError."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "handlers.py PROJECTS, QUOTAS module dicts",
     "suspicion": "In-memory storage loses billed quotas and projects on restart and diverges across workers.",
     "unresolved_fact": "Whether these dicts are placeholders for a real store or the intended production storage."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "handlers.py (all handlers) request[\"session\"]",
     "suspicion": "A route might reach the handlers without the login middleware.",
     "unresolved_fact": "Whether every route to these handlers passes through the login middleware."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "create_project lets a client set the project owner.",
     "evidence": "The owner comes from session[\"user_id\"]; only name is read from the body."},
    {"id": "C2", "candidate": "test_member_cannot_set_quota shows the admin check is sound.",
     "evidence": "Its body has no role key, so the check falls back to the session role; the F1 bypass is never exercised."}
  ]
}
```