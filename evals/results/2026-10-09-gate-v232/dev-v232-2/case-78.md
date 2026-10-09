# Redteam review: `share.py` (sharing and permission layer)

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent and no tools were available here. Nothing was run. Every reproduction below is a test to write and run, not one I observed.

**VERDICT: REWORK.** `can_view` returns `True` whenever the permissions backend raises an error. The context says that backend does go down, so during any outage every user can read every note.

**CONFIDENCE: medium.** The Critical finding is traced to exact lines and does not depend on anything missing. Confidence is limited by:
- a same-context review with no tools;
- the backend client, the callers, the link-sharing handler and any tests were not supplied.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| `request.md` (original request) | seen | yes |
| `context.md` (stakes, backend outages) | seen | yes |
| `share.py` | seen, read in full | yes |
| Backend client (`viewers`, `add_viewer`): return type and failure modes | not supplied | yes, it bears on F1 and the substring suspicion |
| Callers of `can_view` / `share`, HTTP routes, link handler | not supplied | yes, it decides whether `sharing` and `debug`/`telemetry` take effect |
| Tests | not supplied; none referenced | yes, no evidence the outage path was ever exercised |

**COVERAGE**
- Scope: the whole supplied work (one file).
- Checked:
  - documents: `request.md`, `context.md`, `share.py`;
  - functions: `PermissionService.__init__`, `can_view`, `share`, `new_document`;
  - config: `DEFAULTS`.
- Not checked: the backend client, callers, routes and tests (`not_supplied`). Nothing was run (`no_tools`).

**SEATS AND GATE**
- Sensitivity: the work is source code with no personal data, credentials or client records, so the gate passed. The deployed data (notes) is sensitive, which raises the stakes.
- Seats: the local same-context reviewer ran. No subagent or cross-vendor seat was available.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | `share.py:12-15` | `except Exception: return True`: the access check fails open. | The permissions service is down, or slow and raising. Any authenticated user calls `can_view(user, doc)` on a document they were never shared on and gets `True`. They read another person's personal or business notes. Because the catch is broad, it also turns programming errors into "allowed": a `TypeError` from a `None` return, an `AttributeError`, or a `KeyError` on `doc["id"]`. | **Fix:** fail closed. Catch only the backend's specific transport error, then return `False` or raise a `PermissionUnavailable` that callers map to 503. Never grant on error. Log the failure without the note text. **Repro:** `class Down: def viewers(self, _): raise ConnectionError()`; `svc = PermissionService(Down())`; `assert svc.can_view("mallory", {"id": 1, "owner": "alice"}) is False`. On current code this returns `True`, so the test is red. | y/y/y/y |
| F2 | High | CONFIRMED | B | `share.py:2`, `share.py:25`, against `share.py:9-15` | Every new document is created with `sharing: "anyone_with_link"`. The request asks for "viewers are listed per document" and never asks for link sharing. `can_view` ignores `doc["sharing"]` entirely. Two sources of truth now disagree, and the stored default is the most permissive option. | A new document is saved with `sharing="anyone_with_link"`. A link-preview route, export or search index reads that field. It treats the document as public, though the owner never shared it and the viewer list is empty. Even if nothing reads the field today, the next developer who does inherits a public-by-default store. | **Fix:** drop link sharing (it was not requested), or default to `"private"` and enforce it in `can_view`. Never store a mode that the check ignores. Migrate existing records. **Repro:** `d = new_document("alice", "t", 1)`; `assert d["sharing"] != "anyone_with_link"`. This is red on current code. | y/y/n/y |
| F3 | Medium | CONFIRMED | B | `share.py:17-21` (absent function) | There is no way to remove a viewer: there is `add_viewer` but no `remove_viewer` or unshare. A permission layer that can grant but not revoke is incomplete. | An owner shares a note with the wrong person, or with an ex-colleague. They cannot revoke access through this layer. Exposure continues until someone edits the backend by hand. | **Fix:** add `unshare(actor, doc, other)` with the same owner check, plus a test. **Repro:** `hasattr(PermissionService, "unshare")` is `False`. After `share("alice", doc, "bob")`, no call through `PermissionService` makes `can_view("bob", doc)` return `False`. | y/y/n/n |
| F4 | Low | CONFIRMED | B | `share.py:2` | `DEFAULTS` ships `telemetry: True` and `debug: True` for a production app holding personal data. Nothing in the supplied code reads these, so they are dead or used elsewhere. | If another module honours these values, production runs with debug on (stack traces, verbose logs) and telemetry on without consent. Note content or user IDs may leave the system. | **Fix:** default both to `False` and enable them explicitly per environment. Delete them if unused. **Repro:** `from share import DEFAULTS`; `assert DEFAULTS["debug"] is False and DEFAULTS["telemetry"] is False`. This is red on current code. | y/y/n/n |

