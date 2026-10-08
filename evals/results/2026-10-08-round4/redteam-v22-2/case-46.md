# Redteam review: project API handlers

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent and no tools were available in this session. Every finding comes from reading the supplied code line by line. Nothing was executed.

**VERDICT: REWORK.** Both access checks trust values the client sends. Any member can set a billed quota, and any user can read another user's private project list.

**CONFIDENCE: high** for F1 and F2, which are direct single-line traces. **Medium** overall, because I could not run the tests or mutation checks and could not see the server's concurrency model.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, handlers.py, test_handlers.py.
- **Not seen:**
  - The login middleware. Its contract is described in the docstring at handlers.py:3 and taken as given. This matters little, because the defects exist even if the middleware is perfect.
  - The server and runtime model (threads or processes, persistence). This matters for F4.
  - The test run output. The claim "3 tests pass" is UNVERIFIED.

**COVERAGE**
- **Checked:**
  - handlers.py: `create_project`, `list_projects`, `set_quota`, and the module state.
  - test_handlers.py: all 3 tests and the `req` helper.
  - Requirement fit against request.md.
- **Not checked:** middleware, routing, persistence, deployment.

**SEATS AND GATE:** Only the local same-context reviewer ran. The work holds no personal data, credentials or client material, so no seats were refused. No cross-vendor seats were requested.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | handlers.py:25 | `role = body.get("role", request["session"]["role"])`: the role comes from the client body first, and the verified session is only a fallback. | A member POSTs `{"project_id": 1, "quota": 1000000, "role": "admin"}`. The check at line 26 passes, and line 28 writes a billed quota. This is privilege escalation on a billing control. | Use `role = request["session"]["role"]` and never read `role` from the body. **Repro:** `h.set_quota(req({"user_id":"u1","role":"member"}, {"project_id":1,"quota":5,"role":"admin"}))`. Expected 403, observed 200 with `QUOTAS[1] == 5`. | y/y/y/y |
| F2 | Critical | CONFIRMED | B | handlers.py:19 | `user_id = request["query"].get("user_id", request["session"]["user_id"])`: the client's `?user_id=` overrides the verified identity. The request said "list **my** projects". | User u2 calls `GET /projects?user_id=u1` and receives all of u1's projects. Project lists are private per context.md, so this is a data breach. It also drifts from the request. | Use `user_id = request["session"]["user_id"]` and ignore the query value. **Repro:** create a project as u1, then call `h.list_projects(req({"user_id":"u2","role":"member"}, query={"user_id":"u1"}))`. Expected `[]`, observed u1's project. | y/y/y/y |
| F3 | High | CONFIRMED | B | test_handlers.py:13-23 | The tests use only the honest path. None sends a spoofed `role` or `user_id`, and `test_admin_can_set_quota` never asserts that `QUOTAS` changed. The suite passes on code that contains F1 and F2, so "3 tests pass" says nothing about authorization. | A later edit reintroduces F1 or F2, or a fix is reverted, and CI stays green. | Add three tests: member plus body `role:"admin"` returns 403 and `QUOTAS` stays empty; `list_projects` with a foreign `query.user_id` returns only the caller's projects; the admin path asserts `QUOTAS[1] == 5`. **Mutation check:** run the new tests against the current code, where they must go red. Then apply the fix, where they must go green. | y/y/n/y |
| F4 | Medium | PROBABLE | B | handlers.py:13-14 | `id = len(PROJECTS) + 1` followed by an unconditional `PROJECTS[id] = project` is a read-then-write race. The state is also a module-level dict, which is lost on restart and not shared between workers. | Under a threaded server, two concurrent creates both read `len == n` and get the same id. The second create silently overwrites the first, so one project is lost. With several worker processes, each worker has its own `PROJECTS`. | Use a datastore-generated id or a lock with a monotonic counter, and back the data with persistent storage. **Repro:** call `create_project` from two threads with a barrier before the assignment, and observe one entry for two 201 responses. | y/n/y/n |
| F5 | Medium | CONFIRMED | B | handlers.py:28 | `set_quota` does not check that `project_id` exists, and does not check that `quota` is a non-negative integer. | An admin typo or script sets `quota: "-1"`, `quota: null`, or a quota on project 999. The billing system then reads garbage or orphaned keys. | Return 404 for an unknown project. Return 400 unless `quota` is an `int` with `quota >= 0`. **Repro:** an admin sends `{"project_id": 999, "quota": -5}`. Expected 404 or 400, observed 200. | y/y/y/n |
| F6 | Low | CONFIRMED | B | handlers.py:13, 28 | Missing body keys (`name`, `project_id`, `quota`) raise `KeyError`. `name` is not validated for being empty, its type, or its length. | A client sends an empty body and gets a 500 instead of a 400. | Validate inputs and return 400. **Repro:** `h.create_project(req({"user_id":"u1","role":"member"}))` raises `KeyError`. | y/y/n/n |

## Needs validation, refuted, and what holds up

