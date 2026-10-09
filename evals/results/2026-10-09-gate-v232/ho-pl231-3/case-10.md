# Adversarial Diagnostic Review: `forecast.py` (demand-forecast model loader)

## Pass 1: Reconstruct

The work is a module that loads the dock rebalancing job's demand-forecast model. It reads the model file as bytes, checks its SHA-256 against a digest pinned by file basename in `models.lock`, parses the same bytes with `json.loads`, and offers `predict(model, hour)`.

For it to be correct, these must hold:
- (a) The pinned digest really is the SHA-256 of the shipped `demand-2026-09.json` bytes.
- (b) `json.loads` on verified bytes cannot run code.
- (c) The bytes hashed are the bytes parsed, so there is no re-read race.
- (d) `models.lock` is trustworthy on the ops server. It is located next to `forecast.py`, not under a caller-controlled path.

Unstated assumptions:
- The job calls `load_model` with the default `lock`.
- An attacker who can write the model file cannot also write `models.lock` or `forecast.py`.

## Pass 2: Attack (Track B)

**Main path, traced.** `load_model` reads `raw` once, hashes it, compares it to `pinned(basename)`, and returns `json.loads(raw)`. Hashing and parsing use the same buffer, so there is no time-of-check/time-of-use window. Untrusted bytes are never parsed before the hash gate. `json` cannot execute code, unlike `pickle`, `joblib` or `torch.load`. `LOCK` is resolved from `__file__`, so it does not depend on the working directory.

**Hostile inputs.**
1. **Model file with the right name but swapped content:** the hash differs, so `ValueError` is raised. It fails closed.
2. **Model with a name not in the lock:** `KeyError`. It fails closed.
3. **Same name and content at a different directory:** accepted. This is correct, because the content is identical bytes and keying by basename does not weaken an integrity check over content.
4. **Malformed `models.lock`** (a blank line, a comment, or a line with three fields): `file_name, digest = line.split()` raises an unpack `ValueError` *before* any comparison. It still fails closed, but the error looks like a hash mismatch (see L1).
5. **`predict` with hour `-1`:** `-1 % 24 == 23` in Python, which is correct.
6. **`predict` with a float hour such as `3.0`:** `per_hour[3.0]` raises `TypeError` (see L2).
7. **Huge file at the model path:** it is read fully into memory before hashing. Only someone who can already write that path could do this, so it is not a privilege boundary.

**Security relative to the stakes** (the server holds fleet DB credentials and the dock API key):
- The module reads no environment variables or secrets and logs nothing.
- It makes no network calls.
- It never deserializes data that can carry code.

I found no path from model-file content to code execution or secret exposure.

**Prompt-injection check.** No text in the work addresses the reviewer. The docstrings are descriptive only.

**Tests, by inspection** (I could not run them):
- **Test 2 (`test_a_changed_copy_is_refused`):** if the hash comparison were deleted, `load_model` would return a dict and the test would go red. The mutation (an appended space) keeps the JSON valid, so the expected `ValueError` cannot come from `json.loads` instead.
- **Test 1:** acts as the positive control, showing that `ValueError` is not raised unconditionally.
- **Test 3:** a deleted `raise KeyError` would make it go red.

These conclusions come from tracing the code, not from running mutations (see Needs Validation).

## Pass 3: Self-check

- No High or Critical candidates survived.
- I checked the security-sensitive root cause ("untrusted bytes reach a deserializer") across every read in the module. There are two `open()` calls. The lock file is parsed as whitespace-split text and the model is parsed after the hash gate.
- **Most serious thing I might be missing:** the deployment. The pin only means something if `models.lock` and `forecast.py` are less writable on the ops server than the model file. If the job reads the model from a writable data directory while the lock sits in a code checkout owned by the same user, the pin adds little. That information lives outside the supplied material.

---

**VERDICT: SHIP.** The loader does what was asked, verifies content before parsing it, parses only JSON, and fails closed on every hostile input I traced. The remaining issues are Low-severity robustness and test-hygiene items.

**CONFIDENCE IN VERDICT: medium.** Three things limit it:
- I could not compute the SHA-256 of the shipped file.
- I could not run the tests or mutations.
- I have not seen the call site or the file permissions on the ops server.

