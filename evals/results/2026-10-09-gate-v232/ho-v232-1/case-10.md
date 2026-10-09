**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available, so nothing was executed or hashed.

VERDICT: **SHIP WITH FIXES.** The loader parses plain JSON, reads the file once, hashes those same bytes and refuses on mismatch, so it fails closed. The confirmed findings are Low robustness and test-fragility issues. The one open question that matters is the pinned digest, which could not be recomputed here.

CONFIDENCE: **medium.** Three things limit it:
- This is a same-context review.
- With no tools, the SHA-256 in `models.lock` and the claim that "4 tests pass" could not be checked.
- The rebalancing job that calls `load_model` was not supplied.

INPUTS LEDGER:
- **Seen:**
  - request.md
  - context.md
  - `forecast.py`
  - `models.lock`
  - `demand-2026-09.json`
  - `test_forecast.py`
- **Not seen:**
  - **The rebalancing job that calls `load_model` and `predict`.** This matters. How it picks `path`, and whether it catches the exception and falls back to an unpinned model, decides whether the pin protects anything.
  - **Test run output.** This matters somewhat. The context asserts the tests pass, but no output was supplied.
  - **The exact bytes of `demand-2026-09.json`, including any trailing newline.** This matters for the digest only.

COVERAGE:
- **Scope:** the whole work (four files).
- **Checked:**
  - `forecast.py`: `pinned`, `load_model` and `predict`, plus the module constant `LOCK`
  - `models.lock`
  - `demand-2026-09.json`
  - `test_forecast.py`: all four tests
  - request.md
  - context.md
  - Assumptions:
    - JSON parsing cannot execute code.
    - The pin is meaningful while it lives in the same repository.
    - The hash and the parse use the same bytes.
- **Not checked:**
  - **The calling job:** not supplied.
  - **The digest recomputation:** no tools.
  - **A scan for invisible or look-alike characters:** no tools. Visually the files are clean.
  - **Running the tests, including mutation checks:** no tools.

SEATS AND GATE: one seat ran (same-context Claude). Cross-vendor seats were not requested and depth is standard. Sensitivity gate: not sensitive. The work contains no credentials or personal data. The ops server holds credentials, but none appear in the work.

FINDINGS, ordered by severity:

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | CONFIRMED (traced) | B | `forecast.py` `pinned`, line `file_name, digest = line.split()` | A blank line, comment line or extra field in `models.lock` raises an unpacking `ValueError`. This happens before any later entries are reached. | Someone adds a second model with a blank separator line or a `# comment`. Every load then raises `ValueError: not enough values to unpack`. That error has the same type as "hash mismatch", and the job refuses to start with a misleading cause. It fails closed, so there is no security impact. | **Fix:** skip blank lines and lines starting with `#`, and raise a distinct error naming the line number on any other malformed line. **Reproduction (not run):** write a lock of `"\n" + "demand-2026-09.json <digest>\n"` and call `load_model(MODEL, lock=that_file)`. Expected: the model loads. Observed by trace: `ValueError` from unpacking. | a✔ b✔ c✘ d✘ |
| F2 | Low | CONFIRMED (traced) | B | `forecast.py` `load_model` (`raise ValueError`), and `test_forecast.py` `test_a_changed_copy_is_refused` | Three causes all raise `ValueError`: a hash mismatch, a malformed lock line (F1), and invalid JSON (`json.JSONDecodeError` is a `ValueError` subclass). The tamper test only catches the hash check being removed because its mutation (an appended space) happens to remain valid JSON. | Someone later changes the mutation to append non-JSON bytes. The test then stays green even if the hash comparison is deleted, so a removed integrity check goes unnoticed. | **Fix:** raise a dedicated exception (for example `class ModelHashMismatch(ValueError)`) and assert that type in the test. **Reproduction (not run):** in a scratch copy, delete the `if hashlib...` check and change `b" "` to `b"x"`. Observed by trace: the test still passes. With the current `b" "`, it correctly goes red. | a✔ b✔ c✘ d✘ |
| F3 | Low | CONFIRMED (traced) | B | `forecast.py` `pinned` (`open(lock)`) and `load_model` (`open(path, "rb").read()`) | Files are opened without `with`, so handles close only when garbage collection runs. | On CPython, reference counting closes them promptly. On other runtimes, or when `-W error::ResourceWarning` is set in CI, this produces warnings or leaked handles in a long-running job. | **Fix:** use `with open(...) as f`. **Reproduction (not run):** `python -W error::ResourceWarning -m unittest test_forecast`. Expected: clean. Possible observed result: a ResourceWarning, depending on the runtime. | a✔ b✔ c✘ d✘ |