**NEEDS VALIDATION**
- **Whether the session dict can lack `role` or `user_id`.** This depends on the middleware code, which was not supplied.
- **Whether `project_id` type mismatches cause trouble.** Ids are `int` in `PROJECTS`, but the client may send `"1"` to `set_quota`, and the quota would then not be keyed to the project. Settled by knowing how the router parses JSON and what downstream billing reads.

**REFUTED**
- **"`create_project` lets a user create a project owned by someone else."** It reads `owner` from `session["user_id"]` at handlers.py:13, not from the body.

**WHAT HOLDS UP**
- `create_project` takes ownership from the verified session.
- The 403 path in `set_quota` is correct when no spoofed `role` is sent.
- The intended structure matches the three requested handlers. Each of F1 and F2 is a one-line fix.

**UNVERIFIED CLAIMS**
- **"3 tests pass."** Confirm by running `python -m unittest test_handlers` and attaching the output.
- **"Middleware puts the verified user in session."** Confirm by reviewing the middleware.

**QUESTIONS FOR THE AUTHOR**
1. Was reading `role` from the body or `user_id` from the query meant to support admin impersonation? If so, it must be gated on the session role.
2. Is the in-memory store a placeholder, and what server concurrency model runs in production?

**DECISION-MAKER SUMMARY:** Do not release. Any member can change billed quotas (F1) and any user can read anyone's private project list (F2), and the tests cannot catch either (F3). Fix both lines, add the spoof tests, and re-review. Releasing as is risks billing fraud and a privacy breach on day one.

**OWNER SUMMARY:** The new project features let ordinary users act as administrators when changing billed limits, and let anyone see other people's private project lists. The existing tests miss both problems because they only try the honest path. Both fixes are small, but the release should wait until they are fixed and tested.

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
    {"item": "server/runtime concurrency model", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "handlers.py", "kind": "file"},
      {"unit": "handlers.py:create_project", "kind": "function"},
      {"unit": "handlers.py:list_projects", "kind": "function"},
      {"unit": "handlers.py:set_quota", "kind": "function"},
      {"unit": "test_handlers.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "login middleware", "reason": "not supplied"},
      {"unit": "server runtime / persistence", "reason": "not supplied"},
      {"unit": "test execution and mutation check", "reason": "no tools in session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handlers.py:25",
     "scenario": "A member sends body {\"project_id\":1,\"quota\":1000000,\"role\":\"admin\"}; the role check passes and a billed quota is written.",
     "fix": "Read role only from request[\"session\"][\"role\"]; never from the body.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "set_quota(req({'user_id':'u1','role':'member'}, {'project_id':1,'quota':5,'role':'admin'})): expect 403, observe 200 and QUOTAS[1]==5."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handlers.py:19",
     "scenario": "User u2 calls list_projects with ?user_id=u1 and receives u1's private projects.",
     "fix": "Use request[\"session\"][\"user_id\"] only; ignore query user_id.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Create project as u1; list_projects(req({'user_id':'u2','role':'member'}, query={'user_id':'u1'})): expect [], observe u1's project."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_handlers.py:13-23",
     "scenario": "Tests never send spoofed role/user_id and never assert QUOTAS; the suite passes with F1/F2 present, so regressions ship green.",
     "fix": "Add spoofed-role, foreign-user_id and QUOTAS-value assertions; confirm they fail on current code and pass after the fix.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Add test: member with body role=admin expects 403; it fails on current code (observed 200)."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "handlers.py:13-14",
     "scenario": "Two concurrent creates read the same len(PROJECTS) and get the same id; the second overwrites the first. In-memory state is lost on restart and not shared across workers.",
     "fix": "Use datastore-generated ids or a locked counter with persistent storage.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "Two threads call create_project with a barrier before assignment; observe one entry for two 201 responses."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handlers.py:28",
     "scenario": "Admin sets quota -5 or a string, or on nonexistent project 999; billing reads invalid or orphaned values.",
     "fix": "404 on unknown project_id; 400 unless quota is a non-negative int.",
     "answers": {"a": true, "b": true, "c": true, "d": false},
     "reproduction": "Admin set_quota with {'project_id':999,'quota':-5}: expect 404/400, observe 200."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handlers.py:13, 28",
     "scenario": "A request missing name, project_id or quota raises KeyError, giving a 500 instead of a 400.",
     "fix": "Validate required fields and return 400.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "create_project(req({'user_id':'u1','role':'member'})) raises KeyError."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "handlers.py:28",
     "suspicion": "project_id may arrive as a string, so the quota is keyed differently from the int project id.",
     "unresolved_fact": "How the router parses body JSON and how billing reads QUOTAS keys."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "handlers.py:3",
     "suspicion": "Session may lack role or user_id in some middleware path.",
     "unresolved_fact": "Middleware source was not supplied."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "create_project lets a user assign another owner.",
     "evidence": "handlers.py:13 sets owner from session[\"user_id\"], not the body."}
  ]
}
```