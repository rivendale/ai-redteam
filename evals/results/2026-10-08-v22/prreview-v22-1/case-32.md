**Review report**

REVIEWED: PR #91, head `2b8f4d6`, merge base `8e30c1a`. I reviewed only the supplied materials: `PR.md`, `change.patch` and `base/`. I had no checkout or worktree and could run nothing. Any commits after `2b8f4d6` are not reviewed.

TIER: **High.** The change is configuration, but it decides which tools every developer's assistant gets and whether those tools can write. That makes it permissions configuration. It also exposes the user's personal notes to the model. A High-tier review needs two rounds, ideally from two vendors. **This report is round 1 only.** Until round 2 runs, the PR is not reviewed.

DATA (Step 3): The diff holds no personal data, only config and tool descriptions. The reviewed material came to this session from the owner. Whether this endpoint is approved for round 1 is the owner's decision, and this report doesn't settle it. Round 2 should go to an endpoint the owner has approved.

REVIEWERS: Round 1 was a separate instance (Claude, `claude-opus-5-5`) with no part in writing the change. I couldn't read the author from the commit trailers because no commit metadata was supplied, so the author is unknown.

**Checked against the request.** The request was a read-only notes server (search, read) plus a read-only docs search.
- The config declares exactly `notes_search` and `notes_read` for notes, and `search_docs` for docs. Both servers get `--read-only`. Nothing extra is declared.
- I read the three tool descriptions (`agent/mcp.json:9,14,25`). Each describes only what its tool does, with no directives aimed at the model. The PR's claim about descriptions holds.
- `base/servers/files.js:4` computes `writable = --allow-write && !--read-only`, so the docs server is not writable with this config. Verified from the code shown.

**What I could not verify, and why it matters.** "Read-only" here rests on two things, and neither is in the material:
1. Which tools the servers actually advertise. `notes.js` only parses the `--read-only` flag. Its tool handlers aren't shown, so I can't tell whether write or delete tools are withheld when the flag is set. `files.js` "serves text files under --root". I can't tell whether it serves only `search_docs`, or also a read-by-path tool that would bypass the search-only scope.
2. Whether the client honours the `"tools"` list in `mcp.json`. If the assistant exposes every tool a server advertises, the allowlist and descriptions in this file are decoration. Any write tool in `notes.js` would then reach the model.

I can't write these up as findings because I can't point to a defective line. They are the central claim of the PR, though, and they stay unverified until the files below are read.

FINDINGS:

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P3 | `agent/mcp.json:25-26`; enforcement not visible in `base/servers/files.js` | The 0–5 limit on `context_lines` exists only in prose. The schema is a bare `"integer"`, and the shown server code has no clamp. Suppose the model passes `context_lines: 100000`, perhaps nudged by text inside a doc it already searched, or passes `-3`. Each match then returns whole files or behaves undefined, flooding the assistant's context. Access stays read-only and inside `./docs`, hence P3. | Call `search_docs` with `context_lines` values of 100000, -1 and 2.5. Expect a rejection or a clamp to the range 0–5. Also assert the schema declares `minimum: 0, maximum: 5` if the client supports it. |
| 2 | P3 | `agent/mcp.json:5,21`; `base/servers/files.js:3` | `servers/notes.js`, `servers/files.js` and `./docs` resolve against the assistant's working directory, not the repo or config location. A developer who starts the assistant from a subdirectory such as `agent/` or `docs/` gets servers that fail to start. A cwd with its own `docs/` would point the search at the wrong folder. | Launch the config with cwd set to `agent/`. Expect both servers to start, with `search_docs` rooted at `<repo>/docs`. This fails today. |

FILES NEEDED BUT NOT PROVIDED:
- The tool implementations in `servers/notes.js` and `servers/files.js`: the full tool list each server advertises, with and without `--read-only`, and the `search_docs` handler including its `context_lines` handling. The base copies only show argument parsing.
- The assistant client's config loader, to show whether the `"tools"` array in `mcp.json` limits what the model sees and whether the descriptions there replace the server-provided ones.
- The full `base/` tree. No `docs/` directory appears in it, and the patch doesn't add one. If the folder really doesn't exist, `search_docs` has nothing to search.
- The commit trailers for `2b8f4d6`, to identify the author.
- CI checks for this PR.

**Close-out**

The author has not adjudicated these findings yet, and a reviewer may not adjudicate its own.

ADJUDICATION: pending (#1 and #2 need an author decision).

VERIFIED AFTER FIXES: none yet.

MERGE RECOMMENDATION: **do not merge (yet).**
- The High-tier second round has not run.
- The read-only guarantee is unverified until the server tool lists and the client's handling of `"tools"` are reviewed.
- No CI check results were supplied, and a missing check is not green.

The two P3 findings would not block on their own.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "inferred (enforcement code not provided)",
      "location": "agent/mcp.json:25-26; base/servers/files.js",
      "scenario": "context_lines limit of 0-5 is stated only in the description; the schema is an unbounded integer and the shown server code has no clamp. A value such as 100000 or -1 returns whole files or behaves undefined, flooding the assistant's context.",
      "fix": "Declare minimum 0 and maximum 5 in the schema and clamp or reject out-of-range values in the search_docs handler, with a test for 100000, -1 and a non-integer."
    },
    {
      "severity": "P3",
      "evidence_level": "verified from config and files.js:3",
      "location": "agent/mcp.json:5,21; base/servers/files.js:3",
      "scenario": "Server script paths and --root ./docs resolve against the assistant's working directory. Starting the assistant from a subdirectory makes both servers fail to start, or points docs search at the wrong folder.",
      "fix": "Resolve script paths and --root relative to the repo or config location (or document and enforce a required cwd), with a test that launches from agent/."
    }
  ]
}
```