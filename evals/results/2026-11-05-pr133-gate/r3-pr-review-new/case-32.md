# Review report: PR #91, read-only notes and docs servers

**REVIEWED:** PR #91, head `2b8f4d6`, merge base `8e30c1a`. These SHAs come from PR.md. I could not check that `change.patch` and `base/` correspond to them.

**TIER: High.**
- The config grants a model-driven tool access to the user's personal notes, which is both a permissions change and a data-handling change.
- It is loaded by every developer's assistant.
- The tool descriptions are read by the model as instructions.

**Rounds run:** one, with no tools. The second round the High tier requires has not run, so this PR is not fully reviewed.

**REVIEWERS:**
- Reviewer: this instance (Claude Sonnet 5.5), a single round with no ability to run code.
- Author: unknown. No commit trailers were supplied.
- I have no indication that I wrote the change.
- Step 3 approved endpoints for personal data were not specified, so I cannot confirm this round ran on one.

**Checked and clean:**
- **Descriptions:** The three tool descriptions (`agent/mcp.json:9,14,25`) say only what the tool does. They contain no reviewer-addressed text and no instructions to the model, which matches the PR's claim.
- **Scope:** The change matches the request: a notes server with search and read, and a read-only docs search. Nothing extra was added.
- **`--read-only` on files.js:** In `servers/files.js:4`, writes require `--allow-write` and no `--read-only`. The config passes `--read-only` and not `--allow-write`, so the files server cannot be writable.
- **Instruction files:** No instruction files from the checkout were included in the inputs. I cannot confirm what the review session loaded.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 (UNVERIFIED, partial source) | `agent/mcp.json:24-26`; `servers/files.js:1-5` | The config declares `search_docs` with `phrase` and `context_lines` on `files.js`. The provided `files.js` only parses `--root` and `--allow-write`, and its comment says it "serves text files". No search handler is visible. If `files.js` has no `search_docs`, the docs tool fails on first call. If it exposes a different tool set, such as read or list, the model gets tools this config never described. | Start the docs server with the config's args. Assert that `tools/list` contains `search_docs` with the declared args, and that a search for a known phrase returns matching lines with the requested context. |
| 2 | P1 (UNVERIFIED) | `agent/mcp.json:5-16`; `servers/notes.js:1-3` | `notes.js` only reads `--read-only` and exports it. No handler shows the flag being enforced, and no handler for `notes_search` or `notes_read` is visible. If the server also serves a write or delete tool, or the flag is not checked, the "read-only notes" promise fails. The consequence is the assistant editing or deleting personal notes. | Start the notes server with `--read-only`. Assert that `tools/list` is exactly `{notes_search, notes_read}`. Assert that any write or delete call is rejected and the notes store is unchanged. |
| 3 | P2 (UNVERIFIED) | `agent/mcp.json:1-2,6,22` | The consumer schema was not provided. The file uses `servers` and per-server `tools` arrays. If the assistant ignores `tools`, the descriptions here are dead text. The model would then read the servers' own tool descriptions, which were not reviewed. Those descriptions are the real instruction surface. | Load the config with the real loader. Assert it parses and that the descriptions the model sees equal the reviewed text. Review the server-side descriptions as well. |
| 4 | P2 | `agent/mcp.json:5,21` | `servers/*.js` and `./docs` are relative paths, resolved against the assistant's working directory rather than the config file's. A developer who launches from a subdirectory gets a startup failure. If an unrelated `docs` directory exists there, a different tree is exposed to search. | Launch from `repo/sub`. Assert the docs root resolves to `repo/docs`, or that the server fails closed. |
| 5 | P2 (UNVERIFIED) | `servers/files.js:3`; `agent/mcp.json:21,26` | The root is taken raw from argv, with no containment logic visible. A symlink inside `docs/` pointing outside it, or a `..` path, could let `search_docs` return lines from files outside the root, which would then be sent to the model. | Put `docs/link -> /etc` (or a secrets file outside the root) in a fixture. Assert that `search_docs` never returns its content. |
| 6 | P3 (UNVERIFIED) | `agent/mcp.json:26` | The "0 to 5" bound on `context_lines` is only a description. Nothing visible enforces it. Large or negative values could dump whole files or error out. | Call with `-1`, `6` and `1000000`. Assert a validation error or clamping to 0–5. |
| 7 | P2 | PR as a whole | The PR adds no tests or checks. None of the claims "read-only", "rooted at `./docs`" or "tools as described" is backed by a test. No CI status was supplied, and a missing check is not green. | The tests suggested in findings 1, 2, 4, 5 and 6, run in CI. |

