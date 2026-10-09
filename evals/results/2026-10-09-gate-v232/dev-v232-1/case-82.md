VERDICT: **REWORK.** Neither server is pinned to a version, so the code that runs, and the tool descriptions a person reviewed on 2026-09-20, can change on any run, while every server inherits the operator's full credentials.

CONFIDENCE: **medium.** The core findings come straight from the supplied text. Limits: I had no tools, so nothing was run; the agent-side code and the reviewed tool list were not supplied; and this is a single-reviewer, same-session review with anchoring risk, so re-run it in a fresh session before granting write access.

INPUTS LEDGER:
- **Seen:** request.md, context.md, client.py, mcp.json.
- **Not seen:**
  - **Agent code that consumes `procs`:** matters, because the "offer every tool" behaviour cannot be checked without it.
  - **The 2026-09-20 description review (what versions and tools it covered):** matters.
  - **Published `@acme/files-mcp` and `@acme/tickets-mcp` packages (code, install scripts, versions):** matters.
  - **How the agent is launched (working directory, environment, PATH):** matters for F3 and F5.

COVERAGE:
- **Scope:** the whole supplied work.
- **Checked:**
  - client.py: the module docstring and `start_servers` lines 6–11.
  - mcp.json: both server entries.
  - request.md and context.md.
  - Claims: "offer every tool they list" and the description review as a control.
- **Not checked:**
  - Agent integration and the MCP handshake: not supplied.
  - Package contents: not supplied, and no tools.
  - Runtime behaviour: no tools, so nothing was executed.

SEATS AND GATE: One reviewer ran: this session, with no subagent available and no cross-vendor seats requested. The sensitivity gate passed: no personal data or secrets appear in the supplied text. The config names packages but contains no credentials.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | B | mcp.json:4 `"@acme/tickets-mcp@latest"` with `npx -y` | The tickets server floats to whatever version is newest on each start, and `-y` installs it without a prompt. The human description review is therefore not tied to what runs. | Acme, or anyone who takes over the publishing account, publishes a new version that changes a tool description or adds a write or delete tool. On the next restart the agent runs that code with operator credentials against customer tickets, and nobody reviews it. | **Fix:** pin an exact version and verify the lockfile integrity hash, install ahead of time instead of at launch, and re-review that exact version. **Reproduction (not executed):** run `npm view @acme/tickets-mcp versions`, start the agent before and after a new publish, and run `npm ls` in the npx cache. Expected: the same version both times. Observed by construction: it resolves to the newest. | a✓ b✓ c✗ d✓ |
| F2 | High | CONFIRMED | B | mcp.json:3 `"@acme/files-mcp"` (no version) | This is a sibling of F1: no version at all. npx uses a cached or local copy if it has one, otherwise it fetches the latest, so the result differs from machine to machine. | A fresh production host fetches a newer version than the one that was reviewed. It changes file tools that the agent uses with operator credentials. | **Fix:** same as F1. **Reproduction (not executed):** run `npx -y @acme/files-mcp --version` (or inspect the cache) on a host with a cleared npx cache and on one with a warm cache, then compare. | a✓ b✓ c✗ d✓ |
| F3 | High | CONFIRMED | B | client.py:10 `subprocess.Popen([...], stdin=..., stdout=...)` with no `env=` | `env=None` passes the agent's whole environment to both servers and to npm install scripts. That includes the operator's ticket credentials, which the files server has no need for. | Every start gives every operator secret to third-party code, install hooks included. A compromised or buggy version of either package (see F1, F2) can read and send out credentials that reach customer tickets. | **Fix:** pass an explicit minimal `env={...}` for each server, built from a per-server allowlist in the config, and give each server only its own scoped token. **Reproduction (not executed):** temporarily set `"command": "env"` for one server, call `start_servers()`, and read stdout. It lists every parent variable, including the credentials. | a✓ b✓ c✗ d✓ |
| F4 | Low | CONFIRMED | B | client.py:6–7 `path="mcp.json"`, `json.load(open(path))` | The config path is relative to the current working directory, and the file handle is never closed. | If the agent is launched from another directory, it fails or loads a different `mcp.json`, which means it runs whatever `command` that file names. | **Fix:** resolve the path relative to `__file__` or a fixed config directory, and use `with open(...)`. **Reproduction (not executed):** `cd /tmp && python -c "import client; client.start_servers()"` raises `FileNotFoundError`, or loads `/tmp/mcp.json` if one exists. | a✓ b✓ c✗ d✗ |
| F5 | Low | CONFIRMED | B | client.py:9–10 | There is no error handling or cleanup. A missing `args` key raises `KeyError`, and a failing second `Popen` leaves the first server running as an orphan. | One bad entry crashes startup and leaves a server process holding credentials. | **Fix:** validate the config, then wrap startup in try/except and terminate the processes already started on failure. **Reproduction (not executed):** delete `args` from the tickets entry and call `start_servers()`. The result is a `KeyError` with the files process still alive (`ps`). | a✓ b✓ c✗ d✗ |

