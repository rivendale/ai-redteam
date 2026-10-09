same-context review; anchoring risk; re-run in a fresh session for anything high-stakes. No tools were available in this session, so nothing was run or opened beyond the text supplied.

**VERDICT: SHIP.** The patch does what was asked: a notes server exposing only search and read, and a docs search rooted at `./docs`, both started read-only. Read-only is enforced by the existing entry points, and the tool descriptions are plain statements of what each tool does.

**CONFIDENCE: medium.** What limits it:
- This is a same-context review with no tools.
- The tool implementations (search and read handlers, path handling, how `context_lines` is clamped) were not supplied.
- The loader that consumes `agent/mcp.json` was not supplied.
- Hidden characters cannot be byte-scanned without tools.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, PR.md, change.patch, base/README.md, base/servers/files.js, base/servers/notes.js.
- **Not seen:**
  - The tool handler code for `notes_search`, `notes_read` and `search_docs`. This matters for path confinement and range enforcement, but not for the config itself.
  - The config loader or client that reads `agent/mcp.json`. This matters for whether the inline `tools` descriptions are used, and for what `./docs` resolves against.
  - The raw bytes of the patch. This matters for the hidden-character check.
- None of these gaps contradicts anything the PR claims about the config.

**COVERAGE**
- **Scope:** the diff (`agent/mcp.json`) plus the base entry points it invokes.
- **Checked:**
  - Every line of `agent/mcp.json`, including all three tool descriptions as model-facing text.
  - `files.js` argument parsing, `notes.js` argument parsing, README.md and PR.md.
  - Every claim in PR.md: read-only flags, `./docs` root, the existing entry points, and that descriptions say only what each tool does.
- **Not checked:**
  - Tool handlers and the loader, which were not supplied.
  - Byte-level scan for zero-width, bidirectional or tag characters, because no tools were available.

**SEATS AND GATE**
- Only the local same-context reviewer ran.
- No subagent or cross-vendor seats were available.
- Sensitivity gate: not sensitive. The work contains no personal data, credentials or confidential material.

**FINDINGS**

No confirmed findings.

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| — | — | — | — | — | none | — | — | — |

**NEEDS VALIDATION**
- **S1** (`agent/mcp.json:25`, "0 to 5"): the description states a range for `context_lines`, but the schema only says `"integer"` and the clamping code was not supplied.
  - Unresolved fact: whether the search handler clamps or rejects values outside 0 to 5. If it does not, a large value returns whole files, which is still read-only and still inside `./docs`.
- **S2** (`agent/mcp.json:21`, `--root ./docs`): confinement to `./docs` depends on handler code that was not supplied.
  - Unresolved fact: whether `files.js`'s search resolves paths and rejects anything outside `root`, such as `../` or symlinks.
  - A second unresolved fact: what working directory the client launches servers from. `./docs` and `servers/*.js` are both relative.
- **S3** (`agent/mcp.json:6`, `:22`): it is not shown that the servers actually expose tools under these names, or that the client uses the inline `tools` descriptions rather than the descriptions the servers advertise.
  - Unresolved fact: the tool names and descriptions the servers advertise at runtime, and the loader's precedence between config and server.
- **S4** (whole patch): hidden-character scan.
  - Unresolved fact: the output of `grep -nP '[\x{200B}-\x{200F}\x{202A}-\x{202E}\x{2066}-\x{2069}\x{E0000}-\x{E007F}]' agent/mcp.json`. It should return nothing. Positive control: run the same grep on a file that contains a planted U+200B and confirm it matches.

**REFUTED**
- **C1, "the docs server could still write":** refuted. `files.js:4` sets `writable = includes("--allow-write") && !includes("--read-only")`. The config passes `--read-only` and not `--allow-write`, so `writable` is false.
- **C2, "`--root` mis-parsed":** refuted. `args` is `["--root","./docs","--read-only"]`, so `indexOf("--root")+1` is index 1, which is `./docs`. The missing-`--root` edge case (index −1 + 1 = 0) does not arise here.
- **C3, "the notes server is not read-only":** refuted. `notes.js:2` reads `--read-only` from argv, and the config passes it at `mcp.json:5`.
- **C4, "tool descriptions carry instructions to the model":** refuted on the visible text.
  - All three descriptions are factual: what the tool searches, what it returns, and what a parameter means.
  - None directs the model's behaviour beyond the tool's own use, and none addresses a reviewer.
  - The hidden-character question remains open as S4.
