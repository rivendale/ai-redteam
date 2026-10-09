**Note:** This is a review without tools. No code or tests were run. Findings marked CONFIRMED were traced by reading the exact lines quoted. The work was not written in this conversation, so the usual author-anchoring risk does not apply. It is still a single-reviewer pass with no subagent or second seat.

**VERDICT: REWORK.** Two authorization bypasses let any logged-in user grant themselves admin rights on billed quotas and read any other user's private project list.

**CONFIDENCE: high** for the two Criticals, because each is a one-line trace from client input to the sensitive operation. **Medium** for the rest. What limits confidence: no tools, so nothing was executed, and the server and deployment model is unknown.

**INPUTS LEDGER**
- Seen: `request.md`, `context.md`, `handlers.py`, `test_handlers.py`.
- Not seen: the login middleware, which matters a little. The handlers' docstring and the request both say `request["session"]` is verified, so I take that as given. Neither Critical depends on it.
- Not seen: the server, router and deployment (threads or processes, persistence). This matters for S1 and S2.
- Not seen: the test run output. "3 tests pass" is taken on assertion. It does not change the findings.

**COVERAGE**
- Checked: `handlers.py` (`create_project`, `list_projects`, `set_quota`, module state, docstring) and `test_handlers.py` (all 3 tests).
- Not checked: the middleware, routing, storage and deployment, none of which were supplied.

**SEATS AND GATE:** One local reviewer only, with no subagent or cross-vendor seats. The sensitivity gate passed: the material is synthetic code with no personal data or secrets.

**Pass 1, reconstruct:** The work claims to deliver three handlers. Members create and list their own projects, and only admins set billed quotas, with identity taken from the verified session. For this to be correct, every authorization decision must come from `request["session"]` and never from `body` or `query`. The file's own docstring says those are "whatever the client sent". The work fails exactly that assumption, twice. Tracks used: B, plus A for requirement fit.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | `handlers.py:25` `role = body.get("role", request["session"]["role"])` | The admin check reads the role from the client-controlled body first. The session role is only a fallback. | A member POSTs `{"project_id": 1, "quota": 999999, "role": "admin"}`. Line 26 passes, and line 28 writes a billed quota for any project. | Use `role = request["session"]["role"]` and ignore `body["role"]`. Repro test: `set_quota(req({"user_id":"u1","role":"member"}, {"project_id":1,"quota":5,"role":"admin"}))` should return 403. It currently returns 200. | a Y, b Y, c Y, d Y |
| F2 | Critical | CONFIRMED | B | `handlers.py:19` `user_id = request["query"].get("user_id", request["session"]["user_id"])` | "List my projects" accepts any `user_id` from the query string. | User u2 calls `GET /projects?user_id=u1` and receives all of u1's projects. Context says project lists are private. | Use `user_id = request["session"]["user_id"]` unconditionally. Repro test: u1 creates "alpha", then `list_projects(req({"user_id":"u2","role":"member"}, query={"user_id":"u1"}))["body"]` should be `[]`. It currently returns alpha. | a Y, b Y, c Y, d Y |
| F3 | Medium | CONFIRMED | B | `test_handlers.py:15-25` | The tests never send a hostile field, so both Criticals pass all three tests. `test_create_and_list_own` checks only the happy path. Nothing checks that one user cannot see another's projects. | Someone changes the auth source later, or leaves it as is, and CI stays green. The reported "3 tests pass" is consistent with the vulnerable code. | Add the two repro tests from F1 and F2. Both should fail on the current code and pass after the fix, which serves as their positive control. | a Y, b Y, c N, d Y |
| F4 | Medium | CONFIRMED | B | `handlers.py:28` | `set_quota` does not check that `project_id` exists or that `quota` is a non-negative integer. A missing key raises an uncaught `KeyError`. | An admin, or an attacker via F1, sets `quota: -5`, `"lots"` or a quota on project 404. Billing then reads a corrupt value. A body without `quota` gives a 500. | Return 404 if `project_id not in PROJECTS`. Return 400 unless `quota` is an `int >= 0` and below a sane upper bound. Repro: `set_quota(admin, {"project_id": 1, "quota": -5})` with no project 1 should give 404 or 400. It currently gives 200. | a Y, b Y, c Y, d N |
| F5 | Medium | PROBABLE | B | `handlers.py:13` `"id": len(PROJECTS) + 1` | The ID comes from a count that is read and then written, with no lock. | Under a threaded server, two concurrent creates both read `len == 3`, both get id 4, and the second overwrites the first user's project. This is silent data loss. Any future delete also causes ID reuse. | Use `itertools.count()` under a lock, or a DB sequence or UUID. Repro: run 100 parallel `create_project` calls in threads and check `len(PROJECTS) == 100`. | a Y, b N, c Y, d N |
| F6 | Low | CONFIRMED | B | `handlers.py:13` `request["body"]["name"]` | There is no validation of `name`. It can be missing (`KeyError`, so a 500), or it can be a non-string or an unbounded length. | A POST with `{}` gives a 500. A POST with a 10 MB name is stored as is. | Return 400 unless `name` is a non-empty `str` within a length limit. | a Y, b Y, c N, d N |