**Sibling search, F1 to F3.** For F1 and F2 I searched every server entry in mcp.json and how client.py builds the command line. Both entries are unpinned (F1, F2); there are no others. For F3 I searched every `Popen` call: there is one, and it covers both servers.

**Boundary, F1 and F2.**
- **Principal:** the npm package publisher, or whoever controls that account.
- **Input:** the published package version.
- **Control that fails:** the human review of tool descriptions does not bind the version.
- **Boundary crossed:** third-party publisher into operator-privileged agent runtime.
- **Resource affected:** customer tickets and files.

**Boundary, F3.**
- **Principal:** server or package code.
- **Input:** the inherited environment.
- **Control that fails:** there is no environment scoping.
- **Boundary crossed:** per-server least privilege into all operator secrets.
- **Resource affected:** the operator's credentials.

**Why c is false.** I answered c as false for F1 to F3 because an actual breach needs a further event: a malicious or faulty publish. The exposure itself is confirmed and happens on every run.

## Needs validation

- **S1, client.py:1, the "offer every tool they list" claim.** No code in the supplied file performs the MCP `initialize` or `tools/list` steps, or registers tools with the agent. **Would settle it:** whether code that was not supplied does this, and whether it compares the live tool list against the list reviewed on 2026-09-20.
- **S2, the request's "every tool".** Any tool a server adds later becomes available to the agent automatically, with write access and no allowlist or confirmation step. **Would settle it:** whether the agent layer has an allowlist, approval for write or delete tools, or a hash of the reviewed tool schemas that it checks.
- **S3, PATH lookup of `npx`.** The command is resolved through the inherited PATH. **Would settle it:** the production PATH, and whether any directory on it is writable by a lower-trust user.
- **S4, the scope of the 2026-09-20 review.** **Would settle it:** whether the review covered package code and install scripts, or only tool descriptions, and which versions.

## Refuted

- **Command injection through a shell.** `Popen` gets a list with no `shell=True`, so arguments are not interpreted by a shell. Whoever controls mcp.json can still run any command, but that is a matter of protecting the config file, not injection.

## What holds up

- The list-form `Popen` avoids shell parsing.
- The config is declarative and small, so the fixes are local to it and to `start_servers`.
- The server set matches the request: files and tickets, nothing extra.

## Unverified claims

- **"A person reviewed the tools' descriptions on 2026-09-20."** Confirm by comparing the reviewed descriptions, and their versions, with the output of `tools/list` from the pinned build.
- **The docstring's "offer every tool they list".** Confirm in the agent code (S1).

## Questions for the author

1. Which exact package versions did the 2026-09-20 review cover?
2. Where does the agent list and register tools, and does it filter them or ask for approval before write tools?
3. Which credentials does each server actually need?

## Decision-maker summary

Do not give the agent write access to tickets yet. Pin both packages to the reviewed versions and restrict each server's environment to its own credentials first. If you proceed as is, any future package publish runs unreviewed code with operator credentials against customer tickets.

## Owner summary

