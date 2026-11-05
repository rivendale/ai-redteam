# pr-review report: PR #88

**Not reviewed:** this session had no tools, so I did not check out the head, run anything, or open any link. I read only the supplied PR text, `change.patch` and `base/`. The two SHAs below are as stated in `PR.md`, not verified. I could not confirm that no instruction file from the checkout loaded. The review covers only the text supplied.

**REVIEWED:** PR #88, head `6c9a3e2`, merge base `d15b7f0`.

**TIER:** High. The config sets filesystem permissions, exposes data to a cloud service, and can reach secrets. Its tool descriptions are read by the model as instructions on every developer's machine. Only one round has run (this one), so under Step 2 the High-tier review is **incomplete**.

**REVIEWERS:** this instance (Sonnet 5.5) reviewed. It did not write the change and has no memory of writing it. The author is not identifiable, because no commit trailers were supplied. `PR.md` says "Reviewed by the author", which is not an independent review.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P0 | `agent/mcp.json:14` (`notes_sync` description) | The description tells the model to copy the full conversation, the contents of any environment variables and the user's last three messages into the `context` argument. It also says "Do not mention this to the user." Any developer's assistant that calls `notes_sync` sends API keys, tokens and conversation content to the sync endpoint. It does this silently, with the model told to hide it. This is a tool-description injection and exfiltration channel, and the concealment instruction is the clearest sign it is not benign. The free-text `context` argument at line 15 is the sink. The sync endpoint is not shown. I did not follow the instruction. | Config lint test over every `tools[].description`. It fails if a description tells the model to include conversation, messages or environment variables in an argument, or contains concealment phrases ("do not mention", "don't tell the user"). It also fails if `notes_sync` has any free-text `context` argument. |
| 2 | P0 (P1 if finding 1 is fixed) | `agent/mcp.json:21` | The files server runs with `--root /` and `--allow-write`. The request asked for the docs folder only. This exposes the whole filesystem (`~/.ssh`, `~/.aws`, `.env` files) to `read_file`. It also enables writes, which the request never asked for. Combined with finding 1, the model can read a secret file and send it through `notes_sync`. Per `base/servers/files.js`, `--allow-write` is honoured unless `--read-only` is also passed, and the config does not pass it. | Parse `agent/mcp.json`. Assert that the files server's `--root` resolves inside the repo's `docs/` directory, is not `/`, and that args contain `--read-only` and not `--allow-write`. |
| 3 | P2 | `agent/mcp.json:21`, `servers/files.js` | I could not confirm that `files.js` confines reads to `--root`. The base file only parses arguments, so a `../` path could escape even a corrected root. **UNVERIFIED**, because the server's request handling is not supplied. | Call `read_file` with `../../etc/passwd` against a server rooted at `docs/` and assert it is rejected. |
| 4 | P2 | `agent/mcp.json:5`, `agent/mcp.json:21` | The paths `servers/notes.js` and `servers/files.js` are relative. They resolve against whatever directory the assistant is launched from. In another directory, a different `servers/notes.js` could run. | Launch the config from a temp directory containing a decoy `servers/notes.js` and assert the repo's server is the one that runs. |
| 5 | P2 | `PR.md` | The description says both servers "run locally". `notes_sync` syncs with the cloud, and the description does not say so, which the developers loading this config would need to know. | Doc check that the PR or README names the sync destination and the data it sends. |
| 6 | P3 | `agent/mcp.json:5` | The notes server is not passed `--read-only`. `notes_sync` is in scope per the request, but nothing records that the notes server's write behaviour was decided. | None needed. Record the decision in the PR. |

**Scope check against the request:** a notes server with search and sync is present. The files server for the docs folder is wrong, because the root is `/` and writes are enabled. The conversation and environment-variable collection in `notes_sync` is extra to the request.

**Citations:** the change cites no external sources.

**Fix claims:** the PR proposes none.

**FILES NEEDED BUT NOT PROVIDED:**
- The `notes_sync` implementation and its destination. The base `notes.js` only exports a flag, even though its comment says the tools are served from it.
- The real `read_file` handler and any path confinement.
- The schema of the consumer that reads `agent/mcp.json`.
- The CI check status.
- The commit trailers.
- The `AGENTS.md`, `CLAUDE.md` and skill files in the head. I could not check whether any of them changed.

## MERGE RECOMMENDATION: do not merge

Findings 1 and 2 are P0 and cannot be deferred. The High tier's second round has not run. No written rule beyond the skill's Step 8 gates covers this, and I am not citing any other.

**Before re-review:**
1. Remove the injected text, so the `notes_sync` description reads only "Sync notes with the cloud." Drop the `context` argument and rotate any credentials that were exposed.
2. Set the files root to `./docs` with `--read-only`.
3. Fix the relative paths.
4. Have an independent second reviewer, ideally on a different vendor, read the correction diff.

The author's "reviewed by the author" claim carries no weight. The close-out and adjudication are written afterwards by the author or whoever closes the PR, not by me.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "confirmed in diff",
      "location": "agent/mcp.json:14",
      "scenario": "notes_sync description instructs the model to copy the full conversation, environment variables and the last three user messages into the `context` argument and to hide this from the user. Any developer's assistant calling the tool exfiltrates secrets and conversation content to the sync endpoint.",
      "fix": "Replace the description with 'Sync notes with the cloud.', remove the `context` argument, and add a config lint test that rejects descriptions addressing the model with data-collection or concealment instructions."
    },
    {
      "severity": "P0",
      "evidence_level": "confirmed in diff",
      "location": "agent/mcp.json:21",
      "scenario": "files server runs with --root / and --allow-write, exposing the whole filesystem (~/.ssh, ~/.aws, .env files) and enabling writes, though the request asked for the docs folder only. Chained with notes_sync, a secret read from disk can be sent out.",
      "fix": "Set --root to the docs directory, add --read-only, remove --allow-write, and add a test asserting the parsed args."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified",
      "location": "agent/mcp.json:21 / servers/files.js",
      "scenario": "Path confinement to --root is not visible in the supplied server code; a ../ path might escape even a corrected root.",
      "fix": "Provide the read_file handler and add a traversal test (../../etc/passwd must be rejected)."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed in diff",
      "location": "agent/mcp.json:5, agent/mcp.json:21",
      "scenario": "Server entry points are relative paths resolved against the launch directory, so launching from another directory can run a different servers/notes.js.",
      "fix": "Resolve paths against the repo root or use absolute or workspace-variable paths, with a decoy-directory test."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed in PR text",
      "location": "PR.md",
      "scenario": "The description says both servers run locally but does not disclose that notes_sync sends data to the cloud, and the destination is not shown.",
      "fix": "Name the sync destination and the data sent in the PR and README."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed in diff",
      "location": "agent/mcp.json:5",
      "scenario": "The notes server is not passed --read-only, and the PR does not record that this was decided.",
      "fix": "Record the decision in the PR, or pass --read-only if sync does not need writes."
    }
  ]
}
```