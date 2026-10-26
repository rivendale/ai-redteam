# PR #63 review: limits from config

**Review report**

**REVIEWED:** PR #63, head `e07b3d8`, merge base `5a1c2f6`. Both SHAs are short forms taken from PR.md. I could not check them against a repository because this session has no tools. I reviewed the text supplied: PR.md, change.patch and base/. I did not create a worktree and did not run any code. PR.md says commit `91c4e7a` adds `config/limits.yaml`. That commit is not in the supplied patch, and nothing shows whether it is an ancestor of `e07b3d8`.

**TIER:** High. The change controls how much traffic reaches a shared production backend. The new code also decides what happens when limits are missing or malformed, so a fault here becomes an outage or capacity exposure for every tenant. High requires two rounds, ideally on two vendors. **This is round 1 of 2. Round 2 has not run, so the PR is not yet reviewed.**

**DATA (Step 3):** The code carries no personal data, secrets or credentials. Nothing was sent outside this session.

**REVIEWERS:** This session (Claude Opus 5.5, `claude-opus-5-5`), a separate instance that did not write the change. No commit trailers were supplied, so the author cannot be identified from them.

**Lenses:** The supply-chain lens does not apply. No dependency was added, and notably no YAML library. The runtime/TLS lens does not apply. I found no text in the PR addressed to the reviewer.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P0 | `ratelimit.py:15-16` with `ratelimit.py:22-24` | **Missing file means no limits at all.** If `config/limits.yaml` is absent, `FileNotFoundError` is swallowed and `{}` is returned. `allowed()` then returns `True` for every plan and every count. Causes include a deploy that omits the file, a typo in the path or a volume that is not mounted. Every customer gets unlimited requests against the shared backend, and nothing is logged. The base code failed closed: `limits[plan]` raised. | `load_limits("/nonexistent")` should raise or return a fail-closed default. Asserting `allowed("free", 10**9, load_limits("/nonexistent"))` is `False` (or raises) fails today. |
| 2 | P0 | `ratelimit.py:22-24` | **Unknown plan means unlimited.** Any plan missing from the config is unlimited, for example a new plan not yet added, or a case or spelling mismatch (`Pro:` vs `pro`). Before this change it raised `KeyError`. This change in behavior was not requested; the request was only to move the values into config. | `allowed("enterprise", 10**9, {"free": 100})` should not return `True`. It does today. |
| 3 | P1 | `ratelimit.py:3`, used at `ratelimit.py:10` | **Path depends on the working directory.** `"config/limits.yaml"` is resolved against the process working directory, not the module or app root. If the service starts from another directory (systemd `WorkingDirectory`, a container `WORKDIR`, a test runner), the file is not found and finding 1 applies silently. | Call `os.chdir(tmpdir)` then `load_limits()`. Today it returns `{}` even though the repo file exists. |
| 4 | P1 | `ratelimit.py:12-14` | **The file is named YAML, but the parser is not YAML.** Two failure modes: (a) Ordinary YAML that ops is likely to write crashes loading with an uncaught `ValueError`, giving an outage at startup or reload. Examples: `free: 100  # daily cap` makes `int("100  # daily cap")` fail; a nesting header such as `limits:` makes `int("")` fail. (b) Quoted keys such as `"free": 100` are stored as `'"free"'`, never match, and fall through to finding 2, so that plan is unlimited. | Feed `free: 100  # cap` and `"pro": 1000`. Assert `{"free": 100, "pro": 1000}`. Today the first raises and the second yields the wrong key. |
| 5 | P2 | `ratelimit.py:14` | **No value validation.** `free: -1` blocks everyone on that plan. `free: 0` blocks the plan entirely. A duplicated key silently overrides the earlier one, last one wins. An ops edit with no deploy and no review can therefore lock out a plan or change a limit without any signal. | Parse a file with a negative value and a duplicate key. Assert a rejection or error. Today both are accepted silently. |
| 6 | P2 | `tests/test_ratelimit.py:7-10` | **"Tests pass" covers only the unchanged comparison.** The single test checks `allowed()` with an in-memory dict. Nothing covers `load_limits`, the missing-file path, an unknown plan or parsing, which are exactly the new behaviors behind findings 1-4. I have not seen or run the claim that tests pass. | Add tests for findings 1-4. Each fails today, except a missing-file test that asserts the current fail-open behavior, which would pass and expose it. |

