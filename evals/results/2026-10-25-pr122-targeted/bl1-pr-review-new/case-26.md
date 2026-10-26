# PR #63 Review: limits from config

**Review report**

**REVIEWED:** PR #63, head `e07b3d8`, merge base `5a1c2f6`. Both SHAs come from PR.md and could not be checked against a repository. I reviewed the supplied `change.patch` against `base/`, not a throwaway checkout of the head. I ran nothing because this session has no tools.

**TIER: High.** These limits protect a shared production backend. The change decides which callers are throttled and what happens when the config is absent, which is access control and outage exposure even though the diff is small. Step 2: "When unsure, take the higher tier." Under High, this report is **round 1 of 2**. Step 2 says "a High-tier PR whose second round has not run is not reviewed." A second round, ideally on a different vendor, is still required.

**REVIEWERS:** Round 1 is this instance, claude-opus-5-5, which did not write the change. The author is **unknown**: no commit trailers were provided. The code carries no personal data or secrets, so no extra data-handling restriction applied. Nothing was sent to another endpoint.

**Lenses:** The supply-chain lens does not apply because no dependency was added and the parser is hand-written. The runtime/TLS lens does not apply. No reviewer-directed instructions were found in the PR text.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `ratelimit.py:15-16`, `ratelimit.py:22-24` | **The limiter fails open.** If `config/limits.yaml` is missing (not deployed, wrong path, deleted by ops), `load_limits` swallows `FileNotFoundError` and returns `{}`. `allowed` then returns `True` for every plan. A plan missing from the file (a typo like `fre:`, or a new plan nobody added) is also unlimited. The base code raised `KeyError`, which failed closed. Today one missing file removes every limit that protects the shared backend, with no error or log. | Call `allowed("free", 10**9, load_limits("/nonexistent"))` and assert it is `False` or that it raises. Call `allowed("unknown", 10**9, {"free": 100})` and assert it is not `True`. Both fail today. |
| 2 | **P1** | `ratelimit.py:3` | `LIMITS_PATH = "config/limits.yaml"` resolves against the process's current working directory, not the module or repo. A service started from another directory (systemd unit, container `WORKDIR`, test runner) won't find the file. Combined with #1, the result is silent unlimited access. | Run `os.chdir(tmpdir)` and then `load_limits()` with the real config present in the repo. Assert the limits load, or that the call raises. It returns `{}` today. |
| 3 | **P1** | `ratelimit.py:12-14` | The parser is not YAML, though the file is named `.yaml`. Ordinary YAML that ops would reasonably write crashes the load with an uncaught `ValueError`: `free: 100  # per day` (inline comment), `free: "100"` (quoted), a nested `plans:` header (`int("")`), or `pro: 1_000`. The result is a crash on load (outage) for a config edit that is valid YAML. Negative or zero values are also accepted without validation. | Feed `load_limits` a temp file containing `free: 100  # per day` and expect `{"free": 100}` or a clear validation error. Feed it `free: -1` and expect rejection. Today the first raises `ValueError` from `int()` and the second loads silently. |
| 4 | **P1** | `ratelimit.py:6` (no call site in patch) | The request was that ops can change limits **without a deploy**. The patch adds `load_limits` but no caller in the diff calls it, and `allowed` still takes `limits` as a parameter. Nothing shows when the file is read. If callers load once at startup, a change needs a restart. If nothing calls it, the feature does nothing. The request is not shown to be met. | An integration test: start with `free: 1`, edit the file to `free: 5` without restarting, and assert the 2nd request is now allowed. It cannot pass with the code shown. |
| 5 | **P2** | `tests/test_ratelimit.py:6-9` | "Tests pass" is a claim, and I did not see the test run. The one test exercises `allowed` with a hand-built dict, and that behavior was already correct in the base. Nothing tests `load_limits`, a missing file, an unknown plan, comments or malformed lines. #1–#3 all ship under a green suite. | Add the tests from #1–#3. |
| 6 | **P1** | `PR.md` (claim about commit `91c4e7a`) | PR.md says the config file and its values are added in `91c4e7a`. That commit and file were not provided. If `91c4e7a` is not an ancestor of `e07b3d8`, merging deploys the loader without the file, and #1 then makes every plan unlimited in production. The configured values also cannot be checked against the limits that are hard-coded or passed today. | `git merge-base --is-ancestor 91c4e7a e07b3d8`, and a test asserting that `config/limits.yaml` exists in the repo and that `load_limits()` returns every plan in the plan catalogue. |

