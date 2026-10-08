VERDICT: **SHIP.** The config does what was asked: two read-only servers with search and read only, docs rooted at `./docs`, and tool descriptions that only describe the tools. The remaining points are small checks, not blockers.

CONFIDENCE IN VERDICT: **medium.** This review was done without tools, so nothing was run. Only the entry-point stubs shown in `base/servers/` were visible, not the tool implementations, and the assistant client's config semantics are unknown. The work was not produced in this conversation, so there is no anchoring risk from authorship.

## Pass 1: Reconstruct

The PR adds `agent/mcp.json` with two servers:
- **`notes`** runs `servers/notes.js --read-only` and exposes `notes_search` and `notes_read`.
- **`docs`** runs `servers/files.js --root ./docs --read-only` and exposes `search_docs`.

The PR claims that both servers are read-only, that docs is confined to `./docs`, and that the descriptions contain nothing beyond what each tool does.

For this to be correct, five things must hold:
1. The two entry points honour `--read-only`.
2. `files.js` actually serves a tool named `search_docs`.
3. Relative paths resolve from the directory the client launches in.
4. The client exposes only the declared tools, or the servers expose nothing else.
5. The description text contains no instructions to the model.

## Pass 2: Attack (Track B)

**Read-only enforcement (holds).**
- `base/servers/files.js:4`: `writable = args.includes("--allow-write") && !args.includes("--read-only")`. The config passes `--read-only` and not `--allow-write`, so `writable` is `false` either way. CONFIRMED.
- `notes.js` sets `readOnly = true` from the same flag. Whether every handler checks it is not visible.

**Root parsing (holds).**
- `files.js:3`: `args[args.indexOf("--root") + 1]` yields `"./docs"` for the argument order in the patch. CONFIRMED.
- The `-1 → args[0]` pitfall when the flag is absent does not apply here, because the flag is present.

**Tool descriptions (hold).** I read all three descriptions for imperative or hidden instructions and found none:
- No "always", "first call", or "ignore".
- No exfiltration hints.
- No cross-tool directives.

`search_docs` only documents its `context_lines` argument and range. This is CONFIRMED clean, which matters given the stakes noted in the context.

**Path traversal.**
- `search_docs` takes no path argument, so there is no traversal surface. CONFIRMED.
- `notes_read(note_id)` takes a free-form string. Whether `notes.js` treats it as a path is not visible. See finding 3.

**Scope.** Nothing extra was added and nothing was cut relative to the request.

## Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Low | UNVERIFIED | `agent/mcp.json` `docs.args`; `base/servers/files.js` | Nothing shown establishes that `files.js` serves a tool named `search_docs`. Its comment says only that it "serves text files under --root". `notes.js` has the comment saying the tools in `agent/mcp.json` are served from there; `files.js` has no equivalent. | The client starts the docs server, but no `search_docs` tool exists, or it has a different name or argument names (`phrase`, `context_lines`). The tool is then missing or calls fail. | Start the server and list its tools. Confirm the name and argument names match the config exactly. |
| 2 | Low | PROBABLE | `agent/mcp.json`: `"servers/notes.js"`, `"servers/files.js"`, `"./docs"` | All paths are relative. The config lives in `agent/`, but the paths assume the process cwd is the repo root. | A client that resolves paths relative to the config file, or a developer whose assistant starts in a subdirectory, gets "module not found". Worse, `files.js` gets rooted at a different `docs` directory. | Document that the client must launch from the repo root, or use a repo-root variable if the client supports one. Smoke-test from a subdirectory. |
| 3 | Low | UNVERIFIED | `notes_read` `args: {"note_id": "string"}`; `base/servers/notes.js` | `note_id` is unconstrained, and its handling is not visible. | If `notes.js` joins `note_id` onto a directory path, an id like `../../.env` reads files outside the notes store. That is still "read-only" but exceeds the requested scope, and it can be triggered by injected content in a note or doc. | Test `notes_read("../../README.md")` and confirm it is rejected. Validate ids against the actual id format. |
| 4 | Low | UNVERIFIED | `search_docs` description "(0 to 5)"; `args.context_lines: "integer"` | The 0–5 range is stated only in prose and is not in the schema. Server-side enforcement is not visible. | The model passes `context_lines: 100000`, and each match returns whole files. This is noisy and costly in context, but stays inside `./docs`. | Clamp the value in the server, or express the bound in the schema if the config format supports it. |
| 5 | Low | UNVERIFIED | `tools` arrays in `agent/mcp.json` | Two things depend on the client: whether it uses these config-side descriptions at all (it may use server-provided ones instead), and whether it restricts the model to the listed tools. | The server advertises extra tools with their own descriptions, which the model would see. Those descriptions were never reviewed in this PR, and any extra write-capable tools would rely solely on `--read-only` being checked in every handler. | Confirm how the client treats `tools`, then compare the server's advertised tools and descriptions against the config. |

