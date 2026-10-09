# Redteam review: tool-server wiring (`client.py`, `mcp.json`, locks)

**Note:** single reviewer with no tools. I could not run code, recompute hashes or open package sources. Anything that depends on running something is `needs_validation`. The work was not written in this conversation, but re-run with tools before giving the agent ticket write access.

**VERDICT: SHIP WITH FIXES.** The pinning design fails closed and holds up when read. The confirmed defects are startup robustness problems, not security breaches. Several things outside the supplied files (the agent loop, server-side enforcement, the install path) must be settled before write access goes live.

**CONFIDENCE: low.** No tools. The `tools.lock` hashes could not be recomputed. The agent loop and server code were not supplied, and the security claims rest on them.

**INPUTS LEDGER**
- **Seen:**
  - request.md, context.md
  - approved_tools.json, client.py, mcp.json, package.json, package-lock.json, tools.lock
- **Not seen, and matters:**
  - The agent loop that consumes `start_servers()`'s return value. This decides whether the validated tool list is the one the agent uses.
  - The `@acme/files-mcp` and `@acme/tickets-mcp` source or installed `node_modules`. The docs/-only and one-ticket enforcement is claimed to live there.
  - The install command (`npm ci` or `npm install`, and whether `--ignore-scripts` is used).
  - The script that generated `tools.lock`.
- **Not seen, and matters little:** the record of the 2026-09-20 human review.

**COVERAGE**
- **Scope:** the whole supplied work.
- **Checked:**
  - Every supplied file.
  - Functions `schema_hash`, `check_tools`, `list_tools` and `start_servers`.
  - The context's claims about token scope and human review.
- **Not checked:**
  - The agent loop and server code (not_supplied).
  - Recomputing the hashes and running the client (no_tools).

**SEATS AND GATE**
- **Gate:** passed. There is no personal data, and tokens appear only as environment variable names.
- **Seats:** only this local reviewer ran. No subagent or cross-vendor seats were available in this session.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | PROBABLE | B | client.py:24-26 | `list_tools` sends `tools/list` as the first message, with no MCP `initialize` / `notifications/initialized` handshake. It also treats the first stdout line as the response, without matching on `id`. | A server that enforces the MCP lifecycle replies with an error, or emits a log or notification line first. `["result"]` then raises `KeyError` and the agent never wires up. This fails closed, but the request is not delivered. | **Fix:** perform `initialize`, then `notifications/initialized`, then `tools/list`. Read lines until the response with the matching `id` arrives, and follow `nextCursor`. **Repro (not executed):** a stub server that answers any pre-initialize request with `{"jsonrpc":"2.0","id":1,"error":{"code":-32600,"message":"not initialized"}}`. Expected: a handshake, then a tool list. Observed by trace: `KeyError: 'result'`. | a✓ b✗ c✓ d? |
| F2 | Medium | CONFIRMED (trace) | B | client.py:26 | `proc.stdout.readline()` has no timeout. | A server that never writes to stdout (for example, one waiting for `initialize`, or one that hangs) blocks `start_servers()` forever. The agent's startup hangs with no error. | **Fix:** read with a deadline (a thread or `selectors` plus a timeout), then kill the process and raise. **Repro (not executed):** set a server in mcp.json to `{"command":"sleep","args":["600"],"token_env":"FILES_TOKEN"}` and call `start_servers()`. Expected: an error within N seconds. Observed by trace: it blocks. | a✓ b✓ c✗ d✗ |
| F3 | Low | CONFIRMED (trace) | B | client.py:36-41 | Only the server that failed its check is killed. Servers already started and stored in `procs` are leaked when a later server fails. | `files` starts and passes. `tickets` then fails `check_tools`, and the exception propagates. The `files` process keeps running with `FILES_TOKEN` in its environment, and no caller holds a handle to it. | **Fix:** on any exception, kill and `wait()` every process in `procs` before re-raising. **Repro (not executed):** pass `lister=` a stub that returns the approved list for `files` and raises for `tickets`. After the exception, check `ps` for the `files` node process. Expected: gone. Observed by trace: still alive. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION
- **S1: the validated list may not be the list the agent uses** (client.py:37, 42). `start_servers` validates the result of `lister(proc)` and then discards it, returning only the processes. If the agent harness calls `tools/list` again, or honours `notifications/tools/list_changed`, a server can serve the approved set once and a different set later. That is a rug-pull past the pin. Related: `nextCursor` is ignored (line 26), so page 1 could match the lock while later pages add tools.
  - Settled by: the agent-loop code. Does it use only the checked list, and does it re-run `check_tools` on every re-list?
