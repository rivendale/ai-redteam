**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** I had no tools and no subagent, so nothing below was executed. Every result comes from reading the code and tracing how `os.path.join` and `os.path.realpath` behave.

VERDICT: **REWORK**. Two of the three handlers let a request read any file the server process can read, including server files next to the docs directory.
CONFIDENCE: **medium**. The two path-traversal findings are certain from the code. Confidence is limited by having no tools, no routing or HTTP layer, no tests and no second reviewer.

INPUTS LEDGER:
- **Seen:** the original request (request.md), the context (context.md) and `downloads.py`, which is 35 lines.
- **Not seen:** the web or routing layer that calls these functions.
  - **Does it matter?** Yes, for two questions: whether a rider can only get their own receipt, and how `ValueError`, `FileNotFoundError` and `IsADirectoryError` become HTTP responses. It does **not** affect F1 or F2, because the request says the name comes straight from the request.
- **Not seen:** tests. None exist, as context.md says.
  - **Does it matter?** Yes. Nothing guards against traversal regressions.
- **Not seen:** the deployed value of `PEDALO_DOCS` and the directory layout.
  - **Does it matter?** Only a little. Context already says the docs directory sits beside other server files.

COVERAGE:
- **Checked:**
  - `downloads.py` as a whole, plus `_inside`, `receipt`, `manual` and `station_map`.
  - Hostile names traced through each function: `../`, an absolute path, empty, `.`, a sibling-prefix name, a symlink, a directory, and a null byte.
- **Not checked:** the routing layer, authorization, the deployment config, behavior under load, and anything at runtime.

SEATS AND GATE:
- **Seats:** only a local same-context reviewer ran. No subagent was available, and no cross-vendor seats ran because the depth is standard and no seats were requested.
- **Sensitivity gate:** passed. The work is code with no personal data in it, although the receipts it serves are likely to contain personal data.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (traced) | B | `downloads.py:17-20` `receipt` | The file name from the request is passed to `os.path.join` and `open` without any containment check. `_inside` exists in the same file but is not used here. | **Absolute path:** `receipt("/etc/passwd")` opens `/etc/passwd`, because `os.path.join` throws away earlier parts when a later part is absolute. **Relative path:** `receipt("../../app/settings.py")` resolves to `/srv/pedalo/app/settings.py`, which exposes the server files beside the docs directory. | **Fix:** `open(_inside("receipts", name), "rb")`. **Failing test:** set `downloads.DOCS = tmp_path/"docs"`, create `docs/receipts/`, write `docs/secret.txt`, then assert `pytest.raises(ValueError)` around `downloads.receipt("../secret.txt")`. On the current code this returns the bytes, so the test fails. Add the same test for `"/etc/hostname"`. | y/y/y/y |
| F2 | Critical | CONFIRMED (traced) | B | `downloads.py:23-26` `manual` | Same defect as F1. | `manual("../../../../etc/shadow")` or `manual("/srv/pedalo/.env")` reads outside `docs/manuals`. | **Fix:** `open(_inside("manuals", name), "rb")`. **Failing test:** the F1 test with `manuals`. | y/y/y/y |
| F3 | Medium | CONFIRMED | B | Whole module; context.md says "No tests were supplied" | There are no tests. In particular, no test makes F1 or F2 fail, and no test proves `_inside` rejects anything. | The fix for F1 and F2 can be undone silently later, for example by someone "simplifying" back to `os.path.join`. | **Fix:** add traversal tests for all three handlers covering `../x`, an absolute path, `""`, `.` and a symlink out of the folder. **Mutation check:** confirm the tests fail when `_inside` is replaced with a plain join. | y/y/n/n |
| F4 | Low | CONFIRMED (traced) | B | `downloads.py:8-14`, `30-32` | Expected failures leak as unhandled exceptions. `_inside` raises a bare `ValueError`. A missing file raises `FileNotFoundError`, and `station_map("sub")` on a subfolder raises `IsADirectoryError`. | The caller is not shown. If it does not map these errors, a probing request gets a 500, possibly with a traceback that reveals paths, instead of a 404. | Map all three errors to 404 in the handler, and test that a missing name returns 404. | y/y/n/n |

## NEEDS VALIDATION
- **S1, receipt ownership:** `receipt(name)` takes no rider identity. If names are guessable, as `2026-09-r1.pdf` suggests, any rider could download another rider's receipt, which is personal data. **Unresolved fact:** does the calling route check that the requesting rider owns that receipt? The routing layer was not supplied.
- **S2, symlink race:** there is a gap between `realpath` and `open` in `_inside`. If someone can write into `docs/maps`, they could swap a symlink in that window. **Unresolved fact:** can anyone other than the deployer write to the docs folders?

## REFUTED
- **"`_inside` can be bypassed by a sibling folder such as `maps2/`."** Refuted: the check is `startswith(base + os.sep)`, not `startswith(base)`, so `/srv/pedalo/docs/maps2/x` is rejected.
- **"`station_map` with an absolute name escapes the folder."** Refuted: `os.path.join(base, "/etc/passwd")` gives `/etc/passwd`, which fails the prefix check and is rejected.
- **"`station_map` can escape through a symlink inside `maps`."** Refuted: `realpath` resolves the link before the check, so a link pointing outside is rejected. The race in S2 is a separate question.
- **"An empty name or `.` returns the folder."** Refuted: both resolve to `base`, which does not start with `base + os.sep`, so they raise `ValueError`.