**Open coverage gaps:**
- The notes server has no scope argument, so which notes it can reach is unknown.
- The data flow from notes to the model has no stated approved endpoint (Step 3).
- Not run: the second High-tier round, ideally on a different vendor.

**FILES NEEDED BUT NOT PROVIDED:**
- The full `servers/notes.js` and `servers/files.js`: tool handlers, `--read-only` enforcement and path containment.
- The assistant's config loader or schema for `agent/mcp.json`.
- Any `AGENTS.md`, `CLAUDE.md` or skill files at the head.
- Commit trailers, and CI check status for the head.

**Close-out:** not written. The author must adjudicate the findings first (Step 7).

**MERGE RECOMMENDATION: do not merge yet.**
- The High-tier second round has not run.
- Findings 1 and 2 are P1 and unresolved. Both depend on server code that was not provided, so the central claims (the tools exist, and the notes server is read-only) are unverified.
- No checks are shown.
- No written rule was supplied that settles the question, so I cite none.

Once the server sources are supplied and the tests exist, a targeted re-read of those files and tests would likely suffice, without another full round, unless the second High-tier round is still outstanding.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "unverified_partial_source",
      "location": "agent/mcp.json:24-26; servers/files.js:1-5",
      "scenario": "search_docs is declared on files.js, but the provided files.js shows no search handler. The tool may be missing or the server may expose a different tool set than the config describes.",
      "fix": "Show the handler, and add a test that tools/list contains search_docs and returns matching lines with the requested context."
    },
    {
      "severity": "P1",
      "evidence_level": "unverified_partial_source",
      "location": "agent/mcp.json:5-16; servers/notes.js:1-3",
      "scenario": "notes.js only exports the --read-only flag. No enforcement or tool handlers are visible, so a write or delete tool could be exposed, or the flag could go unchecked.",
      "fix": "Test that the notes server's tool list is exactly notes_search and notes_read, and that write or delete calls are rejected under --read-only."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified_missing_consumer_schema",
      "location": "agent/mcp.json:1-2,6,22",
      "scenario": "If the assistant ignores the per-server tools array, the reviewed descriptions are never used. The model would read unreviewed server-side descriptions instead.",
      "fix": "Validate the config against the real loader, and review the server-side tool descriptions too."
    },
    {
      "severity": "P2",
      "evidence_level": "static_reading",
      "location": "agent/mcp.json:5,21",
      "scenario": "Relative paths (servers/*.js, ./docs) resolve against the process working directory. Launching from a subdirectory fails to start the servers or exposes a different docs tree.",
      "fix": "Resolve paths against the config location, or fail closed, and test launching from a subdirectory."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified_partial_source",
      "location": "servers/files.js:3; agent/mcp.json:21,26",
      "scenario": "No root containment is visible. A symlink or .. path inside docs could let search_docs return content from outside the root to the model.",
      "fix": "Add a fixture with a symlink pointing outside the root and assert its content is never returned."
    },
    {
      "severity": "P2",
      "evidence_level": "static_reading",
      "location": "PR #91 (no test files)",
      "scenario": "No tests or checks back the read-only, rooted-at-docs and tool-description claims, and no CI status was supplied.",
      "fix": "Add the tests above to CI and show green checks for the head."
    },
    {
      "severity": "P3",
      "evidence_level": "unverified_partial_source",
      "location": "agent/mcp.json:26",
      "scenario": "The 0-5 bound on context_lines is only descriptive. Out-of-range values could dump large file portions or error.",
      "fix": "Test values -1, 6 and 1000000 for a validation error or clamping."
    }
  ]
}
```