# Redteam report: `share.py` sharing and permission layer

**Single reviewer, no tools.** I could not run the code or tests. Everything below comes from reading the supplied text. Re-run in a fresh session with tools before launch.

**VERDICT: SHIP WITH FIXES.** The core access check is sound. It denies access when the backend fails and lets only the owner share. But there is no way to revoke a viewer, and outages are invisible to operators.

**CONFIDENCE: medium.** It is limited by four things:
- No tools: the tests were not run and no mutation was tried.
- I was the only reviewer.
- The real permissions backend and the callers were not supplied.
- How `user`, `actor` and `doc` are obtained is unknown.

**INPUTS LEDGER:**
- **Seen:** `request.md`, `context.md`, `share.py`, `test_share.py`.
- **Not seen: the real backend client.** This matters: what `viewers()` returns and whether a remove call exists.
- **Not seen: the request handlers or API layer that call `PermissionService`.** This matters: whether `doc` comes from trusted storage and whether `user` is authenticated.
- **Not seen: test run output.** It matters a little: "3 tests pass" is asserted, not shown.

**COVERAGE:**
- **Checked:**
  - `share.py`: `PermissionService.can_view`, `PermissionService.share`, `new_document`, `DEFAULTS`
  - `test_share.py`: all 3 tests, traced by hand against `share.py`
- **Not checked:**
  - The backend implementation (not supplied)
  - The callers and authentication (not supplied)
  - Running the tests and mutation testing (no tools)

**SEATS AND GATE:**
- **Local reviewer:** ran (this session).
- **Cross-vendor seats:** none ran; no tools were available and none were requested.
- **Sensitivity gate:** the work contains no personal data or credentials. The context says production notes hold personal information, but none of it is in the work.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | B | `share.py:17-21` (whole `PermissionService`) | Viewers can be added but never removed. No `unshare`/`remove_viewer` exists, and no owner check guards removal. | An owner shares a note with personal information with the wrong person, or a colleague leaves. The owner cannot revoke access through this layer. Either the viewer keeps access indefinitely, or callers go straight to the backend and skip the owner check. | Add `unshare(actor, doc, other)` with the same owner guard. Test: `share("ann", DOC, "bo")`, then `unshare("ann", DOC, "bo")`, then assert `can_view("bo", DOC)` is False. Also assert that `unshare("eve", …)` raises `PermissionError`. Today `AttributeError: 'PermissionService' object has no attribute 'unshare'`. | a✓ b✓ c✗* d✓ |
| F2 | Medium | CONFIRMED | B | `share.py:13-14` | `except Exception: return False` hides every error without logging. That includes backend outages and also programming bugs such as a `TypeError`. | The context says the backend does go down. During an outage, every shared viewer is silently told "no access". Operators see no error, users see a denial instead of "temporarily unavailable", and an outage looks like a mass permission change. | Catch the backend's connection or timeout errors specifically, log or emit a metric, and still return False. Let other exceptions propagate. Repro: a backend whose `viewers` raises `TypeError` gives `can_view("bo", DOC)` → False with nothing logged. | a✓ b✓ c✗ d✓ |
| F3 | Low | CONFIRMED | B | `share.py:2`, `share.py:24` | The `sharing` field is set to `"private"` but `can_view` never reads it. `telemetry` and `debug` in `DEFAULTS` are unused and were not asked for. | A later developer sets `sharing="public"` and expects it to take effect, but nothing changes. The test `test_new_documents_are_private` passes even when the document is shared, so it suggests a privacy guarantee the code does not enforce. | Remove the field, or make `can_view` consult it. Rename or reword the test so it does not imply enforcement. Drop the unused keys. | a✓ b✓ c✗ d✗ |

\* F1 on (c): the request does not literally name revocation. The finding is High because of (a), (b) and (d). Whether revocation is in scope is the first question for the author.

## Needs validation

- **S1, `share.py:18` and `share.py:9`: who supplies `doc`?** `share()` and `can_view()` trust `doc["owner"]` from the argument. If any caller builds `doc` from the request body instead of loading it from storage, a caller can name themselves owner and share or view anything. *Settled by:* whether every call site loads `doc` server-side by ID.
- **S2, `share.py:12`: what does the real backend's `viewers()` return?** If it can return a string, for example a comma-joined list, then `user in "joanne,bob"` is a substring match. User `"ann"` would then pass. *Settled by:* the real backend's return type.
- **S3, `share.py:9`: are `user` and `actor` authenticated identities?** If either can be `None` or an empty string for anonymous requests, `None == doc["owner"]` matters for documents whose owner is missing. *Settled by:* the auth layer that calls this.
- **S4, test strength.** By hand-tracing, the tests appear to guard the important behavior:
  - Removing the owner guard in `share` makes `assertFalse(can_view("eve"))` fail.
  - Changing the `except` to `return True` makes test 1 fail.

  This is PROBABLE only, because no mutation was run. *Settled by:* applying those two mutations in a scratch copy and seeing the tests go red.

## Refuted