## What holds up

- `--read-only` is passed to both servers, and `files.js` provably disables writes under it.
- The docs root is parsed correctly as `./docs`.
- Only search and read tools are declared, which matches the request exactly.
- No tool description contains instructions, directives, or hidden content.
- `search_docs` has no path argument, so it has no traversal surface.

## Unverified claims

- **"Both run from the existing `servers/` entry points."** True for the files, but it is unconfirmed that `files.js` implements `search_docs`. Confirm by listing the server's tools.
- **"Notes server is read-only."** Only flag parsing is shown, not handler enforcement. Confirm by reading the `notes.js` tool handlers, or by attempting a write.
- **The 0–5 bound on `context_lines`.** Confirm by checking for a clamp in the search handler.

## Questions for the author

1. Does `servers/files.js` register exactly `search_docs(phrase, context_lines)`, or is there a separate docs server?
2. Does the client resolve `args` paths relative to the repo root or relative to `agent/`?
3. Are the `tools` descriptions in this file what the model sees, or does the server's `tools/list` override them?

## Decision-maker summary

The config matches the request, keeps both servers read-only, and its tool descriptions are clean. Before merge, run a 2-minute smoke test: start each server from the repo root and from a subdirectory, list the tools, and try `notes_read` with a `../` id. If you merge without that test, the realistic risk is broken tools for some developers, not a security problem.

```json
{
  "verdict": "SHIP",
  "findings": [
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "agent/mcp.json docs.args; base/servers/files.js",
      "scenario": "files.js may not serve a tool named search_docs with args phrase/context_lines; the tool is then missing or calls fail.",
      "fix": "Start files.js, list its tools, and confirm the name and argument names match the config."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "agent/mcp.json: \"servers/notes.js\", \"servers/files.js\", \"./docs\"",
      "scenario": "Relative paths assume cwd is the repo root; a client resolving them relative to agent/ or launched from a subdirectory fails to start the servers or roots docs elsewhere.",
      "fix": "Document the repo-root requirement or use a repo-root variable; smoke-test from a subdirectory."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "notes_read args.note_id; base/servers/notes.js",
      "scenario": "If note_id is joined onto a path, notes_read('../../.env') reads files outside the notes store, possibly triggered by injected content.",
      "fix": "Test notes_read with a ../ id and confirm rejection; validate ids against the real id format."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "search_docs description '(0 to 5)'; args.context_lines: integer",
      "scenario": "The range is prose-only; a huge context_lines returns whole files and floods the context (stays within ./docs).",
      "fix": "Clamp context_lines server-side or encode the bound in the schema."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "tools arrays in agent/mcp.json",
      "scenario": "If the client uses server-advertised tools/descriptions instead, unreviewed tools or descriptions reach the model, and read-only depends solely on handler checks.",
      "fix": "Confirm how the client treats the tools field; diff server tools/list against the config."
    }
  ]
}
```