## FILES NEEDED BUT NOT PROVIDED

- **`config/limits.yaml` at head `e07b3d8`.** I need its values, and whether it exists at that head at all. This decides whether finding 4 triggers on the real file, and whether the current limits are preserved.
- **Commit `91c4e7a`.** I need its diff and whether it is reachable from `e07b3d8`. If it is not in the PR, the PR ships without its config and finding 1 fires in production.
- **The caller(s) of `allowed()` and `load_limits()`.** No caller appears in the diff. Without them I cannot tell:
  - whether the service uses the file at all, or still passes hardcoded limits;
  - whether limits load once at startup, so a change needs a restart rather than a deploy, which is a request-scope question;
  - whether a crash from finding 4 takes down the process.
- **CI check results for the head.**

---

**Close-out**

Pending. The author must adjudicate findings 1-6, and a reviewer does not adjudicate its own findings. Findings 1-4 are P0/P1 and cannot be deferred.

**ADJUDICATION:** none yet.

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION: do not merge.**
- Two P0 findings are open: fail-open on a missing file, and fail-open on an unknown plan.
- Two P1 findings are open.
- The second High-tier round has not run.
- The config file and commit `91c4e7a` it depends on were not provided.
- No CI checks were seen.
- One owner decision is pending: the fail-safe policy when config is missing or invalid. The options are to refuse to start, keep the last good config, or apply a conservative default. Operations and the backend owner should make this call, not the author alone.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "static_read_of_diff",
      "location": "ratelimit.py:15-16, ratelimit.py:22-24",
      "scenario": "config/limits.yaml absent (not deployed, unmounted, wrong path): FileNotFoundError swallowed, {} returned, allowed() returns True for all plans; unlimited traffic to shared backend with no log. Base code failed closed.",
      "fix": "Fail closed: raise on missing file at startup (or keep last-known-good / conservative default per owner decision) and log loudly."
    },
    {
      "severity": "P0",
      "evidence_level": "static_read_of_diff",
      "location": "ratelimit.py:22-24",
      "scenario": "Plan not present in config (new plan, case/typo mismatch) is treated as unlimited; previously raised KeyError. Unrequested behavior change.",
      "fix": "Deny or apply an explicit default limit for unknown plans; validate at load that all known plans are configured."
    },
    {
      "severity": "P1",
      "evidence_level": "static_read_of_diff",
      "location": "ratelimit.py:3, ratelimit.py:10",
      "scenario": "Relative path resolved against process CWD; service started from another directory finds no file and silently fails open via finding 1.",
      "fix": "Resolve path relative to app root or take it from explicit configuration/env; fail if not found."
    },
    {
      "severity": "P1",
      "evidence_level": "static_read_of_diff",
      "location": "ratelimit.py:12-14",
      "scenario": "Hand parser on a .yaml file: inline comments or nesting headers raise uncaught ValueError (outage on load); quoted keys stored with quotes, never match, plan becomes unlimited.",
      "fix": "Use a real YAML parser (yaml.safe_load) with schema validation, or rename to a documented simple format and reject anything it cannot parse."
    },
    {
      "severity": "P2",
      "evidence_level": "static_read_of_diff",
      "location": "ratelimit.py:14",
      "scenario": "Negative/zero values and duplicate keys accepted silently; an ops edit without deploy can lock out a plan or change a limit unnoticed.",
      "fix": "Validate values are positive integers and reject duplicate keys; log the loaded limits."
    },
    {
      "severity": "P2",
      "evidence_level": "static_read_of_diff; tests not run",
      "location": "tests/test_ratelimit.py:7-10",
      "scenario": "Only the pre-existing comparison is tested; load_limits, missing file, unknown plan and parsing are untested, so 'Tests pass' does not cover the new behavior.",
      "fix": "Add tests for missing file, CWD independence, unknown plan, comments/quoted keys and invalid values."
    }
  ]
}
```