# Redteam review: project API handlers

**Review setup:** I reviewed this myself in this session, with no tools. I am not the author of this work, but no fresh subagent or second seat was available. I could not run the code or the tests, so every trace below is by reading the code. Re-run the tests in a scratch copy before you rely on the mutation claims.

---

**VERDICT: REWORK.** Two authorization checks read identity from client-controlled fields. Any member can raise billed quotas and read any user's private project list, and the passing tests cannot detect either flaw.

**CONFIDENCE: medium.** I traced the two Critical findings directly from the code and I am confident in them. Confidence is limited by:
- no tools, so nothing was executed;
- the login middleware and deployment setup were not supplied.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| Original request (`request.md`) | Seen | — |
| Context (`context.md`) | Seen | — |
| `handlers.py` | Seen | — |
| `test_handlers.py` | Seen | — |
| Login middleware code | Not seen | Partly. The request and docstring say it puts the verified user in `session`. The findings depend only on handlers ignoring `session`, so this gap does not change them. |
| Router, server and worker model, storage plan | Not seen | Yes, for findings 4 and 5 (in-memory state, id race). |
| Output of the "3 tests pass" run | Not seen | Low. The tests are weak whether or not they pass. |

**SEATS AND GATE**
- **Seats:** Only a local reviewer ran. No subagent was available. No cross-vendor seats ran because none were requested and there were no tools.
- **Sensitivity gate:** Passed. The work contains no personal data, credentials or confidential material.

---

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | B | `handlers.py` `set_quota`: `role = body.get("role", request["session"]["role"])` | The admin check trusts a `role` field in the request body. The docstring says the body is "whatever the client sent". The verified `session["role"]` is only a fallback. | A member POSTs `{"project_id": 1, "quota": 100000, "role": "admin"}`. The check passes, and a billed quota is set by a non-admin. | Use `request["session"]["role"]` only and never read role from the body. Add a test: a member session with body `role: "admin"` must get 403. | Confirmed. The strongest defence would be that the middleware strips `role` from the body. The docstring says the body is unfiltered client input, and nothing in the request says otherwise. |
| 2 | Critical | CONFIRMED | B | `handlers.py` `list_projects`: `request["query"].get("user_id", request["session"]["user_id"])` | The handler lists projects for any `user_id` named in the query string. The request asked for "list **my** projects", and context says project lists are private. This is an IDOR and also drift from the request. | User u1 calls `GET /projects?user_id=u2` and receives u2's private projects. Enumerating ids exposes every user's list. | Filter on `session["user_id"]` only. If admins need to list other users' projects, add a separate, role-checked path. Add a test: u1 with `query={"user_id": "u2"}` must not see u2's projects. | Confirmed. No reading of the request supports a caller-chosen user, and nothing checks the caller's identity before honouring the override. |
| 3 | High | CONFIRMED (by reading; mutation not run) | B | `test_handlers.py`, all three tests | The tests only use honest inputs. None sends `body.role` or `query.user_id`, so the suite is green with both Critical bugs present. The "3 tests pass" claim gives no assurance about authorization. | Findings 1 and 2 ship with green CI. A later fix that regresses would also stay green. | Add the two hostile-input tests from findings 1 and 2. Mutation check: run them against the current code and they should go red, which shows they guard the bug. Also add a test where the quota is set on a project the caller does not own. | Confirmed. I traced each test: none exercises a client-supplied identity field. |
| 4 | Medium | CONFIRMED | B | `set_quota`: `QUOTAS[body["project_id"]] = body["quota"]` | Neither `project_id` nor `quota` is validated. It does not check that the project exists, that the quota is a non-negative integer, or that the id has the right type. `"1"` and `1` are different keys from the `int` ids that `create_project` assigns. | Even once only admins can reach it: an admin sets a quota on `"1"`, so billing keyed on `1` sees no quota. Or a negative, string or float quota flows into billing. A missing key raises `KeyError`, which becomes a 500 error. | Return 404 if the project is unknown. Coerce or reject the id type. Validate that `quota` is an `int` at or above 0 with an upper bound. Return 400 for missing fields. | Not a High candidate, so no confirm-or-refute round was needed. |
| 5 | Medium | PROBABLE | B | Module globals `PROJECTS` and `QUOTAS`; `"id": len(PROJECTS) + 1` | All state lives in memory: it is lost on restart and not shared across worker processes. The id comes from a non-atomic read followed by a write. | In production with multiple workers or a restart, projects and billed quotas vanish or differ between workers. Two concurrent creates can get the same id, and the second overwrites the first. | Use the real datastore with database-generated ids. If in-memory storage is intentional for now, say so explicitly. | Not a High candidate. This depends on the deployment model, which was not supplied (see Questions). |
| 6 | Low | CONFIRMED | B | `create_project`: `request["body"]["name"]` | A missing name raises `KeyError`, which becomes a 500 error. An empty, huge or non-string name is accepted. | Malformed client input produces server errors or junk records. | Validate the name: a string, non-empty, with a length cap. Return 400 otherwise. | — |
| 7 | Low | PROBABLE | R/B | `set_quota` | Billed quota changes leave no record of who changed what, or when. | A billing dispute cannot be traced back to an actor. | Log each change with the actor's `session.user_id`, the old and new value, and a timestamp. | — |

