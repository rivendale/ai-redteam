# PR #91 Review Report

**REVIEWED:** PR #91, head `2b8f4d6`, merge base `8e30c1a`. I reviewed the provided `change.patch` and `base/` snapshot, not a live checkout. I had no tools, so I could not create a worktree, confirm the SHAs or run anything.

**TIER: High.** The diff is one small JSON file, but it does three high-risk things:
- It decides permissions: whether the assistant gets read or write access.
- It exposes personal data: the user's notes.
- It is loaded by every developer's assistant, and its tool descriptions are read by the model as instructions.

High tier needs two rounds, ideally from two vendors. **This is round 1 of 2. The PR is not reviewed until round 2 runs.**

**DATA (Step 3):** The inputs say nothing about which endpoints are approved for this code. The diff contains no secrets or personal data, so this round was low-risk. Round 2 must go to an endpoint the owner has approved.

**REVIEWERS:**
- Round 1: a fresh Claude instance (`claude-opus-5-5`) with no part in writing the change.
- Author: not determinable. No commit trailers were provided; read `Co-Authored-By` from `2b8f4d6` before close-out.

### What checks out
- **Descriptions are clean.** All three tool descriptions say only what the tool does. None contains an instruction aimed at the model, such as "always", "before answering", "ignore" or "also call". The PR's claim holds.
- **Read-only flags are set.** Both servers get `--read-only`. In `base/servers/files.js:4`, `writable` is false unless `--allow-write` is passed, and `--read-only` overrides it. Write access for docs is off twice over.
- **The diff matches the request.** It adds a notes server with search and read, and a docs search. Nothing extra is added.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 *(conditional; unverified)* | `agent/mcp.json:5` (`--read-only` passed to notes) and `base/servers/notes.js:2` | `notes.js` only *parses* `--read-only` into an exported flag. The provided code never enforces it. The comment says the tools in `mcp.json` are served from this file. If the server also registers a write tool (e.g. `notes_write`/`notes_delete`), or the client lists tools from the server rather than treating `mcp.json` `"tools"` as an allowlist, every developer's assistant could get write or delete access to the user's notes. The "read-only" in the PR title would then rest on an unchecked flag. | Start `node servers/notes.js --read-only` and call the server's tool list. Assert that it returns exactly `notes_search` and `notes_read`, and that calling any write tool is refused. |
| 2 | P3 | `agent/mcp.json:25-26` | The `search_docs` description promises `context_lines` "0 to 5", but the schema is a bare `"integer"`. `files.js` shows no bound. With `context_lines: 100000`, each match returns whole files, which floods the model's context. The model may also rely on a limit that does not exist. The impact stays within `./docs` and is read-only. | Call `search_docs` with `context_lines: 100000` and with `-1`. Assert each call is rejected or clamped to 0..5. Alternatively, add `"minimum": 0, "maximum": 5` to the schema and test that the client enforces it. |
| 3 | P3 | `agent/mcp.json:4,21` (`servers/…`, `./docs`) | Both the script paths and the docs root are relative to the process working directory. If the assistant is launched outside the repo root, both servers fail to start. In a layout where the scripts are found but cwd differs, `./docs` points at another folder. | Launch the assistant from a subdirectory and from `$HOME`. Assert both servers start and that `search_docs` searches only `<repo>/docs`. |

### FILES NEEDED BUT NOT PROVIDED
- **The rest of `servers/notes.js`:** which tools it registers, and whether `readOnly` gates them. This decides finding 1.
- **The rest of `servers/files.js`:** whether it keeps file access inside `--root` (no `../` escapes or symlink escapes), and whether it implements `context_lines` at all.
- **The client or loader that reads `agent/mcp.json`:** whether `"tools"` is an allowlist or only descriptive, and how relative paths are resolved.
- **Whether `docs/` exists at the merge base.** The base snapshot shows only `README.md` and `servers/`.
- **Commit trailers on `2b8f4d6`,** to identify the author.

---

### Close-out
**ADJUDICATION:** Pending. The author decides on each finding; as reviewer, I do not adjudicate my own findings.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | — | — |
| 2 | — | — |
| 3 | — | — |

**VERIFIED AFTER FIXES:** None yet.

**MERGE RECOMMENDATION: do not merge (yet).**
- Round 2 of the High tier has not run.
- Finding 1 is a potential P1 that cannot be closed without the `notes.js` code and loader code listed above.
- No CI checks were shown. A missing check is not green.

If `notes.js` shows that `--read-only` removes all write tools, finding 1 can be rejected with that line as evidence. The PR would then be close to merge-ready once round 2 and the P3s are dealt with.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "unverified (conditional on code not provided)",
      "location": "agent/mcp.json:5; base/servers/notes.js:2",
      "scenario": "notes.js only parses --read-only into an exported flag; no enforcement is shown. If the server registers write tools or the client lists tools from the server instead of treating mcp.json 'tools' as an allowlist, every developer's assistant gets write/delete access to the user's notes.",
      "fix": "Show or add enforcement so that --read-only registers only notes_search and notes_read; add a test that lists tools under --read-only and asserts exactly those two, with write calls refused."
    },
    {
      "severity": "P3",
      "evidence_level": "verified in provided diff (no bound in schema); enforcement in files.js not shown",
      "location": "agent/mcp.json:25-26",
      "scenario": "The description promises context_lines 0 to 5 but the schema is a bare integer; context_lines=100000 returns whole files and floods context.",
      "fix": "Add minimum 0 / maximum 5 to the schema and clamp or reject in files.js; test with 100000 and -1."
    },
    {
      "severity": "P3",
      "evidence_level": "inferred from relative paths in diff",
      "location": "agent/mcp.json:4,21",
      "scenario": "Script paths and the ./docs root resolve against the process cwd; launched outside the repo root, the servers fail to start or ./docs points elsewhere.",
      "fix": "Resolve paths relative to the config/repo root (or document the required cwd); test launching from a subdirectory and from $HOME."
    }
  ]
}
```