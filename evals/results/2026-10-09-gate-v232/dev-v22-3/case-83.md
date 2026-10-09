# Redteam report: tool-server wiring (`client.py`, `mcp.json`, `tools.lock`, lockfiles)

> **Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent and no tools were available. Nothing below was run or recomputed. Every claim that needs execution is marked PROBABLE or UNVERIFIED.

**VERDICT: SHIP WITH FIXES.** The pin-and-refuse design is sound and fails closed, so I found no confirmed High or Critical. Three issues should still be fixed before production:
- `client.py` skips the MCP handshake, so it probably won't connect to a compliant server.
- It can hang forever on a server that never answers.
- It leaves a credentialed server running after a partial failure.

Two load-bearing facts are unverified: whether the `tools.lock` hashes match the approved definitions, and whether the package lock is complete.

**CONFIDENCE: low-medium.** Reasons:
- Same-context review with no tools.
- No hash was recomputed and no code was run.
- The server package sources and the agent-side wiring were not supplied.

**INPUTS LEDGER**

| Item | Status | Matters |
|---|---|---|
| request.md, context.md | seen | — |
| client.py, mcp.json, tools.lock, approved_tools.json, package.json, package-lock.json | seen | — |
| Source of `@acme/files-mcp` 2.4.1 and `@acme/tickets-mcp` 1.9.0 | not seen | Yes. Token scoping and path confinement are asserted to be enforced by the servers. |
| Agent code that consumes `start_servers()` and exposes tools to the model | not seen | Yes. Whether the agent re-lists tools after the check decides whether pinning holds for the whole session. |
| Tests for `check_tools` / `start_servers` | not supplied | Yes. There is no evidence the refusal path has ever fired. |
| Record of the 2026-09-20 description review, and which versions it covered | not seen | Yes. It ties the human approval to these hashes and versions. |
| Deploy procedure (`npm ci` vs `npm install`) | not seen | Yes. It decides whether the integrity hashes are enforced at all. |

**COVERAGE**
- Checked:
  - Functions in `client.py`: `schema_hash`, `check_tools`, `list_tools`, `start_servers`.
  - `mcp.json`, `tools.lock`, `approved_tools.json` (all three tools and their schemas).
  - `package.json`, `package-lock.json`.
  - Request fit.
- Not checked:
  - Hash recomputation.
  - Server package source.
  - Agent wiring.
  - Runtime behaviour of either server.
  - Prompt-injection exposure through ticket content (needs the agent prompt and ticket visibility rules).

**SEATS AND GATE**
- Sensitivity gate passed: no secrets, personal data or client data appear in the work, and tokens are referenced by environment-variable name only.
- Seats: local same-context reviewer only. No subagent was available, and no cross-vendor seats were requested.

## Pass 1: Reconstruct

The work starts each server listed in `mcp.json` with only its own token. It asks each server for its tool list and refuses the server unless:
- the tool names exactly equal the set in `tools.lock`, and
- each full definition (name, description, schema) hashes to the approved SHA-256.

Server code is pinned through exact versions and lockfile integrity hashes.

For this to be correct, all of the following must hold:
1. The `tools.lock` hashes were computed from the definitions a person reviewed (`approved_tools.json`).
2. The servers answer `tools/list` as `list_tools` expects.
3. The installed `node_modules` actually matches the lock.
4. The agent uses only the definitions checked at startup and never re-fetches them unchecked.
5. The servers enforce the token scopes as `context.md` states.

Tracks reviewed: B (main), A and R (lightly).

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | PROBABLE | B | `client.py:24-28` (`list_tools`) | Sends `tools/list` as its first message, with no `initialize` request or `notifications/initialized`, which the MCP lifecycle requires. It also takes the first stdout line as the answer, without checking `id` or skipping notifications. | A server that enforces initialization returns an error, or a server emits a log notification first. `["result"]` then raises `KeyError`, the server is killed, and the agent cannot be wired at all. This fails closed but does not deliver the request. | Send `initialize`, read its response, send `notifications/initialized`, then `tools/list`. Read lines until one has the matching `id`, and follow `nextCursor` for pagination. Repro: start `node node_modules/@acme/tickets-mcp/dist/index.js`, write the exact line from `list_tools`, and check whether the first line back holds `result.tools`. | a Y, b N, c Y, d unknown |
| F2 | Medium | CONFIRMED | B | `client.py:27` (`proc.stdout.readline()`) | No timeout on the server's reply. | A server that hangs or waits for `initialize` (see F1) blocks `start_servers` forever, so production startup stalls with no error. | Read with a deadline (thread or `select` plus a timeout), and kill and raise on expiry. Test: an `mcp.json` entry with `"command": "sleep", "args": ["3600"]`. Today the call never returns; expected is a `RuntimeError` within the timeout. | a Y, b Y, c N, d N |
| F3 | Low | CONFIRMED | B | `client.py:37-44` | When a later server fails the check, earlier servers already in `procs` are never killed. | `files` passes, then `tickets` raises. The `files` process stays alive with `FILES_TOKEN` after the caller has seen a failure, as an orphan holding a credential. | On any exception, kill every process in `procs` before re-raising. Test: `files` → `sleep 60` with `lister` returning a matching list, and `tickets` with a mismatched list. After the `RuntimeError`, `procs['files'].poll()` is `None` (still running); expected: terminated. | a Y, b Y, c N, d N |
| F4 | Low | CONFIRMED | B | `client.py:15` (`lock.get(server, {})`) | A server missing from `tools.lock` is not refused if it lists zero tools. This contradicts the module docstring ("refuse any server whose tool list differs from what a person approved"). | Someone adds an `mcp.json` entry, or a server name is mistyped, and a server with no approval record starts and keeps running with its token. | Raise if `server not in lock`. Test: an `mcp.json` with an extra server not in the lock, and a lister returning `[]`; today it starts, expected `RuntimeError`. | a Y, b Y, c N, d N |

