# Redteam review: PR #91 (`agent/mcp.json`)

**Review conditions:** no tools in this session and no subagent, so this is a same-context review. I could not run code or open links, so anything about runtime behavior is UNVERIFIED. Re-run in a fresh session with tools before relying on it for anything high-stakes.

**VERDICT: SHIP.** The config matches the request and both servers get `--read-only`. No defect could be confirmed, but three runtime questions (below) should be answered before merge.

**CONFIDENCE: medium.** Three things limit it:
- No tools, so the config could not be loaded in a real client.
- The full server implementations were not supplied (only the arg-parsing stubs).
- The host client's config schema and path-resolution rules were not supplied.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| `request.md` (original request) | seen | — |
| `context.md` | seen | — |
| `work/PR.md` | seen | — |
| `work/change.patch` | seen | — |
| `base/README.md`, `base/servers/files.js`, `base/servers/notes.js` | seen (excerpts) | — |
| Full tool implementations in `servers/` (search, read, `context_lines` handling, write tools) | not seen | Yes. They decide whether "read-only" holds and whether `context_lines` is bounded. |
| Host assistant's config schema and loader (does it accept `servers`/`tools`, and are relative paths resolved from the repo root?) | not seen | Yes. If the format is wrong, the config does nothing. |
| `docs/` folder in the repo | not seen | Minor |
| Commits 2b8f4d6 / 8e30c1a | not openable | No. The patch is self-contained. |

**COVERAGE**
- **Checked:**
  - `agent/mcp.json` lines 1–31: every server, arg and tool description.
  - `base/servers/files.js`: arg parsing and the `writable` logic.
  - `base/servers/notes.js`: `readOnly` parsing.
  - The PR.md claims.
  - Fit against the request.
  - Tool descriptions checked for injected instructions.
- **Not checked:**
  - Server tool handlers (not supplied).
  - The client config loader (not supplied).
  - Whether `docs/` exists.

**SEATS AND GATE**
- Only the local same-context reviewer ran. No subagent was available, and no cross-vendor seats were requested at standard depth.
- Sensitivity gate passed: the work is a config file with no personal data. The notes server will *serve* the user's notes at runtime, but nothing sensitive is in the work itself.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| — | — | — | — | — | No confirmed findings. | — | — | — |

## NEEDS VALIDATION

- **S1. Does the config's `tools` list actually restrict what the model can call?** (`agent/mcp.json:6-17, 22-28`)
  - **Concern:** `files.js` "serves text files under `--root`", so it may expose more than `search_docs` (for example a read or list tool), and `notes.js` may expose write tools that the `tools` arrays do not list.
  - **Unresolved fact:** whether the host client filters to the declared tools, and whether every non-read tool in `notes.js` checks `readOnly` before writing.
  - **To settle it:** list the tools the running servers advertise, then try calling an undeclared or write tool. It should be refused.
- **S2. Is the config format right, and where do relative paths resolve?** (`agent/mcp.json:2, 5, 21`)
  - **Concern:** the top-level key is `servers` and tools are declared inline. Many MCP clients expect `mcpServers` and discover tools from the server. Also, `servers/notes.js` and `./docs` depend on the working directory.
  - **Unresolved fact:** the host client's schema, and whether it launches servers from the repo root or from `agent/`.
  - **To settle it:** load the config in the actual client from a fresh checkout and confirm both servers start and that `search_docs` returns hits only from `<repo>/docs`.
- **S3. Is the `context_lines` limit enforced?** (`agent/mcp.json:25-26`)
  - **Concern:** the description says "0 to 5", but the arg schema is a bare `"integer"` with no minimum or maximum.
  - **Unresolved fact:** whether `files.js` clamps or rejects out-of-range values. If it does not, a value like 10000 could return whole files, which is still read-only and inside `docs/`.
  - **To settle it:** call `search_docs` with `context_lines: -1` and with `1000`, and observe whether they are rejected or clamped.

## REFUTED

- **C1. Is `--read-only` defeated in `files.js`?**
  - Refuted: `writable = args.includes("--allow-write") && !args.includes("--read-only")` evaluates to false, because `--allow-write` is absent and `--read-only` is present (`mcp.json:21`).
- **C2. Could the `--root` parse pick up the wrong value?**
  - Refuted: `args[args.indexOf("--root") + 1]` reads `"./docs"`, because `--root` is present and directly followed by its value.
