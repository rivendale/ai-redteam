**Review report**

**REVIEWED:** PR #91 at head `2b8f4d6`, merge base `8e30c1a`. I read the files supplied in the inputs (`PR.md`, `change.patch`, `base/`). I had no tools in this session, so there was no worktree and nothing was run. If the head has moved past `2b8f4d6`, the later commits were not reviewed.

**TIER:** High. The change is small, but it is configuration that decides access: write capability (`--read-only`) and which filesystem root gets exposed (`--root ./docs`). Every developer's assistant loads it, and the model reads the tool descriptions as instructions. **High tier requires two rounds. This is round 1 only, so the PR is not yet reviewed under the skill.**

**REVIEWERS:** Claude Opus 5.5 (`claude-opus-5-5`), a separate instance. This session did not write the change. No commit trailers were provided, so I could not determine the author. Data approval (Step 3): the content is config only, with no personal data or secrets in the diff.

**Verified against the code:**
- **Docs server write protection holds.** At `base/servers/files.js:4`, `writable` requires `--allow-write` and the absence of `--read-only`. The config passes `--read-only` and no `--allow-write`, so `writable === false`.
- **Tool descriptions are clean.** All three (`agent/mcp.json:9,14,25`) only describe what the tool does. None contains an instruction aimed at the model, such as calling other tools, sending data anywhere, or overriding the user.
- **Scope matches the request.** The notes server has search and read, the docs search is read-only, and nothing extra was added.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `agent/mcp.json:21` (also `:5`) | `--root ./docs` and `servers/*.js` are relative paths. Node resolves them against the process working directory, not the repo. Suppose a developer's assistant starts the server from a subdirectory or from `~`. The docs server is then either rooted at a different `docs/` folder (for example `~/docs`, which exposes unintended files to the model) or fails to start. `files.js:3` takes the root verbatim, and no resolution is visible. | Spawn the docs server with `cwd` set to a temp directory containing its own `docs/secret.txt`. Assert that `search_docs` cannot return `secret.txt` and only searches `<repo>/docs`. This fails today. |
| 2 | P3 | `agent/mcp.json:25-26` | The description promises `context_lines` is "0 to 5", but the arg schema is a bare `integer`, and nothing in `files.js` enforces the range. A call with `context_lines: 100000` returns whole docs files instead of snippets. The bound exists only as advice to the model. This stays within the read-only docs root, so the impact is volume and context flooding, not exposure. | Call `search_docs` with `context_lines: 1000` on a 50-line file. Assert it is rejected or clamped to 5 lines each side. |

**FILES NEEDED BUT NOT PROVIDED:**
- The notes server tool implementation. `base/servers/notes.js` as supplied only exports `readOnly`. I could not see `notes_search` or `notes_read`, or confirm that `readOnly` actually gates any write tools.
- The `search_docs` implementation in, or under, `servers/files.js`. Its root confinement (path traversal handling) and `context_lines` handling are not visible.
- The assistant's config loader. I need to know whether it uses the `tools` blocks in `agent/mcp.json` or takes tool names and descriptions from the servers themselves. If the servers supply them, the descriptions the model actually reads are in code that was not reviewed.

**Close-out:** not written. The author adjudicates the findings, and a reviewer does not adjudicate its own findings.

**Recommendation for the owner:** do not merge yet. Neither finding is a blocker. Two things are still open:
1. The second High-tier round, ideally from another approved vendor.
2. The missing files above. Without them, the read-only claim for the notes server is unverified.

```json
{
  "verdict": "not ready: High tier, round 1 of 2 complete; no P0/P1; notes server read-only enforcement and loader behaviour unverified (files not provided)",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "inferred from code (files.js:3 uses --root verbatim; relative path resolution depends on launcher cwd, not shown)",
      "location": "agent/mcp.json:21",
      "scenario": "Assistant launches the docs server from a cwd other than the repo root; './docs' resolves elsewhere (e.g. ~/docs), exposing unintended files to search_docs, or the server fails to start because 'servers/files.js' is not found.",
      "fix": "Resolve the root and entry points relative to the config/repo (absolute path or ${workspaceFolder}-style variable, or resolve against __dirname in files.js), and add a test spawning from a foreign cwd."
    },
    {
      "severity": "P3",
      "evidence_level": "inferred from code (no range check in shown files.js; schema is bare integer)",
      "location": "agent/mcp.json:25-26",
      "scenario": "Model calls search_docs with context_lines=100000; whole docs files are returned instead of snippets, since the 0-5 bound exists only in the description.",
      "fix": "Enforce the bound server-side (reject or clamp to 0..5) and express it in the schema (minimum 0, maximum 5)."
    }
  ]
}
```