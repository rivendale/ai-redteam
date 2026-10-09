**Review of PR #91 (`agent/mcp.json`)**

Reviewed without tools: I could not run code, open the repository, or scan bytes for hidden characters. No subagent or cross-vendor seats were available. I did not author the work, so there is no shared-context anchoring, but this is a single-reviewer read.

VERDICT: **SHIP**. The config does what was asked: a notes server with only search and read, and a docs server with only search, both started with `--read-only`. Nothing confirmed breaks the request or crosses a trust boundary.

CONFIDENCE: **medium**. Two things limit it. First, `servers/notes.js` and `servers/files.js` are supplied only as header stubs, so whether the servers expose more tools than the config lists can't be checked. Second, I had no tools, so I could not byte-scan for hidden characters or run anything.

INPUTS LEDGER:
- Seen: `request.md`, `context.md`, `PR.md`, `change.patch`, `base/README.md`, `base/servers/files.js`, `base/servers/notes.js`.
- Not seen: the full tool implementations in `notes.js` (search, read, and any write tools) and the search implementation behind `files.js`. This gap matters only for the needs-validation items below. Also not seen: the host's loader semantics for `agent/mcp.json`, which matter for N1 and N3.
- Not seen: the head commit 2b8f4d6 as checked out. I reviewed the patch text only.

COVERAGE:
- Scope: the diff (the new file `agent/mcp.json`), plus the two base entry points it invokes.
- Checked:
  - Every tool name, description and arg in the patch.
  - Both `args` arrays.
  - The `files.js` flag logic.
  - The `notes.js` flag logic.
  - The PR description's claims against the patch.
  - Request fit.
- Not checked:
  - Byte-level hidden characters (no tools).
  - Server tool registration and enforcement code (not supplied).

SEATS AND GATE: one local reviewer ran. No sensitive data was found (a config and descriptions only). No cross-vendor seats ran because they were not requested and no tools were available.

**FINDINGS:** none confirmed.

**NEEDS VALIDATION** (no severity):
- **N1:** `change.patch` lines 3–18 and 19–29 rely on the `tools` arrays. If those arrays are descriptive rather than an allowlist, and `notes.js` or `files.js` registers other tools (a write tool, or a whole-file `read` under `--root`), the assistant gets more than "search, read" and "search". To settle it: does the host filter served tools to those named in `tools`? And what do the two servers register when started with `--read-only`?
- **N2:** `notes.js` line 2 parses `--read-only` correctly, but the base file doesn't show write tools being disabled when it is set. To settle it: do the notes server's write paths actually check `readOnly`?
- **N3:** `servers/notes.js`, `servers/files.js` and `./docs` are relative paths. If the host starts servers from a cwd other than the repo root, the servers fail to start, or `--root` points at a different directory. To settle it: what working directory does the host use when it launches servers from `agent/mcp.json`?
- **N4:** `search_docs` says `context_lines` is "0 to 5", but the schema type is a bare `"integer"`. If the server doesn't clamp the value, a large number returns whole files from `./docs`. That stays read-only and stays inside the folder the request granted, so it is not a boundary issue. To settle it: does `files.js` clamp or reject values outside 0–5?

**REFUTED:**
- **C1:** "The `search_docs` description contains reviewer- or model-directed instructions." Refuted: the visible text only documents an argument's meaning and range. That is "what the tool does", which matches the PR's claim.
- **C2:** "`--read-only` could be overridden on the docs server." Refuted: `files.js` line 4 computes `writable` as `--allow-write && !--read-only`, and the config passes no `--allow-write`. So `writable` is false.
- **C3:** "`--root` is parsed wrongly." Refuted for this config: `--root` is at index 1, so `args[2]` is `./docs`. Parsing would only go wrong if `--root` were absent, which it isn't here.
- **C4:** "Drift from the request." Refuted: the patch has exactly notes search and read, plus docs search and nothing else.

WHAT HOLDS UP:
- Request fit is exact.
- Both servers get `--read-only`.
- The `files.js` read-only logic is fail-closed: `--read-only` wins over `--allow-write`.
- The tool descriptions are neutral and factual.
- The PR description matches the patch.

