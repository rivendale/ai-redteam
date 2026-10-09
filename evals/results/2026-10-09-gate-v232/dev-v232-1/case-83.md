# Redteam review: tool-server wiring for the ticket agent

**VERDICT: SHIP WITH FIXES.** The pinning and approval design holds up: exact package versions with integrity hashes, a schema hash over each full tool definition, a fail-closed tool check, and per-server token isolation. The open findings are availability and cleanup defects in `client.py`, plus checks I could not run.

**CONFIDENCE: medium.** I had no tools in this session, so I could not recompute the `tools.lock` hashes, inspect the packages or run any code. Only one reviewer ran, with no fresh subagent and no cross-vendor seats. I did not write this work, so author anchoring does not apply. The agent code that consumes the started servers was not supplied.

## Inputs ledger

**Seen:**
- Original request
- `context.md`
- `approved_tools.json`, `client.py`, `mcp.json`, `package.json`, `package-lock.json`, `tools.lock`

**Not seen, and whether each gap matters:**
- **The agent loop that uses the processes `start_servers()` returns.** This matters. It decides whether tool calls are limited to the approved set and whether a mid-session `notifications/tools/list_changed` causes an unchecked re-list.
- **The server source under `node_modules/@acme/*`.** This matters. The claims that the servers scope each token and refuse other ticket ids are asserted, not verified.
- **The install and deploy procedure** (`npm ci` or `npm install`, install scripts, whether `node_modules` is immutable). This matters for supply chain.
- **The record of the 2026-09-20 human review.** This matters somewhat. Nothing shows which package version's tool listing was reviewed.

## Coverage

**Scope:** the whole work as supplied (six files).

**Checked:**
- `client.py`: `schema_hash`, `check_tools`, `list_tools`, `start_servers`
- `mcp.json`, `package.json`, `package-lock.json` (integrity strings are well formed: 88-character sha512 base64), `tools.lock`, `approved_tools.json`
- The claim that the agent can use every offered tool
- The token isolation assumption

**Not checked:**
- Server implementations (not supplied)
- Agent loop (not supplied)
- Hash recomputation (no tools)
- Install procedure (not supplied)

## Seats and gate

- **Seats:** a single reviewer in this session ran. No subagent and no cross-vendor seats, because no tools were available.
- **Sensitivity gate:** passed. The work contains no personal data or credentials; tokens are referenced only by environment variable name.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced; not run) | B | `client.py:24-25` (`list_tools`) | `readline()` on the server's stdout has no timeout. The code also takes the first line as the reply to request id 1 without matching the id. In addition, it sends `tools/list` without the MCP `initialize` / `notifications/initialized` handshake first. | A server that waits for `initialize` and never answers, or that hangs, blocks `start_servers()` forever with no error, so the agent never starts. A server that prints a log line or notification first causes a `JSONDecodeError` or `KeyError`. Both cases fail closed, but they look like an outage. | **Fix:** do the `initialize` handshake, read with a deadline (for example a reader thread with `join(timeout)` or `select`), skip lines until the `id` is 1, and raise a clear error on a JSON-RPC `error`. **Reproduction:** set `mcp.json` `files` to `{"command":"sleep","args":["1000"],"token_env":"FILES_TOKEN"}`, set `FILES_TOKEN=x`, and call `start_servers()`. Expected: an error within N seconds. Observed by trace: it never returns. | a✓ b✓ c✗ d✓ |
| F2 | Low | CONFIRMED (traced; not run) | B | `client.py:37-43` (`start_servers`) | Only the server that fails the check is killed. Servers already started remain in the local `procs`, which is discarded when the exception propagates. | The `tickets` tool definitions change, so `check_tools` raises. The `files` node process keeps running as an orphan holding `FILES_TOKEN`, and repeated restarts accumulate orphans. | **Fix:** in the `except` block, kill every process in `procs` as well as `proc` before re-raising. **Reproduction:** change one hex digit of `tickets.update_ticket` in `tools.lock`, call `start_servers()`, and catch the `RuntimeError`. Then run `pgrep -f files-mcp/dist/index.js`. Expected: none. Observed by trace: one process. | a✓ b✓ c✗ d✗ |

## Needs validation

