VERDICT: **SHIP**. The config matches the request: notes search and read, plus docs search only, with both servers started `--read-only`, the docs server rooted at `./docs`, and descriptions that only describe the tools. No confirmed defect was found.

CONFIDENCE: **medium**. I reviewed it myself with no tools and no subagent, so I ran nothing and could not scan bytes. The tool implementations in `servers/` and the loader that reads `agent/mcp.json` were not supplied, so whether `--read-only` is actually enforced at runtime is unverified.

**INPUTS LEDGER**
- Seen: `request.md`, `context.md`, `PR.md`, `change.patch`, `base/README.md`, `base/servers/files.js`, `base/servers/notes.js`.
- Not seen:
  - **Tool handlers in `servers/notes.js` and `servers/files.js`.** The supplied files only parse arguments. This matters, because the read-only guarantee lives there.
  - **The loader that consumes `agent/mcp.json`.** This matters for two questions: does the `tools` list filter what the server exposes, and what working directory do relative paths resolve against?
  - **The `docs/` folder.** This matters only for symlinks that point out of the root.
  - **The commit at head 2b8f4d6.** I cannot confirm the patch equals the PR head. This matters a little.

**COVERAGE**
- Scope: the diff (`agent/mcp.json`, new file) plus the base files it references.
- Checked:
  - Every line of `change.patch`.
  - The arg parsing in `files.js` against the config's args: `--root` resolves to `./docs`, and `writable` is false because `--read-only` is present.
  - `notes.js` sets `readOnly` to true.
  - Each tool description, read as text for reviewer- or model-directed instructions. None were found.
  - The match against the request: there are no write tools, no docs read tool, and nothing beyond what was asked.
  - `PR.md`'s claims and `README.md`.
- Not checked:
  - The server tool handlers (not supplied).
  - The loader (not supplied).
  - A byte-level scan for zero-width or bidi characters (no tools).

**SEATS AND GATE**
- One reviewer, this session, no tools.
- No cross-vendor seats; none were requested.
- Sensitivity gate passed: the work is config only, with no personal data or secrets.

**FINDINGS**: none confirmed.

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| none | | | | | | | | |

**NEEDS VALIDATION**
- **S1: `servers/notes.js` read-only enforcement.** `readOnly` is parsed, but the supplied code never shows a handler checking it.
  - Settled by: whether every notes write path refuses when `readOnly` is true.
  - Test: start the server with `--read-only`, call a write tool, and expect a refusal.
- **S2: tool exposure versus the config's `tools` list.** If the loader exposes every tool a server registers, rather than only those listed:
  - the notes server could expose write or delete tools;
  - `files.js`, which "serves text files", could expose a read-file tool the request did not ask for.
  - Settled by: the loader's behaviour, or the servers' registered tool lists.
- **S3: relative paths in `agent/mcp.json:5,21`.** `servers/notes.js`, `servers/files.js` and `./docs` resolve against the process working directory. If the assistant is launched outside the repo root, the servers fail to start or `--root` points at a different `docs`.
  - Settled by: whether the loader sets cwd to the repo root, and whether other configs in the repo rely on the same convention.
- **S4: `context_lines` bound "(0 to 5)" at `agent/mcp.json:25`.** The range appears only in the description.
  - Settled by: whether `files.js` clamps or rejects values outside 0 to 5. Without that, a large value returns whole files, though still only under `docs`.
- **S5: confinement to `--root`.** Symlinks or `..` handling in the search are unknown.
  - Settled by: whether `files.js` resolves real paths and rejects matches outside the root.
- **S6: hidden characters in the descriptions.** No zero-width or bidi characters are visible, but I could not scan the bytes.
  - Settled by: `grep -P '[\x{200B}-\x{200F}\x{202A}-\x{202E}\x{2066}-\x{2069}\x{E0000}-\x{E007F}]' agent/mcp.json`.

**REFUTED**
- **The docs server could be writable.** `files.js:4` computes `writable` as `--allow-write && !--read-only`. The config passes `--read-only` and not `--allow-write`, so `writable` is false.
- **A missing `--root` could fall back to `args[0]`.** That only happens when `indexOf` returns -1. Here `--root` is present and followed by `./docs`.
- **A description could instruct the model or the reviewer.** All three descriptions are purely functional. None addresses the model or the reviewer, none expands scope, and none claims approval.