- **S2: customer text reaches a write tool.** Ticket content is controlled by the customer. `update_ticket` writes comments and a free-form `status` with the operator's credentials, and there is no approval step in the supplied code. The scoping to one ticket limits the blast radius to the customer's own ticket. Two things could still cause harm: an injected status triggering downstream automation (refunds, SLA, closure), or an injected comment copying internal-only fields returned by `get_ticket` into a customer-visible comment.
  - Settled by: does `get_ticket` return staff-only fields? Are agent comments visible to the customer, and are they rendered as markdown or images? Do any `status` values trigger automation?
- **S3: server-side enforcement.** The docs/-only restriction on `read_file` and the one-ticket restriction on `update_ticket` are asserted, not shown.
  - Settled by: in a sandbox, call `read_file` with `../package.json` and `docs/../../etc/hostname`, and call `update_ticket` with an extra `id` or `ticket_id` argument for another ticket. Expect refusals.
- **S4: the lockfile may be incomplete.** package-lock.json (lockfileVersion 3) lists only the two `@acme` packages. If either has dependencies, they are unpinned or the lockfile was hand-made. Install scripts may also run during install.
  - Settled by: the packages' `dependencies` fields, and whether the deploy uses `npm ci --ignore-scripts` with the integrity check passing.
- **S5: lock and approved list may not match.** The `tools.lock` hashes may not correspond to approved_tools.json.
  - Settled by: recompute `sha256(json.dumps(tool, sort_keys=True))` for each object in approved_tools.json, and compare against what the pinned server versions actually list.

## REFUTED
- **"A duplicate tool name could slip a modified definition past the set check."** Refuted: line 17 hashes every listed entry, so a second definition with a changed hash raises.
- **"Tokens leak across servers."** Refuted: line 34 builds a fresh environment containing only `PATH` and that server's own `TOKEN`.

## WHAT HOLDS UP
- **Whole-object hashing.** It covers description, schema, annotations and any added field. The JSON is canonicalized with `sort_keys`.
- **Fail-closed checks.** The name check uses the symmetric difference, so both added and removed tools fail. A failing server is killed.
- **Version pinning.** Exact versions with integrity hashes are pinned in both package files.
- **Per-server token isolation.**
- **The approved set narrows "every tool they offer."** Any tool a server adds later blocks startup instead of being silently used. Given that the agent will have production write access, this is the right reading of the request, not drift.

## UNVERIFIED CLAIMS
- **"Enforced by each server"** (token scope). Confirm with the S3 sandbox calls.
- **"A person reviewed the tools' descriptions on 2026-09-20."** Confirm with the review record and with the hashes from S5.
- **"Exact versions with integrity hashes."** The strings are well-formed sha512 values (88 characters), but I could not check them against the registry. Confirm with `npm ci`.

## QUESTIONS FOR THE AUTHOR
1. Does the agent receive the exact list that `check_tools` validated, or does it list tools again?
2. Do these servers require `initialize` before `tools/list`?
3. Can `get_ticket` return internal-only data, and are agent comments or status values customer-visible or tied to automation?
4. How is `node_modules` installed in production?

## DECISION-MAKER SUMMARY
The tool-pinning gate is sound. Fix the startup handshake, the missing timeout and the leaked processes before relying on this code. Do not enable ticket write access until S1–S3 are settled. If you proceed anyway, the main risk is a customer's ticket text steering the agent's status changes or comments, or a server changing its tools after the one-time check.

