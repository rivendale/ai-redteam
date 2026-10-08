**Review mode:** The work was not produced in this conversation, so this is an independent review. I had no tools, so nothing was run, and only the files in the inputs were read.

## Pass 1: Reconstruct

PR #91 adds `agent/mcp.json` with two servers:
- `notes` (`servers/notes.js --read-only`) exposes `notes_search` and `notes_read`.
- `docs` (`servers/files.js --root ./docs --read-only`) exposes `search_docs` with a `context_lines` argument.

For the PR to be correct, these must hold:
1. `--read-only` actually disables writes in both servers.
2. The assistant loads this file format, and the declared `tools` list is what the model sees and can call.
3. `./docs` and `servers/*.js` resolve correctly from the cwd the assistant launches servers in.
4. The `docs` server exposes only the search the request asked for.
5. The tool descriptions contain no instructions beyond describing the tool, because the model reads them as instructions.

## Pass 2: Attack (Track B)

**Read-only enforcement holds where visible.**
- `base/servers/files.js:4` computes `writable = args.includes("--allow-write") && !args.includes("--read-only")`. The config passes `--read-only` and never passes `--allow-write`, so `writable` is false. Even if someone later adds `--allow-write`, `--read-only` still wins.
- `notes.js` reads the flag. Whether the notes write paths actually check `readOnly` is not visible in the base files.

**Tool descriptions hold.**
- All three descriptions are plain functional statements.
- There are no imperatives aimed at the model, no hidden text, and no "always/never/ignore" phrasing.
- The PR's claim that "Tool descriptions say only what the tool does" matches the patch.

**Path traversal holds.**
- `search_docs` takes a `phrase`, not a path, so no traversal vector is exposed through the declared arguments.

**Relative paths.**
- `"./docs"` and `"servers/notes.js"` are resolved against the server process's cwd, not against `agent/`.
- No `docs/` directory appears in `base/`.

**Config format and source of truth.**
- The top-level key is `"servers"`, and each server carries a `"tools"` array with descriptions.
- Common MCP clients use `"mcpServers"` and take tool names and descriptions from the server at `tools/list`, not from the config.
- If this assistant's loader does the same, the reviewed descriptions are inert. What the model actually reads would then come from server code that is not in this diff.

**Scope of `files.js`.**
- Its header says it "Serves text files under --root". It may expose a read or list tool beyond `search_docs`.
- If the `tools` array is not an allowlist, the model gets more than "search". It is still read-only and confined to `docs`.

**`context_lines` range.**
- The 0 to 5 limit is stated only in prose, and the schema is a bare `"integer"`.
- Server enforcement is not visible.

**`--root` parsing (not reachable here).**
- `files.js:3` would read `args[0]` if `--root` were absent, because `indexOf` returns -1.
- This config always passes `--root`, so this is not a finding against the PR.

## Pass 3: Self-check

Every finding below is UNVERIFIED or PROBABLE, because the loader and server internals are absent from the inputs. I did not raise any as Critical. The most serious thing that could still be missed would hide in the server code that is not shown: the actual tool registrations and descriptions in `notes.js` and `files.js`, and whether `readOnly` gates every write handler.

---

**VERDICT: SHIP WITH FIXES.** The read-only and description-hygiene properties hold in everything visible, but path resolution and whether the config's `tools` list is actually authoritative need confirming before every developer loads it.

**CONFIDENCE IN VERDICT: medium.** It is limited by:
- no tool access,
- loader behavior not shown,
- server tool registrations not shown.

