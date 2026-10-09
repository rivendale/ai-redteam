**Review mode:** single reviewer, no tools, no subagent available. Nothing was executed. Every finding below comes from tracing the supplied source line by line. The work was not written in this conversation, but you should still re-run this review in a fresh session with tools before production.

VERDICT: **REWORK**. `receipt` and `manual` pass the request's file name straight into `open()`, so a caller can read any file the server process can read, including the server files that sit beside the docs directory.

CONFIDENCE: **medium**. The two traversal findings rest on deterministic `os.path.join` behaviour traced at exact lines, but they were not run. The routing layer and any authorization were not supplied.

INPUTS LEDGER:
- **Seen:** `request.md`, `context.md`, `downloads.py` (31 lines).
- **Not seen:** the HTTP routes or framework that call these functions. This matters for three things: whether names are URL-decoded or normalized before arriving, whether a rider is authorized for a given receipt, and how `ValueError` and `OSError` map to responses.
- **Not seen:** tests. Context says none exist, and that is itself a finding (F3).
- **Not seen:** the deployed value of `PEDALO_DOCS` and the layout under it. This matters little, because traversal works for any value.

COVERAGE:
- **Scope:** the whole work, `downloads.py`.
- **Checked:** `request.md`, `context.md`, `downloads.py`, `_inside`, `receipt`, `manual`, `station_map`, the `DOCS` config line, and the assumption that "names come from the request".
- **Not checked:** routing and handler layer (not supplied), deployed directory layout (not supplied), runtime behaviour (no tools).

SEATS AND GATE:
- **Gate:** passed. The code holds no personal data, credentials or confidential material.
- **Seats:** only this local reviewer ran. No subagent or cross-vendor seat was available in this session.

FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (traced) | B | downloads.py:18 | `receipt` joins an untrusted name with no containment check. `_inside` exists but is not used here. | A requester sends `name="../../app/settings.py"` and gets a server file from beside docs. They can also send an absolute name such as `"/etc/passwd"`: `os.path.join` discards the earlier parts when the last part is absolute, so `/etc/passwd` is opened directly. | **Fix:** `open(_inside("receipts", name), "rb")`. **Repro:** create a temp tree with `PEDALO_DOCS=/tmp/t/docs` and a file `/tmp/t/secret`. Call `receipt("../../secret")`. Expected `ValueError`; the trace shows it returns the secret's bytes. `receipt("/tmp/t/secret")` does the same. | y/y/y/y |
| F2 | Critical | CONFIRMED (traced) | B | downloads.py:24 | `manual` has the same unguarded join as F1. | The same `../` or absolute-path name read any server-readable file through the manuals handler. | **Fix:** `open(_inside("manuals", name), "rb")`. **Repro:** same temp tree, call `manual("../../secret")`. Expected `ValueError`; it returns the bytes. | y/y/y/y |
| F3 | Medium | CONFIRMED | B | downloads.py (whole file); context.md "No tests were supplied" | No test guards containment, so the one correct guard (line 30) can regress silently, and the two missing guards were never caught. | A refactor drops `_inside` from `station_map` and nothing fails. | **Fix:** add a parametrized test over all three functions that asserts `ValueError` for `../x`, `/etc/passwd`, `""` and a symlink pointing outside the folder. Then mutation-check it by removing `_inside` in a scratch copy and confirming the test goes red. **Repro:** that test fails today for `receipt` and `manual`. | y/y/n/n |

**Security boundary for F1 and F2:**
- **Principal:** any requester who can reach the download routes.
- **Input:** the `name` request parameter.
- **Failed control:** no containment check on lines 18 and 24.
- **Boundary crossed:** web request to the server filesystem.
- **Resource exposed:** any file readable by the server process, including the server files beside docs.

**Sibling search:** I checked every `open()` and `os.path.join` in `downloads.py` (lines 9, 10, 18, 24, 30). Lines 18 and 24 are vulnerable (F1, F2). Line 30 is guarded by `_inside`. There are no other sinks.

NEEDS VALIDATION:
- **Receipts are per-rider, but no ownership check is visible.** Names look enumerable (`2026-09-r1.pdf`), so one rider may be able to fetch another rider's receipt. What would settle it: whether the route layer checks that the receipt belongs to the authenticated rider.
- **Error mapping.** `ValueError` from `_inside`, and `FileNotFoundError` or `IsADirectoryError` (for example `manual("")` opens the folder itself), may surface as 500 errors with paths in the message. What would settle it: the handler's exception handling.
- **Whole-file reads.** `f.read()` loads each file fully into memory. What would settle it: the maximum file size in docs and the expected request concurrency.

REFUTED:
- **"`_inside` can be bypassed by a sibling folder sharing the prefix (`maps2`)."** Refuted: line 11 compares against `base + os.sep`, so `maps2/...` does not match `maps/`.
- **"`_inside` can be bypassed with an absolute name or a symlink."** Refuted: `realpath` on line 10 resolves both the join and any symlinks, then the prefix check rejects anything outside. An absolute name resolves outside `base` and is refused.
- **"An empty name in `station_map` returns the folder."** Refuted: `real == base`, which fails the `base + os.sep` prefix check, so it raises `ValueError`.

WHAT HOLDS UP:
- `_inside` is a sound containment check. It resolves symlinks before comparing, uses a separator-terminated prefix, and handles absolute names.
- `station_map` uses it correctly.
- All three handlers asked for in the request exist, with nothing extra.
- A residual symlink-swap race exists between the check and the `open()`, but exploiting it requires write access inside `maps/`.