**Sibling search (F1 and F2)**
- I searched the whole file for other `except` blocks and other paths returning `True` without a viewer check. The only other `True` path is the owner branch (`share.py:10-11`), which is correct.
- `share()` has no try block, so a backend failure there propagates and fails closed.
- No other function reads `DEFAULTS["sharing"]`.
- F1 is a security finding. Its boundary:
  - principal: any authenticated non-viewer;
  - input: any document they request;
  - control that fails: the viewer check, bypassed by `except: return True`;
  - boundary crossed: non-viewer to viewer;
  - resource: every document's notes.
- F2 is not a security finding within the supplied code. Its exposure depends on an unsupplied consumer (see NEEDS VALIDATION).

## NEEDS VALIDATION
- **Membership test may match substrings.** If `backend.viewers()` returns a string (for example `"bobby,alice"`), then `"bob" in ...` is `True`. If it returns `None` on outage, a `TypeError` is raised and F1 turns it into `True`. What settles it: the documented return type of `viewers()`.
- **Link sharing may already be live.** Does any route, export or indexer honour `doc["sharing"] == "anyone_with_link"`? If so, F2 becomes a security finding at Critical severity. What settles it: the callers and routes.
- **Anonymous users may match ownerless documents.** If unauthenticated users are represented as `None` and a document can be created with `owner=None`, then `can_view(None, doc)` returns `True` at line 10. What settles it: how the auth layer represents anonymous users, and whether `new_document` can receive `None`.
- **Unknown principals can be added.** `share()` does not validate `other`: unknown users, self, or duplicates can be added. Whether this matters depends on whether the backend dedupes and validates.

## REFUTED
- **"`share()` lets non-owners share."** Refuted: line 19 compares `actor` against `doc["owner"]` and raises before `add_viewer`.
- **"`share()` fails open on backend error."** Refuted: there is no try block, so the exception propagates and nothing is granted.

## WHAT HOLDS UP
- The owner check in `share()` is correct and placed before the write.
- The owner short-circuit in `can_view` is correct.
- `PermissionService` keeps a clean separation from the backend.

## UNVERIFIED CLAIMS
- The docstring "Only the owner may add a viewer" holds for this method. Whether the backend's `add_viewer` can be reached by another path was not checked, because the routes were not supplied.
- There are no tests, so nothing shows the outage path was ever exercised. Confirm by writing the F1 repro test and seeing it fail.

## QUESTIONS FOR THE AUTHOR
1. Was link sharing a requirement? If not, why is it the default?
2. During a permissions outage, should viewing be denied or return 503? (It must not be allowed.)
3. What type does `backend.viewers()` return, and what does it do when the service is down?

## DECISION-MAKER SUMMARY
Do not launch: during any permissions-service outage, which the context says happens, every user can read every note (F1). Also fix the public-by-default link-sharing setting (F2) and add revocation (F3) before release. Proceeding as is risks a data breach of personal and business notes the first time the backend blips.

