**Review report**

**REVIEWED:** PR #91, head `2b8f4d6`, merge base `8e30c1a`. I reviewed it from the inputs provided (PR.md, change.patch, base/). I had no tools in this session, so I did not open a worktree, run anything or check any SHA.

**TIER:** High. The change is small, but it is a permissions config. It decides which tools every developer's assistant gets and whether they can write. The notes server also carries the user's personal notes, which counts as personal data. High tier needs two rounds. This is round 1 of 2, so the PR is not yet reviewed until a second round, ideally on another vendor, has run.

**DATA:** Nothing was sent outside this session.

**REVIEWERS:** One instance (Opus 5.5) with no part in writing the change. The author is unknown because the commit trailers were not provided.

**Checked and clean:**
- **Request coverage:** The notes server has search and read, the docs search is read-only, and nothing else is added.
- **Tool descriptions:** All three only describe what the tool does. None contains a hidden instruction, a cross-tool directive, or text aimed at the model rather than describing the tool.
- **Write flags:** Both servers get `--read-only` and neither gets `--allow-write`. In `base/servers/files.js:4` this gives `writable === false`.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `agent/mcp.json:5,21` (`"servers/notes.js"`, `"./docs"`) | The script paths and `--root ./docs` are relative, and the config has no `cwd` field. If the client resolves them against its own working directory rather than the repo root (for example, a developer starts the assistant in a subdirectory or another project), two things can go wrong. `node servers/notes.js` fails to start. Or `files.js` serves a different project's `docs/` folder, or none. Whether this happens depends on the client's resolution rule, which was not provided. | Start the client from a subdirectory of the repo. Assert both servers start and `search_docs` returns a line known to exist only in this repo's `docs/`. |
| 2 | P3 | `agent/mcp.json:25-26` (`context_lines`) | The 0–5 range exists only in the description text. The schema is a bare `"integer"`, and nothing in the provided `files.js` enforces a range. A call with `context_lines: 100000` or `-1` reaches the server. Unless the server clamps it, the call returns whole documents (search becomes a full read) or fails on a negative value. This stays inside `./docs`, so the risk is context bloat, not a widened scope. | Call `search_docs` with `context_lines` of 100000 and -1. Assert at most 5 lines of context, or a validation error. Add `minimum: 0, maximum: 5` to the schema if the format supports it. |

**FILES NEEDED BUT NOT PROVIDED:**
- **Tool implementations in `servers/notes.js` and `servers/files.js`.** The base files only parse flags. I need to confirm that `readOnly` and `writable` are enforced in every handler, that `search_docs` is actually served by `files.js`, and that path traversal outside `--root` is blocked (for example `../`, absolute paths, symlinks).
- **The client's rule for the `"tools"` array.** Is it an allowlist, or only descriptions? If the servers expose further tools, such as a file read or list in `files.js` or a write tool in `notes.js`, the assistant may receive more than the request asked for.
- **The client's path-resolution rule for `command`, `args` and the working directory** (needed for finding 1).
- **Commit trailers** (to record the author) and **CI check status**.

**Close-out**

**ADJUDICATION:** Pending. The author must decide each finding. As the reviewer, I do not adjudicate my own findings.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | — | — |
| 2 | — | — |

**VERIFIED AFTER FIXES:** None yet.

**MERGE RECOMMENDATION: do not merge (yet).**
- The High tier's second round has not run.
- Findings 1 and 2 have no decision.
- Read-only enforcement in the server handlers cannot be verified from the material provided, and that is the core claim of this PR.
- Check status is unknown, and a missing check is not green.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "inferred: config has no cwd, client resolution rule not provided",
      "location": "agent/mcp.json:5,21",
      "scenario": "Relative 'servers/notes.js' and '--root ./docs' resolve against the client's working directory; launching the assistant from a subdirectory or another project makes the notes server fail to start or points the docs server at a different or missing docs folder.",
      "fix": "Make paths relative to the config file or repo root (cwd field or a path variable, per the client's format), and add a launch test from a subdirectory."
    },
    {
      "severity": "P3",
      "evidence_level": "read in config; server-side clamping unverified (handler code not provided)",
      "location": "agent/mcp.json:25-26",
      "scenario": "The 0-5 bound on context_lines is only in the description; the schema is a bare integer, so context_lines=100000 or -1 reaches the server and, if unclamped, returns whole documents or errors.",
      "fix": "Enforce 0-5 in the server handler (and in the schema if it supports minimum/maximum); add tests for out-of-range values."
    }
  ]
}
```