UNVERIFIED CLAIMS:
- The module docstring says names "come from the request". How they are decoded is unconfirmed. The route code would confirm it.
- Nothing claims to be tested, and nothing was.

QUESTIONS FOR THE AUTHOR:
1. Was leaving `_inside` off `receipt` and `manual` intentional? If so, what protects them?
2. Where is it checked that a receipt belongs to the requesting rider?

DECISION-MAKER SUMMARY: Two of the three download handlers (F1, F2) let any requester read arbitrary server files via `../` or absolute names. That is a Critical exposure next to the server files the context warns about. The fix is two one-line changes to use the existing `_inside` guard, plus a traversal test (F3). Shipping as-is risks leaking configuration and secrets on day one.

OWNER SUMMARY: Two of the new download features let anyone ask for files outside the documents folder, including the site's own server files. The map download is already protected correctly, and the same protection needs to be applied to receipts and manuals, with a test that proves it. Please hold the release until that is done and someone confirms riders can only download their own receipts.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "downloads.py", "status": "seen", "matters": true},
    {"item": "HTTP routing / handler layer", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local-no-tools", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "downloads.py", "kind": "file"},
      {"unit": "downloads.py:_inside", "kind": "function"},
      {"unit": "downloads.py:receipt", "kind": "function"},
      {"unit": "downloads.py:manual", "kind": "function"},
      {"unit": "downloads.py:station_map", "kind": "function"},
      {"unit": "downloads.py:DOCS", "kind": "config"},
      {"unit": "names come from the request (untrusted)", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "HTTP routing / handler layer", "reason": "not_supplied"},
      {"unit": "deployed PEDALO_DOCS layout", "reason": "not_supplied"},
      {"unit": "runtime execution of reproductions", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "downloads.py:18",
     "scenario": "A requester calls receipt with name '../../app/settings.py' or '/etc/passwd'; os.path.join with no containment check opens and returns a file outside DOCS/receipts.",
     "fix": "Use open(_inside('receipts', name), 'rb').",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "With PEDALO_DOCS=/tmp/t/docs and /tmp/t/secret present, call receipt('../../secret'); expected ValueError, observed (by trace, not executed) the secret's bytes. receipt('/tmp/t/secret') behaves the same.",
     "security": true,
     "boundary": {"principal": "any requester reaching the receipt download route", "input": "the name request parameter",
                  "control": "no containment check before open()", "crossed": "web request to server filesystem",
                  "resource": "any file readable by the server process"},
     "siblings_searched": {"searched": "every open() and os.path.join in downloads.py (lines 9, 10, 18, 24, 30)",
                           "found": "line 24 (manual) has the same flaw, reported as F2; line 30 is guarded by _inside"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "downloads.py:24",
     "scenario": "A requester calls manual with a '../' or absolute name and receives an arbitrary server file.",
     "fix": "Use open(_inside('manuals', name), 'rb').",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "With PEDALO_DOCS=/tmp/t/docs and /tmp/t/secret present, call manual('../../secret'); expected ValueError, observed (by trace, not executed) the secret's bytes.",
     "security": true,
     "boundary": {"principal": "any requester reaching the manual download route", "input": "the name request parameter",
                  "control": "no containment check before open()", "crossed": "web request to server filesystem",
                  "resource": "any file readable by the server process"},
     "siblings_searched": {"searched": "every open() and os.path.join in downloads.py (lines 9, 10, 18, 24, 30)",
                           "found": "line 18 (receipt) has the same flaw, reported as F1; line 30 is guarded"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "downloads.py (no tests supplied; context.md)",
     "scenario": "With no traversal tests, F1 and F2 went unnoticed and removing _inside from station_map would also pass silently.",
     "fix": "Add a parametrized test over receipt, manual and station_map asserting ValueError for '../x', '/etc/passwd', '' and an outward symlink; mutation-check it by removing _inside in a scratch copy.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Write the test above; it fails today for receipt('../x') and manual('../x'), which return or attempt to open files outside their folder instead of raising ValueError."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "downloads.py:16-19",
     "suspicion": "Any rider may fetch another rider's receipt by guessing its enumerable name.",
     "unresolved_fact": "Whether the route layer checks receipt ownership against the authenticated rider (not supplied)."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "downloads.py:12,18,24,30",
     "suspicion": "ValueError, FileNotFoundError or IsADirectoryError may surface as 500s leaking filesystem paths.",
     "unresolved_fact": "How the handler layer maps these exceptions to responses (not supplied)."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "downloads.py:19,25,31",
     "suspicion": "f.read() loads whole files into memory and may exhaust memory under load.",
     "unresolved_fact": "Maximum file size under docs and expected concurrency."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "_inside is bypassable via a sibling folder sharing the prefix (maps2).",
     "evidence": "Line 11 compares against base + os.sep, so maps2/ does not match maps/."},
    {"id": "C2", "candidate": "_inside is bypassable with an absolute name or symlink.",
     "evidence": "Line 10 realpath resolves both before the prefix check, so out-of-folder targets are refused."},
    {"id": "C3", "candidate": "station_map('') returns the maps folder itself.",
     "evidence": "real == base fails startswith(base + os.sep), so ValueError is raised."}
  ]
}
```