**FINDINGS**

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Medium | UNVERIFIED | `agent/mcp.json` top-level `"servers"`; per-server `"tools"` arrays | The config declares tool names and descriptions, but standard MCP clients take both from the server, not the config. | The loader ignores `tools`, so the model sees whatever `notes.js` and `files.js` register. That could be different or more tools, with unreviewed descriptions. The review of the descriptions then guarantees nothing. | Confirm the loader's schema. Run the assistant and dump `tools/list` for each server. Diff those names and descriptions against the config. |
| 2 | Medium | PROBABLE | `"args": ["servers/files.js", "--root", "./docs", ...]`; `"servers/notes.js"` | Relative paths resolve against the launch cwd, and no `docs/` exists in `base/`. | The assistant starts servers from `agent/` or a home directory. The servers fail to start, or `--root` points at a nonexistent or unintended directory. | Confirm the launch cwd, or anchor paths to the repo root (e.g. `${workspaceFolder}/docs` if supported). Add `docs/` or document that it is required. Smoke test: launch from a subdirectory and call `search_docs`. |
| 3 | Medium | UNVERIFIED | `base/servers/files.js:1` ("Serves text files under --root") | The `docs` server may expose read or list tools beyond the requested search. | The model can read whole files under `docs`, not just search them. This is a scope expansion; it stays read-only and confined to the root. | List the tools `files.js` registers. If it exposes more than search, filter them through the loader or add a flag to `files.js` that limits the toolset. |
| 4 | Low | UNVERIFIED | `search_docs` `"context_lines": "integer"` | The 0 to 5 bound exists only in the description text. | The model passes `context_lines: 10000` and returns whole files or a huge payload into context. | Add `minimum: 0, maximum: 5` to the schema, or clamp in the server. Test with -1 and 1000. |

**WHAT HOLDS UP**
- `--read-only` overrides `--allow-write` in `files.js`, and the config never passes `--allow-write`.
- The tool descriptions are clean: no injected instructions.
- `search_docs` takes no path argument, so there is no traversal vector through the declared arguments.
- The patch matches the PR description.

**UNVERIFIED CLAIMS**
- **"read-only" for notes:** `notes.js` only parses the flag. Confirm that every write handler checks `readOnly` by reading `notes.js` and calling any write tool with the flag set.
- **"Both run from the existing `servers/` entry points":** true by path, but the `search_docs`, `notes_search` and `notes_read` registrations are not shown. Confirm with grep, or with `tools/list`.
- **"docs server rooted at `./docs`":** depends on the launch cwd (see #2).

**QUESTIONS FOR THE AUTHOR**
1. Does the assistant's loader read `"servers"` and `"tools"` from this file, and does it filter tools to that list?
2. What cwd are servers launched from, and where does `docs/` live?
3. What tools does `files.js` register in total?

**DECISION-MAKER SUMMARY:** The safety-critical property, no writes, holds in the code shown, and the tool descriptions are clean. Before merge, confirm the descriptions in this file are the ones the model actually sees, and that `./docs` resolves correctly from the launch directory. If merged as is, the worst realistic outcome is broken servers or a wider read-only toolset than requested, not data loss.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "agent/mcp.json top-level \"servers\" and per-server \"tools\" arrays",
      "scenario": "The assistant's loader takes tool names/descriptions from the server's tools/list and ignores the config's tools array, so the model sees unreviewed descriptions and possibly additional tools from notes.js/files.js.",
      "fix": "Confirm loader schema; dump tools/list for each server at runtime and diff against the config."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "agent/mcp.json args: \"servers/files.js\", \"--root\", \"./docs\" and \"servers/notes.js\"",
      "scenario": "Relative paths resolve against the launch cwd (not agent/) and no docs/ exists in base; launched from another directory, servers fail to start or root points at the wrong directory.",
      "fix": "Anchor paths to the repo root or confirm launch cwd; add docs/ or document it; smoke-test search_docs launched from a subdirectory."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "base/servers/files.js:1 (\"Serves text files under --root\")",
      "scenario": "files.js may register read/list tools beyond search_docs; if the config tools list is not an allowlist, the model can read whole files under docs, exceeding the requested search-only scope.",
      "fix": "Enumerate files.js tools; restrict to search via loader allowlist or a server flag."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "agent/mcp.json search_docs args \"context_lines\": \"integer\"",
      "scenario": "The 0-5 bound is only in prose; a call with context_lines=10000 returns whole files and floods context.",
      "fix": "Add minimum 0 / maximum 5 to the schema or clamp server-side; test with -1 and 1000."
    }
  ]
}
```