# Redteam review: `share.py` sharing and permission layer

No subagent or tools were available in this session. I am a single reviewer who did not write the work, so the risk of inheriting the author's assumptions is low, but there is no second seat. Nothing was run. All code statements below come from reading the supplied text.

**VERDICT: SHIP.** The permission check fails closed, sharing is owner-only, and defaults are private. One Low observability gap is open, and the launch should confirm that `doc` is loaded server-side (see Needs validation).

**CONFIDENCE: medium.** It is limited by three things:
- I had no tools, so the claim that the 3 tests pass is unverified.
- The real backend and the callers that construct `doc` were not supplied.
- I could not scan for invisible or look-alike characters.

## Inputs ledger

| Item | Status | Matters? |
|---|---|---|
| request.md | seen | – |
| context.md | seen | – |
| share.py | seen | – |
| test_share.py | seen | – |
| Real permissions backend (`viewers`, `add_viewer` contract) | not supplied | Yes. It decides whether `user in viewers(...)` is a list membership test or a substring test. |
| Callers or request handlers that build `doc` and supply `user` / `actor` | not supplied | Yes. If `doc["owner"]` comes from the client, the owner check can be forged. |
| Test run output | not supplied | Moderate. I traced the tests by reading only. |

## Coverage

**Scope:** the whole work (two files).

**Checked:**
- `share.py`: `DEFAULTS`, `can_view`, `share`, `new_document`
- `test_share.py`: all three tests, plus a by-reading mutation check of each
- request.md and context.md

**Not checked:**
- The backend implementation and the call sites (not supplied)
- Hidden-character scan (no tools)
- Actually running the tests (no tools)

## Seats and gate

- **Seats:** one local reviewer ran. No subagent or cross-vendor seats were available, and none were requested.
- **Sensitivity gate:** the work is code with no personal data in it, so it is not sensitive. The context says production notes contain personal data, but none was supplied here.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | CONFIRMED | B | `share.py` `can_view`, `except Exception: return False` | Backend errors are swallowed with no log, metric or re-raise. A backend outage is indistinguishable from "not a viewer". | The permissions service goes down, which the context says happens. Every shared viewer gets silently denied. Operators see no error, and users see "no access" rather than "temporarily unavailable". It fails closed, so there is no security harm. | **Fix:** keep returning False, but log the exception (and count it) before returning, or return a distinct "unavailable" result the UI can show. **Repro:** `svc = PermissionService(Down())`; `with self.assertLogs(): svc.can_view("bo", DOC)`. This fails today because nothing is logged. | a✓ b✓ c✗ d✓ |

## Needs validation (no severity)

- **S1: where `doc` comes from.** Both `can_view` and `share` trust `doc["owner"]` from the dict they are handed. This is safe only if callers load `doc` server-side by id. It is unsafe if any handler builds it from request input, because a client could then send `owner = self` and share or read any document.
  - **Settles it:** the call sites that construct `doc`.
- **S2: backend return type.** `user in self.backend.viewers(...)` is a membership test only if the result is a list or set. If the real backend returns a comma-joined string, `"an" in "ann,bo"` is True and grants access to the wrong user.
  - **Settles it:** the real backend's `viewers()` return type.
- **S3: identity normalization.** Users are compared with `==` on raw values. If identities can differ by case or whitespace, a viewer could be wrongly denied, or two accounts could be confused.
  - **Settles it:** how the auth layer canonicalizes user IDs.
- **S4: revoking viewers.** There is no way to remove a viewer and no way to list viewers. The request does not spell out revocation, but for personal or business notes a share that cannot be undone may be unacceptable.
  - **Settles it:** whether revocation lives in this layer or elsewhere.

## Refuted

- **"A backend error grants access."** The `except` branch returns False, and test 1 asserts `can_view("eve")` is False under `Down()`.
- **"A non-owner can share."** `share` raises `PermissionError` before calling the backend whenever `actor != doc["owner"]`.
- **"Unsafe defaults."** `DEFAULTS` sets sharing private, telemetry off and debug off, and `new_document` uses private.
- **"Tests never fail."** By reading, each test would go red under a mutation of the code it guards:
  - Change the `except` branch to `return True`: test 1 fails.
  - Set `DEFAULTS["sharing"]` to `"public"`: test 2 fails.
  - Delete the owner check in `share`: test 3 fails.

  I did not run these mutations.

