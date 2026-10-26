# PR #91 Review: read-only notes and docs servers

**Review report**

**REVIEWED:** PR #91, head `2b8f4d6`, merge base `8e30c1a`.
- Both SHAs are short forms copied from `PR.md`. I could not check them against a repository or review in a worktree, because this session has no tools.
- The review covers only the material provided: `change.patch`, `base/README.md`, `base/servers/files.js` and `base/servers/notes.js`.
- Nothing was run.

**TIER:** High.
- The change sets what tools and file access the assistant gets on every developer's machine. That is permissions configuration.
- Tool descriptions in it are read by the model as instructions.
- High tier requires two review rounds. **This is round 1 of 2. The PR is not reviewed until a second round has run**, ideally on a different vendor.

**REVIEWERS:**
- Reviewer: one Claude instance (Opus 5.5, `claude-opus-5-5`), round 1. This instance did not write the change.
- Author: unknown. Commit trailers were not provided.

**Data (Step 3):** The patch contains config only. It holds no notes content or credentials, so reviewing it here is within bounds. The servers will serve the user's notes, which is personal data. Any round that is shown real notes content needs an approved endpoint.

**Supply-chain and runtime lenses:**
- No dependency, lockfile, runtime, base-image or TLS changes. Neither lens applies.
- No OSV lookup is required.

### What was verified

- **Docs server stays read-only.** `servers/files.js:4` computes `writable = args.includes("--allow-write") && !args.includes("--read-only")`. The config passes `--read-only` and never passes `--allow-write` (`agent/mcp.json:21`), so the files server's write flag is false.
- **Docs root is parsed correctly.** `--root` is present, so `args.indexOf("--root") + 1` resolves to `./docs`. The `-1` fallback to `args[0]` is not triggered.
- **Notes server receives the flag.** `--read-only` is passed (`agent/mcp.json:5`), and `notes.js:2` reads it.
- **Tool descriptions are clean.** All three (`agent/mcp.json:9,14,25`) describe only the tool's behaviour. They contain no hidden or reviewer- or model-directed instructions.
- **No injection in the PR.** The PR text contains no reviewer-directed instructions.
- **Scope matches the request.** The change gives notes search and read plus docs search, all read-only, and nothing extra.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P3 | `agent/mcp.json:26` | The 0–5 range for `context_lines` is stated only in the description (line 25). The declared type is a bare `"integer"`. If the model sends `context_lines: 500` or `-1`, the only guard is whatever `files.js` does, and its search code was not provided. An unclamped server returns large spans of docs into context, or errors on a negative value. Impact is bounded: the data is read-only and stays within docs. | Call `search_docs` with `context_lines` set to 6, 500 and -1. Assert each is clamped to the 0–5 range or rejected with an error. This fails today if the server does not clamp. |

### Coverage gaps

These are not findings, but they block a High-tier sign-off.

1. **Read-only enforcement is unseen for notes.** `notes.js` only *computes* `readOnly`. Whether any write, update or delete tool checks it is not in the provided code.
2. **The `tools` lists may not be an allowlist.** I cannot tell whether the loader filters to the tools in `agent/mcp.json`, or whether the servers advertise their own full tool sets.
   - If the servers advertise their own sets, the assistant gets every tool `files.js` and `notes.js` expose. That could include a path-based read or a write tool.
   - In that case, the "read-only" guarantee rests entirely on code not provided.
3. **Path containment in `files.js` is unseen.** I cannot see `..` or symlink handling under `--root`, or how a relative `./docs` resolves against the launch directory.
4. **The loader's config schema is unseen.** I cannot confirm that the `servers` key and the `tools` field are what the assistant's loader reads, as opposed to a file that is silently ignored.

**FILES NEEDED BUT NOT PROVIDED:**
- Full `servers/files.js`, including search, read and path-containment logic and the tool registration list.
- Full `servers/notes.js`, including the tool registration list and any write paths.
- The assistant's config loader or schema for `agent/mcp.json`.
- The commit log with trailers for `8e30c1a..2b8f4d6`.
- CI check results for the head.

**Close-out**

**ADJUDICATION:** Pending. The author adjudicates, not this reviewer.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | — | — |

**VERIFIED AFTER FIXES:** None. No fixes have been made.

**MERGE RECOMMENDATION: do not merge (yet).**
- The High-tier second round has not run.
- The read-only guarantee depends on server code that was not provided (gaps 1–3).
- Finding 1 has no written decision.
- No CI checks were provided, and a missing check is not green.

The config itself looks correct and minimal. Once the server sources are reviewed, round 2 is clean, and finding 1 is adjudicated, this is likely a merge.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "config confirmed; server-side clamping unverified (files.js search code not provided)",
      "location": "agent/mcp.json:26",
      "scenario": "context_lines range 0-5 is stated only in the model-facing description; the declared type is an unbounded integer. A call with context_lines=500 or -1 relies on files.js to clamp; if it does not, large spans of docs enter context or the call errors. Read-only and within docs, so impact is bounded.",
      "fix": "Enforce the 0-5 clamp/rejection in servers/files.js, and declare min/max in the tool schema if the loader supports it; add a test for 6, 500 and -1."
    }
  ]
}
```