- **N1 (`tools.lock` against `approved_tools.json`).** Do the lock hashes equal `sha256(json.dumps(tool, sort_keys=True))` with the default separators for each definition the person reviewed? If the lock came from a different listing, the check enforces something other than what was reviewed. **To settle:** recompute the three hashes from `approved_tools.json`.
- **N2 (`client.py:list_tools` and the agent loop).** Is the tool list checked only at startup? If the agent later re-lists tools (after `list_changed` or on reconnect), or calls a tool name outside the lock, nothing in the supplied code stops it. **To settle:** read the agent loop for re-listing and for a call-time allowlist.
- **N3 (`package-lock.json`).** The lock lists only the two packages, with no `resolved` fields and no transitive entries. **To settle:** check whether `@acme/files-mcp@2.4.1` or `@acme/tickets-mcp@1.9.0` declare dependencies, and whether `npm ci` succeeds against this lock.
- **N4 (install and deploy).** Is the deploy installed with `npm ci` (so integrity is verified) and `--ignore-scripts` (or with install scripts reviewed), in an environment without the operator tokens? Is `node_modules` immutable at runtime? Integrity hashes are checked at install time only, and `mcp.json` runs whatever files sit at that path.
- **N5 (`update_ticket.status` is a free-form string, and ticket text is customer-written).** A customer can write instructions into their own ticket that steer the agent's `update_ticket` call. The token limits this to the session's own ticket. **To settle:** whether the server restricts `status` to an enum, whether comments are public or internal staff notes, and whether status changes (for example closed or refund) trigger downstream workflows. If they do, add a human approval step for status writes.
- **N6 (server-side scoping).** The claims that `read_file` is confined to `docs/` and that `update_ticket` refuses other tickets are taken from the context and tool descriptions. **To settle:** a negative test against each server, for example `read_file("../.env")` and an update attempted from a session opened for ticket A against ticket B.

## Refuted

- **R1: "Tools are pinned by name only, so a description rug-pull passes."** Refuted: `schema_hash` hashes the whole tool object, including `description` and `inputSchema` (`client.py:9`).
- **R2: "A new tool added by a server is silently exposed."** Refuted: the name-set equality check raises on any added or removed tool (`client.py:15-16`).
- **R3: "Tokens leak across servers or from the operator environment."** Refuted: each child process receives only `PATH` and its own `TOKEN` (`client.py:37`).
- **R4: "A duplicate tool name could slip past the set comparison."** Refuted: every listed entry is hash-checked individually, so a differing duplicate raises.

## What holds up

- **Exact version pins.** Both `package.json` and the lockfile pin exact versions, and the integrity strings are well formed.
- **Fail-closed tool check.** A missing lock entry, a changed schema or description, an added tool or a missing token all raise.
- **Least privilege by construction.** The files token is read-only on `docs/`, and `update_ticket` takes no ticket id, so the agent cannot even name another ticket.
- **The request is met.** The agent gets every tool the servers currently offer. New tools are refused until re-approved, which is a defensible narrowing in production.

## Unverified claims

- The servers enforce the token scopes. Confirm with the negative tests in N6.
- `tools.lock` reflects the reviewed definitions. Confirm by recomputing, as in N1.
- The 2026-09-20 review covered versions 2.4.1 and 1.9.0. Confirm from the review record.

## Questions for the author

1. Does the agent ever re-list tools, or call a tool name not in `tools.lock`?
2. Are ticket statuses an enum on the server, and do status changes trigger workflows?
3. How are `node_modules` installed in production?

## Decision-maker summary

The connection design is sound, and no finding blocks write access. Before go-live, fix the startup hang and the orphaned-process cleanup, recompute the lock hashes, and run the two server-scoping negative tests. The main residual risk if you proceed anyway is customer-written ticket text steering status changes. That damage is limited to the customer's own ticket, but it could matter if status changes trigger refunds or closures.

## Owner summary

