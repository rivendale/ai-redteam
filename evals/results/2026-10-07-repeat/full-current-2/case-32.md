VERDICT: **SHIP WITH FIXES.** The config matches the request, and its three tool descriptions contain no hidden instructions. Before merge, three things need checking: that read-only is actually enforced in code, that the declared tool lists actually limit what the model sees, and that the relative paths resolve the same way for every developer.

CONFIDENCE: **medium.** I had no tools, so nothing was run. `base/servers/*.js` are short excerpts that show argument parsing only, not the tool implementations. I am a single reviewer, but I did not author the work, so there is no same-context anchoring.

INPUTS LEDGER:
- **Seen:** request.md, context.md, PR.md, change.patch (`agent/mcp.json`, 31 lines), base/README.md, base/servers/files.js (5 lines), base/servers/notes.js (3 lines).
- **Not seen, matters:**
  - The tool handlers in `servers/notes.js` and `servers/files.js`, meaning which tools each server registers, the descriptions it sends at runtime, and where `readOnly` is enforced.
  - Which client loads `agent/mcp.json`, and whether it honours the `tools` array.
  - Whether a `docs/` directory exists in the base.
  - Commits 2b8f4d6 and 8e30c1a.
- **Not seen, does not matter:** CI status, which is not evidence of correctness anyway.

SEATS AND GATE: One reviewer, with no subagent and no cross-vendor seats. The sensitivity gate passed: the work contains no personal data, credentials or client material. The notes the server will read are personal at runtime, but they are not part of this review.

FINDINGS:

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Medium | UNVERIFIED | B | `base/servers/notes.js:2-3`; `change.patch` notes `args` | For the notes server, read-only is only a parsed flag (`const readOnly = process.argv.includes("--read-only")`). Nothing shown makes a write, update or delete handler check it. For the docs server, `files.js:4` computes `writable` correctly (`--read-only` wins over `--allow-write`), but whether handlers check `writable` is not shown either. | If `notes.js` registers a write tool that never checks `readOnly`, then any developer's assistant can modify or delete notes, whether by a model mistake or by an injected instruction inside a note. | Point to the line in each handler that rejects writes when the flag is set. Add a test that starts each server with `--read-only` and asserts that a write call fails. Confirm the test goes red if that check is removed. | n/a (Medium) |
| 2 | Medium | PROBABLE | B | `change.patch` `"tools": [...]` in both servers | The per-server `tools` arrays with descriptions are not part of standard MCP client config: clients get tool names and descriptions from the server's `tools/list` at runtime. If the loader ignores this field, two things follow. First, the PR claim "Tool descriptions say only what the tool does" applies to strings the model never sees. Second, the list does not restrict the model to search and read. | `files.js` "serves text files under --root", so it probably also exposes read or list tools. If the client ignores `tools`, the model gets those tools, and their server-side descriptions, which were never reviewed, under the docs server. That exceeds the request's "search over the docs folder". | Name the loader and show where it filters by `tools`. If it does not filter, enforce an allowlist in the client config or the server, and review the descriptions emitted by `tools/list`. Test: connect a client and assert that the tool list is exactly `{notes_search, notes_read, search_docs}`. | n/a |
| 3 | Medium | PROBABLE | B | `change.patch` `"servers/notes.js"`, `"servers/files.js"`, `"--root", "./docs"` | All paths are relative, so they resolve against the process working directory, not the repo or the config file. | A developer whose assistant starts from a subdirectory or from `$HOME` gets "module not found". Worse, `./docs` could resolve to an unrelated `docs/` folder outside the project, exposing other files to search. | Anchor the paths to the workspace, for example with `${workspaceFolder}/docs` if the client supports it, or resolve `--root` against the config location. Also have `files.js` refuse a missing or non-directory root. | n/a |
| 4 | Low | UNVERIFIED | B | `search_docs` description, "(0 to 5)" | The 0–5 range for `context_lines` is stated in the description only, and no enforcement is shown. | If the model passes 10000 or a negative value, results may be very large or the server may error. | Clamp or reject the value in the handler, and test with -1, 6 and a non-integer. | n/a |
| 5 | Low | CONFIRMED | B | `base/servers/files.js:3` | `args[args.indexOf("--root") + 1]` falls back to `args[0]` when `--root` is absent. | This is not triggered by this config, which passes `--root`. A future config that omits it gets a root of its first argument, for example `"--read-only"`. | Throw when `--root` is missing. | n/a |

