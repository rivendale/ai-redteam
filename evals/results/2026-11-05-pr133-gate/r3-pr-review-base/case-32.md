# PR #91 review report

**REVIEWED:** PR #91, head `2b8f4d6`, merge base `8e30c1a`. This is a read of `PR.md`, `change.patch` and `base/` only. Nothing was run, and no tools were available in this session.

**TIER: High.** The file defines what a coding assistant on every developer's machine may read: personal notes and a file tree. That is permissions and data-handling configuration, and the tier follows from that, not from the 31-line size. This is round 1 of the two rounds High requires. **Round 2 (ideally a different vendor) has not run, so this PR is not yet reviewed to its tier.**

**Step 3 (data):** The reviewed material is config only, with no note content. Before round 2, or before anyone runs this against real notes, someone must confirm which model endpoints are approved for the user's notes, since `notes_read` returns note text to the model. I have no evidence on that.

**REVIEWERS:** A fresh Sonnet 5.5 instance (`claude-sonnet-5-5`) with no part in writing the change. The author is unknown because no commit trailers were provided.

## What checked out

- **Flags:** The diff passes `--read-only` to both servers (`agent/mcp.json:5`, `:21`).
- **Docs server:** `--root ./docs` is present, and `--allow-write` is absent. In `base/servers/files.js`, `writable` is false in that case, so the docs server is read-only twice over.
- **Entry points:** `servers/notes.js` and `servers/files.js` both exist in the base, as the PR says.
- **Tool descriptions:** They describe function only. I found no text addressed to the model or the reviewer, and no injection.
- **Scope:** The request asked for note search and read, plus docs search. The diff delivers exactly that, with no read tool for docs and nothing extra.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 (UNVERIFIED) | `agent/mcp.json:5`, `base/servers/notes.js:2` | The read-only guarantee for the notes server cannot be confirmed. In `notes.js` the `--read-only` flag is only parsed and exported as `readOnly`, and nothing in the visible code uses it. The tool implementations are not provided. If the server also serves a write or delete tool, or ignores the flag, the assistant gets write access to the user's notes. It is also unknown whether the loader treats the `tools` list as an allowlist, or the server exposes whatever it implements. | Start the notes server with `--read-only` and list its tools. Assert that the set equals `{notes_search, notes_read}` and that any write-style call is rejected. |
| 2 | P2 | `agent/mcp.json:5`, `:21` | Command paths and `./docs` are relative to the assistant's working directory. If the assistant is opened in a subdirectory, the servers fail to start. If it is opened in another repo that has its own `servers/notes.js` or `docs/`, it runs that repo's script, or searches that repo's docs, under this trusted config. This depends on how the loader resolves paths, which is not shown. | Load the config with cwd set to a temp directory containing a decoy `servers/notes.js`. Assert that the decoy is not executed and that the intended server path is used. |
| 3 | P3 | `agent/mcp.json:25-26` | The description limits `context_lines` to 0–5, but the schema is just `"integer"` with no bounds. A prose limit does not enforce anything. A call with `context_lines: 100000` or `-1` may return huge output or be mishandled, depending on the unseen server code. | Call `search_docs` with 6, -1 and 1000000. Assert that each is rejected or clamped to 0–5. |
| 4 | P3 | `base/servers/files.js`, not in the diff | The `./docs` containment depends on the files server's path handling, which is not provided. A `..` segment or a symlink inside `docs/` that points outside it could expose files beyond the folder. This is unverified and not a confirmed exploit. | Put a symlink in a temp `docs/` pointing at a file outside it. Assert that `search_docs` does not return its contents. |

Nothing in the PR tests any of this. A config-load test with a tool-list assertion would cover findings 1 and 2.

**FILES NEEDED BUT NOT PROVIDED:** the real implementations behind `servers/notes.js` (its tool handlers and use of `readOnly`) and `servers/files.js` (the search tool, argument validation and path resolution). Also the loader that reads `agent/mcp.json`, to show how `tools` and relative paths are handled, and the list of CI checks, which I did not see.

**Merge status:** Not clear to merge under Step 8. The required second round has not run, and findings 1 and 2 are open. The close-out and adjudication are for the author and whoever closes the PR, not for this reviewer.

```json
{
  "verdict": "do not merge yet: High-tier second round not run; read-only enforcement unverified",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "unverified",
      "location": "agent/mcp.json:5; base/servers/notes.js:2",
      "scenario": "readOnly is parsed and exported in notes.js but nothing visible enforces it, and the tool handlers are not provided. If the server serves write tools or ignores the flag, the assistant can modify notes. Whether the tools list acts as an allowlist is also unknown.",
      "fix": "Provide the server implementation and loader. Add a test that lists tools under --read-only and asserts only notes_search and notes_read exist and writes are rejected."
    },
    {
      "severity": "P2",
      "evidence_level": "plausible",
      "location": "agent/mcp.json:5, agent/mcp.json:21",
      "scenario": "Relative paths (servers/*.js, ./docs) resolve against the assistant's cwd. Opened in another repo with its own servers/notes.js or docs/, the assistant would run or search that repo's content under this trusted config.",
      "fix": "Resolve paths against the config file or repo root, or use absolute or anchored paths. Add a test with a decoy servers/notes.js in a different cwd."
    },
    {
      "severity": "P3",
      "evidence_level": "unverified",
      "location": "agent/mcp.json:25-26",
      "scenario": "context_lines 0-5 is stated only in prose; the schema has no bounds. Out-of-range values (-1, 1000000) may produce unbounded output or errors.",
      "fix": "Add minimum 0 and maximum 5 to the schema and enforce or clamp server-side. Test with 6, -1 and 1000000."
    },
    {
      "severity": "P3",
      "evidence_level": "unverified",
      "location": "base/servers/files.js (not in diff)",
      "scenario": "Containment to ./docs depends on unseen path handling. A .. segment or symlink inside docs/ could expose files outside the root.",
      "fix": "Provide files.js internals. Add a test with a symlink in docs/ pointing outside and assert it is not readable."
    }
  ]
}
```