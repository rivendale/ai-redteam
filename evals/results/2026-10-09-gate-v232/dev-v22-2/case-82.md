# Redteam report: tool-server wiring (`client.py`, `mcp.json`)

**VERDICT: REWORK.** The server packages are not pinned, so the code that will run with the operator's credentials is not the code whose tool descriptions were reviewed on 2026-09-20. Separately, `client.py` starts processes but does not list or offer any tools.

**CONFIDENCE: medium.** I had no tools in this session, so nothing was run, fetched or resolved against the npm registry. The findings come from reading the two supplied files. The work was not written in this conversation, so the review is independent of its author. The agent code and the reviewed tool descriptions were not supplied.

**INPUTS LEDGER:**
- **Seen:**
  - The original request (verbatim).
  - `context.md`.
  - `client.py` (11 lines).
  - `mcp.json`.
- **Not seen, and each gap matters:**
  - **The record of the 2026-09-20 description review**, including which package versions it covered. This decides whether the review applies to what runs today.
  - **Any agent-side code** that does the MCP handshake (`initialize`, `tools/list`) or registers tools. This decides whether F2 is a gap only in this file or in the whole system.
  - **The `@acme/*` packages themselves, their published versions, any lockfile and `.npmrc`.** These decide F1's exposure window and whether the package names are genuine.
  - **What the files server can reach by default.** This decides how serious the cross-tool risk in S1 is.

**COVERAGE:**
- **Checked:**
  - `client.py`, including `start_servers` (lines 6–11).
  - `mcp.json` (lines 3–4).
  - The assumption "the reviewed descriptions equal the running descriptions".
  - The assumption "start_servers implements the request".
- **Not checked:**
  - Package contents and versions (no network access).
  - The agent loop.
  - The scope of the files server.
  - The tickets server's write semantics.
  - Credential provisioning.

**SEATS AND GATE:**
- No personal data, credentials or client material appear in the supplied work, so the sensitivity gate passed.
- No subagent or cross-vendor seats were available. This was a single reviewer with no tools.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | B | `mcp.json:3-4` | `@acme/files-mcp` has no version and `@acme/tickets-mcp@latest` floats. `npx -y` resolves and installs from the registry on every start, without prompting, and runs install scripts. The 2026-09-20 description review is therefore bound to nothing. | Any release after 2026-09-20 (an ordinary update, a compromised maintainer account, or a malicious publish) is pulled at the next restart. It then runs with the operator's environment. The agent offers whatever tools and descriptions that release lists, including new write tools or changed descriptions that carry injected instructions, with no human seeing the change. | Pin exact versions (`@acme/tickets-mcp@X.Y.Z`) and install from a lockfile with integrity hashes, not `npx -y` at runtime. Record the reviewed versions next to the review. At startup, hash the `tools/list` result (names, descriptions, schemas) and refuse to start if it differs from the reviewed hash. **Reproduction:** run `npm view @acme/tickets-mcp time` and compare the release dates with 2026-09-20. Any later release means production is running unreviewed code. | a✓ b✓ c✗ d✓ |
| F2 | High | PROBABLE | B | `client.py:1`, `client.py:6-11` | The docstring says the code will "offer every tool they list". The function only `Popen`s the processes and returns them. There is no MCP `initialize`, no `tools/list`, nothing reads from the pipes, and no tools are registered with the agent. The work is presented as complete but delivers only part of the request. | The agent starts with both servers running and zero tools available. Alternatively, a caller assumes tools are wired and nothing is. If a server writes more output to the unread stdout pipe than the pipe buffer holds, it blocks. | Implement the stdio MCP client: send `initialize` and `notifications/initialized`, call `tools/list`, register the tools, and route `tools/call`. Better, use the official MCP SDK client. **Test:** start with a stub server that lists one tool, then assert the agent's tool registry contains it. On the current code that assertion fails. Evidence is PROBABLE because the handshake may exist in code that was not supplied. | a✓ b✗ c✓ d✓ |
| F3 | Medium | CONFIRMED | B | `client.py:10` | `Popen` is called without `env=`, so each server inherits the agent's full environment. The files server receives the ticket credentials, and both receive any other operator secrets. | A malicious or buggy release of the files package (see F1) reads the tickets or operator token from `os.environ` and sends it elsewhere. It never needed that token. | Pass a minimal `env` to each server containing only its own credential, `PATH` and anything else strictly required. **Reproduction:** set `FOO=secret` and start a server whose command is `env`; observe `FOO` in its output. | a✓ b✓ c✗ d✗ |
| F4 | Medium | PROBABLE | B | `client.py:7-11` | There is no startup health check or error handling. `Popen` succeeds whenever `npx` exists, even if the package fetch fails or the server exits at once. A missing `args` key raises `KeyError`. The file handle from `open(path)` is never closed. | The registry is unreachable or the package is yanked. The process exits, `start_servers` reports success, and the failure only shows up later as a broken pipe in the middle of a ticket action. | After spawn, complete the `initialize` handshake within a timeout and fail fast on a non-zero exit. Use `with open(...)` and `spec.get("args", [])`. **Reproduction:** point `args` at a package that does not exist, call `start_servers()`, and observe that it returns normally. | a✓ b✗ c✗ d✓ |