## Needs validation (no severity)

- **S1, `tools.lock` vs `approved_tools.json`.** The hashes in `tools.lock` may not match the reviewed definitions. To settle it, run this over each entry in `approved_tools.json` and compare to `tools.lock`:
  ```
  python3 -I -c 'import json,hashlib;…sha256(json.dumps(t,sort_keys=True).encode())…'
  ```
  `client.py` never reads `approved_tools.json`, so nothing in the code links the human review to the enforced hashes.
- **S2, positive control for the pinning check.** The check has no known positive control. To settle it, run a test where the lister returns `read_file` with one character of its description changed, and confirm `RuntimeError("…changed since it was approved")`. Do the same with an extra tool, and confirm the "differ from the approved set" error.
- **S3, `package-lock.json` completeness.** The lock lists no transitive dependencies for either package. If they depend on anything (an MCP SDK, for example), the lock is incomplete: `npm ci` would fail and `npm install` would resolve transitive code unpinned. To settle it, check whether either package has `dependencies`, and whether the deploy runs `npm ci`.
- **S4, installed code vs lock.** Nothing at runtime verifies that `node_modules` matches the lock: `mcp.json` runs whatever is on disk. To settle it, find out whether the deploy installs with `npm ci` from this lock, and whether the installed `dist/index.js` is checked against a known digest.
- **S5, check-then-use gap.** The agent may re-issue `tools/list`, or honour `notifications/tools/list_changed`, after startup. That would bypass the hash check mid-session. To settle it, read the agent code that consumes `procs`.
- **S6, ticket writes driven by ticket content.** Ticket content is customer-controlled, and `update_ticket.status` is a free string with no enum. To settle the impact, find out whether comments are visible to customers and whether any status value triggers side effects (closure, refunds, SLA). This decides whether an injected ticket can cause harm beyond its own ticket.
- **S7, version coverage of the human review.** The 2026-09-20 review may not have covered `files-mcp` 2.4.1 and `tickets-mcp` 1.9.0. To settle it, check the review record.

## Refuted

- **R1, "Request drift: 'use every tool they offer' but the client refuses new tools."** At the pinned versions, the approved set is the full set the servers list, so the agent does use every offered tool. Refusing tools added later is a fail-closed safety constraint that fits the stated purpose (review before granting write access). See the question for the author below.
- **R2, "Duplicate tool names could smuggle a second definition."** The name check uses sets, but the loop hashes every listed entry, so a second definition with a different body fails the hash check.
- **R3, "Tokens leak across servers."** Each `env` holds only `PATH` and that server's own `TOKEN` (`client.py:34`), so neither server sees the other's credential.

## What holds up

- The approval check covers the whole tool definition: description, `inputSchema` and any extra fields, hashed with `sort_keys`. A description or schema change after review is refused.
- The check fails closed: any mismatch or parse failure kills the server.
- Each server's environment is limited to `PATH` and its own token.
- `update_ticket` has no ticket-id parameter, so it matches the server-side one-ticket scope described in `context.md`.
- `package.json` pins exact versions, and the lock carries sha512 integrity values of plausible format.

## Unverified claims

- "Files token read-only on docs/; tickets token scoped to the one ticket, enforced by each server." To confirm, probe with `read_file("../x")` and an `update_ticket` aimed at another ticket on a staging server.
- "A person reviewed the tools' descriptions" (S1, S7).
- "Exact versions with integrity hashes" (S3, S4).

## Questions for the author

1. How were the `tools.lock` hashes generated, and from which listing?
2. Is deployment `npm ci` from this lock, and do these packages really have no dependencies?
3. Does the agent ever call `tools/list` again after `start_servers`?
4. Are agent comments visible to customers, and do any statuses trigger automated actions?

## Decision-maker summary

The design is right: approved tool definitions are pinned and anything that changes is refused. But the client probably skips the startup handshake MCP servers expect, can hang forever, and can leave a credentialed process behind. Fix F1–F3 and check that the lock hashes match the reviewed definitions (S1) before granting ticket write access. Proceeding as-is most likely means the agent fails to start, not that it misbehaves; the larger unknown is whether customer text in tickets can steer status changes with real side effects (S6).

