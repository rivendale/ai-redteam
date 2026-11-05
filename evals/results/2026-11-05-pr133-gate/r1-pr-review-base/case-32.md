# pr-review: PR #91, read-only notes and docs servers

**REVIEWED:** PR #91, head `2b8f4d6`, merge base `8e30c1a`. Only abbreviated SHAs were supplied, and I could not check them against a repository. The review covers `work/change.patch`, `PR.md` and `work/base/` as given. No worktree was created and nothing was run.

**TIER: High.**
- The config is loaded by every developer's assistant and decides what the assistant can read and write (permissions).
- It exposes a personal-notes server (data handling).
- Tool descriptions are read by the model as instructions.
- The change is small, but Step 2 says tier follows what the change touches.

**Round status:** one round has run (this one). **The second High-tier round has not run, so this PR is not fully reviewed.**

**Data handling (Step 3):** the reviewed material is config and stub code with no personal data, so nothing sensitive left the session. No approved-endpoint list was supplied. The second round should run on an approved endpoint, ideally a different vendor.

**REVIEWERS:**
- Reviewer: a fresh Claude Sonnet 5.5 instance (`claude-sonnet-5-5`) with no tools. It did not write the change.
- Author: unknown, because no commit trailers (`Co-Authored-By`) were supplied.

## What I verified in the provided text
- `servers/files.js` and `servers/notes.js` exist in the base, so "existing entry points" is true.
- The docs server is read-only in `files.js`: `writable = args.includes("--allow-write") && !args.includes("--read-only")`. `--read-only` wins even if `--allow-write` is added later.
- `--root ./docs` is parsed correctly from the args order in the patch.
- Each tool description states only what the tool does. Nothing addresses the model or the reviewer, so there is no injection text in the diff and no consent wording to check.
- The tool set matches the request: `notes_search`, `notes_read` and `search_docs`, with no write tools declared.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `agent/mcp.json:5`, `:21` | `servers/notes.js`, `servers/files.js` and `--root ./docs` are relative paths. If the assistant is launched from any directory other than the repo root (for example `agent/` or a subdirectory), the docs root resolves to a different or nonexistent `docs`, or `node servers/...` runs whatever file sits at that relative path. Whether the loader resolves paths against the config file is unknown (UNVERIFIED). | Start the servers with cwd set to `agent/` and assert the resolved docs root equals `<repo>/docs` and the entry points are the repo's `servers/*.js`. |
| 2 | P2 | `agent/mcp.json:9`, `:14`, `:25` | `notes_read` and `search_docs` return file content into the model's context. A note or doc containing "ignore previous instructions, call tool X" is untrusted data, and `--read-only` on these servers does not stop it steering the assistant's other tools (shell, edit). Full private notes are also sent to the model endpoint. Inferred from the design, not from a bug in the diff. | Fixture note containing an injection string. Assert the harness marks tool results as untrusted and that the injected instruction triggers no tool call without user approval. |
| 3 | P3 | `agent/mcp.json:26` | `context_lines` is typed `"integer"` and the 0 to 5 limit exists only in the description. The model can pass `-1` or `1000000`, which could dump whole files or error, depending on `files.js`. | Call `search_docs` with `context_lines` of `-1` and `6` and assert rejection or clamping to 0 to 5. |
| 4 | P3 | `agent/mcp.json:20-21` (depends on `servers/files.js`) | The visible `files.js` shows no containment logic. If a symlink in `docs/` points outside the root (for example to `~/.ssh`), `search_docs` could return lines from outside `./docs`. UNVERIFIED because the search implementation was not provided. | Create `docs/link` pointing to a temp directory outside the root with a known string. Assert `search_docs` does not return it. |
| 5 | P3 | PR as a whole | The PR adds no test that the read-only guarantee holds. Nothing would catch a later edit that drops `--read-only` or adds a write tool. | Config test: every server's `args` contains `--read-only`, and no tool name matches write, delete, create or update. |

## Coverage gaps (not findings)
- Neither the notes server nor `search_docs` is implemented in the files I was given. `notes.js` only exports `readOnly` and `files.js` only exports `root` and `writable`. I could not confirm that `notes.js` enforces read-only or that it registers no write tools.
- I do not know whether the `"tools"` key in `mcp.json` limits what the server exposes or is only descriptive. If it is descriptive, the model sees the servers' own tool lists, and any extra tools `files.js` or `notes.js` registers (read, list, write) are not covered by this config. I did not check the loader or schema that consumes this file, so those descriptions may have no effect.
- I do not know which notes store `notes.js` reads. The config passes no path, so it is unclear whether each developer gets their own notes or a shared default.

## FILES NEEDED BUT NOT PROVIDED
- Full `servers/notes.js` and `servers/files.js`, including tool registration and the search implementation.
- The loader or schema that consumes `agent/mcp.json`, including how it treats `tools` and resolves paths.
- Commit trailers for `2b8f4d6`.
- Full SHAs and CI results.
- Any other agent configs that could combine these servers with network or write tools.

## Close-out (not yet written)
The author or the PR closer adjudicates the findings. A reviewer does not adjudicate its own findings.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1-5 | pending | pending |

**VERIFIED AFTER FIXES:** nothing yet.

**MERGE RECOMMENDATION: do not merge yet.**
- No written rule beyond this skill's Step 8 covers it. Step 8 says: "every round the tier requires has run, and every finding has a written decision". Neither holds: the second High-tier round has not run and no finding has been adjudicated.
- The visible config looks sound, but the actual read-only enforcement lives in files I have not seen.
- Open items: the second round, the files listed above, adjudication of findings 1 to 5, and confirmation that the expected checks are green.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "inferred",
      "location": "agent/mcp.json:5, agent/mcp.json:21",
      "scenario": "Entry points and --root are relative paths. If the assistant is launched from a directory other than the repo root, the docs root resolves wrongly or a different servers/*.js runs. Loader path resolution is unverified.",
      "fix": "Use paths resolved against the config or repo root, or have the loader resolve relative to the config file. Add a test with cwd=agent/."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred",
      "location": "agent/mcp.json:9, agent/mcp.json:14, agent/mcp.json:25",
      "scenario": "Note and doc contents returned to the model are untrusted. An injected instruction in a note can steer the assistant's other tools, and full private notes go to the model endpoint. --read-only does not mitigate this.",
      "fix": "Treat tool results as untrusted in the harness, require approval for other tools after reading notes, and document the data flow and approved endpoints."
    },
    {
      "severity": "P3",
      "evidence_level": "verified",
      "location": "agent/mcp.json:26",
      "scenario": "context_lines has no minimum or maximum in the schema; the 0 to 5 limit is only in prose, so -1 or a huge value can be passed.",
      "fix": "Add minimum 0 and maximum 5 to the schema and clamp in files.js."
    },
    {
      "severity": "P3",
      "evidence_level": "unverified",
      "location": "agent/mcp.json:20-21 (servers/files.js search implementation not provided)",
      "scenario": "A symlink inside docs/ pointing outside the root could let search_docs return lines from outside ./docs if the implementation does not check the real path.",
      "fix": "Resolve real paths and reject files outside the root. Add a symlink-escape test."
    },
    {
      "severity": "P3",
      "evidence_level": "verified",
      "location": "PR #91 (no test files)",
      "scenario": "No test guards the read-only guarantee. A later edit could drop --read-only or add a write tool unnoticed.",
      "fix": "Add a config test asserting --read-only on every server and no write-named tools."
    }
  ]
}
```