NEEDS VALIDATION:
- **S1: does the pinned digest match the shipped file?** This is settled by whether `sha256sum demand-2026-09.json` equals `3fd1600a43716901991c857198c9fb11ee05cfb20aa983f6888a74634424e882`. A trailing newline changes the digest. If it does not match, the job fails closed at startup, which is not a security issue.
- **S2: does the caller fail closed?** This is settled by whether the rebalancing job catches `ValueError` or `KeyError` from `load_model` and then loads a model some other way (for example `json.load` on a "latest" file). It is also settled by whether `path` can be influenced by anything outside the deploy. This is the main residual risk, and the caller was not supplied.
- **S3: do the four tests actually pass?** This is settled by the actual `python -m unittest test_forecast` output from the ops-server environment.
- **S4: are there invisible or look-alike characters?** This is settled by a byte-level scan of all four files for zero-width, bidirectional and tag characters, and for non-ASCII letters in identifiers or the digest.

REFUTED:
- **"Loading the model can execute code."** Refuted. Loading is `json.loads` on bytes. There is no pickle, `eval` or import.
- **"Time-of-check to time-of-use gap between the hash check and the parse."** Refuted. `raw` is read once, and those same bytes are both hashed and parsed.
- **"Looking up by basename lets a file in another directory get through."** Refuted. Lookup is by name, but the comparison is on the contents' hash. A file elsewhere passes only if its bytes are identical to the pinned ones.
- **"A pin stored in the same repository is worthless."** Refuted for this threat. Anyone who can edit `models.lock` can also edit `forecast.py`. The pin still protects against a model file being swapped or corrupted on the server independently of the code.
- **"A missing or empty lock file fails open."** Refuted. A missing lock raises `FileNotFoundError` and an empty one raises `KeyError`. Both fail closed.

WHAT HOLDS UP:
- The integrity check rejects on any byte change and on any name not in the lock.
- The lock location is anchored to the module's own directory rather than the working directory.
- Exceptions propagate instead of being swallowed.
- The model format is data only.
- Tests 2 and 3 do discriminate. Removing the hash check turns test 2 red, and removing the lock lookup turns test 3 red.
- `predict` handles hours of 24 and above, and negative hours, through `% 24`.
- The code stays within the request. `predict` is a small addition beyond "load the model".

UNVERIFIED CLAIMS:
- **"4 tests pass".** Confirm by running them (S3).
- **The digest in `models.lock` matches the file.** Confirm with `sha256sum` (S1).
- **The docstring claim "never code".** This is true of this loader, but depends on the caller not using another loader (S2).

QUESTIONS FOR THE AUTHOR:
1. How does the rebalancing job choose `path`? What does it do when `load_model` raises?
2. Can you paste the `sha256sum` and test output from the ops server?

DECISION-MAKER SUMMARY: The loader is sound and fails closed. Ship it after fixing the lock parsing and tightening the tamper test's exception type, both small. Before it runs on the ops server, confirm the digest and confirm that the calling job never falls back to an unchecked model. That unseen caller is the only place a real bypass could hide.