## NEEDS VALIDATION

- **S1: cross-tool exfiltration path.** Ticket bodies come from customers and are untrusted input to the agent. If the files server can read local secrets and the tickets server can post replies the customer can see, then a ticket containing injected instructions can make the agent read a file and paste it into a reply. "Every tool" plus ticket write access opens that path.
  - *What would settle it:* the actual `tools/list` output of both servers, the filesystem root the files server exposes by default (its `args` set no root), and whether ticket writes reach customers.
- **S2: package identity.** It is not established that `@acme/files-mcp` and `@acme/tickets-mcp` are the vendor's genuine packages rather than look-alikes, or that `.npmrc` points to the intended registry.
  - *What would settle it:* the publisher and maintainers on the registry, the source repository link, and the project's `.npmrc`.
- **S3: approval for write tools.** The request asks for every tool. The context says write access is the thing being gated. It is not established whether any tool call requires human approval.
  - *What would settle it:* the agent's tool-call policy.

## REFUTED

- **"Offering every tool is drift from the request."** Refuted. The request explicitly says "let it use every tool they offer". The risk this creates is covered under F1 and S1, not as drift.
- **"Shell injection via `Popen`."** Refuted. The command is passed as a list without `shell=True`. Its values come from a local config file, not from untrusted input.

## WHAT HOLDS UP

- The list form of `Popen` avoids shell interpretation.
- Server definitions are kept in config rather than hard-coded.
- The `{"servers": {...}}` structure is a reasonable shape for this config.

## UNVERIFIED CLAIMS

- **"A person reviewed the tools' descriptions on 2026-09-20."** To confirm, obtain the review record with the package versions it covered, and diff it against the current `tools/list` output.
- **The docstring's "offer every tool they list."** To confirm, find the agent-side code that calls `tools/list`. It is absent from the supplied files.

## QUESTIONS FOR THE AUTHOR

1. Which exact versions were reviewed on 2026-09-20, and what code performs the MCP handshake and tool registration?
2. Should write tools (ticket updates, file writes) require approval while this is first in production, or is unattended use intended?
3. Which directory does the files server expose?

## DECISION-MAKER SUMMARY

Do not grant ticket write access yet. Pin the server packages to the reviewed versions, check at startup that the tool list matches what was reviewed, and finish the tool wiring. If you proceed as is, any new release of either package runs unreviewed with the operator's credentials against customer tickets.

## OWNER SUMMARY

