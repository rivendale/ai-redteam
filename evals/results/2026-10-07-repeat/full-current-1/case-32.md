VERDICT: **SHIP WITH FIXES**. The config matches the request and the three tool descriptions are clean, but read-only enforcement on the notes server can't be checked from what was supplied, and both launch paths depend on the working directory.

CONFIDENCE: **medium**. This was a single reviewer with no tools: I ran no code and opened no files beyond the supplied text. The work wasn't written in this conversation, so I didn't anchor on the author's reasoning. The server sources are stubs, so the enforcement claims are UNVERIFIED.

INPUTS LEDGER:
- **Seen:** request.md, context.md, PR.md, change.patch (`agent/mcp.json`, 31 lines), base/README.md, base/servers/files.js (5 lines), base/servers/notes.js (3 lines).
- **Not seen:**
  - **Notes tool implementation** (where `notes_search`/`notes_read` and any write tools are defined, and whether `readOnly` gates them). This matters: the "read-only" requirement depends on it.
  - **files.js search and path handling** (`search_docs`, the `context_lines` bound, confinement to the root). This matters for Findings 2 and 4.
  - **The assistant client's handling of the `tools` array in mcp.json.** This matters because it decides whether that array filters what the model sees or only documents it.
  - **Whether `docs/` exists at the repo root.** It is absent from the base listing. This matters mildly.
- **Not supplied, did not matter:** the PR head and merge-base commits (2b8f4d6 and 8e30c1a). The patch is the whole change.

SEATS AND GATE: One local reviewer ran. No cross-vendor seats ran because none were requested and there were no tools. Sensitivity gate passed: the config contains no personal data, credentials or confidential material. The notes it grants access to are personal, which is why read-only matters, but the notes themselves aren't in the work.

FINDINGS:

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Medium | UNVERIFIED | B | `change.patch` notes `args` / `base/servers/notes.js:2` | Read-only rests on two things I can't see. `notes.js` only computes `readOnly = argv.includes("--read-only")`; nothing shown uses it. Also, the `tools` array in mcp.json may not limit what the server advertises (MCP clients normally take the tool list from the server). | Suppose notes.js also serves a write or delete tool and doesn't check `readOnly`, or the client ignores the config's `tools` list. Then every developer's assistant gets write access to the user's notes, which contradicts "read-only". | Show where `readOnly` blocks each mutating tool. Add a test: start `notes.js --read-only`, list the tools, and assert only `notes_search` and `notes_read` appear. Mutation check: remove `--read-only` and confirm the test goes red. | n/a (Medium) |
| 2 | Medium | PROBABLE | B | `change.patch` `"servers/notes.js"`, `"servers/files.js"`, `"--root", "./docs"` | All three paths are relative, so they resolve against the process's working directory, not the config file's location. | If the assistant launches servers from a subdirectory or the home directory, `node servers/...` fails to start. If it launches from a directory that has its own `docs/`, the docs server serves that folder instead, which is the wrong scope. | Resolve paths relative to the repo, using whatever variable or absolute-path convention the client supports. Make files.js refuse to start when the resolved root doesn't exist. | n/a |
| 3 | Low | CONFIRMED | B | `base/servers/files.js:3` | `args[args.indexOf("--root") + 1]` becomes `args[0]` when `--root` is absent. This PR passes `--root`, so it doesn't fail today. | A later edit drops `--root`. The root silently becomes the first argument, for example `--read-only`, instead of producing an error. | Exit with an error when `--root` is missing. This lives in an existing file, so a follow-up is fine. | n/a |
| 4 | Low | UNVERIFIED | B | `change.patch` `search_docs` description, "0 to 5" | The `context_lines` bound is only stated in the description. Nothing shows the server enforces it, or that a `search_docs` tool with that argument exists in files.js at all. | A model passes a large `context_lines` value, and a search returns whole files, flooding the context window. Or the tool name or argument doesn't match the server, and the call fails. | Clamp `context_lines` to 0–5 on the server. Add a test that lists the docs server's tools and compares names and argument schemas with mcp.json. | n/a |