- **"Backend outage grants access" (fail-open).** Refuted: `share.py:13-14` returns False on exception, and `test_backend_error_denies_a_stranger_but_not_the_owner` asserts this.
- **"`share` bypasses the owner check".** Refuted: `share.py:19-20` raises before `add_viewer`, and test 3 covers it.
- **"Owner locked out during outage".** Refuted: the owner check at `share.py:9-10` runs before the backend call.

## What holds up

- The access check fails closed when the backend errors.
- The owner short-circuit avoids the backend, so owners keep access during outages.
- The owner-only sharing guard is correct.
- Tests 1 and 3 assert real behavior in both directions (allow and deny), not just the happy path.

## Unverified claims

- **"3 tests in `test_share.py` pass".** By hand-trace they would pass on this code, but they were not run. Confirm with `python -m unittest test_share -v`.

## Questions for the author

1. Is revoking a viewer in scope for launch, and if so, where does it live and is it owner-guarded?
2. Is `doc` always loaded from storage by ID before it reaches `PermissionService`?
3. What exactly does the real `backend.viewers()` return?

## Decision-maker summary

The permission check is sound and denies access when the backend fails. Two gaps should be closed before launch:
- Add an owner-guarded way to revoke a viewer (F1).
- Log backend failures instead of swallowing them (F2).

Also confirm that callers pass a server-loaded document (S1). If you ship as is, mistaken shares of personal notes cannot be undone through this layer, and backend outages will look like silent access denials.

## Owner summary

The basic rule, that only the owner can share and that strangers are blocked even when the permission service is down, looks right. However, once a note is shared there is currently no way to take the access back. When the permission service fails, nobody is alerted. Both should be fixed before launch.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "share.py", "status": "seen", "matters": true},
    {"item": "test_share.py", "status": "seen", "matters": true},
    {"item": "real permissions backend client", "status": "not_seen", "matters": true},
    {"item": "callers / API handlers and auth layer", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Work contains code only; no personal data or credentials in the supplied material."},
  "coverage": {
    "checked": [
      {"unit": "share.py", "kind": "file"},
      {"unit": "share.py:PermissionService.can_view", "kind": "function"},
      {"unit": "share.py:PermissionService.share", "kind": "function"},
      {"unit": "share.py:new_document", "kind": "function"},
      {"unit": "share.py:DEFAULTS", "kind": "config"},
      {"unit": "test_share.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "permissions backend implementation", "reason": "not supplied"},
      {"unit": "callers and authentication", "reason": "not supplied"},
      {"unit": "test execution and mutation testing", "reason": "no tools in this session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "share.py:17-21 (PermissionService)",
     "scenario": "An owner shares a personal note with the wrong user; no unshare exists, so access cannot be revoked through this layer, or callers bypass the owner guard by calling the backend directly.",
     "fix": "Add an owner-guarded unshare(actor, doc, other) that removes the viewer from the backend.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "share('ann', DOC, 'bo'); call unshare('ann', DOC, 'bo'); expect can_view('bo', DOC) False; observe AttributeError because unshare does not exist."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "share.py:13-14",
     "scenario": "During a backend outage (stated in context) or on any programming error, every shared viewer is silently denied with no log or metric, so the outage is invisible and indistinguishable from revoked access.",
     "fix": "Catch only backend connection/timeout errors, log or emit a metric, still return False; let other exceptions propagate.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Backend whose viewers() raises TypeError: can_view('bo', DOC) returns False and nothing is logged; expected a raised error or a logged event."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "share.py:2, share.py:24",
     "scenario": "A developer sets sharing='public' expecting it to apply; can_view never reads it, and test_new_documents_are_private implies an enforced privacy guarantee that does not exist. telemetry/debug defaults are unused extras.",
     "fix": "Remove the sharing field and unused DEFAULTS keys, or make can_view consult sharing; reword the test.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Create a doc with sharing='public'; can_view('stranger', doc) returns False; the field has no effect."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "share.py:9, share.py:18",
     "suspicion": "doc['owner'] is trusted from the argument; a caller that builds doc from request input lets anyone claim ownership.",
     "unresolved_fact": "Whether every call site loads doc from storage by ID server-side."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "share.py:12",
     "suspicion": "If backend.viewers() returns a string, 'in' does substring matching and grants access to unlisted users.",
     "unresolved_fact": "The real backend's return type for viewers()."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "share.py:9, share.py:19",
     "suspicion": "Anonymous user/actor values (None or empty) may match a document with a missing or empty owner.",
     "unresolved_fact": "Whether the auth layer guarantees a non-empty authenticated identity."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "test_share.py",
     "suspicion": "Tests appear to guard the owner check and the fail-closed path, but have not been shown to fail under mutation.",
     "unresolved_fact": "Whether removing the owner guard in share() or changing the except branch to return True turns the tests red in a scratch copy."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Backend outage grants access (fail-open).", "evidence": "share.py:13-14 returns False on exception; test 1 asserts eve is denied with a Down backend."},
    {"id": "C2", "candidate": "share() lets a non-owner add viewers.", "evidence": "share.py:19-20 raises PermissionError before add_viewer; test 3 asserts it."},
    {"id": "C3", "candidate": "Owner loses access during a backend outage.", "evidence": "share.py:9-10 returns True for the owner before any backend call; test 1 asserts it."}
  ]
}
```