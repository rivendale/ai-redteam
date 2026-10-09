**Review mode:** single reviewer, no tools, no subagent. Code was traced by reading, not by running. I did not write this work, but nothing was executed, so anything that depends on running something is UNVERIFIED.

**VERDICT: SHIP.** The loader parses JSON only, hashes and parses the same bytes, and fails closed. Nothing on the load path can run code on the server that holds the credentials, and no Critical or High finding survived. The two findings below are worth fixing but do not block the run.

**CONFIDENCE: medium.** Nothing was run. The pinned digest and the "4 tests pass" claim are unverified, and the code that calls this module was not supplied.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, `forecast.py`, `models.lock`, `demand-2026-09.json`, `test_forecast.py`.
- **Not seen:**
  - The rebalancing job that calls `load_model`/`predict`. This matters for which path and hour it passes; see S3.
  - Test run output. This matters for whether the pin matches; see S1.
  - Deploy layout and file permissions on the ops server. These matter only weakly; see R1.

**COVERAGE**
- **Checked:** all four files; `forecast.py:pinned`, `load_model` and `predict`; all four tests; the docstring claims "plain JSON weights, never code" and "must match the hash pinned for its name"; the 24-entry `per_hour` array (counted: 24).
- **Not checked:** the caller job, the actual SHA-256 of the model bytes, and runtime behaviour of the tests.

**SEATS AND GATE:**
- Local reviewer only.
- No subagent or cross-vendor seats were available in this session.
- Sensitivity gate passed: the work contains no credentials or personal data. The context only says the server holds credentials.
- No instructions to the reviewer were found embedded in the work.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced Python semantics) | B | `forecast.py:11` `file_name, digest = line.split()` | Any blank, comment or extra-token line in `models.lock` raises an unpacking `ValueError`. That is the same exception type `load_model` uses for "does not match the pinned hash". | Someone adds `# pinned 2026-09-30` or a trailing blank line to `models.lock`. Every load then raises `ValueError: too many/not enough values to unpack`, even for the correct model. The job stops (it fails closed), and anyone handling `ValueError` as "tampered model" gets a false tamper alarm. | Skip blank and `#` lines, and raise a distinct error that names the malformed lock line. **Test:** write a lock containing `"\n# c\ndemand-2026-09.json <digest>\n"` and assert that `load_model(MODEL, lock=tmp)` returns `base == 10`. It currently raises `ValueError`. | a✓ b✓ c✗ d✗ |
| F2 | Low | CONFIRMED (traced) | B | `forecast.py:22`, `forecast.py:26` | The model's shape is never validated after loading. `predict` assumes `base` is a number and `per_hour` holds 24 numbers. `json.loads` also accepts `NaN`/`Infinity`. | A future model is re-pinned with 23 `per_hour` entries, or with `"base": NaN`. It loads without error, then `predict(m, 23)` raises `IndexError` partway through the job, or every forecast silently becomes NaN. | After `json.loads`, check that `per_hour` is a list of 24 finite numbers and `base` is a finite number; raise otherwise. **Test:** pin a 23-entry model in a temp lock and assert that `load_model` raises. It currently loads. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION
- **S1:** Whether `3fd1600a…e882` is the SHA-256 of the exact bytes of `demand-2026-09.json`, including any trailing newline. **Settle it with:** `sha256sum demand-2026-09.json`, or a test run log showing `test_the_shipped_model_matches_its_pinned_hash` passing.
- **S2:** Whether the tests have ever been seen to fail. **Settle it with:** in a scratch copy, delete the hash comparison at `forecast.py:20-21` and confirm `test_a_changed_copy_is_refused` goes red. Then make `pinned` return the first digest regardless of name and confirm `test_a_model_not_in_the_lock_is_refused` goes red.
- **S3:** Which path the rebalancing job passes in, and whether the September 2026 model is the one intended for runs from 2026-10-08 onward. **Settle it with:** the caller code and the model-rollover plan.

## REFUTED
- **R1: "The lock sits beside the model, so the pin protects nothing."** Anyone who can edit `models.lock` can already edit `forecast.py`. The model is data, so tampering with it can at worst produce wrong forecast numbers, which is less than what editing the code allows. The pin guards against accidental or out-of-band model swaps, which matches what the docstring claims.
- **R2: "Loading a model on a server holding credentials risks code execution."** Only `json.loads` is used. There is no pickle, `eval`, `import` or deserialiser that can run code.
- **R3: "TOCTOU between the hash check and the parse."** The same `raw` bytes are hashed (line 20) and then parsed (line 22). The file is read once.
- **R4: "Lookup by basename lets a file from any directory through."** It passes only if its bytes hash to the pinned digest, which means it is byte-identical to the pinned model.
- **R5: "test 2 could pass on a JSON parse error (JSONDecodeError is a ValueError)."** Appending a space leaves the JSON valid, so only the hash check can raise in that test.