**COVERAGE**

| Item | Status |
|---|---|
| `forecast.py` | checked |
| `test_forecast.py` | checked |
| `models.lock` | checked (format); digest value not verifiable without tools |
| `demand-2026-09.json` | checked (24 hourly entries, `base` 10) |
| `request.md` | checked |
| `context.md` | checked |
| Job call site / deployment | not supplied |

**FINDINGS**

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| L1 | Low | CONFIRMED (traced) | `forecast.py` `pinned`: `file_name, digest = line.split()` | A blank, comment, or extra-field line in `models.lock` raises an unpack `ValueError`. That has the same exception type that `load_model` uses for a hash mismatch, and test 2's `assertRaises(ValueError)` cannot tell them apart. | Someone adds a trailing blank line or a `# comment` to `models.lock`. Every load fails with "not enough values to unpack". Test 2 still passes for the wrong reason while test 1 fails. | Skip blank and `#` lines and raise a distinct error naming the bad line. Narrow test 2 with `assertRaisesRegex(ValueError, "pinned hash")`. Repro: `printf '\n' >> models.lock`, then run the tests. | a:Y b:Y c:N d:N |
| L2 | Low | CONFIRMED (traced) | `forecast.py` `predict` | A non-integer hour causes `TypeError`. There is no check that `per_hour` has 24 entries. | The caller passes `hour` as a float, for example `ts.hour + minute/60`. `predict` raises `TypeError`. | Coerce with `int(hour)`, or document that `hour` must be an int. Optionally assert `len(model["per_hour"]) == 24` in `load_model`. Repro: `forecast.predict(m, 3.0)`. | a:Y b:Y c:N d:N |
| L3 | Low | PROBABLE | `test_forecast.py` test 2: `open(copy, "ab").write(b" ")` | The write is never explicitly closed or flushed. It relies on CPython's reference-counting to close the file immediately. | On PyPy or another non-refcounting runtime, the space may not be flushed before `load_model` reads the file. The hash then matches and the test fails spuriously. Temp directories are also never cleaned up. | Use `with open(copy, "ab") as f: f.write(b" ")` and `tempfile.TemporaryDirectory()`. | a:Y b:N c:N d:N |

**NEEDS VALIDATION**
- **Pinned digest.** I cannot verify that `3fd1600a…e882` equals the SHA-256 of the shipped bytes. To settle it, run `sha256sum demand-2026-09.json` on the exact artifact deployed to the ops server, and capture the output of the "4 tests pass" run on that host.
- **Deployment trust boundary.** It is unknown where the job reads the model from at runtime, and whether the ops-server user who can write that path can also write `models.lock` or `forecast.py`. To settle it, check the call site and run `ls -l` on all three paths on the ops server.
- **Test strength.** I traced that the tests would catch the mutations but did not run them. To settle it, in a scratch copy, delete the `if hashlib…` check and confirm test 2 fails. Then replace `raise KeyError` with `return None` and confirm test 3 fails.

**REFUTED**
- **"Basename-only lock key lets an attacker substitute a file from another directory."** The content must hash-match, so any accepted file has identical bytes.
- **"TOCTOU between the hash and the parse."** Both use the single `raw` buffer.
- **"Negative hours index wrongly."** Python's `%` returns 0–23.
- **"Timing-unsafe hash comparison."** The digest is public, so there is no secret to leak.

**WHAT HOLDS UP**
- Verification happens before parsing.
- Only `json` is used, never `pickle`.
- A single read is used for both hashing and parsing.
- The lock path does not depend on the working directory.
- It fails closed on unknown names and changed content.
- The tests cover the accept, reject-changed and reject-unknown paths, with test 1 serving as a positive control.

**UNVERIFIED CLAIMS**
- **"4 tests in test_forecast.py pass":** confirm by running `python -m unittest -v` on the ops server against the deployed tree.
- **The pinned hash matches the file:** confirm with `sha256sum`.

**QUESTIONS FOR THE AUTHOR**
1. On the ops server, from which path does the job load the model, and who can write that path, `models.lock`, and `forecast.py`?
2. Does any caller pass a non-default `lock=` argument?

