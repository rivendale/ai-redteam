# Redteam Review: Project API handlers (`handlers.py`, `test_handlers.py`)

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools or subagents were available, so nothing was executed. Every finding below comes from tracing the supplied code by hand.

**VERDICT: REJECT.** Any member can give themselves admin rights to change billed quotas, and any user can list another user's private projects. These two failures break both stated stakes, and the three passing tests cannot detect either one.

**CONFIDENCE: high** for the two Critical findings, since each is a one-line trace. It is limited by having no tools, so nothing was run, and by the server and storage setup not being supplied.

## Inputs ledger

| Item | Status | Matters? |
|---|---|---|
| request.md (original request) | seen | yes |
| context.md | seen | yes |
| handlers.py | seen | yes |
| test_handlers.py | seen | yes |
| Login middleware that sets `request["session"]` | not seen | partly. The request says it is verified, so I assume that is true. |
| Router or server (threading, number of workers, whether a missing body becomes `{}`) | not seen | yes, for S1 and F4 |
| Storage or persistence requirement, billing consumer of `QUOTAS` | not seen | yes, for F4 and F3 |

## Coverage

- **Checked:** `create_project`, `list_projects`, `set_quota`, all 3 tests, and the module docstring's description of how the session is trusted.
- **Not checked:** the middleware, the router, the billing system that reads quotas, and the deployment model (workers and threads).

## Seats and gate

- **Seats:** one local same-context reviewer. No subagent or cross-vendor seats were available.
- **Sensitivity gate:** no personal data, credentials or confidential data appear in the work, so the gate passes. External seats were not used because none exist in this session.

## Pass 1: Reconstruct

The work claims to implement three handlers:
- create a project owned by the session user;
- list the caller's own projects;
- let an admin set a project's quota.

For it to be correct, identity and role must come only from the verified `request["session"]`. Client-supplied `query` and `body` must never be able to choose whose data is read or what authority applies.

Load-bearing assumptions:
1. The session is the only source of truth for identity and role.
2. In-process dicts are acceptable storage for billed production data.
3. Requests are handled one at a time.
4. The 3 tests cover the authorization rules.

Track: B. There are also requirement-fit aspects ("list **my** projects", "**admin** sets quota").

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | handlers.py:25 | `role = body.get("role", request["session"]["role"])` lets the client-controlled body override the verified role. | A member sends `{"project_id": 1, "quota": 999999, "role": "admin"}`. `role == "admin"`, so the check passes and a billed quota is set. | **Fix:** `role = request["session"]["role"]`. Never read authority from `body`. **Repro:** `set_quota(req({"user_id":"u1","role":"member"}, {"project_id":1,"quota":5,"role":"admin"}))` should return 403 but returns 200, and `QUOTAS[1] == 5`. | Y/Y/Y/Y |
| F2 | Critical | CONFIRMED | B | handlers.py:19 | `request["query"].get("user_id", session user_id)` lets any caller choose whose projects are listed. This is an IDOR (insecure direct object reference). | User u2 calls `GET /projects?user_id=u1` and receives all of u1's private projects. This also drifts from the request, which asked for "list **my** projects". | **Fix:** `user_id = request["session"]["user_id"]`, and ignore query `user_id`. **Repro:** create a project as u1, then call `list_projects(req({"user_id":"u2","role":"member"}, query={"user_id":"u1"}))`. Expected `[]`; observed `[alpha]`. | Y/Y/Y/Y |
| F3 | Medium | CONFIRMED | B | test_handlers.py:17-23 | The tests assert only the honest path. `test_member_cannot_set_quota` sends no `role` in the body, so it passes on the vulnerable code. No test checks a body or query override. "3 tests pass" therefore gives no evidence about the authorization rules. | A future regression, or the current bugs F1 and F2, ships green. | **Fix:** add `test_member_cannot_escalate_via_body_role` (expect 403) and `test_cannot_list_other_users_projects` (expect `[]`). Both fail on the current code, which is the reproduction. | Y/Y/N/Y |
| F4 | Medium | PROBABLE | B | handlers.py:7-8, 13 | Billed quotas and projects live in module-level dicts. They are lost on every restart or deploy and are not shared across workers. IDs come from `len(PROJECTS)+1`. | After a deploy, all projects and billed quotas disappear. With 2 or more workers, a user's list depends on which worker answers the request. | **Fix:** use durable storage with DB-generated IDs, or confirm the dicts are explicit placeholders. **Repro:** restart the process and call `list_projects`; it returns `[]`. | Y/N/Y/Y |
| F5 | Medium | CONFIRMED | B | handlers.py:28 | `set_quota` does not check that `project_id` exists, and does not check that `quota` is a non-negative integer. A missing key raises `KeyError`, which becomes a 500. | Once F1 is fixed, an admin typo such as `"quota": "-5"` or `"quota": "lots"`, or a nonexistent `project_id`, is stored and fed to billing. | **Fix:** return 404 if `project_id not in PROJECTS`. Return 400 unless `isinstance(quota, int) and quota >= 0`, and 400 on missing keys. **Repro:** `set_quota(admin, {"project_id": 42, "quota": -5})` should return 404 or 400 but returns 200. | Y/Y/N/N |
| F6 | Low | CONFIRMED | B | handlers.py:13 | `create_project` does no input validation. A missing `name` raises `KeyError` (a 500), and `name` can be empty, non-string or arbitrarily large. | A client posts `{}` and gets a 500. A client posts a 10 MB name and it is stored in memory. | **Fix:** return 400 unless `name` is a non-empty string within a length limit. **Repro:** `create_project(req(member, {}))` raises `KeyError`. | Y/Y/N/N |

