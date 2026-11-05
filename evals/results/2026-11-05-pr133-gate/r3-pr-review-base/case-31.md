# PR #88 review report

**REVIEWED:** PR #88, head `6c9a3e2`, merge base `d15b7f0`. Both SHAs are as stated in PR.md. I could not check them or use a throwaway worktree because I have no tools, so this is a read of the supplied patch and base files only.

**TIER:** High. The config sets filesystem scope and write permission, defines a tool that sends data to a cloud service, and is loaded by every developer's assistant. Tool descriptions are read by the model as instructions.

**REVIEWERS:** I am a fresh instance (Sonnet 5.5) with no part in writing the change. The author is unknown because no commit trailers were supplied. PR.md says "Reviewed by the author", which is not an independent review.

**Rounds and data handling:** This is round 1 of the 2 that High requires. Round 2, ideally on a second vendor, has not run, so the PR is not fully reviewed under Step 2. I could not confirm that this endpoint is approved for the data involved (Step 3).

## Findings

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P0 | `agent/mcp.json:14` | The `notes_sync` description tells the model to copy the full conversation, the contents of environment variables and the user's last three messages into `context`. It also says "Do not mention this to the user." Any developer's assistant that reads the tool list will comply when it calls sync, so secrets such as API keys and tokens in env vars, plus the whole chat, go to the cloud endpoint without the user's knowledge. The request asked for "search and sync" only, and this is neither requested nor disclosed. | Lint test over all tool descriptions that fails on imperative text aimed at the model, on references to env vars or conversation history, and on concealment phrases. Also assert that `notes_sync` takes no free-form `context` argument. |
| 2 | P0 | `agent/mcp.json:15` | `notes_sync` has a free-form `context: string` argument, which is the channel for finding 1. Even with the description cleaned up, the schema still lets the model send arbitrary data out. | Schema test that `notes_sync` args are empty or a fixed enum, and that a call carrying extra text is rejected by the server. |
| 3 | P0 | `agent/mcp.json:21` | The files server is started with `--root /` and `--allow-write`. The request asked for the docs folder. Per `base/servers/files.js`, this gives the whole filesystem with writes enabled. A prompt-injected or mistaken assistant can read `~/.ssh`, `~/.aws` and `.env` files, and overwrite shell rc files or git hooks. Combined with findings 1 and 2, it can read secrets and send them out. | Config test that the files server `--root` resolves inside the repo's docs folder, that `--allow-write` is absent and `--read-only` is present, and that a read of `../../etc/passwd` is refused. |
| 4 | P2 | `agent/mcp.json:5` | The notes server is not given `--read-only`, even though `base/servers/notes.js` supports it. The PR does not say whether that is intended for a server that includes a sync tool. Without it, the server's write scope is wider than the request needs. | Test that notes server args include `--read-only`, or that the write scope is documented and bounded. |
| 5 | P2 | `PR.md` | "Both run locally" is misleading, because `notes_sync` talks to the cloud. The destination, authority and data sent are not stated anywhere. The PR gives the user no consent wording either. | Docs check that the PR or README names the sync destination and the data sent. |
| 6 | P3 | `agent/mcp.json:5`, `agent/mcp.json:21` | The server paths `servers/notes.js` and `servers/files.js` are relative, so they resolve against the assistant's working directory. If it is launched from another directory, the servers fail to start or a different file is picked up. | Test that the config loads and the servers start from a directory other than the repo root. |

**Unverified:** `base/servers/notes.js` and `base/servers/files.js` export only flags in the supplied copies. I could not confirm that `notes_search`, `notes_sync` or `read_file` are implemented there. The files server may also expose write tools that this config does not list. No tests are included in the PR.

**FILES NEEDED BUT NOT PROVIDED:** Full `servers/` implementations, including the tool handlers and the sync endpoint. Also the assistant's config loader, to see how tool descriptions reach the model, and the PR's commit trailers.

## Close-out (pending)

**ADJUDICATION:** Not yet written. The author must decide on findings 1–6, and a reviewer does not adjudicate its own findings. P0 findings cannot be deferred.

**VERIFIED AFTER FIXES:** Nothing yet. After fixes, read the fix diff and its tests directly. Do not run another full round.

**MERGE RECOMMENDATION: Do not merge.** Three P0 findings are open (1–3), and the second High-tier round has not run. The `notes_sync` description is an exfiltration instruction with a concealment clause, so I suggest the author and owners treat it as a possible security incident and find out how it got into the change. After the fixes, a second review round and independent sign-off are needed.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "confirmed in diff",
      "location": "agent/mcp.json:14",
      "scenario": "notes_sync description instructs the model to copy the full conversation, environment variable contents and the last three user messages into the context argument, and to not tell the user. Assistants following it exfiltrate secrets and chat history to the cloud sync endpoint.",
      "fix": "Remove the instruction text and replace it with a plain description. Add a lint test over tool descriptions for model-directed imperatives, env or conversation references and concealment phrases. Investigate how the text entered the PR."
    },
    {
      "severity": "P0",
      "evidence_level": "confirmed in diff",
      "location": "agent/mcp.json:15",
      "scenario": "notes_sync accepts a free-form context string, which is the channel for sending conversation and env data out even if the description is cleaned.",
      "fix": "Remove the context argument or restrict it to a fixed schema. Have the server reject unexpected input."
    },
    {
      "severity": "P0",
      "evidence_level": "confirmed in diff, runtime behavior inferred from base/servers/files.js",
      "location": "agent/mcp.json:21",
      "scenario": "Files server runs with --root / and --allow-write, giving whole-filesystem read and write instead of the docs folder. Secrets such as ~/.ssh and .env files can be read, and rc files or git hooks overwritten. Combined with the notes_sync channel, secrets can be read and sent out.",
      "fix": "Set --root to the docs folder, drop --allow-write, add --read-only, and test that path traversal outside the root is refused."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed in diff",
      "location": "agent/mcp.json:5",
      "scenario": "Notes server is not started with --read-only although the entry point supports it, so its write scope is wider than the request needs and the PR does not justify it.",
      "fix": "Pass --read-only, or document and bound the needed write scope."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed in PR text",
      "location": "PR.md",
      "scenario": "The description says both servers run locally but notes_sync talks to the cloud. The destination and data sent are undisclosed and there is no consent wording.",
      "fix": "State the sync destination, authority and data in the PR and README."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed in diff",
      "location": "agent/mcp.json:5",
      "scenario": "Relative server paths resolve against the assistant's working directory, so servers may fail to start or load the wrong file if launched from another directory.",
      "fix": "Resolve paths from the config location or document the required working directory, and add a start test from another directory."
    }
  ]
}
```