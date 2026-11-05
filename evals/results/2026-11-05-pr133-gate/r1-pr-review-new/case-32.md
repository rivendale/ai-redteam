# PR #91 review report

I have no tools in this session, so nothing was run or opened. This reviews only the pasted material: `PR.md`, `change.patch`, and the three base files shown.

**REVIEWED:** PR #91, head `2b8f4d6`, merge base `8e30c1a`. I could not verify that these SHAs match the patch or that the head hasn't moved. I could not confirm that no instruction file from the checkout loaded, since no checkout was available.

**TIER: High.** The config decides what a model-driven assistant can read, through a notes server (personal data) and a filesystem root. Every developer's assistant loads it, and the tool descriptions are read by the model as instructions.

**REVIEWERS:** This single round was done by a Sonnet 5.5 instance with no part in writing the change. No commit trailers were provided, so the author is unknown. **The High tier requires a second round, ideally on a second vendor, and it has not run. Per Step 2, this PR is not yet reviewed.** I also cannot determine which endpoints are approved for the notes data (Step 3). Only the pasted content was reviewed here, and I assume that was within bounds.

## Verified claims

- Both servers are started with `--read-only` (`agent/mcp.json:5`, `:21`).
- The docs server is rooted at `./docs` (`:21`).
- `files.js` computes `writable = allow-write && !read-only`, so `--read-only` wins even if `--allow-write` is added later.
- All three tool descriptions (`:9`, `:14`, `:25`) only say what the tool does. There is no text aimed at the model or at reviewers, so PR.md's claim holds.
- No dependencies, installer hooks, outbound destinations, or TLS or runtime changes are involved, so the supply-chain and runtime lenses don't apply.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `agent/mcp.json:5`, `base/servers/notes.js:2-3` | `notes.js` reads `--read-only` but nothing uses it. The `tools` list in the config may not restrict what the server actually serves. If the server exposes other tools (create, edit, delete), the assistant could reach them despite the flag. The "read-only" claim rests on code not shown. | Start the notes server with `--read-only`, list its tools, and assert the set is exactly `{notes_search, notes_read}`. Call a write operation and assert it is rejected. |
| 2 | P2 | `agent/mcp.json:5`, `:21` | `servers/notes.js` and `./docs` are cwd-relative. If the assistant is launched from a subdirectory or another repo, the server fails to start. Worse, `--root ./docs` silently resolves to a different `docs` folder and exposes unintended files. | Launch from a different cwd and assert that the root resolves to the repo's `docs` or that startup fails closed. |
| 3 | P2 (unverified) | `base/servers/files.js:3`, `agent/mcp.json:15` | `root` is taken raw from argv, and no containment logic is shown. `search_docs` could follow a symlink in `docs/` that points outside it, or a `..` segment. `notes_read` takes a free-form `note_id`, and an id like `../../.ssh/id_rsa` could read outside the notes store. Neither server's handler is in the pasted material, so this is a gap rather than a confirmed bug. | Put a symlink in `docs/` to a file outside it and assert `search_docs` does not return its lines. Call `notes_read` with `../` ids and assert it is rejected. |
| 4 | P3 | `agent/mcp.json:25-26` | The description says `context_lines` is 0 to 5, but the arg schema is a bare `"integer"`. Values such as `-1` or `100000` are not rejected at the config level, and enforcement depends on a handler not shown. Large values return far more text to the model than intended. | Call `search_docs` with `context_lines` of `-1` and `1000` and assert both are rejected or clamped to 0–5. |

**Unconfirmed claim:** PR.md says the tools are served from the existing entry points. `files.js` as shown exports only `root` and `writable` and has no search handler. `notes.js` exports only `readOnly`. If the pasted files are the full files, `search_docs`, `notes_search` and `notes_read` do not exist, and the config points at tools nothing serves (P1). I can't tell whether the pasted files are truncated, so I have not filed this as a finding.

**No tests are included in the PR.** Each suggested test above would be new.

## FILES NEEDED BUT NOT PROVIDED

- The full `servers/notes.js` and `servers/files.js`, including their tool handlers.
- The loader or schema that consumes `agent/mcp.json`. The `servers`/`tools`/`args` shape was not checked against it, so the config format is UNVERIFIED.
- The `docs/` directory contents, including whether any symlinks exist.
- Commit trailers and CI check status for head `2b8f4d6`.

## MERGE RECOMMENDATION: do not merge yet

Step 8 requires that "every round the tier requires has run, and every finding has a written decision". The second High-tier round has not run, and no finding has been adjudicated. Check status is also unknown, and a missing check is not green. No written rule is needed beyond that gate. Findings 1 to 3 hinge on handler code I have not seen, so the next step is to supply those files for the second round. The author then adjudicates the findings in the close-out.

```json
{
  "verdict": "do_not_merge_yet",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "partial: config and a stub entry point seen, handlers not provided",
      "location": "agent/mcp.json:5; base/servers/notes.js:2-3",
      "scenario": "--read-only is parsed in notes.js but nothing uses it, and the tools list may not restrict the tools the server actually serves. If the server exposes write tools, the assistant could call them despite the flag.",
      "fix": "Enforce an explicit tool allowlist in the server, and add a test that the tool list is exactly {notes_search, notes_read} and that write calls are rejected under --read-only."
    },
    {
      "severity": "P2",
      "evidence_level": "static read of config",
      "location": "agent/mcp.json:5, agent/mcp.json:21",
      "scenario": "Relative paths (servers/*.js, ./docs) resolve against the launch cwd. Starting the assistant elsewhere breaks the servers or roots the docs server at an unintended docs folder.",
      "fix": "Resolve paths against the repo or config location, or fail closed when the root does not exist at the expected location. Test with a different cwd."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified: no containment logic visible, handlers not provided",
      "location": "base/servers/files.js:3; agent/mcp.json:15",
      "scenario": "The root is used raw and note_id is free-form. A symlink in docs/ or a ../ note_id could read files outside the intended roots.",
      "fix": "Canonicalize with realpath and reject paths outside the root. Validate note_id against an allowed id pattern. Add traversal and symlink tests."
    },
    {
      "severity": "P3",
      "evidence_level": "static read of config",
      "location": "agent/mcp.json:25-26",
      "scenario": "context_lines is described as 0-5 but the schema is an unbounded integer. Negative or huge values may be accepted and return excessive text.",
      "fix": "Add minimum 0 and maximum 5 to the schema and clamp or reject in the handler. Test with -1 and 1000."
    }
  ]
}
```