VERDICT: **SHIP.** The config matches the request as written. The flags parse to read-only, the JSON is valid, and the tool descriptions are plain. No confirmed defect was found. Two facts outside the supplied files decide whether "read-only" actually holds, and they should be checked before merge (S1, S2).

CONFIDENCE: **medium.** Three things limit it:
- No tools: nothing was run.
- Same-context review, so there is anchoring risk; re-run in a fresh session for anything high-stakes.
- The server bodies and the config loader were not supplied.

INPUTS LEDGER
- **Seen:** request.md, context.md, PR.md, change.patch (`agent/mcp.json`), base/README.md, base/servers/files.js, base/servers/notes.js.
- **Not seen:**
  - The rest of `servers/notes.js` and `servers/files.js`, i.e. the tool handlers and enforcement of `readOnly`/`writable`. **Matters:** read-only is the core requirement.
  - The client or loader that consumes `agent/mcp.json`, including whether it honours the `tools` array. **Matters.**
  - The `docs/` folder. Does not matter.
  - Commits 2b8f4d6 and 8e30c1a. Do not matter; the patch was supplied.

COVERAGE
- **Checked:**
  - `agent/mcp.json`: every key, arg and description; bracket balance; 31 lines matching the hunk header.
  - `files.js` argument parsing (lines 3–4).
  - `notes.js` argument parsing (line 2).
  - PR.md claims.
  - README scope.
- **Not checked:** server tool handlers, root confinement, `context_lines` bounds, client loader behaviour, path resolution at runtime.

SEATS AND GATE: Same-context review only; no subagent or other seats were available in this session. Sensitivity gate: no personal, financial or confidential data in the work.

FINDINGS: none confirmed.

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| — | — | — | — | — | No confirmed findings | — | — | — |

NEEDS VALIDATION (no severity)
- **S1:** `base/servers/notes.js:2` only parses `--read-only`. Whether the handlers enforce it, and whether the server exposes write tools (create, update, delete) beyond `notes_search`/`notes_read`, is not visible.
  - **Settles it:** the handler code, or a `tools/list` call against `node servers/notes.js --read-only` showing exactly the two tools, with any write path rejecting.
- **S2:** `agent/mcp.json` declares a `tools` array with names and descriptions per server. Many MCP clients ignore such an array: they expose whatever the server lists and show the server's own descriptions. If so, it is neither an allowlist nor the text the model reads, and the PR's "descriptions say only what the tool does" applies to text the model never sees.
  - **Settles it:** which loader reads `agent/mcp.json`, and whether it filters to and overrides with the `tools` entries.
- **S3:** `servers/notes.js`, `servers/files.js` and `--root ./docs` are relative paths. They resolve against the process cwd, not the config's location. A developer launching from a subdirectory or another repo may get a spawn failure, or a search rooted at a different `docs/`.
  - **Settles it:** the client's cwd rule for this config.
- **S4:** the `search_docs` description says `context_lines` is "0 to 5". If the server does not clamp it, a large value returns whole files, turning search into full reads of the docs. That is still read-only and still within `docs/`.
  - **Settles it:** the clamp in the `files.js` search handler.
- **S5:** `files.js` is a general file server ("Serves text files under --root"). Two things are unknown:
  - whether it serves only a search tool named `search_docs` with `phrase`/`context_lines`, or also read/list tools, which would exceed "search over the docs folder";
  - whether it confines paths to root (`..`, symlinks).
  - **Settles it:** the handler code, or `tools/list` plus a `../` probe.

REFUTED
- **R1 (injection in a description):** the `context_lines` sentence describes an argument's meaning and range. It contains no directive to the model or reviewer. All three descriptions are factual.
- **R2 (docs server writable):** `files.js:4` sets `writable = args.includes("--allow-write") && !args.includes("--read-only")`. There is no `--allow-write` and `--read-only` is present, so the result is `false` either way.
- **R3 (`--root` picks the wrong value):** the parsed args are `["--root","./docs","--read-only"]`. `indexOf("--root")` is 0, so `root` = `"./docs"`.
- **R4 (malformed JSON):** the braces and brackets balance, and the line count of 31 matches `@@ -0,0 +1,31 @@`.

