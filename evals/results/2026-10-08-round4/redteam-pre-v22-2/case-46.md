VERDICT: **REWORK**. Two authorization checks read client-supplied fields instead of the verified session. Any member can set billed quotas, and any caller can list another user's private projects.

CONFIDENCE: **high** for the two Criticals, **medium** overall. Both Criticals are traced line by line in the code shown. No code or tests were run (no tools), and I am the only reviewer; no subagent or second seat was available.

INPUTS LEDGER:
- **Seen:** the original request, the context (production, quotas are billed, project lists are private, "3 tests pass"), `handlers.py`, `test_handlers.py`.
- **Not seen:**
  - The login middleware. This matters little: the Criticals bypass it rather than depend on it.
  - The router, the persistence layer and the deployment model (worker count). These matter for findings 4 and 5.
  - The test run output. "3 tests pass" is UNVERIFIED, but it does not change the verdict because the tests do not cover the failures.

SEATS AND GATE:
- **Sensitivity gate:** no personal data, credentials or confidential material in the work, so it passed.
- **Seats:** only the local reviewer ran. No subagent or cross-vendor seat was available in this session.
- **Independence:** I did not write this code, so this is not a same-context review.

## Reconstruct

The work claims three handlers:
- `create_project` stores a project owned by the session user.
- `list_projects` returns the caller's own projects.
- `set_quota` lets only admins set a project's quota.

For it to be correct, every identity and role decision must come from `request["session"]`, which the middleware verifies. The file's own docstring says `query` and `body` are "whatever the client sent". The load-bearing assumption is that nothing client-controlled reaches an authorization decision, and two handlers break it.

Tracks: B (code) and A (requirement fit).

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | B | `handlers.py` `set_quota`: `role = body.get("role", request["session"]["role"])` | The role is taken from the request body first. The verified session role is only a fallback. | A member POSTs `{"role": "admin", "project_id": 7, "quota": 1000000}`. `role` is `"admin"`, the check passes, and the billed quota is written. A member can also set quotas on projects they do not own. | Use `role = request["session"]["role"]` only. Add a test: member session plus `body={"role": "admin", ...}` must return 403 and leave `QUOTAS` unchanged. | **confirmed.** A defender could argue the middleware strips `body.role`, but the docstring says the body is "whatever the client sent", and nothing in the shown code strips it. |
| 2 | Critical | CONFIRMED | B, A | `handlers.py` `list_projects`: `request["query"].get("user_id", request["session"]["user_id"])` | The owner filter comes from a query parameter. This is an IDOR (insecure direct object reference), and it also drifts from the request, which asked for "list my projects". | User u1 calls `?user_id=u2` and receives u2's private projects. Project lists are stated to be private. | Filter on `request["session"]["user_id"]` only. Add a test: u2 owns a project, u1 sends `query={"user_id": "u2"}`, and the result must be empty or 403. | **confirmed.** A defender could call it an admin feature, but there is no role check and the request never asked for one. |
| 3 | Medium | CONFIRMED (by trace) | B | `test_handlers.py`, all three tests | The tests never send the hostile fields: no `role` in the body, no `user_id` in the query. Both Criticals pass the current suite. | Change `set_quota` to read the session only, or leave it as it is, and the three tests stay green either way. They do not distinguish safe code from vulnerable code. "3 tests pass" is not evidence of authorization. | Add the two negative tests from findings 1 and 2. Confirm each goes red against the current code before fixing it. | n/a |
| 4 | Medium | PROBABLE | B | `create_project`: `"id": len(PROJECTS) + 1` | IDs are derived from the dict size, which is a read-then-write race. | Two concurrent creates in a threaded server get the same id. The second silently overwrites the first, so a user's project is lost or ownership changes. Any future delete would also reuse ids. | Use an atomic counter or a database sequence or UUID, and insert only if the id is absent. | n/a |
| 5 | Medium | PROBABLE | B | Module globals `PROJECTS`, `QUOTAS` | State lives in memory per process. | On restart, all projects and billed quotas are lost. With more than one worker, each worker holds different data, so lists and quotas are inconsistent. Persistence was not specified; whether this is intended is UNVERIFIED. | Confirm the intended storage. For production, persist to the real data store. | n/a |
| 6 | Medium | CONFIRMED (by trace) | B | `set_quota`: `QUOTAS[body["project_id"]] = body["quota"]` | Nothing is validated: the project may not exist, `quota` can be negative, a string or huge, and a missing key raises `KeyError`, which becomes a 500. | An admin sets a quota on a non-existent id, or sets `"quota": "-1"`, and billing consumes the garbage value. A typo yields a 500 instead of a 400. | Check that `project_id` exists in `PROJECTS` and that `quota` is a non-negative int within bounds. Return 400 or 404 otherwise. | n/a |
| 7 | Low | CONFIRMED (by trace) | B, R | `set_quota` | A billed quota change leaves no audit record of who changed what. | A billing dispute cannot establish who changed a quota or when. | Log actor (session user id), project, old and new value, and timestamp. | n/a |
| 8 | Low | CONFIRMED (by trace) | B | `create_project`: `request["body"]["name"]` | A missing name raises `KeyError` (500). There is no type or length check. | A client omits `name` and gets a 500. A 10 MB name is stored as is. | Validate that `name` is present, a string and bounded in length. Return 400 otherwise. | n/a |