**FILES NEEDED BUT NOT PROVIDED:**
- `config/limits.yaml` at `e07b3d8`
- commit `91c4e7a` and its relation to the head
- every caller of `ratelimit.allowed` / `load_limits`, which shows how and when limits are loaded
- the plan catalogue (the list of valid plans)
- CI results for `e07b3d8`
- commit trailers, to identify the author

---

**Close-out**

ADJUDICATION: **Not yet written.** The author must adjudicate each finding. A reviewer never adjudicates its own findings. Findings #1, #2, #3, #4 and #6 are P0/P1, so they cannot be deferred. Each must be Accepted, with a fix commit, a regression test and a read of the fix diff, or Rejected with evidence.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1–6 | pending | — |

VERIFIED AFTER FIXES: Nothing yet, because no fixes have been made.

**MERGE RECOMMENDATION: Do not merge.** Several conditions fail:

- **Step 8:** "Recommend merge only when all of these hold: every round the tier requires has run, and every finding has a written decision; every expected check is present and green …; no unresolved blocker remains." The second High-tier round has not run, and no finding has a decision.
- **Step 8:** No CI check was provided, and "a missing check is not green."
- **P0 #1 is an open blocker.** The limiter fails open and lifts every limit on the shared backend.

Suggested direction for the author:
- On a missing or unparseable file, fail closed or refuse to start.
- Deny or default-limit plans that are not in the file.
- Resolve the path explicitly.
- Use a real YAML parser with validation, with the dependency then reviewed under the supply-chain lens.
- Show where reload happens.

These suggestions are UNVERIFIED until they are checked against the callers and the config, neither of which was provided.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "code-read (not executed)",
      "location": "ratelimit.py:15-16, ratelimit.py:22-24",
      "scenario": "Missing config file is swallowed and returns {}; allowed() returns True when a plan has no limit, so a missing file or unknown/typo'd plan gets unlimited requests against the shared backend. Base code failed closed with KeyError.",
      "fix": "Fail closed: raise or refuse to start on a missing file; deny or apply a default limit for unknown plans; log loudly. Add regression tests for both cases."
    },
    {
      "severity": "P1",
      "evidence_level": "code-read (not executed)",
      "location": "ratelimit.py:3",
      "scenario": "Relative path resolves against the process CWD; a service started elsewhere finds no file and, via finding 1, silently runs with no limits.",
      "fix": "Resolve the path relative to the module or take an explicit configured absolute path; test load_limits() after chdir."
    },
    {
      "severity": "P1",
      "evidence_level": "code-read (not executed)",
      "location": "ratelimit.py:12-14",
      "scenario": "Hand-rolled parser rejects valid YAML (inline comments, quoted values, nested keys, 1_000), raising an uncaught ValueError on load and causing an outage; negative or zero limits are accepted without validation.",
      "fix": "Use a real YAML parser with schema validation (positive ints, known plans), and review that dependency; add malformed-input tests."
    },
    {
      "severity": "P1",
      "evidence_level": "code-read; callers not provided",
      "location": "ratelimit.py:6",
      "scenario": "load_limits has no call site in the patch, so nothing shows limits are reloaded at runtime; the request ('change without a deploy') is not demonstrated and may need a restart or do nothing.",
      "fix": "Wire loading into the request path with defined reload semantics (e.g. mtime check or TTL) and add an integration test that edits the file without a restart."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read; test run not observed",
      "location": "tests/test_ratelimit.py:6-9",
      "scenario": "'Tests pass' covers only allowed() with a hand-built dict, which is unchanged base behavior; load_limits and the fail-open paths are untested, so findings 1-3 ship under a green suite.",
      "fix": "Add tests for missing file, unknown plan, CWD independence and malformed or commented lines."
    },
    {
      "severity": "P1",
      "evidence_level": "unverified; artifact not provided",
      "location": "PR.md (reference to commit 91c4e7a and config/limits.yaml)",
      "scenario": "Config file and commit 91c4e7a were not provided; if 91c4e7a is not an ancestor of e07b3d8, merging ships the loader without the file and every plan becomes unlimited in production.",
      "fix": "Confirm ancestry (git merge-base --is-ancestor 91c4e7a e07b3d8), include the file in the reviewed head, and add a test that it exists and covers every plan."
    }
  ]
}
```