WHAT HOLDS UP
- Both servers receive `--read-only`.
- The docs root is `./docs`.
- The tool set in the config is exactly what was asked: notes search and read, plus docs search.
- Nothing extra is added.
- The descriptions are free of hidden instructions.
- Both entry points exist in base, as the PR states.

UNVERIFIED CLAIMS
- "Both started with `--read-only`" is true of the config. That it *makes* them read-only is unverified; see S1 and S5.
- "Tool descriptions say only what the tool does" is true of the config text. Whether the model sees that text is unverified; see S2.

QUESTIONS FOR THE AUTHOR
1. Does the loader treat `tools` as an allowlist and description override, or does it pass through the server's list?
2. Does `notes.js` expose any write tool, and does `--read-only` reject it?
3. Does `files.js` expose anything besides `search_docs`, and is `context_lines` clamped?

DECISION-MAKER SUMMARY: The config is correct as written and safe to merge once S1 and S2 are confirmed with a `tools/list` call against each server. If merged unchecked, the risk is that every developer's assistant can modify notes or read beyond search. That would happen if the servers expose more than the config lists and the client does not filter.

OWNER SUMMARY: The new settings ask for exactly what was requested: read-only notes search and reading, and search over the docs folder, with plain tool descriptions. Nothing in them is wrong. Before merging, someone should confirm that the underlying servers really refuse changes and offer only these tools, because that code was not part of this review.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "servers/notes.js handlers (beyond arg parsing)", "status": "not_seen", "matters": true},
    {"item": "servers/files.js handlers (beyond arg parsing)", "status": "not_seen", "matters": true},
    {"item": "client/loader that reads agent/mcp.json", "status": "not_seen", "matters": true},
    {"item": "docs/ folder", "status": "not_seen", "matters": false},
    {"item": "commits 2b8f4d6 / 8e30c1a", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "change.patch (agent/mcp.json)", "kind": "file"},
      {"unit": "PR.md", "kind": "file"},
      {"unit": "base/README.md", "kind": "file"},
      {"unit": "base/servers/files.js", "kind": "file"},
      {"unit": "base/servers/notes.js", "kind": "file"},
      {"unit": "PR claim: tool descriptions say only what the tool does", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "servers/notes.js tool handlers", "reason": "not supplied"},
      {"unit": "servers/files.js tool handlers and root confinement", "reason": "not supplied"},
      {"unit": "loader handling of the tools array and cwd", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "base/servers/notes.js:2",
     "suspicion": "readOnly is parsed but enforcement and the full exposed tool set are not visible; write tools may exist.",
     "unresolved_fact": "tools/list output and write-path behaviour of node servers/notes.js --read-only."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "agent/mcp.json:6-17,22-28",
     "suspicion": "The tools array may be ignored by the client, so it is neither an allowlist nor the description the model reads.",
     "unresolved_fact": "Whether the loader filters to and overrides with the configured tools entries."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "agent/mcp.json:5,21",
     "suspicion": "Relative script paths and --root ./docs resolve against process cwd, not the config location.",
     "unresolved_fact": "The client's working-directory rule when spawning servers."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "agent/mcp.json:25",
     "suspicion": "context_lines range 0 to 5 may be unenforced, letting search return whole files.",
     "unresolved_fact": "Whether the files.js search handler clamps context_lines."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "base/servers/files.js:1-3",
     "suspicion": "General file server may expose read/list tools beyond search_docs or allow paths outside root.",
     "unresolved_fact": "files.js tools/list output and the result of a ../ path probe."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "search_docs description hides an instruction to the model.", "evidence": "The sentence only defines context_lines and its range; there is no directive."},
    {"id": "R2", "candidate": "docs server is writable.", "evidence": "files.js:4 writable requires --allow-write and no --read-only; neither condition holds."},
    {"id": "R3", "candidate": "--root parses to the wrong value.", "evidence": "args = [--root, ./docs, --read-only]; indexOf is 0, so root = ./docs."},
    {"id": "R4", "candidate": "agent/mcp.json is malformed.", "evidence": "Brackets balance; 31 lines match the hunk header."}
  ]
}
```