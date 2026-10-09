VERDICT: **SHIP WITH FIXES**. The loader is small, only reads JSON and fails closed, but the hash pin is only as strong as write access to the directory it sits in, and nobody has stated who has that access on the ops server.

CONFIDENCE IN VERDICT: **medium**. I had no tools, so I could not compute the SHA-256 of `demand-2026-09.json`, run the tests, or mutate the code. The "4 tests pass" claim comes with no output. The deployment permissions on the ops server are unknown.

## Pass 1: Reconstruct

`forecast.py` loads a demand model from a caller-supplied path. It reads the bytes once, hashes them, and compares the hash to the digest that `models.lock` records for the file's basename. If they match, it parses the bytes as JSON. `predict` returns `base + per_hour[hour % 24]`.

For this to be correct, all of the following must be true:
- The pinned digest is the real digest of the shipped file.
- Whoever can change the model cannot also change `models.lock`.
- The caller passes a sensible path and an integer hour.
- The September 2026 model is the one the job should use.

## Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Medium | CONFIRMED (design); PROBABLE (exposure) | `forecast.py:5` `LOCK = os.path.join(os.path.dirname(...__file__), "models.lock")`; module docstring "pinned in models.lock, in this repository"; `load_model(path, lock=LOCK)` | The pin and the artifact sit in the same directory under the same control, so the hash proves the two files agree with each other, not that the model is authentic. The `lock` parameter also lets any caller supply its own lock file. | Someone with write access to the deploy directory on the ops server (or a compromised CI step) replaces the model and updates `models.lock` to match. The job then loads it without complaint and rebalancing runs on a tampered forecast. Impact is limited to bad dispatch decisions: JSON cannot execute code. | Deploy the module, model and lock as read-only to the job user, with a separate owner. Alternatively, verify a signature or a digest held outside the deploy directory. Drop the `lock` override from the production call path, or document that it is test-only. |
| 2 | Low | CONFIRMED (code order); PROBABLE (reachability) | `load_model`: `raw = open(path, "rb").read()` runs before `pinned(...)` | The loader reads any path in full, with no size limit, before checking whether the name is even in the lock. | If the path comes from config or the command line, a path like `/dev/zero` or a very large file exhausts memory on the server that holds the credentials. That is an availability problem, not a leak, since nothing is echoed back. | Call `pinned(basename)` first, then refuse files over a small size limit (for example `os.path.getsize` under 1 MB) before reading. Add a test that an unlisted name raises before any read. |
| 3 | Low | CONFIRMED | `pinned`: `file_name, digest = line.split()` | A blank line, a comment, or a third field in `models.lock` raises an unpacking `ValueError`. That is the same exception type as a hash mismatch. | Someone adds a trailing blank line or a `# comment` to the lock, and every load fails with `ValueError`. A caller that treats `ValueError` as "tampered model" raises a false alarm or masks the real cause. It still fails closed. | Skip blank and `#` lines. Raise a distinct error for a malformed lock. Add a test with a blank line in a temporary lock. |
| 4 | Low | CONFIRMED | `predict` | `hour` is not validated. A float such as `24.0` or `None` raises `TypeError`, and the model shape (24 integers) is not checked after loading. | The caller passes `datetime.hour / 1` or a float from arithmetic, and the job crashes mid-run. The shipped model does have 24 entries, which I counted. | Coerce `hour` with `int` or reject non-integers. Assert `len(per_hour) == 24` in `load_model`. |
| 5 | Low | CONFIRMED | `load_model` and `pinned` use bare `open(...)`; tests use `tempfile.mkdtemp()` | File handles are never explicitly closed, and the temporary directories are never cleaned up. | This is harmless on CPython because handles close when they go out of scope. It leaks handles on other Python runtimes and leaves temp directories behind on each test run. | Use `with open(...)`, and `tempfile.TemporaryDirectory()` in the tests. |

## What holds up

