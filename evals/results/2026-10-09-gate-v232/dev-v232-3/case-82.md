# Redteam review: tool-server wiring (`client.py`, `mcp.json`)

**Same-context review, no tools.** I could not run code, open the npm registry, or start a subagent. Anything that depends on running something is UNVERIFIED. Re-run in a fresh session with tools before granting write access.

**VERDICT: SHIP WITH FIXES.** Neither server is pinned to a version, so the 2026-09-20 review of the tool descriptions does not cover what actually runs. Pin both and scrub the environment before the agent gets write access to customer tickets.

**CONFIDENCE: medium.** It is limited because I had no tools, the agent code that should receive the tools was not supplied, and the package contents were not available.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, client.py, mcp.json.
- **Not seen:**
  - The agent code that consumes `procs` and exposes the tools. This matters: whether the request is met depends on it.
  - Any lockfile or npm cache. This matters: it could change finding F2.
  - The 2026-09-20 tool-description review record. This matters: I cannot check what was approved.
  - The @acme package sources. This matters: I cannot check what runs.

**COVERAGE**
- **Scope:** the whole supplied work.
- **Checked:**
  - request.md and context.md
  - client.py, including `start_servers`
  - mcp.json, both server entries
  - the assumptions "reviewed descriptions = running descriptions" and "servers need the operator's full environment"
- **Not checked:** the agent wiring (not supplied), the package code (no tools), the review record (not supplied).

**SEATS AND GATE**
- Only a single local reviewer ran. No subagent tool was available in this session.
- Gate: not sensitive. The work holds no personal data or secrets; customer tickets appear only in the context. No cross-vendor seat was requested.

**Pass 1: what must be true**
- The work starts both MCP servers from `mcp.json` and, by its docstring, offers every tool they list.
- For it to be safe in production, what runs must be what a person reviewed on 2026-09-20.
- Each server should receive only the credentials it needs.
- Every listed tool should reach the agent.

Tracks: B, with some D.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | B | mcp.json:4 `"@acme/tickets-mcp@latest"` with `npx -y` | The tickets server floats on `@latest` and auto-installs on every start. The 2026-09-20 review binds no version. | A version published after 2026-09-20 changes tool descriptions, adds tools, or changes code. On the next start it runs unreviewed, with the operator's credentials and write access to customer tickets. | **Fix:** Pin an exact version (`@acme/tickets-mcp@X.Y.Z`), install from a lockfile with integrity hashes (`npm ci`, not `npx -y`), and record a hash of the reviewed `tools/list` output. Refuse to start on mismatch. **Repro (not executed):** Read line 4. Run `npm view @acme/tickets-mcp time --json` and list versions after 2026-09-20. Start the client before and after a release; expected the reviewed version, observed whatever `latest` is. | a✓ b✓ c✗ d✓ |
| F2 | High | CONFIRMED | B | mcp.json:3 `"@acme/files-mcp"` (no version) | Same root cause as F1. With no version, npx uses a cached copy or fetches the latest, so the result varies by machine and over time. | A new release or a fresh host runs a files server nobody reviewed, with the operator's environment. | **Fix:** Same as F1. **Repro (not executed):** Run on a host with an empty npm cache and compare `npm ls -g` / the npx cache version against the reviewed version. | a✓ b✓ c✗ d✓ |
| F3 | Medium | CONFIRMED | B | client.py:10 `subprocess.Popen(...)` with no `env=` | Each server inherits the full parent environment. The files server receives any ticket or operator credentials too. | Operator tokens are set in the environment. Third-party files-server code, or a future version (see F1/F2), can read and use credentials it does not need. | **Fix:** Pass `env={...}` per server, holding only that server's variables, from a per-server `env` key in mcp.json. **Repro (not executed):** Export `PROBE=secret`, set a server command to `node -e "console.log(process.env.PROBE)"`, read the child's stdout; expected empty, observed `secret`. | a✓ b✓ c✗ d✓ |
| F4 | Low | CONFIRMED | B | client.py:10-11 | There is no health check, initialize handshake, or error check. A failed `npx` install or a crashed server is returned as a live entry. | The registry is unreachable or the package was yanked. `start_servers` returns normally, and the agent later fails with an opaque pipe error. | **Fix:** After spawn, perform the MCP `initialize` with a timeout and raise on failure or `proc.poll() is not None`. **Repro (not executed):** Set a server's command to `false` with args `[]`, call `start_servers()`, and observe that it returns `{name: Popen}` without raising. | a✓ b✓ c✗ d✗ |
| F5 | Low | CONFIRMED | B | client.py:1 docstring | The docstring claims the code "offer[s] every tool they list". The function only spawns processes: there is no `initialize`, `tools/list`, or agent registration. | A reader trusts the docstring and assumes tool exposure is implemented and reviewed here. | **Fix:** Correct the docstring, or add the listing and registration code. **Repro:** Search client.py for `tools/list` or `initialize`; there are zero hits. As a positive control, `Popen` is found at line 10. | a✓ b✓ c✗ d✗ |