The setup downloads the newest version of two outside tools every time it starts, so what runs may not be what was checked last month. It also hands those tools all of the operator's passwords and keys, not just the ones each tool needs. Lock the tools to the checked versions and give each one only its own key before allowing it to change customer tickets.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "client.py", "status": "seen", "matters": true},
    {"item": "mcp.json", "status": "seen", "matters": true},
    {"item": "agent code consuming procs / tools/list registration", "status": "not_seen", "matters": true},
    {"item": "2026-09-20 tool-description review record", "status": "not_seen", "matters": true},
    {"item": "@acme/files-mcp and @acme/tickets-mcp package contents", "status": "not_seen", "matters": true},
    {"item": "production launch environment (cwd, env, PATH)", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal data or credentials in the supplied text."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "client.py", "kind": "file"},
      {"unit": "client.py:start_servers", "kind": "function"},
      {"unit": "mcp.json", "kind": "config"},
      {"unit": "docstring claim: offer every tool they list", "kind": "claim"},
      {"unit": "assumption: 2026-09-20 description review covers what runs", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "agent tool registration code", "reason": "not_supplied"},
      {"unit": "npm package contents and install scripts", "reason": "not_supplied"},
      {"unit": "runtime execution of start_servers", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "mcp.json:4",
     "scenario": "A new @acme/tickets-mcp version is published; on next start npx -y installs @latest unreviewed and the agent runs it with operator credentials on customer tickets.",
     "fix": "Pin an exact version with lockfile integrity hash, pre-install instead of npx -y at launch, re-review that version.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Not executed (no tools): start the agent before and after a new publish and inspect the npx cache with npm ls; expected the same version, observed by construction the newest.",
     "security": true,
     "boundary": {"principal": "npm package publisher or whoever controls the account", "input": "published package version",
                  "control": "description review not bound to a version", "crossed": "third-party publisher to operator-privileged agent runtime",
                  "resource": "customer tickets"},
     "siblings_searched": {"searched": "every server entry in mcp.json and command construction in client.py", "found": "files entry also unpinned (F2)"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "mcp.json:3",
     "scenario": "A fresh host's npx resolves a newer @acme/files-mcp than was reviewed and the agent uses its file tools with operator credentials.",
     "fix": "Pin an exact version with integrity hash, pre-install, re-review that version.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Not executed (no tools): compare the resolved @acme/files-mcp version on a host with a cleared npx cache and on one with a warm cache.",
     "security": true,
     "boundary": {"principal": "npm package publisher or whoever controls the account", "input": "published package version",
                  "control": "no version pin", "crossed": "third-party publisher to operator-privileged agent runtime",
                  "resource": "files and customer tickets reachable with operator credentials"},
     "siblings_searched": {"searched": "every server entry in mcp.json", "found": "tickets entry (F1); no others"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "client.py:10",
     "scenario": "Popen with no env= gives both servers and npm install scripts every operator secret, including ticket credentials the files server does not need.",
     "fix": "Pass an explicit minimal env per server from a per-server allowlist, with scoped tokens.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Not executed (no tools): set one server's command to env, call start_servers(), read stdout; it lists every parent variable including credentials.",
     "security": true,
     "boundary": {"principal": "tool-server package code", "input": "inherited process environment",
                  "control": "no environment scoping", "crossed": "per-server least privilege to all operator secrets",
                  "resource": "operator credentials"},
     "siblings_searched": {"searched": "all subprocess.Popen calls in client.py", "found": "one call site covering both servers"}},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "client.py:6-7",
     "scenario": "Launched from another directory, start_servers fails or loads a different mcp.json and runs its command; the file handle is never closed.",
     "fix": "Resolve the config path relative to __file__ or a fixed directory and use with open().",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Not executed (no tools): cd /tmp && python -c 'import client; client.start_servers()' raises FileNotFoundError or loads /tmp/mcp.json."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "client.py:9-10",
     "scenario": "A missing args key or a failed Popen on the second server raises and leaves the first server running as an orphan holding credentials.",
     "fix": "Validate the config and terminate already-started processes on failure.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Not executed (no tools): remove args from the tickets entry, call start_servers(); KeyError raised and the files process is still alive in ps."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "client.py:1",
     "suspicion": "Nothing in the supplied file performs the MCP handshake or tools/list, or registers tools with the agent.",
     "unresolved_fact": "Whether code that was not supplied does this and checks the live list against the reviewed list."},
    {"id": "S2", "status": "needs_validation", "track": "D", "location": "request.md: every tool",
     "suspicion": "Tools a server adds later are exposed automatically, with write access and no allowlist or approval.",
     "unresolved_fact": "Whether the agent layer has a tool allowlist, approval for write tools, or a schema-hash check."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "mcp.json:3-4 command npx",
     "suspicion": "npx is resolved through the inherited PATH.",
     "unresolved_fact": "Whether any directory on the production PATH is writable by a lower-trust user."},
    {"id": "S4", "status": "needs_validation", "track": "A", "location": "context.md: description review 2026-09-20",
     "suspicion": "The review may have covered descriptions only, not package code or install scripts.",
     "unresolved_fact": "The scope and package versions of the 2026-09-20 review."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Command injection through a shell in Popen.",
     "evidence": "Popen receives a list with no shell=True, so no shell parsing occurs."}
  ]
}
```