## Self-check

The most serious problem that could still be missed would hide in the unseen router: whether `set_quota` is reachable without the login middleware. If it is, `request["session"]` raises a `KeyError`, which fails closed, so the gap is low risk.

## Summary

**WHAT HOLDS UP:**
- `create_project` sets `owner` from the session rather than the body, which is correct.
- A missing `session` raises an error rather than granting access.
- The default paths (no hostile fields) behave as requested.

**UNVERIFIED CLAIMS:**
- "3 tests pass" was not run here. Running `python -m unittest` would settle it, but it matters little given finding 3.
- How the middleware handles the body and query is unknown. Reading the middleware code would settle it.

**QUESTIONS FOR THE AUTHOR:**
1. Was `?user_id=` meant to let admins view other users' lists? If so, it needs a session-role check.
2. What is the intended persistence and worker model?

**DECISION-MAKER SUMMARY:** Do not release. Findings 1 and 2 let any logged-in user grant billed quota and read other users' private project lists, and the passing tests do not cover either case. Fix both to use the session only, add the two negative tests, then re-review.

**OWNER SUMMARY:** The new project features have two security holes. Any logged-in user could change billing limits, and any user could see other people's private project lists. Both are small code fixes with matching tests, and this should not go live until they are done.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "login middleware", "status": "not_seen", "matters": false},
    {"item": "router / persistence / deployment model", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "local-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "handlers.py set_quota: role = body.get(\"role\", request[\"session\"][\"role\"])", "scenario": "Member sends body {\"role\":\"admin\",\"project_id\":7,\"quota\":1000000}; check passes and billed quota is written, on any project.", "fix": "Read role only from request[\"session\"]; test member+body role=admin returns 403 and QUOTAS unchanged.", "status": "confirmed"},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "handlers.py list_projects: request[\"query\"].get(\"user_id\", ...)", "scenario": "User u1 calls ?user_id=u2 and receives u2's private projects (IDOR; also drift from 'list my projects').", "fix": "Filter on request[\"session\"][\"user_id\"] only; test cross-user query returns no foreign projects.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "test_handlers.py (all three tests)", "scenario": "No test sends body role or query user_id; the suite is green with the vulnerable code, so 'tests pass' does not evidence authorization.", "fix": "Add negative tests for findings 1 and 2; confirm they fail on current code before fixing."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "handlers.py create_project: \"id\": len(PROJECTS) + 1", "scenario": "Concurrent creates get the same id; second overwrites first, losing a project or changing owner.", "fix": "Atomic counter/DB sequence or UUID; insert-if-absent."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "handlers.py module globals PROJECTS, QUOTAS", "scenario": "Restart loses all projects and billed quotas; multiple workers see divergent state.", "fix": "Persist to the production data store; confirm intended storage."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "handlers.py set_quota: QUOTAS[body[\"project_id\"]] = body[\"quota\"]", "scenario": "Quota set on nonexistent project or to negative/string value feeds billing; missing key yields 500.", "fix": "Validate project exists and quota is bounded non-negative int; return 400/404."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "handlers.py set_quota", "scenario": "Billed quota changes leave no record of actor or old/new value; disputes cannot be resolved.", "fix": "Write audit log entry with session user, project, old/new quota, timestamp."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "handlers.py create_project: request[\"body\"][\"name\"]", "scenario": "Missing name returns 500; unbounded name size accepted.", "fix": "Validate presence, type and length; return 400."}
  ]
}
```