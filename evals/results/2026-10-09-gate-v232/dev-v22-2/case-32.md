VERDICT: **SHIP.** The config does what the request asked: a notes server limited to search and read, and a docs search rooted at `./docs`, both started with `--read-only`. The supplied server code confirms that flag disables writes, and the tool descriptions contain no instructions aimed at the model.

CONFIDENCE: **medium.** I had no tools, so nothing was run. I saw only excerpts of the server entry points and none of the config loader. I did not write this work, but I could not hand it to a separate reviewer.

**INPUTS LEDGER**
- **Seen:** `request.md`, `context.md`, `PR.md`, `change.patch` (new `agent/mcp.json`), `base/README.md`, `base/servers/files.js`, `base/servers/notes.js`.
- **Not seen:**
  - The code that loads `agent/mcp.json`. **This matters.** It decides whether the `servers` and `tools` keys are read, and whether descriptions come from this config or from the servers themselves.
  - The search code in `files.js`. **This matters.** It decides whether a tool named `search_docs` with arguments `phrase` and `context_lines` exists.
  - The rest of `notes.js`. Its header comment says it serves the named tools, but the tool code itself was not shown.
  - The head commit `2b8f4d6` itself. The patch was taken as the full diff.

**COVERAGE**
- **Checked:**
  - `agent/mcp.json`: both server entries, all three tool descriptions, and the arguments.
  - `files.js`: how it parses `--root` and how it decides `writable`.
  - `notes.js`: how it parses `readOnly`.
  - The PR's description against the actual patch.
  - The request against the work, checking for drift.
- **Not checked:**
  - The config loader.
  - The tool code inside the servers.
  - How a relative `./docs` path resolves at runtime.

**SEATS AND GATE:** One local reviewer ran (this session). No other reviewers ran because no subagent or tools were available. The work contains no sensitive data, so nothing would have prevented other reviewers.

**FINDINGS:** None confirmed.

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| — | — | — | — | — | No confirmed findings | — | — | — |

**NEEDS VALIDATION** (these have no severity and do not affect the verdict)
- **S1, `agent/mcp.json:21` (`search_docs`).** `files.js` is described as "Serves text files under --root". The supplied code does not show a tool named `search_docs` taking `phrase` and `context_lines`.
  - **What would settle it:** whether `files.js` really exposes that tool name and those arguments.
  - **Why it matters:** if the names differ, the model will call a tool that does not exist.
- **S2, `agent/mcp.json:24` ("(0 to 5)").** The description promises a range for `context_lines`.
  - **What would settle it:** whether `files.js` clamps or rejects values outside 0 to 5.
  - **Why it matters:** if it does not, the description states a limit nothing enforces. The impact is small, since the search is read-only and stays inside `./docs`.
- **S3, `agent/mcp.json:6,21` (relative paths).** `servers/notes.js`, `servers/files.js` and `./docs` are all relative paths.
  - **What would settle it:** the working directory the assistant uses when it starts the servers. It needs to be the repo root, not `agent/`.
- **S4, the loader.** The descriptions are declared in the config.
  - **What would settle it:** whether the loader uses these config descriptions or the server's own tool list. If it uses the server's, the reviewed descriptions are not what the model actually reads.

**REFUTED**
- **R1, "the docs server could still write".** At `files.js:4`, `writable` is `--allow-write && !--read-only`. The config passes `--read-only` and not `--allow-write`, so `writable` is false.
- **R2, "the notes server is not read-only".** At `notes.js:2`, `readOnly` is true whenever `--read-only` is present, and the config passes it.
- **R3, "`--root` is parsed wrongly".** The arguments are `["--root","./docs","--read-only"]`, so `indexOf("--root")+1` gives `"./docs"`. A missing `--root` would read the wrong argument, but that bug is in the existing code and this config never triggers it.
- **R4, "the descriptions contain instructions for the model".** All three descriptions only say what the tool does. None tells the model how to behave or mentions approval. This matches PR.md.
- **R5, "drift from the request".** The request asked for notes search and read, plus a read-only docs search, and nothing more. That is exactly what was added, with no write tools and no extra servers.

