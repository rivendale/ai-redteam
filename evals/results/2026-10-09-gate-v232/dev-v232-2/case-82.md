VERDICT: **REWORK.** Both tool servers are fetched unpinned from the npm registry on every start and run with the operator's credentials. Separately, the code never actually lists or offers any tools, so the request is not met.

CONFIDENCE: **medium.** Limits: no tools in this session. I could not run the code, open the packages or the registry, or run `tools/validate_findings.py`. No subagent was available, so this is a single-reviewer pass. The work was not written in this conversation, so anchoring risk is low. The agent code and the 2026-09-20 tool review record were not supplied.

INPUTS LEDGER:
- **Seen:** request.md, context.md, client.py (11 lines, complete), mcp.json (complete).
- **Not seen, and it matters:**
  - The agent code that consumes `start_servers()`. It decides whether tools are ever listed or offered anywhere else (F2).
  - The 2026-09-20 tool-description review: which tools, which package versions (F3).
  - The `@acme/files-mcp` and `@acme/tickets-mcp` package contents and publishers (S1, S2).
  - The runtime environment: which credentials are in the process env and the working directory (F4, S3).
- **Not seen, and it does not matter:** the npm lockfile. None is referenced; with `npx -y` and no version, a lockfile would not pin anything anyway.

COVERAGE:
- **Scope:** the whole work (2 files).
- **Checked:**
  - client.py: `start_servers` and its docstring.
  - mcp.json: both server entries.
  - request.md and context.md.
  - Assumptions: "a person reviewed the tools" covers what runs today; Popen env inheritance; tool listing.
- **Not checked:**
  - Agent code (not_supplied).
  - Package source and install scripts (no_tools).
  - Registry metadata and publish history (no_tools).
  - Review record (not_supplied).

SEATS AND GATE:
- Local reviewer only.
- Same-vendor subagent and cross-vendor seats did not run: no tools in this session. They were not refused by the gate.
- Sensitivity gate passed: the work contains no personal data or secrets. It only *handles* operator credentials at runtime.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | mcp.json:4 (`"@acme/tickets-mcp@latest"`, `-y`) | The tickets server is resolved to whatever the registry calls `latest` on every start. `-y` auto-confirms the install, so install scripts and server code run unreviewed. | Someone who can publish `@acme/tickets-mcp` (the maintainer, a stolen npm token, a hijacked account) pushes a new version. On the next agent start it runs inside the operator's environment with ticket write credentials. It can then exfiltrate credentials or alter customer tickets. | Pin an exact version plus an integrity hash: install from a committed lockfile and run the local binary instead of `npx -y`. Install with `--ignore-scripts`. Re-review on every bump. **Repro:** publish 1.0.1 of a test package to a private registry, start with this config, and observe that 1.0.1 runs without any change to mcp.json. | a✓ b✓ c✓ d✗ |
| F2 | Critical | CONFIRMED | B | mcp.json:3 (`"@acme/files-mcp"`, no version) | Sibling of F1. A bare package name with `npx -y` also resolves to the latest version on each start, unless a locally installed copy happens to exist. | Same as F1, for the files server. It inherits the same environment (see F4), so it also receives the ticket credentials. | Same as F1. **Repro:** as for F1 with the files package, or with an empty npx cache: the version run equals the registry's current `latest`. | a✓ b✓ c✓ d✗ |
| F3 | High | CONFIRMED | B/D | mcp.json:3-4 together with client.py:1 ("offer every tool they list") | Nothing ties the tools offered to the set a person reviewed on 2026-09-20. There is no allowlist, no description/schema hash, and no version pin. Any tool added or re-described in a later release is offered automatically. Its description lands in the model's context unreviewed. | Today is 2026-10-08. A routine tickets release adds `bulk_close_tickets`, or rewords a description to tell the model to "always CC this address". The agent receives and uses it with operator credentials. No one reviewed it. | After the handshake, hash each server's `tools/list` (name, description, input schema). Compare against a committed snapshot from the review. Fail closed on any difference until it is re-reviewed. "Every tool" then means every *reviewed* tool, which is consistent with the request. **Repro:** change one tool description in a local copy of the server and start the client. Expected: refuse to start. Observed: no check exists. | a✓ b✓ c✓ d✓ |
| F4 | High | PROBABLE | B | client.py:4-11 (whole function) | The request is to *wire the agent* and *let it use every tool*. The function only spawns processes. It sends no MCP `initialize`, no `tools/list`, does not read stdout, and does not register tools with the agent. The docstring claims behaviour the code does not have. | The caller gets a dict of `Popen` objects, and the agent has zero tools. If the stdout pipe is never read, servers can block once the pipe buffer fills (see F6). PROBABLE only because the agent code that might do the handshake was not supplied. | Implement the handshake and tool listing (an MCP client library session per server), or point to where it lives and fix the docstring. **Repro:** call `start_servers()` and inspect the return value: only `Popen` objects, no tool list. A grep of client.py for `initialize`, `tools/list` or `stdin.write` finds nothing; the positive control is that grep for `Popen` finds line 10. | a✓ b✗ c✓ d✓ |
| F5 | Medium | CONFIRMED | B | client.py:10 (`subprocess.Popen(...)` with no `env=`) | Popen with `env=None` passes the full parent environment to both servers. Every operator secret in the env goes to both: the ticket token, cloud keys, and anything else present. The files server needs none of the ticket credentials. | F1, F2 or F3 lands in the files server. That server now also holds the ticket credentials and any unrelated secrets, which widens the blast radius. | Pass an explicit minimal `env=` per server, for example `{"PATH": ..., "TICKETS_TOKEN": ...}` for tickets only. **Repro:** set `SECRET=x`, configure a server as `{"command":"sh","args":["-c","env"]}`, call `start_servers` and read stdout: `SECRET=x` appears. | a✓ b✓ c✗ d✓ |
| F6 | Low | CONFIRMED | B | client.py:7-11 | There is no lifecycle handling: no timeout, no crash detection or restart, no shutdown. `open(path)` is never closed. A missing `"args"` key raises a bare KeyError. stdout is piped but never read. | A server crashes or blocks on a full stdout pipe. The agent keeps running with a dead tool and nothing logs it. | Use a context-managed session per server with a startup timeout, health check, logging and clean termination. Validate the config shape. **Repro:** use a spec without `"args"` and observe a KeyError with no message naming the server. | a✓ b✓ c✗ d✗ |