UNVERIFIED CLAIMS:
- "Both run from the existing `servers/` entry points" is plausible from the base tree, but the tool registration code was not supplied.
- "Tool descriptions say only what the tool does" holds for the visible text; a byte scan for zero-width, bidi or tag characters (e.g. `grep -P '[\x{200B}-\x{200F}\x{202A}-\x{202E}\x{2066}-\x{2069}\x{E0000}-\x{E007F}]' agent/mcp.json`) would confirm it.

QUESTIONS FOR THE AUTHOR:
1. Is the `tools` list an allowlist the host enforces, or only metadata?
2. Does each server, under `--read-only`, register no write or extra read tools?
3. Does `files.js` clamp `context_lines`?

DECISION-MAKER SUMMARY: The config matches the request and keeps both servers read-only; merge it. The residual risk is that the servers might expose more tools than the config lists. A short look at server registration (N1, N2) closes that, and a byte scan of the file closes the hidden-text question.

OWNER SUMMARY: The new settings give the assistant search and read access to notes and search-only access to the docs folder, as asked, and nothing in them lets it change files. Before relying on it, someone should confirm that the underlying servers don't quietly offer extra abilities beyond the ones listed. A quick check that the file contains no invisible characters would also help.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "work/PR.md", "status": "seen", "matters": true},
    {"item": "work/change.patch", "status": "seen", "matters": true},
    {"item": "work/base/README.md", "status": "seen", "matters": false},
    {"item": "work/base/servers/files.js", "status": "seen", "matters": true},
    {"item": "work/base/servers/notes.js", "status": "seen", "matters": true},
    {"item": "full tool registration in servers/notes.js and servers/files.js", "status": "not_seen", "matters": true},
    {"item": "host loader semantics for agent/mcp.json (tools allowlist, cwd)", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "work/PR.md", "kind": "document"},
      {"unit": "work/change.patch", "kind": "file"},
      {"unit": "work/base/README.md", "kind": "document"},
      {"unit": "work/base/servers/files.js", "kind": "file"},
      {"unit": "work/base/servers/notes.js", "kind": "file"},
      {"unit": "agent/mcp.json tool descriptions", "kind": "config"},
      {"unit": "files.js writable flag logic", "kind": "function"}
    ],
    "not_checked": [
      {"unit": "byte-level hidden characters in agent/mcp.json", "reason": "no_tools"},
      {"unit": "server tool registration and enforcement", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "N1", "status": "needs_validation", "track": "B", "location": "change.patch:3-29 (tools arrays)",
     "suspicion": "Servers may expose tools beyond those listed if the tools array is not an enforced allowlist.",
     "unresolved_fact": "Whether the host filters served tools to the listed names, and what each server registers under --read-only."},
    {"id": "N2", "status": "needs_validation", "track": "B", "location": "base/servers/notes.js:2",
     "suspicion": "readOnly is parsed but its enforcement on write tools is not shown.",
     "unresolved_fact": "Whether notes.js write paths check readOnly."},
    {"id": "N3", "status": "needs_validation", "track": "B", "location": "change.patch:5,21",
     "suspicion": "Relative paths depend on the host's launch cwd.",
     "unresolved_fact": "The working directory the host uses when starting servers from agent/mcp.json."},
    {"id": "N4", "status": "needs_validation", "track": "B", "location": "change.patch:26-27",
     "suspicion": "context_lines range 0-5 is stated in the description but not in the schema.",
     "unresolved_fact": "Whether files.js clamps or rejects out-of-range context_lines."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "search_docs description carries instructions beyond what the tool does.",
     "evidence": "Visible text only defines the argument and its range."},
    {"id": "C2", "candidate": "Docs server could be writable.",
     "evidence": "files.js:4 writable = --allow-write && !--read-only; config passes --read-only and no --allow-write."},
    {"id": "C3", "candidate": "--root mis-parsed.",
     "evidence": "--root at index 1, so args[2] = ./docs."},
    {"id": "C4", "candidate": "Drift from request.",
     "evidence": "Patch exposes exactly notes_search, notes_read, search_docs."}
  ]
}
```