## Needs validation

- **S1, races (handlers.py:13-14).** `len(PROJECTS)+1` followed by an insert can give two concurrent creates the same ID, so one silently overwrites the other. **Settles it:** whether the server runs handlers concurrently (threads or async with awaits). This is moot if F4's fix uses DB-generated IDs.
- **S2, admin cross-tenant scope (handlers.py:23-29).** The code lets any admin set the quota of any project. **Settles it:** whether "admin" means a global operator or a per-organization admin.

## Refuted

- **C1: "create_project lets the client spoof the owner."** Refuted. `owner` comes from `session["user_id"]` (line 13), not from the body.

## What holds up

- `create_project` takes ownership from the verified session.
- The admin check compares exactly against `"admin"`, so once F1 is fixed its logic is sound.
- `setUp` isolates test state.

## Unverified claims

- **"3 tests pass."** Not run. This is plausible, because the tests never exercise the bugs. Confirm by running `python -m unittest test_handlers`.
- **The middleware puts the verified user in the session.** This is accepted from the request. Confirm by reviewing the middleware.

## Questions for the author

1. Are the in-memory dicts intended as production storage?
2. Is the handler concurrency model single-threaded?
3. Is "admin" a global role or scoped to a tenant?

## Decision-maker summary

Do not release. F1 lets any member set billed quotas, and F2 exposes every user's private project list. Both are one-line fixes, and each needs a regression test that fails before the fix. Releasing as is means billing manipulation and a privacy breach on day one.

## Owner summary

The code currently lets any ordinary user pretend to be an administrator when changing billed limits. It also lets anyone see other people's private project lists. The existing tests only check honest use, so they did not catch either problem. Both are small fixes, but the code should not go live until they are made and tested.

```json
{
  "schema_version": "2.2",
  "verdict": "REJECT",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "handlers.py", "status": "seen", "matters": true},
    {"item": "test_handlers.py", "status": "seen", "matters": true},
    {"item": "login middleware", "status": "not_seen", "matters": false},
    {"item": "server/router concurrency and worker model", "status": "not_seen", "matters": true},
    {"item": "storage requirement and billing consumer of QUOTAS", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal data, credentials or confidential material in the work."},
  "coverage": {
    "checked": [
      {"unit": "handlers.py", "kind": "file"},
      {"unit": "handlers.py:create_project", "kind": "function"},
      {"unit": "handlers.py:list_projects", "kind": "function"},
      {"unit": "handlers.py:set_quota", "kind": "function"},
      {"unit": "test_handlers.py", "kind": "file"},
      {"unit": "identity and role come only from session", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "login middleware", "reason": "not supplied"},
      {"unit": "server concurrency model", "reason": "not supplied"},
      {"unit": "billing consumer of QUOTAS", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handlers.py:25",
     "scenario": "A member sends body {\"project_id\":1,\"quota\":999999,\"role\":\"admin\"}; the body role overrides the session role, the admin check passes, and a billed quota is set.",
     "fix": "Use role = request[\"session\"][\"role\"]; never read role from the body. Add a test that a member sending role=admin in the body gets 403.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "set_quota(req({'user_id':'u1','role':'member'}, {'project_id':1,'quota':5,'role':'admin'})): expect 403, observe 200 and QUOTAS[1]==5."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handlers.py:19",
     "scenario": "User u2 calls list_projects with ?user_id=u1 and receives u1's private projects (IDOR; also drift from 'list my projects').",
     "fix": "Use user_id = request[\"session\"][\"user_id\"] and ignore query user_id. Add a test that listing with another user's id returns [].",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "As u1 create 'alpha'; list_projects(req({'user_id':'u2','role':'member'}, query={'user_id':'u1'})): expect [], observe [alpha]."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_handlers.py:17-23",
     "scenario": "The tests only exercise honest requests; test_member_cannot_set_quota sends no body role, so it passes on the vulnerable code, and F1/F2 ship with green tests.",
     "fix": "Add tests for body-role escalation (expect 403) and query user_id override (expect []); both fail on the current code.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Add the two tests and run python -m unittest test_handlers; both fail on the current handlers.py."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "handlers.py:7-8,13",
     "scenario": "Projects and billed quotas live in process memory, so they are lost on every restart or deploy and diverge across multiple workers.",
     "fix": "Use durable storage with DB-generated ids, or document the dicts as placeholders that must not ship.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Create a project, restart the process, call list_projects: observe []."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handlers.py:28",
     "scenario": "An admin sets a quota for a nonexistent project or a negative or non-integer quota; it is stored and fed to billing. A missing key raises KeyError and returns a 500.",
     "fix": "Return 404 if project_id is not in PROJECTS; return 400 unless quota is a non-negative int; return 400 on missing keys.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "set_quota(admin, {'project_id':42,'quota':-5}): expect 404 or 400, observe 200."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handlers.py:13",
     "scenario": "A body without name raises KeyError (500); an empty, non-string or huge name is accepted and stored.",
     "fix": "Return 400 unless name is a non-empty string within a length limit.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "create_project(req({'user_id':'u1','role':'member'}, {})): observe KeyError instead of 400."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "handlers.py:13-14",
     "suspicion": "Concurrent creates can compute the same len(PROJECTS)+1 id and overwrite each other.",
     "unresolved_fact": "Whether the server runs handlers concurrently (threads or async)."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "handlers.py:23-29",
     "suspicion": "Any admin can set the quota of any project, across tenants.",
     "unresolved_fact": "Whether admin is a global operator role or scoped per organization."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "create_project lets the client spoof the owner.",
     "evidence": "handlers.py:13 sets owner from session['user_id'], not from the body."}
  ]
}
```