**Severity questions:** a = concrete failure scenario, b = CONFIRMED rather than PROBABLE, c = breaks the request, loses data, breaches security or harms customers, d = likely under realistic use.

**Severity notes:**
- **F1 and F2** are Critical on a/b/c. A malicious publish is not the likely case on any given start, so d is false.
- **F3** is High rather than Critical because benign tool additions are the realistic, routine trigger.

**Security boundaries:**
- **F1 and F2:** the package publisher or registry (lower trust) controls the package code, which becomes code run at operator privilege. The missing control is version and integrity pinning. The boundary crossed is third-party registry to the operator's process. The resources at risk are customer tickets, files and operator credentials.
- **F3:** the package publisher controls tool names, descriptions and schemas, which enter the model's context and its action set. The missing control is that no reviewed-snapshot check exists. The boundary crossed is publisher to the agent's decision context.

**Sibling searches:**
- **F1:** searched every server entry in mcp.json for unpinned or `@latest` specs. Found F2 (files). There are no other entries.
- **F3:** searched for any allowlist, hash or filter in client.py or mcp.json. Found none.
- **F4:** searched client.py for any other place tools are listed. None found; the rest of the agent code was not supplied.

## NEEDS VALIDATION
- **S1:** Are `@acme/files-mcp` and `@acme/tickets-mcp` the genuine packages, and not a typosquat or an unclaimed scope? *Settles it:* the npm owner of `@acme` and its publish history.
- **S2:** Do the packages have install scripts? *Settles it:* `scripts.preinstall`, `install` and `postinstall` in each package.json.
- **S3:** Persistence via the working directory. `mcp.json` and npx resolution are relative to the cwd. If the files server can write in the agent's cwd, a prompt injection in a customer ticket could have the agent write a new `mcp.json` or `node_modules/.bin` entry. That code would run on the next start. *Settles it:* the files server's root directory configuration and the agent's cwd.
- **S4:** Is customer ticket text treated as untrusted when it reaches a model that has file and ticket write tools? *Settles it:* the agent code and whether any per-action confirmation exists. It was not supplied.