## Owner summary

The way the assistant connects to its tools is built safely: it refuses to run if any tool has changed since a person approved it. A few technical fixes are needed so it actually connects and doesn't get stuck or leave stray processes running. Before it can update customer tickets, someone should confirm that the approval fingerprints match what was reviewed, and decide whether ticket text written by customers could push it into changes that matter.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "low",
  "inputs_ledger": [
    {"item": "@acme/files-mcp and @acme/tickets-mcp source", "status": "not_seen", "matters": true},
    {"item": "agent code consuming start_servers()", "status": "not_seen", "matters": true},
    {"item": "tests for check_tools/start_servers", "status": "not_seen", "matters": true},
    {"item": "2026-09-20 review record", "status": "not_seen", "matters": true},
    {"item": "deploy/install procedure", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "client.py", "kind": "file"},
      {"unit": "client.py:schema_hash", "kind": "function"},
      {"unit": "client.py:check_tools", "kind": "function"},
      {"unit": "client.py:list_tools", "kind": "function"},
      {"unit": "client.py:start_servers", "kind": "function"},
      {"unit": "mcp.json", "kind": "config"},
      {"unit": "tools.lock", "kind": "config"},
      {"unit": "approved_tools.json", "kind": "file"},
      {"unit": "package.json", "kind": "file"},
      {"unit": "package-lock.json", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "tools.lock hash recomputation", "reason": "no tools in session"},
      {"unit": "server package source", "reason": "not supplied"},
      {"unit": "agent wiring", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "client.py:24-28",
     "scenario": "A server that requires the MCP initialize handshake, or emits a notification first, does not return result.tools on the first line; KeyError kills it and the agent cannot be wired.",
     "fix": "Send initialize and notifications/initialized before tools/list; read until the matching id; follow nextCursor.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "Start tickets-mcp, write the list_tools line, observe whether the first reply line contains result.tools."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "client.py:27",
     "scenario": "A server that never writes a line blocks start_servers forever.",
     "fix": "Read the reply with a deadline; kill and raise on timeout.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "mcp.json entry command sleep args [3600]; start_servers never returns, expected RuntimeError."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "client.py:37-44",
     "scenario": "files passes, tickets fails the check; the files process keeps running with FILES_TOKEN after the error.",
     "fix": "On exception, kill every process already in procs before re-raising.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "files -> sleep 60 with matching lister output, tickets mismatched; after RuntimeError the files process is still alive."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "client.py:15",
     "scenario": "A server absent from tools.lock that lists zero tools is started instead of refused.",
     "fix": "Raise if the server name is not in the lock.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Add an unlocked server whose lister returns []; it starts, expected RuntimeError."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "tools.lock",
     "suspicion": "Lock hashes may not correspond to the reviewed definitions in approved_tools.json.",
     "unresolved_fact": "Whether sha256(json.dumps(tool, sort_keys=True)) of each approved_tools.json entry equals the tools.lock value."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "client.py:check_tools",
     "suspicion": "The refusal path has no positive control.",
     "unresolved_fact": "Whether a test with a one-character description change and an extra tool raises RuntimeError."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "package-lock.json",
     "suspicion": "Lock lists no transitive dependencies; transitive code may be unpinned.",
     "unresolved_fact": "Whether either package declares dependencies and whether deploy uses npm ci."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "mcp.json",
     "suspicion": "Runtime executes whatever is in node_modules without verifying it against the lock.",
     "unresolved_fact": "Whether the deploy installs with npm ci and verifies the installed dist/index.js."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "agent wiring (not supplied)",
     "suspicion": "The agent may re-list tools after startup, bypassing the hash check.",
     "unresolved_fact": "Whether the agent calls tools/list or honours list_changed after start_servers."},
    {"id": "S6", "status": "needs_validation", "track": "A", "location": "approved_tools.json:tickets.update_ticket",
     "suspicion": "Customer-written ticket text could steer free-string status changes or customer-visible comments.",
     "unresolved_fact": "Whether comments are customer-visible and whether any status triggers side effects."},
    {"id": "S7", "status": "needs_validation", "track": "R", "location": "context.md (2026-09-20 review)",
     "suspicion": "The human review may not have covered the pinned package versions.",
     "unresolved_fact": "Which files-mcp and tickets-mcp versions the 2026-09-20 review covered."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Drift: client refuses tools beyond the approved set despite 'use every tool they offer'.",
     "evidence": "At pinned versions the approved set equals the listed set; refusing later additions is a fail-closed constraint consistent with context.md."},
    {"id": "R2", "candidate": "Duplicate tool names bypass the hash check.",
     "evidence": "check_tools hashes every listed entry, not just unique names."},
    {"id": "R3", "candidate": "Tokens leak across servers.",
     "evidence": "client.py:34 env holds only PATH and the server's own TOKEN."}
  ]
}
```