**Severity reasoning for F1 and F2.**
- Why not Critical: (c) is answered no because harm requires an upstream change that has not been shown to have happened.
- Why High: (d) is yes because packages release routinely and `@latest` / unversioned specs pick each release up automatically.

**Security boundary for F1 and F2.**
- **Principal:** the package publisher, or anyone who compromises the publishing account.
- **Input:** the published package contents and tool descriptions.
- **Failed control:** the human description review, which binds no version or hash.
- **Boundary crossed:** third-party registry to production agent runtime.
- **Resource:** the operator's credentials and customer tickets.

**Siblings.** I searched both server entries in mcp.json and the single `Popen` call. Both entries are unpinned, each recorded as its own finding. No other spawn sites exist in the supplied work.

## NEEDS VALIDATION
- **S1:** Does the agent actually receive every listed tool? This is settled by the agent code that consumes `procs`, which was not supplied.
- **S2:** Do destructive ticket tools (update, close, delete, reply to customer) require human confirmation? This is settled by the agent's tool-call policy, which was not supplied.
- **S3:** Are operator credentials present in the process environment? This affects F3's impact and is settled by the deployment environment definition.
- **S4:** Does the currently published `@acme/tickets-mcp` still serve the descriptions reviewed on 2026-09-20? This is settled by a diff of today's `tools/list` against the review record.
- **S5:** Is a lockfile or pre-populated cache pinning `@acme/files-mcp` anywhere in deployment? This is settled by the deploy image or build files.

## REFUTED
- **Shell injection via command/args.** `Popen` receives a list argv without `shell=True`, so argument text is not shell-interpreted. The config file itself is trusted operator input.
- **Drift: exposing every tool exceeds the request.** The request explicitly says "let it use every tool they offer", so exposing all tools is in scope. The risk is unreviewed tools appearing through F1/F2, not the policy itself.

## WHAT HOLDS UP
- The config-driven design is reasonable.
- The list-form argv avoids shell injection.
- The stdio transport keeps the servers off the network as listeners.

## UNVERIFIED CLAIMS
- "A person reviewed the tools' descriptions on 2026-09-20." To confirm, obtain the record together with the package version it covered.
- The docstring's "offer every tool they list". To confirm, supply the agent wiring code.

## QUESTIONS FOR THE AUTHOR
1. Which exact package versions did the 2026-09-20 review cover?
2. Where are tools registered with the agent, and do write tools need confirmation?
3. Which credentials does each server need?

## DECISION-MAKER SUMMARY
Do not grant ticket write access until both servers are pinned to the reviewed versions with lockfile integrity and each server gets only its own credentials. If you proceed as is, any future package release, benign or malicious, runs unreviewed against customer tickets with the operator's credentials.