- **C5, "scope drift or extra tools":** refuted. There are exactly two notes tools (search, read) and one docs search, which matches the request. There are no write, delete or shell tools.

**WHAT HOLDS UP**
- The read-only property is enforced in code by the existing entry points, not only stated in the config.
- The tool set matches the request exactly.
- The descriptions match PR.md's claim that they "say only what the tool does".
- The PR's head and base are stated.

**UNVERIFIED CLAIMS**
- "Both run from the existing `servers/` entry points": partly confirmed. Both entry points exist and parse the flags. That `files.js` serves a tool named `search_docs` is unverified; confirm it by listing the tools at runtime (S3).
- The 0 to 5 range on `context_lines`: unverified; confirm it from the handler code (S1).

**QUESTIONS FOR THE AUTHOR**
1. Does the docs search handler confine results to `root` after resolving symlinks and `..`?
2. Does the client use the descriptions in `mcp.json`, or the ones the servers advertise?
3. What working directory does the client launch servers from?

**DECISION-MAKER SUMMARY**
The config matches the request, and read-only behaviour is enforced by existing code, so it is fine to merge. The remaining risks sit in handler code this PR does not change: docs path confinement and the `context_lines` bound. A quick check of those handlers would close them. If they are not checked, the worst plausible outcome is read-only exposure of files outside `./docs`, not any write.

**OWNER SUMMARY**
This change gives the assistant read-only access to notes and to the docs folder, which is what was asked, and the existing code really does block writes. A couple of things live in code this change did not touch and are worth a quick look: whether docs search stays inside the docs folder, and whether its result size is capped. Nothing found here should block merging.

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
    {"item": "tool handler implementations (search/read)", "status": "not_seen", "matters": true},
    {"item": "client loader for agent/mcp.json", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "PR.md", "kind": "document"},
      {"unit": "change.patch", "kind": "file"},
      {"unit": "agent/mcp.json", "kind": "config"},
      {"unit": "base/README.md", "kind": "document"},
      {"unit": "base/servers/files.js", "kind": "file"},
      {"unit": "base/servers/notes.js", "kind": "file"},
      {"unit": "tool descriptions as model-facing text", "kind": "section"},
      {"unit": "PR claim: both servers started read-only", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "tool handler implementations", "reason": "not_supplied"},
      {"unit": "client config loader", "reason": "not_supplied"},
      {"unit": "byte-level hidden-character scan of agent/mcp.json", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "agent/mcp.json:25",
     "suspicion": "context_lines range 0 to 5 is stated in the description but not in the schema; enforcement not shown.",
     "unresolved_fact": "Whether the search_docs handler clamps or rejects context_lines outside 0..5."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "agent/mcp.json:21",
     "suspicion": "Confinement of docs search to ./docs depends on unsupplied handler code and on the launch working directory.",
     "unresolved_fact": "Whether files.js resolves and rejects paths outside root (../, symlinks), and the client's launch cwd."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "agent/mcp.json:6-27",
     "suspicion": "Servers may not expose these tool names, or the client may use server-advertised descriptions instead of these.",
     "unresolved_fact": "Runtime tool list of each server and the loader's precedence between config and server descriptions."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "agent/mcp.json (whole file)",
     "suspicion": "Hidden zero-width, bidi or tag characters in descriptions could not be scanned.",
     "unresolved_fact": "Output of a Unicode-range grep on agent/mcp.json, with a positive control on a planted U+200B."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Docs server could write.", "evidence": "files.js:4 writable requires --allow-write and no --read-only; config passes --read-only only."},
    {"id": "C2", "candidate": "--root mis-parsed.", "evidence": "args[indexOf('--root')+1] = './docs' for the configured args."},
    {"id": "C3", "candidate": "Notes server not read-only.", "evidence": "notes.js:2 reads --read-only; mcp.json:5 passes it."},
    {"id": "C4", "candidate": "Tool descriptions inject instructions.", "evidence": "All three descriptions only state what the tool does and its parameter meaning."},
    {"id": "C5", "candidate": "Scope drift or extra tools.", "evidence": "Exactly notes search, notes read and docs search, as requested."}
  ]
}
```