- **No code execution.** `json.loads` cannot run code, so the "plain JSON weights, never code" docstring is accurate. Given the stakes, this matters most. The module never touches the credentials, the network, subprocesses, pickle or eval.
- **No race between check and use.** The bytes are read once, and those same bytes are both hashed and parsed.
- **Fails closed.** An unknown name raises `KeyError`, a mismatched hash raises `ValueError`, and the error messages contain no file contents.
- **Basename lookup is safe.** A file with the right name in another directory still has to match the hash.
- **The tests guard real behaviour,** judged by reasoning since I could not run mutations:
  - If the hash comparison is removed, `test_a_changed_copy_is_refused` goes red. An appended space is still valid JSON, so the expected `ValueError` can only come from the hash check.
  - If the `KeyError` branch is removed, `pinned` returns `None`, the mismatch raises `ValueError`, and `test_a_model_not_in_the_lock_is_refused` goes red because it expects `KeyError`.
  - If `% 24` is removed, index 25 raises `IndexError`, and `test_predict_uses_the_hour` goes red.

## Unverified claims

- **The pinned digest is correct** (`3fd1600a…e882`). Run `sha256sum demand-2026-09.json` on the exact deployed bytes, and watch for a trailing newline.
- **"4 tests pass."** No output was provided. Run `python -m unittest -v test_forecast` on the ops-server checkout.
- **The mutation reasoning above.** Confirm it by deleting each guard in a scratch copy and checking that the matching test goes red.
- **Deployment permissions.** Run `ls -l` on the module directory on the ops server, and identify the job's user.

## Questions for the author

1. Who can write to the directory holding `forecast.py`, the model and `models.lock` on the ops server? Is that the same account the job runs as? A "yes" raises finding 1 to High.
2. Where does `path` come from: hardcoded, config, or the command line? This decides whether finding 2 matters.
3. Today is 2026-10-08 and the only pinned model is `demand-2026-09`. Is the job meant to run on September's model, and how does a new month's model get pinned and reviewed?

## Decision-maker summary

The loader is safe to run in the sense that matters most here: it cannot execute code and it refuses any unlisted or altered model. Before the job runs on the ops server, make the model and lock files read-only to the job's account, and confirm the pinned hash and the passing tests on that machine. Otherwise, anyone who can write those files can feed the job a fake forecast unnoticed, and the September model may already be out of date.

## Owner summary

The new forecast loader only reads plain numbers and rejects files that have been changed, so it cannot be used to run harmful code on the server. Its protection only works if the files it checks against cannot be edited by the account that runs the job, and that still needs to be set up and confirmed. Someone should also confirm the model in use is the right month's.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "forecast.py LOCK = os.path.join(os.path.dirname(os.path.abspath(__file__)), \"models.lock\"); docstring 'pinned in models.lock, in this repository'; load_model(path, lock=LOCK)",
      "scenario": "Anyone with write access to the deploy directory (or a compromised CI step) replaces the model and updates models.lock to match; the hash check passes and the rebalancing job runs on a tampered forecast. The caller-overridable lock parameter allows the same bypass.",
      "fix": "Deploy module, model and lock read-only to the job user with a separate owner, or verify a signature or a digest held outside the deploy directory; keep the lock override out of production use."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "forecast.py load_model: raw = open(path, \"rb\").read() before pinned(...)",
      "scenario": "If path is caller- or config-controlled, a path such as /dev/zero or a huge file is read fully before the lock check, exhausting memory on the server that holds the credentials.",
      "fix": "Check the basename against the lock first, cap the file size before reading, and add a test that an unlisted name raises before any read."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "forecast.py pinned: file_name, digest = line.split()",
      "scenario": "A blank line, comment or extra field in models.lock raises an unpacking ValueError, the same type as a hash mismatch, so every load fails and the cause looks like tampering.",
      "fix": "Skip blank and comment lines, raise a distinct error for a malformed lock, and add a test with a blank line in a temporary lock."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "forecast.py predict(model, hour)",
      "scenario": "A float or None hour raises TypeError and crashes the job; the per_hour length is never validated after load.",
      "fix": "Coerce or validate hour as an int and assert len(per_hour) == 24 in load_model."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "forecast.py open(...) without a with block; test_forecast.py tempfile.mkdtemp()",
      "scenario": "File handles are not explicitly closed (harmless on CPython, leaks on other runtimes) and temp directories accumulate on each test run.",
      "fix": "Use with open(...) and tempfile.TemporaryDirectory()."
    }
  ]
}
```