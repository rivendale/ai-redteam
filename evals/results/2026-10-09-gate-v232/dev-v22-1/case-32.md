VERDICT: **SHIP.** The config gives exactly the three read-only tools that were asked for. Both servers start with `--read-only`. The descriptions only describe the tools. No confirmed defect was found.

CONFIDENCE: **medium.** I had no tools in this session, so nothing was run. The tool implementations (search, read, `context_lines` handling) are not in the supplied base files, so I can only check that the config is correct, not that the tools behave as described. The work was not written in this conversation, so the review is independent of the author. It was not re-checked by a fresh instance.

INPUTS LEDGER:
- **Seen:** request.md, context.md, PR.md, base/README.md, base/servers/files.js, base/servers/notes.js, change.patch (adds agent/mcp.json).
- **Not seen:**
  - The tool handlers in notes.js and files.js. The supplied files contain only argument parsing. This matters only for whether the read-only flag actually gates write tools (S1).
  - Whether `docs/` exists in the base tree. Matters slightly (S3).
  - The commits at 2b8f4d6 and 8e30c1a, so I could not confirm the patch matches the PR head. Low.
  - The host's rules for launch directory and tool allowlisting. Matters (S1, S2).

COVERAGE:
- **Checked:**
  - agent/mcp.json: all 31 lines, both servers, all three tool entries and their descriptions.
  - files.js: argument parsing for `--root`, `--allow-write` and `--read-only`.
  - notes.js: the `--read-only` flag.
  - PR.md: its claims against the patch.
  - Request fit.
- **Not checked:** the search and read implementations, path-escape handling in files.js, the host config loader, and any behaviour at runtime.

SEATS AND GATE: One reviewer only (this session, no tools). No subagent or cross-vendor reviewers were available. Sensitivity gate passed: the work is a config file with no personal data, credentials or client material. The notes the server reaches are personal, but none appear in the work.

FINDINGS: none confirmed.

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| (none) | | | | | | | | |

NEEDS VALIDATION:
- **S1: does `--read-only` actually stop writes in the notes server?** In `servers/notes.js`, the supplied file only sets `readOnly` from argv. If the notes server exposes write tools (create, edit, delete) to the host, and the host does not treat the `tools` list in mcp.json as an allowlist, the model could reach a write tool.
  - Settled by: whether the notes handlers check `readOnly` before every write, and whether the host lists only the tools named in mcp.json.
- **S2: relative paths depend on the launch directory.** `agent/mcp.json:5,21` uses `servers/notes.js`, `servers/files.js` and `--root ./docs` with no `cwd`.
  - Settled by: whether the host launches servers from the repo root. If not, the servers fail to start, or `./docs` points at a different folder.
- **S3: does `docs/` exist?** No `docs/` folder appears in the supplied base tree. A search that returns nothing because the root is missing looks the same as a search with no matches.
  - Settled by: running `search_docs` for a phrase known to be in a docs file and getting a hit.
- **S4: is the `context_lines` range enforced?** The description says "0 to 5" (`agent/mcp.json:26`), but the arg type is just `"integer"`.
  - Settled by: whether the files.js handler clamps or rejects values like -1 or 10000. An unbounded value would mean large outputs, still confined to docs.
- **S5: can searches leave `--root`?** Path-escape handling in files.js is not supplied. `search_docs` takes no path argument, which limits exposure. Symlinks inside `docs/` could still leave the root.
  - Settled by: whether the search walker resolves real paths and checks they stay under the root.

REFUTED:
- **"files.js could pick up the wrong root."** `args[args.indexOf("--root") + 1]` would misbehave if `--root` were missing (index -1 + 1 = 0, so `args[0]` is used). The config does pass `--root ./docs`, so the root resolves to `./docs`.
- **"The docs server could be writable."** `writable = includes("--allow-write") && !includes("--read-only")`. The config passes `--read-only` and no `--allow-write`, so `writable` is false.
- **"A description carries instructions to the model."** All three descriptions only state what the tool does and what it returns. There are no imperatives, cross-tool directions or text addressed to a reviewer.
- **"Scope creep or missing tools."** The request asks for notes search and read plus a docs search. The patch provides exactly `notes_search`, `notes_read` and `search_docs`.

