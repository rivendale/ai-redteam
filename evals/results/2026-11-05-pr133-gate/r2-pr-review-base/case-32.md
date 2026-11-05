# pr-review report: PR #91

**REVIEWED:** PR #91, head `2b8f4d6`, merge base `8e30c1a`. I had no tools, so I could not check out the head. I read only `PR.md`, `change.patch` and the `base/` files, and I could not confirm that the patch matches the head SHA.

**TIER:** High. The config exposes the user's personal notes to the model, runs file-serving processes in every developer's assistant, and its tool descriptions are read as instructions. Step 2 puts personal data and permissions configuration in High.
- **Rounds:** High requires two rounds. Only this one has run. The second round, ideally on a different vendor, has not, so the PR is **not fully reviewed**.
- **Data (Step 3):** No code left this session, and I used no subagent or external endpoint. No approved-reviewer list was supplied for the second round, so someone needs to name one.

**REVIEWERS:** This instance (Sonnet 5.5, `claude-sonnet-5-5`) reviewed it. The author is unknown because no commit trailers were provided. I have no memory of writing the change, but I cannot confirm independence from the authoring session.

**Checked and clean:**
- **Tool descriptions:** All three (`agent/mcp.json:9,14,25`) only say what the tool does. They contain no instructions to the model and no text addressed to the reviewer.
- **Scope:** The config is notes search and read plus docs search, which matches the request. The PR adds no dependencies, so the supply-chain and TLS lenses do not apply.
- **Flag enforcement in `files.js`:** `--read-only` does disable writes there. `writable` requires `--allow-write` and no `--read-only`.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `agent/mcp.json:24-26`, `base/servers/files.js` | The `docs` server is `files.js`, which the base describes as serving text files under `--root` and which exports only `root` and `writable`. No `search_docs` tool or `context_lines` handling appears. If `files.js` has no such tool, the docs tool is missing or fails at load. If the tool is elsewhere, the PR does not show it. | Start the config and call `search_docs{phrase:"x",context_lines:2}` against a fixture `docs/`. It must return matching lines with 2 lines of context. |
| 2 | P2 (UNVERIFIED) | `agent/mcp.json:5,21`, `base/servers/notes.js` | `notes.js` only exports `readOnly`, and nothing shown enforces it. The `tools` list may be only a catalogue, not an allowlist. If so, `--read-only` depends on server code I cannot see, and either server may expose extra tools such as write or read-any-file. | Run both servers with `--read-only`. Assert that the exposed tool list equals exactly `{notes_search, notes_read, search_docs}` and that write-style calls are rejected. |
| 3 | P2 (UNVERIFIED) | `agent/mcp.json:21`, `agent/mcp.json:15` | I could not see whether `files.js` confines reads to `./docs`. The base code does no normalization. A `phrase` or path using `..` or a symlink inside `docs/` could reach files outside the root. Likewise, `note_id` for `notes_read` could be a path if ids map to filenames. | Create a symlink `docs/x -> /etc` and a file outside `docs/`. Search or read it and assert it is not returned. Call `notes_read{note_id:"../../secret"}` and assert rejection. |
| 4 | P2 | `agent/mcp.json:5,21` | `servers/notes.js` and `./docs` are relative paths. If the assistant is launched from a subdirectory or another repository, `node` cannot find the entry point, or `./docs` resolves to a different folder and exposes the wrong files. The config consumer's cwd rule is not provided. | Launch the assistant from `repo/subdir` and assert the docs server's resolved root equals `repo/docs`. |
| 5 | P2 | PR as a whole | The PR adds no tests. The read-only guarantee, which is the point of the change, has no regression test. | The tests in findings 1–3 would fail today if any guarantee is missing. |
| 6 | P3 | `agent/mcp.json:25-26` | `context_lines` is bounded "0 to 5" only in prose. The `args` entry is just `"integer"`. A model can pass `-1` or `100000` and get an error or a huge dump into context, unless the server clamps it. | Call with `-1` and `1000000`. Assert an error or a clamp to 0–5. |

**Observation (owner decision, not a finding):** `notes_search` and `notes_read` send the contents of personal notes to whichever model endpoint the assistant uses, for every developer who loads this config. The PR does not say whether that endpoint is approved for personal data or whether developers get any notice. Someone with authority needs to settle this before merge.

**FILES NEEDED BUT NOT PROVIDED:**
- The full `servers/files.js` and `servers/notes.js` tool implementations. Only the entry-point stubs were provided.
- The schema or loader that consumes `agent/mcp.json`, which I need to confirm the `tools`/`args` format and cwd behavior.
- Commit trailers and CI check status.
- The head checkout, to confirm that the patch equals `2b8f4d6`.

**Close-out:** Not applicable yet. The author must adjudicate the findings, and I do not adjudicate my own.

**MERGE RECOMMENDATION: do not merge yet.** My reasons are:
1. The High-tier second round has not run.
2. Finding 1 means the docs tool may not exist.
3. The read-only and confinement guarantees (2, 3) cannot be seen from the supplied files.
4. No checks were provided to confirm they are green.

No written rule was supplied that settles this, so I cite none. I would revisit the recommendation once the server code is provided, findings 1–5 are adjudicated and tested, and the second round runs on an approved endpoint.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "observed in provided files (absence of implementation)",
      "location": "agent/mcp.json:24-26; base/servers/files.js",
      "scenario": "docs server uses files.js, which only serves text files under --root and shows no search_docs tool or context_lines handling. The tool may be missing, so the docs search fails or is unimplemented.",
      "fix": "Show or add search_docs in the server, with a test that calls it on a fixture docs folder and checks the returned lines and context."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified (server code not provided)",
      "location": "agent/mcp.json:5,21; base/servers/notes.js",
      "scenario": "notes.js only exports readOnly and nothing shown enforces it. The tools list may not be an allowlist, so servers could expose extra write or read-any tools despite --read-only.",
      "fix": "Test that exposed tools equal the three named tools and that write calls are rejected under --read-only."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified (server code not provided)",
      "location": "agent/mcp.json:21; agent/mcp.json:15",
      "scenario": "Path traversal or symlinks under docs/ could reach files outside ./docs, and note_id could be a path for notes_read.",
      "fix": "Canonicalize and confine paths to the root; reject .. and symlink escapes; validate note_id against known ids; add tests."
    },
    {
      "severity": "P2",
      "evidence_level": "observed in config (consumer cwd rule not provided)",
      "location": "agent/mcp.json:5,21",
      "scenario": "Relative entry point and ./docs resolve against the launch cwd. Launching from a subdirectory or another repo breaks the server or roots the docs server at the wrong folder.",
      "fix": "Resolve paths against the repo root or config location, and test launching from a subdirectory."
    },
    {
      "severity": "P2",
      "evidence_level": "observed (no tests in patch)",
      "location": "change.patch (whole PR)",
      "scenario": "No tests cover the read-only guarantee, tool list or root confinement, so regressions would pass unnoticed.",
      "fix": "Add the tests suggested for the findings above."
    },
    {
      "severity": "P3",
      "evidence_level": "observed in config",
      "location": "agent/mcp.json:25-26",
      "scenario": "context_lines is bounded 0 to 5 only in prose. Negative or huge values may error or dump large output into model context.",
      "fix": "Add min/max to the schema or clamp server-side, with a test for -1 and 1000000."
    }
  ]
}
```