The way the assistant connects to the files and tickets systems is careful: it only accepts the exact tools a person approved, and each system gets its own limited key. Two small fixes are needed so it does not hang at startup or leave stray processes running. A few checks still need doing before go-live, chiefly confirming that the systems really refuse anything outside the one ticket and the public docs.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "agent loop consuming start_servers() procs", "status": "not_seen", "matters": true},
    {"item": "node_modules/@acme/files-mcp and tickets-mcp source", "status": "not_seen", "matters": true},
    {"item": "install/deploy procedure", "status": "not_seen", "matters": true},
    {"item": "2026-09-20 review record", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-session-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "client.py", "kind": "file"},
      {"unit": "client.py:schema_hash", "kind": "function"},
      {"unit": "client.py:check_tools", "kind": "function"},
      {"unit": "client.py:list_tools", "kind": "function"},
      {"unit": "client.py:start_servers", "kind": "function"},
      {"unit": "mcp.json", "kind": "config"},
      {"unit": "package.json", "kind": "config"},
      {"unit": "package-lock.json", "kind": "config"},
      {"unit": "tools.lock", "kind": "config"},
      {"unit": "approved_tools.json", "kind": "config"},
      {"unit": "per-server token isolation", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "tools.lock hash recomputation", "reason": "no_tools"},
      {"unit": "@acme server implementations", "reason": "not_supplied"},
      {"unit": "agent loop", "reason": "not_supplied"},
      {"unit": "install procedure", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "client.py:24-25 (list_tools)",
     "scenario": "A server that waits for MCP initialize, or hangs, never writes a line; proc.stdout.readline() blocks forever and the agent never starts. A log line or notification printed first makes json.loads or ['result'] fail.",
     "fix": "Perform the initialize/initialized handshake, read with a deadline, match the response id, and raise clearly on a JSON-RPC error.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Set mcp.json files to {\"command\":\"sleep\",\"args\":[\"1000\"],\"token_env\":\"FILES_TOKEN\"}, export FILES_TOKEN=x, call start_servers(); expected an error within a timeout, traced behavior is an indefinite block (traced, not run)."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "client.py:37-43 (start_servers)",
     "scenario": "tickets fails check_tools; only the tickets proc is killed, and the already-started files node process is orphaned holding FILES_TOKEN.",
     "fix": "On failure, kill every proc in procs as well as the current one before re-raising.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Alter one hex digit of tickets.update_ticket in tools.lock, call start_servers() and catch RuntimeError, then pgrep -f files-mcp/dist/index.js; expected none, traced result is one live process (traced, not run)."},
    {"id": "N1", "status": "needs_validation", "track": "B", "location": "tools.lock",
     "suspicion": "Lock hashes may not correspond to the reviewed definitions in approved_tools.json.",
     "unresolved_fact": "Whether sha256(json.dumps(tool, sort_keys=True)) of each approved_tools.json entry equals the tools.lock value."},
    {"id": "N2", "status": "needs_validation", "track": "B", "location": "client.py:list_tools / agent loop",
     "suspicion": "The tool check runs only at startup; a later re-list or a call to an unlisted name is not gated.",
     "unresolved_fact": "Whether the agent loop re-lists tools on list_changed or reconnect, and whether it enforces a call-time allowlist."},
    {"id": "N3", "status": "needs_validation", "track": "B", "location": "package-lock.json",
     "suspicion": "Transitive dependencies are absent from the lock and would be unpinned.",
     "unresolved_fact": "Whether either @acme package declares dependencies, and whether npm ci succeeds against this lock."},
    {"id": "N4", "status": "needs_validation", "track": "B", "location": "mcp.json args / deploy",
     "suspicion": "Integrity is verified only at install; install scripts may run with operator tokens; node_modules may be mutable at runtime.",
     "unresolved_fact": "Whether deploy uses npm ci with --ignore-scripts (or reviewed scripts), without tokens, onto an immutable node_modules."},
    {"id": "N5", "status": "needs_validation", "track": "D", "location": "approved_tools.json tickets.update_ticket.inputSchema.status",
     "suspicion": "Customer-written ticket text can steer free-form status or comment writes on the same ticket.",
     "unresolved_fact": "Whether the server restricts status to an enum, whether comments are internal, and whether status changes trigger downstream workflows."},
    {"id": "N6", "status": "needs_validation", "track": "B", "location": "context.md token scoping; approved_tools.json descriptions",
     "suspicion": "Server-side confinement to docs/ and to one ticket is asserted, not shown.",
     "unresolved_fact": "Results of read_file('../.env') and of a cross-ticket update attempt against each server."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Tools are pinned by name only, so a description change passes.", "evidence": "schema_hash hashes the whole tool object including description and inputSchema (client.py:9)."},
    {"id": "R2", "candidate": "A newly offered tool is silently exposed.", "evidence": "The name-set equality check raises on any added or removed tool (client.py:15-16)."},
    {"id": "R3", "candidate": "Tokens leak across servers or from the operator environment.", "evidence": "Each child process receives only PATH and its own TOKEN (client.py:37)."},
    {"id": "R4", "candidate": "A duplicate tool name slips past the set comparison.", "evidence": "Every listed entry is hash-checked individually, so a differing duplicate raises."}
  ]
}
```