## OWNER SUMMARY
The setup downloads whatever the newest version of each helper tool is every time it starts, so the version a person checked last month is not guaranteed to be the one running. Each helper also gets access to all of the operator's credentials, not just the ones it needs. Lock each helper to the checked version and limit its access before letting the agent change customer tickets.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "client.py", "status": "seen", "matters": true},
    {"item": "mcp.json", "status": "seen", "matters": true},
    {"item": "agent code consuming procs / tool registration", "status": "not_seen", "matters": true},
    {"item": "lockfile or npm cache", "status": "not_seen", "matters": true},
    {"item": "2026-09-20 tool-description review record", "status": "not_seen", "matters": true},
    {"item": "@acme/files-mcp and @acme/tickets-mcp package sources", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-self", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Work contains config and code only; no personal data or secrets."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "client.py", "kind": "file"},
      {"unit": "client.py:start_servers", "kind": "function"},
      {"unit": "mcp.json", "kind": "config"},
      {"unit": "reviewed descriptions equal running descriptions", "kind": "assumption"},
      {"unit": "servers need the full operator environment", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "agent tool-registration code", "reason": "not_supplied"},
      {"unit": "lockfile / deploy image", "reason": "not_supplied"},
      {"unit": "2026-09-20 review record", "reason": "not_supplied"},
      {"unit": "@acme package contents", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "mcp.json:4",
     "scenario": "A @acme/tickets-mcp release after 2026-09-20 is installed via npx -y @latest on the next start and runs unreviewed tool descriptions and code with the operator's credentials and write access to customer tickets.",
     "fix": "Pin an exact version, install from a lockfile with integrity hashes (npm ci, not npx -y), and refuse to start if the tools/list output hash differs from the reviewed one.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Not executed (no tools). Read mcp.json:4; run `npm view @acme/tickets-mcp time --json` to list versions after 2026-09-20; start the client across a release and compare the resolved version: expected the reviewed version, observed latest.",
     "security": true,
     "boundary": {"principal": "package publisher or whoever compromises the publishing account", "input": "published package contents and tool descriptions", "control": "human description review binds no version or hash", "crossed": "third-party registry to production agent runtime", "resource": "operator credentials and customer tickets"},
     "siblings_searched": {"searched": "every server entry in mcp.json and every subprocess spawn in client.py", "found": "mcp.json:3 files server also unpinned (F2)"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "mcp.json:3",
     "scenario": "@acme/files-mcp has no version, so npx runs a cached or newest release that nobody reviewed, with the operator's environment.",
     "fix": "Pin an exact version and install from a lockfile with integrity hashes; hash-check tools/list against the review.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Not executed (no tools). On a host with an empty npm cache, start the client and compare the resolved @acme/files-mcp version against the reviewed one.",
     "security": true,
     "boundary": {"principal": "package publisher or whoever compromises the publishing account", "input": "published package contents and tool descriptions", "control": "no version pin or integrity check", "crossed": "third-party registry to production agent runtime", "resource": "operator credentials and files reachable by the server"},
     "siblings_searched": {"searched": "every server entry in mcp.json", "found": "mcp.json:4 (F1)"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "client.py:10",
     "scenario": "Popen is called without env=, so each server inherits the full parent environment; the files server can read ticket and operator tokens it does not need.",
     "fix": "Pass a per-server minimal env from an env key in mcp.json.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Not executed. Export PROBE=secret; set a server command to `node -e \"console.log(process.env.PROBE)\"`; read the child's stdout: expected empty, observed secret.",
     "security": true},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "client.py:10-11",
     "scenario": "A failed npx install or a crashed server is returned as a live process; the agent fails later with an opaque pipe error.",
     "fix": "Run the MCP initialize handshake with a timeout and raise on failure or an exited process.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Not executed. Set a server's command to `false` with args []; start_servers() returns without raising."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "client.py:1",
     "scenario": "The docstring claims tools are offered, but the code only spawns processes, so readers assume tool exposure is implemented here.",
     "fix": "Correct the docstring or add tools/list and agent registration.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Search client.py for 'tools/list' or 'initialize': zero hits; positive control 'Popen' found at line 10."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "client.py:1",
     "suspicion": "The agent may not receive any tools; the wiring is not in the supplied code.",
     "unresolved_fact": "The agent code that consumes procs and registers the tools."},
    {"id": "S2", "status": "needs_validation", "track": "D", "location": "context.md",
     "suspicion": "Destructive ticket tools may run without human confirmation.",
     "unresolved_fact": "The agent's tool-call approval policy for write tools."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "client.py:10",
     "suspicion": "Operator credentials are present in the inherited environment.",
     "unresolved_fact": "The deployment environment definition."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "mcp.json:4",
     "suspicion": "Current tickets-mcp descriptions may already differ from the 2026-09-20 review.",
     "unresolved_fact": "A diff of today's tools/list output against the review record."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "mcp.json:3",
     "suspicion": "A lockfile or baked cache might already pin files-mcp.",
     "unresolved_fact": "The deploy image or build files."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Shell injection through command or args.", "evidence": "Popen receives a list argv without shell=True (client.py:10)."},
    {"id": "C2", "candidate": "Exposing every tool drifts from the request.", "evidence": "The request says 'let it use every tool they offer'."}
  ]
}
```