No Critical or High findings, so the confirm-or-refute round is empty.

WHAT HOLDS UP:
- **Request fit.** The config adds exactly two servers, notes (search, read) and docs (search), both started with `--read-only`. Nothing beyond the request is added.
- **Tool descriptions are clean.** I read all three in full as the positive control:
  - "Search the user's notes by keyword. Returns titles and short snippets."
  - "Return the text of one note by id."
  - "Search the docs folder for a phrase and return matching lines. `context_lines` is the number of lines shown before and after each match (0 to 5)."

  None addresses the model with instructions, mentions other tools, or asks it to send data anywhere.
- **The docs server cannot become writable from this config.** `files.js:4` makes `--read-only` override `--allow-write`, and `--allow-write` is not passed.
- **`search_docs` takes no path argument,** so there is no traversal surface through its inputs.
- **No secrets, environment variables or network endpoints** appear in the config.

UNVERIFIED CLAIMS:
- "both started with `--read-only`" is true of the args. That it makes the servers read-only depends on handler code; settle it with finding 1's test.
- "Both run from the existing `servers/` entry points" is true by path. Whether `files.js` actually registers a tool named `search_docs` is not shown; settle it by listing the tools at runtime.
- "Tool descriptions say only what the tool does" is true of the config strings. Whether those are the descriptions the model receives is unknown; see finding 2.

QUESTIONS FOR THE AUTHOR:
1. Which client loads `agent/mcp.json`, and does it filter tools by the `tools` array?
2. Where in `notes.js` is `readOnly` checked before a write?
3. What working directory does the assistant start in for every developer?

DECISION-MAKER SUMMARY: The config does what was asked, and its tool descriptions are safe. Before merge, the author should show that read-only is enforced in server code, that the model only receives the three listed tools, and that the paths resolve from any start directory. If merged without these checks, the realistic risk is an assistant that can still write to notes, or that sees extra tools whose descriptions nobody reviewed, on every developer's machine.

OWNER SUMMARY: The new setup gives the assistant search and read access to notes and documentation, as requested, and its wording is safe. Before it goes live, someone should confirm that the "read-only" setting really blocks changes and that the assistant cannot see more tools than intended. The file locations should also be made to work no matter where the assistant is started.

```json
{
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "servers/notes.js tool handlers", "status": "not_seen", "matters": true},
    {"item": "servers/files.js tool handlers", "status": "not_seen", "matters": true},
    {"item": "client loader semantics for agent/mcp.json 'tools'", "status": "not_seen", "matters": true},
    {"item": "docs/ directory in base", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "findings": [
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "base/servers/notes.js:2-3; agent/mcp.json notes args",
     "scenario": "readOnly is only parsed; if a write handler never checks it, the assistant can modify or delete notes despite --read-only",
     "fix": "Show the enforcing check in each write handler; add a test that a write fails under --read-only and goes red when the check is removed", "status": "open"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "agent/mcp.json \"tools\" arrays",
     "scenario": "If the client ignores the config-declared tools, the model receives the server's full tool list and runtime descriptions, which were never reviewed, possibly including file read/list beyond 'search docs'",
     "fix": "Confirm the loader filters by 'tools' or add an allowlist; assert that tools/list is exactly {notes_search, notes_read, search_docs}", "status": "open"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "agent/mcp.json servers/*.js and --root ./docs",
     "scenario": "Relative paths resolve against the process working directory; from another directory the server fails to start or ./docs points at an unrelated folder",
     "fix": "Anchor paths to the workspace or config directory; fail if root is missing or not a directory", "status": "open"},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "track": "B", "location": "agent/mcp.json search_docs description '(0 to 5)'",
     "scenario": "The range is stated only in the description; out-of-range context_lines may return huge output or error",
     "fix": "Clamp or validate in the handler; test -1, 6 and a non-integer", "status": "open"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "base/servers/files.js:3",
     "scenario": "A missing --root makes indexOf return -1, so root becomes args[0]; not triggered by this config",
     "fix": "Throw when --root is absent", "status": "open"}
  ]
}
```