## NEEDS VALIDATION
- **S1, `handlers.py:7-8`:** Billed quotas and projects live in process-memory dicts. They are lost on restart and diverge across worker processes. Unresolved fact: whether production runs a single process with these dicts as the real store, or whether this is a placeholder for a DB layer.
- **S2, `handlers.py:28`:** Quota changes affect billing, but no audit record is written showing who set what and when. Unresolved fact: whether billing or compliance requires an audit trail for quota changes, or whether one is recorded elsewhere.

## REFUTED
- **The session itself may be forged.** The request states the middleware puts the verified user in the session, and the handlers only read it. This is out of scope and not a defect of this work.
- **A member could create a project owned by someone else.** Refuted: `handlers.py:13` takes `owner` from `session["user_id"]`, not from the body.

## WHAT HOLDS UP
- `create_project` sets the owner from the verified session (line 13), which is correct.
- The `list_projects` filter is correct once the `user_id` source is fixed (line 20).
- `set_quota` does have a 403 path, and `test_member_cannot_set_quota` would go red if the check were deleted. It only guards against the wrong mutation.
- `setUp` clears state between tests, so the tests are isolated.

## UNVERIFIED CLAIMS
- "3 tests pass." Not run here. To confirm, run `python3 -m unittest test_handlers -v`. Expect 3 passes on current code, and that the F1 and F2 repro tests fail.

## QUESTIONS FOR THE AUTHOR
1. Is there a legitimate need for admins to list another user's projects? If so, gate it on `session["role"] == "admin"`, not on the query alone.
2. Are `PROJECTS` and `QUOTAS` the production store, and is the server threaded or multi-process? The answers settle S1 and F5.

## DECISION-MAKER SUMMARY
Do not release. F1 lets any member set billed quotas, and F2 exposes every user's private project list. Both are one-line fixes plus two tests. Releasing as is means unauthorized billing changes and a privacy breach, with the current test suite showing green throughout.

## OWNER SUMMARY
The code trusts information sent by the user in two places where it should trust only the login system. As a result, any logged-in user can change billed limits and see other people's private project lists. The fixes are small, but the release should wait until they are made and tested.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "handlers.py", "status": "seen", "matters": true},
    {"item": "test_handlers.py", "status": "seen", "matters": true},
    {"item": "login middleware", "status": "not_seen", "matters": false},
    {"item": "server/deployment and storage config", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "synthetic code, no personal data or secrets"},
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
      {"unit": "server/deployment and storage config", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handlers.py:25",
     "scenario": "A member sends {\"project_id\": 1, \"quota\": 999999, \"role\": \"admin\"}; the role is read from the client body, the admin check passes, and a billed quota is written.",
     "fix": "Read role only from request[\"session\"][\"role\"]; ignore body[\"role\"].",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "set_quota(req({\"user_id\":\"u1\",\"role\":\"member\"}, {\"project_id\":1,\"quota\":5,\"role\":\"admin\"})); expect 403, observe 200."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handlers.py:19",
     "scenario": "User u2 calls list_projects with query user_id=u1 and receives u1's private projects.",
     "fix": "Use request[\"session\"][\"user_id\"] unconditionally.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "u1 creates 'alpha'; list_projects(req({\"user_id\":\"u2\",\"role\":\"member\"}, query={\"user_id\":\"u1\"})) returns alpha; expect []."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_handlers.py:15-25",
     "scenario": "No test sends a hostile role or user_id, so both Critical bypasses pass all 3 tests and CI is green.",
     "fix": "Add the F1 and F2 reproduction tests; confirm they fail on current code and pass after the fix.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Add the F1/F2 tests and run python3 -m unittest; they fail on the current code."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handlers.py:28",
     "scenario": "set_quota accepts a negative, non-integer, or nonexistent-project quota, corrupting billed data; a missing key raises KeyError (500).",
     "fix": "404 if project_id not in PROJECTS; 400 unless quota is int >= 0 within a bound; 400 on missing keys.",
     "answers": {"a": true, "b": true, "c": true, "d": false},
     "reproduction": "set_quota(admin, {\"project_id\": 1, \"quota\": -5}) with no project 1; expect 404/400, observe 200."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "handlers.py:13",
     "scenario": "Two concurrent creates on a threaded server both compute id len(PROJECTS)+1 and the second overwrites the first user's project.",
     "fix": "Allocate IDs from a locked counter, DB sequence, or UUID.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "Run 100 create_project calls across threads; expect len(PROJECTS)==100, may observe fewer."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handlers.py:13",
     "scenario": "A POST with {} raises KeyError (500); a non-string or huge name is stored unchecked.",
     "fix": "Return 400 unless name is a non-empty str within a length limit.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "create_project(req(member, {})); expect 400, observe KeyError."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "handlers.py:7-8",
     "suspicion": "Billed quotas and projects are held in process memory and would be lost on restart or diverge across workers.",
     "unresolved_fact": "Whether these dicts are the production store and whether the server runs multiple processes."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "handlers.py:28",
     "suspicion": "Billed quota changes leave no audit record of who changed what.",
     "unresolved_fact": "Whether billing or compliance requires a quota-change audit trail, or one exists elsewhere."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "A member can create a project owned by another user.",
     "evidence": "handlers.py:13 sets owner from session[\"user_id\"], not from the body."},
    {"id": "C2", "candidate": "The session itself can be forged.",
     "evidence": "The request states the middleware supplies the verified user; the handlers only read it, so this is out of scope."}
  ]
}
```