## WHAT HOLDS UP
- `_inside` is a correct containment check. It resolves both the base and the target with `realpath`, compares against the base plus a separator, and handles absolute names, `..`, symlinks and the sibling-prefix case.
- `station_map` uses `_inside` and is safe against traversal.
- The three handlers match the request in scope, with nothing extra.

## UNVERIFIED CLAIMS
- The module docstring says "Names come from the request." That confirms the names are attacker-controlled. It does not say how the route passes or decodes them, for example whether `%2F` is URL-decoded first. That cannot change F1 or F2, but checking the router would confirm it.
- `_inside`'s docstring says it refuses "any name that resolves outside that folder". This holds by trace, apart from the race in S2. Confirm it with the tests in F3.

## QUESTIONS FOR THE AUTHOR
1. Does the receipt route check that the requesting rider owns the receipt? This settles S1.
2. Was skipping `_inside` in `receipt` and `manual` deliberate, for example because of trust in an upstream filter? If so, where is that filter? Without it, F1 and F2 stand.

## DECISION-MAKER SUMMARY
Do not deploy this as written. The receipt and manual downloads let any requester read arbitrary files on the server, including the server files next to the docs directory. The fix is two lines: route both handlers through the existing `_inside` check, as the map handler already does. Add traversal tests, and confirm separately that riders can only fetch their own receipts.

## OWNER SUMMARY
Two of the three new download features can be tricked into handing out any file on the server, including private configuration, not just the documents they are meant to serve. The third feature already has the right protection, and the same protection can be applied to the other two with a very small change. It is also worth confirming that riders can only download their own receipts before this goes live.

The JSON below follows schema 2.2, but I could not run `tools/validate_findings.py` against it in this session.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "downloads.py", "status": "seen", "matters": true},
    {"item": "routing/HTTP layer calling the handlers", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true},
    {"item": "deployed PEDALO_DOCS value and directory layout", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Code only; no personal data in the work itself."},
  "coverage": {
    "checked": [
      {"unit": "downloads.py", "kind": "file"},
      {"unit": "downloads.py:_inside", "kind": "function"},
      {"unit": "downloads.py:receipt", "kind": "function"},
      {"unit": "downloads.py:manual", "kind": "function"},
      {"unit": "downloads.py:station_map", "kind": "function"}
    ],
    "not_checked": [
      {"unit": "routing/HTTP layer", "reason": "not supplied"},
      {"unit": "runtime behavior", "reason": "no tools in this session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "downloads.py:17-20 (receipt)",
     "scenario": "receipt('/etc/passwd') or receipt('../../app/settings.py') opens files outside docs/receipts because the request-supplied name is joined without a containment check; os.path.join discards DOCS for an absolute name.",
     "fix": "open(_inside('receipts', name), 'rb').",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "With downloads.DOCS=tmp/docs, docs/receipts/ and docs/secret.txt present, call receipt('../secret.txt'); expect ValueError, observe the file's bytes."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "downloads.py:23-26 (manual)",
     "scenario": "manual('/srv/pedalo/.env') or manual('../../../../etc/shadow') reads outside docs/manuals.",
     "fix": "open(_inside('manuals', name), 'rb').",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "As F1 with docs/manuals/ and manual('../secret.txt'); expect ValueError, observe the file's bytes."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "downloads.py (module); context.md 'No tests were supplied'",
     "scenario": "No test guards containment, so F1/F2 shipped and a later refactor can remove _inside unnoticed.",
     "fix": "Add traversal tests (../x, absolute path, '', '.', symlink out) for all three handlers; confirm they fail when _inside is replaced by a plain join.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Replace _inside body with return os.path.join(DOCS, folder, name); no test fails today because none exist."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "downloads.py:8-14, 30-32",
     "scenario": "A rejected, missing, or directory name raises ValueError/FileNotFoundError/IsADirectoryError; if the unseen caller does not map them, the client gets a 500, possibly with a path-revealing traceback.",
     "fix": "Map these exceptions to 404 in the handler.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Call station_map('nope.png'); observe FileNotFoundError propagates; expect a handled not-found result."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "downloads.py:17-20",
     "suspicion": "Any rider may fetch another rider's receipt by guessing its name.",
     "unresolved_fact": "Whether the calling route checks receipt ownership (routing layer not supplied)."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "downloads.py:10-14, 31",
     "suspicion": "Symlink swap between realpath and open (TOCTOU) could escape the maps folder.",
     "unresolved_fact": "Whether anyone other than the deployer can write to the docs folders."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "_inside bypassable via sibling folder like maps2/.",
     "evidence": "Check is startswith(base + os.sep), not startswith(base)."},
    {"id": "R2", "candidate": "station_map with an absolute name escapes.",
     "evidence": "join yields the absolute path, which fails the prefix check and raises ValueError."},
    {"id": "R3", "candidate": "station_map escapes via a symlink inside maps.",
     "evidence": "realpath resolves the link before the prefix check."},
    {"id": "R4", "candidate": "Empty name or '.' returns the folder.",
     "evidence": "Both resolve to base, which does not start with base + os.sep."}
  ]
}
```