---

## WHAT HOLDS UP
- `create_project` takes the owner from `session["user_id"]`, not from the client. Ownership cannot be spoofed at creation.
- `set_quota` falls back to the session role. Once the body override is removed, the check uses the right source.
- `setUp` clears the global state, so the tests are isolated from each other.

## UNVERIFIED CLAIMS
- **"3 tests pass":** Not run here. Settle it by running `python -m unittest test_handlers` in a scratch copy. Even if they pass, finding 3 stands.
- **"The middleware has put the verified user in `session`":** Accepted as given. It does not affect the findings, because the handlers bypass `session` anyway.

## QUESTIONS FOR THE AUTHOR
1. Is there a real requirement for admins to list another user's projects or to pass a role in the body? If not, findings 1 and 2 are simply bugs to delete.
2. Is the in-memory storage a placeholder, or what actually ships? What is the worker and process model in production?

## DECISION-MAKER SUMMARY
Do not release. Any logged-in member can set billed quotas (finding 1) and read any user's private projects (finding 2), and the passing tests do not cover either case. The fix is small: read identity only from `session` and add two hostile-input tests. Then address validation and storage before production.

## OWNER SUMMARY
The code lets any ordinary user pretend to be an admin by adding one field to their request, which lets them change billed limits. It also lets any user see anyone else's private project list just by asking for it. Both are quick to fix, and the existing tests did not catch them, so new tests should be added along with the fix.

---

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "handlers.py", "status": "seen", "matters": true},
    {"item": "test_handlers.py", "status": "seen", "matters": true},
    {"item": "login middleware code", "status": "not_seen", "matters": false},
    {"item": "deployment/worker model and storage plan", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "local-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "handlers.py set_quota: role = body.get(\"role\", request[\"session\"][\"role\"])",
     "scenario": "A member sends body {\"project_id\":1,\"quota\":100000,\"role\":\"admin\"}; the admin check passes and a billed quota is set by a non-admin.",
     "fix": "Read role only from request[\"session\"][\"role\"]; add a test where a member session with body role=admin gets 403.", "status": "confirmed"},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "handlers.py list_projects: request[\"query\"].get(\"user_id\", ...)",
     "scenario": "User u1 requests ?user_id=u2 and receives u2's private projects (IDOR; drift from 'list my projects').",
     "fix": "Filter on session[\"user_id\"] only; add a test that u1 with query user_id=u2 sees none of u2's projects.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "test_handlers.py (all three tests)",
     "scenario": "No test sends body.role or query.user_id, so the suite passes with both Critical bugs present and would not catch a regression.",
     "fix": "Add hostile-input tests for findings 1 and 2 and confirm they fail against the current code.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "handlers.py set_quota: QUOTAS[body[\"project_id\"]] = body[\"quota\"]",
     "scenario": "No check that the project exists or that the quota is a valid type or range; key \"1\" vs 1 mismatch splits quotas; a negative or string quota reaches billing; a missing key returns 500.",
     "fix": "Return 404 for unknown projects, validate the id type and that quota is a non-negative int with a bound, and return 400 for missing fields."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "handlers.py module globals PROJECTS/QUOTAS; id = len(PROJECTS) + 1",
     "scenario": "Multi-worker or restarted production loses or diverges projects and billed quotas; concurrent creates collide on an id and overwrite.",
     "fix": "Use a persistent datastore with database-generated ids, or document in-memory storage as a placeholder."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "handlers.py create_project: request[\"body\"][\"name\"]",
     "scenario": "A missing name returns 500; an empty or huge name is accepted.",
     "fix": "Validate name (string, non-empty, length cap) and return 400 otherwise."},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "R", "location": "handlers.py set_quota",
     "scenario": "Billed quota changes leave no record of who changed what, so disputes cannot be traced.",
     "fix": "Log actor, project, old and new quota, and timestamp for each change."}
  ]
}
```