## OWNER SUMMARY
The check that blocks unapproved or altered tools is well built and fails safe. A few startup problems could make the agent hang or fail to start, and those need small fixes. Before the agent can change tickets, someone should confirm how the agent actually picks up its tools and what a customer could make it write or change.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "low",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "approved_tools.json", "status": "seen", "matters": true},
    {"item": "client.py", "status": "seen", "matters": true},
    {"item": "mcp.json", "status": "seen", "matters": true},
    {"item": "package.json", "status": "seen", "matters": true},
    {"item": "package-lock.json", "status": "seen", "matters": true},
    {"item": "tools.lock", "status": "seen", "matters": true},
    {"item": "agent loop consuming start_servers()", "status": "not_seen", "matters": true},
    {"item": "@acme/files-mcp and @acme/tickets-mcp source", "status": "not_seen", "matters": true},
    {"item": "install command / CI", "status": "not_seen", "matters": true},
    {"item": "tools.lock generation script", "status": "not_seen", "matters": true},
    {"item": "2026-09-20 human review record", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "local-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "no personal data; tokens referenced by env var name only"},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "approved_tools.json", "kind": "config"},
      {"unit": "client.py", "kind": "file"},
      {"unit": "client.py:schema_hash", "kind": "function"},
      {"unit": "client.py:check_tools", "kind": "function"},
      {"unit": "client.py:list_tools", "kind": "function"},
      {"unit": "client.py:start_servers", "kind": "function"},
      {"unit": "mcp.json", "kind": "config"},
      {"unit": "package.json", "kind": "config"},
      {"unit": "package-lock.json", "kind": "config"},
      {"unit": "tools.lock", "kind": "config"},
      {"unit": "tokens are scoped and enforced by each server", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "agent loop", "reason": "not_supplied"},
      {"unit": "server package source", "reason": "not_supplied"},
      {"unit": "recomputing tools.lock hashes", "reason": "no_tools"},
      {"unit": "running client.py", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "client.py:24-26",
     "scenario": "A server enforcing the MCP lifecycle errors on tools/list before initialize, or emits a log or notification line first; ['result'] raises KeyError and the agent never wires up (fails closed, request not delivered).",
     "fix": "Send initialize and notifications/initialized first, read until the response whose id matches, and follow nextCursor.",
     "reproduction": "Not executed. Stub server that answers any pre-initialize request with a JSON-RPC error; call start_servers(); expected a tool list after the handshake, observed by trace KeyError 'result'.",
     "answers": {"a": true, "b": false, "c": true, "d": false}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "client.py:26",
     "scenario": "A server that never writes to stdout makes proc.stdout.readline() block forever; startup hangs with no error.",
     "fix": "Read with a deadline (selectors or a thread plus timeout); on expiry, kill the process and raise.",
     "reproduction": "Not executed. Set a server to command 'sleep', args ['600'] in mcp.json and call start_servers(); expected an error within N seconds, observed by trace an indefinite block.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "client.py:36-41",
     "scenario": "files starts and passes, then tickets fails check_tools; the exception propagates and the files process stays alive and unreferenced, holding FILES_TOKEN.",
     "fix": "On any exception, kill and wait() every process already in procs before re-raising.",
     "reproduction": "Not executed. Pass lister= a stub that returns the approved list for files and raises for tickets; after the exception, the files node process is still in ps.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "client.py:37,42",
     "suspicion": "The validated tool list is discarded; if the agent re-lists or honours list_changed, or tools sit on later pages (nextCursor), unapproved tools can bypass the pin.",
     "unresolved_fact": "Whether the agent loop uses only the checked list and re-runs check_tools on any re-list."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "approved_tools.json: tickets.update_ticket",
     "suspicion": "Customer-controlled ticket text can steer update_ticket status and comments, possibly copying internal fields into customer-visible comments or triggering status automation.",
     "unresolved_fact": "Whether get_ticket returns staff-only fields, whether agent comments are customer-visible or rendered, and whether status values trigger automation."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "context.md: token scoping",
     "suspicion": "The docs/-only and one-ticket restrictions are asserted, not shown.",
     "unresolved_fact": "Sandbox calls read_file('../package.json') and update_ticket with another ticket id are refused by the servers."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "package-lock.json",
     "suspicion": "The lockfile lists no transitive dependencies; install scripts may run.",
     "unresolved_fact": "The packages' dependencies, and whether deploy uses npm ci --ignore-scripts."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "tools.lock",
     "suspicion": "The hashes may not correspond to approved_tools.json.",
     "unresolved_fact": "sha256(json.dumps(tool, sort_keys=True)) for each approved tool equals its tools.lock entry."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "A duplicate tool name could slip a modified definition past the set check.",
     "evidence": "client.py:17-19 hashes every listed entry, so any differing duplicate raises."},
    {"id": "C2", "candidate": "Tokens leak across servers.",
     "evidence": "client.py:34 builds a fresh env containing only PATH and that server's own TOKEN."}
  ]
}
```