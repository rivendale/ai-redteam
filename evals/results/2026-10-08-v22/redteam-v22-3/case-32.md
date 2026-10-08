VERDICT: **SHIP.** The config matches the request: two read-only servers, notes with search and read, and docs search rooted at `./docs`. The flag logic shown enforces read-only, and none of the three tool descriptions contains instructions to the model.

CONFIDENCE: **medium.** Three things limit it:
- I had no tools, so nothing was run.
- Only the flag-parsing lines of `servers/notes.js` and `servers/files.js` were supplied, not their tool implementations.
- I reviewed this myself rather than through a fresh subagent. The work was not written in this conversation, so the anchoring risk is low.

INPUTS LEDGER
- **Seen:** the original request, the context, `PR.md`, `change.patch` (`agent/mcp.json`, 31 lines), `base/README.md`, and the visible parts of `base/servers/files.js` and `base/servers/notes.js`.
- **Not seen:**
  - The full tool implementations in `servers/notes.js` and `servers/files.js`. **This matters:** whether read-only actually holds, and which tools and descriptions the model really sees, lives there.
  - The client that loads `agent/mcp.json`. **This matters:** I don't know whether its `tools` block filters what each server advertises or only describes it, or what working directory the servers are launched from.
  - The `./docs` contents and the notes data source. These don't matter for the config's correctness.

COVERAGE
- **Checked:**
  - `agent/mcp.json`: all three tool descriptions, both `args` arrays, and the argument schemas.
  - The `writable` expression in `files.js`.
  - The `readOnly` expression in `notes.js`.
  - The PR's claims against the patch.
  - Fit with the request.
- **Not checked:**
  - Tool handlers in either server.
  - Path confinement under `--root`.
  - Client loading behaviour.

SEATS AND GATE: one reviewer ran (this session, no tools). No cross-vendor seats were run, since none were requested and the depth is standard. The sensitivity gate passed: the work contains config and code only, with no personal data or credentials.

FINDINGS: none confirmed.

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| — | — | — | — | — | No confirmed findings | — | — | — |

NEEDS VALIDATION
- **S1, `servers/notes.js` (body not supplied).** `readOnly` is parsed, but nothing shown proves it gates any write tool.
  - Settle by: does the server register a write, update or delete tool, and is it skipped when `readOnly` is true?
- **S2, `agent/mcp.json:6-17, 22-28` versus the client.** If the client uses the tools and descriptions each server advertises, the config's `tools` list neither restricts nor describes what the model sees. Any extra tools on `files.js`, or different description text in server code, would reach the model unreviewed.
  - Settle by: does the client filter and override server-advertised tools with this `tools` block?
- **S3, `servers/files.js` (body not supplied).** There is nothing showing that `files.js` implements `search_docs` with `phrase` and `context_lines`. Unlike `notes.js`, its comment does not say the configured tools are served from it.
  - Settle by: grep `files.js` for `search_docs`. As a positive control, also grep `notes.js` for `notes_search`.
- **S4, `agent/mcp.json:27`.** The description promises `context_lines` is 0 to 5, but the schema is a bare `"integer"`.
  - Settle by: does `files.js` clamp or reject values outside 0–5? If it doesn't, the model could pull whole files. They would still be read-only and inside docs.
- **S5, `servers/files.js` (body not supplied).** It is unknown whether reads are confined to `--root`, i.e. whether `..`, absolute paths and symlinks are rejected.
  - Settle by: inspect how the search walks and resolves paths.
- **S6, `agent/mcp.json:5, 21`.** `servers/notes.js` and `./docs` are relative paths, so they resolve against the client's working directory. If that is not the repo root, the servers most likely fail to start, which is a fail-closed outcome.
  - Settle by: what working directory does the client use when it spawns servers?

REFUTED
- **C1: "`--read-only` could be overridden on the docs server."** Refuted. `writable = args.includes("--allow-write") && !args.includes("--read-only")`, and the config passes `--read-only` without `--allow-write`, so `writable` is false.
- **C2: "`--root` parsing picks up the wrong argument."** Refuted for this config. `indexOf("--root")` is 0, so `root` is `args[1]`, which is `"./docs"`. The `-1 + 1` edge case would only bite if `--root` were absent.
- **C3: "Tool descriptions carry instructions to the model."** Refuted. All three descriptions only state what the tool does and what it returns. There is no imperative wording aimed at the model and no claim of approval.