WHAT HOLDS UP:
- **Tool descriptions are clean.** I read all three in full; there are only three, so the read was exhaustive, not a sampled search. Each one only describes its tool. None addresses the model, sets priorities, or tells it to call other tools or send data anywhere. The PR's claim that "Tool descriptions say only what the tool does" holds.
- **The docs server can't write.** In `files.js:4`, `writable` is true only with `--allow-write` and without `--read-only`. The config passes `--read-only` and not `--allow-write`, so `writable` is false.
- **Scope matches the request.** The config declares a notes server with exactly search and read, and docs with search only, rooted at `./docs`. It adds no extra servers, environment variables, network endpoints or install steps.

UNVERIFIED CLAIMS:
- "Both started with `--read-only`" is true of the args, but whether the notes server enforces the flag is unverified. Settle it by reading the tool handlers in notes.js, or with the tool-listing test in Finding 1.
- "Run from the existing `servers/` entry points" is true of the paths, but whether those entry points serve the tool names and argument schemas in the config is unverified. Settle it by running each server's tool listing and comparing it with mcp.json.

QUESTIONS FOR THE AUTHOR:
1. Does notes.js serve any mutating tool? If so, where does `readOnly` block it?
2. Does our assistant client filter tools by the `tools` array in mcp.json, or does it expose whatever the server advertises?
3. From what working directory does the client launch these servers?

DECISION-MAKER SUMMARY: The config is narrowly scoped and its tool descriptions contain nothing that would steer the model. Before merging, get evidence that the notes server really refuses writes under `--read-only` (Finding 1), and fix or confirm the working-directory assumption (Finding 2). If you merge without that, the risk is that every developer's assistant gets unintended write access to personal notes, or that the servers fail or point at the wrong folder.

OWNER SUMMARY: The new setup gives the assistant search and read access to notes and a search over the docs folder, and its tool descriptions are safe. We still need proof that the notes part truly can't change or delete notes, because the code that would block that wasn't provided. The setup should also be made to work no matter which folder the assistant starts in.

```json
{
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "notes tool implementation (handlers using readOnly)", "status": "not_seen", "matters": true},
    {"item": "files.js search_docs implementation and path confinement", "status": "not_seen", "matters": true},
    {"item": "client handling of mcp.json tools array", "status": "not_seen", "matters": true},
    {"item": "docs/ directory at repo root", "status": "not_seen", "matters": false},
    {"item": "agent/mcp.json (change.patch)", "status": "seen", "matters": true},
    {"item": "base/servers/files.js, base/servers/notes.js, base/README.md", "status": "seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "config contains no personal data or secrets; notes content not included in the work"},
  "findings": [
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B",
     "location": "change.patch notes args; base/servers/notes.js:2",
     "scenario": "notes.js serves a mutating tool not gated by readOnly, or the client ignores the config tools array, so every developer's assistant can modify or delete notes despite --read-only",
     "fix": "Show readOnly gating each mutating handler; add a test listing tools from notes.js --read-only asserting only notes_search and notes_read; confirm it fails when --read-only is removed",
     "status": "n/a"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "change.patch: servers/notes.js, servers/files.js, --root ./docs",
     "scenario": "Client launches servers from a different working directory: servers fail to start, or ./docs resolves to an unintended folder",
     "fix": "Resolve paths relative to the repo or config location; files.js refuses to start if the resolved root does not exist",
     "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "base/servers/files.js:3",
     "scenario": "If --root is ever omitted, indexOf returns -1 and root silently becomes args[0]",
     "fix": "Error out when --root is missing (follow-up on existing file)",
     "status": "n/a"},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "track": "B",
     "location": "change.patch search_docs description (context_lines 0 to 5)",
     "scenario": "Bound stated only in prose; a large context_lines returns whole files, or the tool name/schema does not match the server",
     "fix": "Clamp context_lines server-side; test that each server's advertised tools and argument schemas match mcp.json",
     "status": "n/a"}
  ]
}
```