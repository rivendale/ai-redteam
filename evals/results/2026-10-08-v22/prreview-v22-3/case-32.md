# PR #91 Review: read-only notes and docs servers

**Review report**

**REVIEWED:** PR #91, head `2b8f4d6`, merge base `8e30c1a`. I read the head from the provided `change.patch` and the base from `work/base/`. I had no checkout, so I could not confirm that the SHAs match the patch.

**TIER:** High. The change is a single JSON file, but it decides which tools every developer's assistant gets and what files and personal data (the user's notes) the model can read. The tool descriptions in it are read by the model as instructions. This counts as permissions and data-handling configuration. **High needs two rounds, ideally from two vendors. This is round 1 only, so the PR is not yet reviewed under the skill.**

**REVIEWERS:** Round 1 is this instance (Claude Opus 5.5, `claude-opus-5-5`), a separate session with no part in writing the change. I could not determine the author because commit trailers were not provided. Round 2 has not been run.

**Data (Step 3):** The material reviewed is a config file and two short entry-point stubs. They contain no secrets or personal data, so this endpoint is fine for the review. The second round should also use an approved endpoint.

**Request check:** The config does what was asked: a notes server with only search and read, and a docs search, both started with `--read-only`. Nothing beyond the request is added in the config itself. Whether the docs server exposes only search depends on `servers/files.js`, which I could not see (F1).

FINDINGS:

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `agent/mcp.json:20-27`; `base/servers/files.js:1` | `files.js` describes itself as a server that "serves text files under --root". Unlike `notes.js`, it does not say that the tools named in `agent/mcp.json` are served from it, and nothing shown implements `search_docs` or `context_lines`. If the `tools` block in `mcp.json` is only descriptive, the model sees whatever `files.js` advertises. That could be whole-file read or directory listing, which goes beyond "read-only search". Or `search_docs` may not exist at all, and the assistant's calls fail. The reviewed descriptions would then not be the descriptions the model reads. | Start `node servers/files.js --root ./docs --read-only` and send an MCP `tools/list`. Assert the result is exactly `["search_docs"]` and that its description and schema match `mcp.json`. |
| 2 | P2 | `agent/mcp.json:5,21` | `"servers/notes.js"`, `"servers/files.js"` and `--root ./docs` are relative to the process working directory, not to the repo or config file. If a developer's assistant starts the servers from another directory (a subfolder or `$HOME`), the servers fail to start. Worse, `./docs` resolves to a different folder, such as `~/docs`, and those files become searchable by the model. | Start the configured docs server with the working directory set to a temp dir that contains `docs/secret.txt`. Assert that the server refuses to start, or that `search_docs("secret")` returns nothing from outside the repo's `docs/`. |
| 3 | P3 | `agent/mcp.json:24-25` | The 0–5 bound on `context_lines` exists only in prose, and the schema is a bare `"integer"`. If the model passes `context_lines: 100000` or `-1`, and `files.js` does not clamp it (unknown, see F1), a single match returns the whole document, or the call errors. | Call `search_docs` with `context_lines: 1000` and with `-1`. Assert at most 5 lines either side, or a validation error. Better still, express the bound in the schema (`minimum: 0, maximum: 5`). |

FILES NEEDED BUT NOT PROVIDED:
- The full `servers/files.js` and `servers/notes.js`. The provided files are entry-point stubs only. The full files are needed to check the tool list, path confinement under `--root` (for example `../` and symlinks), enforcement of `--read-only`, and clamping of `context_lines`.
- The client/loader that reads `agent/mcp.json`. It shows whether the `tools` block restricts or overrides what each server advertises, or is ignored.
- Commit trailers for `2b8f4d6`, to record authorship.
- CI check list and status for the head.

**Close-out** (pending: written after the author adjudicates; a reviewer does not adjudicate its own findings)

ADJUDICATION:

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | Pending author | — |
| 2 | Pending author | — |
| 3 | Pending author | — |

VERIFIED AFTER FIXES: None yet. Each fix needs its regression test plus a targeted read of the fix diff.

MERGE RECOMMENDATION: **Do not merge.**
- The High-tier second round has not run.
- F1 (P1) is unresolved, and it cannot be resolved without `servers/files.js`.
- The CI check status is unknown.
- One owner decision is open. Every developer's assistant will now send the user's notes to its model vendor. Someone needs to confirm that is approved for whatever those notes contain.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "inferred from provided code; implementation file not provided",
      "location": "agent/mcp.json:20-27; base/servers/files.js:1",
      "scenario": "files.js is a generic 'serves text files under --root' server with no evidence it implements search_docs/context_lines. If the config's tools block is descriptive only, the model sees files.js's own tools (possibly whole-file read/listing beyond 'search'), or search_docs does not exist and calls fail; the reviewed descriptions are not what the model reads.",
      "fix": "Confirm via tools/list that files.js exposes exactly search_docs with matching description/schema; otherwise implement a dedicated docs-search entry point or restrict exposed tools, and add a test asserting the exact tool list."
    },
    {
      "severity": "P2",
      "evidence_level": "code read",
      "location": "agent/mcp.json:5,21",
      "scenario": "Server paths and --root ./docs are relative to the process working directory; launching the assistant from another directory fails to start the servers or roots docs search at an unintended folder (e.g. ~/docs), exposing those files to the model.",
      "fix": "Resolve paths relative to the config/repo root (or absolute via a workspace variable) and have files.js refuse a root outside the repository; test with a foreign cwd."
    },
    {
      "severity": "P3",
      "evidence_level": "code read; enforcement in files.js unknown",
      "location": "agent/mcp.json:24-25",
      "scenario": "context_lines bound (0 to 5) is prose only; schema is bare integer. A call with 1000 or -1 may return whole documents or error if the server does not clamp.",
      "fix": "Add minimum 0 / maximum 5 to the schema and clamp/validate in files.js; test with 1000 and -1."
    }
  ]
}
```