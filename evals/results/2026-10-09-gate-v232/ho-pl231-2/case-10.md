# Adversarial Diagnostic Review: `forecast.py` (demand-forecast model loader)

## Pass 1: Reconstruct

The work is a small module that loads a JSON demand model for the dock rebalancing job. It refuses to load any file whose SHA-256 differs from the digest pinned for its basename in `models.lock`, which sits next to `forecast.py`. It also adds a `predict(model, hour)` helper. Four tests cover the shipped model, a tampered copy, an unpinned name, and hour wrapping.

For this to be correct and safe on a server holding fleet DB credentials and the dock control API key, these must be true:

- **(A1)** Loading the model cannot execute code.
- **(A2)** `models.lock` has the same or higher trust than the code. It is reviewed in the repo and not writable by whoever supplies model files.
- **(A3)** The pinned digest actually matches the shipped JSON.
- **(A4)** The bytes that are hashed are the bytes that are parsed.
- **(A5)** The lock file is always well-formed.
- **(A6, unstated)** The caller passes the right model path and an integer hour in the right time zone.

## Pass 2: Attack (Track B, with a security focus)

**Code execution / deserialization (A1).**
- `load_model` uses only `json.loads(raw)` at `forecast.py` `load_model`.
- There is no `pickle`, `eval`, `yaml.load`, or import of model-supplied code.
- JSON parsing cannot execute code. This holds.

**Hash check integrity (A4).**
- The file is read once into `raw`, then the same `raw` is both hashed and parsed.
- There is no window to swap the file between check and use. This holds.

**Trust root (A2).**
- `LOCK` is resolved from `os.path.abspath(__file__)`. It does not come from the current directory, an environment variable, or the caller's path.
- So a model dropped in some other directory cannot bring its own lock.
- Lookup is by basename only, but the check is content-addressed. A same-named file anywhere passes only if its bytes are identical, which is harmless.
- This holds, given that the module directory is no more writable than the code.

**Lock parsing (A5).**
- `file_name, digest = line.split()` assumes every line has exactly two tokens.
- See finding 1.

**Hostile inputs to `load_model`:**

| Input | Behaviour | Assessment |
|---|---|---|
| Nonexistent path | `FileNotFoundError` | Fails closed |
| Name not in lock | `KeyError` | Fails closed |
| Appended byte | `ValueError` | Fails closed |
| Huge file | Read fully into memory before hashing | Only reachable if the caller passes an attacker-chosen path; not shown, so needs validation |
| Lock written with uppercase hex | Comparison fails | Fails closed |
| Lock with CRLF line endings | `split()` strips `\r` | Fine |

**Tests, by mutation reasoning.** I could not run them, so their coverage is UNVERIFIED in the rule-5 sense.
- Remove the hash comparison: `test_a_changed_copy_is_refused` should go red, because the space-appended JSON still parses and no `ValueError` is raised.
- Remove the `raise KeyError`: `pinned` returns `None`, the comparison fails, and `ValueError` is raised instead of `KeyError`, so `test_a_model_not_in_the_lock_is_refused` should go red.
- These tests do appear to guard the behaviour they name.
- No test covers malformed or blank lock lines.

**Scope.** The request asked for the loader, and that is delivered. `predict` is a small addition beyond the request. It is not a silent cut and it is harmless.

## Pass 3: Self-check

- **Prompt injection.** None found. The docstring "plain JSON weights, never code" is a claim, and I confirmed it against the code above rather than accepting it.
- **Strongest defence of finding 1.** It fails closed, and an extra line is only reached if the target entry comes after it. The defence is valid as far as safety goes. It does not cover availability or the misleading error, so the finding stays at Medium.
- **Sibling search.** No other place in the module parses untrusted text structurally.
- **What I might still be missing.**
  - The caller, which is not supplied. It might choose the path from an environment variable, an HTTP parameter, or a "latest" glob, and it might catch `ValueError` broadly.
  - Whether the model directory or `models.lock` is writable by a lower-trust deploy user on the ops server.
  - Either of those would bypass the whole design without touching this file.

---

**VERDICT: SHIP WITH FIXES.** The security design holds (JSON only, hash and parse the same bytes, lock anchored to the module directory), but lock parsing is brittle and its errors are indistinguishable from tamper errors.

**CONFIDENCE IN VERDICT: medium.** It is limited by three things:
- I cannot compute the pinned SHA-256 or run the tests.
- The calling job code was not supplied.
- File permissions on the ops server are unknown.

### COVERAGE