OWNER SUMMARY: The code that loads the forecast file checks it against a recorded fingerprint and refuses to run if the file was changed, which is the right behavior. A few small robustness fixes are worth making. Before relying on it, someone should confirm the fingerprint matches the real file and that the job using this code doesn't quietly skip the check when it fails.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "forecast.py", "status": "seen", "matters": true},
    {"item": "models.lock", "status": "seen", "matters": true},
    {"item": "demand-2026-09.json", "status": "seen", "matters": true},
    {"item": "test_forecast.py", "status": "seen", "matters": true},
    {"item": "rebalancing job that calls load_model", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No credentials or personal data in the work; the server's credentials are not included."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "forecast.py", "kind": "file"},
      {"unit": "forecast.py:pinned", "kind": "function"},
      {"unit": "forecast.py:load_model", "kind": "function"},
      {"unit": "forecast.py:predict", "kind": "function"},
      {"unit": "models.lock", "kind": "config"},
      {"unit": "demand-2026-09.json", "kind": "data"},
      {"unit": "test_forecast.py", "kind": "file"},
      {"unit": "pin in same repository is meaningful", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "rebalancing job caller", "reason": "not_supplied"},
      {"unit": "SHA-256 recomputation of demand-2026-09.json", "reason": "no_tools"},
      {"unit": "test execution and mutation runs", "reason": "no_tools"},
      {"unit": "invisible-character byte scan", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "forecast.py:pinned, `file_name, digest = line.split()`",
     "scenario": "A blank or comment line in models.lock raises an unpacking ValueError before later entries are read, so every load fails with an error indistinguishable from a hash mismatch (fails closed).",
     "fix": "Skip blank and '#' lines; raise a distinct error with the line number for other malformed lines.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Lock file '\\n' + 'demand-2026-09.json <digest>\\n'; call load_model(MODEL, lock=that_file); expect a loaded model, observe ValueError (traced, not run)."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "forecast.py:load_model raise ValueError; test_forecast.py:test_a_changed_copy_is_refused",
     "scenario": "Hash mismatch, malformed lock and JSONDecodeError all raise ValueError; if the test mutation becomes invalid JSON, the test stays green with the hash check deleted.",
     "fix": "Raise a dedicated ModelHashMismatch(ValueError) and assert that type in the test.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "In a scratch copy, delete the hash check and change b' ' to b'x'; the test still passes (traced, not run)."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "forecast.py:pinned open(lock); forecast.py:load_model open(path, 'rb')",
     "scenario": "File handles are not closed deterministically; on non-CPython runtimes or with ResourceWarning as an error, a long-running job leaks handles or CI fails.",
     "fix": "Use `with open(...) as f`.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "python -W error::ResourceWarning -m unittest test_forecast; may raise ResourceWarning depending on runtime (not run)."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "models.lock:1",
     "suspicion": "The pinned digest may not match the shipped file bytes.",
     "unresolved_fact": "Output of sha256sum demand-2026-09.json compared with 3fd1600a...e882."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "rebalancing job caller (not supplied)",
     "suspicion": "The caller may catch the load error and fall back to an unpinned model, or take path from untrusted input.",
     "unresolved_fact": "The caller's exception handling and the source of `path`."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "context.md: 'Tests: 4 tests in test_forecast.py pass.'",
     "suspicion": "The claim that the tests pass is asserted, not evidenced.",
     "unresolved_fact": "Actual unittest output from the ops-server environment."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "all four files",
     "suspicion": "Invisible or look-alike characters could not be scanned for.",
     "unresolved_fact": "A byte-level scan for zero-width, bidi, tag and non-ASCII identifier characters."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Model loading can execute code.", "evidence": "load_model uses json.loads on bytes; no pickle, eval or import."},
    {"id": "C2", "candidate": "Time-of-check to time-of-use gap between hash and parse.", "evidence": "raw is read once and the same bytes are hashed and parsed."},
    {"id": "C3", "candidate": "Basename lookup allows substituting a file from another directory.", "evidence": "The comparison is on the content hash; only identical bytes pass."},
    {"id": "C4", "candidate": "A pin in the same repository is worthless.", "evidence": "Editing the lock requires the same access as editing forecast.py; the pin still catches a model swapped on the server independently."},
    {"id": "C5", "candidate": "A missing or empty lock fails open.", "evidence": "open() raises FileNotFoundError; an empty lock raises KeyError; both fail closed."}
  ]
}
```