## REFUTED
- **Shell injection via Popen.** The arguments are passed as a list, without `shell=True`, so shell metacharacters in args are not interpreted.
- **Unsafe deserialization of mcp.json.** `json.load` cannot execute code. The trust question is who can write the file, which is S3.

## WHAT HOLDS UP
- Popen uses argv-list form, not a shell string.
- JSON config loading is safe.
- Two servers are named, matching the request.
- Pinning the version and snapshotting the reviewed tool list are compatible with "every tool they offer".

## UNVERIFIED CLAIMS
- **"Offer every tool they list" (client.py docstring).** Not implemented in the supplied code. Confirm by showing the handshake code.
- **"A person reviewed the tools' descriptions on 2026-09-20".** Confirm by producing the record with package versions and a tool list. Then diff it against today's `tools/list`.

## QUESTIONS FOR THE AUTHOR
1. Where are `initialize` and `tools/list` performed, and is the result filtered against anything?
2. Which exact package versions did the 2026-09-20 review cover?
3. What credentials are in the agent process environment, and what directory can the files server write to?

## DECISION-MAKER SUMMARY
Do not grant ticket write access yet:
- Both tool servers download and run their latest published code on every start, with operator credentials. The tools the agent gets are not tied to what was reviewed.
- Pin the versions, snapshot and enforce the reviewed tool list, and pass each server only the credentials it needs.
- Proceeding as-is means one bad package release can read or alter customer tickets unnoticed.