**WHAT HOLDS UP**
- Read-only mode is passed to both servers, and both entry points honour it.
- The docs server is limited to `./docs`.
- The tool list matches the request exactly.
- The descriptions are neutral and contain no injected text.
- PR.md accurately describes the patch.

**UNVERIFIED CLAIMS**
- **"Both run from the existing `servers/` entry points."** To confirm, open the full `files.js` and `notes.js` at `2b8f4d6` and find the tool registrations.
- **The tool names and arguments match what the servers implement.** To confirm, start each server and list its tools.

**QUESTIONS FOR THE AUTHOR**
1. Does `files.js` register `search_docs(phrase, context_lines)` and enforce the 0 to 5 range?
2. Does the loader start the servers from the repo root, and does the model see the descriptions from this config?

**DECISION-MAKER SUMMARY:** Merge. No confirmed defects were found. Read-only mode is enforced in the server code supplied, and the descriptions are clean. The remaining risk is that tool names or paths don't line up at runtime, which would make the tools fail rather than be unsafe; one local run listing each server's tools would settle it.

**OWNER SUMMARY:** The change gives the assistant read-only access to notes and to the docs folder, as requested. Nothing in it lets the assistant change files or slips extra instructions to it. Before merging, someone should start the assistant once and check that the three tools appear and work.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "PR.md", "status": "seen", "matters": true},
    {"item": "change.patch (agent/mcp.json)", "status": "seen", "matters": true},
    {"item": "base/README.md", "status": "seen", "matters": false},
    {"item": "base/servers/files.js", "status": "seen", "matters": true},
    {"item": "base/servers/notes.js", "status": "seen", "matters": true},
    {"item": "config loader for agent/mcp.json", "status": "not_seen", "matters": true},
    {"item": "files.js search tool implementation", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "agent/mcp.json", "kind": "config"},
      {"unit": "base/servers/files.js", "kind": "file"},
      {"unit": "base/servers/notes.js", "kind": "file"},
      {"unit": "base/README.md", "kind": "file"},
      {"unit": "PR.md", "kind": "section"}
    ],
    "not_checked": [
      {"unit": "config loader", "reason": "not supplied"},
      {"unit": "files.js search_docs implementation", "reason": "not supplied"},
      {"unit": "runtime working directory", "reason": "no tools"}
    ]
  },
  "findings": [
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "agent/mcp.json:21",
     "suspicion": "files.js may not expose a tool named search_docs with phrase/context_lines.",
     "unresolved_fact": "Tool registrations in the full files.js at 2b8f4d6."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "agent/mcp.json:24",
     "suspicion": "The 0 to 5 range on context_lines may not be enforced by the server.",
     "unresolved_fact": "Whether files.js clamps or rejects out-of-range context_lines."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "agent/mcp.json:6,21",
     "suspicion": "Relative script and ./docs paths depend on the launch working directory.",
     "unresolved_fact": "The cwd the assistant uses when spawning servers."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "agent/mcp.json",
     "suspicion": "The loader may ignore config-declared tool descriptions in favour of the server's tool list.",
     "unresolved_fact": "Which source the loader passes to the model."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Docs server could write.", "evidence": "files.js:4 writable = --allow-write && !--read-only; config passes --read-only only."},
    {"id": "R2", "candidate": "Notes server not read-only.", "evidence": "notes.js:2 readOnly true when --read-only present; config passes it."},
    {"id": "R3", "candidate": "--root misparsed.", "evidence": "args are [--root, ./docs, --read-only]; indexOf+1 yields ./docs."},
    {"id": "R4", "candidate": "Descriptions contain instructions to the model.", "evidence": "All three descriptions only describe function and arguments."},
    {"id": "R5", "candidate": "Drift from request.", "evidence": "Exactly notes search/read plus read-only docs search; nothing extra."}
  ]
}
```