- **C3. Do the tool descriptions inject instructions to the model (the context flags that descriptions are read as instructions)?**
  - Refuted: all three descriptions only describe what the tool does and its arguments. None contains a directive.

## WHAT HOLDS UP

- **Requirement fit:**
  - The notes server exposes exactly search and read.
  - The docs server exposes exactly one search.
  - Both are started with `--read-only`.
  - The docs server is rooted at `./docs`.
  - Nothing extra was added.
- **PR.md claims are accurate:**
  - Both servers use the existing `servers/` entry points.
  - `notes.js` states that the named tools are served from it.
  - The descriptions stay factual.
- **Patch integrity:** the hunk header `+1,31` matches the 31 lines added, and the JSON is well-formed.

## UNVERIFIED CLAIMS

- **"Read-only" end to end:** only flag parsing was seen, not enforcement inside the handlers (see S1).
- **The config is loaded by every developer's assistant:** this depends on the client accepting this format and path (see S2).

## QUESTIONS FOR THE AUTHOR

1. What tools do `notes.js` and `files.js` advertise at runtime, and does the client hide the ones not declared in `mcp.json`?
2. Which client and schema does this config target, and what working directory does it launch servers from?
3. Does `files.js` enforce the 0–5 range for `context_lines`?

## DECISION-MAKER SUMMARY

The config does what was asked, and no defect was confirmed from the supplied files. Before merging, have the author show the tool list each running server advertises and a successful load in the real client. If you merge without that, you risk shipping a config that silently fails to load, or one that exposes tools beyond read and search.

## OWNER SUMMARY

The change sets up the assistant to search and read notes and to search the docs, without being able to change anything, and it looks correct as written. Two things still need a quick live check: that the assistant really only gets the read and search abilities, and that the setup file loads correctly on developers' machines. Once those are confirmed, it is fine to merge.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "work/PR.md", "status": "seen", "matters": true},
    {"item": "work/change.patch", "status": "seen", "matters": true},
    {"item": "base/servers/files.js (arg parsing only)", "status": "seen", "matters": true},
    {"item": "base/servers/notes.js (arg parsing only)", "status": "seen", "matters": true},
    {"item": "full tool handlers in servers/", "status": "not_seen", "matters": true},
    {"item": "host client config schema and loader", "status": "not_seen", "matters": true},
    {"item": "docs/ folder", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Work is a config file with no personal or confidential data."},
  "coverage": {
    "checked": [
      {"unit": "agent/mcp.json", "kind": "config"},
      {"unit": "PR.md", "kind": "file"},
      {"unit": "base/README.md", "kind": "file"},
      {"unit": "base/servers/files.js", "kind": "file"},
      {"unit": "base/servers/notes.js", "kind": "file"},
      {"unit": "tool descriptions contain no instructions", "kind": "claim"},
      {"unit": "both servers start read-only", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "servers/ tool handlers", "reason": "not supplied"},
      {"unit": "host client config loader", "reason": "not supplied"},
      {"unit": "docs/", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "agent/mcp.json:6-17,22-28",
     "suspicion": "Servers may advertise tools beyond those declared (e.g. file read/list in files.js, write tools in notes.js), so the declared list may not restrict the model.",
     "unresolved_fact": "Whether the client filters to declared tools and whether notes.js write handlers check readOnly."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "agent/mcp.json:2,5,21",
     "suspicion": "Top-level key 'servers' with inline tools may not match the client's schema; relative paths depend on launch cwd.",
     "unresolved_fact": "The host client's config schema and the working directory it launches servers from."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "agent/mcp.json:25-26",
     "suspicion": "context_lines range 0-5 is stated only in prose; the arg schema is an unbounded integer.",
     "unresolved_fact": "Whether files.js clamps or rejects out-of-range context_lines."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "files.js could be writable despite --read-only.",
     "evidence": "writable = includes('--allow-write') && !includes('--read-only') is false for the configured args."},
    {"id": "C2", "candidate": "--root parsing could pick the wrong value.",
     "evidence": "--root is present and immediately followed by './docs' at mcp.json:21."},
    {"id": "C3", "candidate": "Tool descriptions inject instructions into the model.",
     "evidence": "All three descriptions are purely descriptive; no directives present."}
  ]
}
```