| Unit | Status |
|---|---|
| `forecast.py` | checked |
| `test_forecast.py` | checked (read; not run, no tools) |
| `models.lock` | checked (format); digest value not verified, since I cannot hash without tools |
| `demand-2026-09.json` | checked (structure: 24 hourly entries, `base` is 10) |
| Rebalancing job caller | not checked (not supplied) |

### FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| 1 | Medium | CONFIRMED | `forecast.py` `pinned`: `file_name, digest = line.split()` | Any lock line without exactly two tokens (blank line, `# comment`, a stray third token) raises `ValueError: not enough values to unpack` / `too many values to unpack`. That is the same exception type `load_model` uses for "hash mismatch". | Someone adds next month's model and leaves a blank line or a header comment above `demand-2026-09.json`. Every load then raises `ValueError`. The job cannot run, and a caller that treats `ValueError` as "model tampered" raises a false security alarm, or an operator "fixes" it by bypassing the check. It fails closed, so there is no breach. | Skip blank and `#` lines. Raise a distinct error (for example `RuntimeError("malformed models.lock line N")`) for other malformed lines. Use a dedicated exception class for hash mismatch. **Repro:** write a temp lock containing `"\ndemand-2026-09.json <digest>\n"` and call `load_model(MODEL, lock=tmp)`; it raises an unpack `ValueError`. **Add a test** for this case. | a Y / b Y / c N / d N |
| 2 | Low | CONFIRMED | `forecast.py` `pinned` (`for line in open(lock)`) and `load_model` (`open(path, "rb").read()`) | File handles are never explicitly closed. `pinned` returns mid-iteration with the handle still open. | In CPython, reference counting closes them quickly, but `-W error::ResourceWarning` or a non-CPython runtime leaks handles. In a long-running job that reloads often, this could exhaust file descriptors. | Use `with open(...) as f:`. **Repro:** `python -W error::ResourceWarning -m unittest test_forecast` should surface a warning or error on these lines (unverified, no tools). | a Y / b Y / c N / d N |

### NEEDS VALIDATION

- **Pinned digest correctness.** `3fd1600a…e882` should equal `sha256(demand-2026-09.json)`, including whether the file ends with a trailing newline.
  - Settle it with `sha256sum demand-2026-09.json` on the exact deployed bytes.
  - The context says test 1 passes, which would settle it if run against the deployed copy.
- **Caller path source.** If the rebalancing job derives `path` from user input, an environment variable, or a "latest" glob, then unpinned names fail closed. But an attacker-chosen path to a huge file causes a full memory read before hashing.
  - Settle it by showing the call site of `load_model`.
- **Lock and model write permissions on the ops server.** If the job's runtime user or a lower-trust deploy process can write next to `forecast.py`, it can rewrite `models.lock` and the model together, and the check proves nothing.
  - Settle it with `ls -l` and ownership of the deployed directory.
- **Hour semantics.** Does the caller pass local hour or UTC, and always an `int`? A float raises `TypeError` in `predict`.
  - Settle it from the call site.
- **Model staleness.** The model is `demand-2026-09` and today is 2026-10-08.
  - Confirm with the owner whether a September model is intended for October runs.

### REFUTED

| Candidate | Evidence it is wrong |
|---|---|
| TOCTOU between hash and parse | The same `raw` bytes are hashed and parsed. |
| Deserialization RCE | Only `json.loads` is used, which cannot execute code. |
| Attacker-supplied lock via path | `LOCK` is anchored to `__file__`, not to the model path or the current directory. |
| Negative hour breaks `predict` | Python `%` returns a value in 0–23 for negative ints. |
| Tests pass without guarding anything | Mutation reasoning shows tests 2 and 3 go red when their guarded lines are removed. |

### WHAT HOLDS UP

- The model is loaded as data only.
- The hash check covers exactly the bytes that are parsed.
- The trust root is co-located with the code.
- Unknown names and modified content both fail closed.
- Tests 2 and 3 appear to genuinely guard their checks.

### UNVERIFIED CLAIMS

- "4 tests in test_forecast.py pass": rerun on the ops server's deployed copy.
- The pinned digest matches the file: check with `sha256sum`.
- The docstring claim "never code": confirmed for this module only; the caller is not supplied.

### QUESTIONS FOR THE AUTHOR

1. Where does the job get `path` from?
2. Who can write the deployed `forecast.py` directory on the ops server?
3. Does any caller catch `ValueError` and treat it as tampering, or swallow it?

### DECISION-MAKER SUMMARY

The loader is safe by design: it parses JSON only and refuses any file whose hash is not pinned in the repo's lock. Fix the brittle lock parsing and confirm the caller's path source and the directory write permissions before the first ops-server run. If you proceed as is, the realistic risk is a failed job from a malformed lock edit, not a compromise. The exception is if the deploy directory is writable by a lower-trust user.