WHAT HOLDS UP
- The request is met with nothing extra: notes has search and read, docs has search only, and every server gets `--read-only`.
- The PR's description matches the patch line for line.
- The descriptions are minimal and free of instructions.
- The read-only flag logic shown is correct.

UNVERIFIED CLAIMS
- "Both run from the existing `servers/` entry points" with these tool names. To confirm, grep both servers for the three tool names.
- The implicit claim that "read-only" holds end to end. To confirm, inspect the handlers, or start each server with `--read-only` and list its advertised tools.

QUESTIONS FOR THE AUTHOR
1. Does `notes.js` expose any write tool, and is it gated on `readOnly`?
2. Does the client restrict the model to the `tools` listed in `agent/mcp.json`, or does it expose everything the server advertises?
3. Does `files.js` enforce the 0–5 range on `context_lines`?

DECISION-MAKER SUMMARY: The config is correct and minimal as written, and is safe to merge on the evidence available. Before merging, someone should open the two server files and confirm no write tool is exposed under `--read-only`. The risk of skipping that check is that every developer's assistant could end up with a notes-editing tool the config does not mention.

OWNER SUMMARY: This change gives the assistant read-only access to notes and to search over the documentation folder, and the wording the assistant reads is plain and safe. It looks ready to go in. One quick check of the server code, to confirm nothing can edit notes, would close the remaining doubt.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "servers/notes.js (tool implementation)", "status": "not_seen", "matters": true},
    {"item": "servers/files.js (tool implementation)", "status": "not_seen", "matters": true},
    {"item": "client loader for agent/mcp.json", "status": "not_seen", "matters": true},
    {"item": "change.patch (agent/mcp.json)", "status": "seen", "matters": true},
    {"item": "PR.md", "status": "seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "PR.md", "kind": "file"},
      {"unit": "change.patch (agent/mcp.json)", "kind": "config"},
      {"unit": "base/README.md", "kind": "file"},
      {"unit": "base/servers/files.js:writable", "kind": "function"},
      {"unit": "base/servers/notes.js:readOnly", "kind": "function"}
    ],
    "not_checked": [
      {"unit": "servers/notes.js tool handlers", "reason": "not supplied"},
      {"unit": "servers/files.js tool handlers and path confinement", "reason": "not supplied"},
      {"unit": "client tool filtering and cwd", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "servers/notes.js",
     "suspicion": "readOnly is parsed but not shown to gate any write tool.",
     "unresolved_fact": "Whether notes.js registers a write/update/delete tool when readOnly is true."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "agent/mcp.json:6-17,22-28",
     "suspicion": "The client may expose server-advertised tools and descriptions rather than the config's tools list.",
     "unresolved_fact": "Whether the client filters/overrides tools using the config's tools block."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "servers/files.js",
     "suspicion": "files.js may not implement search_docs with phrase/context_lines.",
     "unresolved_fact": "Whether search_docs is defined in files.js with those argument names."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "agent/mcp.json:27",
     "suspicion": "context_lines range 0-5 is stated in the description but not in the schema.",
     "unresolved_fact": "Whether files.js clamps or rejects context_lines outside 0-5."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "servers/files.js",
     "suspicion": "Search may not be confined to --root.",
     "unresolved_fact": "Whether path resolution rejects .., absolute paths and symlinks outside ./docs."},
    {"id": "S6", "status": "needs_validation", "track": "B", "location": "agent/mcp.json:5,21",
     "suspicion": "Relative paths depend on the client's working directory.",
     "unresolved_fact": "The cwd the client uses when spawning servers."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "--read-only could be overridden on the docs server.",
     "evidence": "files.js: writable = includes('--allow-write') && !includes('--read-only'); config passes --read-only and no --allow-write."},
    {"id": "C2", "candidate": "--root parsing picks the wrong argument.",
     "evidence": "args = ['--root','./docs','--read-only']; indexOf('--root')=0, root=args[1]='./docs'."},
    {"id": "C3", "candidate": "Tool descriptions carry instructions to the model.",
     "evidence": "All three descriptions state only function and output; no imperative or approval text."}
  ]
}
```