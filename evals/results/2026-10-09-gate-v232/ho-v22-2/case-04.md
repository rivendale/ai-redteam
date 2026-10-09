**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** I had no tools in this session, so nothing was executed. Every code trace below is by reading only.

---

**VERDICT: SHIP WITH FIXES.** The containment check in `_inside` holds against every escape I traced, but the tests only guard one traversal shape, and receipt ownership is unresolved.

**CONFIDENCE: medium.** Limits: no tools (tests not run, no mutation run), same-context review, and the routing/auth layer that calls these handlers was not supplied.

**INPUTS LEDGER**
- **Seen:** `request.md`, `context.md`, `downloads.py`, `test_downloads.py`.
- **Not seen:** the web routing layer that calls `receipt`, `manual` and `station_map`. It **matters**: it decides who may call `receipt`, how the name is URL-decoded, and how `ValueError` or `FileNotFoundError` become HTTP responses.
- **Not seen:** the test run output behind "2 tests pass". It matters a little; the claim is unverified.
- **Not seen:** the deployed `PEDALO_DOCS` value and the folder layout. This is minor.

**COVERAGE**
- **Checked:**
  - `downloads.py`: `_inside`, `receipt`, `manual`, `station_map`
  - `test_downloads.py`: `setUp`, both tests
  - the assumption "realpath plus `startswith(base + sep)` contains the path"
- **Not checked:** the routing/auth layer, deployment config, and whether anything writes into the docs folders.

**SEATS AND GATE:** I reviewed in this same context. No subagent or cross-vendor seats were available because I had no tools. The work contains no personal data, so the gate passed. Note that the receipts the code serves are personal financial records.

### Pass 1: Reconstruct
Three handlers each resolve a request-supplied name against `DOCS/<folder>` and read the file. `_inside` refuses any name whose fully resolved path is not strictly under the resolved folder. For this to be correct:
- `realpath` must resolve `..`, absolute paths and symlinks before the prefix check.
- The `+ os.sep` must block sibling-prefix folders.
- The caller must not grant access the request didn't intend.

Unstated assumption: any caller may fetch any receipt by name. Tracks: **B**, with a touch of **R** for the receipts.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | PROBABLE | B | `test_downloads.py:test_traversal_is_refused_by_every_handler` | The only escape tested is `"../secret.txt"`. Weaker checks would still pass. | Someone later "simplifies" `_inside` to `if ".." in name: raise`, or to `startswith(base)` without `os.sep`, or swaps `realpath` for `abspath`. Both tests stay green, but `receipt("/srv/pedalo/server.env")`, a symlink in `maps/` pointing outside, or `"../receipts-old/x.pdf"` (a sibling-prefix folder) would then leak files. | Add refusal tests for: an absolute path to `tmp/secret.txt`; a symlink inside `maps/` pointing to `tmp/secret.txt`; a sibling folder `receiptsX/` reached via `"../receiptsX/a.txt"`. Repro: apply each weakened mutation in a scratch copy and confirm the current suite stays green while the new tests go red. | a✔ b✘ c✘ d✘ |
| F2 | Low | CONFIRMED | B | `test_downloads.py:setUp` | `downloads.DOCS` is reassigned globally and never restored. The temp dirs are never removed, and files are opened without being closed. | Any other test module importing `downloads` in the same run sees the last temp dir as `DOCS`. Temp dirs also pile up on CI. | Use `addCleanup` to restore `DOCS` and to `shutil.rmtree` the tmp dir. Use `with open(...)` for the writes. | a✔ b✔ c✘ d✘ |

### NEEDS VALIDATION
- **S1, receipt ownership.** `receipt(name)` returns any rider's receipt to whoever supplies the name, and the docstring example `2026-09-r1.pdf` looks sequential and guessable. If the caller does not check that the receipt belongs to the logged-in rider, this is an enumerable leak of customer financial data, which would be Critical. *Fact that settles it:* does the route for `receipt` enforce ownership, or are receipt names unguessable per-rider tokens? The request did not ask for ownership checks, so this may be a gap in the request rather than in the code.
- **S2, error mapping.** Refusals raise `ValueError`. Missing files raise `FileNotFoundError`, and a directory name raises `IsADirectoryError`. *Fact:* does the caller map these to 403/404, or does it return 500 with a traceback that exposes `/srv/pedalo/...` paths?
- **S3, TOCTOU.** There is a gap between `realpath` and `open`. A symlink swapped in during that window would escape the folder. *Fact:* can any process or user write into `receipts/`, `manuals/` or `maps/`? If nothing writes there, this is moot.
- **S4, "2 tests pass".** *Fact:* the output of `python -m unittest test_downloads`.

### REFUTED
- **Sibling-prefix bypass** (`/docs/receipts-evil`): refuted. The check uses `base + os.sep`, so `receipts-evil/...` does not match `receipts/`.
- **Absolute-path name** (`"/etc/passwd"`): refuted. `os.path.join(base, "/etc/passwd")` discards `base`, and `realpath` yields `/etc/passwd`, which fails the prefix check, so it is refused.
- **Symlink inside the folder pointing outside:** refuted. `realpath` resolves the link target before the check.
- **Empty name, `"."`, or `"receipts/.."`:** refuted. These resolve to `base` or above it, and `base` does not start with `base + sep`, so they are refused.
- **Null byte in name:** refuted. Python raises `ValueError` in `lstat` or `open` before any read.
- **Test override not taking effect:** refuted. `_inside` reads the module global `DOCS` at call time, so the `setUp` assignment applies.
- **Traversal test can never fail:** refuted by trace. With the check removed, `"../secret.txt"` reads the file and `assertRaises` fails, so the test does go red for that mutation. It does not run, which is why F1 stands.

