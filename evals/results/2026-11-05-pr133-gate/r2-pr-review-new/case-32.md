# pr-review: PR #91, read-only notes and docs servers

## Review report

**REVIEWED:** PR #91, head `2b8f4d6`, merge base `8e30c1a`. I read only the supplied PR text, the patch and the base excerpts. I could not open a checkout or confirm that no checkout instruction file loaded. This session started in an unrelated directory, and the patch touches no `AGENTS.md`, `CLAUDE.md` or skill files.

**TIER:** High. The config decides which data and which filesystem root the assistant can reach. It exposes the user's personal notes to a model on every developer's machine, and tool descriptions are read as instructions. Tier is set by what the change touches, not by its 31 lines.

**REVIEWERS:** This is one reviewer round, from a single instance of Sonnet 5.5. No commit trailers were supplied, so the author is unknown and independence cannot be confirmed. The High tier's second round, ideally on a different vendor, has not run. I have not established which endpoints are approved for notes data (Step 3), and no code was sent anywhere. The PR is not fully reviewed under this skill until that round runs.

**Checked and found clean:**
- The three tool descriptions (`notes_search`, `notes_read`, `search_docs`) describe only what each tool does. They contain no instructions to the model and no text addressed to reviewers.
- The PR's claim that descriptions "say only what the tool does" holds.
- The `--read-only` flag on `files.js` works as claimed: `writable = allow-write && !read-only`, and no `--allow-write` is passed.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 (UNVERIFIED) | `agent/mcp.json:25-29` (`search_docs`), `base/servers/files.js` | The config advertises `search_docs` with `phrase` and `context_lines`. The `files.js` shown only parses `--root` and `--allow-write` and exports `{root, writable}`. It registers no search tool and has no `context_lines` handling. The PR changes no server file, so if this is the full file, the model is offered a tool that fails or does not exist. | Start the docs server with the shipped args and call `search_docs{phrase:"x", context_lines:2}`. Assert matching lines come back with 2 lines of context. |
| 2 | P1 (UNVERIFIED) | `agent/mcp.json:7-17`, `base/servers/notes.js` | Same gap for `notes_search` and `notes_read`. The `notes.js` comment says the tools are served from there, but the shown code defines none, and `readOnly` is exported and never used. If the tools are missing, or later added with a write path, the flag does nothing. | Call `notes_search` and `notes_read` against a fixture note store. Assert that a write-capable tool, if one exists, is absent or rejected under `--read-only`. |
| 3 | P2 (UNVERIFIED) | `agent/mcp.json:23-24` | `--root ./docs` and `servers/files.js` resolve against the assistant's launch cwd, not the config's location. A developer who launches from a subdirectory or another repo gets a missing root, so `root` is `undefined` or a different `./docs`. `files.js` shows no confinement check. A `../` path or a symlink in docs could read outside the root, which is a data-exposure risk. | Launch from a different cwd and assert the server fails closed or resolves the same root. With a docs symlink to `/etc` and a `../` query, assert nothing outside the root is returned. |
| 4 | P2 (UNVERIFIED) | `agent/mcp.json:27-29` | The `0 to 5` bound on `context_lines` appears only in the description, not as a schema constraint. A model-supplied `-1`, `10000` or a non-integer depends on server code I cannot see. Large values could return whole files. | Call with `-1`, `6` and `1e9`. Assert rejection or clamping to 0..5. |
| 5 | P2 | `agent/mcp.json:4-18` | The `tools` arrays may not act as an allowlist. The consumer schema is not provided, and the layout (`servers`/`tools`/`args`) differs from the common MCP form. If the loader ignores `tools`, the servers expose whatever they implement. "Read-only" then depends only on the flags in findings 1 and 2. | Load the config in the real loader and list the tools the model sees. Assert exactly these three. |
| 6 | P3 | PR as a whole | No test or doc change accompanies the config, so none of the read-only, root or bounds claims are demonstrated. "Read-only" is an assertion until a test is seen. | Add a config test covering findings 1-5. |

**FILES NEEDED BUT NOT PROVIDED:**
- Full `servers/files.js` and `servers/notes.js` at the head. The excerpts look abbreviated.
- The loader or schema that reads `agent/mcp.json`.
- The notes store and its path.
- Any tests.
- CI check results.
- Commit trailers.
- Proof of the head SHA (`2b8f4d6`) and that the base files are unchanged at the head.

## Close-out

Not applicable yet. A reviewer does not adjudicate its own findings, and the author has not responded.

**ADJUDICATION:** pending for all 6 findings. P1 findings cannot be deferred.

**VERIFIED AFTER FIXES:** nothing yet. The head has not moved as far as I can tell.

**MERGE RECOMMENDATION:** Do not merge yet. Step 8 is not satisfied:
- The High tier's second round has not run.
- Two P1 findings are unresolved because the tool implementations are not shown.
- Check status is unknown.
- No written decisions exist.

The config text itself is clean. Once the full server files and loader are supplied and the second round runs, this is likely a "merge after fixes" outcome.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "unverified",
      "location": "agent/mcp.json:25-29; base/servers/files.js",
      "scenario": "search_docs (phrase, context_lines) is advertised, but the shown files.js implements no search tool or context_lines handling and the PR changes no server file; the tool may be missing or fail.",
      "fix": "Show or add the search implementation, and add a test that calls search_docs with context_lines and checks the output."
    },
    {
      "severity": "P1",
      "evidence_level": "unverified",
      "location": "agent/mcp.json:7-17; base/servers/notes.js",
      "scenario": "notes_search and notes_read are not defined in the shown notes.js, and the exported readOnly flag is never used, so read-only is unenforced in visible code.",
      "fix": "Provide the notes tool implementation and test that no write path exists under --read-only."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified",
      "location": "agent/mcp.json:23-24",
      "scenario": "Relative ./docs root and servers/ path depend on launch cwd, and no root confinement is visible, so a different cwd, a ../ query or a symlink could expose files outside docs.",
      "fix": "Resolve the root relative to the config, fail closed if it is missing, and enforce path confinement with tests for traversal and symlinks."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified",
      "location": "agent/mcp.json:27-29",
      "scenario": "The 0-5 bound on context_lines is stated only in the description; out-of-range or non-integer values depend on unseen server validation.",
      "fix": "Add minimum and maximum to the argument schema and clamp or reject server-side, with tests."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified",
      "location": "agent/mcp.json:4-18",
      "scenario": "If the loader does not treat the tools arrays as an allowlist, the servers expose whatever tools they implement, so the read-only guarantee rests only on server flags.",
      "fix": "Confirm the loader's schema and test that the model sees exactly the three listed tools."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed",
      "location": "PR #91 (no test files)",
      "scenario": "The PR adds no tests, so read-only, root and bounds claims are unverified assertions.",
      "fix": "Add a config test covering the findings above."
    }
  ]
}
```