## OWNER SUMMARY
When the service that checks who may see a note is unavailable, the app currently lets everyone see every note instead of blocking access. New notes are also marked as viewable by anyone with the link, and there is no way to take back access once it is given. These need to be fixed before launch, because the notes hold private personal and business information.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "share.py", "status": "seen", "matters": true},
    {"item": "permissions backend client (viewers/add_viewer)", "status": "not_seen", "matters": true},
    {"item": "callers, routes, link-sharing handler", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Work is source code with no personal data or credentials; deployed data is sensitive, which raises stakes but not the gate."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "share.py", "kind": "file"},
      {"unit": "share.py:PermissionService.__init__", "kind": "function"},
      {"unit": "share.py:PermissionService.can_view", "kind": "function"},
      {"unit": "share.py:PermissionService.share", "kind": "function"},
      {"unit": "share.py:new_document", "kind": "function"},
      {"unit": "share.py:DEFAULTS", "kind": "config"}
    ],
    "not_checked": [
      {"unit": "permissions backend client", "reason": "not_supplied"},
      {"unit": "callers and routes", "reason": "not_supplied"},
      {"unit": "tests", "reason": "not_supplied"},
      {"unit": "execution of any reproduction", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "share.py:12-15",
     "scenario": "When the permissions backend is down (or any exception occurs, including TypeError/KeyError), can_view returns True, so any authenticated user can read any document's notes.",
     "fix": "Fail closed: catch only the backend's transport error and return False or raise PermissionUnavailable (mapped to 503); never grant on error.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Backend whose viewers() raises ConnectionError; assert PermissionService(backend).can_view('mallory', {'id': 1, 'owner': 'alice'}) is False; current code returns True.",
     "security": true,
     "boundary": {"principal": "any authenticated user not on the viewer list", "input": "a request to view any document id", "control": "viewer check bypassed by except Exception: return True", "crossed": "non-viewer to viewer", "resource": "every document's notes"},
     "siblings_searched": {"searched": "all except blocks and all return-True paths in share.py", "found": "none other; owner branch at line 10-11 is correct; share() has no try and fails closed"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "share.py:2, share.py:25",
     "scenario": "Every new document is stored with sharing='anyone_with_link', which was not requested and which can_view ignores; any consumer honouring the field exposes unshared documents publicly.",
     "fix": "Remove link sharing or default to 'private' and enforce it in can_view; migrate existing records.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "d = new_document('alice', 't', 1); assert d['sharing'] != 'anyone_with_link'; fails on current code.",
     "security": false,
     "siblings_searched": {"searched": "all reads and writes of DEFAULTS and doc['sharing'] in share.py", "found": "only new_document writes it; nothing reads it"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "share.py:17-21",
     "scenario": "An owner who shares by mistake cannot revoke access through the permission layer; exposure persists.",
     "fix": "Add unshare(actor, doc, other) with the same owner check, plus a test.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "assert hasattr(PermissionService, 'unshare'); fails on current code."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "share.py:2",
     "scenario": "If any module honours DEFAULTS, production runs with debug and telemetry on for personal data without consent.",
     "fix": "Default debug and telemetry to False; enable per environment, or delete if unused.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "from share import DEFAULTS; assert DEFAULTS['debug'] is False and DEFAULTS['telemetry'] is False; fails on current code."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "share.py:13",
     "suspicion": "If viewers() returns a string, 'in' does substring matching and grants near-match usernames.",
     "unresolved_fact": "The return type of backend.viewers()."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "share.py:25",
     "suspicion": "A link handler may already honour sharing='anyone_with_link', making every new document public.",
     "unresolved_fact": "Whether any route, export or indexer reads doc['sharing']."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "share.py:10",
     "suspicion": "Anonymous user represented as None matches a document created with owner None.",
     "unresolved_fact": "How the auth layer represents unauthenticated users and whether new_document can receive owner=None."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "share() lets non-owners add viewers.", "evidence": "share.py:19-20 raises PermissionError before add_viewer when actor != owner."},
    {"id": "C2", "candidate": "share() fails open on backend error.", "evidence": "share.py:21 has no try block; the exception propagates and nothing is granted."}
  ]
}
```