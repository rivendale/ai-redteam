# Adversarial diagnostic review: `forecast.py` (demand-forecast model loader)

**Limits of this review:** I had no tools in this session. I could not run the tests, compute the SHA-256 of `demand-2026-09.json`, or apply mutations in a scratch copy. Wherever a conclusion depends on execution, I say so.

## Pass 1: Reconstruct

The work provides `load_model(path)`. It reads a model file once, hashes those exact bytes with SHA-256, and compares the hash to a digest pinned by basename in `models.lock` next to the module. It parses the bytes with `json.loads` only if they match. `predict(model, hour)` returns `base + per_hour[hour % 24]`.

For this to be correct, these must hold:
1. `json.loads` cannot execute code. This is true for the stdlib.
2. The pinned digest really is the hash of the shipped file.
3. `models.lock` is no easier to tamper with than `forecast.py` itself. Both live in the repo, so the trust root is the repo.
4. The caller passes an integer hour.
5. The pinned model is the right one to use now. Unstated: it is named for 2026-09, and today is 2026-10-08.

## Pass 2: Attack (Track B)

**Security, given the stakes (credentials and dock API key on the ops server).**
- **No code-execution path.** The only deserializer is `json.loads`. There is no pickle, `torch.load`, `yaml.load` or `eval`.
- **No time-of-check/time-of-use gap.** The file is read once (`raw = open(path, "rb").read()`), and the same `raw` is both hashed and parsed. Swapping the file between the check and the parse is not possible.
- **Path tricks gain nothing.** Lookup is by basename (`forecast.py:20`), so any directory works. But the content must still match the pinned digest, so a file at `/tmp/demand-2026-09.json` loads only if it is byte-identical to the shipped one.
- **The module never touches credentials or the network.** The security design holds.

**Hostile inputs.**
- *Unknown name:* raises `KeyError` and fails closed.
- *Changed content:* raises `ValueError` and fails closed.
- *Huge file:* read fully into memory before the hash check (Low; see findings).
- *Malformed lock lines:* a blank line, comment or third column makes `file_name, digest = line.split()` raise an unpacking `ValueError`. This still fails closed, but the error is misleading.
- *Duplicate lock entries:* first match wins.

**Tests: do they actually guard the code (reasoned mutations, not run)?**
- *Remove the hash check:* `test_a_changed_copy_is_refused` appends `b" "`. Trailing whitespace is valid JSON, so `json.loads` would succeed and the test would go red. The author avoided the trap of appending a non-JSON byte, which would let `JSONDecodeError` (a subclass of `ValueError`) make the test pass with no hash check at all.
- *Same mutation:* `test_a_model_not_in_the_lock_is_refused` would also go red.
- *Key the lookup by full path instead of basename:* test 2 would raise `KeyError` instead of `ValueError` and go red.
- Conclusion: the tests look discriminating. I have not confirmed this by execution.

**Requirement fit.** The request was "load the demand-forecast model." The work does that and nothing extra. Choosing which model file to load is left to the caller, and the caller is not shown.

## Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Medium | UNVERIFIED | `models.lock:1`, file name `demand-2026-09.json` | The only pinned model is named for September 2026; today is 2026-10-08. Nothing checks that the model is still current. | If models are monthly, the job rebalances October docks on September demand, and nothing in the code signals it. | Confirm with the owner whether the model is meant to be monthly. If so, pin the current one, or have the job log or assert the model's period. |
| 2 | Low | CONFIRMED (by reading) | `forecast.py:12-13` `file_name, digest = line.split()` | A blank line, comment or extra column raises an unhelpful unpacking `ValueError` from inside `pinned`. | Someone adds a trailing blank line or `# comment` to `models.lock`. Every load fails with "not enough values to unpack", which looks like a code bug rather than a lock format error. Fails closed, so this costs availability only. | Skip blank and `#` lines, and raise a clear error on a malformed line. Add a test with a blank line in the lock. |
| 3 | Low | CONFIRMED (by reading) | `forecast.py:31` `model["per_hour"][hour % 24]` | No type check on `hour`. | The caller passes `datetime.hour` (fine) or a float such as `7.0` from arithmetic. `7.0 % 24` is a float, so list indexing raises `TypeError` mid-job. | Require `int(hour)`, or document it; add a test with a float hour. |
| 4 | Low | CONFIRMED (by reading) | `forecast.py:19` `open(path, "rb").read()` | The whole file is read before it is checked, with no size cap. Files are also opened without `with`, here and at line 11. | A large file with the pinned name is hashed in full before being rejected. This is a memory and time cost only, with no integrity risk. | Check `os.path.getsize` against a sane cap first; use `with open(...)`. |

