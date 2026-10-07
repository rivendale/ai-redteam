# Review: notes service handlers

Verdict: REWORK. One route returns every user's notes to any logged-in user.

| # | Severity | Where | Problem |
|---|---|---|---|
| 1 | Critical | app.py:29 | /admin/export has no admin check |

```json
{
  "verdict": "Rework",
  "findings": [
    {"id": "R1", "severity": "critical", "evidence": "confirmed",
     "location": {"file": "app.py", "line": 29},
     "issue": "/admin/export never calls auth.require_admin, unlike /admin/users",
     "failure_scenario": "tok-alice sends GET /admin/export and receives root's and bob's notes with status 200",
     "recommendation": "call auth.require_admin(user) before store.export_all(); add a test with a non-admin token"}
  ],
  "ledger": {"read": ["request.md", "app.py", "auth.py", "store.py", "test_app.py"], "not_read": []}
}
```