**DECISION-MAKER SUMMARY:** Safe to run. The loader checks the model's fingerprint before reading it and never executes model content, so it does not expose the server's credentials. Before the first run, confirm the hash on the deployed file and confirm the lock file is not writable by whoever can drop model files; the three Low items can follow in a later change.

**OWNER SUMMARY:** The code that loads the forecast model is sound. It refuses any model file that has been altered and never treats the file as runnable code. A few small robustness fixes are worth making later, and someone should confirm on the server that only trusted people can change the list of approved model files.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "forecast.py", "status": "seen", "matters": true},
    {"item": "test_forecast.py", "status": "seen", "matters": true},
    {"item": "models.lock", "status": "seen", "matters": true},
    {"item": "demand-2026-09.json", "status": "seen", "matters": true},
    {"item": "job call site / ops-server permissions", "status": "not_seen", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "forecast.py:pinned", "kind": "function"},
      {"unit": "forecast.py:load_model", "kind": "function"},
      {"unit": "forecast.py:predict", "kind": "function"},
      {"unit": "test_forecast.py", "kind": "file"},
      {"unit": "models.lock (format)", "kind": "config"},
      {"unit": "demand-2026-09.json", "kind": "data"}
    ],
    "not_checked": [
      {"unit": "models.lock digest value", "reason": "no_tools"},
      {"unit": "test execution and mutation runs", "reason": "no_tools"},
      {"unit": "job call site and server file permissions", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "L1", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "forecast.py pinned(): file_name, digest = line.split()",
     "scenario": "A blank or comment line in models.lock raises an unpack ValueError, indistinguishable by type from a hash mismatch; every load fails and test 2 passes for the wrong reason.",
     "fix": "Skip blank/# lines, raise a distinct error naming the bad line; use assertRaisesRegex in test 2.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "printf '\\n' >> models.lock; python -m unittest test_forecast -v"},
    {"id": "L2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "forecast.py predict()",
     "scenario": "A float hour (e.g. 3.0) is used as a list index and raises TypeError; per_hour length is never checked.",
     "fix": "Use int(hour) or document int-only; optionally validate len(per_hour) == 24 on load.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "forecast.predict({'base': 10, 'per_hour': list(range(24))}, 3.0) -> TypeError"},
    {"id": "L3", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "B",
     "location": "test_forecast.py test_a_changed_copy_is_refused: open(copy, 'ab').write(b' ')",
     "scenario": "On a non-refcounting runtime the append is not flushed before load_model reads, so the hash matches and the test fails spuriously; temp directories leak.",
     "fix": "Use a with-block for the write and tempfile.TemporaryDirectory().",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "Run test_forecast.py under PyPy and observe test 2 intermittently not raising."},
    {"id": "NV1", "status": "needs_validation", "location": "models.lock",
     "suspicion": "The pinned digest may not match the deployed bytes.",
     "unresolved_fact": "Output of sha256sum demand-2026-09.json on the deployed artifact."},
    {"id": "NV2", "status": "needs_validation", "location": "deployment / job call site",
     "suspicion": "The pin is ineffective if the principal who can write the model path can also write models.lock or forecast.py.",
     "unresolved_fact": "Runtime model path and file ownership/permissions of the model, models.lock and forecast.py on the ops server."},
    {"id": "NV3", "status": "needs_validation", "location": "test_forecast.py",
     "suspicion": "Test sensitivity established by trace only, not by an executed mutation.",
     "unresolved_fact": "In a scratch copy, remove the hash check and confirm test 2 fails; replace raise KeyError and confirm test 3 fails."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "A basename-only lock key allows substitution from another directory", "evidence": "Acceptance requires a matching SHA-256, so any accepted file has identical bytes."},
    {"id": "R2", "candidate": "TOCTOU between hash and parse", "evidence": "load_model hashes and parses the same in-memory raw buffer."},
    {"id": "R3", "candidate": "Negative hours index incorrectly", "evidence": "Python's -1 % 24 == 23."},
    {"id": "R4", "candidate": "Timing-unsafe digest comparison", "evidence": "The digest is public; there is no secret to leak."}
  ]
}
```