I considered and dropped these:
- **Non-constant-time hash compare:** no secret is being compared.
- **Lock tampering:** anyone who can edit `models.lock` can edit `forecast.py`, so the trust root is the same.
- **No schema validation:** the content is pinned, so the schema is fixed.

## What holds up

- The safe parser plus a single-read hash pin is the right design for a host that holds credentials. There is no deserialization or time-of-check/time-of-use path.
- Every failure mode found fails closed: unknown name, changed bytes and malformed lock all raise.
- The tests appear discriminating. The space-append test avoids the `JSONDecodeError ⊂ ValueError` false pass.
- `per_hour` has exactly 24 entries, and `hour % 24` handles values above 23 and negative values.

## Unverified claims

- **The pinned digest matches the shipped file.** Confirm with `sha256sum demand-2026-09.json` against `models.lock`.
- **"4 tests in test_forecast.py pass."** Confirm with `python -m unittest test_forecast -v` on the ops server checkout. Line-ending conversion such as `autocrlf` could change the bytes there; that fails closed but would block the job.
- **The tests go red under mutation.** Confirm in a scratch copy: delete the hash comparison in `load_model` and verify tests 2 and 3 fail.
- **How the rebalancing job calls `load_model` and `predict`.** The calling code is not in the review; check the path source and the hour type.

## Questions for the author

1. Is the model monthly, and should October's job use `demand-2026-09.json`?
2. What type does the job pass as `hour`?

## Verdict

**VERDICT: SHIP.** The loader is safe for a credential-holding host and fails closed. The remaining issues are low-severity robustness items plus one open question about which model is current.

**CONFIDENCE IN VERDICT: medium.** I could not run the tests, compute the hash or see the calling job.

## Decision-maker summary

The loader can run on the ops server: it only parses plain JSON, after checking the exact bytes against a pinned hash, and every error path refuses to load. Before the first run, confirm the hash and test pass on the ops server's own checkout. Also confirm that a September-named model is the intended one for October. The remaining risk is stale forecasts, not a security exposure.

## Owner summary

The new code that loads the demand forecast is built safely: it refuses any model file that differs from the approved one and never runs code from that file. The one open question is whether the approved forecast, which is labelled for September, is still the right one to use in October. A few small robustness improvements are suggested, but none of them block running the job.

```json
{
  "verdict": "SHIP",
  "findings": [
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "models.lock:1 / demand-2026-09.json",
      "scenario": "Only a September-2026 model is pinned and today is 2026-10-08; if models are monthly, October rebalancing uses stale demand with no warning.",
      "fix": "Confirm model cadence with the owner; pin the current model or have the job log/assert the model period."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "forecast.py:12-13 `file_name, digest = line.split()`",
      "scenario": "A blank line, comment or extra column in models.lock raises 'not enough values to unpack' on every load; fails closed but blocks the job with a misleading error.",
      "fix": "Skip blank/# lines, raise a clear error on malformed lines; add a test with a blank line in the lock."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "forecast.py:31 `model[\"per_hour\"][hour % 24]`",
      "scenario": "A float hour (e.g. 7.0) yields a float index and raises TypeError mid-job.",
      "fix": "Coerce or validate hour as int; add a float-hour test."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "forecast.py:19 `open(path, \"rb\").read()` (and line 11)",
      "scenario": "An oversized file with the pinned name is read fully into memory before rejection; file handles are not closed via context managers.",
      "fix": "Check file size against a cap before reading; use `with open(...)`."
    }
  ]
}
```