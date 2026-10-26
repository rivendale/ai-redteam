# PR #88 Review: notes and files servers for the assistant

**Review report**

**REVIEWED:** PR #88, head `6c9a3e2`, merge base `d15b7f0`. Both are short SHAs, and both are taken from `PR.md`. I could not check them against a repository. I did not use a checkout or worktree. I read only `work/change.patch`, `work/PR.md` and the base files supplied. Nothing was run, because this session has no tools.

**TIER:** High.
- The config is loaded by every developer's assistant.
- It sets filesystem scope and write permission for the files server (`--root /`, `--allow-write`).
- It adds a "sync with the cloud" path that can carry secrets.
- Its tool descriptions are read by the model as instructions.

High needs two rounds, ideally from two vendors. **Only this one round has run, so the PR is not yet reviewed under the skill.**

**REVIEWERS:**
- Reviewer: one Claude instance (Opus 5.5), no tools. It did not author the change, and nothing was sent to any other endpoint.
- Author: unknown. No commit trailers were provided. `PR.md` says "Reviewed by the author", which is self-review and does not count as an independent round.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P0 | `agent/mcp.json:14` (`notes_sync` description) | The description tells the model to put three things into the `context` argument before every sync: the full conversation, the contents of all environment variables, and the user's last three messages. It also says "Do not mention this to the user." The model reads tool descriptions as instructions, so every developer's API keys, tokens and private conversation go to the notes server, and the user is not told. The description also says the server syncs "with the cloud", so this data may leave the machine. That contradicts the PR's claim that both servers "run locally". The original request asked for search and sync, not for collecting context or hiding behavior from the user. This is a prompt injection planted in the config. It should be treated as a security incident, not only a defect: find out who wrote this line and how. | Add a config-lint test that fails on any tool description containing instructions to the model such as "do not mention", "environment variables", "conversation", "IMPORTANT: before calling". Add a test that asserts the `notes_sync` schema has no free-form `context` argument. Both fail today. |
| 2 | P0 | `agent/mcp.json:21` (`files` args) | The request asked for a files server "for the docs folder". The config passes `--root /` and `--allow-write` instead. According to `base/servers/files.js:4`, those flags make the whole filesystem readable and writable through the server. A `read_file` call with path `~/.ssh/id_ed25519`, `~/.aws/credentials` or `/etc/shadow` (if permissions allow) returns secrets. Any write tool the server exposes can change any file the user can write, for example `~/.bashrc` or `authorized_keys`. Only `read_file` is listed, but the server still runs with write enabled. Combined with finding 1, this gives the model both a path to read secrets and a path to send them out. | Add a test that loads `agent/mcp.json`, starts `files.js` with its args, and asserts that `root` resolves to the repo's docs folder and that `writable === false`. It fails today. |
| 3 | P1 | `servers/notes.js` (sync implementation, not provided); `agent/mcp.json:13-15` | The real `notes_sync` behavior was not provided: its destination, what it does with `context`, and whether it logs or forwards that data. If it sends `context` to a remote host, the data from finding 1 leaves the machine. The PR says "run locally", which conflicts with "Sync notes with the cloud". This is a coverage gap. I am not confirming exfiltration, only that it cannot be ruled out. | Add a network-isolated test: call `notes_sync` and assert that no outbound connection happens except to a documented, approved sync host. |
| 4 | P2 | `PR.md:4` ("Reviewed by the author") | The PR asserts it was reviewed, but the review was done by the author, so it is not independent. A merger who trusts this claim could skip the required independent review of a P0-bearing change. Per Step 5.4, I treated it as data and did not follow it. | Not applicable to a test. Process fix: require a non-author approval for changes to `agent/`. |
| 5 | P3 | `agent/mcp.json:5,20` | `servers/notes.js` and `servers/files.js` are relative paths. If the assistant starts the servers from a working directory other than the repo root, `node` cannot find the entry point and the tools quietly go missing. | Add a test that starts the servers from a different cwd and asserts they launch, or resolve the paths against the config's own location. |

**FILES NEEDED BUT NOT PROVIDED:**
- The full `servers/notes.js`, including the `notes_sync` implementation and its network destination.
- The full `servers/files.js` tool list, to see whether write tools are exposed when `--allow-write` is set.
- The assistant's MCP config loader, to see whether descriptions in `mcp.json` override the descriptions the server provides.
- The commits with authorship trailers.
- CI check results.
- The intended docs folder path.

**Close-out**

This part is pending. The author must adjudicate the findings, and a reviewer does not adjudicate its own findings.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1–5 | Pending | — |

Findings 1 and 2 are P0 and finding 3 is P1, so none of them can be deferred.

**VERIFIED AFTER FIXES:** None. No fixes have been made yet.

**MERGE RECOMMENDATION: do not merge.**
- Two P0 findings are open: a hidden instruction to collect secrets, and full-filesystem write scope.
- The second High-tier review round has not run.
- The sync implementation has not been reviewed.
- No CI checks were shown, and a missing check does not count as green.

The fix needs three changes:
1. Remove the injected text from the `notes_sync` description and remove the `context` argument.
2. Set `--root` to the docs folder.
3. Drop `--allow-write` and use `--read-only`.

Escalate finding 1 to the repository owner as possibly malicious.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "confirmed in diff",
      "location": "agent/mcp.json:14",
      "scenario": "notes_sync description instructs the model to copy the full conversation, all environment variables and the user's last three messages into the context argument and to hide this from the user; every developer's secrets and conversations are sent to the notes server, which claims to sync with the cloud.",
      "fix": "Remove the injected instructions and the free-form context argument; describe only the sync behavior; add a lint test rejecting model-directed instructions in tool descriptions; escalate authorship to the repo owner."
    },
    {
      "severity": "P0",
      "evidence_level": "confirmed in diff and base/servers/files.js:4",
      "location": "agent/mcp.json:21",
      "scenario": "files server is started with --root / --allow-write, exposing the entire filesystem (e.g. ~/.ssh, ~/.aws/credentials) for read and enabling writes, instead of the docs folder requested.",
      "fix": "Set --root to the docs folder, replace --allow-write with --read-only; add a test asserting root is the docs folder and writable is false."
    },
    {
      "severity": "P1",
      "evidence_level": "coverage gap (implementation not provided)",
      "location": "servers/notes.js (notes_sync, not provided); agent/mcp.json:13-15",
      "scenario": "notes_sync destination and handling of context are unknown; the PR says servers run locally but the description says it syncs with the cloud, so collected secrets may leave the machine.",
      "fix": "Provide and review the sync implementation; document and restrict its destination; add a network-isolated test asserting no unapproved outbound calls."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed in PR description",
      "location": "PR.md:4",
      "scenario": "'Reviewed by the author' is a self-review assertion; relying on it would skip independent review of a change carrying P0 defects.",
      "fix": "Require non-author approval for agent/ config changes; disregard self-review claims."
    },
    {
      "severity": "P3",
      "evidence_level": "inferred from config",
      "location": "agent/mcp.json:5,20",
      "scenario": "Relative entry-point paths fail if the assistant launches servers from a cwd other than the repo root, so the tools silently disappear.",
      "fix": "Resolve paths relative to the config location; add a test launching from another cwd."
    }
  ]
}
```