## What holds up

- `can_view` fails closed on any backend exception, and the owner keeps access during an outage. This is a sound availability choice.
- Owner-only sharing is enforced before the backend write.
- Defaults are private.
- The tests assert real behavior and cover the fail-closed path.

Minor note: the `doc["sharing"]` field, `telemetry` and `debug` are never read by the permission logic. That is harmless now, because it fails closed, but someone setting `sharing="public"` would expect it to do something.

## Unverified claims

- **"3 tests pass":** run `python -m unittest test_share` in a clean environment.
- **Backend behavior:** read the real client.

## Questions for the author

1. Is `doc` always loaded server-side by id, never from the request?
2. What type does the real `viewers()` return?
3. Is revoking a viewer in scope for launch?

## Decision-maker summary

The permission logic is correct and fails closed. Before launch, confirm that `doc` is loaded server-side and that the backend returns a list. Add logging on backend failures so outages are visible. If the first assumption is false, any user could read or share any note.

## Owner summary

The sharing code correctly limits who can see and share a note, and it locks people out rather than letting them in when the permission system is down. Two things should be confirmed before launch: that the app looks up who owns a note itself rather than trusting what the user's device sends, and that outages get logged so the team notices them. It may also be worth deciding whether owners need a way to un-share a note.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "share.py", "status": "seen", "matters": true},
    {"item": "test_share.py", "status": "seen", "matters": true},
    {"item": "real permissions backend", "status": "not_seen", "matters": true},
    {"item": "callers constructing doc/user", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-single-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Work is code only; no personal data supplied."},
  "coverage": {
    "checked": [
      {"unit": "share.py", "kind": "file"},
      {"unit": "test_share.py", "kind": "file"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "share.py:PermissionService.can_view", "kind": "function"},
      {"unit": "share.py:PermissionService.share", "kind": "function"},
      {"unit": "share.py:new_document", "kind": "function"},
      {"unit": "share.py:DEFAULTS", "kind": "config"}
    ],
    "not_checked": [
      {"unit": "real permissions backend", "reason": "not_supplied"},
      {"unit": "callers constructing doc", "reason": "not_supplied"},
      {"unit": "test execution and hidden-character scan", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "share.py: PermissionService.can_view, except Exception: return False",
     "scenario": "When the permissions backend is down, every shared viewer is silently denied with no log or metric, so the outage is invisible to operators and users see a misleading no-access result (fails closed, no security harm).",
     "fix": "Log and count the exception before returning False, or return a distinct unavailable result for the UI.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "svc = PermissionService(Down()); with self.assertLogs(): svc.can_view('bo', DOC) -> fails today because nothing is logged."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "share.py: can_view and share use doc['owner']",
     "suspicion": "If any caller builds doc from client input, a forged owner field bypasses both checks.",
     "unresolved_fact": "Whether every call site loads doc server-side by id."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "share.py: user in self.backend.viewers(doc['id'])",
     "suspicion": "If the real backend returns a string, membership becomes a substring match and grants access to the wrong user.",
     "unresolved_fact": "The return type of the real backend's viewers()."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "share.py: user == doc['owner'], actor != doc['owner']",
     "suspicion": "Raw equality on user IDs may mis-match if identities are not canonicalized.",
     "unresolved_fact": "How the auth layer normalizes user identifiers."},
    {"id": "S4", "status": "needs_validation", "track": "D", "location": "share.py: PermissionService (no revoke or list method)",
     "suspicion": "Shares cannot be revoked through this layer.",
     "unresolved_fact": "Whether revocation is in scope for launch or handled elsewhere."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "A backend error grants access.", "evidence": "The except branch returns False; test 1 asserts can_view('eve') is False under Down()."},
    {"id": "C2", "candidate": "A non-owner can share.", "evidence": "share raises PermissionError before add_viewer when actor != doc['owner']; test 3 covers it."},
    {"id": "C3", "candidate": "Unsafe defaults.", "evidence": "DEFAULTS sets sharing private, telemetry False, debug False; new_document uses the private default."}
  ]
}
```