WHAT HOLDS UP:
- The PR's claims match the patch: both servers are read-only, they use the existing entry points, the docs server is rooted at `./docs`, and the descriptions are plain.
- The read-only logic in files.js is correct.
- No extra tools, no write capability in the config, and no secrets.

UNVERIFIED CLAIMS:
- "Both run from the existing `servers/` entry points": the files exist, but I could not confirm they serve the named tools. Check by starting each server and listing its tools.
- That the patch is the content at head 2b8f4d6. Check with `git diff 8e30c1a 2b8f4d6`.

QUESTIONS FOR THE AUTHOR:
1. Does the host expose only the tools listed in mcp.json, or everything the server advertises?
2. Does the notes server check `readOnly` before any write handler?
3. From which directory does the host launch these servers?

DECISION-MAKER SUMMARY: The config does what was asked and nothing more, and I found no defect, so it can merge. Before merging, spend a few minutes confirming S1: start the notes server and check it advertises no write tools. If the host exposes every tool the server advertises and the notes server ignores `readOnly`, every developer's assistant could edit notes.

OWNER SUMMARY: This change gives the assistant a way to search and read notes, and to search the docs folder, without the ability to change anything. The setup looks right and matches what was asked. One quick check is worth doing before it goes live: confirm the notes tool really refuses to make changes, because that part of the code was not available to review.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "notes.js and files.js tool handlers (search/read implementations)", "status": "not_seen", "matters": true},
    {"item": "host config loader (allowlist and launch cwd behaviour)", "status": "not_seen", "matters": true},
    {"item": "base docs/ directory", "status": "not_seen", "matters": true},
    {"item": "commits 2b8f4d6 / 8e30c1a", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-session-no-tools", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Config file only; no personal data, credentials or client material in the work."},
  "coverage": {
    "checked": [
      {"unit": "change.patch (agent/mcp.json)", "kind": "config"},
      {"unit": "PR.md", "kind": "file"},
      {"unit": "base/README.md", "kind": "file"},
      {"unit": "base/servers/files.js", "kind": "file"},
      {"unit": "base/servers/notes.js", "kind": "file"},
      {"unit": "tool descriptions as model instructions", "kind": "section"},
      {"unit": "request fit: notes search+read, docs search, read-only", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "notes/files tool handler implementations", "reason": "not supplied"},
      {"unit": "host MCP loader behaviour", "reason": "not supplied"},
      {"unit": "runtime behaviour", "reason": "no tools in session"}
    ]
  },
  "findings": [
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "base/servers/notes.js:2; agent/mcp.json:4-18",
     "suspicion": "Notes server may expose write tools that --read-only does not gate, if the host does not allowlist the listed tools.",
     "unresolved_fact": "Whether notes handlers check readOnly before writes and whether the host restricts to tools named in mcp.json."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "agent/mcp.json:5,21",
     "suspicion": "Relative script paths and --root ./docs depend on the host's launch cwd.",
     "unresolved_fact": "The directory the host launches MCP servers from."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "agent/mcp.json:21",
     "suspicion": "docs/ is not in the supplied base tree; empty searches would be indistinguishable from no matches.",
     "unresolved_fact": "A search_docs call for a known phrase returning a hit."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "agent/mcp.json:26-27",
     "suspicion": "context_lines '0 to 5' bound is stated in the description but not in the arg type.",
     "unresolved_fact": "Whether the files.js search handler clamps or rejects out-of-range values."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "base/servers/files.js",
     "suspicion": "Search may follow symlinks out of --root.",
     "unresolved_fact": "Whether the search walker resolves real paths and confines them under root."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "files.js root resolves wrongly.", "evidence": "--root ./docs is passed, so indexOf+1 yields './docs'; the -1 case does not arise."},
    {"id": "R2", "candidate": "Docs server is writable.", "evidence": "writable requires --allow-write and no --read-only; config passes --read-only only."},
    {"id": "R3", "candidate": "Tool descriptions contain instructions to the model.", "evidence": "All three descriptions only state function and output; no imperatives or cross-tool directions."},
    {"id": "R4", "candidate": "Drift from the request.", "evidence": "Exactly notes_search, notes_read, search_docs, all read-only, as requested."}
  ]
}
```