The setup always downloads the newest version of each tool add-on. The version that was checked by a person is not the one guaranteed to run, so an unreviewed or tampered update could act on customer tickets with full staff access. The connection code also does not yet hand the tools to the assistant, so the work is not finished. Lock the versions, give each add-on only the access it needs, and finish the connection before turning on ticket editing.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "client.py", "status": "seen", "matters": true},
    {"item": "mcp.json", "status": "seen", "matters": true},
    {"item": "2026-09-20 tool-description review record and versions covered", "status": "not_seen", "matters": true},
    {"item": "agent-side MCP handshake / tool registration code", "status": "not_seen", "matters": true},
    {"item": "@acme/files-mcp and @acme/tickets-mcp packages, lockfile, .npmrc", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Work contains config and code only; no personal data, credentials or client material."},
  "coverage": {
    "checked": [
      {"unit": "client.py", "kind": "file"},
      {"unit": "client.py:start_servers", "kind": "function"},
      {"unit": "mcp.json", "kind": "config"},
      {"unit": "reviewed descriptions equal running descriptions", "kind": "assumption"},
      {"unit": "start_servers implements 'offer every tool'", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "@acme/files-mcp package contents", "reason": "no tools; not supplied"},
      {"unit": "@acme/tickets-mcp package contents", "reason": "no tools; not supplied"},
      {"unit": "agent loop / tool registration", "reason": "not supplied"},
      {"unit": "files server default filesystem scope", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "mcp.json:3-4",
     "scenario": "A release of either package published after the 2026-09-20 review is fetched by 'npx -y' at the next restart and runs with the operator's environment; the agent offers its new or changed tools and descriptions with no human review.",
     "fix": "Pin exact versions installed from a lockfile with integrity hashes instead of runtime 'npx -y'; record the reviewed versions; hash the tools/list result at startup and refuse to start on mismatch with the reviewed hash.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Run 'npm view @acme/tickets-mcp time' and compare release dates with 2026-09-20; any later release means production runs unreviewed code."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "client.py:1, client.py:6-11",
     "scenario": "start_servers only spawns processes: no initialize, no tools/list, no tool registration, stdout never read; the agent starts with no tools despite the docstring claiming it offers every tool.",
     "fix": "Implement the stdio MCP client handshake (initialize, initialized, tools/list) and register the tools, ideally via the official MCP SDK client.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Start with a stub MCP server listing one tool; assert the agent's tool registry contains it; this fails on the current code."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "client.py:10",
     "scenario": "Popen without env= gives each server the full agent environment, so the files server receives the ticket and operator credentials it never needs and can leak them if compromised.",
     "fix": "Pass a minimal per-server env containing only its own credential and PATH.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Set FOO=secret, configure a server whose command is 'env', start it, and observe FOO in its output."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "client.py:7-11",
     "scenario": "If the registry is unreachable or the package is yanked, the process exits but start_servers returns success; the failure surfaces later mid-action. A missing 'args' key raises KeyError; the config file handle is never closed.",
     "fix": "Complete the initialize handshake within a timeout and fail fast on a non-zero exit; use 'with open(...)' and spec.get('args', []).",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "Set args to a non-existent package, call start_servers(), and observe it returns normally."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "mcp.json:3-4",
     "suspicion": "Untrusted ticket content could steer the agent to read local files and post them in customer-visible ticket replies.",
     "unresolved_fact": "The actual tools/list output of both servers, the files server's default filesystem root, and whether ticket writes reach customers."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "mcp.json:3-4",
     "suspicion": "The @acme package names may not be the vendor's genuine packages, or may resolve against an unintended registry.",
     "unresolved_fact": "The registry publisher and maintainers, the linked source repository, and the project's .npmrc."},
    {"id": "S3", "status": "needs_validation", "track": "A", "location": "context.md",
     "suspicion": "No human approval gate exists on write tools before ticket write access is granted.",
     "unresolved_fact": "The agent's tool-call approval policy."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Offering every tool is drift from the request.",
     "evidence": "The request explicitly says 'let it use every tool they offer'; the risk is captured in F1 and S1."},
    {"id": "R2", "candidate": "Shell injection via Popen.",
     "evidence": "client.py:10 passes a list without shell=True, and its values come from local config."}
  ]
}
```