## OWNER SUMMARY
The setup downloads the newest version of each helper program every time it starts and gives it full access, so a bad update could reach customer tickets without anyone checking. It also does not yet hand the tools to the assistant as intended. Fix both, lock the helpers to the reviewed versions, and give each one only the access it needs before going live.

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
    {"item": "agent code consuming start_servers()", "status": "not_seen", "matters": true},
    {"item": "2026-09-20 tool description review record", "status": "not_seen", "matters": true},
    {"item": "@acme/files-mcp and @acme/tickets-mcp package contents", "status": "not_seen", "matters": true},
    {"item": "runtime environment and working directory", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "local-same-session", "status": "ran", "cross_vendor": false},
    {"vendor": "claude-subagent", "status": "not_run", "cross_vendor": false},
    {"vendor": "cross-vendor", "status": "not_run", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal data or secrets in the work; it handles operator credentials only at runtime."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "client.py", "kind": "file"},
      {"unit": "client.py:start_servers", "kind": "function"},
      {"unit": "mcp.json", "kind": "config"},
      {"unit": "reviewed tool set equals tool set offered today", "kind": "assumption"},
      {"unit": "client.py docstring: offer every tool they list", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "agent code consuming start_servers()", "reason": "not_supplied"},
      {"unit": "2026-09-20 review record", "reason": "not_supplied"},
      {"unit": "@acme/files-mcp and @acme/tickets-mcp source and install scripts", "reason": "no_tools"},
      {"unit": "npm registry ownership and publish history", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "mcp.json:4",
     "scenario": "A new @acme/tickets-mcp version is published (by the maintainer or via a stolen token); on the next start npx -y fetches and runs it with the operator's ticket write credentials, unreviewed.",
     "fix": "Pin an exact version with an integrity hash via a committed lockfile, run the local binary instead of npx -y, install with --ignore-scripts, re-review on every bump.",
     "answers": {"a": true, "b": true, "c": true, "d": false},
     "reproduction": "Publish 1.0.1 of a test package to a private registry, start with this config, and observe 1.0.1 running with no change to mcp.json.",
     "security": true,
     "boundary": {"principal": "anyone able to publish @acme/tickets-mcp", "input": "the package code at the 'latest' tag",
                  "control": "no version or integrity pin; -y auto-confirms", "crossed": "third-party registry to operator process",
                  "resource": "customer tickets and operator credentials"},
     "siblings_searched": {"searched": "every server entry in mcp.json for unpinned or @latest specs", "found": "files server (F2)"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "mcp.json:3",
     "scenario": "@acme/files-mcp has no version, so npx -y resolves the registry's latest on each start; a malicious release runs with the full inherited env including ticket credentials.",
     "fix": "Same as F1: exact version plus integrity, local install, --ignore-scripts.",
     "answers": {"a": true, "b": true, "c": true, "d": false},
     "reproduction": "With an empty npx cache, start the client; the version run equals the registry's current latest, not a pinned one.",
     "security": true,
     "boundary": {"principal": "anyone able to publish @acme/files-mcp", "input": "the package code at the latest version",
                  "control": "no version or integrity pin", "crossed": "third-party registry to operator process",
                  "resource": "files and inherited operator credentials"},
     "siblings_searched": {"searched": "every server entry in mcp.json", "found": "tickets server (F1)"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "mcp.json:3-4; client.py:1",
     "scenario": "A routine release after the 2026-09-20 review adds or rewords a tool; the agent receives it with operator credentials and nobody reviewed it.",
     "fix": "Hash each server's tools/list (name, description, schema) against a committed reviewed snapshot; fail closed on any difference.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Change one tool description in a local server copy and start the client; expected refusal, observed no check exists.",
     "security": true,
     "boundary": {"principal": "the package publisher", "input": "tool names, descriptions and schemas",
                  "control": "no allowlist or schema hash", "crossed": "publisher to the agent's context and action set",
                  "resource": "customer tickets and files"},
     "siblings_searched": {"searched": "client.py and mcp.json for any allowlist, filter or hash", "found": "none"}},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "client.py:4-11",
     "scenario": "start_servers only spawns processes; no initialize or tools/list and no registration with the agent, so the agent gets no tools despite the docstring.",
     "fix": "Implement the MCP handshake and tool registration per server, or point to where it happens and correct the docstring.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Call start_servers() and inspect the return value: only Popen objects. A grep for initialize, tools/list or stdin.write finds nothing (positive control: Popen is found at line 10).",
     "security": false,
     "siblings_searched": {"searched": "client.py for any other tool-listing path", "found": "none; agent code not supplied"}},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "client.py:10",
     "scenario": "Popen without env= gives both servers every secret in the operator's environment, so a compromised files server also holds the ticket credentials.",
     "fix": "Pass a minimal explicit env= per server.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Set SECRET=x, configure a server as sh -c env, call start_servers, read stdout: SECRET=x appears."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "client.py:7-11",
     "scenario": "A server crashes or blocks on an unread stdout pipe and nothing detects it; a malformed entry raises a bare KeyError.",
     "fix": "Use context-managed sessions with startup timeout, health check, logging, shutdown and config validation.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Use a server spec without 'args'; observe KeyError: 'args' with no server name."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "mcp.json:3-4",
     "suspicion": "Package names may be typosquats or an unclaimed scope.",
     "unresolved_fact": "npm owner of the @acme scope and the publish history of both packages."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "mcp.json:3-4",
     "suspicion": "The packages may run install scripts at fetch time.",
     "unresolved_fact": "preinstall, install and postinstall in each package.json."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "client.py:7",
     "suspicion": "A cwd-relative mcp.json and npx resolution could let a ticket-driven file write plant code that runs on the next start.",
     "unresolved_fact": "The files server's writable root and the agent's working directory."},
    {"id": "S4", "status": "needs_validation", "track": "D", "location": "agent code (not supplied)",
     "suspicion": "Untrusted customer ticket text reaches a model holding file and ticket write tools without per-action confirmation.",
     "unresolved_fact": "Whether the agent gates write actions or treats ticket content as untrusted."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Shell injection through Popen arguments.", "evidence": "Popen receives an argv list without shell=True (client.py:10)."},
    {"id": "C2", "candidate": "Unsafe deserialization of mcp.json.", "evidence": "json.load cannot execute code; who can write the file is tracked as S3."}
  ]
}
```

I could not run `python3 tools/validate_findings.py` on this report because this session has no tools. Its schema conformance is unverified.