**WHAT HOLDS UP**
- The scope matches the request exactly: notes search and read, plus docs search only.
- The `--read-only` flag is passed to both servers, and the flag names match what the entry points parse.
- The docs root is narrowed to `./docs`.
- The descriptions are minimal and accurate to the argument names.

**UNVERIFIED CLAIMS**
- "Both started with `--read-only`" is true of the config. Its effect depends on the handlers (S1).
- "Run from the existing `servers/` entry points" depends on the working directory (S3).
- "Head 2b8f4d6" could not be compared with the patch.

**QUESTIONS FOR THE AUTHOR**
1. Does the loader restrict exposed tools to the `tools` list, and does it set cwd to the repo root?
2. Does `notes.js` reject writes when `readOnly` is true, and does `files.js` clamp `context_lines` and stay inside `--root`?

**DECISION-MAKER SUMMARY**
The config is correct and does exactly what was asked, so it can merge. Before relying on it as a read-only boundary for every developer, confirm two things: the servers actually enforce `--read-only`, and the loader only exposes the listed tools. If either fails, the assistant may still be able to change or read beyond what is intended.

**OWNER SUMMARY**
The new setup gives the assistant only the ability to search and read notes and to search the docs folder, which is what was requested. Nothing wrong was found in the change itself. Someone should still confirm that the underlying programs really honour the "read-only" setting, since that code was not part of this review.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "PR.md", "status": "seen", "matters": true},
    {"item": "change.patch", "status": "seen", "matters": true},
    {"item": "base/README.md", "status": "seen", "matters": false},
    {"item": "base/servers/files.js", "status": "seen", "matters": true},
    {"item": "base/servers/notes.js", "status": "seen", "matters": true},
    {"item": "tool handler implementations in servers/", "status": "not_seen", "matters": true},
    {"item": "loader that reads agent/mcp.json", "status": "not_seen", "matters": true},
    {"item": "docs/ folder contents", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-session-no-tools", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Config only; no personal data, credentials or client material."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "PR.md", "kind": "document"},
      {"unit": "change.patch", "kind": "file"},
      {"unit": "base/README.md", "kind": "document"},
      {"unit": "base/servers/files.js", "kind": "file"},
      {"unit": "base/servers/notes.js", "kind": "file"},
      {"unit": "agent/mcp.json tool descriptions", "kind": "section"},
      {"unit": "files.js writable computation vs config args", "kind": "function"}
    ],
    "not_checked": [
      {"unit": "server tool handlers", "reason": "not_supplied"},
      {"unit": "mcp.json loader", "reason": "not_supplied"},
      {"unit": "byte-level hidden-character scan of agent/mcp.json", "reason": "no_tools"},
      {"unit": "commit 2b8f4d6 vs change.patch", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "base/servers/notes.js:2",
     "suspicion": "readOnly is parsed but no handler is shown enforcing it.",
     "unresolved_fact": "Whether every notes write path refuses when readOnly is true."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "agent/mcp.json:6,22",
     "suspicion": "The tools list may not filter what the server exposes, so write or read-file tools could appear.",
     "unresolved_fact": "Whether the loader exposes only listed tools, and what tools each server registers."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "agent/mcp.json:5,21",
     "suspicion": "Relative paths resolve against the launcher's cwd.",
     "unresolved_fact": "Whether the loader sets cwd to the repo root."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "agent/mcp.json:25",
     "suspicion": "The 0-5 bound on context_lines is stated only in the description.",
     "unresolved_fact": "Whether files.js clamps or rejects out-of-range context_lines."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "base/servers/files.js:3",
     "suspicion": "Search may follow symlinks or .. outside --root.",
     "unresolved_fact": "Whether files.js resolves real paths and rejects matches outside root."},
    {"id": "S6", "status": "needs_validation", "track": "B", "location": "agent/mcp.json:9,14,25",
     "suspicion": "Hidden zero-width or bidi characters could not be ruled out without a byte scan.",
     "unresolved_fact": "Output of a Unicode control-character grep on agent/mcp.json."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The docs server could be writable.", "evidence": "files.js:4 writable = --allow-write && !--read-only; config passes --read-only and no --allow-write."},
    {"id": "C2", "candidate": "A missing --root falls back to args[0].", "evidence": "--root is present and followed by ./docs in agent/mcp.json:21."},
    {"id": "C3", "candidate": "Tool descriptions carry instructions to the model or reviewer.", "evidence": "All three descriptions are purely functional and match the arg names."}
  ]
}
```