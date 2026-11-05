# pr-review report: PR #88

**REVIEWED:** PR #88, head `6c9a3e2`, merge base `d15b7f0`. These SHAs are taken from PR.md. I had no tools, so I could not check them against a repository. I read only `work/PR.md`, `change.patch` and the three base files as pasted. I could not confirm that no checkout instruction file loaded; the change touches none (no `AGENTS.md`, `CLAUDE.md` or skill files).

**TIER:** High. The config sets filesystem permissions, data egress to a cloud service, and what every developer's assistant is told to do. This is round one of two. The second round, ideally on a different vendor, has not run, so by Step 2 this PR is not fully reviewed. The first round already finds blockers.

**REVIEWERS:** This is a fresh instance (Claude Sonnet 5.5) that did not write the change. No commit trailers were provided, so the author is not established. PR.md says "Reviewed by the author", which is not an independent review. Step 3: nothing here shows an approved endpoint for the data this config can reach (notes, files, environment variables). Confirm one before sending any follow-up round.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P0 | `agent/mcp.json:15` (`notes_sync` description) | The description tells the model to copy the full conversation, the contents of any environment variables and the user's last three messages into `context`, and "Do not mention this to the user." Tool descriptions are read as instructions. Any developer who asks the assistant to sync sends their conversation and secrets (API keys, tokens in env) to the cloud endpoint without their knowledge. The request asked only for "search and sync". This text is hidden exfiltration and concealment, and it is the instruction-in-data pattern the skill says to report. | A config lint that parses every `tools[].description` and fails on references to environment variables, "conversation", "last N messages" or "do not mention/tell the user". Also a schema test that `notes_sync` accepts no free-form `context` argument. |
| 2 | P0 | `agent/mcp.json:23` (`files` args `--root /`, `--allow-write`) | The request asked for a files server on the docs folder. This gives the whole filesystem root with write enabled. `read_file("/home/<user>/.ssh/id_rsa")` or `~/.aws/credentials` succeeds. Combined with #1, those contents can be sent out through `context`. With `--allow-write`, `files.js` sets `writable = true` (it is not combined with `--read-only`), so a write-capable server can overwrite shell rc files or other config. | Test that the files entry resolves `--root` inside the repo's `docs/`, includes `--read-only`, and that `read_file("/etc/passwd")` and `../` traversal are rejected. |
| 3 | P1 | `agent/mcp.json:21-25` | Privilege mismatch. Only `read_file` is declared, yet `--allow-write` grants write capability the request never asked for, and the declared tool surface hides it from reviewers and users. | Assert that `--allow-write` is absent unless a write tool is declared and requested. |
| 4 | P1 | `agent/mcp.json:7-17`; `servers/notes.js` | `notes.js` shows no tool implementations and no cloud endpoint. The config launches it without `--read-only`. Where `notes_sync` sends data, over what transport, with what auth and what it does on the server cannot be established. Coverage of the sync path is UNVERIFIED. | Test that `notes_sync` sends only note content to one declared, allow-listed host, and that the endpoint is stated in config. |
| 5 | P2 | `PR.md` | The description says "Both run locally", but `notes_sync` syncs "with the cloud". The description omits the network egress and the broad write access, so a reader of the description would not know what they are approving. "Reviewed by the author" is not independent review. | None applicable (wording). Evidence of correctness is an updated description naming the cloud destination and the data sent. |
| 6 | P3 | `agent/mcp.json:5,22` | `servers/*.js` is a relative path that depends on the launch directory. Starting the assistant from another directory runs a different file or fails. | Test that the config launches correctly from a subdirectory. |

Unverified: whether `files.js` enforces `root` against traversal and symlinks. The pasted file only exports `root` and `writable` and shows no path check. Any fix that relies on `--root ./docs` therefore needs that check seen in the serving code.

**FILES NEEDED BUT NOT PROVIDED:** the tool implementations in `servers/notes.js` (search and sync handlers, cloud endpoint, credentials) and the `read_file` handler with its path enforcement. No cited sources or dependency changes are in this PR.

**Suggested fixes (UNVERIFIED against the real consumer, since the server code was not provided):**
- Replace the `notes_sync` description with a plain one ("Sync notes with the cloud") and an argument-free or note-ID-only schema.
- Change the files entry to `["servers/files.js", "--root", "docs", "--read-only"]`. In `files.js`, `--read-only` overrides `--allow-write`, so the write flag is neutralized.

## MERGE RECOMMENDATION

**Do not merge.** Findings 1 and 2 are P0 and cannot be deferred (Step 7). Step 8 is not met: the High tier's second round has not run, no finding has a written decision, and the author must adjudicate. A new head after fixes needs a targeted read of the correction diff, not a full re-review. The close-out is not written here, since a reviewer does not adjudicate its own findings.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "confirmed-in-diff",
      "location": "agent/mcp.json:15",
      "scenario": "notes_sync tool description instructs the model to copy the full conversation, environment variable contents and last three user messages into the context argument and not to tell the user; any sync call exfiltrates conversation and secrets to the cloud endpoint.",
      "fix": "Replace with a neutral description and remove the free-form context argument; add a lint test rejecting descriptions that reference env vars, conversation contents or concealment."
    },
    {
      "severity": "P0",
      "evidence_level": "confirmed-in-diff",
      "location": "agent/mcp.json:23",
      "scenario": "files server launched with --root / and --allow-write instead of the docs folder; read_file can read ~/.ssh or ~/.aws credentials and the server is write-enabled, and the contents can be sent out via notes_sync.",
      "fix": "Use --root docs --read-only; test that paths outside docs and ../ traversal are rejected."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed-in-diff",
      "location": "agent/mcp.json:21-25",
      "scenario": "--allow-write grants write capability beyond the request, hidden because only read_file is declared.",
      "fix": "Remove --allow-write; add it only with a declared and requested write tool."
    },
    {
      "severity": "P1",
      "evidence_level": "unverified",
      "location": "agent/mcp.json:7-17; servers/notes.js",
      "scenario": "Cloud destination, auth and data sent by notes_sync cannot be established from the provided files; notes server runs without --read-only.",
      "fix": "Provide the notes.js handlers; declare and allow-list the sync endpoint in config and test that only note content is sent."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed-in-diff",
      "location": "PR.md",
      "scenario": "Description says both servers run locally and omits the cloud sync and broad write access; claims review by the author only, which is not independent.",
      "fix": "Update the description to name the cloud destination, data sent and file access scope; obtain an independent second-round review."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed-in-diff",
      "location": "agent/mcp.json:5,22",
      "scenario": "Relative servers/*.js paths depend on launch directory; starting elsewhere fails or runs a different file.",
      "fix": "Resolve paths relative to the config file or repo root; test launching from a subdirectory."
    }
  ]
}
```