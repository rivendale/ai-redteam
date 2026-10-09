# Adversarial Diagnostic Review: `forecast.py` (demand-model loader)

## Pass 1: Reconstruct

The work loads a demand-forecast model for the dock rebalancing job. It reads the file's bytes once, hashes them with SHA-256, and compares the hash with the digest pinned for that file's basename in `models.lock`, which sits beside `forecast.py`. It parses JSON only after the hash matches. It also adds `predict(model, hour)`. For this to be safe on an ops server that holds the fleet DB credentials and the dock control API key, several things must hold:

- **Model is data, not code.** Loading must never execute code. `json.loads` cannot execute code.
- **Lock integrity.** The lock must be at least as trusted as the code. It lives in the repo next to `forecast.py`.
- **No race.** The bytes that were hashed must be the bytes that get parsed.
- **Correct pin.** The pinned digest must match the shipped file. I could not check this.
- **Unstated:** the job passes a sane path, the lock file is well-formed, and future pinned models keep the same shape that `predict` assumes.

## Pass 2: Attack (Track B)

**Security against the stated stakes holds.**
- No `pickle`, `eval`, `yaml.load` or import of the model. `json.loads` cannot run code, so the docstring's "never code" claim is true.
- The hash is computed over `raw`, and the same `raw` is parsed. There is no read-twice race.
- The hash is checked before parsing, so a hostile file cannot reach the parser unless an attacker can also edit `models.lock`. Anyone who can edit the lock can already edit `forecast.py`.
- Keying by basename does not open a bypass. A file elsewhere with the same name passes only if its content is byte-identical to the pinned file.
- `!=` instead of a constant-time compare is fine here. The digest is not a secret.
- The module never touches credentials or the API key.

**Hostile inputs:**
- **Empty or garbage model file:** the hash mismatches, so it raises `ValueError`. Fails closed.
- **Unlisted name:** raises `KeyError`. Fails closed.
- **Malformed lock:** see F1.
- **Huge path target:** see F4.
- **Negative hour:** Python's `%` maps it into 0–23, which is correct.
- **Float hour:** `25.5 % 24` is a float, so `list` indexing raises `TypeError`. Callers must pass integers.

**Tests:**
- Without the hash comparison, `test_a_changed_copy_is_refused` would go red: the trailing space is valid JSON, so no `ValueError` would be raised.
- Without the lookup, `test_a_model_not_in_the_lock_is_refused` would go red.
- I could not run these mutations (no tools), so that is reasoned, not observed. The gap is in F1.

## Pass 3: Self-check

- I dropped any concern about timing attacks, path traversal and the JSON parser. Each failed under scrutiny for the reasons above.
- The most serious problem I could still be missing is outside the shown code: how the job builds `path`, and whether the job falls back to something unpinned when `load_model` raises. I cannot see the caller.

---

**VERDICT: SHIP.** The loader fails closed on every path I traced, never executes model content, and has no route from the model file to the server's credentials. The findings below are low-severity hardening, not blockers.

**CONFIDENCE IN VERDICT: medium.** I could not run the tests, compute the pinned SHA-256, or see the calling job.

## FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Low | CONFIRMED | `pinned()`: `file_name, digest = line.split()` | Blank, comment or three-field lines in `models.lock` raise `ValueError: not enough/too many values to unpack`. That is the same exception type used for hash mismatch. | Someone adds a trailing blank line or `# comment` above an entry. Lookups past that line crash with a misleading error. `test_a_changed_copy_is_refused` also expects `ValueError`, so it could pass for the wrong reason if the lock were malformed. | Skip blank lines and `#` lines; raise a distinct error naming the bad lock line. Add a test with a blank or comment line in a temp lock. Assert the mismatch error message, not only its type. |
| 2 | Low | PROBABLE | `load_model` return; `predict` | The loaded structure is never validated. `predict` assumes `base` is a number and `per_hour` is a list of exactly 24 numbers. | The next model is pinned with 23 entries or string values. It loads cleanly, then the job crashes mid-run at hour 23 with `IndexError`, or with `TypeError` on `int + str`. | Check the shape inside `load_model` after parsing. Add a test using a pinned temp model with a bad shape. |
| 3 | Low | UNVERIFIED | Hash over raw bytes vs. git checkout | Any line-ending or encoding rewrite at checkout changes the bytes, for example `core.autocrlf` or `.gitattributes text=auto` on the ops host. | The ops checkout normalizes newlines, the hash mismatches, and the job refuses to run. This fails safe but causes an outage. | Add `*.json -text` (or `binary`) to `.gitattributes`. Run the tests on the ops server's actual checkout. |
| 4 | Low | PROBABLE | `open(path, "rb").read()` | The whole file is read before checking. Lock and model handles are never closed. | Only matters if the caller's `path` can be influenced: pointing it at a very large file or `/dev/zero` exhausts memory before the hash check. The unclosed handles produce `ResourceWarning`. | Hash in chunks with a size cap, use `with open(...)`, and confirm the caller hardcodes the path. |
| 5 | Low | UNVERIFIED | Filename `demand-2026-09.json`, today 2026-10-08 | The name suggests a September model running in October. | If this is the September forecast rather than a model trained in September, rebalancing runs on a stale demand profile. | Confirm the intended model, and the process (and reviewer) for rotating `models.lock`. |