## WHAT HOLDS UP
- The loader is JSON-only, which is the right choice on a credential-holding host.
- The read is single, and the hash covers exactly the bytes that are parsed.
- A name missing from the lock fails closed with `KeyError`.
- `LOCK` is resolved from `__file__`, so it does not depend on the working directory.
- `hour % 24` handles out-of-range and negative hours.
- The shipped model has exactly 24 hourly entries.
- The scope matches the request: a loader plus a small `predict`.

## UNVERIFIED CLAIMS
- "4 tests in test_forecast.py pass." Confirm with a run log.
- The pinned digest matches the file. See S1.

## QUESTIONS FOR THE AUTHOR
1. Will `models.lock` ever hold comments or multiple models? This decides whether F1 matters soon.
2. Which model path does the job pass, and how does it roll over monthly?

## DECISION-MAKER SUMMARY
Safe to run. The loader cannot execute code from the model file and refuses any model not pinned by hash. Before the next model update, harden the lock-file parsing (F1) and the model shape checks (F2). Otherwise a routine edit could stop the job or produce silent NaN forecasts.

## OWNER SUMMARY
The code that loads the bike-dock demand forecast is safe to run on the operations server. It only reads plain data and rejects any file that has been changed. Two small robustness fixes are recommended before the next forecast update so that an ordinary edit cannot stop the job or produce blank forecasts.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "forecast.py", "status": "seen", "matters": true},
    {"item": "models.lock", "status": "seen", "matters": true},
    {"item": "demand-2026-09.json", "status": "seen", "matters": true},
    {"item": "test_forecast.py", "status": "seen", "matters": true},
    {"item": "rebalancing job caller code", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": true},
    {"item": "ops server deploy layout and permissions", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Work contains no credentials or personal data; context only states the server holds them."},
  "coverage": {
    "checked": [
      {"unit": "forecast.py", "kind": "file"},
      {"unit": "forecast.py:pinned", "kind": "function"},
      {"unit": "forecast.py:load_model", "kind": "function"},
      {"unit": "forecast.py:predict", "kind": "function"},
      {"unit": "models.lock", "kind": "config"},
      {"unit": "demand-2026-09.json", "kind": "data"},
      {"unit": "test_forecast.py", "kind": "file"},
      {"unit": "docstring: plain JSON weights, never code", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "rebalancing job caller", "reason": "not supplied"},
      {"unit": "SHA-256 of demand-2026-09.json", "reason": "no tools to compute it"},
      {"unit": "test execution and mutation", "reason": "no tools to run tests"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "forecast.py:11",
     "scenario": "A comment or blank line added to models.lock makes every load raise an unpacking ValueError, the same type as a hash mismatch; the job stops and the failure reads as a tampered model.",
     "fix": "Skip blank and '#' lines in pinned() and raise a distinct error naming any malformed lock line.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Write a temp lock '\\n# c\\ndemand-2026-09.json <digest>\\n'; call load_model(MODEL, lock=tmp); expect base == 10, observe ValueError (unpack)."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "forecast.py:22, forecast.py:26",
     "scenario": "A future re-pinned model with 23 per_hour entries or base NaN loads cleanly, then predict raises IndexError at hour 23 or returns NaN for every hour.",
     "fix": "After json.loads, require base to be a finite number and per_hour a list of 24 finite numbers; raise otherwise.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Pin a 23-entry per_hour model in a temp lock; expect load_model to raise, observe it loads and predict(m, 23) raises IndexError."},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "models.lock:1",
     "suspicion": "The pinned digest may not match the shipped model bytes.",
     "unresolved_fact": "Output of sha256sum demand-2026-09.json, or a log of test_the_shipped_model_matches_its_pinned_hash passing."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "test_forecast.py",
     "suspicion": "Tests have not been shown to go red when the guarded code is broken.",
     "unresolved_fact": "In a scratch copy, removing forecast.py:20-21 turns test_a_changed_copy_is_refused red."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "rebalancing job (not supplied)",
     "suspicion": "The job may pass a September 2026 model for October runs, or an untested path or hour type.",
     "unresolved_fact": "The caller code and the monthly model rollover plan."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Lock co-located with the model gives no protection.", "evidence": "Write access to models.lock implies write access to forecast.py; the model is data, so tampering with it can only skew numbers."},
    {"id": "R2", "candidate": "Model loading risks code execution on the credential-holding server.", "evidence": "Only json.loads is used; no pickle, eval or import."},
    {"id": "R3", "candidate": "TOCTOU between hash check and parse.", "evidence": "The same raw bytes are hashed at line 20 and parsed at line 22."},
    {"id": "R4", "candidate": "Basename lookup admits files from other directories.", "evidence": "They must hash to the pinned digest, so they are byte-identical."},
    {"id": "R5", "candidate": "test_a_changed_copy_is_refused passes via JSONDecodeError.", "evidence": "An appended space keeps the JSON valid, so only the hash check can raise."}
  ]
}
```