### WHAT HOLDS UP
- The core containment logic is right. It uses `realpath` on both the base and the target, then a strict prefix check with a separator. That is the standard correct pattern.
- All three handlers share one guard, so there is no path that skips the check.
- Files are opened read-only in binary mode with context managers.
- The scope matches the request exactly: three handlers, nothing extra.

### UNVERIFIED CLAIMS
- "2 tests in test_downloads.py pass." Confirm by running the suite.
- That the tests catch regressions. Confirm with the F1 mutation runs.

### QUESTIONS FOR THE AUTHOR
1. Does the route serving `receipt` check that the receipt belongs to the requesting rider? (Settles S1. A "no" changes the verdict to REWORK.)
2. How are `ValueError` and `FileNotFoundError` turned into HTTP responses?
3. Does anything write into the docs folders at runtime?

### DECISION-MAKER SUMMARY
The path-traversal guard is correct, and I found no way to read files outside the three folders. Before production, confirm that riders can only fetch their own receipts (S1), and add the three extra traversal tests (F1). Shipping without the S1 answer risks exposing every rider's receipts to anyone who guesses file names.

### OWNER SUMMARY
The new download code correctly stops people from reaching other files on the server. Before it goes live, someone should confirm that riders can only download their own receipts, not other riders'. The tests should also be extended so a future change can't quietly weaken the protection.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "downloads.py", "status": "seen", "matters": true},
    {"item": "test_downloads.py", "status": "seen", "matters": true},
    {"item": "routing/auth layer calling the handlers", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Work contains no personal data; it serves receipts at runtime (see S1)."},
  "coverage": {
    "checked": [
      {"unit": "downloads.py", "kind": "file"},
      {"unit": "downloads.py:_inside", "kind": "function"},
      {"unit": "downloads.py:receipt", "kind": "function"},
      {"unit": "downloads.py:manual", "kind": "function"},
      {"unit": "downloads.py:station_map", "kind": "function"},
      {"unit": "test_downloads.py", "kind": "file"},
      {"unit": "realpath + startswith(base + os.sep) contains the path", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "routing/auth layer", "reason": "not supplied"},
      {"unit": "PEDALO_DOCS deployment config", "reason": "not supplied"},
      {"unit": "test execution and mutation runs", "reason": "no tools in this session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "test_downloads.py:test_traversal_is_refused_by_every_handler",
     "scenario": "_inside is later weakened to an '..'-substring check or a startswith without os.sep; both tests stay green while absolute paths, outward symlinks or sibling-prefix folders leak files.",
     "fix": "Add refusal tests for an absolute path, a symlink inside a folder pointing outside, and a sibling folder reached via '../receiptsX/a.txt'.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "In a scratch copy, replace the check with `if '..' in name: raise ValueError`; run the suite: expect red, observe green. Then add the new tests: they go red."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_downloads.py:setUp",
     "scenario": "downloads.DOCS is overwritten globally and never restored, and temp dirs are never removed; other test modules in the same run see a stale DOCS.",
     "fix": "Use addCleanup to restore DOCS and shutil.rmtree the temp dir; write fixtures with `with open(...)`.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Run a second test module that calls downloads.manual after T; observe it resolves against the leftover temp dir instead of PEDALO_DOCS."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "downloads.py:receipt",
     "suspicion": "Any caller can fetch any rider's receipt by a guessable name (e.g. 2026-09-r1.pdf).",
     "unresolved_fact": "Whether the route serving receipt enforces rider ownership or uses unguessable per-rider names."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "downloads.py:_inside",
     "suspicion": "ValueError/FileNotFoundError/IsADirectoryError may surface as 500 with server paths in the response.",
     "unresolved_fact": "How the caller maps these exceptions to HTTP responses."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "downloads.py:_inside and handlers",
     "suspicion": "A symlink swapped in between realpath and open would escape the folder.",
     "unresolved_fact": "Whether any process or user can write into receipts/, manuals/ or maps/ at runtime."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "context.md",
     "suspicion": "The claim that 2 tests pass is unverified.",
     "unresolved_fact": "Output of `python -m unittest test_downloads`."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Sibling-prefix folder bypass (receipts-evil).", "evidence": "The check is startswith(base + os.sep), not startswith(base)."},
    {"id": "C2", "candidate": "Absolute-path name escapes the folder.", "evidence": "os.path.join discards base; realpath('/etc/passwd') fails the prefix check and is refused."},
    {"id": "C3", "candidate": "Symlink in a folder pointing outside.", "evidence": "realpath resolves the target before the check."},
    {"id": "C4", "candidate": "Empty name or '.' returns the folder itself.", "evidence": "It resolves to base, which does not start with base + os.sep, so it is refused."},
    {"id": "C5", "candidate": "Null byte truncates the path.", "evidence": "Python raises ValueError on embedded null bytes before any read."},
    {"id": "C6", "candidate": "Test override of DOCS has no effect.", "evidence": "_inside reads the module global DOCS at call time."}
  ]
}
```