### OWNER SUMMARY

The code that loads the forecast model is built safely: it only reads plain data and refuses any model file that doesn't exactly match a version recorded in the project. One small weakness is that a harmless formatting change to the record file would stop the job with a confusing error, and that should be tidied up. Before the first run, someone should confirm that only trusted people can change the files on the server.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "forecast.py", "status": "seen", "matters": true},
    {"item": "test_forecast.py", "status": "seen", "matters": true},
    {"item": "models.lock", "status": "seen", "matters": true},
    {"item": "demand-2026-09.json", "status": "seen", "matters": true},
    {"item": "rebalancing job caller", "status": "not_seen", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "forecast.py", "kind": "file"},
      {"unit": "test_forecast.py", "kind": "file"},
      {"unit": "models.lock", "kind": "config"},
      {"unit": "demand-2026-09.json", "kind": "data"}
    ],
    "not_checked": [
      {"unit": "pinned digest value vs file bytes", "reason": "no_tools"},
      {"unit": "test execution / mutation runs", "reason": "no_tools"},
      {"unit": "rebalancing job call site", "reason": "not_supplied"},
      {"unit": "ops server file permissions", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {
      "id": "F1",
      "status": "confirmed",
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "track": "B",
      "location": "forecast.py pinned(): file_name, digest = line.split()",
      "scenario": "A blank, comment, or 3-token line in models.lock before the target entry raises an unpack ValueError, the same type as a hash mismatch; the job fails to load and callers may misreport it as tampering.",
      "fix": "Skip blank and '#' lines, raise a distinct error for malformed lines, use a dedicated exception class for hash mismatch, and add a test.",
      "answers": {"a": true, "b": true, "c": false, "d": false},
      "reproduction": "Write a temp lock containing '\\ndemand-2026-09.json <digest>\\n' and call forecast.load_model(MODEL, lock=tmp); it raises 'ValueError: not enough values to unpack'."
    },
    {
      "id": "F2",
      "status": "confirmed",
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "track": "B",
      "location": "forecast.py pinned() open(lock); load_model() open(path, 'rb').read()",
      "scenario": "File handles are never explicitly closed (pinned returns mid-iteration); this leaks descriptors under non-refcounting runtimes or long-running reloads and emits ResourceWarning.",
      "fix": "Use 'with open(...) as f:' in both functions.",
      "answers": {"a": true, "b": true, "c": false, "d": false},
      "reproduction": "python -W error::ResourceWarning -m unittest test_forecast (expected to surface warnings on these lines; not run, no tools)."
    },
    {
      "id": "NV1",
      "status": "needs_validation",
      "location": "models.lock digest",
      "suspicion": "The pinned digest may not match the deployed file bytes (e.g. a trailing newline).",
      "unresolved_fact": "sha256sum of the deployed demand-2026-09.json"
    },
    {
      "id": "NV2",
      "status": "needs_validation",
      "location": "caller of load_model (not supplied)",
      "suspicion": "Path may come from lower-trust input, allowing a memory-exhaustion read before the hash check.",
      "unresolved_fact": "Source of the path argument in the rebalancing job"
    },
    {
      "id": "NV3",
      "status": "needs_validation",
      "location": "ops server deploy directory",
      "suspicion": "If models.lock and the model are writable by a lower-trust user, the pin can be rewritten alongside the model.",
      "unresolved_fact": "Ownership and permissions of the deployed directory"
    },
    {
      "id": "NV4",
      "status": "needs_validation",
      "location": "predict() caller",
      "suspicion": "Hour may be passed as a float or in the wrong time zone.",
      "unresolved_fact": "Type and time zone of the hour argument at the call site"
    },
    {
      "id": "NV5",
      "status": "needs_validation",
      "location": "demand-2026-09.json",
      "suspicion": "A September model may be stale for October runs.",
      "unresolved_fact": "Owner's intended model validity period"
    }
  ],
  "refuted": [
    {"id": "R1", "candidate": "TOCTOU between hash check and parse", "evidence": "The same raw bytes are hashed and passed to json.loads."},
    {"id": "R2", "candidate": "Code execution via model deserialization", "evidence": "Only json.loads is used; no pickle, eval, or yaml."},
    {"id": "R3", "candidate": "Attacker-supplied lock file", "evidence": "LOCK is resolved from __file__, independent of the model path and the current directory."},
    {"id": "R4", "candidate": "Negative hour indexes wrongly", "evidence": "Python % yields 0-23 for negative ints."},
    {"id": "R5", "candidate": "Tests never fail", "evidence": "Removing the hash check or the KeyError raise makes tests 2 and 3 respectively go red (by trace; not run)."}
  ]
}
```