## WHAT HOLDS UP

- The model is never executed: JSON only, parsed after the hash check.
- There is a single read, so no swap is possible between check and parse.
- Unlisted names and changed bytes both fail closed.
- The basename key gives no bypass, because content is still hashed.
- The `predict` hour wrapping handles hours ≥24 and negative hours.
- The shipped `per_hour` has exactly 24 entries, which I counted.
- Two tests, by reasoning, would go red if their guarded check were removed.

## UNVERIFIED CLAIMS

| Claim | How to confirm |
|---|---|
| "4 tests pass" | Run `python -m unittest test_forecast -v` on the ops checkout. |
| The pinned digest `3fd1600a…e882` matches `demand-2026-09.json` | `sha256sum demand-2026-09.json` on the deployed copy. |
| The tests catch regressions | In a scratch copy, delete the hash comparison and confirm `test_a_changed_copy_is_refused` fails. Separately, make `pinned` return the first digest regardless of name and confirm `test_a_model_not_in_the_lock_is_refused` fails. |

## QUESTIONS FOR THE AUTHOR

1. How does the rebalancing job choose `path`? Is it hardcoded or built from input?
2. What does the job do when `load_model` raises? Does it abort, or fall back to an unpinned or previous model?
3. Who can change `models.lock`, and is a lock change code-reviewed like a code change?

## DECISION-MAKER SUMMARY

Safe to run: the loader refuses any model file that does not match the reviewed hash and never executes model content, so it gives no route to the server's credentials. Before the first run, run the tests on the ops server's checkout and confirm the job aborts, rather than falling back, when loading fails. Remaining risk is operational, not security: a malformed lock or a badly shaped future model would stop the job with a confusing error.

## OWNER SUMMARY

The code that loads the demand forecast checks that the file is exactly the one that was reviewed, and treats it as plain numbers that can never run as a program. It does not expose the server's passwords or keys. A few small improvements would make errors clearer and catch a badly formed future forecast earlier, but nothing here should stop the job from running.

```json
{
  "verdict": "SHIP",
  "findings": [
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "forecast.py pinned(): `file_name, digest = line.split()`",
      "scenario": "A blank, comment, or three-field line in models.lock raises ValueError (unpack), the same type as a hash mismatch; lookups past it crash with a misleading error, and test_a_changed_copy_is_refused could pass for the wrong reason.",
      "fix": "Skip blank and '#' lines, raise a distinct error naming the bad lock line, add a test with a blank or comment line, and assert the mismatch message rather than only the exception type."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "forecast.py load_model return value; predict()",
      "scenario": "A future pinned model with 23 per_hour entries or non-numeric values loads cleanly, then the job crashes mid-run with IndexError or TypeError.",
      "fix": "Validate base is numeric and per_hour is 24 numbers in load_model after parsing; add a test with a pinned temp model of the wrong shape."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "Raw-byte SHA-256 vs. git checkout of demand-2026-09.json",
      "scenario": "core.autocrlf or text=auto on the ops host rewrites line endings, the hash mismatches, and the job refuses to run (fails safe, but an outage).",
      "fix": "Add `*.json -text` to .gitattributes and run the tests on the ops server's checkout."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "forecast.py load_model: `open(path, \"rb\").read()`; pinned(): `open(lock)`",
      "scenario": "If the caller's path can be influenced, a huge file or /dev/zero exhausts memory before the hash check; unclosed handles emit ResourceWarning.",
      "fix": "Hash in chunks with a size cap, use `with open(...)`, and confirm the caller hardcodes the path."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "Model filename demand-2026-09.json (review date 2026-10-08)",
      "scenario": "If this is the September demand profile rather than a model trained in September, October rebalancing uses stale demand.",
      "fix": "Confirm the intended model and document the models.lock rotation and review process."
    }
  ]
}
```