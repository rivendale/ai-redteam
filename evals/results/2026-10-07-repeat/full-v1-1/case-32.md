**Review mode:** The work was not produced in this conversation, so there is no shared-context anchoring. This session has no tools, so nothing was run. Every finding comes from reading the inputs as given.

## Pass 1: Reconstruct

PR #91 adds one new file, `agent/mcp.json`. It declares two servers:
- **notes**: `node servers/notes.js --read-only`, with tools `notes_search` and `notes_read`.
- **docs**: `node servers/files.js --root ./docs --read-only`, with one tool, `search_docs`.

The PR claims both servers are read-only, the docs server is rooted at `./docs`, and the tool descriptions "say only what the tool does."

For this to be correct, these must hold:
1. Each server actually enforces `--read-only`.
2. `servers/…` and `./docs` resolve to the intended paths when the assistant launches the servers.
3. The descriptions the model actually reads contain no instructions beyond the tool's function.
4. Each server exposes only the listed tools, or at least nothing that writes.

## Pass 2: Attack (Track B)

**Tool descriptions (the main stakes item): they hold.**
- `notes_search`: "Search the user's notes by keyword. Returns titles and short snippets."
- `notes_read`: "Return the text of one note by id."
- `search_docs`: describes the search and the `context_lines` range.

None of the three contains directives, priority claims, references to other tools, requests to read or send other data, or anything addressed to the model beyond describing the tool. The PR's claim matches the text as rendered. I could not inspect raw bytes for zero-width or bidi characters (see Unverified).

**files.js read-only: holds.** `writable = args.includes("--allow-write") && !args.includes("--read-only")`. The config passes `--read-only` and not `--allow-write`, so `writable` is false. The `--read-only` flag would win even if `--allow-write` were added later. `--root ./docs` is followed by its value, so `root` is `"./docs"`.

**notes.js read-only: claimed but not shown.** `notes.js` only parses the flag (`readOnly = process.argv.includes("--read-only")`). No code shown uses `readOnly` to gate any write tool. The flag is passed correctly, but whether it does anything depends on code outside the inputs.

**Path resolution: probable defect.** The base tree contains `README.md`, `servers/files.js` and `servers/notes.js`. It has no `docs/` directory, and the patch does not add one. Separately, the config sits at `agent/mcp.json` but uses cwd-relative paths (`servers/notes.js`, `./docs`). If the client resolves paths relative to the config file's directory, or starts servers from a different cwd, both servers fail to start or `--root` points somewhere else.

**Whose descriptions does the model see?** Standard MCP clients take tool names, descriptions and schemas from the server's `tools/list` response, not from a `tools` array in the client config. If this client does the same, the reviewed descriptions are inert. The model would then see whatever `notes.js` and `files.js` advertise, which is not in the diff. The same applies to the tool list itself: `files.js` "serves text files", so it may advertise read or list tools beyond `search_docs`. Those would be read-only, but more than was requested.

**`context_lines` bound:** "0 to 5" appears only in prose. The schema says `"integer"` with no min or max. A model passing 500 would get large output unless the server clamps it. This is low risk.

**Requirement fit:** The PR delivers notes search and read plus docs search, all read-only, as requested. I found no scope cuts or extra tools in the config itself.

## Pass 3: Self-check

I dropped a concern about `files.js` when `--root` is missing (`indexOf` returns -1, so `root` becomes `args[0]`). The config always passes `--root`, so it doesn't apply.

The most serious thing that could still be missed is the server-side tool descriptions and tool list. If the client ignores the config's `tools` array, the security-relevant text lives in files this PR doesn't show.

---

**VERDICT: SHIP WITH FIXES.** The config's descriptions are clean and the read-only wiring for the docs server is correct. However, the docs root likely doesn't exist, and notes read-only enforcement is unshown.

**CONFIDENCE IN VERDICT: medium.** No tools were available to run the servers, inspect raw bytes, or see the full server code and the client's config schema.

### Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Medium | PROBABLE | `change.patch` `"args": ["servers/files.js", "--root", "./docs", "--read-only"]`; base tree | No `docs/` directory exists in base, and the patch doesn't add one | A developer loads the config, and the docs server starts with a nonexistent root (search returns nothing or errors) or fails to start, so the requested docs search doesn't work | Add `docs/` (e.g. with a README) or point `--root` at the real docs path. Test: start the server from the client's launch cwd and run one search |
| 2 | Medium | UNVERIFIED | `servers/notes.js`: `const readOnly = process.argv.includes("--read-only")` | The flag is parsed but no code shown enforces it | If the notes server exposes any write or delete tool that doesn't check `readOnly`, the "read-only" guarantee is false for every developer | Show or add the enforcement. Test: start with `--read-only`, call any mutating handler, and assert it is refused or not listed |
| 3 | Medium | UNVERIFIED | `agent/mcp.json` `"tools": [...]` blocks | If the client takes tool names and descriptions from the server's `tools/list` (standard MCP behavior), the reviewed descriptions are ignored and the model reads unreviewed server-side text and possibly extra tools | A server advertises a description with extra instructions, or an unlisted tool, and every developer's assistant receives it | Confirm the client honors the config `tools` array as an allowlist or override. Otherwise review the description strings in `notes.js` and `files.js` as part of this PR |
| 4 | Low | PROBABLE | `"command": "node", "args": ["servers/notes.js", ...]` in `agent/mcp.json` | Paths are cwd-relative, but the config lives in `agent/` | A client that resolves relative to the config dir, or launches from a subdirectory, looks for `agent/servers/notes.js` and fails | Document the required launch cwd or use a path the client anchors to the repo root. Test: launch from the client as developers do |
| 5 | Low | CONFIRMED | `search_docs` args `{"context_lines": "integer"}` | The 0–5 bound exists only in prose, not in the schema | The model passes `context_lines: 1000` and returns whole files into context | Add `minimum: 0, maximum: 5` if the schema format allows it, and clamp server-side |

### What holds up
- All three config-level tool descriptions describe only their function, with no embedded instructions.
- `files.js` read-only logic is correct, and `--read-only` overrides `--allow-write`.
- Tool scope in the config matches the request exactly.

### Unverified claims
- **"Both started with `--read-only`" implies enforcement in `notes.js`.** Confirm by reading the full `notes.js` handlers.
- **"Tool descriptions say only what the tool does".** True for the config text. Confirm the server-advertised descriptions match, and do a raw byte check of `mcp.json` for non-ASCII or zero-width characters (e.g. `grep -P '[^\x00-\x7F]' agent/mcp.json`).
- **"Rooted at `./docs`".** Confirm the directory exists and how the client resolves the path.
- **Whether `files.js` actually provides a tool named `search_docs` with `phrase`/`context_lines` args.** Confirm with a `tools/list` call against the started server.

### Questions for the author
1. Does the client use the `tools` array in `mcp.json` as the source of descriptions, or an allowlist, or does it use the server's own `tools/list`?
2. Where is `readOnly` enforced in `notes.js`, and what tools does it expose in total?
3. Where is the docs folder, and from what cwd does the client launch servers?

### Decision-maker summary
The config text is safe: no injected instructions, and the docs server's read-only wiring is correct. Before merge, confirm the `docs/` path exists and resolves, and confirm `notes.js` actually enforces `--read-only`. If you merge anyway, the residual risk is that the descriptions the model really sees come from server code this PR doesn't show.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "change.patch agent/mcp.json docs args [\"servers/files.js\", \"--root\", \"./docs\", \"--read-only\"]; base tree has no docs/",
      "scenario": "Docs server starts with a nonexistent root or fails to start, so the requested docs search returns nothing or errors for every developer",
      "fix": "Add docs/ or point --root at the real docs path; test by launching from the client's cwd and running one search"
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "servers/notes.js: const readOnly = process.argv.includes(\"--read-only\")",
      "scenario": "Flag is parsed but enforcement is not shown; any write tool that ignores readOnly breaks the read-only guarantee",
      "fix": "Show or add enforcement; test that mutating handlers are refused or unlisted under --read-only"
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "agent/mcp.json \"tools\" arrays",
      "scenario": "If the client uses server-advertised tools/list, the reviewed descriptions are ignored and unreviewed server-side descriptions or extra tools reach the model",
      "fix": "Confirm the client honors the config tools array as allowlist/override, or review description strings in notes.js and files.js in this PR"
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "agent/mcp.json \"args\": [\"servers/notes.js\", ...] and \"./docs\"",
      "scenario": "Client resolves paths relative to agent/ or another cwd; servers fail to start",
      "fix": "Document or anchor the launch cwd; test launching as developers do"
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "search_docs args {\"context_lines\": \"integer\"}",
      "scenario": "Model passes a large context_lines value and dumps whole files into context; the 0-5 bound is prose only",
      "fix": "Add minimum/maximum to the schema if supported and clamp server-side"
    }
  ]
}
```